"""vfi.py - Volume Flow Indicator (LazyBear / Katsanos), context columns only. Formula: FORMULAS.md section 32.

Defaults are LazyBear's script defaults (SOURCED). The full-window None rule and smooth_kind="ema" are OURS.
"""
import math


def vfi(high, low, close, volume, length=130, coef=0.2, vcoef=2.5, smooth=3, stdev_len=30, smooth_kind="sma"):
    """-> (vfi_raw, vfi_smoothed), lists aligned to the input, None until defined.
    raw = SUM(vcp, length) / vave, first defined at bar max(stdev_len, length) + length - 1.
    smoothed = SMA(raw, smooth) (or EMA, SMA-seeded, with smooth_kind="ema"); smooth <= 1 returns raw."""
    n = len(close)
    if not (len(high) == len(low) == len(volume) == n):
        raise ValueError("high/low/close/volume length mismatch")
    if smooth_kind not in ("sma", "ema"):
        raise ValueError("smooth_kind must be 'sma' or 'ema'")
    typ = [(high[i] + low[i] + close[i]) / 3.0 for i in range(n)]
    if any(t <= 0 for t in typ):
        raise ValueError("typical price must be positive (log)")
    inter = [None] + [math.log(typ[i]) - math.log(typ[i - 1]) for i in range(1, n)]
    vcp = [None] * n
    for i in range(max(stdev_len, length), n):
        w = inter[i - stdev_len + 1:i + 1]
        m = sum(w) / stdev_len
        vinter = math.sqrt(sum((x - m) ** 2 for x in w) / stdev_len)   # population stdev (section 22)
        cutoff = coef * vinter * close[i]
        vave = sum(volume[i - length:i]) / length                       # previous bars only
        vc = min(volume[i], vcoef * vave)
        mf = typ[i] - typ[i - 1]
        vcp[i] = vc if mf > cutoff else (-vc if mf < -cutoff else 0.0)
    raw = [None] * n
    first = max(stdev_len, length) + length - 1
    for i in range(first, n):
        vave = sum(volume[i - length:i]) / length
        raw[i] = sum(vcp[i - length + 1:i + 1]) / vave if vave else None
    if smooth <= 1:
        return raw, list(raw)
    sm = [None] * n
    prev = None
    for i in range(n):
        w = raw[i - smooth + 1:i + 1] if i >= smooth - 1 else []
        if len(w) < smooth or any(x is None for x in w):
            prev = None
            continue
        if smooth_kind == "sma" or prev is None:
            prev_sma = sum(w) / smooth
            sm[i] = prev_sma
            prev = prev_sma
        else:
            a = 2.0 / (smooth + 1)
            prev = a * raw[i] + (1 - a) * prev
            sm[i] = prev
    return raw, sm
