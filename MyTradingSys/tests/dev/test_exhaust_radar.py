from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "dev"))
import exhaust  # type: ignore


def _utc(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def test_roll_reset_forward_by_7_day_steps_until_future():
    now = _utc("2026-10-28T12:00:00Z")
    stale_reset = _utc("2026-10-20T09:00:00Z")
    rolled, steps = exhaust.roll_weekly_reset(stale_reset, now)
    assert rolled == _utc("2026-11-03T09:00:00Z")
    assert steps == 2
    assert rolled > now


def test_radar_detects_t48_t24_t2_and_flags_stale_signal_reading():
    now = _utc("2026-10-28T10:00:00Z")
    rows = [
        {
            "ts": "2026-10-28T09:30:00Z",
            "host": "JIS-NUC",
            "lane": "A",
            "kind": "status",
            "text": "BUDGET 5h=20%@2026-10-28T14:00Z wk=62%@2026-10-29T20:00Z s7=10%@2026-10-29T20:00Z",
        },
        {
            "ts": "2026-10-27T01:00:00Z",
            "host": "JIS-NB",
            "lane": "B",
            "kind": "status",
            "text": "BUDGET 5h=10%@2026-10-27T05:00Z wk=50%@2026-10-21T18:00Z s7=0%@2026-10-21T18:00Z",
        },
        {
            "ts": "2026-10-28T09:50:00Z",
            "host": "JIS-NUC",
            "lane": "C",
            "kind": "status",
            "text": "BUDGET 5h=15%@2026-10-28T13:00Z wk=97%@2026-10-28T11:30:00Z s7=0%@2026-10-28T11:30:00Z",
        },
    ]
    rep = exhaust.radar(rows, now=now)
    by_login = {r["login"]: r for r in rep["logins"]}

    # Login A: 34h to reset, 38% left -> T-48 alert
    assert by_login["A"]["threshold"] == "T-48"
    assert by_login["A"]["week_left_pct"] == 38.0
    assert by_login["A"]["stale_reading"] is False

    # Login B: reset 2026-10-21T18:00Z rolled +7d -> 2026-10-28T18:00Z (8h away -> T-24), reading is >6h old -> stale_reading True
    assert by_login["B"]["threshold"] == "T-24"
    assert by_login["B"]["rolled_weeks"] == 1
    assert by_login["B"]["stale_reading"] is True

    # Login C: 1.5h away, but week_left_pct == 3% (<= 5%) -> no exhaust alert needed
    assert by_login["C"]["threshold"] is None


def test_radar_banner_emits_once_per_threshold_and_names_ready_cards(tmp_path: Path):
    now = _utc("2026-10-28T10:00:00Z")
    tasks_dir = tmp_path / "MyTradingSys" / "system" / "tasks"
    tasks_dir.mkdir(parents=True)
    card = {
        "id": "sample-drain-card",
        "title": "Sample drain card",
        "state": "ready",
        "lane": "SONNET",
        "priority": "P1",
        "est_turns": 4,
    }
    (tasks_dir / "sample-drain-card.json").write_text(json.dumps(card), encoding="utf-8")

    rows = [
        {
            "ts": "2026-10-28T09:45:00Z",
            "host": "JIS-NUC",
            "lane": "A",
            "kind": "status",
            "text": "BUDGET 5h=10%@2026-10-28T14:00Z wk=60%@2026-10-29T10:00Z s7=10%@2026-10-29T10:00Z",
        }
    ]
    state_dir = tmp_path / "state"
    b1 = exhaust.radar_banner(rows, now=now, state_dir=state_dir, repo=tmp_path)
    assert "RESET T-24" in b1
    assert "login=A" in b1
    assert "40% left" in b1 or "40.0% left" in b1
    assert "sample-drain-card" in b1

    # Second call at same threshold is deduped
    b2 = exhaust.radar_banner(rows, now=now, state_dir=state_dir, repo=tmp_path)
    assert b2 == ""

    # Advancing into T-2 window emits again for the new threshold
    later = _utc("2026-10-29T08:30:00Z")
    b3 = exhaust.radar_banner(rows, now=later, state_dir=state_dir, repo=tmp_path)
    assert "RESET T-2" in b3
