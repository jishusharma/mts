"""refresh_main_checkout.py error branches: temp repos only (never the real checkout).
Kept apart from test_refresh_main_checkout.py so each file fits the ship gate's per-step time ceiling."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import refresh_main_checkout as R

ENV = ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]


def g(cwd, *a):
    r = subprocess.run(["git", *ENV, "-C", str(cwd), *a], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def commit(repo, name, text=None):
    (Path(repo) / name).write_text(text or name, encoding="utf-8")
    g(repo, "add", name)
    g(repo, "commit", "-q", "-m", name)


class ErrorBranches(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        base = Path(self.td.name)
        self.origin, self.clone, self.up = base / "origin.git", base / "clone", base / "up"
        g(base, "init", "-q", "--bare", str(self.origin))
        g(self.origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")  # git < 2.28 has no init -b
        g(base, "clone", "-q", str(self.origin), str(self.clone))
        g(self.clone, "checkout", "-q", "-B", "fast-track")
        # the script under test runs bare `git merge`/`git stash` (no -c identity): give the clone its own
        # identity so the test does not depend on a global user.name/email (absent on some hosts).
        g(self.clone, "config", "user.name", "t")
        g(self.clone, "config", "user.email", "t@t")
        g(self.clone, "config", "commit.gpgsign", "false")
        commit(self.clone, "a.txt")
        g(self.clone, "push", "-q", "origin", "fast-track")
        g(base, "clone", "-q", str(self.origin), str(self.up))
        for n in ("b.txt", "c.txt"):
            commit(self.up, n)
        g(self.up, "push", "-q", "origin", "fast-track")
        self.out = []

    def tearDown(self):
        self.td.cleanup()

    def run_r(self, **kw):
        return R.refresh(self.clone, say=self.out.append, **kw)

    def text(self):
        return "\n".join(self.out)

    # ---- error branches: each test fails if the matching guard in refresh() is removed ----
    def test_wrong_branch_stops_untouched(self):
        g(self.clone, "checkout", "-q", "-b", "other")
        ok, stash = self.run_r(apply=True)
        self.assertFalse(ok)
        self.assertIsNone(stash)
        self.assertIn("expected 'fast-track'", self.text())
        self.assertEqual(g(self.clone, "rev-parse", "--abbrev-ref", "HEAD"), "other")

    def test_fetch_failure_stops(self):
        g(self.clone, "remote", "set-url", "origin", str(self.clone.parent / "nope.git"))
        (self.clone / "dirty.txt").write_text("x")
        ok, stash = self.run_r(apply=True)
        self.assertFalse(ok)
        self.assertIsNone(stash)
        self.assertIn("git fetch origin failed", self.text())
        self.assertEqual(g(self.clone, "stash", "list"), "")
        self.assertEqual((self.clone / "dirty.txt").read_text(), "x")

    def test_stash_failure_stops_before_merge(self):
        (self.clone / "dirty.txt").write_text("x")
        head = g(self.clone, "rev-parse", "HEAD")
        (self.clone / ".git" / "index.lock").write_text("")  # stash cannot take the index lock
        ok, stash = self.run_r(apply=True)
        self.assertFalse(ok)
        self.assertIsNone(stash)
        self.assertIn("stash failed", self.text())
        self.assertEqual(g(self.clone, "rev-parse", "HEAD"), head)
        self.assertEqual((self.clone / "dirty.txt").read_text(), "x")

    def test_merge_conflict_is_aborted_tree_unchanged(self):
        commit(self.clone, "b.txt", "local-b")  # origin also adds b.txt: add/add conflict
        g(self.clone, "branch", "wip/x")
        head = g(self.clone, "rev-parse", "HEAD")
        (self.clone / "dirty.txt").write_text("x")
        ok, stash = self.run_r(apply=True, wip_branch="wip/x", merge_if_diverged=True)
        self.assertFalse(ok)
        self.assertIn("aborted", self.text())
        self.assertEqual(g(self.clone, "rev-parse", "HEAD"), head)
        self.assertFalse((self.clone / ".git" / "MERGE_HEAD").exists())
        self.assertEqual((self.clone / "b.txt").read_text(), "local-b")
        self.assertIn(stash, g(self.clone, "stash", "list"))  # dirty work kept, not dropped
        self.assertIn("git stash pop --index", self.text())

    def test_tracked_protected_changed_both_sides_keeps_local(self):
        (self.up / "MyTradingSys" / "execution").mkdir(parents=True)
        commit(self.up, "MyTradingSys/execution/HALT", "v1")
        g(self.up, "push", "-q", "origin", "fast-track")
        g(self.clone, "pull", "-q", "--ff-only", "origin", "fast-track")
        ex = self.clone / "MyTradingSys" / "execution"
        commit(self.up, "MyTradingSys/execution/HALT", "upstream-v2")
        g(self.up, "push", "-q", "origin", "fast-track")
        (ex / "HALT").write_text("local-halt")  # tracked + protected: never stashed, upstream also changed it
        head = g(self.clone, "rev-parse", "HEAD")
        ok, stash = self.run_r(apply=True)
        self.assertFalse(ok)
        self.assertIn("ff-only impossible", self.text())
        self.assertEqual((ex / "HALT").read_text(), "local-halt")
        self.assertEqual(g(self.clone, "rev-parse", "HEAD"), head)
        self.assertEqual(g(self.clone, "stash", "list"), "")

    def test_head_not_in_wip_branch_blocks(self):
        g(self.clone, "branch", "wip/old")  # wip points at the pre-local-commit tip
        commit(self.clone, "local.txt")
        head = g(self.clone, "rev-parse", "HEAD")
        ok, _ = self.run_r(apply=True, wip_branch="wip/old", merge_if_diverged=True)
        self.assertFalse(ok)
        self.assertIn("is not contained in 'wip/old'", self.text())
        self.assertEqual(g(self.clone, "rev-parse", "HEAD"), head)


if __name__ == "__main__":
    unittest.main()
