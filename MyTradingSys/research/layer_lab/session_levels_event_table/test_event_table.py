import importlib.util
from datetime import datetime, timezone
from pathlib import Path

MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("session_levels_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)
DAY = 86400000
MIN = 60000
BASE = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)


def _bar(t, h, l, c):
    return {"t": t, "o": c, "h": h, "l": l, "c": c}


def _fixture():
    prior = [_bar(BASE + i * MIN, 100, 90, 95) for i in range(1440)]
    current = [_bar(BASE + DAY + i * MIN, 99, 98, 99) for i in range(1440)]
    current[500] = _bar(BASE + DAY + 500 * MIN, 101, 99, 100.5)
    current[501] = _bar(BASE + DAY + 501 * MIN, 102, 98, 99)
    # 4h after fail: short-side favorable low 95, adverse high 101.
    current[502] = _bar(BASE + DAY + 502 * MIN, 101, 95, 98)
    return prior + current


def test_failed_break_row_has_hand_computed_level_spike_and_r():
    rows = event_table.build_event_table(_fixture(), source="synthetic")
    assert len(rows) == 1
    row = rows[0]
    assert row["side"] == "high"
    assert row["level"] == 100
    assert row["touch_time_ms"] == BASE + DAY + 500 * MIN
    assert row["fail_time_ms"] == BASE + DAY + 501 * MIN
    assert row["spike"] == 102
    assert row["r_price"] == 2
    assert row["mfe_r"] == 2.0
    assert row["mae_r"] == 1.0


def test_insufficient_prior_bars_gives_no_event():
    bars = _fixture()
    bars = [b for b in bars if b["t"] >= BASE + 100 * MIN]
    rows = event_table.build_event_table(bars, source="synthetic")
    assert rows == []


def test_bars_after_four_hour_horizon_do_not_change_excursions():
    bars = _fixture()
    rows_before = event_table.build_event_table(bars, source="synthetic")
    bars.append(_bar(BASE + DAY + 742 * MIN, 1000, 1, 500))
    rows_after = event_table.build_event_table(bars, source="synthetic")
    assert rows_after[0]["mfe_r"] == rows_before[0]["mfe_r"]
    assert rows_after[0]["mae_r"] == rows_before[0]["mae_r"]


def test_missing_forward_minute_is_marked_not_in_data():
    bars = _fixture()
    bars = [bar for bar in bars if bar["t"] != BASE + DAY + 600 * MIN]
    rows = event_table.build_event_table(bars, source="synthetic")
    assert rows[0]["forward_status"] == "NOT_IN_DATA"
    assert rows[0]["mfe_r"] is None
    assert rows[0]["mae_r"] is None
