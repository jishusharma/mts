"""
Pure core of the testnet live alert runner.

This module contains the decision logic for running registered layers on closed bars,
detecting new alerts, and formatting them for emission. It never fetches data, writes files,
places orders, or filters signals - it only calls registered layer functions and formats outputs.

All functions are pure (no side effects) and use only stdlib.
"""

from MyTradingSys.backtest.layers.alerts.alert_emitter import format_alert, new_alerts
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.layers.rsi.rsi_ma import rsi_ma as _rsi_ma

MAX_EMITTED = 2000


def latest_closed_t(bars: list) -> int:
    """
    Get the timestamp of the latest closed bar.
    
    Args:
        bars: List of bar dictionaries with at least a "t" key (int epoch ms).
        
    Returns:
        The timestamp of the latest bar.
        
    Raises:
        ValueError: If bars is empty or not strictly ascending by "t".
    """
    if not bars:
        raise ValueError("Bars list cannot be empty")
    
    for i in range(len(bars) - 1):
        if bars[i]["t"] >= bars[i + 1]["t"]:
            raise ValueError("Bars must be strictly ascending by 't'")
            
    return bars[-1]["t"]


def build_registry(entries: list) -> dict:
    """
    Build a registry from a list of layer entries.
    
    Args:
        entries: List of dictionaries describing registered layers with keys:
                 "layer" (str), "sub" (str), "tf" (str), "fn" (callable), "params_id" (str).
                 
    Returns:
        Dictionary mapping registry keys to entry dictionaries.
        
    Raises:
        ValueError: If any entry is missing required keys or if duplicate keys are found.
    """
    registry = {}
    
    for entry in entries:
        required_keys = {"layer", "sub", "tf", "fn", "params_id"}
        if not all(key in entry for key in required_keys):
            missing = required_keys - set(entry.keys())
            raise ValueError(f"Entry missing required keys: {missing}")
            
        key = f'{entry["layer"]}|{entry["sub"]}|{entry["tf"]}'
        
        if key in registry:
            raise ValueError(f"Duplicate registration for key: {key}")
            
        registry[key] = entry
        
    return registry


def empty_state() -> dict:
    """
    Create a fresh state dictionary.
    
    Returns:
        A new state dictionary with empty last_t and prev_events.
    """
    return {"last_t": {}, "prev_events": {}}


def run_registry(registry: dict, bars_by_tf: dict, state: dict) -> dict:
    """
    Run all registered layers on their respective bar histories and detect new alerts.
    
    Args:
        registry: Output of build_registry().
        bars_by_tf: Dictionary mapping timeframes to lists of closed bars.
        state: Current state dictionary (from empty_state() or loaded from disk).
        
    Returns:
        Dictionary with keys "alerts", "state", and "errors".
    """
    new_last_t = dict(state.get("last_t", {}))
    new_prev_events = dict(state.get("prev_events", {}))
    emitted = list(state.get("emitted", []))
    emitted_set = set(emitted)
    alerts = []
    errors = []
    
    for key, entry in registry.items():
        tf = entry["tf"]
        bars = bars_by_tf.get(tf)
        
        if not bars:
            continue
            
        try:
            latest = latest_closed_t(bars)
            prev_last = state.get("last_t", {}).get(tf)
            
            if prev_last is not None and latest <= prev_last:
                continue
                
            events = entry["fn"](bars)
            
            if not isinstance(events, list):
                raise TypeError(f"Layer function must return a list, got {type(events)}")
                
            prev_events_list = state.get("prev_events", {}).get(key, [])
            fresh = new_alerts(prev_events_list, events)
            
            # Only events at most `confirm_lag_bars` (+1 bar slack) behind the latest closed bar are actionable ("t" is
            # the bar open time; each layer declares how many bars after its "t" it can first be seen, default 0):
            # older events are history (first run / restart / window slide) and must never be emitted as live alerts.
            # On a fresh state (no prev_events for this key) there is no slack beyond the layer's own lag (min 1 bar,
            # the behaviour since 6ad9fd0): the layer's confirmation bar, never older backlog.
            bar_ms = (bars[-1]["t"] - bars[-2]["t"]) if len(bars) > 1 else 0
            lag = int(entry.get("confirm_lag_bars", 0))
            allowed = max(lag, 1) if key not in state.get("prev_events", {}) else lag + 1
            fresh = [e for e in fresh if e.get("t") is not None and e["t"] >= latest - allowed * bar_ms]
            rsi_v = rsi_ma_v = None
            if fresh:
                # None only if history is shorter than the RSI warm-up (live runs have ~99 bars).
                try:
                    rs = rsi_core([b["c"] for b in bars], period=14)
                    rsi_v = rs[-1] if rs else None
                    ma = _rsi_ma(rs, "SMA", 14)
                    rsi_ma_v = ma[-1] if ma else None
                except (KeyError, ValueError, TypeError):
                    rsi_v = rsi_ma_v = None
            for event in fresh:
                ekey = f'{key}|{event.get("t")}|{event.get("event")}'
                if ekey in emitted_set:
                    continue
                emitted_set.add(ekey)
                emitted.append(ekey)
                alert = format_alert(entry["layer"], entry["sub"], tf, event, entry["params_id"],
                                     rsi_value=rsi_v, rsi_ma_value=rsi_ma_v)
                alert["t_confirm"] = latest  # open time of the latest closed bar when first seen (auto-trader ages from it)
                alerts.append(alert)
                
            new_prev_events[key] = events
            new_last_t[tf] = latest
            
        except Exception as exc:
            errors.append({"key": key, "error": str(exc)})
            continue
            
    return {"alerts": alerts, "state": {"last_t": new_last_t, "prev_events": new_prev_events,
                                                        "emitted": emitted[-MAX_EMITTED:]}, "errors": errors}
