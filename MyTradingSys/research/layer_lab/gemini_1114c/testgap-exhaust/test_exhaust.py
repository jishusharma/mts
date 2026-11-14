"""Unit tests for scripts/dev/exhaust.py pure functions (normal, empty, malformed cases).

Every expected constant is SOURCED from scripts/dev/exhaust.py and scripts/dev/traffic.py
(e.g. MIN_DRAIN_LEFT_PCT=5.0, THRESHOLDS_H, SPAWN_CEIL=80, EXHAUST_CEIL=95).
No network, no scheduler, no filesystem writes.

Broken scratch copy check: mutating scripts/dev/exhaust.py line 54 from
`if week_left_pct <= MIN_DRAIN_LEFT_PCT or hours_to_reset <= 0:` to
`if week_left_pct < MIN_DRAIN_LEFT_PCT or hours_to_reset <= 0:` caused
`test_check_read_and_threshold_boundaries` to fail (`AssertionError: assert 'T-2' is None`).
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "dev"))
import exhaust  # noqa: E402


def test_parse_and_fmt_utc_normal_and_malformed():
    dt0 = exhaust.parse_utc("2026-11-14T09:00Z")
    assert dt0 == datetime(2026, 11, 14, 9, 0, tzinfo=timezone.utc)
    assert exhaust.fmt_utc(dt0) == "2026-11-14T09:00Z"

    dt_compact = exhaust._parse_any_utc("20261114T090015Z")
    assert dt_compact == datetime(2026, 11, 14, 9, 0, 15, tzinfo=timezone.utc)
    assert exhaust.fmt_utc(dt_compact) == "2026-11-14T09:00:15Z"

    dt_offset = exhaust.parse_utc("2026-11-14T14:30:00+05:30")
    assert exhaust.fmt_utc(dt_offset) == "2026-11-14T09:00Z"

    with pytest.raises(ValueError):
        exhaust.parse_utc("")
    with pytest.raises(ValueError):
        exhaust._parse_any_utc("not-a-timestamp")


def test_check_read_and_threshold_boundaries():
    now = datetime(2026, 11, 14, 7, 10, tzinfo=timezone.utc)
    assert exhaust.check_read(datetime(2026, 11, 14, 7, 0, tzinfo=timezone.utc), now) == 10.0
    assert exhaust.check_read(datetime(2026, 11, 14, 7, 15, tzinfo=timezone.utc), now) == -5.0

    # MIN_DRAIN_LEFT_PCT = 5.0; THRESHOLDS_H = ((2.0, "T-2"), (24.0, "T-24"), (48.0, "T-48"))
    assert exhaust._threshold_for(1.5, 20.0) == "T-2"
    assert exhaust._threshold_for(2.0, 5.0) is None
    assert exhaust._threshold_for(24.0, 5.1) == "T-24"
    assert exhaust._threshold_for(48.0, 10.0) == "T-48"
    assert exhaust._threshold_for(48.1, 10.0) is None
    assert exhaust._threshold_for(0.0, 50.0) is None


def test_radar_empty_and_malformed_rows():
    now = datetime(2026, 11, 14, 10, 0, tzinfo=timezone.utc)

    empty_rep = exhaust.radar([], now=now)
    assert empty_rep["as_of"] == "2026-11-14T10:00Z"
    assert empty_rep["alerts"] == []
    assert [r["login"] for r in empty_rep["logins"]] == ["A", "B", "C"]
    assert all(
        r["status"] == "missing"
        and r["threshold"] is None
        and r["week_left_pct"] is None
        and r["rolled_weeks"] == 0
        and r["stale_reading"] is True
        for r in empty_rep["logins"]
    )

    malformed_rows = [
        {"ts": "2026-11-14T09:50Z", "lane": "A", "text": "HEARTBEAT ok"},
        {"ts": "2026-11-14T09:50Z", "lane": "A", "text": "BUDGET wk=40%@9999-99-99T00:00Z"},
        {"ts": "bad-ts", "lane": "B", "text": "BUDGET wk=120%@2026-11-14T11:00Z"},
    ]
    rep = exhaust.radar(malformed_rows, now=now)
    by_login = {r["login"]: r for r in rep["logins"]}
    assert by_login["A"]["status"] == "bad_reset"
    assert by_login["A"]["week_left_pct"] == 60.0
    assert by_login["A"]["threshold"] is None
    assert by_login["A"]["stale_reading"] is True

    assert by_login["B"]["status"] == "ok"
    assert by_login["B"]["week_left_pct"] == 0.0
    assert by_login["B"]["age_hours"] == 0.0
    assert by_login["B"]["stale_reading"] is False
    assert by_login["B"]["threshold"] is None
    assert by_login["C"]["status"] == "missing"


def test_plan_normal_and_five_stop_ceiling():
    reset = datetime(2026, 11, 14, 9, 0, tzinfo=timezone.utc)
    models = {"opus": 10.0, "sonnet": 50.0, "haiku": 100.0}

    # 90 min to reset (1.5 h): phase="plan", five_ceiling(1.5) == EXHAUST_CEIL (95)
    p_plan = exhaust.plan(
        "C", 80.0, 12.0, reset, models,
        now=reset - timedelta(minutes=90),
        read_utc="2026-11-14T07:25Z",
        source="get_usage",
    )
    assert p_plan == {
        "login": "C",
        "phase": "plan",
        "minutes_to_reset": 90,
        "week": 80.0,
        "five": 12.0,
        "models": ["opus", "sonnet"],
        "five_stop": 95,
        "read_utc": "2026-11-14T07:25Z",
        "source": "get_usage",
    }

    # 150 min to reset (2.5 h): phase="none", five_ceiling(2.5) == SPAWN_CEIL (80)
    p_none = exhaust.plan("A", 20.0, 5.0, reset, {}, now=reset - timedelta(minutes=150))
    assert p_none["phase"] == "none"
    assert p_none["five_stop"] == 80

    # 0 min to reset: phase="done", five_ceiling(0.0) == SPAWN_CEIL (80)
    p_done = exhaust.plan("A", 20.0, 5.0, reset, {}, now=reset)
    assert p_done["phase"] == "done"
    assert p_done["five_stop"] == 80


def test_holder_empty_and_fallback_who():
    assert exhaust.holder("A", []) == ""
    claims = [
        ("exhaust-login-b", {"who": "worker-1"}),
        ("exhaust-login-a", {}),
    ]
    assert exhaust.holder("B", claims) == "worker-1"
    assert exhaust.holder("A", claims) == "unknown"
    assert exhaust.holder("C", claims) == ""
