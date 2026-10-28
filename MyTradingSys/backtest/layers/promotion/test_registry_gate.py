"""Tests for the promotion registry reader and the live shadow gate (registry.py, poll_once wiring, auto_trader reject).
Expected values are written by hand: shadow -> no "side" + collection_only; unregistered / testnet -> unchanged;
unreadable registry -> everything collection-only (fail closed); registry is re-read on every call (restart/reset)."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
from MyTradingSys.backtest.layers.alerts.live_runner_core import build_registry, empty_state
from MyTradingSys.backtest.layers.promotion import registry as reg

EXEC = Path(__file__).resolve().parents[3] / "execution"
sys.path.insert(0, str(EXEC))
import auto_trader as at  # noqa: E402


def entry(setup_id="layer:fabio:volume_fvg:", mode="shadow"):
    return {"setup_id": setup_id, "mode": mode, "manifest": "m.json", "promoted_at": "2026-10-15T00:00:00Z", "commit": "abc"}


def alert(layer="fabio", sub="volume_fvg", tf="1h", **kw):
    a = {"layer": layer, "sub": sub, "tf": tf, "event": "e", "side": "long", "t_close": 1}
    a.update(kw)
    return a


class RegistryFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "promoted_setups.json"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, entries, version=1):
        self.path.write_text(json.dumps({"version": version, "entries": entries}), encoding="utf-8")

    def test_shipped_registry_is_well_formed_and_empty(self):
        self.assertEqual(reg.load_registry(), ([], None))

    def test_empty_registry_changes_nothing(self):
        self.write([])
        a = [alert(), alert(layer="rsi", sub="rsi_events")]
        self.assertEqual(reg.apply_promotion_gate(a, self.path), a)

    def test_shadow_entry_makes_matching_alert_collection_only(self):
        self.write([entry()])
        out = reg.apply_promotion_gate([alert(), alert(layer="rsi", sub="rsi_events")], self.path)
        self.assertNotIn("side", out[0])
        self.assertIs(out[0]["collection_only"], True)
        self.assertEqual(out[0]["shadow_side"], "long")
        self.assertEqual(out[1], alert(layer="rsi", sub="rsi_events"))      # other layer untouched

    def test_testnet_entry_does_not_strip(self):
        self.write([entry(mode="testnet")])
        self.assertEqual(reg.apply_promotion_gate([alert()], self.path), [alert()])

    def test_input_alert_is_not_mutated(self):
        self.write([entry()])
        a = alert()
        reg.apply_promotion_gate([a], self.path)
        self.assertEqual(a, alert())

    def test_unreadable_or_malformed_registry_fails_closed(self):
        bad = [None, "not json", json.dumps([1]), json.dumps({"version": 2, "entries": []}),
               json.dumps({"version": 1, "entries": [{"setup_id": "x"}]}),
               json.dumps({"version": 1, "entries": [entry(mode="live")]}),
               json.dumps({"version": 1, "entries": [entry(), entry()]})]
        for text in bad:
            if text is None:
                if self.path.exists():
                    self.path.unlink()
            else:
                self.path.write_text(text, encoding="utf-8")
            out = reg.apply_promotion_gate([alert()], self.path)
            self.assertNotIn("side", out[0], text)
            self.assertIs(out[0]["collection_only"], True, text)

    def test_registry_is_reread_on_every_call(self):
        self.write([entry()])
        self.assertIs(reg.apply_promotion_gate([alert()], self.path)[0].get("collection_only"), True)
        self.write([])                                   # demoted/removed between two polls (restart or reset)
        self.assertEqual(reg.apply_promotion_gate([alert()], self.path), [alert()])

    def test_non_trade_events_ignored(self):
        # an alert with no side (balance/other events are never alerts) stays side-less and gains no shadow_side
        self.write([entry()])
        out = reg.apply_promotion_gate([alert(side=None)], self.path)
        self.assertNotIn("shadow_side", out[0])

    def test_longest_prefix_wins(self):
        self.write([entry("layer:fabio:", "shadow"), entry("layer:fabio:volume_fvg:", "testnet")])
        self.assertEqual(reg.apply_promotion_gate([alert()], self.path), [alert()])


class PollOnceWiring(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = reg.DEFAULT_PATH
        reg.DEFAULT_PATH = Path(self.tmp.name) / "promoted_setups.json"

    def tearDown(self):
        reg.DEFAULT_PATH = self.old
        self.tmp.cleanup()

    def run_poll(self):
        row = lambda t: [t, "1", "1", "1", "1", "1", t + 59999, "1", 1, "1", "1", "0"]
        raw = [row(0), row(60000), row(120000)]
        r = build_registry([{"layer": "L", "sub": "S", "tf": "1h",
                             "fn": lambda bars: [{"t": b["t"], "event": "e", "side": "long"} for b in bars], "params_id": "P"}])
        return cli.poll_once(r, "BTCUSDT", ["1h"], lambda s, i, l: raw, empty_state())["alerts"]

    def test_poll_once_strips_side_for_shadow_entry(self):
        reg.DEFAULT_PATH.write_text(json.dumps({"version": 1, "entries": [entry("layer:L:S:")]}), encoding="utf-8")
        alerts = self.run_poll()
        self.assertTrue(alerts)
        self.assertTrue(all("side" not in a and a["collection_only"] is True for a in alerts))

    def test_poll_once_unchanged_for_empty_registry(self):
        reg.DEFAULT_PATH.write_text(json.dumps({"version": 1, "entries": []}), encoding="utf-8")
        alerts = self.run_poll()
        self.assertTrue(alerts and all(a.get("side") == "long" and "collection_only" not in a for a in alerts))

    def test_poll_once_fails_closed_on_missing_registry(self):
        alerts = self.run_poll()                 # file does not exist
        self.assertTrue(alerts and all("side" not in a and a["collection_only"] is True for a in alerts))


class AutoTraderRejectsCollectionOnly(unittest.TestCase):
    NOW = datetime(2026, 9, 29, 0, 0, 0, tzinfo=timezone.utc)
    T15 = int(datetime(2026, 9, 28, 23, 30, tzinfo=timezone.utc).timestamp() * 1000)

    def sig(self, **kw):
        a = {"layer": "rsi", "sub": "rsi_events", "event": "support", "tf": "15m", "t_close": self.T15}
        a.update(kw)
        c = json.loads(json.dumps(at.DEFAULT_CONFIG))
        c["pre_pipeline_sources"] = {"layer:rsi:": {"reason": "fixture", "review_by": "2026-10-23"}}   # fable H1 default-deny
        return at.layer_signal(a, c, self.NOW)

    def test_rule_mapped_alert_still_trades_when_not_collection_only(self):
        self.assertNotIn("reject", self.sig())

    def test_rule_mapped_collection_only_alert_is_rejected(self):
        # layer_rules maps rsi:support -> long even without "side": stripping side alone would not stop it
        s = self.sig(collection_only=True)
        self.assertIn("collection_only", s["reject"])


class DecisionForSourceTest(unittest.TestCase):
    """Pure default-deny lookup (fable H1). Hand-written expectations."""
    GF = {"layer:old:": {"reason": "r", "review_by": "2026-10-23"}}

    def test_decisions(self):
        e = [entry("layer:new:", "testnet"), entry("layer:old:x:", "shadow")]
        d = reg.decision_for_source
        self.assertEqual(d("layer:new:a:15m", e, self.GF), "trade")
        self.assertEqual(d("layer:old:x:15m", e, self.GF), "shadow")      # entry beats grandfather
        self.assertEqual(d("layer:old:y:15m", e, self.GF), "trade")       # grandfathered, no entry
        self.assertEqual(d("layer:other:a:15m", e, self.GF), "unregistered")
        self.assertEqual(d("layer:other:a:15m", [], {}), "unregistered")

    def test_errors_fail_closed(self):
        d = reg.decision_for_source
        self.assertEqual(d("layer:old:a:1h", None, self.GF), "registry_error")
        for bad in (None, [], {"layer:old:": {"reason": "r"}}, {"": {"reason": "r", "review_by": "2026-10-23"}}):
            self.assertEqual(d("layer:old:a:1h", [], bad), "registry_error")


if __name__ == "__main__":
    unittest.main()
