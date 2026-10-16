"""Offline tests for the auto_trader promotion DEFAULT-DENY gate (fable H1; no exchange, no subprocess).
Run: python -m pytest MyTradingSys/execution/test_auto_trader_promotion.py

Rule: a source with no promoted_setups.json entry trades only if it starts with a pre_pipeline_sources prefix; a shadow
entry never trades; an unreadable registry or malformed grandfather list rejects everything (Tom included).
The gate only decides accept/reject of a signal: it moves no balance and holds no state, so non-trade balance moves
(deposits, fees, funding) are untouched by construction; the registry and list are re-read on every call (restart)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_trader as at  # noqa: E402
import test_auto_trader as _base  # noqa: E402

NOW, T15, tom_alert = _base.NOW, _base.LayerSignalTest.T15, _base.tom_alert
SHIPPED = Path(__file__).resolve().parent / "auto_trader_config.json"
UNREG = "unregistered (promotion pipeline)"

# Independent fixture: every source that can trade today (an alert per concrete source of each calibrated family).
# Derived by hand from size_overrides + accounts in the config as of 2026-10-16, not from pre_pipeline_sources.
TODAYS_SOURCES = [
    ("turn_of_candle", "turn_of_candle", "1m"), ("rsi", "rsi_events", "5m"), ("rsi", "rsi_events", "15m"),
    ("rsi", "rsi_events", "1h"), ("rsi", "malkan_bull", "15m"), ("rsi", "malkan_bear", "1h"),
    ("session", "session_levels", "15m"), ("positioning", "funding_cvd_fade", "1h"),
    ("fabio", "cvd_absorption", "15m"), ("fabio", "cvd_absorption", "1h"), ("fabio", "escalation", "1h"),
    ("fabio", "volume_fvg", "15m"), ("fabio", "other_sub", "15m"),
    ("cryptocred", "sr_flip", "15m"), ("cryptocred", "sr_flip", "1h"), ("cryptocred", "fib_pullback", "15m"),
    ("cryptocred", "fib_pullback", "1h"), ("cryptocred", "other_sub", "15m"),
]


def alert(layer, sub, tf="15m"):
    t = T15 if tf == "15m" else int((NOW.timestamp() - at.TF_SECONDS[tf] * 1.1) * 1000)
    return {"layer": layer, "sub": sub, "tf": tf, "side": "long", "event": "x", "t_close": t}


def shipped_cfg():
    c = at.load_config(SHIPPED)
    c["trade_blocklist"], c["trade_blocklist_reasons"] = [], {}   # promotion gate only; blocklist is tested elsewhere
    return c


class PromotionGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.reg = Path(self.tmp.name) / "promoted_setups.json"
        self.write_reg([])
        saved = getattr(at, "PROMOTED_SETUPS", None)
        self.addCleanup(setattr, at, "PROMOTED_SETUPS", saved)
        at.PROMOTED_SETUPS = self.reg

    def write_reg(self, entries, raw=None):
        self.reg.write_text(raw if raw is not None else json.dumps({"version": 1, "entries": entries}),
                            encoding="utf-8", newline="\n")

    @staticmethod
    def entry(setup_id, mode):
        return {"setup_id": setup_id, "mode": mode, "manifest": "m.json", "promoted_at": "2026-10-16", "commit": "abc"}

    def sig(self, layer, sub, tf="15m", cfg=None):
        return at.layer_signal(alert(layer, sub, tf), cfg or shipped_cfg(), NOW)

    # --- no behaviour change for today's trading set --------------------------------------------------------------
    def test_todays_sources_still_trade_with_shipped_config(self):
        for layer, sub, tf in TODAYS_SOURCES:
            s = self.sig(layer, sub, tf)
            self.assertNotIn("reject", s, s.get("reject"))
            self.assertIn("plan_args", s)

    def test_tom_passes_the_gate_with_shipped_config(self):
        self.assertIsNone(at.promotion_reject("tom", shipped_cfg()))
        s = at.tom_signal(tom_alert(), {"tom_last_alert_no": 43}, shipped_cfg(), NOW)
        self.assertNotEqual(s.get("reject"), UNREG)
        self.assertFalse(str(s.get("reject", "")).startswith("promotion registry error"))

    # --- default deny --------------------------------------------------------------------------------------------
    def test_new_layer_with_rules_size_and_account_but_no_entry_is_rejected(self):
        c = shipped_cfg()
        c["size_overrides"]["layer:newbie:"] = {"size_usd": 50, "max_loss_usd": 2}
        c["accounts"]["layer:newbie:"] = "jishu_22"
        s = self.sig("newbie", "n1", cfg=c)
        self.assertEqual(s["reject"], UNREG)
        self.assertNotIn("plan_args", s)

    def test_catch_all_only_source_is_rejected(self):
        self.assertEqual(self.sig("consensus", "c1")["reject"], UNREG)

    def test_testnet_entry_lets_a_new_layer_trade(self):
        self.write_reg([self.entry("layer:newbie:", "testnet")])
        self.assertNotIn("reject", self.sig("newbie", "n1"))

    def test_shadow_entry_beats_grandfather(self):
        self.write_reg([self.entry("layer:session:", "shadow")])
        s = self.sig("session", "session_levels")
        self.assertIn("collection_only", s["reject"])

    def test_registry_is_reread_every_call(self):
        self.assertEqual(self.sig("newbie", "n1")["reject"], UNREG)
        self.write_reg([self.entry("layer:newbie:", "testnet")])          # "restart": nothing cached in the process
        self.assertNotIn("reject", self.sig("newbie", "n1"))
        self.write_reg([self.entry("layer:newbie:", "shadow")])
        self.assertIn("collection_only", self.sig("newbie", "n1")["reject"])

    def test_tom_unregistered_when_not_grandfathered(self):
        c = _base.cfg()
        c["pre_pipeline_sources"] = {"layer:": {"reason": "r", "review_by": "2026-10-23"}}
        s = at.tom_signal(tom_alert(), {"tom_last_alert_no": 43}, c, NOW)
        self.assertEqual(s["reject"], UNREG)

    # --- fail closed ----------------------------------------------------------------------------------------------
    def test_unreadable_registry_rejects_every_layer_and_tom(self):
        for raw in ("{not json", json.dumps({"version": 2, "entries": []}), json.dumps({"version": 1, "entries": [1]})):
            self.write_reg([], raw=raw)
            for layer, sub, tf in TODAYS_SOURCES[:4]:
                self.assertIn("promotion registry error", self.sig(layer, sub, tf)["reject"])
            s = at.tom_signal(tom_alert(), {"tom_last_alert_no": 43}, _base.cfg(), NOW)
            self.assertIn("promotion registry error", s["reject"])

    def test_missing_registry_file_rejects_all(self):
        self.reg.unlink()
        self.assertIn("promotion registry error", self.sig("rsi", "rsi_events", "5m")["reject"])
        self.assertIn("promotion registry error", at.promotion_reject("tom", _base.cfg()))

    def test_malformed_grandfather_list_rejects_all(self):
        good = {"reason": "r", "review_by": "2026-10-23"}
        bad_tables = [None, [], "x", {"layer:": "oops"}, {"layer:": {"reason": "r"}},
                      {"layer:": {"reason": "", "review_by": "2026-10-23"}},
                      {"layer:": {"reason": "r", "review_by": "next week"}},
                      {"layer:": {"reason": "r", "review_by": "2026-13-40"}},
                      {"": good}, {"layer:": good, "tom": 5}]
        for t in bad_tables:
            c = _base.cfg()
            c["pre_pipeline_sources"] = t
            self.assertIn("promotion registry error", self.sig("rsi", "rsi_events", "5m", cfg=c)["reject"], t)
            self.assertIn("promotion registry error", at.promotion_reject("tom", c), t)

    def test_unreadable_config_rejects_layers_and_tom(self):
        c = at.load_config(Path(self.tmp.name) / "no_such_config.json")
        self.assertIsNone(c["pre_pipeline_sources"])
        self.assertIn("promotion registry error", self.sig("rsi", "rsi_events", "5m", cfg=c)["reject"])
        self.assertIn("promotion registry error", at.promotion_reject("tom", c))

    def test_missing_key_means_empty_list_default_deny(self):
        c = _base.cfg()
        del c["pre_pipeline_sources"]
        self.assertEqual(at.promotion_reject("layer:rsi:rsi_events:5m", {**c, "pre_pipeline_sources": {}}), UNREG)

    # --- the shipped list ------------------------------------------------------------------------------------------
    def test_shipped_list_is_explicit_and_complete(self):
        raw = json.loads(SHIPPED.read_text(encoding="utf-8"))
        gf = raw["pre_pipeline_sources"]
        want = {k for k in list(raw["size_overrides"]) + list(raw["accounts"]) if k != "layer:"} | {"tom"}
        self.assertEqual(set(gf), want)
        self.assertNotIn("layer:", gf)                                    # the catch-all would defeat default-deny
        for k, v in gf.items():
            self.assertTrue(v["reason"].startswith(("grandfathered pre-pipeline testnet calibration",
                                                    "grandfathered testnet calibration, operator 2026-10-16")), k)
            self.assertEqual(v["review_by"], "2026-10-23", k)


if __name__ == "__main__":
    unittest.main()
