"""Revert the commit that turned fast-track CI red (CLAUDE.md Boot 2: revert within 10 min, never forward-fix trunk).

    python scripts/dev/ci_revert.py           dry run: print the plan (or why it refuses), change nothing
    python scripts/dev/ci_revert.py --apply   git revert it in THIS worktree, then sync.py ship --fix-ci

The breaking commit = the first red run of the streak trunk is still in (mts_doctor.first_red_sha over ci_fetch). Refuses, printing
the manual steps, when that commit is a merge, is not on origin/fast-track, or later trunk commits touch the same files (a revert
would undo or clash with them: a person decides). Never forces, rebases or resets; run by hand only, never scheduled or hooked
(SCHEDULING_POLICY.md). A revert conflict runs git revert --abort and leaves the tree as it was.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mts_doctor as D

TRUNK = "origin/fast-track"
REFUSED = 2
SHIP_CMD = [sys.executable, "scripts/dev/sync.py", "ship", "--fix-ci"]   # pure revert: sync.pure_revert skips the local gate


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def refusal(repo, sha):
    """None when sha is safe to revert alone, else the reason."""
    if _git(repo, "merge-base", "--is-ancestor", sha, TRUNK).returncode != 0:
        return f"{sha[:8]} is not on {TRUNK}"
    if len(_git(repo, "rev-list", "--parents", "-n", "1", sha).stdout.split()) > 2:
        return f"{sha[:8]} is a merge commit (revert by hand: git revert -m 1 {sha})"
    files = [f for f in _git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", sha).stdout.splitlines() if f]
    later = [f for f in _git(repo, "diff", "--name-only", sha, TRUNK, "--", *files).stdout.splitlines() if f] if files else []
    if later:
        return f"later commits on {TRUNK} touch the same files: {', '.join(later[:5])}"
    return None


def apply(repo, sha, ship):
    if _git(repo, "status", "--porcelain").stdout.strip():
        print("REFUSED: worktree has uncommitted changes; commit or ship them first")
        return REFUSED
    if _git(repo, "revert", "--no-commit", sha).returncode != 0:
        _git(repo, "revert", "--abort")
        print(f"REFUSED: revert of {sha[:8]} conflicts in this worktree; aborted, tree unchanged. Revert by hand: git revert {sha}")
        return REFUSED
    subj = _git(repo, "log", "-1", "--format=%s", sha).stdout.strip()
    msg = [f'Revert "{subj}"', f"This reverts commit {sha}.", f"Result: reverts {sha} (CI red)", "Next: END: trunk back to the last green code"]
    out = _git(repo, "commit", "--quiet", *[a for m in msg for a in ("-m", m)])
    if out.returncode != 0:
        _git(repo, "revert", "--abort")
        print(f"REFUSED: commit failed ({out.stderr.strip()[:120]}); aborted, tree unchanged")
        return REFUSED
    print(f"reverted {sha[:8]} as {_git(repo, 'rev-parse', '--short', 'HEAD').stdout.strip()}; shipping")
    return ship(repo)


def _ship(repo):
    return subprocess.run(SHIP_CMD, cwd=str(repo)).returncode


def main(argv=None, repo=None, runs=None, gated=None, ship=None):
    argv = sys.argv[1:] if argv is None else argv
    repo = Path(repo or Path.cwd())
    if runs is None:
        _git(repo, "fetch", "--quiet", "origin", "fast-track")
        runs = D.ci_fetch()
        if isinstance(runs, str):
            print(f"unavailable: GitHub API: {runs}")
            return 1
    sha = D.first_red_sha(runs, gated=gated or (lambda s: D.ci_gated(s, repo)))
    if not sha:
        print("trunk green: nothing to revert")
        return 0
    why = refusal(repo, sha)
    if why:
        print(f"REFUSED: {why}")
        print(f"manual: git -C <your worktree> revert {sha}; python scripts/dev/sync.py ship --fix-ci")
        return REFUSED
    print(f"PLAN: git revert --no-commit {sha}; commit 'Result: reverts {sha} (CI red)'; {' '.join(SHIP_CMD[1:])}")
    if "--apply" not in argv:
        print("dry run: nothing changed (add --apply)")
        return 0
    return apply(repo, sha, ship or _ship)


if __name__ == "__main__":
    sys.exit(main())
