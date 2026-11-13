"""Forced-move fade: event detection and trade simulation (PRE_REG.md). Pure functions."""
import bisect
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backtest"))
import fees  # noqa: E402

RT_FEE = fees.BINANCE_TAKER * 2
BAR = 900_000


def atr_prior(h, l, c, n=14):
    """Wilder ATR through bar i-1 at index i (never uses bar i)."""
    out = np.full(len(c), np.nan)
    tr = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    a = None
    for j in range(len(tr)):          # tr[j] belongs to bar j+1
        if a is None:
            if j + 1 == n:
                a = tr[:n].mean(); out[j + 2] = a
        else:
            a = (a * (n - 1) + tr[j]) / n
            if j + 2 < len(c):
                out[j + 2] = a
    return out


def roll_prior(x, w, fn):
    """fn over the w values before index i."""
    out = np.full(len(x), np.nan)
    if len(x) > w:
        v = np.lib.stride_tricks.sliding_window_view(x, w)[:-1]
        out[w:] = fn(v, axis=1)
    return out


def impulses(t, o, h, l, c, v, oi):
    """Return dict of arrays over bars: atr, med, impulse direction (+1 up, -1 down, 0), range_atr, volx, dOI (nan if missing)."""
    atr = atr_prior(h, l, c)
    med = roll_prior(v, 20, np.median)
    hh = roll_prior(h, 16, np.max); ll = roll_prior(l, 16, np.min)
    up = h > hh; dn = l < ll
    d = np.where(up & ~dn, 1, np.where(dn & ~up, -1, 0))
    rng = (h - l) / atr
    volx = v / med
    # OI at T and T+30m by timestamp
    oit = np.array([x[0] for x in oi]); oiv = np.array([x[1] for x in oi])
    a = np.full(len(t), np.nan); z = np.full(len(t), np.nan)
    for off, arr in ((0, a), (2 * BAR, z)):
        idx = np.searchsorted(oit, t + off)
        ok = idx < len(oit)
        ok[ok] = oit[idx[ok]] == (t + off)[ok]
        arr[ok] = oiv[idx[ok]]
    return dict(atr=atr, med=med, dir=d, rng=rng, volx=volx, doi=z / a - 1)


def fwd_sim(t, o, h, l, c, ft, fr, e, side, stop, target, hold):
    """Enter at close of bar e; walk bars e+1..e+hold. Returns fee-net return or None if data gap."""
    n = len(c)
    if e + hold >= n or t[e + hold] - t[e] != hold * BAR:
        return None
    p0 = c[e]
    px, k = None, hold
    for j in range(e + 1, e + hold + 1):
        if side > 0:
            if l[j] <= stop: px, k = min(stop, o[j]), j - e; break
            if target is not None and h[j] >= target: px, k = target, j - e; break
        else:
            if h[j] >= stop: px, k = max(stop, o[j]), j - e; break
            if target is not None and l[j] <= target: px, k = target, j - e; break
    if px is None:
        px = c[e + hold]
    t0, t1 = t[e] + BAR, t[e] + BAR * (1 + k)
    f = sum(fr[bisect.bisect_right(ft, t0):bisect.bisect_right(ft, t1)])
    return side * (px / p0 - 1) - RT_FEE - side * f
