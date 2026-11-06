"""Null, realised-minus-null per cell, Brier of null vs cell-conditioned model out of sample, Holm. Definitions frozen in PRE_REG.md.

    python flip_model.py            # reads flip_table.csv.gz, writes cells.csv, per_tf.csv, tleft_calibration.csv, RESULT.md

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
MIN_BARS = 30
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
    """Mean of e with a cluster-robust standard error (cluster = bar), G/(G-1) correction, two-sided normal p. -> (mean, se, z, p)."""
    e = np.asarray(e, float)
    n = len(e)
    if n < 2:
        return float("nan"), float("nan"), float("nan"), 1.0
    mean = e.mean()
    codes, G = pd.factorize(np.asarray(cluster))[0], None
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
    tab["cid"] = tab["tf"] + "|" + tab["bar_ms"].astype(str)
    return tab


def groups_of():
    sys.path.insert(0, str(HERE))
    import flip_table as ft
    return ft.GROUPS


def evaluate(fam, groups, colour):
    """cells frame for one colour definition (open | pc): one row per (group, cell)."""
    y, p0 = "y_" + colour, "p0_" + colour
    rows = []
    cells = sorted(fam["cell"].unique())
    for gname, tfs in groups.items():
        g = fam[fam["tf"].isin(tfs)]
        fit, sc = g[g["win"] == "fit"], g[g["win"] == "score"]
        for cell in cells:
            f, s = fit[fit["cell"] == cell], sc[sc["cell"] == cell]
            delta_fit = float((f[y] - f[p0]).mean()) if len(f) else 0.0
            r = {"group": gname, "cell": cell, "colour": colour, "n_fit": len(f), "n": len(s), "bars": int(s["cid"].nunique()), "delta_fit": delta_fit}
            if len(s):
                pc = np.clip(s[p0] + delta_fit, *CLIP)
                mean, se, z, p = cluster_mean_z((s[y] - s[p0]).to_numpy(), s["cid"].to_numpy())
                r.update(realised=float(s[y].mean()), null=float(s[p0].mean()), delta=mean, se=se, z=z, p=p,
                         brier_null=float(((s[p0] - s[y]) ** 2).mean()), brier_cond=float(((pc - s[y]) ** 2).mean()))
            else:
                r.update(realised=float("nan"), null=float("nan"), delta=float("nan"), se=float("nan"), z=float("nan"), p=1.0,
                         brier_null=float("nan"), brier_cond=float("nan"))
            if r["bars"] < MIN_BARS:
                r["p"] = 1.0                      # NOT_POWERED: never counts
            rows.append(r)
    out = pd.DataFrame(rows)
    out["holm12"] = np.nan
    for gname in groups:
        idx = out.index[out["group"] == gname]
        out.loc[idx, "holm12"] = _holm(out.loc[idx, "p"].fillna(1.0).to_numpy(), 12)
    out["holm48"] = _holm(out["p"].fillna(1.0).to_numpy(), len(out))
    out["lowers_brier"] = out["brier_cond"] < out["brier_null"]
    out["counts"] = (out["bars"] >= MIN_BARS) & out["lowers_brier"] & (out["holm12"] < 0.05)
    out["survives_48"] = out["counts"] & (out["holm48"] < 0.05)
    return out


def per_tf(fam, groups, cells_by_colour):
    rows = []
    for colour, cells in cells_by_colour.items():
        y, p0 = "y_" + colour, "p0_" + colour
        shift = {(r.group, r.cell): r.delta_fit for r in cells.itertuples()}
        for gname, tfs in groups.items():
            for tf in tfs:
                s = fam[(fam["tf"] == tf) & (fam["win"] == "score")]
                if not len(s):
                    rows.append({"tf": tf, "group": gname, "colour": colour, "rows": 0, "bars": 0, "brier_null": np.nan, "brier_cond": np.nan, "status": "NOT_IN_DATA"})
                    continue
                d = s["cell"].map(lambda c: shift.get((gname, c), 0.0)).to_numpy()
                pc = np.clip(s[p0].to_numpy() + d, *CLIP)
                rows.append({"tf": tf, "group": gname, "colour": colour, "rows": len(s), "bars": int(s["cid"].nunique()),
                             "brier_null": float(((s[p0] - s[y]) ** 2).mean()), "brier_cond": float(((pc - s[y]) ** 2).mean()), "status": "ok"})
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
            mean, se, z, p = cluster_mean_z((b["y_open"] - b["p0_open"]).to_numpy(), b["cid"].to_numpy())
            rows.append({"group": gname, "t_left": "%.1f-%.1f" % (lo, min(hi, 1.0)), "n": len(b), "bars": int(b["cid"].nunique()),
                         "realised": float(b["y_open"].mean()), "null": float(b["p0_open"].mean()), "delta": mean, "se": se})
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


def write_result(cells, ptf, calib, fam, groups):
    mix = (HERE / "regime_mix.txt").read_text(encoding="utf-8").strip().splitlines()
    op = cells[cells["colour"] == "open"]
    pcc = cells[cells["colour"] == "pc"]
    cnt = op[op["counts"]]
    s48 = op[op["survives_48"]]
    lows = op[op["lowers_brier"] & (op["bars"] >= MIN_BARS)]
    last_ms = int(fam["bar_ms"].max())
    L = ["# RESULT: candle-close-colour probability per timeframe (card candle-flip-probability-study-1106)", ""]
    for ln in (mix[1], mix[0]):            # "Regime mix (score 2025-01-01..now): 96 weeks: ..." -> "Regime mix: score 2025-01-01..now: 96 weeks: ..."
        head, rest = ln.split("): ", 1)
        L.append("Regime mix: " + head.split("(", 1)[1] + ": " + rest)
    L.append("")
    if len(cnt):
        names = "; ".join("%s %s" % (r.group, r.cell) for r in cnt.itertuples())
        verdict = "**Verdict: %d of %d (group, cell) tests count (Brier lowered out of sample AND Holm p < 0.05, m = 12 per group, open-colour): %s. Survive the study-wide m = 48: %d. The Brier gains are small (table below).**" % (
            len(cnt), len(op), names, len(s48))
    else:
        verdict = ("**Verdict: no cell counts. %d of %d powered (group, cell) tests lower the Brier out of sample, none with Holm p < 0.05 (m = 12 per group) in open-colour; "
                   "survive m = 48: 0. The random-walk null is the engine; the gauge ships as the pure-maths P(keeps colour).**" % (len(lows), int((op["bars"] >= MIN_BARS).sum())))
    L += [verdict, ""]
    agree = int(((op.set_index(["group", "cell"])["counts"]) == (pcc.set_index(["group", "cell"])["counts"])).sum())
    L += ["Prior-close colour check: the `counts` flag agrees with open-colour in %d of %d tests (columns for both in `cells.csv`)." % (agree, len(op)), ""]
    L += ["Fit 2024 (bar close <= 2025-01-01), score bars opening 2025-01-01 .. %s UTC, one row = one evaluation minute inside a bar; n is rows, bars is the cluster count. " % pd.to_datetime(last_ms, unit="ms").strftime("%Y-%m-%d"),
          "1m has no inside, so 1m = NOT_IN_DATA. delta = realised - null (keeps-colour rate), Holm p (12) within the table, Holm p (48) over all four tables. NOT_POWERED = fewer than 30 bars (p = 1).", ""]
    L += ["## Size of the gain (score window, open-colour, all 12 cells of a group pooled, rows weighted)", "",
          "| group | rows | Brier null | Brier cond | gain | gain % | cells that count |", "|---|---|---|---|---|---|---|"]
    for gname in groups:
        g = op[(op["group"] == gname) & (op["n"] > 0)]
        w = g["n"] / g["n"].sum()
        bn, bc = float((w * g["brier_null"]).sum()), float((w * g["brier_cond"]).sum())
        L.append("| %s | %d | %s | %s | %s | %.2f%% | %d of 12 |" % (gname, int(g["n"].sum()), _f(bn, 5), _f(bc, 5), "%+.5f" % (bc - bn), 100 * (bn - bc) / bn, int(g["counts"].sum())))
    po = ptf[(ptf["colour"] == "open") & (ptf["status"] == "ok")]
    dd = po["brier_cond"] - po["brier_null"]
    L += ["", "Reading (computed from the tables, not an extra test): the change in Brier (conditioned minus null) per timeframe runs from %+.5f to %+.5f (worse on %d of %d timeframes), "
          "i.e. a gain of at most %.1f%% of the null's Brier. The sign pattern (keeps-colour rate above the null in Asia and EU with the price inside the bands, below it at the band and in US) "
          "is what a session-blind ATR scale and fat tails would give; this study did not test that, it is a hypothesis for a session-adjusted sigma." % (
              dd.min(), dd.max(), int((dd > 0).sum()), len(dd), 100 * float((-dd / po["brier_null"]).max())), ""]
    for gname in groups:
        g = op[op["group"] == gname]
        L += ["## %s (%s)" % (gname, ", ".join(t for t in groups[gname] if t != "1m")), "",
              "| cell | n | bars | realised | null | delta | Brier null | Brier cond | Holm p (12) | Holm p (48) | counts |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in g.itertuples():
            status = "NOT_POWERED" if r.bars < MIN_BARS else ("YES" if r.counts else "no")
            L.append("| %s | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (r.cell, r.n, r.bars, _f(r.realised), _f(r.null), _f(r.delta), _f(r.brier_null, 5), _f(r.brier_cond, 5), _f(r.holm12, 3), _f(r.holm48, 3), status))
        L.append("")
    L += ["## Brier per timeframe (score window, family rows; cond = the group's fitted cell shifts)", "",
          "| tf | colour | rows | bars | Brier null | Brier cond | cond - null |", "|---|---|---|---|---|---|---|"]
    for r in ptf.itertuples():
        L.append("| %s | %s | %d | %d | %s | %s | %s |" % (r.tf, r.colour, r.rows, r.bars, _f(r.brier_null, 5), _f(r.brier_cond, 5),
                                                         "-" if r.brier_null != r.brier_null else "%+.5f" % (r.brier_cond - r.brier_null)))
    L += ["", "## The null's own calibration by time left (score window, open-colour, all 12 cells pooled)", "",
          "| group | t_left | n | bars | realised | null | delta | se |", "|---|---|---|---|---|---|---|---|"]
    for r in calib.itertuples():
        L.append("| %s | %s | %d | %d | %s | %s | %s | %s |" % (r.group, r.t_left, r.n, r.bars, _f(r.realised), _f(r.null), _f(r.delta), _f(r.se)))
    (HERE / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


def main():
    fam = load_family(HERE / "flip_table.csv.gz")
    groups = {k: [t for t in v if t != "1m"] for k, v in groups_of().items()}
    log_holdout_once()
    by = {c: evaluate(fam, groups, c) for c in ("open", "pc")}
    cells = pd.concat(by.values(), ignore_index=True)
    ptf = per_tf(fam, groups, by)
    calib = tleft_calibration(fam, groups)
    cells.to_csv(HERE / "cells.csv", index=False, lineterminator="\n", float_format="%.6g")
    ptf.to_csv(HERE / "per_tf.csv", index=False, lineterminator="\n", float_format="%.6g")
    calib.to_csv(HERE / "tleft_calibration.csv", index=False, lineterminator="\n", float_format="%.6g")
    write_result(cells, ptf, calib, fam, groups)
    print((HERE / "RESULT.md").read_text(encoding="utf-8")[:6000])


if __name__ == "__main__":
    sys.exit(main())
