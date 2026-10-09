"""B148: a token must be refreshed as the account that issued it, never as MAIN after MTS_ACCOUNT was restored."""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deribit_orders as do  # noqa: E402


class ReauthAccountTest(unittest.TestCase):
    def setUp(self):
        do._TOKEN_ACCOUNT.clear()
        self.addCleanup(do._TOKEN_ACCOUNT.clear)
        self.loaded = []

        def load_secret(env=None, account=do._ENV_ACCOUNT):
            if account is do._ENV_ACCOUNT:
                account = os.environ.get("MTS_ACCOUNT") or None
            self.loaded.append(account)
            return {"client_id": "i", "client_secret": "s", "env": "test"}
        p = mock.patch.object(do, "_load_secret", load_secret)
        p.start()
        self.addCleanup(p.stop)
        self.n = 0
        self.expired_once = True

        def post(method, params, token=None):
            if method == "public/auth":
                self.n += 1
                return {"result": {"access_token": f"tok{self.n}", "scope": "account:read"}}
            if self.expired_once and token == "tok1":
                self.expired_once = False
                return {"error": {"code": 13009, "message": "unauthorized"}}
            return {"result": {"equity": 1.0}}
        p2 = mock.patch.object(do, "_post", post)
        p2.start()
        self.addCleanup(p2.stop)

    def test_expired_subaccount_token_is_refreshed_as_that_subaccount(self):
        with mock.patch.dict(os.environ, {"MTS_ACCOUNT": "jishu_7"}):
            tok = do.authenticate()
        os.environ.pop("MTS_ACCOUNT", None)          # the monitor restores the env after authenticating
        self.loaded.clear()
        do._call("private/get_account_summary", {}, tok)
        self.assertEqual(self.loaded, ["jishu_7"])   # old code loaded None = MAIN

    def test_main_token_stays_main_even_if_env_names_a_subaccount(self):
        os.environ.pop("MTS_ACCOUNT", None)
        tok = do.authenticate()
        self.loaded.clear()
        with mock.patch.dict(os.environ, {"MTS_ACCOUNT": "jishu_7"}):
            do._call("private/get_account_summary", {}, tok)
        self.assertEqual(self.loaded, [None])


if __name__ == "__main__":
    unittest.main()
