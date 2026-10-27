import sys; sys.dont_write_bytecode = True
"""Guards `aibridge_install.py --fresh` and `aibridge_verify.py` (operator 2026-10-27: the DSA bridge must exist on every MTS machine).
Expected: a machine with NO AIBridge ends with a config (own random token, loopback, one chrome-extension origin), a policy with the
secrets deny, every payload file installed, and the verify script reporting every file/fix row PASS against that tree."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
DEV = ROOT / "scripts" / "dev"


def _run(*a):
    return subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True, timeout=120)


def test_fresh_install_then_verify(tmp_path):
    dst = tmp_path / "AIBridge"
    r = _run(DEV / "aibridge_install.py", dst, "--fresh", "--origin=chrome-extension://abcdefghijklmnopabcdefghijklmnop")
    assert r.returncode == 0, r.stdout + r.stderr
    cfg = json.loads((dst / "src" / "config.json").read_text())
    assert cfg["bind"] == "127.0.0.1" and cfg["port"] == 7181
    assert cfg["allowed_origins"] == ["chrome-extension://abcdefghijklmnopabcdefghijklmnop"]
    assert len(cfg["token"]) >= 32
    bg = (dst / "extension" / "background.js").read_text()
    assert cfg["token"] in bg and "__TOKEN__" not in bg
    pol = json.loads((dst / "src" / "policy.json").read_text())
    assert pol["auto_mode"] == "fluent" and any(".secrets" in d["re"] for d in pol["deny_path_regex"])
    for rel in ("src/audit.ps1", "extension/panel.css", "src/concurrency.ps1", "tasks/mts-boot.json"):
        assert (dst / rel).is_file(), rel
    v = _run(DEV / "aibridge_verify.py", dst, "--json", "--no-roundtrip")
    rows = json.loads(v.stdout[: v.stdout.rindex("]") + 1])
    bad = [x for x in rows if x["status"] == "FAIL" and (x["check"].startswith(("file:", "fix:")) or x["check"] == "installed")]
    assert not bad, bad


def test_install_without_fresh_refuses_on_empty_root(tmp_path):
    r = _run(DEV / "aibridge_install.py", tmp_path / "none")
    assert r.returncode != 0 and "--fresh" in (r.stdout + r.stderr)


def test_verify_flags_stale_install(tmp_path):
    dst = tmp_path / "AIBridge"
    assert _run(DEV / "aibridge_install.py", dst, "--fresh", "--origin=chrome-extension://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").returncode == 0
    lp = dst / "extension" / "loop.js"
    lp.write_text(lp.read_text().replace("L.postGate = function", "L.oldGate = function"))
    v = _run(DEV / "aibridge_verify.py", dst, "--json", "--no-roundtrip")
    rows = json.loads(v.stdout[: v.stdout.rindex("]") + 1])
    assert any(x["check"].startswith("fix:B196 post gate") and x["status"] == "FAIL" for x in rows)
    assert v.returncode == 1
