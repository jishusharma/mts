"""C: drive guard: report free space and prune regenerable %TEMP% garbage left by gates, tests and Claude sessions.

Usage:
  python scripts/dev/c_drive_guard.py            report only (free GB, runaway task outputs, prunable temp)
  python scripts/dev/c_drive_guard.py --apply    prune now
  python scripts/dev/c_drive_guard.py hook       SessionStart hook: silent when C: has >= MTS_C_MIN_FREE_GB (default 15) free;
                                                 otherwise prints one warning line and starts a detached --apply run
  python scripts/dev/c_drive_guard.py logon      logon run: prunes at every logon, whatever the free space; one line to the log
  python scripts/dev/c_drive_guard.py install    register `logon` under HKCU Run (no admin, no scheduled task); run from the primary checkout
  python scripts/dev/c_drive_guard.py status     registered or not, for which checkout, last logon line
  python scripts/dev/c_drive_guard.py uninstall  remove the logon run

What it prunes (only entries whose newest file is older than the age limit; locked entries are skipped):
  %TEMP%/<prefix>*            test and gate scratch dirs (PREFIXES): 24 h
  %TEMP%/claude/<proj>/<sid>  Claude session scratch + background-task output: 3 days
What it never prunes: KEEP_NAMES (state other code reads: role injection records, host health, gate slots, relay).
What it only reports: a Claude background-task .output file over 500 MB (a runaway, e.g. a bare `python -` REPL looping on
WinError 6 wrote 3.5 GB at ~0.5 MB/s on 2026-10-18). Stopping the process is the operator's call; the line names the file.
Never touches the repo, .secrets, F:, the live tree or anything outside %TEMP%.
Who writes each prefix, and where the logs are: MyTradingSys/system/STATION_CLEANUP.md.
"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

TEMP = Path(os.environ.get("MTS_GUARD_TEMP") or os.path.expandvars(r"%LOCALAPPDATA%\Temp"))
LOG = Path(os.environ.get("MTS_GUARD_LOG") or os.path.expandvars(r"%LOCALAPPDATA%\MTS\logs\c_drive_guard.log"))
PREFIXES = ("tmp", "mts_", "r2_", "rmd_", "kill_switch_cli_", "staged_tests_", "gate_timing_test_", "aibridge_selftest_",
            "pytest-of-", "gate_budget_test_", "dsa_tpl_", "e2e_a2_", "dsa-boot-", "cicd_ps_", "lab_query_", "soak6_")
KEEP_NAMES = ("mts_roles", "mts_host_health", "mts_gate_slots", "mts_relay")
TEMP_AGE_H = 24
SESSION_AGE_H = 72
RUNAWAY_MB = 500
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "MTSTempGuard"


def free_gb(drive="C:\\"):
    try:
        return shutil.disk_usage(drive).free / 1e9
    except OSError:     # no C: (Linux CI): this is a Windows guard, stay silent
        return float("inf")


FILE_ATTRIBUTE_REPARSE_POINT = 0x400     # junctions and symlinks: never walked, never pruned


def is_reparse(st):
    return bool(getattr(st, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT)


def scan(path):
    """Entries of a directory, or [] when it cannot be listed. Never raises."""
    try:
        with os.scandir(path) as it:
            return list(it)
    except OSError:
        return []


def dir_not_reparse(path):
    """True for a real directory: not a junction, not a symlink, not a file."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    return os.path.isdir(path) and not is_reparse(st)


def stale_size(path, cutoff):
    """(stale, bytes) for one entry. stale: nothing under it is newer than cutoff. One pass that stops at the first newer
    entry. Fails closed: a reparse point, a git worktree or clone (a `.git` inside), or anything that cannot be read,
    counts as not stale."""
    st = os.lstat(path)
    if st.st_mtime >= cutoff or is_reparse(st):
        return False, 0
    if not os.path.isdir(path) or os.path.islink(path):
        return True, st.st_size
    total = 0
    todo = [path]
    while todo:
        try:
            with os.scandir(todo.pop()) as it:
                for e in it:
                    s = e.stat(follow_symlinks=False)
                    if e.name == ".git" or s.st_mtime >= cutoff or is_reparse(s):
                        return False, 0
                    if e.is_dir(follow_symlinks=False):
                        todo.append(e.path)
                    else:
                        total += s.st_size
        except OSError:
            return False, 0
    return True, total


def candidates(now=None):
    """(path, bytes) of every prunable entry."""
    now = now or time.time()
    out = []
    if TEMP.is_dir():
        cutoff = now - TEMP_AGE_H * 3600
        for e in scan(TEMP):
            if e.name == "claude" or e.name.lower() in KEEP_NAMES or not e.name.startswith(PREFIXES):
                continue
            try:
                stale, size = stale_size(e.path, cutoff)
            except OSError:
                continue
            if stale:
                out.append((e.path, size))
    cl = TEMP / "claude"
    if dir_not_reparse(cl):
        cutoff = now - SESSION_AGE_H * 3600
        for proj in scan(cl):
            if not proj.is_dir(follow_symlinks=False) or is_reparse(proj.stat(follow_symlinks=False)):
                continue
            for sess in scan(proj.path):
                try:
                    stale, size = stale_size(sess.path, cutoff)
                except OSError:
                    continue
                if stale:
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


def log(msg):
    """Append one timestamped line to the logon log. Never raises: a logon run must end quietly."""
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a", encoding="utf-8", newline="\n") as f:
            f.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), msg))
    except OSError:
        pass


def logon():
    """Logon run: prune now whatever the free space and log one line. A failure is logged, and the run still returns 0."""
    try:
        before = free_gb()
        n, freed = prune(apply=True)
        log("logon: C free %.1f GB -> %.1f GB; pruned %d temp entries, %.2f GB; runaway outputs %d"
            % (before, free_gb(), n, freed / 1e9, len(runaways())))
    except Exception as e:     # the log says why; a restart must not show an error box
        log("logon: error %r" % (e,))
    return 0


def logon_command(python=None, script=None):
    """The HKCU Run command line. conhost --headless: no console window at logon (same launch as the Antigravity daemon)."""
    conhost = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "conhost.exe")
    return '"%s" --headless "%s" "%s" logon' % (conhost, python or sys.executable,
                                             script or str(Path(__file__).resolve()))


def installed_command(key=RUN_KEY, name=RUN_NAME):
    """The registered Run command line, or None when there is none (or not Windows)."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
            return winreg.QueryValueEx(k, name)[0]
    except (ImportError, OSError):
        return None


def install(checkout=None, key=RUN_KEY, name=RUN_NAME):
    """Register `logon` for one checkout. Refuses a git worktree: tidy removes those and the run would point at nothing."""
    root = Path(checkout) if checkout else Path(__file__).resolve().parents[2]
    if (root / ".git").is_file():
        print("refused: %s is a git worktree; run install from the primary checkout" % root)
        return 2
    script = root / "scripts" / "dev" / "c_drive_guard.py"
    if not script.is_file():
        print("refused: %s not found" % script)
        return 2
    if os.name != "nt":
        print("refused: Windows only")
        return 2
    import winreg
    cmd = logon_command(script=str(script))
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, name, 0, winreg.REG_SZ, cmd)
    print("installed: HKCU\\%s  %s = %s" % (key, name, cmd))
    return 0


def uninstall(key=RUN_KEY, name=RUN_NAME):
    if os.name != "nt":
        print("refused: Windows only")
        return 2
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, name)
        print("removed: HKCU\\%s  %s" % (key, name))
    except FileNotFoundError:
        print("not installed")
    return 0


def status(key=RUN_KEY, name=RUN_NAME):
    cur = installed_command(key, name)
    if cur is None:
        print("logon run: not installed (python scripts/dev/c_drive_guard.py install, from the primary checkout)")
    else:
        print("logon run: installed" + (" for this checkout" if cur == logon_command() else "; NOT this checkout: " + cur))
        print("command: " + cur)
    try:
        last = LOG.read_text(encoding="utf-8").splitlines()[-1]
    except (OSError, IndexError):
        last = "none yet (log %s)" % LOG
    print("last logon line: " + last)
    return 0


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
    if argv[:1] == ["logon"]:
        return logon()
    if argv[:1] == ["install"]:
        return install()
    if argv[:1] == ["uninstall"]:
        return uninstall()
    if argv[:1] == ["status"]:
        return status()
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
