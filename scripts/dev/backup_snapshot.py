"""Snapshot every worktree (committed + uncommitted + untracked) to origin/backup/<host>/<worktree>.

Why: a session that expires or a disk that dies must not lose work. Reads the working tree through a
temporary index, so it never touches the real index, the working files, stashes or branches, and it is safe
to run while other sessions edit (it is not a commit in anyone's history; backup refs are never merged).
Each run chains onto the previous backup commit (fast-forward pushes only, no force) and has the worktree
HEAD as second parent, so unpushed commits are reachable too. Unchanged trees are skipped.
Respects .gitignore; secrets-looking paths are dropped from the snapshot as well.

Usage: python scripts/dev/backup_snapshot.py [--repo DIR] [--remote origin] [--dry-run]
"""
import argparse
import os
import re
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

SECRET_PATHSPECS = [
    ":(glob)**/.secrets/**", ":(glob).secrets/**", ":(glob)**/.env", ":(glob).env",
    ":(glob)**/.env.*", ":(glob)**/*.pem", ":(glob)**/*.key", ":(glob)**/id_rsa*",
]


def git(args, cwd, env=None, check=True):
    e = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    if env:
        e.update(env)
    r = subprocess.run(["git"] + args, cwd=str(cwd), env=e, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        raise RuntimeError("git %s failed in %s: %s" % (" ".join(args), cwd, r.stderr.strip()))
    return r


def worktrees(repo):
    out = git(["worktree", "list", "--porcelain"], repo).stdout
    paths = []
    for line in out.splitlines():
        if line.startswith("worktree "):
            paths.append(Path(line[len("worktree "):]))
    return paths


def slug(text):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-") or "x"


def snapshot_tree(wt):
    """Tree sha of HEAD + every non-ignored file in the worktree, via a throwaway index."""
    with tempfile.TemporaryDirectory() as td:
        env = {"GIT_INDEX_FILE": str(Path(td) / "idx")}
        if git(["rev-parse", "--verify", "-q", "HEAD"], wt, check=False).returncode == 0:
            git(["read-tree", "HEAD"], wt, env)
        git(["add", "-A", "--", "."], wt, env)
        git(["rm", "-r", "--cached", "-q", "--ignore-unmatch", "--"] + SECRET_PATHSPECS, wt, env)
        return git(["write-tree"], wt, env).stdout.strip()


def backup_one(wt, remote, host, dry_run):
    name = slug(wt.name)
    ref = "refs/heads/backup/%s/%s" % (slug(host), name)
    local_ref = "refs/mts-backup/%s/%s" % (slug(host), name)
    tree = snapshot_tree(wt)
    prev = git(["rev-parse", "--verify", "-q", local_ref], wt, check=False).stdout.strip()
    if prev and git(["rev-parse", prev + "^{tree}"], wt).stdout.strip() == tree:
        return name, "unchanged"
    head = git(["rev-parse", "--verify", "-q", "HEAD"], wt, check=False).stdout.strip()
    parents = [p for p in (prev, head) if p]
    args = ["commit-tree", tree]
    for p in parents:
        args += ["-p", p]
    args += ["-m", "backup snapshot %s/%s (not for merge)" % (host, name)]
    commit = git(args, wt, {"GIT_AUTHOR_NAME": "mts-backup", "GIT_AUTHOR_EMAIL": "mts-backup@localhost",
                            "GIT_COMMITTER_NAME": "mts-backup", "GIT_COMMITTER_EMAIL": "mts-backup@localhost"}).stdout.strip()
    if dry_run:
        return name, "would push %s" % commit[:9]
    git(["push", "-q", remote, "%s:%s" % (commit, ref)], wt)
    git(["update-ref", local_ref, commit], wt)
    return name, "pushed %s" % commit[:9]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    repo = Path(a.repo)
    host = socket.gethostname()
    failed = 0
    for wt in worktrees(repo):
        if not wt.exists():
            continue
        try:
            name, what = backup_one(wt, a.remote, host, a.dry_run)
            print("%-28s %s" % (name, what))
        except Exception as exc:  # one broken worktree must not stop the others
            failed += 1
            print("%-28s FAILED %s" % (wt.name, exc), file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
