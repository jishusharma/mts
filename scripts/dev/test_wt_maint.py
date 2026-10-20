"""Tests for wt_maint.py: real git repos in a temp dir (bare origin + primary clone + worktrees)."""
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync
import wt_maint

FAR = 48 * 3600   # "now" this far ahead makes every tree look idle for 48 h


def g(cwd, *a):
    r = subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


class Env(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        t = Path(self.tmp)
        self.origin = t / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(self.origin)], check=True)
        g(self.origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")
        self.prim = t / "primary"
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.prim)], check=True, capture_output=True)
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            g(self.prim, "config", k, v)
        g(self.prim, "checkout", "-q", "-b", "fast-track")
        (self.prim / "a.txt").write_text("a")
        g(self.prim, "add", ".")
        g(self.prim, "commit", "-qm", "init")
        g(self.prim, "push", "-q", "origin", "fast-track")
        self.t = t

    def tearDown(self):
        # git marks objects read-only on Windows
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def tree(self, name, branch=None, commit=False):
        p = self.t / name
        g(self.prim, "worktree", "add", "-q", "-b", branch or f"jis/{name}", str(p), "origin/fast-track")
        g(p, "config", "user.email", "t@t")
        g(p, "config", "user.name", "t")
        if commit:
            (p / "new.txt").write_text("x")
            g(p, "add", ".")
            g(p, "commit", "-qm", "work")
        return p

    def run_maint(self, apply=True, now=None):
        out = []
        s = wt_maint.run(self.prim, apply=apply, now=now if now is not None else time.time() + FAR, log=out.append, host="JIS-NUC")
        return s, out


class Safety(Env):
    def test_finished_tree_removed_and_branch_deleted(self):
        p = self.tree("mts-x-done")
        s, _ = self.run_maint()
        self.assertEqual(s["removed"], ["mts-x-done"])
        self.assertFalse(p.exists())
        self.assertNotIn("jis/mts-x-done", g(self.prim, "branch"))

    def test_dry_run_changes_nothing(self):
        p = self.tree("mts-x-done")
        s, _ = self.run_maint(apply=False)
        self.assertEqual(s["removed"], ["mts-x-done"])
        self.assertTrue(p.exists())
        self.assertIn("jis/mts-x-done", g(self.prim, "branch"))

    def test_live_tree_kept(self):
        p = self.tree("mts-x-live")
        (p / ".mts_live").write_text("")
        s, _ = self.run_maint()
        self.assertEqual(s["removed"], [])
        self.assertTrue(p.exists())

    def test_lane_and_codex_trees_kept(self):
        a, b, c = self.tree("mts-push"), self.tree("mts-codex-lab"), self.tree("mts-x-codex-run", branch="codex/foo")
        s, _ = self.run_maint()
        self.assertEqual(s["removed"], [])
        self.assertTrue(a.exists() and b.exists() and c.exists())

    def test_recent_tree_kept(self):
        p = self.tree("mts-x-fresh")
        s, _ = self.run_maint(now=time.time())
        self.assertEqual(s["removed"], [])
        self.assertTrue(p.exists())

    def test_dirty_tree_kept_and_reported(self):
        p = self.tree("mts-x-dirty")
        (p / "a.txt").write_text("changed")
        s, _ = self.run_maint()
        self.assertTrue(p.exists())
        self.assertEqual([r["name"] for r in s["held"]], ["mts-x-dirty"])
        self.assertIn("mts-x-dirty", (self.prim / "Dumps" / "worktree_report.txt").read_text())

    def test_unshipped_commits_kept_and_reported(self):
        p = self.tree("mts-x-ahead", commit=True)
        s, _ = self.run_maint()
        self.assertTrue(p.exists())
        self.assertIn("jis/mts-x-ahead", g(self.prim, "branch"))
        self.assertEqual([r["name"] for r in s["held"]], ["mts-x-ahead"])

    def test_ignored_data_moved_to_dumps_before_removal(self):
        (self.prim / ".gitignore").write_text("out/\n")
        g(self.prim, "add", ".")
        g(self.prim, "commit", "-qm", "ignore")
        g(self.prim, "push", "-q", "origin", "fast-track")
        p = self.tree("mts-x-data")
        (p / "out").mkdir()
        (p / "out" / "res.csv").write_text("1,2")
        s, _ = self.run_maint()
        self.assertFalse(p.exists())
        self.assertEqual((self.prim / "Dumps" / "wt_rescue" / "mts-x-data" / "out" / "res.csv").read_text(), "1,2")

    def test_merged_branch_deleted_but_checked_out_and_fast_track_kept(self):
        g(self.prim, "branch", "old-merged", "origin/fast-track")
        p = self.tree("mts-x-live-branch", branch="jis/checked-out")
        (p / ".mts_live").write_text("")
        self.run_maint()
        branches = g(self.prim, "branch")
        self.assertNotIn("old-merged", branches)
        self.assertIn("jis/checked-out", branches)
        self.assertIn("fast-track", branches)

    def test_unmerged_branch_kept(self):
        p = self.tree("mts-x-wip", commit=True)
        g(self.prim, "worktree", "remove", "--force", str(p))
        self.run_maint()
        self.assertIn("jis/mts-x-wip", g(self.prim, "branch"))


class Idempotent(Env):
    def test_second_run_is_a_noop(self):
        self.tree("mts-x-done")
        self.tree("mts-x-ahead", commit=True)
        g(self.prim, "branch", "old-merged", "origin/fast-track")
        s1, _ = self.run_maint()
        s2, _ = self.run_maint()
        self.assertEqual(s1["removed"], ["mts-x-done"])
        self.assertEqual(s2["removed"], [])
        self.assertEqual(s2["branches"], [])
        self.assertEqual([r["name"] for r in s2["held"]], ["mts-x-ahead"])

    def test_supervisor_log_line_appended_on_apply_only(self):
        log = self.prim / wt_maint.SUPERVISOR_LOG_REL
        log.parent.mkdir(parents=True)
        log.write_text("# log\n")
        self.run_maint(apply=False)
        self.assertEqual(log.read_text(), "# log\n")
        self.run_maint()
        self.assertEqual(len(log.read_text().splitlines()), 2)
        self.assertIn("JIS-NUC", log.read_text())


class Device(unittest.TestCase):
    def test_known_names(self):
        self.assertEqual(wt_maint.device_name("jis-nb"), "JIS-NB")
        self.assertEqual(wt_maint.device_name("JIS-NUC"), "JIS-NUC")
        self.assertEqual(wt_maint.device_name("DESKTOP-F7IU69N"), "Lenovo laptop")

    def test_unknown_host_keeps_own_name_and_task_name_is_safe(self):
        self.assertEqual(wt_maint.device_name("Some-PC"), "SOME-PC")
        self.assertEqual(wt_maint.task_name("Lenovo laptop"), "MTS-WorktreeMaint-Lenovo-laptop")
        self.assertEqual(wt_maint.task_name("JIS-NUC"), "MTS-WorktreeMaint-JIS-NUC")

    def test_install_script_has_no_hardcoded_user_path_and_is_headless(self):
        s = wt_maint.install_script(Path("D:/x/repo"), "JIS-NB")
        self.assertIn("conhost.exe", s)
        self.assertIn("--headless", s)
        self.assertIn("D:/x/repo", s.replace("\\", "/"))
        self.assertIn("MTS-WorktreeMaint-JIS-NB", s)
        src = Path(wt_maint.__file__).read_text(encoding="utf-8")
        self.assertNotIn("E-ngineers", src)


if __name__ == "__main__":
    unittest.main()
