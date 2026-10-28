import sys; sys.dont_write_bytecode = True
"""test_aibridge_version_bump.py - every DSA-bridge change bumps the bridge version (operator 2026-10-28: fix this miss ALWAYS).

The bridge files (scripts/aibridge/**, dsa.py, aibridge_install/verify/health.py, bridge_selftest.ps1, register_aibridge.ps1) must
match the fingerprint recorded for the current version in scripts/aibridge/RELEASES.json, and the three version strings must say
that version. Before the 0.7.2 bump this failed: B196 (8fb185ac0, 2026-10-25) changed the extension with no bump.
The guard logic lives in scripts/dev/aibridge_version.py; this file runs it on the tree and on a copy with one byte changed.
"""
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
sys.path.insert(0, str(ROOT / "scripts" / "dev"))
import aibridge_version as av  # noqa: E402


def test_bridge_version_is_bumped_for_every_bridge_change():
    assert av.check(ROOT) == []


def test_guard_flags_a_bridge_change_without_a_bump(tmp_path):
    # copy the bridge files and the release record, then change one byte of the extension without bumping
    for rel in av.bridge_files(ROOT):
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)
    (tmp_path / av.RELEASES_REL).write_bytes((ROOT / av.RELEASES_REL).read_bytes())
    assert av.check(tmp_path) == []
    loop = tmp_path / "scripts/aibridge/extension/loop.js"
    loop.write_bytes(loop.read_bytes() + b"\n// a fix with no bump\n")
    problems = av.check(tmp_path)
    assert len(problems) == 1 and "bump the bridge version" in problems[0], problems
