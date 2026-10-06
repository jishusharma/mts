import sys; sys.dont_write_bytecode = True
"""test_b091_build_check_tiers.py - B091 spec (items/B091_build_check_speed.md, fixes A and B).

Spec: Build-Check -Quick skips the math tests (the release gate runs them); -ReadOnly does not rewrite
BUILD_REPORT.md, so the tree stays clean between runs. Set BUILD_CHECK_SCRIPT to test a staged copy.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(os.environ.get("BUILD_CHECK_SCRIPT", ROOT / "scripts" / "Build-Check.ps1"))
REPORT = ROOT / "MyTradingSys" / "runtime" / "BUILD_REPORT.md"
PS = shutil.which("powershell") or shutil.which("pwsh")

# Build-Check's full tier runs this suite, so a test that calls Build-Check would recurse without end.
NESTED = os.environ.get("B091_NESTED") == "1"
pytestmark = pytest.mark.skipif(PS is None or NESTED, reason="powershell missing or already inside a Build-Check run")


def run(*flags):
    return subprocess.run([PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), *flags],
                          capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT, env={**os.environ, "B091_NESTED": "1"})


@pytest.fixture(scope="module")
def quick_ro():
    before = REPORT.read_bytes() if REPORT.exists() else None
    p = run("-Quick", "-ReadOnly")
    after = REPORT.read_bytes() if REPORT.exists() else None
    return p.stdout, before, after


def test_quick_skips_math_tests(quick_ro):
    out = quick_ro[0]
    assert "Math tests:    SKIP (quick tier" in out
    assert "Math tests:    PASS" not in out


def test_quick_status_names_the_tier(quick_ro):
    status = [l for l in quick_ro[0].splitlines() if l.startswith("STATUS:")]
    assert status and "QUICK" in status[0]


def test_read_only_leaves_report_untouched(quick_ro):
    assert quick_ro[1] == quick_ro[2]
    assert "not written (-ReadOnly)" in quick_ro[0]
