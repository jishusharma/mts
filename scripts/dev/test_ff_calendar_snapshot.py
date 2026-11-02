"""Spec-derived tests for scripts/dev/ff_calendar_snapshot.py.

Covers:
  - render:
    * single-event list and integer epoch ms serialization
    * multi-event list serialization with compact separators
    * float epoch timestamp conversion to integer ms
    * empty list raising ValueError
    * non-list data (None, dict, string) raising ValueError
    * JS wrapper syntax: 'window.LIVEAID_CAL_SNAP = ...;\n'
  - main:
    * successful fetch stub writing snapshot JS file and returning 0
    * fetch error keeping old file and returning 1
    * malformed data error path returning 1
"""
import json
from pathlib import Path
import pytest

import ff_calendar_snapshot as ffs


def test_render_single_event_and_exact_js_wrapper():
    events = [{"title": "USD CPI", "country": "USD", "impact": "High"}]
    ms = 1730560000000
    res = ffs.render(events, ms)
    expected_prefix = 'window.LIVEAID_CAL_SNAP = {"fetched_ms":1730560000000,"events":['
    assert res.startswith(expected_prefix)
    assert res.endswith("};\n")


def test_render_multi_events_compact_separators():
    events = [
        {"title": "USD FOMC Rate", "impact": "High"},
        {"title": "EUR ECB Press Conference", "impact": "High"},
    ]
    ms = 1730561234567
    res = ffs.render(events, ms)
    # Compact separators: no space after colon or comma
    assert ',"events":[' in res
    assert '},{"title":' in res
    assert res.endswith("};\n")


def test_render_float_ms_cast_to_int():
    events = [{"title": "Event"}]
    res = ffs.render(events, 1730560000999.88)
    assert '"fetched_ms":1730560000999,' in res
    payload = json.loads(res.replace("window.LIVEAID_CAL_SNAP = ", "").rstrip(";\n"))
    assert isinstance(payload["fetched_ms"], int)
    assert payload["fetched_ms"] == 1730560000999


def test_render_empty_list_raises_value_error():
    with pytest.raises(ValueError, match="not a non-empty list"):
        ffs.render([], 1730560000000)


def test_render_none_raises_value_error():
    with pytest.raises(ValueError, match="not a non-empty list"):
        ffs.render(None, 1730560000000)


def test_render_dict_raises_value_error():
    with pytest.raises(ValueError, match="not a non-empty list"):
        ffs.render({"error": "rate limited"}, 1730560000000)


def test_render_string_raises_value_error():
    with pytest.raises(ValueError, match="not a non-empty list"):
        ffs.render("invalid payload", 1730560000000)


def test_main_success_with_stubbed_fetch(monkeypatch, tmp_path, capsys):
    out_file = tmp_path / "ff_calendar_snapshot.js"
    mock_events = [{"title": "USD Non-Farm Payrolls", "impact": "High"}]
    monkeypatch.setattr(ffs, "fetch", lambda: mock_events)

    code = ffs.main(out=out_file)
    assert code == 0
    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8")
    assert content.startswith("window.LIVEAID_CAL_SNAP = ")
    assert "USD Non-Farm Payrolls" in content
    assert "1 events ->" in capsys.readouterr().out


def test_main_fetch_error_preserves_old_file(monkeypatch, tmp_path, capsys):
    out_file = tmp_path / "ff_calendar_snapshot.js"
    old_content = "window.LIVEAID_CAL_SNAP = {'old': true};\n"
    out_file.write_text(old_content, encoding="utf-8")

    def failing_fetch():
        raise OSError("Network unreachable")

    monkeypatch.setattr(ffs, "fetch", failing_fetch)

    code = ffs.main(out=out_file)
    assert code == 1
    # Old file preserved
    assert out_file.read_text(encoding="utf-8") == old_content
    assert "FAILED, old file kept: Network unreachable" in capsys.readouterr().err


def test_main_malformed_feed_returns_error_code(monkeypatch, tmp_path, capsys):
    out_file = tmp_path / "ff_calendar_snapshot.js"
    monkeypatch.setattr(ffs, "fetch", lambda: [])  # empty list

    code = ffs.main(out=out_file)
    assert code == 1
    assert "not a non-empty list" in capsys.readouterr().err
