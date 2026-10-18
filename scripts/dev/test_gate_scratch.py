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


if __name__ == "__main__":
    unittest.main()
