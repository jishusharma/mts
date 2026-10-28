"""Offline tests for the daily_loss_monitor blind-halt failure cap (no exchange: deribit_orders is faked).
2026-10-07 19:24Z a DNS blip (3 x getaddrinfo failures, 90 s) wrote HALT_DAILY_LOSS and stopped all testnet trading.
Testnet now tolerates MAX_CONSECUTIVE_FAILURES_TESTNET failures; mainnet keeps MAX_CONSECUTIVE_FAILURES (unchanged).
Run: python -m pytest MyTradingSys/execution/test_dlm_failure_cap.py"""
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import daily_loss_monitor as dlm  # noqa: E402


class _Done(BaseException):
    """Ends main()'s loop; BaseException so the monitor's except Exception does not count it."""


class FakeDo(types.ModuleType):
    def __init__(self, env):
        super().__init__("deribit_orders")
        self.env = env
        self.auth_calls = 0

    def active_env(self):
        return self.env

    def select_environment(self, mainnet):
        self.env = "mainnet" if mainnet else "test"

    def authenticate(self):
        self.auth_calls += 1
        return "tok"


class FailureCapTest(unittest.TestCase):
    def run_main(self, env, fail_n, argv=()):
        """fail_n run_once failures, then one success that ends the loop via --once semantics (StopIteration)."""
        fake = FakeDo(env)
        calls = {"n": 0}

        def run_once(*a, **k):
            calls["n"] += 1
            if calls["n"] <= fail_n:
                raise RuntimeError("transport error: getaddrinfo failed")
            raise _Done   # recovered: leave the infinite loop
        halts = []
        with mock.patch.dict(sys.modules, {"deribit_orders": fake}), \
                mock.patch.object(dlm, "run_once", run_once), \
                mock.patch.object(dlm, "write_halt", lambda p, d, r, n: halts.append((p, r))), \
                mock.patch.object(dlm, "write_blind_halt", lambda p, d, r, n: halts.append((p, r)) or True), \
                mock.patch.object(dlm.time, "sleep", lambda s: None):
            try:
                rc = dlm.main(list(argv) + (["--mainnet"] if env == "mainnet" else []))
            except _Done:
                rc = None
        return rc, halts, calls["n"]

    def test_testnet_survives_three_failures(self):
        rc, halts, n = self.run_main("test", 3)
        self.assertEqual(halts, [])
        self.assertIsNone(rc)
        self.assertEqual(n, 4)

    def test_testnet_halts_at_testnet_cap(self):
        cap = dlm.MAX_CONSECUTIVE_FAILURES_TESTNET
        rc, halts, n = self.run_main("test", cap + 5)
        # 2026-10-17: testnet stays alive after the blind halt (so it can clear it); mainnet still exits 1
        self.assertEqual((rc, n, len(halts)), (None, cap + 6, 1))
        self.assertEqual(halts[0][0], dlm.HALT_PATH)
        self.assertIn(f"{cap} consecutive failures", halts[0][1])

    def test_mainnet_cap_unchanged(self):
        self.assertEqual(dlm.MAX_CONSECUTIVE_FAILURES, 3)
        with mock.patch("builtins.input", lambda *a: "MAINNET"):
            rc, halts, n = self.run_main("mainnet", 10)
        self.assertEqual((rc, n, len(halts)), (1, 3, 1))
        self.assertEqual(halts[0][0], dlm.HALT_PATH_MAINNET)

    def test_testnet_cap_is_bounded(self):
        # fail closed still: at the 30 s poll the blind window stays under 15 minutes
        self.assertTrue(3 < dlm.MAX_CONSECUTIVE_FAILURES_TESTNET * dlm.POLL_INTERVAL_SECONDS <= 900)

    def test_failure_count_resets_after_success(self):
        cap = dlm.MAX_CONSECUTIVE_FAILURES_TESTNET
        seq = [True] * (cap - 1) + [False] + [True] * (cap - 1)   # True = fail
        fake = FakeDo("test")
        it = iter(seq)

        def run_once(*a, **k):
            try:
                fail = next(it)
            except StopIteration:
                raise KeyboardInterrupt
            if fail:
                raise RuntimeError("blip")
            return {"ok": True}
        halts = []
        with mock.patch.dict(sys.modules, {"deribit_orders": fake}), \
                mock.patch.object(dlm, "run_once", run_once), \
                mock.patch.object(dlm, "format_breach_report", lambda r: ""), \
                mock.patch.object(dlm, "write_halt", lambda p, d, r, n: halts.append(r)), \
                mock.patch.object(dlm.time, "sleep", lambda s: None):
            with self.assertRaises(KeyboardInterrupt):
                dlm.main([])
        self.assertEqual(halts, [])


if __name__ == "__main__":
    unittest.main()
