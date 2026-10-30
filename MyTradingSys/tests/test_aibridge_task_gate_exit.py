import sys; sys.dont_write_bytecode = True
"""B209 item 4: task mode must not print PASS (exit 0) over a gate whose log says FAILED: N step(s).

Runs scripts/aibridge/scripts/run-task.ps1 with an inline plan (Windows PowerShell only; skipped elsewhere).
Before the fix a step that printed 'FAILED: 2 step(s)' and exited 0 produced 'TASK RESULT: PASS'.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
RUN = ROOT / "scripts" / "aibridge" / "scripts" / "run-task.ps1"
PS = shutil.which("powershell.exe") or shutil.which("powershell")
pytestmark = pytest.mark.skipif(not PS, reason="needs Windows PowerShell")


def run_plan(tmp_path, cmd):
    # run-task writes its logs under <parent of scripts>/run; copy the runner into a scratch layout
    base = tmp_path / "bridge"
    (base / "scripts").mkdir(parents=True)
    shutil.copy2(RUN, base / "scripts" / "run-task.ps1")
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"name": "t", "spec": {"steps": [{"name": "gate", "cmd": cmd, "cwd": str(tmp_path)}]}}), encoding="utf-8")
    p = subprocess.run([PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(base / "scripts" / "run-task.ps1"), str(spec)],
                       capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout


def test_failed_line_with_exit_zero_is_a_fail(tmp_path):
    rc, out = run_plan(tmp_path, "Write-Output 'FAILED: 2 step(s)'; exit 0")
    assert "TASK RESULT: FAIL" in out and "TASK RESULT: PASS" not in out, out
    assert rc == 1


def test_clean_step_still_passes(tmp_path):
    rc, out = run_plan(tmp_path, "Write-Output 'FAILED: 0 step(s)'; exit 0")
    assert "TASK RESULT: PASS" in out and rc == 0, out
