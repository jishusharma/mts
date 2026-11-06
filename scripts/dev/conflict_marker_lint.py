#!/usr/bin/env python3
"""conflict_marker_lint.py - no tracked text file may contain a committed merge-conflict marker.

    python scripts/dev/conflict_marker_lint.py [--root <repo>]

A line that starts with seven '<' or seven '>' characters and a space (the way git writes them) in any file from `git ls-files`
is an unresolved merge. Exit 1 and print `path:line: text` for each; exit 0 when none. Binary files (a NUL byte in the first 8000 bytes)
are skipped, and so are this lint and its own test (they must spell the markers). Untracked files are not scanned.

Why (card ship-gate-refuses-committed-merge-confli): PLAN_API_CREDITS had `<<<<<<< HEAD` rows on trunk 2026-11-06, and the 8dbd7408f
revert put markers in 5 task cards; nothing in the gate looked. Twin: revert-leaves-conflict-markers.
"""
import argparse
import subprocess
import sys
from pathlib import Path

MARKERS = ("<" * 7 + " ", ">" * 7 + " ")
SKIP = ("scripts/dev/conflict_marker_lint.py", "scripts/dev/test_conflict_marker_lint.py")
SNIFF = 8000


def tracked_files(root):
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True).stdout
    return [p for p in out.decode("utf-8", "replace").split("\0") if p]


def scan_bytes(data):
    """[(line number, text)] of the marker lines in a file's bytes; [] for a binary file."""
    if b"\0" in data[:SNIFF]:
        return []
    hits = []
    for n, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
        if line.startswith(MARKERS):
            hits.append((n, line))
    return hits


def scan(root):
    """[(path, line number, text)] over every tracked file under root."""
    root = Path(root)
    found = []
    for rel in tracked_files(root):
        if rel in SKIP:
            continue
        try:
            data = (root / rel).read_bytes()
        except OSError:
            continue   # tracked but deleted in the work tree, a symlink to nowhere, a submodule dir
        found += [(rel, n, t) for n, t in scan_bytes(data)]
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]), help="git work tree to scan (default: this repo)")
    args = ap.parse_args(argv)
    hits = scan(args.root)
    for rel, n, text in hits:
        print(f"{rel}:{n}: {text[:100]}")
    if hits:
        print(f"conflict_marker_lint: FAIL {len(hits)} merge-conflict marker line(s) in {len({h[0] for h in hits})} tracked file(s); resolve them")
        return 1
    print("conflict_marker_lint: OK no merge-conflict markers in tracked text files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
