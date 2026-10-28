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
    def reg(login, dry=False, home=None):
        calls.append(login)
        return {"line": "Successor task: MTS-SuccWake-%s fireAt now (4b2)" % login}
    return reg


def test_wakes_once_after_boot(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)
    calls = []
    assert L.logon("B", home=home, boot=1000.0, register=_reg(calls), sleep=lambda s: None) == 0
    assert calls == ["B"]
    p = L.stamp_file("B", home)
    assert p.is_file()
    os.utime(p, (5000.0, 5000.0))
    L.logon("B", home=home, boot=1000.0, register=_reg(calls), sleep=lambda s: None)   # a second logon, same boot
    assert calls == ["B"]


def test_skips_when_supervisor_planned_since_boot(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)
    pf = L.plan_file("B", home)
    pf.parent.mkdir(parents=True)
    pf.write_text("{}", encoding="utf-8")
    os.utime(pf, (5000.0, 5000.0))
    calls = []
    L.logon("B", home=home, boot=1000.0, register=_reg(calls), sleep=lambda s: None)
    assert calls == []


def test_old_plan_before_boot_still_wakes(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)
    pf = L.plan_file("B", home)
    pf.parent.mkdir(parents=True)
    pf.write_text("{}", encoding="utf-8")
    os.utime(pf, (100.0, 100.0))
    calls = []
    L.logon("B", home=home, boot=5000.0, register=_reg(calls), sleep=lambda s: None)
    assert calls == ["B"]


def test_error_is_logged_not_raised(tmp_path, monkeypatch):
    home = _env(tmp_path, monkeypatch)

    def boom(login, dry=False, home=None):
        raise RuntimeError("no gate")
    assert L.logon("B", home=home, boot=1000.0, register=boom, sleep=lambda s: None) == 0
    assert "error" in (tmp_path / "wake" / "logon_wake.log").read_text(encoding="utf-8")


def test_bad_login_refused_and_command_shape():
    assert L.logon("Z", register=_reg([]), sleep=lambda s: None) == 0
    cmd = L.logon_command("B", python="py.exe", script="x.py")
    assert "--headless" in cmd and cmd.endswith("logon --login B")


def test_install_refuses_worktree(tmp_path):
    (tmp_path / ".git").write_text("gitdir: x", encoding="utf-8")
    assert L.install("B", checkout=tmp_path) == 2
