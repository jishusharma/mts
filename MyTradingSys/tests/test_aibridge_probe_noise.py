import sys; sys.dont_write_bytecode = True
"""AIBridge root cause 5: a bare TCP connect (supervisor liveness probe) wrote 2 audit rows (not_found + aborted 404 write).
The agent must drop a request with no request line silently; supervisor probes GET /ping instead. Installer --help must not install."""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])


def test_installer_help_does_not_install():
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "dev" / "aibridge_install.py"), "--help", "--dry"],
                       capture_output=True, text=True, timeout=60)
    assert p.returncode == 0 and "usage" in p.stdout.lower() and "would write" not in p.stdout


def test_supervisor_probe_uses_ping():
    src = (ROOT / "scripts" / "dev" / "supervisor.py").read_text(encoding="utf-8")
    i = src.index("def _local_bridge")
    assert "/ping" in src[i:i + 700]


@pytest.mark.skipif(not __import__("shutil").which("powershell.exe"), reason="needs Windows PowerShell")
def test_bare_connect_leaves_no_audit_rows():
    from aibridge_scratch import Scratch
    s = Scratch()
    try:
        audit = os.path.join(s.sdir, "audit.jsonl")
        n0 = sum(1 for _ in open(audit, "rb")) if os.path.exists(audit) else 0
        for _ in range(3):
            socket.create_connection(("127.0.0.1", s.port), timeout=2).close()
        time.sleep(2)
        assert s.http("GET", "/ping")[1].get("ok")          # still answering
        n1 = sum(1 for _ in open(audit, "rb")) if os.path.exists(audit) else 0
        assert n1 == n0
    finally:
        s.close()


@pytest.mark.skipif(not __import__("shutil").which("powershell.exe") or os.name != "nt", reason="needs Windows PowerShell")
def test_parent_kill_leaves_no_probe_powershell():
    """Scratch agent.ps1 must die with its parent python (capped/killed pytest never runs close())."""
    code = ("import sys,time;sys.path.insert(0,%r);from aibridge_scratch import Scratch;s=Scratch();"
            "print(s.work,flush=True);time.sleep(600)" % str(Path(__file__).resolve().parent))
    p = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, text=True)
    work = p.stdout.readline().strip()
    assert "aib_probe_" in work

    def alive():
        q = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                            "(Get-CimInstance Win32_Process -Filter \"Name='powershell.exe'\" | Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -like '*%s*agent.ps1*' } | Measure-Object).Count"
                            % os.path.basename(work)], capture_output=True, text=True, timeout=60)
        return int(q.stdout.strip() or 0)
    try:
        assert alive() >= 1                                  # probe is really running
        subprocess.call(["taskkill", "/F", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # parent only, no /T
        p.wait(timeout=30)
        for _ in range(20):
            if alive() == 0:
                break
            time.sleep(0.5)
        assert alive() == 0
    finally:
        subprocess.call(["powershell.exe", "-NoProfile", "-Command",
                         "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*%s*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" % os.path.basename(work)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import shutil
        shutil.rmtree(work, ignore_errors=True)
