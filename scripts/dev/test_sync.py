"""sync.py: two clones of one origin ship to fast-track without losing each other's work."""
import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync


def sh(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def commit(repo, name, text):
    (repo / name).write_text(text, newline="\n")
    sh(repo, "add", name)
    sh(repo, "commit", "-q", "-m", name)


class SyncTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        origin = self.tmp / "origin.git"
        sh(self.tmp, "init", "-q", "--bare", str(origin))
        sh(origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")  # git < 2.28 has no init -b
        self.a, self.b = self.tmp / "a", self.tmp / "b"
        for c in (self.a, self.b):
            sh(self.tmp, "clone", "-q", str(origin), str(c))
            sh(c, "config", "user.email", "t@t")
            sh(c, "config", "user.name", "t")
        commit(self.a, "README.md", "x\n")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        sh(self.b, "pull", "-q", "origin", "fast-track")
        self.gated = []

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def gate(self, repo):
        self.gated.append(repo)

    def head_files(self, repo):
        sh(repo, "fetch", "-q", "origin")
        r = subprocess.run(["git", "ls-tree", "--name-only", "origin/fast-track"], cwd=repo,
                           capture_output=True, text=True)
        return set(r.stdout.split())

    def test_concurrent_ships_both_land(self):
        commit(self.a, "a.py", "a\n")
        commit(self.b, "b.py", "b\n")
        sync.ship(self.a, gate=self.gate)
        sync.ship(self.b, gate=self.gate)  # b is behind: must merge, not fail or overwrite
        self.assertEqual(self.head_files(self.a), {"README.md", "a.py", "b.py"})

    def test_docs_only_skips_gate_code_runs_it(self):
        commit(self.a, "NOTE.md", "n\n")
        sync.ship(self.a, gate=self.gate)
        self.assertEqual(self.gated, [])
        commit(self.a, "c.py", "c\n")
        sync.ship(self.a, gate=self.gate)
        self.assertEqual(self.gated, [self.a])

    def test_live_tree_refused(self):
        (self.a / sync.LIVE_MARKER).write_text("", newline="\n")
        with self.assertRaises(sync.SyncError):
            sync.start(self.a)
        with self.assertRaises(sync.SyncError):
            sync.ship(self.a, gate=self.gate)

    def test_other_sessions_uncommitted_work_does_not_block(self):
        (self.a / "README.md").write_text("half-done by another session\n", newline="\n")
        commit(self.a, "mine.py", "m\n")
        commit(self.b, "theirs.py", "t\n")
        sync.ship(self.b, gate=self.gate)
        sync.ship(self.a, gate=self.gate)  # merges theirs.py, pushes mine.py, leaves README.md alone
        self.assertEqual(self.head_files(self.a), {"README.md", "mine.py", "theirs.py"})
        self.assertEqual((self.a / "README.md").read_text(), "half-done by another session\n")

    def test_news_shows_result_line_not_code(self):
        (self.a / "f.py").write_text("x\n", newline="\n")
        sh(self.a, "add", "f.py")
        sh(self.a, "commit", "-q", "-m", "Tom alerts fire on 3m", "-m", "Result: 4 alerts in 2h replay")
        sync.ship(self.a, gate=self.gate)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sync.news(self.b)
        self.assertIn("Tom alerts fire on 3m", buf.getvalue())
        self.assertIn("Result: 4 alerts in 2h replay", buf.getvalue())

    def test_failed_gate_pushes_nothing(self):
        commit(self.a, "bad.py", "x\n")

        def fail(repo):
            raise sync.SyncError("gate")
        with self.assertRaises(sync.SyncError):
            sync.ship(self.a, gate=fail)
        self.assertNotIn("bad.py", self.head_files(self.b))

    def test_start_pulls_others_work(self):
        commit(self.a, "a.py", "a\n")
        sync.ship(self.a, gate=self.gate)
        sync.start(self.b)
        self.assertTrue((self.b / "a.py").exists())


if __name__ == "__main__":
    unittest.main()
