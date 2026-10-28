"""
Offline tests for the 4-gate mainnet flag (S5_MAINNET_FLAG.md) and the hard
mainnet notional cap. NO network: urllib.request.urlopen is replaced by a
recorder for every test, secret files are temp files, input() is patched.
No test ever reaches a real Deribit host; refusal tests assert zero HTTP calls.

Run: python -m unittest test_mainnet_flag_offline -v   (from MyTradingSys/execution)
"""
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import deribit_orders as do
import executor


class Recorder:
    """Stands in for urllib.request.urlopen. Records URLs; answers from `responder`."""

    def __init__(self, scope="session:x"):
        self.urls = []
        self.scope = scope

    def __call__(self, req, timeout=None):
        self.urls.append(req.full_url)
        method = req.full_url.rsplit("/api/v2/", 1)[1]
        if method == "public/auth":
            result = {"access_token": "tok", "scope": self.scope}
        elif method == "private/get_transaction_log":
            result = {"logs": [], "continuation": None}
        else:
            result = {"order": {"order_id": "O1"}}
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "result": result}).encode()

        class R(io.BytesIO):
            def __enter__(self_):
                return self_

            def __exit__(self_, *a):
                return False
        return R(body)


CONFIRM = do.MAINNET_CONFIRMATION


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.test_secret = Path(self.tmp.name) / "testnet.secret.json"
        self.main_secret = Path(self.tmp.name) / "mainnet.secret.json"
        self.rec = Recorder()
        self.patches = [
            mock.patch.object(do, "SECRET", self.test_secret),
            mock.patch.object(do, "MAINNET_SECRET", self.main_secret),
            mock.patch("urllib.request.urlopen", self.rec),
            # B148: the account now comes from MTS_ACCOUNT at call time; tests must not inherit the host's value
            mock.patch.dict(os.environ),
        ]
        os.environ.pop("MTS_ACCOUNT", None)
        for p in self.patches:
            p.start()
        do._ACTIVE_ENV = "test"

    def tearDown(self):
        do._ACTIVE_ENV = "test"
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def write(self, path, env):
        path.write_text(json.dumps({"env": env, "client_id": "id", "client_secret": "s"}), encoding="utf-8")

    def go_mainnet(self):
        self.write(self.main_secret, "mainnet")
        with mock.patch("builtins.input", return_value=CONFIRM):
            do.select_environment(True)


class TestRefusalMatrix(Base):
    def test_named_account_never_selects_a_mainnet_secret(self):
        # B148 shipped behaviour: MTS_ACCOUNT set + mainnet flag -> refused before any prompt or network call
        self.write(self.main_secret, "mainnet")
        os.environ["MTS_ACCOUNT"] = "sharma"
        with mock.patch("builtins.input", side_effect=AssertionError("must fail before prompt")):
            with self.assertRaisesRegex(RuntimeError, "named accounts are testnet-only"):
                do.select_environment(True)
        self.assertEqual(do.active_env(), "test")
        self.assertEqual(self.rec.urls, [])

    def test_row1_no_flag_is_testnet_unchanged(self):
        self.write(self.test_secret, "test")
        with mock.patch("builtins.input", side_effect=AssertionError("no prompt on testnet")):
            self.assertEqual(do.select_environment(False), "test")
        self.assertEqual(do.active_env(), "test")
        self.assertEqual(do._base(), "https://test.deribit.com/api/v2")
        self.assertEqual(do.authenticate(), "tok")
        self.assertEqual(self.rec.urls, ["https://test.deribit.com/api/v2/public/auth"])

    def test_row1b_testnet_secret_must_still_say_test(self):
        self.write(self.test_secret, "mainnet")  # two-way: a mainnet secret never authenticates testnet
        with self.assertRaisesRegex(RuntimeError, 'env must be "test"'):
            do.authenticate()
        self.assertEqual(self.rec.urls, [])

    def test_row2_mainnet_secret_missing(self):
        with mock.patch("builtins.input", side_effect=AssertionError("must fail before prompt")):
            with self.assertRaisesRegex(RuntimeError, "MISSING"):
                do.select_environment(True)
        self.assertEqual(do.active_env(), "test")
        self.assertEqual(self.rec.urls, [])

    def test_row3_mainnet_secret_env_test(self):
        self.write(self.main_secret, "test")
        with mock.patch("builtins.input", side_effect=AssertionError("must fail before prompt")):
            with self.assertRaisesRegex(RuntimeError, 'env must be "mainnet"'):
                do.select_environment(True)
        self.assertEqual(do.active_env(), "test")
        self.assertEqual(self.rec.urls, [])

    def test_row4_withdraw_scope_refused_on_mainnet(self):
        self.go_mainnet()
        self.rec.scope = "account:read trade:read_write wallet:read_write"
        with self.assertRaisesRegex(RuntimeError, "key can withdraw"):
            do.authenticate()
        # the only call made was the auth itself, to the mainnet base (recorder, never real)
        self.assertEqual(self.rec.urls, ["https://www.deribit.com/api/v2/public/auth"])

    def test_row5_wrong_confirmation_refused_no_network(self):
        self.write(self.main_secret, "mainnet")
        for typed in ("", "y", "yes", CONFIRM.lower(), CONFIRM + " ", "I understand"):
            with mock.patch("builtins.input", return_value=typed):
                with self.assertRaises(do.MainnetRefused):
                    do.select_environment(True)
            self.assertEqual(do.active_env(), "test")
        self.assertEqual(self.rec.urls, [])

    def test_kill_only_accepts_only_the_word_kill(self):
        self.write(self.main_secret, "mainnet")
        for typed in ("", "KILL", "Kill", "kill ", " kill", "y", CONFIRM):
            with mock.patch("builtins.input", return_value=typed):
                with self.assertRaises(do.MainnetRefused):
                    do.select_environment(True, kill_only=True)
            self.assertEqual(do.active_env(), "test")
        self.assertEqual(self.rec.urls, [])
        with mock.patch("builtins.input", return_value="kill"):
            self.assertEqual(do.select_environment(True, kill_only=True), "mainnet")
        self.assertEqual(self.rec.urls, [])   # selecting stays offline

    def test_kill_word_does_not_open_the_normal_mainnet_path(self):
        self.write(self.main_secret, "mainnet")
        with mock.patch("builtins.input", return_value="kill"):
            with self.assertRaises(do.MainnetRefused):
                do.select_environment(True)          # trading path still needs the full sentence
        self.assertEqual(do.active_env(), "test")

    def test_kill_only_still_needs_secret_flag_and_tty(self):
        with mock.patch("builtins.input", side_effect=AssertionError("must fail before prompt")):
            with self.assertRaisesRegex(RuntimeError, "MISSING"):
                do.select_environment(True, kill_only=True)
        self.write(self.main_secret, "mainnet")
        with mock.patch("builtins.input", side_effect=EOFError):
            with self.assertRaises(do.MainnetRefused):
                do.select_environment(True, kill_only=True)
        self.assertEqual(do.active_env(), "test")

    def test_row5b_no_tty_eof_refused(self):
        self.write(self.main_secret, "mainnet")
        with mock.patch("builtins.input", side_effect=EOFError):
            with self.assertRaises(do.MainnetRefused):
                do.select_environment(True)
        self.assertEqual(do.active_env(), "test")
        self.assertEqual(self.rec.urls, [])

    def test_row6_exact_confirmation_reaches_mainnet_auth(self):
        self.go_mainnet()
        self.assertEqual(do.active_env(), "mainnet")
        self.assertEqual(self.rec.urls, [])  # selecting is offline
        self.assertEqual(do.authenticate(), "tok")
        self.assertEqual(self.rec.urls, ["https://www.deribit.com/api/v2/public/auth"])

    def test_select_false_after_mainnet_returns_to_testnet(self):
        self.go_mainnet()
        self.assertEqual(do.select_environment(False), "test")
        self.assertEqual(do._base(), do.BASE)

    def test_sanity_bases_differ_and_default_is_test(self):
        self.assertNotEqual(do.BASE, do.MAINNET_BASE)
        self.assertEqual(do.DEFAULT_ENV, "test")
        self.assertEqual(do._ACTIVE_ENV, "test")  # import never enables mainnet
        self.assertEqual(do.MAINNET_SECRET.name, "mainnet.secret.json")


class TestMainnetNotionalCap(Base):
    def test_default_cap_is_50(self):
        self.assertEqual(do.MAINNET_MAX_NOTIONAL_USD, 50.0)

    def test_order_above_cap_refused_before_any_call(self):
        self.go_mainnet()
        for fn in (do.buy, do.sell):
            with self.assertRaises(do.MainnetRefused):
                fn("tok", "BTC-PERPETUAL", 51, "market")
        with self.assertRaises(do.MainnetRefused):
            do.buy("tok", "BTC-PERPETUAL", 10000, "limit", price=1.0)
        self.assertEqual(self.rec.urls, [])

    def test_order_at_cap_allowed(self):
        self.go_mainnet()
        do.buy("tok", "BTC-PERPETUAL", 50, "market", label="x")
        self.assertEqual(self.rec.urls, ["https://www.deribit.com/api/v2/private/buy"])

    def test_bad_amount_and_other_instrument_refused_on_mainnet(self):
        self.go_mainnet()
        for inst, amt in (("BTC-PERPETUAL", 0), ("BTC-PERPETUAL", -5), ("BTC-PERPETUAL", "10"),
                          ("ETH-PERPETUAL", 10)):
            with self.assertRaises(do.MainnetRefused):
                do.buy("tok", inst, amt, "market")
        self.assertEqual(self.rec.urls, [])

    def test_reduce_only_stop_and_close_not_blocked(self):
        self.go_mainnet()
        do.stop_market("tok", "BTC-PERPETUAL", "SELL", 50, 60000.0, "stop")
        do.close_position("tok", "BTC-PERPETUAL")
        self.assertEqual(len(self.rec.urls), 2)

    def test_cap_is_read_at_call_time(self):
        self.go_mainnet()
        with mock.patch.object(do, "MAINNET_MAX_NOTIONAL_USD", 5.0):
            with self.assertRaises(do.MainnetRefused):
                do.buy("tok", "BTC-PERPETUAL", 10, "market")
        self.assertEqual(self.rec.urls, [])

    def test_testnet_large_order_unaffected(self):
        do.buy("tok", "BTC-PERPETUAL", 5000, "market")
        self.assertEqual(self.rec.urls, ["https://test.deribit.com/api/v2/private/buy"])

    def test_plan_level_cap_in_executor_preflight(self):
        compiled = {"plan_id": "p1", "max_position_size": 80, "stop_order": {"order_type": "stop_market"},
                    "caps_check": {"max_notional_usd": 1000, "within_max_loss": True},
                    "entry_orders": [{"amount": 80}]}
        nohalt = Path(self.tmp.name) / "nohalt"
        self.assertEqual(executor.preflight(compiled, None, None, nohalt, nohalt), [])  # testnet: fine (compiled file ok)
        self.go_mainnet()
        reasons = executor.preflight(compiled, {}, None, nohalt, nohalt)  # raw plan given (mainnet refuses plan=None, spec 128)
        self.assertTrue(any("MAINNET_MAX_NOTIONAL_USD" in r for r in reasons), reasons)
        compiled["max_position_size"] = 50
        compiled["entry_orders"] = [{"amount": 50}]
        self.assertEqual(executor.preflight(compiled, {}, None, nohalt, nohalt), [])


class TestTransactionLogFetch(Base):
    def test_paginates_and_fails_closed(self):
        pages = [{"logs": [{"change": 1}], "continuation": "c1"}, {"logs": [{"change": 2}], "continuation": None}]
        with mock.patch.object(do, "_call", side_effect=pages) as c:
            self.assertEqual(do.get_transaction_log("tok", "BTC", 1, 2), [{"change": 1}, {"change": 2}])
            self.assertEqual(c.call_args_list[1][0][1]["continuation"], "c1")
        with mock.patch.object(do, "_call", return_value={"logs": [], "continuation": "again"}):
            with self.assertRaises(do.DeribitError):
                do.get_transaction_log("tok", "BTC", 1, 2, max_pages=3)


if __name__ == "__main__":
    unittest.main()
