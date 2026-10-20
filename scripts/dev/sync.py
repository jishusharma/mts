"""One way for any session on any machine to share work: origin/fast-track is the only meeting point.

  python scripts/dev/sync.py start [slug] [--quiet]  # up to date with origin/fast-track; in a shared/dirty tree makes your own worktree;
                                           # in a lane tree (mts-app, mts-relay, mts-dsa) `start <slug>` switches to branch <host>/<slug>
  python scripts/dev/sync.py health  # stale/overlapping claims, shared or orphan worktrees, branches never shipped
  python scripts/dev/sync.py ship [--full] [--fix-ci] [--release <slug>] [--after <slug>]  # merge origin/fast-track, SMOKE gate (steps for the changed paths; live path = all; --full = all), push; CI runs the full suite behind
                                           # ordinary code ships run the FAST gate (GATE_SPEED.md: ~60 s, tests chosen by import graph); a red CI blocks code ships until
                                           # fixed: --fix-ci ships the fix through it with the full gate; --after waits for predecessor order ticket
  python scripts/dev/sync.py news [hours=24]  # what shipped: feature + Result line per commit, no code
  python scripts/dev/sync.py claim "<task>" [--area <paths>]  # tell parallel sessions what you work on (shipped at once); refused only when --area overlaps an open claim
  python scripts/dev/sync.py claims  # open claims on origin/fast-track (host, account, task, age); release: `release <slug>`
  python scripts/dev/sync.py where [--all]  # trees holding work not on origin/fast-track (nothing lost?); --all lists every tree
  python scripts/dev/sync.py tidy [--apply] [--all]  # retire finished worktrees (session, App-named, mts-relay-*; clean + fully on origin/fast-track + idle 24 h); dry run by default

Rules live in MyTradingSys/system/PARALLEL.md. The live tree (a checkout holding the gitignored marker
file .mts_live) is never synced or shipped from: the running system imports it, so it changes only by
the supervisor deploy (stop, ff-merge, gate, restart).
"""
import json
import os
import random
import re
import socket
import inspect
import subprocess
import tempfile
import threading
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TRUNK = "fast-track"
LIVE_MARKER = ".mts_live"
DOC_SUFFIXES = (".md", ".txt")
PUSH_TRIES = 3
CLAIMS_DIR = "MyTradingSys/system/claims"
CARDS_DIR = "MyTradingSys/system/tasks"
STALE_HOURS = 24
# Generated or whole-file-rewritten files that every session touches. A collision here is never worth a
# stalled session: origin's text wins, the loser regenerates (STATUS.md) or re-applies its one-line edit.
TAKE_ORIGIN = ("MyTradingSys/system/NEXT_SESSION.md", "MyTradingSys/research/STATUS.md",
               "MyTradingSys/runtime/BUILD_REPORT.md")
NOT_SHIPPED_HOURS = 24
ROW_CAP = 15  # rows `where` / `health` print before pointing at `where --all`
# Rows of `git status --short` that are nobody's work: the desktop mirror a pull writes (regenerable data, git-ignored on
# current trees, tracked on old bases) and the stray AGENTS.md / .codex of older trees.
MIRROR_PREFIXES = ("runtime_data/_mirror/", "runtime_data/_mirror.")
STRAY_UNTRACKED = ("AGENTS.md", ".codex/", "runtime_data/gate_timing.jsonl", "runtime_data/")


class SyncError(Exception):
    pass


def git(repo, *args, check=True):
    # `status` refreshes and rewrites the index under index.lock; where/health/tidy run it in other sessions' trees,
    # where that can break their `git add` and reset the idle clock tidy reads, so status never takes optional locks.
    opts = ["--no-optional-locks"] if args and args[0] == "status" else []
    r = subprocess.run(["git", "-C", str(repo), *opts, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SyncError(f"git {' '.join(args)} failed:\n{r.stdout}{r.stderr}".rstrip())
    return r


def is_noise(row, strays=True):
    """True for a `status --short` row that is not anyone's work (see MIRROR_PREFIXES, STRAY_UNTRACKED)."""
    path = row[3:].strip('"')
    return path.startswith(MIRROR_PREFIXES) or (strays and row.startswith("??") and path in STRAY_UNTRACKED)


def toplevel(path):
    return Path(git(path, "rev-parse", "--show-toplevel").stdout.strip())


def refuse_live(repo):
    if (repo / LIVE_MARKER).exists():
        raise SyncError(
            f"{repo} is the live tree ({LIVE_MARKER} present). Sessions do not work here.\n"
            f"Make a worktree:  git worktree add ../mts-<slug> -b {socket.gethostname().lower()}/<slug> origin/{TRUNK}")


FETCH_TRIES = 3


def fetch_trunk(repo, tries=FETCH_TRIES, sleep=time.sleep):
    """`git fetch origin fast-track`, retried: every worktree of this repo shares refs/remotes/origin/fast-track, so two trees fetching
    at once fail with "incorrect old value provided" / "cannot lock ref" (2026-10-18: a ship that had passed its whole gate died here)."""
    for i in range(1, tries + 1):
        r = git(repo, "fetch", "--quiet", "origin", TRUNK, check=False)
        if r.returncode == 0:
            return
        if i < tries:
            sleep(1.0 + 2 * i * random.random())
    raise SyncError(f"git fetch --quiet origin {TRUNK} failed {tries}x:\n{r.stdout}{r.stderr}".rstrip())


def merge_trunk(repo):
    """Fetch and merge origin/fast-track into HEAD (never rebase). Returns the commits pulled in.
    A conflict confined to TAKE_ORIGIN files is resolved to origin's text and reported; any other stops."""
    fetch_trunk(repo)
    incoming = git(repo, "rev-list", "--count", f"HEAD..origin/{TRUNK}").stdout.strip()
    if incoming != "0":
        r = git(repo, "merge", "--no-edit", f"origin/{TRUNK}", check=False)
        if r.returncode != 0 and not git(repo, "diff", "--name-only", "--diff-filter=U").stdout.split() \
                and "runtime_data/_mirror" in r.stdout + r.stderr:
            # Trunk untracked the pulled mirror while this tree holds a pulled (edited) copy of it: regenerable data,
            # nobody's work. Drop the copy so the merge can delete the tracked files; the next pull rewrites it.
            git(repo, "checkout", "--", "runtime_data/_mirror", check=False)
            git(repo, "clean", "-fdq", "--", "runtime_data/_mirror", check=False)
            r = git(repo, "merge", "--no-edit", f"origin/{TRUNK}", check=False)
        if r.returncode != 0:
            bad = git(repo, "diff", "--name-only", "--diff-filter=U").stdout.split()
            if not bad or any(f not in TAKE_ORIGIN for f in bad):
                raise SyncError(
                    f"merge of origin/{TRUNK} conflicts; resolve, `git commit`, then run ship again.\n{r.stdout}{r.stderr}".rstrip())
            for f in bad:
                git(repo, "checkout", "--theirs", "--", f)
                git(repo, "add", "--", f)
                print(f"merge: {f} collided; took origin's text. Re-apply your edit there if it mattered.")
            git(repo, "commit", "-q", "--no-edit")
    return int(incoming)


def changed_between(repo, a, b):
    """Paths that differ between two revisions (or `a...b`): --no-renames so a rename lists the old path too (its importers must be
    selected), -z so a path with a space stays one path."""
    out = git(repo, "diff", "--name-only", "--no-renames", "-z", a, *([b] if b else [])).stdout.split("\0")
    return [f for f in out if f]


def outgoing_files(repo):
    return changed_between(repo, f"origin/{TRUNK}...HEAD", None)


def needs_gate(files):
    return any(not f.endswith(DOC_SUFFIXES) for f in files)


GATE_SLOTS = 2
GATE_WAIT_NOTE_S = 60


def pid_alive(pid):
    """True when a process with this PID exists (Windows: OpenProcess via ctypes; elsewhere: signal 0)."""
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.OpenProcess.restype = ctypes.c_void_p
        h = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ctypes.get_last_error() == 5 or k32.GetLastError() == 5  # access denied: it exists
        code = ctypes.c_ulong()
        ok = k32.GetExitCodeProcess(ctypes.c_void_p(h), ctypes.byref(code))
        k32.CloseHandle(ctypes.c_void_p(h))
        return bool(ok) and code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


GATE_PRECHECK_SLOTS = 2


def host_gate_slots_dir(name="gate-slots", repo=None):
    """Host-wide gate slots directory (SUPERVISOR.md SV7).
    Separate clones on the same host share the same slot pool so concurrent gates respect the machine budget.
    MTS_GATE_SLOTS_DIR overrides the base directory for tests."""
    env_dir = os.environ.get("MTS_GATE_SLOTS_DIR")
    if env_dir:
        base = Path(env_dir)
    else:
        base = Path(tempfile.gettempdir()) / "mts_gate_slots"
    d = base / name
    d.mkdir(parents=True, exist_ok=True)
    return d


class GateSlotTimeout(Exception):
    """No gate slot came free within the caller's wait budget (auto_deploy treats this as 'do not deploy', never as a green gate)."""


class gate_slot:
    """Machine-wide limit on concurrent gates (ship gates and the auto_deploy gate): at most GATE_SLOTS slot files under
    host-wide gate slots directory, each holding its owner's PID, created with O_EXCL. A slot whose PID is dead is reclaimed.
    Released on exit, whatever raised. timeout=None waits forever (ship); a number of seconds raises GateSlotTimeout when no slot
    came free in that time (deploy: fail closed)."""

    def __init__(self, repo, slots=GATE_SLOTS, alive=pid_alive, sleep=time.sleep, note_every=GATE_WAIT_NOTE_S, poll=2.0, timeout=None,
                 name="gate-slots"):
        self.repo, self.slots, self.alive, self.sleep = repo, slots, alive, sleep
        self.note_every, self.poll, self.path, self.timeout, self.name = note_every, poll, None, timeout, name
        self.wait_s = 0.0

    def _dir(self):
        return host_gate_slots_dir(self.name, self.repo)

    def _try(self, d):
        busy = 0
        for i in range(self.slots):
            p = d / f"slot-{i}"
            for _ in range(2):
                try:
                    fd = os.open(str(p), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                except FileExistsError:
                    try:
                        raw = p.read_text().strip()
                        # GATE_SPEED review: an empty file is its creator mid-write (O_EXCL create, then write), not a dead owner 0;
                        # reclaiming it let two gates hold one slot. Only an empty file older than 10 s is stale.
                        owner = int(raw) if raw else (0 if time.time() - p.stat().st_mtime > 10 else None)
                    except (OSError, ValueError):
                        owner = None  # unreadable or half-written: its creator may be mid-write; treat as busy
                    if owner is not None and not self.alive(owner):
                        print(f"gate slot {i}: owner PID {owner} is dead, reclaiming")
                        try:
                            p.unlink()
                        except OSError:
                            pass
                        continue
                    busy += 1
                    break
                with os.fdopen(fd, "w") as f:
                    f.write(str(os.getpid()))
                return p, busy
        return None, busy

    def __enter__(self):
        d = self._dir()
        start = last = time.monotonic()
        while True:
            self.path, busy = self._try(d)
            if self.path:
                self.wait_s = time.monotonic() - start
                return self
            left = None if self.timeout is None else self.timeout - (time.monotonic() - start)
            if left is not None and left <= 0:
                raise GateSlotTimeout(f"no gate slot free after {self.timeout:g}s ({busy}/{self.slots} busy)")
            if time.monotonic() - last >= self.note_every:
                print(f"gate slot busy ({busy}/{self.slots}), waiting")
                last = time.monotonic()
            self.sleep(self.poll if left is None else max(0.0, min(self.poll, left)))

    def __exit__(self, *exc):
        if self.path:
            try:
                self.path.unlink()
            except OSError:
                pass
            self.path = None
        return False


def run_gate(repo, files=None):
    """The ship gate. files = paths changed vs origin/fast-track: run the smoke gate (scripts/dev/gate_select.py picks the steps; live-path
    or unknown paths = every --quick step). files=None, or SYNC_FULL_GATE=1 (`ship --full`), runs the whole --quick gate. Docs-only
    selections take no gate slot: they are seconds. The full suite runs behind in CI; auto_deploy only takes green/fast-track.
    GATE_SPEED.md: the ship gate runs --precheck (cheap steps + the tests that reference the change, no slot; a failure stops it in about
    a minute), --fail-fast, --slot (run_all_tests takes the gate slot for the main phase only; docs selections take none) and --record
    (a step that passed on this exact clean tree is not run again). `ship --full` still runs every step, with the same four flags."""
    cmd = [sys.executable, "scripts/dev/run_all_tests.py", "--quick", "--precheck", "--fail-fast", "--slot", "--record"]
    list_file = None
    if files:
        fd, list_file = tempfile.mkstemp(prefix="mts_changed_", suffix=".txt")
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(files) + "\n")
        cmd += ["--changed-file", list_file]     # full gate too: the precheck targets the tests that reference the change
        if not os.environ.get("SYNC_FULL_GATE"):
            cmd += ["--smoke"]
            if not os.environ.get("SYNC_NO_FAST"):
                cmd += ["--fast"]    # GATE_SPEED X1-X3: import-graph test selection inside a time budget; the rest runs in CI
    try:
        r = subprocess.run(cmd, cwd=repo)
    finally:
        if list_file:
            try:
                os.unlink(list_file)
            except OSError:
                pass
    if r.returncode != 0:
        raise SyncError("offline gate (--quick) failed; nothing pushed")


def shared_tree_reason(repo):
    """Why this checkout is not a clean per-session tree, or None. At the start of a session nothing in the
    tree is ours, so uncommitted files and unshipped commits belong to another session."""
    ahead = git(repo, "rev-list", "--count", f"origin/{TRUNK}..HEAD", check=False).stdout.strip()
    # Mirror churn is not another session's work; a stray AGENTS.md still counts (it can collide with the tracked one on merge).
    dirty = [l for l in git(repo, "status", "--short").stdout.splitlines() if l and not is_noise(l, strays=False)]
    if dirty:
        return f"{len(dirty)} uncommitted file(s)"
    if ahead not in ("", "0"):
        return f"{ahead} commit(s) not shipped to origin/{TRUNK}"
    return None


def branch_prefix(repo, host):
    """Host prefix for a new branch, in the exact case the ref store already uses. On a case-insensitive FS (Windows) refs
    are files: `git worktree add -b jis-nb/x` next to an existing refs/heads/JIS-NB/ directory stores the ref under JIS-NB/
    while HEAD keeps the typed `jis-nb/x`, which then never resolves (23 invisible trees, 2026-10-15). So reuse the case of an
    existing prefix; with none, the hostname as the OS spells it."""
    for ref in git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.split():
        head, sep, _ = ref.partition("/")
        if sep and head.lower() == host.lower():
            return head
    return host


# Persistent per-lane trees (operator q20, 2026-10-15): `start <slug>` inside one switches to a fresh branch instead of making a worktree.
SWITCH_LANES = ("mts-app", "mts-relay", "mts-dsa")


def switch_lane_branch(repo, slug):
    """Inside a persistent lane tree: move to a fresh branch <host>/<slug> off origin/fast-track. Refuses when the tree holds
    work (uncommitted files or commits not on origin), so nothing is left behind; the previous task's branch is deleted when it
    is fully on origin/fast-track. Returns the branch name."""
    slug = slugify(slug)
    reason = shared_tree_reason(repo)
    if reason:
        raise SyncError(f"lane tree {Path(repo).name} holds work ({reason}); commit and `sync.py ship` it first (`sync.py where` shows it).")
    git(repo, "fetch", "--quiet", "origin", TRUNK)
    branch = f"{branch_prefix(repo, socket.gethostname())}/{slug}"
    old = git(repo, "branch", "--show-current").stdout.strip()
    if git(repo, "rev-parse", "--verify", "-q", f"refs/heads/{branch}", check=False).returncode == 0             and git(repo, "merge-base", "--is-ancestor", branch, f"origin/{TRUNK}", check=False).returncode != 0:
        raise SyncError(f"branch {branch} already has commits not on origin/{TRUNK}; pick another slug or ship it (`sync.py where`).")
    git(repo, "switch", "-q", "-C", branch, f"origin/{TRUNK}")
    if old and old != branch and old != TRUNK and git(repo, "merge-base", "--is-ancestor", old, f"origin/{TRUNK}", check=False).returncode == 0:
        git(repo, "branch", "-D", old, check=False)
    return branch


def new_worktree(repo, slug=None):
    host = socket.gethostname().lower()
    slug = slugify(slug) if slug else time.strftime("s%m%d-%H%M%S", time.gmtime())
    path = Path(repo).resolve().parent / f"mts-{host}-{slug}"
    n = 1
    while path.exists():
        n += 1
        path = path.with_name(f"mts-{host}-{slug}-{n}")
    git(repo, "fetch", "--quiet", "origin", TRUNK)
    branch = f"{branch_prefix(repo, socket.gethostname())}/{slug}" + ("" if n == 1 else f"-{n}")
    git(repo, "worktree", "add", "-q", str(path), "-b", branch, f"origin/{TRUNK}")
    # Belt and braces: whatever the FS did, HEAD must name the ref that exists.
    real = {h.lower(): h for h in git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.split()}.get(branch.lower())
    if real and real != branch:
        git(path, "symbolic-ref", "HEAD", f"refs/heads/{real}")
    return path


PRIOR_DIRS = ("MyTradingSys/research", "MyTradingSys/research/layer_lab", "MyTradingSys/system/tasks")
PRIOR_STOP = {"the", "and", "for", "run", "fix", "new", "dev"}


def prior_work(repo, slug, ref=f"origin/{TRUNK}"):
    """Study folders and task cards on the trunk whose name holds every word of the slug (2026-10-16: the same prompt ran
    twice and the second session found the first one's folder only at ship time). Names only; [] when nothing matches."""
    words = [w for w in re.split(r"[-_\s]+", (slug or "").lower()) if len(w) >= 3 and w not in PRIOR_STOP]
    if not words:
        return []
    hits = []
    for d in PRIOR_DIRS:
        r = git(repo, "ls-tree", "--full-tree", "--name-only", f"{ref}:{d}", check=False)  # --full-tree: same answer from a subdir
        for name in (r.stdout or "").split():
            parts = set(re.split(r"[-_.\s]+", name.lower()))
            if all(w in parts for w in words):
                hits.append(f"{d}/{name}")
    return hits


def start(repo, slug=None, here=False, quiet=False):
    """Bring a tree up to date. Returns the tree the session must work in: `repo` when it is clean, else a
    fresh worktree off origin/fast-track (printed as `WORKTREE: <path>`); never touches the other files."""
    refuse_live(repo)
    if slug and not here and Path(repo).resolve().name in SWITCH_LANES:
        print(f"lane tree {Path(repo).name}: switched to {switch_lane_branch(repo, slug)} off origin/{TRUNK}; work here")
        reason = None
    else:
        reason = None if here else shared_tree_reason(repo)
    if reason:
        path = new_worktree(repo, slug)
        print(f"this tree is shared ({reason}); not working here.")
        print(f"WORKTREE: {path}")
        print(f"work ONLY there: cd {path}")
        repo = path
    n = merge_trunk(repo)
    branch = git(repo, "branch", "--show-current").stdout.strip() or "(detached)"
    print(f"host={socket.gethostname()} branch={branch} pulled={n} head={git(repo, 'rev-parse', '--short', 'HEAD').stdout.strip()}")
    if not quiet:
        print_claims(repo)
    prior = prior_work(repo, slug)
    if prior:
        print(f"prior work on {TRUNK} matching '{slug}' (read it before building; same task twice = compare, never overwrite):")
        for p in prior[:12]:
            print(f"  {p}")
    if not quiet:
        pull_mirror(repo)
    return repo


def claim_areas(kv):
    """Paths a claim covers (the `area:` line), without trailing slashes; [] for '-' or none."""
    return [a.strip().rstrip("/") for a in re.split(r"[,\s]+", kv.get("area", "-")) if a.strip() not in ("", "-")]


def area_overlap(xs, ys):
    """First pair (x, y) of paths, one from each list, that are equal or nested; None when the lists do not meet."""
    return next(((x, y) for x in xs for y in ys if x == y or x.startswith(y + "/") or y.startswith(x + "/")), None)


def health(repo):
    """Collision health, one line per problem, last line `HEALTH: <n> issue(s)`. Returns n. Read-only."""
    git(repo, "fetch", "--quiet", "origin", TRUNK)
    issues = []
    now = time.time()
    claims = read_claims(repo, f"origin/{TRUNK}")
    areas = {}
    for slug, kv in claims:
        age_h = (now - int(kv.get("epoch", now))) / 3600
        if age_h > STALE_HOURS:
            issues.append(f"STALE-CLAIM {slug}: {kv.get('host','?')}/{kv.get('account','?')} {age_h:.0f}h old")
        areas[slug] = claim_areas(kv)
    slugs = sorted(areas)
    for i, a in enumerate(slugs):
        for b in slugs[i + 1:]:
            hit = area_overlap(areas[a], areas[b])
            if hit:
                issues.append(f"OVERLAP claims {a} / {b}: {hit[0]} ~ {hit[1]}")
    broken = []
    for t in survey(repo):
        p, branch = Path(t["path"]), t["branch"]
        if not p.exists():
            issues.append(f"ORPHAN worktree {p.name}: folder gone (git worktree prune)")
            continue
        if (p / LIVE_MARKER).exists():
            continue
        if t["ahead"] is None:
            broken.append(t)
            continue
        reason = unshipped_reason(t)
        if reason and branch in (TRUNK, "master", "main"):
            issues.append(f"SHARED {p.name} [{branch}]: sessions work on the trunk branch here; {reason}")
        elif reason:
            issues.append(f"UNSHIPPED {p.name} [{branch}]: {reason}")
    if broken:
        issues.append(broken_summary(broken))
    rows = git(repo, "for-each-ref", "refs/remotes/origin", "--format=%(refname:short)|%(committerdate:unix)").stdout.splitlines()
    for row in rows:
        ref, _, ts = row.partition("|")
        short = ref.removeprefix("origin/")
        if short in (TRUNK, "HEAD", "origin", "main", "master") or short.startswith(("backup/", "green/", "claude/", "shots-inbox/")):
            continue
        ahead = git(repo, "rev-list", "--count", f"origin/{TRUNK}..{ref}", check=False).stdout.strip()
        if ahead not in ("", "0") and ts and (now - int(ts)) / 3600 > NOT_SHIPPED_HOURS:
            issues.append(f"NEVER-SHIPPED branch {short}: {ahead} commit(s), last {(now - int(ts)) / 3600:.0f}h ago")
    # UNSHIPPED rows first, collisions after them: daily_hygiene reads only the last lines of this output and needs
    # STALE-CLAIM / OVERLAP / ORPHAN / SHARED / NEVER-SHIPPED there (the capped UNSHIPPED rows could push them out).
    unshipped = [i for i in issues if i.startswith("UNSHIPPED")]
    for i in unshipped[:ROW_CAP]:
        print(i)
    if len(unshipped) > ROW_CAP:
        print(f"... {len(unshipped) - ROW_CAP} more UNSHIPPED tree(s): sync.py where --all")
    for i in issues:
        if not i.startswith("UNSHIPPED"):
            print(i)
    print(f"HEALTH: {len(issues)} issue(s)")
    return len(issues)


def pull_mirror(repo):
    """Best effort: refresh runtime_data/_mirror (desktop live state, read-only) so a work tree can answer live questions."""
    script = Path(repo) / "scripts" / "dev" / "live_mirror.py"
    if not script.exists():
        return
    try:
        r = subprocess.run([sys.executable, str(script), "pull"], capture_output=True, text=True, timeout=45, cwd=repo)
        print("live mirror: " + ((r.stdout or r.stderr).strip().splitlines() or ["no output"])[-1])
    except (subprocess.TimeoutExpired, OSError) as e:
        print(f"live mirror: skipped ({type(e).__name__}); run live_mirror.py pull by hand")


def call_gate(gate, repo, files):
    """Older gates take (repo); the default takes (repo, files)."""
    try:
        n = len(inspect.signature(gate).parameters)
    except (TypeError, ValueError):
        n = 1
    return gate(repo, files) if n >= 2 else gate(repo)


def run_docs_gate(repo, files):
    """Docs/data-only ship: the cheap doc invariants (task cards, INDEX/BUGS, doc size and contract tests), no gate slot.
    Skipped where the repo has no gate script (throwaway repos)."""
    if (Path(repo) / "scripts" / "dev" / "run_all_tests.py").exists() and not os.environ.get("SYNC_NO_DOCS_GATE"):
        run_gate(repo, files)


def ci_state(fetch=None):
    """GATE_SPEED X6: (state, line) of fast-track CI. state: 'red' (the newest ci_watch.MIN_STREAK finished runs failed), 'green', or
    'unknown' (offline, rate limited, no runs: never a block). A cached red is re-fetched before it counts, because a fix may have gone
    green since. A newer run in flight does NOT clear a red (fast-track always has one pending); `ship --fix-ci` is the way through.
    fetch(use_cache) -> runs newest first (default ci_watch.current)."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import ci_watch
        get = fetch or ci_watch.current
        runs = get(True)
        if not runs:
            return "unknown", "CI state unknown (offline or no runs)"
        if ci_watch.streak(runs)[0] >= ci_watch.MIN_STREAK:
            runs = get(False) or runs
        n, bad, ok = ci_watch.streak(runs)
        if n >= ci_watch.MIN_STREAK:
            return "red", ci_watch.message(runs)
        return "green", f"CI: {n} failed run(s) in a row, last green {ok['head_sha'][:8] if ok else '-'}"
    except Exception as e:      # never block on a tool failure
        return "unknown", f"CI state unknown ({type(e).__name__}: {e})"


def ci_applies(files):
    """A red CI blocks code ships only: a docs/data-only ship (gate_select's own definition, not just the suffix) is how a fix is explained."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import gate_select
        return any(not gate_select._is_doc(f.replace(chr(92), "/")) for f in files)
    except Exception:
        return needs_gate(files)


class CiCheck:
    """ci_state() on a thread: the network call (4 s cap) overlaps the gate instead of adding to it."""

    def __init__(self, fetch=None):
        self.result = ("unknown", "CI check did not finish")
        self.thread = threading.Thread(target=self._run, args=(fetch,), daemon=True)
        self.thread.start()

    def _run(self, fetch):
        self.result = ci_state(fetch)

    def verdict(self, wait=8.0):
        self.thread.join(wait)
        return self.result


def enforce_ci(check):
    """Print the CI line; raise SyncError when CI is red and this ship is not the fix (`ship --fix-ci` sets SYNC_FIX_CI and the full gate)."""
    if check is None:
        return
    state, line = check.verdict()
    if state == "red":
        if os.environ.get("SYNC_FIX_CI"):
            print(f"{line}\n--fix-ci: shipping through a red CI with the FULL gate")
            return
        raise SyncError(f"{line}\nFix-first: a code ship is blocked while CI is red. If this ship is the fix, run `sync.py ship --fix-ci` "
                        "(full gate); otherwise fix CI before shipping other code.")
    print(line if state == "unknown" else f"CI {state}: {line}")


def stale_pages_lines(repo):
    """STALE lines from artifacts.py (published pages whose repo build differs from the last publish); raises on tool failure."""
    r = subprocess.run([sys.executable, str(Path(repo) / "scripts" / "dev" / "artifacts.py"), "stale"],
                       capture_output=True, text=True, timeout=300)
    return [l for l in r.stdout.splitlines() if l.startswith("STALE ")]


class StalePages:
    """warn_stale_pages on a thread started before the push, so its ~2 s overlaps the push (GATE_SPEED X4/X6); report() waits at most `wait`."""

    def __init__(self, repo):
        self.lines, self.error = [], None
        self.thread = threading.Thread(target=self._run, args=(repo,), daemon=True)
        self.thread.start()

    def _run(self, repo):
        try:
            self.lines = stale_pages_lines(repo)
        except Exception as e:
            self.error = e

    def report(self, wait=4.0):
        self.thread.join(wait)
        if self.thread.is_alive():
            print("stale-page check still running; skipped (run `artifacts.py stale` by hand)")
        else:
            show_stale(self.lines, self.error)


def show_stale(lines, error=None):
    if error is not None:
        print(f"WARNING: stale-page check failed: {error}")
        return
    if lines:
        print(f"WARNING: {len(lines)} published page(s) lag the repo (republish, then artifacts.py publish-record --slug X):")
        print("\n".join("  " + l for l in lines))


def warn_stale_pages(repo):
    """Warning only (never a block): published pages whose repo build differs from the last publish."""
    try:
        lines = stale_pages_lines(repo)
    except Exception as e:
        print(f"WARNING: stale-page check failed: {e}")
        return
    if lines:
        print(f"WARNING: {len(lines)} published page(s) lag the repo (republish, then artifacts.py publish-record --slug X):")
        print("\n".join("  " + l for l in lines))


SHIP_PUSH_TRIES = 5   # GATE_SPEED D4: 3 of 4 passing ships of one session (2026-10-18) lost at least one push race; claims keep PUSH_TRIES
REGATES = 1           # at most this many re-gates after a lost race (only when the incoming commits touch what we ship)


def race_overlap(repo, incoming, outgoing):
    """GATE_SPEED D4: after a lost push race, the incoming trunk files that can break what we ship: the same path, or an incoming
    module that one of our outgoing .py files references (gate_select.references). Empty = push without a re-gate (CI covers the merge)."""
    same = sorted(set(incoming) & set(outgoing))
    if same:
        return same
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import gate_select
    except ImportError:
        return sorted(f for f in incoming if f.endswith(".py"))   # fail closed: cannot tell, so every incoming module counts
    ours = [Path(repo) / f for f in outgoing if f.endswith(".py") and (Path(repo) / f).is_file()]
    theirs = [Path(repo) / f for f in incoming if f.endswith(".py") and (Path(repo) / f).is_file()]
    our_stems = [Path(f).stem for f in outgoing if f.endswith(".py") and Path(f).stem not in gate_select.SHARED_STEMS]
    fwd = {f for f in incoming if f.endswith(".py") and Path(f).stem not in gate_select.SHARED_STEMS
           and any(gate_select.references(Path(f).stem, p) for p in ours)}
    # GATE_SPEED review: the other direction too - an incoming module that imports/names one of OUR changed modules is as dangerous
    back = {p.relative_to(repo).as_posix() for p in theirs if any(gate_select.references(s, p) for s in our_stems)}
    return sorted(fwd | back)


def wait_after(repo, slug, timeout=3600, poll=2.0, sleep=time.sleep, now_fn=time.time, fetch_fn=None):
    """Wait for predecessor <slug> to ship or fail, or lapse after timeout (default 60 min).
    Never holds or acquires a gate slot while waiting.
    Returns: 'shipped', 'failed', or 'lapsed'.
    """
    start = now_fn()
    claim_path = f"{CLAIMS_DIR}/{slug}.md"
    card_path = f"{CARDS_DIR}/{slug}.json"
    while True:
        if fetch_fn is not None:
            fetch_fn(repo)
        else:
            fetch_trunk(repo)

        card_res = git(repo, "cat-file", "-p", f"origin/{TRUNK}:{card_path}", check=False)
        if card_res.returncode == 0:
            try:
                card = json.loads(card_res.stdout)
                st = card.get("status") or card.get("state")
                if st in ("failed", "tried"):
                    return "failed"
                if st in ("done", "released", "shipped"):
                    return "shipped"
            except Exception:
                pass

        claim_res = git(repo, "cat-file", "-e", f"origin/{TRUNK}:{claim_path}", check=False)
        if claim_res.returncode != 0:
            return "shipped"

        if now_fn() - start >= timeout:
            return "lapsed"

        sleep(poll)


def record_ship_timing(repo, wait_s, run_s, retry_s, ok=True, sha=None, path=None):
    """Append one JSON line {step, name, wait_s, run_s, retry_s, ok, utc, sha} to runtime_data/gate_timing.jsonl
    (MTS_GATE_TIMING overrides the path). SV7: logs wait, run and retry seconds per ship. Never raises."""
    try:
        p = Path(path or os.environ.get("MTS_GATE_TIMING") or (Path(repo) / "runtime_data" / "gate_timing.jsonl"))
        p.parent.mkdir(parents=True, exist_ok=True)
        short_sha = sha
        if not short_sha:
            r = git(repo, "rev-parse", "--short=8", "HEAD", check=False)
            short_sha = r.stdout.strip() if r.returncode == 0 else ""
        row = {
            "step": "ship",
            "name": "sync.ship",
            "wait_s": round(float(wait_s), 2),
            "run_s": round(float(run_s), 2),
            "retry_s": round(float(retry_s), 2),
            "wait": round(float(wait_s), 2),
            "run": round(float(run_s), 2),
            "retry": round(float(retry_s), 2),
            "secs": round(float(wait_s + run_s + retry_s), 2),
            "ok": bool(ok),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sha": short_sha,
        }
        with open(p, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row) + "\n")
    except Exception:
        pass


def ship(repo, gate=run_gate, docs_gate=run_docs_gate, release_slug=None, after_slug=None, sleep=time.sleep):
    """release_slug (traffic buster B4): the claim file is deleted in a commit on this branch, so the release rides the
    same push as the work (no separate fetch + push). Nothing to ship: falls back to the plumbing release.
    after_slug (SV3): wait for predecessor order ticket to finish or lapse before running the gate; never holds a gate slot while waiting.
    A lost push race (GATE_SPEED D4) re-merges and pushes again after a 1-5 s jitter, up to SHIP_PUSH_TRIES; it re-runs the gate
    only when the incoming commits overlap what we ship (race_overlap), at most REGATES times."""
    refuse_live(repo)  # only commits are pushed; uncommitted files stay where they are
    wait_s = 0.0
    run_s = 0.0
    retry_s = 0.0
    if after_slug:
        t_wait_0 = time.monotonic()
        res = wait_after(repo, after_slug)
        wait_s += time.monotonic() - t_wait_0
        print(f"order ticket --after {after_slug}: {res}")
    rel = f"{CLAIMS_DIR}/{release_slug}.md" if release_slug else None
    released = False
    regates = 0
    files = []
    ci = None
    ok = False
    try:
        for attempt in range(1, SHIP_PUSH_TRIES + 1):
            before = git(repo, "rev-parse", "HEAD").stdout.strip()
            merge_trunk(repo)
            shipped_before, files = files, outgoing_files(repo)
            if not files:
                if release_slug:
                    release(repo, release_slug)
                else:
                    print("nothing to ship")
                return
            if attempt == 1:
                if gate is run_gate and ci_applies(files):    # custom gates (tests, throwaway repos) stay hermetic: no network
                    ci = CiCheck()
                if needs_gate(files):
                    t_gate_0 = time.monotonic()
                    call_gate(gate, repo, files)
                    run_s += time.monotonic() - t_gate_0
                elif docs_gate:
                    t_gate_0 = time.monotonic()
                    docs_gate(repo, files)
                    run_s += time.monotonic() - t_gate_0
                enforce_ci(ci)
            else:
                after = git(repo, "rev-parse", "HEAD").stdout.strip()
                hit = race_overlap(repo, changed_between(repo, before, after), shipped_before) if after != before else []
                if hit and regates < REGATES and needs_gate(files):
                    regates += 1
                    print(f"incoming commits touch what we ship ({', '.join(hit[:5])}); re-running the gate")
                    t_gate_0 = time.monotonic()
                    call_gate(gate, repo, files)
                    run_s += time.monotonic() - t_gate_0
                elif hit:
                    print(f"incoming commits touch {', '.join(hit[:5])}; re-gate limit reached, CI checks the merge")
            if rel and git(repo, "cat-file", "-e", f"HEAD:{rel}", check=False).returncode == 0:
                git(repo, "rm", "--quiet", "-f", rel)
                git(repo, "commit", "--quiet", "-m", f"release {release_slug}" + chr(10) * 2 + f"Result: claim {release_slug} closed with the ship")
                released = True
            pages = StalePages(repo)       # overlaps the push
            r = git(repo, "push", "--quiet", "origin", f"HEAD:refs/heads/{TRUNK}", check=False)
            if r.returncode == 0:
                ok = True
                print(f"shipped {len(files)} file(s) to origin/{TRUNK}" + (f"; released {release_slug}" if released else ""))
                pages.report()
                return
            print(f"push rejected (someone shipped first), retry {attempt}/{SHIP_PUSH_TRIES}")
            if attempt < SHIP_PUSH_TRIES:
                t_retry_0 = time.monotonic()
                sleep(1.0 + 4.0 * random.random())   # two ships that lost to the same push must not collide again in lockstep
                retry_s += time.monotonic() - t_retry_0
        raise SyncError(f"push still rejected after {SHIP_PUSH_TRIES} tries:\n{r.stderr}")
    finally:
        if files:
            record_ship_timing(repo, wait_s=wait_s, run_s=run_s, retry_s=retry_s, ok=ok)


def news(repo, hours=24):
    """Operator digest: one block per shipped commit - subject, Result: line, areas touched. No code."""
    git(repo, "fetch", "--quiet", "origin", TRUNK)
    log = git(repo, "log", f"origin/{TRUNK}", f"--since={hours} hours ago", "--no-merges",
              "--format=%x1e%h|%ad|%s%n%b%x1f", "--date=format:%m-%d %H:%M", "--name-only").stdout
    lines = []
    for rec in log.split("\x1e")[1:]:
        head, _, files = rec.partition("\x1f")
        first, _, body = head.partition("\n")
        h, when, subject = first.split("|", 2)
        result = next((l.strip() for l in body.splitlines() if l.strip().lower().startswith("result:")),
                      "Result: (not stated)")
        areas = sorted({"/".join(f.split("/")[:-1][-2:]) or f for f in files.split() if f})  # parent folder
        more = f" +{len(areas) - 4}" if len(areas) > 4 else ""
        lines.append(f"{when} {h}  {subject}\n    {result}\n    areas: {', '.join(areas[:4])}{more}")
    print("\n".join(lines) if lines else f"nothing shipped in the last {hours} h")


def worktrees(repo):
    """[(path, branch)] of every worktree of this repo."""
    out, rows, cur = git(repo, "worktree", "list", "--porcelain").stdout, [], {}
    for line in out.splitlines() + [""]:
        if not line:
            if cur.get("worktree"):
                rows.append((cur["worktree"], cur.get("branch", "(detached)").replace("refs/heads/", "")))
            cur = {}
        else:
            k, _, v = line.partition(" ")
            cur[k] = v
    return rows


def tree_state(path):
    """(ahead, work, noise) of the worktree at `path`: commits not on origin/fast-track, the uncommitted
    `status --short` rows that are real work, and the rows that are not (is_noise). ahead is None when HEAD does not
    resolve (unborn, pointing at a missing ref, or the folder is gone); work and noise are then empty."""
    r = git(path, "rev-list", "--count", f"origin/{TRUNK}..HEAD", check=False)
    if r.returncode != 0:
        return None, [], []
    rows = [l for l in git(path, "status", "--short", check=False).stdout.splitlines() if l]
    return int(r.stdout.strip() or 0), [l for l in rows if not is_noise(l)], [l for l in rows if is_noise(l)]


def survey(repo):
    """One dict per worktree (path, name, branch, ahead, work, noise, fix), looked at in parallel: about 3 git calls each
    and 90+ trees. `fix` says what to do about a tree whose HEAD does not resolve (ahead is None)."""
    rows = worktrees(repo)
    with ThreadPoolExecutor(max_workers=8) as pool:
        states = list(pool.map(lambda row: tree_state(row[0]), rows))
    trees = [dict(path=p, name=Path(p).name, branch=b, ahead=s[0], work=s[1], noise=s[2], fix="")
             for (p, b), s in zip(rows, states)]
    broken = [t for t in trees if t["ahead"] is None]
    if broken:
        # A HEAD that names `jis-nb/x` while the branch is `JIS-NB/x` (made on a case-insensitive FS) never resolves.
        heads = {h.lower(): h for h in git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.split()}
        for t in broken:
            real = heads.get(t["branch"].lower())
            if not Path(t["path"]).exists():
                t["fix"] = "folder gone: `git worktree prune`"
            elif real and real != t["branch"]:
                t["fix"] = f"HEAD names {t['branch']} but the branch is {real}: git -C {t['path']} symbolic-ref HEAD refs/heads/{real}"
            else:
                t["fix"] = "branch has no commits (ref missing); copy any wanted files out, then `git worktree remove`"
    return trees


def unshipped_reason(t):
    """Why a surveyed tree holds work, or None: real uncommitted files first, else commits not on origin."""
    if t["work"]:
        return f"{len(t['work'])} uncommitted file(s)"
    if t["ahead"]:
        return f"{t['ahead']} commit(s) not shipped to origin/{TRUNK}"
    return None


def broken_summary(broken):
    names = ", ".join(t["name"] for t in broken[:5]) + (", ..." if len(broken) > 5 else "")
    return f"BROKEN    {len(broken)} tree(s) with HEAD on a missing ref ({names}); `sync.py where --all` prints the fix per tree"


def where(repo, all_=False):
    """Same-page check for any account or machine: what is shipped, and what is still only in a worktree.
    Default: this tree plus every tree holding real work (commits not on origin, or uncommitted files that are not the
    pulled mirror / a stray AGENTS.md), at most ROW_CAP rows and one summary line (~1 KB). all_: every tree, one row each."""
    git(repo, "fetch", "--quiet", "origin", TRUNK)
    tip = git(repo, "log", "-1", "--format=%h %ar %s", f"origin/{TRUNK}").stdout.strip()
    print(f"origin/{TRUNK}: {tip}")
    here = Path(repo).resolve()
    trees = survey(repo)
    for t in trees:
        t["flag"] = "BROKEN" if t["ahead"] is None else "UNSHIPPED" if unshipped_reason(t) else "ok"

    def row(t):
        tracked = sum(1 for l in t["work"] if not l.startswith("??"))
        return (f"{t['flag']:9} {t['name']:28} [{t['branch']}] unshipped-commits={t['ahead']} modified={tracked} "
                f"untracked={len(t['work']) - tracked}" + (f" ignored-noise={len(t['noise'])}" if all_ and t["noise"] else ""))
    broken = [t for t in trees if t["flag"] == "BROKEN"]
    if all_:
        for t in trees:
            print(f"BROKEN    {t['name']:28} [{t['branch']}] {t['fix']}" if t["flag"] == "BROKEN" else row(t))
    else:
        # This tree first, always (flagged or ok): the end-of-session check is about it. The cap applies to the rest.
        mine = [t for t in trees if t["flag"] != "BROKEN" and Path(t["path"]).resolve() == here]
        others = [t for t in trees if t["flag"] == "UNSHIPPED" and t not in mine]
        room = max(ROW_CAP - len(mine), 0)
        for t in mine + others[:room]:
            print(row(t))
        if len(others) > room:
            print(f"... {len(others) - room} more with unshipped work: sync.py where --all")
        if broken:
            print(broken_summary(broken))
    open_items = sum(t["flag"] != "ok" for t in trees)
    print(f"{open_items} worktree(s) hold work that is not on origin/{TRUNK}; commit and `sync.py ship` them (the live tree is shipped by its owners)"
          + ("" if all_ else f" [{len(trees)} trees checked; `sync.py where --all` lists every one]"))


def account(repo):
    """Which Claude/GitHub identity is working: MTS_ACCOUNT env wins, else git user.name."""
    return os.environ.get("MTS_ACCOUNT") or git(repo, "config", "user.name", check=False).stdout.strip() or "unknown"


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "task"


def read_claims(repo, ref):
    """[(slug, {key: value})] of claim files on `ref`."""
    names = git(repo, "ls-tree", "--name-only", ref, f"{CLAIMS_DIR}/", check=False).stdout.split()
    rows = []
    for n in names:
        if not n.endswith(".md"):
            continue
        body = git(repo, "show", f"{ref}:{n}").stdout
        kv = dict(l.split(": ", 1) for l in body.splitlines() if ": " in l)
        rows.append((Path(n).stem, kv))
    return rows


def print_claims(repo, ref=None):
    ref = ref or f"origin/{TRUNK}"
    rows = read_claims(repo, ref)
    if not rows:
        print("claims: none open")
        return
    now = time.time()
    for slug, kv in rows:
        age_h = (now - int(kv.get("epoch", now))) / 3600
        stale = " STALE (ask the owner or release it)" if age_h > STALE_HOURS else ""
        print(f"claim {slug}: {kv.get('host','?')} / {kv.get('account','?')} - {kv.get('task','?')} "
              f"[area: {kv.get('area','-')}] {age_h:.0f}h old{stale}")


def push_claim_commit(repo, rel, text, msg):
    """Traffic buster (2026-10-16): put ONE claim-file change on origin/fast-track as a commit built with plumbing on
    top of origin's tip: no merge commit, no gate, no dependence on this tree's state (dirty or ahead is fine). text=None
    removes the file. Returns the pushed sha. Afterwards this branch is fast-forwarded to it when it can be (never a merge)."""
    for attempt in range(1, PUSH_TRIES + 1):
        git(repo, "fetch", "--quiet", "origin", TRUNK)
        parent = git(repo, "rev-parse", f"origin/{TRUNK}").stdout.strip()
        idx = Path(git(repo, "rev-parse", "--absolute-git-dir").stdout.strip()) / f"claim-index-{os.getpid()}"
        env = {**os.environ, "GIT_INDEX_FILE": str(idx)}

        def plumb(*args, stdin=None):
            r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env, input=stdin)
            if r.returncode != 0:
                raise SyncError(f"git {' '.join(args)} failed:" + chr(10) + f"{r.stdout}{r.stderr}".rstrip())
            return r.stdout.strip()
        try:
            plumb("read-tree", parent)
            if text is None:
                plumb("update-index", "--force-remove", rel)
            else:
                blob = plumb("hash-object", "-w", "--stdin", stdin=text)
                plumb("update-index", "--add", "--cacheinfo", f"100644,{blob},{rel}")
            commit = plumb("commit-tree", plumb("write-tree"), "-p", parent, "-m", msg)
        finally:
            idx.unlink(missing_ok=True)
        if git(repo, "push", "--quiet", "origin", f"{commit}:refs/heads/{TRUNK}", check=False).returncode == 0:
            git(repo, "merge", "--ff-only", "--quiet", commit, check=False)  # only when this branch has nothing unshipped
            return commit
        print(f"push rejected (someone shipped first), retry {attempt}/{PUSH_TRIES}")
    raise SyncError(f"claim push still rejected after {PUSH_TRIES} tries")


def new_files_only_reason(repo, task, area="-"):
    """B16 (B2 made automatic): why a claim is pointless, or '' (claim as usual). A task whose whole scope is NEW files under
    its own dated folder (`..._2026-10-17/`) has nothing to collide on. Scope = the --area paths, else `scope_in` of the task
    card named like the task (id, or the task text slugified), read from origin's tip. Fails open: no card, no scope,
    a live-path card, an existing file, any path outside a dated folder = claim."""
    dated = re.compile(r"\d{4}-\d{2}-\d{2}")
    paths = [x for x in re.split(r"[,\s]+", area) if x not in ("", "-")]
    where = "--area"
    if not paths:
        for cid in dict.fromkeys([str(task).strip(), slugify(task)]):
            r = git(repo, "show", f"origin/{TRUNK}:{CARDS_DIR}/{cid}.json", check=False)
            if r.returncode == 0:
                break
        else:
            return ""
        try:
            card = json.loads(r.stdout)
        except ValueError:
            return ""
        if card.get("live_path"):
            return ""
        where = f"card {cid}"
        for entry in card.get("scope_in") or []:
            if re.match(r"\s*read-only", entry, re.I):
                continue  # reads collide with nothing
            found = re.findall(r"[\w.\-]+(?:/[\w.\-]*)+", entry)
            if not found:
                return ""
            paths += found
    if not paths:
        return ""
    for pth in paths:
        parts = pth.rstrip("/").split("/")
        is_dir = pth.endswith("/") or "." not in parts[-1]
        if not any(dated.search(d) for d in (parts if is_dir else parts[:-1])):
            return ""
        if not is_dir and git(repo, "cat-file", "-e", f"origin/{TRUNK}:{pth}", check=False).returncode == 0:
            return ""  # edits a file that already exists
    return f"{where} writes only new files under dated folders ({', '.join(sorted(set(paths))[:3])})"


def claim(repo, task, area="-", gate=run_gate, force=False):
    if str(task).startswith("--"):
        raise SyncError(f"claim name {task!r} looks like a flag, not a task name; usage: sync.py claim \"<task>\" [--area <paths>]")
    refuse_live(repo)
    if not force:
        git(repo, "fetch", "--quiet", "origin", TRUNK)
        why = new_files_only_reason(repo, task, area)
        if why:
            print(f"no claim needed (B2): {why}. Nothing to release: finish with sync.py ship. Claim anyway: sync.py claim \"<task>\" --force")
            return
    slug0 = slugify(task)
    mine = claim_areas({"area": area})
    NL = chr(10)
    for attempt in range(1, PUSH_TRIES + 1):  # re-check on every retry: a racing claim may have landed
        git(repo, "fetch", "--quiet", "origin", TRUNK)
        open_claims = read_claims(repo, f"origin/{TRUNK}")
        for other, kv in open_claims:
            # With areas on both sides a claim blocks only on overlap (operator q20); a claim without --area cannot be compared,
            # so there only the same task name blocks.
            theirs = claim_areas(kv)
            hit = area_overlap(mine, theirs) if mine and theirs else None
            if hit or (other == slug0 and not (mine and theirs)):
                raise SyncError(f"already claimed by {kv.get('host')} / {kv.get('account')}: {kv.get('task')}"
                                + (f" (area {hit[0]} ~ {hit[1]})" if hit else "") + ". Pick another task or area, or ask them (a claim over 24 h old is stale: release it).")
        taken = {s for s, _ in open_claims}
        slug, n = slug0, 1
        while slug in taken:  # same task name, disjoint areas: both may work
            n += 1
            slug = f"{slug0}-{n}"
        body = NL.join([f"task: {task}", f"host: {socket.gethostname()}", f"account: {account(repo)}",
                        f"area: {area}", f"epoch: {int(time.time())}", ""])
        msg = NL.join([f"claim {slug}", "", f"Result: {account(repo)} on {socket.gethostname()} works on: {task}"])
        try:
            push_claim_commit(repo, f"{CLAIMS_DIR}/{slug}.md", body, msg)
        except SyncError:
            if attempt == PUSH_TRIES:
                raise
            continue
        print(f"claimed {slug}; release with: sync.py release {slug}")
        return


def release(repo, slug, gate=run_gate):
    refuse_live(repo)
    git(repo, "fetch", "--quiet", "origin", TRUNK)
    rel = f"{CLAIMS_DIR}/{slug}.md"
    if git(repo, "cat-file", "-e", f"origin/{TRUNK}:{rel}", check=False).returncode != 0:
        raise SyncError(f"no claim {slug} on origin/{TRUNK}")
    ahead = git(repo, "rev-list", "--count", f"origin/{TRUNK}..HEAD", check=False).stdout.strip()
    if ahead.isdigit() and int(ahead) > 0:
        print(f"hint (B4): this tree has {ahead} unshipped commit(s); `sync.py ship --release {slug}` closes the claim in the same push and saves a commit")
    push_claim_commit(repo, rel, None, f"release {slug}" + chr(10) * 2 + f"Result: claim {slug} closed")
    print(f"released {slug}")


# Fixed lanes other tooling points at (dispatcher prompts, codex lab, push recipe): `tidy --all` still keeps them.
# mts-control-room is the working folder of the Claude routine mts-control-room (~/.claude/scheduled-tasks/mts-control-room/
# SKILL.md); it sits idle between runs, so without this `tidy --all` would remove it as hand-named.
LANE_WORKTREES = ("mts-push", "mts-refiner", "mts-codex-lab", "mts-codex", "mts-dsa", "mts-relay", "mts-control-room", "mts-app")


TIDY_IDLE_HOURS = 24
TIDY_KEEP_LINES = 10  # keep-reasons listed one per line; the rest only counted in the last line
QUIET_KEEPS = ("lane", "hand-named")  # decided by the name alone: counted, never listed
# Ignored paths that are rebuilt for free; anything else ignored (Dumps/, runtime_data/, fetched klines) is data.
# target/ = Maven build output; settings.local.json is an identical copy in every tree; control_room/ is generated HTML;
# ACCOUNT_DAILY_LOSS.jsonl is what the daily-loss tests write into a work tree's journal. _mirror (and its .lock/.tmp
# staging dirs) is the desktop live state, re-pulled by `sync.py start` / `live_mirror.py brief`; .pytest_tmp/ and .codex/
# are test-runner and tool droppings. All three are in .gitignore, so `status --ignored` lists them in every tree.
REGENERABLE = ("__pycache__/", ".pytest_cache/", ".pyc", " target/", ".claude/settings.local.json", "runtime_data/control_room/",
               "journal/ACCOUNT_DAILY_LOSS.jsonl", "runtime_data/_mirror", ".pytest_tmp/", ".codex/",
               "runtime_data/gate_timing.jsonl")


def holds_files(root, rel):
    """True when ignored path `rel` under `root` is a file or a directory with at least one file below it (an empty
    ignored directory, such as Dumps/workers/, loses nothing when its tree is removed)."""
    path = Path(root) / rel.strip('"')
    return path.is_file() or any(files for _, _, files in os.walk(path))


def ignored_data(p):
    """Ignored paths in worktree `p` that are not trivially regenerable (`git worktree remove` deletes them)."""
    out = git(p, "status", "--porcelain", "--ignored=matching", check=False).stdout.splitlines()
    return [l[3:] for l in out if l.startswith("!! ") and not any(m in l for m in REGENERABLE) and holds_files(p, l[3:])]


def last_reflog_stamp(f):
    """Epoch of the last entry in reflog file `f` (`<old> <new> <name> <email> <epoch> <tz>\t<msg>`), or None. The file's
    mtime is no sign of life: `git gc` (reflog expire) rewrites it without adding an entry."""
    try:
        lines = [l for l in Path(f).read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    except OSError:
        return None
    m = re.search(r" (\d+) [+-]\d{4}$", lines[-1].split("\t", 1)[0]) if lines else None
    return int(m.group(1)) if m else None


def idle_hours(p, branch, now):
    """Hours since the last sign of life: newest of the branch tip commit, the worktree's index/HEAD mtimes and the
    time of the last entry in its logs/HEAD."""
    stamps = []
    r = git(p, "log", "-1", "--format=%ct", branch, check=False).stdout.strip()
    if r.isdigit():
        stamps.append(int(r))
    gd = git(p, "rev-parse", "--absolute-git-dir", check=False).stdout.strip()
    if gd:
        for n in ("index", "HEAD"):
            f = Path(gd) / n
            if f.exists():
                stamps.append(f.stat().st_mtime)
        last = last_reflog_stamp(Path(gd) / "logs" / "HEAD")
        if last is not None:
            stamps.append(last)
    return (now - max(stamps)) / 3600 if stamps else 0.0


def is_app_tree(p):
    """Worktrees the Claude desktop app and EnterWorktree make live in <repo>/.claude/worktrees/<random-name>."""
    return p.parent.name == "worktrees" and p.parent.parent.name == ".claude"


def repair_heads(repo, apply=True):
    """Point a worktree whose HEAD names `jis-nb/x` at the real `JIS-NB/x` (case-only mismatch from a case-insensitive FS).
    Only HEAD moves: no file, index or commit is touched. Returns the paths repaired (or that would be)."""
    done = []
    for t in survey(repo):
        m = re.search(r"symbolic-ref HEAD (refs/heads/\S+)$", t["fix"])
        if t["ahead"] is None and m and Path(t["path"]).exists():
            if apply:
                git(t["path"], "symbolic-ref", "HEAD", m.group(1), check=False)
            done.append(t["path"])
            print(f"{'repaired' if apply else 'would repair'}  {t['name']}: HEAD -> {m.group(1)}")
    return done


def tidy(repo, apply=False, include_named=False, min_idle_hours=TIDY_IDLE_HOURS, now=None):
    """Retire finished worktrees: `../mts-<host>-<slug>` made by `start`, the App's `.claude/worktrees/*` and `../mts-relay-*`.
    Dry run unless apply. Removed only when: not the primary tree, not the one we are in, no live marker, clean (the pulled
    mirror and a stray AGENTS.md/.codex do not count), no ignored data files (those are deleted with the tree), branch fully
    on origin/fast-track, and idle for `min_idle_hours` (a just-started tree is clean and "on origin" too, so cleanliness
    alone cannot tell it from a finished one). Lanes (mts-push, mts-relay ...) and anything else are never touched unless
    include_named. Prints the removals, at most TIDY_KEEP_LINES keep reasons, and a last line with a count per reason.
    Returns the paths removed (or that would be)."""
    now = time.time() if now is None else now
    git(repo, "fetch", "--quiet", "origin", TRUNK)
    if apply:
        repair_heads(repo)   # a case-broken HEAD would hide the tree from every check below
    here = Path(repo).resolve()
    rows = worktrees(repo)
    out, kept, listed = [], {}, 0

    def keep(p, key, why):
        nonlocal listed
        kept[key] = kept.get(key, 0) + 1
        if key not in QUIET_KEEPS and listed < TIDY_KEEP_LINES:
            listed += 1
            print(f"keep  {p.name}: {why}")

    for path, branch in rows[1:]:
        p = Path(path).resolve()
        if p == here or not p.exists() or (p / LIVE_MARKER).exists():
            continue
        auto = (re.match(r"mts-.+-s\d{4}-\d{6}(-\d+)?$", p.name) or p.name.startswith((f"mts-{socket.gethostname().lower()}-", "mts-relay-"))
                or is_app_tree(p))
        if p.name in LANE_WORKTREES:
            keep(p, "lane", "named lane")
            continue
        if not (auto or include_named):
            keep(p, "hand-named", "hand-named")
            continue
        if branch in ("(detached)", TRUNK, "master", "main"):
            keep(p, "branch", f"branch {branch}")
            continue
        rows_dirty = [l for l in git(p, "status", "--short", check=False).stdout.splitlines() if l]
        if any(not is_noise(l) for l in rows_dirty):
            keep(p, "uncommitted", "uncommitted files")
            continue
        anc = git(repo, "merge-base", "--is-ancestor", branch, f"origin/{TRUNK}", check=False).returncode
        if anc > 1:
            keep(p, "unborn", f"HEAD names {branch}, which is not a branch (see `sync.py where --all`)")
            continue
        if anc == 1:
            keep(p, "unshipped", f"{branch} has commits not on origin/{TRUNK}")
            continue
        data = ignored_data(p)
        if data:
            keep(p, "data", f"ignored data would be deleted ({len(data)} path(s), e.g. {data[0]}); move it to the "
                            f"primary tree's Dumps/ first")
            continue
        idle = idle_hours(p, branch, now)
        if idle < min_idle_hours:
            keep(p, "active", f"active {idle:.1f} h ago (tidy waits {min_idle_hours} h)")
            continue
        if apply:
            # --force only for the noise rows above (pulled mirror, stray AGENTS.md/.codex): git counts untracked files as dirt
            r = git(repo, "worktree", "remove", *(["--force"] if rows_dirty else []), str(p), check=False)
            if r.returncode != 0:
                keep(p, "remove-failed", f"remove failed ({r.stderr.strip()[:80]})")
                continue
            git(repo, "branch", "-d", branch, check=False)
        print(f"{'removed' if apply else 'would remove'}  {p.name} [{branch}]")
        out.append(str(p))
    if apply:
        git(repo, "worktree", "prune", check=False)
    counts = ", ".join(f"{k} {n}" for k, n in sorted(kept.items(), key=lambda kv: (-kv[1], kv[0])))
    print(f"{'removed' if apply else 'would remove'} {len(out)}; kept {sum(kept.values())}" + (f" ({counts})" if kept else "")
          + ("" if apply else "; `sync.py tidy --apply` removes, `--all` also tries hand-named trees"))
    return out


def lease_guard(argv):
    """TRAFFIC_CONTROLLER.md Part A: a singleton-role session (Pipeliner) ships, claims and releases
    only while it holds its lease (scripts/dev/lease.py); fails closed. Any other session: no-op, no network."""
    if not argv or argv[0] not in ("ship", "claim", "release"):
        return 0
    import lease
    try:
        lease.guard(toplevel(Path.cwd()), lease.MIN_FOR_SHIP if argv[0] == "ship" else 0)
    except (lease.LeaseError, SyncError) as e:
        print(f"sync: LEASE {'REFUSED' if getattr(e, 'code', 4) == lease.REFUSED else 'UNREACHABLE'}: {e}", file=sys.stderr)
        return getattr(e, "code", lease.UNREACHABLE)
    return 0


def toplevel_or_none():
    try:
        return toplevel(Path.cwd())
    except Exception:
        return None


def run_host_health(repo):
    """Host-health preflight (host_health.py): reap dead gates/tickets, report strays, disk and CPU queue. Fail closed: never raises,
    never blocks a ship; errors go to <temp>/mts_host_health/health.log."""
    try:
        if repo is None:
            return []
        import host_health
        return host_health.run_safe(repo)
    except Exception as e:
        try:
            print(f"host health skipped: {e!r}")
        except Exception:
            pass
        return []


def main(argv):
    cmds = {"start": start, "ship": ship, "news": news, "claims": print_claims, "health": health}
    extra = {"claim", "release"}
    refused = lease_guard(argv)
    if refused:
        return refused
    if argv and argv[0] == "where" and set(argv[1:]) <= {"--all"}:
        try:
            where(toplevel(Path.cwd()), "--all" in argv)
        except SyncError as e:
            print(f"sync: {e}", file=sys.stderr)
            return 1
        return 0
    if argv and argv[0] == "tidy" and len(argv) <= 3:
        try:
            tidy(toplevel(Path.cwd()), "--apply" in argv, "--all" in argv)
        except SyncError as e:
            print(f"sync: {e}", file=sys.stderr)
            return 1
        return 0
    if argv and argv[0] in extra and len(argv) >= 2:
        try:
            repo = toplevel(Path.cwd())
            if argv[0] == "release":
                release(repo, argv[1])
            else:
                area = argv[argv.index("--area") + 1] if "--area" in argv else "-"
                claim(repo, argv[1], area, force="--force" in argv)
        except SyncError as e:
            print(f"sync: {e}", file=sys.stderr)
            return 1
        return 0
    if argv and argv[0] == "start" and len(argv) <= 4:
        try:
            here = "--here" in argv
            quiet = "--quiet" in argv or "-q" in argv
            rest = [a for a in argv[1:] if a not in ("--here", "--quiet", "-q")]
            start(toplevel(Path.cwd()), rest[0] if rest else None, here, quiet=quiet)
        except SyncError as e:
            print(f"sync: {e}", file=sys.stderr)
            return 1
        return 0
    if argv and argv[0] == "ship":
        run_host_health(toplevel_or_none())
        try:
            if "--fix-ci" in argv:
                # GATE_SPEED X6: the way through a red-CI block is the FULL gate (never the fast one), so it cannot be a cheap bypass
                os.environ["SYNC_FIX_CI"] = "1"
                os.environ["SYNC_FULL_GATE"] = "1"
                argv = [a for a in argv if a != "--fix-ci"]
            if "--full" in argv:
                os.environ["SYNC_FULL_GATE"] = "1"
                argv = [a for a in argv if a != "--full"]
            release_slug = None
            if "--release" in argv:
                i = argv.index("--release")
                if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                    raise SyncError("usage: sync.py ship [--full] [--fix-ci] [--release <slug>] [--after <slug>]")
                release_slug = argv[i + 1]
                argv = argv[:i] + argv[i + 2:]
            after_slug = None
            if "--after" in argv:
                i = argv.index("--after")
                if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                    raise SyncError("usage: sync.py ship [--full] [--fix-ci] [--release <slug>] [--after <slug>]")
                after_slug = argv[i + 1]
                argv = argv[:i] + argv[i + 2:]
            if len(argv) != 1:
                raise SyncError(f"unknown arguments to ship: {' '.join(argv[1:])}")
            ship(toplevel(Path.cwd()), release_slug=release_slug, after_slug=after_slug)
        except SyncError as e:
            print(f"sync: {e}", file=sys.stderr)
            return 1
        return 0
    if not argv or argv[0] not in cmds or (argv[0] != "news" and len(argv) != 1):
        print(__doc__)
        return 2
    try:
        repo = toplevel(Path.cwd())
        if argv[0] == "health":
            run_host_health(repo)
        if argv[0] == "news":
            news(repo, *(int(a) for a in argv[1:2]))
        else:
            cmds[argv[0]](repo)
    except SyncError as e:
        print(f"sync: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
