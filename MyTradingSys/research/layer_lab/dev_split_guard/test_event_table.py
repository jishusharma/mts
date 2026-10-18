import importlib.util
from pathlib import Path

MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("dev_split_guard_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)


def test_inclusive_dev_boundaries_and_later_timestamp_fails_closed():
    rows = [
        {"timestamp": "2022-01-01T00:00:00Z", "tag": "start"},
        {"timestamp": "2024-06-30T23:59:59Z", "tag": "end"},
        {"timestamp": "2024-07-01T00:00:00Z", "tag": "validation"},
    ]
    kept, dropped = event_table.dev_only(rows, "timestamp")
    assert [row["tag"] for row in kept] == ["start", "end"]
    assert dropped == 1
    try:
        event_table.assert_dev(rows, "timestamp")
    except ValueError as exc:
        assert "2024-07-01T00:00:00Z" in str(exc)
    else:
        raise AssertionError("assert_dev accepted a VALIDATION timestamp")


def test_milliseconds_and_iso_timestamps_produce_identical_results():
    iso = [{"t": "2022-01-01T00:00:00Z"}, {"t": "2024-07-01T00:00:00Z"}]
    millis = [{"t": 1640995200000}, {"t": 1719792000000}]
    iso_kept, iso_dropped = event_table.dev_only(iso, "t")
    ms_kept, ms_dropped = event_table.dev_only(millis, "t")
    assert iso_kept == [{"t": "2022-01-01T00:00:00Z"}]
    assert ms_kept == [{"t": 1640995200000}]
    assert iso_dropped == ms_dropped == 1


def test_missing_timestamp_raises_instead_of_silently_dropping():
    try:
        event_table.dev_only([{"tag": "missing"}], "timestamp")
    except ValueError as exc:
        assert "timestamp" in str(exc)
    else:
        raise AssertionError("missing timestamp did not fail closed")


def test_rows_before_dev_start_are_dropped():
    rows = [{"t": 1640995199999}, {"t": 1640995200000}]
    kept, dropped = event_table.dev_only(rows, "t")
    assert kept == [{"t": 1640995200000}]
    assert dropped == 1
