"""refresh_main_checkout.py: bring a stale primary checkout up to origin/fast-track without losing anything.

Usage (run from any tree; the target is --repo, default the repo this file lives in):
  python scripts/dev/refresh_main_checkout.py [--repo PATH] [--branch fast-track] [--wip-branch NAME]
        dry run (default): lists dirty/staged/untracked files, the wip branch check, what each step WOULD do
  ... --apply             act: named stash -> merge --ff-only origin/<branch> -> stash pop --index -> post steps
  ... --apply --merge-if-diverged   when ff-only is impossible (local-only commits, all kept on the wip branch):
                          plain `git merge origin/<branch>` (never rebase/reset); a conflicting merge is aborted.
  --no-fetch              skip `git fetch origin` (tests); --no-post: skip c_drive_guard/wt_maint (tests)
Never rebases, resets, force-pushes or deletes. A stash that cannot be popped cleanly stays in the stash list
(named `refresh-main-<utc>`) and is reported; nothing is dropped. Post steps (after a clean refresh, run from the
refreshed tree): c_drive_guard.py install, status; wt_maint.py; then the ack line is printed for the operator.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ACK_LINE = "python scripts/dev/mts_signal.py ack b-4c2dfe done"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def classify(porcelain):
    """-> (staged, unstaged, untracked) lists of paths from `git status --porcelain`."""
    staged, unstaged, untracked = [], [], []
    for line in porcelain.splitlines():
        if len(line) < 4:
            continue
        x, y, path = line[0], line[1], line[3:]
        if x == "?" and y == "?":
            untracked.append(path)
            continue
        if x not in " ?":
            staged.append(path)
        if y not in " ?":
            unstaged.append(path)
    return staged, unstaged, untracked


def is_ancestor(repo, a, b):
    return git(repo, "merge-base", "--is-ancestor", a, b).returncode == 0


def _pop_hint(say, stash):
    if stash:
        say(f"your dirty work is safe in stash '{stash}': git stash pop --index (after resolving)")


def refresh(repo, branch="fast-track", wip_branch=None, apply=False, merge_if_diverged=False, fetch=True, say=print):
    """Return (ok, stash_name_or_None). Every decision is said; nothing is destroyed."""
    repo = Path(repo)
    say(f"refresh_main_checkout [{'APPLY' if apply else 'DRY-RUN'}] repo={repo}")
    cur = git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if cur != branch:
        say(f"STOP: checked out branch is '{cur}', expected '{branch}'. Nothing changed.")
        return False, None
    if fetch:
        f = git(repo, "fetch", "origin")
        if f.returncode:
            say(f"STOP: git fetch origin failed: {f.stderr.strip()}")
            return False, None
    remote = f"origin/{branch}"
    if git(repo, "rev-parse", "--verify", "-q", remote).returncode:
        say(f"STOP: {remote} does not exist.")
        return False, None
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    behind = git(repo, "rev-list", "--count", f"HEAD..{remote}").stdout.strip()
    ahead = git(repo, "rev-list", "--count", f"{remote}..HEAD").stdout.strip()
    say(f"HEAD {head[:9]}: {behind} behind, {ahead} ahead of {remote}")

    staged, unstaged, untracked = classify(git(repo, "status", "--porcelain").stdout)
    for label, items in (("staged", staged), ("unstaged", unstaged), ("untracked", untracked)):
        say(f"{label}: {len(items)}")
        for p in items[:15]:
            say(f"   {p}")
        if len(items) > 15:
            say(f"   ... +{len(items) - 15} more")

    diverged = ahead != "0"
    if diverged:
        if not wip_branch:
            say(f"STOP: {ahead} local-only commit(s) and no --wip-branch given to prove they are preserved.")
            return False, None
        if git(repo, "rev-parse", "--verify", "-q", wip_branch).returncode:
            say(f"STOP: wip branch '{wip_branch}' does not exist; local-only commits would be unprotected.")
            return False, None
        if not is_ancestor(repo, "HEAD", wip_branch):
            say(f"STOP: HEAD {head[:9]} is not contained in '{wip_branch}'; commit it there first.")
            return False, None
        say(f"wip branch '{wip_branch}' contains HEAD: local-only commits are preserved")
        if not merge_if_diverged:
            say("NOTE: ff-only will fail (diverged); add --merge-if-diverged to merge instead.")
    elif wip_branch and git(repo, "rev-parse", "--verify", "-q", wip_branch).returncode:
        say(f"note: wip branch '{wip_branch}' not found (no local-only commits, so nothing depends on it)")

    dirty = bool(staged or unstaged or untracked)
    stash = ("refresh-main-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())) if dirty else None
    if not apply:
        if stash:
            say(f"WOULD: git stash push -u -m {stash}")
        say(f"WOULD: git merge --ff-only {remote}" + (f" (else git merge {remote})" if merge_if_diverged else ""))
        if stash:
            say("WOULD: git stash pop --index (conflicts: stash kept, reported)")
        say("WOULD: c_drive_guard.py install, c_drive_guard.py status, wt_maint.py; then run:")
        say(ACK_LINE)
        say("dry run only; add --apply to act.")
        return True, stash

    if dirty:
        s = git(repo, "stash", "push", "-u", "-m", stash)
        if s.returncode or "No local changes" in s.stdout:
            say(f"STOP: stash failed: {(s.stderr or s.stdout).strip()}")
            return False, None
        say(f"stashed dirty work as '{stash}' (kept until popped cleanly)")

    m = git(repo, "merge", "--ff-only", remote)
    if m.returncode:
        if diverged and merge_if_diverged:
            m = git(repo, "merge", "--no-edit", remote)
            if m.returncode:
                git(repo, "merge", "--abort")
                say(f"merge conflicted and was aborted; tree unchanged. {m.stdout.strip()[-300:]}")
                _pop_hint(say, stash)
                return False, stash
            say(f"merged {remote} (diverged; local commits kept on '{wip_branch}')")
        else:
            say(f"ff-only impossible: {m.stderr.strip() or m.stdout.strip()}")
            _pop_hint(say, stash)
            return False, stash
    else:
        say(f"fast-forwarded to {git(repo, 'rev-parse', '--short', 'HEAD').stdout.strip()}")

    if stash:
        p = git(repo, "stash", "pop", "--index")
        if p.returncode:
            say("stash pop hit conflicts/overlaps; the stash is KEPT, nothing lost:")
            say("   " + (p.stderr.strip() or p.stdout.strip())[:600].replace("\n", "\n   "))
            say(f"   inspect: git -C {repo} stash list ; git -C {repo} stash show -p stash@{{0}}")
            return False, stash
        say(f"stash '{stash}' popped cleanly")
    return True, stash


def post_steps(repo, say=print):
    ok = True
    for args in (["scripts/dev/c_drive_guard.py", "install"], ["scripts/dev/c_drive_guard.py", "status"],
                 ["scripts/dev/wt_maint.py"]):
        say("run: python " + " ".join(args))
        r = subprocess.run([sys.executable, *args], cwd=str(repo), capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        out = (r.stdout + r.stderr).strip()
        say("   " + out[-1500:].replace("\n", "\n   ") if out else "   (no output)")
        if r.returncode:
            say(f"   exit {r.returncode}")
            ok = False
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--branch", default="fast-track")
    ap.add_argument("--wip-branch", default=None)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--merge-if-diverged", action="store_true")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--no-post", action="store_true")
    a = ap.parse_args(argv)
    ok, _ = refresh(a.repo, a.branch, a.wip_branch, a.apply, a.merge_if_diverged, not a.no_fetch)
    if not ok:
        return 1
    if a.apply:
        if not a.no_post:
            post_steps(a.repo)
        print(ACK_LINE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
