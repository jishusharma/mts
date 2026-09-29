"""Offline tests for kill_switch --account (spec 124). Derived from the spec, not from the implementation."""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import kill_switch
from test_kill_switch import FakeDeribitModule


class EnvRecordingModule(FakeDeribitModule):
    def __init__(self, data):
        super().__init__(data)
        self.env_at_auth = []

    def authenticate(self):
        self.env_at_auth.append(os.environ.get("MTS_ACCOUNT"))
        return super().authenticate()


class TestKillSwitchAccount(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ks_acct_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.halt = self.tmp / "HALT"
        self.saved_mod = sys.modules.get("deribit_orders")
        self.saved_env = os.environ.get("MTS_ACCOUNT")
        os.environ.pop("MTS_ACCOUNT", None)
        self.fake = EnvRecordingModule({"BTC-PERPETUAL": {"size": 10, "orders": ["o1"]}})
        sys.modules["deribit_orders"] = self.fake

    def tearDown(self):
        if self.saved_mod is not None:
            sys.modules["deribit_orders"] = self.saved_mod
        else:
            sys.modules.pop("deribit_orders", None)
        if self.saved_env is None:
            os.environ.pop("MTS_ACCOUNT", None)
        else:
            os.environ["MTS_ACCOUNT"] = self.saved_env

    def _main(self, argv):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = kill_switch.main(argv, halt_path=self.halt)
        return rc, out.getvalue()

    def test_account_sets_mts_account_during_auth(self):
        rc, _ = self._main(["--confirm", "KILL", "--account", "fabio"])
        self.assertEqual(rc, 0)
        self.assertEqual(self.fake.env_at_auth, ["fabio"])
        self.assertEqual(self.fake._data["BTC-PERPETUAL"]["size"], 0)
        self.assertTrue(self.halt.exists())

    def test_env_restored_after_run(self):
        os.environ["MTS_ACCOUNT"] = "previous"
        self._main(["--confirm", "KILL", "--account", "fabio"])
        self.assertEqual(os.environ.get("MTS_ACCOUNT"), "previous")

    def test_env_removed_after_run_when_unset_before(self):
        self._main(["--confirm", "KILL", "--account", "fabio"])
        self.assertNotIn("MTS_ACCOUNT", os.environ)

    def test_without_account_env_untouched(self):
        rc, _ = self._main(["--confirm", "KILL"])
        self.assertEqual(rc, 0)
        self.assertEqual(self.fake.env_at_auth, [None])

    def test_bad_labels_refused_before_anything_happens(self):
        for bad in ["Fabio", "../x", "a b", "a" * 33, "fa-bio", ""]:
            rc, out = self._main(["--confirm", "KILL", "--account", bad])
            self.assertEqual(rc, 2, msg=repr(bad))
            self.assertIn("REFUSED", out)
            self.assertFalse(self.halt.exists(), msg=repr(bad))
            self.assertEqual(self.fake.auth_calls, 0, msg=repr(bad))

    def test_account_with_mainnet_refused(self):
        rc, out = self._main(["--confirm", "KILL", "--account", "fabio", "--mainnet"])
        self.assertEqual(rc, 2)
        self.assertIn("REFUSED", out)
        self.assertFalse(self.halt.exists())
        self.assertEqual(self.fake.auth_calls, 0)

    def test_confirm_still_checked_first(self):
        rc, out = self._main(["--account", "fabio"])
        self.assertEqual(rc, 1)
        self.assertFalse(self.halt.exists())
        self.assertEqual(self.fake.auth_calls, 0)

    def test_env_restored_even_when_auth_fails(self):
        def boom():
            raise RuntimeError("auth down")
        self.fake.authenticate = boom
        rc, _ = self._main(["--confirm", "KILL", "--account", "fabio"])
        self.assertEqual(rc, 1)
        self.assertTrue(self.halt.exists())
        self.assertNotIn("MTS_ACCOUNT", os.environ)


if __name__ == "__main__":
    unittest.main()
