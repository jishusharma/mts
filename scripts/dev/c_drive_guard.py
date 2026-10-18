"""C: drive guard: report free space and prune regenerable %TEMP% garbage left by gates, tests and Claude sessions.

Usage:
  python scripts/dev/c_drive_guard.py            report only (free GB, runaway task outputs, prunable temp)
  python scripts/dev/c_drive_guard.py --apply    prune now
  python scripts/dev/c_drive_guard.py hook       SessionStart hook: silent when C: has >= MTS_C_MIN_FREE_GB (default 15) free;
                                                 otherwise prints one warning line and starts a detached --apply run

What it prunes (only entries whose newest file is older than the age limit; locked entries are skipped):
  %TEMP%/<prefix>*            test and gate scratch dirs (tmp*, mts_*, r2_*, ...): 24 h. 2026-10-18 JIS-NB: 101k dirs, ~2 GB.
  %TEMP%/claude/<proj>/<sid>  Claude session scratch + background-task output: 3 days.
What it only reports: a Claude background-task .output file over 500 MB (a runaway, e.g. a bare `python -` REPL looping on
WinError 6 wrote 3.5 GB at ~0.5 MB/s on 2026-10-18). Stopping the process is the operator's call; the line names the file.
Never touches the repo, .secrets, F:, the live tree or anything outside %TEMP%.
"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

TEMP = Path(os.environ.get("MTS_GUARD_TEMP") or os.path.expandvars(r"%LOCALAPPDATA%\Temp"))
PREFIXES = ("tmp", "mts_", "r2_", "rmd_", "kill_switch_cli_", "staged_tests_", "gate_timing_test_", "aibridge_selftest_",
            "pytest-of-")
TEMP_AGE_H = 24
SESSION_AGE_H = 72
RUNAWAY_MB = 500


def free_gb(drive="C:\\"):
    try:
        return shutil.disk_usage(drive).free / 1e9
    except OSError:     # no C: (Linux CI): this is a Windows guard, stay silent
        return float("inf")


def newest_and_size(path):
    """Newest mtime and total byte size of a file or tree (lstat, no link following)."""
    st = os.lstat(path)
    newest, size = st.st_mtime, 0
    if not os.path.isdir(path) or os.path.islink(path):
        return newest, st.st_size
    for root, dirs, files in os.walk(path):
        for n in dirs + files:
            try:
                s = os.lstat(os.path.join(root, n))
            except OSError:
                continue
            newest = max(newest, s.st_mtime)
            if n in files:
                size += s.st_size
    return newest, size


def candidates(now=None):
    """(path, bytes) of every prunable entry."""
    now = now or time.time()
    out = []
    if TEMP.is_dir():
        for e in os.scandir(TEMP):
            if e.name == "claude" or not e.name.startswith(PREFIXES):
                continue
            try:
                newest, size = newest_and_size(e.path)
            except OSError:
                continue
            if newest < now - TEMP_AGE_H * 3600:
                out.append((e.path, size))
    cl = TEMP / "claude"
    if cl.is_dir():
        for proj in os.scandir(cl):
            if not proj.is_dir():
                continue
            for sess in os.scandir(proj.path):
                try:
                    newest, size = newest_and_size(sess.path)
                except OSError:
                    continue
                if newest < now - SESSION_AGE_H * 3600:
                    out.append((sess.path, size))
    return out


def runaways():
    """Claude background-task outputs over RUNAWAY_MB: (path, MB)."""
    out = []
    for p in (TEMP / "claude").glob("*/*/tasks/*.output"):
        try:
            mb = p.stat().st_size / 1e6
        except OSError:
            continue
        if mb > RUNAWAY_MB:
            out.append((str(p), mb))
    return out


def remove(path):
    try:
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True
    except OSError:
        return not os.path.exists(path)


def prune(apply):
    freed = n = 0
    for path, size in candidates():
        if not apply or remove(path):
            freed += size
            n += 1
    return n, freed


def main(argv):
    if argv[:1] == ["hook"]:
        limit = float(os.environ.get("MTS_C_MIN_FREE_GB", "15"))
        gb = free_gb()
        if gb >= limit:
            return 0
        msg = f"C: LOW: {gb:.1f} GB free (< {limit:g}); c_drive_guard --apply started in the background."
        for p, mb in runaways():
            msg += f" RUNAWAY task output {mb:.0f} MB: {p}"
        print(msg)
        flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--apply"], creationflags=flags,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
        except OSError:
            pass
        return 0
    apply = "--apply" in argv
    before = free_gb()
    print(f"C: free {before:.2f} GB")
    for p, mb in runaways():
        print(f"RUNAWAY task output {mb:.0f} MB (stop its process, then delete): {p}")
    n, freed = prune(apply)
    verb = "pruned" if apply else "would prune"
    print(f"{verb} {n} temp entries, {freed / 1e9:.2f} GB" + ("" if apply else " (dry run; --apply to prune)"))
    if apply:
        print(f"C: free now {free_gb():.2f} GB")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
