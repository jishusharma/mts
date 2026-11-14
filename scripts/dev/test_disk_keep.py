"""disk_keep: floors per host, DISK/DISK ACT lines, safe tree move. Nothing here needs F: or D: (temp folders stand in for drives)."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import disk_keep as dk  # noqa: E402
import sync  # noqa: E402

PLAN = {"hosts": {
    "JIS-DESKTOP": {"status": "KNOWN", "drives": {"C:\\": {"floor_gb": 20}, "F:\\": {"floor_gb": 20}, "D:\\": {"floor_gb": 0}},
                    "overflow": {"wt": "D:\\MTS\\wt_cold", "data": "D:\\MTS\\data_cold"}},
    "JIS-NUC": {"status": "UNKNOWN", "fact_cmd": "python scripts/dev/disk_keep.py facts"}}}


def git(cwd, *a):
    subprocess.run(["git", "-C", str(cwd), *a], check=True, capture_output=True)


class StatusTests(unittest.TestCase):
    def test_floor_breach_prints_disk_act_and_ok_does_not(self):
        free = {"C:\\": 25.0, "F:\\": 12.0, "D:\\": 600.0}
        with mock.patch.object(dk, "free_gb", side_effect=lambda d: free[d]):
            lines = dk.status_lines(PLAN, "JIS-NB")                # old host name resolves through hosts.py
        self.assertEqual(len([l for l in lines if l.startswith("DISK ACT")]), 1)
        self.assertTrue(any("F:\\" in l and "LOW" in l for l in lines))
        self.assertTrue(any(l.startswith("DISK C:") and "ok" in l for l in lines))

    def test_unknown_host_names_the_command_to_run(self):
        lines = dk.status_lines(PLAN, "JIS-NUC")
        self.assertEqual(len(lines), 1)
        self.assertIn("DISK UNKNOWN", lines[0])
        self.assertIn("disk_keep.py facts", lines[0])

    def test_missing_plan_and_unlisted_host_never_raise(self):
        self.assertIn("DISK UNKNOWN", dk.status_lines({"hosts": {}}, "X")[0])
        self.assertEqual(dk.load_plan(Path("/nonexistent/plan.json")), {"hosts": {}})

    def test_shipped_plan_has_the_desktop_floors(self):
        row = dk.load_plan()["hosts"]["JIS-DESKTOP"]
        self.assertEqual(row["drives"]["C:\\"]["floor_gb"], 20)
        self.assertEqual(row["drives"]["F:\\"]["floor_gb"], 20)
        self.assertTrue(row["overflow"]["wt"].startswith("D:"))

    def test_supervisor_plan_source_calls_disk_keep(self):
        src = (Path(__file__).resolve().parent / "supervisor.py").read_text(encoding="utf-8")
        self.assertIn("disk_keep.status_lines", src)


class MoveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        self.main = self.tmp / "main"
        self.main.mkdir()
        for c in (["init", "-q", "-b", "fast-track"], ["config", "user.email", "a@b"], ["config", "user.name", "t"]):
            git(self.main, *c)
        (self.main / "a.txt").write_text("1")
        git(self.main, "add", ".")
        git(self.main, "commit", "-qm", "i")
        self.wt = self.tmp / "mts-x-cold"
        git(self.main, "worktree", "add", "-q", str(self.wt), "-b", "cold")
        (self.wt / "big.bin").write_bytes(b"x" * 5000)

    def test_move_copies_verifies_repairs_and_removes_source(self):
        ok, msg = dk.move_tree(self.main, self.wt, self.tmp / "cold")
        self.assertTrue(ok, msg)
        self.assertFalse(self.wt.exists())
        new = self.tmp / "cold" / "mts-x-cold"
        self.assertEqual((new / "big.bin").stat().st_size, 5000)
        listed = {os.path.normcase(str(Path(p).resolve())) for p, _ in sync.worktrees(self.main)}
        self.assertIn(os.path.normcase(str(new.resolve())), listed)
        subprocess.run(["git", "-C", str(new), "status", "--short"], check=True, capture_output=True)   # the moved tree still works

    def test_failed_verify_keeps_the_source(self):
        with mock.patch.object(dk, "tree_size", side_effect=[(1, 1), (2, 2)]):
            ok, msg = dk.move_tree(self.main, self.wt, self.tmp / "cold")
        self.assertFalse(ok)
        self.assertTrue((self.wt / "big.bin").exists())
        self.assertFalse((self.tmp / "cold" / "mts-x-cold").exists())

    def test_cold_trees_keeps_dirty_claimed_busy_lane_and_active_trees(self):
        row = {"overflow": {"wt": str(self.tmp / "cold")}, "protect": []}
        later = time.time() + 100 * 3600
        ok, keep = dk.cold_trees(row, 24, self.main, now=later, snapshot=[], claims=[])
        self.assertEqual([Path(p).name for p, _, _ in ok], [])    # big.bin is untracked: dirty
        self.assertIn("uncommitted files", dict(keep)[str(self.wt)])
        (self.wt / "big.bin").unlink()
        ok, keep = dk.cold_trees(row, 24, self.main, now=later, snapshot=[], claims=[])
        self.assertEqual([Path(p).name for p, _, _ in ok], ["mts-x-cold"])
        ok, keep = dk.cold_trees(row, 24, self.main, now=later, snapshot=[], claims=["cold"])
        self.assertEqual(dict(keep)[str(self.wt)], "open claim")
        ok, keep = dk.cold_trees(row, 24, self.main, now=later, snapshot=[{"pid": 1, "cmd": f"python {self.wt}\\x.py"}], claims=[])
        self.assertEqual(dict(keep)[str(self.wt)], "live process names it")
        ok, keep = dk.cold_trees(row, 24, self.main, now=time.time(), snapshot=[], claims=[])
        self.assertIn("active", dict(keep)[str(self.wt)])
        ok, keep = dk.cold_trees({**row, "protect": [str(self.tmp)]}, 24, self.main, now=later, snapshot=[], claims=[])
        self.assertEqual(dict(keep)[str(self.wt)], "protected path")

    def test_cold_cache_file_moves_and_stays_a_cache_hit(self):
        import data_cache
        cache, cold = self.tmp / "cache", self.tmp / "data_cold"
        with mock.patch.dict(os.environ, {"MTS_DATA_CACHE": str(cache)}):
            f = data_cache.cached("b/x.npz", lambda: b"abc")
            old = time.time() - 400 * 3600
            os.utime(f, (old, old))
            row = {"overflow": {"data": str(cold)}, "cold_after_hours": {"data": 168}}
            files = dk.cold_cache_files(row)
            self.assertEqual(dk.move_cache(row, files, True), 1)
            self.assertFalse(f.exists())
            with mock.patch.object(data_cache, "cold_path", return_value=cold / "b" / "x.npz"):
                self.assertEqual(data_cache.cached("b/x.npz", lambda: self.fail("refetched")).read_bytes(), b"abc")


if __name__ == "__main__":
    unittest.main()
