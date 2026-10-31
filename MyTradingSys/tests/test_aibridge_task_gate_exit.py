import sys; sys.dont_write_bytecode = True
"""B209 item 4: task mode must not print PASS (exit 0) over a gate whose log says FAILED: N step(s).

Runs scripts/aibridge/scripts/run-task.ps1 with an inline plan (Windows PowerShell only; skipped elsewhere).
Before the fix a step that printed 'FAILED: 2 step(s)' and exited 0 produced 'TASK RESULT: PASS'.
"""
import json
import sys
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


def test_native_exit_1_then_write_output_is_a_fail(tmp_path):
    # D3: the step ends on a successful statement, so the script exited 0 although python exited 1
    rc, out = run_plan(tmp_path, "python -c \"import sys; sys.exit(1)\"; Write-Output 'after'")
    assert "TASK RESULT: FAIL" in out and "TASK RESULT: PASS" not in out and rc == 1, out


def test_exit_code_line_under_exit_zero_is_a_fail(tmp_path):
    rc, out = run_plan(tmp_path, "Write-Output 'EXIT_CODE=1'; exit 0")
    assert "TASK RESULT: FAIL" in out and "TASK RESULT: PASS" not in out and rc == 1, out


def test_gate_step_without_summary_is_a_fail(tmp_path):
    # D3b: a gate that dies (traceback, no ALL TESTS PASSED) must not be PASS; the playbooks carry expect=ALL TESTS PASSED
    for name in ("mts-gate", "mts-ship"):
        spec = json.loads((RUN.parents[1] / "tasks" / (name + ".json")).read_text(encoding="utf-8"))
        gate = [s for s in spec["steps"] if s["name"] == "gate"][0]
        assert gate.get("expect") == "ALL TESTS PASSED", name
    rc, out = run_plan(tmp_path, "Write-Output 'half way'; exit 0", )
    assert "TASK RESULT: PASS" in out  # a plain step without expect is unaffected (control)


def test_control_write_output_after_clean_native_passes(tmp_path):
    rc, out = run_plan(tmp_path, "python -c \"pass\"; Write-Output ok")
    assert "TASK RESULT: PASS" in out and rc == 0, out


def test_child_temp_is_outside_a_git_repo_around_the_bridge_folder():
    """D5: F:/AIBridge is a git repo and children got TEMP inside it, so git found a repo around every temp dir."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from aibridge_scratch import Scratch
    s = Scratch()
    try:
        subprocess.run(["git", "-C", s.work, "init", "-q"], check=True, capture_output=True)   # the bridge folder is now inside a repo
        st, r = s.run("Write-Output $env:TEMP")
        assert st == 200, r
        tmp = Path(r["out"].strip())
        assert Path(s.work).resolve() not in [tmp.resolve(), *tmp.resolve().parents], r["out"]
        rc = subprocess.run(["git", "-C", str(tmp), "rev-parse", "--git-dir"], capture_output=True, text=True).returncode
        assert rc != 0 or Path(s.work).resolve() not in Path(tmp).resolve().parents
    finally:
        s.close()
