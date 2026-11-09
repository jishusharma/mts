#!/usr/bin/env python3
"""Tests for conflict_marker_lint.py: a tracked text file with a '<<<<<<< ' or '>>>>>>> ' line start fails the gate (exit 1, file:line).

    python scripts/dev/test_conflict_marker_lint.py

Card ship-gate-refuses-committed-merge-confli (PLAN_API_CREDITS had marker rows on trunk 2026-11-06; the 8dbd7408f revert put markers in
5 task cards). Fixtures are written into a throwaway git repo and the markers are built with "<" * 7, so this file never has a marker line.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LINT = Path(__file__).resolve().parent / "conflict_marker_lint.py"
OURS = "<" * 7 + " HEAD"
THEIRS = ">" * 7 + " abc1234 (some commit)"
SEP = "=" * 7


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def make_repo(files, untracked=None):
    """A temp git repo whose tracked files are {relpath: bytes}; untracked likewise (not added)."""
    d = tempfile.TemporaryDirectory()
    root = Path(d.name)
    git(root, "init", "-q")
    for rel, data in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    git(root, "add", "-A")
    for rel, data in (untracked or {}).items():
        (root / rel).write_bytes(data)
    return d, root


def run_lint(root):
    r = subprocess.run([sys.executable, str(LINT), "--root", str(root)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


class ConflictMarkerLint(unittest.TestCase):
    def test_marker_line_fails_and_names_file_line(self):
        text = f"a,b\n{OURS}\nx,1\n{SEP}\nx,2\n{THEIRS}\nc,d\n".encode()
        d, root = make_repo({"docs/PLAN_API_CREDITS.md": text})
        with d:
            code, out = run_lint(root)
        self.assertEqual(code, 1, out)
        self.assertIn("docs/PLAN_API_CREDITS.md:2", out)
        self.assertIn("docs/PLAN_API_CREDITS.md:6", out)

    def test_clean_tree_passes(self):
        d, root = make_repo({"a.md": b"hello\n", "b.py": b"x = 1\n"})
        with d:
            code, out = run_lint(root)
        self.assertEqual(code, 0, out)

    def test_only_line_start_with_trailing_space_counts(self):
        # prose that mentions the marker, an indented marker, a bare 7-char run and a longer run are not conflicts
        lines = [f"see '{OURS}' in the log", f"  {OURS}", "<" * 7, "<" * 8 + " x", ">" * 7 + "x"]
        d, root = make_repo({"a.md": ("\n".join(lines) + "\n").encode()})
        with d:
            code, out = run_lint(root)
        self.assertEqual(code, 0, out)

    def test_binary_file_is_skipped(self):
        d, root = make_repo({"img.bin": b"\x00\x01\x02\n" + OURS.encode() + b"\n"})
        with d:
            code, out = run_lint(root)
        self.assertEqual(code, 0, out)

    def test_untracked_file_is_not_scanned(self):
        d, root = make_repo({"a.md": b"ok\n"}, untracked={"scratch.md": (OURS + "\n").encode()})
        with d:
            code, out = run_lint(root)
        self.assertEqual(code, 0, out)

    def test_own_test_fixtures_are_skipped(self):
        d, root = make_repo({"scripts/dev/test_conflict_marker_lint.py": (OURS + "\n").encode(),
                             "scripts/dev/conflict_marker_lint.py": (THEIRS + "\n").encode()})
        with d:
            code, out = run_lint(root)
        self.assertEqual(code, 0, out)

    def test_crlf_and_non_utf8_text_still_scanned(self):
        d, root = make_repo({"w.md": b"a\r\n" + OURS.encode() + b"\r\nb\xff\r\n"})
        with d:
            code, out = run_lint(root)
        self.assertEqual(code, 1, out)
        self.assertIn("w.md:2", out)

    def test_real_tree_is_scanned_without_crash(self):
        # the live worktree: exit 0 (clean) or 1 (names offenders), never a traceback
        r = subprocess.run([sys.executable, str(LINT)], capture_output=True, text=True)
        self.assertIn(r.returncode, (0, 1), r.stderr)
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
