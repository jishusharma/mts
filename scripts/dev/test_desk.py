"""desk.py: post -> take -> done across two clones, wait reads origin, finished tasks cannot be reopened."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import desk


def sh(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


class DeskTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        origin = self.tmp / "origin.git"
        sh(self.tmp, "init", "-q", "--bare", str(origin))
        sh(origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")
        self.a, self.b = self.tmp / "a", self.tmp / "b"
        for c in (self.a, self.b):
            sh(self.tmp, "clone", "-q", str(origin), str(c))
            sh(c, "config", "user.email", "t@t")
            sh(c, "config", "user.name", "t")
        (self.a / "README.md").write_text("x\n")
        sh(self.a, "add", "."), sh(self.a, "commit", "-q", "-m", "init")
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        sh(self.b, "pull", "-q", "origin", "fast-track")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_round_trip(self):
        rid = desk.post(self.a, "Copy klines", "copy F:/MTS/data/x to NUC", "file exists", ship=False)
        sh(self.a, "push", "-q", "origin", "HEAD:fast-track")
        self.assertIsNone(desk.wait(self.a, rid, timeout=0.3, poll=0.1))  # still open
        sh(self.b, "pull", "-q", "origin", "fast-track")
        self.assertEqual([t["status"] for t in desk.tasks(self.b)], ["pending"])
        desk.take(self.b, rid, ship=False)
        with self.assertRaises(SystemExit):
            desk.take(self.b, rid, ship=False)  # already taken
        desk.finish(self.b, rid, "copied 2 files", ship=False)
        sh(self.b, "push", "-q", "origin", "HEAD:fast-track")
        got = desk.wait(self.a, rid, timeout=5, poll=0.1)  # a never pulled: reads origin directly
        self.assertEqual((got["status"], got["result"]), ("done", "copied 2 files"))
        with self.assertRaises(SystemExit):
            desk.finish(self.b, rid, "again", ship=False)

    def test_declined_task_raises_operator_line(self):
        rid = desk.post(self.a, "Restart runner", "restart alert runner", "running", ship=False)
        desk.finish(self.a, rid, "declined: restarts are supervisor-only", failed=True, ship=False)
        msg = subprocess.run(["git", "log", "-1", "--format=%B"], cwd=self.a, capture_output=True, text=True).stdout
        self.assertIn("Operator: desk task", msg)
        self.assertEqual(desk.tasks(self.a)[0]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
