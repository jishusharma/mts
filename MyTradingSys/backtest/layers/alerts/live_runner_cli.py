"""
Thin IO/CLI shell around sibling module `live_runner_core.py` (not yet on disk when this task was packed).

This module fetches closed Binance klines over public REST, wires two registered layers (RSI and FABIO CVD),
and calls sibling module 085's pure core every poll. Alert-only: no orders, no execution imports, no keys,
no mainnet (public market-data endpoint only).
"""

import json
import pathlib
import argparse
import time
import urllib.request
import urllib.parse
import sys

from MyTradingSys.backtest.layers.alerts.alert_emitter import append_alerts_jsonl
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events
from MyTradingSys.backtest.layers.fabio.fabio_cvd_absorption import cvd_absorption_events


def klines_to_bars(raw: list) -> list:
    """
    Pure mapper, no network. `raw` is Binance `/api/v3/klines` response format:
    a list of rows, each row a list/tuple of at least 10 elements
    `[open_time_ms, open, high, low, close, volume, close_time_ms, quote_asset_volume, num_trades,
    taker_buy_base_asset_volume, taker_buy_quote_asset_volume, ignore]` (strings or numbers -- cast with
    `int`/`float`). Raise `ValueError` if any row has fewer than 10 elements. Map each row `r` to
    `{"t": int(r[0]), "o": float(r[1]), "h": float(r[2]), "l": float(r[3]), "c": float(r[4]),
    "v": float(r[5]), "tbv": float(r[9])}` (same bar shape as `bt_data.load_klines`: `t/o/h/l/c/v/tbv`).
    Return the mapped list in the same order as `raw` (do not sort or filter here). Return `[]` if `raw`
    is empty.
    """
    if not raw:
        return []
    
    bars = []
    for r in raw:
        if len(r) < 10:
            raise ValueError("Each row must have at least 10 elements")
        bar = {
            "t": int(r[0]),
            "o": float(r[1]),
            "h": float(r[2]),
            "l": float(r[3]),
            "c": float(r[4]),
            "v": float(r[5]),
            "tbv": float(r[9])
        }
        bars.append(bar)
    
    return bars


def fetch_closed_bars(fetch_fn, symbol: str, interval: str, limit: int = 100) -> list:
    """
    Fetches closed bars using `fetch_fn` and processes them.
    Drops the last possibly-open row to ensure only closed bars are returned.
    Raises `ValueError` if fewer than 2 bars are returned or if bars are not strictly ascending by time.
    """
    raw = fetch_fn(symbol, interval, limit)
    bars = klines_to_bars(raw)
    
    if len(bars) < 2:
        raise ValueError("Not enough closed bars returned")
        
    # Drop the last possibly-open bar
    closed = bars[:-1]
    
    # Check strictly ascending by time
    for i in range(1, len(closed)):
        if closed[i]["t"] <= closed[i-1]["t"]:
            raise ValueError("Bars are not strictly ascending by time")
            
    return closed


def default_fetch_klines(symbol: str, interval: str, limit: int) -> list:
    """
    Real network call (not unit-tested; tests only use the injectable `fetch_fn` above).
    Builds URL and fetches from Binance's public market-data endpoint.
    """
    url = "https://api.binance.com/api/v3/klines?" + urllib.parse.urlencode({
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    })
    
    with urllib.request.urlopen(url, timeout=10) as resp:
        body = resp.read()
        
    return json.loads(body)


def load_state(path) -> dict:
    """
    Loads the state from a JSON file.
    If the file does not exist, returns an empty state.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"last_t": {}, "prev_events": {}}


def save_state(state: dict, path) -> None:
    """
    Saves the state to a JSON file.
    Creates parent directories if needed.
    """
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(state, f, sort_keys=True, indent=2)


def build_default_registry() -> dict:
    """
    Builds and returns a registry for two registered layers: RSI and FABIO CVD.
    More layers can be added in the same way in future work.
    """
    def _rsi_layer_fn(bars):
        closes = [b["c"] for b in bars]
        ts = [b["t"] for b in bars]
        rsi = rsi_core(closes, period=14)
        return rsi_events(rsi, ts, level=40.0, tolerance=0.5)

    def _fabio_cvd_layer_fn(bars):
        return cvd_absorption_events(bars)

    entries = [
        {
            "layer": "rsi",
            "sub": "rsi_events",
            "tf": "1h",
            "fn": _rsi_layer_fn,
            "params_id": "rsi_40_tol0.5_L1_2026-09-29"
        },
        {
            "layer": "rsi",
            "sub": "rsi_events",
            "tf": "15m",
            "fn": _rsi_layer_fn,
            "params_id": "rsi_40_tol0.5_L1_2026-09-29"
        },
        {
            "layer": "fabio",
            "sub": "cvd_absorption",
            "tf": "1h",
            "fn": _fabio_cvd_layer_fn,
            "params_id": "fabio_cvd_default_2026-09-29"
        }
    ]
    
    # Import here to avoid circular dependency
    from MyTradingSys.backtest.layers.alerts.live_runner_core import build_registry
    
    return build_registry(entries)


def poll_once(registry: dict, symbol: str, tfs: list, fetch_fn, state: dict, limit: int = 100) -> dict:
    """
    Polls for closed bars from multiple timeframes and runs the registry.
    """
    bars_by_tf = {}
    fetch_errors = []
    
    for tf in sorted(set(tfs)):
        try:
            bars_by_tf[tf] = fetch_closed_bars(fetch_fn, symbol, tf, limit)
        except Exception as exc:
            fetch_errors.append({"key": f"fetch:{tf}", "error": str(exc)})
    
    # Import here to avoid circular dependency
    from MyTradingSys.backtest.layers.alerts.live_runner_core import run_registry
    
    result = run_registry(registry, bars_by_tf, state)
    
    return {
        "alerts": result["alerts"],
        "state": result["state"],
        "errors": fetch_errors + result["errors"]
    }


def main(argv=None) -> int:
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--tfs", default="1h,15m")
    parser.add_argument("--state-path", default="MyTradingSys/runtime/live_alert_state.json")
    parser.add_argument("--alerts-dir", default="MyTradingSys/runtime/alerts")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--poll-seconds", type=int, default=60)
    parser.add_argument("--once", action="store_true")
    
    args = parser.parse_args(argv)
    
    registry = build_default_registry()
    state = load_state(args.state_path)
    
    def loop_body():
        nonlocal state
        result = poll_once(registry, args.symbol, args.tfs.split(","), default_fetch_klines, state, args.limit)
        
        # Group alerts by timeframe
        alerts_by_tf = {}
        for alert in result["alerts"]:
            tf = alert["tf"]
            if tf not in alerts_by_tf:
                alerts_by_tf[tf] = []
            alerts_by_tf[tf].append(alert)
            
        # Write alerts to JSONL files
        for tf, group in alerts_by_tf.items():
            append_alerts_jsonl(group, pathlib.Path(args.alerts_dir) / f"{tf}.jsonl")
            
        save_state(result["state"], args.state_path)
        state = result["state"]
        
        print(f"alerts={len(result['alerts'])} errors={len(result['errors'])}")
        
        # Print errors to stderr
        for error in result["errors"]:
            print(json.dumps(error), file=sys.stderr)
            
    if args.once:
        loop_body()
        return 0
        
    try:
        while True:
            loop_body()
            time.sleep(args.poll_seconds)
    except KeyboardInterrupt:
        print("stopped")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
