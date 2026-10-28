"""Offline tests for the pre-mainnet audit fixes (tag premainnet1): B1 close-first kill switch,
B2 mainnet kill ignores MTS_ACCOUNT, H1 per-env daily-loss state/HALT. Fake clients only."""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path

import daily_loss_monitor as dlm
import kill_switch
import executor


class OrderStateUnknown(Exception):
    pass


class StopClient:
    """Position 50 with one reduce-only protective stop and one entry order."""
    def __init__(self, close_fails=False, close_leaves=False):
        self.size = 50
        self.orders = {"stop1": True, "entry1": False}  # id -> reduce_only
        self.close_fails, self.close_leaves = close_fails, close_leaves
        self.log = []

    def get_positions(self, token, currency="BTC", kind="future"):
        return [{"instrument_name": "BTC-PERPETUAL", "size": self.size}]

    def get_open_orders(self, token, instrument_name, type_="all"):
        return [{"order_id": k, "reduce_only": v} for k, v in self.orders.items()]

    def cancel(self, token, order_id):
        self.log.append(("cancel", order_id))
        self.orders.pop(order_id)

    def close_position(self, token, instrument_name="BTC-PERPETUAL"):
        self.log.append(("close", instrument_name))
        if self.close_fails:
            raise OrderStateUnknown("timeout")
        if not self.close_leaves:
            self.size = 0
        return {}


class TestB1CloseFirst(unittest.TestCase):
    def test_failed_close_keeps_stop(self):
        c = StopClient(close_fails=True)
        r = kill_switch.kill_all(c, "t")
        self.assertFalse(r["ok"])
        self.assertIn("stop1", c.orders)  # protective stop still live
        self.assertNotIn("stop1", r["cancelled_orders"])
        self.assertEqual(r["protective_orders_kept"], ["stop1"])
        self.assertIn("NOT FLAT", kill_switch.format_kill_report(r))

    def test_close_not_confirmed_flat_keeps_stop(self):
        c = StopClient(close_leaves=True)
        r = kill_switch.kill_all(c, "t")
        self.assertIn("stop1", c.orders)
        self.assertFalse(r["ok"])

    def test_stop_cancelled_last_after_close(self):
        c = StopClient()
        r = kill_switch.kill_all(c, "t")
        self.assertTrue(r["ok"])
        self.assertEqual(c.log[0][0], "close")
        self.assertEqual(c.log[-1], ("cancel", "stop1"))
        self.assertEqual(c.orders, {})

    def test_reread_failure_keeps_stop(self):
        c = StopClient()
        calls = {"n": 0}
        orig = c.get_positions

        def flaky(*a, **k):
            calls["n"] += 1
            if calls["n"] >= 3:  # discovery=1, close-read=2, verify=3
                raise TimeoutError("read down")
            return orig(*a, **k)
        c.get_positions = flaky
        r = kill_switch.kill_all(c, "t")
        self.assertIn("stop1", c.orders)
        self.assertFalse(r["ok"])


class MainnetFake(types.ModuleType):
    def __init__(self):
        super().__init__("deribit_orders")
        self.env_seen = []
        self.selected = False

    def select_environment(self, mainnet=False, kill_only=False):
        self.kill_only = kill_only
        if os.environ.get("MTS_ACCOUNT"):
            raise RuntimeError("REFUSED: named accounts are testnet-only")
        self.selected = True

    def authenticate(self):
        self.env_seen.append(os.environ.get("MTS_ACCOUNT"))
        return "tok"

    def get_positions(self, token, currency="BTC", kind="future"):
        return []

    def get_open_orders(self, *a, **k):
        return []


class TestB2MainnetIgnoresAccount(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.saved_mod = sys.modules.get("deribit_orders")
        self.saved_env = os.environ.get("MTS_ACCOUNT")
        self.fake = MainnetFake()
        sys.modules["deribit_orders"] = self.fake
        os.environ["MTS_ACCOUNT"] = "fabio"

    def tearDown(self):
        if self.saved_mod is not None:
            sys.modules["deribit_orders"] = self.saved_mod
        else:
            sys.modules.pop("deribit_orders", None)
        if self.saved_env is None:
            os.environ.pop("MTS_ACCOUNT", None)
        else:
            os.environ["MTS_ACCOUNT"] = self.saved_env

    def test_mainnet_kill_ignores_stale_account_with_warning(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = kill_switch.main(["--confirm", "KILL", "--mainnet"], halt_path=self.tmp / "HALT")
        self.assertEqual(rc, 0)
        self.assertTrue(self.fake.selected)
        self.assertTrue(self.fake.kill_only)   # kill switch uses the short `kill` confirmation, not the S5 sentence
        self.assertEqual(self.fake.env_seen, [None])
        self.assertIn("WARNING", out.getvalue())
        self.assertEqual(os.environ.get("MTS_ACCOUNT"), "fabio")  # restored for the shell

    def test_mainnet_kill_needs_no_confirm_flag_only_the_typed_word(self):
        with contextlib.redirect_stdout(io.StringIO()):
            rc = kill_switch.main(["--mainnet"], halt_path=self.tmp / "HALT")
        self.assertEqual(rc, 0)
        self.assertTrue(self.fake.kill_only)

    def test_mainnet_kill_wrong_confirm_flag_and_testnet_without_flag_still_refused(self):
        for argv in (["--mainnet", "--confirm", "kill"], ["--confirm", "kill"], []):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(kill_switch.main(argv, halt_path=self.tmp / "HALT2"), 1, argv)
        self.assertFalse(self.fake.selected)


class BreachClient:
    def __init__(self, env):
        self._env = env
        self.kill_calls = 0

    def active_env(self):
        return self._env

    def get_account_summary(self, token, currency="BTC"):
        return {"equity": 1.0, "futures_session_upl": 0.0}

    def get_transaction_log(self, token, currency="BTC", start_ms=0, end_ms=0):
        return [{"type": "trade", "change": -0.001}]  # -0.001 BTC * 60000 = -60 USD

    def get_ticker(self, instrument_name="BTC-PERPETUAL"):
        return {"mark_price": 60000.0}

    def get_positions(self, token, currency="BTC", kind="future"):
        self.kill_calls += 1
        return []

    def get_open_orders(self, *a, **k):
        return []


class TestH1PerEnvState(unittest.TestCase):
    ATTRS = [(dlm, "STATE_PATH"), (dlm, "HALT_PATH"), (dlm, "STATE_PATH_MAINNET"), (dlm, "HALT_PATH_MAINNET"),
             (executor, "HALT_DAILY_LOSS_PATH"), (executor, "HALT_DAILY_LOSS_PATH_MAINNET")]

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.saved = [getattr(m, a) for m, a in self.ATTRS]
        self.saved_journal = dlm.journal.append_event
        dlm.STATE_PATH, dlm.HALT_PATH = self.tmp / "s.json", self.tmp / "HDL"
        dlm.STATE_PATH_MAINNET, dlm.HALT_PATH_MAINNET = self.tmp / "sm.json", self.tmp / "HDLM"
        executor.HALT_DAILY_LOSS_PATH, executor.HALT_DAILY_LOSS_PATH_MAINNET = self.tmp / "HDL", self.tmp / "HDLM"
        dlm.journal.append_event = lambda *a, **k: None
        self.clock = lambda: datetime.now(timezone.utc)

    def tearDown(self):
        for (m, a), v in zip(self.ATTRS, self.saved):
            setattr(m, a, v)
        dlm.journal.append_event = self.saved_journal

    def test_testnet_trip_does_not_mask_mainnet_breach(self):
        t = BreachClient("test")
        rt = dlm.run_once(t, "tok", clock=self.clock, cap_usd=-10.0, pnl_source="transaction_log")
        self.assertFalse(rt["ok"])
        self.assertTrue(dlm.HALT_PATH.exists())
        self.assertFalse(dlm.HALT_PATH_MAINNET.exists())
        m = BreachClient("mainnet")
        rm = dlm.run_once(m, "tok", clock=self.clock, cap_usd=-10.0)
        self.assertFalse(rm["ok"])
        self.assertGreater(m.kill_calls, 0, "mainnet breach must still trigger kill_all")
        self.assertTrue(dlm.HALT_PATH_MAINNET.exists())

    def test_executor_halt_check_is_per_env(self):
        dlm.write_halt(dlm.HALT_PATH, datetime.now(timezone.utc).strftime("%Y-%m-%d"), "x", self.clock())
        orig = executor.do.active_env
        try:
            executor.do.active_env = lambda: "mainnet"
            self.assertEqual([r for r in executor._halt_check_mid_run() if "HALT_DAILY_LOSS" in r], [])
            executor.do.active_env = lambda: "test"
            self.assertTrue([r for r in executor._halt_check_mid_run() if "HALT_DAILY_LOSS" in r])
        finally:
            executor.do.active_env = orig


if __name__ == "__main__":
    unittest.main()
