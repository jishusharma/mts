def minute_of_quarter(t_ms: int) -> int:
    """Return the minute of the quarter (0-14) for a given timestamp."""
    return (t_ms // 60000) % 15


def toc_minute_stats(bars: list) -> dict:
    """Compute turn-of-candle statistics from a list of bars."""
    if not bars:
        raise ValueError("Bars list is empty")
    
    # Check for zero open prices
    for bar in bars:
        if bar["o"] == 0:
            raise ValueError("Bar has zero open price")

    # Compute returns and group by minute of quarter
    turn_returns = []
    other_returns = []
    by_minute = {}

    for bar in bars:
        t = bar["t"]
        o = bar["o"]
        c = bar["c"]
        
        ret = (c - o) / o
        
        minute = minute_of_quarter(t)
        
        # Track returns by minute
        if minute not in by_minute:
            by_minute[minute] = []
        by_minute[minute].append(ret)
        
        # Categorize into turn or other
        if minute == 0:
            turn_returns.append(ret)
        else:
            other_returns.append(ret)

    # Compute means and counts
    turn_mean = sum(turn_returns) / len(turn_returns) if turn_returns else None
    other_mean = sum(other_returns) / len(other_returns) if other_returns else None
    turn_n = len(turn_returns)
    other_n = len(other_returns)

    # Convert by_minute to mean returns
    by_minute_means = {m: sum(rets) / len(rets) for m, rets in by_minute.items()}

    return {
        "turn_mean": turn_mean,
        "other_mean": other_mean,
        "turn_n": turn_n,
        "other_n": other_n,
        "by_minute": by_minute_means
    }


def turn_of_candle_events(bars: list, lead_minutes: int = 1, side: str = "long") -> list:
    """Generate turn-of-candle events for a list of bars."""
    if not (1 <= lead_minutes <= 14):
        raise ValueError("lead_minutes must be between 1 and 14")

    if side not in ("long", "short"):
        raise ValueError("side must be 'long' or 'short'")

    events = []
    target_minute = 15 - lead_minutes

    for i, bar in enumerate(bars):
        minute = minute_of_quarter(bar["t"])
        if minute == target_minute:
            events.append({"i": i, "side": side})

    return events
