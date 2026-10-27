import sys; sys.dont_write_bytecode = True
"""test_aibridge_payload.py - guards the AIBridge v0.7.0 payload in scripts/aibridge (operator 2026-10-14: DSA bridge must be fluent).

Expected behaviour comes from the DSA coordinator field reports of 2026-10-12 and 2026-10-14 (multi-line blocks, deterministic
auto-run, no cached result, PS 5.1 stated, fresh environment, parallel chats), not from the code under test.
The live agent test starts a scratch agent on a free local port (Windows only) and drives it over HTTP; the node test covers the extension helpers.
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
    assert '"version": "0.7.1"' in (PAYLOAD / "extension/manifest.json").read_text(encoding="utf-8")
    assert "$AgentVersion = '0.7.1'" in (PAYLOAD / "src/agent.ps1").read_text(encoding="utf-8")
    assert "L.VERSION = '0.7.1'" in (PAYLOAD / "extension/loop.js").read_text(encoding="utf-8")


def _blob_eol(p):
    """`git ls-files --eol` index column for p ('i/lf', 'i/crlf', ...), or None when git cannot say (no repo / untracked)."""
    r = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--eol", "--", str(p.relative_to(ROOT)).replace(os.sep, "/")],
                       capture_output=True, text=True)
    return r.stdout.split()[0] if r.returncode == 0 and r.stdout.strip() else None


def test_payload_is_ascii_lf_no_bom():
    # LF is checked on the committed blob (index), not the checkout: a Windows runner's autocrlf turns the working copy into CRLF.
    for p in list(PAYLOAD.rglob("*.ps1")) + list(PAYLOAD.rglob("*.js")) + list(PAYLOAD.rglob("*.json")):
        b = p.read_bytes()
        assert not b.startswith(b"\xef\xbb\xbf"), p
        eol = _blob_eol(p)
        if eol is None:
            assert b"\r" not in b, p   # no git metadata: fall back to the bytes on disk
        else:
            assert eol in ("i/lf", "i/none"), f"{p}: committed blob is {eol}"
        b.decode("ascii")


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_extension_helpers_node():
    r = subprocess.run(["node", "tests/loop.test.js"], cwd=PAYLOAD, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr


# 159 s quiet for two concurrent runs; 280 s timed out with six ship gates on one machine (2026-10-15). OURS: room for that load.
SELFTEST_TIMEOUT_S = 900


def _kill_tree(p):
    """Stop a still-running child and everything it started (the selftest's PowerShell agent). No-op once it has exited."""
    if p.poll() is None:
        subprocess.call(["taskkill", "/T", "/F", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.communicate()


def _selftest_env_name():
    """The registry variable name one selftest run would use (--print-env-name prints it and exits without starting an agent)."""
    p = subprocess.Popen([sys.executable, "tests/agent_live_selftest.py", "--print-env-name"], cwd=PAYLOAD,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        return p.communicate(timeout=30)[0].strip()
    except subprocess.TimeoutExpired:
        _kill_tree(p)
        pytest.fail("agent_live_selftest.py has no --print-env-name mode: it started the full run instead")


@pytest.mark.skipif(os.name != "nt", reason="the selftest drives the HKCU Environment registry key (winreg)")
def test_selftest_registry_variable_is_unique_per_run():
    """Gate failure 2026-10-16 (Step 4b): the selftest writes its fresh-environment variable under the HKCU Environment key, which every
    process of the user shares, and deletes it when done. With one fixed name, two runs at once (the concurrent test below, or two
    ship gates) deleted each other's value before the agent read it. Two runs must never pick the same name."""
    names = [_selftest_env_name() for _ in range(3)]
    for n in names:
        assert re.fullmatch(r"AIB_SELFTEST_[0-9A-F]{12}", n), names
    assert len(set(names)) == 3, names


@pytest.mark.skipif(os.name != "nt" or shutil.which("powershell.exe") is None, reason="needs Windows PowerShell")
def test_agent_live_selftest():
    r = subprocess.run([sys.executable, "tests/agent_live_selftest.py"], cwd=PAYLOAD, capture_output=True, text=True, timeout=SELFTEST_TIMEOUT_S)
    fails = [ln for ln in r.stdout.splitlines() if ln.startswith("FAIL")]
    assert r.returncode == 0 and not fails, "\n".join(fails)[:3000] or r.stderr[-2000:]
    assert re.search(r"\d+ passed, 0 failed", r.stdout)
