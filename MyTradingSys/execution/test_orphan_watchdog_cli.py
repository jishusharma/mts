"""Offline tests for orphan_watchdog_cli (spec 123). Derived from the spec, not from the implementation."""
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path

import orphan_watchdog_cli as cli
import pm_heartbeat


class FakeReadClient:
    def __init__(self, size=0):
        self.size = size

    def get_positions(self, token, currency="BTC", kind="future"):
        return [{"instrument_name": "BTC-PERPETUAL", "size": self.size}] if self.size else []

    def get_open_orders(self, token, instrument_name="BTC-PERPETUAL", type_="all"):
        return []


class TestAccountLabels(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="owcli_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_labels_from_config_default_first_unique_sorted(self):
        p = self.tmp / "cfg.json"
        p.write_text(json.dumps({"accounts": {"layer:fabio:": "fabio", "layer:x:": "zed", "layer:y:": "fabio"}}), encoding="utf-8")
        self.assertEqual(cli.account_labels(p), ["default", "fabio", "zed"])

    def test_missing_config_falls_back_to_every_secret_file_label(self):
        sd = self.tmp / "secrets"
        sd.mkdir()
        for n in ("fabio", "jishu_3", "jishu_12"):
            (sd / f"testnet_{n}.secret.json").write_text("{}", encoding="utf-8")
        (sd / "testnet.secret.json").write_text("{}", encoding="utf-8")        # main file is not a label
        self.assertEqual(cli.account_labels(self.tmp / "nope.json", sd), ["default", "fabio", "jishu_12", "jishu_3"])
        self.assertEqual(cli.account_labels(self.tmp / "nope.json", self.tmp / "nosuchdir"), ["default"])

    def test_bad_labels_in_config_are_dropped(self):
        p = self.tmp / "cfg.json"
        p.write_text(json.dumps({"accounts": {"a:": "Bad Label", "b:": "ok_1", "c:": "../x"}}), encoding="utf-8")
        self.assertEqual(cli.account_labels(p), ["default", "ok_1"])


class TestRealGetClient(unittest.TestCase):
    def setUp(self):
        self.saved_mod = sys.modules.get("deribit_orders")
        self.saved_env = os.environ.get("MTS_ACCOUNT")
        self.seen = []
        seen = self.seen
        fake = types.ModuleType("deribit_orders")
        fake.authenticate = lambda: (seen.append(os.environ.get("MTS_ACCOUNT")), "tok")[1]
        sys.modules["deribit_orders"] = fake

    def tearDown(self):
        if self.saved_mod is not None:
            sys.modules["deribit_orders"] = self.saved_mod
        else:
            sys.modules.pop("deribit_orders", None)
        if self.saved_env is None:
            os.environ.pop("MTS_ACCOUNT", None)
        else:
            os.environ["MTS_ACCOUNT"] = self.saved_env

    def test_named_account_sets_env_during_auth_and_restores(self):
        os.environ.pop("MTS_ACCOUNT", None)
        client, token = cli.real_get_client("fabio")
        self.assertEqual(token, "tok")
        self.assertIs(client, sys.modules["deribit_orders"])
        self.assertEqual(self.seen, ["fabio"])
        self.assertNotIn("MTS_ACCOUNT", os.environ)

    def test_default_account_clears_env_during_auth_and_restores(self):
        os.environ["MTS_ACCOUNT"] = "fabio"
        cli.real_get_client("default")
        self.assertEqual(self.seen, [None])
        self.assertEqual(os.environ.get("MTS_ACCOUNT"), "fabio")


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="owcli_main_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.hb = self.tmp / "hb"
        self.halt = self.tmp / "HALT"
        self.cfg = self.tmp / "cfg.json"
        self.cfg.write_text(json.dumps({"accounts": {"layer:fabio:": "fabio"}}), encoding="utf-8")

    def _main(self, clients, argv=("--once",), alive=lambda pid: True):
        return cli.main(list(argv), get_client=lambda label: (clients[label], "tok"), hb_dir=self.hb,
                        halt_path=self.halt, log_path=self.tmp / "log.jsonl", alive=alive, config_path=self.cfg)

    def test_clean_returns_0_no_halt(self):
        rc = self._main({"default": FakeReadClient(), "fabio": FakeReadClient()})
        self.assertEqual(rc, 0)
        self.assertFalse(self.halt.exists())

    def test_orphan_returns_3_and_halts(self):
        rc = self._main({"default": FakeReadClient(), "fabio": FakeReadClient(size=10)})
        self.assertEqual(rc, 3)
        self.assertIn("fabio", self.halt.read_text(encoding="utf-8"))

    def test_confirmed_halt_is_recorded_in_the_log(self):
        # B148: the CLI path used to log only orphan_seen, so `mts status` never showed a confirmed orphan halt
        self._main({"default": FakeReadClient(), "fabio": FakeReadClient(size=10)})
        events = [json.loads(x)["event"] for x in (self.tmp / "log.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(events, ["orphan_seen", "orphan_halt"])

    def test_live_heartbeat_for_account_suppresses_halt(self):
        pm_heartbeat.write_heartbeat("p1", account="fabio", pid=77, hb_dir=self.hb)
        rc = self._main({"default": FakeReadClient(), "fabio": FakeReadClient(size=10)}, alive=lambda pid: pid == 77)
        self.assertEqual(rc, 0)
        self.assertFalse(self.halt.exists())

    def test_stale_heartbeat_with_reused_pid_does_not_suppress_halt(self):
        # B148 part 5: manager died 20 min ago, Windows reused pid 77, pid_alive says True: still an orphan
        from datetime import datetime, timedelta, timezone
        old = datetime.now(timezone.utc) - timedelta(minutes=20)
        pm_heartbeat.write_heartbeat("p1", account="fabio", pid=77, hb_dir=self.hb, now=old)
        rc = self._main({"default": FakeReadClient(), "fabio": FakeReadClient(size=10)}, alive=lambda pid: True)
        self.assertEqual(rc, 3)
        self.assertIn("fabio", self.halt.read_text(encoding="utf-8"))

    def test_hb_max_age_flag_is_honoured(self):
        from datetime import datetime, timedelta, timezone
        old = datetime.now(timezone.utc) - timedelta(minutes=20)
        pm_heartbeat.write_heartbeat("p1", account="fabio", pid=77, hb_dir=self.hb, now=old)
        rc = self._main({"default": FakeReadClient(), "fabio": FakeReadClient(size=10)},
                        argv=("--once", "--hb-max-age", "3600"), alive=lambda pid: True)
        self.assertEqual(rc, 0)

    def test_dead_heartbeat_does_not_suppress(self):
        pm_heartbeat.write_heartbeat("p1", account="fabio", pid=77, hb_dir=self.hb)
        rc = self._main({"default": FakeReadClient(), "fabio": FakeReadClient(size=10)}, alive=lambda pid: False)
        self.assertEqual(rc, 3)

    def test_read_error_only_returns_1(self):
        def gc(label):
            raise RuntimeError("down")
        rc = cli.main(["--once"], get_client=gc, hb_dir=self.hb, halt_path=self.halt,
                      log_path=self.tmp / "log.jsonl", alive=lambda p: True, config_path=self.cfg)
        self.assertEqual(rc, 1)
        self.assertFalse(self.halt.exists())

    def test_no_mainnet_flag(self):
        with self.assertRaises(SystemExit):
            self._main({}, argv=("--mainnet",))


if __name__ == "__main__":
    unittest.main()


def test_cli_reads_the_heartbeat_dir_position_manager_writes():
    """Regression 2026-09-29: CLI read execution/heartbeat/ while position_manager writes pm_heartbeats/
    -> a live, protected jishu_2 trade was reported as an orphan and HALT was written."""
    import inspect
    import orphan_watchdog_cli as cli
    src = inspect.getsource(cli)
    assert 'HERE / "heartbeat"' not in src
    assert "pm_heartbeat.DEFAULT_HB_DIR" in src
