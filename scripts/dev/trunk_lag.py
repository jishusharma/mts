"""Trunk lag: tell a running session, at each operator prompt, when its tree has fallen behind trunk (operator 2026-10-22).

Operator 2026-10-22: "Claude always looks at the stale data ... sessions are not looking into the latest code." `sync.py start`
merges trunk once at boot; a session that then runs for hours reads code, docs and STATUS from that old base. Claude Code
UserPromptSubmit hook (.claude/settings.json): fetches origin/fast-track at most every FETCH_EVERY_S, counts the trunk commits
this tree lacks and, when the oldest of them landed more than LAG_S ago or MAX_BEHIND are missing, prints one line telling
the session to merge before it reads code or quotes state. Silent otherwise. Never raises, never blocks; skips the live tree.
Env: MTS_TRUNK_LAG=off disables.
Run by hand: python scripts/dev/trunk_lag.py check   (prints the line, or nothing)
"""
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nowin  # noqa: E402

nowin.install()

TRUNK = "fast-track"
FETCH_EVERY_S = 600
LAG_S = 3600
MAX_BEHIND = 30
STAMP = "mts_trunk_fetch"


def git(repo, *args, timeout=8):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=timeout)


def message(behind, oldest_age_s):
    """The warning line, or '' when the tree is close enough to trunk."""
    if behind <= 0 or (oldest_age_s < LAG_S and behind < MAX_BEHIND):
        return ""
    age = f"{oldest_age_s / 3600:.1f} h" if oldest_age_s >= 3600 else f"{oldest_age_s / 60:.0f} min"
    return (f"TRUNK LAG: this tree is {behind} commit(s) behind origin/{TRUNK}; the oldest one landed {age} ago. Code, docs, "
            f"cards and STATUS read here are that old. Run `git merge origin/{TRUNK}` (or `python scripts/dev/sync.py start "
            f"<slug>`) before reading code or quoting state.")


def lag(repo, now=None, fetch=True):
    """(commits behind origin/fast-track, age in s of the oldest of them); (0, 0) when unknown."""
    now = now or time.time()
    gd = git(repo, "rev-parse", "--absolute-git-dir").stdout.strip()
    if not gd:
        return 0, 0
    stamp = Path(gd) / STAMP
    if fetch:
        try:
            last = float(stamp.read_text().strip())
        except (OSError, ValueError):
            last = 0
        if now - last >= FETCH_EVERY_S:
            git(repo, "fetch", "--quiet", "origin", TRUNK)
            try:
                stamp.write_text(str(now), newline=chr(10))
            except OSError:
                pass
    out = git(repo, "log", "--format=%ct", f"HEAD..origin/{TRUNK}").stdout.split()
    if not out:
        return 0, 0
    return len(out), max(0, now - min(int(x) for x in out))


def check(repo=None, fetch=True):
    repo = Path(repo or os.getcwd())
    if ".mts_live" in repo.resolve().parts:
        return ""
    behind, age = lag(repo, fetch=fetch)
    return message(behind, age)


def main(argv):
    if os.environ.get("MTS_TRUNK_LAG", "").lower() == "off":
        return 0
    if argv[:1] in (["hook"], ["check"]):
        try:
            if argv[:1] == ["hook"]:
                sys.stdin.read()
            text = check()
        except Exception:
            return 0
        if text:
            print(text)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
