"""
Unit tests for MyTradingSys/execution/trade_plan_validator.py (hand-computed cases).

Scratch mutation verification:
- Copied MyTradingSys/execution/trade_plan_validator.py to scratch dir and mutated
  line 166 from `_require(total_pct <= 100.0001,` to `_require(total_pct <= 200.0,`.
- Re-ran pytest against the broken scratch copy: 1 failed, 4 passed.
- Failing test: `test_validate_targets_sum_exceeds_100` (AssertionError: `assert True is False`).
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
EXEC_DIR = REPO_ROOT / "MyTradingSys" / "execution"
if str(EXEC_DIR) not in sys.path:
    sys.path.insert(0, str(EXEC_DIR))

import trade_plan_validator as tpv  # noqa: E402


def _base_valid_plan() -> dict:
    """Return a minimal valid market plan (OURS, hand-computed)."""
    return {
        "plan_id": "plan-001",
        "account": "testnet-main",
        "instrument": "BTC-PERPETUAL",
        "side": "LONG",
        "validity": {
            "start": "2026-11-14T00:00:00Z",
            "end": "2026-11-15T00:00:00Z",
        },
        "entry": {"type": "market"},
        "base_unit": 100,
        "stop": {"type": "fixed_percent", "percent_below_entry": 5.0},
        "caps": {
            "max_notional_usd": 100,
            "max_loss_usd": -50,
            "max_concurrent_orders": 2,
        },
    }


def test_validate_normal_ladder_plan():
    """Normal ladder plan at exact order_count (6 <= 6), notional (600 <= 400*1.5), and loss (-500) bounds."""
    plan = _base_valid_plan()
    plan["entry"] = {
        "type": "ladder",
        "range": {"low": 80000, "high": 85000},
        "rungs": 3,
        "size_multipliers": [1, 2, 3],
    }
    plan["targets"] = [
        {"amount_percent": 50, "pnl_target_percent": 2.0},
        {"amount_percent": 50, "pnl_target_percent": 5.0},
    ]
    plan["breakeven_after_first_target"] = True
    plan["caps"] = {
        "max_notional_usd": 400,
        "max_loss_usd": -500,
        "max_concurrent_orders": 6,
    }
    ok, reason = tpv.validate(plan)
    assert ok is True
    assert reason == "OK"


def test_validate_empty_plan():
    """Empty dict fails on the first required field ('plan_id')."""
    ok, reason = tpv.validate({})
    assert ok is False
    assert reason == "missing required field: plan_id"


def test_validate_malformed_iso8601_and_order_cap():
    """Malformed ISO-8601 timestamp and concurrent order count exceeding cap both fail."""
    bad_ts = _base_valid_plan()
    bad_ts["validity"]["start"] = "not-a-timestamp"
    ok, reason = tpv.validate(bad_ts)
    assert ok is False
    assert "validity.start: not a valid ISO-8601 timestamp" in reason

    over_cap = _base_valid_plan()
    over_cap["targets"] = [
        {"amount_percent": 50, "pnl_target_percent": 2.0},
        {"amount_percent": 50, "pnl_target_percent": 5.0},
    ]
    # 1 stop + 1 market entry + 2 targets = 4 concurrent orders > max_concurrent_orders (3)
    over_cap["caps"]["max_concurrent_orders"] = 3
    ok2, reason2 = tpv.validate(over_cap)
    assert ok2 is False
    assert "plan requires 4 concurrent orders" in reason2


def test_validate_targets_sum_exceeds_100():
    """Targets whose amount_percent sums to 105 (> 100.0001) are rejected."""
    plan = _base_valid_plan()
    plan["targets"] = [
        {"amount_percent": 60, "pnl_target_percent": 2.0},
        {"amount_percent": 45, "pnl_target_percent": 5.0},
    ]
    plan["caps"]["max_concurrent_orders"] = 4
    ok, reason = tpv.validate(plan)
    assert ok is False
    assert "targets amount_percent sums to 105, must not exceed 100" in reason


def test_parse_iso8601_z_normalization():
    """_parse_iso8601 normalizes trailing 'Z' to UTC and raises ValidationError on bad input."""
    dt = tpv._parse_iso8601("2026-11-14T09:00:00Z", "validity.start")
    assert dt == datetime(2026, 11, 14, 9, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(tpv.ValidationError):
        tpv._parse_iso8601("invalid-date", "validity.start")
