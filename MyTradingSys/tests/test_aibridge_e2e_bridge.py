import sys; sys.dont_write_bytecode = True
"""test_aibridge_e2e_bridge.py - scripts/aibridge/tests/e2e_bridge.py reports PASS on the trunk payload and FAIL on a deliberately
broken scratch copy (the 0.7.3 behaviour put back: no native exit propagation, no EXIT_CODE fail pattern, no selectBlocks/replyWatch)."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "aibridge" / "tests" / "e2e_bridge.py"
PAYLOAD = ROOT / "scripts" / "aibridge"
IS_WIN = os.name == "nt" and shutil.which("powershell.exe") is not None and shutil.which("node") is not None
needs = pytest.mark.skipif(not IS_WIN, reason="needs Windows PowerShell and node")


def _e2e(payload, out):
    p = subprocess.run([sys.executable, str(SCRIPT), "--json", "--payload", str(payload), "--out", str(out)],
                       capture_output=True, text=True, timeout=280)
    return p.returncode, json.loads(p.stdout)


def _verdicts(rep):
    return {c["case"]: c["verdict"] for c in rep["cases"]}


@needs
def test_e2e_passes_on_trunk(tmp_path):
    rc, rep = _e2e(PAYLOAD, tmp_path)
    v = _verdicts(rep)
    assert rc == 0 and rep["ok"], rep
    assert [v[k] for k in ("E0", "E1", "E2", "E3", "E4")] == ["PASS"] * 5 and v["E5"] == "NOT_CHECKED"
    assert rep["bridge_version"] != "?"


@needs
def test_e2e_fails_on_old_runner_copy(tmp_path):
    bad = tmp_path / "old073"
    shutil.copytree(PAYLOAD, bad, ignore=shutil.ignore_patterns("tests"))
    rt = bad / "scripts" / "run-task.ps1"
    s = rt.read_text(encoding="utf-8")
    s2 = s.replace("if (`$null -ne `$global:LASTEXITCODE) { exit [int]`$global:LASTEXITCODE }", "").replace("|EXIT_CODE=[1-9]\\d*\\s*$", "")
    assert s2 != s
    rt.write_text(s2, encoding="utf-8", newline="")
    lj = bad / "extension" / "loop.js"
    t = lj.read_text(encoding="utf-8")
    t2 = t.replace("L.selectBlocks =", "L.selectBlocksOld =").replace("L.replyWatch =", "L.replyWatchOld =")
    assert t2 != t
    lj.write_text(t2, encoding="utf-8", newline="")
    rc, rep = _e2e(bad, tmp_path / "out")
    v = _verdicts(rep)
    assert rc == 1 and not rep["ok"]
    assert [v[k] for k in ("E1", "E2", "E3", "E4")] == ["FAIL"] * 4, v
