"""
MalkanView 40/60 regime classifier plus single-timeframe bull/bear bounce setups.

Cites:
- MLK-R1 (regime/range-shift, WEB_RESEARCH.md lines 39-62 and 84-89: "Whenever the market is bearish,
  it won't be able to cross 60 ... whenever in a bullish trend, it won't be able to cross 40")
- MLK-S1 (Bullish candlestick forms at 40 RSI level on daily chart = buy signal)
- MLK-S2 (Bearish candlestick forms at 60 RSI level on daily chart = short signal)

D2 rule: the 40/60 numbers are private to malkan_40_60. No other module imports them.
This file is the one place those numbers may live as defaults.

MLK-GAP1: The real Malkan 5-star setup gates a Daily entry on Monthly AND Weekly RSI regime
(a 3-timeframe composition). This module implements the single-timeframe mechanics only:
regime + 40/60 bounce/reject + entry-candle color. A caller must run it once per timeframe
(via the timeframe layer, D1) and combine results itself to reconstruct the full multi-timeframe setup.

Source: MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md (medium-high confidence)
"""

from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events


def malkan_regime(rsi: list, lo: float = 40.0, hi: float = 60.0, lookback: int = 20) -> list:
    """
    Identical algorithm to the scoped `rsi_regime`: returns a list the same length as `rsi`.
    A value at index `i` requires exactly `lookback` consecutive non-`None` `rsi` values ending at `i`
    (walking backward from `i`, collecting non-`None` values until `lookback` are found or the start
    of the series is reached without enough — if not enough, output `None` at `i`).
    Given the window: `min_rsi = min(window)`, `max_rsi = max(window)`.
    `"BULL"` if `min_rsi >= lo and max_rsi >= hi`.
    Else `"BEAR"` if `max_rsi <= hi and min_rsi <= lo`.
    Else `"RANGE"`.
    Raise `ValueError` if not `0 < lo < hi < 100`, or if `lookback < 1`.
    """
    if not (0 < lo < hi < 100):
        raise ValueError("lo and hi must satisfy 0 < lo < hi < 100")
    if lookback < 1:
        raise ValueError("lookback must be at least 1")

    result = [None] * len(rsi)
    for i in range(len(rsi)):
        window = []
        j = i
        while len(window) < lookback and j >= 0:
            if rsi[j] is not None:
                window.append(rsi[j])
            j -= 1

        if len(window) == lookback:
            min_rsi = min(window)
            max_rsi = max(window)
            if min_rsi >= lo and max_rsi >= hi:
                result[i] = "BULL"
            elif max_rsi <= hi and min_rsi <= lo:
                result[i] = "BEAR"
            else:
                result[i] = "RANGE"
        # else: leave as None

    return result


def malkan_setup_bull(bars: list, rsi: list, regime: list, level: float = 40.0, tolerance: float = 2.0, require_bullish_candle: bool = True) -> list:
    """
    [MLK-S1, MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md lines 108-134:
    "Bullish candlestick forms at 40 RSI level on daily chart = buy signal"]
    `bars` is a list of dicts with at least `o`,`c`,`t` (same shape as elsewhere in this codebase),
    same length and index-alignment as `rsi`/`regime`.
    `ts = [b["t"] for b in bars]`.
    Call `events = rsi_events(rsi, ts, level=level, tolerance=tolerance)`.
    For each event in `events` with `event["event"] == "support"` (RSI approached `level` from above
    and bounced back up — a level=40 support in an uptrend is exactly the Malkan bull bounce):
    find the bar `b` in `bars` whose `"t" == event["t"]`; look up that bar's index `i` (via the `ts`
    list) to read `regime[i]`. Skip this event if `regime[i] != "BULL"` [MLK-GAP1: the full 5-star
    setup gates on Monthly+Weekly RSI regime; this single-timeframe module uses this timeframe's own
    `malkan_regime` as the simplified regime gate — document this simplification in the module docstring].
    If `require_bullish_candle` is True, also skip if `b["c"] <= b["o"]` (not a bullish/green candle).
    Otherwise emit `{"t": event["t"], "side": "long", "rule_id": "MLK-S1", "event": "support",
    "level_value": level, "regime": regime[i]}`.
    Return one signal per qualifying event, sorted ascending by `"t"`. Return `[]` if there are no
    qualifying events (this is the normal case, not an error — do not raise).
    """
    ts = [b["t"] for b in bars]
    events = rsi_events(rsi, ts, level=level, tolerance=tolerance)
    signals = []
    for event in events:
        if event["event"] == "support":
            t = event["t"]
            i = ts.index(t)  # Find index of bar with timestamp t
            if regime[i] != "BULL":
                continue
            b = bars[i]
            if require_bullish_candle and b["c"] <= b["o"]:
                continue
            signals.append({
                "t": t,
                "side": "long",
                "rule_id": "MLK-S1",
                "event": "support",
                "level_value": level,
                "regime": regime[i]
            })
    return sorted(signals, key=lambda x: x["t"])


def malkan_setup_bear(bars: list, rsi: list, regime: list, level: float = 60.0, tolerance: float = 2.0, require_bearish_candle: bool = True) -> list:
    """
    [MLK-S2, WEB_RESEARCH.md lines 135-159: "Bearish candlestick forms at 60 RSI level on daily chart = short signal"]
    Mirror of `malkan_setup_bull`: `events = rsi_events(rsi, ts, level=level, tolerance=tolerance)`;
    use `event["event"] == "rejection"` (RSI approached `level` from below and got rejected back down
    — the Malkan bear bounce/reject at 60). Skip unless `regime[i] == "BEAR"`.
    If `require_bearish_candle`, skip unless `b["c"] < b["o"]` (a bearish/red candle).
    Emit `{"t": event["t"], "side": "short", "rule_id": "MLK-S2", "event": "rejection",
    "level_value": level, "regime": regime[i]}`.
    Return one signal per qualifying event, sorted ascending by `"t"`.
    """
    ts = [b["t"] for b in bars]
    events = rsi_events(rsi, ts, level=level, tolerance=tolerance)
    signals = []
    for event in events:
        if event["event"] == "rejection":
            t = event["t"]
            i = ts.index(t)  # Find index of bar with timestamp t
            if regime[i] != "BEAR":
                continue
            b = bars[i]
            if require_bearish_candle and b["c"] >= b["o"]:
                continue
            signals.append({
                "t": t,
                "side": "short",
                "rule_id": "MLK-S2",
                "event": "rejection",
                "level_value": level,
                "regime": regime[i]
            })
    return sorted(signals, key=lambda x: x["t"])
