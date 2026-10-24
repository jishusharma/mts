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
        self.old_temp, self.old_log = g.TEMP, g.LOG
        g.TEMP = self.root
        g.LOG = Path(self.logdir.name) / "c_drive_guard.log"

    def tearDown(self):
        g.TEMP, g.LOG = self.old_temp, self.old_log
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
        for name in ("gate_budget_test_abc", "dsa_tpl_x1", "e2e_a2_q", "desk-y_51efmr", "dsa-boot-3"):
            make(self.root, name + "/f.txt", 30)
        n, _ = g.prune(apply=True)
        self.assertEqual(n, 5)
        self.assertEqual(list(self.root.iterdir()), [])

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
