import sys; sys.dont_write_bytecode = True
"""test_build_check_report_reasons.py - Build-Check report must say WHY a build failed (field report 2026-10-14).

DSA session: BUILD_REPORT said only 'Java compile: FAIL (2.4 s)'; the cause (mvn under JDK 11, pom targets 17) took 12 turns.
Spec: (1) a failing Java compile lists the first 5 [ERROR] lines of the mvn output plus a 'java: ... mvn: ...' line; the Java tests
FAIL path does the same. (2) STATUS names the failing axes and sits right after the host line (one STATUS line only).
(3) In-flight .new files older than 48 h are listed under their own 'Stale .new files' heading.
The run uses a fake mvn/java on PATH (a .cmd shim), so no real Maven is needed. Set BUILD_CHECK_SCRIPT to test a staged copy.
"""
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(os.environ.get("BUILD_CHECK_SCRIPT", ROOT / "scripts" / "Build-Check.ps1"))
PS = shutil.which("powershell") or shutil.which("pwsh")

# Build-Check's full tier runs this suite, so a test that calls Build-Check would recurse without end.
NESTED = os.environ.get("B091_NESTED") == "1"
pytestmark = pytest.mark.skipif(PS is None or NESTED or os.name != "nt",
                                reason="powershell/.cmd shims missing or already inside a Build-Check run")

STALE_DIR = ROOT / "MyTradingSys" / "runtime" / "_b_report_reasons_test"


@pytest.fixture(scope="module")
def failing_run(tmp_path_factory):
    shim = tmp_path_factory.mktemp("fakebin")
    errs = "\r\n".join("echo [ERROR] fake error number %d invalid target release: 17" % i for i in range(1, 9))
    (shim / "mvn.cmd").write_text("@echo off\r\necho [INFO] banner line\r\n%s\r\nexit /b 1\r\n" % errs, newline="")
    (shim / "java.cmd").write_text('@echo off\r\necho openjdk version "11.0.99" 1>&2\r\necho second line 1>&2\r\nexit /b 0\r\n', newline="")
    STALE_DIR.mkdir(parents=True, exist_ok=True)
    stale, fresh = STALE_DIR / "old_thing.py.new", STALE_DIR / "fresh_thing.py.new"
    stale.write_text("x"); fresh.write_text("x")
    old = time.time() - 72 * 3600
    os.utime(stale, (old, old))
    try:
        env = {**os.environ, "B091_NESTED": "1", "PATH": str(shim) + os.pathsep + os.environ["PATH"]}
        p = subprocess.run([PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), "-Quick", "-ReadOnly"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT, env=env)
    finally:
        shutil.rmtree(STALE_DIR, ignore_errors=True)
    return p.stdout.splitlines()


def test_compile_fail_lists_first_five_errors(failing_run):
    i = next(n for n, l in enumerate(failing_run) if l.startswith("Java compile:  FAIL"))
    errs = [l for l in failing_run[i + 1:i + 10] if l.startswith("    [ERROR]")]
    assert len(errs) == 5
    assert "invalid target release: 17" in errs[0]
    assert not any("error number 6" in l for l in failing_run)


def test_compile_fail_names_java_and_mvn(failing_run):
    j = [l for l in failing_run if l.startswith("  java: ")]
    assert j, "no 'java:' line"
    assert 'openjdk version "11.0.99"' in j[0] and "second line" not in j[0]
    assert re.search(r"mvn: \S*mvn\.cmd", j[0])


def test_status_names_failing_axes_after_host(failing_run):
    assert failing_run[1].startswith("host:")
    assert failing_run[2].startswith("STATUS: FAIL (") and "QUICK" in failing_run[2]
    assert "Java compile" in failing_run[2]
    assert sum(1 for l in failing_run if l.startswith("STATUS:")) == 1


def test_stale_new_files_listed_separately(failing_run):
    head = "Stale .new files (older than 48 h; archive with python scripts/dev/declutter_backups.py --apply):"
    h = failing_run.index(head)
    inflight = next(n for n, l in enumerate(failing_run) if l.startswith("In-flight .new files:"))
    fresh_block = failing_run[inflight:h]
    assert any("fresh_thing.py.new" in l for l in fresh_block)
    assert not any("old_thing.py.new" in l for l in fresh_block)
    assert any("old_thing.py.new" in l for l in failing_run[h:])


def test_java_tests_fail_path_shows_reasons():
    txt = SCRIPT.read_text(encoding="utf-8")
    seg = txt[txt.index('"Java tests:    FAIL'):]
    seg = seg[:seg.index("$overallFail = $true")]
    assert "Get-FailSnippet" in seg and "java:" in txt
