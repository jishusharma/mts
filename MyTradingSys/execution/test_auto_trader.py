"""Offline tests for auto_trader.py (no exchange, no subprocess). Run: python MyTradingSys/execution/test_auto_trader.py"""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_trader as at  # noqa: E402

NOW = datetime(2026, 9, 29, 0, 0, 0, tzinfo=timezone.utc)


def cfg():
    return json.loads(json.dumps(at.DEFAULT_CONFIG))


def tom_alert(no=44, verdict="SETUP_FORMING", setup="ct_short", entry=83537.3, stop=83704.37, target=82985.43,
              time="2026-09-28T23:58:00Z", rr="gross 3.3 / net 2.48"):
    card = (f"ALERT #{no}\n---\nVERDICT: {verdict}\nWHY:     proof 5\nTIME:    {time}\nPRICE:   83523.8\n"
            f"SETUP:   {setup}\nZONE:    15m_swing_high @ {entry}\n\nENTRY:   {entry}\nSTOP:    {stop}\n"
            f"TARGET:  {target}\nR:R:     {rr}\n")
    return {"title": f"MTS ALERT #{no}", "card_text": card}


class TomSignalTest(unittest.TestCase):
    def test_actionable_short_builds_limit_plan(self):
        st = {"tom_last_alert_no": 43}
        s = at.tom_signal(tom_alert(), st, cfg(), NOW)
        self.assertNotIn("reject", s)
        a = s["plan_args"]
        self.assertEqual(a[a.index("--side") + 1], "short")
        self.assertEqual(a[a.index("--entry") + 1], "limit")
        self.assertEqual(float(a[a.index("--price") + 1]), 83537.3)
        # stop % = (83704.37-83537.3)/83537.3*100 = 0.2 (hand: 167.07/83537.3 = 0.0019999)
        self.assertAlmostEqual(float(a[a.index("--stop") + 1]), 0.2, places=3)
        # target % = (83537.3-82985.43)/83537.3*100 = 0.661 (hand: 551.87/83537.3)
        self.assertAlmostEqual(float(a[a.index("--targets") + 1]), 0.661, places=3)
        self.assertEqual(st["tom_last_alert_no"], 44)

    def test_same_alert_not_traded_twice(self):
        st = {"tom_last_alert_no": 43}
        self.assertIsNotNone(at.tom_signal(tom_alert(), st, cfg(), NOW))
        self.assertIsNone(at.tom_signal(tom_alert(), st, cfg(), NOW))

    def test_older_alert_ignored(self):
        self.assertIsNone(at.tom_signal(tom_alert(no=40), {"tom_last_alert_no": 43}, cfg(), NOW))

    def test_non_actionable_verdict_rejected(self):
        s = at.tom_signal(tom_alert(verdict="WAIT_RR"), {"tom_last_alert_no": 0}, cfg(), NOW)
        self.assertIn("verdict", s["reject"])

    def test_stale_alert_rejected(self):
        s = at.tom_signal(tom_alert(time="2026-09-28T23:50:00Z"), {"tom_last_alert_no": 0}, cfg(), NOW)
        self.assertIn("stale", s["reject"])

    def test_low_net_rr_rejected(self):
        s = at.tom_signal(tom_alert(rr="gross 2.1 / net 1.75"), {"tom_last_alert_no": 0}, cfg(), NOW)
        self.assertIn("net_rr", s["reject"])

    def test_misordered_levels_rejected(self):
        # short with stop BELOW entry is inconsistent -> never trade it
        s = at.tom_signal(tom_alert(stop=83000.0, target=82000.0), {"tom_last_alert_no": 0}, cfg(), NOW)
        self.assertIn("not ordered", s["reject"])

    def test_long_setup(self):
        s = at.tom_signal(tom_alert(setup="tf_long", entry=80000, stop=79600, target=81200),
                          {"tom_last_alert_no": 0}, cfg(), NOW)
        self.assertEqual(s["side"], "long")
        self.assertNotIn("reject", s)

    def test_garbage_alert(self):
        self.assertIsNone(at.tom_signal({"title": "x"}, {"tom_last_alert_no": 0}, cfg(), NOW))
        self.assertIsNone(at.tom_signal({}, {}, cfg(), NOW))


class LayerSignalTest(unittest.TestCase):
    T15 = int(datetime(2026, 9, 28, 23, 30, tzinfo=timezone.utc).timestamp() * 1000)  # opens 23:30, closes 23:45

    def test_rsi_support_long(self):
        s = at.layer_signal({"layer": "rsi", "sub": "rsi_events", "event": "support", "tf": "15m",
                             "t_close": self.T15}, cfg(), NOW)
        self.assertEqual(s["side"], "long")
        self.assertNotIn("reject", s)
        self.assertEqual(s["plan_args"][s["plan_args"].index("--entry") + 1], "market")

    def test_rsi_cross_direction(self):
        up = at.layer_signal({"layer": "rsi", "event": "cross", "direction": "up", "tf": "15m",
                              "t_close": self.T15}, cfg(), NOW)
        dn = at.layer_signal({"layer": "rsi", "event": "cross", "direction": "down", "tf": "15m",
                              "t_close": self.T15}, cfg(), NOW)
        self.assertEqual((up["side"], dn["side"]), ("long", "short"))

    def test_side_field_wins_for_new_layers(self):
        s = at.layer_signal({"layer": "brand_new_layer", "kind": "x", "side": "short", "tf": "1h",
                             "t_close": self.T15}, cfg(), NOW)
        self.assertEqual(s["side"], "short")
        self.assertNotIn("reject", s)

    def test_unmapped_event_rejected(self):
        s = at.layer_signal({"layer": "rsi", "event": "wiggle", "tf": "15m", "t_close": self.T15}, cfg(), NOW)
        self.assertIn("unmapped", s["reject"])

    def test_stale_bar_rejected(self):
        old = self.T15 - 3 * 900 * 1000   # closed 45 min before the fresh one -> > 1.2 bars old
        s = at.layer_signal({"layer": "rsi", "event": "support", "tf": "15m", "t_close": old}, cfg(), NOW)
        self.assertIn("stale", s["reject"])

    def test_disabled_layer(self):
        c = cfg()
        c["disabled_layers"] = ["rsi"]
        s = at.layer_signal({"layer": "rsi", "event": "support", "tf": "15m", "t_close": self.T15}, c, NOW)
        self.assertEqual(s["reject"], "layer disabled")


class OffsetsTest(unittest.TestCase):
    def test_first_sight_skips_history_then_reads_new_complete_lines(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "15m.jsonl"
            f.write_text('{"a": 1}\n', encoding="utf-8")
            st = {}
            self.assertEqual(at.read_new_layer_alerts(st, Path(d)), [])
            with open(f, "a", encoding="utf-8") as fh:
                fh.write('{"a": 2}\n{"a": 3')            # second line not finished yet
            self.assertEqual(at.read_new_layer_alerts(st, Path(d)), [{"a": 2}])
            with open(f, "a", encoding="utf-8") as fh:
                fh.write('}\n')
            self.assertEqual(at.read_new_layer_alerts(st, Path(d)), [{"a": 3}])
            self.assertEqual(at.read_new_layer_alerts(st, Path(d)), [])

    def test_truncated_file_resets_without_replay(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "1h.jsonl"
            f.write_text('{"a": 1}\n{"a": 2}\n', encoding="utf-8")
            st = {}
            at.read_new_layer_alerts(st, Path(d))
            f.write_text('{"b": 1}\n', encoding="utf-8")
            self.assertEqual(at.read_new_layer_alerts(st, Path(d)), [])


class CycleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.saved = {k: getattr(at, k) for k in ("TOM_ALERT", "LAYER_ALERT_DIR", "HALT", "HALT_DAILY_LOSS",
                                                   "LOG_PATH", "place", "AUTO_PAUSE")}
        at.TOM_ALERT, at.LAYER_ALERT_DIR = d / "last_alert.json", d / "alerts"
        at.HALT, at.HALT_DAILY_LOSS, at.LOG_PATH = d / "HALT", d / "HALT_DAILY_LOSS", d / "log.jsonl"
        at.AUTO_PAUSE = d / "AUTO_PAUSE"
        at.LAYER_ALERT_DIR.mkdir()
        self.placed = []

        class P:
            def __init__(s, rc=None):
                s.rc = rc

            def poll(s):
                return s.rc

        self.P = P

        def fake_place(sig, dry_run):
            self.placed.append(sig)
            return {"outcome": "entered", "plan_id": f"p{len(self.placed)}", "proc": P()}
        at.place = fake_place

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(at, k, v)
        self.tmp.cleanup()

    def events(self):
        return [json.loads(l)["event"] for l in at.LOG_PATH.read_text(encoding="utf-8").splitlines()]

    def test_tom_trades_then_layer_skipped_busy(self):
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")
        f = at.LAYER_ALERT_DIR / "15m.jsonl"
        f.write_text("", encoding="utf-8")
        st = {"tom_last_alert_no": 43}
        at.read_new_layer_alerts(st)     # register file offset
        f.write_text(json.dumps({"layer": "rsi", "event": "support", "tf": "15m",
                                 "t_close": LayerSignalTest.T15}) + "\n", encoding="utf-8")
        active = at.cycle(st, cfg(), False, {}, NOW)
        self.assertEqual([s["source"] for s in self.placed], ["tom"])
        self.assertEqual(active["plan_id"], "p1")
        self.assertEqual(self.events(), ["trade_attempt", "skipped_busy"])

    def test_halt_blocks_all_trading(self):
        at.HALT.write_text("x", encoding="utf-8")
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW)
        self.assertEqual(self.placed, [])
        self.assertEqual(self.events(), ["skipped_halt"])

    def test_auto_pause_blocks_only_new_auto_trades(self):
        at.AUTO_PAUSE.write_text("", encoding="utf-8")
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW)
        self.assertEqual(self.placed, [])
        self.assertEqual(self.events(), ["skipped_auto_pause"])
        self.assertFalse(at.HALT.exists())

    def test_closed_trade_frees_the_slot(self):
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")
        active = {"proc": self.P(rc=0), "plan_id": "old", "source": "tom"}
        active = at.cycle({"tom_last_alert_no": 43}, cfg(), False, active, NOW)
        self.assertEqual(self.events(), ["trade_closed", "trade_attempt"])
        self.assertEqual(active["plan_id"], "p1")

    def test_failed_entry_leaves_slot_free(self):
        at.place = lambda sig, dry: {"outcome": "entry_failed", "plan_id": "x"}
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")
        self.assertEqual(at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW), {})


if __name__ == "__main__":
    unittest.main(verbosity=1)
