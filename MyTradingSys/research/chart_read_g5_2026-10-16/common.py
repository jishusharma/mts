"""Shared helpers for the four chart-read G5 screens (2026-10-16). DEV only (bars before 2024-07-01).

Screen, ran before G3 marks by operator decision 2026-10-16. Costs, delay, clustering and the PASS rule are the
template of research/gross_effect_screen_2026-10-15/ (PRE_REG.md s.1, s.3, s.4); the loader and cluster helpers are
imported from its screen.py. Nothing here chooses a study parameter.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "gross_effect_screen_2026-10-15"))
import screen as S  # noqa: E402  (loader refuses any bar >= 2024-07-01)

TS0, MS, DAYMIN, NDAYS_DEV = S.TS0, S.MS, S.DAYMIN, S.NDAYS_DEV
C_PCT = S.C_PCT                 # 0.14 % round trip = 2 x (5 bp fee + 2 bp slippage); SOURCED: gross_effect_screen PRE_REG s.1
FUND_PCT = S.FUND_PCT           # 1 bp per 00/08/16 UTC settlement crossed (raw_fund archive absent); OURS, as the template
N_MIN = S.N_MIN                 # 200 events, OURS, as the template
PER8H = 8 * 3600 * 1000
DELAY = 1                       # extra 1m bars between the decision-bar close and the fill (template d=1)


def load():
    return S.load_dev(S.dev_files())


def agg(A, n):
    """n-minute bars aligned to UTC multiples of n. A bar with any missing 1m bar is NaN in every field."""
    m = len(A["O"]) // n
    out = {}
    for k, f in (("O", None), ("H", np.max), ("L", np.min), ("C", None), ("V", np.sum), ("TBV", np.sum), ("QV", np.sum)):
        x = A[k][: m * n].reshape(m, n)
        out[k] = x[:, 0] if k == "O" else x[:, -1] if k == "C" else f(x, axis=1)
    bad = np.isnan(A["O"][: m * n].reshape(m, n)).any(1) | np.isnan(A["C"][: m * n].reshape(m, n)).any(1)
    bad |= np.isnan(A["H"][: m * n].reshape(m, n)).any(1) | np.isnan(A["L"][: m * n].reshape(m, n)).any(1)
    for k in out:
        out[k] = np.where(bad, np.nan, out[k])
    return out


# ------------------------------------------------------------------ indicators (FORMULAS.md)
def sma(x, n):
    return pd.Series(np.asarray(x, float)).rolling(n).mean().to_numpy()


def bb(c, n=20, k=2.0):
    """Bollinger: SMA(n) +/- k population SD (chart legend, OPR-BB-MTF-CENTER draft). Returns lo, mid, up."""
    s = pd.Series(np.asarray(c, float))
    mid = s.rolling(n).mean().to_numpy()
    sd = s.rolling(n).std(ddof=0).to_numpy()
    return mid - k * sd, mid, mid + k * sd


def atr_sma(H, L, C, n=14):
    """Plain SMA of the true range (FORMULAS.md s.12), NaN until n valid TRs."""
    H, L, C = (np.asarray(x, float) for x in (H, L, C))
    pc = np.concatenate(([np.nan], C[:-1]))
    tr = np.maximum(H - L, np.maximum(np.abs(H - pc), np.abs(L - pc)))
    return pd.Series(tr).rolling(n).mean().to_numpy()


def rsi_wilder(c, n=14):
    """FORMULAS.md s.1 (SMA seed over the first n deltas, then Wilder smoothing). A NaN close restarts the seed."""
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    cnt, sg, sl, ag, al = 0, 0.0, 0.0, 0.0, 0.0
    for i in range(1, len(c)):
        if np.isnan(c[i]) or np.isnan(c[i - 1]):
            cnt, sg, sl = 0, 0.0, 0.0
            continue
        d = c[i] - c[i - 1]
        g, l = max(d, 0.0), max(-d, 0.0)
        if cnt < n:
            sg, sl, cnt = sg + g, sl + l, cnt + 1
            if cnt < n:
                continue
            ag, al = sg / n, sl / n
        else:
            ag, al = (ag * (n - 1) + g) / n, (al * (n - 1) + l) / n
        out[i] = (100.0 if ag > 0 else 50.0) if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
    return out


# ------------------------------------------------------------------ statistics
def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    den = 1.0 + z * z / n
    ctr = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return float(ctr - half), float(ctr + half)


def fmt_ci(k, n):
    if n == 0:
        return "n=0"
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {100 * k / n:.1f}% [{100 * lo:.1f}, {100 * hi:.1f}]" + (" (n<10, not read)" if n < 10 else "")


def cm_se(g, day):
    """Mean and day-clustered SE: Var(mean) = sum_days (sum_i (g_i - m))^2 / n^2."""
    g = np.asarray(g, float)
    n = len(g)
    if n == 0:
        return float("nan"), float("nan")
    m = g.mean()
    _, inv = np.unique(np.asarray(day), return_inverse=True)
    s = np.bincount(inv, weights=g - m)
    return float(m), float(np.sqrt((s ** 2).sum()) / n)


diff_se = S.diff_cluster          # OLS of g on [1, f], day-clustered sandwich; returns (diff, se)
tstat = S.tstat
max_dd = S.max_dd


def cooldown_mask(t, side, cd):
    """Keep an event only if no KEPT event of the same side lies within cd bars before it (template s.5.1)."""
    t, side = np.asarray(t), np.asarray(side)
    keep = np.zeros(len(t), bool)
    last = {}
    for i in np.argsort(t, kind="stable"):
        s = int(side[i])
        if s in last and t[i] - last[s] <= cd:
            continue
        last[s] = t[i]
        keep[i] = True
    return keep


# ------------------------------------------------------------------ trades on the 1m tape
def trade_gross(O, t, side, h, d=DELAY):
    """Gross % of notional. t = 1m index of the LAST 1m bar of the decision bar (decision at its close).
    p_in = O[t+1+d], p_out = O[t+1+d+h]; NaN if either is outside the DEV tape (VALIDATION is never read)."""
    O = np.asarray(O, float)
    t = np.asarray(t, np.int64)
    n = len(O)
    e, x = t + 1 + d, t + 1 + d + h
    pin = np.where((e >= 0) & (e < n), O[np.clip(e, 0, n - 1)], np.nan)
    pout = np.where((x >= 0) & (x < n), O[np.clip(x, 0, n - 1)], np.nan)
    return np.asarray(side) * (pout / pin - 1.0) * 100.0


def funding_pct(e, x):
    """Flat 1 bp per 00/08/16 UTC settlement crossed between the entry bar open e and exit bar open x (1m indices)."""
    e, x = np.asarray(e, np.int64), np.asarray(x, np.int64)
    return FUND_PCT * ((TS0 + x * MS) // PER8H - (TS0 + e * MS) // PER8H)


def net_cells(A, t, side, hs, d=DELAY):
    """dict h -> gross after funding (still gross of the 0.14 % trading cost), NaN where the exit is beyond DEV."""
    t = np.asarray(t, np.int64)
    out = {}
    for h in hs:
        out[h] = trade_gross(A["O"], t, side, h, d) - funding_pct(t + 1 + d, t + 1 + d + h)
    return out


def placebo_gross(A, t, side, h, lags=(-7, 7), d=DELAY):
    """Report-only control: the same side and hour taken lags days earlier/later (weekday-matched); lags are printed."""
    gs, ds, ts = [], [], []
    for lag in lags:
        tt = np.asarray(t, np.int64) + lag * DAYMIN
        ok = (tt >= 0) & (tt + 1 + d + h < len(A["O"]))
        g = trade_gross(A["O"], tt[ok], np.asarray(side)[ok], h, d) - funding_pct(tt[ok] + 1 + d, tt[ok] + 1 + d + h)
        gs.append(g)
        ds.append((tt[ok] + 1 + d) // DAYMIN)
        ts.append(tt[ok])
    return np.concatenate(gs), np.concatenate(ds), np.concatenate(ts)


def excursion(A, e, side, h, atr):
    """MFE and MAE in ATR units over the h 1m bars starting at the entry bar e (long/short signed)."""
    e = np.asarray(e, np.int64)
    n = len(A["O"])
    idx = e[:, None] + np.arange(h)[None, :]
    inb = (e >= 0) & (idx[:, -1] < n)
    ii = np.clip(idx, 0, n - 1)
    hi, lo = A["H"][ii].max(1), A["L"][ii].min(1)
    pin = A["O"][np.clip(e, 0, n - 1)]
    side = np.asarray(side)
    fav = np.where(side == 1, hi - pin, pin - lo) / atr
    adv = np.where(side == 1, pin - lo, hi - pin) / atr
    return np.where(inb, fav, np.nan), np.where(inb, adv, np.nan)


# ------------------------------------------------------------------ verdict (template PRE_REG s.4, one arm vs one control)
def verdict_arm(g, day, gc, dayc, t, mdd_bh, n_min=N_MIN):
    """g, gc = side-signed gross % after funding (NaN allowed); day = UTC day id; t = time order for the drawdown.
    PASS iff n >= n_min and mean >= C and t_cost >= 2 and DIFF >= +0.05 % and t_DIFF >= 2 and MDD <= buy-and-hold MDD.
    INCONCLUSIVE iff n < n_min (never relabelled FAIL). FAIL otherwise. Cluster-robust by UTC day."""
    g, gc = np.asarray(g, float), np.asarray(gc, float)
    day, dayc, t = np.asarray(day), np.asarray(dayc), np.asarray(t)
    ok, okc = ~np.isnan(g), ~np.isnan(gc)
    n = int(ok.sum())
    r = dict(n=n, n_ctrl=int(okc.sum()))
    if n == 0:
        r.update(mean=np.nan, se=np.nan, net=np.nan, t_net=np.nan, mean_ctrl=np.nan, diff=np.nan, se_diff=np.nan, t_diff=np.nan,
                 mdd=np.nan, mdd_bh=mdd_bh, mde=np.nan, verdict="INCONCLUSIVE")
        return r
    mean, se = cm_se(g[ok], day[ok])
    order = np.argsort(t[ok], kind="stable")
    mdd = max_dd((g[ok] - C_PCT)[order])
    if okc.sum():
        gg = np.concatenate((g[ok], gc[okc]))
        ff = np.concatenate((np.ones(n), np.zeros(int(okc.sum()))))
        diff, dse = diff_se(gg, ff, np.concatenate((day[ok], dayc[okc])))
        mean_c = float(gc[okc].mean())
    else:
        diff = dse = mean_c = float("nan")
    t_net = tstat(mean - C_PCT, se)
    t_diff = tstat(diff, dse) if not np.isnan(diff) else float("nan")
    r.update(mean=mean, se=se, net=mean - C_PCT, t_net=t_net, mean_ctrl=mean_c, diff=diff, se_diff=dse, t_diff=t_diff, mdd=mdd,
             mdd_bh=mdd_bh, mde=2.8 * se)
    ok_pass = (n >= n_min and mean >= C_PCT and t_net >= 2.0 and not np.isnan(diff) and diff >= 0.05 and t_diff >= 2.0
               and mdd <= mdd_bh)
    r["verdict"] = "PASS" if ok_pass else ("INCONCLUSIVE" if n < n_min else "FAIL")
    return r


def headline(verdicts):
    """Study word from arm words: PASS if any arm passes; FAIL only if every arm is FAIL; else INCONCLUSIVE."""
    v = list(verdicts)
    if "PASS" in v:
        return "PASS"
    return "FAIL" if v and all(x == "FAIL" for x in v) else "INCONCLUSIVE"


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def arm_row(name, r):
    f = lambda x, p=4: "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{p}f}"
    return [name, r["n"], f(r["mean"]), f(r["se"]), f(r["net"]), f(r["t_net"], 2), r["n_ctrl"], f(r["mean_ctrl"]), f(r["diff"]),
            f(r["t_diff"], 2), f(r["mdd"], 2), f(r["mde"]), r["verdict"]]


ARM_HEAD = ["arm", "n", "mean G % (after funding)", "SE (day-cl.)", "net of 0.14 %", "t_net", "n_ctrl", "mean_ctrl", "DIFF vs ctrl %",
            "t_DIFF", "MDD (% clip)", "MDE 80 % (2.8 SE)", "verdict"]
