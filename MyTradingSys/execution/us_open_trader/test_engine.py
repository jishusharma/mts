"""test_engine.py - pure engine rules, hand-computed expectations (DESIGN section 2). No network, no clock."""
import calendar
import copy
import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine  # noqa: E402

# Epoch ms computed independently of engine.py (calendar.timegm).
ARM = calendar.timegm((2026, 11, 13, 13, 35, 0)) * 1000   # arm_utc 13:35
FLAT = calendar.timegm((2026, 11, 13, 16, 30, 0)) * 1000  # flat_utc 16:30
MIN = 60000
FEE_RT = 2 * 0.0005  # round-trip fee fraction (fee_per_side 0.0005)

PLAN = {
    "day": "2026-11-13", "frozen_utc": "2026-11-13T13:10Z", "ref_feed": "binance_spot_BTCUSDT",
    "instrument": "BTC-PERPETUAL", "arm_utc": "13:35", "flat_utc": "16:30", "max_entries": 3,
    "amount_usd": 5000, "leverage": 50, "be_at_r": 1.0, "fee_per_side": 0.0005,
    "orders": [
        {"id": "A", "side": "buy", "kind": "breakout", "trigger": 69620, "stop_dist": 250, "target_dist": 360,
         "level": "Europe high 69,571", "confluence": ["live_aid:EU_HIGH"], "arm_after": None},
        {"id": "B", "side": "sell", "kind": "breakout", "trigger": 68490, "stop_dist": 250, "target_dist": 370,
         "level": "Europe low 68,516", "confluence": ["live_aid:EU_LOW"], "arm_after": None},
        {"id": "C", "side": "sell", "kind": "fade", "trigger": 69980, "stop_dist": 250, "target_dist": 500,
         "level": "cluster 70,000", "confluence": ["analyst:Michael_70000"], "arm_after": "A"},
        {"id": "D", "side": "buy", "kind": "fade", "trigger": 68120, "stop_dist": 250, "target_dist": 500,
         "level": "200w 68,000-68,100", "confluence": ["analyst:Krown_68100"], "arm_after": "B"},
    ],
}


def plan(**kw):
    p = copy.deepcopy(PLAN)
    p.update(kw)
    return p


def bar(i, o, h, l, c=None):
    return {"t": ARM + i * MIN, "o": o, "h": h, "l": l, "c": o if c is None else c}


def run(bars, p=None):
    return engine.replay(p or PLAN, bars)


def types(res):
    return [(e["type"], e["order_id"], e["reason"]) for e in res["events"]]


# A quiet first bar that does not touch anything (A 69620 / B 68490 / C 69980 / D 68120).
Q = bar(0, 69000, 69100, 68900)


class TestEngine(unittest.TestCase):
    def assertR(self, trade, gross, net):
        self.assertAlmostEqual(trade["r_gross"], gross, places=9)
        self.assertAlmostEqual(trade["r_net"], net, places=9)

    def test_bars_before_arm_ignored(self):
        early = {"t": ARM - MIN, "o": 69000, "h": 69700, "l": 68400, "c": 69000}  # would trigger A and B
        res = run([early, Q])
        self.assertEqual(res["events"], [])
        self.assertEqual(res["trades"], [])
        self.assertTrue(res["state"]["started"])  # Q was the first armed bar, early was not

    def test_void_at_arm_breakout_buy(self):
        # first armed bar opens 69700 >= A trigger 69620 -> A void. Nothing else crossed.
        res = run([bar(0, 69700, 69710, 69690)])
        self.assertEqual(types(res), [("void", "A", "crossed_at_arm")])
        # later bar touching 69620 cannot fill A
        res = run([bar(0, 69700, 69710, 69690), bar(1, 69500, 69650, 69400)])
        self.assertEqual(res["trades"], [])
        self.assertEqual(res["state"]["status"]["A"], "void")

    def test_void_at_arm_breakout_sell_and_fades(self):
        # open 68400: B (sell breakout, 68490) crossed (<=). D (buy fade 68120) not (68400 > 68120).
        res = run([bar(0, 68400, 68410, 68390)])
        self.assertEqual(types(res), [("void", "B", "crossed_at_arm")])
        # open 70100: A (69620) crossed up, C (sell fade 69980) crossed up
        res = run([bar(0, 70100, 70110, 70090)])
        self.assertEqual(sorted(types(res)), [("void", "A", "crossed_at_arm"), ("void", "C", "crossed_at_arm")])
        # open 68000: B crossed down, D (buy fade 68120) crossed down
        res = run([bar(0, 68000, 68010, 67990)])
        self.assertEqual(sorted(types(res)), [("void", "B", "crossed_at_arm"), ("void", "D", "crossed_at_arm")])

    def test_void_releases_arm_after(self):
        # A void at arm -> fade C armed at once; bar1 high 69990 >= 69980 -> C enters at 69980
        res = run([bar(0, 69700, 69710, 69690), bar(1, 69700, 69990, 69690)])
        self.assertEqual(types(res)[-1], ("enter", "C", "fade"))
        self.assertEqual(res["state"]["position"]["entry"], 69980)

    def test_breakout_buy_triggers_at_trigger(self):
        res = run([Q, bar(1, 69500, 69625, 69450)])  # h 69625 >= 69620
        ev = res["events"][-1]
        self.assertEqual((ev["type"], ev["order_id"], ev["price"], ev["t"]), ("enter", "A", 69620, ARM + MIN))
        pos = res["state"]["position"]
        self.assertEqual((pos["stop"], pos["target"]), (69370, 69980))  # 69620-250, 69620+360
        # exactly touching counts (AT/ABOVE)
        res = run([Q, bar(1, 69500, 69620, 69450)])
        self.assertEqual(res["events"][-1]["type"], "enter")
        # one tick short: no trigger
        res = run([Q, bar(1, 69500, 69619, 69450)])
        self.assertEqual(res["events"], [])

    def test_breakout_sell_triggers_at_trigger(self):
        res = run([Q, bar(1, 68600, 68650, 68485)])  # l 68485 <= 68490
        ev = res["events"][-1]
        self.assertEqual((ev["type"], ev["order_id"], ev["price"]), ("enter", "B", 68490))
        pos = res["state"]["position"]
        self.assertEqual((pos["stop"], pos["target"]), (68740, 68120))  # +250, -370
        self.assertEqual(run([Q, bar(1, 68600, 68650, 68491)])["events"], [])

    def test_fade_sell_and_buy_trigger(self):
        # A stops first (so C armed): bar1 enter A, bar2 stop at 69370, bar3 high 69985 -> C sell fade at 69980
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69500, 69600, 69360), bar(3, 69800, 69985, 69700)])
        self.assertEqual(types(res), [("enter", "A", "breakout"), ("exit", "A", "stop"), ("enter", "C", "fade")])
        pos = res["state"]["position"]
        self.assertEqual((pos["entry"], pos["stop"], pos["target"]), (69980, 70230, 69480))
        # B stops first, then D buy fade: bar3 low 68110 <= 68120
        res = run([Q, bar(1, 68600, 68650, 68485), bar(2, 68600, 68745, 68500), bar(3, 68300, 68400, 68110)])
        self.assertEqual(types(res), [("enter", "B", "breakout"), ("exit", "B", "stop"), ("enter", "D", "fade")])
        pos = res["state"]["position"]
        self.assertEqual((pos["entry"], pos["stop"], pos["target"]), (68120, 67870, 68620))

    def test_fade_not_armed_until_arm_after_released(self):
        # bar1 touches A (69620) and C (69980) but C is gated by A: A enters, C does not
        # (open 69900 is nearer C 69980 than A 69620, so an ungated C would win the tie)
        res = run([Q, bar(1, 69900, 69990, 69490)])
        self.assertEqual(types(res), [("enter", "A", "breakout")])
        self.assertEqual(res["state"]["status"]["C"], "pending")
        # D gated by B the same way: bar touches B (68490) and D (68120)
        res = run([Q, bar(1, 68200, 68650, 68100)])  # open nearer D 68120 than B 68490
        self.assertEqual(types(res), [("enter", "B", "breakout")])
        self.assertEqual(res["state"]["status"]["D"], "pending")

    def test_two_triggers_in_one_bar_nearer_open_wins(self):
        # open 69000: A dist 620, B dist 510 -> B wins. Entry-bar stop: h 69700 >= 68740 -> stop at 68740
        res = run([Q, bar(1, 69000, 69700, 68400)])
        self.assertEqual(types(res), [("enter", "B", "breakout"), ("exit", "B", "stop")])
        # open 69600: A dist 20, B dist 1110 -> A wins; l 68400 <= 69370 -> stop at 69370
        res = run([Q, bar(1, 69600, 69700, 68400)])
        self.assertEqual(types(res), [("enter", "A", "breakout"), ("exit", "A", "stop")])
        # both entries are single per order: no second entry in that same bar
        self.assertEqual(len(res["trades"]), 1)

    def test_entry_bar_stop_exits_in_same_bar_and_r(self):
        res = run([Q, bar(1, 69600, 69700, 69300)])  # A enters 69620, l 69300 <= 69370
        tr = res["trades"][0]
        self.assertEqual((tr["entry_t"], tr["exit_t"], tr["entry"], tr["exit"], tr["exit_reason"]),
                         (ARM + MIN, ARM + MIN, 69620, 69370, "stop"))
        # r_gross = (69370-69620)/250 = -1 ; r_net = -1 - 0.001*69620/250 = -1.27848
        self.assertR(tr, -1.0, -1.0 - FEE_RT * 69620 / 250)
        self.assertAlmostEqual(tr["r_net"], -1.27848, places=9)
        self.assertIsNone(res["state"]["position"])

    def test_target_not_counted_on_entry_bar(self):
        # entry bar reaches 70000 (> target 69980) and l 69500 > stop: stays open, no BE move either
        res = run([Q, bar(1, 69500, 70000, 69500)])
        self.assertEqual(res["trades"], [])
        self.assertFalse(res["state"]["position"]["moved"])
        self.assertEqual(types(res), [("enter", "A", "breakout")])
        # next bar touches target -> exit target
        res = run([Q, bar(1, 69500, 70000, 69500), bar(2, 69900, 69985, 69800)])
        self.assertEqual(res["trades"][0]["exit_reason"], "target")

    def test_target_exit_and_r_buy(self):
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69800, 69985, 69800)])
        tr = res["trades"][0]
        self.assertEqual((tr["exit"], tr["exit_reason"]), (69980, "target"))
        # r_gross 360/250 = 1.44 ; r_net = 1.44 - 69.62/250 = 1.44 - 0.27848 = 1.16152
        self.assertR(tr, 1.44, 1.16152)

    def test_target_exit_and_r_sell(self):
        res = run([Q, bar(1, 68600, 68650, 68485), bar(2, 68300, 68400, 68100)])
        tr = res["trades"][0]
        self.assertEqual((tr["order_id"], tr["exit"], tr["exit_reason"]), ("B", 68120, "target"))
        # r_gross 370/250 = 1.48 ; r_net = 1.48 - 68.49/250 = 1.48 - 0.27396 = 1.20604
        self.assertR(tr, 1.48, 1.20604)

    def test_stop_r_sell(self):
        res = run([Q, bar(1, 68600, 68650, 68485), bar(2, 68600, 68745, 68500)])
        tr = res["trades"][0]
        self.assertEqual((tr["exit"], tr["exit_reason"]), (68740, "stop"))
        self.assertR(tr, -1.0, -1.0 - 68.49 / 250)  # -1.27396

    def test_stop_and_target_same_bar_is_stop(self):
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69600, 69990, 69360)])
        tr = res["trades"][0]
        self.assertEqual((tr["exit"], tr["exit_reason"]), (69370, "stop"))

    def test_stop_and_target_same_bar_sell(self):
        res = run([Q, bar(1, 68600, 68650, 68485), bar(2, 68500, 68745, 68100)])
        self.assertEqual((res["trades"][0]["exit"], res["trades"][0]["exit_reason"]), (68740, "stop"))

    def test_break_even_move_effective_next_bar(self):
        # bar1 enter A 69620. bar2 h 69880 (fav 260 >= 1R=250), l 69500 (< new stop 69620 but not yet effective)
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69700, 69880, 69500)])
        self.assertEqual(types(res), [("enter", "A", "breakout"), ("move_stop", "A", "be")])
        self.assertEqual(res["trades"], [])
        pos = res["state"]["position"]
        self.assertEqual((pos["stop"], pos["moved"]), (69620, True))
        mv = res["events"][-1]
        self.assertEqual((mv["t"], mv["price"]), (ARM + 2 * MIN, 69620))
        # bar3 low 69610 <= 69620 -> be_stop at 69620, r_gross 0, r_net = -69.62/250 = -0.27848
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69700, 69880, 69500), bar(3, 69700, 69750, 69610)])
        tr = res["trades"][0]
        self.assertEqual((tr["exit"], tr["exit_reason"], tr["stop_moved"]), (69620, "be_stop", True))
        self.assertR(tr, 0.0, -0.27848)

    def test_break_even_threshold_exact_and_short_side(self):
        # fav exactly 250 moves; 249 does not (A)
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69700, 69870, 69500)])  # 69870-69620 = 250
        self.assertTrue(res["state"]["position"]["moved"])
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69700, 69869, 69500)])  # 249
        self.assertFalse(res["state"]["position"]["moved"])
        # sell B entry 68490: l 68240 -> fav 250 -> stop to 68490; next bar h 68495 -> be_stop at 68490
        res = run([Q, bar(1, 68600, 68650, 68485), bar(2, 68400, 68480, 68240), bar(3, 68300, 68495, 68250)])
        tr = res["trades"][0]
        self.assertEqual((tr["exit"], tr["exit_reason"]), (68490, "be_stop"))
        self.assertR(tr, 0.0, -68.49 / 250)

    def test_time_exit_at_flat_open(self):
        mid = {"t": FLAT - MIN, "o": 69700, "h": 69800, "l": 69650, "c": 69700}
        flat_bar = {"t": FLAT, "o": 69700, "h": 69900, "l": 69000, "c": 69500}
        res = run([Q, bar(1, 69500, 69625, 69450), mid, flat_bar])
        tr = res["trades"][0]
        self.assertEqual((tr["exit_t"], tr["exit"], tr["exit_reason"]), (FLAT, 69700, "time"))
        # r_gross = 80/250 = 0.32 ; r_net = 0.32 - 0.27848 = 0.04152
        self.assertR(tr, 0.32, 0.04152)
        cancels = sorted((e["order_id"], e["reason"]) for e in res["events"] if e["type"] == "cancel")
        self.assertEqual(cancels, [("B", "flat_time"), ("C", "flat_time"), ("D", "flat_time")])
        self.assertTrue(res["state"]["done"])
        # position state after: nothing more happens
        st, ev = engine.step(res["state"], {"t": FLAT + MIN, "o": 60000, "h": 90000, "l": 50000, "c": 70000})
        self.assertEqual(ev, [])

    def test_flat_bar_with_no_position_cancels_everything(self):
        res = run([Q, {"t": FLAT, "o": 69000, "h": 70500, "l": 68000, "c": 69000}])
        self.assertEqual(res["trades"], [])  # flat bar never triggers an entry
        self.assertEqual({e["reason"] for e in res["events"]}, {"flat_time"})
        self.assertEqual(len(res["events"]), 4)
        self.assertTrue(res["state"]["done"])

    def test_flat_wins_over_stop_on_flat_bar(self):
        # first bar with t >= flat: exit at open even though its range hits the stop
        flat_bar = {"t": FLAT, "o": 69500, "h": 69600, "l": 69000, "c": 69100}
        res = run([Q, bar(1, 69500, 69625, 69450), flat_bar])
        tr = res["trades"][0]
        self.assertEqual((tr["exit"], tr["exit_reason"]), (69500, "time"))

    def test_target_of_breakout_cancels_other_breakouts(self):
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69800, 69985, 69800)])
        self.assertEqual(res["state"]["status"]["B"], "cancelled")
        self.assertIn(("cancel", "B", "breakout_target_hit"), types(res))
        # D arm_after B cancelled -> armed: low 68110 later enters D
        res2 = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69800, 69985, 69800), bar(3, 68300, 68400, 68110)])
        self.assertEqual(types(res2)[-1], ("enter", "D", "fade"))
        # a later bar touching B's trigger does not fill B
        self.assertEqual(res["state"]["status"]["B"], "cancelled")

    def test_stop_leaves_opposite_breakout_armed(self):
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69500, 69600, 69360), bar(3, 68600, 68700, 68485)])
        self.assertEqual(types(res), [("enter", "A", "breakout"), ("exit", "A", "stop"), ("enter", "B", "breakout")])
        self.assertEqual(res["state"]["entries"], 2)

    def test_fade_target_does_not_cancel_breakouts(self):
        # A stops, C enters (69980), C target 69480 hit next bar; B untouched and still pending
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69500, 69600, 69360), bar(3, 69800, 69985, 69700),
                   bar(4, 69600, 69700, 69470)])
        tr = res["trades"][1]
        self.assertEqual((tr["order_id"], tr["exit"], tr["exit_reason"]), ("C", 69480, "target"))
        # r_gross = 500/250 = 2 ; r_net = 2 - 0.001*69980/250 = 2 - 0.27992 = 1.72008
        self.assertR(tr, 2.0, 1.72008)
        self.assertEqual(res["state"]["status"]["B"], "pending")

    def test_each_order_fills_once(self):
        # A fills, stops, then price re-crosses 69620: A must not refill
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69500, 69600, 69360), bar(3, 69500, 69700, 69450)])
        self.assertEqual([t[1] for t in types(res) if t[0] == "enter"], ["A"])

    def test_no_second_entry_in_the_exit_bar(self):
        # A open; bar2 stops A (l 69360). Same bar has h 69990 that would touch C (armed by A closing): no entry
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69600, 69990, 69360)])
        self.assertEqual(types(res), [("enter", "A", "breakout"), ("exit", "A", "stop")])

    def test_max_entries(self):
        p = plan(max_entries=1)
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69500, 69600, 69360), bar(3, 68600, 68700, 68100)], p)
        self.assertEqual(len(res["trades"]), 1)
        self.assertEqual(res["state"]["entries"], 1)
        reasons = sorted((e["order_id"], e["reason"]) for e in res["events"] if e["type"] == "cancel")
        self.assertEqual(reasons, [("B", "max_entries"), ("C", "max_entries"), ("D", "max_entries")])
        # max_entries 2: A stop, B enters (2nd), B stop -> then D/C could not enter (cap reached)
        p = plan(max_entries=2)
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69500, 69600, 69360), bar(3, 68600, 68700, 68485),
                   bar(4, 68600, 68745, 68500), bar(5, 68300, 68400, 68100)], p)
        self.assertEqual([t["order_id"] for t in res["trades"]], ["A", "B"])
        self.assertEqual(res["state"]["status"]["D"], "cancelled")

    def test_three_entries_allowed_by_default(self):
        res = run([Q, bar(1, 69500, 69625, 69450), bar(2, 69500, 69600, 69360),  # A stop
                   bar(3, 68600, 68700, 68485), bar(4, 68600, 68745, 68500),     # B enter + stop
                   bar(5, 68300, 68400, 68110)])                                 # D (armed after B closed) enters
        self.assertEqual([t[1] for t in types(res) if t[0] == "enter"], ["A", "B", "D"])

    def test_force_exit(self):
        res = run([Q, bar(1, 69500, 69625, 69450)])
        st, ev = engine.force_exit(res["state"], ARM + 5 * MIN, 69370, "stop")
        self.assertEqual(ev, [{"t": ARM + 5 * MIN, "type": "exit", "order_id": "A", "price": 69370, "reason": "stop"}])
        tr = st["trades"][0]
        self.assertEqual((tr["exit_t"], tr["exit"], tr["exit_reason"]), (ARM + 5 * MIN, 69370, "stop"))
        self.assertR(tr, -1.0, -1.27848)
        self.assertIsNone(st["position"])
        self.assertEqual(st["status"]["A"], "closed")
        # C is released by A closing: next bar touching 69980 enters C
        st, ev = engine.step(st, bar(6, 69900, 69985, 69800))
        self.assertEqual(ev[0]["order_id"], "C")
        # no position -> no-op
        st2 = engine.new_state(PLAN)
        st2, ev = engine.force_exit(st2, ARM, 69000, "stop")
        self.assertEqual((ev, st2["trades"]), ([], []))

    def test_force_exit_of_breakout_target_cancels_other_breakouts(self):
        res = run([Q, bar(1, 69500, 69625, 69450)])
        st, ev = engine.force_exit(res["state"], ARM + 2 * MIN, 69980, "target")
        self.assertIn(("cancel", "B", "breakout_target_hit"), [(e["type"], e["order_id"], e["reason"]) for e in ev])

    def test_trade_row_keys(self):
        res = run([Q, bar(1, 69600, 69700, 69300)])
        self.assertEqual(set(res["trades"][0]), {
            "order_id", "side", "kind", "level", "confluence", "entry_t", "entry", "exit_t", "exit",
            "exit_reason", "r_gross", "r_net", "stop_moved"})
        self.assertEqual(res["trades"][0]["confluence"], ["live_aid:EU_HIGH"])
        self.assertEqual(res["trades"][0]["level"], "Europe high 69,571")

    def test_state_json_roundtrip_mid_run_identical(self):
        bars = [Q, bar(1, 69500, 69625, 69450), bar(2, 69700, 69880, 69500), bar(3, 69700, 69750, 69610),
                bar(4, 68600, 68700, 68485), bar(5, 68400, 68480, 68240), bar(6, 68300, 68400, 68110),
                {"t": FLAT, "o": 68200, "h": 68300, "l": 68100, "c": 68200}]
        straight = run(bars)
        for cut in range(len(bars) + 1):
            st = engine.new_state(PLAN)
            events = []
            for b in bars[:cut]:
                st, ev = engine.step(st, b)
                events += ev
            st = json.loads(json.dumps(st))  # persist + reload mid-run
            for b in bars[cut:]:
                st, ev = engine.step(st, b)
                events += ev
            self.assertEqual(st, straight["state"], "cut %d" % cut)
            self.assertEqual(events, straight["events"], "cut %d" % cut)
            self.assertEqual(st["trades"], straight["trades"], "cut %d" % cut)
        self.assertGreaterEqual(len(straight["trades"]), 2)  # the scenario really traded

    def test_bad_plans_rejected(self):
        p = plan()
        p["orders"][1]["id"] = "A"
        with self.assertRaises(ValueError):
            engine.new_state(p)
        with self.assertRaises(ValueError):
            engine.new_state(plan(flat_utc="13:00"))
        p = plan()
        p["orders"][2]["arm_after"] = "Z"
        with self.assertRaises(ValueError):
            engine.new_state(p)

    def test_new_state_does_not_alias_plan(self):
        st = engine.new_state(PLAN)
        st["plan"]["orders"][0]["trigger"] = 1
        self.assertEqual(PLAN["orders"][0]["trigger"], 69620)


if __name__ == "__main__":
    unittest.main()
