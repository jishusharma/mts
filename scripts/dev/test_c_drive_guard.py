"""c_drive_guard prunes only old, known-prefix %TEMP% entries and old Claude session dirs; it reports runaway task outputs."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c_drive_guard as g

TEST_KEY = r"Software\MTSTempGuardTest"
TEST_NAME = "MTSTempGuardTest"


def make(root, rel, age_h, size=10):
    """Write root/rel and age the file and every directory below root to age_h hours."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)
    t = time.time() - age_h * 3600
    while path != root:
        os.utime(path, (t, t))
        path = path.parent
    return root / rel


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.root = Path(self.d.name)
        self.logdir = tempfile.TemporaryDirectory()
        self.old_temp, self.old_log, self.old_stamp = g.TEMP, g.LOG, g.STAMP
        g.TEMP = self.root
        g.LOG = Path(self.logdir.name) / "c_drive_guard.log"
        g.STAMP = Path(self.logdir.name) / "c_drive_guard.stamp"
        g.STAMP.write_text("x", encoding="utf-8")      # daily run not due unless a test ages this

    def tearDown(self):
        g.TEMP, g.LOG, g.STAMP = self.old_temp, self.old_log, self.old_stamp
        self.d.cleanup()
        self.logdir.cleanup()

    def test_prunes_only_old_known_prefix_and_old_sessions(self):
        r = self.root
        make(r, "mts_s4_old/bt/f.txt", 30)
        make(r, "tmpabc12345/f.txt", 30)
        make(r, "mts_s4_new/f.txt", 1)
        make(r, "precious/f.txt", 500)
        make(r, "claude/proj/sess_old/tasks/a.output", 100)
        make(r, "claude/proj/sess_new/tasks/a.output", 10)
        n, freed = g.prune(apply=True)
        self.assertEqual(n, 3)
        self.assertEqual(freed, 30)
        left = sorted(p.name for p in self.root.iterdir())
        self.assertEqual(left, ["claude", "mts_s4_new", "precious"])
        self.assertEqual([p.name for p in (self.root / "claude" / "proj").iterdir()], ["sess_new"])

    def test_prunes_the_gate_and_test_prefixes_seen_in_temp(self):
        for name in ("gate_budget_test_abc", "dsa_tpl_x1", "e2e_a2_q", "dsa-boot-3"):
            make(self.root, name + "/f.txt", 30)
        n, _ = g.prune(apply=True)
        self.assertEqual(n, 4)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_git_worktrees_are_never_pruned(self):
        # desk.py makes its scratch checkout with `git worktree add` under %TEMP%\desk-*: a crashed post leaves unshipped commits
        make(self.root, "desk-y_51efmr/wt/.git", 30)
        make(self.root, "gate_budget_test_wt/tree/.git", 30)
        n, _ = g.prune(apply=True)
        self.assertEqual(n, 0)
        self.assertTrue((self.root / "desk-y_51efmr").exists())
        self.assertTrue((self.root / "gate_budget_test_wt").exists())

    def test_state_dirs_other_code_reads_are_never_pruned(self):
        for name in ("mts_roles", "mts_host_health", "mts_gate_slots", "mts_relay"):
            make(self.root, name + "/state.json", 500)
        n, _ = g.prune(apply=True)
        self.assertEqual(n, 0)
        self.assertEqual(len(list(self.root.iterdir())), 4)

    def test_one_new_file_deep_inside_keeps_the_whole_entry(self):
        make(self.root, "tmpdeep/a/b/old.txt", 30)
        make(self.root, "tmpdeep/a/b/new.txt", 1)
        n, _ = g.prune(apply=True)
        self.assertEqual(n, 0)
        self.assertTrue((self.root / "tmpdeep").exists())

    def test_dry_run_deletes_nothing(self):
        make(self.root, "tmpabc12345/f.txt", 30)
        n, _ = g.prune(apply=False)
        self.assertEqual(n, 1)
        self.assertTrue((self.root / "tmpabc12345").exists())

    def test_runaway_output_is_reported(self):
        p = make(self.root, "claude/proj/sess/tasks/big.output", 0)
        old = g.RUNAWAY_MB
        g.RUNAWAY_MB = 0
        try:
            self.assertEqual([r[0] for r in g.runaways()], [str(p)])
        finally:
            g.RUNAWAY_MB = old

    def test_hook_is_silent_above_the_limit(self):
        os.environ["MTS_C_MIN_FREE_GB"] = "0"
        try:
            self.assertEqual(g.main(["hook"]), 0)
        finally:
            os.environ.pop("MTS_C_MIN_FREE_GB", None)

    def test_own_gate_basetemps_go_after_6_h_other_prefixes_after_24(self):
        make(self.root, "mts_s4_8h/f.txt", 8)
        make(self.root, "mts_s5c_8h/f.txt", 8)
        make(self.root, "tmpabc_8h/f.txt", 8)
        make(self.root, "mts_s4_1h/f.txt", 1)
        g.prune(apply=True)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["mts_s4_1h", "tmpabc_8h"])

    def test_plan_lists_each_item_with_a_reason_and_deletes_nothing(self):
        make(self.root, "mts_s4_old/f.txt", 30)
        old = g.run_tidy
        g.run_tidy = lambda apply: ["would remove  agent-1 [b]: clean, no ignored data, on origin/fast-track, idle 2.0 h",
                                    "would remove 1; kept 0"]
        try:
            rows = g.plan()
        finally:
            g.run_tidy = old
        self.assertEqual([(r[0], Path(r[1]).name) for r in rows], [("temp", "mts_s4_old"), ("worktree", "agent-1 [b]")])
        self.assertTrue(all(r[3] for r in rows))
        self.assertTrue((self.root / "mts_s4_old").exists())

    def test_never_deletes_other_apps_files_or_the_claude_app_folder(self):
        make(self.root, "OtherApp/f.txt", 900)
        make(self.root, "Claude/f.txt", 900)           # the app's own data folder name, never matches a prefix
        make(self.root, "AnthropicClaude/f.txt", 900)
        make(self.root, "xmts_s4_notprefix/f.txt", 900)
        g.prune(apply=True)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()),
                         ["AnthropicClaude", "Claude", "OtherApp", "xmts_s4_notprefix"])
        self.assertEqual(g.candidates(), [])

    def test_hook_runs_the_guard_once_a_day_and_not_again(self):
        started = []
        old = g.start_apply_detached
        g.start_apply_detached = lambda: started.append(1)
        os.environ["MTS_C_MIN_FREE_GB"] = "0"
        try:
            t = time.time() - 30 * 3600
            os.utime(g.STAMP, (t, t))
            g.main(["hook"])
            g.main(["hook"])
        finally:
            g.start_apply_detached = old
            os.environ.pop("MTS_C_MIN_FREE_GB", None)
        self.assertEqual(started, [1])

    def test_low_disk_hook_starts_at_most_one_run_per_hour(self):
        started = []
        old = g.start_apply_detached
        g.start_apply_detached = lambda: started.append(1)
        os.environ["MTS_C_MIN_FREE_GB"] = "100000"     # every drive is "low"
        try:
            t = time.time() - 2 * 3600
            os.utime(g.STAMP, (t, t))
            with contextlib.redirect_stdout(io.StringIO()):
                for _ in range(5):                     # 5 session starts in a row
                    g.main(["hook"])
        finally:
            g.start_apply_detached = old
            os.environ.pop("MTS_C_MIN_FREE_GB", None)
        self.assertEqual(started, [1])

    def test_second_apply_run_skips_while_the_first_holds_the_lock(self):
        old_lock, old_apply = g.LOCK, g.apply_all
        g.LOCK = Path(self.logdir.name) / "c_drive_guard.lock"
        ran = []
        g.apply_all = lambda mode: (ran.append(1), (0, 0, 0))[1]
        try:
            g.LOCK.write_text(str(os.getpid()), encoding="utf-8")     # a live run holds it
            with contextlib.redirect_stdout(io.StringIO()):
                g.main(["--apply"])
            self.assertEqual(ran, [])
            g.LOCK.write_text("999999", encoding="utf-8")             # stale: that pid is gone
            with contextlib.redirect_stdout(io.StringIO()):
                g.main(["--apply"])
            self.assertEqual(ran, [1])
            self.assertFalse(g.LOCK.exists())
        finally:
            g.LOCK, g.apply_all = old_lock, old_apply

    def test_tidy_child_runs_without_a_console_window(self):
        seen = {}
        old = subprocess.run
        subprocess.run = lambda *a, **k: (seen.update(k), subprocess.CompletedProcess(a, 0, "", ""))[1]
        try:
            g.run_tidy(False)
        finally:
            subprocess.run = old
        self.assertEqual(seen.get("creationflags"), getattr(subprocess, "CREATE_NO_WINDOW", 0))

    def test_apply_logs_one_line_with_the_gb_freed(self):
        make(self.root, "mts_s4_old/f.txt", 30)
        old, old_note = g.run_tidy, g.main_checkout_note
        g.run_tidy = lambda apply: ["removed  agent-1 [b]: x"]
        g.main_checkout_note = lambda pull=True: "main checkout 3 behind; hook may be stale"
        try:
            g.apply_all("apply")
        finally:
            g.run_tidy, g.main_checkout_note = old, old_note
        lines = g.LOG.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("freed", lines[0])
        self.assertIn("1 worktrees retired", lines[0])
        self.assertIn("main checkout 3 behind; hook may be stale", lines[0])

    def test_low_space_on_the_repo_drive_counts_not_only_c(self):
        old_free, old_drive = g.free_gb, g.repo_drive
        g.repo_drive = lambda: "F:\\"
        g.free_gb = lambda d="C:\\": 50.0 if d == "C:\\" else 4.0
        try:
            self.assertEqual(g.low_drives(15), [("F:\\", 4.0)])
            g.repo_drive = lambda: "C:\\"
            self.assertEqual(g.low_drives(15), [])
        finally:
            g.free_gb, g.repo_drive = old_free, old_drive

    def _repo_pair(self, tmp):
        def sh(cwd, *a):
            subprocess.run(["git", "-C", str(cwd), *a], check=True, capture_output=True)
        origin, main = Path(tmp) / "origin.git", Path(tmp) / "main"
        sh(tmp, "init", "-q", "--bare", "-b", "fast-track", str(origin))
        sh(tmp, "clone", "-q", str(origin), str(main))
        for c in (main,):
            sh(c, "config", "user.email", "a@b.c")
            sh(c, "config", "user.name", "t")
        (main / "a.txt").write_text("1", newline="\n")
        sh(main, "add", "."); sh(main, "commit", "-q", "-m", "one"); sh(main, "push", "-q", "origin", "HEAD:fast-track")
        other = Path(tmp) / "other"
        sh(tmp, "clone", "-q", str(origin), str(other))
        sh(other, "config", "user.email", "a@b.c"); sh(other, "config", "user.name", "t")
        (other / "b.txt").write_text("2", newline="\n")
        sh(other, "add", "."); sh(other, "commit", "-q", "-m", "two"); sh(other, "push", "-q", "origin", "HEAD:fast-track")
        return main

    def test_main_checkout_behind_is_pulled_when_clean_and_left_alone_when_dirty(self):
        with tempfile.TemporaryDirectory() as tmp:
            main = self._repo_pair(tmp)
            old = g.main_checkout
            g.main_checkout = lambda: main
            try:
                (main / "a.txt").write_text("edited", newline="\n")
                note = g.main_checkout_note()
                self.assertIn("main checkout 1 behind; hook may be stale", note)
                self.assertIn("not pulled", note)
                self.assertFalse((main / "b.txt").exists())
                subprocess.run(["git", "-C", str(main), "checkout", "-q", "--", "a.txt"], check=True)
                self.assertIn("pulled", g.main_checkout_note())
                self.assertTrue((main / "b.txt").exists())
            finally:
                g.main_checkout = old

    def test_logon_prunes_whatever_the_free_space_and_logs_one_line(self):
        make(self.root, "tmpold/f.txt", 30)
        make(self.root, "mts_s4_new/f.txt", 1)
        self.assertEqual(g.main(["logon"]), 0)
        self.assertFalse((self.root / "tmpold").exists())
        self.assertTrue((self.root / "mts_s4_new").exists())
        lines = g.LOG.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("logon: C free", lines[0])
        self.assertIn("pruned 1 temp entries", lines[0])

    def test_logon_command_is_headless_and_runs_the_logon_mode(self):
        cmd = g.logon_command(python=r"C:\Py\python.exe", script=r"C:\repo\scripts\dev\c_drive_guard.py")
        self.assertIn("--headless", cmd)
        self.assertIn(r'"C:\Py\python.exe" "C:\repo\scripts\dev\c_drive_guard.py" logon', cmd)
        self.assertTrue(cmd.endswith(" logon"))

    @unittest.skipUnless(os.name == "nt", "junctions are Windows reparse points")
    def test_a_junction_is_never_walked_or_pruned(self):
        target = tempfile.TemporaryDirectory()
        link = self.root / "tmpjunction"
        try:
            keep = make(Path(target.name), "precious.txt", 500)
            subprocess.run(["cmd", "/c", "mklink", "/J", str(link), target.name], check=True, capture_output=True)
            n, _ = g.prune(apply=True)
            self.assertEqual(n, 0)
            self.assertTrue(keep.exists())
        finally:
            if link.exists():
                os.rmdir(link)     # removes the junction only
            target.cleanup()

    @unittest.skipUnless(os.name == "nt", "junctions are Windows reparse points")
    def test_a_junction_under_claude_is_never_followed(self):
        # a junction in %TEMP%\claude\<proj> pointing at a folder outside %TEMP% must not lead the guard into it
        target = tempfile.TemporaryDirectory()
        proj_link = self.root / "claude" / "projjunction"
        try:
            keep = make(Path(target.name), "sess_old/tasks/a.output", 100)
            proj_link.parent.mkdir(parents=True)
            subprocess.run(["cmd", "/c", "mklink", "/J", str(proj_link), target.name], check=True, capture_output=True)
            n, _ = g.prune(apply=True)
            self.assertEqual(n, 0)
            self.assertTrue(keep.exists())
        finally:
            if proj_link.exists():
                os.rmdir(proj_link)     # removes the junction only
            target.cleanup()

    def test_install_refuses_a_git_worktree(self):
        with tempfile.TemporaryDirectory() as wt, contextlib.redirect_stdout(io.StringIO()) as out:
            Path(wt, ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
            Path(wt, "scripts", "dev").mkdir(parents=True)
            Path(wt, "scripts", "dev", "c_drive_guard.py").write_text("", encoding="utf-8")
            self.assertEqual(g.install(checkout=wt, key=TEST_KEY, name=TEST_NAME), 2)
        self.assertIn("git worktree", out.getvalue())
        self.assertIsNone(g.installed_command(TEST_KEY, TEST_NAME))


@unittest.skipUnless(os.name == "nt", "HKCU Run is Windows only")
class RunKeyTest(unittest.TestCase):
    def setUp(self):
        self.co = tempfile.TemporaryDirectory()
        Path(self.co.name, ".git").mkdir()
        Path(self.co.name, "scripts", "dev").mkdir(parents=True)
        Path(self.co.name, "scripts", "dev", "c_drive_guard.py").write_text("", encoding="utf-8")

    def tearDown(self):
        import winreg
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, TEST_KEY)
        except OSError:
            pass
        self.co.cleanup()

    def test_install_status_uninstall_roundtrip(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(g.install(checkout=self.co.name, key=TEST_KEY, name=TEST_NAME), 0)
            cmd = g.installed_command(TEST_KEY, TEST_NAME)
            self.assertIn(str(Path(self.co.name, "scripts", "dev", "c_drive_guard.py")), cmd)
            self.assertEqual(g.uninstall(key=TEST_KEY, name=TEST_NAME), 0)
        self.assertIsNone(g.installed_command(TEST_KEY, TEST_NAME))


if __name__ == "__main__":
    unittest.main()
