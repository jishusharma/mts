"""
MyTradingSys/backtest/layers/cryptocred/cc_structure.py - CryptoCred Market Structure (C08) swing detection and MSB classification.

Interpretation choices:
- Fixed-width fractal for swing detection (C08-Rule1)
- "Break most recent lower-high/higher-low by close" as minimal mechanical form of sequence-violation definition (C08-E01, C08-E05)
- Range-extreme close as proxy for "not noise" (C08-E03)
Implements cluster C08 (MSB Definition & Significance) from MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md.
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

    # Audit #14 (FORMULAS.md s9): MSB = a close beyond the MOST RECENT confirmed opposing swing
    # at that bar (swing known by that bar, confirmed_i < k), gated by the lower-high / higher-low
    # prior sequence when require_prior_sequence. Each broken swing fires at most once.
    highs = sorted(swing_highs, key=lambda s: s["i"])
    lows = sorted(swing_lows, key=lambda s: s["i"])

    def _scan(side, direction):
        fired = set()
        for k in range(len(bars)):
            known = [s for s in side if s["confirmed_i"] < k and s["i"] < k]
            if not known:
                continue
            last = known[-1]
            if last["i"] in fired:
                continue
            if require_prior_sequence:
                if len(known) < 2:
                    continue
                prev = known[-2]
                if direction == "bull" and last["price"] >= prev["price"]:
                    continue
                if direction == "bear" and last["price"] <= prev["price"]:
                    continue
            close = bars[k]["c"]
            broke = close > last["price"] if direction == "bull" else close < last["price"]
            if broke:
                fired.add(last["i"])
                events.append({
                    "t": bars[k]["t"],
                    "i": k,
                    "direction": direction,
                    "broken_level": last["price"],
                    "broken_swing_i": last["i"],
                    "confirm_i": k,
                    "at_range_extreme": is_range_extreme(bars, k, range_lookback, range_extreme_pct)
                })

    _scan(highs, "bull")
    _scan(lows, "bear")

    if filter_range_noise:
        events = [e for e in events if e["at_range_extreme"]]

    return sorted(events, key=lambda x: x["i"])

