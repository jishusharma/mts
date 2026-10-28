"""
Testnet ALERTS-ONLY sink for D1's `bar_closed(tf, bar)` -> layer-event pipeline.

This module formats layer events into D2's alert schema, detects "the event stream changed"
per timeframe, and appends JSONL, one file per timeframe. It never imports execution code,
never places or modifies an order, never filters or gates a Tom or any other layer's signal.
"""

import json
import pathlib
from datetime import datetime


def format_alert(layer: str, sub: str, tf: str, event: dict, params_id: str, rsi_value=None, rsi_ma_value=None) -> dict:
    """
    Build and return one alert dict by merging base keys with event keys.
    
    Args:
        layer: The layer name (e.g., "rsi").
        sub: The sub-layer name (e.g., "rsi_events").
        tf: Timeframe string (e.g., "1h").
        event: Event dictionary from a layer.
        params_id: Unique identifier for the parameter set used.
        rsi_value: Optional RSI value at close time.
        rsi_ma_value: Optional RSI moving average value at close time.
        
    Returns:
        Formatted alert dictionary.
        
    Raises:
        ValueError: If event does not contain a "t" key.
    """
    if "t" not in event:
        raise ValueError("Event must contain a 't' key.")
    
    base = {
        "layer": layer,
        "sub": sub,
        "tf": tf,
        "params_id": params_id,
        "rsi": rsi_value,
        "rsi_ma": rsi_ma_value
    }
    
    result = {**base, **event}
    t_close = result.pop("t")
    result["t_close"] = t_close
    
    return result


def new_alerts(prev_events: list, curr_events: list) -> list:
    """
    Determine which events in curr_events are new compared to prev_events.
    
    An alert is a change in the event stream for one timeframe.
    
    Args:
        prev_events: List of previously seen events.
        curr_events: List of currently seen events.
        
    Returns:
        List of new events that were not present in prev_events.
    """
    prev_set = {(e.get("t"), e.get("event")) for e in prev_events}
    return [e for e in curr_events if (e.get("t"), e.get("event")) not in prev_set]


def append_alerts_jsonl(alerts: list, path) -> int:
    """
    Append alerts to a JSONL file.
    
    Args:
        alerts: List of alert dictionaries.
        path: File path to append to.
        
    Returns:
        Number of lines written (number of alerts).
    """
    if not alerts:
        # Ensure parent directory exists even when no alerts
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        return 0

    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'a', newline='', encoding='utf-8') as f:
        for alert in alerts:
            line = json.dumps(alert, sort_keys=True) + "\n"
            f.write(line)
            
    return len(alerts)

