"""Offline tests: testnet blind-halt auto-recovery in daily_loss_monitor (operator 2026-10-17, card
blind-monitor-halt-recovery; policy: MyTradingSys/system/BLIND_HALT_POLICY.md). No exchange, no real halt files:
every path is a temp file, the clock is injected.
Rule under test: the monitor clears ONLY its own blind halt (kind "blind"), testnet only, after 30 min of clean
reads; a real loss halt is never cleared; max 2 clears per UTC day; a re-blind within 60 min of a clear stays.
Run: python -m pytest MyTradingSys/execution/test_dlm_blind_recovery.py"""
import json
import shutil
import sys
import tempfile
import types
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import daily_loss_monitor as dlm  # noqa: E402

T0 = datetime(2026, 10, 17, 10, 0, tzinfo=timezone.utc)
OK = {"ok": True, "state": {"breached_today": False}}


class Clock:
    def __init__(self):
        self.now = T0

    def __call__(self):
        return self.now

    def adv(self, minutes):
        self.now += timedelta(minutes=minutes)


class Base(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.d, True)
        self.halt, self.state = self.d / "HALT_DAILY_LOSS", self.d / "state.json"
        self.hold = self.d / "HALT_DAILY_LOSS.hold"
        self.clock = Clock()
        self.events = []
        p = mock.patch.object(dlm.journal, "append_event", lambda *a, **k: self.events.append((a, k)))
        p.start()
        self.addCleanup(p.stop)
        dlm.save_state({"date": "2026-10-17", "day_start_equity": 1.0, "breached_today": False}, self.state)

    def rec(self, env="test"):
        return dlm.BlindRecovery(env, self.halt, self.state, clock=self.clock, hold_path=self.hold)

    def blind(self):
        dlm.write_blind_halt(self.halt, "2026-10-17", "daily_loss_monitor blind: 20 consecutive failures, last 502",
                             self.clock.now)

    def clean_for(self, rec, minutes, result=OK):
        """One reading per minute for `minutes`+1 readings; returns the last outcome."""
        out = None
        for _ in range(minutes + 1):
            out = rec.note_clean(result)
            self.clock.adv(1)
        return out


class BlindHaltFile(Base):
    def test_blind_halt_is_tagged_and_still_json_for_preflight(self):
        self.blind()
        j = json.loads(self.halt.read_text())
        self.assertEqual((j["kind"], j["owner"]), ("blind", "daily_loss_monitor"))
        for k in ("date", "reason", "ts_iso"):
            self.assertIn(k, j)
        self.assertEqual(dlm.halt_kind(self.halt), "blind")

    def test_kinds(self):
        self.assertEqual(dlm.halt_kind(self.halt), "none")
        dlm.write_halt(self.halt, "2026-10-17", "daily loss -600", self.clock.now)
        self.assertEqual(dlm.halt_kind(self.halt), "loss")           # no kind field = a loss halt
        self.halt.write_text("{torn", encoding="utf-8")
        self.assertEqual(dlm.halt_kind(self.halt), "loss")           # unreadable fails closed: never cleared
        self.halt.write_text(json.dumps({"kind": "blind", "owner": "someone_else"}), encoding="utf-8")
        self.assertEqual(dlm.halt_kind(self.halt), "loss")           # not ours

    def test_blind_never_overwrites_a_loss_halt(self):
        dlm.write_halt(self.halt, "2026-10-17", "daily loss -600", self.clock.now)
        before = self.halt.read_text()
        self.assertFalse(dlm.write_blind_halt(self.halt, "2026-10-17", "blind", self.clock.now))
        self.assertEqual(self.halt.read_text(), before)


class Clearing(Base):
    def test_clears_after_30_clean_minutes_not_before(self):
        self.blind()
        r = self.rec()
        for _ in range(30):                                  # readings at minute 0..29: window under 30 min
            self.assertIn(r.note_clean(OK), ("waiting",))
            self.clock.adv(1)
        self.assertTrue(self.halt.exists())
        self.assertEqual(r.note_clean(OK), "cleared")        # minute 30
        self.assertFalse(self.halt.exists())
        self.assertEqual(len(dlm.load_state(self.state)["blind_clears"]), 1)
        self.assertTrue(self.events)                         # journalled

    def test_failure_resets_the_clean_window(self):
        self.blind()
        r = self.rec()
        self.clean_for(r, 25)
        r.note_failure()
        self.clean_for(r, 25)
        self.assertTrue(self.halt.exists())
        self.clean_for(r, 10)
        self.assertFalse(self.halt.exists())

    def test_restart_does_not_shortcut_the_window(self):
        self.blind()
        r = self.rec()
        self.clean_for(r, 29)
        r2 = self.rec()                              # process restart: new object, no memory of the clean time
        self.assertEqual(r2.note_clean(OK), "waiting")
        self.assertTrue(self.halt.exists())

    def test_loss_halt_never_cleared(self):
        dlm.write_halt(self.halt, "2026-10-17", "daily loss -600", self.clock.now)
        r = self.rec()
        self.clean_for(r, 120)
        self.assertTrue(self.halt.exists())

    def test_breach_reading_resets_and_blocks(self):
        self.blind()
        r = self.rec()
        self.clean_for(r, 25)
        bad = {"ok": False, "state": {"breached_today": True}}
        self.assertNotEqual(r.note_clean(bad), "cleared")
        self.clock.adv(10)
        self.assertEqual(r.note_clean(OK), "waiting")          # window restarted by the breach reading
        self.assertTrue(self.halt.exists())

    def test_breached_flag_blocks_even_if_reading_ok(self):
        self.blind()
        r = self.rec()
        self.clean_for(r, 60, result={"ok": True, "state": {"breached_today": True}})
        self.assertTrue(self.halt.exists())

    def test_non_trade_balance_move_is_not_a_loss(self):
        # a transfer/deposit moves equity but not the transaction-log P&L: the reading is ok, so it may clear
        self.blind()
        r = self.rec()
        self.assertEqual(self.clean_for(r, 30), "cleared")

    def test_mainnet_never_clears_and_keeps_old_halt_format(self):
        mh = self.d / "HALT_DAILY_LOSS_MAINNET"
        dlm.write_halt(mh, "2026-10-17", "daily_loss_monitor blind: 3 consecutive failures", self.clock.now)
        self.assertNotIn("kind", json.loads(mh.read_text()))
        r = dlm.BlindRecovery("mainnet", mh, self.state, clock=self.clock, hold_path=self.hold)
        self.clean_for(r, 120)
        self.assertTrue(mh.exists())
        self.assertEqual(dlm.halt_kind(mh), "loss")

    def test_mainnet_never_clears_even_a_blind_tagged_file(self):
        mh = self.d / "HALT_DAILY_LOSS_MAINNET"
        dlm.write_blind_halt(mh, "2026-10-17", "blind", self.clock.now)
        r = dlm.BlindRecovery("mainnet", mh, self.state, clock=self.clock, hold_path=self.hold)
        self.clean_for(r, 120)
        self.assertTrue(mh.exists())

    def test_hold_file_pins_the_halt(self):
        self.blind()
        self.hold.write_text("operator pin")
        r = self.rec()
        self.assertEqual(self.clean_for(r, 60), "held")
        self.assertTrue(self.halt.exists())

    def test_max_two_clears_per_day(self):
        r = self.rec()
        for _ in range(2):
            self.blind()
            self.assertEqual(self.clean_for(r, 30), "cleared")
            self.clock.adv(120)                                  # outside the flap window
        self.blind()
        self.assertEqual(self.clean_for(r, 60), "cap")
        self.assertTrue(self.halt.exists())

    def test_reblind_within_60_min_of_a_clear_stays(self):
        r = self.rec()
        self.blind()
        self.assertEqual(self.clean_for(r, 30), "cleared")
        self.blind()                                             # blind again right after the clear (flap)
        self.assertEqual(self.clean_for(r, 60), "flap")
        self.assertTrue(self.halt.exists())

    def test_unreadable_state_does_not_clear(self):
        self.blind()
        r = self.rec()
        self.clean_for(r, 25)
        self.state.write_text("{torn", encoding="utf-8")
        self.assertNotEqual(self.clean_for(r, 10), "cleared")
        self.assertTrue(self.halt.exists())


class _Done(BaseException):
    pass


class FakeDo(types.ModuleType):
    def __init__(self, env):
        super().__init__("deribit_orders")
        self.env = env

    def active_env(self):
        return self.env

    def select_environment(self, mainnet):
        self.env = "mainnet" if mainnet else "test"

    def authenticate(self):
        return "tok"


class MainLoop(Base):
    def run_main(self, env, script, argv=()):
        """script: list of 'fail' / 'ok'; after it is exhausted the loop ends."""
        fake, it = FakeDo(env), iter(script)

        def run_once(*a, **k):
            try:
                s = next(it)
            except StopIteration:
                raise _Done
            if s == "fail":
                raise RuntimeError("HTTP 502")
            return {"ok": True, "state": {"breached_today": False}}

        def sleep(_):
            self.clock.adv(1)
        halt = self.d / ("HALT_DAILY_LOSS_MAINNET" if env == "mainnet" else "HALT_DAILY_LOSS")
        with mock.patch.dict(sys.modules, {"deribit_orders": fake}), \
                mock.patch.object(dlm, "run_once", run_once), \
                mock.patch.object(dlm, "_utc_now", self.clock), \
                mock.patch.object(dlm, "format_breach_report", lambda r: ""), \
                mock.patch.object(dlm, "refresh_named_accounts", lambda do, cur, labels: {}), \
                mock.patch.object(dlm, "named_account_labels", lambda: []), \
                mock.patch.object(dlm, "HALT_PATH", halt), mock.patch.object(dlm, "HALT_PATH_MAINNET", halt), \
                mock.patch.object(dlm, "STATE_PATH", self.state), \
                mock.patch.object(dlm, "HALT_HOLD_PATH", self.hold), \
                mock.patch.object(dlm.time, "sleep", sleep):
            try:
                rc = dlm.main(list(argv) + (["--mainnet"] if env == "mainnet" else []))
            except _Done:
                rc = None
        return rc, halt

    def test_testnet_blind_halt_then_clean_reads_clears_and_process_stays_alive(self):
        cap = dlm.MAX_CONSECUTIVE_FAILURES_TESTNET
        rc, halt = self.run_main("test", ["fail"] * cap + ["ok"] * 35)
        self.assertIsNone(rc)                          # still running: it did not exit(1) at the blind halt
        self.assertFalse(halt.exists())                # cleared after 30 clean minutes
        self.assertEqual(len(dlm.load_state(self.state)["blind_clears"]), 1)

    def test_testnet_stays_halted_before_30_minutes(self):
        cap = dlm.MAX_CONSECUTIVE_FAILURES_TESTNET
        rc, halt = self.run_main("test", ["fail"] * cap + ["ok"] * 10)
        self.assertIsNone(rc)
        self.assertEqual(dlm.halt_kind(halt), "blind")

    def test_api_errors_keep_the_halt(self):
        cap = dlm.MAX_CONSECUTIVE_FAILURES_TESTNET
        script = ["fail"] * cap + (["ok"] * 20 + ["fail"]) * 3
        rc, halt = self.run_main("test", script)
        self.assertEqual(dlm.halt_kind(halt), "blind")

    def test_once_mode_and_mainnet_still_exit_and_halt(self):
        rc, halt = self.run_main("test", ["fail"], argv=["--once"])
        self.assertEqual(rc, 1)
        with mock.patch("builtins.input", lambda *a: "MAINNET"):
            rc, halt = self.run_main("mainnet", ["fail"] * 3)
        self.assertEqual(rc, 1)
        self.assertEqual(dlm.halt_kind(halt), "loss")  # mainnet halt carries no blind tag: never auto-cleared


if __name__ == "__main__":
    unittest.main()
