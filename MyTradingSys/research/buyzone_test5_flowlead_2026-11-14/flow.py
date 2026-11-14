"""Test 5 engine: large-trade flow lead test. Rules are frozen in PRE_REG.md (read it first).
Pure functions on arrays; no file is read here except load_flow_dir, which takes a directory argument.
"""
import json
import os

import numpy as np
import pandas as pd

DAY = 86400000
FEES = {"12": 0.0012, "6": 0.0006}
NDRAW = 2000
NBOOT = 10000
SEED = 1114
BLOCK_DAYS = 7
MIN_Q = 10          # a quintile with fewer days marks the cell UNDERPOWERED


def split_mask(ts_ms, name):
    d = pd.to_datetime(np.asarray(ts_ms, dtype=np.int64), unit="ms")
    if name == "DEV":
        return np.asarray(d <= pd.Timestamp("2023-12-31"))
    if name == "VAL":
        return np.asarray(d >= pd.Timestamp("2024-01-01"))
    if name == "RECENT":
        return np.asarray(d >= pd.Timestamp("2025-07-01"))
    raise ValueError(name)


def load_flow_dir(path):
    """{date string: reduced flow dict} for one venue directory of fetch_flow.py output; unreadable files are skipped."""
    out = {}
    if not os.path.isdir(path):
        return out
    for fn in os.listdir(path):
        if not fn.endswith(".json"):
            continue
        try:
            out[fn[:-5]] = json.load(open(os.path.join(path, fn)))
        except Exception:
            continue
    return out


def net_flow_bp(spot, fut, k, venue):
    """Normalised net large flow in bp of whole-day notional for one day.
    spot, fut: per-day dicts (or None); k: '1' or '5'; venue: 'ALL', 'SPOT' or 'FUT'. NaN when the needed venue is missing."""
    def net(d):
        return d["buy" + k] - d["sell" + k]
    if venue == "SPOT":
        return 1e4 * net(spot) / spot["total"] if spot and spot["total"] > 0 else np.nan
    if venue == "FUT":
        return 1e4 * net(fut) / fut["total"] if fut and fut["total"] > 0 else np.nan
    if not spot or not fut or spot["total"] + fut["total"] <= 0:
        return np.nan
    return 1e4 * (net(spot) + net(fut)) / (spot["total"] + fut["total"])


def quintile_edges(dev_vals):
    v = np.asarray(dev_vals, float)
    v = v[~np.isnan(v)]
    return np.percentile(v, [20, 40, 60, 80])


def quint(vals, edges):
    """0 = lowest flow ... 4 = highest; computed from frozen edges only."""
    return np.searchsorted(np.asarray(edges), np.asarray(vals, float), side="right")


def spread_stats(F, ret, edges):
    """dict(n, cnt[5], mean[5] (return units), spread (return units, Q5 - Q1), underpowered)."""
    F = np.asarray(F, float)
    ret = np.asarray(ret, float)
    ok = ~np.isnan(F) & ~np.isnan(ret)
    q = quint(F[ok], edges)
    r = ret[ok]
    cnt = np.array([(q == i).sum() for i in range(5)])
    mean = np.array([r[q == i].mean() if cnt[i] else np.nan for i in range(5)])
    return {"n": int(ok.sum()), "cnt": cnt, "mean": mean, "spread": mean[4] - mean[0],
            "underpowered": bool((cnt < MIN_Q).any())}


def spearman(a, b):
    a = pd.Series(np.asarray(a, float))
    b = pd.Series(np.asarray(b, float))
    ok = a.notna() & b.notna()
    if ok.sum() < 5:
        return np.nan
    return float(a[ok].rank().corr(b[ok].rank()))


def fee_rows(st, fee):
    """Descriptive fee-net rows in bp: long top quintile, short bottom quintile, two-leg spread (2 x fee)."""
    m = st["mean"]
    return {"long_q5": (m[4] - fee) * 1e4, "short_q1": (-m[0] - fee) * 1e4, "two_leg": (m[4] - m[0] - 2 * fee) * 1e4}


def shuffle_placebo(F, ret, phase, edges, ndraw=NDRAW, seed=SEED):
    """Spreads (return units) of ndraw within-phase permutations of F against fixed returns and phases."""
    F = np.asarray(F, float)
    ret = np.asarray(ret, float)
    phase = np.asarray(phase)
    ok = ~np.isnan(F) & ~np.isnan(ret)
    F, ret, phase = F[ok], ret[ok], phase[ok]
    n = len(F)
    rng = np.random.default_rng(seed)
    P = np.empty((ndraw, n), dtype=np.int64)
    for ph in np.unique(phase):
        g = np.where(phase == ph)[0]
        P[:, g] = g[np.argsort(rng.random((ndraw, len(g))), axis=1)]
    q = quint(F[P], edges)          # (ndraw, n)
    out = np.empty(ndraw)
    for i in range(ndraw):
        hi = q[i] == 4
        lo = q[i] == 0
        out[i] = (ret[hi].mean() - ret[lo].mean()) if hi.any() and lo.any() else np.nan
    return out


def pct_of(actual, draws):
    d = np.asarray(draws, float)
    d = d[~np.isnan(d)]
    return float((d < actual).mean() * 100) if len(d) else np.nan


def block_ci(ts_ms, F, ret, edges, nboot=NBOOT, seed=SEED, block_days=BLOCK_DAYS):
    """95% CI of the Q5 - Q1 spread by resampling block_days-calendar-day blocks of flow days."""
    F = np.asarray(F, float)
    ret = np.asarray(ret, float)
    ts = np.asarray(ts_ms, dtype=np.int64)
    ok = ~np.isnan(F) & ~np.isnan(ret)
    F, ret, ts = F[ok], ret[ok], ts[ok]
    if len(F) < 20:
        return (np.nan, np.nan)
    q = quint(F, edges)
    blk = (ts // DAY) // block_days
    u, inv = np.unique(blk, return_inverse=True)
    nb = len(u)
    S = np.zeros((nb, 5))
    N = np.zeros((nb, 5))
    np.add.at(S, (inv, q), ret)
    np.add.at(N, (inv, q), 1.0)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, nb, size=(nboot, nb))
    s = S[idx].sum(1)
    c = N[idx].sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        m = s / c
    sp = m[:, 4] - m[:, 0]
    sp = sp[~np.isnan(sp)]
    if len(sp) == 0:
        return (np.nan, np.nan)
    return tuple(np.percentile(sp, [2.5, 97.5]))
