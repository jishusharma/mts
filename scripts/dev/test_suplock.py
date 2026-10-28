"""Supervisor lock: a recycled pid must not read as a live supervisor (apparatus_fixes.md 2026-10-11)."""
import datetime as dt, os, shutil, subprocess, sys, pathlib
import pytest

LIB = pathlib.Path(__file__).resolve().parents[1] / "core" / "suplock.ps1"
PS = shutil.which("pwsh") or shutil.which("powershell")
pytestmark = pytest.mark.skipif(not PS, reason="no powershell on this host")


def _live(content):
    cmd = f". '{LIB}'; Get-SupLockLivePid '{content}'"
    r = subprocess.run([PS, "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=60)
    return int(r.stdout.strip() or 0)


def _iso(delta_s):
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=delta_s)).isoformat()


def _target_pid():
    # a long-lived real process we can name: start a sleeper
    return subprocess.Popen([PS, "-NoProfile", "-Command", "Start-Sleep 60"])


def test_recycled_pid_is_stale():
    p = _target_pid()
    try:
        # lock written 10 min BEFORE this process started -> pid was recycled
        assert _live(f"{p.pid} {_iso(-600)}") == 0
    finally:
        p.kill()


def test_real_holder_is_live():
    p = _target_pid()
    try:
        import time; time.sleep(2)
        assert _live(f"{p.pid} {_iso(0)}") == p.pid
    finally:
        p.kill()


def test_dead_or_garbage_is_stale():
    assert _live(f"999999 {_iso(0)}") == 0
    assert _live("garbage") == 0
    assert _live("") == 0
