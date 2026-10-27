"""successor_wake.py (4b2 one-time successor task): golden --dry PowerShell, past --at refused, register
idempotent, the supervisor handover chain wiring (default registers, --no-wake registers nothing, one
Successor line, idempotent), and the budget-aware fireAt from the pacer's last plan (d-47).

Fails on the pre-change code: `import successor_wake` is a ModuleNotFoundError (the file did not exist)
and `supervisor.handover` had no `wake`/`dry` parameters.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import successor_wake as W
import supervisor as S

T0 = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)


def _plan(slots=4, mode="NORMAL", five=10, week=20, five_reset="2026-10-19T14:00Z", week_reset="2026-10-25T09:00Z",
          cap=95):
    return {"plan": {"mode": mode, "slots": slots, "five": five, "week": week, "cap": cap,
                     "five_reset": five_reset, "week_reset": week_reset}}


# ---------- the one-time task itself ----------
def test_dry_golden_one_once_trigger_no_repeat_self_unregister():
    ps = W.build_ps(W.task_name("C"), "C", "2026-10-19T14:00:00Z", "claude-sonnet-5-5",
                    "You are Supervisor. Login C. Continue", "F:/MTS/mts-jis-nuc")
    assert ps.count("-Once -At") == 1 and ps.count("$fireAt = [DateTime]::Parse") == 1
    # one fireAt, no repeat trigger, no cron (SCHEDULING_POLICY 4: a one-time task, unregistered after it fires)
    for bad in ("RepetitionInterval", "-Weekly", "-Daily", "-AtLogOn", "cron"):
        assert bad not in ps, bad
    assert "claude-sonnet-5-5" in ps              # the task prompt names the model (4b2 rule)
    assert "Unregister-ScheduledTask" in ps        # self-unregister IS the "gone after it fires" rule
    assert "Register-ScheduledTask" in ps and "-Force" in ps
    assert "powershell.exe -NoProfile -ExecutionPolicy Bypass -File" in ps   # no nested -Command quoting


def test_task_name_and_fireat_format():
    assert W.task_name("b") == "MTS-SuccWake-B"
    assert W.iso_utc(T0) == "2026-10-19T12:00:00Z"
    assert W.parse_utc("2026-10-19T14:00Z") == datetime(2026, 10, 19, 14, 0, tzinfo=timezone.utc)


def test_past_at_refused_even_when_dry():
    assert W.main(["--login", "C", "--at", "2020-01-01T00:00Z", "--dry"]) == 2
    # a future --at still runs: the golden PowerShell prints, nothing registers
    assert W.main(["--login", "C", "--at", "2027-01-01T00:00:00Z", "--dry"]) == 0


def test_register_idempotent_reregister_is_force():
    a = W.build_ps(W.task_name("A"), "A", "2026-10-19T14:00:00Z", "m", "p", "F:/x")
    b = W.build_ps(W.task_name("A"), "A", "2026-10-19T15:00:00Z", "m", "p", "F:/x")   # a second run
    assert a.count("$task = 'MTS-SuccWake-A'") == 1 and b.count("$task = 'MTS-SuccWake-A'") == 1
    assert "-Force" in a and "-Force" in b        # re-registering the existing task overwrites, never duplicates


def test_upsert_line_idempotent_one_successor_line():
    f = Path("x.md")
    f.write_text("body line\n")
    W.upsert_line(f, W.handover_line("MTS-SuccWake-C", "2026-10-19T14:00:00Z"))
    W.upsert_line(f, W.handover_line("MTS-SuccWake-C", "2026-10-19T15:00:00Z"))
    t = f.read_text()
    assert t.count("Successor task:") == 1 and "15:00:00" in t and "14:00:00" not in t
    f.unlink()


# ---------- the budget-aware fireAt (d-47) ----------
def test_fireat_slots_at_least_one_is_now():
    fa, why = S.successor_fireat(_plan(slots=4), T0)
    assert fa == W.iso_utc(T0) and "slots 4" in why


def test_fireat_stop_five_block_waits_for_the_5h_reset():
    fa, why = S.successor_fireat(_plan(slots=0, mode="STOP", five=90), T0)
    assert fa == "2026-10-19T14:00:00Z" and "5h" in why


def test_fireat_stop_weekly_at_cap_waits_for_the_weekly_reset():
    fa, why = S.successor_fireat(_plan(slots=0, mode="STOP", five=5, week=99), T0)
    assert fa == "2026-10-25T09:00:00Z" and "weekly" in why


def test_fireat_no_last_plan_defaults_to_now():
    fa, why = S.successor_fireat({}, T0)
    assert fa == W.iso_utc(T0)


# ---------- the handover chain wiring (the ENDED path: handover send=True) ----------
@pytest.fixture
def _no_real_register(monkeypatch):
    """The ENDED handover's default wake must never hit the real Task Scheduler (nor the real signal clone)."""
    calls = []
    monkeypatch.setattr(W, "register", lambda *a, **k: calls.append((a, k)) or 0)
    import sys as _sys, types as _types
    monkeypatch.setitem(_sys.modules, "mts_signal", _types.SimpleNamespace(send=lambda *a, **k: True))
    return calls


def test_handover_registers_by_default_and_writes_one_successor_line(tmp_path, monkeypatch, _no_real_register):
    import sync
    monkeypatch.setattr(sync, "read_claims", lambda repo, ref: [])
    home = tmp_path / "home"
    home.mkdir()
    (home / "A-last-plan.json").write_text(json.dumps(_plan(slots=4)), encoding="utf-8")
    p = S.handover(tmp_path, "a", note="n", host="JIS-NUC", home=home, now=T0, send=True)
    assert len(_no_real_register) == 1 and _no_real_register[0][0][0] == "A"
    t = p.read_text(encoding="utf-8")
    assert t.count("Successor task:") == 1 and "MTS-SuccWake-A" in t
    assert W.iso_utc(T0) in t                              # slots >= 1 -> fireAt = now


def test_handover_no_wake_registers_nothing_and_writes_no_line(tmp_path, monkeypatch, _no_real_register):
    import sync
    monkeypatch.setattr(sync, "read_claims", lambda repo, ref: [])
    home = tmp_path / "home"
    home.mkdir()
    p = S.handover(tmp_path, "a", note="n", host="JIS-NUC", home=home, now=T0, send=True, wake=False)
    assert _no_real_register == []
    assert "Successor task:" not in p.read_text(encoding="utf-8")


def test_handover_reregister_updates_the_line_never_duplicates(tmp_path, monkeypatch, _no_real_register):
    import sync
    monkeypatch.setattr(sync, "read_claims", lambda repo, ref: [])
    home = tmp_path / "home"
    home.mkdir()
    S.handover(tmp_path, "a", note="n", host="JIS-NUC", home=home, now=T0, send=True)
    p2 = S.handover(tmp_path, "a", note="n", host="JIS-NUC", home=home, now=T0 + timedelta(minutes=5), send=True)
    t = p2.read_text(encoding="utf-8")
    assert t.count("Successor task:") == 1 and W.iso_utc(T0 + timedelta(minutes=5)) in t


def test_handover_non_ended_writes_no_successor(tmp_path, monkeypatch, _no_real_register):
    """A handover without the ENDED heartbeat (send=False) records no successor: the chain advances only on ENDED."""
    import sync
    monkeypatch.setattr(sync, "read_claims", lambda repo, ref: [])
    home = tmp_path / "home"
    home.mkdir()
    p = S.handover(tmp_path, "a", note="n", host="JIS-NUC", home=home, now=T0)
    assert _no_real_register == []
    assert "Successor task:" not in p.read_text(encoding="utf-8")


def test_handover_dry_registers_nothing_but_reports_fireat(tmp_path, monkeypatch, _no_real_register, capsys):
    import sync
    monkeypatch.setattr(sync, "read_claims", lambda repo, ref: [])
    home = tmp_path / "home"
    home.mkdir()
    (home / "A-last-plan.json").write_text(json.dumps(_plan(slots=4)), encoding="utf-8")
    p = S.handover(tmp_path, "a", note="n", host="JIS-NUC", home=home, now=T0, send=True, dry=True)
    assert _no_real_register == []
    out = capsys.readouterr().out
    assert "DRY MTS-SuccWake-A would register fireAt" in out and "nothing registered" in out
    assert "Successor task:" in p.read_text(encoding="utf-8")
