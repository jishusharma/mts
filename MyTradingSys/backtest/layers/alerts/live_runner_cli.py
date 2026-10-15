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


# Bars between an event's "t" and the first closed bar on which the detector can report it (measured by
# replaying 7 days of BTCUSDT 15m/1h through a sliding 99-bar window, 2026-09-29). Every layer's t is its
# confirmation bar except volume_fvg (its scan stops one bar short of the newest bar, so a touch shows up 1 bar
# later). live_runner_core allows this lag + 1 bar of slack (0 slack on a fresh state).
CONFIRM_LAG_BARS = {"volume_fvg": 1}


# ---- Fabio v3 live emitter (staged MTS-2026-10-02-1930Z-CLI-BLD-fabio-v3-shadow) -----------------------------------
# Decision per grid parameter, from research/FABIO_V3_SOURCING_2026-10-02.md: SOURCE = a Fabio quote gives the numeric
# value; SHADOW = it does not (NS-grid). A cell is SOURCE only if every parameter it uses is SOURCE. A SOURCE signal is
# an ordinary fabio.* alert (has "side", the auto-trader maps it). A SHADOW signal is collection-only: tagged
# `collection_only`, carries `shadow_side` and NO "side" and no layer_rules entry, so the auto-trader's layer_side()
# returns None and it rejects the alert as unmapped (same pattern as turn_of_candle). No order path exists here.
FABIO_V3_DECISIONS = {"N": "SHADOW", "p": "SHADOW", "z_hi": "SHADOW", "m_c": "SHADOW", "f": "SHADOW"}
FABIO_V3_GRID = {"N": (60, 120, 240), "p": (0.05, 0.10), "z_hi": (2.0, 2.5, 3.0), "m_c": (5, 15), "f": (0.003, 0.005)}
# Not grid-expanded here (spec 7.2 main grid values): day gate off, confirm entry (a discrete SIGNAL on one bar; the
# resting-limit ARMED state persists across bars and is not an event), event management.
FABIO_V3_FIXED = {"g": "off", "entry_mode": "confirm", "mgmt": "event"}
FABIO_V3_FLOW_COLS = ("buy_vol", "sell_vol", "b99_buy_vol", "b99_sell_vol", "thr_days", "fp")
FABIO_V3_PARAMS_ID = "fabio_v3_grid_2026-10-02"


def fabio_v3_cells(grid=None):
    """Cartesian product of the grid as a list of dicts (stable order)."""
    import itertools
    grid = FABIO_V3_GRID if grid is None else grid
    keys = list(grid)
    return [dict(zip(keys, vals)) for vals in itertools.product(*(grid[k] for k in keys))]


def fabio_v3_cell_decision(cell, decisions=None):
    """"SOURCE" only if every parameter of the cell is SOURCE; a missing or unknown decision is SHADOW (fail closed)."""
    decisions = FABIO_V3_DECISIONS if decisions is None else decisions
    return "SOURCE" if cell and all(decisions.get(k) == "SOURCE" for k in cell) else "SHADOW"


def fabio_v3_flow_window(bars):
    """The partial NY window (open .. last closed bar) of 1m ORDER-FLOW bars, or None. Order-flow bars carry
    aggTrades columns (FABIO_V3_FLOW_COLS); plain Binance klines ({t,o,h,l,c,v,tbv}) do not, so on a klines feed this
    returns None and the layer is silent (poll line shows 0). Also None if the window has a gap, is empty, or any bar
    has thr_days == 0 (own-day big-trade thresholds = look-ahead, spec section 1)."""
    import datetime as dt
    from MyTradingSys.backtest.layers.fabio.v3.day_gates import ny_open_utc
    if not bars or any(c not in bars[-1] for c in FABIO_V3_FLOW_COLS):
        return None
    last = bars[-1]["t"]
    opener = ny_open_utc(dt.datetime.fromtimestamp(last / 1000.0, dt.timezone.utc).date())
    if opener is None:
        return None
    t0 = int(opener.timestamp() * 1000)
    win = [b for b in bars if t0 <= b["t"] <= last]
    if not win or win[0]["t"] != t0 or len(win) != (last - t0) // 60000 + 1:
        return None
    if any(b.get("thr_days", 0) == 0 for b in win):
        return None
    return win


FABIO_V3_OF_DIR = pathlib.Path(__file__).resolve().parents[4] / "MyTradingSys" / "runtime" / "orderflow_live"


def fabio_v3_live_flow(bars, of_dir=None):
    """Default flow source of the v3 layer. Bars that already carry the order-flow columns are used as given. On the
    klines feed (no such columns) the live order-flow writer's files (orderflow_live.py, R3) are read and cut at the last
    closed kline's open time, so the layer and the registry agree on "now". Any read problem, a gap, thr_days == 0 or a
    missing file -> None (silent, fail closed)."""
    win = fabio_v3_flow_window(bars)
    if win or not bars:
        return win
    try:
        from MyTradingSys.backtest.layers.fabio.orderflow_live import load_live_bars
        last = bars[-1]["t"]
        # a NY window is at most 390 bars: read only the last ~7 h
        of = [b for b in load_live_bars(of_dir or FABIO_V3_OF_DIR, since_ms=last - 7 * 3600 * 1000) if b["t"] <= last]
    except Exception:  # noqa: BLE001
        return None
    if not of or of[-1]["t"] != last:      # the writer is behind the klines: stale window, stay silent
        return None
    return fabio_v3_flow_window(of)


def make_fabio_v3_layer(grid=None, decisions=None, fixed=None, run_fn=None, flow_fn=None):
    """Layer function fn(bars) -> events for the live registry: one engine run per grid cell, an event per SIGNAL.
    `run_fn(win, config)` defaults to fabio v3 engine.run (imported lazily), `flow_fn(bars)` to fabio_v3_live_flow;
    both injectable for tests. Event "t" = the signal bar's open time, "event" is unique per (cell, model, side)."""
    cells = fabio_v3_cells(grid)
    fixed = dict(FABIO_V3_FIXED if fixed is None else fixed)

    def _layer(bars):
        win = (flow_fn or fabio_v3_live_flow)(bars)
        if not win:
            return []
        run = run_fn
        if run is None:
            from MyTradingSys.backtest.layers.fabio.v3.engine import run
        events = []
        for cell in cells:
            res = run(win, {**cell, **fixed})
            if res.get("verdict") != "SIGNAL":
                continue
            side = {1: "long", -1: "short"}.get(res.get("side"))
            if side is None:
                continue
            decision = fabio_v3_cell_decision(cell, decisions)
            tag = "_".join("%s%s" % (k, cell[k]) for k in cell)
            ev = {"t": win[-1]["t"], "event": "v3_%s_%s_%s" % (tag, res["model"], side), "model": res["model"],
                  "cell": dict(cell), "decision": decision, "entry_ref": res.get("entry"), "stop": res.get("stop"),
                  "target": res.get("target")}
            if decision == "SOURCE":
                ev["side"] = side
            else:
                ev["collection_only"] = True
                ev["shadow_side"] = side
            events.append(ev)
        return events

    return _layer


def build_default_registry(fetch_funding=None) -> dict:
    """
    Builds and returns a registry for two registered layers: RSI and FABIO CVD.
    More layers can be added in the same way in future work.
    """
    def _fabio_cvd_layer_fn(bars):
        return cvd_absorption_events(bars)

    from MyTradingSys.backtest.layers.alerts import live_layers as ll
    _rsi_layer_fn = ll.rsi_level_layer

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
            "layer": "rsi",
            "sub": "rsi_events",
            "tf": "5m",
            "fn": _rsi_layer_fn,
            "params_id": "rsi_40_tol0.5_L1_2026-09-29"
        },
        {
            "layer": "fabio",
            "sub": "cvd_absorption",
            "tf": "1h",
            "fn": _fabio_cvd_layer_fn,
            "params_id": "fabio_cvd_default_2026-09-29"
        },
        {
            "layer": "fabio",
            "sub": "cvd_absorption",
            "tf": "15m",
            "fn": _fabio_cvd_layer_fn,
            "params_id": "fabio_cvd_default_2026-09-29"
        }
    ]
    suffix = "_defaults_2026-09-29"
    for layer, sub, tf, fn in [
        ("fabio", "escalation", "1h", ll.escalation_layer),
        ("fabio", "volume_fvg", "1h", ll.volume_fvg_layer),
        ("session", "session_momentum", "15m", ll.session_momentum_layer),
        ("positioning", "funding_cvd_fade", "1h", ll.make_funding_layer(fetch_funding)),
        ("rsi", "malkan_bull", "1h", ll.malkan_bull_layer),
        ("rsi", "malkan_bear", "1h", ll.malkan_bear_layer),
        ("cryptocred", "sr_flip", "1h", ll.cc_sr_flip_layer),
        ("cryptocred", "fib_pullback", "1h", ll.cc_fib_pullback_layer),
        ("cryptocred", "failed_msb", "1h", ll.cc_failed_msb_layer),
        ("turn_of_candle", "turn_of_candle", "1m", ll.turn_of_candle_layer),
        # 2026-09-30 extra timeframes for fill collection (detectors are bar-index based, tf-agnostic)
        ("fabio", "escalation", "15m", ll.escalation_layer),
        ("fabio", "volume_fvg", "15m", ll.volume_fvg_layer),
        ("cryptocred", "sr_flip", "15m", ll.cc_sr_flip_layer),
        ("cryptocred", "fib_pullback", "15m", ll.cc_fib_pullback_layer),
        ("cryptocred", "failed_msb", "15m", ll.cc_failed_msb_layer),
    ]:
        entries.append({"layer": layer, "sub": sub, "tf": tf, "fn": fn, "params_id": sub + suffix,
                        "confirm_lag_bars": CONFIRM_LAG_BARS.get(sub, 0)})
    # Fabio v3: one key, all grid cells inside (a SHADOW cell is collection-only, see FABIO_V3_DECISIONS)
    entries.append({"layer": "fabio", "sub": "v3_grid", "tf": "1m", "fn": make_fabio_v3_layer(),
                    "params_id": FABIO_V3_PARAMS_ID, "confirm_lag_bars": 0})
    
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
    # Promotion gate (system/PROMOTION_PIPELINE.md): a shadow registry entry, or an unreadable registry, makes the
    # alert collection-only. Empty registry = no change.
    from MyTradingSys.backtest.layers.promotion.registry import apply_promotion_gate
    result["alerts"] = apply_promotion_gate(result["alerts"])
    
    return {
        "alerts": result["alerts"],
        "state": result["state"],
        "errors": fetch_errors + result["errors"]
    }


def format_poll_line(registry: dict, result: dict, now_ms: int = None) -> str:
    """One line per poll: UTC time, totals, then alerts per registered layer key (0 included, so a dead layer
    is visible), then the error count. Pure."""
    import datetime
    now = datetime.datetime.fromtimestamp((now_ms if now_ms is not None else time.time() * 1000) / 1000.0,
                                          datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    counts = {k: 0 for k in registry}
    for a in result["alerts"]:
        k = f'{a["layer"]}|{a["sub"]}|{a["tf"]}'
        counts[k] = counts.get(k, 0) + 1
    per = " ".join(f"{k}={n}" for k, n in sorted(counts.items()))
    return f"poll {now} alerts={len(result['alerts'])} errors={len(result['errors'])} {per}"


def main(argv=None) -> int:
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--tfs", default="1h,15m,5m,1m")
    parser.add_argument("--state-path", default="MyTradingSys/runtime/live_alert_state.json")
    parser.add_argument("--alerts-dir", default="MyTradingSys/runtime/alerts")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--poll-seconds", type=int, default=60)
    parser.add_argument("--consensus-dir", default=None,
                        help="directory for consensus_<date>.jsonl rows (default Dumps/consensus)")
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

        # Consensus row (observation only: never gates a core, never raises). One row per poll in which the Fabio
        # core emitted an alert or the Tom card advanced (research/ARCHITECTURE_TWO_CORES_2026-10-01.md:29-43).
        # Runs after the alert files are written because the rsi block is read back from them.
        try:
            from MyTradingSys.backtest.layers.consensus.hook import consensus_after_poll
            consensus_after_poll(
                result["alerts"], alerts_dir=pathlib.Path(args.alerts_dir),
                state_path=pathlib.Path(args.state_path).with_name("consensus_hook_state.json"),
                base_dir=args.consensus_dir)
        except Exception as exc:  # noqa: BLE001 - observation must never stop the alert runner
            print(json.dumps({"key": "consensus_hook", "error": str(exc)}), file=sys.stderr, flush=True)

        save_state(result["state"], args.state_path)
        state = result["state"]
        
        print(format_poll_line(registry, result), flush=True)
        
        # Print errors to stderr
        for error in result["errors"]:
            print(json.dumps(error), file=sys.stderr, flush=True)
            
    if args.once:
        loop_body()
        return 0
        
    try:
        while True:
            loop_body()
            time.sleep(args.poll_seconds)
    except KeyboardInterrupt:
        print("stopped", flush=True)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
