import unittest

from MyTradingSys.backtest.layers.fabio import fabio_of_model as M


def b1(o, h, l, c):
    return {"o": o, "h": h, "l": l, "c": c}


def tfbar(o, h, l, c, delta, big=(0, 0, 0, 0)):
    return {"o": o, "h": h, "l": l, "c": c, "delta": delta, "big": {"99": big, "999": big}}


class TestProfile(unittest.TestCase):
    def test_value_area_hand_computed(self):
        # bins 100..150 volumes 10,30,60,40,20,5 -> total 165, 70% = 115.5
        prof = {100.0: 10, 110.0: 30, 120.0: 60, 130.0: 40, 140.0: 20, 150.0: 5}
        lv = M.profile_levels(prof)
        # start POC bin 120 (60); above pair 40+20=60 beats below pair 30+10=40 -> take 130,140 -> 120 >= 115.5
        self.assertEqual(lv["poc"], 125.0)
        self.assertEqual(lv["val"], 120.0)
        self.assertEqual(lv["vah"], 150.0)   # top bin 140 + 10

    def test_lvn_and_hvn(self):
        prof = {100.0: 50, 110.0: 5, 120.0: 60, 130.0: 40, 140.0: 3, 150.0: 45}
        lv = M.profile_levels(prof)
        self.assertEqual(lv["poc"], 125.0)
        self.assertIn(115.0, lv["lvns"])          # local minimum, <= 0.5 x median
        self.assertIn(125.0, lv["hvns"])
        self.assertNotIn(105.0, lv["lvns"])       # edge bin is never an LVN

    def test_empty(self):
        self.assertIsNone(M.profile_levels({}))

    def test_proxy_profile_spreads_uniformly(self):
        bars = [{"buy_vol": 6.0, "sell_vol": 0.0, "l": 100.0, "h": 120.0}]
        p = M.build_profile(bars, "proxy")
        self.assertAlmostEqual(p[100.0], 3.0)
        self.assertAlmostEqual(p[110.0], 3.0)
        self.assertNotIn(120.0, p)


class TestSessions(unittest.TestCase):
    def test_sequence_and_state(self):
        seq = M.session_sequence([0, 86400000])   # 1970-01-01/02: US standard, UK winter
        self.assertEqual([s[0] for s in seq], ["asia", "london", "ny"] * 2)
        self.assertEqual(seq[1][1], 480 * 60000)
        self.assertEqual(seq[2][1], 870 * 60000)   # B102: ny 14:30 UTC in standard time
        self.assertEqual(seq[2][2], 1320 * 60000)
        lv = {"vah": 110.0, "val": 90.0}
        self.assertEqual(M.session_state(111, lv), "imb_up")
        self.assertEqual(M.session_state(89, lv), "imb_dn")
        self.assertEqual(M.session_state(100, lv), "balance")


class TestSessionsDst(unittest.TestCase):
    def test_dst_anchors(self):
        from datetime import datetime, timezone
        def d0(y, m, d):
            return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)
        # 2026-07-15: US DST + UK BST -> london 07:00, ny 13:30 UTC; fixed-UTC model gave 08:00
        seq = M.session_sequence([d0(2026, 7, 15)])
        self.assertEqual((seq[0][2] - seq[0][1]) // 60000, 420)
        self.assertEqual((seq[1][1] - d0(2026, 7, 15)) // 60000, 420)
        self.assertEqual((seq[2][1] - d0(2026, 7, 15)) // 60000, 810)
        # 2026-03-20: US DST started (Mar 8), UK not yet (Mar 29) -> london 08:00, ny 13:30
        seq = M.session_sequence([d0(2026, 3, 20)])
        self.assertEqual([(s[1] - d0(2026, 3, 20)) // 60000 for s in seq], [0, 480, 810])
        # 2026-01-14: winter -> ny 14:30
        seq = M.session_sequence([d0(2026, 1, 14)])
        self.assertEqual([(s[1] - d0(2026, 1, 14)) // 60000 for s in seq], [0, 480, 870])


class TestTfBars(unittest.TestCase):
    def test_aggregate_and_skip_incomplete(self):
        def m(t, o, h, l, c, bv, sv):
            d = {"t": t * 60000, "o": o, "h": h, "l": l, "c": c, "buy_vol": bv, "sell_vol": sv, "delta": bv - sv}
            for p in ("99", "999"):
                d.update({f"b{p}_buy_vol": 1.0, f"b{p}_sell_vol": 0.5, f"b{p}_buy_n": 1, f"b{p}_sell_n": 0})
            return d
        bars = [m(0, 1, 2, 0.5, 1.5, 3, 1), m(1, 1.5, 3, 1, 2, 2, 2), m(2, 2, 2.5, 1.8, 2.2, 1, 4), m(5, 9, 9, 9, 9, 1, 1)]
        tb = M.build_tf_bars(bars, 3)
        self.assertEqual(len(tb), 1)                       # the lone minute-5 bucket is incomplete
        self.assertEqual((tb[0]["o"], tb[0]["h"], tb[0]["l"], tb[0]["c"]), (1, 3, 0.5, 2.2))
        self.assertEqual(tb[0]["delta"], 2 + 0 - 3)
        self.assertEqual(tb[0]["big"]["99"], (3.0, 1.5, 3, 0))
        self.assertEqual((tb[0]["i0"], tb[0]["i1"]), (0, 3))

    def test_mean_abs_delta_prev(self):
        tb = [tfbar(1, 1, 1, 1, d) for d in (1, -3, 2, -4)]
        self.assertEqual(M.mean_abs_delta_prev(tb, 2), [None, None, 2.0, 2.5])


class TestFade(unittest.TestCase):
    LV = [("VAH", 100.0)]

    def run_fade(self, bar, flow="true"):
        tb = [bar]
        return M.fade_events(tb, [10.0], self.LV, 0, 1, 2.5, "99", flow)

    def test_absorption_short_at_vah(self):
        ev = self.run_fade(tfbar(99.5, 100.05, 99.4, 99.8, 50, (30, 5, 3, 1)))
        self.assertEqual(len(ev), 1)
        self.assertEqual((ev[0]["side"], ev[0]["kind"]), ("short", "VAH"))
        self.assertAlmostEqual(ev[0]["stop"], 100.15)

    def test_no_event_when_price_accepted_above_or_closes_above(self):
        self.assertEqual(self.run_fade(tfbar(99.5, 100.5, 99.4, 100.3, 50, (30, 5, 3, 1))), [])   # extended > tol
        self.assertEqual(self.run_fade(tfbar(99.5, 100.05, 99.4, 100.02, 50, (30, 5, 3, 1))), [])  # close beyond level

    def test_needs_heavy_delta_and_big_trades(self):
        self.assertEqual(self.run_fade(tfbar(99.5, 100.05, 99.4, 99.8, 24, (30, 5, 3, 1))), [])   # 24 < 2.5*10
        self.assertEqual(self.run_fade(tfbar(99.5, 100.05, 99.4, 99.8, 50, (5, 30, 1, 3))), [])   # big sellers
        self.assertEqual(self.run_fade(tfbar(99.5, 100.05, 99.4, 99.8, 50, (30, 5, 1, 0))), [])   # only 1 big print
        self.assertEqual(len(self.run_fade(tfbar(99.5, 100.05, 99.4, 99.8, 50, (0, 0, 0, 0)), "proxy")), 1)

    def test_long_at_val_mirror(self):
        ev = M.fade_events([tfbar(100.5, 100.6, 99.95, 100.2, -50, (5, 30, 0, 3))], [10.0], [("VAL", 100.0)],
                           0, 1, 2.5, "99", "true")
        self.assertEqual((ev[0]["side"], ev[0]["kind"]), ("long", "VAL"))
        self.assertAlmostEqual(ev[0]["stop"], 99.85)


class TestBreak(unittest.TestCase):
    def test_up_break_then_retest_holds(self):
        agg = tfbar(99.95, 100.6, 99.9, 100.5, 40, (20, 2, 3, 1))
        rt = tfbar(100.5, 100.6, 100.05, 100.3, 5)
        ev = M.break_events([agg, rt], [10.0, 10.0], [("VAH", 100.0)], 0, 2, 1, 2.5, "99", "true")
        self.assertEqual(len(ev), 1)
        self.assertEqual((ev[0]["bi"], ev[0]["side"]), (1, "long"))
        self.assertAlmostEqual(ev[0]["stop"], 99.8)   # min(agg low 99.9, retest low 100.05) - 0.1

    def test_failed_retest_gives_nothing(self):
        agg = tfbar(99.95, 100.6, 99.9, 100.5, 40, (20, 2, 3, 1))
        fail = tfbar(100.5, 100.5, 99.5, 99.7, -5)
        self.assertEqual(M.break_events([agg, fail], [10.0, 10.0], [("VAH", 100.0)], 0, 2, 1, 2.5, "99", "true"), [])

    def test_down_break_mirror(self):
        agg = tfbar(100.05, 100.1, 99.4, 99.5, -40, (2, 20, 1, 3))
        rt = tfbar(99.5, 99.95, 99.4, 99.7, -5)
        ev = M.break_events([agg, rt], [10.0, 10.0], [("VAL", 100.0)], 0, 2, -1, 2.5, "99", "true")
        self.assertEqual(ev[0]["side"], "short")
        self.assertAlmostEqual(ev[0]["stop"], 100.2)   # max(100.1, 99.95) + 0.1


class TestSimulate(unittest.TestCase):
    def sim(self, bars, side="long", mode="mkt", level=100.0, stop=99.0, hvns=(), trail=False):
        return M.simulate_trade(bars, 0, len(bars) - 1, side, mode, level, stop, list(hvns), trail, 3)

    def test_breakeven_scratch_then_fees(self):
        bars = [b1(100, 100.5, 99.5, 100), b1(100, 101.2, 100, 101), b1(101, 101, 99.9, 100)]
        r = self.sim(bars)
        self.assertEqual((r["reason"], r["gross_R"]), ("be", 0.0))
        self.assertAlmostEqual(r["net_R"], -(0.0005 + 0.0005) * 100 / 1.0)   # fees.py DERIBIT taker 5 bp/side: net = gross - (fee_in+fee_out)*entry/risk = -0.10 R
        self.assertEqual(r["taker_legs"], 2)

    def test_full_stop(self):
        r = self.sim([b1(100, 100.2, 98.9, 99)])
        self.assertEqual((r["reason"], r["gross_R"]), ("stop", -1.0))

    def test_target_3R(self):
        r = self.sim([b1(100, 100.5, 99.5, 100), b1(100, 103.2, 100, 103)])
        self.assertEqual((r["reason"], r["gross_R"]), ("target", 3.0))
        self.assertAlmostEqual(r["net_R"], 3.0 - (0.0005 + 0.0) * 100)   # taker in 5 bp, maker target out 0: 3 - 0.0005*100/1 = 2.95
        self.assertEqual(r["taker_legs"], 1)

    def test_hvn_target_nearer_than_3R(self):
        r = self.sim([b1(100, 102.2, 100, 102)], hvns=[102.0, 100.4])   # 100.4 is < 1R away -> ignored
        self.assertEqual((r["reason"], r["gross_R"]), ("target", 2.0))

    def test_stop_before_target_same_bar(self):
        r = self.sim([b1(100, 103.5, 98.5, 100)])
        self.assertEqual(r["reason"], "stop")

    def test_time_exit(self):
        r = self.sim([b1(100, 100.4, 99.7, 100.2), b1(100.2, 100.6, 100.0, 100.5)])
        self.assertEqual(r["reason"], "time")
        self.assertAlmostEqual(r["gross_R"], 0.5)

    def test_short_mirror(self):
        r = self.sim([b1(100, 100.5, 99.5, 100), b1(100, 100, 96.8, 97)], side="short", stop=101.0)
        self.assertEqual((r["reason"], r["gross_R"]), ("target", 3.0))

    def test_trail_after_2R(self):
        bars = [b1(100, 102.5, 100, 102.4), b1(102.4, 102.6, 101.4, 101.5)]
        r = self.sim(bars, trail=True)
        self.assertEqual(r["reason"], "trail")
        self.assertAlmostEqual(r["gross_R"], 1.5)      # bar 0 high 102.5 (2.5R) -> trail stop 101.5; bar 1 low 101.4 hits it

    def test_no_trail_variant_uses_be_stop(self):
        bars = [b1(100, 102.5, 100, 102.4), b1(102.4, 102.6, 99.9, 100.5)]
        r = self.sim(bars, trail=False)
        self.assertEqual((r["reason"], r["gross_R"]), ("be", 0.0))

    def test_limit_fill_and_no_fill(self):
        bars = [b1(98, 99.0, 97.5, 98.5), b1(98.5, 100.2, 98.4, 99.5), b1(99.5, 99.6, 95.0, 96)]
        r = M.simulate_trade(bars, 0, 2, "short", "limit", 100.0, 101.0, [], False, 3)
        self.assertEqual(r["entry"], 100.0)
        self.assertEqual(r["risk"], 1.0)
        self.assertEqual(r["reason"], "target")           # bar 2 low 95.0 <= 97 (3R)
        self.assertAlmostEqual(r["net_R"], 3.0 - (0.0 + 0.0) * 100)   # DERIBIT maker 0 both legs: net = 3.0 exactly
        self.assertEqual(r["taker_legs"], 0)
        self.assertIsNone(M.simulate_trade(bars[:1], 0, 0, "short", "limit", 100.0, 101.0, [], False, 3))

    def test_limit_needs_through_by_one_tick(self):
        # short limit at 100.0: high 100.05 only touches (< 100.1) -> no fill; high 100.1 trades through -> fill
        self.assertIsNone(M.simulate_trade([b1(99, 100.05, 98, 99)], 0, 0, "short", "limit", 100.0, 101.0, [], False, 3))
        self.assertIsNotNone(M.simulate_trade([b1(99, 100.1, 98, 99)], 0, 0, "short", "limit", 100.0, 101.0, [], False, 3))
        self.assertIsNone(M.simulate_trade([b1(101, 102, 100.05, 101)], 0, 0, "long", "limit", 100.0, 99.0, [], False, 3))

    def test_target_needs_through_by_one_tick(self):
        bars = [b1(100, 100.5, 99.5, 100), b1(100, 103.05, 100, 102.9), b1(102.9, 103.1, 102, 103)]
        r = self.sim(bars)
        self.assertEqual((r["reason"], r["gross_R"]), ("target", 3.0))
        self.assertEqual(r["n_bars"], 3)   # bar 1 only touched 103.05 (< 103.1): not filled

    def test_net_at_slippage_on_taker_legs_only(self):
        r = self.sim([b1(100, 100.5, 99.5, 100), b1(100, 103.2, 100, 103)])   # taker in, maker out, R = 1
        self.assertAlmostEqual(M.net_at(r, 0.0002), r["net_R"] - 1 * 0.0002 * 100)
        lim = M.simulate_trade([b1(99, 100.1, 98, 99), b1(99, 99, 96, 97)], 0, 1, "short", "limit", 100.0, 101.0, [], False, 3)
        self.assertEqual(lim["taker_legs"], 0)
        self.assertEqual(M.net_at(lim, 0.0005), lim["net_R"])

    def test_limit_fill_bar_stop(self):
        bars = [b1(99, 101.5, 98.5, 99)]
        r = M.simulate_trade(bars, 0, 0, "short", "limit", 100.0, 101.0, [], False, 3)
        self.assertEqual((r["reason"], r["gross_R"]), ("stop_fill_bar", -1.0))

    def test_min_risk_floor_widens_stop(self):
        # entry 100, spec stop 99.99 (R=0.01 = 0.01%); floor 0.15% -> stop 99.85, R=0.15
        bars = [b1(100, 100.4, 99.9, 100.3)]
        r = M.simulate_trade(bars, 0, 0, "long", "mkt", 100.0, 99.99, [], False, 3, 0.0015)
        self.assertAlmostEqual(r["risk"], 0.15)
        self.assertAlmostEqual(r["gross_R"], 0.3 / 0.15)   # time exit at close 100.3
        r0 = M.simulate_trade(bars, 0, 0, "long", "mkt", 100.0, 99.99, [], False, 3)
        self.assertAlmostEqual(r0["risk"], 0.01)

    def test_invalid_stop_rejected(self):
        self.assertIsNone(self.sim([b1(100, 101, 99, 100)], stop=100.5))


class TestBreakLimit(unittest.TestCase):
    def test_up_limit_at_level_after_aggression_bar(self):
        agg = tfbar(99.95, 100.6, 99.9, 100.5, 40, (20, 2, 3, 1))
        ev = M.break_limit_events([agg], [10.0], [("VAH", 100.0)], 0, 1, 1, 2.5, "99", "true")
        self.assertEqual(len(ev), 1)
        self.assertEqual((ev[0]["side"], ev[0]["level"], ev[0]["bi"]), ("long", 100.0, 0))
        self.assertAlmostEqual(ev[0]["stop"], 99.8)          # min(agg low 99.9, level 100) - 0.1
        agg2 = tfbar(99.95, 100.6, 100.02, 100.5, 40, (20, 2, 3, 1))   # bar entirely above the level: stop below level
        ev2 = M.break_limit_events([agg2], [10.0], [("VAH", 100.0)], 0, 1, 1, 2.5, "99", "true")
        self.assertAlmostEqual(ev2[0]["stop"], 99.9)

    def test_down_mirror_and_filters(self):
        agg = tfbar(100.05, 100.1, 99.4, 99.5, -40, (2, 20, 1, 3))
        ev = M.break_limit_events([agg], [10.0], [("VAL", 100.0)], 0, 1, -1, 2.5, "99", "true")
        self.assertEqual(ev[0]["side"], "short")
        self.assertAlmostEqual(ev[0]["stop"], 100.2)
        weak = tfbar(100.05, 100.1, 99.4, 99.5, -20, (2, 20, 1, 3))    # 20 < 2.5 * 10
        self.assertEqual(M.break_limit_events([weak], [10.0], [("VAL", 100.0)], 0, 1, -1, 2.5, "99", "true"), [])


class TestStats(unittest.TestCase):
    def test_stats_hand_computed(self):
        s = M.trade_stats([1.0, -2.0, -1.0, 3.0], [1, -2, -1, 3], ["target", "stop", "be", "target"])
        self.assertEqual(s["n"], 4)
        self.assertEqual(s["win"], 0.5)
        self.assertEqual(s["exp_net_R"], 0.25)
        self.assertAlmostEqual(s["pf"], 4.0 / 3.0)
        self.assertEqual(s["max_dd_R"], 3.0)      # cum 1,-1,-2,1 ; peak 1 -> trough -2
        self.assertEqual(s["be_share"], 0.25)

    def test_empty(self):
        self.assertEqual(M.trade_stats([])["n"], 0)


class TestDocstring(unittest.TestCase):
    def test_docstring_names_dst_sessions(self):
        self.assertIn("B102", M.__doc__)
        self.assertIn("session_bounds", M.__doc__)



if __name__ == "__main__":
    unittest.main()
