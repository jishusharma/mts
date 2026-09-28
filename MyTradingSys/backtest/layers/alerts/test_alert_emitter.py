import json
import shutil
import tempfile
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.alerts.alert_emitter import (
    format_alert, new_alerts, append_alerts_jsonl,
)


class TestFormatAlert(unittest.TestCase):
    """Spec 080-alert-emitter.md hand-computed check."""

    def test_hand_computed_check(self):
        event = {"t": 100, "event": "support", "level_value": 60, "tolerance_used": 2, "penetration": 1}
        got = format_alert("rsi", "rsi_events", "1h", event, "rsi_default_2026-09-28",
                            rsi_value=61.0, rsi_ma_value=None)
        expected = {
            "layer": "rsi", "sub": "rsi_events", "tf": "1h",
            "params_id": "rsi_default_2026-09-28", "rsi": 61.0, "rsi_ma": None,
            "t_close": 100, "event": "support", "level_value": 60,
            "tolerance_used": 2, "penetration": 1,
        }
        self.assertEqual(got, expected)
        # original event dict must not be mutated (still has "t", not "t_close")
        self.assertEqual(event, {"t": 100, "event": "support", "level_value": 60,
                                  "tolerance_used": 2, "penetration": 1})

    def test_missing_t_key_raises(self):
        with self.assertRaises(ValueError):
            format_alert("rsi", "rsi_events", "1h", {"event": "support"}, "params")

    def test_passes_through_sub_layer_specific_keys_unchanged(self):
        event = {"t": 21, "event": "rejection", "rule_id": "MLK-S2", "side": "short", "regime": "BEAR"}
        got = format_alert("rsi", "malkan_40_60", "1d", event, "malkan_40_60_default_2026-09-28")
        self.assertEqual(got["rule_id"], "MLK-S2")
        self.assertEqual(got["side"], "short")
        self.assertEqual(got["regime"], "BEAR")
        self.assertEqual(got["t_close"], 21)
        self.assertNotIn("t", got)


class TestNewAlerts(unittest.TestCase):
    """Spec 080 hand-computed check + first-check convention."""

    def test_hand_computed_check(self):
        prev = [{"t": 6, "event": "rejection"}]
        curr = [{"t": 6, "event": "rejection"}, {"t": 8, "event": "cross", "direction": "up"}]
        got = new_alerts(prev, curr)
        self.assertEqual(got, [{"t": 8, "event": "cross", "direction": "up"}])

    def test_empty_prev_means_everything_is_new(self):
        curr = [{"t": 1, "event": "support"}, {"t": 2, "event": "failure"}]
        self.assertEqual(new_alerts([], curr), curr)

    def test_does_not_mutate_inputs(self):
        prev = [{"t": 6, "event": "rejection"}]
        curr = [{"t": 6, "event": "rejection"}, {"t": 8, "event": "cross"}]
        prev_copy = [dict(e) for e in prev]
        curr_copy = [dict(e) for e in curr]
        new_alerts(prev, curr)
        self.assertEqual(prev, prev_copy)
        self.assertEqual(curr, curr_copy)


class TestAppendAlertsJsonl(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)

    def test_writes_one_sorted_json_line_per_alert_and_returns_count(self):
        path = Path(self.tmpdir) / "alerts" / "1h.jsonl"
        alerts = [{"t_close": 1, "event": "support"}, {"t_close": 2, "event": "failure"}]
        n = append_alerts_jsonl(alerts, path)
        self.assertEqual(n, 2)
        lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0]), alerts[0])
        self.assertEqual(json.loads(lines[1]), alerts[1])

    def test_appends_on_subsequent_calls(self):
        path = Path(self.tmpdir) / "1h.jsonl"
        append_alerts_jsonl([{"t_close": 1, "event": "a"}], path)
        append_alerts_jsonl([{"t_close": 2, "event": "b"}], path)
        lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)

    def test_empty_alerts_creates_parent_dir_but_not_file(self):
        path = Path(self.tmpdir) / "nested" / "1h.jsonl"
        n = append_alerts_jsonl([], path)
        self.assertEqual(n, 0)
        self.assertTrue(path.parent.is_dir())
        self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
