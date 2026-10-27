from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import successor_wake as sw  # type: ignore
import supervisor as S  # type: ignore


def _utc(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def test_dry_run_emits_single_fire_at_self_unregister_and_no_cron(tmp_path: Path):
    now = _utc("2026-10-28T00:00:00Z")
    fire = _utc("2026-10-28T02:15:00Z")
    script = sw.build_ps_script(
        login="A",
        fire_at=fire,
        cwd=tmp_path,
        model="claude-sonnet-5-5",
        prompt_text="Read SUPERVISOR_A.md",
        now=now,
    )
    assert "MTS-SuccWake-A" in script
    assert script.count("New-ScheduledTaskTrigger -Once -At") == 1
    for banned in ("-RepetitionInterval", "-RepetitionDuration", "-Daily", "-Weekly", "/sc minute", "/sc hourly"):
        assert banned not in script
    assert 'Unregister-ScheduledTask -TaskName "MTS-SuccWake-A" -Confirm:$false' in script
    assert "New-ScheduledTaskPrincipal" in script and "Interactive" in script
    assert "Register-ScheduledTask" in script and "-Force" in script


def test_past_fire_at_refused_closed(tmp_path: Path):
    now = _utc("2026-10-28T03:00:00Z")
    past = _utc("2026-10-28T02:00:00Z")
    with pytest.raises(ValueError, match="past"):
        sw.build_ps_script(
            login="B",
            fire_at=past,
            cwd=tmp_path,
            model="claude-sonnet-5-5",
            prompt_text="Read SUPERVISOR_B.md",
            now=now,
        )
    rc = sw.main(["--login", "B", "--at", "2026-10-28T02:00:00Z", "--cwd", str(tmp_path), "--dry"], now=now)
    assert rc == 2


def test_budget_fire_at_immediate_when_slots_available_or_reset_when_stop(tmp_path: Path):
    now = _utc("2026-10-28T01:00:00Z")
    plan = {
        "login": "A",
        "slots": 2,
        "mode": "NORMAL",
        "five_reset": "2026-10-28T04:00:00Z",
        "week_reset": "2026-11-02T00:00:00Z",
        "week_pct": 40,
    }
    (tmp_path / "A-last-plan.json").write_text(json.dumps(plan), encoding="utf-8")
    fire1 = sw.budget_fire_at(tmp_path, "A", now=now)
    assert fire1 == now + dt.timedelta(minutes=1)

    plan_stop = {**plan, "slots": 0, "mode": "STOP"}
    (tmp_path / "A-last-plan.json").write_text(json.dumps(plan_stop), encoding="utf-8")
    fire2 = sw.budget_fire_at(tmp_path, "A", now=now)
    assert fire2 == _utc("2026-10-28T04:00:00Z")

    # Within T-48h of weekly reset with >5% left:
    # if 5h budget is exhausted (slots=0, mode=STOP), wait for five_reset so it doesn't wake into a blocked 5h window
    plan_t48_stop = {
        **plan_stop,
        "week_reset": "2026-10-29T12:00:00Z",
        "week_pct": 65,
    }
    (tmp_path / "A-last-plan.json").write_text(json.dumps(plan_t48_stop), encoding="utf-8")
    fire3_stop = sw.budget_fire_at(tmp_path, "A", now=now)
    assert fire3_stop == _utc("2026-10-28T04:00:00Z")

    # Within T-48h of weekly reset with >5% left AND 5h slots available: wake immediately (now + 1m) to drain weekly pool
    plan_t48_ready = {
        **plan_t48_stop,
        "slots": 1,
        "mode": "DRAIN",
    }
    (tmp_path / "A-last-plan.json").write_text(json.dumps(plan_t48_ready), encoding="utf-8")
    fire3_ready = sw.budget_fire_at(tmp_path, "A", now=now)
    assert fire3_ready == now + dt.timedelta(minutes=1)


def test_handover_file_updated_idempotently_and_stays_valid_form(tmp_path: Path):
    now = _utc("2026-10-28T01:00:00Z")
    S.handover(tmp_path, "c", role="supervisor", now=now, wake=False)
    ho = tmp_path / "MyTradingSys" / "system" / "handover" / "SUPERVISOR_C.md"
    assert ho.is_file()

    fire1 = _utc("2026-10-28T02:00:00Z")
    fire2 = _utc("2026-10-28T03:30:00Z")
    sw.record_handover_line(ho, "C", fire1)
    sw.record_handover_line(ho, "C", fire2)
    text = ho.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if "Successor task:" in ln]
    assert len(lines) == 1
    assert "2026-10-28T03:30:00Z" in lines[0]
    assert S.validate_form(text) == []


def test_supervisor_handover_registers_unless_no_wake(tmp_path: Path):
    now = _utc("2026-10-28T01:00:00Z")
    calls: list[tuple[str, str]] = []
    with patch.object(sw, "_run_ps", side_effect=lambda script: calls.append(("ps", script)) or (0, "")):
        S.handover(tmp_path, "a", role="supervisor", now=now, wake=True)
        assert len(calls) == 1
        ho = (tmp_path / "MyTradingSys" / "system" / "handover" / "SUPERVISOR_A.md").read_text(encoding="utf-8")
        assert "Successor task: MTS-SuccWake-A" in ho
        assert S.validate_form(ho) == []

        calls.clear()
        S.handover(tmp_path, "a", role="supervisor", now=now, wake=False)
        assert len(calls) == 0


def test_dry_run_and_failed_ps_do_not_write_handover_line(tmp_path: Path):
    now = _utc("2026-10-28T01:00:00Z")
    S.handover(tmp_path, "b", role="supervisor", now=now, wake=False)
    ho = tmp_path / "MyTradingSys" / "system" / "handover" / "SUPERVISOR_B.md"
    assert "Successor task:" not in ho.read_text(encoding="utf-8")

    # Dry run must not write handover line
    res_dry = sw.register_for_handover(tmp_path, "b", ho, now=now, dry=True)
    assert res_dry["ok"] is True and res_dry.get("dry") is True
    assert "Successor task:" not in ho.read_text(encoding="utf-8")

    # Failed registration (rc != 0) must not write handover line
    with patch.object(sw, "_run_ps", return_value=(1, "access denied")):
        res_fail = sw.register_for_handover(tmp_path, "b", ho, now=now, dry=False)
        assert res_fail["ok"] is False
        assert "Successor task:" not in ho.read_text(encoding="utf-8")
