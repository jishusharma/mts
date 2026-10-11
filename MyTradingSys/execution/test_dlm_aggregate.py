"""Offline tests: daily_loss_monitor caps the AGGREGATE P&L of the main account plus every named testnet subaccount
(operator 2026-10-08). Spec: daily_loss_monitor.py docstring "AGGREGATE OVER NAMED TESTNET SUBACCOUNTS".
Expected numbers: equity source, pnl_usd = (equity_now - day_start_equity) * mark_price (same docstring);
existing threshold DEFAULT_DAILY_LOSS_CAP_USD = -500 (daily_loss_guard.py). No exchange: clients are fakes.
Run: python -m pytest MyTradingSys/execution/test_dlm_aggregate.py"""
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import daily_loss_monitor as dlm  # noqa: E402

NOW = datetime(2026, 10, 8, 9, 0, tzinfo=timezone.utc)
MARK = 60000.0


class Fake:
    def __init__(self, equity=1.0):
        self.equity, self.closed = equity, []

    def active_env(self):
        return "test"

    def get_account_summary(self, token, currency="BTC"):
        return {"equity": self.equity}

    def get_ticker(self, instrument_name="BTC-PERPETUAL"):
        return {"mark_price": MARK}

    def get_positions(self, token, currency="BTC", kind="future"):
        return [{"instrument_name": "BTC-PERPETUAL", "size": 10}]

    def get_open_orders(self, token, instrument_name="BTC-PERPETUAL", type_="all"):
        return []

    def cancel(self, token, order_id):
        return {}

    def close_position(self, token, instrument_name="BTC-PERPETUAL"):
        self.closed.append(instrument_name)
        return {"ok": True}


class AggregateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dlmagg_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        p = mock.patch.object(dlm.journal, "append_event")
        self.journal = p.start()
        self.addCleanup(p.stop)
        self.state, self.halt = self.tmp / "state.json", self.tmp / "HALT_DAILY_LOSS"
        self.main, self.j7, self.j8 = Fake(), Fake(), Fake()

    def run_once(self, accounts=None):
        return dlm.run_once(self.main, "tok", clock=lambda: NOW, state_path=self.state, halt_path=self.halt,
                            accounts=accounts)

    def accts(self):
        return {"jishu_7": (self.j7, "t7"), "jishu_8": (self.j8, "t8")}

    def test_loss_on_jishu_7_alone_halts(self):
        """Failing-first: a -600 USD loss on non-main jishu_7 (main flat) breaches the -500 cap."""
        self.run_once(self.accts())                           # baselines: equity 1.0 everywhere
        self.j7.equity = 0.99                                 # (0.99 - 1.0) * 60000 = -600
        r = self.run_once(self.accts())
        self.assertFalse(r["ok"])
        self.assertAlmostEqual(r["total_pnl_usd"], -600.0)
        self.assertTrue(self.halt.exists())
        self.assertTrue(self.j7.closed)                       # the losing subaccount is flattened

    def test_breach_flattens_every_account_in_the_aggregate(self):
        self.run_once(self.accts())
        self.j7.equity = 0.99
        self.run_once(self.accts())
        self.assertTrue(self.main.closed and self.j7.closed and self.j8.closed)

    def test_sum_breaches_when_no_single_account_does(self):
        self.run_once(self.accts())
        self.main.equity, self.j7.equity = 0.995, 0.995       # -300 + -300 = -600
        r = self.run_once(self.accts())
        self.assertFalse(r["ok"])
        self.assertEqual(r["per_account_pnl_usd"], {"main": -300.0, "jishu_7": -300.0, "jishu_8": 0.0})

    def test_gains_offset_losses_in_the_sum(self):
        self.run_once(self.accts())
        self.j7.equity, self.j8.equity = 0.99, 1.005          # -600 + 300 = -300
        r = self.run_once(self.accts())
        self.assertTrue(r["ok"])
        self.assertAlmostEqual(r["total_pnl_usd"], -300.0)
        self.assertFalse(self.halt.exists())

    def test_inside_cap_no_halt(self):
        self.run_once(self.accts())
        self.j7.equity = 0.995                                # -300
        self.assertTrue(self.run_once(self.accts())["ok"])
        self.assertFalse(self.halt.exists())

    def test_baselines_persist_per_account(self):
        self.j8.equity = 2.0
        self.run_once(self.accts())
        st = json.loads(self.state.read_text(encoding="utf-8"))
        self.assertEqual(st["accounts"], {"jishu_7": 1.0, "jishu_8": 2.0})
        self.assertEqual(st["day_start_equity"], 1.0)         # main baseline keeps its old place

    def test_unreadable_subaccount_fails_the_iteration(self):
        self.run_once(self.accts())

        def boom(*a, **k):
            raise ConnectionError("down")
        self.j8.get_account_summary = boom
        with self.assertRaises(ConnectionError):
            self.run_once(self.accts())

    def test_no_accounts_is_the_old_single_account_behaviour(self):
        self.run_once()
        self.main.equity = 0.99
        r = self.run_once()
        self.assertFalse(r["ok"])
        self.assertNotIn("accounts", json.loads(self.state.read_text(encoding="utf-8")))
        self.assertNotIn("per_account_pnl_usd", r)


class DiscoveryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dlmdisc_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_labels_from_config_with_secret_only(self):
        cfg = self.tmp / "cfg.json"
        cfg.write_text(json.dumps({"accounts": {"a:": "jishu_7", "b:": "jishu_8", "c:": "jishu_7", "d:": "Bad X",
                                                "e:": "../x"}}), encoding="utf-8")
        (self.tmp / "testnet_jishu_7.secret.json").write_text("{}", encoding="utf-8")
        self.assertEqual(dlm.named_account_labels(cfg, self.tmp), ["jishu_7"])

    def test_unreadable_config_keeps_last_good_list_and_never_returns_empty(self):
        cfg = self.tmp / "cfg2.json"
        cfg.write_text(json.dumps({"accounts": {"a:": "jishu_7"}}), encoding="utf-8")
        (self.tmp / "testnet_jishu_7.secret.json").write_text("{}", encoding="utf-8")
        self.assertEqual(dlm.named_account_labels(cfg, self.tmp), ["jishu_7"])
        cfg.write_text("{ not json", encoding="utf-8")
        self.assertEqual(dlm.named_account_labels(cfg, self.tmp), ["jishu_7"])   # B148: not []
        with self.assertRaises(RuntimeError):                                    # no earlier good read: fail closed
            dlm.named_account_labels(self.tmp / "missing.json", self.tmp)

    def test_auth_per_label_with_env_set_and_restored(self):
        seen = []
        do = types.SimpleNamespace(authenticate=lambda: (seen.append(os.environ.get("MTS_ACCOUNT")), "t")[1])
        saved = os.environ.get("MTS_ACCOUNT")
        os.environ.pop("MTS_ACCOUNT", None)
        try:
            out = dlm.refresh_named_accounts(do, {"jishu_9": (do, "old")}, ["jishu_7", "jishu_8"])
            self.assertEqual(seen, ["jishu_7", "jishu_8"])
            self.assertEqual(sorted(out), ["jishu_7", "jishu_8"])     # dropped label removed
            self.assertNotIn("MTS_ACCOUNT", os.environ)
            again = dlm.refresh_named_accounts(do, out, ["jishu_7", "jishu_8"])
            self.assertEqual(len(seen), 2)                            # existing tokens reused
            self.assertIs(again["jishu_7"], out["jishu_7"])
        finally:
            if saved is not None:
                os.environ["MTS_ACCOUNT"] = saved

    def test_main_loop_passes_named_accounts_on_testnet(self):
        class _Done(BaseException):
            pass
        fake = types.ModuleType("deribit_orders")
        fake.active_env = lambda: "test"
        fake.authenticate = lambda: "tok"
        got = {}

        def run_once(*a, **k):
            got.update(k)
            raise _Done
        with mock.patch.dict(sys.modules, {"deribit_orders": fake}), \
                mock.patch.object(dlm, "named_account_labels", lambda: ["jishu_7"]), \
                mock.patch.object(dlm, "run_once", run_once):
            with self.assertRaises(_Done):
                dlm.main([])
        self.assertEqual(list(got["accounts"]), ["jishu_7"])


if __name__ == "__main__":
    unittest.main()
