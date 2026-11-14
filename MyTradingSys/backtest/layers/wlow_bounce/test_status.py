"""Unit tests for MyTradingSys/backtest/layers/wlow_bounce/status.py.

Mutation test record (Step 3):
Mutated copy created in scratch file with flipped branch:
  File: MyTradingSys/backtest/layers/wlow_bounce/status.py:38
  Original: return [{"t": int(r[0]), "o": float(r[1]), "h": float(r[2]), "l": float(r[3]), "c": float(r[4]), "v": float(r[5]), "tbv": float(r[9])}
            for r in rows if int(r[6]) < now_ms]
  Mutated:  return [{"t": int(r[0]), "o": float(r[1]), "h": float(r[2]), "l": float(r[3]), "c": float(r[4]), "v": float(r[5]), "tbv": float(r[9])}
            for r in rows if int(r[6]) >= now_ms]
Resulting failure when pointed at mutated copy:
  MyTradingSys/backtest/layers/wlow_bounce/test_status.py::test_fetch_candles_filters_forming_bar failed with:
    AssertionError: assert [{'t': 1700003600000, 'o': 102.0, 'h': 106.0, 'l': 101.0, 'c': 104.0, 'v': 8.0, 'tbv': 3.0}] == [{'t': 1700000000000, 'o': 100.0, 'h': 105.0, 'l': 95.0, 'c': 102.0, 'v': 10.0, 'tbv': 4.0}]
      At index 0 diff: {'t': 1700003600000, 'o': 102.0, 'h': 106.0, 'l': 101.0, 'c': 104.0, 'v': 8.0, 'tbv': 3.0} != {'t': 1700000000000, 'o': 100.0, 'h': 105.0, 'l': 95.0, 'c': 102.0, 'v': 10.0, 'tbv': 4.0}
"""
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
import pytest

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.layers.wlow_bounce import status as S


def test_fetch_candles_filters_forming_bar():
    # SOURCED: "t": int(r[0]), "o": float(r[1]), "h": float(r[2]), "l": float(r[3]), "c": float(r[4]), "v": float(r[5]), "tbv": float(r[9]) (MyTradingSys/backtest/layers/wlow_bounce/status.py:37)
    # SOURCED: for r in rows if int(r[6]) < now_ms (MyTradingSys/backtest/layers/wlow_bounce/status.py:38)
    # OURS: row 0 close time 1700003599999 < 1700005000000 (kept); row 1 close time 1700007199999 >= 1700005000000 (dropped)
    # OURS: parsed row 0 has t=1700000000000, o=100.0, h=105.0, l=95.0, c=102.0, v=10.0, tbv=4.0
    rows = [
        [1700000000000, "100.0", "105.0", "95.0", "102.0", "10.0", 1700003599999, "1000.0", 50, "4.0", "400.0", "0"],
        [1700003600000, "102.0", "106.0", "101.0", "104.0", "8.0", 1700007199999, "800.0", 40, "3.0", "300.0", "0"],
    ]
    with patch("MyTradingSys.backtest.layers.wlow_bounce.status._get", return_value=rows):
        res = S.fetch_candles(now_ms=1700005000000)
    assert res == [{
        "t": 1700000000000,
        "o": 100.0,
        "h": 105.0,
        "l": 95.0,
        "c": 102.0,
        "v": 10.0,
        "tbv": 4.0,
    }]


def test_fetch_candles_empty():
    # SOURCED: for r in rows if int(r[6]) < now_ms (MyTradingSys/backtest/layers/wlow_bounce/status.py:38)
    # OURS: empty input list returns empty list []
    with patch("MyTradingSys.backtest.layers.wlow_bounce.status._get", return_value=[]):
        res = S.fetch_candles(now_ms=1700000000000)
    assert res == []


def test_fetch_candles_malformed_missing_fields_raises():
    # SOURCED: float(r[2]), float(r[9]) required indexes (MyTradingSys/backtest/layers/wlow_bounce/status.py:37)
    # OURS: row with fewer columns raises IndexError
    with patch("MyTradingSys.backtest.layers.wlow_bounce.status._get", return_value=[[1700000000000, "100.0"]]):
        with pytest.raises(IndexError):
            S.fetch_candles(now_ms=1700000000000)


def test_fetch_oi_normal():
    # SOURCED: cur = float(_get("/fapi/v1/openInterest?symbol=BTCUSDT")["openInterest"]) (MyTradingSys/backtest/layers/wlow_bounce/status.py:44)
    # SOURCED: chg = cur - float(hist[0]["sumOpenInterest"]) if len(hist) >= k + 1 else None (MyTradingSys/backtest/layers/wlow_bounce/status.py:46)
    # OURS: cur = 50000.5, len(hist) = 3 >= 2 + 1 = 3, chg = 50000.5 - 48000.0 = 2000.5
    side_effects = [
        {"openInterest": "50000.5"},
        [{"sumOpenInterest": "48000.0"}, {"sumOpenInterest": "49000.0"}, {"sumOpenInterest": "50000.0"}],
    ]
    with patch("MyTradingSys.backtest.layers.wlow_bounce.status._get", side_effect=side_effects):
        res = S.fetch_oi(k=2)
    assert res == (50000.5, 2000.5)


def test_fetch_oi_insufficient_history():
    # SOURCED: chg = cur - float(hist[0]["sumOpenInterest"]) if len(hist) >= k + 1 else None (MyTradingSys/backtest/layers/wlow_bounce/status.py:46)
    # OURS: k=2 requires len(hist) >= 3; with len(hist) = 1, chg is None
    side_effects = [
        {"openInterest": "50000.5"},
        [{"sumOpenInterest": "48000.0"}],
    ]
    with patch("MyTradingSys.backtest.layers.wlow_bounce.status._get", side_effect=side_effects):
        res = S.fetch_oi(k=2)
    assert res == (50000.5, None)


def test_fetch_oi_malformed_error_returns_none_tuple():
    # SOURCED: except Exception: return None, None (MyTradingSys/backtest/layers/wlow_bounce/status.py:48-49)
    # OURS: Exception raised by _get produces (None, None)
    with patch("MyTradingSys.backtest.layers.wlow_bounce.status._get", side_effect=RuntimeError("network down")):
        res = S.fetch_oi(k=2)
    assert res == (None, None)


def test_report_normal_idle():
    # SOURCED: "asof_bar_open": datetime.fromtimestamp(candles[i]["t"] / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ") (status.py:57)
    # SOURCED: "gap_to_upper_pct": (candles[i]["c"] / bb[i] - 1) * 100 if bb[i] else None (status.py:59)
    # SOURCED: "net_delta_last_K": D.delta_sum(candles, i - K + 1, i) (status.py:60)
    # OURS: 20 constant bars (c=100.0, v=10.0, tbv=6.0) from 1767225600000 ms (2026-01-01 00:00 UTC)
    # OURS: bar 19 t=1767294000000 ms -> "2026-01-01T19:00Z"
    # OURS: bb_upper=100.0, close=100.0 -> gap=0.0%; rsi14=50.0; net_delta_last_4 = 4 * (2*6.0 - 10.0) = 8.0
    candles = [
        {"t": 1767225600000 + i * 3600000, "o": 100.0, "h": 100.0, "l": 100.0, "c": 100.0, "v": 10.0, "tbv": 6.0}
        for i in range(20)
    ]
    res = S.report(candles, oi=(1234.5, 56.7))
    assert res == {
        "asof_bar_open": "2026-01-01T19:00Z",
        "state": "IDLE",
        "close": 100.0,
        "rsi14": 50.0,
        "bb_upper": 100.0,
        "gap_to_upper_pct": 0.0,
        "net_delta_last_K": 8.0,
        "oi_now": 1234.5,
        "oi_change_last_K_h": 56.7,
    }


def test_report_empty_candles_raises_index_error():
    # SOURCED: i = len(candles) - 1 (MyTradingSys/backtest/layers/wlow_bounce/status.py:55)
    # SOURCED: candles[i]["t"] (MyTradingSys/backtest/layers/wlow_bounce/status.py:57)
    # OURS: empty candles list has i = -1, candles[-1] raises IndexError
    with pytest.raises(IndexError):
        S.report([])
