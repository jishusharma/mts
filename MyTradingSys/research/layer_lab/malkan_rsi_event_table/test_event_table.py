import importlib.util
from pathlib import Path

MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("malkan_rsi_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)

START = 1640995200000  # 2022-01-01 UTC
HOUR = 3_600_000
N = 60


def _bars(start=START):
    # every bar: range 2, flat close 100, so TR = 2 and ATR14 = 2 everywhere
    return [{"t": start + i * HOUR, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0} for i in range(N)]


def _rsi(base, a, b):
    out = [base] * N
    out[22], out[23] = a, b
    return out


def _bull(start=START):
    bars = _bars(start)
    bars[23].update(o=99.5, c=100.5)       # green event bar
    bars[30]["h"] = 106.0                  # long MFE = (106-100)/2 = 3R
    bars[35]["l"] = 97.0                   # long MAE = (100-97)/2 = 1.5R
    return bars, _rsi(70.0, 41.0, 43.0)    # dips into the 38..42 band, exits above


def _bear():
    bars = _bars()
    bars[23].update(o=100.5, c=99.5)       # red event bar
    bars[28]["l"] = 94.0                   # short MFE = (100-94)/2 = 3R
    bars[33]["h"] = 102.0                  # short MAE = (102-100)/2 = 1R
    return bars, _rsi(30.0, 59.0, 57.0)    # rises into the 58..62 band, drops out below


def test_bull_bounce_gives_one_long_row_with_hand_values():
    bars, rsi = _bull()
    rows = event_table.build_event_table(bars, rsi=rsi)
    assert len(rows) == 1
    row = rows[0]
    assert row["side"] == "long" and row["status"] == "OK"
    assert row["timestamp"] == bars[23]["t"]
    assert row["entry_t"] == bars[24]["t"] and row["entry"] == 100.0
    assert row["risk_r"] == 2.0
    assert row["mfe_R"] == 3.0 and row["mae_R"] == 1.5
    assert row["bars_forward"] == 24


def test_bear_reject_gives_one_short_row_with_hand_values():
    bars, rsi = _bear()
    rows = event_table.build_event_table(bars, rsi=rsi)
    assert len(rows) == 1
    row = rows[0]
    assert row["side"] == "short" and row["status"] == "OK"
    assert row["mfe_R"] == 3.0 and row["mae_R"] == 1.0


def test_near_miss_three_points_above_band_gives_no_row():
    bars, _ = _bull()
    assert event_table.build_event_table(bars, rsi=_rsi(70.0, 45.0, 47.0)) == []


def test_wrong_color_event_bar_gives_no_row():
    bars, rsi = _bull()
    bars[23].update(o=100.5, c=99.5)
    assert event_table.build_event_table(bars, rsi=rsi) == []


def test_no_bar_after_horizon_is_read():
    bars, rsi = _bull()
    base = event_table.build_event_table(bars, rsi=rsi)
    for i in range(48, N):  # entry bar 24 + 24 forward bars ends at index 47
        bars[i].update(o=1e9, h=1e9, l=-1e9, c=1e9)
    assert event_table.build_event_table(bars, rsi=rsi) == base


def test_entry_is_next_bar_open_not_event_close():
    bars, rsi = _bull()
    bars[24].update(o=101.0, h=101.0, l=101.0, c=101.0)
    row = event_table.build_event_table(bars, rsi=rsi)[0]
    assert row["entry"] == 101.0
    assert row["mfe_R"] == 2.5  # (106-101)/2


def test_atr_needs_fifteen_bars():
    bars = _bars()
    assert event_table.atr14_at(bars, 13) is None   # only 14 bars up to index 13
    assert event_table.atr14_at(bars, 14) == 2.0


def test_gap_inside_forward_window_is_not_in_data():
    bars, rsi = _bull()
    del bars[40], rsi[40]
    row = event_table.build_event_table(bars, rsi=rsi)[0]
    assert row["status"] == "NOT_IN_DATA"
    assert row["mfe_R"] == "" and row["mae_R"] == ""


def test_short_forward_window_is_not_in_data():
    bars, rsi = _bull()
    row = event_table.build_event_table(bars[:40], rsi=rsi[:40])[0]
    assert row["status"] == "NOT_IN_DATA"


def test_bars_on_or_after_dev_end_are_dropped():
    bars, rsi = _bull(event_table.DEV_END_MS - 30 * HOUR)  # window crosses 2024-07-01
    row = event_table.build_event_table(bars, rsi=rsi)[0]
    assert row["status"] == "NOT_IN_DATA"
    assert row["bars_forward"] == 0
