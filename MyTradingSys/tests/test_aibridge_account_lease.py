import sys; sys.dont_write_bytecode = True
"""test_aibridge_account_lease.py - one machine per DeepSeek account (card dsa-bridge-avoid-deepseek-block-1108, DSA_BLOCK_REVIEW.md rank 2).

Block day 2026-11-07: one account was driven from three machines. The agent keeps an account lease (account label, host,
heartbeat) in a lease folder every host can see (config lease_dir; default run\\leases on this host only). Hands-free arms only when
the lease is granted. Two fake hosts run the real scripts/aibridge/src/lease.ps1 against one folder (Windows PowerShell):
the second host asking for the same label is refused account_in_use. Fails on 0.7.32 (no lease.ps1).
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
LEASE_PS1 = ROOT / "scripts" / "aibridge" / "src" / "lease.ps1"
PS = shutil.which("powershell") or shutil.which("pwsh")
pytestmark = pytest.mark.skipif(PS is None, reason="no PowerShell")


def lease(dir_, host, account, action="acquire", now=None, ttl=180):
    """Call Invoke-AccountLease as `host`; `now` (epoch s) is the fake clock. -> dict(ok, reason, holder)."""
    assert LEASE_PS1.is_file(), "lease.ps1 missing (0.7.32 has no account lease)"
    cmd = (". '%s'; $r = Invoke-AccountLease -Account '%s' -Dir '%s' -Me '%s' -Action '%s' -TtlS %d%s; $r | ConvertTo-Json -Compress"
           % (LEASE_PS1, account, dir_, host, action, ttl, (" -NowS %d" % now) if now is not None else ""))
    r = subprocess.run([PS, "-NoProfile", "-NonInteractive", "-Command", cmd], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_second_host_for_the_same_account_is_refused(tmp_path):
    a = lease(tmp_path, "JIS-NB", "awgp", now=1000)
    assert a["ok"] is True
    b = lease(tmp_path, "JIS-NUC", "awgp", now=1030)
    assert b["ok"] is False and b["reason"] == "account_in_use" and b["holder"] == "JIS-NB"
    c = lease(tmp_path, "DESKTOP-F7IU69N", "awgp", now=1060)
    assert c["ok"] is False and c["reason"] == "account_in_use"


def test_holder_renews_and_other_accounts_are_free(tmp_path):
    assert lease(tmp_path, "JIS-NB", "awgp", now=1000)["ok"] is True
    assert lease(tmp_path, "JIS-NB", "awgp", action="beat", now=1100)["ok"] is True
    assert lease(tmp_path, "JIS-NUC", "awgp", now=1200)["ok"] is False        # renewed at 1100: still held at 1200
    assert lease(tmp_path, "JIS-NUC", "other-account", now=1200)["ok"] is True


def test_lease_ends_on_release_or_after_the_ttl(tmp_path):
    assert lease(tmp_path, "JIS-NB", "awgp", now=1000)["ok"] is True
    assert lease(tmp_path, "JIS-NUC", "awgp", now=1000 + 181)["ok"] is True   # JIS-NB went silent for over 180 s
    assert lease(tmp_path, "JIS-NUC", "awgp", action="release", now=1300)["ok"] is True
    assert lease(tmp_path, "JIS-NB", "awgp", now=1301)["ok"] is True


def test_only_the_holder_can_release(tmp_path):
    assert lease(tmp_path, "JIS-NB", "awgp", now=1000)["ok"] is True
    assert lease(tmp_path, "JIS-NUC", "awgp", action="release", now=1010)["ok"] is False
    assert lease(tmp_path, "JIS-NUC", "awgp", now=1020)["ok"] is False


def test_agent_wires_the_lease_into_the_event_path():
    agent = (ROOT / "scripts" / "aibridge" / "src" / "agent.ps1").read_text(encoding="utf-8")
    assert "lease.ps1" in agent and "Invoke-AccountLease" in agent and "account_in_use" in agent


def test_live_agent_grants_then_refuses_when_another_host_holds_the_account(tmp_path):
    """The real agent over HTTP (scratch copy): an arm request is granted; with another host's fresh lease file it is refused account_in_use."""
    import sys
    sys.path.insert(0, str(ROOT / "MyTradingSys" / "tests"))
    import time
    from aibridge_scratch import Scratch
    lease_dir = tmp_path / "leases"
    ag = Scratch({"lease_dir": str(lease_dir)})
    try:
        def ask(ev):
            return ag.http("POST", "/run", {"token": ag.token, "event": ev, "auto": True, "rid": "t1"})
        code, body = ask("LEASE awgp")
        assert code == 200 and body.get("lease") == "ok", body
        assert (lease_dir / "awgp.json").is_file()
        assert ask("LEASE_BEAT awgp")[1].get("lease") == "ok"
        assert ask("LEASE_RELEASE awgp")[1].get("lease") == "ok"
        assert not (lease_dir / "awgp.json").exists()
        (lease_dir / "awgp.json").write_text(json.dumps({"account": "awgp", "host": "JIS-NUC", "ts": int(time.time())}), encoding="utf-8")
        code, body = ask("LEASE awgp")
        assert code == 200 and body.get("lease") == "account_in_use" and body.get("holder") == "JIS-NUC", body
        assert ask("LEASE other")[1].get("lease") == "ok"
    finally:
        ag.close()
