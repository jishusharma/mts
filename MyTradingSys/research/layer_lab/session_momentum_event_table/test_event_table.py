import importlib.util
from pathlib import Path

MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("session_momentum_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)

DAY = 86_400_000
M5 = 300_000
H1 = 3_600_000
D0 = 1646092800000  # 2022-03-01T00:00Z
assert D0 % DAY == 0


def _day(start, first_close=100.4, price=100.0):
    """288 flat 5m bars; the 6th bar (entry bar) closes at first_close."""
    bars = []
    for k in range(288):
        bars.append({"t": start + k * M5, "o": price, "h": price, "l": price, "c": price})
    bars[5].update({"h": max(price, first_close), "l": min(price, first_close), "c": first_close})
    for b in bars[6:]:
        b.update({"o": first_close, "h": first_close, "l": first_close, "c": first_close})
    return bars


def _hours(start, n):
    # flat close 100, high 101 / low 99: every true range is 2
    return [{"t": start + i * H1, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0} for i in range(n)]


def _hours_for(day_start, days=1, before=20):
    return _hours(day_start - before * H1, before + 24 * days)


def test_plus_point_four_percent_gives_one_long_row_at_sixth_bar_close():
    rows = event_table.build_event_table(_day(D0), _hours_for(D0))
    assert len(rows) == 1
    row = rows[0]
    assert row["side"] == "long"
    assert row["t"] == D0 + 5 * M5  # entry bar open
    assert row["entry"] == 100.4  # close of the 6th bar
    assert row["status"] == "OK"


def test_minus_point_four_percent_gives_one_short_row():
    rows = event_table.build_event_table(_day(D0, first_close=99.6), _hours_for(D0))
    assert [r["side"] for r in rows] == ["short"]
    assert rows[0]["entry"] == 99.6


def test_exactly_zero_first_return_gives_no_row():
    assert event_table.build_event_table(_day(D0, first_close=100.0), _hours_for(D0)) == []


def test_mfe_mae_hand_values_and_r_excludes_unclosed_hour():
    bars = _day(D0)
    bars[10]["h"] = 101.4   # +1.0 from entry 100.4
    bars[20]["l"] = 99.4    # -1.0 from entry 100.4
    hours = _hours_for(D0)
    # hour opening at D0 closes at D0+1h, after the entry bar open (D0+25m): must not be used
    hours[20]["h"], hours[20]["l"] = 500.0, -300.0
    # 15th closed hour back: only its close is the previous close of the oldest TR
    hours[5]["h"], hours[5]["l"] = 900.0, -900.0
    row = event_table.build_event_table(bars, hours)[0]
    # 14 true ranges of 2.0 -> ATR14 = 2.0 = R
    assert row["r"] == 2.0
    assert row["mfe_R"] == (101.4 - 100.4) / 2.0
    assert row["mae_R"] == (100.4 - 99.4) / 2.0
    assert row["bars_forward"] == 282


def test_short_side_mfe_mae_are_mirrored():
    bars = _day(D0, first_close=99.6)
    bars[10]["l"] = 98.6    # favourable for a short: 1.0
    bars[20]["h"] = 100.1   # adverse: 0.5
    row = event_table.build_event_table(bars, _hours_for(D0))[0]
    assert row["mfe_R"] == 0.5
    assert row["mae_R"] == 0.25


def test_forward_window_stops_at_midnight():
    day1 = _day(D0)
    day2 = _day(D0 + DAY, first_close=100.0, price=100.0)  # zero return: no event
    day2[0]["h"] = 5000.0   # first bar of next day, must never enter day 1's window
    row = event_table.build_event_table(day1 + day2, _hours_for(D0, days=2))[0]
    assert row["mfe_R"] == 0.0 and row["mae_R"] == 0.0
    assert row["bars_forward"] == 282


def test_missing_bar_in_first_thirty_minutes_is_not_in_data():
    bars = _day(D0)
    del bars[2]
    rows = event_table.build_event_table(bars, _hours_for(D0))
    assert len(rows) == 1
    assert rows[0]["status"] == "NOT_IN_DATA"
    assert rows[0]["mfe_R"] == "" and rows[0]["r"] == ""


def test_missing_forward_bar_is_not_in_data():
    bars = _day(D0)
    del bars[100]
    rows = event_table.build_event_table(bars, _hours_for(D0))
    assert rows[0]["status"] == "NOT_IN_DATA"


def test_too_little_hourly_history_is_not_in_data():
    rows = event_table.build_event_table(_day(D0), _hours(D0 - 10 * H1, 10 + 24))
    assert rows[0]["status"] == "NOT_IN_DATA"


def test_bars_outside_dev_are_dropped_before_building():
    start = 1719792000000  # 2024-07-01T00:00Z
    assert event_table.build_event_table(_day(start), _hours_for(start)) == []
