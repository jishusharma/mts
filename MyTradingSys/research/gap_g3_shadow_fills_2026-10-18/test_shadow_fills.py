import sys
sys.dont_write_bytecode = True
"""Fail-first tests for shadow_fills.py.

Verifies:
1. Touch fill vs trade-through fill logic on 1m bars and trade tapes (TICK = 0.5 USD for BTC-PERPETUAL).
2. Stop-market fill and adverse slippage calculation in basis points (slip_bp).
3. Side-by-side comparison metrics between testnet fills and real shadow tape:
   - Fill rates (testnet vs shadow touch vs shadow trade-through)
   - Phantom fills (filled on testnet, but unreached on real tape)
   - Slippage discrepancy (testnet optimism vs real tape slippage)
"""
import math
from pathlib import Path
import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Fails before shadow_fills.py exists:
import shadow_fills as sf

# SOURCED: MyTradingSys/backtest/maker_model.py:34 TICK = 0.5
TICK = 0.5


def test_touch_vs_trade_through_limit_buy():
    # Synthetic 1m bars
    # Bar 0: Low exactly touches limit (80000.0), but does not trade through (needs <= 79999.5)
    # Bar 1: Low drops to 79990.0, trading through the level
    bars = [
        {"timestamp": 0, "open": 80050.0, "high": 80100.0, "low": 80000.0, "close": 80020.0, "volume": 10.0},
        {"timestamp": 60000, "open": 80020.0, "high": 80030.0, "low": 79990.0, "close": 80010.0, "volume": 15.0},
    ]
    order = {
        "order_id": "ord_buy_1",
        "placed_time": 0,
        "side": "buy",
        "order_type": "limit",
        "price": 80000.0,
        "amount": 100.0,
        "window_ms": 120000,
        "testnet_status": "filled",
        "testnet_fill_price": 80000.0,
        "testnet_fill_time": 0,
    }

    res = sf.score_order_against_bars(order, bars, tick=TICK)
    # Touch model: filled on bar 0
    assert res["touch_filled"] is True
    assert res["touch_fill_time"] == 0
    assert res["touch_fill_price"] == 80000.0
    assert res["touch_slip_bp"] == 0.0

    # Trade-through model: filled on bar 1
    assert res["through_filled"] is True
    assert res["through_fill_time"] == 60000
    assert res["through_fill_price"] == 80000.0
    assert res["through_slip_bp"] == 0.0


def test_touch_vs_trade_through_limit_sell():
    # Bar 0: High touches 80500.0, but does not trade through (needs >= 80500.5)
    # Bar 1: High remains at 80490.0 (no trade through)
    bars = [
        {"timestamp": 0, "open": 80450.0, "high": 80500.0, "low": 80420.0, "close": 80460.0, "volume": 5.0},
        {"timestamp": 60000, "open": 80460.0, "high": 80490.0, "low": 80430.0, "close": 80440.0, "volume": 8.0},
    ]
    order = {
        "order_id": "ord_sell_1",
        "placed_time": 0,
        "side": "sell",
        "order_type": "limit",
        "price": 80500.0,
        "amount": 50.0,
        "window_ms": 120000,
        "testnet_status": "filled",
        "testnet_fill_price": 80500.0,
        "testnet_fill_time": 0,
    }

    res = sf.score_order_against_bars(order, bars, tick=TICK)
    assert res["touch_filled"] is True
    assert res["touch_fill_time"] == 0
    assert res["touch_fill_price"] == 80500.0

    # Trade-through never occurred
    assert res["through_filled"] is False
    assert res["through_fill_time"] is None
    assert res["through_fill_price"] is None


def test_stop_market_fill_and_slippage():
    # SOURCED: MyTradingSys/backtest/maker_model.py:8 gap through the stop fills at the bar open
    # Sell stop order at 79800.0. Bar 0 does not reach; Bar 1 opens gapped at 79750.0.
    bars = [
        {"timestamp": 0, "open": 79850.0, "high": 79860.0, "low": 79820.0, "close": 79830.0, "volume": 4.0},
        {"timestamp": 60000, "open": 79750.0, "high": 79770.0, "low": 79710.0, "close": 79730.0, "volume": 12.0},
    ]
    order_sell_stop = {
        "order_id": "ord_stop_sell",
        "placed_time": 0,
        "side": "sell",
        "order_type": "stop",
        "price": 79800.0,
        "amount": 100.0,
        "window_ms": 120000,
        "testnet_status": "filled",
        "testnet_fill_price": 79800.0,  # Testnet had zero slippage
        "testnet_fill_time": 60000,
    }

    res = sf.score_order_against_bars(order_sell_stop, bars, tick=TICK)
    assert res["touch_filled"] is True
    assert res["touch_fill_price"] == 79750.0  # Fills at bar open
    # Adverse slippage for sell: (stop_px - fill_px) / stop_px * 1e4
    # (79800 - 79750) / 79800 * 10000 = 50 / 79800 * 10000 = 6.26566416... bp [OURS]
    expected_slip = (79800.0 - 79750.0) / 79800.0 * 10000.0
    assert math.isclose(res["touch_slip_bp"], expected_slip, rel_tol=1e-5)

    # Testnet had 0.0 slip, so testnet was optimistic by expected_slip bp
    assert res["testnet_slip_bp"] == 0.0
    assert math.isclose(res["slip_discrepancy_bp"], -expected_slip, rel_tol=1e-5)


def test_trade_level_tape():
    trades = [
        {"timestamp": 1000, "price": 80010.0, "amount": 0.5},
        {"timestamp": 2000, "price": 80000.0, "amount": 1.2},
        {"timestamp": 3000, "price": 79999.0, "amount": 0.8},
    ]
    order = {
        "order_id": "ord_tick_1",
        "placed_time": 500,
        "side": "buy",
        "order_type": "limit",
        "price": 80000.0,
        "amount": 1.0,
        "window_ms": 5000,
        "testnet_status": "filled",
        "testnet_fill_price": 80000.0,
        "testnet_fill_time": 2000,
    }

    res = sf.score_order_against_trades(order, trades, tick=TICK)
    assert res["touch_filled"] is True
    assert res["touch_fill_time"] == 2000
    assert res["touch_fill_price"] == 80000.0

    assert res["through_filled"] is True
    assert res["through_fill_time"] == 3000
    assert res["through_fill_price"] == 80000.0


def test_side_by_side_summary_and_phantom_detection():
    # 5 orders:
    # 1. Filled on testnet, filled on touch and through
    # 2. Filled on testnet, filled on touch, NOT filled on through (touch-only)
    # 3. Filled on testnet, but unreached on shadow tape (PHANTOM fill!)
    # 4. Unfilled on testnet, unfilled on shadow tape
    # 5. Stop order filled on testnet at stop px (0 slip), slipped on shadow tape (gapped 50 USD = 6.2657 bp)
    bars = [
        {"timestamp": 0, "open": 80050.0, "high": 80100.0, "low": 80000.0, "close": 80020.0, "volume": 10.0},
        {"timestamp": 60000, "open": 80020.0, "high": 80030.0, "low": 79990.0, "close": 80010.0, "volume": 15.0},
        {"timestamp": 120000, "open": 80010.0, "high": 80500.0, "low": 80000.0, "close": 80480.0, "volume": 10.0},
        {"timestamp": 180000, "open": 79750.0, "high": 79780.0, "low": 79700.0, "close": 79720.0, "volume": 12.0},
    ]

    orders = [
        # Order 1: Buy limit 80000.0 -> touch at bar 0, through at bar 1
        {
            "order_id": "ord_1",
            "placed_time": 0,
            "side": "buy",
            "order_type": "limit",
            "price": 80000.0,
            "amount": 10.0,
            "window_ms": 300000,
            "testnet_status": "filled",
            "testnet_fill_price": 80000.0,
            "testnet_fill_time": 0,
        },
        # Order 2: Sell limit 80500.0 -> touch at bar 2 (high=80500.0), no through
        {
            "order_id": "ord_2",
            "placed_time": 0,
            "side": "sell",
            "order_type": "limit",
            "price": 80500.0,
            "amount": 10.0,
            "window_ms": 300000,
            "testnet_status": "filled",
            "testnet_fill_price": 80500.0,
            "testnet_fill_time": 120000,
        },
        # Order 3: Sell limit 81000.0 -> max high is 80500.0, never touched on tape! PHANTOM!
        {
            "order_id": "ord_3",
            "placed_time": 0,
            "side": "sell",
            "order_type": "limit",
            "price": 81000.0,
            "amount": 10.0,
            "window_ms": 300000,
            "testnet_status": "filled",
            "testnet_fill_price": 81000.0,
            "testnet_fill_time": 10000,
        },
        # Order 4: Buy limit 79000.0 -> never reached
        {
            "order_id": "ord_4",
            "placed_time": 0,
            "side": "buy",
            "order_type": "limit",
            "price": 79000.0,
            "amount": 10.0,
            "window_ms": 300000,
            "testnet_status": "no_fill",
            "testnet_fill_price": None,
            "testnet_fill_time": None,
        },
        # Order 5: Sell stop 79800.0 -> triggers bar 3, open 79750.0 (50 USD slip = 6.2657 bp)
        {
            "order_id": "ord_5",
            "placed_time": 0,
            "side": "sell",
            "order_type": "stop",
            "price": 79800.0,
            "amount": 10.0,
            "window_ms": 300000,
            "testnet_status": "filled",
            "testnet_fill_price": 79800.0,
            "testnet_fill_time": 180000,
        },
    ]

    summary = sf.compare_orders_side_by_side(orders, bars, tick=TICK)
    assert summary["n_orders"] == 5

    # Testnet: 4 filled (ord_1, ord_2, ord_3, ord_5) -> fill rate = 4/5 = 0.80
    assert summary["testnet_fill_count"] == 4
    assert math.isclose(summary["testnet_fill_rate"], 0.80)

    # Shadow touch: 3 filled (ord_1, ord_2, ord_5) -> fill rate = 3/5 = 0.60
    assert summary["shadow_touch_fill_count"] == 3
    assert math.isclose(summary["shadow_touch_fill_rate"], 0.60)

    # Shadow trade-through: 2 filled (ord_1, ord_5) -> fill rate = 2/5 = 0.40
    assert summary["shadow_through_fill_count"] == 2
    assert math.isclose(summary["shadow_through_fill_rate"], 0.40)

    # Phantom fills:
    # Touch phantom: ord_3 filled on testnet but not on shadow touch -> 1 / 5 = 0.20
    assert summary["phantom_touch_count"] == 1
    assert math.isclose(summary["phantom_touch_rate"], 0.20)

    # Trade-through phantom: ord_2 and ord_3 filled on testnet but not on shadow through -> 2 / 5 = 0.40
    assert summary["phantom_through_count"] == 2
    assert math.isclose(summary["phantom_through_rate"], 0.40)

    # Table formatting
    md_table = sf.format_side_by_side_table(summary)
    assert "Testnet Fills" in md_table
    assert "Shadow Touch" in md_table
    assert "Shadow Trade-Through" in md_table
