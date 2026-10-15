"""One way for any session on any machine to share work: origin/fast-track is the only meeting point.

  python scripts/dev/sync.py start [slug]  # up to date with origin/fast-track; in a shared/dirty tree makes your own worktree
  python scripts/dev/sync.py health  # stale/overlapping claims, shared or orphan worktrees, branches never shipped
  python scripts/dev/sync.py ship    # merge origin/fast-track, gate, push HEAD to origin/fast-track
  python scripts/dev/sync.py news [hours=24]  # what shipped: feature + Result line per commit, no code
  python scripts/dev/sync.py claim "<task>" [--area <paths>]  # tell parallel sessions what you work on (shipped at once)
  python scripts/dev/sync.py claims  # open claims on origin/fast-track (host, account, task, age); release: `release <slug>`
  python scripts/dev/sync.py where [--all]  # trees holding work not on origin/fast-track (nothing lost?); --all lists every tree
  python scripts/dev/sync.py tidy [--apply] [--all]  # retire finished worktrees (session, App-named, mts-relay-*; clean + fully on origin/fast-track + idle 24 h); dry run by default

Rules live in MyTradingSys/system/PARALLEL.md. The live tree (a checkout holding the gitignored marker
file .mts_live) is never synced or shipped from: the running system imports it, so it changes only by
the supervisor deploy (stop, ff-merge, gate, restart).
"""
import os
import re
import socket
import subprocess
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TRUNK = "fast-track"
LIVE_MARKER = ".mts_live"
DOC_SUFFIXES = (".md", ".txt")
PUSH_TRIES = 3
CLAIMS_DIR = "MyTradingSys/system/claims"
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
STRAY_UNTRACKED = ("AGENTS.md", ".codex/")


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


def merge_trunk(repo):
    """Fetch and merge origin/fast-track into HEAD (never rebase). Returns the commits pulled in.
    A conflict confined to TAKE_ORIGIN files is resolved to origin's text and reported; any other stops."""
    git(repo, "fetch", "--quiet", "origin", TRUNK)
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


def outgoing_files(repo):
    out = git(repo, "diff", "--name-only", f"origin/{TRUNK}...HEAD").stdout.split()
    return [f for f in out if f]


def needs_gate(files):
    return any(not f.endswith(DOC_SUFFIXES) for f in files)


def run_gate(repo):
    r = subprocess.run([sys.executable, "scripts/dev/run_all_tests.py", "--quick"], cwd=repo)
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


def new_worktree(repo, slug=None):
    host = socket.gethostname().lower()
    slug = slugify(slug) if slug else time.strftime("s%m%d-%H%M%S", time.gmtime())
    path = Path(repo).resolve().parent / f"mts-{host}-{slug}"
    n = 1
    while path.exists():
        n += 1
        path = path.with_name(f"mts-{host}-{slug}-{n}")
    branch = f"{host}/{slug}" + ("" if n == 1 else f"-{n}")
    git(repo, "fetch", "--quiet", "origin", TRUNK)
    git(repo, "worktree", "add", "-q", str(path), "-b", branch, f"origin/{TRUNK}")
    return path


def start(repo, slug=None, here=False):
    """Bring a tree up to date. Returns the tree the session must work in: `repo` when it is clean, else a
    fresh worktree off origin/fast-track (printed as `WORKTREE: <path>`); never touches the other files."""
    refuse_live(repo)
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
    print_claims(repo)
    pull_mirror(repo)
    return repo


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
        areas[slug] = [a.strip().rstrip("/") for a in re.split(r"[,\s]+", kv.get("area", "-")) if a.strip() not in ("", "-")]
    slugs = sorted(areas)
    for i, a in enumerate(slugs):
        for b in slugs[i + 1:]:
            hit = [(x, y) for x in areas[a] for y in areas[b] if x == y or x.startswith(y + "/") or y.startswith(x + "/")]
            if hit:
                issues.append(f"OVERLAP claims {a} / {b}: {hit[0][0]} ~ {hit[0][1]}")
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
        if short in (TRUNK, "HEAD", "origin", "main", "master") or short.startswith(("backup/", "green/", "claude/")):
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


def ship(repo, gate=run_gate):
    refuse_live(repo)  # only commits are pushed; uncommitted files stay where they are
    for attempt in range(1, PUSH_TRIES + 1):
        merge_trunk(repo)
        files = outgoing_files(repo)
        if not files:
            print("nothing to ship")
            return
        if attempt == 1 and needs_gate(files):
            gate(repo)
        r = git(repo, "push", "--quiet", "origin", f"HEAD:refs/heads/{TRUNK}", check=False)
        if r.returncode == 0:
            print(f"shipped {len(files)} file(s) to origin/{TRUNK}")
            return
        print(f"push rejected (someone shipped first), retry {attempt}/{PUSH_TRIES}")
    raise SyncError(f"push still rejected after {PUSH_TRIES} tries:\n{r.stderr}")


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


def claim(repo, task, area="-", gate=run_gate):
    if str(task).startswith("--"):
        raise SyncError(f"claim name {task!r} looks like a flag, not a task name; usage: sync.py claim \"<task>\" [--area <paths>]")
    refuse_live(repo)
    git(repo, "fetch", "--quiet", "origin", TRUNK)
    slug = slugify(task)
    existing = dict(read_claims(repo, f"origin/{TRUNK}"))
    if slug in existing:
        kv = existing[slug]
        raise SyncError(f"already claimed by {kv.get('host')} / {kv.get('account')}: {kv.get('task')}. Pick another task or ask them.")
    path = repo / CLAIMS_DIR / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    NL = chr(10)
    path.write_text(NL.join([f"task: {task}", f"host: {socket.gethostname()}", f"account: {account(repo)}",
                             f"area: {area}", f"epoch: {int(time.time())}", ""]), newline=chr(10))
    rel = f"{CLAIMS_DIR}/{slug}.md"  # relative: a 8.3 short temp path is "outside repository" to git
    git(repo, "add", rel)
    msg = NL.join([f"claim {slug}", "", f"Result: {account(repo)} on {socket.gethostname()} works on: {task}"])
    git(repo, "commit", "-q", "-m", msg, "--", rel)
    ship(repo, gate=gate)
    print(f"claimed {slug}; release with: sync.py release {slug}")


# Fixed lanes other tooling points at (dispatcher prompts, codex lab, push recipe): `tidy --all` still keeps them.
# mts-control-room is the working folder of the Claude routine mts-control-room (~/.claude/scheduled-tasks/mts-control-room/
# SKILL.md); it sits idle between runs, so without this `tidy --all` would remove it as hand-named.
LANE_WORKTREES = ("mts-push", "mts-refiner", "mts-codex-lab", "mts-codex", "mts-dsa", "mts-relay", "mts-control-room")


TIDY_IDLE_HOURS = 24
TIDY_KEEP_LINES = 10  # keep-reasons listed one per line; the rest only counted in the last line
QUIET_KEEPS = ("lane", "hand-named")  # decided by the name alone: counted, never listed
# Ignored paths that are rebuilt for free; anything else ignored (Dumps/, runtime_data/, fetched klines) is data.
# target/ = Maven build output; settings.local.json is an identical copy in every tree; control_room/ is generated HTML;
# ACCOUNT_DAILY_LOSS.jsonl is what the daily-loss tests write into a work tree's journal. _mirror (and its .lock/.tmp
# staging dirs) is the desktop live state, re-pulled by `sync.py start` / `live_mirror.py brief`; .pytest_tmp/ and .codex/
# are test-runner and tool droppings. All three are in .gitignore, so `status --ignored` lists them in every tree.
REGENERABLE = ("__pycache__/", ".pytest_cache/", ".pyc", " target/", ".claude/settings.local.json", "runtime_data/control_room/",
               "journal/ACCOUNT_DAILY_LOSS.jsonl", "runtime_data/_mirror", ".pytest_tmp/", ".codex/")


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


def release(repo, slug, gate=run_gate):
    refuse_live(repo)
    merge_trunk(repo)
    path = repo / CLAIMS_DIR / f"{slug}.md"
    if not path.exists():
        raise SyncError(f"no claim {slug} on origin/{TRUNK}")
    rel = f"{CLAIMS_DIR}/{slug}.md"
    git(repo, "rm", "-q", rel)
    git(repo, "commit", "-q", "-m", f"release {slug}"+chr(10)*2+f"Result: claim {slug} closed", "--", rel)
    ship(repo, gate=gate)
    print(f"released {slug}")


def main(argv):
    cmds = {"start": start, "ship": ship, "news": news, "claims": print_claims, "health": health}
    extra = {"claim", "release"}
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
                claim(repo, argv[1], area)
        except SyncError as e:
            print(f"sync: {e}", file=sys.stderr)
            return 1
        return 0
    if argv and argv[0] == "start" and len(argv) <= 3:
        try:
            here = "--here" in argv
            rest = [a for a in argv[1:] if a != "--here"]
            start(toplevel(Path.cwd()), rest[0] if rest else None, here)
        except SyncError as e:
            print(f"sync: {e}", file=sys.stderr)
            return 1
        return 0
    if not argv or argv[0] not in cmds or (argv[0] != "news" and len(argv) != 1):
        print(__doc__)
        return 2
    try:
        repo = toplevel(Path.cwd())
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
