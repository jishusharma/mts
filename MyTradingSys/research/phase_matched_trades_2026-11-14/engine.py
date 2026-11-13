"""Phase-matched trade study engine (PRE_REG.md). Pure functions; data loading in run.py."""
import sys
import os
sys.dont_write_bytecode = True
import numpy as np

H1 = 3600000
DAY = 86400000
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "backtest")))
import fees  # noqa: E402  (single cost module)
COST = round(2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13, 10)   # 0.0012 round trip: 5 bp taker per side + 2 bp round-trip slippage (fees.py)
NONE, UP, DOWN, RANGE = 0, 1, 2, 3
PH = {UP: "UP", DOWN: "DOWN", RANGE: "RANGE"}


def wilder_rsi(c, n=14):
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    up, dn = np.maximum(d, 0), np.maximum(-d, 0)
    au, ad = up[:n].mean(), dn[:n].mean()
    out[n] = 100.0 if ad == 0 else 100 - 100 / (1 + au / ad)
    for i in range(n, len(d)):
        au = (au * (n - 1) + up[i]) / n
        ad = (ad * (n - 1) + dn[i]) / n
        out[i + 1] = 100.0 if ad == 0 else 100 - 100 / (1 + au / ad)
    return out


def ema(c, n=20):
    c = np.asarray(c, float)
    a = 2.0 / (n + 1)
    out = np.empty(len(c))
    out[0] = c[0]
    for i in range(1, len(c)):
        out[i] = a * c[i] + (1 - a) * out[i - 1]
    return out


def adx_di(h, l, c, n=14):
    """Wilder ADX, +DI, -DI (arrays; NaN until valid)."""
    h, l, c = (np.asarray(x, float) for x in (h, l, c))
    m = len(c)
    adx = np.full(m, np.nan)
    pdi = np.full(m, np.nan)
    mdi = np.full(m, np.nan)
    if m < 2 * n + 1:
        return adx, pdi, mdi
    tr = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    up = h[1:] - h[:-1]
    dn = l[:-1] - l[1:]
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    st, sp, sm = tr[:n].sum(), pdm[:n].sum(), mdm[:n].sum()
    dx = []
    for i in range(n - 1, len(tr)):
        if i > n - 1:
            st = st - st / n + tr[i]
            sp = sp - sp / n + pdm[i]
            sm = sm - sm / n + mdm[i]
        p, q = 100 * sp / st, 100 * sm / st
        j = i + 1
        pdi[j], mdi[j] = p, q
        dx.append(0.0 if p + q == 0 else 100 * abs(p - q) / (p + q))
        k = len(dx)
        if k == n:
            adx[j] = np.mean(dx)
        elif k > n:
            adx[j] = (adx[j - 1] * (n - 1) + dx[-1]) / n
    return adx, pdi, mdi


def daily_phase(dh, dl, dc):
    """Label per daily bar d, decided at the close of d using bars <= d only."""
    dc = np.asarray(dc, float)
    m = len(dc)
    lab = np.zeros(m, int)
    adx, pdi, mdi = adx_di(dh, dl, dc)
    ma = np.full(m, np.nan)
    cs = np.cumsum(np.insert(dc, 0, 0.0))
    ma[19:] = (cs[20:] - cs[:-20]) / 20
    for d in range(m):
        if d < 5 or np.isnan(adx[d]) or np.isnan(ma[d]) or np.isnan(ma[d - 5]):
            continue
        if dc[d] > ma[d] and ma[d] > ma[d - 5] and adx[d] >= 20 and pdi[d] > mdi[d]:
            lab[d] = UP
        elif dc[d] < ma[d] and ma[d] < ma[d - 5] and adx[d] >= 20 and mdi[d] > pdi[d]:
            lab[d] = DOWN
        else:
            lab[d] = RANGE
    return lab


def bar_day_index(bar_t, dt, lag=1):
    """Daily index of the day (bar day - lag); -1 if missing. lag=1 is the no-look-ahead rule (previous completed day).
    lag=0 is the deliberately WRONG version (same day's close used for bars earlier that day)."""
    bar_t = np.asarray(bar_t, np.int64)
    key = bar_t - bar_t % DAY - lag * DAY
    idx = np.searchsorted(dt, key)
    ok = (idx < len(dt)) & (dt[np.minimum(idx, len(dt) - 1)] == key)
    return np.where(ok, idx, -1)


def bar_phase(bar_t, dt, lab, lag=1):
    idx = bar_day_index(bar_t, dt, lag)
    return np.where(idx >= 0, lab[np.maximum(idx, 0)], NONE)


def swing_high_before(h, s, n_back=48, k=3):
    """Most recent confirmed pivot high (higher than k bars each side), pivot p with p+k <= s. Price or nan."""
    for p in range(s - k, max(s - n_back, k) - 1, -1):
        v = h[p]
        if v > h[p - k:p].max() and v > h[p + 1:p + k + 1].max():
            return v
    return np.nan


def signals(t, o, h, l, c, dt, dh, dl, lag=1):
    """Return dict type -> list of (S, side, stop, aux). Entry bar is S+1. 1h bar arrays; dt/dh/dl daily."""
    n = len(c)
    rsi = wilder_rsi(c)
    e = ema(c)
    di = bar_day_index(t, dt, lag)
    ok = di >= 0
    pdh = np.where(ok, dh[np.maximum(di, 0)], np.nan)
    pdl = np.where(ok, dl[np.maximum(di, 0)], np.nan)
    rh = np.full(len(dt), np.nan)
    rl = np.full(len(dt), np.nan)
    for k in range(19, len(dt)):
        rh[k] = dh[k - 19:k + 1].max()
        rl[k] = dl[k - 19:k + 1].min()
    RH = np.where(ok, rh[np.maximum(di, 0)], np.nan)
    RL = np.where(ok, rl[np.maximum(di, 0)], np.nan)
    out = {"T1": [], "T2": [], "T3": [], "T4": []}
    for s in range(100, n - 2):
        if not ok[s] or np.isnan(pdh[s]) or np.isnan(rsi[s]):
            continue
        if rsi[s] >= 60 and (h[s] >= pdh[s] or (c[s - 1] < e[s - 1] and h[s] >= e[s])):
            out["T1"].append((s, -1, h[s - 5:s + 1].max() * 1.001, pdl[s]))
        if rsi[s] <= 40 and (l[s] <= pdl[s] or (c[s - 1] > e[s - 1] and l[s] <= e[s])):
            out["T2"].append((s, 1, l[s - 5:s + 1].min() * 0.999, pdh[s]))
        if not np.isnan(RH[s]) and (RH[s] - RL[s]) / RL[s] >= 0.04:
            body = abs(c[s] - o[s])
            mid = (RH[s] + RL[s]) / 2
            if h[s] >= 0.99 * RH[s] and c[s] < o[s] and (h[s] - o[s]) >= body:
                out["T3"].append((s, -1, RH[s] * 1.005, mid))
            elif l[s] <= 1.01 * RL[s] and c[s] > o[s] and (o[s] - l[s]) >= body:
                out["T3"].append((s, 1, RL[s] * 0.995, mid))
        if c[s] < pdl[s] and c[s - 1] >= pdl[s]:
            sh = swing_high_before(h, s)
            if not np.isnan(sh) and sh > c[s]:
                out["T4"].append((s, -1, sh, None))
    return out


def simulate(o, h, l, c, s, side, stop, tgt_kind, tgt_val, maxbars):
    """Enter at open[s+1]. tgt_kind 'R' (tgt_val = R multiple) or 'P' (tgt_val = price).
    Returns (exit_idx, exit_price, entry) or None (skipped)."""
    e = s + 1
    if e + maxbars > len(c):
        return None
    entry = o[e]
    if (side == 1 and entry <= stop) or (side == -1 and entry >= stop):
        return None
    R = abs(entry - stop)
    if tgt_kind == "R":
        tgt = entry + side * tgt_val * R
    else:
        tgt = tgt_val
        if tgt is None or np.isnan(tgt) or (side == 1 and tgt <= entry) or (side == -1 and tgt >= entry):
            return None
    for j in range(e, e + maxbars):
        if side == -1:
            if h[j] >= stop:
                return j, (max(stop, o[j]) if j > e else stop), entry
            if l[j] <= tgt:
                return j, tgt, entry
        else:
            if l[j] <= stop:
                return j, (min(stop, o[j]) if j > e else stop), entry
            if h[j] >= tgt:
                return j, tgt, entry
    j = e + maxbars - 1
    return j, c[j], entry


def funding_between(ft, cf, t0, t1):
    """Sum of funding rates with t0 < ts <= t1 (cf = cumulative with leading 0)."""
    a = np.searchsorted(ft, t0, side="right")
    b = np.searchsorted(ft, t1, side="right")
    return cf[b] - cf[a]


def net_r(side, entry, exitp, stop, fund):
    net_pct = side * (exitp / entry - 1) - COST - side * fund
    R = abs(entry - stop) / entry
    return net_pct, net_pct / R
