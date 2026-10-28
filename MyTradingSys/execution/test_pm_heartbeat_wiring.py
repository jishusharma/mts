"""Offline tests: position_manager.manage() owns a heartbeat file for its lifetime (hb1)."""
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pm_heartbeat
import position_manager as pm


class TestManageHeartbeat(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="pm_hbw_")) / "hbs"
        self.addCleanup(shutil.rmtree, self.dir.parent, True)
        p = mock.patch.object(pm_heartbeat, "DEFAULT_HB_DIR", self.dir)
        p.start()
        self.addCleanup(p.stop)
        self.f = self.dir / "planX.json"

    def test_exists_during_and_gone_after_normal_exit(self):
        seen = {}

        def impl(*a, **k):
            seen["during"] = self.f.exists()
            seen["rec"] = pm_heartbeat.read_heartbeats(self.dir)
            return {"status": "managing"}

        with mock.patch.dict(os.environ, {"MTS_ACCOUNT": "fabio"}), mock.patch.object(pm, "_manage_impl", impl):
            self.assertEqual(pm.manage("planX")["status"], "managing")
        self.assertTrue(seen["during"])
        self.assertEqual(seen["rec"][0]["account"], "fabio")
        self.assertEqual(seen["rec"][0]["pid"], os.getpid())
        self.assertFalse(self.f.exists())

    def test_default_account_when_unset(self):
        env = {k: v for k, v in os.environ.items() if k != "MTS_ACCOUNT"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(pm, "_manage_impl", lambda *a, **k: {}):
            pm.manage("planX")
            # gone after; check live_accounts label via a fresh write with same account rule
        pm_heartbeat.write_heartbeat("planX", account=None, hb_dir=self.dir)
        self.assertEqual(pm_heartbeat.live_accounts(self.dir, alive=lambda p: True), {"default"})

    def test_gone_after_exception_and_halt(self):
        for exc in (RuntimeError("boom"), pm.ManagerHalted("halt")):
            def impl(*a, **k):
                self.assertTrue(self.f.exists())
                raise exc
            with mock.patch.object(pm, "_manage_impl", impl):
                with self.assertRaises(type(exc)):
                    pm.manage("planX")
            self.assertFalse(self.f.exists(), repr(exc))

    def test_heartbeat_write_failure_does_not_stop_manager(self):
        with mock.patch.object(pm_heartbeat, "write_heartbeat", side_effect=OSError("disk")), \
                mock.patch.object(pm, "_manage_impl", lambda *a, **k: {"ok": 1}):
            self.assertEqual(pm.manage("planX"), {"ok": 1})

    # --- B148 part 5: the running manager must keep refreshing beat_utc, or the age rule would call it dead ---
    def test_refresh_is_throttled_and_well_inside_the_age_limit(self):
        self.assertLessEqual(pm.HEARTBEAT_REFRESH_SECONDS * 5, pm_heartbeat.DEFAULT_MAX_AGE_S)
        calls = []
        with mock.patch.object(pm_heartbeat, "beat", lambda plan_id, **k: calls.append(plan_id) or True):
            t = pm._beat_heartbeat("planX", 1000.0, now=1000.0 + pm.HEARTBEAT_REFRESH_SECONDS - 1)
            self.assertEqual((calls, t), ([], 1000.0))            # too soon: no write, last unchanged
            t = pm._beat_heartbeat("planX", 1000.0, now=1000.0 + pm.HEARTBEAT_REFRESH_SECONDS)
            self.assertEqual((calls, t), (["planX"], 1000.0 + pm.HEARTBEAT_REFRESH_SECONDS))

    def test_refresh_failure_never_stops_the_manager(self):
        with mock.patch.object(pm_heartbeat, "beat", side_effect=OSError("disk")):
            t = pm._beat_heartbeat("planX", 0.0, now=10_000.0)
        self.assertEqual(t, 10_000.0)                              # no exception, and no retry storm every 2 s poll

    def test_poll_loop_calls_the_refresh_every_iteration(self):
        import inspect
        src = inspect.getsource(pm._manage_impl)
        self.assertIn("_beat_heartbeat(plan_id", src)
        self.assertLess(src.index("_beat_heartbeat(plan_id"), src.index("time.sleep(POLL_INTERVAL_SECONDS)"))


if __name__ == "__main__":
    unittest.main()
