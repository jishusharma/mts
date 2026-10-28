"""
MyTradingSys/backtest/layers/timeframe/tf_resample.py - D1 (RSI_TF_LAYER_DESIGN.md) timeframe resampling.
Closed bars only, gaps reported not filled, registry-driven.
"""
import datetime
import math


def bucket_start(t_ms: int, tf: str, registry: dict) -> int:
    """
    Compute the start time (epoch ms) of the bucket containing t_ms for timeframe tf.
    Boundary regimes:
    - seconds: epoch-aligned (floor(t_sec / seconds) * seconds)
    - day_reset_seconds: counted from 00:00 UTC each day; the last bucket of the day is cut at midnight (T088 7h)
    - days: epoch-day-mod-N with configurable anchor date
    - week: Monday-anchored ISO week (epoch_day % 7 == 4 is Monday)
    - month: first day of calendar UTC month
    """
    entry = registry["timeframes"][tf]
    unit = entry["unit"]
    
    if unit == "seconds":
        sec = t_ms // 1000
        seconds = entry["seconds"]
        return (sec // seconds) * seconds * 1000
    
    elif unit == "day_reset_seconds":
        day_ms = (t_ms // 86400000) * 86400000
        step = entry["seconds"] * 1000
        return day_ms + ((t_ms - day_ms) // step) * step
    
    elif unit == "days":
        anchor_date = entry["anchor_date"]
        y, m, d = map(int, anchor_date.split("-"))
        anchor_ms = datetime.datetime(y, m, d, tzinfo=datetime.timezone.utc).timestamp() * 1000
        anchor_day = anchor_ms // 86400000
        
        epoch_day = t_ms // 86400000
        offset = epoch_day - anchor_day
        days = entry["days"]
        bucket_day = anchor_day + days * (offset // days)
        
        return bucket_day * 86400000
    
    elif unit == "week":
        epoch_day = t_ms // 86400000
        # Monday is where epoch_day % 7 == 4 (1970-01-01 is Thursday)
        bucket_day = epoch_day - ((epoch_day - 4) % 7)
        return bucket_day * 86400000
    
    elif unit == "month":
        # Convert t_ms to UTC datetime, get first day of that month
        dt = datetime.datetime.fromtimestamp(t_ms/1000, tz=datetime.timezone.utc)
        y, m = dt.year, dt.month
        first_of_month = datetime.datetime(y, m, 1, tzinfo=datetime.timezone.utc)
        return int(first_of_month.timestamp() * 1000)
    
    else:
        raise ValueError(f"Unsupported unit '{unit}' for timeframe '{tf}'")


def bucket_end(t_ms: int, tf: str, registry: dict) -> int:
    """
    Compute the end time (epoch ms) of the bucket containing t_ms for timeframe tf.
    """
    entry = registry["timeframes"][tf]
    start = bucket_start(t_ms, tf, registry)
    unit = entry["unit"]
    
    if unit == "seconds":
        return start + entry["seconds"] * 1000
    elif unit == "day_reset_seconds":
        return min(start + entry["seconds"] * 1000, (start // 86400000 + 1) * 86400000)
    elif unit == "days":
        return start + entry["days"] * 86400000
    elif unit == "week":
        return start + 7 * 86400000
    elif unit == "month":
        # Get first day of next month
        start_dt = datetime.datetime.fromtimestamp(start/1000, tz=datetime.timezone.utc)
        if start_dt.month == 12:
            next_month = datetime.datetime(start_dt.year + 1, 1, 1, tzinfo=datetime.timezone.utc)
        else:
            next_month = datetime.datetime(start_dt.year, start_dt.month + 1, 1, tzinfo=datetime.timezone.utc)
        return int(next_month.timestamp() * 1000)
    else:
        raise ValueError(f"Unsupported unit '{unit}' for timeframe '{tf}'")


def resample(bars_1m: list, tf: str, registry: dict) -> list:
    """
    Resample 1m bars to the given timeframe tf.
    Returns closed bars only (no partial trailing buckets).
    Gap count is computed and reported but not filled.
    """
    if not bars_1m:
        return []
    
    if tf not in registry["timeframes"]:
        raise ValueError(f"Timeframe '{tf}' not found in registry")
    
    # Group bars by bucket
    buckets = {}
    for bar in bars_1m:
        start = bucket_start(bar["t"], tf, registry)
        if start not in buckets:
            buckets[start] = []
        buckets[start].append(bar)
    
    # Compute results for each bucket
    result = []
    last_bar_close_ms = bars_1m[-1]["t"] + 60000
    
    for bucket_start_ms, bars_in_bucket in sorted(buckets.items()):
        # Skip buckets that haven't closed yet
        if bucket_end(bucket_start_ms, tf, registry) > last_bar_close_ms:
            continue
            
        # Compute OHLCV stats
        o = bars_in_bucket[0]["o"]
        c = bars_in_bucket[-1]["c"]
        h = max(bar["h"] for bar in bars_in_bucket)
        l = min(bar["l"] for bar in bars_in_bucket)
        
        v = 0
        for bar in bars_in_bucket:
            v += bar.get("v", 0)
            
        n_bars = len(bars_in_bucket)
        
        # Compute expected minutes per bucket
        entry = registry["timeframes"][tf]
        unit = entry["unit"]
        if unit == "seconds":
            n_expected = entry["seconds"] // 60
        elif unit == "days":
            n_expected = entry["days"] * 1440
        elif unit == "week":
            n_expected = 10080
        elif unit in ("month", "day_reset_seconds"):
            n_expected = (bucket_end(bucket_start_ms, tf, registry) - bucket_start_ms) // 60000
        else:
            raise ValueError(f"Unsupported unit '{unit}' for timeframe '{tf}'")
            
        gap_count = max(0, n_expected - n_bars)
        
        result.append({
            "t": bucket_start_ms,
            "o": o,
            "h": h,
            "l": l,
            "c": c,
            "v": v,
            "gap_count": gap_count,
            "n_bars": n_bars
        })
    
    return result
