"""
MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py - FAB-005/FAB-006 volume profile "real FVG" detector.

This module implements:
- FAB-005: anchor a FIXED-RANGE volume profile over one swing leg (point A to point B),
  compute its value area (70% of volume), and the single lowest-volume PRICE LEVEL
  inside that value area is the "real fair value gap".
- FAB-006: price is expected to react/reject at that level.

Key caveat: this module approximates volume-at-price using 1m kline OHLCV data.
Each bar's volume is spread uniformly across its own [low, high] range into price bins.
This is trade-level order-flow data approximation, not actual volume-at-price.

The video's data is trade-level order-flow; this module only has 1m kline OHLCV (no aggTrades),
so volume-at-price is APPROXIMATED by spreading each bar's volume uniformly across its own
`[low, high]` range into price bins -- document this as the key caveat (1m volume-profile approximation).
"""

from MyTradingSys.backtest.layers.cryptocred.cc_structure import find_swings
import random


def swing_legs(bars: list, left: int = 2, right: int = 2, use_body: bool = True) -> list:
    """
    Find consecutive swing points and form legs between them.
    
    Args:
        bars: List of bar dicts with keys "o", "h", "l", "c", "v", "t"
        left: Left-side fractal lookback
        right: Right-side fractal lookback
        use_body: Whether to use bar body for swing detection
        
    Returns:
        List of leg dicts with keys "a_i", "b_i", "a_price", "b_price", "confirmed_i"
    """
    swings = find_swings(bars, left=left, right=right, use_body=use_body)
    
    legs = []
    for k in range(len(swings) - 1):
        legs.append({
            "a_i": swings[k]["i"],
            "b_i": swings[k+1]["i"],
            "a_price": swings[k]["price"],
            "b_price": swings[k+1]["price"],
            "confirmed_i": swings[k+1]["confirmed_i"]
        })
    
    return legs


def build_profile(bars: list, a_i: int, b_i: int, n_bins: int = 20) -> dict:
    """
    Builds a volume-at-price histogram over bars[a_i : b_i+1] inclusive.
    
    Args:
        bars: List of bar dicts with keys "o", "h", "l", "c", "v", "t"
        a_i: Start index (inclusive)
        b_i: End index (inclusive)
        n_bins: Number of bins to use
        
    Returns:
        Dict with keys "lo", "hi", "n_bins", "bin_width", "volumes"
        
    Raises:
        ValueError: If indices are invalid or range is zero
    """
    if a_i >= b_i:
        raise ValueError("a_i must be less than b_i")
    if a_i < 0 or b_i >= len(bars):
        raise ValueError("Indices out of range")
    
    # Compute price range
    lo = min(bar["l"] for bar in bars[a_i : b_i+1])
    hi = max(bar["h"] for bar in bars[a_i : b_i+1])
    
    if hi <= lo:
        raise ValueError("Price range must be > 0")
        
    w = (hi - lo) / n_bins
    
    # Initialize volumes
    volumes = [0.0] * n_bins
    
    # Distribute volume across bins for each bar
    for bar in bars[a_i : b_i+1]:
        bar_lo = bar["l"]
        bar_hi = bar["h"]
        bar_v = bar["v"]
        
        if bar_hi == bar_lo:
            # Zero-range bar: put all volume in the single bin containing that price
            bin_idx = int((bar_lo - lo) / w)
            if bin_idx >= n_bins:
                bin_idx = n_bins - 1
            volumes[bin_idx] += bar_v
        else:
            # Non-zero range bar: distribute volume across overlapping bins
            for m in range(n_bins):
                bin_lo = lo + m * w
                bin_hi = lo + (m + 1) * w
                
                overlap = max(0, min(bar_hi, bin_hi) - max(bar_lo, bin_lo))
                
                if overlap > 0:
                    volumes[m] += bar_v * overlap / (bar_hi - bar_lo)
    
    return {
        "lo": lo,
        "hi": hi,
        "n_bins": n_bins,
        "bin_width": w,
        "volumes": volumes
    }


def value_area(profile: dict, pct: float = 0.70) -> tuple:
    """
    Compute the value area from a volume profile.
    
    Args:
        profile: Volume profile dict from build_profile()
        pct: Percentage of volume to include (default 0.70)
        
    Returns:
        Tuple (lo_bin_index, hi_bin_index) inclusive
        
    Raises:
        ValueError: If total volume <= 0 or pct invalid
    """
    if not profile["volumes"]:
        raise ValueError("No volumes in profile")
        
    total = sum(profile["volumes"])
    
    if total <= 0:
        raise ValueError("Total volume must be > 0")
        
    if not (0 < pct <= 1):
        raise ValueError("pct must be between 0 and 1")
        
    # Find POC (price of center)
    poc = profile["volumes"].index(max(profile["volumes"]))
    
    included = {poc}
    covered = profile["volumes"][poc]
    
    while covered < pct * total:
        lo_edge = min(included)
        hi_edge = max(included)
        
        # Get volumes of adjacent bins
        vol_lo = profile["volumes"][lo_edge - 1] if lo_edge > 0 else 0
        vol_hi = profile["volumes"][hi_edge + 1] if hi_edge < len(profile["volumes"]) - 1 else 0
        
        # If both exist, choose the larger volume (tie-break: prefer lower price)
        if vol_lo > 0 and vol_hi > 0:
            if vol_lo >= vol_hi:
                included.add(lo_edge - 1)
                covered += vol_lo
            else:
                included.add(hi_edge + 1)
                covered += vol_hi
        elif vol_lo > 0:
            included.add(lo_edge - 1)
            covered += vol_lo
        elif vol_hi > 0:
            included.add(hi_edge + 1)
            covered += vol_hi
        else:
            # Both edges exhausted, stop
            break
    
    return (min(included), max(included))


def lowest_volume_level(profile: dict, va: tuple) -> dict:
    """
    Find the bin with minimum volume within the value area.
    
    Args:
        profile: Volume profile dict from build_profile()
        va: Tuple (lo_bin_index, hi_bin_index) inclusive
        
    Returns:
        Dict with keys "bin_index", "price_lo", "price_hi", "volume"
        
    Raises:
        ValueError: If va indices are invalid
    """
    lo_bin, hi_bin = va
    
    if lo_bin > hi_bin:
        raise ValueError("lo_bin must be <= hi_bin")
        
    if lo_bin < 0 or hi_bin >= len(profile["volumes"]):
        raise ValueError("va indices out of range")
    
    # Find minimum volume in the value area
    min_volume = float('inf')
    min_idx = -1
    
    for idx in range(lo_bin, hi_bin + 1):
        vol = profile["volumes"][idx]
        if vol < min_volume:
            min_volume = vol
            min_idx = idx
    
    return {
        "bin_index": min_idx,
        "price_lo": profile["lo"] + min_idx * profile["bin_width"],
        "price_hi": profile["lo"] + (min_idx + 1) * profile["bin_width"],
        "volume": min_volume
    }


def random_va_level(profile: dict, va: tuple, seed: int) -> dict:
    """
    Control for FAB-006 testing: same return shape as lowest_volume_level,
    but idx is chosen uniformly at random from range(lo_bin, hi_bin+1).
    
    Args:
        profile: Volume profile dict from build_profile()
        va: Tuple (lo_bin_index, hi_bin_index) inclusive
        seed: Random seed for reproducibility
        
    Returns:
        Dict with keys "bin_index", "price_lo", "price_hi", "volume"
    """
    lo_bin, hi_bin = va
    
    if lo_bin > hi_bin:
        raise ValueError("lo_bin must be <= hi_bin")
        
    if lo_bin < 0 or hi_bin >= len(profile["volumes"]):
        raise ValueError("va indices out of range")
    
    # Choose random bin index
    rand = random.Random(seed)
    bin_idx = rand.randrange(lo_bin, hi_bin + 1)
    
    return {
        "bin_index": bin_idx,
        "price_lo": profile["lo"] + bin_idx * profile["bin_width"],
        "price_hi": profile["lo"] + (bin_idx + 1) * profile["bin_width"],
        "volume": profile["volumes"][bin_idx]
    }

