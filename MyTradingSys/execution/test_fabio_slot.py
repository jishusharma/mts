"""Offline tests: Fabio dedicated testnet slot (account routing). No network, no subprocess, no real secrets."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_trader as at  # noqa: E402
import deribit_orders as do  # noqa: E402

FABIO = "layer:fabio:x:5m"
RSI = "layer:rsi:support:15m"


class Proc:
    def poll(self):
        return None


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.patches = [mock.patch.object(at, "SECRETS_DIR", self.dir),
                        mock.patch.object(at, "LOG_PATH", self.dir / "log.jsonl"),
                        mock.patch.object(at, "_warned_missing", set()),
                        mock.patch.object(at, "tom_signal", lambda *a, **k: None),
                        mock.patch.object(at, "AUTO_PAUSE", self.dir / "NOPAUSE"),
                        mock.patch.object(at, "brakes", lambda: [])]
        for p in self.patches:
            p.start()
        self.cfg = json.loads(json.dumps(at.DEFAULT_CONFIG))
        self.placed = []

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def fake_place(self, sig, dry_run, account=None):
        self.placed.append((sig["source"], account))
        return {"outcome": "entered", "plan_id": f"p{len(self.placed)}", "proc": Proc()}

    def run_cycle(self, sources, active, extra):
        sigs = [{"source": s, "key": f"k{i}{s}", "side": "long", "plan_args": []} for i, s in enumerate(sources)]
        with mock.patch.object(at, "layer_signal", lambda a, c, n: a), \
                mock.patch.object(at, "read_new_layer_alerts", lambda st: sigs), \
                mock.patch.object(at, "place", self.fake_place):
            return at.cycle({}, self.cfg, False, active, extra=extra)

    def events(self):
        p = self.dir / "log.jsonl"
        return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


class Routing(Base):
    def test_prefix_routing(self):
        (self.dir / "testnet_fabio.secret.json").write_text("{}")
        self.assertEqual(at.account_for(FABIO, self.cfg), "fabio")
        self.assertIsNone(at.account_for(RSI, self.cfg))

    def test_per_account_busy(self):
        (self.dir / "testnet_fabio.secret.json").write_text("{}")
        rsi_busy = {"proc": Proc(), "plan_id": "rsi1", "source": RSI}
        extra = {}
        active = self.run_cycle([FABIO, RSI], rsi_busy, extra)
        self.assertEqual(self.placed, [(FABIO, "fabio")])       # fabio placed despite busy default slot
        self.assertIs(active, rsi_busy)
        self.assertIn("fabio", extra)
        self.run_cycle([FABIO], active, extra)                   # second fabio blocked by open fabio trade
        self.assertEqual(len(self.placed), 1)
        self.assertEqual([e["event"] for e in self.events()].count("skipped_busy"), 2)

    def test_missing_file_falls_back_to_shared_slot_and_logs_once(self):
        busy = {"proc": Proc(), "plan_id": "rsi1", "source": RSI}
        extra = {}
        self.run_cycle([FABIO], busy, extra)
        self.run_cycle([FABIO], busy, extra)
        self.assertEqual(self.placed, [])
        self.assertEqual(extra, {})
        self.assertEqual([e["event"] for e in self.events()].count("fabio_account_missing"), 1)
        active = self.run_cycle([FABIO], {}, extra)               # free shared slot: trades on default account
        self.assertEqual(self.placed, [(FABIO, None)])
        self.assertTrue(active)


class Secrets(unittest.TestCase):
    def test_path_selection(self):
        self.assertEqual(do.secret_path_for("test").name, "testnet.secret.json")
        self.assertEqual(do.secret_path_for("test", "fabio").name, "testnet_fabio.secret.json")

    def test_mainnet_refuses_account(self):
        with self.assertRaises(RuntimeError):
            do.secret_path_for("mainnet", "fabio")
        with mock.patch.dict(os.environ, {"MTS_ACCOUNT": "fabio"}):
            with self.assertRaisesRegex(RuntimeError, "testnet-only"):
                do._load_secret("mainnet")

    def test_bad_label_and_env_mismatch(self):
        with self.assertRaises(RuntimeError):
            do.secret_path_for("test", "../x")
        with tempfile.TemporaryDirectory() as d:
            sec = Path(d) / "testnet.secret.json"
            (Path(d) / "testnet_fabio.secret.json").write_text(json.dumps({"env": "mainnet"}))
            with mock.patch.object(do, "SECRET", sec), mock.patch.dict(os.environ, {"MTS_ACCOUNT": "fabio"}):
                with self.assertRaisesRegex(RuntimeError, "env must be"):
                    do._load_secret("test")


if __name__ == "__main__":
    unittest.main()
