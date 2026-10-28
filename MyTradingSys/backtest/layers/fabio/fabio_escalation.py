"""
MyTradingSys/backtest/layers/fabio/fabio_escalation.py - FAB-002 ("aggression that fails to break a protected level = absorption") and FAB-003
("escalating aggression -- a record-volume, record-delta bar -- into an already-absorbed level =
expect a BREAKOUT in the aggressor's direction, not a reversal").

Both are quoted UNDEFINED on exact thresholds ("really aggressive" delta size, how many attempts, "all-time high on volume" reference
window) -- every threshold below is this module's own explicit grid parameter, not from the video.
"""

from MyTradingSys.backtest.layers.cryptocred.cc_structure import find_swings

def bar_delta(bar: dict) -> float:
    """Returns `2 * bar["tbv"] - bar["v"]`."""
    return 2 * bar["tbv"] - bar["v"]

def escalation_events(bars: list, left: int = 2, right: int = 2, use_body: bool = True, level_tolerance: float = 0.001, aggression_k: float = 2.0, record_lookback: int = 20) -> list:
    if level_tolerance < 0:
        raise ValueError("level_tolerance must be >= 0")
    if aggression_k <= 0:
        raise ValueError("aggression_k must be > 0")
    if record_lookback < 1:
        raise ValueError("record_lookback must be >= 1")

    # Get confirmed swings
    swings = find_swings(bars, left, right, use_body)
    confirmed_swing_map = {s["i"]: s for s in swings if s["confirmed_i"] <= len(bars) - 1}

    result = []
    level_states = {}  # level_i -> {"first_absorbed_i": int or None, "absorbed": bool}

    # Process each confirmed swing
    for lvl in swings:
        if lvl["confirmed_i"] >= len(bars):
            continue

        level_i = lvl["i"]
        level_states[level_i] = {"first_absorbed_i": None, "absorbed": False}

        # Scan bars from confirmed_i + 1 onwards
        i = lvl["confirmed_i"] + 1
        while i < len(bars):
            bar = bars[i]
            is_at_level = False

            if lvl["kind"] == "high":
                is_at_level = abs(bar["h"] - lvl["price"]) <= lvl["price"] * level_tolerance
            else:  # low
                is_at_level = abs(bar["l"] - lvl["price"]) <= lvl["price"] * level_tolerance

            if not is_at_level:
                i += 1
                continue

            # Compute average delta for the window ending at i (excluding i itself)
            start_window = max(0, i - record_lookback)
            if start_window >= i:
                # No prior data to compute avg_abs_delta
                i += 1
                continue

            window_deltas = [abs(bar_delta(bars[j])) for j in range(start_window, i)]
            avg_abs_delta = sum(window_deltas) / len(window_deltas)

            delta = bar_delta(bar)
            is_aggressive = abs(delta) >= aggression_k * avg_abs_delta

            if not is_aggressive or delta == 0:
                i += 1
                continue

            # Determine direction of the aggressive test
            direction = "up" if delta > 0 else "down"

            # Check absorption condition (FAB-002)
            absorbed = False
            if lvl["kind"] == "high" and direction == "up":
                # For a high level tested with an up aggressive test, it's absorbed if close does not break through
                if bar["c"] <= lvl["price"] * (1 + level_tolerance):
                    absorbed = True
            elif lvl["kind"] == "low" and direction == "down":
                # For a low level tested with a down aggressive test, it's absorbed if close does not break through
                if bar["c"] >= lvl["price"] * (1 - level_tolerance):
                    absorbed = True

            if absorbed and level_states[level_i]["first_absorbed_i"] is None:
                level_states[level_i]["first_absorbed_i"] = i
                level_states[level_i]["absorbed"] = True
                # Continue to look for escalation after this absorption
                i += 1
                continue

            # If we've already absorbed, check for escalation (FAB-003)
            if level_states[level_i]["first_absorbed_i"] is not None:
                first_absorbed_i = level_states[level_i]["first_absorbed_i"]
                if i <= first_absorbed_i:
                    i += 1
                    continue

                # Check if this bar is an aggressive test of the same level and direction
                start_window_k = max(0, i - record_lookback)
                window_deltas_k = [abs(bar_delta(bars[j])) for j in range(start_window_k, i)]
                avg_abs_delta_k = sum(window_deltas_k) / len(window_deltas_k)

                delta_k = bar_delta(bars[i])
                is_aggressive_k = abs(delta_k) >= aggression_k * avg_abs_delta_k

                if not is_aggressive_k or delta_k == 0:
                    i += 1
                    continue

                direction_k = "up" if delta_k > 0 else "down"
                if direction_k != direction:
                    i += 1
                    continue

                # Check record volume and delta conditions (FAB-003)
                window_volumes = [bars[j]["v"] for j in range(start_window_k, i + 1)]
                window_deltas_magnitude = [abs(bar_delta(bars[j])) for j in range(start_window_k, i + 1)]

                max_volume = max(window_volumes)
                max_delta = max(window_deltas_magnitude)

                if bars[i]["v"] == max_volume and abs(delta_k) == max_delta:
                    # Fire escalation event
                    result.append({
                        "t": bar["t"],
                        "i": i,
                        "level_i": level_i,
                        "level_price": lvl["price"],
                        "level_kind": lvl["kind"],
                        "side": "long" if direction == "up" else "short",
                        "kind": "escalation_breakout",
                        "absorbed_i": first_absorbed_i,
                        "escalation_i": i,
                        "delta_k": delta_k,
                        "volume_k": bars[i]["v"]
                    })
                    # Stop scanning this level after firing
                    break

            i += 1

    # Sort events by index ascending
    result.sort(key=lambda x: x["i"])
    return result
