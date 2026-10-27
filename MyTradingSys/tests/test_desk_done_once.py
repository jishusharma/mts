"""desk.py take/finish re-read the row ON TRUNK (origin/fast-track) before committing: a row another writer already
closed there is refused even when the local copy is still pending (tc4-desk-done-once, 2026-10-18 triple close)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import desk  # noqa: E402


def git(repo, *args):
    import os
    e = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, env=e)
    assert r.returncode == 0, r.stderr
    return r.stdout


class DoneOnceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "checkout", "-q", "-b", "fast-track")
        self.row = {"id": "r1", "title": "t", "status": "pending"}
        desk.save(self.repo, self.row)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "row")

    def tearDown(self):
        self.tmp.cleanup()

    def trunk(self, status):
        r = dict(self.row, status=status)
        desk.save(self.repo, r)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "closed elsewhere")
        git(self.repo, "update-ref", "refs/remotes/origin/fast-track", "HEAD")
        desk.save(self.repo, self.row)  # local copy stays stale-pending

    def test_trunk_status(self):
        self.trunk("done")
        self.assertEqual(desk.trunk_status(self.repo, "r1"), "done")
        self.assertIsNone(desk.trunk_status(self.repo, "nope"))

    def test_finish_refused_when_trunk_closed(self):
        self.trunk("done")
        with self.assertRaises(SystemExit) as cm:
            desk.finish(str(self.repo), "r1", "again", ship=False)
        self.assertIn("already done", str(cm.exception))

    def test_take_refused_when_trunk_closed(self):
        self.trunk("failed")
        with self.assertRaises(SystemExit):
            desk.take(str(self.repo), "r1", ship=False)


if __name__ == "__main__":
    unittest.main()
