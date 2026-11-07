"""squeeze.py - Squeeze Momentum (LazyBear), context columns only. Formula: FORMULAS.md section 31.

Defaults are LazyBear's script defaults (SOURCED). The 1e-9 relative tie tolerance is OURS.
"""
import math


def _sma(a, i, n):
    return sum(a[i - n + 1:i + 1]) / n


def squeeze_momentum(high, low, close, bb_len=20, bb_mult=2.0, kc_len=20, kc_mult=1.5, mom_len=20):
    """-> (squeeze_on, squeeze_off, momentum), each a list aligned to the input, None until defined.
    squeeze_on: BB inside KC (strict); squeeze_off: BB outside KC (strict); both False when equal/overlapping."""
    n = len(close)
    if not (len(high) == len(low) == n):
        raise ValueError("high/low/close length mismatch")
    tr = [high[i] - low[i] if i == 0 else
          max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])) for i in range(n)]
    src = [None] * n
    for i in range(kc_len - 1, n):
        hh = max(high[i - kc_len + 1:i + 1])
        ll = min(low[i - kc_len + 1:i + 1])
        src[i] = close[i] - ((hh + ll) / 2.0 + _sma(close, i, kc_len)) / 2.0
    on = [None] * n
    off = [None] * n
    mom = [None] * n
    for i in range(n):
        if i >= max(bb_len, kc_len) - 1:
            m = _sma(close, i, bb_len)
            sd = math.sqrt(sum((c - m) ** 2 for c in close[i - bb_len + 1:i + 1]) / bb_len)
            bb_hw = bb_mult * sd
            kc_hw = kc_mult * _sma(tr, i, kc_len)
            tol = 1e-9 * max(1.0, abs(bb_hw), abs(kc_hw))
            on[i] = bb_hw < kc_hw - tol
            off[i] = bb_hw > kc_hw + tol
        if i >= kc_len + mom_len - 2:
            y = src[i - mom_len + 1:i + 1]
            xm = (mom_len - 1) / 2.0
            sxx = sum((k - xm) ** 2 for k in range(mom_len))
            ym = sum(y) / mom_len
            slope = sum((k - xm) * y[k] for k in range(mom_len)) / sxx if sxx else 0.0
            mom[i] = ym + slope * (mom_len - 1 - xm)
    return on, off, mom
