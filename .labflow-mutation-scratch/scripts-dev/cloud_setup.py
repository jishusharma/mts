#!/usr/bin/env python
"""cloud_setup.py - SessionStart hook for Claude Code cloud containers (no-op everywhere else).

On claude.ai/code containers (CLAUDE_CODE_REMOTE=true) the clone is fresh, often on a stale harness branch
and without pytest/numpy, so the offline gate reads 4 false FAILs. This hook:
  1. installs the gate's Python deps (same list as .github/workflows/ci.yml) when missing;
  2. fetches origin/fast-track + origin/green/fast-track;
  3. prints one block: current branch vs origin/fast-track, and the CI green line from make_status.py.
It never merges, resets or checks out: the session decides (PARALLEL.md: cloud harness branches open a PR into
fast-track, CI auto-merges it when green). Exit 0 always; a hook failure must not block the session.
"""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GATE_DEPS = ("pytest", "numpy", "pandas", "tzdata")   # same order as the pip line in .github/workflows/ci.yml (test_cloud_setup checks it)


def is_cloud(env=None):
    return (env if env is not None else os.environ).get("CLAUDE_CODE_REMOTE", "").lower() == "true"


def git(*args):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, timeout=120)
    return r.stdout.strip() if r.returncode == 0 else ""


def main(env=None):
    if not is_cloud(env):
        return 0
    lines = ["[CLOUD SETUP]"]
    missing = [m for m in GATE_DEPS if importlib.util.find_spec(m) is None]
    if missing:
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *missing], capture_output=True, text=True,
                           timeout=300)
        lines.append(f"pip install {' '.join(missing)}: {'ok' if r.returncode == 0 else 'FAILED ' + r.stderr[-200:]}")
    git("fetch", "-q", "origin", "fast-track", "green/fast-track")
    branch = git("branch", "--show-current") or "(detached)"
    counts = git("rev-list", "--left-right", "--count", "HEAD...origin/fast-track").split()
    if len(counts) == 2:
        lines.append(f"branch {branch}: {counts[0]} ahead, {counts[1]} behind origin/fast-track"
                     + (" - STALE: start from origin/fast-track before working" if counts[1] != "0" else ""))
    try:
        sys.path.insert(0, str(REPO / "scripts" / "dev"))
        import make_status
        lines.append(make_status.get_ci_line(cwd=str(REPO)))
    except Exception as e:  # never block the session on a status line
        lines.append(f"CI green: unavailable ({type(e).__name__})")
    lines.append("Ship from cloud: push the harness branch, open a PR into fast-track (CI auto-merges on green).")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[CLOUD SETUP] skipped: {type(e).__name__}: {e}")
        sys.exit(0)
