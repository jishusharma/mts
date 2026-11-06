"""sync.commit_pending must refuse to commit when HEAD does not resolve (orphan initial commit, 11-06 gq-leftovers-b)."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync


def sh(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def count(repo):
    r = subprocess.run(["git", "-C", repo, "rev-list", "--all", "--count"], capture_output=True, text=True)
    return r.stdout.strip()


class OrphanCommit(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        sh(self.d, "init", "-q")
        sh(self.d, "config", "user.email", "t@t")
        sh(self.d, "config", "user.name", "t")

    def test_unborn_head_route_tag_refuses(self):
        with self.assertRaises(sync.SyncError):
            sync.commit_pending(self.d, None, nxt="END: test")
        self.assertEqual(count(self.d), "0")

    def test_unborn_head_result_commit_refuses(self):
        (Path(self.d) / "a.txt").write_text("x")
        with self.assertRaises(sync.SyncError):
            sync.commit_pending(self.d, "works", nxt="END: test")
        self.assertEqual(count(self.d), "0")

    def test_normal_route_tag_commits(self):
        (Path(self.d) / "a.txt").write_text("x")
        sh(self.d, "add", "-A")
        sh(self.d, "commit", "-q", "-m", "base")
        sync.commit_pending(self.d, None, nxt="END: test")
        self.assertEqual(count(self.d), "2")


if __name__ == "__main__":
    unittest.main()
