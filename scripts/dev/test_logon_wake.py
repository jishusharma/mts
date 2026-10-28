"""Tests for logon_wake.py (SCHEDULING_POLICY 4d). Stub register / no registry / no real task.
Run: python scripts/dev/test_logon_wake.py"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import logon_wake as L


def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("MTS_SUCC_WAKE_DIR", str(tmp_path / "wake"))
    return tmp_path / "home"


def _reg(calls):
    def reg(login, dry=False, home=None, prompt_file=None):
        calls.append(login)
        return {"line": "Successor task: MTS-SuccWake-%s fireAt now (4b2)" % login}
    return reg


def test_wakes_once_after_boot(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)
    calls = []
    assert L.logon("B", home=home, boot=1000.0, register=_reg(calls), sleep=lambda s: None, refresh=lambda r: 'stub', launch=lambda: 'stub') == 0
    assert calls == ["B"]
    p = L.stamp_file("B", home)
    assert p.is_file()
    os.utime(p, (5000.0, 5000.0))
    L.logon("B", home=home, boot=1000.0, register=_reg(calls), sleep=lambda s: None, refresh=lambda r: 'stub', launch=lambda: 'stub')   # a second logon, same boot
    assert calls == ["B"]


def test_skips_when_supervisor_planned_since_boot(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)
    pf = L.plan_file("B", home)
    pf.parent.mkdir(parents=True)
    pf.write_text("{}", encoding="utf-8")
    os.utime(pf, (5000.0, 5000.0))
    calls = []
    L.logon("B", home=home, boot=1000.0, register=_reg(calls), sleep=lambda s: None, refresh=lambda r: 'stub', launch=lambda: 'stub')
    assert calls == []


def test_old_plan_before_boot_still_wakes(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)
    pf = L.plan_file("B", home)
    pf.parent.mkdir(parents=True)
    pf.write_text("{}", encoding="utf-8")
    os.utime(pf, (100.0, 100.0))
    calls = []
    L.logon("B", home=home, boot=5000.0, register=_reg(calls), sleep=lambda s: None, refresh=lambda r: 'stub', launch=lambda: 'stub')
    assert calls == ["B"]


def test_error_is_logged_not_raised(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)

    def boom(login, dry=False, home=None, prompt_file=None):
        raise RuntimeError("no gate")
    assert L.logon("B", home=home, boot=1000.0, register=boom, sleep=lambda s: None, refresh=lambda r: 'stub', launch=lambda: 'stub') == 0
    assert "error" in (tmp_path / "wake" / "logon_wake.log").read_text(encoding="utf-8")


def test_bad_login_refused_and_command_shape():
    assert L.logon("Z", register=_reg([]), sleep=lambda s: None, refresh=lambda r: 'stub', launch=lambda: 'stub') == 0
    cmd = L.logon_command("B", python="py.exe", script="x.py")
    assert "--headless" in cmd and cmd.endswith("logon --login B")


def test_install_refuses_worktree(tmp_path):
    (tmp_path / ".git").write_text("gitdir: x", encoding="utf-8")
    assert L.install("B", checkout=tmp_path) == 2


def test_recovery_prompt_covers_every_restart_step(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)
    pr = L.recovery_prompt("B", 1000.0, home, str(tmp_path / "wake"))
    for need in ("You are Supervisor. Login B", "sync.py start", "station --apply", "sync.py claims", "release",
                 "origin/fast-track", "supervisor.py plan", "RED", "never from memory", "USAGE"):
        assert need in pr, need
    assert "'@" not in pr


def test_logon_hands_the_recovery_prompt_to_register(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)
    seen = {}

    def reg(login, dry=False, home=None, prompt_file=None):
        seen["text"] = Path(prompt_file).read_text(encoding="utf-8")
        return {"line": "Successor task: x"}
    L.logon("B", home=home, boot=1000.0, register=reg, sleep=lambda s: None, refresh=lambda r: "stub", launch=lambda: "stub")
    assert "UNPLANNED RESTART RECOVERY" in seen["text"]


def test_new_boot_wakes_again_even_with_an_old_stamp(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)
    calls = []
    L.logon("B", home=home, boot=1000.0, register=_reg(calls), sleep=lambda s: None, refresh=lambda r: "stub", launch=lambda: "stub")
    os.utime(L.stamp_file("B", home), (1500.0, 1500.0))
    L.logon("B", home=home, boot=9000.0, register=_reg(calls), sleep=lambda s: None, refresh=lambda r: "stub", launch=lambda: "stub")   # rebooted again
    assert calls == ["B", "B"]


def test_unreadable_boot_still_wakes_not_silent(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)
    calls = []
    L.logon("B", home=home, boot=0.0, register=_reg(calls), sleep=lambda s: None, refresh=lambda r: "stub", launch=lambda: "stub")
    assert calls == ["B"]


def test_refresh_clone_never_raises_and_reports_dirty():
    class R:
        returncode = 1
    assert "not fast-forwarded" in L.refresh_clone(Path("."), run=lambda *a: R())

    def boom(*a):
        raise OSError("no git")
    assert "failed" in L.refresh_clone(Path("."), run=boom)


def test_real_register_dry_accepts_the_recovery_prompt(tmp_path, monkeypatch):
    """Integration: the real successor_wake.register in --dry accepts the prompt file (no here-string clash)."""
    import successor_wake as W
    home = _env(tmp_path, monkeypatch)
    pf = tmp_path / "p.txt"
    pf.write_text(L.recovery_prompt("B", 1000.0, home, str(tmp_path)), encoding="utf-8")
    r = W.register("B", dry=True, prompt_file=str(pf), home=home, base=str(tmp_path))
    assert "UNPLANNED RESTART RECOVERY" in r["script"] and r["ran"] is False


def test_launch_app_starts_only_when_not_running():
    started = []
    assert L.launch_app(running=True, start=lambda: started.append(1)) == "already running" and not started
    assert L.launch_app(running=False, start=lambda: started.append(1)) == "started" and started == [1]


def test_launch_app_never_raises():
    def boom():
        raise OSError("no explorer")
    assert "failed" in L.launch_app(running=False, start=boom)


def test_logon_starts_the_app_even_when_no_wake_is_needed(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)
    pf = L.plan_file("B", home)
    pf.parent.mkdir(parents=True)
    pf.write_text("{}", encoding="utf-8")
    os.utime(pf, (5000.0, 5000.0))
    seen = []
    L.logon("B", home=home, boot=1000.0, register=_reg([]), sleep=lambda s: None, refresh=lambda r: "stub", launch=lambda: seen.append(1) or "started")
    assert seen == [1]
