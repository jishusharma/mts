"""C: drive guard: report free space and prune regenerable %TEMP% garbage left by gates, tests and Claude sessions.

Usage:
  python scripts/dev/c_drive_guard.py            report only (free GB, runaway task outputs, prunable temp)
  python scripts/dev/c_drive_guard.py --apply    prune now
  python scripts/dev/c_drive_guard.py hook       SessionStart hook: starts a detached --apply run once per day per host (stamp file)
                                                 and whenever C: has < MTS_C_MIN_FREE_GB (default 15) free; silent otherwise,
                                                 or one warning line when low
  python scripts/dev/c_drive_guard.py plan       dry run: every item it would delete, one line each with the reason
  python scripts/dev/c_drive_guard.py logon      logon run: prunes at every logon, whatever the free space; one line to the log
  python scripts/dev/c_drive_guard.py install    register `logon` under HKCU Run (no admin, no scheduled task); run from the primary checkout
  python scripts/dev/c_drive_guard.py status     registered or not, for which checkout, last logon line
  python scripts/dev/c_drive_guard.py uninstall  remove the logon run

What it prunes (only entries whose newest file is older than the age limit; locked entries are skipped):
  %TEMP%/<prefix>*            test and gate scratch dirs (PREFIXES): 24 h
  %TEMP%/mts_s4_* mts_s5c_* mts_changed_*   this repo's own gate basetemps (OWN_PREFIXES): 6 h
  worktrees                   `sync.py tidy --apply`: clean, shipped, no ignored data, idle 1 h (the rules live in sync.py)
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
LOCK = LOG.parent / "c_drive_guard.lock"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)   # a console-less parent otherwise gives each child python a visible window
LOW_GAP_S = 3600
PREFIXES = ("tmp", "mts_", "r2_", "rmd_", "kill_switch_cli_", "staged_tests_", "gate_timing_test_", "aibridge_selftest_",
            "pytest-of-", "gate_budget_test_", "dsa_tpl_", "e2e_a2_", "dsa-boot-", "cicd_ps_", "lab_query_", "soak6_")
KEEP_NAMES = ("mts_roles", "mts_host_health", "mts_gate_slots", "mts_relay")
TEMP_AGE_H = 24
OWN_PREFIXES = ("mts_s4_", "mts_s5c_", "mts_changed_")   # this repo's gate/test basetemps: nobody else writes these names
OWN_AGE_H = 6                                            # DECISION (OURS): 6 h as the card said; a gate run lasts minutes
DAILY_H = 20                                             # DECISION (OURS): "once per day" = at most one run per 20 h
STAMP = Path(os.environ.get("MTS_GUARD_STAMP") or os.path.expandvars(r"%LOCALAPPDATA%\MTS\logs\c_drive_guard.stamp"))
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
        for e in scan(TEMP):
            if e.name == "claude" or e.name.lower() in KEEP_NAMES or not e.name.startswith(PREFIXES):
                continue
            cutoff = now - (OWN_AGE_H if e.name.startswith(OWN_PREFIXES) else TEMP_AGE_H) * 3600
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


def reason(path):
    """Why `candidates` lists this path (one phrase)."""
    name = Path(path).name
    if TEMP / "claude" in Path(path).parents:
        return "Claude session scratch older than %d h" % SESSION_AGE_H
    if name.startswith(OWN_PREFIXES):
        return "this repo's gate basetemp, nothing under it newer than %d h" % OWN_AGE_H
    return "known temp prefix %r, nothing under it newer than %d h" % (name.startswith(PREFIXES) and
                                                                      next(x for x in PREFIXES if name.startswith(x)), TEMP_AGE_H)


def sync_script():
    return Path(__file__).resolve().parent / "sync.py"


def run_tidy(apply):
    """`sync.py tidy [--apply]` for the checkout this script lives in. Returns its output lines ([] on any failure: never raises)."""
    try:
        r = subprocess.run([sys.executable, str(sync_script()), "tidy"] + (["--apply"] if apply else []),
                           capture_output=True, text=True, timeout=600, cwd=str(Path(__file__).resolve().parents[2]),
                           stdin=subprocess.DEVNULL, creationflags=NO_WINDOW)
        return (r.stdout or "").splitlines()
    except (OSError, subprocess.SubprocessError):
        return []


def plan():
    """Dry-run listing: (kind, path-or-name, bytes, reason) for everything --apply would delete. Deletes nothing."""
    rows = [("temp", p, size, reason(p)) for p, size in candidates()]
    for line in run_tidy(False):
        if line.startswith("would remove  "):
            name, _, why = line[len("would remove  "):].partition(": ")
            rows.append(("worktree", name, 0, why or "finished tree"))
    return rows


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


def repo_root():
    return Path(__file__).resolve().parents[2]


def repo_drive():
    """Drive (or mount) the checkout sits on: C:\\ , F:\\ ... Derived from this file, never hard-coded."""
    return repo_root().anchor or "C:\\"


def low_drives(limit):
    """[(drive, free GB)] below `limit` among C: and the repo's own drive (one entry when they are the same)."""
    out = []
    for d in dict.fromkeys(["C:\\", repo_drive()]):
        gb = free_gb(d)
        if gb < limit:
            out.append((d, gb))
    return out


def main_checkout():
    """The primary checkout of this repo (parent of the shared .git dir), or None. Works from any worktree on any host."""
    try:
        r = subprocess.run(["git", "-C", str(repo_root()), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                           capture_output=True, text=True, timeout=30)
        common = Path(r.stdout.strip())
        return common.parent if r.returncode == 0 and common.name == ".git" else None
    except (OSError, subprocess.SubprocessError):
        return None


def main_checkout_note(pull=True):
    """Hooks come from the MAIN checkout's settings.json, so a stale main means stale hooks. Returns a log phrase:
    'main checkout <n> behind; hook may be stale', plus the result of `git pull --ff-only` when the tree is clean and on the
    trunk. A dirty or off-trunk main is left alone and said so. Never raises."""
    main = main_checkout()
    if main is None:
        return "main checkout unknown"

    def git(*a, t=120):
        return subprocess.run(["git", "-C", str(main), *a], capture_output=True, text=True, timeout=t)
    try:
        git("fetch", "--quiet", "origin", "fast-track")
        behind = git("rev-list", "--count", "HEAD..origin/fast-track").stdout.strip() or "?"
        if behind in ("0", "?"):
            return "main checkout %s behind" % behind
        note = "main checkout %s behind; hook may be stale" % behind
        branch = git("branch", "--show-current").stdout.strip()
        dirty = git("status", "--porcelain", "--untracked-files=no").stdout.strip()
        if not pull:
            return note
        if dirty:
            return note + "; not pulled: main tree has uncommitted files"
        if branch != "fast-track":
            return note + "; not pulled: main is on %s" % (branch or "a detached HEAD")
        r = git("pull", "--ff-only", "--quiet", "origin", "fast-track")
        return note + ("; pulled (fast-forward)" if r.returncode == 0 else "; pull failed (not a fast-forward)")
    except (OSError, subprocess.SubprocessError) as e:
        return "main checkout check failed (%s)" % type(e).__name__


def apply_all(tag):
    """Prune temp, retire finished worktrees, log ONE line with the GB freed. Never raises."""
    before = free_gb()
    n, freed = prune(apply=True)
    gone = [l for l in run_tidy(True) if l.startswith("removed  ")]
    after = free_gb()
    log("%s: C free %.1f GB -> %.1f GB (freed %.2f GB); %d temp entries (%.2f GB); %d worktrees retired; %s"
        % (tag, before, after, max(after - before, 0) if after != float("inf") else 0, n, freed / 1e9, len(gone),
           main_checkout_note()))
    return n, freed, len(gone)


def daily_due(now=None):
    """True when the stamp file is missing or older than DAILY_H hours."""
    try:
        return (now or time.time()) - STAMP.stat().st_mtime > DAILY_H * 3600
    except OSError:
        return True


def touch_stamp():
    try:
        STAMP.parent.mkdir(parents=True, exist_ok=True)
        STAMP.write_text(time.strftime("%Y-%m-%dT%H:%M:%S") + "\n", encoding="utf-8")
    except OSError:
        pass


def low_due(now=None):
    """Low-disk path: True when no run started in the last LOW_GAP_S (every session start was spawning one)."""
    try:
        return (now or time.time()) - STAMP.stat().st_mtime > LOW_GAP_S
    except OSError:
        return True


def take_lock():
    """One --apply run per host: O_EXCL lock file holding our pid; a lock whose pid is gone is replaced. False = another run holds it."""
    for _ in range(2):
        try:
            fd = os.open(str(LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        except FileExistsError:
            try:
                pid = int(LOCK.read_text(encoding="utf-8").strip() or "0")
            except (OSError, ValueError):
                pid = 0
            if pid and pid_alive(pid):
                return False
            try:
                LOCK.unlink()
            except OSError:
                return False
        except OSError:
            return True        # no lock dir: run unlocked rather than never
    return False


def pid_alive(pid):
    if os.name == "nt":
        r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, creationflags=NO_WINDOW)
        return str(pid) in (r.stdout or "")
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def release_lock():
    try:
        if LOCK.read_text(encoding="utf-8").strip() == str(os.getpid()):
            LOCK.unlink()
    except OSError:
        pass


def start_apply_detached():
    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | NO_WINDOW
    try:
        subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--apply"], creationflags=flags,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
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
        low = low_drives(limit)
        gb = min([g for _, g in low] or [free_gb()])
        if not low:
            if daily_due():
                touch_stamp()
                start_apply_detached()
            return 0
        due = low_due()
        msg = "LOW: " + ", ".join(f"{d} {g:.1f} GB free" for d, g in low) + f" (< {limit:g}); " + (
            "c_drive_guard --apply started in the background." if due else "c_drive_guard ran in the last hour.")
        for p, mb in runaways():
            msg += f" RUNAWAY task output {mb:.0f} MB: {p}"
        print(msg)
        if due:
            touch_stamp()
            start_apply_detached()
        return 0
    if argv[:1] == ["plan"]:
        rows = plan()
        for kind, name, size, why in rows:
            print("would delete  %-8s %s (%.2f GB): %s" % (kind, name, size / 1e9, why))
        print("would delete %d item(s); nothing deleted (--apply deletes)" % len(rows))
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
    if apply:
        if not take_lock():
            print("another c_drive_guard --apply is running on this host; skipped")
            return 0
        try:
            n, freed, trees = apply_all("apply")
        finally:
            release_lock()
        print(f"pruned {n} temp entries, {freed / 1e9:.2f} GB; retired {trees} worktrees")
        print(f"C: free now {free_gb():.2f} GB")
        return 0
    n, freed = prune(False)
    print(f"would prune {n} temp entries, {freed / 1e9:.2f} GB (dry run; `plan` lists each with its reason, --apply prunes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
