"""Tests for successor_wake.py and the supervisor.py handover wiring (SCHEDULING_POLICY 4b2).
--dry / stub runner only: no real scheduled task is ever registered, HALT is never touched, nothing reads secrets.
Run: python scripts/dev/test_successor_wake.py"""
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import successor_wake as W
import supervisor as S

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)
HERE_REPO = Path(__file__).resolve().parents[2]


def _repo(tmp_path):
    (tmp_path / "MyTradingSys" / "system" / "handover").mkdir(parents=True, exist_ok=True)
    (tmp_path / "scripts" / "dev").mkdir(parents=True, exist_ok=True)
    (tmp_path / "scripts" / "dev" / "sync.py").write_text("", encoding="utf-8")
    return tmp_path


def _dry(tmp_path, **kw):
    return W.register("C", cwd=_repo(tmp_path), dry=True, now=NOW, plan={"mode": "NORMAL", "slots": 2}, **kw)


def test_dry_golden_one_fireat_no_repeat_selfunregister(tmp_path):
    r = _dry(tmp_path, at="2026-10-27T20:05Z")
    s = r["script"]
    assert s.count("$FireAt =") == 1 and "-Once -At $FireAt" in s
    for bad in ("RepetitionInterval", "-Daily", "-Weekly", "-AtLogOn", "cron", "-Repetition"):
        assert bad not in s
    assert "claude-sonnet-5-5" in s and "Unregister-ScheduledTask -TaskName 'MTS-SuccWake-C'" in s
    assert "-LogonType Interactive" in s and "conhost.exe" in s and "--headless" in s and s.count("Register-ScheduledTask") == 1
    assert "You are Supervisor. Login C." in s and "SUPERVISOR_C.md" in s
    assert r["line"] == "Successor task: MTS-SuccWake-C fireAt 2026-10-27T20:05Z (4b2)"


def test_fire_now_has_no_trigger_and_starts_task(tmp_path):
    r = _dry(tmp_path)
    assert "FireAt" not in r["script"] and "-Trigger" not in r["script"] and "Start-ScheduledTask" in r["script"]
    assert r["fire_at"] == "2026-10-27T12:00Z"


def test_past_at_refused(tmp_path):
    with pytest.raises(W.WakeError, match="past"):
        W.register("C", cwd=_repo(tmp_path), at="2026-10-27T11:00Z", dry=True, now=NOW)
    with pytest.raises(W.WakeError):
        W.register("C", cwd=_repo(tmp_path), at="not-a-time", dry=True, now=NOW)


def test_non_mts_checkout_and_bad_login_refused(tmp_path):
    with pytest.raises(W.WakeError, match="not an MTS checkout"):
        W.register("C", cwd=tmp_path, dry=True, now=NOW)
    with pytest.raises(W.WakeError, match="login"):
        W.register("Z", cwd=_repo(tmp_path), dry=True, now=NOW)


def test_model_and_prompt_file_override(tmp_path):
    pf = tmp_path / "p.txt"
    pf.write_text("custom boot prompt", encoding="utf-8")
    r = _dry(tmp_path, model="claude-haiku-4-5", prompt_file=str(pf))
    assert "--model claude-haiku-4-5" in r["script"] and "custom boot prompt" in r["script"]


def test_usage_handoff_written_next_to_prompt(tmp_path):
    """The woken session must be handed its own usage: a USAGE file beside the task's prompt (old code wrote none)."""
    plan = {"mode": "NORMAL", "slots": 2, "five": 40.0, "week": 20.0, "five_reset": "2026-10-27T15:00Z", "week_reset": "2026-11-01T00:00Z"}
    r = W.register("C", cwd=_repo(tmp_path), at="2026-10-27T20:05Z", dry=True, now=NOW, plan=plan)
    s = r["script"]
    assert 'Budget handoff:' in s, "prompt must hand the usage line to the woken session"
    assert '[IO.File]::WriteAllText("$d/USAGE", $u)' in s, "the usage JSON must be written next to prompt.txt"
    import json
    m = re.search(r"\$u = @'\n(.*?)\n'@", s, re.S)
    assert m, "no USAGE here-string in the script"
    u = json.loads(m.group(1))
    assert u["login"] == "C" and u["pacer_mode"] == "NORMAL" and u["slots"] == 2
    assert u["five_pct"] == 40.0 and u["week_pct"] == 20.0 and u["plan"]["five_reset"] == "2026-10-27T15:00Z"
    assert u["file"].endswith("/USAGE")
    # the prompt names the file the woken session reads
    assert u["file"] in s and "Budget handoff:" in s
    # a present plan carries no missing-note
    assert not u["note"].startswith("pacer plan missing")


def test_usage_missing_plan_is_noted(tmp_path):
    """A missing / unreadable pacer plan is a note, not an error: the woken session re-reads from get_usage.
    `home` points at an empty dir so load_plan() never reads a real pacer file."""
    r = W.register("A", cwd=_repo(tmp_path), at="2026-10-27T20:05Z", dry=True, now=NOW, plan=None, home=tmp_path / "no-plan")
    s = r["script"]
    m = re.search(r"\$u = @'\n(.*?)\n'@", s, re.S)
    import json
    u = json.loads(m.group(1))
    assert u["pacer_mode"] == "unknown" and u["plan"] is None and u["five_pct"] is None
    assert "re-read from get_usage" in u["note"]
    assert "re-read from get_usage" in s, "the prompt line must tell the woken session to re-read usage"


def test_wake_usage_pure_shape():
    now = NOW
    assert W.wake_usage("C", None, now)["pacer_mode"] == "unknown"
    p = {"mode": "STOP", "slots": 0, "five": 80.0, "week": 70.0, "five_reset": "2026-10-27T15:00Z", "week_reset": "2026-11-01T00:00Z"}
    u = W.wake_usage("B", p, now)
    assert u["pacer_mode"] == "STOP" and u["slots"] == 0 and u["five_pct"] == 80.0 and u["week_pct"] == 70.0
    assert W.usage_rel("B") == f"{W.BASE_DIR}/B/{W.USAGE_REL}"


def test_budget_aware_fire_at(tmp_path):
    now = NOW
    ok = {"mode": "NORMAL", "slots": 2, "five": 10, "week": 20, "cap": 85}
    assert W.plan_fire_at(ok, now)[0] == now
    stop5 = {"mode": "STOP", "slots": 0, "five": 85, "week": 40, "cap": 85, "five_reset": "2026-10-27T15:00Z", "week_reset": "2026-11-01T00:00Z"}
    assert W.plan_fire_at(stop5, now)[0] == datetime(2026, 10, 27, 15, 2, tzinfo=timezone.utc)
    stopw = {**stop5, "week": 86}
    assert W.plan_fire_at(stopw, now)[0] == datetime(2026, 11, 1, 0, 2, tzinfo=timezone.utc)
    assert W.plan_fire_at(None, now)[0] == now
    assert W.plan_fire_at({**stop5, "five_reset": "2026-10-27T11:00Z"}, now)[0] == now      # reset already past
    # end to end: a STOP plan registers a trigger at the reset, not "now"
    s = W.register("C", cwd=_repo(tmp_path / "stop"), dry=True, now=NOW, plan=stop5)
    assert "-Once -At $FireAt" in s["script"] and s["fire_at"] == "2026-10-27T15:02Z"


def test_real_path_records_one_line_and_second_run_updates(tmp_path):
    repo = _repo(tmp_path)
    ho = repo / W.HANDOVER_REL.format("C")
    ho.write_text("# Supervisor C handover | x\n\n## Goal\ng\n", encoding="utf-8")
    ran = []
    for at in ("2026-10-27T20:05Z", "2026-10-27T21:05Z"):
        W.register("C", cwd=repo, at=at, now=NOW, runner=ran.append)
    t = ho.read_text(encoding="utf-8")
    assert len(ran) == 2 and ran[0].count("Register-ScheduledTask") == 1      # idempotent: -Force, same task name
    assert "-Force" in ran[0]
    assert t.count("Successor task:") == 1 and "21:05Z" in t and "20:05Z" not in t
    assert t.splitlines()[0].startswith("# Supervisor C") and t.splitlines()[1].startswith("Successor task:")


def test_registered_handover_still_valid_form(tmp_path, monkeypatch):
    import sync
    monkeypatch.setattr(sync, "read_claims", lambda repo, ref: [])
    repo = _repo(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    p = S.handover(repo, "c", host="JIS-NB", home=home, now=NOW)
    W.record_handover(repo, "C", "Successor task: MTS-SuccWake-C fireAt 2026-10-27T20:05Z (4b2)")
    assert S.validate_form(p.read_text(encoding="utf-8")) == []


# ---- supervisor.py handover wiring ----
def _cli(monkeypatch, tmp_path, extra):
    import sync
    import mts_signal
    monkeypatch.setattr(sync, "read_claims", lambda repo, ref: [])
    monkeypatch.setattr(mts_signal, "resolve_login", lambda x: ("C", ""))
    calls = []

    def fake(login, **kw):
        calls.append((login, kw))
        return {"line": "Successor task: MTS-SuccWake-C fireAt X (4b2)", "why": "stub"}
    monkeypatch.setattr(W, "register", fake)
    monkeypatch.chdir(_repo(tmp_path))
    rc = S.main(["handover", "--login", "C", "--no-send"] + extra)
    return rc, calls


def test_handover_default_registers_successor(tmp_path, monkeypatch):
    rc, calls = _cli(monkeypatch, tmp_path, [])
    assert rc == 0 and len(calls) == 1 and calls[0][0] == "C"


def test_handover_no_wake_registers_nothing(tmp_path, monkeypatch):
    rc, calls = _cli(monkeypatch, tmp_path, ["--no-wake"])
    assert rc == 0 and calls == []


def test_handover_lead_never_wakes(tmp_path, monkeypatch):
    rc, calls = _cli(monkeypatch, tmp_path, ["--role", "lead"])
    assert calls == []


def test_handover_register_failure_does_not_break_handover(tmp_path, monkeypatch, capsys):
    import sync
    import mts_signal
    monkeypatch.setattr(sync, "read_claims", lambda repo, ref: [])
    monkeypatch.setattr(mts_signal, "resolve_login", lambda x: ("C", ""))

    def boom(*a, **k):
        raise W.WakeError("no cli")
    monkeypatch.setattr(W, "register", boom)
    monkeypatch.chdir(_repo(tmp_path))
    assert S.main(["handover", "--login", "C", "--no-send"]) == 0
    assert "NOT registered" in capsys.readouterr().out
    assert (tmp_path / W.HANDOVER_REL.format("C")).is_file()


def test_library_handover_default_does_not_wake(tmp_path, monkeypatch):
    """S.handover() called as a library (every other test) must never register a task; only the CLI default does."""
    import sync
    monkeypatch.setattr(sync, "read_claims", lambda repo, ref: [])
    monkeypatch.setattr(W, "register", lambda *a, **k: pytest.fail("registered from library call"))
    home = tmp_path / "h"
    home.mkdir()
    S.handover(_repo(tmp_path), "c", host="JIS-NB", home=home, now=NOW)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
