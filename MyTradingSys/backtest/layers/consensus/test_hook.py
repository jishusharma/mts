"""Tests for consensus/hook.py. Expected values are written by hand from the fixtures below, not read from the code."""
import json
import tempfile
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.consensus import hook

CARD = ("VERDICT: SETUP_FORMING\nTIME: 2026-10-08 10:00\nPRICE: 101.0\nSETUP: range_long\nENTRY: 100\nSTOP: 99\n"
        "TARGET: 102\nR:R: gross 2.0 / net 1.8\n")


def tom_file(d, no, card=CARD):
    p = Path(d) / "last_alert.json"
    p.write_text(json.dumps({"title": "MTS ALERT #%d" % no, "card_text": card}), encoding="utf-8")
    return p


def fabio_alert(t=1000, **kw):
    a = {"layer": "fabio", "sub": "v3_grid", "tf": "1m", "event": "v3_x_A_long", "model": "A", "side": "long",
         "entry_ref": 100.5, "stop": 99.5, "target": 103.0, "t_close": t}
    a.update(kw)
    return a


class Env:
    """Temp dirs for one test: tom card dir, snapshots, alerts, state, consensus output."""

    def __init__(self, tc):
        self.tmp = tempfile.TemporaryDirectory()
        tc.addCleanup(self.tmp.cleanup)
        r = Path(self.tmp.name)
        self.card_dir, self.snaps, self.alerts, self.out = r / "c", r / "s", r / "a", r / "o"
        for d in (self.card_dir, self.snaps, self.alerts):
            d.mkdir()
        self.state = r / "state.json"

    def call(self, alerts, **kw):
        return hook.consensus_after_poll(alerts, tom_path=self.card_dir / "last_alert.json", snap_dir=self.snaps,
                                         alerts_dir=self.alerts, state_path=self.state, base_dir=self.out, **kw)

    def rows(self):
        out = []
        for f in sorted(self.out.glob("consensus_*.jsonl")) if self.out.exists() else []:
            out += [json.loads(line) for line in f.read_text(encoding="utf-8").splitlines()]
        return out


class ReadTom(unittest.TestCase):
    def test_card_fields_parsed(self):
        e = Env(self)
        tom = hook.read_tom(tom_file(e.card_dir, 6))
        self.assertEqual(tom, {"alert_no": 6, "verdict": "SETUP_FORMING", "setup": "range_long", "side": "long",
                               "entry": 100.0, "stop": 99.0, "target": 102.0, "net_rr": 1.8})

    def test_short_setup_side(self):
        e = Env(self)
        card = CARD.replace("range_long", "range_short")
        self.assertEqual(hook.read_tom(tom_file(e.card_dir, 1, card))["side"], "short")

    def test_missing_stop_or_missing_file_is_none(self):
        e = Env(self)
        self.assertIsNone(hook.read_tom(e.card_dir / "last_alert.json"))
        self.assertIsNone(hook.read_tom(tom_file(e.card_dir, 2, CARD.replace("STOP: 99\n", ""))))

    def test_garbage_json_is_none(self):
        e = Env(self)
        (e.card_dir / "last_alert.json").write_text("{nope", encoding="utf-8")
        self.assertIsNone(hook.read_tom(e.card_dir / "last_alert.json"))


class FabioBlock(unittest.TestCase):
    def test_newest_fabio_alert_wins_and_others_ignored(self):
        got = hook.fabio_from_alerts([fabio_alert(t=1000, model="A"), {"layer": "rsi", "t_close": 9999},
                                      fabio_alert(t=2000, model="B", side="short")])
        self.assertEqual(got, {"verdict": "v3_grid:v3_x_A_long", "model": "B", "side": "short", "entry": 100.5,
                               "stop": 99.5, "target": 103.0})

    def test_shadow_alert_reports_shadow_side(self):
        a = fabio_alert()
        del a["side"]
        a["shadow_side"] = "short"
        self.assertEqual(hook.fabio_from_alerts([a])["side"], "short")

    def test_no_fabio_alert_is_none(self):
        self.assertIsNone(hook.fabio_from_alerts([{"layer": "rsi"}]))
        self.assertIsNone(hook.fabio_from_alerts(None))


class AfterPoll(unittest.TestCase):
    def test_fabio_alert_writes_one_row_with_snapshot_and_null_tom(self):
        e = Env(self)
        (e.snaps / "BTCUSDT_20261008_1200.json").write_text(json.dumps({"current_price": 100.25}), encoding="utf-8")
        (e.snaps / "BTCUSDT_20261008_1100.json").write_text(json.dumps({"current_price": 90.0}), encoding="utf-8")
        self.assertTrue(e.call([fabio_alert()]))
        rows = e.rows()
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r["snapshot_id"], r["price"]), ("BTCUSDT_20261008_1200", 100.25))
        self.assertIsNone(r["tom"])
        self.assertEqual(r["fabio"]["model"], "A")
        self.assertEqual(r["notes"], "trigger=fabio")

    def test_no_core_fired_writes_nothing(self):
        e = Env(self)
        self.assertFalse(e.call([{"layer": "rsi", "tf": "15m"}]))
        self.assertFalse(e.call([]))
        self.assertEqual(e.rows(), [])

    def test_tom_first_start_remembers_card_without_a_row(self):
        e = Env(self)
        tom_file(e.card_dir, 5)
        self.assertFalse(e.call([]))
        self.assertEqual(json.loads(e.state.read_text(encoding="utf-8")), {"tom_alert_no": 5})
        self.assertEqual(e.rows(), [])

    def test_new_tom_alert_writes_row_once(self):
        e = Env(self)
        tom_file(e.card_dir, 5)
        e.call([])
        tom_file(e.card_dir, 6)
        self.assertTrue(e.call([]))
        self.assertFalse(e.call([]))            # same card #6 again: nothing new
        rows = e.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["tom"], {"verdict": "SETUP_FORMING", "setup": "range_long", "side": "long",
                                          "entry": 100.0, "stop": 99.0, "target": 102.0, "net_rr": 1.8})
        self.assertIsNone(rows[0]["fabio"])
        self.assertEqual(rows[0]["notes"], "trigger=tom; snapshot_id absent in input")

    def test_both_cores_in_one_poll_is_one_row(self):
        e = Env(self)
        tom_file(e.card_dir, 5)
        e.call([])
        tom_file(e.card_dir, 6)
        self.assertTrue(e.call([fabio_alert()]))
        rows = e.rows()
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["notes"].startswith("trigger=tom+fabio"))
        self.assertIsNotNone(rows[0]["tom"])
        self.assertIsNotNone(rows[0]["fabio"])

    def test_rsi_block_is_filled_from_persisted_alerts(self):
        e = Env(self)
        rec = {"layer": "rsi", "sub": "rsi_events", "tf": "15m", "event": "support", "rsi": 41.5, "rsi_ma": 44.0,
               "level_value": 40.0, "t_close": 1000, "t_confirm": 2000}
        (e.alerts / "15m.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")
        self.assertTrue(e.call([fabio_alert()]))
        r15 = e.rows()[0]["rsi"]["15m"]
        self.assertEqual((r15["rsi"], r15["ma_sma"], r15["support_or_reject"]), (41.5, 44.0, "support"))
        self.assertIsNone(e.rows()[0]["rsi"]["1h"]["rsi"])

    def test_never_raises_on_broken_inputs(self):
        e = Env(self)
        e.state.write_text("{broken", encoding="utf-8")
        (e.card_dir / "last_alert.json").write_text("[]", encoding="utf-8")
        for bad in (None, [None], [{"layer": "fabio", "t_close": "x"}], "text"):
            try:
                e.call(bad)
            except Exception as exc:  # noqa: BLE001
                self.fail("raised %r for %r" % (exc, bad))

    def test_unwritable_output_returns_false_not_raise(self):
        e = Env(self)
        blocker = Path(e.tmp.name) / "file_not_dir"
        blocker.write_text("x", encoding="utf-8")
        e.out = blocker / "sub"                  # a path under a regular file cannot be created
        self.assertFalse(e.call([fabio_alert()]))


if __name__ == "__main__":
    unittest.main()
