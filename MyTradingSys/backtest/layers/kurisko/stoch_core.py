"""Stochastic lines for the Kurisko quad rotation. Pure functions of closed bars, stdlib only.

Definition and worked numbers: backtest/layers/FORMULAS.md section 24.
raw %K_k[t] = 100*(C[t]-LL)/(HH-LL) over bars t-k+1..t; HH == LL gives NaN (never 0 or 100).
Plotted line = D = SMA_d(SMA_slow(raw %K)) (KURISKO_SPEC s5 gap 2: "here I'm using the D line"); slow = 1 means no slowing.
A NaN anywhere in an SMA window gives NaN. Output at index t uses bars <= t only.
"""
import math

NAN = float("nan")


def sma(xs, n):
    """Simple moving average over the last n values; NaN until n values exist or if any value in the window is NaN."""
    out = [NAN] * len(xs)
    for i in range(n - 1, len(xs)):
        w = xs[i - n + 1:i + 1]
        if not any(math.isnan(v) for v in w):
            out[i] = sum(w) / n
    return out


def raw_k(high, low, close, k):
    out = [NAN] * len(close)
    for i in range(k - 1, len(close)):
        hs, ls = high[i - k + 1:i + 1], low[i - k + 1:i + 1]
        c = close[i]
        if any(math.isnan(v) for v in hs) or any(math.isnan(v) for v in ls) or math.isnan(c):
            continue
        hh, ll = max(hs), min(ls)
        if hh == ll:
            continue
        out[i] = 100.0 * (c - ll) / (hh - ll)
    return out


def stoch_line(high, low, close, k, d, slow=1):
    r = raw_k(high, low, close, k)
    if slow > 1:
        r = sma(r, slow)
    return sma(r, d) if d > 1 else r
