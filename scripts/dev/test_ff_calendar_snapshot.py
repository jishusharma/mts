"""Spec-derived tests for the serialized same-origin calendar snapshot."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ff_calendar_snapshot as snapshot


def expected(events, fetched_ms):
    return "window.LIVEAID_CAL_SNAP = " + json.dumps(
        {"fetched_ms": fetched_ms, "events": events}, separators=(",", ":")
    ) + ";\n"


@pytest.mark.parametrize("age_ms", [26 * 60 * 60 * 1000, 26 * 60 * 60 * 1000 - 1, 26 * 60 * 60 * 1000 + 1])
def test_timestamp_at_and_around_documented_26_hour_age_boundary(age_ms):
    # The page's age rule is 26 h; render stores the supplied timestamp verbatim as an integer.
    fetched = 2_000_000_000_000 - age_ms
    events = [{"title": "CPI", "impact": "High"}]
    assert snapshot.render(events, fetched) == expected(events, fetched)


def test_empty_event_list_is_rejected():
    with pytest.raises(ValueError, match="non-empty list"):
        snapshot.render([], 123)


@pytest.mark.parametrize("events", [None, {}, "event", 7])
def test_non_list_feed_is_rejected(events):
    with pytest.raises(ValueError, match="non-empty list"):
        snapshot.render(events, 123)


def test_malformed_timestamp_is_rejected_by_integer_conversion():
    with pytest.raises((TypeError, ValueError)):
        snapshot.render([{"title": "CPI"}], "not-an-epoch")


def test_valid_render_is_compact_javascript_assignment_with_newline():
    events = [{"title": "USD CPI", "country": "USD", "date": "2026-11-03T13:30:00"}]
    assert snapshot.render(events, 1_798_000_000_123) == (
        'window.LIVEAID_CAL_SNAP = {"fetched_ms":1798000000123,"events":'
        '[{"title":"USD CPI","country":"USD","date":"2026-11-03T13:30:00"}]};\n'
    )


def test_non_integer_numeric_timestamp_is_truncated_to_integer():
    events = [{"title": "NFP"}]
    assert snapshot.render(events, 1234.9) == expected(events, 1234)


def test_list_items_are_preserved_without_feed_schema_rewriting():
    events = [{"unexpected": [1, None, True]}, "malformed-but-list-item"]
    assert snapshot.render(events, 456) == expected(events, 456)
