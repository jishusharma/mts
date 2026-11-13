"""Unit tests for MyTradingSys/backtest/layers/tick/build_tiers.py.

Mutation test record (Step 3):
Mutated copy created in scratch file with flipped branch:
  File: MyTradingSys/backtest/layers/tick/build_tiers.py:36
  Original: a += [x for x in b if x["t"] > last]
  Mutated:  a += [x for x in b if x["t"] <= last]
Resulting failure when pointed at mutated copy:
  MyTradingSys/backtest/layers/tick/test_build_tiers.py::test_klines_all_merges_and_deduplicates failed with:
    AssertionError: assert [1000, 1500, 2000, 2000] == [1000, 2000, 3000]
      At index 1 diff: 1500 != 2000
      Left contains one more item: 2000
"""
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.layers.tick import build_tiers as bt


def test_of_as_klines_normal():
    # SOURCED: "v": d["buy_vol"] + d["sell_vol"], "tbv": d["buy_vol"] (MyTradingSys/backtest/layers/tick/build_tiers.py:42-43)
    # OURS: 10.0 + 5.0 = 15.0 for v, 10.0 for tbv; other fields preserved verbatim
    days = [{"t": 1700000000000, "o": 100.0, "h": 105.0, "l": 95.0, "c": 102.0, "buy_vol": 10.0, "sell_vol": 5.0}]
    result = bt.of_as_klines(days)
    assert result == [{
        "t": 1700000000000,
        "o": 100.0,
        "h": 105.0,
        "l": 95.0,
        "c": 102.0,
        "v": 15.0,
        "tbv": 10.0,
    }]


def test_of_as_klines_empty():
    # SOURCED: [d for d in days] list comprehension over empty input (MyTradingSys/backtest/layers/tick/build_tiers.py:42-43)
    # OURS: empty input list returns empty list []
    assert bt.of_as_klines([]) == []


def test_of_as_klines_malformed_missing_key_raises():
    # SOURCED: requires "t", "o", "h", "l", "c", "buy_vol", "sell_vol" (MyTradingSys/backtest/layers/tick/build_tiers.py:42-43)
    # OURS: dict missing required keys raises KeyError
    with pytest.raises(KeyError):
        bt.of_as_klines([{"t": 1700000000000}])


def test_klines_all_merges_and_deduplicates():
    # SOURCED: last = a[-1]["t"] if a else 0 (MyTradingSys/backtest/layers/tick/build_tiers.py:35)
    # SOURCED: a += [x for x in b if x["t"] > last] (MyTradingSys/backtest/layers/tick/build_tiers.py:36)
    # OURS: with last=2000, b timestamps [1500, 2000, 3000] filtered to [3000], resulting in [1000, 2000, 3000]
    a = [{"t": 1000, "c": 10.0}, {"t": 2000, "c": 20.0}]
    b = [{"t": 1500, "c": 15.0}, {"t": 2000, "c": 20.0}, {"t": 3000, "c": 30.0}]
    with patch("MyTradingSys.backtest.layers.tick.build_tiers.load_klines", side_effect=[a, b]):
        res = bt.klines_all()
    assert [x["t"] for x in res] == [1000, 2000, 3000]


def test_klines_all_empty_first_source():
    # SOURCED: last = a[-1]["t"] if a else 0 (MyTradingSys/backtest/layers/tick/build_tiers.py:35)
    # SOURCED: a.sort(key=lambda x: x["t"]) (MyTradingSys/backtest/layers/tick/build_tiers.py:37)
    # OURS: when a is empty, all entries of b > 0 are retained and sorted ascending by t
    a = []
    b = [{"t": 2000, "c": 20.0}, {"t": 1000, "c": 10.0}]
    with patch("MyTradingSys.backtest.layers.tick.build_tiers.load_klines", side_effect=[a, b]):
        res = bt.klines_all()
    assert [x["t"] for x in res] == [1000, 2000]


def test_flag_rate_normal():
    # SOURCED: n_days = (bars_1m[-1]["t"] - bars_1m[0]["t"]) / 86400000 (MyTradingSys/backtest/layers/tick/build_tiers.py:55)
    # SOURCED: {"days": round(n_days, 1), "flags": len(flags), "per_day": round(len(flags) / n_days, 2), "by": by} (MyTradingSys/backtest/layers/tick/build_tiers.py:60)
    # OURS: 86400000 ms span = 1.0 day; empty tier table produces 0 flags and 0.0 per_day
    bar0 = {"t": 0, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0, "v": 10.0, "tbv": 5.0}
    bar1 = {"t": 86400000, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0, "v": 10.0, "tbv": 5.0}
    res = bt.flag_rate([bar0, bar1], {}, tfs=(1,))
    assert res == {"days": 1.0, "flags": 0, "per_day": 0.0, "by": {}}


def test_flag_rate_empty_bars_raises():
    # SOURCED: tick_extremes.resample: raise ValueError("bars must not be empty") (tick_extremes.py:20)
    # OURS: empty bars_1m raises ValueError from resample
    with pytest.raises(ValueError, match="bars must not be empty"):
        bt.flag_rate([], {})
