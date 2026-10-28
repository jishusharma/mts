import statistics

def bucket_start_ms(t_ms: int, tf_minutes: int) -> int:
    """Floor-aligned UTC bucket start: (t_ms // (tf_minutes * 60000)) * (tf_minutes * 60000). Raise ValueError if tf_minutes <= 0."""
    if tf_minutes <= 0:
        raise ValueError("tf_minutes must be positive")
    return (t_ms // (tf_minutes * 60000)) * (tf_minutes * 60000)

def resample(bars: list, tf_minutes: int) -> list:
    """Groups 1-minute bars into tf_minutes-wide buckets aligned to UTC epoch via bucket_start_ms.
    
    Mechanical epoch-floor bucketing, same convention as layers/timeframe/tf_resample.py for seconds-unit timeframes.
    Raise ValueError if bars is empty or tf_minutes <= 0. Only emit a bucket once it is CLOSED:
    bucket_start_ms(t, tf_minutes) + tf_minutes * 60000 <= bars[-1]["t"] + 60000.
    A bucket with zero underlying bars (a full gap) is skipped, never synthesized.
    For each closed bucket, compute and return a dict with keys: t, o, h, l, c, v, tbv, n, net_delta, cvd_change, volume, price_change_pct.
    Raise ValueError if o == 0 for a bucket (division by zero in price_change_pct).
    """
    if not bars:
        raise ValueError("bars must not be empty")
    if tf_minutes <= 0:
        raise ValueError("tf_minutes must be positive")
    
    last_bar_t = bars[-1]["t"]
    closed_buckets = []
    
    # Group bars by bucket start time
    buckets_by_start = {}
    for bar in bars:
        bucket_start = bucket_start_ms(bar["t"], tf_minutes)
        if bucket_start not in buckets_by_start:
            buckets_by_start[bucket_start] = []
        buckets_by_start[bucket_start].append(bar)
    
    # Process each bucket
    for bucket_start, bucket_bars in sorted(buckets_by_start.items()):
        # Check if bucket is closed
        bucket_end = bucket_start + tf_minutes * 60000
        if bucket_end > last_bar_t + 60000:
            continue
            
        # Compute bucket stats
        first_bar = bucket_bars[0]
        last_bar = bucket_bars[-1]
        
        o = first_bar["o"]
        h = max(bar["h"] for bar in bucket_bars)
        l = min(bar["l"] for bar in bucket_bars)
        c = last_bar["c"]
        v = sum(bar["v"] for bar in bucket_bars)
        tbv = sum(bar["tbv"] for bar in bucket_bars)
        n = len(bucket_bars)
        
        # Calculate indicators
        net_delta = 2 * tbv - v
        cvd_change = net_delta  # Same as net_delta in this context
        volume = v
        price_change_pct = (c - o) / o * 100.0 if o != 0 else 0
        
        if o == 0:
            raise ValueError("Division by zero in price_change_pct")
            
        closed_buckets.append({
            "t": bucket_start,
            "o": o,
            "h": h,
            "l": l,
            "c": c,
            "v": v,
            "tbv": tbv,
            "n": n,
            "net_delta": net_delta,
            "cvd_change": cvd_change,
            "volume": volume,
            "price_change_pct": price_change_pct
        })
    
    return closed_buckets

def session_tag(t_ms: int) -> str:
    """UTC-minute-of-day session windows.
    
    Asian 00:00-08:00 UTC, European 08:00-16:30 UTC narrowed here to keep the four windows disjoint and covering 24h,
    American 13:00-21:00 UTC -- the 13:00-16:30 overlap is its own explicit "overlap" tag rather than an invented priority rule.
    """
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
    """True if t_ms falls within window_min minutes (inclusive) of a funding reset at UTC 00:00, 08:00 or 16:00."""
    md = (t_ms // 60000) % 1440
    resets = [0, 480, 960]
    for r in resets:
        distance = min(abs(md - r), 1440 - abs(md - r))
        if distance <= window_min:
            return True
    return False

def gap_tiers(values_desc: list, factor: float = 1.5) -> list:
    """Detects natural breaks in the gap distribution between consecutive ranks and returns a list of tier numbers.

    values_desc must already be sorted non-increasing (raise ValueError if it is not, or if it is empty).
    Compute gaps[i] = values_desc[i] - values_desc[i+1] for i in 0..len-2.
    If there are no gaps (a single value), return [1].
    median_gap = statistics.median(gaps).
    Start tier = 1, result = [1].
    For i in 0..len(gaps)-1: if median_gap > 0 and gaps[i] > factor * median_gap, increment tier.
    Append tier to result. Return result.
    """
    if not values_desc:
        raise ValueError("values_desc must not be empty")
    if len(values_desc) < 2:
        return [1]
    
    # Check non-increasing
    for i in range(len(values_desc) - 1):
        if values_desc[i] < values_desc[i + 1]:
            raise ValueError("values_desc must be non-increasing")
    
    gaps = []
    for i in range(len(values_desc) - 1):
        gap = values_desc[i] - values_desc[i + 1]
        gaps.append(gap)
    
    median_gap = statistics.median(gaps)
    
    if median_gap <= 0:
        return [1] * len(values_desc)
    
    tier = 1
    result = [1]
    
    for gap in gaps:
        if gap > factor * median_gap:
            tier += 1
        result.append(tier)
    
    return result

def rank_extremes(buckets: list, indicator: str, top_n: int = 20) -> dict:
    """Builds extreme rankings for a given indicator across buckets.
    
    buckets is the output of resample (ascending time order).
    indicator is one of "net_delta", "cvd_change", "volume", "price_change_pct".
    HIGH side: sort descending by value (stable sort), take first min(top_n, len(buckets)), run gap_tiers on their values.
    LOW side: sort ascending by value (stable), negate each value to make it non-increasing for gap_tiers,
    run gap_tiers on the negated list, assign back to original order.
    Return {"high": [...], "low": [...]}.
    """
    if not buckets:
        raise ValueError("buckets must not be empty")
    
    valid_indicators = ("net_delta", "cvd_change", "volume", "price_change_pct")
    if indicator not in valid_indicators:
        raise ValueError(f"indicator must be one of {valid_indicators}")
    
    # Build list of (value, bucket) pairs
    value_bucket_pairs = [(bucket[indicator], bucket) for bucket in buckets]
    
    # High side: sort descending by value (stable)
    high_sorted = sorted(value_bucket_pairs, key=lambda x: x[0], reverse=True)
    high_top = high_sorted[:top_n]
    high_values = [pair[0] for pair in high_top]
    
    # Get tiers for high side
    high_tiers = gap_tiers(high_values)
    
    # Build high result list
    high_result = []
    for i, (value, bucket) in enumerate(high_top):
        high_result.append({
            "t": bucket["t"],
            "value": value,
            "tier": high_tiers[i],
            "session": session_tag(bucket["t"]),
            "funding_window": in_funding_window(bucket["t"]),
            "price_change_pct": bucket["price_change_pct"]
        })
    
    # Low side: sort ascending by value (stable)
    low_sorted = sorted(value_bucket_pairs, key=lambda x: x[0])
    low_top = low_sorted[:top_n]
    low_values = [pair[0] for pair in low_top]
    
    # Negate values to make them non-increasing for gap_tiers
    negated_low_values = [-v for v in low_values]
    
    # Get tiers for low side
    low_tiers = gap_tiers(negated_low_values)
    
    # Build low result list (assign back original order)
    low_result = []
    for i, (value, bucket) in enumerate(low_top):
        low_result.append({
            "t": bucket["t"],
            "value": value,
            "tier": low_tiers[i],
            "session": session_tag(bucket["t"]),
            "funding_window": in_funding_window(bucket["t"]),
            "price_change_pct": bucket["price_change_pct"]
        })
    
    return {"high": high_result, "low": low_result}

def build_tier_table(bars: list, timeframes: list = (1, 2, 3, 5, 10, 15), indicators: list = ("net_delta", "cvd_change", "volume", "price_change_pct"), top_n: int = 20) -> dict:
    """Orchestrator for building tier tables across multiple timeframes and indicators.
    
    For each tf in timeframes (int minutes): call resample(bars, tf).
    If that call raises ValueError OR it returns an empty list, skip this tf entirely.
    Otherwise, for each name in indicators: compute rank_extremes(buckets, name, top_n).
    Return a nested dict {str(tf): {indicator_name: {"high": [...], "low": [...]}}}.
    """
    result = {}
    
    for tf in timeframes:
        try:
            buckets = resample(bars, tf)
        except ValueError:
            continue
            
        if not buckets:
            continue
            
        tf_result = {}
        for indicator in indicators:
            try:
                tf_result[indicator] = rank_extremes(buckets, indicator, top_n)
            except ValueError:
                # If we can't compute extremes for this indicator, skip it
                pass
                
        if tf_result:
            result[str(tf)] = tf_result
            
    return result
