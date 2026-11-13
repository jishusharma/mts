"""Core functions for the NK RSI / Hilega Milega crypto port (see PRE_REG.md). No outcome logic beyond fwd_* helpers."""
import numpy as np, pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

def rsi_wilder(close, n):
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    rs = up / dn
    return 100 - 100 / (1 + rs)

def wma(s, n):
    w = np.arange(1, n + 1, dtype=float); w /= w.sum()
    v = s.values
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = (sliding_window_view(v, n) * w).sum(axis=1)
    return pd.Series(out, index=s.index)

def hilega_state(close):
    """OURS-EXTERNAL: RSI(9), fast EMA(3) of RSI, slow WMA(21) of RSI. +1 BUY, -1 SELL, 0 neutral/unknown."""
    r = rsi_wilder(close, 9)
    fast = r.ewm(span=3, adjust=False).mean()
    slow = wma(r, 21)
    st = pd.Series(0, index=close.index, dtype=int)
    st[(fast > slow) & (r > 50)] = 1
    st[(fast < slow) & (r < 50)] = -1
    st[slow.isna()] = 0
    return st

def resample(df5, rule, expected):
    g = df5.resample(rule, label='left', closed='left')
    o = g.agg({'o': 'first', 'h': 'max', 'l': 'min', 'c': 'last', 'v': 'sum'})
    cnt = g['c'].count()
    return o[cnt >= expected].dropna()

def load5(path):
    df = pd.read_csv(path)
    df.index = pd.to_datetime(df['t'], unit='ms')
    df = df.drop(columns='t').astype(float)
    return df[~df.index.duplicated()].sort_index()

def fwd_ret(c, ei, xi):
    """Return exit/entry-1 for index arrays ei, xi into price array c (NaN when out of range or missing)."""
    n = len(c)
    ok = (ei >= 0) & (xi < n) & (ei < n)
    r = np.full(len(ei), np.nan)
    e = c[np.clip(ei, 0, n - 1)]; x = c[np.clip(xi, 0, n - 1)]
    r[ok] = x[ok] / e[ok] - 1
    return r

def split_of(ts):
    if ts < pd.Timestamp('2024-07-01'): return 'DEV'
    if ts < pd.Timestamp('2025-07-01'): return 'VALIDATION'
    return 'RECENT'

def bh(pvals, q=0.10):
    p = np.asarray(pvals, float); m = len(p)
    order = np.argsort(p); passed = np.zeros(m, bool)
    thr = q * (np.arange(1, m + 1) / m)
    k = np.where(p[order] <= thr)[0]
    if len(k): passed[order[:k.max() + 1]] = True
    return passed

def week_bootstrap(rets, weeks, draws=4000, seed=1):
    rets = np.asarray(rets, float); weeks = np.asarray(weeks)
    u, inv = np.unique(weeks, return_inverse=True)
    S = np.bincount(inv, rets, minlength=len(u)); C = np.bincount(inv, minlength=len(u)).astype(float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(u), (draws, len(u)))
    m = S[idx].sum(1) / C[idx].sum(1)
    return np.percentile(m, [2.5, 97.5]), float((m <= 0).mean())
