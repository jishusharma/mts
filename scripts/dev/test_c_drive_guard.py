"""c_drive_guard prunes only old, known-prefix %TEMP% entries and old Claude session dirs; it reports runaway task outputs."""
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c_drive_guard as g


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
        self.old_temp = g.TEMP
        g.TEMP = self.root

    def tearDown(self):
        g.TEMP = self.old_temp
        self.d.cleanup()

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


if __name__ == "__main__":
    unittest.main()
