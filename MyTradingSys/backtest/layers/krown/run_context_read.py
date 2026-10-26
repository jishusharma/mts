"""Confluence S3: standalone context read, PRE_REG_CONFLUENCE.md s3.1 (D1 vs naive trend baselines) and s3.2 (b) (BBWP_4h vs next-24h realised vol).
Run exactly as frozen on DEV (2022-01-01..2024-06-30). DEV_EXT needs 2020-21 perp 1h bars that do not exist on this host: reported NOT_RUN (s0.3, s4.6),
never substituted. VALIDATION / HOLDOUT bars (>= 2024-07-01) are never read: the loader masks them before any value is used and guard() raises on any.
The sizing arm (test 18) needs the pooled S4 events and is not part of this card. Writes run/CONTEXT_READ.md and appends run/ACCESS_LOG.md.
Labels: SOURCED = quote + file:line in PRE_REG_CONFLUENCE.md; OURS = judgement.
"""
import csv
import datetime as dt
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                                   # MyTradingSys/
RUN = ROOT / "research" / "krown_audit_2026-10-22" / "run"
sys.path.insert(0, str(ROOT.parent))
sys.path.insert(0, str(ROOT / "research" / "context_null_2026-10-16"))

CUT = 1719792000000                # 2024-07-01 UTC exclusive (s0.4)
Y2023 = 1672531200000              # 2022 | 2023-24H1 split (s1)
H1 = 3_600_000
DAY = 86_400_000
COST = 0.10                        # % round trip, primary (s1)
Z_HOLM = 2.991                     # Holm m = 18 (s2)
Z_NOM = 1.96
HORIZON = 24                       # bars of 1h (s3.1)
NPZ = Path("F:/MTS/data/bigtrade/cache/perp/klines_1h.npz")
CTX = RUN / "context_dev.csv"


class AccessViolation(Exception):
    pass


def guard(ts, cut=CUT):
    """Raise if any bar open time is at or after the cut (s0.4)."""
    ts = np.asarray(ts)
    if ts.size and int(ts.max()) >= cut:
        raise AccessViolation("bar %d >= cut %d" % (int(ts.max()), cut))


def week_of(ts_ms):
    """Monday-anchored week index (1970-01-01 was a Thursday)."""
    return (np.asarray(ts_ms, dtype=np.int64) // DAY + 3) // 7


def cluster_mean(x, groups):
    """Mean of x with the cluster-robust SE (CR0): sqrt(sum_g (sum_{i in g}(x_i - mean))^2) / n. Returns mean, se, t, n_groups."""
    x = np.asarray(x, float)
    n = len(x)
    m = x.mean()
    _, inv = np.unique(groups, return_inverse=True)
    s = np.bincount(inv, weights=x - m)
    se = float(np.sqrt((s * s).sum()) / n)
    return float(m), se, (float(m / se) if se > 0 else float("nan")), len(s)


def slope_cluster(x, y, groups):
    """OLS slope of y on x (with intercept), CR0 cluster SE. Returns slope, se, t."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    xc, yc = x - x.mean(), y - y.mean()
    sxx = (xc * xc).sum()
    b = (xc * yc).sum() / sxx
    e = yc - b * xc
    _, inv = np.unique(groups, return_inverse=True)
    s = np.bincount(inv, weights=xc * e)
    se = float(np.sqrt((s * s).sum()) / sxx)
    return float(b), se, (float(b / se) if se > 0 else float("nan"))


def _rank(x, method="average"):
    import pandas as pd
    return pd.Series(np.asarray(x, float)).rank(method=method).to_numpy()


def spearman_cluster(x, y, groups):
    """Spearman rho = OLS slope of the standardised average ranks (so rho is exact); t from the week-clustered slope SE (OURS)."""
    rx, ry = _rank(x), _rank(y)
    zx, zy = (rx - rx.mean()) / rx.std(), (ry - ry.mean()) / ry.std()
    b, se, t = slope_cluster(zx, zy, groups)
    return b, se, t


def block_ci(vals, ts_ms, n_boot=1000, block_days=20, seed=0):
    """20-day block bootstrap (OURS) of the mean of vals: percentile 2.5 / 97.5. Blocks are resampled whole."""
    blk = (np.asarray(ts_ms, dtype=np.int64) // DAY) // block_days
    _, inv = np.unique(blk, return_inverse=True)
    sums = np.bincount(inv, weights=np.asarray(vals, float))
    cnts = np.bincount(inv).astype(float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(sums), size=(n_boot, len(sums)))
    est = sums[idx].sum(1) / cnts[idx].sum(1)
    return float(np.percentile(est, 2.5)), float(np.percentile(est, 97.5))


def mde(n, weeks, z=Z_HOLM + 0.8416, sd=2.5, rho=0.3):
    """Minimum detectable effect on a mean at 80 % power (OURS inputs, PRE_REG s3.1): z * sd * sqrt(deff / n), deff = 1 + (n/weeks - 1) rho."""
    deff = 1 + (n / weeks - 1) * rho
    return z * sd * (deff / n) ** 0.5


# ---------------------------------------------------------------------------------------------------------------- data
def load_context():
    d1, h4 = [], []
    with open(CTX, newline="", encoding="utf-8") as f:
        rows = csv.DictReader(r for r in f if not r.startswith("#"))
        for r in rows:
            if int(r["open_ms"]) >= CUT:
                raise AccessViolation("context row %s >= cut" % r["open_utc"])
            (d1 if r["tf"] == "1d" else h4).append(r)
    return d1, h4


def _int(s):
    return int(float(s)) if s not in ("", None) else None


def prepare_daily(d1):
    d1 = sorted(d1, key=lambda r: int(r["available_at"]))
    av = np.array([int(r["available_at"]) for r in d1], dtype=np.int64)
    sides = {
        "D1": np.array([_side_d1(_int(r["trend_1d_ours"]), _int(r["trend_1w_ours"])) for r in d1]),
        "sma": np.array([_int(r["naive_trend_sma200"]) for r in d1]),
        "ret": np.array([_int(r["naive_trend_ret20"]) for r in d1]),
    }
    return av, sides


def _side_d1(t1d, t1w):
    """+1 if both up, -1 if both down, else 0 (s3.1; range -> 0, F17)."""
    if t1d == 1 and t1w == 1:
        return 1
    if t1d == -1 and t1w == -1:
        return -1
    return 0


def build_points(t, o, c, av, sides, horizon=HORIZON, cost=COST):
    """Decision points = every closed 1h bar k whose entry (bar k+1 open) and exit (close of bar k+horizon) exist.
    decision_ts = t[k] + 1h; context row = last row with available_at < decision_ts (strict; point-in-time).
    gross = (c[k+h] / o[k+1] - 1) * 100 (long sign). Returns dict of arrays."""
    guard(t)
    n = len(t)
    k = np.arange(0, n - horizon)
    dec = t[k] + H1
    fwd_gross = (c[k + horizon] / o[k + 1] - 1.0) * 100.0
    pos = np.searchsorted(av, dec, side="left") - 1          # last index with av < dec
    ok = pos >= 0
    out = {"k": k[ok], "dec": dec[ok], "gross": fwd_gross[ok]}
    for name, arr in sides.items():
        out["side_" + name] = arr[pos[ok]]
    out["net"] = {nm: out["side_" + nm] * out["gross"] - cost * (out["side_" + nm] != 0) for nm in sides}
    return out


def strata(t, c, k):
    """Hour-of-day x realised-vol tercile key of closed bar k (context_null.context_key, bars <= k only); None when unknown."""
    import context_null as cn
    cfg = cn.Config(bar_min=60, ts0_ms=int(t[0]), match=("hour", "vol"))
    rv = cn.rolling_rv(c, cfg.vol_win_min // cfg.bar_min)
    return [cn.context_key(c, int(i), cfg, rv=rv) for i in k]


def matched_mean(vals, keys, weeks):
    """Equal stratum weights: mean over strata of the stratum mean; CR0 cluster SE with weights w_i = 1/(S n_s). Returns mean, se, t, n_strata."""
    vals = np.asarray(vals, float)
    ks = [k for k in keys]
    uniq = {}
    for i, key in enumerate(ks):
        uniq.setdefault(key, []).append(i)
    S = len(uniq)
    w = np.zeros(len(vals))
    for key, ix in uniq.items():
        w[ix] = 1.0 / (S * len(ix))
    est = (w * vals).sum()
    # centre each observation on its stratum mean so the influence of an observation is w_i (x_i - m_stratum)
    cen = np.zeros(len(vals))
    for key, ix in uniq.items():
        cen[ix] = vals[ix] - vals[ix].mean()
    _, inv = np.unique(weeks, return_inverse=True)
    s = np.bincount(inv, weights=w * cen)
    se = float(np.sqrt((s * s).sum()))
    return float(est), se, (float(est / se) if se > 0 else float("nan")), S


# ---------------------------------------------------------------------------------------------------------------- tests s3.1 / s3.2
def read_31(P, t, c):
    res = {}
    d1 = P["side_D1"]
    wk = week_of(P["dec"])
    yr = P["dec"] < Y2023
    nz = d1 != 0
    res["n_points"] = len(d1)
    res["weeks_all"] = len(np.unique(wk))
    res["n_D1"] = int(nz.sum())
    res["weeks_D1"] = len(np.unique(wk[nz]))
    res["share_D1_nonzero"] = float(nz.mean())
    res["share_up"] = float((d1 == 1).mean())
    res["share_down"] = float((d1 == -1).mean())
    res["mde_pop"] = mde(len(d1), res["weeks_all"])
    res["mde_D1"] = mde(res["n_D1"], res["weeks_D1"])
    for nm in ("D1", "sma", "ret"):
        s = P["side_" + nm]
        m = s != 0
        res["E_" + nm] = cluster_mean(P["net"][nm][m], wk[m]) + (int(m.sum()),)
    # best baseline on the D1 != 0 points (s3.1: larger E on the same points; chosen on DEV and fixed for DEV_EXT)
    on = {nm: float(P["net"][nm][nz].mean()) for nm in ("sma", "ret")}
    best = max(on, key=lambda k: on[k])
    res["best"] = best
    res["on_D1_points"] = on
    diff = P["net"]["D1"][nz] - P["net"][best][nz]
    res["Delta"] = cluster_mean(diff, wk[nz])
    res["Delta_other"] = {nm: cluster_mean(P["net"]["D1"][nz] - P["net"][nm][nz], wk[nz]) for nm in ("sma", "ret")}
    res["E_D1_year"] = {
        "2022": cluster_mean(P["net"]["D1"][nz & yr], wk[nz & yr]) + (int((nz & yr).sum()),),
        "2023-24H1": cluster_mean(P["net"]["D1"][nz & ~yr], wk[nz & ~yr]) + (int((nz & ~yr).sum()),),
    }
    res["ci_E_D1"] = block_ci(P["net"]["D1"][nz], P["dec"][nz])
    res["ci_Delta"] = block_ci(diff, P["dec"][nz])
    # literal reading beside: side x (gross - cost), cost sign-flipped for shorts
    lit = d1[nz] * (P["gross"][nz] - COST)
    res["E_D1_literal"] = cluster_mean(lit, wk[nz])
    # context-matched line (beside)
    keys_all = strata(t, c, P["k"])
    sel = [i for i in np.flatnonzero(nz) if keys_all[i] is not None]
    res["matched"] = matched_mean(P["net"]["D1"][sel], [keys_all[i] for i in sel], wk[sel]) + (len(sel),)
    e, de = res["E_D1"], res["Delta"]
    y1, y2 = res["E_D1_year"]["2022"][0], res["E_D1_year"]["2023-24H1"][0]
    res["checks"] = {
        "E_D1>0 & t>=%.3f" % Z_HOLM: bool(e[0] > 0 and e[2] >= Z_HOLM),
        "Delta>0 & t>=%.2f" % Z_NOM: bool(de[0] > 0 and de[2] >= Z_NOM),
        "E_D1>0 in 2022 and 2023-24H1": bool(y1 > 0 and y2 > 0),
    }
    res["verdict"] = "PASS" if all(res["checks"].values()) else "FAIL"
    return res


def read_32(t, c, h4):
    """BBWP_4h at each closed 4h bar vs realised vol of the next 24 h (sqrt of the sum of squared 1h log returns)."""
    guard(t)
    idx = {int(x): i for i, x in enumerate(t)}
    lr = np.zeros(len(t))
    lr[1:] = np.diff(np.log(c))
    cs = np.concatenate(([0.0], np.cumsum(lr * lr)))
    bb, rv, dec = [], [], []
    for r in h4:
        if r["bbwp_4h_ours"] in ("", None):
            continue
        d = int(r["open_ms"]) + 4 * H1                      # decision = 4h bar close
        j = idx.get(d)                                      # first 1h bar after the decision
        if j is None or j + HORIZON > len(t):
            continue
        bb.append(float(r["bbwp_4h_ours"]))
        fwd_rv = float(np.sqrt(cs[j + HORIZON] - cs[j]))    # returns of bars j..j+23, the first measured from the close of bar j-1 (= decision)
        rv.append(fwd_rv)
        dec.append(d)
    bb, rv, dec = np.array(bb), np.array(rv), np.array(dec, dtype=np.int64)
    wk = week_of(dec)
    rho, se, tt = spearman_cluster(bb, rv, wk)
    dec_i = ((_rank(bb, "first") - 1) * 10 // len(bb)).astype(int)
    table = [(q + 1, int((dec_i == q).sum()), float(bb[dec_i == q].min()), float(bb[dec_i == q].max()), float(rv[dec_i == q].mean() * 100)) for q in range(10)]
    yr = dec < Y2023
    yy = {}
    for nm, m in (("2022", yr), ("2023-24H1", ~yr)):
        yy[nm] = spearman_cluster(bb[m], rv[m], wk[m]) + (int(m.sum()),)
    return {"n": len(bb), "weeks": len(np.unique(wk)), "rho": rho, "se": se, "t": tt, "table": table, "years": yy,
            "positive": bool(rho > 0), "t_ge_nominal": bool(tt >= Z_NOM)}


# ---------------------------------------------------------------------------------------------------------------- run + write
def f(x, nd=3):
    return "%.*f" % (nd, x)


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def write_md(r31, r32, meta):
    L = []
    a = L.append
    a("# CONTEXT_READ (S3): Krown D1 vs naive trend, BBWP_4h vs next-24h realised vol")
    a("")
    a("Generated by `MyTradingSys/backtest/layers/krown/run_context_read.py`, run %s UTC. Frozen by `PRE_REG_CONFLUENCE.md` s3.1-3.2 (commit 80413ab75, before this file). "
      "Class C2, weight CRUCIAL. DEV only (2022-01-01..2024-06-30). No bar >= 2024-07-01 was read (`ACCESS_LOG.md`). Every number: OURS unless a label says SOURCED." % meta["run_utc"])
    a("")
    a("## Verdict")
    a("")
    a("| test | verdict | basis |")
    a("|---|---|---|")
    a("| 3.1 context read (a), Holm test 1 | **%s** | %s |" % (r31["verdict"], "; ".join("%s: %s" % (k, "yes" if v else "NO") for k, v in r31["checks"].items())))
    a("| 3.2 context read (b), descriptive | rho = %s, t = %s | no verdict by design (PRE_REG s3.2); expectation \"positive\": **%s** |" % (f(r32["rho"]), f(r32["t"], 2), "met" if r32["positive"] else "NOT met"))
    a("| DEV_EXT arms of both | **NOT_RUN** | 2020-21 perp 1h bars absent on this host (`F:/MTS/data/bigtrade/cache/perp/klines_1h.npz` starts 2022-01-01; `dev_ext_2019_2021` absent); s0.3 / s4.6: reported NOT_RUN, nothing substituted |")
    a("")
    if r31["verdict"] == "FAIL":
        a("**Consequence (PRE_REG s3.1, SOURCED):** FAIL closes the Krown CONTEXT role for filters in this run: test 2 (pooled conditional read) and the (a)-PASS branches of T2/T4 are not run; D1 remains a tag; the sizing arm and T2 primary run regardless.")
    else:
        a("**Consequence:** PASS on DEV. Rule 3 (s4) still needs the same-sign statistic on DEV_EXT, which is NOT_RUN here, so the VALIDATION precondition is NOT met by this file; test 2 may proceed in S4 as hypothesis-generating.")
    a("")
    a("## 3.1 Context read (a): D1 vs naive trend baselines, signed 24 h net return")
    a("")
    a("Definition (as frozen, s3.1): decision points are all closed 1h bars of DEV; entry at the next 1h open; r24 = close of the 24th bar after the decision over the entry open, "
      "minus 0.10 % per position taken (DECISION OURS: cost subtracted after the sign, per s1 \"signed by the event side; minus 0.10 %\"; a flat side pays nothing; funding not modelled, 24 h window, OURS). "
      "Side from the last 1d context row with available_at < decision_ts (strict). Overlapping windows: SE clustered by Monday-anchored week (CR0, OURS formula), 20-day block bootstrap beside (1,000 resamples, seed 0).")
    a("")
    a("| quantity | value | label |")
    a("|---|---|---|")
    a("| decision points (DEV 1h bars with entry and a 24-bar exit before the cut) | %d (the pre-reg's 21,888 minus the last 24 whose exit would cross 2024-07-01) | OURS |" % r31["n_points"])
    a("| weeks (all / D1 != 0) | %d / %d | OURS |" % (r31["weeks_all"], r31["weeks_D1"]))
    a("| side_D1 shares: +1 / -1 / 0 | %s / %s / %s | OURS |" % (f(r31["share_up"]), f(r31["share_down"]), f(1 - r31["share_D1_nonzero"])))
    a("| MDE on E_D1, 80 %% power (sd 2.5 %%, rho 0.3, z %.3f + 0.842): population n / D1-nonzero n | %s %% / %s %% (pre-reg states about 0.47 %%) | OURS |" % (Z_HOLM, f(r31["mde_pop"], 2), f(r31["mde_D1"], 2)))
    a("")
    a("| side X | n points (side != 0) | E_X, mean net % | SE (week) | t (week) | weeks |")
    a("|---|---|---|---|---|---|")
    for nm, lab in (("D1", "D1 (1d and 1w both up / both down)"), ("sma", "naive_trend_sma200"), ("ret", "naive_trend_ret20")):
        m, se, tt, g, nn = r31["E_" + nm]
        a("| %s | %d | %s | %s | %s | %d |" % (lab, nn, f(m), f(se), f(tt, 2), g))
    a("")
    a("Best baseline on the D1 != 0 points (mean net %% with flat = 0): sma200 %s, ret20 %s -> **%s** (fixed for DEV_EXT; not run).  " % (f(r31["on_D1_points"]["sma"]), f(r31["on_D1_points"]["ret"]), r31["best"]))
    a("")
    a("| statistic | value | SE (week) | t (week) | block 95 % CI | pass bar |")
    a("|---|---|---|---|---|---|")
    m, se, tt, g, nn = r31["E_D1"]
    a("| E_D1 | %s | %s | %s | [%s, %s] | > 0 and t >= %.3f (Holm m = 18): %s |" % (f(m), f(se), f(tt, 2), f(r31["ci_E_D1"][0]), f(r31["ci_E_D1"][1]), Z_HOLM, "met" if r31["checks"]["E_D1>0 & t>=%.3f" % Z_HOLM] else "NOT met"))
    m, se, tt, g = r31["Delta"]
    a("| Delta = D1 - %s (paired, D1 != 0 points) | %s | %s | %s | [%s, %s] | > 0 and t >= %.2f: %s |" % (r31["best"], f(m), f(se), f(tt, 2), f(r31["ci_Delta"][0]), f(r31["ci_Delta"][1]), Z_NOM, "met" if r31["checks"]["Delta>0 & t>=%.2f" % Z_NOM] else "NOT met"))
    a("")
    a("Delta against the other baseline (beside, no verdict): " + "; ".join("D1 - %s = %s (t %s)" % (nm, f(v[0]), f(v[2], 2)) for nm, v in r31["Delta_other"].items()) + ".")
    a("")
    a("### Year split (bar: E_D1 > 0 in both)")
    a("")
    a("| period | n | E_D1 | SE (week) | t |")
    a("|---|---|---|---|---|")
    for nm, v in r31["E_D1_year"].items():
        a("| %s | %d | %s | %s | %s |" % (nm, v[4], f(v[0]), f(v[1]), f(v[2], 2)))
    a("")
    a("### Beside, no verdict")
    a("")
    mm = r31["matched"]
    a("- Context-matched E_D1 (hour-of-day x realised-vol tercile strata, equal stratum weights, %d strata, %d points): %s %% (SE %s, t %s)." % (mm[3], mm[4], f(mm[0]), f(mm[1]), f(mm[2], 2)))
    lit = r31["E_D1_literal"]
    a("- Literal reading, side x (gross - 0.10 %%) i.e. cost sign-flipped for shorts: E_D1 = %s %% (t %s). Reported only to show the verdict does not hinge on the cost-sign reading; the primary is the one above." % (f(lit[0]), f(lit[2], 2)))
    a("- DEV_EXT: NOT_RUN (see Verdict).")
    a("")
    a("## 3.2 Context read (b): BBWP_4h vs the realised volatility of the next 24 h (descriptive)")
    a("")
    a("Population: every closed DEV 4h bar with a BBWP_4h value (7/100, SOURCED FORMULAS.md:537, KR-Q01) and 24 following 1h bars before the cut: n = %d, weeks = %d. "
      "Realised vol = sqrt(sum of squared 1h log returns) over the 24 h after the 4h close (first return from the close at the decision). Spearman rho (average ranks) = slope of standardised ranks; "
      "the t uses a week-clustered CR0 slope SE (OURS approximation)." % (r32["n"], r32["weeks"]))
    a("")
    a("| statistic | value |")
    a("|---|---|")
    a("| Spearman rho | %s |" % f(r32["rho"], 4))
    a("| SE (week) / t (week) | %s / %s |" % (f(r32["se"], 4), f(r32["t"], 2)))
    for nm, v in r32["years"].items():
        a("| rho %s (n %d) | %s (t %s) |" % (nm, v[3], f(v[0], 4), f(v[2], 2)))
    a("")
    a("| BBWP decile | n | BBWP min | BBWP max | mean next-24h realised vol (%) |")
    a("|---|---|---|---|---|")
    for q, n_, lo, hi, v in r32["table"]:
        a("| %d | %d | %s | %s | %s |" % (q, n_, f(lo, 1), f(hi, 1), f(v, 3)))
    a("")
    if r32["positive"]:
        a("Expectation stated in advance (positive): **met**. The sizing arm (test 18, S4) keeps BBWP_4h as its predicted-vol input.")
    else:
        a("Expectation stated in advance (positive): **NOT met** (rho <= 0). Per s3.2 the sizing arm in S4 uses trailing 7-day realised vol instead.")
    a("")
    a("## Not in this card")
    a("")
    a("- Sizing arm (test 18): needs the pooled S4 events; run in S4. DEV_EXT arms: NOT_RUN (data). VALIDATION / HOLDOUT: never read.")
    a("- Rule 7 re-derivation: the week-clustered SE and the Spearman slope SE are checked against hand values in `test_run_context_read.py` (toy x = [1,3,2,6], weeks [A,A,B,B]: mean 3, SE 0.707107, t 4.242641); BBWP is the FORMULAS.md:537 worked example already tested in `test_krown_context.py`.")
    (RUN / "CONTEXT_READ.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


def append_access(meta):
    rows = meta["access"]
    L = ["", "## S3 context read run %s UTC (run_context_read.py)" % meta["run_utc"], "",
         "| file | min bar/ts used | max bar/ts used | rows | note |", "|---|---|---|---|---|"]
    for name, a, b, n, note in rows:
        L.append("| %s | %s | %s | %d | %s |" % (name, iso(a), iso(b), n, note))
    mx = max(b for _, _, b, _, _ in rows)
    L.append("")
    L.append("Maximum bar/decision time used: %s (%d) < %d. PASS. DEV_EXT perp 1h bars (2020-21): absent, not opened." % (iso(mx), mx, CUT))
    with open(RUN / "ACCESS_LOG.md", "a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")


def main():
    z = np.load(NPZ)
    tt = z["t"]
    m = tt < CUT                                             # mask before any value is used
    t, o, c = tt[m].astype(np.int64), z["o"][m], z["c"][m]
    guard(t)
    d1, h4 = load_context()
    av, sides = prepare_daily(d1)
    P = build_points(t, o, c, av, sides)
    r31 = read_31(P, t, c)
    r32 = read_32(t, c, h4)
    last_dec = int(P["dec"].max())
    meta = {"run_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "access": [
                ("bigtrade/cache/perp/klines_1h.npz", int(t.min()), int(t.max()), int(len(t)), "np.load reads whole arrays; mask t < cut applied before any value is used"),
                ("run/context_dev.csv (1d rows)", min(int(r["open_ms"]) for r in d1), max(int(r["open_ms"]) for r in d1), len(d1), "context rows incl. DEV_EXT days; only used where available_at < decision_ts"),
                ("run/context_dev.csv (4h rows)", min(int(r["open_ms"]) for r in h4), max(int(r["open_ms"]) for r in h4), len(h4), "BBWP_4h only"),
                ("decision times (3.1 points)", int(P["dec"].min()), last_dec, int(len(P["dec"])), "decision = bar close; a time equal to the cut is the close of a bar that opened before it")]}
    write_md(r31, r32, meta)
    append_access(meta)
    print(r31["verdict"], r31["E_D1"], r31["Delta"], r32["rho"], r32["t"])


if __name__ == "__main__":
    main()
