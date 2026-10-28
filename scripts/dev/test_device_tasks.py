"""device_tasks.py: one registry, task x device matrix, check, add (DEVICE_TASKS.md)."""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import device_tasks as dt
import c_drive_guard as g

REG = {"devices": ["JIS-DESKTOP", "JIS-NUC"], "tasks": []}


def task(i, applies, verify="x"):
    return {"id": i, "what": "w", "run": "r", "verify": verify, "applies_to": applies, "added": "2026-10-28", "by_hook": "manual"}


class DeviceTasksTest(unittest.TestCase):
    def test_task_for_x_is_in_the_matrix_for_x_and_not_y(self):
        reg = copy.deepcopy(REG)
        dt.add_task(reg, task("only-nuc", ["JIS-NUC"]))
        m = dt.matrix(reg, [])
        row = [r for r in m if r[0] == "only-nuc"][0]
        self.assertEqual(m[0], ["task", "JIS-DESKTOP", "JIS-NUC"])
        self.assertEqual(row[1:], ["-", "UNKNOWN"])
        self.assertEqual(dt.check(reg, "JIS-NUC", lambda c: 0), [("only-nuc", "DONE")])
        self.assertEqual(dt.check(reg, "JIS-DESKTOP", lambda c: 0), [])

    def test_all_covers_a_newly_added_device_and_old_names_match(self):
        reg = copy.deepcopy(REG)
        dt.add_task(reg, task("everyone", "all"))
        self.assertFalse(dt.applies(reg["tasks"][0], "JIS-LAPTOP", reg["devices"]))
        reg["devices"].append("JIS-LAPTOP")
        self.assertTrue(dt.applies(reg["tasks"][0], "JIS-LAPTOP", reg["devices"]))
        self.assertTrue(dt.applies(reg["tasks"][0], "DESKTOP-F7IU69N", reg["devices"]))   # old name of the laptop
        self.assertTrue(dt.applies(reg["tasks"][0], "jis-nb", reg["devices"]))             # old name of the desktop

    def test_failing_verify_is_missing_no_verify_or_crash_is_unknown(self):
        reg = copy.deepcopy(REG)
        dt.add_task(reg, task("bad", "all", "fails"))
        dt.add_task(reg, task("man", "all", "manual"))
        dt.add_task(reg, task("hang", "all", "hangs"))
        rc = {"fails": 3, "hangs": None}
        got = dict(dt.check(reg, "JIS-NUC", lambda c: rc[c]))
        self.assertEqual(got, {"bad": "MISSING", "man": "UNKNOWN", "hang": "UNKNOWN"})

    def test_matrix_fills_from_the_latest_report_per_host(self):
        reg = copy.deepcopy(REG)
        dt.add_task(reg, task("a", "all"))
        rows = [{"t": "20261028T010000Z", "kind": "ack", "id": "device-tasks", "host": "jis-nb", "dt": {"a": "MISSING"}},
                {"t": "20261028T020000Z", "kind": "ack", "id": "device-tasks", "host": "jis-desktop", "dt": {"a": "DONE"}},
                {"t": "20261028T030000Z", "kind": "ack", "id": "b-123456", "host": "jis-nuc", "dt": {"a": "DONE"}}]
        self.assertEqual(dt.matrix(reg, rows)[1], ["a", "DONE", "UNKNOWN"])

    def test_add_refuses_duplicates_and_missing_fields_and_prints_the_broadcast(self):
        reg = copy.deepcopy(REG)
        line = dt.add_task(reg, task("t1", ["JIS-NUC"]))
        self.assertIn("mts_signal.py broadcast", line)
        self.assertIn("--prio high", line)
        self.assertIn("t1", line)
        with self.assertRaises(ValueError):
            dt.add_task(reg, task("t1", "all"))
        with self.assertRaises(ValueError):
            dt.add_task(reg, task("t2", "all", verify=""))

    def test_add_command_writes_the_registry_without_sending(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.json"
            p.write_text(json.dumps(REG), encoding="utf-8")
            old = dt.REG
            dt.REG = p
            try:
                rc = dt.main(["add", "--id", "z", "--what", "w", "--run", "r", "--verify", "v", "--applies", "JIS-NUC", "--no-send"])
                self.assertEqual(rc, 0)
                self.assertEqual(dt.load_reg(p)["tasks"][0]["id"], "z")
                self.assertEqual(dt.main(["add-device", "JIS-NEW"]), 0)
                self.assertIn("JIS-NEW", dt.load_reg(p)["devices"])
            finally:
                dt.REG = old

    def test_shipped_registry_is_valid_one_entry_per_id(self):
        reg = dt.load_reg(Path(dt.__file__).resolve().parents[2] / "MyTradingSys" / "system" / "DEVICE_TASKS.json")
        ids = [t["id"] for t in reg["tasks"]]
        self.assertEqual(len(ids), len(set(ids)))
        for t in reg["tasks"]:
            for k in ("id", "what", "run", "verify", "applies_to", "added", "by_hook"):
                self.assertTrue(t.get(k), (t.get("id"), k))
            self.assertNotIn("&&", t["run"])
            self.assertNotIn("&&", t["verify"])

    def test_daily_hook_starts_the_report_only_check(self):
        started = []
        with tempfile.TemporaryDirectory() as d:
            old = (g.STAMP, g.start_apply_detached, g.start_check_detached)
            g.STAMP = Path(d) / "stamp"
            g.start_apply_detached = lambda: None
            g.start_check_detached = lambda: started.append(1)
            os.environ["MTS_C_MIN_FREE_GB"] = "0"
            try:
                g.main(["hook"])
                g.main(["hook"])
            finally:
                os.environ.pop("MTS_C_MIN_FREE_GB", None)
                g.STAMP, g.start_apply_detached, g.start_check_detached = old
        self.assertEqual(len(started), 1)

    def test_logon_status_check_fails_when_not_installed(self):
        self.assertEqual(g.status(key=r"Software\MTSNoSuchKey", name="nope", check=True), 1)
        self.assertEqual(g.status(key=r"Software\MTSNoSuchKey", name="nope"), 0)


if __name__ == "__main__":
    unittest.main()
