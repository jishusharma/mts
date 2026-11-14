"""nk2 pivot S/R reclaim study. See PRE_REG.md. STUDY_BUG=1 env = deliberate look-ahead (pivots/phase from the SAME day)."""
import os, sys, json
import numpy as np

CACHE = r"F:\MTS\data_cache\binance"
SYMS = "BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()
DAY = 86400000
SPLIT = 1704067200000  # 2024-01-01 UTC
BUG = bool(os.environ.get("STUDY_BUG"))
FEE_TAKER, FEE_MAKER = 0.0012, 0.0006


def load15(sym):
    return np.load(os.path.join(CACHE, sym + "USDT_15m.npz"))["a"]


def resample(a, k):
    """aggregate k consecutive 15m bars aligned to UTC (k=4 -> 1h, 96 -> 1d). drops incomplete groups."""
    g = a[:, 0] // (900000 * k)
    idx = np.flatnonzero(np.r_[True, g[1:] != g[:-1]])
    ends = np.r_[idx[1:], len(a)]
    keep = (ends - idx) == k
    idx, ends = idx[keep], ends[keep]
    out = np.empty((len(idx), 6))
    for j, (s, e) in enumerate(zip(idx, ends)):
        out[j] = [a[s, 0], a[s, 1], a[s:e, 2].max(), a[s:e, 3].min(), a[e - 1, 4], a[s:e, 5].sum()]
    return out


def pivots(h, l, c):
    p = (h + l + c) / 3.0
    return dict(P=p, R1=2 * p - l, S1=2 * p - h, R2=p + (h - l), S2=p - (h - l), R3=h + 2 * (p - l), S3=l - 2 * (h - p))


def wilder(x, n):
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    out[n - 1] = x[:n].mean()
    for i in range(n, len(x)):
        out[i] = (out[i - 1] * (n - 1) + x[i]) / n
    return out


def daily_phase(d):
    """d: daily bars [t,o,h,l,c,v]. returns phase array aligned to d: phase known at the CLOSE of bar i (applies to day i+1).
    0=RANGE 1=UP -1=DOWN"""
    h, l, c = d[:, 2], d[:, 3], d[:, 4]
    n = len(d)
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    up = np.r_[0, np.maximum(h[1:] - h[:-1], 0)]
    dn = np.r_[0, np.maximum(l[:-1] - l[1:], 0)]
    upm = np.where(up > dn, up, 0.0)
    dnm = np.where(dn > up, dn, 0.0)
    atr, su, sd = wilder(tr, 14), wilder(upm, 14), wilder(dnm, 14)
    with np.errstate(all="ignore"):
        dip, dim = 100 * su / atr, 100 * sd / atr
        dx = 100 * abs(dip - dim) / (dip + dim)
    dx0 = np.nan_to_num(dx[13:])  # dx valid from index 13
    adx = np.full(n, np.nan)
    if len(dx0) >= 14:
        a = wilder(dx0, 14)
        adx[13:] = a
    ma = np.full(n, np.nan)
    cs = np.cumsum(np.r_[0, c])
    ma[19:] = (cs[20:] - cs[:-20]) / 20
    slope = np.full(n, np.nan)
    slope[5:] = ma[5:] - ma[:-5]
    ph = np.zeros(n, dtype=int)
    ph[(adx >= 20) & (dip > dim) & (slope > 0)] = 1
    ph[(adx >= 20) & (dim > dip) & (slope < 0)] = -1
    return ph


def day_tables(a15):
    """per 15m bar: pivots dict arrays + phase, using previous UTC day (BUG: same day)."""
    d = resample(a15, 96)
    ph = daily_phase(d)
    dt = d[:, 0].astype(np.int64)
    day = (a15[:, 0] // DAY).astype(np.int64) * DAY
    pos = np.searchsorted(dt, day)  # index of the bar's own day in d (if complete)
    ok = (pos < len(dt)) & (dt[np.minimum(pos, len(dt) - 1)] == day)
    src = pos if BUG else pos - 1  # previous day
    valid = (src >= 0) & (src < len(dt))
    srcc = np.clip(src, 0, len(dt) - 1)
    # for a day without a complete own-day bar the previous day must exist exactly yesterday
    valid &= dt[srcc] == (day if BUG else day - DAY)
    lv = pivots(d[srcc, 2], d[srcc, 3], d[srcc, 4])
    phase = ph[srcc]
    return lv, phase, valid


def atr14(a):
    h, l, c = a[:, 2], a[:, 3], a[:, 4]
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    out = np.full(len(a), np.nan)
    cs = np.cumsum(np.r_[0, tr])
    out[13:] = (cs[14:] - cs[:-14]) / 14  # simple 14-bar mean (known at bar close)
    return out


LEVELS = ["S3", "S2", "S1", "P", "R1", "R2", "R3"]


def prep(sym, tf):
    """returns dict for signal tf: bars a (tf), levels per bar, phase per bar, valid per bar, atr."""
    a15 = load15(sym)
    lv15, ph15, v15 = day_tables(a15)
    if tf == 1:
        a, lv, ph, v = a15, lv15, ph15, v15
    else:
        # take the table at the first 15m bar of each tf bar (same UTC day anyway)
        g = a15[:, 0] // (900000 * tf)
        idx = np.flatnonzero(np.r_[True, g[1:] != g[:-1]])
        ends = np.r_[idx[1:], len(a15)]
        keep = (ends - idx) == tf
        a = resample(a15, tf)
        idx = idx[keep]
        lv = {k: x[idx] for k, x in lv15.items()}
        ph, v = ph15[idx], v15[idx]
    return dict(a=a, lv=lv, ph=ph, valid=v, atr=atr14(a), sym=sym)


def simulate(D, i, side, bars_max):
    """signal at bar i close; enter next open. returns (R_gross, stop_dist_frac, exit_idx, rr_ok) or None."""
    a = D["a"]
    n = len(a)
    if i + 2 >= n or np.isnan(D["atr"][i]):
        return None
    e = a[i + 1, 1]
    if side > 0:
        swing = a[max(0, i - 5):i + 1, 3].min()
        dist = max(e - swing, 0.6 * D["atr"][i], 0.005 * e)
        stop = e - dist
        cands = [D["lv"][k][i] for k in LEVELS if D["lv"][k][i] > e]
        if not cands:
            return None
        tgt = min(cands)
        if tgt - e < dist:
            return None
    else:
        swing = a[max(0, i - 5):i + 1, 2].max()
        dist = max(swing - e, 0.6 * D["atr"][i], 0.005 * e)
        stop = e + dist
        cands = [D["lv"][k][i] for k in LEVELS if D["lv"][k][i] < e]
        if not cands:
            return None
        tgt = max(cands)
        if e - tgt < dist:
            return None
    j1 = min(n, i + 2 + bars_max)
    seg = a[i + 1:j1]
    if side > 0:
        hs, ts = seg[:, 4] <= stop, seg[:, 2] >= tgt
    else:
        hs, ts = seg[:, 4] >= stop, seg[:, 3] <= tgt
    fs = np.argmax(hs) if hs.any() else 10**9
    ft = np.argmax(ts) if ts.any() else 10**9
    if fs == 10**9 and ft == 10**9:
        k = len(seg) - 1
        px = seg[k, 4]
    elif fs <= ft:  # stop first or same bar -> stop wins
        k, px = fs, seg[fs, 4]
    else:
        k, px = ft, tgt
    r = side * (px - e) / dist
    return r, dist / e, i + 1 + k, e


def signals(D, side, level, tf):
    """bar indices i where trigger closes (level X): long prev close < X <= close; short prev close > Y >= close."""
    a, lv = D["a"], D["lv"][level]
    c = a[:, 4]
    cond = np.zeros(len(a), bool)
    if side > 0:
        cond[1:] = (c[:-1] < lv[1:]) & (c[1:] >= lv[1:])
        # prev close must be below the SAME day level
        cond[1:] &= c[:-1] < lv[1:]
    else:
        cond[1:] = (c[:-1] > lv[1:]) & (c[1:] <= lv[1:])
    return np.flatnonzero(cond & D["valid"])


def run_trades(D, side, level, tf, phases, bars_max):
    """sequential one-position-at-a-time trades. returns list of (entry_ms, exit_idx, R, distfrac, phase, entry_px)."""
    out, busy = [], -1
    a = D["a"]
    for i in signals(D, side, level, tf):
        if i <= busy or D["ph"][i] not in phases:
            continue
        s = simulate(D, i, side, bars_max)
        if s is None:
            continue
        r, df, xi, e = s
        out.append((a[i + 1, 0], r, df, int(D["ph"][i])))
        busy = xi
    return out


def net(R, df, fee):
    return R - fee / df


def bh(ps, q=0.05):
    m = len(ps)
    order = np.argsort(ps)
    ok = np.zeros(m, bool)
    thr = -1
    for rank, j in enumerate(order, 1):
        if ps[j] <= q * rank / m:
            thr = rank
    for rank, j in enumerate(order, 1):
        if rank <= thr:
            ok[j] = True
    return ok
