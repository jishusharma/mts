"""
MyTradingSys/backtest/layers/cryptocred/cc_retest.py - Retest detection and classification (C07).
Stdlib only. Based on cc_structure's MSB events.
Rules cited:
- C07-E01: retests are optional; find_retest returning None is valid.
- C07-E04: a valid retest requires the level to hold before being touched again.
- C07-E05: immediate vs rounded retest based on bar count since break.
- C07-E06: split-position preference not implemented here.
- C07-E07: per-instrument precedent not implemented here.
- C07-E08: R:R-based skip not implemented here.
- C07-E09: hidden HTF retests not implemented here.
- C07-E10: context judgment not implemented here.
"""
from MyTradingSys.backtest.layers.cryptocred.cc_structure import is_range_extreme


def find_retest(bars: list, msb_event: dict, tolerance_pct: float = 0.0015, invalidate_pct: float = 0.005, expiry_bars: int = 200) -> dict | None:
    if tolerance_pct <= 0:
        raise ValueError("tolerance_pct must be positive")
    if invalidate_pct <= 0:
        raise ValueError("invalidate_pct must be positive")
    if expiry_bars < 1:
        raise ValueError("expiry_bars must be at least 1")

    direction = msb_event["direction"]
    broken_level = msb_event["broken_level"]
    confirm_i = msb_event["confirm_i"]

    # Determine the range of bars to scan
    start_k = confirm_i
    end_k = min(confirm_i + expiry_bars, len(bars) - 1)

    for k in range(start_k, end_k + 1):
        bar = bars[k]
        if direction == "bull":
            # Support level: L * (1 + tolerance_pct)
            touch_level = broken_level * (1 + tolerance_pct)
            invalidate_level = broken_level * (1 - invalidate_pct)
            if bar["l"] <= touch_level:
                return {"t": bar["t"], "i": k, "level": broken_level, "bars_since_break": k - confirm_i}
            # Check for invalidation before any touch
            if bar["c"] < invalidate_level:
                return None
        elif direction == "bear":
            # Resistance level: L * (1 - tolerance_pct)
            touch_level = broken_level * (1 - tolerance_pct)
            invalidate_level = broken_level * (1 + invalidate_pct)
            if bar["h"] >= touch_level:
                return {"t": bar["t"], "i": k, "level": broken_level, "bars_since_break": k - confirm_i}
            # Check for invalidation before any touch
            if bar["c"] > invalidate_level:
                return None

    return None


def classify_retest_timing(retest: dict, immediate_bars: int = 5) -> str:
    if immediate_bars < 1:
        raise ValueError("immediate_bars must be at least 1")
    if retest is None:
        raise ValueError("retest must not be None")

    if retest["bars_since_break"] <= immediate_bars:
        return "immediate"
    else:
        return "rounded"
