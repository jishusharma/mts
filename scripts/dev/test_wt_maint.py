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


_TEMPLATE = {}


NO_MAINTENANCE = (("maintenance.auto", "false"), ("gc.auto", "0"), ("gc.autoDetach", "false"))   # git's background maintenance leaves a transient objects/maintenance.lock


def _template():
    """Build the bare origin + primary clone once per run; each test copies it (a fresh repo per test, ~0.1 s instead of ~0.6 s)."""
    if "dir" not in _TEMPLATE:
        t = Path(tempfile.mkdtemp())
        origin = t / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
        g(origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")
        for k, v in NO_MAINTENANCE:
            g(origin, "config", k, v)
        prim = t / "primary"
        subprocess.run(["git", "clone", "-q", str(origin), str(prim)], check=True, capture_output=True)
        for k, v in (("user.email", "t@t"), ("user.name", "t"), *NO_MAINTENANCE):
            g(prim, "config", k, v)
        g(prim, "checkout", "-q", "-b", "fast-track")
        (prim / "a.txt").write_text("a")
        g(prim, "add", ".")
        g(prim, "commit", "-qm", "init")
        g(prim, "push", "-q", "origin", "fast-track")
        _TEMPLATE["dir"] = t
    return _TEMPLATE["dir"]


def tearDownModule():
    import shutil
    if "dir" in _TEMPLATE:
        shutil.rmtree(_TEMPLATE.pop("dir"), ignore_errors=True)


class Env(unittest.TestCase):
    def setUp(self):
        import shutil
        self.tmp = tempfile.mkdtemp()
        t = Path(self.tmp)
        src = _template()
        self.origin = t / "origin.git"
        self.prim = t / "primary"
        # CI flake (test_dirty_shipped_tree_idle_a_day..., shutil.Error on objects/maintenance.lock, 2026-11-11): a detached git maintenance
        # run from the template build deleted its lock mid-copy. The template now disables maintenance; a lock file is never copied.
        skip_locks = shutil.ignore_patterns("*.lock")
        shutil.copytree(src / "origin.git", self.origin, ignore=skip_locks)
        shutil.copytree(src / "primary", self.prim, ignore=skip_locks)
        g(self.prim, "remote", "set-url", "origin", str(self.origin))   # the copy must push to its own origin, not the template's
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

    def test_gemini_trees_kept(self):
        # Gemini work trees (F:\MTS\mts-gemini) are finished-looking when idle and merged; the Gemini Antigravity project
        # opens that folder, so the nightly job must never remove it (2026-10-23 it did, and the project broke).
        a = self.tree("mts-gemini", branch="jis-nuc/gemini-start")
        b = self.tree("mts-x-gemini-run", branch="gemini-q/x")
        s, _ = self.run_maint()
        self.assertEqual(s["removed"], [])
        self.assertTrue(a.exists() and b.exists())

    def test_gpt_trees_kept(self):
        # GPT-lane trees are protected like Codex trees: merged + idle is not evidence the lab is done with them.
        a = self.tree("mts-x-gpt-lab", branch="jis/x-lab")
        b = self.tree("mts-x-run", branch="gpt/crucial")
        s, _ = self.run_maint()
        self.assertEqual(s["removed"], [])
        self.assertTrue(a.exists() and b.exists())

    def test_recent_tree_kept(self):
        p = self.tree("mts-x-fresh")
        s, _ = self.run_maint(now=time.time())
        self.assertEqual(s["removed"], [])
        self.assertTrue(p.exists())

    def test_dirty_tree_kept_and_reported(self):
        p = self.tree("mts-x-dirty")
        (p / "a.txt").write_text("changed")
        s, _ = self.run_maint(now=time.time() + 10 * 3600)   # idle 10 h: under DIRTY_IDLE_HOURS
        self.assertTrue(p.exists())
        self.assertEqual([r["name"] for r in s["held"]], ["mts-x-dirty"])
        self.assertIn("mts-x-dirty", (self.prim / "Dumps" / "worktree_report.txt").read_text())

    def test_dirty_shipped_tree_idle_a_day_is_patch_saved_then_removed(self):
        p = self.tree("mts-x-olddirty")
        (p / "a.txt").write_text("changed")
        (p / "scratch.txt").write_text("untracked work")
        s, out = self.run_maint()   # now = +48 h
        self.assertFalse(p.exists())
        self.assertEqual(s["held"], [])
        dest = self.prim / "Dumps" / "wt_rescue" / "mts-x-olddirty"
        self.assertIn("+changed", (dest / "uncommitted.patch").read_text())
        self.assertEqual((dest / "untracked" / "scratch.txt").read_text(), "untracked work")
        self.assertTrue(any("saved to Dumps/wt_rescue/mts-x-olddirty" in l for l in out))

    def test_dirty_shipped_tree_with_binary_diff_and_untracked_dir_rescued_safely(self):
        p = self.tree("mts-x-bindir")
        (p / "a.txt").write_bytes(b"changed \x98 binary \xff")
        (p / "subdir").mkdir()
        (p / "subdir" / "nested.txt").write_text("nested")
        s, out = self.run_maint()
        self.assertFalse(p.exists())
        dest = self.prim / "Dumps" / "wt_rescue" / "mts-x-bindir"
        self.assertTrue((dest / "uncommitted.patch").exists())
        self.assertEqual((dest / "untracked" / "subdir" / "nested.txt").read_text(), "nested")

    def test_dirty_tree_with_unshipped_commits_is_never_removed_however_idle(self):
        p = self.tree("mts-x-aheaddirty", commit=True)
        (p / "a.txt").write_text("changed")
        s, _ = self.run_maint()
        self.assertTrue(p.exists())
        self.assertEqual([r["name"] for r in s["held"]], ["mts-x-aheaddirty"])

    def test_dirty_tree_with_a_huge_untracked_file_stays(self):
        p = self.tree("mts-x-big")
        (p / "big.bin").write_bytes(b"x" * 2000)
        old = wt_maint.BIG_UNTRACKED_MB
        wt_maint.BIG_UNTRACKED_MB = 0.001
        try:
            s, _ = self.run_maint()
        finally:
            wt_maint.BIG_UNTRACKED_MB = old
        self.assertTrue(p.exists())
        self.assertFalse((self.prim / "Dumps" / "wt_rescue" / "mts-x-big").exists())

    def test_no_log_flag_leaves_the_supervisor_log_alone(self):
        log = self.prim / wt_maint.SUPERVISOR_LOG_REL
        log.parent.mkdir(parents=True)
        log.write_text("head" + chr(10))
        self.tree("mts-x-done")
        out = []
        wt_maint.run(self.prim, apply=True, now=time.time() + FAR, log=out.append, host="JIS-NUC", write_log=False)
        self.assertEqual(log.read_text(), "head" + chr(10))

    def test_unshipped_commits_kept_and_reported(self):
        p = self.tree("mts-x-ahead", commit=True)
        s, _ = self.run_maint()
        self.assertTrue(p.exists())
        self.assertIn("jis/mts-x-ahead", g(self.prim, "branch"))
        self.assertEqual([r["name"] for r in s["held"]], ["mts-x-ahead"])

    def test_hand_made_tree_whose_branch_vanished_is_a_trunk_copy_and_removed(self):
        p = self.tree("mts-x-lost")
        g(self.prim, "update-ref", "-d", "refs/heads/jis/mts-x-lost")     # what `branch -d JIS/x` did to a jis/x worktree on Windows
        self.assertIn("A  a.txt", g(p, "status", "--short"))               # git now shows all of trunk as staged-new
        s, out = self.run_maint()
        self.assertFalse(p.exists())
        self.assertEqual(s["held"], [])
        self.assertIn("mts-x-lost", s["removed"])

    def test_trunk_copy_with_real_edits_is_reported_then_patch_saved(self):
        p = self.tree("mts-x-lostdirty")
        g(self.prim, "update-ref", "-d", "refs/heads/jis/mts-x-lostdirty")
        (p / "a.txt").write_text("changed")
        (p / "scratch.txt").write_text("untracked work")
        s, _ = self.run_maint(now=time.time() + 10 * 3600)
        self.assertTrue(p.exists())
        self.assertEqual([r["why"] for r in s["held"]], ["2 uncommitted file(s) in a trunk copy (branch gone)"])
        s, _ = self.run_maint()
        self.assertFalse(p.exists())
        dest = self.prim / "Dumps" / "wt_rescue" / "mts-x-lostdirty"
        self.assertIn("+changed", (dest / "uncommitted.patch").read_text())
        self.assertEqual((dest / "untracked" / "scratch.txt").read_text(), "untracked work")

    def test_merged_branch_a_worktree_names_in_another_case_is_kept(self):
        p = self.tree("mts-x-case", branch="jis/mixed")
        (p / ".mts_live").write_text("")
        g(p, "symbolic-ref", "HEAD", "refs/heads/jis/MIXED")              # how a hand-made tree looks on a case-insensitive FS
        self.run_maint()
        self.assertIn("jis/mixed", g(self.prim, "branch"))

    def test_idle_tree_with_unshipped_commits_is_parked_branch_kept_and_pushed(self):
        p = self.tree("mts-x-park", commit=True)
        s, out = self.run_maint(now=time.time() + (wt_maint.PARK_IDLE_HOURS + 8) * 3600)
        self.assertFalse(p.exists())
        self.assertEqual(s["parked"], ["mts-x-park"])
        self.assertEqual(s["held"], [])
        self.assertIn("jis/mts-x-park", g(self.prim, "branch"))
        self.assertIn("jis/mts-x-park", g(self.prim, "ls-remote", "--heads", "origin"))
        self.assertIn("parked", (self.prim / "Dumps" / "worktree_report.txt").read_text())
        self.assertTrue(any("restore: git worktree add ../mts-x-park jis/mts-x-park" in l for l in out))

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



class GatewayMarker(Env):
    """C: guard freed 0.66 GB because the machine flag put .gateway_owner in all 66 trees: a stale marker must not pin a finished tree."""
    def test_idle_gateway_tree_that_is_finished_is_removed(self):
        p = self.tree("mts-gw-done")
        (p / sync.GATEWAY_MARKER).write_text("x")
        s, _ = self.run_maint()
        self.assertEqual(s["removed"], ["mts-gw-done"])

    def test_gateway_tree_in_use_is_kept(self):
        p = self.tree("mts-gw-live")
        (p / sync.GATEWAY_MARKER).write_text("x")
        s, _ = self.run_maint(now=time.time())
        self.assertEqual(s["removed"], [])
        self.assertTrue(p.exists())

    def test_idle_gateway_tree_with_unshipped_commit_is_kept(self):
        p = self.tree("mts-gw-work", commit=True)
        (p / sync.GATEWAY_MARKER).write_text("x")
        s, _ = self.run_maint()
        self.assertEqual(s["removed"], [])
        self.assertTrue(p.exists())


class SharedConstants(unittest.TestCase):
    def test_supervisor_log_rel_is_cicd_runs(self):
        """dedupe CODE 25: one SUPERVISOR_LOG_REL (cicd_run owns it); wt_maint imports it."""
        import cicd_run
        self.assertIs(wt_maint.SUPERVISOR_LOG_REL, cicd_run.SUPERVISOR_LOG_REL)


class TemplateIsQuiet(Env):
    def test_template_repos_disable_git_background_maintenance(self):
        """Flake fix (test_value_audit_1113): a detached `git maintenance` left objects/maintenance.lock that vanished mid-copytree."""
        for repo in (self.origin, self.prim):
            for k, v in NO_MAINTENANCE:
                self.assertEqual(g(repo, "config", "--get", k), v, (repo.name, k))
        self.assertEqual(list(self.origin.rglob("*.lock")), [])


if __name__ == "__main__":
    unittest.main()
