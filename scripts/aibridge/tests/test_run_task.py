"""B209 item 4: run-task.ps1 must never print TASK RESULT: PASS over a failed step, and must exit non-zero.
Run: python -m pytest scripts/aibridge/tests/test_run_task.py  (Windows PowerShell 5.1 only; skipped elsewhere)"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

RUNNER = Path(__file__).resolve().parents[1] / "scripts" / "run-task.ps1"
PS = shutil.which("powershell")
pytestmark = pytest.mark.skipif(not PS, reason="needs Windows PowerShell")


def _run(steps):
    with tempfile.TemporaryDirectory() as d:
        # run a copy under a temp base: the runner writes <base>/run, which must not land inside the version-fingerprinted tree
        (Path(d) / "scripts").mkdir()
        runner = Path(d) / "scripts" / "run-task.ps1"
        shutil.copyfile(RUNNER, runner)
        spec = Path(d) / "spec.json"
        spec.write_text(json.dumps({"name": "t", "spec": {"steps": steps}}), encoding="utf-8")
        p = subprocess.run([PS, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(runner),
                            "-SpecFile", str(spec)], capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout


def _py(code):
    return f'& "{sys.executable}" -c "{code}"'


def test_native_nonzero_exit_fails_the_step():
    rc, out = _run([{"name": "bad", "cmd": _py("import sys; print('FAILED: 2 step(s)'); sys.exit(1)")}])
    assert "TASK RESULT: FAIL" in out and "TASK RESULT: PASS" not in out, out
    assert rc != 0


def test_continue_step_failure_still_fails_the_task():
    rc, out = _run([{"name": "bad", "cmd": _py("import sys; sys.exit(1)"), "on_fail": "continue"},
                    {"name": "ok", "cmd": _py("print(1)")}])
    assert "TASK RESULT: PASS" not in out and "TASK RESULT: FAIL" in out, out
    assert rc != 0


def test_all_green_passes():
    rc, out = _run([{"name": "ok", "cmd": _py("print(1)")}])
    assert "TASK RESULT: PASS" in out and rc == 0, out


def _kind(cmd):
    checks = RUNNER.parents[1] / "src" / "checks.ps1"
    script = f". '{checks}'; $pol = [pscustomobject]@{{}}; Get-CmdKind $env:AIB_CMD $pol"
    import os
    p = subprocess.run([PS, "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True, timeout=60,
                       env={**os.environ, "AIB_CMD": cmd})
    return p.stdout.strip()


def test_kind_ignores_words_inside_string_literals():
    """B209 item 5: a read-only Select-String whose pattern contains write-ish words (rm, ac, mv, git push) was stamped write."""
    assert _kind("Select-String -Path a.md -Pattern 'git push|rm -rf|Set-Content' | Select -First 3") == "read"
    assert _kind('Get-Content a.md | Select-String "Remove-Item"') == "read"


def test_kind_still_flags_real_writes():
    assert _kind("Set-Content -Path a.txt -Value 'x'") == "write"
    assert _kind("git push origin main") == "write"
    assert _kind("Remove-Item 'a b.txt'") == "write"
    assert _kind("'x' | Out-File a.txt") == "write"
    assert _kind("echo hi > out.txt") == "write"
