"""C: drive guard: report free space and prune regenerable %TEMP% garbage left by gates, tests and Claude sessions.

Usage:
  python scripts/dev/c_drive_guard.py            report only (free GB, runaway task outputs, prunable temp)
  python scripts/dev/c_drive_guard.py --apply    prune now
  python scripts/dev/c_drive_guard.py hook       SessionStart hook: starts a detached --apply run once per day per host (stamp file)
                                                 and whenever C: has < MTS_C_MIN_FREE_GB (default 15) free; silent otherwise,
                                                 or one warning line when low
  python scripts/dev/c_drive_guard.py plan       dry run: every item it would delete, one line each with the reason
  python scripts/dev/c_drive_guard.py logon      logon run: prunes at every logon, whatever the free space; one line to the log
  python scripts/dev/c_drive_guard.py procs      stray shells/runtimes (python, pythonw, node, pwsh, powershell, cmd, bash, conhost) older
                                                 than 24 h: report only (the daily run logs the counts too)
  python scripts/dev/c_drive_guard.py procs --apply   kill the KILL rows by PID, re-checked in a fresh snapshot (never by image name)
  python scripts/dev/c_drive_guard.py install [--repo PATH ...]   register `logon` under HKCU Run (no admin, no scheduled task); run from the
                                                 primary checkout; --repo: also retire the worktrees of that other clone (JIS-NB: IdeaProjects)
  python scripts/dev/c_drive_guard.py status [--check]   registered or not, for which checkout, last logon line; --check: exit 1 if not registered
  (the daily hook also runs `device_tasks.py check --send`, report-only: DEVICE_TASKS.md)
  python scripts/dev/c_drive_guard.py uninstall  remove the logon run

What it prunes (only entries whose newest file is older than the age limit; locked entries are skipped):
  %TEMP%/<prefix>*            test and gate scratch dirs (PREFIXES): 24 h
  %TEMP%/mts_s4_* mts_s5c_* mts_changed_*   this repo's own gate basetemps (OWN_PREFIXES): 6 h
  worktrees                   `wt_maint.py --apply --no-log`, the same job on every device: finished trees (hand-named too) idle 1 h; trees with
                              uncommitted files only when their branch is on trunk and they are idle 24 h, patch saved to Dumps/wt_rescue first;
                              never unshipped commits, lane, codex, gemini, gpt or live trees; merged local branches deleted
  %TEMP%/claude/<proj>/<sid>  Claude session scratch + background-task output: 3 days
  caches outside %TEMP% (buckets; dry run prints GB per bucket): Dumps/wt_rescue regenerable caches (wt_maint.RESCUE_SKIP);
                              Chrome/Edge Cache, Code Cache, GPUCache only while that browser is not running (never Service Worker
                              storage, cookies or profiles); older playwright browser revisions; Claude session logs
                              (~/.claude/projects/*/<uuid>) older than 14 days (never memory/); sibling mts-* and .claude/worktrees
                              folders with no .git that are no worktree, idle 7 days. The Claude app VM image is only reported.
What it never prunes: KEEP_NAMES (state other code reads: role injection records, host health, gate slots, relay).
What it only reports: a Claude background-task .output file over 500 MB (a runaway, e.g. a bare `python -` REPL looping on
WinError 6 wrote 3.5 GB at ~0.5 MB/s on 2026-10-18). Stopping the process is the operator's call; the line names the file.
Never touches tracked repo files, .secrets, .env, browser profiles, F:, the live tree or anything not named above.
Who writes each prefix, and where the logs are: MyTradingSys/system/STATION_CLEANUP.md.
"""
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import hosts                 # per-host worktree root (F:\MTS\wt on the desktop)
import host_health as hh     # process snapshot, ancestor chain, own pids (stdlib only; scripts/dev sits on sys.path)

TEMP =Path(os.environ.get("MTS_GUARD_TEMP") or os.path.expandvars(r"%LOCALAPPDATA%\Temp"))
LOG = Path(os.environ.get("MTS_GUARD_LOG") or os.path.expandvars(r"%LOCALAPPDATA%\MTS\logs\c_drive_guard.log"))
PREFIXES = ("tmp", "mts_", "r2_", "rmd_", "kill_switch_cli_", "staged_tests_", "gate_timing_test_", "aibridge_selftest_",
            "pytest-of-", "gate_budget_test_", "dsa_tpl_", "e2e_a2_", "dsa-boot-", "cicd_ps_", "lab_query_", "soak6_")
KEEP_NAMES = ("mts_roles", "mts_host_health", "mts_gate_slots", "mts_relay")
TEMP_AGE_H = 24
OWN_PREFIXES = hh.OWN_TEMP_PREFIXES   # this repo's gate/test basetemps: nobody else writes these names
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


# ---- regenerable caches outside %TEMP% (buckets): dry run lists GB per bucket, --apply / logon prune them ----
# Measured on JIS-NB 2026-11-01 (C: 9.3 GB free of 121): Dumps/wt_rescue 6.55 GB, of which 6.37 GB was sim_desk/cache/bars that
# wt_maint copied out of every retired tree (rebuilt by `desk.py --build` in about a minute); real rescued work was 3 MB.
HOME = Path(os.environ.get("MTS_GUARD_HOME") or os.path.expanduser("~"))
LOCALAPPDATA = Path(os.environ.get("MTS_GUARD_LOCALAPPDATA") or os.path.expandvars(r"%LOCALAPPDATA%"))
MAIN = None                     # primary checkout; None = main_checkout() (tests set a folder)
BROWSERS = (("Google/Chrome/User Data", "chrome.exe"), ("Microsoft/Edge/User Data", "msedge.exe"))
BROWSER_CACHES = ("Cache", "Code Cache", "GPUCache")    # per profile; never Service Worker storage, cookies or the profile itself
BROWSER_SHARED = ("GrShaderCache", "ShaderCache", "GraphiteDawnCache")
CLAUDE_LOG_DAYS = 14            # DECISION (OURS): token_audit reads the last 7 days; twice that, then session logs go
ORPHAN_DAYS = 7                 # DECISION (OURS): a sibling mts-* folder with no .git, not a worktree, untouched this long
PLAYWRIGHT_DAYS = 1
LIVE_MARKER = ".mts_live"       # sync.LIVE_MARKER: the live tree is never pruned
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(\.jsonl)?$")


def main_root():
    return Path(MAIN) if MAIN else main_checkout()


def worktree_paths(main):
    """Resolved paths of every git worktree of `main`, or None when git cannot say (callers then prune nothing)."""
    try:
        r = subprocess.run(["git", "-C", str(main), "worktree", "list", "--porcelain"], capture_output=True, text=True,
                           timeout=60, creationflags=NO_WINDOW)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return {os.path.normcase(str(Path(l[9:]).resolve())) for l in r.stdout.splitlines() if l.startswith("worktree ")}


def running(image):
    try:
        return any(p["name"].lower() == image for p in hh.snapshot())
    except Exception:           # unknown = running: never prune a cache a browser may hold open
        return True


def stale_rows(bucket, paths, cutoff, why):
    out = []
    for p in paths:
        try:
            stale, size = stale_size(str(p), cutoff)
        except OSError:
            continue
        if stale:
            out.append((bucket, str(p), size, why))
    return out


def rescue_cache_rows(main, now=None):
    """Regenerable caches wt_maint copied into Dumps/wt_rescue (wt_maint.RESCUE_SKIP); the rest of a rescue is kept."""
    from wt_maint import RESCUE_SKIP
    ends = tuple("/" + s.lower() for s in RESCUE_SKIP)    # any depth: older rescues sit under <tree>/files/
    paths, todo = [], [str(Path(main) / "Dumps" / "wt_rescue")]
    while todo:
        for e in scan(todo.pop()):
            if not e.is_dir(follow_symlinks=False) or not dir_not_reparse(e.path):
                continue
            if e.path.replace("\\", "/").lower().endswith(ends):
                paths.append(e.path)
            else:
                todo.append(e.path)
    return stale_rows("rescue-cache", paths, now or time.time(), "regenerable cache copied by wt_maint")


def browser_rows(local, run=None, now=None):
    run = run or running
    out = []
    for rel, image in BROWSERS:
        root = Path(local) / rel
        if not dir_not_reparse(root):
            continue
        if run(image):
            continue            # its cache files are open: next logon run, before the browser starts
        dirs = [root / s for s in BROWSER_SHARED]
        for prof in scan(root):
            if prof.is_dir(follow_symlinks=False):
                dirs += [Path(prof.path) / c for c in BROWSER_CACHES]
        out += stale_rows("browser-cache", [d for d in dirs if dir_not_reparse(d)], now or time.time(), image + " not running")
    return out


def playwright_rows(local, now=None):
    """Older revisions of a playwright browser when a newer one of the same kind sits beside it."""
    root = Path(local) / "ms-playwright"
    newest = {}
    for e in scan(root):
        kind, _, rev = e.name.rpartition("-")
        if kind and rev.isdigit() and e.is_dir(follow_symlinks=False):
            newest.setdefault(kind, []).append((int(rev), e.path))
    old = [p for revs in newest.values() for _, p in sorted(revs)[:-1]]
    return stale_rows("playwright-old", old, (now or time.time()) - PLAYWRIGHT_DAYS * 86400, "a newer revision is installed")


def claude_log_rows(home, now=None):
    """Claude session logs (<uuid>.jsonl and <uuid>/) untouched CLAUDE_LOG_DAYS; never memory/ or any other name."""
    paths = []
    for proj in scan(Path(home) / ".claude" / "projects"):
        if proj.is_dir(follow_symlinks=False):
            paths += [e.path for e in scan(proj.path) if UUID_RE.match(e.name)]
    return stale_rows("claude-logs", paths, (now or time.time()) - CLAUDE_LOG_DAYS * 86400,
                      "session log older than %d days" % CLAUDE_LOG_DAYS)


def orphan_rows(main, trees=None, now=None):
    """Sibling mts-* folders and .claude/worktrees/* that are no git worktree and hold no .git: what a failed removal leaves."""
    trees = worktree_paths(main) if trees is None else trees
    if trees is None:
        return []
    cands = [Path(e.path) for r in hosts.worktree_roots(Path(main).parent) for e in scan(Path(r)) if e.name.startswith("mts-")]
    cands += [Path(e.path) for e in scan(Path(main) / ".claude" / "worktrees")]
    cands = [p for p in cands if dir_not_reparse(p) and os.path.normcase(str(p.resolve())) not in trees
             and not (p / ".git").exists() and not (p / LIVE_MARKER).exists()]
    return stale_rows("orphan-tree", cands, (now or time.time()) - ORPHAN_DAYS * 86400,
                      "no .git, not a worktree, idle %d days" % ORPHAN_DAYS)


def bucket_rows():
    """(bucket, path, bytes, reason) for every cache prunable outside %TEMP%. Never raises: a failing bucket adds nothing."""
    main = main_root()
    jobs = [lambda: browser_rows(LOCALAPPDATA), lambda: playwright_rows(LOCALAPPDATA), lambda: claude_log_rows(HOME)]
    if main:
        jobs += [lambda: rescue_cache_rows(main), lambda: orphan_rows(main)]
    out = []
    for job in jobs:
        try:
            out += job()
        except Exception:
            pass
    return out


def report_only():
    """(label, GB) of big items the guard never deletes, so the report names them."""
    out = []
    for vm in (LOCALAPPDATA / "Claude-Data").glob("*/vm_bundles"):
        out.append(("Claude app VM image (app-managed, never deleted)", dir_bytes(vm) / 1e9))
    return out


def dir_bytes(p):
    total, todo = 0, [str(p)]
    while todo:
        for e in scan(todo.pop()):
            try:
                if e.is_dir(follow_symlinks=False):
                    todo.append(e.path)
                else:
                    total += e.stat(follow_symlinks=False).st_size
            except OSError:
                pass
    return total


def prune_buckets(apply, rows=None):
    """-> {bucket: [n, bytes]} of what was (or would be) freed."""
    out = {}
    for bucket, path, size, _ in (bucket_rows() if rows is None else rows):
        if not apply or remove(path):
            n = out.setdefault(bucket, [0, 0])
            n[0] += 1
            n[1] += size
    return out


def bucket_text(done):
    return ", ".join("%s %d (%.2f GB)" % (b, n, s / 1e9) for b, (n, s) in sorted(done.items())) or "none"


NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)   # every child: no console window on the operator's screen, ever
LOCK =LOG.parent / "c_drive_guard.lock"                 # one copy per host and user (LOG lives under LOCALAPPDATA)
LOCK_STALE_H = 2


def pid_alive(pid):
    """True when process `pid` exists. Windows: OpenProcess (os.kill(pid, 0) would send CTRL_C_EVENT there)."""
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not h:
            return False
        code = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(h)
        return bool(ok) and code.value == 259
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def take_lock():
    """Create the lock with O_EXCL and our pid. A lock whose pid is dead (or older than LOCK_STALE_H) is stale: replaced once.
    Returns True when we hold it, False when another live copy does."""
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        try:
            fd = os.open(str(LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        except FileExistsError:
            try:
                pid = int(LOCK.read_text(encoding="utf-8").strip() or 0)
                age_h = (time.time() - LOCK.stat().st_mtime) / 3600
            except (OSError, ValueError):
                pid, age_h = 0, 99
            if pid_alive(pid) and age_h < LOCK_STALE_H:
                return False
            try:
                LOCK.unlink()
            except OSError:
                return False
    return False


def drop_lock():
    try:
        if LOCK.read_text(encoding="utf-8").strip() == str(os.getpid()):
            LOCK.unlink()
    except OSError:
        pass


def maint_script():
    return Path(__file__).resolve().parent / "wt_maint.py"


def run_tidy(apply, repos=()):
    """`wt_maint.py [--apply --no-log]` for the checkout this script lives in (--no-log: the guard must not dirty the primary
    tree with a SUPERVISOR_LOG line). `repos`: other clones whose trees the job also covers (`--repo`; the logon Run value may point
    at a checkout that is not the one holding the worktrees). Returns its output lines ([] on any failure: never raises)."""
    out = []
    for repo in [None, *repos]:
        try:
            r = subprocess.run([sys.executable, str(maint_script())] + (["--apply", "--no-log"] if apply else [])
                               + (["--repo", str(repo)] if repo else []),
                               capture_output=True, text=True, timeout=600, cwd=str(Path(__file__).resolve().parents[2]),
                               creationflags=NO_WINDOW)
            out += (r.stdout or "").splitlines()
        except (OSError, subprocess.SubprocessError):
            pass
    return out


def repo_args(argv):
    """Values of every `--repo PATH` in argv."""
    return [argv[i + 1] for i, a in enumerate(argv[:-1]) if a == "--repo"]


def _git_out(tree, *args):
    try:
        r = subprocess.run(["git", "-C", str(tree), *args], capture_output=True, text=True, timeout=60, creationflags=NO_WINDOW)
        return r.stdout if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def unshipped_study_rows(main, min_hours=6.0, now=None, trunk="origin/fast-track"):
    """[(path, idle_hours, state, result)] for study trees (mts-*, any root) idle >= min_hours with work not on trunk:
    state = 'dirty' (uncommitted) and/or 'ahead N' (commits git cherry says trunk lacks); result = 'RESULT.md' when the tree holds
    one, else 'no RESULT'. Read-only: the supervisor ships/tidies these (WORKERS.md rule 12); the guard never deletes them."""
    now = time.time() if now is None else now
    trees = worktree_paths(main)
    if not trees:
        return []
    out = []
    for p in sorted(trees):
        pp = Path(p)
        if not pp.name.startswith("mts-") or not pp.is_dir() or (pp / LIVE_MARKER).exists():
            continue
        if os.path.normcase(str(pp)) == os.path.normcase(str(Path(main).resolve())):
            continue
        status = _git_out(pp, "status", "--porcelain", "-uall")
        if status is None:
            continue
        last = _git_out(pp, "log", "-1", "--format=%ct")
        newest = float(last.strip()) if last and last.strip().isdigit() else 0.0
        for line in status.splitlines():
            f = pp / line[3:].strip().strip('"').split(" -> ")[-1]
            try:
                newest = max(newest, f.stat().st_mtime)
            except OSError:
                pass
        idle = (now - newest) / 3600 if newest else 1e9
        if idle < min_hours:
            continue
        cherry = _git_out(pp, "cherry", trunk) or ""
        ahead = sum(1 for l in cherry.splitlines() if l.startswith("+"))
        state = ", ".join(x for x in (("dirty" if status.strip() else ""), (f"ahead {ahead}" if ahead else "")) if x)
        if not state:
            continue
        changed = status + (_git_out(pp, "diff", "--name-only", trunk + "...HEAD") or "")    # RESULT counts only if this tree made it
        has = any(l.replace("\\", "/").split("/")[-1].strip().upper().startswith("RESULT") for l in changed.splitlines())
        out.append((str(pp), idle, state, "RESULT.md" if has else "no RESULT"))
    return out


def plan():
    """Dry-run listing: (kind, path-or-name, bytes, reason) for everything --apply would delete. Deletes nothing."""
    rows = [("temp", p, size, reason(p)) for p, size in candidates()] + bucket_rows()
    for line in run_tidy(False):
        if line.startswith("would remove  "):
            name, _, why = line[len("would remove  "):].partition(": ")
            rows.append(("worktree", name, 0, why or "finished tree"))
    return rows


def unshipped_lines(main=None):
    """Plan text for the supervisor: one line per unshipped study tree older than 6 h (empty when none / git cannot say)."""
    main = main or main_checkout()
    if not main:
        return []
    return ["UNSHIPPED %s idle %.0f h: %s, %s -> supervisor: ship then sync.py tidy" % (p, h, st, rs)
            for p, h, st, rs in unshipped_study_rows(main)]


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
                           capture_output=True, text=True, timeout=30, creationflags=NO_WINDOW)
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
        return subprocess.run(["git", "-C", str(main), *a], capture_output=True, text=True, timeout=t, creationflags=NO_WINDOW)
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


# ---- stray shells and runtimes (procs): reported by the daily run, killed only by `procs --apply`, only by PID ----
PROC_NAMES = ("python.exe", "pythonw.exe", "node.exe", "pwsh.exe", "powershell.exe", "cmd.exe", "bash.exe", "conhost.exe")
PROC_AGE_H = 24
PROC_SAFE = ("desk.py", "sim_desk", "layers.fabio", "scripts/dev/", "mytradingsys/")   # the allow list (STRAY_REAP_POLICY.md)
PROC_NEVER = (".mts_live", "live_runner", "loop-supervisor", "start-trading-day", "oi_recorder", "orderflow_live",
              "htf_context_live", "deploy", "auto_deploy", "wait_then_ship", "cicd_run")


def proc_verdict(p, by, now):
    """(verdict, reason) for one process, or None when it is no candidate (not a shell or runtime name, unknown or under
    PROC_AGE_H old). KILL: old, a safe pattern, no never-kill text in it or its ancestors, no claude.exe ancestor.
    PROTECTED: a never-kill rule hit. UNMATCHED: old, but no safe pattern: reported, never killed. Fails closed."""
    name = p["name"].lower()
    if "java" in name:
        return ("PROTECTED", "java: never")
    if name not in PROC_NAMES or not p["created"] or now - p["created"] < PROC_AGE_H * 3600:
        return None
    up = hh.chain(by, p["pid"])
    cmd = p["cmd"].lower()
    text = " ".join([cmd] + [a["cmd"].lower() for a in up])
    if any(m in text for m in PROC_NEVER) or ("sync.py" in text and "ship" in text):
        return ("PROTECTED", "never-kill text in its command line or an ancestor's")
    if any(a["name"].lower() == "claude.exe" for a in up):
        return ("PROTECTED", "claude.exe ancestor")
    if not any(m in cmd for m in PROC_SAFE):
        return ("UNMATCHED", "no safe pattern: reported, not killed")
    return ("KILL", "safe pattern, old, no protected rule")


def proc_rows(procs, now=None):
    """One dict per candidate in a snapshot (never this process or its ancestors), KILL rows first."""
    now = now or time.time()
    by = hh.index(procs)
    keep = hh.own_pids(by)
    out = []
    for p in procs:
        v = None if p["pid"] in keep else proc_verdict(p, by, now)
        if v:
            out.append({"pid": p["pid"], "name": p["name"], "created": p["created"], "cmd": p["cmd"],
                        "age_h": (now - p["created"]) / 3600, "verdict": v[0], "reason": v[1]})
    return sorted(out, key=lambda r: (r["verdict"] != "KILL", -r["age_h"]))


def proc_line(r):
    return "%-9s PID %-6d %-14s %6.0f h  %s  | %s" % (r["verdict"], r["pid"], r["name"], r["age_h"], r["reason"], r["cmd"][:110])


def procs_summary(procs=None, now=None):
    """One log phrase for the daily run: counts and PIDs only, never kills. Never raises."""
    try:
        rows = proc_rows(hh.snapshot() if procs is None else procs, now)
        kills = [r["pid"] for r in rows if r["verdict"] == "KILL"]
        return "%d KILL candidate(s) %s (report only; `c_drive_guard.py procs --apply` kills by PID), %d PROTECTED, %d UNMATCHED old" % (
            len(kills), kills, sum(r["verdict"] == "PROTECTED" for r in rows), sum(r["verdict"] == "UNMATCHED" for r in rows))
    except Exception as e:      # the log says why; the daily run must still finish
        return "unavailable (%s)" % type(e).__name__


def kill_pid(pid):
    """Stop one process by PID (taskkill /PID, no tree, no image name). True when taskkill reports success."""
    try:
        r = subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True, text=True, timeout=30, creationflags=NO_WINDOW)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def procs_apply(snapshot=hh.snapshot, now=None, kill=kill_pid):
    """Kill every KILL row by PID. Each one is re-checked in a fresh snapshot: same PID, same start time, still KILL. Returns (killed, skipped)
    as lists of PIDs and text lines."""
    cands = [r for r in proc_rows(snapshot(), now) if r["verdict"] == "KILL"]
    fresh_all = snapshot()
    by = hh.index(fresh_all)
    killed, skipped = [], []
    for r in cands:
        cur = by.get(r["pid"])
        if cur is None or cur["created"] != r["created"]:
            skipped.append("PID %d: gone or reused since the report, not killed" % r["pid"])
            continue
        again = proc_verdict(cur, by, now or time.time())
        if not again or again[0] != "KILL":
            skipped.append("PID %d: no longer a KILL candidate, not killed" % r["pid"])
            continue
        if kill(r["pid"]):
            killed.append(r["pid"])
        else:
            skipped.append("PID %d: taskkill failed" % r["pid"])
    return killed, skipped


def apply_all(tag):
    """Prune temp, retire finished worktrees, log ONE line with the GB freed. Never raises."""
    before = free_gb()
    n, freed = prune(apply=True)
    gone = [l for l in run_tidy(True) if l.startswith("removed  ")]
    done = prune_buckets(True)      # after tidy: a tree retired now has its rescue cache pruned in the same run
    after = free_gb()
    log("%s: C free %.1f GB -> %.1f GB (freed %.2f GB); %d temp entries (%.2f GB); %d worktrees retired; caches: %s; %s; procs (report only): %s"
        % (tag, before, after, max(after - before, 0) if after != float("inf") else 0, n, freed / 1e9, len(gone),
           bucket_text(done), main_checkout_note(), procs_summary()))
    return n, freed + sum(s for _, s in done.values()), len(gone)


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


def start_apply_detached():
    """Detached --apply run. CREATE_NO_WINDOW only: with DETACHED_PROCESS the child has no console and every console program
    it starts (git, python) opens its own visible window (operator 2026-10-25). Output goes to a log, never a console."""
    flags = NO_WINDOW | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG.parent / "c_drive_guard.out", "ab") as out:
            subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--apply"], creationflags=flags,
                             stdin=subprocess.DEVNULL, stdout=out, stderr=out, close_fds=True)
    except OSError:
        pass


def start_check_detached():
    """Report-only `device_tasks.py check --send` (DEVICE_TASKS.md): this host's result goes out as one mts_signal line. Never raises."""
    script = Path(__file__).resolve().parent / "device_tasks.py"
    if os.environ.get("MTS_NO_DEVICE_TASKS") or not script.is_file():
        return
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG.parent / "c_drive_guard.out", "ab") as out:
            subprocess.Popen([sys.executable, str(script), "check", "--send"], creationflags=NO_WINDOW,
                             stdin=subprocess.DEVNULL, stdout=out, stderr=out, close_fds=True)
    except OSError:
        pass


LOGON_GRACE_S = 180      # seconds the logon run idles before pruning (OURS; headless, costs nothing while waiting)


def logon(repos=()):
    """Logon run: prune now whatever the free space and log one line. A failure is logged, and the run still returns 0."""
    try:
        before = free_gb()
        n, freed = prune(apply=True)
        gone = [l for l in (run_tidy(True, repos) if repos else run_tidy(True)) if l.startswith("removed  ")]
        done = prune_buckets(True)
        log("logon: C free %.1f GB -> %.1f GB; pruned %d temp entries, %.2f GB; %d worktrees retired; caches: %s; runaway outputs %d"
            % (before, free_gb(), n, freed / 1e9, len(gone), bucket_text(done), len(runaways())))
    except Exception as e:     # the log says why; a restart must not show an error box
        log("logon: error %r" % (e,))
    return 0


def logon_command(python=None, script=None, repos=()):
    """The HKCU Run command line. conhost --headless: no console window at logon (same launch as the Antigravity daemon)."""
    conhost = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "conhost.exe")
    return '"%s" --headless "%s" "%s" logon' % (conhost, python or sys.executable,
                                             script or str(Path(__file__).resolve())) + "".join(' --repo "%s"' % r for r in repos)


def installed_command(key=RUN_KEY, name=RUN_NAME):
    """The registered Run command line, or None when there is none (or not Windows)."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
            return winreg.QueryValueEx(k, name)[0]
    except (ImportError, OSError):
        return None


def install(checkout=None, key=RUN_KEY, name=RUN_NAME, repos=()):
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
    cmd = logon_command(script=str(script), repos=repos)
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


def status(key=RUN_KEY, name=RUN_NAME, check=False):
    """check=True (device_tasks.py verify): exit 1 when the logon run is not registered at all."""
    cur = installed_command(key, name)
    if cur is None:
        print("logon run: not installed (python scripts/dev/c_drive_guard.py install, from the primary checkout)")
    else:
        print("logon run: installed" + (" for this checkout" if cur.startswith(logon_command()) else "; NOT this checkout: " + cur))
        print("command: " + cur)
    try:
        last = LOG.read_text(encoding="utf-8").splitlines()[-1]
    except (OSError, IndexError):
        last = "none yet (log %s)" % LOG
    print("last logon line: " + last)
    return 1 if check and cur is None else 0


def main(argv):
    if argv[:1] == ["hook"]:
        limit = float(os.environ.get("MTS_C_MIN_FREE_GB", "15"))
        low = low_drives(limit)
        gb = min([g for _, g in low] or [free_gb()])
        if not low:
            if daily_due():
                touch_stamp()
                start_apply_detached()
                start_check_detached()
            return 0
        touch_stamp()
        msg = "LOW: " + ", ".join(f"{d} {g:.1f} GB free" for d, g in low) + f" (< {limit:g}); c_drive_guard --apply started in the background."
        for p, mb in runaways():
            msg += f" RUNAWAY task output {mb:.0f} MB: {p}"
        unshipped = unshipped_lines()
        if unshipped:
            msg += " %d unshipped study tree(s) >6 h (supervisor ships+tidies): " % len(unshipped) + " | ".join(u.split(" -> ")[0] for u in unshipped[:5])
        print(msg)
        start_apply_detached()
        return 0
    if argv[:1] == ["plan"]:
        rows = plan()
        for kind, name, size, why in rows:
            print("would delete  %-8s %s (%.2f GB): %s" % (kind, name, size / 1e9, why))
        print("would delete %d item(s); nothing deleted (--apply deletes)" % len(rows))
        if low_drives(float(os.environ.get("MTS_C_MIN_FREE_GB", "15"))) or "--unshipped" in argv:
            for line in unshipped_lines():
                print(line)
        return 0
    if argv[:1] == ["procs"]:
        if "--apply" in argv:
            killed, skipped = procs_apply()
            for line in skipped:
                print(line)
            print("killed %d by PID: %s" % (len(killed), killed))
            log("procs --apply: killed %s; skipped %d" % (killed, len(skipped)))
            return 0
        rows = proc_rows(hh.snapshot())
        for r in rows:
            print(proc_line(r))
        print("%d candidate(s): %d KILL, %d PROTECTED, %d UNMATCHED; nothing killed (`procs --apply` kills the KILL rows)"
              % (len(rows), sum(r["verdict"] == "KILL" for r in rows), sum(r["verdict"] == "PROTECTED" for r in rows),
                 sum(r["verdict"] == "UNMATCHED" for r in rows)))
        return 0
    if argv[:1] == ["logon"]:
        time.sleep(LOGON_GRACE_S)     # boot audit 2026-11-06: the cleanup (git, caches) must not compete with the logon
        return logon(repo_args(argv))
    if argv[:1] == ["install"]:
        return install(repos=repo_args(argv))
    if argv[:1] == ["uninstall"]:
        return uninstall()
    if argv[:1] == ["status"]:
        return status(check="--check" in argv)
    apply = "--apply" in argv
    before = free_gb()
    print(f"C: free {before:.2f} GB")
    for p, mb in runaways():
        print(f"RUNAWAY task output {mb:.0f} MB (stop its process, then delete): {p}")
    if apply:
        if not take_lock():
            print("another c_drive_guard run holds %s; exiting" % LOCK)
            return 0
        try:
            n, freed, trees = apply_all("apply")
        finally:
            drop_lock()
        print(f"pruned {n} temp entries + caches, {freed / 1e9:.2f} GB; retired {trees} worktrees")
        print(f"C: free now {free_gb():.2f} GB")
        return 0
    n, freed = prune(False)
    print("%-15s %5s %8s" % ("bucket", "items", "GB"))
    print("%-15s %5d %8.2f" % ("temp", n, freed / 1e9))
    for bucket, (k, size) in sorted(prune_buckets(False).items()):
        print("%-15s %5d %8.2f" % (bucket, k, size / 1e9))
    for label, gb in report_only():
        print("report only: %s %.2f GB" % (label, gb))
    print("dry run: nothing deleted (`plan` lists each item with its reason, --apply prunes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
