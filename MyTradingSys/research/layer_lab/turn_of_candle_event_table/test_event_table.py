import importlib.util
from pathlib import Path

MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("turn_of_candle_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)

M1 = 60_000
H1 = 3_600_000
Q = 15 * M1
D0 = 1646092800000  # 2022-03-01T00:00Z, a quarter boundary


def _flat(start, n, price=100.0):
    return [{"t": start + k * M1, "o": price, "h": price, "l": price, "c": price} for k in range(n)]


def _hours(day_start, n=60, before=30):
    # every true range is 2 -> ATR14 = 2.0
    s = day_start - before * H1
    return [{"t": s + i * H1, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0} for i in range(n)]


def test_rows_only_where_next_bar_is_minute_zero_and_entry_is_minute14_close():
    bars = _flat(D0, 45)  # three quarters: minutes 0..44
    bars[14]["c"] = 100.5
    rows = event_table.build_event_table(bars, _hours(D0))
    # entry bars with mq 14 at k=14 and k=29 (k=44 has no 15 forward bars -> NOT_IN_DATA row)
    assert [r["t"] for r in rows] == [D0 + 14 * M1, D0 + 29 * M1, D0 + 44 * M1]
    assert rows[0]["entry"] == 100.5
    assert all((r["t"] // M1) % 15 == 14 for r in rows)
    assert rows[2]["status"] == "NOT_IN_DATA"


def test_first_fourteen_bars_give_no_row():
    assert event_table.build_event_table(_flat(D0, 14), _hours(D0)) == []


def test_long_short_mfe_mae_hand_values_and_mirror():
    bars = _flat(D0, 30)
    bars[20]["h"] = 101.0   # +1.0 from entry 100
    bars[25]["l"] = 99.0    # -1.0 from entry 100
    row = event_table.build_event_table(bars, _hours(D0))[0]
    assert row["r"] == 2.0
    assert row["long_mfe_R"] == 0.5 and row["long_mae_R"] == 0.5
    assert row["short_mfe_R"] == row["long_mae_R"]
    assert row["short_mae_R"] == row["long_mfe_R"]
    bars[18]["l"] = 98.0    # -2.0 -> short MFE 1.0R
    row = event_table.build_event_table(bars, _hours(D0))[0]
    assert row["long_mae_R"] == 1.0 and row["short_mfe_R"] == 1.0 and row["long_mfe_R"] == 0.5


def test_forward_bars_are_exactly_next_fifteen_and_ret_first_min():
    bars = _flat(D0, 40)
    bars[15].update({"o": 100.0, "c": 100.2, "h": 100.2})  # boundary bar
    bars[29]["h"] = 101.0   # 15th forward bar: counted
    bars[30]["h"] = 150.0   # 16th forward bar: ignored
    row = event_table.build_event_table(bars, _hours(D0))[0]
    assert row["bars_forward"] == 15
    assert row["long_mfe_R"] == (101.0 - 100.0) / 2.0
    assert abs(row["ret_first_min"] - 0.002) < 1e-12


def test_gap_in_forward_bars_is_not_in_data_never_zero():
    bars = _flat(D0, 40)
    del bars[20]
    row = event_table.build_event_table(bars, _hours(D0))[0]
    assert row["status"] == "NOT_IN_DATA"
    assert row["long_mfe_R"] == "" and row["short_mae_R"] == "" and row["r"] == ""


def test_thin_1h_history_is_not_in_data():
    row = event_table.build_event_table(_flat(D0, 30), _hours(D0, n=3, before=1))[0]
    assert row["status"] == "NOT_IN_DATA"


def test_r_ignores_unclosed_hour():
    bars = _flat(D0 + 3 * H1 + 45 * M1, 30)
    hours = _hours(D0)
    for h in hours:
        if h["t"] >= D0 + 3 * H1:  # hour containing the entry bar opens at D0+3h: not closed
            h["h"], h["l"] = 900.0, -900.0
    assert event_table.build_event_table(bars, hours)[0]["r"] == 2.0


def test_post_dev_bars_dropped():
    end = event_table.DEV_END_MS
    bars = _flat(end - 15 * M1, 30)
    rows = event_table.build_event_table(bars, _hours(end - 15 * M1))
    assert all(r["t"] < end for r in rows)
