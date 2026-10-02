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

    def test_max_hold_is_8_bars_of_signal_tf(self):
        for tf, mins in (("15m", "120"), ("1h", "480")):
            t = self.T15 if tf == "15m" else int(datetime(2026, 9, 28, 23, 0, tzinfo=timezone.utc).timestamp() * 1000)
            s = at.layer_signal({"layer": "rsi", "event": "support", "tf": tf, "t_close": t}, cfg(), NOW)
            self.assertEqual(s["plan_args"][s["plan_args"].index("--max-hold-minutes") + 1], mins)

    def test_tom_max_hold_is_8_bars_of_zone_tf(self):
        # tom_alert() ZONE is 15m_swing_high: 8 x 15 = 120; 5m -> 40; 1h -> 480; no tf -> 15m fallback
        for zone, mins in (("15m_swing_high", "120"), ("5m_swing_high", "40"), ("1h_swing_low", "480"), ("weird", "120")):
            a = tom_alert()
            a["card_text"] = a["card_text"].replace("15m_swing_high", zone)
            s = at.tom_signal(a, {"tom_last_alert_no": 43}, cfg(), NOW)
            self.assertEqual(s["plan_args"][s["plan_args"].index("--max-hold-minutes") + 1], mins, zone)

    def test_tom_explicit_max_hold_minutes_wins_and_bars_can_be_disabled(self):
        c = cfg()
        c["tom"]["max_hold_minutes"] = 30
        s = at.tom_signal(tom_alert(), {"tom_last_alert_no": 43}, c, NOW)
        self.assertEqual(s["plan_args"][s["plan_args"].index("--max-hold-minutes") + 1], "30")
        c = cfg()
        c["tom"]["max_hold_bars"] = None
        s = at.tom_signal(tom_alert(), {"tom_last_alert_no": 43}, c, NOW)
        self.assertNotIn("--max-hold-minutes", s["plan_args"])

    # ---- 2026-10-02: 3m in TF_SECONDS ---------------------------------------------------------------------------
    # Expected numbers by hand: 3 min = 180 s; max-hold minutes = max_hold_bars (8, DEFAULT_CONFIG) * 180 s / 60 = 24;
    # freshness window = max_age_bars (1.2) * 180 s = 216 s. Before the fix a "3m_" zone fell back to the 15m default
    # (8 * 900 / 60 = 120) and a 3m layer alert was rejected "no t_close/tf".
    T3 = int(datetime(2026, 9, 28, 23, 54, tzinfo=timezone.utc).timestamp() * 1000)  # opens 23:54, closes 23:57, NOW = 180 s after close

    def test_tf_seconds_has_3m_and_keeps_1d(self):
        self.assertEqual(at.TF_SECONDS.get("3m"), 180)
        self.assertEqual(at.TF_SECONDS.get("1d"), 86400)

    def test_tom_3m_zone_max_hold_is_8_bars_of_3m(self):
        a = tom_alert()
        a["card_text"] = a["card_text"].replace("15m_swing_high", "3m_swing_high")
        s = at.tom_signal(a, {"tom_last_alert_no": 43}, cfg(), NOW)
        self.assertNotIn("reject", s)
        self.assertEqual(s["detail"]["zone_tf"], "3m")
        self.assertEqual(s["plan_args"][s["plan_args"].index("--max-hold-minutes") + 1], "24")

    def test_layer_3m_alert_is_accepted_when_fresh_with_max_hold_8_bars(self):
        s = at.layer_signal({"layer": "rsi", "sub": "rsi_events", "event": "support", "tf": "3m",
                             "t_close": self.T3}, cfg(), NOW)
        self.assertNotIn("reject", s)
        self.assertEqual(s["plan_args"][s["plan_args"].index("--max-hold-minutes") + 1], "24")

    def test_layer_3m_alert_stale_after_1_2_bars(self):
        # opens 23:50, closes 23:53, NOW 00:00:00 -> 420 s after close > 216 s
        t = int(datetime(2026, 9, 28, 23, 50, tzinfo=timezone.utc).timestamp() * 1000)
        s = at.layer_signal({"layer": "rsi", "sub": "rsi_events", "event": "support", "tf": "3m", "t_close": t}, cfg(), NOW)
        self.assertIn("stale", s.get("reject", ""))

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
                                                   "LOG_PATH", "place", "AUTO_PAUSE", "record_ledger",
                                                   "exchange_flat", "spawn_manager", "OPERATOR_ALERTS")}
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
        self.ledger = []
        at.record_ledger = lambda *a: self.ledger.append(a)
        self.flat = True
        at.exchange_flat = lambda acct=None: self.flat
        self.spawned = []
        at.spawn_manager = lambda pid, acct=None: (self.spawned.append((pid, acct)), P(rc=None))[1]
        at.OPERATOR_ALERTS = d / "alerts.log"

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
        self.assertEqual(self.ledger, [("old", "tom", None, 0)])    # outcome ledger hook

    def test_closed_named_account_trade_writes_ledger_with_account(self):
        extra = {"jishu_2": {"proc": self.P(rc=1), "plan_id": "px", "source": "layer:rsi:x:15m"}}
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW, extra=extra)
        self.assertEqual(self.ledger, [("px", "layer:rsi:x:15m", "jishu_2", 1)])
        self.assertEqual(extra, {})

    def test_manager_exit_with_open_position_respawns_and_keeps_slot(self):
        self.flat = False
        extra = {"jishu_2": {"proc": self.P(rc=3), "plan_id": "px", "source": "layer:rsi:x:15m"}}
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW, extra=extra)
        self.assertIn("jishu_2", extra)
        self.assertEqual(self.spawned, [("px", "jishu_2")])
        self.assertIsNone(extra["jishu_2"]["proc"].poll())
        self.assertEqual(self.ledger, [])
        self.assertEqual(self.events(), ["manager_lost"])

    def test_default_slot_open_position_respawn_uses_no_account(self):
        self.flat = False
        active = {"proc": self.P(rc=1), "plan_id": "old", "source": "tom"}
        active = at.cycle({"tom_last_alert_no": 43}, cfg(), False, active, NOW)
        self.assertEqual(active["plan_id"], "old")
        self.assertEqual(self.spawned, [("old", None)])

    def test_manager_exit_with_flat_account_closes_trade(self):
        self.flat = True
        extra = {"jishu_2": {"proc": self.P(rc=1), "plan_id": "px", "source": "s"}}
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW, extra=extra)
        self.assertEqual(extra, {})
        self.assertEqual(self.spawned, [])
        self.assertEqual(self.events(), ["trade_closed"])
        self.assertEqual(self.ledger, [("px", "s", "jishu_2", 1)])

    def test_respawn_limit_writes_operator_alert_and_keeps_slot_busy(self):
        self.flat = False
        extra = {"jishu_2": {"proc": self.P(rc=3), "plan_id": "px", "source": "s", "respawns": at.MAX_RESPAWNS}}
        for _ in range(2):
            at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW, extra=extra)
        self.assertIn("jishu_2", extra)
        self.assertEqual(self.spawned, [])
        self.assertEqual(len(at.OPERATOR_ALERTS.read_text(encoding="utf-8").splitlines()), 1)   # alerted once
        self.assertEqual(self.events(), ["manager_lost"])

    def test_unreadable_exchange_keeps_slot_without_respawn(self):
        self.flat = None
        extra = {"jishu_2": {"proc": self.P(rc=3), "plan_id": "px", "source": "s"}}
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW, extra=extra)
        self.assertIn("jishu_2", extra)
        self.assertEqual(self.spawned, [])
        self.assertEqual(self.ledger, [])

    def test_failed_entry_leaves_slot_free(self):
        at.place = lambda sig, dry: {"outcome": "entry_failed", "plan_id": "x"}
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")
        self.assertEqual(at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW), {})


class RecoverTest(CycleTest):
    """Restart recovery: adopt live managers, respawn dead ones with an open position, close dead+flat ones."""

    def attempt(self, plan_id, account=None, source="layer:rsi:x:15m"):
        return {"ts": "2026-09-29T18:00:00Z", "event": "trade_attempt", "source": source, "outcome": "entered",
                "plan_id": plan_id, "account": account}

    def write_log(self, rows):
        at.LOG_PATH.write_text("".join(json.dumps(r) + chr(10) for r in rows), encoding="utf-8")

    def cmd(self, plan_id, exe="C:/Py/python.exe"):
        return f"{exe} C:/repo/MyTradingSys/execution/position_manager.py {plan_id}"

    def logged(self):
        return [json.loads(l) for l in at.LOG_PATH.read_text(encoding="utf-8").splitlines()]

    def test_open_plans_skip_closed_and_non_entered(self):
        self.write_log([self.attempt("a"), self.attempt("b"), {"event": "trade_closed", "plan_id": "a"},
                        {"event": "trade_attempt", "outcome": "no_fill", "plan_id": "c"}])
        self.assertEqual([e["plan_id"] for e in at.open_plans_from_log()], ["b"])

    def test_manager_pids_exact_plan_and_python_only(self):
        procs = [(1, self.cmd("L-1")), (2, self.cmd("L-10")), (3, 'bash.exe -c "x position_manager.py L-1"'),
                 (4, self.cmd("L-1").replace("python.exe", "pythonw.exe"))]
        self.assertEqual(at.manager_pids("L-1", procs), [1, 4])

    def test_alive_manager_is_adopted_named_account_from_log(self):
        self.write_log([self.attempt("L-9", "jishu_2")])
        alive = {77: True}
        self.flat = None     # exchange must not be needed while the manager lives
        active, extra = at.recover_slots(procs=[(77, self.cmd("L-9"))], alive_fn=lambda pid: alive[pid])
        self.assertEqual(active, {})
        self.assertEqual(extra["jishu_2"]["plan_id"], "L-9")
        self.assertEqual([e["event"] for e in self.logged() if e["event"] == "adopted"], ["adopted"])
        # busy: a new signal for that account is skipped, then manager exits -> exchange check via settle_slot
        self.assertFalse(at.settle_slot(extra["jishu_2"], "jishu_2"))
        alive[77] = False
        self.flat = True
        self.assertTrue(at.settle_slot(extra["jishu_2"], "jishu_2"))
        self.assertEqual(self.ledger, [("L-9", "layer:rsi:x:15m", "jishu_2", at.ADOPTED_RC)])

    def test_dead_manager_open_position_is_respawned(self):
        self.write_log([self.attempt("L-5")])
        self.flat = False
        active, extra = at.recover_slots(procs=[])
        self.assertEqual(active["plan_id"], "L-5")
        active = at.cycle({"tom_last_alert_no": 43}, cfg(), False, active, NOW, extra=extra)
        self.assertEqual(self.spawned, [("L-5", None)])
        self.assertEqual(active["plan_id"], "L-5")
        self.assertEqual(self.ledger, [])

    def test_dead_manager_flat_account_is_closed_with_ledger_row(self):
        self.write_log([self.attempt("L-6", "jishu_3")])
        self.flat = True
        active, extra = at.recover_slots(procs=[])
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, active, NOW, extra=extra)
        self.assertEqual(extra, {})
        self.assertEqual(self.spawned, [])
        self.assertEqual(self.ledger, [("L-6", "layer:rsi:x:15m", "jishu_3", at.ADOPTED_RC)])
        self.assertIn("trade_closed", [e["event"] for e in self.logged()])

    def test_older_dead_plan_of_same_account_is_superseded(self):
        self.write_log([self.attempt("old"), self.attempt("new")])
        active, extra = at.recover_slots(procs=[(5, self.cmd("new"))], alive_fn=lambda p: True)
        self.assertEqual(active["plan_id"], "new")
        ev = self.logged()
        self.assertTrue(any(e.get("plan_id") == "old" and e.get("note") == "superseded_at_restart" for e in ev))



if __name__ == "__main__":
    unittest.main(verbosity=1)
