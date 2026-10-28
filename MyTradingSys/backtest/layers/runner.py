"""
Implements the D3 forward-return study machinery ("Measured per timeframe x level x event type:
event count, forward return after N bars (N = 1, 3, 5, 10, 20), hit rate vs a no-event baseline,
max adverse move") and the D5 run manifest.

This module computes forward returns from events against a close-price series, with
"max adverse move" computed from CLOSE prices only (no separate intrabar high/low in this module's
inputs). A caller with real OHLC bars that wants a true intrabar max-adverse-excursion should compute
it upstream and is not required to use this module's mae field.

This module never touches the filesystem, source revisions, or the network itself — build_manifest's
caller is responsible for computing revision_hash and data_file_hashes (e.g. via the repository's own
source-revision lookup and file hashing) before calling in.
"""

import hashlib
import uuid


def forward_return_stats(events: list, closes: list, horizons: tuple = (1, 3, 5, 10, 20)) -> dict:
    """
    Computes forward return statistics for events against a close-price series.

    Args:
        events: List of dicts with keys "i" (int index into closes) and "side" ("long" or "short")
        closes: List of closing prices
        horizons: Tuple of horizon periods to compute stats for

    Returns:
        Dict keyed by horizon integers, each containing:
            {"n": int, "mean_return": float or None, "hit_rate": float or None, "mae": float or None}

    Raises:
        ValueError: if closes is empty or any event has invalid side
    """
    if not closes:
        raise ValueError("closes cannot be empty")

    for e in events:
        if e["side"] not in ("long", "short"):
            raise ValueError(f"Invalid side '{e['side']}' in event {e}")

    result = {}
    for h in horizons:
        contributing_events = []
        for e in events:
            i = e["i"]
            side = e["side"]
            sgn = 1.0 if side == "long" else -1.0
            if i + h >= len(closes):
                continue

            ret = sgn * (closes[i + h] - closes[i]) / closes[i]
            # Compute mae: min sgn * (closes[j] - closes[i]) / closes[i] for j in [i+1, i+h]
            mae_vals = []
            for j in range(i + 1, min(i + h, len(closes) - 1) + 1):
                mae_val = sgn * (closes[j] - closes[i]) / closes[i]
                mae_vals.append(mae_val)
            mae = min(mae_vals)

            contributing_events.append({"ret": ret, "mae": mae})

        if not contributing_events:
            result[h] = {"n": 0, "mean_return": None, "hit_rate": None, "mae": None}
        else:
            n = len(contributing_events)
            mean_return = sum(e["ret"] for e in contributing_events) / n
            hit_rate = sum(1 for e in contributing_events if e["ret"] > 0) / n
            mae = sum(e["mae"] for e in contributing_events) / n
            result[h] = {"n": n, "mean_return": mean_return, "hit_rate": hit_rate, "mae": mae}

    return result


def baseline_return_stats(closes: list, horizons: tuple = (1, 3, 5, 10, 20)) -> dict:
    """
    Computes baseline forward return statistics over every bar in closes as an implicit long-only event.

    Args:
        closes: List of closing prices
        horizons: Tuple of horizon periods to compute stats for

    Returns:
        Dict keyed by horizon integers, each containing:
            {"n": int, "mean_return": float or None, "hit_rate": float or None, "mae": float or None}

    Raises:
        ValueError: if closes is empty
    """
    if not closes:
        raise ValueError("closes cannot be empty")

    # Create synthetic events for every bar as long-only events
    events = [{"i": i, "side": "long"} for i in range(len(closes))]
    return forward_return_stats(events, closes, horizons)


def build_manifest(revision_hash: str, params_id: str, data_file_hashes: dict, command: str,
                   start: str, end: str, row_counts: dict, **extra) -> dict:
    """
    Builds a run manifest dictionary with required fields and any extra fields.

    Args:
        revision_hash: Repository's current source-revision identifier
        params_id: Unique identifier for the parameter set used
        data_file_hashes: Dict mapping data file names to their hashes
        command: The command that was executed
        start: Start date/time of the backtest
        end: End date/time of the backtest
        row_counts: Dict mapping table names to row counts
        **extra: Any additional fields to include in the manifest

    Returns:
        Complete manifest dictionary with run_id and all input fields plus extras
    """
    # Generate a reasonably unique run_id from start and a hash of other fields
    manifest_str = f"{start}_{revision_hash}_{params_id}_{command}_{row_counts}"
    run_id = hashlib.md5(manifest_str.encode()).hexdigest()[:8]
    if not run_id:
        run_id = str(uuid.uuid4())[:8]

    return {
        "run_id": run_id,
        "revision_hash": revision_hash,
        "params_id": params_id,
        "data_file_hashes": data_file_hashes,
        "command": command,
        "start": start,
        "end": end,
        "row_counts": row_counts,
        **extra
    }
