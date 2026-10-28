"""
T040 tick-based delta layer, part 3 of 3.

This module is the FLAG DECISION LOGIC ONLY for tick-sourced events.
It classifies live indicator readings against tier tables, decides whether
to flag them based on cooldown rules, and formats the flags as JSONL events.
"""

import json
import pathlib
from datetime import datetime


def tier_boundaries(occurrences: list) -> list:
    """
    Compute tier boundaries from a list of occurrences ordered most-to-least extreme.
    
    Args:
        occurrences: List of dicts with "value" and "tier" keys, ordered most-to-least extreme.
        
    Returns:
        List of (tier, boundary_value) tuples in tier-ascending order.
        
    Raises:
        ValueError: If occurrences is empty.
    """
    if not occurrences:
        raise ValueError("Occurrences list cannot be empty.")
    
    # Group by tier and find the least extreme value for each tier
    tier_groups = {}
    for item in occurrences:
        tier = item["tier"]
        value = item["value"]
        if tier not in tier_groups:
            tier_groups[tier] = []
        tier_groups[tier].append(value)
    
    # Return (tier, boundary) pairs in ascending tier order
    result = []
    for tier in sorted(tier_groups.keys()):
        # The least extreme value is the last one in the ordered list for that tier
        boundary_value = tier_groups[tier][-1]
        result.append((tier, boundary_value))
    
    return result


def classify_reading(value: float, high_bounds: list, low_bounds: list) -> dict:
    """
    Classify a reading against high and low boundaries.
    
    Args:
        value: The indicator reading to classify.
        high_bounds: List of (tier, boundary) tuples for high side, ascending by tier.
        low_bounds: List of (tier, boundary) tuples for low side, ascending by tier.
        
    Returns:
        Dict with "side" and "tier" keys indicating the classification.
    """
    # Check high side first
    for tier, boundary in high_bounds:
        if value >= boundary:
            return {"side": "high", "tier": tier}
    
    # Check low side
    for tier, boundary in low_bounds:
        if value <= boundary:
            return {"side": "low", "tier": tier}
    
    # No match on either side
    return {"side": None, "tier": None}


def should_emit(state: dict, key: tuple, tier: int, now_ms: int, cooldown_ms: int) -> bool:
    """
    Determine whether to emit a flag for the given reading.
    
    Args:
        state: Dictionary mapping keys to last emission info.
        key: Tuple of (indicator, tf, side).
        tier: Tier number of the current reading.
        now_ms: Current timestamp in milliseconds.
        cooldown_ms: Cooldown period in milliseconds.
        
    Returns:
        True if the flag should be emitted, False otherwise.
    """
    # If never emitted before
    if key not in state:
        return True
    
    last_emit_info = state[key]
    
    # Escalation always emits immediately
    if tier < last_emit_info["last_tier"]:
        return True
    
    # Same or less extreme tier, but cooldown has passed
    if now_ms - last_emit_info["last_emit_ms"] >= cooldown_ms:
        return True
    
    # Otherwise suppress emission
    return False


def make_flag(indicator: str, tf: str, side: str, tier: int, value: float, t_ms: int, extra: dict = None) -> dict:
    """
    Create a flag event dictionary.
    
    Args:
        indicator: The indicator name.
        tf: Timeframe string.
        side: "high" or "low".
        tier: Tier number.
        value: Indicator reading.
        t_ms: Timestamp in milliseconds.
        extra: Optional additional fields to merge into the result.
        
    Returns:
        Formatted flag event dictionary.
    """
    base = {
        "t": t_ms,
        "event": "tick_extreme",
        "source": "tick",
        "indicator": indicator,
        "tf": tf,
        "side": side,
        "tier": tier,
        "value": value
    }
    
    if extra is None:
        return base
    
    # Merge extra fields, with base keys taking precedence
    result = {**extra, **base}
    return result


def replay(historical: list, tiers_table: dict, cooldown_ms: int = 1800000) -> list:
    """
    Replay historical tick data through the flagger logic.
    
    Args:
        historical: List of tick readings with keys "t", "tf", "indicator", "value".
        tiers_table: Tier table mapping tf -> indicator -> {"high": [...], "low": [...]}.  
        cooldown_ms: Cooldown period in milliseconds.
        
    Returns:
        List of flag events to emit.
    """
    # Precompute bounds cache
    bounds_cache = {}
    for tf, indicators in tiers_table.items():
        for indicator, sides in indicators.items():
            high = sides.get("high", [])
            low = sides.get("low", [])
            bounds_cache[(tf, indicator)] = (
                tier_boundaries(high) if high else [],
                tier_boundaries(low) if low else []
            )
    
    # Initialize state and flags
    state = {}
    flags = []
    
    for item in historical:
        tf = item["tf"]
        indicator = item["indicator"]
        value = item["value"]
        t_ms = item["t"]
        
        if (tf, indicator) not in bounds_cache:
            continue  # Skip if no tier table for this (tf, indicator) pair
            
        high_bounds, low_bounds = bounds_cache[(tf, indicator)]
        result = classify_reading(value, high_bounds, low_bounds)
        
        # No flag needed if neutral reading
        if result["side"] is None:
            continue
            
        # Compute key for state tracking
        key = (indicator, tf, result["side"])
        
        # Check if we should emit
        if should_emit(state, key, result["tier"], t_ms, cooldown_ms):
            flag = make_flag(
                indicator=indicator,
                tf=tf,
                side=result["side"],
                tier=result["tier"],
                value=value,
                t_ms=t_ms
            )
            flags.append(flag)
            
            # Update state
            state[key] = {
                "last_tier": result["tier"],
                "last_emit_ms": t_ms
            }
    
    return flags

