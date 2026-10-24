"""Offline tests for auto_trader.py (no exchange, no subprocess). Run: python MyTradingSys/execution/test_auto_trader.py"""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_trader as at  # noqa: E402
import net_rr_floor as nrf  # noqa: E402  (on sys.path via auto_trader)

NOW = datetime(2026, 9, 29, 0, 0, 0, tzinfo=timezone.utc)


def cfg():
    """Default config with the promotion default-deny (fable H1) grandfathering everything: these tests are about
    sizing/stops/brackets, not the promotion gate (that is test_auto_trader_promotion.py)."""
    c = json.loads(json.dumps(at.DEFAULT_CONFIG))
    gf = {"reason": "test fixture", "review_by": "2026-10-23"}
    c["pre_pipeline_sources"] = {"layer:": dict(gf), "tom": dict(gf)}
    return c


def tom_alert(no=44, verdict="SETUP_FORMING", setup="ct_short", entry=83537.3, stop=83704.37, target=82985.43,
              time="2026-09-28T23:58:00Z", rr="gross 3.3 / net 2.48", runner=None):
    runner_line = f"RUNNER_TARGET: {runner}\n" if runner is not None else ""
    card = (f"ALERT #{no}\n---\nVERDICT: {verdict}\nWHY:     proof 5\nTIME:    {time}\nPRICE:   83523.8\n"
            f"SETUP:   {setup}\nZONE:    15m_swing_high @ {entry}\n\nENTRY:   {entry}\nSTOP:    {stop}\n"
            f"TARGET:  {target}\n{runner_line}R:R:     {rr}\n")
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

    def with_floor(self, content):
        """Point the shared net_rr floor reader at a temp file (content None = file absent)."""
        d = Path(tempfile.mkdtemp())
        f = d / "net_rr_floor.json"
        if content is not None:
            f.write_text(content, encoding="utf-8")
        p = mock.patch.object(nrf, "FLOOR_PATH", f)
        p.start()
        self.addCleanup(p.stop)

    def test_low_net_rr_rejected(self):
        self.with_floor('{"net_rr_floor": 2.0}')
        s = at.tom_signal(tom_alert(rr="gross 2.1 / net 1.75"), {"tom_last_alert_no": 0}, cfg(), NOW)
        self.assertEqual(s["reject"], "net_rr 1.75 < 2.0")

    def test_net_rr_floor_is_the_shared_file_and_is_reread_per_alert(self):
        # net 1.75: floor 1.25 -> accepted; floor 2.0 -> rejected; floor back to 1.25 -> accepted. Same process, no restart.
        self.with_floor('{"net_rr_floor": 1.25}')
        self.assertIsNone(at.tom_signal(tom_alert(no=50, rr="gross 2.1 / net 1.75"), {"tom_last_alert_no": 0}, cfg(), NOW).get("reject"))
        nrf.FLOOR_PATH.write_text('{"net_rr_floor": 2.0}', encoding="utf-8")
        self.assertIn("1.75 < 2.0", at.tom_signal(tom_alert(no=51, rr="gross 2.1 / net 1.75"), {"tom_last_alert_no": 0}, cfg(), NOW).get("reject"))
        nrf.FLOOR_PATH.write_text('{"net_rr_floor": 1.25}', encoding="utf-8")
        self.assertIsNone(at.tom_signal(tom_alert(no=52, rr="gross 2.1 / net 1.75"), {"tom_last_alert_no": 0}, cfg(), NOW).get("reject"))

    def test_unreadable_net_rr_floor_rejects(self):
        self.with_floor(None)
        s = at.tom_signal(tom_alert(rr="gross 9.0 / net 6.75"), {"tom_last_alert_no": 0}, cfg(), NOW)
        self.assertIn("floor unreadable", s["reject"])

    def test_config_carries_no_floor_key(self):
        self.assertNotIn("min_net_rr", at.DEFAULT_CONFIG["tom"])

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


class TomRunnerTest(unittest.TestCase):
    """R2 (2026-10-03): RUNNER_TARGET on the card -> 50/50 two-target plan + breakeven flag; absent -> one target.
    Hand numbers: short entry 83537.3, TARGET 82985.43 -> 0.661 %; RUNNER 82000.0 -> (1537.3/83537.3) = 1.84 %."""

    def sig(self, c=None, **kw):
        return at.tom_signal(tom_alert(**kw), {"tom_last_alert_no": 43}, c or cfg(), NOW)

    def arg(self, s, flag):
        return s["plan_args"][s["plan_args"].index(flag) + 1]

    def test_card_with_runner_builds_two_targets_and_breakeven_flag(self):
        s = self.sig(runner=82000.0)
        self.assertNotIn("reject", s)
        self.assertEqual(self.arg(s, "--targets"), "50@0.661,50@1.84")
        self.assertIn("--breakeven-after-first-target", s["plan_args"])
        self.assertEqual(self.arg(s, "--size"), "200")                      # same total size, the split adds none
        self.assertEqual(s["log"], {"runner_target": 82000.0})

    def test_parse_keeps_target_and_reads_runner(self):
        p = at.parse_tom_alert(tom_alert(runner=82000.0))
        self.assertEqual((p["target"], p["runner_target"], p["alert_no"]), (82985.43, 82000.0, 44))
        self.assertIsNone(at.parse_tom_alert(tom_alert())["runner_target"])

    def test_card_without_runner_is_single_target_exactly_as_before(self):
        s = self.sig()
        self.assertEqual(self.arg(s, "--targets"), "0.661")
        self.assertNotIn("--breakeven-after-first-target", s["plan_args"])
        self.assertEqual(s["log"], {"runner_skipped": "no RUNNER_TARGET"})

    def test_runner_at_or_before_the_target_is_ignored(self):
        for r in (82985.43, 83100.0, 0, "junk"):
            s = self.sig(runner=r)
            self.assertEqual(self.arg(s, "--targets"), "0.661", r)
            self.assertNotIn("--breakeven-after-first-target", s["plan_args"], r)

    def test_long_runner_must_be_above_target(self):
        ok = self.sig(setup="tf_long", entry=80000, stop=79600, target=81200, runner=83000)
        self.assertEqual(self.arg(ok, "--targets"), "50@1.5,50@3.75")
        bad = self.sig(setup="tf_long", entry=80000, stop=79600, target=81200, runner=81000)
        self.assertEqual(self.arg(bad, "--targets"), "1.5")

    def test_share_is_config_and_zero_is_off(self):
        c = cfg()
        c["tom"]["runner_leg_pct"] = 30                                    # near 70 %, runner 30 %
        self.assertEqual(self.arg(self.sig(c, runner=82000.0), "--targets"), "70@0.661,30@1.84")
        c["tom"]["runner_leg_pct"] = 0
        self.assertEqual(self.arg(self.sig(c, runner=82000.0), "--targets"), "0.661")

    def test_rejected_alert_builds_no_plan_even_with_a_runner(self):
        s = self.sig(time="2026-09-28T23:50:00Z", runner=82000.0)
        self.assertIn("stale", s["reject"])
        self.assertNotIn("plan_args", s)

    def test_runner_does_not_touch_layer_signals(self):
        s = at.layer_signal({"layer": "rsi", "event": "support", "tf": "15m", "t_close": LayerSignalTest.T15,
                             "runner_target": 1.0}, cfg(), NOW)
        self.assertNotIn("--breakeven-after-first-target", s["plan_args"])
        self.assertEqual(s["plan_args"][s["plan_args"].index("--targets") + 1], "2")


class LayerSignalTest(unittest.TestCase):
    T15 = int(datetime(2026, 9, 28, 23, 30, tzinfo=timezone.utc).timestamp() * 1000)  # opens 23:30, closes 23:45

    def test_rsi_support_long(self):
        s = at.layer_signal({"layer": "rsi", "sub": "rsi_events", "event": "support", "tf": "15m",
                             "t_close": self.T15}, cfg(), NOW)
        self.assertEqual(s["side"], "long")
        self.assertNotIn("reject", s)
        self.assertEqual(s["plan_args"][s["plan_args"].index("--entry") + 1], "market")

    def test_unmapped_reject_text_uses_fallback_key(self):
        s = at.layer_signal({"layer": "rsi", "kind": "wiggle", "tf": "15m", "t_close": self.T15}, cfg(), NOW)
        self.assertEqual(s["reject"], "unmapped rsi:wiggle (add a layer_rules entry)")

    def test_collection_only_without_side_is_shadow_not_unmapped(self):
        # fabio v3_grid emits shadow events with shadow_side and no side: they must read as shadow, never "unmapped"
        a = {"layer": "fabio", "kind": "v3_grid", "tf": "1m", "t_close": self.T15,
             "collection_only": True, "shadow_side": "long"}
        s = at.layer_signal(a, cfg(), NOW)
        self.assertTrue(s["reject"].startswith("collection_only fabio:v3_grid"), s["reject"])
        self.assertNotIn("plan_args", s)

    def test_non_collection_alert_without_side_is_still_unmapped(self):
        s = at.layer_signal({"layer": "rsi", "kind": "wiggle", "tf": "15m", "t_close": self.T15,
                             "collection_only": False}, cfg(), NOW)
        self.assertTrue(s["reject"].startswith("unmapped"), s["reject"])

    def test_collection_only_with_side_is_rejected(self):
        s = at.layer_signal({"layer": "rsi", "sub": "rsi_events", "event": "support", "tf": "15m",
                             "t_close": self.T15, "collection_only": True}, cfg(), NOW)
        self.assertTrue(s["reject"].startswith("collection_only"), s["reject"])
        self.assertNotIn("plan_args", s)

    def test_disabled_layer_beats_collection_only(self):
        c = cfg()
        c["disabled_layers"] = ["fabio"]
        s = at.layer_signal({"layer": "fabio", "kind": "v3_grid", "tf": "1m", "t_close": self.T15,
                             "collection_only": True}, c, NOW)
        self.assertEqual(s["reject"], "layer disabled")

    def test_max_hold_is_8_bars_of_signal_tf(self):
        for tf, mins in (("15m", "120"), ("1h", "480")):
            t = self.T15 if tf == "15m" else int(datetime(2026, 9, 28, 23, 0, tzinfo=timezone.utc).timestamp() * 1000)
            s = at.layer_signal({"layer": "rsi", "event": "support", "tf": tf, "t_close": t}, cfg(), NOW)
            self.assertEqual(s["plan_args"][s["plan_args"].index("--max-hold-minutes") + 1], mins)

    def test_tom_max_hold_is_flat_whatever_the_zone_tf(self):
        # TF5 E2: the zone name no longer scales the time exit (before: 5m -> 40, 1h -> 480, 4h -> 1920 min).
        for zone in ("15m_swing_high", "5m_swing_high", "1h_swing_low", "4h_val", "weird"):
            a = tom_alert()
            a["card_text"] = a["card_text"].replace("15m_swing_high", zone)
            s = at.tom_signal(a, {"tom_last_alert_no": 43}, cfg(), NOW)
            self.assertEqual(s["plan_args"][s["plan_args"].index("--max-hold-minutes") + 1], "120", zone)

    def test_tom_explicit_max_hold_minutes_wins_and_none_disables(self):
        c = cfg()
        c["tom"]["max_hold_minutes"] = 30
        s = at.tom_signal(tom_alert(), {"tom_last_alert_no": 43}, c, NOW)
        self.assertEqual(s["plan_args"][s["plan_args"].index("--max-hold-minutes") + 1], "30")
        c = cfg()
        c["tom"]["max_hold_minutes"] = None
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

    def test_tom_3m_zone_max_hold_is_the_flat_value(self):
        # TF5 E2: was 8 x 3m = 24 min; now the flat tom.max_hold_minutes (120) and no zone_tf field.
        a = tom_alert()
        a["card_text"] = a["card_text"].replace("15m_swing_high", "3m_swing_high")
        s = at.tom_signal(a, {"tom_last_alert_no": 43}, cfg(), NOW)
        self.assertNotIn("reject", s)
        self.assertNotIn("zone_tf", s["detail"])
        self.assertEqual(s["plan_args"][s["plan_args"].index("--max-hold-minutes") + 1], "120")

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

    def test_rsi_cross_side_by_level(self):
        # B128 M29-11 (operator 2026-10-08): side comes from the level crossed, not the direction alone. Source MLK-R1
        # (malkan_40_60.py): a bull regime cannot cross 40 downward, a bear regime cannot cross 60 upward, so a cross
        # down through 40 -> short and a cross up through 60 -> long. Every other cross (incl. unknown level) -> no side.
        def sig(level, direction):
            alert = {"layer": "rsi", "event": "cross", "direction": direction, "tf": "15m", "t_close": self.T15}
            if level is not None:
                alert["level_value"] = level
            return at.layer_signal(alert, cfg(), NOW)
        self.assertEqual(sig(40.0, "down")["side"], "short")
        self.assertEqual(sig(60.0, "up")["side"], "long")
        for level, direction in ((40.0, "up"), (60.0, "down"), (50.0, "up"), (50.0, "down"), (None, "up"), (None, "down")):
            s = sig(level, direction)
            self.assertIsNone(s["side"], (level, direction))
            self.assertIn("unmapped", s["reject"], (level, direction))

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
                                                   "exchange_flat", "spawn_manager", "OPERATOR_ALERTS",
                                                   "deribit_mark")}
        at.TOM_ALERT, at.LAYER_ALERT_DIR = d / "last_alert.json", d / "alerts"
        at.HALT, at.HALT_DAILY_LOSS, at.LOG_PATH = d / "HALT", d / "HALT_DAILY_LOSS", d / "log.jsonl"
        at.AUTO_PAUSE = d / "AUTO_PAUSE"
        at.LAYER_ALERT_DIR.mkdir()
        self.placed = []
        self.placed_accounts = []

        class P:
            def __init__(s, rc=None):
                s.rc = rc

            def poll(s):
                return s.rc

        self.P = P

        def fake_place(sig, dry_run, account=None):  # cycle() passes the routed account as a 3rd arg
            self.placed.append(sig)
            self.placed_accounts.append(account)
            return {"outcome": "entered", "plan_id": f"p{len(self.placed)}", "proc": P()}
        at.place = fake_place
        self.ledger = []
        at.record_ledger = lambda *a: self.ledger.append(a)
        self.flat = True
        at.exchange_flat = lambda acct=None: self.flat
        self.spawned = []
        at.spawn_manager = lambda pid, acct=None: (self.spawned.append((pid, acct)), P(rc=None))[1]
        at.OPERATOR_ALERTS = d / "alerts.log"
        self.mark = 83523.8                  # = tom_alert() PRICE: basis 0
        at.deribit_mark = lambda instrument="BTC-PERPETUAL": self.mark

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

    def rows_of(self, event):
        return [r for r in (json.loads(l) for l in at.LOG_PATH.read_text(encoding="utf-8").splitlines())
                if r["event"] == event]

    def test_layer_trade_log_rows_carry_bracket_source(self):
        # B118: the layer bracket (stop_pct 1.0, targets 2, size 100, ...) is NO-SOURCE; every layer row says so.
        f = at.LAYER_ALERT_DIR / "15m.jsonl"
        f.write_text("", encoding="utf-8")
        st = {}
        at.read_new_layer_alerts(st)
        f.write_text(json.dumps({"layer": "rsi", "sub": "rsi_events", "event": "support", "tf": "15m",
                                 "t_close": LayerSignalTest.T15}) + "\n", encoding="utf-8")
        at.cycle(st, cfg(), False, {}, NOW)
        row = self.rows_of("trade_attempt")[0]
        self.assertTrue(row["source"].startswith("layer:"))
        # T09-F2: rsi_events 15m now trades its tested bracket and the row says which backtest line
        self.assertEqual(row["bracket_source"], "TESTED:rsi/run_rsi_backtest.py:56-58")
        self.assertEqual(cfg()["layers"]["bracket_source"], "SAMPLING")      # the default bracket's own label is unchanged

    def test_tom_trade_row_has_no_bracket_source(self):
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW)
        self.assertNotIn("bracket_source", self.rows_of("trade_attempt")[0])

    def test_trade_attempt_logs_the_runner_target(self):
        at.TOM_ALERT.write_text(json.dumps(tom_alert(runner=82000.0)), encoding="utf-8")
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW)
        self.assertIn("--breakeven-after-first-target", self.placed[0]["plan_args"])
        row = self.rows_of("trade_attempt")[0]
        self.assertEqual(row["runner_target"], 82000.0)
        self.assertNotIn("runner_skipped", row)

    def test_trade_attempt_logs_why_it_stayed_single_target(self):
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW)
        row = self.rows_of("trade_attempt")[0]
        self.assertEqual(row["runner_skipped"], "no RUNNER_TARGET")
        self.assertNotIn("runner_target", row)

    def test_restart_does_not_replay_a_runner_alert(self):
        at.TOM_ALERT.write_text(json.dumps(tom_alert(runner=82000.0)), encoding="utf-8")
        st = {"tom_last_alert_no": 43}
        at.cycle(st, cfg(), False, {}, NOW)
        self.assertEqual(len(self.placed), 1)
        st_after_restart = json.loads(json.dumps(st))                 # auto_trader_state.json round trip
        self.assertEqual(st_after_restart["tom_last_alert_no"], 44)
        at.cycle(st_after_restart, cfg(), False, {}, NOW)
        self.assertEqual(len(self.placed), 1)                         # same alert #44 is not traded twice
        # a first start (no state file) adopts the card's alert number, runner line or not, and trades nothing
        self.assertEqual(at.parse_tom_alert(at.load_json(at.TOM_ALERT, {}))["alert_no"], 44)

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



# ---------------------------------------------------------------- TF5 (pipeline row 1.7, EXEC_PROVENANCE_AUDIT H5 1-3)
# Hand numbers (not from the code):
#   E1a short: card ENTRY 83537.3, PRICE 83523.8, mark 83543.8 -> basis +20.0 -> venue limit 83557.3.
#   E1a long:  ENTRY 80000, PRICE 80010.0, mark 80025.5 -> basis +15.5 -> venue limit 80015.5.
#   E1a negative basis: PRICE 83523.8, mark 83500.3 -> basis -23.5 -> short limit 83513.8.
#   Stop / target % are taken from the CARD levels, so they do not change with the basis: 0.2 and 0.661 (see above).
#   E3: 50/50 legs are floor10(size/2) each: 20 -> 10+10 = 20 ok; 30 -> 10+10 = 20 != 30 refused; 10 -> 0 refused;
#       30/70 at 40 -> near floor10(28) = 20, runner floor10(12) = 10, 30 != 40 refused; 30/70 at 100 -> 70+30 ok.

REPO_ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
LIVE_CFG = REPO_ROOT / "MyTradingSys" / "execution" / "auto_trader_config.json"


def staged_config_path() -> Path:
    """The staged config while TF5 is unpromoted, the live one after the promote."""
    new = LIVE_CFG.with_name(LIVE_CFG.name + ".new")
    return new if new.exists() else LIVE_CFG


class TF5VenuePriceTest(unittest.TestCase):
    def sig(self, mark, **kw):
        s = at.tom_signal(tom_alert(**kw), {"tom_last_alert_no": 0}, cfg(), NOW)
        self.assertNotIn("reject", s)
        return s, at.apply_venue_price(s, mark_fn=lambda: mark)

    def arg(self, s, flag):
        return s["plan_args"][s["plan_args"].index(flag) + 1]

    def test_card_price_is_parsed(self):
        self.assertEqual(at.parse_tom_alert(tom_alert())["price"], 83523.8)

    def test_short_limit_moves_by_the_basis(self):
        s, why = self.sig(83543.8)
        self.assertIsNone(why)
        self.assertEqual(float(self.arg(s, "--price")), 83557.3)
        self.assertAlmostEqual(float(self.arg(s, "--stop")), 0.2, places=3)      # % from the card levels
        self.assertEqual(self.arg(s, "--targets"), "0.661")
        self.assertEqual(s["log"]["basis"], 20.0)
        self.assertEqual((s["log"]["card_entry"], s["log"]["venue_entry"]), (83537.3, 83557.3))

    def test_long_limit_moves_by_the_basis(self):
        s = at.tom_signal(tom_alert(setup="tf_long", entry=80000, stop=79600, target=81200).copy(),
                          {"tom_last_alert_no": 0}, cfg(), NOW)
        s["detail"]["price"] = 80010.0
        self.assertIsNone(at.apply_venue_price(s, mark_fn=lambda: 80025.5))
        self.assertEqual(float(self.arg(s, "--price")), 80015.5)

    def test_negative_basis_moves_the_limit_down(self):
        s, why = self.sig(83500.3)
        self.assertIsNone(why)
        self.assertEqual(float(self.arg(s, "--price")), 83513.8)

    def test_unreadable_or_invalid_mark_refuses_the_entry(self):
        def boom(exc):
            def f():
                raise exc
            return f
        for fn in (boom(OSError("timeout")), boom(KeyError("mark_price")), boom(ValueError("non-JSON")),
                   boom(RuntimeError("deribit error")), lambda: float("nan"), lambda: 0, lambda: -5.0,
                   lambda: None, lambda: "junk", lambda: float("inf")):
            s = at.tom_signal(tom_alert(), {"tom_last_alert_no": 0}, cfg(), NOW)
            before = list(s["plan_args"])
            why = at.apply_venue_price(s, mark_fn=fn)
            self.assertTrue(why and why.startswith("deribit mark"), why)
            self.assertEqual(s["plan_args"], before)                         # price left untouched

    def test_card_without_price_refuses_the_entry(self):
        a = tom_alert()
        a["card_text"] = a["card_text"].replace("PRICE:   83523.8\n", "")
        s = at.tom_signal(a, {"tom_last_alert_no": 0}, cfg(), NOW)
        self.assertIsNone(s["detail"]["price"])
        self.assertEqual(at.apply_venue_price(s, mark_fn=lambda: 83543.8), "no card PRICE: venue basis unknown")

    def test_mark_reader_uses_only_the_public_ticker(self):
        # A non-trade balance move (funding, transfer) or a dead auth path cannot change or block the price read:
        # the reader never authenticates and never reads the account.
        import deribit_orders as do
        with mock.patch.object(do, "get_ticker", return_value={"mark_price": 84000.5}) as tk, \
                mock.patch.object(do, "authenticate", side_effect=AssertionError("auth")), \
                mock.patch.object(do, "get_account_summary", side_effect=AssertionError("account")):
            self.assertEqual(at.deribit_mark(), 84000.5)
        tk.assert_called_once_with("BTC-PERPETUAL")

    def test_layer_signals_are_not_venue_priced(self):
        s = at.layer_signal({"layer": "rsi", "event": "support", "tf": "15m", "t_close": LayerSignalTest.T15},
                            cfg(), NOW)
        self.assertNotIn("venue_price", s)
        self.assertNotIn("executor_args", s)


class TF5CycleTest(unittest.TestCase):
    """Live path through cycle(): fail closed, no retry after a refusal, restart/reset state."""
    setUp, tearDown, rows_of, events = CycleTest.setUp, CycleTest.tearDown, CycleTest.rows_of, CycleTest.events

    def test_mark_api_error_places_nothing_and_logs_the_reason(self):
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")

        def down(instrument="BTC-PERPETUAL"):
            raise OSError("connection reset")
        at.deribit_mark = down
        st = {"tom_last_alert_no": 43}
        active = at.cycle(st, cfg(), False, {}, NOW)
        self.assertEqual((self.placed, active), ([], {}))
        row = self.rows_of("signal_rejected")[0]
        self.assertIn("deribit mark unreadable: OSError", row["reason"])
        # the alert is consumed: once the ticker is back, the same alert is NOT traded late
        at.deribit_mark = lambda instrument="BTC-PERPETUAL": 83543.8
        at.cycle(st, cfg(), False, {}, NOW)
        self.assertEqual(self.placed, [])

    def test_entered_trade_logs_the_basis_and_venue_price(self):
        self.mark = 83543.8
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW)
        a = self.placed[0]["plan_args"]
        self.assertEqual(float(a[a.index("--price") + 1]), 83557.3)
        row = self.rows_of("trade_attempt")[0]
        self.assertEqual((row["basis"], row["venue_entry"], row["deribit_mark"]), (20.0, 83557.3, 83543.8))

    def test_busy_slot_does_not_read_the_mark(self):
        calls = []
        at.deribit_mark = lambda instrument="BTC-PERPETUAL": calls.append(1) or 83523.8
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")
        busy = {"proc": self.P(rc=None), "plan_id": "busy", "source": "tom"}
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, busy, NOW)
        self.assertEqual((calls, self.placed), ([], []))

    def test_halt_does_not_read_the_mark(self):
        calls = []
        at.deribit_mark = lambda instrument="BTC-PERPETUAL": calls.append(1) or 83523.8
        at.HALT.write_text("x", encoding="utf-8")
        at.TOM_ALERT.write_text(json.dumps(tom_alert()), encoding="utf-8")
        at.cycle({"tom_last_alert_no": 43}, cfg(), False, {}, NOW)
        self.assertEqual((calls, self.placed), ([], []))

    def test_restart_loads_tf5_config_and_does_not_replay(self):
        # main() = a restart: DEFAULT_CONFIG merged with the (staged) config file, state from disk.
        d = Path(self.tmp.name)
        saved = (at.STATE_PATH, at.recover_slots)
        at.STATE_PATH = d / "state.json"
        at.recover_slots = lambda: ({}, {})
        self.addCleanup(lambda: (setattr(at, "STATE_PATH", saved[0]), setattr(at, "recover_slots", saved[1])))
        at.STATE_PATH.write_text(json.dumps({"tom_last_alert_no": 43}), encoding="utf-8")
        alert = tom_alert(time=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), runner=82000.0)
        at.TOM_ALERT.write_text(json.dumps(alert), encoding="utf-8")
        # this test is about config loading and no-replay, not the B146 fee gate (D09, covered in test_b146_fee_to_stop):
        # its fixture alert has a 0.2 % stop, so run it on the staged config without the gate
        raw = json.loads(staged_config_path().read_text(encoding="utf-8"))
        raw["tom"].pop("max_fee_to_stop", None)
        cfg_path = d / "cfg_no_gate.json"
        cfg_path.write_text(json.dumps(raw), encoding="utf-8")
        self.assertEqual(at.main(["--once", "--config", str(cfg_path)]), 0)
        self.assertEqual(len(self.placed), 1)
        a = self.placed[0]["plan_args"]
        self.assertEqual(a[a.index("--size") + 1], "20")                         # E3 CFG 10 -> 20
        self.assertEqual(a[a.index("--targets") + 1], "50@0.661,50@1.84")       # so the 50/50 split now forms
        self.assertEqual(a[a.index("--max-hold-minutes") + 1], "120")           # E2 flat
        self.assertEqual(self.placed[0]["executor_args"], ["--max-entry-seconds", "600"])   # E1b
        self.assertEqual(json.loads(at.STATE_PATH.read_text(encoding="utf-8"))["tom_last_alert_no"], 44)
        at.main(["--once", "--config", str(cfg_path)])                          # second restart: same alert
        self.assertEqual(len(self.placed), 1)

    def test_reset_state_never_trades_the_alert_already_on_disk(self):
        # state file deleted (reset): first start marks the current alert as seen and trades nothing.
        d = Path(self.tmp.name)
        saved = (at.STATE_PATH, at.recover_slots)
        at.STATE_PATH = d / "missing_state.json"
        at.recover_slots = lambda: ({}, {})
        self.addCleanup(lambda: (setattr(at, "STATE_PATH", saved[0]), setattr(at, "recover_slots", saved[1])))
        alert = tom_alert(time=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        at.TOM_ALERT.write_text(json.dumps(alert), encoding="utf-8")
        at.main(["--once", "--config", str(staged_config_path())])
        self.assertEqual(self.placed, [])


class TF5EntryWaitTest(unittest.TestCase):
    def test_wait_is_a_config_key_passed_to_the_executor(self):
        s = at.tom_signal(tom_alert(), {"tom_last_alert_no": 0}, cfg(), NOW)
        self.assertEqual(s["executor_args"], ["--max-entry-seconds", "600"])
        c = cfg()
        c["tom"]["max_entry_seconds"] = 240
        s = at.tom_signal(tom_alert(), {"tom_last_alert_no": 0}, c, NOW)
        self.assertEqual(s["executor_args"], ["--max-entry-seconds", "240"])

    def test_bad_wait_value_refuses_the_entry(self):
        for bad in (0, -1, "600", 1.5, True, None):
            c = cfg()
            c["tom"]["max_entry_seconds"] = bad
            s = at.tom_signal(tom_alert(), {"tom_last_alert_no": 0}, c, NOW)
            self.assertIn("max_entry_seconds", s.get("reject", ""), bad)
            self.assertNotIn("plan_args", s)

    def test_place_passes_the_wait_to_executor_go_only(self):
        cmds = []

        def fake_run(cmd, timeout=900, account=None):
            cmds.append(cmd)
            if cmd[1].endswith("new_plan.py"):
                return 0, "SAVED S-lim-test"
            return 0, "OK: no_fill"
        saved = at.run
        at.run = fake_run
        self.addCleanup(lambda: setattr(at, "run", saved))
        s = at.tom_signal(tom_alert(), {"tom_last_alert_no": 0}, cfg(), NOW)
        self.assertEqual(at.place(s, dry_run=False)["outcome"], "no_fill")
        go = [c for c in cmds if "--go" in c][0]
        self.assertEqual(go[go.index("--max-entry-seconds") + 1], "600")
        self.assertNotIn("--max-entry-seconds", cmds[0])                       # not a new_plan argument


class TF5SizeAndSplitTest(unittest.TestCase):
    P = {"side": "short", "entry": 83537.3, "target": 82985.43, "runner_target": 82000.0}

    def split(self, size, pct=50):
        return at.runner_split(self.P, {"size_usd": size, "runner_leg_pct": pct})

    def test_size_20_splits_50_50(self):
        self.assertEqual(self.split(20), ("50@0.661,50@1.84", None))

    def test_legs_that_do_not_sum_to_the_size_are_refused(self):
        legs, why = self.split(30)
        self.assertIsNone(legs)
        self.assertEqual(why, "legs 10+10 do not sum to size 30")
        legs, why = self.split(40, pct=30)
        self.assertEqual((legs, why), (None, "legs 20+10 do not sum to size 40"))
        self.assertEqual(self.split(100, pct=30)[0], "70@0.661,30@1.84")

    def test_size_10_still_too_small(self):
        self.assertIn("too small", self.split(10)[1])

    def test_staged_config_values(self):
        c = json.loads(staged_config_path().read_text(encoding="utf-8"))["tom"]
        self.assertEqual((c["size_usd"], c["max_hold_minutes"], c["max_entry_seconds"]), (20, 120, 600))

    def test_no_zone_tf_scaling_left_in_the_tom_path(self):
        self.assertNotIn("max_hold_bars", at.DEFAULT_CONFIG["tom"])
        self.assertNotIn("zone_tf", at.parse_tom_alert(tom_alert()))


class LayerExitTest(unittest.TestCase):
    """T09-F2: per-layer exit table (rsi tested bracket, cc event stop), SAMPLING default, fail closed on bad entries."""
    T15 = LayerSignalTest.T15
    T1H = int(datetime(2026, 9, 28, 23, 0, tzinfo=timezone.utc).timestamp() * 1000)   # opens 23:00, closes 00:00 = NOW
    RSI_SRC = "TESTED:rsi/run_rsi_backtest.py:56-58"
    CC_SRC = "TESTED:cryptocred/run_cc_setups.py:170"

    def rsi(self, c=None, tf="15m"):
        return at.layer_signal({"layer": "rsi", "sub": "rsi_events", "event": "support", "tf": tf,
                                "t_close": self.T15 if tf == "15m" else self.T1H}, c or cfg(), NOW)

    def cc(self, side="long", entry=100.0, stop=98.5, c=None, sub="sr_flip", **extra):
        a = {"layer": "cryptocred", "sub": sub, "event": f"{sub}_{side}", "side": side, "tf": "1h",
             "t_close": self.T1H, "entry_price": entry, "stop": stop}
        a.update(extra)
        for k in [k for k, v in a.items() if v is None]:
            del a[k]
        return at.layer_signal(a, c or cfg(), NOW)

    @staticmethod
    def arg(s, flag):
        return s["plan_args"][s["plan_args"].index(flag) + 1]

    def test_layer_exit_per_layer(self):
        # rsi_events 15m: the RSI backtest bracket 1% / 2% / 100 bars (run_rsi_backtest.py:56-58), 100 x 15 min
        s = self.rsi()
        self.assertNotIn("reject", s)
        self.assertEqual((self.arg(s, "--stop"), self.arg(s, "--targets"), self.arg(s, "--max-hold-minutes")),
                         ("1", "2", "1500"))
        self.assertEqual(s["log"], {"bracket_source": self.RSI_SRC})
        # cc: the event stop (1.5% below entry 100), tested hold 1440 min; target stays SAMPLING and says so
        s = self.cc()
        self.assertNotIn("reject", s)
        self.assertEqual((self.arg(s, "--stop"), self.arg(s, "--targets"), self.arg(s, "--max-hold-minutes")),
                         ("1.5", "2", "1440"))
        self.assertEqual(s["log"], {"bracket_source": self.CC_SRC, "sampling_fields": ["targets"]})
        # short: stop above entry
        self.assertEqual(self.arg(self.cc(side="short", entry=200.0, stop=203.0), "--stop"), "1.5")
        # an unknown layer / an rsi tf with no tested exit keeps the labelled SAMPLING bracket, 8 bars of its tf
        t3 = int(datetime(2026, 9, 28, 23, 54, tzinfo=timezone.utc).timestamp() * 1000)
        for s in (at.layer_signal({"layer": "brand_new_layer", "kind": "x", "side": "short", "tf": "1h",
                                   "t_close": self.T1H}, cfg(), NOW),
                  at.layer_signal({"layer": "rsi", "sub": "rsi_events", "event": "support", "tf": "3m",
                                   "t_close": t3}, cfg(), NOW)):
            self.assertNotIn("reject", s)
            self.assertEqual(s["log"], {"bracket_source": "SAMPLING"})
            self.assertEqual(self.arg(s, "--stop"), "1.0")
            self.assertEqual(self.arg(s, "--targets"), "2")
        self.assertEqual(self.arg(self.rsi(tf="1h"), "--max-hold-minutes"), "6000")

    def test_event_stop_missing_zero_or_wrong_side_rejects(self):
        for kw in ({"stop": None}, {"stop": 0}, {"stop": float("nan")}, {"stop": 100.0}, {"stop": 101.0},
                   {"entry": None}, {"entry": 0}, {"stop": True}):
            s = self.cc(**kw)
            self.assertIn("bad layers.exits", s.get("reject", ""), kw)
            self.assertNotIn("plan_args", s)
        s = self.cc(side="short", entry=100.0, stop=99.0)            # short stop below entry
        self.assertIn("wrong side", s["reject"])

    def test_bad_exit_table_entry_rejects_and_untouched_layers_still_trade(self):
        bad = [{"stop_pct": 1.0},                                                     # no TESTED source
               {"stop_pct": 1.0, "source": "OURS"},
               {"stop_pct": 0, "source": self.RSI_SRC}, {"stop_pct": 100, "source": self.RSI_SRC},
               {"stop_pct": -1, "source": self.RSI_SRC}, {"stop_pct": "1", "source": self.RSI_SRC},
               {"stop_pct": 1.0, "stop": "event", "source": self.RSI_SRC},            # both stops
               {"source": self.RSI_SRC},                                              # no stop
               {"stop_pct": 1.0, "targets": "abc", "source": self.RSI_SRC},
               {"stop_pct": 1.0, "targets": "0", "source": self.RSI_SRC},
               {"stop_pct": 1.0, "max_hold_bars": 0, "source": self.RSI_SRC},
               {"stop_pct": 1.0, "max_hold_bars": 5, "max_hold_minutes": 5, "source": self.RSI_SRC},
               {"stop_pct": 1.0, "wat": 1, "source": self.RSI_SRC}, "junk", None]
        for entry in bad:
            c = cfg()
            c["layers"]["exits"] = {"layer:rsi:rsi_events:15m": entry}
            s = self.rsi(c)
            self.assertIn("bad layers.exits", s.get("reject", ""), entry)
            self.assertNotIn("plan_args", s)
            self.assertNotIn("reject", self.rsi(c, tf="1h"))                      # other prefixes unaffected
        c = cfg()
        c["layers"]["exits"] = ["not", "an", "object"]
        self.assertIn("bad layers.exits", self.rsi(c)["reject"])

    def test_no_exit_table_is_the_old_sampling_bracket(self):
        c = cfg()
        del c["layers"]["exits"]
        s = self.rsi(c)
        self.assertEqual((self.arg(s, "--stop"), self.arg(s, "--max-hold-minutes"), s["log"]),
                         ("1.0", "120", {"bracket_source": "SAMPLING"}))

    def test_config_reload_gives_same_plan_args(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "auto_trader_config.json"
            f.write_text(json.dumps({"layers": {"size_usd": 20, "max_loss_usd": 2, "max_age_bars": 2.0}}), encoding="utf-8")
            plans = []
            for _ in range(2):                               # a restart = a fresh load_config + fresh signal
                c = at.load_config(f)
                c["pre_pipeline_sources"] = cfg()["pre_pipeline_sources"]
                plans += [self.rsi(c)["plan_args"], self.cc(c=c)["plan_args"]]
        self.assertEqual(plans[0], plans[2])
        self.assertEqual(plans[1], plans[3])
        self.assertEqual(self.arg({"plan_args": plans[0]}, "--max-hold-minutes"), "1500")   # table survived the file overlay

    def test_layer_signal_keeps_no_state_and_does_not_mutate_config(self):
        # non-trade balance moves and API errors live in the cycle/executor path; layer_signal does no I/O and holds no state
        c = cfg()
        before = json.dumps(c, sort_keys=True)
        a = self.cc()
        with mock.patch("builtins.open", side_effect=AssertionError("layer_signal must not do I/O")), \
                mock.patch.object(at.subprocess, "run", side_effect=AssertionError("layer_signal must not call out")):
            first = at.layer_signal(a["detail"], c, NOW)
            second = at.layer_signal(a["detail"], c, NOW)
        self.assertEqual(first, second)
        self.assertEqual(json.dumps(c, sort_keys=True), before)

    def test_every_layer_trade_row_carries_a_known_bracket_source(self):
        for s in (self.rsi(), self.cc(), self.rsi(tf="1h"),
                  at.layer_signal({"layer": "brand_new_layer", "kind": "x", "side": "long", "tf": "1h",
                                   "t_close": self.T1H}, cfg(), NOW)):
            src = s["log"]["bracket_source"]
            self.assertTrue(src == "SAMPLING" or src.startswith("TESTED:") and ":" in src[len("TESTED:"):], src)


if __name__ == "__main__":
    unittest.main(verbosity=1)
