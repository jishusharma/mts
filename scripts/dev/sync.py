"""One way for any session on any machine to share work: origin/fast-track is the only meeting point.

  python scripts/dev/sync.py start   # bring this checkout up to date with origin/fast-track
  python scripts/dev/sync.py ship    # merge origin/fast-track, gate, push HEAD to origin/fast-track
  python scripts/dev/sync.py news [hours=24]  # what shipped: feature + Result line per commit, no code
  python scripts/dev/sync.py where   # every worktree: commits not on origin/fast-track, uncommitted files (nothing lost?)

Rules live in MyTradingSys/system/PARALLEL.md. The live tree (a checkout holding the gitignored marker
file .mts_live) is never synced or shipped from: the running system imports it, so it changes only by
the supervisor deploy (stop, ff-merge, gate, restart).
"""
import socket
import subprocess
import sys
from pathlib import Path

TRUNK = "fast-track"
LIVE_MARKER = ".mts_live"
DOC_SUFFIXES = (".md", ".txt")
PUSH_TRIES = 3


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
    """Fetch and merge origin/fast-track into HEAD (never rebase). Returns the commits pulled in."""
    git(repo, "fetch", "--quiet", "origin", TRUNK)
    incoming = git(repo, "rev-list", "--count", f"HEAD..origin/{TRUNK}").stdout.strip()
    if incoming != "0":
        r = git(repo, "merge", "--no-edit", f"origin/{TRUNK}", check=False)
        if r.returncode != 0:
            raise SyncError(
                f"merge of origin/{TRUNK} conflicts; resolve, `git commit`, then run ship again.\n{r.stdout}")
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


def start(repo):
    # Uncommitted files may be another session's work in progress: not ours to judge. git merge
    # refuses by itself only when an incoming commit touches one of them.
    refuse_live(repo)
    n = merge_trunk(repo)
    branch = git(repo, "branch", "--show-current").stdout.strip() or "(detached)"
    print(f"host={socket.gethostname()} branch={branch} pulled={n} head={git(repo, 'rev-parse', '--short', 'HEAD').stdout.strip()}")


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


def main(argv):
    cmds = {"start": start, "ship": ship, "news": news, "where": where}
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
