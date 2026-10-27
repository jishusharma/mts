"""desk.py post returns the id of an open (pending/taken) row with the same title and target instead of
queueing a second one (traffic.py desk_rows_posted_twice, 2026-10-23)."""
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import desk  # noqa: E402


class PostOnceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=self.repo, check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def rows(self):
        return desk.tasks(self.repo)

    def test_same_open_title_posts_once(self):
        a = desk.post(str(self.repo), "Run X", "n", "d", ship=False)
        time.sleep(1.1)
        b = desk.post(str(self.repo), "run x", "n", "d", ship=False)
        self.assertEqual(a, b)
        self.assertEqual(len(self.rows()), 1)

    def test_other_target_or_closed_row_posts_again(self):
        a = desk.post(str(self.repo), "Run Y", "n", "d", target="DSA", ship=False)
        time.sleep(1.1)
        b = desk.post(str(self.repo), "Run Y", "n", "d", target="JIS-NB", ship=False)
        self.assertNotEqual(a, b)
        row = desk.get(self.repo, a)
        row["status"] = "done"
        desk.save(self.repo, row)
        time.sleep(1.1)
        c = desk.post(str(self.repo), "Run Y", "n", "d", target="DSA", ship=False)
        self.assertNotIn(c, (a, b))


if __name__ == "__main__":
    unittest.main()
