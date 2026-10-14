import sys; sys.dont_write_bytecode = True
"""test_aibridge_payload.py - guards the AIBridge v0.7.0 payload in scripts/aibridge (operator 2026-10-14: DSA bridge must be fluent).

Expected behaviour comes from the DSA coordinator field reports of 2026-10-12 and 2026-10-14 (multi-line blocks, deterministic
auto-run, no cached result, PS 5.1 stated, fresh environment, parallel chats), not from the code under test.
The live agent test starts a scratch agent on port 7199 (Windows only) and drives it over HTTP; the node test covers the extension helpers.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
PAYLOAD = ROOT / "scripts" / "aibridge"


def test_payload_files_exist_and_versions_agree():
    for rel in ("src/agent.ps1", "src/checks.ps1", "extension/content.js", "extension/loop.js", "extension/background.js",
                "extension/manifest.json", "scripts/run-task.ps1", "scripts/start-agent.ps1", "policy_patch.json"):
        assert (PAYLOAD / rel).is_file(), rel
    assert '"version": "0.7.0"' in (PAYLOAD / "extension/manifest.json").read_text(encoding="utf-8")
    assert "$AgentVersion = '0.7.0'" in (PAYLOAD / "src/agent.ps1").read_text(encoding="utf-8")
    assert "L.VERSION = '0.7.0'" in (PAYLOAD / "extension/loop.js").read_text(encoding="utf-8")


def test_payload_is_ascii_lf_no_bom():
    for p in list(PAYLOAD.rglob("*.ps1")) + list(PAYLOAD.rglob("*.js")) + list(PAYLOAD.rglob("*.json")):
        b = p.read_bytes()
        assert not b.startswith(b"\xef\xbb\xbf"), p
        assert b"\r" not in b, p
        b.decode("ascii")


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_extension_helpers_node():
    r = subprocess.run(["node", "tests/loop.test.js"], cwd=PAYLOAD, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.skipif(os.name != "nt" or shutil.which("powershell.exe") is None, reason="needs Windows PowerShell")
def test_agent_live_selftest():
    r = subprocess.run([sys.executable, "tests/agent_live_selftest.py"], cwd=PAYLOAD, capture_output=True, text=True, timeout=280)
    fails = [ln for ln in r.stdout.splitlines() if ln.startswith("FAIL")]
    assert r.returncode == 0 and not fails, "\n".join(fails)[:3000] or r.stderr[-2000:]
    assert re.search(r"\d+ passed, 0 failed", r.stdout)
