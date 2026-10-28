"""Offline tests for deribit_read --account (spec 125). Derived from the spec, not from the implementation."""
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import deribit_read


class TestDeribitReadAccount(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dr_acct_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.orig_secret = deribit_read.SECRET
        self.orig_call = deribit_read.call
        deribit_read.SECRET = self.tmp / "testnet.secret.json"
        self._secret(deribit_read.SECRET, "default-id")
        self._secret(self.tmp / "testnet_fabio.secret.json", "fabio-id")
        self.calls = []

        def fake_call(method, params, token=None):
            self.calls.append((method, dict(params)))
            if method == "public/auth":
                return {"access_token": "tok", "scope": "trade:read"}
            if method == "private/get_account_summary":
                return {}
            return []

        deribit_read.call = fake_call
        self.addCleanup(self._restore)

    def _restore(self):
        deribit_read.SECRET = self.orig_secret
        deribit_read.call = self.orig_call

    @staticmethod
    def _secret(path, cid):
        path.write_text(json.dumps({"client_id": cid, "client_secret": "s", "env": "test"}), encoding="utf-8")

    def _main(self, argv):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = deribit_read.main(argv)
        return rc, out.getvalue()

    def _auth_client_id(self):
        return [p for m, p in self.calls if m == "public/auth"][0]["client_id"]

    def test_resolve_secret_default(self):
        self.assertEqual(deribit_read.resolve_secret(None), deribit_read.SECRET)
        self.assertEqual(deribit_read.resolve_secret(""), deribit_read.SECRET)

    def test_resolve_secret_named(self):
        self.assertEqual(deribit_read.resolve_secret("fabio"), deribit_read.SECRET.parent / "testnet_fabio.secret.json")

    def test_resolve_secret_bad_label_raises(self):
        for bad in ["Fabio", "../x", "a b", "a" * 33, "x/y", "fa-bio"]:
            with self.assertRaises(ValueError, msg=repr(bad)):
                deribit_read.resolve_secret(bad)

    def test_default_run_uses_default_secret(self):
        rc, _ = self._main([])
        self.assertEqual(rc, 0)
        self.assertEqual(self._auth_client_id(), "default-id")

    def test_account_run_uses_named_secret(self):
        rc, _ = self._main(["--account", "fabio"])
        self.assertEqual(rc, 0)
        self.assertEqual(self._auth_client_id(), "fabio-id")

    def test_missing_account_file_returns_2_no_network(self):
        rc, out = self._main(["--account", "ghost"])
        self.assertEqual(rc, 2)
        self.assertIn("MISSING", out)
        self.assertIn("testnet_ghost.secret.json", out)
        self.assertEqual(self.calls, [])

    def test_bad_label_returns_2_no_network(self):
        rc, out = self._main(["--account", "../etc"])
        self.assertEqual(rc, 2)
        self.assertIn("REFUSED", out)
        self.assertEqual(self.calls, [])

    def test_named_secret_with_wrong_env_refused(self):
        (self.tmp / "testnet_fabio.secret.json").write_text(
            json.dumps({"client_id": "x", "client_secret": "s", "env": "mainnet"}), encoding="utf-8")
        rc, out = self._main(["--account", "fabio"])
        self.assertEqual(rc, 2)
        self.assertIn("REFUSED", out)
        self.assertEqual(self.calls, [])

    def test_secret_value_never_printed(self):
        _, out = self._main(["--account", "fabio"])
        self.assertNotIn("fabio-id", out)


if __name__ == "__main__":
    unittest.main()
