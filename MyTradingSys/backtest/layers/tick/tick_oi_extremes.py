"""
Part 2 of the T040 full-history extreme-tier design (see
MyTradingSys/items/T040_tick_delta_layer.md, decision "s6") -- open-interest version.

FLAGS/context only, never gates or filters any other layer's signal, read-only, no verdict-path wiring.
"""

import statistics
from datetime import datetime, timezone


def resample_oi(bars: list, tf_minutes: int) -> list:
    """Resample OI data to specified timeframe buckets."""
    if not bars:
        raise ValueError("bars cannot be empty")
    if tf_minutes <= 0 or tf_minutes % 5 != 0:
        raise ValueError("tf_minutes must be a positive multiple of 5")
    
    last_t = bars[-1]["t"]
    bucket_end = last_t + 5 * 60000  # Last native bar's coverage
    buckets = []
    
    # Group bars by bucket start time
    bucket_map = {}
    for bar in bars:
        bucket_start = (bar["t"] // (tf_minutes * 60000)) * (tf_minutes * 60000)
        if bucket_start not in bucket_map:
            bucket_map[bucket_start] = []
        bucket_map[bucket_start].append(bar)
    
    # Process each bucket
    for bucket_start in sorted(bucket_map.keys()):
        # Only emit buckets that are closed
        if bucket_start + tf_minutes * 60000 <= bucket_end:
            bucket_bars = bucket_map[bucket_start]
            if not bucket_bars:
                continue
            last_bar = bucket_bars[-1]
            buckets.append({
                "t": bucket_start,
                "oi_last": last_bar["oi"],
                "oi_usd_last": last_bar["oi_usd"],
                "n": len(bucket_bars)
            })
    
    return buckets


def oi_delta_series(buckets: list) -> list:
    """Calculate OI deltas from resampled buckets."""
    if len(buckets) < 2:
        raise ValueError("buckets must contain at least 2 elements")
    
    deltas = []
    for i in range(1, len(buckets)):
        delta = buckets[i]["oi_last"] - buckets[i-1]["oi_last"]
        deltas.append({
            "t": buckets[i]["t"],
            "oi_delta": delta
        })
    
    return deltas


def session_tag(t_ms: int) -> str:
    """Determine trading session based on timestamp."""
    md = (t_ms // 60000) % 1440
    if 0 <= md < 480:
        return "asian"
    elif 480 <= md < 780:
        return "european"
    elif 780 <= md < 990:
        return "overlap"
    elif 990 <= md < 1260:
        return "american"
    else:
        return "off_hours"


def in_funding_window(t_ms: int, window_min: int = 30) -> bool:
    """Check if timestamp is within a funding window."""
    md = (t_ms // 60000) % 1440
    for r in (0, 480, 960):
        distance = min(abs(md - r), 1440 - abs(md - r))
        if distance <= window_min:
            return True
    return False


def gap_tiers(values_desc: list, factor: float = 1.5) -> list:
    """Assign tiers based on gaps between values."""
    if not values_desc or not all(a >= b for a, b in zip(values_desc, values_desc[1:], strict=False)):
        raise ValueError("values_desc must be non-empty and strictly non-increasing")
    
    gaps = [values_desc[i] - values_desc[i+1] for i in range(len(values_desc)-1)]
    if not gaps:
        return [1]
    
    median_gap = statistics.median(gaps)
    if median_gap == 0:
        return [1] * len(values_desc)
    
    threshold = factor * median_gap
    tiers = [1] * len(values_desc)
    current_tier = 1
    
    for i in range(len(gaps)):
        if gaps[i] > threshold:
            current_tier += 1
        tiers[i+1] = current_tier
    
    return tiers


def rank_oi_extremes(oi_delta_list: list, top_n: int = 20) -> dict:
    """Rank OI extremes by delta values."""
    if not oi_delta_list:
        raise ValueError("oi_delta_list cannot be empty")
    
    # HIGH side (biggest OI build-up)
    high_sorted = sorted(oi_delta_list, key=lambda x: x["oi_delta"], reverse=True)
    high_top = high_sorted[:top_n]
    high_values = [x["oi_delta"] for x in high_top]
    high_tiers = gap_tiers(high_values)
    
    # LOW side (biggest OI unwind)
    low_sorted = sorted(oi_delta_list, key=lambda x: x["oi_delta"])
    low_top = low_sorted[:top_n]
    low_values = [-x["oi_delta"] for x in low_top]  # Negate to get non-increasing order
    low_tiers = gap_tiers(low_values)
    
    # Assign back tiers in original ascending order
    high_result = []
    for i, entry in enumerate(high_top):
        high_result.append({
            "t": entry["t"],
            "value": entry["oi_delta"],
            "tier": high_tiers[i],
            "session": session_tag(entry["t"]),
            "funding_window": in_funding_window(entry["t"])
        })
    
    low_result = []
    for i, entry in enumerate(low_top):
        low_result.append({
            "t": entry["t"],
            "value": entry["oi_delta"],
            "tier": low_tiers[i],
            "session": session_tag(entry["t"]),
            "funding_window": in_funding_window(entry["t"])
        })
    
    return {"high": high_result, "low": low_result}


def build_oi_tier_table(bars: list, timeframes: list = (5, 10, 15), top_n: int = 20) -> dict:
    """Build OI tier tables for specified timeframes."""
    result = {}
    
    for tf in timeframes:
        try:
            buckets = resample_oi(bars, tf)
            if len(buckets) < 2:
                continue
            deltas = oi_delta_series(buckets)
            table = rank_oi_extremes(deltas, top_n)
            result[str(tf)] = table
        except ValueError:
            # Skip this timeframe if it fails
            continue
    
    return result
