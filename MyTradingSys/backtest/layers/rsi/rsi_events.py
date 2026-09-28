"""
Generic level and line interactions with a tolerance band: support, rejection, cross.
Works on any level (70/50/30, 40/60) or on the rsi_ma line.

Edge cases handled:
- Exact touch, touch-and-close-back both directions
- Close-through-band failure
- Single-bar band-skip cross
- Multiple resolving band runs at the same level
- An unresolved trailing run
- RSI flat on the level
- Warm-up bars (no RSI yet)
- Data gap mid-series (carry prev_side/run_entry_side across None entries unchanged)

Note: this module is close-based only (it receives a single rsi series with no separate high/low RSI),
so intrabar RSI is explicitly out of scope here.
"""

def rsi_events(rsi: list, ts: list, level: float, tolerance: float, direction_names: tuple = ("above", "below")) -> list:
    if tolerance <= 0:
        raise ValueError("tolerance must be > 0")
    if len(rsi) != len(ts):
        raise ValueError("rsi and ts must have the same length")
    
    # Validate direction_names
    if not isinstance(direction_names, tuple) or len(direction_names) != 2:
        raise ValueError("direction_names must be a tuple of length 2")
    
    above_name, below_name = direction_names
    
    events = []
    prev_side = None
    in_run = False
    run_entry_side = None
    run_start = None  # index where the current run started (for penetration calculation)
    
    for i, rsi_val in enumerate(rsi):
        if rsi_val is None:
            continue
            
        # Classify the current bar
        lower_bound = level - tolerance
        upper_bound = level + tolerance
        
        if rsi_val > upper_bound:
            side = above_name
        elif rsi_val < lower_bound:
            side = below_name
        else:
            side = "band"
            
        if side == "band":
            # If we're not already in a run, start one
            if not in_run:
                in_run = True
                run_entry_side = prev_side
                run_start = i
            continue  # Do not update prev_side while in the band
            
        else:  # side is either above_name or below_name
            # If we were in a run, this bar closes it. A run resolution is never also a
            # cross: the band run is what a same-bar band-skip ("cross") explicitly excludes
            # ("no band run in between"), so the two are mutually exclusive per bar.
            if in_run:
                in_run = False

                # Emit event based on entry side and exit side
                if run_entry_side is not None:
                    if side == run_entry_side:
                        event_type = "support" if side == above_name else "rejection"
                        # support/rejection: deepest dip into the band over the run's band bars.
                        penetration = 0.0
                        for j in range(run_start, i):
                            if rsi[j] is not None:
                                dist = abs(rsi[j] - level)
                                penetration = max(penetration, dist)
                    else:
                        event_type = "failure"
                        # failure: how far past the level the resolving bar closed.
                        penetration = abs(rsi_val - level)

                    events.append({
                        "t": ts[i],
                        "event": event_type,
                        "level_value": level,
                        "tolerance_used": tolerance,
                        "penetration": penetration
                    })
            elif prev_side is not None and prev_side != side:
                # Direct side-to-side flip with no band run in between: a cross.
                events.append({
                    "t": ts[i],
                    "event": "cross",
                    "level_value": level,
                    "tolerance_used": tolerance,
                    "penetration": abs(rsi_val - level),
                    "direction": "up" if side == above_name else "down"
                })

            # Update prev_side for next iteration
            prev_side = side
    
    return events
