"""
Pure core of the testnet live alert runner.

This module contains the decision logic for running registered layers on closed bars,
detecting new alerts, and formatting them for emission. It never fetches data, writes files,
places orders, or filters signals - it only calls registered layer functions and formats outputs.

All functions are pure (no side effects) and use only stdlib.
"""

from MyTradingSys.backtest.layers.alerts.alert_emitter import format_alert, new_alerts


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
            
            for event in fresh:
                alerts.append(format_alert(entry["layer"], entry["sub"], tf, event, entry["params_id"]))
                
            new_prev_events[key] = events
            new_last_t[tf] = latest
            
        except Exception as exc:
            errors.append({"key": key, "error": str(exc)})
            continue
            
    return {"alerts": alerts, "state": {"last_t": new_last_t, "prev_events": new_prev_events}, "errors": errors}
