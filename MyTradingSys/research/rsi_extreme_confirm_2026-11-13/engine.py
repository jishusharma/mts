"""Hourly RSI extreme + confirming candle: trade simulator (PRE_REG.md in this folder). Pure numpy, no I/O.

Short side is simulated as a long in negated prices (open', high' = -low, low' = -high, close' = -close), so there is one code path.
"""
import numpy as np

W = 24            # hard cap: bars held, entry bar included (OURS)
STOPS = ("atr025", "atr100", "pct1", "low_pct1")
EXITS = ("tgt2r", "rsi50", "time24")
ATR_K = {"atr025": 0.25, "atr100": 1.0}
PCT = 0.01        # OURS, operator "maybe 1%"
TARGET_R = 2.0    # OURS
HOUR_MS = 3600000


def wilder_atr(h, l, c, n=14):
    """Wilder ATR (RMA of true range); nan before index n."""
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    tr = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    a = tr[:n].mean()
    out[n] = a
    for i in range(n + 1, len(c)):
        a = (a * (n - 1) + tr[i - 1]) / n
        out[i] = a
    return out


def fund_cum(t, fts, frate):
    """G[k] = sum of funding with settlement ts <= t[k] (bar open). Charge for a hold from open[e] to open[x+1] is G[x+1]-G[e]."""
    if len(fts) == 0:
        return np.zeros(len(t))
    cum = np.concatenate([[0.0], np.cumsum(frate)])
    return cum[np.searchsorted(fts, t, side="right")]


def fwd_outcomes(side, stop, exit_, s, t, o, h, l, c, rsi, atr, G, taker):
    """Outcome of a trade for every setup bar index in `s`. side +1 long / -1 short.
    Entry at open of bar s+2; stop from the setup bar s; walks bars s+2 .. s+2+W-1 (these are outcomes, not signals).
    Returns dict of arrays aligned with s: valid, e, x, net_pct, net_r, mae_r, rpct.
    """
    s = np.asarray(s, dtype=int)
    d = float(side)
    n = len(c)
    e = s + 2
    valid = (e + W < n) & (s >= 0)
    e = np.where(valid, e, 0)
    ss = np.where(valid, s, 0)
    idx = np.minimum(e[:, None] + np.arange(W)[None, :], n - 1)
    # contiguous hourly bars only
    valid &= (t[np.minimum(e + W, n - 1)] - t[e] == W * HOUR_MS) & (t[e] - t[ss] == 2 * HOUR_MS)
    O = d * o[idx]
    C = d * c[idx]
    if side > 0:
        H, Lo = h[idx], l[idx]
    else:
        H, Lo = -l[idx], -h[idx]
    entry = d * o[e]
    if stop in ATR_K:
        P = (l[ss] - ATR_K[stop] * atr[ss]) if side > 0 else -(h[ss] + ATR_K[stop] * atr[ss])
    elif stop == "pct1":
        P = entry * (1 - PCT) if side > 0 else entry * (1 + PCT)
    elif stop == "low_pct1":
        P = (l[ss] * (1 - PCT)) if side > 0 else -(h[ss] * (1 + PCT))
    else:
        raise ValueError(stop)
    R = entry - P
    valid &= np.isfinite(R) & (R > 0)
    R = np.where(valid, R, 1.0)
    stop_hit = Lo <= P[:, None]
    ev = stop_hit.copy()
    tgt = entry + TARGET_R * R
    tgt_hit = np.zeros_like(stop_hit)
    if exit_ == "tgt2r":
        tgt_hit = (H >= tgt[:, None]) & ~stop_hit
        ev |= tgt_hit
    elif exit_ == "rsi50":
        ev |= (d * (rsi[idx] - 50.0) > 0) & ~stop_hit
    elif exit_ != "time24":
        raise ValueError(exit_)
    ev[:, W - 1] = True
    j = ev.argmax(axis=1)
    r = np.arange(len(s))
    sj, tj = stop_hit[r, j], tgt_hit[r, j]
    px = np.where(sj, np.minimum(O[r, j], P), np.where(tj, tgt, C[r, j]))
    x = e + j
    exit_real = d * px
    entry_real = o[e]
    fund = G[np.minimum(x + 1, n - 1)] - G[e]
    net_pct = d * (exit_real / entry_real - 1.0) - 2.0 * taker - d * fund
    rpct = R / np.abs(entry)
    net_r = net_pct / rpct
    held = np.arange(W)[None, :] <= j[:, None]
    mae_p = entry - np.where(held, Lo, np.inf).min(axis=1)
    mae_r = np.maximum(mae_p, 0.0) / R
    return {"valid": valid, "e": e, "x": x, "net_pct": net_pct, "net_r": net_r, "mae_r": mae_r, "rpct": rpct}


def confirm_mask(side, c, rsi, atr):
    """Setup bar s has its confirm bar s+1 closing beyond c[s] (long: above, short: below). No RSI condition. Index s."""
    n = len(c)
    m = np.zeros(n, bool)
    cc = c[1:] > c[:-1] if side > 0 else c[1:] < c[:-1]
    m[:-1] = cc
    m &= np.isfinite(rsi) & np.isfinite(atr)
    return m


def pick_one_position(e, x):
    """Greedy chronological (inputs sorted by e): take a signal only if its entry bar is after the previous taken trade's exit bar."""
    keep = []
    free = -1
    for k in range(len(e)):
        if e[k] > free:
            keep.append(k)
            free = x[k]
    return np.array(keep, dtype=int)
