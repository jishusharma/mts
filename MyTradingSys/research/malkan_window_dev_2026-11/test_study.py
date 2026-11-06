"""malkan_window_dev_2026-11: loader never reads a bar at/after DEV end; a hand-built 2-pivot fixture lands in the PRE_REG arm."""
import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("malkan_window_study", HERE / "study.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)

HDR = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"


def _row(t, c):
    return "%d,%s,%s,%s,%s,1,%d,1,1,1,1,0\n" % (t, c, c, c, c, t + 59999)


def test_loader_refuses_bars_at_or_after_dev_end(tmp_path):
    end = study.DEV_END_MS
    (tmp_path / "BTCUSDT-1m-2024-06.csv").write_text(HDR + _row(end - 120000, 10) + _row(end - 60000, 11) + _row(end, 99), newline="\n")
    (tmp_path / "BTCUSDT-1m-2024-07.csv").write_text(HDR + _row(end + 60000, 98), newline="\n")
    bars = study.load_1m(tmp_path, "BTCUSDT")
    assert [b["t"] for b in bars] == [end - 120000, end - 60000]
    assert max(b["t"] for b in bars) < end
    with pytest.raises(ValueError):
        study.load_1m(tmp_path, "BTCUSDT", end_ms=end + 1)


def test_arm_edges():
    f = study.arm_of
    assert [f(n) for n in (3, 10, 11, 12, 13, 18, 19, 50, 51, 2)] == \
        ["S3_10", "S3_10", "B11_12", "B11_12", "C13_18", "C13_18", "D19_50", "D19_50", None, None]


def test_two_pivot_fixture_falls_in_named_arm():
    # lows at index 1 (close 3, RSI 30) and 12 (close 2.5, RSI 35): lower low, higher RSI low, bars = 12 - 1 + 1 = 12
    c = [5, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4.5, 3.5, 2.5, 4, 5]
    rsi = [50.0] * len(c)
    rsi[1], rsi[12] = 30.0, 35.0
    ts = [i * 3600000 for i in range(len(c))]
    evs = study.divergences(c, rsi, ts, "bullish")
    assert [(e["bars"], e["arm"], e["i"]) for e in evs] == [(12, "B11_12", 13)]
    # a bearish read of the same bars finds nothing
    assert study.divergences(c, rsi, ts, "bearish") == []


def test_trade_sign_and_cost():
    bars = [{"t": i * 3600000, "c": 100.0 + i} for i in range(30)]
    ev = [{"i": 2}]
    long_t = study.trades_for(ev, bars, "bullish", 7)
    short_t = study.trades_for(ev, bars, "bearish", 7)
    assert abs(long_t[0]["gross"] - (109 - 102) / 102 * 100) < 1e-9
    assert abs(short_t[0]["gross"] + long_t[0]["gross"]) < 1e-9
    assert abs(study.cell_stats([1.0, 1.0], [1, 2])["net"] - (1.0 - 0.14)) < 1e-9
    assert study.trades_for([{"i": 25}], bars, "bullish", 7) == []   # no exit bar: dropped