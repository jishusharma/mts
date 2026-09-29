"""Offline tests for pm_heartbeat (spec 121). Derived from the spec, not from the implementation."""
import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import pm_heartbeat as hb


class TestPmHeartbeat(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="pm_hb_")) / "hbs"  # dir does not exist yet
        self.addCleanup(shutil.rmtree, self.dir.parent, True)

    def test_write_creates_dir_and_json(self):
        now = datetime(2026, 9, 29, 10, 0, 0, tzinfo=timezone.utc)
        p = hb.write_heartbeat("L-mkt-0929-1000", account="fabio", pid=4321, hb_dir=self.dir, now=now)
        self.assertEqual(p, self.dir / "L-mkt-0929-1000.json")
        self.assertTrue(p.exists())
        d = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(d["plan_id"], "L-mkt-0929-1000")
        self.assertEqual(d["account"], "fabio")
        self.assertEqual(d["pid"], 4321)
        self.assertTrue(d["started_utc"].startswith("2026-09-29T10:00:00"))
        self.assertNotIn(b"\r\n", p.read_bytes())

    def test_default_pid_is_current_process(self):
        p = hb.write_heartbeat("plan1", hb_dir=self.dir)
        self.assertEqual(json.loads(p.read_text(encoding="utf-8"))["pid"], os.getpid())

    def test_no_tmp_files_left_behind(self):
        hb.write_heartbeat("plan1", pid=1, hb_dir=self.dir)
        self.assertEqual([x.name for x in self.dir.iterdir()], ["plan1.json"])

    def test_bad_plan_id_rejected(self):
        for bad in ["", "../x", "a/b", "a\\b", "x" * 81, "a b"]:
            with self.assertRaises(ValueError, msg=repr(bad)):
                hb.hb_path(bad, self.dir)

    def test_remove(self):
        hb.write_heartbeat("plan1", pid=1, hb_dir=self.dir)
        self.assertTrue(hb.remove_heartbeat("plan1", self.dir))
        self.assertFalse(hb.remove_heartbeat("plan1", self.dir))  # already gone: False, no raise
        self.assertEqual(hb.read_heartbeats(self.dir), [])

    def test_read_sorted_and_skips_garbage(self):
        hb.write_heartbeat("b-plan", account="fabio", pid=2, hb_dir=self.dir)
        hb.write_heartbeat("a-plan", pid=1, hb_dir=self.dir)
        (self.dir / "junk.json").write_text("{not json", encoding="utf-8")
        (self.dir / "list.json").write_text("[1, 2]", encoding="utf-8")
        got = hb.read_heartbeats(self.dir)
        self.assertEqual([g["plan_id"] for g in got], ["a-plan", "b-plan"])

    def test_read_missing_dir_is_empty(self):
        self.assertEqual(hb.read_heartbeats(self.dir / "nope"), [])

    def test_live_accounts_uses_alive_callable(self):
        hb.write_heartbeat("p-default", pid=10, hb_dir=self.dir)
        hb.write_heartbeat("p-fabio", account="fabio", pid=20, hb_dir=self.dir)
        hb.write_heartbeat("p-dead", account="other", pid=30, hb_dir=self.dir)
        alive = lambda pid: pid in (10, 20)
        self.assertEqual(hb.live_accounts(self.dir, alive=alive), {"default", "fabio"})

    def test_live_accounts_none_alive(self):
        hb.write_heartbeat("p1", account="fabio", pid=20, hb_dir=self.dir)
        self.assertEqual(hb.live_accounts(self.dir, alive=lambda pid: False), set())

    def test_empty_string_account_is_default(self):
        hb.write_heartbeat("p1", account="", pid=10, hb_dir=self.dir)
        self.assertEqual(hb.live_accounts(self.dir, alive=lambda pid: True), {"default"})

    def test_pid_alive_real(self):
        self.assertTrue(hb.pid_alive(os.getpid()))
        # fail-safe: unknown/corrupt pid values are treated as alive
        for bad in (0, -5, None, "12", 1.5):
            self.assertTrue(hb.pid_alive(bad), repr(bad))

    def test_pid_alive_dead_pid(self):
        import subprocess, sys
        p = subprocess.Popen([sys.executable, "-c", "pass"])
        p.wait()
        self.assertFalse(hb.pid_alive(p.pid))


if __name__ == "__main__":
    unittest.main()
