"""Hidden-console rule (operator 2026-11-11, windows flashing all night): every subprocess run/Popen/check_output/call/check_call in
scripts/dev and .claude/hooks passes creationflags (nowin.NOWIN, or getattr(subprocess, "CREATE_NO_WINDOW", 0)), or is on the explicit
INTERACTIVE list below (their output is the operator's console, which CREATE_NO_WINDOW would swallow). A new call without the flag fails here."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nowin       # noqa: E402
import nowin_scan  # noqa: E402

REPO = HERE.parents[1]
SCOPE = [HERE, REPO / ".claude" / "hooks"]
# file -> number of calls allowed without the flag (they inherit the console on purpose: the operator reads their output).
# Shrinks only: an entry whose count drops must be lowered (test_allowlist_is_exact), a new call needs the flag instead of a new entry.
INTERACTIVE = {
    "aibridge_install.py": 2, "cbp_schedule.py": 2, "ci_revert.py": 1, "desk.py": 1, "dsa.py": 3, "dsa_seed.py": 1,
    "lane_health.py": 1, "logon_wake.py": 1, "refresh_klines.py": 1, "run_staged_tests.py": 1, "station_disk_report.py": 1,
    "aibridge_health.py": 1, "aibridge_verify.py": 1,   # dsa.py (above) and these are fingerprinted bridge files: a code change needs a bridge version bump (aibridge_version.py), its own card
    "sync.py": 1,   # the gate run; sync installs nowin, which adds the flag when the console is hidden
}
# Run by Claude hooks (.claude/settings.json) or the ship path: no entry on the list above, ever, except sync's one gate run.
HOOK_RUN = ["c_drive_guard.py", "ci_watch.py", "mts_signal.py", "preship.py", "role_loader.py", "shot.py", "stop_guard.py",
            "trunk_lag.py", "usage_reminder.py", "supervisor.py", "bg_watch.py", "artifacts.py", "gemini_queue.py"]


def scan(src):
    return nowin_scan.offending_calls(src)


def files():
    for d in SCOPE:
        if d.is_dir():
            for p in sorted(d.glob("*.py")):
                if not p.name.startswith("test_") and not p.name.startswith("nowin_"):
                    yield p


def offenders():
    out = {}
    for p in files():
        n = len(scan(p.read_text(encoding="utf-8")))
        if n:
            out[p.name] = n
    return out


def test_no_subprocess_call_lacks_creationflags():
    bad = {k: v for k, v in offenders().items() if v > INTERACTIVE.get(k, 0)}
    assert not bad, (f"subprocess calls without creationflags (a console window flashes on Windows): {bad}. "
                     "Add creationflags=nowin.NOWIN (or getattr(subprocess, 'CREATE_NO_WINDOW', 0)).")


def test_allowlist_is_exact():
    found = offenders()
    stale = {k: (v, found.get(k, 0)) for k, v in INTERACTIVE.items() if found.get(k, 0) != v}
    assert not stale, f"INTERACTIVE entries out of date (allowed, found): {stale}: lower or delete them"


@pytest.mark.parametrize("name", [n for n in HOOK_RUN if n not in INTERACTIVE])
def test_hook_run_files_are_clean(name):
    p = HERE / name
    assert p.is_file(), name
    assert scan(p.read_text(encoding="utf-8")) == [], f"{name} runs from a hook or the ship path: every child needs creationflags"


def test_scanner_flags_a_bare_call_and_accepts_the_flag():
    assert len(scan("import subprocess\nsubprocess.run(['git'], capture_output=True)\n")) == 1
    assert len(scan("import subprocess\nsubprocess.Popen(['git'])\nsubprocess.check_output(['git'])\n")) == 2
    assert len(scan("from subprocess import run\nrun(['git'])\n")) == 1
    assert scan("import subprocess\nsubprocess.run(['git'], creationflags=0x08000000)\n") == []
    assert scan("import subprocess\nsubprocess.run(['git'], **kw)\n") == []
    assert scan("import subprocess\nsubprocess.getoutput('x')\nos.run(1)\n") == []


def test_nowin_constant_is_the_hidden_window_flag_only_on_windows():
    assert nowin.NOWIN == (0x08000000 if sys.platform == "win32" else 0)
