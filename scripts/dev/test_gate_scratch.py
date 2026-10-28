"""B194: the gate's per-step pytest scratch dirs (mts_s4_*) must not outlive the run (963 leaked dirs slowed the JIS-NB logon to 340 s)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_all_tests as r


class GateScratch(unittest.TestCase):
    def test_scratch_dirs_are_removed_at_exit(self):
        n = len(r._SCRATCH)
        cmd = r.pytest_cmd(["x"])
        d = r._SCRATCH[-1]
        self.assertEqual(len(r._SCRATCH), n + 1)
        self.assertTrue(os.path.isdir(d))
        self.assertTrue(any(a.startswith("--basetemp=") and d in a for a in cmd))
        open(os.path.join(d, "f.txt"), "w").close()
        r._drop_scratch()
        self.assertFalse(os.path.exists(d))

    def test_children_get_a_run_scoped_temp_root_removed_at_exit(self):
        """2026-10-28: tests' own tempfile.mkdtemp leftovers refilled %TEMP% (~190 dirs / 10 min). A child that makes a temp dir must
        land under the run root, and removing the gate temp dirs must take it with it."""
        import subprocess, tempfile
        keys = ("TEMP", "TMP", "TMPDIR", "MTS_RUN_TEMP", "MTS_NO_RUN_TEMP")
        saved = {k: os.environ.get(k) for k in keys}
        real = tempfile.gettempdir()
        saved_td = tempfile.tempdir
        os.environ.pop("MTS_RUN_TEMP", None); os.environ.pop("MTS_NO_RUN_TEMP", None)
        try:
            root = r.run_temp_root()
            self.assertTrue(root and os.path.isdir(root))
            self.assertEqual(tempfile.gettempdir(), real)   # this process keeps the shared temp dir (gate slots)
            out = subprocess.run([sys.executable, "-c", "import tempfile;print(tempfile.mkdtemp(prefix='leak_'))"],
                                 capture_output=True, text=True).stdout.strip()
            self.assertTrue(os.path.isdir(out))
            self.assertEqual(os.path.dirname(out), root)
            r._remove_gate_tmp()
            self.assertFalse(os.path.exists(out))
            self.assertFalse(os.path.exists(root))
        finally:
            for k, v in saved.items():
                if v is None: os.environ.pop(k, None)
                else: os.environ[k] = v
            tempfile.tempdir = saved_td


if __name__ == "__main__":
    unittest.main()
