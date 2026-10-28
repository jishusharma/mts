"""
D3 tolerance study machinery for RSI events.

Parameters swept: tolerance 0 to 5 RSI points in 0.5 steps (symmetric band only).
Measured per timeframe x level x event type: event count, forward return after N bars,
hit rate vs a no-event baseline, max adverse move.

Note: this module implements the symmetric-tolerance case only.
Asymmetric above/below sweep would require changing rsi_events' signature,
which is out of scope here (see SCOPE NOTE in task description).

Chosen tolerance: best out-of-sample on walk-forward splits, then the existing PBO check
(D3) is NOT implemented by pick_best_tolerance — it only picks the best IN-SAMPLE mean return
at one horizon, and a caller doing real tolerance selection must run this per split and
cross-check with bt/ref_pbo.py separately; this is a deliberate scope line, not a missing feature.
"""

from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events
from MyTradingSys.backtest.layers.runner import forward_return_stats


def event_side(event: dict) -> str:
    """
    Maps one `rsi_events` event dict to a trade side string, "long" or "short", or None if this
    event type has no directional trading interpretation for this driver.

    Rule (this driver's own heuristic, not a D2/D3 rule — document as such):
    "support" -> "long" (RSI held above the level, bullish continuation).
    "rejection" -> "short" (RSI held below the level, bearish continuation).
    "cross" -> "long" if event["direction"] == "up" else "short".
    "failure" -> None (the level broke; ambiguous, excluded from the directional study — do not guess a side for it).
    """
    if event["event"] == "support":
        return "long"
    elif event["event"] == "rejection":
        return "short"
    elif event["event"] == "cross":
        return "long" if event["direction"] == "up" else "short"
    elif event["event"] == "failure":
        return None
    else:
        raise ValueError(f"Unknown event type: {event['event']}")


def sweep_tolerances(rsi: list, ts: list, closes: list, level: float, tolerances: tuple = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0), horizons: tuple = (1, 3, 5, 10, 20)) -> dict:
    """
    Sweeps symmetric tolerance band over a grid and computes forward return statistics.

    Assumes ts values are usable as indices into closes (i.e., ts == list(range(len(rsi))).
    For each tolerance in tolerances (skip silently if tol <= 0):
        call rsi_events(rsi, ts, level=level, tolerance=tol)
        Build runner_events list:
            for each event in events, let side = event_side(event);
            skip the event if side is None;
            otherwise append {"i": event["t"], "side": side}
        Call forward_return_stats(runner_events, closes, horizons=horizons)
        Store sweep[tol] = {"n_events_total": len(events), "n_events_scored": len(runner_events), "stats": stats}
    Return sweep (dict keyed by tolerance floats given in tolerances, in the order given).
    Raise ValueError if closes is empty.
    """
    if not closes:
        raise ValueError("closes must not be empty")

    sweep = {}
    for tol in tolerances:
        if tol <= 0:
            continue
        events = rsi_events(rsi, ts, level=level, tolerance=tol)
        runner_events = []
        for event in events:
            side = event_side(event)
            if side is not None:
                runner_events.append({"i": event["t"], "side": side})
        stats = forward_return_stats(runner_events, closes, horizons=horizons)
        sweep[tol] = {
            "n_events_total": len(events),
            "n_events_scored": len(runner_events),
            "stats": stats
        }
    return sweep


def pick_best_tolerance(sweep: dict, horizon: int, min_events: int = 5) -> float:
    """
    Among the tolerances in sweep whose stats[horizon]["n"] is not None and >= min_events,
    return the tolerance with the highest stats[horizon]["mean_return"].
    Return None if no tolerance qualifies (too few events at every tolerance for this horizon).
    Ties: return the SMALLEST qualifying tolerance (prefer a tighter band when two tolerances tie on mean return).

    Raise KeyError if horizon is not a key of every per-tolerance stats dict in sweep.
    """
    for data in sweep.values():
        if horizon not in data["stats"]:
            raise KeyError(f"Horizon {horizon} not found in all tolerance stats")

    best_tol = None
    best_mean_return = None

    for tol in sorted(sweep.keys()):
        stats = sweep[tol]["stats"]
        n = stats[horizon]["n"]
        if n is not None and n >= min_events:
            mean_return = stats[horizon]["mean_return"]
            if mean_return is not None and (best_mean_return is None or mean_return > best_mean_return):
                best_mean_return = mean_return
                best_tol = tol

    return best_tol
