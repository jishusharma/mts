"""malkan_window_wide_2026-11: wide pivots (strength 3) find a 14-bar swing pair strength 1 misses; loader refuses bars at/after DEV end."""
import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("malkan_window_wide", HERE / "wide.py")
wide = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wide)

HDR = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"


def _row(t, c):
    return "%d,%s,%s,%s,%s,1,%d,1,1,1,1,0\n" % (t, c, c, c, c, t + 59999)


def _fixture():
    # lows at 3 (close 3) and 16 (close 2.5): 14 bars apart inclusive. A dip at 9 (close 6) is a strength-1 low but not a strength-3 low.
    c = [8, 7, 5, 3, 5, 6, 7, 8, 7, 6, 7, 5.5, 7, 6, 5, 4, 2.5, 4, 5, 6, 7, 8]
    rsi = [50.0] * len(c)
    rsi[3], rsi[16] = 30.0, 35.0
    rsi[9] = 45.0
    return c, rsi, [i * 3600000 for i in range(len(c))]


def test_strength3_finds_pair_14_apart_that_strength1_misses():
    c, rsi, ts = _fixture()
    ev3 = wide.divergences(c, rsi, ts, "bullish", 3)
    assert [(e["bars"], e["arm"], e["b_i"], e["i"]) for e in ev3] == [(14, "C13_18", 16, 19)]   # event at b + strength: causal
    ev1 = wide.divergences(c, rsi, ts, "bullish", 1)
    assert all(e["arm"] != "C13_18" for e in ev1)   # strength 1 sees the dip at 9 and never pairs 3 with 16
    assert wide.divergences(c, rsi, ts, "bearish", 3) == []


def test_loader_refuses_bars_at_or_after_dev_end(tmp_path):
    end = wide.DEV_END_MS
    (tmp_path / "BTCUSDT-1m-2024-06.csv").write_text(HDR + _row(end - 120000, 10) + _row(end - 60000, 11) + _row(end, 99), newline="\n")
    (tmp_path / "BTCUSDT-1m-2024-07.csv").write_text(HDR + _row(end + 60000, 98), newline="\n")
    bars = wide.load_1m(tmp_path, "BTCUSDT")
    assert max(b["t"] for b in bars) < end
    with pytest.raises(ValueError):
        wide.load_1m(tmp_path, "BTCUSDT", end_ms=end + 1)


def test_short_symbol_is_no_signal():
    assert wide.coverage_ok(7199) is False and wide.coverage_ok(7200) is True
