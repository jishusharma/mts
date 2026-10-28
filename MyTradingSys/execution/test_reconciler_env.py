"""Offline tests for reconciler --mainnet and env refusal (spec 127). Derived from the spec.
Needs journal.py with plan_env/assert_env/EnvMismatch (spec 126) promoted first."""
import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import journal
import reconciler


class Env:
    """Patches reconciler.do: records every exchange call; env is configurable."""

    def __init__(self, env="test", select_raises=None):
        self.env, self.calls, self.select_raises, self.selected = env, [], select_raises, []

    def install(self, tc):
        d = reconciler.do
        for name, fn in {
            "active_env": lambda: self.env,
            "authenticate": lambda: self.calls.append("authenticate") or "tok",
            "get_order_state": lambda token, oid: self.calls.append("get_order_state") or {},
            "get_position": lambda token, instrument="BTC-PERPETUAL": self.calls.append("get_position") or {"size": 0},
            "get_open_orders": lambda token, instrument="BTC-PERPETUAL", type_="all":
                self.calls.append("get_open_orders") or [],
            "select_environment": self._select,
        }.items():
            p = mock.patch.object(d, name, fn)
            p.start()
            tc.addCleanup(p.stop)

    def _select(self, mainnet=False):
        self.selected.append(mainnet)
        if self.select_raises:
            raise self.select_raises
        return "mainnet" if mainnet else "test"


class ReconcilerEnvTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="rec_env_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        p = mock.patch.object(journal, "JOURNAL_DIR", self.tmp)
        p.start()
        self.addCleanup(p.stop)

    def _run(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = reconciler.main(argv)
        return rc, out.getvalue()

    def test_mainnet_journal_refused_on_testnet_without_touching_anything(self):
        journal.append_event("pm1", "intent", {"env": "mainnet"})
        before = (self.tmp / "pm1.jsonl").read_text(encoding="utf-8")
        env = Env("test")
        env.install(self)
        with self.assertRaises(journal.EnvMismatch):
            reconciler.reconcile("pm1")
        self.assertEqual(env.calls, [], "no auth / exchange call before the env check")
        self.assertEqual((self.tmp / "pm1.jsonl").read_text(encoding="utf-8"), before,
                         "a refused reconcile must not append mismatch_halt or anything else")

    def test_testnet_journal_refused_on_mainnet(self):
        journal.append_event("pt1", "intent", {"env": "test"})
        env = Env("mainnet")
        env.install(self)
        with self.assertRaises(journal.EnvMismatch):
            reconciler.reconcile("pt1")
        self.assertEqual(env.calls, [])

    def test_matching_env_reconciles_ok(self):
        journal.append_event("ok1", "intent", {"env": "mainnet"})
        env = Env("mainnet")
        env.install(self)
        res = reconciler.reconcile("ok1")
        self.assertEqual(res["status"], "reconciled_ok")
        self.assertIn("authenticate", env.calls)

    def test_main_mainnet_flag_selects_mainnet_then_reconciles(self):
        journal.append_event("ok2", "intent", {"env": "mainnet"})
        env = Env("mainnet")
        env.install(self)
        rc, out = self._run(["ok2", "--mainnet"])
        self.assertEqual(rc, 0)
        self.assertEqual(env.selected, [True])
        self.assertIn("OK", out)

    def test_main_without_flag_does_not_select_mainnet(self):
        journal.append_event("ok3", "intent", {"env": "test"})
        env = Env("test")
        env.install(self)
        rc, _ = self._run(["ok3"])
        self.assertEqual(rc, 0)
        self.assertNotIn(True, env.selected)

    def test_main_env_mismatch_returns_2_and_says_refused(self):
        journal.append_event("pm2", "intent", {"env": "mainnet"})
        env = Env("test")
        env.install(self)
        rc, out = self._run(["pm2"])
        self.assertEqual(rc, 2)
        self.assertIn("REFUSED", out)
        self.assertEqual(env.calls, [])

    def test_main_select_environment_refusal_returns_1_before_reconcile(self):
        journal.append_event("pm3", "intent", {"env": "mainnet"})
        env = Env("test", select_raises=RuntimeError("REFUSED: no secret"))
        env.install(self)
        rc, out = self._run(["pm3", "--mainnet"])
        self.assertEqual(rc, 1)
        self.assertIn("REFUSED", out)
        self.assertEqual(env.calls, [])


if __name__ == "__main__":
    unittest.main()
