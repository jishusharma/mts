"""
MyTradingSys/backtest/layers/cryptocred/cc_structure.py - CryptoCred Market Structure (C08) swing detection and MSB classification.

Interpretation choices:
- Fixed-width fractal for swing detection (C08-Rule1)
- "Break most recent lower-high/higher-low by close" as minimal mechanical form of sequence-violation definition (C08-E01, C08-E05)
- Range-extreme close as proxy for "not noise" (C08-E03)
Implements cluster C08 (MSB Definition & Significance) from MyTradingSys/research/cross_trader_consolidated.md.
"""

def find_swings(bars: list, left: int = 2, right: int = 2, use_body: bool = True) -> list:
    if not bars:
        raise ValueError("bars must not be empty")
    if left < 1 or right < 1:
        raise ValueError("left and right must be >= 1")

    def body_high(bar):
        return max(bar["o"], bar["c"]) if use_body else bar["h"]

    def body_low(bar):
        return min(bar["o"], bar["c"]) if use_body else bar["l"]

    result = []
    for i in range(left, len(bars) - right):
        current_bar = bars[i]
        is_high = True
        is_low = True

        # Check left side
        for j in range(i - left, i):
            if body_high(current_bar) <= body_high(bars[j]):
                is_high = False
            if body_low(current_bar) >= body_low(bars[j]):
                is_low = False

        # Check right side
        for j in range(i + 1, i + right + 1):
            if body_high(current_bar) <= body_high(bars[j]):
                is_high = False
            if body_low(current_bar) >= body_low(bars[j]):
                is_low = False

        if is_high:
            result.append({
                "i": i,
                "t": current_bar["t"],
                "price": body_high(current_bar),
                "kind": "high",
                "confirmed_i": i + right
            })
        elif is_low:
            result.append({
                "i": i,
                "t": current_bar["t"],
                "price": body_low(current_bar),
                "kind": "low",
                "confirmed_i": i + right
            })

    return result


def is_range_extreme(bars: list, i: int, lookback: int = 50, extreme_pct: float = 0.25) -> bool:
    if not bars:
        raise ValueError("bars must not be empty")
    start = max(0, i - lookback)
    relevant_bars = bars[start:i]
    if len(relevant_bars) < 2:
        return False

    range_hi = max(b["h"] for b in relevant_bars)
    range_lo = min(b["l"] for b in relevant_bars)
    span = range_hi - range_lo
    if span <= 0:
        return False

    close = bars[i]["c"]
    return close >= range_hi - extreme_pct * span or close <= range_lo + extreme_pct * span


def classify_msb(bars: list, swings: list, require_prior_sequence: bool = True, filter_range_noise: bool = False, range_lookback: int = 50, range_extreme_pct: float = 0.25) -> list:
    if not bars or not swings:
        raise ValueError("bars and swings must not be empty")

    swing_highs = [s for s in swings if s["kind"] == "high"]
    swing_lows = [s for s in swings if s["kind"] == "low"]

    events = []

    # Bullish MSB candidates
    for i in range(1, len(swing_highs)):
        H_prev = swing_highs[i - 1]
        H_last = swing_highs[i]

        if require_prior_sequence and H_last["price"] >= H_prev["price"]:
            continue

        start_idx = max(H_last["i"], H_last["confirmed_i"])
        for k in range(start_idx + 1, len(bars)):
            if bars[k]["c"] > H_last["price"]:
                events.append({
                    "t": bars[k]["t"],
                    "i": k,
                    "direction": "bull",
                    "broken_level": H_last["price"],
                    "broken_swing_i": H_last["i"],
                    "confirm_i": k,
                    "at_range_extreme": is_range_extreme(bars, k, range_lookback, range_extreme_pct)
                })
                break

    # Bearish MSB candidates
    for i in range(1, len(swing_lows)):
        L_prev = swing_lows[i - 1]
        L_last = swing_lows[i]

        if require_prior_sequence and L_last["price"] <= L_prev["price"]:
            continue

        start_idx = max(L_last["i"], L_last["confirmed_i"])
        for k in range(start_idx + 1, len(bars)):
            if bars[k]["c"] < L_last["price"]:
                events.append({
                    "t": bars[k]["t"],
                    "i": k,
                    "direction": "bear",
                    "broken_level": L_last["price"],
                    "broken_swing_i": L_last["i"],
                    "confirm_i": k,
                    "at_range_extreme": is_range_extreme(bars, k, range_lookback, range_extreme_pct)
                })
                break

    if filter_range_noise:
        events = [e for e in events if e["at_range_extreme"]]

    return sorted(events, key=lambda x: x["i"])

