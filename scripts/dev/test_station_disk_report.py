import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import station_disk_report as s


class T(unittest.TestCase):
    def test_tree_gb_counts_bytes_and_budget_cut(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            Path(d, "a.bin").write_bytes(b"x" * 1000)
            g, cut = s.tree_gb(d)
            self.assertAlmostEqual(g, 1000 / 1e9)
            self.assertFalse(cut)

    def test_report_is_one_short_line(self):
        line = s.report()
        self.assertNotIn("\n", line)
        self.assertIn("free=", line)
        self.assertTrue("java=" in line or "procs=n/a" in line)


if __name__ == "__main__":
    unittest.main()
