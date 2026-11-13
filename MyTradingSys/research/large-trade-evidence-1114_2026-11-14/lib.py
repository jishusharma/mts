"""Pure functions for the large-trade evidence study (PRE_REG.md fixes every definition before the first outcome run).
All thresholds and windows are OURS unless the PRE_REG says SOURCED. No orders, no account data."""
import numpy as np
import pandas as pd

M15 = 900_000
H1 = 3_600_000
DAY = 86_400_000
FEE = 0.0012           # round-trip fee, 12 bp (operator fee-net number)
ERA_B_START = 1733097600000  # 2024-12-02 00:00Z = first row of our recorded F:/MTS/data/orderflow_1m


# ------------------------------------------------------------------ phase (daily, from the PRIOR close)
def adx_di(high, low, close, n=14):
    """Wilder ADX/DI, same maths as MyTradingSys/backtest/layers/adx/adx.py (FORMULAS.md section 30); numpy vectors in/out, NaN where undefined."""
    from MyTradingSys.backtest.layers.adx.adx import adx_di as core
    dp, dm, ax = core(list(map(float, high)), list(map(float, low)), list(map(float, close)), n)
    f = lambda v: np.array([np.nan if x is None else x for x in v], float)
    return f(dp), f(dm), f(ax)


def phase_table(daily):
    """daily: DataFrame t(ms), o,h,l,c. Returns DataFrame indexed by UTC day number D (t//DAY) giving phase computed with bars through D-1 only.
    UP = ADX14>=20 & DI+>DI- & SMA20 rising; DOWN = ADX14>=20 & DI->DI+ & SMA20 falling; else RANGE.
    dd = 1 - close[D-1] / max(high up to D-1); ddb: 0 (<10%), 1 (10-25%), 2 (25-40%), 3 (>=40%)."""
    d = daily.sort_values("t").reset_index(drop=True)
    dip, dim, adx = adx_di(d.h.values, d.l.values, d.c.values, 14)
    sma = d.c.rolling(20).mean().values
    slope = np.r_[np.nan, np.diff(sma)]
    ath = d.h.cummax().values
    dd = 1.0 - d.c.values / ath
    ph = np.full(len(d), "NA", dtype=object)
    ok = ~np.isnan(adx) & ~np.isnan(slope)
    up = ok & (adx >= 20) & (dip > dim) & (slope > 0)
    dn = ok & (adx >= 20) & (dim > dip) & (slope < 0)
    ph[ok] = "RANGE"; ph[up] = "UP"; ph[dn] = "DOWN"
    ddb = np.where(dd < 0.10, 0, np.where(dd < 0.25, 1, np.where(dd < 0.40, 2, 3)))
    day = (d.t.values // DAY).astype(np.int64)
    # signal known after close of day x applies to day x+1
    out = pd.DataFrame({"day": day + 1, "phase": ph, "ddb": ddb, "adx": adx, "dip": dip, "dim": dim, "dd": dd, "close": d.c.values})
    return out.set_index("day")


# ------------------------------------------------------------------ grids
def to_grid15(df1m, ld_cols):
    """1m frame (t,o,h,l,c + ld columns in USD) -> dict of arrays on a complete 15m grid. NaN price where a 15m bucket has no trades."""
    b = df1m.t.values // M15
    g = df1m.assign(b=b).groupby("b", sort=True)
    a = g.agg(o=("o", "first"), h=("h", "max"), l=("l", "min"), c=("c", "last"), **{k: (k, "sum") for k in ld_cols})
    lo, hi = a.index.min(), a.index.max()
    a = a.reindex(np.arange(lo, hi + 1))
    out = {"t0": int(lo) * M15}
    for k in ["o", "h", "l", "c"]:
        out[k] = a[k].values.astype(float)
    for k in ld_cols:
        out[k] = np.nan_to_num(a[k].values.astype(float))
    out["n"] = len(a)
    return out


def tdec(G, idx):
    """Decision time (ms) at the close of 15m bucket idx."""
    return G["t0"] + (np.asarray(idx) + 1) * M15


def hour_idx(G):
    """Indices of 15m buckets that close on a full UTC hour."""
    i = np.arange(G["n"])
    return i[((G["t0"] + (i + 1) * M15) % H1) == 0]


def trailing(x, idx, k):
    """Sum of x over the k 15m buckets ending at idx (inclusive)."""
    cs = np.r_[0.0, np.cumsum(x)]
    lo = np.clip(idx - k + 1, 0, None)
    return cs[idx + 1] - cs[lo]


def hourly_bars(G, hi):
    """1h OHLC for the hours closing at 15m bucket hi (4 buckets ending at hi)."""
    o = np.full(len(hi), np.nan); h = o.copy(); l = o.copy(); c = o.copy()
    for j, i in enumerate(hi):
        if i < 3:
            continue
        sl = slice(i - 3, i + 1)
        if np.isnan(G["c"][sl]).any():
            continue
        o[j] = G["o"][i - 3]; h[j] = G["h"][sl].max(); l[j] = G["l"][sl].min(); c[j] = G["c"][i]
    return o, h, l, c


def atr_sma(h, l, c, n=14):
    """Core ATR (plain SMA of true range, FORMULAS.md section 12), value at each bar inclusive."""
    pc = np.r_[np.nan, c[:-1]]
    tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)])
    return pd.Series(tr).rolling(n).mean().values


def zscore_hourly(x, win=720, minp=480):
    """x / std of the PRIOR `win` hourly values (causal, excludes the current)."""
    s = pd.Series(x).rolling(win, min_periods=minp).std().shift(1).values
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(s > 0, x / s, np.nan)


def fwd_ret(G, idx, hours):
    """Forward simple return from close of bucket idx to close hours later."""
    k = 4 * hours
    j = idx + k
    ok = j < G["n"]
    r = np.full(len(idx), np.nan)
    c0 = G["c"][idx]
    c1 = np.where(ok, G["c"][np.minimum(j, G["n"] - 1)], np.nan)
    r[:] = c1 / c0 - 1.0
    return r


# ------------------------------------------------------------------ cluster bootstrap on cluster sums
class Boot:
    """Cluster bootstrap with a cached multinomial weight matrix per number of clusters (seed fixed in PRE_REG)."""
    def __init__(self, B=20000, seed=1114):
        self.B, self.seed, self.cache = B, seed, {}

    def weights(self, K):
        if K not in self.cache:
            if len(self.cache) >= 3:
                self.cache.pop(next(iter(self.cache)))
            rng = np.random.default_rng(self.seed + K)
            self.cache[K] = rng.multinomial(K, np.full(K, 1.0 / K), size=self.B).astype(np.float32)
        return self.cache[K]


def _p(b, obs):
    b = b[~np.isnan(b)]
    if len(b) == 0:
        return np.nan
    return max(2 * min((b <= 0).mean(), (b >= 0).mean()), 1.0 / len(b))


def corr_cluster(x, y, cl, boot):
    """Rank (Spearman) correlation with cluster-bootstrap CI/p, ranks fixed from the full sample."""
    m = ~(np.isnan(x) | np.isnan(y))
    x, y, cl = x[m], y[m], cl[m]
    n = len(x)
    if n < 30:
        return dict(n=n, ic=np.nan, lo=np.nan, hi=np.nan, p=np.nan, K=0)
    rx = pd.Series(x).rank().values; ry = pd.Series(y).rank().values
    u, inv = np.unique(cl, return_inverse=True)
    K = len(u)
    S = np.stack([np.bincount(inv, w, K) for w in (np.ones(n), rx, ry, rx * rx, ry * ry, rx * ry)], 1)
    def corr(S_):
        N, sx, sy, sxx, syy, sxy = S_
        cov = sxy / N - sx * sy / N / N
        vx = sxx / N - (sx / N) ** 2; vy = syy / N - (sy / N) ** 2
        return cov / np.sqrt(vx * vy)
    ic = float(corr(S.sum(0)))
    W = boot.weights(K)
    T = W @ S.astype(np.float32)
    with np.errstate(invalid="ignore", divide="ignore"):
        b = corr(T.T.astype(np.float64))
    return dict(n=n, ic=ic, lo=float(np.nanquantile(b, 0.025)), hi=float(np.nanquantile(b, 0.975)), p=float(_p(b, ic)), K=K)


def diff_cluster(v, a, b_, cl, boot):
    """mean(v[a]) - mean(v[b]) with cluster-bootstrap CI/p. a, b_ boolean masks."""
    m = ~np.isnan(v)
    v, a, b_, cl = v[m], a[m], b_[m], cl[m]
    na, nb = int(a.sum()), int(b_.sum())
    if na < 5 or nb < 5:
        return dict(na=na, nb=nb, ma=np.nan, mb=np.nan, d=np.nan, lo=np.nan, hi=np.nan, p=np.nan, K=0)
    u, inv = np.unique(cl, return_inverse=True)
    K = len(u)
    S = np.stack([np.bincount(inv, a.astype(float), K), np.bincount(inv, v * a, K),
                  np.bincount(inv, b_.astype(float), K), np.bincount(inv, v * b_, K)], 1)
    tot = S.sum(0)
    d = tot[1] / tot[0] - tot[3] / tot[2]
    T = boot.weights(K) @ S.astype(np.float32)
    with np.errstate(invalid="ignore", divide="ignore"):
        bs = T[:, 1] / T[:, 0] - T[:, 3] / T[:, 2]
    return dict(na=na, nb=nb, ma=float(tot[1] / tot[0]), mb=float(tot[3] / tot[2]), d=float(d),
                lo=float(np.nanquantile(bs, 0.025)), hi=float(np.nanquantile(bs, 0.975)), p=float(_p(bs, d)), K=K)


def mean_cluster(v, cl, boot):
    m = ~np.isnan(v)
    v, cl = v[m], cl[m]
    if len(v) < 5:
        return dict(n=len(v), mean=np.nan, lo=np.nan, hi=np.nan)
    u, inv = np.unique(cl, return_inverse=True)
    K = len(u)
    S = np.stack([np.bincount(inv, None, K).astype(float), np.bincount(inv, v, K)], 1)
    T = boot.weights(K) @ S.astype(np.float32)
    bs = T[:, 1] / T[:, 0]
    return dict(n=len(v), mean=float(v.mean()), lo=float(np.quantile(bs, 0.025)), hi=float(np.quantile(bs, 0.975)))


def holm(ps, alpha=0.05):
    """Holm step-down: returns list of bool pass flags in input order (NaN p never passes)."""
    idx = [i for i, p in enumerate(ps) if not np.isnan(p)]
    order = sorted(idx, key=lambda i: ps[i])
    ok = [False] * len(ps)
    m = len(order)
    for r, i in enumerate(order):
        if ps[i] <= alpha / (m - r):
            ok[i] = True
        else:
            break
    return ok


# ------------------------------------------------------------------ test 2: first touch of +/-1 ATR within 24 h
def first_touch(G, idx, atr_price, horizon_buckets=96):
    """From close of bucket idx: +1 if close+ATR is touched first, -1 if close-ATR first, 0 none or both in the same 15m bucket, NaN if path missing."""
    out = np.full(len(idx), np.nan)
    for q, (i, a) in enumerate(zip(idx, atr_price)):
        if np.isnan(a) or i + horizon_buckets >= G["n"]:
            continue
        c0 = G["c"][i]
        hh = G["h"][i + 1:i + 1 + horizon_buckets]; ll = G["l"][i + 1:i + 1 + horizon_buckets]
        if np.isnan(hh).any():
            continue
        up = np.nonzero(hh >= c0 + a)[0]; dn = np.nonzero(ll <= c0 - a)[0]
        u = up[0] if len(up) else 10 ** 9; d = dn[0] if len(dn) else 10 ** 9
        out[q] = 0 if u == d else (1 if u < d else -1)
    return out


# ------------------------------------------------------------------ test 3: divergence trigger and trade simulation
def simulate_entries(G, hi, atr_h, side, hold_buckets=96):
    """Entry at the open of the 15m bucket after the hourly close idx. Stop = max(0.6 ATR, 0.5 %) from entry, checked on 15m high/low from the
    entry bucket on, filled at the stop; time exit at the close of the 96th bucket (24 h). Returns net return (after FEE), exit bucket index, stop pct."""
    n = len(hi)
    net = np.full(n, np.nan); ex = np.full(n, -1); sp = np.full(n, np.nan)
    for q in range(n):
        i = hi[q]
        j0 = i + 1
        if j0 + hold_buckets - 1 >= G["n"] or np.isnan(atr_h[q]):
            continue
        e = G["o"][j0]
        hh = G["h"][j0:j0 + hold_buckets]; ll = G["l"][j0:j0 + hold_buckets]
        if np.isnan(e) or np.isnan(hh).any():
            continue
        s = max(0.6 * atr_h[q] / e, 0.005)
        sp[q] = s
        if side > 0:
            hit = np.nonzero(ll <= e * (1 - s))[0]
        else:
            hit = np.nonzero(hh >= e * (1 + s))[0]
        if len(hit):
            r = -s; ex[q] = j0 + hit[0]
        else:
            cend = G["c"][j0 + hold_buckets - 1]
            r = side * (cend / e - 1.0); ex[q] = j0 + hold_buckets - 1
        net[q] = r - FEE
    return net, ex, sp


def divergence_flags(hl, hh, ld, win=12, fresh=3):
    """Hourly arrays. Bull: lowest low of the last `win` hours is below the lowest low of the `win` hours before it, made within the latest `fresh`
    hours, and large-delta over the last window > over the earlier window. Bear mirrors. Returns (bull, bear) boolean arrays."""
    n = len(hl)
    bull = np.zeros(n, bool); bear = np.zeros(n, bool)
    cs = np.r_[0.0, np.cumsum(ld)]
    for k in range(2 * win - 1, n):
        a = slice(k - win + 1, k + 1); b = slice(k - 2 * win + 1, k - win + 1)
        la, lb = hl[a], hl[b]; ha, hb = hh[a], hh[b]
        if np.isnan(la).any() or np.isnan(lb).any() or np.isnan(ha).any() or np.isnan(hb).any():
            continue
        lda = cs[k + 1] - cs[k - win + 1]; ldb = cs[k - win + 1] - cs[k - 2 * win + 1]
        if la.min() < lb.min() and np.argmin(la) >= win - fresh and lda > ldb:
            bull[k] = True
        if ha.max() > hb.max() and np.argmax(ha) >= win - fresh and lda < ldb:
            bear[k] = True
    return bull, bear


def one_at_a_time(entry_idx, exit_idx):
    """Chronological non-overlap: skip a signal whose entry is before the previous kept exit. Returns kept positions."""
    keep = []; last = -1
    for q in np.argsort(entry_idx):
        if entry_idx[q] > last and exit_idx[q] >= 0:
            keep.append(q); last = exit_idx[q]
    return np.array(keep, dtype=int)


def placebo_p(pool_net, n, obs_mean, draws=5000, seed=1114):
    """P(mean of n random same-phase entries >= observed mean)."""
    pool_net = pool_net[~np.isnan(pool_net)]
    if len(pool_net) < 10 or n < 1:
        return np.nan, np.nan
    rng = np.random.default_rng(seed + n)
    m = pool_net[rng.integers(0, len(pool_net), size=(draws, n))].mean(1)
    return float((m >= obs_mean).mean()), float(m.mean())
