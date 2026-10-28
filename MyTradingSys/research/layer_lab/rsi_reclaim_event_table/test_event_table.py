import importlib.util
from pathlib import Path

MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("rsi_reclaim_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)

START = 1640995200000  # 2022-01-01 UTC
HOUR = 3_600_000
N = 70


def _bars(start=START):
    # every bar: range 2, flat close 100, so TR = 2 and ATR14 = 2 everywhere
    return [{"t": start + i * HOUR, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0} for i in range(N)]


def _rsi(**points):
    out = [50.0] * N  # 50 is above the long band and below the short band: never arms either side
    for key, value in points.items():
        out[int(key[1:])] = value
    return out


def _series(values, first=20, base=50.0):
    return [base] * first + list(values) + [base] * (N - first - len(values))


def test_direct_cross_gives_band_bars_zero_and_dwell_four():
    bars = _bars()
    rows = event_table.build_event_table(bars, rsi=_series([35, 35, 35, 35, 45]))
    assert len(rows) == 1
    row = rows[0]
    assert row["side"] == "long" and row["status"] == "OK"
    assert row["timestamp"] == bars[24]["t"]
    assert row["dwell_below"] == 4 and row["band_bars"] == 0 and row["depth"] == 5.0


def test_band_bars_count_between_run_and_reclaim():
    rows = event_table.build_event_table(_bars(), rsi=_series([35, 40, 40, 45]))
    assert len(rows) == 1
    assert rows[0]["dwell_below"] == 1 and rows[0]["band_bars"] == 2


def test_band_pop_between_below_runs_restarts_dwell():
    rows = event_table.build_event_table(_bars(), rsi=_series([35, 35, 40, 35, 35, 45]))
    assert len(rows) == 1
    assert rows[0]["dwell_below"] == 2 and rows[0]["band_bars"] == 0


def test_none_bars_carry_state():
    rows = event_table.build_event_table(_bars(), rsi=_series([35, 35, None, 35, 45]))
    assert len(rows) == 1
    assert rows[0]["dwell_below"] == 3 and rows[0]["band_bars"] == 0


def test_short_side_mirrors_at_level_60():
    bars = _bars()
    rows = event_table.build_event_table(bars, rsi=_series([65, 65, 65, 55]))
    assert len(rows) == 1
    row = rows[0]
    assert row["side"] == "short" and row["timestamp"] == bars[23]["t"]
    assert row["dwell_below"] == 3 and row["band_bars"] == 0 and row["depth"] == 5.0


def test_short_side_band_pop_and_band_bars():
    rows = event_table.build_event_table(_bars(), rsi=_series([65, 60, 60, 60, 55]))
    assert len(rows) == 1
    assert rows[0]["dwell_below"] == 1 and rows[0]["band_bars"] == 3


def test_clearance_two_ignores_band_edge():
    # 41.9 is inside 38..42 (not below, not above): no reclaim without a clean exit
    assert event_table.build_event_table(_bars(), rsi=_series([35, 35] + [41.9] * 48)) == []


def test_entry_is_next_bar_open_and_long_mfe_mae_hand_values():
    bars = _bars()
    bars[25].update(o=101.0, h=101.0, l=101.0, c=101.0)   # entry bar = reclaim index 24 + 1
    bars[30]["h"] = 106.0                                 # long MFE = (106-101)/2 = 2.5R
    bars[35]["l"] = 98.0                                  # long MAE = (101-98)/2 = 1.5R
    row = event_table.build_event_table(bars, rsi=_series([35, 35, 35, 35, 45]))[0]
    assert row["entry_t"] == bars[25]["t"] and row["entry"] == 101.0
    assert row["risk_r"] == 2.0
    assert row["mfe_R"] == 2.5 and row["mae_R"] == 1.5 and row["bars_forward"] == 24


def test_short_mfe_mae_hand_values():
    bars = _bars()
    bars[29]["l"] = 94.0    # short MFE = (100-94)/2 = 3R
    bars[33]["h"] = 102.0   # short MAE = (102-100)/2 = 1R
    row = event_table.build_event_table(bars, rsi=_series([65, 65, 65, 55]))[0]
    assert row["entry"] == 100.0 and row["mfe_R"] == 3.0 and row["mae_R"] == 1.0


def test_no_bar_after_horizon_is_read():
    bars = _bars()
    rsi = _series([35, 35, 35, 35, 45])
    base = event_table.build_event_table(bars, rsi=rsi)
    for i in range(50, N):  # entry 25 + 24 forward bars ends at index 48
        bars[i].update(o=1e9, h=1e9, l=-1e9, c=1e9)
    assert event_table.build_event_table(bars, rsi=rsi) == base


def test_incomplete_forward_window_is_not_in_data():
    bars = _bars()[:40]
    row = event_table.build_event_table(bars, rsi=_series([35, 35, 35, 35, 45])[:40])[0]
    assert row["status"] == "NOT_IN_DATA"
    assert row["mfe_R"] == "" and row["mae_R"] == ""
    assert row["dwell_below"] == 4  # event columns survive


def test_gap_inside_forward_window_is_not_in_data():
    bars = _bars()
    rsi = _series([35, 35, 35, 35, 45])
    del bars[40], rsi[40]
    assert event_table.build_event_table(bars, rsi=rsi)[0]["status"] == "NOT_IN_DATA"


def test_gap_inside_below_run_is_not_in_data():
    bars = _bars()
    rsi = _series([35, 35, 35, 35, 45])
    del bars[22], rsi[22]
    assert event_table.build_event_table(bars, rsi=rsi)[0]["status"] == "NOT_IN_DATA"


def test_bars_on_or_after_dev_end_are_dropped():
    bars = _bars(event_table.DEV_END_MS - 30 * HOUR)  # window crosses 2024-07-01
    row = event_table.build_event_table(bars, rsi=_series([35, 35, 35, 35, 45]))[0]
    assert row["status"] == "NOT_IN_DATA" and row["bars_forward"] == 0
