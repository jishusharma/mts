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

    # --- B148 part 5 (operator D10 2026-10-09: heartbeat older than 10 minutes = dead, whatever the pid says) ---
    NOW = datetime(2026, 10, 9, 12, 0, 0, tzinfo=timezone.utc)

    def _at(self, seconds_before):
        from datetime import timedelta
        return self.NOW - timedelta(seconds=seconds_before)

    def test_default_limit_is_ten_minutes(self):
        self.assertEqual(hb.DEFAULT_MAX_AGE_S, 600)

    def test_reused_pid_with_stale_beat_is_not_live(self):
        # the manager crashed 11 min ago; Windows handed its pid to another process, so pid_alive() says True
        hb.write_heartbeat("p1", account="fabio", pid=77, hb_dir=self.dir, now=self._at(660))
        self.assertEqual(hb.live_accounts(self.dir, alive=lambda pid: True, now=self.NOW), set())

    def test_fresh_beat_with_live_pid_is_live(self):
        hb.write_heartbeat("p1", account="fabio", pid=77, hb_dir=self.dir, now=self._at(30))
        self.assertEqual(hb.live_accounts(self.dir, alive=lambda pid: True, now=self.NOW), {"fabio"})

    def test_beat_exactly_at_the_limit_is_still_live_one_second_over_is_not(self):
        hb.write_heartbeat("p1", account="a", pid=1, hb_dir=self.dir, now=self._at(600))
        hb.write_heartbeat("p2", account="b", pid=2, hb_dir=self.dir, now=self._at(601))
        self.assertEqual(hb.live_accounts(self.dir, alive=lambda pid: True, now=self.NOW), {"a"})

    def test_fresh_beat_with_dead_pid_is_still_dead(self):
        hb.write_heartbeat("p1", account="fabio", pid=77, hb_dir=self.dir, now=self._at(5))
        self.assertEqual(hb.live_accounts(self.dir, alive=lambda pid: False, now=self.NOW), set())

    def test_legacy_heartbeat_without_beat_field_stays_pid_only(self):
        # managers started before this change never refresh their file: they must not be called dead by age
        (self.dir).mkdir(parents=True, exist_ok=True)
        (self.dir / "old.json").write_text(json.dumps({"plan_id": "old", "account": "fabio", "pid": 5,
                                                       "started_utc": self._at(86400).isoformat()}), encoding="utf-8")
        self.assertEqual(hb.live_accounts(self.dir, alive=lambda pid: True, now=self.NOW), {"fabio"})

    def test_unparseable_or_future_beat_fails_open(self):
        (self.dir).mkdir(parents=True, exist_ok=True)
        for name, beat in (("junk", "not-a-date"), ("fut", "2099-01-01T00:00:00+00:00"), ("naive", "2026-10-09T11:59:00")):
            (self.dir / (name + ".json")).write_text(json.dumps({"plan_id": name, "account": name, "pid": 5,
                                                                 "beat_utc": beat}), encoding="utf-8")
        self.assertEqual(hb.live_accounts(self.dir, alive=lambda pid: True, now=self.NOW), {"junk", "fut", "naive"})

    def test_max_age_none_disables_the_age_rule(self):
        hb.write_heartbeat("p1", account="fabio", pid=77, hb_dir=self.dir, now=self._at(99999))
        self.assertEqual(hb.live_accounts(self.dir, alive=lambda pid: True, max_age_s=None, now=self.NOW), {"fabio"})

    def test_beat_refreshes_only_the_beat_time(self):
        hb.write_heartbeat("p1", account="fabio", pid=77, hb_dir=self.dir, now=self._at(900))
        self.assertTrue(hb.beat("p1", hb_dir=self.dir, now=self.NOW))
        d = json.loads((self.dir / "p1.json").read_text(encoding="utf-8"))
        self.assertEqual((d["account"], d["pid"]), ("fabio", 77))
        self.assertTrue(d["started_utc"].startswith("2026-10-09T11:45:00"))
        self.assertTrue(d["beat_utc"].startswith("2026-10-09T12:00:00"))
        self.assertEqual(hb.live_accounts(self.dir, alive=lambda pid: True, now=self.NOW), {"fabio"})

    def test_beat_does_not_resurrect_a_removed_heartbeat(self):
        self.assertFalse(hb.beat("gone", hb_dir=self.dir, now=self.NOW))
        self.assertFalse((self.dir / "gone.json").exists())

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
