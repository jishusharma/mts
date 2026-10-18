import sys
sys.dont_write_bytecode = True
"""T086 / G3: Shadow Fills vs Testnet Fills Comparison Utility.

Builds a read-only comparison utility comparing testnet fills against shadow fills
(first trade at or through the order price on the public Binance/Deribit tape)
side by side, without changing GO_LIVE_BAR.md (operator decision q-gap-b 2026-10-15).

References:
- SOURCED: MyTradingSys/research/backtest_gap_review_2026-10-13/REPORT.md:129-131
  "Fix: log a shadow fill for every testnet order, computed from the real market tape
   at the same timestamps (Binance aggTrades, already fetchable), and measure the
   go-live bar on shadow fills; testnet fills become a plumbing check."
- SOURCED: MyTradingSys/backtest/maker_model.py:34 TICK = 0.5
  Deribit BTC-PERPETUAL tick size (0.5 USD).
- SOURCED: MyTradingSys/backtest/maker_model.py:8
  "gap through the stop fills at the bar open"
- SOURCED: MyTradingSys/system/GO_LIVE_BAR.md:6-15
  GO-LIVE BAR criteria (retained per operator decision q-gap-b).
"""
import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# SOURCED: MyTradingSys/backtest/maker_model.py:34 TICK = 0.5
DEFAULT_TICK = 0.5


def compute_slip_bp(side: str, order_type: str, order_px: float, fill_px: float) -> float:
    """Computes signed adverse slippage in basis points relative to order price.
    
    Positive = adverse (buyer paid more, seller received less).
    Negative = favourable (buyer paid less, seller received more).
    """
    if order_px <= 0:
        return 0.0
    sgn = 1.0 if side.lower() in ("buy", "long") else -1.0
    # For a BUY: (fill_px - order_px) / order_px * 1e4
    # For a SELL: (order_px - fill_px) / order_px * 1e4
    adverse_diff = sgn * (fill_px - order_px)
    return (adverse_diff / order_px) * 10000.0


def score_order_against_bars(
    order: Dict[str, Any],
    bars: List[Dict[str, Any]],
    tick: float = DEFAULT_TICK,
) -> Dict[str, Any]:
    """Scores an order record against 1m OHLCV bars for touch and trade-through fills.
    
    Order schema:
      - side: 'buy'/'long' or 'sell'/'short'
      - order_type: 'limit' or 'stop'/'market'
      - price: limit or stop trigger price
      - placed_time: ms timestamp
      - window_ms: optional lifetime in ms (None = unlimited)
      - testnet_status: 'filled' or 'no_fill'/'cancelled'
      - testnet_fill_price: float or None
      - testnet_fill_time: ms timestamp or None
    """
    side = str(order.get("side", "buy")).lower()
    sgn = 1.0 if side in ("buy", "long") else -1.0
    order_type = str(order.get("order_type", "limit")).lower()
    is_limit = order_type == "limit"
    price = float(order["price"])
    placed_t = int(order.get("placed_time", 0))
    window_ms = order.get("window_ms")
    end_t = (placed_t + int(window_ms)) if window_ms is not None else float("inf")

    touch_filled = False
    touch_fill_time = None
    touch_fill_price = None

    through_filled = False
    through_fill_time = None
    through_fill_price = None

    # Filter and sort candidate bars
    valid_bars = [b for b in bars if placed_t <= b["timestamp"] <= end_t]
    valid_bars.sort(key=lambda b: b["timestamp"])

    for bar in valid_bars:
        t_bar = bar["timestamp"]
        op = float(bar["open"])
        hi = float(bar["high"])
        lo = float(bar["low"])

        if is_limit:
            # BUY limit: touch when low <= price; through when low <= price - tick
            # SELL limit: touch when high >= price; through when high >= price + tick
            bar_touch = (lo <= price) if sgn > 0 else (hi >= price)
            bar_through = (lo <= price - tick) if sgn > 0 else (hi >= price + tick)

            if bar_touch and not touch_filled:
                touch_filled = True
                touch_fill_time = t_bar
                touch_fill_price = price

            if bar_through and not through_filled:
                through_filled = True
                through_fill_time = t_bar
                through_fill_price = price

        else:
            # STOP order:
            # BUY stop: triggers when high >= price; through when high >= price + tick
            # SELL stop: triggers when low <= price; through when low <= price - tick
            bar_touch = (hi >= price) if sgn > 0 else (lo <= price)
            bar_through = (hi >= price + tick) if sgn > 0 else (lo <= price - tick)

            if bar_touch and not touch_filled:
                touch_filled = True
                touch_fill_time = t_bar
                # SOURCED: maker_model.py:8 gap through stop fills at bar open
                if (sgn > 0 and op >= price) or (sgn < 0 and op <= price):
                    touch_fill_price = op
                else:
                    touch_fill_price = price

            if bar_through and not through_filled:
                through_filled = True
                through_fill_time = t_bar
                if (sgn > 0 and op >= price) or (sgn < 0 and op <= price):
                    through_fill_price = op
                else:
                    through_fill_price = price

        if touch_filled and through_filled:
            break

    # Slippages
    touch_slip_bp = (
        compute_slip_bp(side, order_type, price, touch_fill_price)
        if touch_filled and touch_fill_price is not None
        else None
    )
    through_slip_bp = (
        compute_slip_bp(side, order_type, price, through_fill_price)
        if through_filled and through_fill_price is not None
        else None
    )

    # Testnet fields
    t_status = str(order.get("testnet_status", "")).lower()
    testnet_filled = t_status == "filled"
    testnet_fill_price = float(order["testnet_fill_price"]) if order.get("testnet_fill_price") is not None else None
    testnet_fill_time = order.get("testnet_fill_time")
    testnet_slip_bp = (
        compute_slip_bp(side, order_type, price, testnet_fill_price)
        if testnet_filled and testnet_fill_price is not None
        else None
    )

    # Discrepancy
    slip_discrepancy = None
    if testnet_slip_bp is not None and touch_slip_bp is not None:
        slip_discrepancy = testnet_slip_bp - touch_slip_bp

    return {
        "order_id": order.get("order_id"),
        "side": side,
        "order_type": order_type,
        "price": price,
        "placed_time": placed_t,
        "touch_filled": touch_filled,
        "touch_fill_time": touch_fill_time,
        "touch_fill_price": touch_fill_price,
        "touch_slip_bp": touch_slip_bp,
        "through_filled": through_filled,
        "through_fill_time": through_fill_time,
        "through_fill_price": through_fill_price,
        "through_slip_bp": through_slip_bp,
        "testnet_filled": testnet_filled,
        "testnet_fill_time": testnet_fill_time,
        "testnet_fill_price": testnet_fill_price,
        "testnet_slip_bp": testnet_slip_bp,
        "slip_discrepancy_bp": slip_discrepancy,
        "phantom_touch": testnet_filled and not touch_filled,
        "phantom_through": testnet_filled and not through_filled,
    }


def score_order_against_trades(
    order: Dict[str, Any],
    trades: List[Dict[str, Any]],
    tick: float = DEFAULT_TICK,
) -> Dict[str, Any]:
    """Scores an order record against individual trades (e.g. aggTrades)."""
    side = str(order.get("side", "buy")).lower()
    sgn = 1.0 if side in ("buy", "long") else -1.0
    order_type = str(order.get("order_type", "limit")).lower()
    is_limit = order_type == "limit"
    price = float(order["price"])
    placed_t = int(order.get("placed_time", 0))
    window_ms = order.get("window_ms")
    end_t = (placed_t + int(window_ms)) if window_ms is not None else float("inf")

    touch_filled = False
    touch_fill_time = None
    touch_fill_price = None

    through_filled = False
    through_fill_time = None
    through_fill_price = None

    valid_trades = [tr for tr in trades if placed_t <= tr["timestamp"] <= end_t]
    valid_trades.sort(key=lambda tr: tr["timestamp"])

    for tr in valid_trades:
        t_tr = tr["timestamp"]
        px = float(tr["price"])

        if is_limit:
            bar_touch = (px <= price) if sgn > 0 else (px >= price)
            bar_through = (px <= price - tick) if sgn > 0 else (px >= price + tick)

            if bar_touch and not touch_filled:
                touch_filled = True
                touch_fill_time = t_tr
                touch_fill_price = price

            if bar_through and not through_filled:
                through_filled = True
                through_fill_time = t_tr
                through_fill_price = price

        else:
            bar_touch = (px >= price) if sgn > 0 else (px <= price)
            bar_through = (px >= price + tick) if sgn > 0 else (px <= price - tick)

            if bar_touch and not touch_filled:
                touch_filled = True
                touch_fill_time = t_tr
                touch_fill_price = px

            if bar_through and not through_filled:
                through_filled = True
                through_fill_time = t_tr
                through_fill_price = px

        if touch_filled and through_filled:
            break

    touch_slip_bp = (
        compute_slip_bp(side, order_type, price, touch_fill_price)
        if touch_filled and touch_fill_price is not None
        else None
    )
    through_slip_bp = (
        compute_slip_bp(side, order_type, price, through_fill_price)
        if through_filled and through_fill_price is not None
        else None
    )

    t_status = str(order.get("testnet_status", "")).lower()
    testnet_filled = t_status == "filled"
    testnet_fill_price = float(order["testnet_fill_price"]) if order.get("testnet_fill_price") is not None else None
    testnet_fill_time = order.get("testnet_fill_time")
    testnet_slip_bp = (
        compute_slip_bp(side, order_type, price, testnet_fill_price)
        if testnet_filled and testnet_fill_price is not None
        else None
    )

    slip_discrepancy = None
    if testnet_slip_bp is not None and touch_slip_bp is not None:
        slip_discrepancy = testnet_slip_bp - touch_slip_bp

    return {
        "order_id": order.get("order_id"),
        "side": side,
        "order_type": order_type,
        "price": price,
        "placed_time": placed_t,
        "touch_filled": touch_filled,
        "touch_fill_time": touch_fill_time,
        "touch_fill_price": touch_fill_price,
        "touch_slip_bp": touch_slip_bp,
        "through_filled": through_filled,
        "through_fill_time": through_fill_time,
        "through_fill_price": through_fill_price,
        "through_slip_bp": through_slip_bp,
        "testnet_filled": testnet_filled,
        "testnet_fill_time": testnet_fill_time,
        "testnet_fill_price": testnet_fill_price,
        "testnet_slip_bp": testnet_slip_bp,
        "slip_discrepancy_bp": slip_discrepancy,
        "phantom_touch": testnet_filled and not touch_filled,
        "phantom_through": testnet_filled and not through_filled,
    }


def compare_orders_side_by_side(
    orders: List[Dict[str, Any]],
    tape: List[Dict[str, Any]],
    tick: float = DEFAULT_TICK,
    tape_type: str = "bars",
) -> Dict[str, Any]:
    """Compares a collection of testnet/paper orders against public tape."""
    score_fn = score_order_against_bars if tape_type == "bars" else score_order_against_trades
    scored = [score_fn(o, tape, tick=tick) for o in orders]
    n = len(orders)

    if n == 0:
        return {
            "n_orders": 0,
            "testnet_fill_count": 0,
            "testnet_fill_rate": 0.0,
            "shadow_touch_fill_count": 0,
            "shadow_touch_fill_rate": 0.0,
            "shadow_through_fill_count": 0,
            "shadow_through_fill_rate": 0.0,
            "phantom_touch_count": 0,
            "phantom_touch_rate": 0.0,
            "phantom_through_count": 0,
            "phantom_through_rate": 0.0,
            "testnet_mean_slip_bp": 0.0,
            "shadow_touch_mean_slip_bp": 0.0,
            "shadow_through_mean_slip_bp": 0.0,
            "mean_slip_discrepancy_bp": 0.0,
            "scored_orders": [],
        }

    t_filled = sum(1 for s in scored if s["testnet_filled"])
    touch_filled = sum(1 for s in scored if s["touch_filled"])
    through_filled = sum(1 for s in scored if s["through_filled"])

    p_touch = sum(1 for s in scored if s["phantom_touch"])
    p_through = sum(1 for s in scored if s["phantom_through"])

    t_slips = [s["testnet_slip_bp"] for s in scored if s["testnet_slip_bp"] is not None]
    touch_slips = [s["touch_slip_bp"] for s in scored if s["touch_slip_bp"] is not None]
    through_slips = [s["through_slip_bp"] for s in scored if s["through_slip_bp"] is not None]
    discrepancies = [s["slip_discrepancy_bp"] for s in scored if s["slip_discrepancy_bp"] is not None]

    def _mean(arr):
        return sum(arr) / len(arr) if arr else 0.0

    return {
        "n_orders": n,
        "testnet_fill_count": t_filled,
        "testnet_fill_rate": t_filled / n,
        "shadow_touch_fill_count": touch_filled,
        "shadow_touch_fill_rate": touch_filled / n,
        "shadow_through_fill_count": through_filled,
        "shadow_through_fill_rate": through_filled / n,
        "phantom_touch_count": p_touch,
        "phantom_touch_rate": p_touch / n,
        "phantom_through_count": p_through,
        "phantom_through_rate": p_through / n,
        "testnet_mean_slip_bp": _mean(t_slips),
        "shadow_touch_mean_slip_bp": _mean(touch_slips),
        "shadow_through_mean_slip_bp": _mean(through_slips),
        "mean_slip_discrepancy_bp": _mean(discrepancies),
        "scored_orders": scored,
    }


def format_side_by_side_table(summary: Dict[str, Any]) -> str:
    """Formats summary metrics into a clean markdown side-by-side comparison table."""
    n = summary["n_orders"]
    t_rate = summary["testnet_fill_rate"] * 100.0
    touch_rate = summary["shadow_touch_fill_rate"] * 100.0
    through_rate = summary["shadow_through_fill_rate"] * 100.0
    p_touch_rate = summary["phantom_touch_rate"] * 100.0
    p_through_rate = summary["phantom_through_rate"] * 100.0

    lines = [
        "| Metric | Testnet Fills (Synthetic) | Shadow Touch (Real Tape) | Shadow Trade-Through (Real Tape) |",
        "|---|---|---|---|",
        f"| Total Orders Evaluated | {n} | {n} | {n} |",
        f"| Fills Count | {summary['testnet_fill_count']} | {summary['shadow_touch_fill_count']} | {summary['shadow_through_fill_count']} |",
        f"| Fill Rate (%) | {t_rate:.1f}% | {touch_rate:.1f}% | {through_rate:.1f}% |",
        f"| Phantom Fills vs Real Tape | 0 (baseline) | {summary['phantom_touch_count']} ({p_touch_rate:.1f}%) | {summary['phantom_through_count']} ({p_through_rate:.1f}%) |",
        f"| Mean Adverse Slippage (bp) | {summary['testnet_mean_slip_bp']:.2f} bp | {summary['shadow_touch_mean_slip_bp']:.2f} bp | {summary['shadow_through_mean_slip_bp']:.2f} bp |",
        f"| Slippage Discrepancy (bp) | 0.00 bp | {summary['mean_slip_discrepancy_bp']:.2f} bp | {summary['testnet_mean_slip_bp'] - summary['shadow_through_mean_slip_bp']:.2f} bp |",
    ]
    return "\n".join(lines)


def load_orders_jsonl(path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Loads order records from a JSONL file."""
    orders = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    orders.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return orders


def load_bars_csv(path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Loads 1m bars from CSV file (columns: timestamp,open,high,low,close,volume)."""
    bars = []
    with open(path, "r", encoding="utf-8") as f:
        headers = None
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if headers is None:
                headers = [h.lower() for h in parts]
                continue
            row = dict(zip(headers, parts))
            bars.append({
                "timestamp": int(float(row.get("timestamp") or row.get("open_time") or 0)),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row.get("volume", 0.0)),
            })
    return bars


def main():
    parser = argparse.ArgumentParser(description="G3 Shadow Fills vs Testnet Comparison Utility")
    parser.add_argument("--orders", type=str, help="Path to orders JSONL file")
    parser.add_argument("--bars", type=str, help="Path to 1m bars CSV file")
    parser.add_argument("--tick", type=float, default=DEFAULT_TICK, help="Instrument tick size (default 0.5 USD)")
    args = parser.parse_args()

    if args.orders and args.bars:
        orders = load_orders_jsonl(args.orders)
        bars = load_bars_csv(args.bars)
        summary = compare_orders_side_by_side(orders, bars, tick=args.tick)
        print(format_side_by_side_table(summary))
    else:
        print("Running built-in DEV demonstration fixture:")
        # Demo fixture
        bars = [
            {"timestamp": 0, "open": 80050.0, "high": 80100.0, "low": 80000.0, "close": 80020.0, "volume": 10.0},
            {"timestamp": 60000, "open": 80020.0, "high": 80030.0, "low": 79990.0, "close": 80010.0, "volume": 15.0},
            {"timestamp": 120000, "open": 80010.0, "high": 80500.0, "low": 80000.0, "close": 80480.0, "volume": 10.0},
            {"timestamp": 180000, "open": 79750.0, "high": 79780.0, "low": 79700.0, "close": 79720.0, "volume": 12.0},
        ]
        orders = [
            {"order_id": "ord_1", "placed_time": 0, "side": "buy", "order_type": "limit", "price": 80000.0, "amount": 10.0, "testnet_status": "filled", "testnet_fill_price": 80000.0, "testnet_fill_time": 0},
            {"order_id": "ord_2", "placed_time": 0, "side": "sell", "order_type": "limit", "price": 80500.0, "amount": 10.0, "testnet_status": "filled", "testnet_fill_price": 80500.0, "testnet_fill_time": 120000},
            {"order_id": "ord_3", "placed_time": 0, "side": "sell", "order_type": "limit", "price": 81000.0, "amount": 10.0, "testnet_status": "filled", "testnet_fill_price": 81000.0, "testnet_fill_time": 10000},
            {"order_id": "ord_4", "placed_time": 0, "side": "buy", "order_type": "limit", "price": 79000.0, "amount": 10.0, "testnet_status": "no_fill"},
            {"order_id": "ord_5", "placed_time": 0, "side": "sell", "order_type": "stop", "price": 79800.0, "amount": 10.0, "testnet_status": "filled", "testnet_fill_price": 79800.0, "testnet_fill_time": 180000},
        ]
        summary = compare_orders_side_by_side(orders, bars, tick=DEFAULT_TICK)
        print(format_side_by_side_table(summary))


if __name__ == "__main__":
    main()
