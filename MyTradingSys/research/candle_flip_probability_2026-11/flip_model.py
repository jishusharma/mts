"""Null, realised-minus-null per cell, Brier of null vs cell-conditioned model out of sample, Holm. Definitions frozen in PRE_REG.md,
changes after the Haiku review (REVIEW.md) are the Amendments section of PRE_REG.md.

    python flip_model.py            # reads flip_table.csv.gz, writes cells.csv, per_tf.csv, tleft_calibration.csv, regime_split.csv, RESULT.md

`P_close_colour` is the function the live-aid strip mirrors in tf_strip.js (same formula, same clip).
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SIGMA_K = 2.0 * math.sqrt(2.0 / math.pi)       # 1.5958: sigma_bar = ATR / SIGMA_K (SOURCED Brownian range)
CLIP = (0.001, 0.999)
TFS = ("1w", "5d", "3d", "2d", "1d", "12h", "8h", "7h", "6h", "4h", "3h", "2h", "1h", "30m", "15m", "10m", "5m", "3m", "2m", "1m")
MIN_BARS = 30          # distinct score bars AND distinct score weeks a cell needs, distinct fit bars a cell shift needs
START_MS = 1704067200000
WEEK_MS = 7 * 86400000
D_BINS, T_BINS = 8, 5  # post-review baseline: |d| quantile bins (fit window) x time-left fifths
_erf = np.frompyfunc(math.erf, 1, 1)


def _phi(x):
    x = np.asarray(x, float)
    return 0.5 * (1.0 + np.asarray(_erf(x / math.sqrt(2.0)), dtype=float))


def p_keep(d_sd, t_left):
    """Null P(the bar closes with the colour it has now). d_sd = (price - ref) / sigma_bar, t_left = fraction of the bar left (0 < t <= 1).
    The remaining move is N(0, t sigma^2), so P(other side of ref) = Phi(-|d|/sqrt(t)) and P(keeps) = Phi(|d|/sqrt(t)). d = 0 gives 0.5."""
    return _phi(np.abs(np.asarray(d_sd, float)) / np.sqrt(np.asarray(t_left, float)))


def P_close_colour(tf, d_atr, t_left, ctx=None):
    """P(the open candle of timeframe `tf` closes with its current colour), in [0, 1], or None when an input is unreadable (fail closed).
    d_atr = (price - reference) / ATR14 of the timeframe (sign ignored), t_left in [0, 1] = fraction of the bar left.
    ctx = None gives the pure random-walk null; ctx = {"delta": x} adds a fitted cell shift, then clips to [0.001, 0.999]."""
    if tf not in TFS:
        return None
    try:
        d = float(d_atr)
        t = float(t_left)
    except (TypeError, ValueError):
        return None
    if not (math.isfinite(d) and math.isfinite(t)) or t < 0 or t > 1:
        return None
    if t == 0:
        return 1.0 if d != 0 else 0.5
    p = float(p_keep(d * SIGMA_K, t))
    if isinstance(ctx, dict) and isinstance(ctx.get("delta"), (int, float)) and math.isfinite(ctx["delta"]):
        p = min(CLIP[1], max(CLIP[0], p + ctx["delta"]))
    return p


def cluster_mean_z(e, cluster):
    """Mean of e with a cluster-robust standard error, G/(G-1) correction, two-sided normal p. -> (mean, se, z, p)."""
    e = np.asarray(e, float)
    n = len(e)
    if n < 2:
        return float("nan"), float("nan"), float("nan"), 1.0
    mean = e.mean()
    codes = pd.factorize(np.asarray(cluster))[0]
    G = codes.max() + 1
    s = np.bincount(codes, weights=e - mean, minlength=G)
    if G < 2:
        return float(mean), float("nan"), float("nan"), 1.0
    var = G / (G - 1.0) * float((s * s).sum()) / (n * n)
    se = math.sqrt(var)
    if se == 0:
        return float(mean), 0.0, float("inf") if mean != 0 else 0.0, 0.0 if mean != 0 else 1.0
    z = mean / se
    return float(mean), se, float(z), math.erfc(abs(z) / math.sqrt(2.0))


def _holm(p, m):
    sys.path.insert(0, str(REPO))
    from MyTradingSys.backtest import research_kit as rk
    return rk.holm(p, m=m)


def load_family(path):
    tab = pd.read_csv(path)
    tab = tab[tab["sess"] < 3].copy()
    tab["session"] = tab["sess"].map({0: "Asia", 1: "EU", 2: "US"})
    tab["cell"] = tab["htf"] + "/" + tab["session"] + "/" + tab["bb"]
    tab["cid"] = tab["tf"] + "|" + tab["bar_ms"].astype(str)         # one bar of one timeframe
    tab["wid"] = (tab["bar_ms"] - START_MS) // WEEK_MS               # UTC week of the bar open (Monday start): the cluster of the tests (amendment A1)
    return tab


def groups_of():
    sys.path.insert(0, str(HERE))
    import flip_table as ft
    return ft.GROUPS


def fit_baseline(g, colour):
    """Post-review baseline (amendment A5): the null recalibrated on |d| x t_left, fitted on the group's FIT rows only. Returns p_base for every row of g
    (bins with fewer than 30 fit rows fall back to the null)."""
    d, t, y, p0 = np.abs(g["d_" + colour].to_numpy()), g["t_left"].to_numpy(), g["y_" + colour].to_numpy(), g["p0_" + colour].to_numpy()
    fit = (g["win"] == "fit").to_numpy()
    edges = np.quantile(d[fit], np.linspace(0, 1, D_BINS + 1)[1:-1])
    b = np.digitize(d, edges) * T_BINS + np.digitize(t, [0.2, 0.4, 0.6, 0.8])
    nb = D_BINS * T_BINS
    cnt = np.bincount(b[fit], minlength=nb)
    sy = np.bincount(b[fit], weights=y[fit], minlength=nb)
    mean = np.where(cnt >= MIN_BARS, sy / np.maximum(cnt, 1), np.nan)
    pb = mean[b]
    return np.where(np.isnan(pb), p0, pb)


def evaluate(fam, groups, colour):
    """cells frame for one colour definition (open | pc): one row per (group, cell), 12 cells (1d and 1w rows have no HTF cell). Adds fam['pb_<colour>']."""
    y, p0, pbn = "y_" + colour, "p0_" + colour, "pb_" + colour
    fam[pbn] = np.nan
    cells = sorted(fam.loc[fam["htf"] != "na", "cell"].unique())
    rows = []
    for gname, tfs in groups.items():
        gi = fam.index[fam["tf"].isin(tfs)]
        fam.loc[gi, pbn] = fit_baseline(fam.loc[gi], colour)
        g = fam[fam["tf"].isin(tfs) & (fam["htf"] != "na")]
        fit, sc = g[g["win"] == "fit"], g[g["win"] == "score"]
        for cell in cells:
            f, s = fit[fit["cell"] == cell], sc[sc["cell"] == cell]
            fbars = int(f["cid"].nunique())
            ok_fit = fbars >= MIN_BARS                                   # amendment A3: no shift fitted on fewer than 30 fit bars
            d1 = float((f[y] - f[p0]).mean()) if ok_fit else 0.0
            d2 = float((f[y] - f[pbn]).mean()) if ok_fit else 0.0
            r = {"group": gname, "cell": cell, "colour": colour, "n_fit": len(f), "fit_bars": fbars, "n": len(s), "bars": int(s["cid"].nunique()),
                 "weeks": int(s["wid"].nunique()), "delta_fit": d1, "delta_fit_base": d2}
            nan = float("nan")
            if len(s):
                pc = np.clip(s[p0] + d1, *CLIP)
                pc2 = np.clip(s[pbn] + d2, *CLIP)
                mean, se, z, p = cluster_mean_z((s[y] - s[p0]).to_numpy(), s["wid"].to_numpy())
                _, _, _, p_bar = cluster_mean_z((s[y] - s[p0]).to_numpy(), s["cid"].to_numpy())
                m2, se2, z2, p2 = cluster_mean_z((s[y] - s[pbn]).to_numpy(), s["wid"].to_numpy())
                r.update(realised=float(s[y].mean()), null=float(s[p0].mean()), delta=mean, se=se, z=z, p=p, p_bar=p_bar,
                         brier_null=float(((s[p0] - s[y]) ** 2).mean()), brier_cond=float(((pc - s[y]) ** 2).mean()),
                         base=float(s[pbn].mean()), delta2=m2, se2=se2, p2=p2,
                         brier_base=float(((s[pbn] - s[y]) ** 2).mean()), brier_cond2=float(((pc2 - s[y]) ** 2).mean()))
            else:
                r.update(realised=nan, null=nan, delta=nan, se=nan, z=nan, p=1.0, p_bar=1.0, brier_null=nan, brier_cond=nan,
                         base=nan, delta2=nan, se2=nan, p2=1.0, brier_base=nan, brier_cond2=nan)
            if r["bars"] < MIN_BARS or r["weeks"] < MIN_BARS:
                r["p"] = r["p2"] = 1.0                                   # NOT_POWERED: never counts
            rows.append(r)
    out = pd.DataFrame(rows)
    for col, src in (("holm12", "p"), ("holm12_2", "p2")):
        out[col] = np.nan
        for gname in groups:
            idx = out.index[out["group"] == gname]
            out.loc[idx, col] = _holm(out.loc[idx, src].fillna(1.0).to_numpy(), 12)
    out["holm48"] = _holm(out["p"].fillna(1.0).to_numpy(), len(out))
    out["holm48_2"] = _holm(out["p2"].fillna(1.0).to_numpy(), len(out))
    pow_ = (out["bars"] >= MIN_BARS) & (out["weeks"] >= MIN_BARS)
    out["lowers_brier"] = out["brier_cond"] < out["brier_null"]
    out["counts"] = pow_ & out["lowers_brier"] & (out["holm12"] < 0.05)
    out["survives_48"] = out["counts"] & (out["holm48"] < 0.05)
    out["counts2"] = pow_ & (out["brier_cond2"] < out["brier_base"]) & (out["holm12_2"] < 0.05)
    out["survives_48_2"] = out["counts2"] & (out["holm48_2"] < 0.05)
    return out


def per_tf(fam, groups, cells_by_colour):
    rows = []
    for colour, cells in cells_by_colour.items():
        y, p0, pbn = "y_" + colour, "p0_" + colour, "pb_" + colour
        sh1 = {(r.group, r.cell): r.delta_fit for r in cells.itertuples()}
        sh2 = {(r.group, r.cell): r.delta_fit_base for r in cells.itertuples()}
        for gname, tfs in groups.items():
            for tf in tfs:
                s = fam[(fam["tf"] == tf) & (fam["win"] == "score")]
                if not len(s):
                    rows.append({"tf": tf, "group": gname, "colour": colour, "rows": 0, "bars": 0, "brier_null": np.nan, "brier_cond": np.nan,
                                 "brier_base": np.nan, "brier_cond2": np.nan, "status": "NOT_IN_DATA"})
                    continue
                d1 = s["cell"].map(lambda c: sh1.get((gname, c), 0.0)).to_numpy()   # 1d / 1w rows have no cell: shift 0
                d2 = s["cell"].map(lambda c: sh2.get((gname, c), 0.0)).to_numpy()
                pc, pc2 = np.clip(s[p0].to_numpy() + d1, *CLIP), np.clip(s[pbn].to_numpy() + d2, *CLIP)
                rows.append({"tf": tf, "group": gname, "colour": colour, "rows": len(s), "bars": int(s["cid"].nunique()),
                             "brier_null": float(((s[p0] - s[y]) ** 2).mean()), "brier_cond": float(((pc - s[y]) ** 2).mean()),
                             "brier_base": float(((s[pbn] - s[y]) ** 2).mean()), "brier_cond2": float(((pc2 - s[y]) ** 2).mean()), "status": "ok"})
    return pd.DataFrame(rows)


def tleft_calibration(fam, groups):
    rows = []
    edges = [0, 0.2, 0.4, 0.6, 0.8, 1.0000001]
    for gname, tfs in groups.items():
        s = fam[fam["tf"].isin(tfs) & (fam["win"] == "score")]
        for lo, hi in zip(edges[:-1], edges[1:]):
            b = s[(s["t_left"] > lo) & (s["t_left"] <= hi)] if lo > 0 else s[(s["t_left"] >= lo) & (s["t_left"] <= hi)]
            if not len(b):
                continue
            mean, se, z, p = cluster_mean_z((b["y_open"] - b["p0_open"]).to_numpy(), b["wid"].to_numpy())
            rows.append({"group": gname, "t_left": "%.1f-%.1f" % (lo, min(hi, 1.0)), "n": len(b), "weeks": int(b["wid"].nunique()),
                         "realised": float(b["y_open"].mean()), "null": float(b["p0_open"].mean()), "delta": mean, "se": se})
    return pd.DataFrame(rows)


def regime_split(fam, groups):
    """Amendment A7 (REVIEW.md #11): score-window delta of the null and of the recalibrated baseline by the weekly regime tag of the bar-open week."""
    rw = pd.read_csv(HERE / "regime_weeks.csv")
    tag = dict(zip((rw["week_ms"] - START_MS) // WEEK_MS, rw["regime"]))
    s0 = fam[fam["win"] == "score"].copy()
    s0["regime"] = s0["wid"].map(tag)
    rows = []
    for gname, tfs in groups.items():
        for reg in ("bull", "range"):
            b = s0[s0["tf"].isin(tfs) & (s0["regime"] == reg)]
            if not len(b):
                continue
            m1, se1, _, _ = cluster_mean_z((b["y_open"] - b["p0_open"]).to_numpy(), b["wid"].to_numpy())
            m2, se2, _, _ = cluster_mean_z((b["y_open"] - b["pb_open"]).to_numpy(), b["wid"].to_numpy())
            rows.append({"group": gname, "regime": reg, "n": len(b), "weeks": int(b["wid"].nunique()), "delta_null": m1, "se_null": se1, "delta_base": m2, "se_base": se2})
    return pd.DataFrame(rows)


def log_holdout_once():
    sys.path.insert(0, str(REPO))
    from MyTradingSys.backtest import splits
    p = Path(splits.HOLDOUT_LOG)
    if p.exists() and "candle_flip_probability_2026-11" in p.read_text(encoding="utf-8", errors="replace"):
        return
    splits.read_holdout("candle_flip_probability_2026-11", "flip_model.py score pass over public klines, window 2025-01-01..2026-11-06 (holdout part 2025-07..)",
                        "Lead ordered score window 2025-01-01..now; calibration of a context probability, no trade return; holdout BURNED for the flip-probability family",
                        "", window="2025-07..2026-11")


def _f(x, k=4):
    return "-" if x != x else ("%." + str(k) + "f") % x


def write_result(cells, ptf, calib, reg, fam, groups):
    mix = (HERE / "regime_mix.txt").read_text(encoding="utf-8").strip().splitlines()
    op = cells[cells["colour"] == "open"]
    cnt, s48 = op[op["counts"]], op[op["survives_48"]]
    cnt2, s48b = op[op["counts2"]], op[op["survives_48_2"]]
    powered = int(((op["bars"] >= MIN_BARS) & (op["weeks"] >= MIN_BARS)).sum())
    last_ms = int(fam["bar_ms"].max())
    L = ["# RESULT: candle-close-colour probability per timeframe (card candle-flip-probability-study-1106)", ""]
    for ln in (mix[1], mix[0]):            # "Regime mix (score 2025-01-01..now): 96 weeks: ..." -> "Regime mix: score 2025-01-01..now: 96 weeks: ..."
        head, rest = ln.split("): ", 1)
        L.append("Regime mix: " + head.split("(", 1)[1] + ": " + rest)
    L.append("")
    names = lambda d: "; ".join("%s %s" % (r.group.split(" ")[0], r.cell) for r in d.itertuples()) or "none"
    L += ["**Verdict: against the pre-registered random-walk null, %d of %d powered (group, cell) tests count (Brier lowered out of sample AND Holm p < 0.05 at m = 12 per group, "
          "week-clustered SEs) and %d survive the study-wide m = 48: %s. Against the same null recalibrated on |d| and time left (post-review baseline, fitted on 2024), %d count and %d survive m = 48: %s. "
          "The gains are tiny (table below) and the whole score window sits in the repo's burned holdout, so nothing here is a clean out-of-sample claim for a new rule.**" % (
              len(cnt), powered, len(s48), names(s48), len(cnt2), len(s48b), names(s48b)), ""]
    L += ["What changed after the Haiku review (`REVIEW.md`; `PRE_REG.md` Amendments A1-A8): SEs now cluster by UTC week (the bar-level clusters of the frozen plan are in `cells.csv` as `p_bar`); "
          "1d and 1w rows have no HTF cell (their own colour was in it) and are excluded from the 12 cells; a cell shift needs 30 fit bars; the headline is m = 48; "
          "a recalibrated baseline, a regime split and the null's calibration are added. The first run (bar clusters, 16 counted cells) is superseded and is not a result.", ""]
    L += ["Fit 2024 (bar close <= 2025-01-01), score bars opening 2025-01-01 .. %s UTC, one row = one evaluation minute inside a bar; n is rows, bars the distinct bars, weeks the distinct UTC weeks (the cluster). " % pd.to_datetime(last_ms, unit="ms").strftime("%Y-%m-%d"),
          "1m has no inside, so 1m = NOT_IN_DATA. delta = realised - null (keeps-colour rate), Holm p (12) within the table, Holm p (48) over all four tables. NOT_POWERED = fewer than 30 bars or 30 weeks (p = 1). "
          "The prior-close colour is run too (`cells.csv`), but on 24/7 spot it is the open colour to the tick, so agreement between the two is not evidence of anything.", ""]
    L += ["## Size of the gain (score window, open-colour, rows of the 12 cells pooled and weighted; 1d and 1w rows are not in the cells)", "",
          "| group | rows | Brier null | Brier cond (cells on null) | gain | gain % | Brier baseline (abs d x t) | baseline gain % | Brier cond on baseline | cells count (null) | cells count (baseline) |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for gname in groups:
        g = op[(op["group"] == gname) & (op["n"] > 0)]
        w = g["n"] / g["n"].sum()
        bn, bc, bb, b2 = (float((w * g[c]).sum()) for c in ("brier_null", "brier_cond", "brier_base", "brier_cond2"))
        L.append("| %s | %d | %s | %s | %+.5f | %.2f%% | %s | %.2f%% | %s | %d of 12 | %d of 12 |" % (
            gname, int(g["n"].sum()), _f(bn, 5), _f(bc, 5), bc - bn, 100 * (bn - bc) / bn, _f(bb, 5), 100 * (bn - bb) / bn, _f(b2, 5),
            int(g["counts"].sum()), int(g["counts2"].sum())))
    po = ptf[(ptf["colour"] == "open") & (ptf["status"] == "ok")]
    dd = po["brier_cond"] - po["brier_null"]
    sg = cnt.assign(side=np.where(cnt["delta"] > 0, "delta > 0", "delta < 0"), bb=cnt["cell"].str.split("/").str[2]).groupby(["bb", "side"]).size()
    L += ["", "Reading, computed from the tables (no mechanism is claimed): per timeframe the change in Brier (conditioned minus null) runs from %+.5f to %+.5f (worse on %d of %d timeframes), "
          "a gain of at most %.1f%% of the null's Brier; no materiality floor was pre-registered, so these are statistical, not economic, gains. "
          "The counted cells split by band position and sign of delta: %s. " % (
              dd.min(), dd.max(), int((dd > 0).sum()), len(dd), 100 * float((-dd / po["brier_null"]).max()),
              ", ".join("%s %s: %d" % (k[0], k[1], v) for k, v in sg.items()) or "none") +
          "The null itself is off (table at the end): the keeps-colour rate runs above it late in long bars, so cell shifts fitted on the null partly measure that error; "
          "the baseline columns remove it, and the 'at band' cells select large |price - mean|, so they largely proxy |d|.", ""]
    for gname in groups:
        g = op[op["group"] == gname]
        L += ["## %s (%s)" % (gname, ", ".join(t for t in groups[gname] if t != "1m")), "",
              "| cell | n | bars | weeks | fit bars | realised | null | delta | Brier null | Brier cond | Holm p (12) | Holm p (48) | counts |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in g.itertuples():
            status = "NOT_POWERED" if (r.bars < MIN_BARS or r.weeks < MIN_BARS) else ("YES" if r.counts else "no")
            L.append("| %s | %d | %d | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (r.cell, r.n, r.bars, r.weeks, r.fit_bars, _f(r.realised), _f(r.null), _f(r.delta), _f(r.brier_null, 5), _f(r.brier_cond, 5), _f(r.holm12, 3), _f(r.holm48, 3), status))
        L += ["", "Post-review baseline for the same cells (null recalibrated on |d| x t_left from 2024; delta2 = realised - baseline):", "",
              "| cell | base | delta2 | Brier base | Brier cond2 | Holm p (12) | Holm p (48) | counts vs baseline |", "|---|---|---|---|---|---|---|---|"]
        for r in g.itertuples():
            status = "NOT_POWERED" if (r.bars < MIN_BARS or r.weeks < MIN_BARS) else ("YES" if r.counts2 else "no")
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (r.cell, _f(r.base), _f(r.delta2), _f(r.brier_base, 5), _f(r.brier_cond2, 5), _f(r.holm12_2, 3), _f(r.holm48_2, 3), status))
        L.append("")
    L += ["## Brier per timeframe (score window, all family rows incl. 1d/1w; cond = the group's fitted cell shifts, base = recalibrated null)", "",
          "| tf | colour | rows | bars | Brier null | Brier cond | cond - null | Brier base | base - null |", "|---|---|---|---|---|---|---|---|---|"]
    for r in ptf.itertuples():
        nn = r.brier_null != r.brier_null
        L.append("| %s | %s | %d | %d | %s | %s | %s | %s | %s |" % (r.tf, r.colour, r.rows, r.bars, _f(r.brier_null, 5), _f(r.brier_cond, 5),
                                                                   "-" if nn else "%+.5f" % (r.brier_cond - r.brier_null), _f(r.brier_base, 5), "-" if nn else "%+.5f" % (r.brier_base - r.brier_null)))
    L += ["", "## Score-window delta by weekly regime (open-colour, all rows of the group; weeks = distinct UTC weeks; fit was 66% bull, score is 76% range)", "",
          "| group | regime | n | weeks | delta vs null | se | delta vs baseline | se |", "|---|---|---|---|---|---|---|---|"]
    for r in reg.itertuples():
        L.append("| %s | %s | %d | %d | %s | %s | %s | %s |" % (r.group, r.regime, r.n, r.weeks, _f(r.delta_null), _f(r.se_null), _f(r.delta_base), _f(r.se_base)))
    L += ["", "## The null's own calibration by time left (score window, open-colour, all rows of the group; week-clustered se)", "",
          "| group | t_left | n | weeks | realised | null | delta | se |", "|---|---|---|---|---|---|---|---|"]
    for r in calib.itertuples():
        L.append("| %s | %s | %d | %d | %s | %s | %s | %s |" % (r.group, r.t_left, r.n, r.weeks, _f(r.realised), _f(r.null), _f(r.delta), _f(r.se)))
    (HERE / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


def main():
    fam = load_family(HERE / "flip_table.csv.gz")
    groups = {k: [t for t in v if t != "1m"] for k, v in groups_of().items()}
    log_holdout_once()
    by = {c: evaluate(fam, groups, c) for c in ("open", "pc")}
    cells = pd.concat(by.values(), ignore_index=True)
    ptf = per_tf(fam, groups, by)
    calib = tleft_calibration(fam, groups)
    reg = regime_split(fam, groups)
    for name, df in (("cells.csv", cells), ("per_tf.csv", ptf), ("tleft_calibration.csv", calib), ("regime_split.csv", reg)):
        df.to_csv(HERE / name, index=False, lineterminator="\n", float_format="%.6g")
    write_result(cells, ptf, calib, reg, fam, groups)
    print((HERE / "RESULT.md").read_text(encoding="utf-8")[:9000])


if __name__ == "__main__":
    sys.exit(main())
