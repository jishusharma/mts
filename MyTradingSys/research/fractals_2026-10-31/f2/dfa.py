"""Rolling detrended fluctuation analysis (DFA-1) Hurst on 1h log returns. See PRE_REG.md and FORMULAS.md s27.

Pure numpy, no look-ahead: H[i] uses returns i-W+1..i only (known at the close of 1h bar i).
"""
import numpy as np

WINDOW = 480                      # returns per window = 20 days (OURS)
SCALES = (8, 16, 32, 60, 96, 160)  # box sizes, all divide 480 so every return is used (OURS)


def fluct2(x, s):
    """Mean squared residual of the linear detrend of the demeaned profile in boxes of s, rows of x are series.

    x: (m, n) returns. Profile y = cumsum(x - rowmean). Boxes of length s from the front, nb = n // s.
    Per box: least-squares line; residual MSE. Returns F^2(s) per row (mean over boxes of box MSE).
    """
    x = np.atleast_2d(np.asarray(x, float))
    m, n = x.shape
    y = np.cumsum(x - x.mean(1, keepdims=True), axis=1)
    nb = n // s
    b = y[:, : nb * s].reshape(m, nb, s)
    t = np.arange(s, dtype=float)
    tm = t - t.mean()
    slope = (b * tm).sum(2) / (tm ** 2).sum()
    res = b - b.mean(2, keepdims=True) - slope[:, :, None] * tm
    return (res ** 2).mean(2).mean(1)


def dfa_alpha(x, scales=SCALES):
    """DFA exponent of the series x (1-D): slope of log F(s) on log s. alpha ~ 0.5 white noise, > 0.5 persistent."""
    f2 = np.array([fluct2(x, s)[0] for s in scales])
    return float(np.polyfit(np.log(scales), 0.5 * np.log(f2), 1)[0])


def rolling_alpha(r, window=WINDOW, scales=SCALES, chunk=1500):
    """H[i] = dfa_alpha(r[i-window+1 : i+1]); NaN for i < window-1. r is a 1-D array of returns (NaN-free)."""
    r = np.asarray(r, float)
    n = len(r)
    if n < window:
        return np.full(n, np.nan)
    win = np.lib.stride_tricks.sliding_window_view(r, window)   # (n-window+1, window)
    lx = np.log(scales)
    xm = lx - lx.mean()
    parts = [np.full(window - 1, np.nan)]
    for w in np.array_split(win, max(1, -(-len(win) // chunk))):
        lf = np.stack([0.5 * np.log(fluct2(w, s)) for s in scales], axis=1)
        parts.append((lf * xm).sum(1) / (xm ** 2).sum())
    return np.concatenate(parts)
