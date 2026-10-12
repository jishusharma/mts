"""One way for any session on any machine to share work: origin/fast-track is the only meeting point.

  python scripts/dev/sync.py start [slug]  # up to date with origin/fast-track; in a shared/dirty tree makes your own worktree
  python scripts/dev/sync.py health  # stale/overlapping claims, shared or orphan worktrees, branches never shipped
  python scripts/dev/sync.py ship    # merge origin/fast-track, gate, push HEAD to origin/fast-track
  python scripts/dev/sync.py news [hours=24]  # what shipped: feature + Result line per commit, no code
  python scripts/dev/sync.py claim "<task>" [--area <paths>]  # tell parallel sessions what you work on (shipped at once)
  python scripts/dev/sync.py claims  # open claims on origin/fast-track (host, account, task, age); release: `release <slug>`
  python scripts/dev/sync.py where   # every worktree: commits not on origin/fast-track, uncommitted files (nothing lost?)
  python scripts/dev/sync.py tidy [--apply] [--all]  # retire finished session worktrees (clean + fully on origin/fast-track); dry run by default

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


class SyncError(Exception):
    pass


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SyncError(f"git {' '.join(args)} failed:\n{r.stdout}{r.stderr}".rstrip())
    return r


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
        if r.returncode != 0:
            bad = git(repo, "diff", "--name-only", "--diff-filter=U").stdout.split()
            if not bad or any(f not in TAKE_ORIGIN for f in bad):
                raise SyncError(
                    f"merge of origin/{TRUNK} conflicts; resolve, `git commit`, then run ship again.\n{r.stdout}")
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
    dirty = [l for l in git(repo, "status", "--short").stdout.splitlines() if l]
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
    for path, branch in worktrees(repo):
        p = Path(path)
        if not p.exists():
            issues.append(f"ORPHAN worktree {p.name}: folder gone (git worktree prune)")
            continue
        if (p / LIVE_MARKER).exists():
            continue
        reason = shared_tree_reason(p)
        if reason and branch in (TRUNK, "master", "main"):
            issues.append(f"SHARED {p.name} [{branch}]: sessions work on the trunk branch here; {reason}")
        elif reason:
            issues.append(f"UNSHIPPED {p.name} [{branch}]: {reason}")
    rows = git(repo, "for-each-ref", "refs/remotes/origin", "--format=%(refname:short)|%(committerdate:unix)").stdout.splitlines()
    for row in rows:
        ref, _, ts = row.partition("|")
        short = ref.removeprefix("origin/")
        if short in (TRUNK, "HEAD", "origin", "main", "master") or short.startswith(("backup/", "green/", "claude/")):
            continue
        ahead = git(repo, "rev-list", "--count", f"origin/{TRUNK}..{ref}", check=False).stdout.strip()
        if ahead not in ("", "0") and ts and (now - int(ts)) / 3600 > NOT_SHIPPED_HOURS:
            issues.append(f"NEVER-SHIPPED branch {short}: {ahead} commit(s), last {(now - int(ts)) / 3600:.0f}h ago")
    for i in issues:
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


def where(repo):
    """Same-page check for any account or machine: what is shipped, and what is still only in a worktree."""
    git(repo, "fetch", "--quiet", "origin", TRUNK)
    tip = git(repo, "log", "-1", "--format=%h %ar %s", f"origin/{TRUNK}").stdout.strip()
    print(f"origin/{TRUNK}: {tip}")
    open_items = 0
    for path, branch in worktrees(repo):
        ahead = git(Path(path), "rev-list", "--count", f"origin/{TRUNK}..HEAD").stdout.strip()
        dirty = [l for l in git(Path(path), "status", "--short").stdout.splitlines() if l]
        tracked = sum(1 for l in dirty if not l.startswith("??"))
        flag = "ok" if ahead == "0" and not dirty else "UNSHIPPED"
        open_items += flag != "ok"
        print(f"{flag:9} {Path(path).name:28} [{branch}] unshipped-commits={ahead} modified={tracked} untracked={len(dirty) - tracked}")
    print(f"{open_items} worktree(s) hold work that is not on origin/{TRUNK}; commit and `sync.py ship` them (the live tree is shipped by its owners)")


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
LANE_WORKTREES = ("mts-push", "mts-refiner", "mts-codex-lab", "mts-codex", "mts-dsa", "mts-relay")


def tidy(repo, apply=False, include_named=False):
    """Retire finished session worktrees (`../mts-<host>-<slug>` made by `start`). Dry run unless apply.
    Removed only when: not the primary tree, not the one we are in, no live marker, clean, branch fully on
    origin/fast-track. Named lanes (mts-push, mts-codex-lab ...) and anything else are never touched.
    Returns the paths removed (or that would be)."""
    git(repo, "fetch", "--quiet", "origin", TRUNK)
    here = Path(repo).resolve()
    rows = worktrees(repo)
    out = []
    for path, branch in rows[1:]:
        p = Path(path).resolve()
        if p == here or not p.exists() or (p / LIVE_MARKER).exists():
            continue
        auto = re.match(r"mts-.+-s\d{4}-\d{6}(-\d+)?$", p.name) or p.name.startswith(f"mts-{socket.gethostname().lower()}-")
        if p.name in LANE_WORKTREES or not (auto or include_named):
            print(f"keep  {p.name}: named lane or hand-named (`tidy --all` includes hand-named ones)")
            continue
        if branch in ("(detached)", TRUNK, "master", "main"):
            print(f"keep  {p.name}: branch {branch}")
            continue
        if git(p, "status", "--porcelain", check=False).stdout.strip():
            print(f"keep  {p.name}: uncommitted files")
            continue
        if git(repo, "merge-base", "--is-ancestor", branch, f"origin/{TRUNK}", check=False).returncode != 0:
            print(f"keep  {p.name}: {branch} has commits not on origin/{TRUNK}")
            continue
        if apply:
            r = git(repo, "worktree", "remove", str(p), check=False)
            if r.returncode != 0:
                print(f"keep  {p.name}: remove failed ({r.stderr.strip()[:80]})")
                continue
            git(repo, "branch", "-d", branch, check=False)
        print(f"{'removed' if apply else 'would remove'}  {p.name} [{branch}]")
        out.append(str(p))
    if apply:
        git(repo, "worktree", "prune", check=False)
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
    cmds = {"start": start, "ship": ship, "news": news, "where": where, "claims": print_claims, "health": health}
    extra = {"claim", "release"}
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
