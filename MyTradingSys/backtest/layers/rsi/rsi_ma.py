"""
Smoothing line on the RSI, as shipped with the standard indicator.
D2 isolation rule: the 40/60 numbers are private to malkan_40_60. No other module imports them.
Default SMA 14 per D4.
"""
from typing import List, Optional

def rsi_ma(rsi: List[Optional[float]], type: str = "SMA", length: int = 14) -> List[Optional[float]]:
    """
    Smoothing line over an RSI series (itself possibly containing leading `None`s).
    Returns a list the same length as `rsi`. A value at index `i` requires `length` CONSECUTIVE non-`None` `rsi` values ending at `i` (i.e. `rsi[i-length+1 : i+1]` all non-`None`); if that window is not fully available (not enough history, or a `None` inside the window), the output at `i` is `None`.
    `type == "SMA"`: arithmetic mean of the window.
    `type == "WMA"`: linearly weighted mean, weights `1..length` assigned oldest-to-newest within the window (most recent value gets weight `length`); result = `sum(weight*value)/sum(weights)`.
    `type == "EMA"`: exponential moving average, `alpha = 2/(length+1)`. The FIRST available value (first index with a full window) is seeded as the SMA of that window (not a raw EMA from index 0 — this matches the Wilder-style warm-up convention used elsewhere in this layer). Every subsequent index (even if some `rsi` values before it were `None` earlier in the series but the window at THIS index is now short one entry due to a gap — in that case output `None` for this index per the windowing rule above, and do NOT advance the recursive `prev` state past a gap; if a `None` breaks the chain, the next valid window reseeds via SMA again) recurses: `prev = (rsi[i]-prev)*alpha + prev`.
    `type == "RMA"` (SMMA): same seeding/reseeding convention as EMA, `alpha = 1/length` instead of `2/(length+1)`.
    Raise `ValueError` if `type` not in `("SMA","EMA","RMA","WMA")`, or if `length < 1`.
    """
    if type not in ("SMA", "EMA", "RMA", "WMA"):
        raise ValueError("Type must be one of SMA, EMA, RMA, WMA")
    if length < 1:
        raise ValueError("Length must be >= 1")

    result = [None] * len(rsi)
    
    # Precompute weights for WMA
    if type == "WMA":
        wma_weights = list(range(1, length + 1))
        wma_weight_sum = sum(wma_weights)
    
    for i in range(len(rsi)):
        # Check if we have enough non-None values ending at index i
        window_start = i - length + 1
        if window_start < 0:
            continue
            
        window = rsi[window_start:i+1]
        
        # Check if all values in the window are non-None
        if any(x is None for x in window):
            continue
            
        if type == "SMA":
            result[i] = sum(window) / length
            
        elif type == "WMA":
            weighted_sum = sum(w * v for w, v in zip(wma_weights, window))
            result[i] = weighted_sum / wma_weight_sum
            
        elif type == "EMA" or type == "RMA":
            alpha = 2.0 / (length + 1) if type == "EMA" else 1.0 / length

            # Reseed (the value at this index IS the SMA seed, no extra recursive step on
            # top of it) whenever this is the very first full window, or the chain was broken
            # by a gap (result[i-1] is None even though this window is now fully valid again).
            if i == length - 1 or result[i - 1] is None:
                result[i] = sum(window) / length
            else:
                prev = result[i - 1]
                result[i] = (rsi[i] - prev) * alpha + prev
            
    return result
