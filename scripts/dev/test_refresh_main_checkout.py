"""refresh_main_checkout.py: temp repos only (never the real checkout)."""
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


class T(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        base = Path(self.td.name)
        self.origin, self.clone, self.up = base / "origin.git", base / "clone", base / "up"
        g(base, "init", "-q", "--bare", str(self.origin))
        g(self.origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")  # git < 2.28 has no init -b
        g(base, "clone", "-q", str(self.origin), str(self.clone))
        g(self.clone, "checkout", "-q", "-B", "fast-track")
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

    def test_dry_run_changes_nothing(self):
        (self.clone / "dirty.txt").write_text("x")
        (self.clone / "a.txt").write_text("changed")
        head = g(self.clone, "rev-parse", "HEAD")
        ok, _ = self.run_r()
        self.assertTrue(ok)
        self.assertEqual(g(self.clone, "rev-parse", "HEAD"), head)
        self.assertEqual(g(self.clone, "stash", "list"), "")
        self.assertIn("untracked: 1", self.text())
        self.assertIn("unstaged: 1", self.text())
        self.assertIn("WOULD", self.text())
        self.assertIn(R.ACK_LINE, self.text())
        self.assertEqual((self.clone / "a.txt").read_text(), "changed")

    def test_apply_stashes_ffs_and_restores(self):
        (self.clone / "dirty.txt").write_text("x")
        (self.clone / "a.txt").write_text("changed")
        ok, _ = self.run_r(apply=True)
        self.assertTrue(ok, self.text())
        self.assertEqual(g(self.clone, "rev-parse", "HEAD"), g(self.up, "rev-parse", "HEAD"))
        self.assertEqual((self.clone / "dirty.txt").read_text(), "x")
        self.assertEqual((self.clone / "a.txt").read_text(), "changed")
        self.assertEqual(g(self.clone, "stash", "list"), "")

    def test_conflicting_pop_keeps_stash(self):
        # staged new file that origin also created with other content: pop cannot apply, stash must be kept
        (self.clone / "b.txt").write_text("mine")
        g(self.clone, "add", "b.txt")
        ok, stash = self.run_r(apply=True)
        self.assertFalse(ok)
        self.assertIn(stash, g(self.clone, "stash", "list"))
        self.assertIn("KEPT", self.text())

    def test_diverged_needs_wip_branch_and_never_resets(self):
        commit(self.clone, "local.txt")
        head = g(self.clone, "rev-parse", "HEAD")
        ok, _ = self.run_r(apply=True)
        self.assertFalse(ok)
        self.assertEqual(g(self.clone, "rev-parse", "HEAD"), head)
        g(self.clone, "branch", "wip/x")
        ok, _ = self.run_r(apply=True, wip_branch="wip/x")
        self.assertFalse(ok)
        self.assertEqual(g(self.clone, "rev-parse", "HEAD"), head)
        ok, _ = self.run_r(apply=True, wip_branch="wip/x", merge_if_diverged=True)
        self.assertTrue(ok, self.text())
        self.assertTrue(R.is_ancestor(self.clone, head, "HEAD"))
        self.assertTrue((self.clone / "c.txt").exists() and (self.clone / "local.txt").exists())

    def test_wip_branch_missing_blocks(self):
        commit(self.clone, "local.txt")
        ok, _ = self.run_r(apply=True, wip_branch="wip/nope")
        self.assertFalse(ok)
        self.assertIn("does not exist", self.text())

    def test_classify(self):
        s, u, t = R.classify("A  x\n M y\nMM z\n?? n\n D w\n")
        self.assertEqual((s, u, t), (["x", "z"], ["y", "z", "w"], ["n"]))

    def _protected_files(self):
        ex = self.clone / "MyTradingSys" / "execution"
        ex.mkdir(parents=True)
        (ex / "HALT").write_text("halt-me")
        (ex / "AUTO_PAUSE_x").write_text("pause")
        rt = self.clone / "MyTradingSys" / "runtime"
        rt.mkdir()
        (rt / "state.csv").write_text("s")
        return ex

    def test_dry_run_lists_protected(self):
        self._protected_files()
        (self.clone / "dirty.txt").write_text("x")
        ok, _ = self.run_r()
        self.assertTrue(ok)
        self.assertIn("PROTECTED (left in place): MyTradingSys/execution/AUTO_PAUSE_x, "
                      "MyTradingSys/execution/HALT, MyTradingSys/runtime/state.csv", self.text())
        self.assertIn("untracked: 1", self.text())

    def test_apply_never_stashes_protected_untracked(self):
        ex = self._protected_files()
        (self.clone / "dirty.txt").write_text("x")
        ok, _ = self.run_r(apply=True)
        self.assertTrue(ok, self.text())
        self.assertEqual((ex / "HALT").read_text(), "halt-me")
        self.assertEqual((ex / "AUTO_PAUSE_x").read_text(), "pause")
        self.assertEqual(g(self.clone, "stash", "list"), "")
        self.assertEqual((self.clone / "dirty.txt").read_text(), "x")

    def test_protected_present_while_stash_kept_after_conflict(self):
        ex = self._protected_files()
        (self.clone / "b.txt").write_text("mine")
        g(self.clone, "add", "b.txt")
        ok, stash = self.run_r(apply=True)
        self.assertFalse(ok)
        self.assertEqual((ex / "HALT").read_text(), "halt-me")
        self.assertNotIn("HALT", g(self.clone, "stash", "show", "--include-untracked", "--name-only", "stash@{0}"))

    def test_only_protected_dirty_means_no_stash(self):
        ex = self._protected_files()
        ok, stash = self.run_r(apply=True)
        self.assertTrue(ok, self.text())
        self.assertIsNone(stash)
        self.assertEqual((ex / "HALT").read_text(), "halt-me")

    def test_upstream_adding_same_protected_path_aborts_merge(self):
        (self.up / "MyTradingSys" / "execution").mkdir(parents=True)
        commit(self.up, "MyTradingSys/execution/HALT", "upstream")
        g(self.up, "push", "-q", "origin", "fast-track")
        ex = self.clone / "MyTradingSys" / "execution"
        ex.mkdir(parents=True)
        (ex / "HALT").write_text("local-halt")
        ok, _ = self.run_r(apply=True)
        self.assertFalse(ok)
        self.assertEqual((ex / "HALT").read_text(), "local-halt")

    def test_is_protected(self):
        for p in ("MyTradingSys/execution/HALT", "MyTradingSys/execution/HALT_DAILY_LOSS",
                  "MyTradingSys/execution/AUTO_PAUSE", "MyTradingSys/runtime/a/b.csv", ".mts_live/x"):
            self.assertTrue(R.is_protected(p), p)
        for p in ("scripts/dev/x.py", "MyTradingSys/execution/live_runner.py"):
            self.assertFalse(R.is_protected(p), p)

    def test_cli_default_is_dry(self):
        self.assertEqual(R.main(["--repo", str(self.clone)]), 0)
        self.assertNotEqual(g(self.clone, "rev-parse", "HEAD"), g(self.up, "rev-parse", "HEAD"))


if __name__ == "__main__":
    unittest.main()
