import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import station_disk_report as s


class T(unittest.TestCase):
    def test_tree_gb_counts_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "a.bin").write_bytes(b"x" * 1000)
            g, cut = s.tree_gb(d)
            self.assertAlmostEqual(g, 1000 / 1e9)
            self.assertFalse(cut)

    def test_platform_choices_are_pure(self):
        self.assertEqual(s.drives(True), ("C:\\", "F:\\"))
        self.assertEqual(s.drives(False), ("/",))
        self.assertEqual(s.drive_label("C:\\", True), "C")
        self.assertEqual(s.drive_label("/", False), "root")
        self.assertEqual(s.proc_command(False)[0], "ps")
        self.assertEqual(s.proc_command(True)[0], "tasklist")

    def test_count_procs_reads_both_outputs(self):
        win = '"java.exe","12","Console","1","1 K"\n"python.exe","3","Console","1","1 K"\n"Python3.exe","4","x","1","1 K"\n'
        self.assertEqual(s.count_procs(win), "java=1 python=2")
        posix = "java\n/usr/bin/python3\nbash\npython3.12\n"
        self.assertEqual(s.count_procs(posix), "java=1 python=2")

    def test_report_is_one_line(self):
        self.assertNotIn("\n", s.report())


if __name__ == "__main__":
    unittest.main()
