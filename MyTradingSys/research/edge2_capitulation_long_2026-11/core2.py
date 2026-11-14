"""Pure vectorised mechanics for edge2_capitulation_long_2026-11 (see PRE_REG.md)."""
import sys
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import fees  # noqa: E402

RT_FEE = 2 * fees.BINANCE_TAKER
K_STOP = 0.25


def capitulation(h, l, c, a):
    """Reading e (long side): range >= 3 x ATR[i-1] and close in the lower 25% of the bar's range."""
    n = len(c)
    rng_ = h - l
    ok = np.zeros(n, bool)
    ok[1:] = (a[:-1] > 0) & np.isfinite(a[:-1]) & (rng_[1:] > 0)
    big = np.zeros(n, bool)
    big[1:] = rng_[1:] >= 3 * a[:-1]
    with np.errstate(invalid="ignore", divide="ignore"):
        pos = (c - l) / rng_
    return ok & big & (pos <= 0.25)


def fwd_trades(t, o, l, c, a, hold, bar_ms, ft, cs):
    """For every setup bar i: entry at close of bar i+1, stop = low[i]-0.25*ATR[i], time exit at close of bar i+1+hold.
    Stop checked on bars i+2..i+1+hold, filled at min(stop, open). Returns (ret, xj) arrays length n.
    ret = net fraction after round-trip fee and funding (long pays); NaN if not enterable."""
    n = len(c)
    ret = np.full(n, np.nan)
    xj = np.zeros(n, int)
    m = n - 1 - hold  # setup i in 0..m-1 has window i+2..i+1+hold
    if m <= 0:
        return ret, xj
    wl = np.lib.stride_tricks.sliding_window_view(l[2:], hold)[:m]
    S = l[:m] - K_STOP * a[:m]
    entry = c[1:m + 1]
    hit = wl <= S[:, None]
    anyh = hit.any(1)
    first = hit.argmax(1)
    j = np.where(anyh, np.arange(m) + 2 + first, np.arange(m) + 1 + hold)
    exit_px = np.where(anyh, np.minimum(S, o[j]), c[j])
    te = t[1:m + 1] + bar_ms
    tx = t[j] + bar_ms
    fund = cs[np.searchsorted(ft, tx, side="right")] - cs[np.searchsorted(ft, te, side="right")]
    r = exit_px / entry - 1.0 - RT_FEE - fund
    good = (entry > S) & np.isfinite(S)
    ret[:m] = np.where(good, r, np.nan)
    xj[:m] = j
    return ret, xj
