"""
D2's "rsi_ma support" feature — RSI pulls back to its own MA line (within tolerance) and closes back on the trend side
-> `ma_support` / `ma_rejection`. Separate feature, switchable, per timeframe.

Implemented by composing the already-verified rsi_events band state machine on the (rsi - rsi_ma) difference series
(rsi_events.py Case E1 in layers/rsi/TEST_PLAN.md is the state machine this reuses unchanged).

Note: "cross" and "failure" outcomes keep their rs_events names since D2 only names the two touch-and-hold outcomes.
The "level_value" -> "rsi_ma_value" field substitution is made because the reference line (rsi_ma) moves every bar
here, unlike rsi_events' fixed level.
"""

from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events

def rsi_ma_events(rsi: list, rsi_ma: list, ts: list, tolerance: float, direction_names: tuple = ("above", "below")) -> list:
    if tolerance <= 0:
        raise ValueError("tolerance must be > 0")
    if len(rsi) != len(ts) or len(rsi_ma) != len(ts):
        raise ValueError("rsi, rsi_ma and ts must have the same length")
    
    # Build diff list: None where either series is None (warm-up or gap)
    diff = [None if (rsi[i] is None or rsi_ma[i] is None) else rsi[i] - rsi_ma[i] for i in range(len(ts))]
    
    # Call rsi_events on the difference series with level=0.0
    events = rsi_events(diff, ts, level=0.0, tolerance=tolerance, direction_names=direction_names)
    
    # Transform event names and add rs_ma_value
    result = []
    for event in events:
        # Rename support/rejection to ma_support/ma_rejection
        if event["event"] == "support":
            event["event"] = "ma_support"
        elif event["event"] == "rejection":
            event["event"] = "ma_rejection"
        
        # Add rsi_ma_value at the resolving bar
        t_index = ts.index(event["t"])
        event["rsi_ma_value"] = rsi_ma[t_index]
        
        # Remove level_value (misleading here since reference line moves)
        del event["level_value"]
        
        result.append(event)
    
    return result
