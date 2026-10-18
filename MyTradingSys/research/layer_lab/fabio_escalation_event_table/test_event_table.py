import importlib.util
from pathlib import Path

import pytest

MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("fabio_escalation_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)

START = 1640995200000  # 2022-01-01 UTC
HOUR = 3_600_000
N = 60
# TRs of bars 17..30 in _long(): 3 flat (1), bar 20 2.5, bar 21 2.5 (prev close 102), 3 flat,
# bar 25 2.5, bar 26 2.0 (prev close 101.5), 3 flat, bar 30 2.55
ATR = (3 + 2.5 + 2.5 + 3 + 2.5 + 2 + 3 + 2.55) / 14


def _bars(start=START):
    # flat bars: range 1, delta 2*55-100 = 10
    return [{"t": start + i * HOUR, "o": 100.0, "h": 100.5, "l": 99.5, "c": 100.0, "v": 100.0, "tbv": 55.0}
            for i in range(N)]


def _long(start=START):
    bars = _bars(start)
    bars[20].update(o=100.0, c=102.0, h=102.0)      # swing high, body high 102, confirmed at 22
    bars[25].update(c=101.5, h=102.0, v=300.0, tbv=250.0)  # aggressive up test, close holds: absorbed
    bars[30].update(c=102.0, h=102.05, v=400.0, tbv=350.0)  # record volume + record delta (300): escalation
    bars[35]["h"] = 106.0   # long MFE = (106 - 100) / ATR
    bars[40]["l"] = 97.0    # long MAE = (100 - 97) / ATR
    return bars


def _mirror(bars):
    out = []
    for b in bars:
        out.append({"t": b["t"], "o": 200 - b["o"], "h": 200 - b["l"], "l": 200 - b["h"],
                    "c": 200 - b["c"], "v": b["v"], "tbv": b["v"] - b["tbv"]})
    return out


def test_record_delta_break_of_absorbed_high_gives_one_long_row_with_hand_values():
    bars = _long()
    rows = event_table.build_event_table(bars)
    assert len(rows) == 1
    row = rows[0]
    assert row["timestamp"] == bars[30]["t"]
    assert row["side"] == "long" and row["status"] == "OK"
    assert row["entry_t"] == bars[31]["t"] and row["entry"] == 100.0   # next bar open, not event close 102
    assert row["risk_r"] == pytest.approx(ATR)
    assert row["mfe_R"] == pytest.approx(6.0 / ATR)
    assert row["mae_R"] == pytest.approx(3.0 / ATR)
    assert row["bars_forward"] == 24


def test_aggressor_down_through_absorbed_low_gives_short_row():
    bars = _mirror(_long())
    rows = event_table.build_event_table(bars)
    assert len(rows) == 1
    row = rows[0]
    assert row["side"] == "short" and row["status"] == "OK"
    assert row["timestamp"] == bars[30]["t"] and row["entry"] == 100.0
    assert row["mfe_R"] == pytest.approx(6.0 / ATR)
    assert row["mae_R"] == pytest.approx(3.0 / ATR)


def test_delta_below_k_times_average_gives_no_row():
    bars = _long()
    # window avg |delta| over bars 10..29 = (19*10 + 200) / 20 = 19.5; k*avg = 39 > 30
    bars[30].update(v=100.0, tbv=65.0)
    assert event_table.build_event_table(bars) == []


def test_absorption_before_swing_is_confirmed_is_not_used():
    bars = _long()
    bars[25].update(c=100.0, h=100.5, v=100.0, tbv=55.0)   # remove the real absorption
    bars[21].update(c=100.0, h=102.0, v=300.0, tbv=250.0)  # aggressive test one bar after the swing,
    # but confirmed_i = 22, so it cannot be the absorption
    assert event_table.build_event_table(bars) == []


def test_bars_after_event_do_not_change_the_event():
    bars = _long()
    base = event_table.build_event_table(bars)[0]
    altered = [dict(b) for b in bars]
    for k in range(32, N):
        altered[k].update(o=500.0, h=900.0, l=1.0, c=800.0, v=1.0, tbv=0.5)
    row = event_table.build_event_table(altered)[0]
    assert row["timestamp"] == base["timestamp"] and row["side"] == base["side"]


def test_gap_in_forward_window_is_not_in_data():
    bars = _long()
    del bars[40]
    row = event_table.build_event_table(bars)[0]
    assert row["status"] == "NOT_IN_DATA"
    assert row["mfe_R"] == "" and row["mae_R"] == ""


def test_short_forward_window_is_not_in_data():
    bars = _long()[:50]   # entry bar 31 + 24 bars would need index 54
    row = event_table.build_event_table(bars)[0]
    assert row["status"] == "NOT_IN_DATA"
    assert row["mfe_R"] == ""


def test_bars_before_dev_start_are_dropped():
    assert event_table.build_event_table(_long(START - 100 * HOUR)) == []
