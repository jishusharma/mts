"""Offline tests for the auto_trader layer trade_blocklist (no exchange, no subprocess).
Run: python -m pytest MyTradingSys/execution/test_auto_trader_blocklist.py"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_trader as at  # noqa: E402
import test_auto_trader as _base  # noqa: E402  (module import: its test classes must not be collected twice)

NOW, cfg, tom_alert, T15 = _base.NOW, _base.cfg, _base.tom_alert, _base.LayerSignalTest.T15

HERE = Path(__file__).resolve().parent
SHIPPED = HERE / "auto_trader_config.json"

# (alert dict, expected source) for every layer that must stop trading
BLOCKED_ALERTS = [
    ({"layer": "session", "sub": "session_momentum", "tf": "15m", "side": "long"},
     "layer:session:session_momentum:15m"),
    ({"layer": "positioning", "sub": "funding_cvd_fade", "tf": "1h", "side": "short"},
     "layer:positioning:funding_cvd_fade:1h"),
    ({"layer": "turn_of_candle", "sub": "turn_of_candle", "tf": "1m", "side": "long"},
     "layer:turn_of_candle:turn_of_candle:1m"),
    ({"layer": "fabio", "sub": "escalation", "tf": "1h", "side": "long"}, "layer:fabio:escalation:1h"),
    ({"layer": "fabio", "sub": "escalation", "tf": "15m", "side": "short"}, "layer:fabio:escalation:15m"),
    ({"layer": "rsi", "sub": "rsi_events", "tf": "15m", "side": "long"}, "layer:rsi:rsi_events:15m"),
]


def shipped_cfg():
    """Shipped config with its parked research blocklist re-applied. Testnet calibration ships an empty blocklist
    (operator 2026-10-07: all layers fire); the blocklist mechanism is still tested against the real verdicts."""
    c = at.load_config(SHIPPED)
    parked = c["trade_blocklist_parked"]
    c["trade_blocklist"], c["trade_blocklist_reasons"] = list(parked), dict(parked)
    return c


class BlocklistCycleTest(unittest.TestCase):
    """Reuses CycleTest's fixture (tmp log/alerts dir, fake place, fake ledger) without re-running its tests."""
    tearDown = _base.CycleTest.tearDown

    def setUp(self):
        _base.CycleTest.setUp(self)
        # Account routing depends on which testnet secret files exist on the host (the desktop has them, the
        # cloud does not). Pin it: no named-account secrets by default; tests that need routing call routed().
        saved = at.account_secret_path
        self.addCleanup(setattr, at, "account_secret_path", saved)
        self.secrets = Path(self.tmp.name) / "secrets"
        self.secrets.mkdir()
        at.account_secret_path = lambda label: self.secrets / f"testnet_{label}.secret.json"
        at._warned_missing.clear()
        # These tests are about the blocklist, not routing: a missing secret used to fall to the shared slot, now it
        # rejects (B148, covered in test_fabio_slot). Keep the shared-slot behaviour for the blocklist cases.
        saved_missing = at.account_secret_missing
        self.addCleanup(setattr, at, "account_secret_missing", saved_missing)
        at.account_secret_missing = lambda source, cfg: None

    def routed(self, *labels):
        """Simulate the desktop: secret files present for these account labels."""
        for lab in labels:
            (self.secrets / f"testnet_{lab}.secret.json").write_text("{}", encoding="utf-8")
    rows_of = _base.CycleTest.rows_of
    P = None  # set by setUp

    def t_close(self, tf):
        return T15 if tf == "15m" else int((NOW.timestamp() - at.TF_SECONDS[tf] * 1.1) * 1000)

    def feed(self, *alerts, st):
        """Append layer alerts (fresh t_close) after registering file offsets once, like the live runner does."""
        files = {al["tf"]: at.LAYER_ALERT_DIR / f"{al['tf']}.jsonl" for al in alerts}
        for f in files.values():
            if not f.exists():
                f.write_text("", encoding="utf-8")
        at.read_new_layer_alerts(st)
        for al in alerts:
            a = {**al, "event": al.get("event", "support" if al.get("sub") == "rsi_events" else "x"), "t_close": self.t_close(al["tf"])}
            with open(files[al["tf"]], "a", encoding="utf-8") as fh:
                fh.write(json.dumps(a) + "\n")

    def events(self):
        return [e for e in _base.CycleTest.events(self) if not e.endswith("_account_missing")]

    def test_shipped_config_blocks_every_failed_layer_and_documents_reason(self):
        c = shipped_cfg()
        for alert, source in BLOCKED_ALERTS:
            r = at.trade_block_reason(source, c)
            self.assertTrue(r and r != at.BLOCKLIST_INVALID, source)
            self.assertIn(r, c["trade_blocklist_reasons"].values(), source)
        for prefix in c["trade_blocklist"]:
            self.assertTrue(c["trade_blocklist_reasons"].get(prefix), prefix)   # every entry has a reason

    def test_shipped_config_leaves_other_layers_and_tom_unblocked(self):
        c = shipped_cfg()
        for source in ("tom", "layer:rsi:rsi_events:1h", "layer:fabio:volume_fvg:1h", "layer:fabio:cvd_absorption:15m",
                       "layer:cryptocred:sr_flip:1h", "layer:rsi:malkan_bull:1h"):
            self.assertIsNone(at.trade_block_reason(source, c), source)

    def test_shipped_config_is_either_blocking_or_an_explicit_parked_calibration(self):
        # B150: the gate must not pin an empty list (restoring the parked list would fail it). Either the layers are blocked,
        # or the empty list is a documented calibration (parked entries kept) that mainnet refuses (executor.mainnet_config_refusals).
        c = at.load_config(SHIPPED)
        if c["trade_blocklist"]:
            for _, source in BLOCKED_ALERTS:
                self.assertTrue(at.trade_block_reason(source, c), source)
        else:
            self.assertTrue(c.get("trade_blocklist_parked"), "empty blocklist needs trade_blocklist_parked")
            self.assertIn("_calibration", c)
            for _, source in BLOCKED_ALERTS:
                self.assertIsNone(at.trade_block_reason(source, c), source)

    def test_shipped_config_keeps_account_routing(self):
        self.assertEqual(shipped_cfg()["accounts"]["layer:turn_of_candle:"], "jishu_1")
        self.assertEqual(shipped_cfg()["accounts"]["layer:rsi:rsi_events:1h"], "jishu_4")

    def test_every_layer_group_has_its_own_account(self):
        """One position per account: layer groups that fire together must not share an account."""
        c = shipped_cfg()
        groups = ["layer:turn_of_candle:turn_of_candle:1m", "layer:rsi:rsi_events:5m", "layer:rsi:rsi_events:15m",
                  "layer:rsi:rsi_events:1h", "layer:rsi:malkan_bull:1h", "layer:rsi:malkan_bear:1h",
                  "layer:session:session_momentum:15m", "layer:positioning:funding_cvd_fade:1h",
                  "layer:fabio:cvd_absorption:15m", "layer:fabio:cvd_absorption:1h", "layer:fabio:escalation:15m",
                  "layer:fabio:volume_fvg:15m", "layer:fabio:v3_grid:1m", "layer:cryptocred:sr_flip:15m",
                  "layer:cryptocred:sr_flip:1h", "layer:cryptocred:fib_pullback:15m", "layer:cryptocred:fib_pullback:1h"]
        secrets = Path(self.tmp.name) / "all_secrets"
        secrets.mkdir()
        for lab in set(c["accounts"].values()):
            (secrets / f"testnet_{lab}.secret.json").write_text("{}", encoding="utf-8")
        at.account_secret_path = lambda label: secrets / f"testnet_{label}.secret.json"
        got = {g: at.account_for(g, c) for g in groups}
        self.assertNotIn(None, got.values(), got)
        self.assertEqual(len(set(got.values())), len(groups), got)
        self.assertNotIn("tom", c["accounts"])      # Tom keeps the default (main) slot

    def test_blocked_sources_never_reach_place(self):
        c = shipped_cfg()
        st = {"tom_last_alert_no": 43}
        self.feed(*[a for a, _ in BLOCKED_ALERTS], st=st)
        at.cycle(st, c, False, {}, NOW)
        self.assertEqual(self.placed, [])
        self.assertEqual(self.events(), ["layer_trade_blocked"] * len(BLOCKED_ALERTS))
        rows = self.rows_of("layer_trade_blocked")
        self.assertEqual(sorted(r["source"] for r in rows), sorted(s for _, s in BLOCKED_ALERTS))
        self.assertTrue(all(r["reason"] and r["reason"] != at.BLOCKLIST_INVALID for r in rows))

    def test_non_blocked_layer_still_placed(self):
        c = shipped_cfg()
        st = {"tom_last_alert_no": 43}
        self.feed({"layer": "rsi", "sub": "rsi_events", "tf": "1h", "side": "long"},
                  {"layer": "session", "sub": "session_momentum", "tf": "15m", "side": "long"}, st=st)
        at.cycle(st, c, False, {}, NOW)
        self.assertEqual([s["source"] for s in self.placed], ["layer:rsi:rsi_events:1h"])
        self.assertEqual(self.events(), ["layer_trade_blocked", "trade_attempt"])

    def test_tom_never_blocked_even_when_blocklist_is_malformed(self):
        c = cfg()
        c["trade_blocklist"] = "layer:"            # malformed -> layers blocked
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")
        at.cycle({"tom_last_alert_no": 43}, c, False, {}, NOW)
        self.assertEqual([s["source"] for s in self.placed], ["tom"])
        self.assertNotIn("layer_trade_blocked", self.events())

    def test_blocked_signal_does_not_consume_the_slot_or_block_next_layer(self):
        c = shipped_cfg()
        st = {"tom_last_alert_no": 43}
        self.feed({"layer": "turn_of_candle", "sub": "turn_of_candle", "tf": "1m", "side": "long"},
                  {"layer": "rsi", "sub": "rsi_events", "tf": "1h", "side": "long"}, st=st)
        active = at.cycle(st, c, False, {}, NOW)
        self.assertEqual(active["source"], "layer:rsi:rsi_events:1h")

    def test_blocklist_applies_before_halt_and_busy(self):
        c = shipped_cfg()
        at.HALT.write_text("x", encoding="utf-8")
        st = {"tom_last_alert_no": 43}
        self.feed({"layer": "fabio", "sub": "escalation", "tf": "1h", "side": "long"}, st=st)
        at.cycle(st, c, False, {"proc": self.P(), "plan_id": "busy", "source": "tom"}, NOW)
        self.assertEqual(self.events(), ["layer_trade_blocked"])

    # ---- malformed / missing config: fail closed for layers

    def test_missing_key_means_nothing_blocked(self):
        c = cfg()
        del c["trade_blocklist"]
        del c["trade_blocklist_reasons"]
        self.assertIsNone(at.trade_block_reason("layer:rsi:rsi_events:1h", c))

    def test_malformed_blocklist_blocks_all_layers_without_crashing(self):
        for bad in (None, "layer:fabio:", {"layer:fabio:": 1}, 7, ["ok:", 3], ["ok:", ""], [None]):
            c = cfg()
            c["trade_blocklist"] = bad
            self.assertEqual(at.trade_block_reason("layer:rsi:rsi_events:1h", c), at.BLOCKLIST_INVALID, bad)
            self.assertIsNone(at.trade_block_reason("tom", c), bad)

    def test_malformed_reasons_blocks_all_layers(self):
        c = cfg()
        c["trade_blocklist"] = ["layer:fabio:escalation:"]
        c["trade_blocklist_reasons"] = ["not", "a", "dict"]
        self.assertEqual(at.trade_block_reason("layer:rsi:rsi_events:1h", c), at.BLOCKLIST_INVALID)

    def test_missing_reason_for_entry_still_blocks(self):
        c = cfg()
        c["trade_blocklist"] = ["layer:fabio:escalation:"]
        self.assertIn("no reason", at.trade_block_reason("layer:fabio:escalation:1h", c))

    def test_malformed_blocklist_in_cycle_places_no_layer_trade_and_logs(self):
        c = cfg()
        c["trade_blocklist"] = {"oops": 1}
        st = {"tom_last_alert_no": 43}
        self.feed({"layer": "rsi", "sub": "rsi_events", "tf": "1h", "side": "long"}, st=st)
        at.cycle(st, c, False, {}, NOW)
        self.assertEqual(self.placed, [])
        self.assertEqual(self.rows_of("layer_trade_blocked")[0]["reason"], at.BLOCKLIST_INVALID)

    def _config_file(self, text):
        p = Path(self.tmp.name) / "cfg.json"
        if text is not None:
            p.write_text(text, encoding="utf-8")
        return p

    def test_unreadable_config_file_blocks_all_layers(self):
        for text in (None, "{not json", "[1, 2]", ""):          # None = file missing
            c = at.load_config(self._config_file(text) if text is not None else Path(self.tmp.name) / "nope.json")
            self.assertEqual(at.trade_block_reason("layer:rsi:rsi_events:1h", c), at.BLOCKLIST_INVALID, repr(text))
            self.assertIsNone(at.trade_block_reason("tom", c))
        self.assertIn("config_unreadable", self.events())

    def test_config_file_null_blocklist_blocks_all_layers(self):
        c = at.load_config(self._config_file('{"trade_blocklist": null}'))
        self.assertEqual(at.trade_block_reason("layer:x:y:1h", c), at.BLOCKLIST_INVALID)

    def test_valid_config_file_without_blocklist_key_blocks_nothing(self):
        c = at.load_config(self._config_file('{"layers": {"size_usd": 5}}'))
        self.assertEqual(c["layers"]["size_usd"], 5)
        self.assertIsNone(at.trade_block_reason("layer:rsi:rsi_events:15m", c))

    # ---- restart: the blocked alert stays consumed

    def test_restart_does_not_replay_a_blocked_alert(self):
        c = shipped_cfg()
        st = {"tom_last_alert_no": 43}
        self.feed({"layer": "session", "sub": "session_momentum", "tf": "15m", "side": "long"}, st=st)
        at.cycle(st, c, False, {}, NOW)
        self.assertEqual(self.events(), ["layer_trade_blocked"])
        state_file = Path(self.tmp.name) / "state.json"
        at.save_json(state_file, st)                               # what main() does after each cycle
        st2 = at.load_json(state_file, {})                         # process restart
        at.cycle(st2, c, False, {}, NOW)
        at.cycle(st2, c, False, {}, NOW)
        self.assertEqual(self.events(), ["layer_trade_blocked"])   # exactly one event, no retry per poll
        self.assertEqual(self.placed, [])

    def test_unblocking_later_does_not_resurrect_old_blocked_alert(self):
        c = shipped_cfg()
        st = {"tom_last_alert_no": 43}
        self.feed({"layer": "fabio", "sub": "escalation", "tf": "1h", "side": "long"}, st=st)
        at.cycle(st, c, False, {}, NOW)
        c["trade_blocklist"] = []
        at.cycle(st, c, False, {}, NOW)
        self.assertEqual(self.placed, [])

    def test_api_error_path_unchanged_for_non_blocked_layer(self):
        """place() failing (entry_failed / plan_refused) leaves the slot free and logs; blocklist adds no new path."""
        at.place = lambda sig, dry, account=None: {"outcome": "entry_failed", "plan_id": "x"}
        st = {"tom_last_alert_no": 43}
        self.feed({"layer": "rsi", "sub": "rsi_events", "tf": "1h", "side": "long"}, st=st)
        self.assertEqual(at.cycle(st, shipped_cfg(), False, {}, NOW), {})
        self.assertEqual(self.events(), ["trade_attempt"])

    # ---- desktop routing: layers go to named-account slots (jishu_4 for rsi via "layer:")

    def test_non_blocked_layer_placed_on_routed_account(self):
        self.routed("jishu_1", "jishu_2", "jishu_3", "jishu_4")
        c = shipped_cfg()
        st = {"tom_last_alert_no": 43}
        self.feed({"layer": "rsi", "sub": "rsi_events", "tf": "1h", "side": "long"},
                  {"layer": "session", "sub": "session_momentum", "tf": "15m", "side": "long"}, st=st)
        extra = {}
        active = at.cycle(st, c, False, {}, NOW, extra)
        self.assertEqual([s["source"] for s in self.placed], ["layer:rsi:rsi_events:1h"])
        self.assertEqual(self.placed_accounts, [c["accounts"]["layer:rsi:rsi_events:1h"]])
        self.assertEqual(active, {})
        self.assertEqual(extra[c["accounts"]["layer:rsi:rsi_events:1h"]]["source"], "layer:rsi:rsi_events:1h")
        self.assertIn("layer_trade_blocked", self.events())

    def test_blocked_layer_never_placed_on_routed_account(self):
        self.routed("jishu_1", "jishu_2", "jishu_3", "jishu_4")
        st = {"tom_last_alert_no": 43}
        self.feed(*[a for a, _ in BLOCKED_ALERTS], st=st)
        extra = {}
        at.cycle(st, shipped_cfg(), False, {}, NOW, extra)
        self.assertEqual(self.placed, [])
        self.assertEqual(extra, {})

    def test_routed_api_error_leaves_account_slot_free(self):
        self.routed("jishu_3")
        at.place = lambda sig, dry, account=None: {"outcome": "entry_failed", "plan_id": "x"}
        st = {"tom_last_alert_no": 43}
        self.feed({"layer": "rsi", "sub": "rsi_events", "tf": "1h", "side": "long"}, st=st)
        extra = {}
        self.assertEqual(at.cycle(st, shipped_cfg(), False, {}, NOW, extra), {})
        self.assertEqual(extra, {})


if __name__ == "__main__":
    unittest.main()
