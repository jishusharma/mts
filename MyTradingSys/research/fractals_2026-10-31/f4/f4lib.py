"""F4 library: 8h state features, RULE/ANALOG events, trade simulator, controls. See PRE_REG.md (frozen before any run)."""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "MyTradingSys", "backtest"))
import fees  # noqa: E402

TAKER = fees.BINANCE_TAKER
BAR = 28800
HORIZONS = (3, 6, 9)
K = 20
SPACING = 3
MIN_LIB = 200
PATH_L = 24
NSCAL = 7
SCAL_COLS = ("pctb", "bwpct_prev", "rsi", "rsigap", "stoch", "volz", "cvd")


def build_8h(d):
    """8h bars from 1h rows (cols t,o,h,l,c,v,tbv; t = open time in s). Complete buckets (8 hours) only."""
    d = d.drop_duplicates("t").sort_values("t")
    g = (d.t.to_numpy() // BAR).astype(np.int64)
    a = d.assign(g=g).groupby("g").agg(o=("o", "first"), h=("h", "max"), l=("l", "min"), c=("c", "last"),
                                       v=("v", "sum"), tbv=("tbv", "sum"), n=("t", "size"))
    a = a[a.n == 8].copy()
    a["t"] = a.index.to_numpy() * BAR
    return a[["t", "o", "h", "l", "c", "v", "tbv"]].reset_index(drop=True)


def delta(v, tbv):
    return 2.0 * np.asarray(tbv, float) - np.asarray(v, float)


def cvd_slope(v, tbv, win=8):
    dl = pd.Series(delta(v, tbv))
    vs = pd.Series(np.asarray(v, float))
    return (dl.rolling(win).sum() / vs.rolling(win).sum()).to_numpy()


def features(b):
    c = b.c.astype(float)
    mid = c.rolling(20).mean()
    sd = c.rolling(20).std(ddof=0)
    up, lo = mid + 2 * sd, mid - 2 * sd
    bw = (up - lo) / mid
    pctb = (c - lo) / (up - lo)
    bwpct = bw.rolling(90).apply(lambda x: float((x <= x[-1]).mean()), raw=True)
    dd = c.diff()
    au = dd.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    ad = (-dd).clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    rsi = 100 - 100 / (1 + au / ad.replace(0, 1e-12))
    rsi.iloc[:14] = np.nan
    rsigap = rsi - rsi.rolling(14).mean()
    mn, mx = rsi.rolling(14).min(), rsi.rolling(14).max()
    stoch = ((rsi - mn) / (mx - mn).replace(0, np.nan)).rolling(3).mean()
    v = b.v.astype(float)
    volz = (v - v.shift(1).rolling(20).mean()) / v.shift(1).rolling(20).std(ddof=0).replace(0, np.nan)
    inband = ((c >= lo) & (c <= up)).astype(float).where(lo.notna())
    lr = np.log(c).diff()
    return pd.DataFrame({"pctb": pctb, "bw": bw, "bwpct_prev": bwpct.shift(1), "rsi": rsi, "rsigap": rsigap,
                         "stoch": stoch, "volz": volz, "cvd": cvd_slope(b.v, b.tbv), "lower": lo, "upper": up,
                         "inband": inband, "vol30": lr.rolling(30).std(ddof=0)})


def rule_events(F):
    inside6 = F.inband.shift(1).rolling(6).min() == 1.0
    return ((F.bwpct_prev <= 0.30) & inside6 & (F.pctb < 0) & (F.volz >= 2.0)).fillna(False).to_numpy()


def sim_trade(side, E, stop, lows, highs, last_close):
    """side -1 short / +1 long. 1R = |stop-E|, target 2R. Stop first if both inside one hour. Returns (net R, net % of E)."""
    risk = (stop - E) if side < 0 else (E - stop)
    if not risk > 0:
        return np.nan, np.nan
    target = E + side * 2.0 * risk
    X = last_close
    for lo, hi in zip(lows, highs):
        if side < 0:
            if hi >= stop:
                X = stop
                break
            if lo <= target:
                X = target
                break
        else:
            if lo <= stop:
                X = stop
                break
            if hi >= target:
                X = target
                break
    fee = TAKER * (E + X)
    return side * (X - E) / risk - fee / risk, side * (X - E) / E * 100.0 - fee / E * 100.0


def valid_bars(bt):
    """Signal bar s valid: bars s-130..s consecutive and s..s+9 consecutive."""
    n = len(bt)
    ok = np.zeros(n, dtype=bool)
    for s in range(130, n - 9):
        ok[s] = bt[s] - bt[s - 130] == 130 * BAR and bt[s + 9] - bt[s] == 9 * BAR
    return ok


def trade_tables(b, h1):
    """For every valid bar and horizon: continuation-short (cr/cp) and fade-long (fr/fp) net R / net %. Arrays (n,) per key."""
    n = len(b)
    t1 = h1.t.to_numpy()
    lo1, hi1, cl1 = h1.l.to_numpy(float), h1.h.to_numpy(float), h1.c.to_numpy(float)
    o1 = h1.o.to_numpy(float)
    out = {(k, h): np.full(n, np.nan) for k in ("cr", "fr", "cp", "fp") for h in HORIZONS}
    bt = b.t.to_numpy()
    ok = valid_bars(bt)
    bh, bl = b.h.to_numpy(float), b.l.to_numpy(float)
    for s in np.flatnonzero(ok):
        i0 = np.searchsorted(t1, bt[s] + BAR)
        if i0 + 72 > len(t1) or t1[i0] != bt[s] + BAR or t1[i0 + 71] - t1[i0] != 71 * 3600:
            continue
        E = o1[i0]
        for h in HORIZONS:
            m = 8 * h
            lw, hg, lc = lo1[i0:i0 + m], hi1[i0:i0 + m], cl1[i0 + m - 1]
            r, p = sim_trade(-1, E, bh[s], lw, hg, lc)
            out[("cr", h)][s], out[("cp", h)][s] = r, p
            r, p = sim_trade(1, E, bl[s], lw, hg, lc)
            out[("fr", h)][s], out[("fp", h)][s] = r, p
    return out, ok


def path_matrix(b):
    """Row s = z-scored log close path c[s-23..s]; NaN rows where not computable or flat."""
    lc = np.log(b.c.to_numpy(float))
    n = len(lc)
    P = np.full((n, PATH_L), np.nan)
    if n >= PATH_L:
        w = np.lib.stride_tricks.sliding_window_view(lc, PATH_L)
        sd = w.std(axis=1)
        z = (w - w.mean(axis=1, keepdims=True)) / np.where(sd > 1e-12, sd, np.nan)[:, None]
        P[PATH_L - 1:] = z
    return P


def analog_neighbours(F, P, valid, s):
    """Chosen neighbour bar indices for query s (library: valid, pctb<0, index <= s-9). Empty if < MIN_LIB library bars."""
    X = F[list(SCAL_COLS)].to_numpy(float)
    ok_row = valid & (F.pctb.to_numpy() < 0) & np.isfinite(X).all(axis=1) & np.isfinite(P).all(axis=1)
    lib = np.flatnonzero(ok_row[: s - 9 + 1])
    if len(lib) < MIN_LIB or not ok_row[s]:
        return np.empty(0, dtype=np.int64)
    mu, sd = X[lib].mean(axis=0), X[lib].std(axis=0)
    sd = np.where(sd > 1e-12, sd, 1.0)
    w = np.sqrt(NSCAL / PATH_L)
    A = np.hstack([(X[lib] - mu) / sd, P[lib] * w])
    q = np.hstack([(X[s] - mu) / sd, P[s] * w])
    d = np.sqrt(((A - q) ** 2).sum(axis=1))
    chosen = []
    for j in np.argsort(d):
        e = int(lib[j])
        if all(abs(e - c) >= SPACING for c in chosen):
            chosen.append(e)
            if len(chosen) == K:
                break
    return np.array(chosen if len(chosen) == K else [], dtype=np.int64)


def non_overlap(idx, h):
    """Keep events in time order, skipping one whose bar index is before the previous kept bar + h."""
    keep, last = [], -10 ** 9
    for j, s in enumerate(idx):
        if s >= last:
            keep.append(j)
            last = s + h
    return np.array(keep, dtype=int)


def draw_means(pool_vals, pool_strata, counts, n_draws, seed):
    """Per-draw mean of sum_j counts[j] values drawn with replacement from pool stratum j."""
    rng = np.random.default_rng(seed)
    tot = np.zeros(n_draws)
    n = int(np.sum(counts))
    for j, cj in enumerate(counts):
        if cj == 0:
            continue
        pv = pool_vals[(pool_strata == j) & np.isfinite(pool_vals)]
        if len(pv) == 0:
            continue
        tot += pv[rng.integers(0, len(pv), (n_draws, int(cj)))].sum(axis=1)
    return tot / max(n, 1)


def p_greater(real, draws):
    draws = np.asarray(draws, float)
    return float((1 + (draws >= real).sum()) / (1 + len(draws)))


def holm(ps):
    ps = np.asarray(ps, float)
    order = np.argsort(ps)
    m = len(ps)
    adj = np.empty(m)
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (m - rank) * ps[i])
        adj[i] = min(1.0, run)
    return adj


def month_bootstrap(vals, months, seed=41, n=2000):
    vals = np.asarray(vals, float)
    um, inv = np.unique(months, return_inverse=True)
    s, c = np.bincount(inv, weights=vals), np.bincount(inv)
    rng = np.random.default_rng(seed)
    means = np.empty(n)
    for i in range(n):
        pick = rng.integers(0, len(um), len(um))
        means[i] = s[pick].sum() / c[pick].sum()
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))
