"""Krown core detector tests. Expected numbers come from FORMULAS.md section 21 (hand values), never from krown_core.py output."""
import json
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import krown_core as kc  # noqa: E402

HERE = Path(__file__).parent


class TestParams(unittest.TestCase):
    def test_every_param_has_label_and_source(self):
        with open(HERE / "params" / "krown_params.json", encoding="utf-8") as f:
            raw = json.load(f)
        self.assertGreater(len(raw["params"]), 20)
        for name, p in raw["params"].items():
            self.assertIn(p["label"], ("SOURCED", "OURS"), name)
            self.assertTrue(p["source"].strip(), name)
            if p["label"] == "SOURCED":
                self.assertIn("KR-", p["source"], name)

    def test_loaded_values_and_default_off(self):
        v = kc.load_params()
        self.assertEqual(v["vol_mult"], 2)
        self.assertEqual(v["vol_sma"], 20)
        self.assertEqual(v["bbwp_basis"], 7)
        self.assertEqual(v["bbwp_lookback"], 100)
        self.assertEqual(v["bbwp_high"], 85)
        self.assertIs(v["enabled"], False)


class TestZones(unittest.TestCase):
    def test_zone_bounds(self):
        self.assertEqual(kc.zone_bounds("L", 104, 90), (90, 104))
        self.assertEqual(kc.zone_bounds("H", 112, 120), (112, 120))

    def test_zone_not_used_before_confirming_close(self):
        # swing low at bar 2 (low 6), k=2: known at bar 4, a zone only from then on
        h = [12, 11, 10, 11, 12, 13, 14, 15]
        l = [10, 9, 6, 9, 10, 11, 12, 13]
        c = [11, 10, 7, 10, 11, 12, 13, 14]
        v = [100] * 8
        p = dict(kc.load_params(), zone_k=2, zone_min_turns=1)
        for t in range(0, 4):
            self.assertEqual(kc.zones_at(h, l, c, v, t, p), [], t)
        z = kc.zones_at(h, l, c, v, 4, p)
        self.assertEqual(len(z), 1)
        self.assertEqual((z[0]["lo"], z[0]["hi"], z[0]["kind"], z[0]["avail"]), (6, 7, "L", 4))

    def test_needs_two_turns_unless_heavy_volume(self):
        # two swing lows with extremes 6 and 6.5 inside zone [6,7] -> 2 turns
        h = [12, 11, 10, 11, 12, 11, 10, 11, 12]
        l = [10, 9, 6, 9, 10, 9, 6.5, 9, 10]
        c = [11, 10, 7, 10, 11, 10, 8, 10, 11]
        v = [100] * 9
        p = dict(kc.load_params(), zone_k=2, zone_min_turns=2)
        self.assertEqual(kc.zones_at(h, l, c, v, 5, p), [])  # one turn only so far
        z = kc.zones_at(h, l, c, v, 8, p)
        self.assertEqual([(q["lo"], q["hi"], q["turns"]) for q in z if q["kind"] == "L"], [(6, 7, 2)])
        # heavy volume on the first pivot (>= 2x prior mean) marks it at once
        v2 = [100] * 9
        v2[2] = 300
        p2 = dict(p, vol_sma=2)
        z2 = kc.zones_at(h, l, c, v2, 4, p2)
        self.assertEqual(len(z2), 1)
        self.assertTrue(z2[0]["heavy"])

    def test_at_most_five_zones(self):
        rng = random.Random(3)
        n = 300
        c = [100 + 10 * rng.random() for _ in range(n)]
        h = [x + 3 * rng.random() for x in c]
        l = [x - 3 * rng.random() for x in c]
        v = [100 + 200 * rng.random() for _ in range(n)]
        p = dict(kc.load_params(), zone_k=2, zone_min_turns=1)
        self.assertLessEqual(len(kc.zones_at(h, l, c, v, n - 1, p)), 5)


class TestVolume(unittest.TestCase):
    def test_ratio_and_flags(self):
        self.assertAlmostEqual(kc.vol_ratio([100] * 20 + [250], 20)[20], 2.5)
        self.assertAlmostEqual(kc.vol_ratio([100] * 20 + [200], 20)[20], 2.0)
        self.assertAlmostEqual(kc.vol_ratio([100] * 20 + [50], 20)[20], 0.5)
        self.assertIsNone(kc.vol_ratio([100] * 20 + [50], 20)[19])
        self.assertEqual(kc.vol_flags(2.5, 2.0, 0.5), (True, False))
        self.assertEqual(kc.vol_flags(2.0, 2.0, 0.5), (True, False))
        self.assertEqual(kc.vol_flags(0.5, 2.0, 0.5), (False, True))
        self.assertEqual(kc.vol_flags(None, 2.0, 0.5), (False, False))

    def test_same_slot_ratio(self):
        v = [1.0] * 15
        v[0], v[7], v[14] = 100, 300, 400
        r = kc.vol_ratio_slot(v, 7, 2)
        self.assertAlmostEqual(r[14], 2.0)
        self.assertIsNone(r[13])


class TestCandles(unittest.TestCase):
    def test_strict_engulfing(self):
        h = [105, 106]
        l = [100, 99]
        self.assertEqual(kc.engulfing(h, l, [103, 106], 1), "bull")
        self.assertIsNone(kc.engulfing(h, l, [103, 104], 1))  # loose form: no
        self.assertEqual(kc.engulfing([105, 106], [100, 99.5], [103, 99], 1), "bear")
        self.assertIsNone(kc.engulfing([105, 106], [100, 99.5], [103, 101], 1))

    def test_hammer_star_doji(self):
        p = kc.load_params()
        self.assertTrue(kc.is_hammer(100, 101, 90, 100.5, p))
        self.assertFalse(kc.is_hammer(100, 110, 99, 100.5, p))
        self.assertTrue(kc.is_shooting_star(100, 110, 99, 100.5, p))
        self.assertFalse(kc.is_shooting_star(100, 101, 90, 100.5, p))
        self.assertTrue(kc.is_doji(100, 105, 95, 100.5, p))
        self.assertFalse(kc.is_doji(100, 105, 95, 103, p))

    def test_confirmation_close_beyond_wick(self):
        h = [101, 101, 101, 103]
        c = [100, 100.5, 100.9, 102]
        l = [90, 99, 99, 99]
        self.assertEqual(kc.confirm_index("bull", h, l, c, 0, 3), 3)
        self.assertIsNone(kc.confirm_index("bull", h, l, c, 0, 2))
        self.assertIsNone(kc.confirm_index("bear", [105, 105, 105], [95, 96, 94], [100, 99, 95.5], 0, 3))
        self.assertEqual(kc.confirm_index("bear", [105, 105, 105], [95, 96, 94], [100, 99, 94], 0, 3), 2)

    def test_three_black_crows(self):
        o = [110, 109, 107, 105]
        c = [109, 107, 105, 103]
        self.assertTrue(kc.three_crows(o, c, 3))
        self.assertFalse(kc.three_crows(o, [109, 107, 105, 106], 3))
        self.assertTrue(kc.three_crows(o, c, 2))
        self.assertFalse(kc.three_crows(o, c, 1))  # fewer than three bars


class TestStructure(unittest.TestCase):
    H = [10, 12, 11, 14, 13, 12, 17, 15, 13]
    L = [8, 9, 7, 9, 10, 8, 11, 12, 6]
    C = [9, 11, 8, 13, 12, 9, 16, 13, 7.5]

    def test_swings(self):
        got = kc.swings(self.H, self.L, 1)
        self.assertEqual(got, [(1, "H", 12, 2), (2, "L", 7, 3), (3, "H", 14, 4), (5, "L", 8, 6), (6, "H", 17, 7)])

    def test_swing_strict_on_ties(self):
        self.assertEqual(kc.swings([1, 2, 2, 1], [0, 0, 0, 0], 1), [])

    def test_dominant_low_and_reversal(self):
        st = kc.trend_state(self.H, self.L, self.C, 1, 0.0)
        self.assertEqual([s["state"] for s in st], ["range"] * 6 + ["up", "up", "down"])
        self.assertEqual(st[6]["dom_low"], 7)
        self.assertEqual(st[7]["dom_low"], 8)
        self.assertEqual(st[8]["dom_high"], 17)

    def test_no_reversal_on_wick_only(self):
        c = list(self.C)
        c[8] = 8.5  # trades through 6 but closes above the dominant low 8
        st = kc.trend_state(self.H, self.L, c, 1, 0.0)
        self.assertEqual(st[8]["state"], "up")

    def test_state_is_causal(self):
        rng = random.Random(11)
        n = 200
        c = [100 + 8 * rng.random() for _ in range(n)]
        h = [x + 2 * rng.random() for x in c]
        l = [x - 2 * rng.random() for x in c]
        full = kc.trend_state(h, l, c, 2, 0.01)
        for t in (40, 90, 150):
            part = kc.trend_state(h[:t + 1], l[:t + 1], c[:t + 1], 2, 0.01)
            self.assertEqual(part, full[:t + 1])


class TestVolRegime(unittest.TestCase):
    def test_bbwp_hand_values(self):
        out = kc.bbwp([10, 10, 12, 11, 15, 15, 14], 2, 3)
        self.assertEqual(out[:4], [None] * 4)
        self.assertAlmostEqual(out[4], 100.0)
        self.assertAlmostEqual(out[5], 0.0)
        self.assertAlmostEqual(out[6], 100 / 3)

    def test_first_value_index_is_basis_plus_lookback(self):
        out = kc.bbwp([1 + (i % 5) for i in range(120)], 7, 100)
        self.assertIsNone(out[105])
        self.assertIsNotNone(out[106])

    def test_regime(self):
        self.assertEqual(kc.bbwp_regime(85, 85, 30), "expansion")
        self.assertEqual(kc.bbwp_regime(30, 85, 30), "compression")
        self.assertEqual(kc.bbwp_regime(50, 85, 30), "normal")
        self.assertIsNone(kc.bbwp_regime(None, 85, 30))


class TestAverages(unittest.TestCase):
    def test_ema_sma_seed(self):
        e = kc.ema([1, 2, 3, 4, 5, 6], 5)
        self.assertEqual(e[:4], [None] * 4)
        self.assertAlmostEqual(e[4], 3.0)
        self.assertAlmostEqual(e[5], 4.0)
        self.assertEqual(kc.sma([1, 2, 3, 4], 2), [None, 1.5, 2.5, 3.5])

    def test_leash(self):
        low = [10, 11, 12, 13, 12.5, 11]
        high = [20] * 6
        ema = [None, 9, 9.5, 10, 11, 12]
        self.assertEqual(kc.leash(low, high, ema, 3), [(5, "long", 4)])
        # a run of 2 is not late enough
        self.assertEqual(kc.leash([10, 11, 12, 11], [20] * 4, [None, 9, 9.5, 12], 3), [])
        # mirror: high below the average
        self.assertEqual(kc.leash([0] * 6, [10, 9, 8, 7, 7.5, 9], [None, 11, 10.5, 10, 9, 8.5], 3), [(5, "short", 4)])

    def test_cross_state(self):
        self.assertEqual(kc.crosses([1, 2, 3, 1], [2, 2, 2, 2]), [None, None, "up", "down"])
        # tie bar skipped, no cross from + via 0 to +
        self.assertEqual(kc.crosses([3, 2, 3], [2, 2, 2]), [None, None, None])


class TestRsi(unittest.TestCase):
    def test_wilder_hand_values(self):
        r = kc.rsi([10, 11, 10, 12], 2)
        self.assertEqual(r[:2], [None, None])
        self.assertAlmostEqual(r[2], 50.0)
        self.assertAlmostEqual(r[3], 100 - 100 / 6)

    def test_flat_window_returns_50(self):
        # FORMULAS.md s1 step 4 & AUDIT.md B-item: a perfectly flat window returns 50 (neutral), not 100
        closes = [5.0] * 20
        r = kc.rsi(closes, period=14)
        self.assertEqual(r[14], 50.0)
        self.assertEqual(r[19], 50.0)

    def test_zone(self):
        self.assertEqual([kc.rsi_zone(x) for x in (61, 60, 50, 40, 39, None)],
                         ["bull", "range", "range", "range", "bear", None])

    def test_macd_defined_after_slow_period(self):
        c = [100 + i for i in range(60)]
        m, s = kc.macd(c, 12, 26, 9)
        self.assertIsNone(m[24])
        self.assertIsNotNone(m[25])
        self.assertGreater(m[40], 0)  # steady rise: fast EMA above slow EMA


class TestRange(unittest.TestCase):
    H = [10, 11, 10.5, 11]
    L = [9, 9.5, 9, 9.5]

    def test_range_hand_values(self):
        p = dict(kc.load_params(), range_n=4)
        r = kc.range_state(self.H + [11.2], self.L + [9.4], [9.5, 10, 10, 10, 9.4], 4, p)
        self.assertEqual((r["top"], r["bottom"], r["height"]), (11, 9, 2))
        self.assertAlmostEqual(r["position"], 0.2)
        self.assertEqual(r["edge"], "low")
        self.assertIsNone(r["breakout"])

    def test_breakout_close(self):
        p = dict(kc.load_params(), range_n=4)
        r = kc.range_state(self.H + [12], self.L + [10], [9.5, 10, 10, 10, 11.5], 4, p)
        self.assertEqual(r["breakout"], "up")
        r = kc.range_state(self.H + [10], self.L + [8], [9.5, 10, 10, 10, 8.5], 4, p)
        self.assertEqual(r["breakout"], "down")

    def test_too_wide_is_no_range(self):
        p = dict(kc.load_params(), range_n=4)
        self.assertIsNone(kc.range_state([10, 20, 15, 18, 16], [5, 9, 8, 9, 9], [9, 10, 10, 10, 10], 4, p))

    def test_prior_bars_only(self):
        p = dict(kc.load_params(), range_n=4)
        a = kc.range_state(self.H + [11.2], self.L + [9.4], [9.5, 10, 10, 10, 9.4], 4, p)
        b = kc.range_state(self.H + [11.2, 99], self.L + [9.4, 1], [9.5, 10, 10, 10, 9.4, 50], 4, p)
        self.assertEqual(a, b)

    def test_coil_score(self):
        h = [11, 12, 11, 12, 11, 10.5, 10.4, 10.5, 10.4, 10.5]
        l = [9, 8, 9, 8, 9, 10, 10.2, 10, 10.2, 10]
        # last 5 bars mean range 1.9/5 = 0.38 over the 5 before them 14/5 = 2.8 -> 0.135714
        self.assertAlmostEqual(kc.coil_score(h, l, 9, 5, 5), 1.9 / 14, places=6)


class TestTops(unittest.TestCase):
    def test_three_of_four_fires_once(self):
        n = 12
        candle = [False] * n
        vol = [False] * n
        volat = [False] * n
        mom = [False] * n
        candle[5], vol[6], volat[7] = True, True, True
        self.assertEqual(kc.tops(candle, vol, volat, mom, 3, 3), [7])

    def test_stale_signals_do_not_fire(self):
        n = 12
        candle = [False] * n
        vol = [False] * n
        volat = [False] * n
        mom = [False] * n
        candle[1], vol[2], volat[8] = True, True, True  # third signal too late for window 3
        self.assertEqual(kc.tops(candle, vol, volat, mom, 3, 3), [])

    def test_bearish_divergence(self):
        h = [1, 5, 2, 6, 1]
        l = [0, 4, 1, 5, 0]
        rsi = [50, 70, 50, 60, 40]
        # swing highs at 1 (5) and 3 (6, known at 4): price higher, RSI lower -> flagged at 4
        self.assertEqual(kc.bear_divergence(h, l, rsi, 1), [4])
        self.assertEqual(kc.bear_divergence(h, l, [50, 70, 50, 80, 40], 1), [])


class TestRangeProjection(unittest.TestCase):
    def test_range_target_and_prior_trend(self):
        # KR-R07: first-leg target = range height from the breakout. Range [9.5, 10.5], height 1.0.
        h = [10.5] * 5 + [11.6]
        l = [9.5] * 5 + [10.4]
        c = [10.0] * 5 + [11.0]
        p = dict(kc.load_params(), range_n=5)
        rs = kc.range_state(h, l, c, 5, p)
        self.assertEqual(rs["breakout"], "up")
        self.assertAlmostEqual(kc.range_target(rs, "long"), 11.5)  # broken edge 10.5 + 1.0
        self.assertAlmostEqual(kc.range_target(dict(rs, close=11.0), "long"), 12.0)  # breakout close + 1.0
        self.assertIsNone(kc.range_target(rs, "short"))  # no downside break
        self.assertIsNone(kc.range_target(None, "long"))
        down = dict(rs, breakout="down", close=9.0)
        self.assertAlmostEqual(kc.range_target(down, "short"), 8.0)
        # KR-L12: rising swing highs/lows (k=1), then a flat high and a flat low -> state 'range', prior trend 'up'
        hh = [10, 12, 11, 14, 13, 16, 15, 16.05, 15, 15.5, 15]
        ll = [9, 10, 9.5, 11, 10.5, 12, 11.5, 11.8, 11.55, 11.9, 11.9]
        cc = [9.5, 11, 10, 13, 12, 15, 13, 15, 13, 14, 13]
        ts = kc.trend_state(hh, ll, cc, 1, 0.01)
        self.assertEqual(ts[7]["state"], "up")
        self.assertEqual(ts[10]["state"], "range")
        self.assertEqual(kc.prior_trend_bias(hh, ll, cc, 10, 1, 0.01), "up")
        self.assertEqual(kc.prior_trend_bias(hh, ll, cc, 7, 1, 0.01), "up")
        self.assertIsNone(kc.prior_trend_bias(hh, ll, cc, 2, 1, 0.01))


class TestRsiLabels(unittest.TestCase):
    def test_rsi_confirm_and_extreme(self):
        p = kc.load_params()
        line = [None, 50, 72, 69.9, 28, 10, 91, 40]
        self.assertTrue(kc.rsi_confirms_break(line, 2, "long", p))   # 72 > 70
        self.assertFalse(kc.rsi_confirms_break(line, 3, "long", p))  # 69.9
        self.assertFalse(kc.rsi_confirms_break(line, 0, "long", p))  # None
        self.assertTrue(kc.rsi_confirms_break(line, 4, "short", p))  # 28 < 30
        self.assertFalse(kc.rsi_confirms_break(line, 2, "short", p))
        self.assertEqual(kc.rsi_extreme(line, 5, p), ("low", "extreme"))    # 10 <= 10
        self.assertEqual(kc.rsi_extreme(line, 6, p), ("high", "extreme"))   # 91 >= 90
        self.assertEqual(kc.rsi_extreme(line, 4, p), ("low", "stretched"))  # 28
        self.assertEqual(kc.rsi_extreme(line, 2, p), ("high", "stretched")) # 72
        self.assertIsNone(kc.rsi_extreme(line, 7, p))
        self.assertIsNone(kc.rsi_extreme(line, 0, p))
        with open(HERE / "params" / "krown_params.json", encoding="utf-8") as f:
            raw = json.load(f)["params"]
        for k in ("rsi_ob", "rsi_os", "rsi_ext_low", "rsi_ext_high"):
            self.assertEqual(raw[k]["label"], "OURS", k)


class TestRangeTell(unittest.TestCase):
    def test_range_tell_and_grade(self):
        p = kc.load_params()  # tell_fast 5, tell_slow 10, tell_n 5
        flat = [100.0] * 30
        shrink = [100] * 25 + [50] * 5  # last 5 sum 250 vs prior 5 sum 500 -> 0.5
        r = kc.range_tell(flat, shrink, 29, p)
        self.assertEqual((r["flat"], r["tangled"], r["vol_shrinking"], r["tell"]), (True, True, True, True))
        self.assertAlmostEqual(r["vol_ratio"], 0.5)
        trend = [100.0 + i for i in range(30)]
        r = kc.range_tell(trend, [100] * 30, 29, p)
        self.assertEqual((r["flat"], r["tangled"], r["vol_shrinking"], r["tell"]), (False, False, False, False))
        self.assertIsNone(kc.range_tell(flat, shrink, 5, p))  # too little history
        # grade: width over mid of the last range_n bars, bars = trailing bars staying inside range_width_max
        pg = dict(p, range_n=20)
        h = [30] * 10 + [10.5] * 20
        l = [0] * 10 + [9.5] * 20
        g = kc.range_grade(h, l, 29, pg)
        self.assertEqual(g["bars"], 20)
        self.assertAlmostEqual(g["width"], 0.1)
        self.assertEqual(g["grade"], "loose")
        g = kc.range_grade([10.1] * 30, [9.9] * 30, 29, pg)
        self.assertEqual(g["bars"], 30)
        self.assertAlmostEqual(g["width"], 0.02)
        self.assertEqual(g["grade"], "tight")
        self.assertIsNone(kc.range_grade(h, l, 5, pg))


class TestRoleFlip(unittest.TestCase):
    ZONE = {"lo": 100.0, "hi": 102.0, "kind": "L", "avail": 0}

    def test_zone_role_flip_and_retest(self):
        import krown_events as ke
        z = self.ZONE
        c = [105, 104, 103, 99, 97, 98, 101.5, 99, 96]
        self.assertEqual(kc.flip_state(z, c, 2, 5), {"broken": None, "flipped": False, "retested": None, "side": None})
        s = kc.flip_state(z, c, 5, 5)  # close 99 < lo at bar 3, no return yet
        self.assertEqual((s["broken"], s["flipped"], s["retested"], s["side"]), (3, True, None, "down"))
        s = kc.flip_state(z, c, 6, 5)  # 101.5 back inside the zone at bar 6, inside the window
        self.assertEqual((s["broken"], s["flipped"], s["retested"]), (3, True, 6))
        self.assertEqual(kc.flip_state(z, c, 8, 5)["retested"], 6)  # first touch only
        self.assertIsNone(kc.flip_state(z, c, 6, 2)["retested"])  # window 2 covers bars 4-5 only
        # a close back above the zone kills the flip
        c2 = [105, 99, 103.5, 98]
        s = kc.flip_state(z, c2, 3, 5)
        self.assertEqual((s["broken"], s["flipped"]), (1, False))
        # resistance zone broken upward: retest from above
        zh = {"lo": 110.0, "hi": 112.0, "kind": "H", "avail": 0}
        s = kc.flip_state(zh, [108, 109, 113, 115, 111.0], 4, 5)
        self.assertEqual((s["broken"], s["side"], s["flipped"], s["retested"]), (2, "up", True, 4))
        # event: only at the retest bar, short after a support break, long after a resistance break
        self.assertIsNone(ke.retest_event(z, c, 5, 5))
        self.assertEqual(ke.retest_event(z, c, 6, 5),
                         {"i": 6, "side": "short", "setup": "Z10", "tags": ["role_flip", "retest"]})
        self.assertIsNone(ke.retest_event(z, c, 7, 5))
        self.assertEqual(ke.retest_event(zh, [108, 109, 113, 115, 111.0], 4, 5)["side"], "long")


def test_candle_volume_labels():
    p = dict(kc.load_params(), vol_sma=3, low_n=3)
    # KR-C05: body/range 9/10 = 0.9 >= 0.8 full body; 5/10 = 0.5 is not
    assert kc.full_body(100, 110, 100, 109, p) == "bull"
    assert kc.full_body(109, 110, 100, 100, p) == "bear"
    assert kc.full_body(100, 110, 100, 105, p) is None
    # KR-V06: prior ranges 2,2,2 (mean 2); last range 0.1 <= 0.5 * 2 and volume ratio 3 >= 2 -> absorption
    h, l = [12, 12, 12, 10.5], [10, 10, 10, 10.4]
    assert kc.effort_result(3.0, h, l, 3, p) == "absorption"
    assert kc.effort_result(1.0, h, l, 3, p) is None
    assert kc.effort_result(3.0, [12, 12, 12, 12], [10, 10, 10, 10], 3, p) is None
    # KR-V08: close at the lowest of the last 3 closes: ratio 0.4 <= 0.5 apathy, 2.5 >= 2 panic, 1.0 neither
    c = [10, 9, 8, 7]
    assert kc.apathy_panic(0.4, c, 3, p) == "apathy"
    assert kc.apathy_panic(2.5, c, 3, p) == "panic"
    assert kc.apathy_panic(1.0, c, 3, p) is None
    assert kc.apathy_panic(0.4, [10, 9, 8, 9], 3, p) is None


def test_ma_pair_state_and_slope():
    # EMA2 / EMA3 of 1,2,3,2,1 by hand (seed = SMA of first n, alpha 2/(n+1)):
    # fast: t1 1.5, t2 2.5, t3 2.1667, t4 1.3889 ; slow: t2 2, t3 2, t4 1.5
    s = kc.ma_pair_state([1, 2, 3, 2, 1], 2, 3)
    assert s["above"] == [None, None, True, True, False]
    assert s["cross"] == [(4, "down")]
    assert kc.ma_slope([1, 2, 4, 7, None], 2) == [None, None, 3, 5, None]


def test_vol_trap_and_exhaust():
    p = dict(kc.load_params(), vol_trap_bbwp=85, vol_exhaust_bbwp=85)
    line = [None, 40, 90, 95, 80, 60]
    assert kc.vol_trap(line, 2, p) is True
    assert kc.vol_trap(line, 1, p) is False
    assert kc.vol_trap(line, 0, p) is False
    # first bar back below 85 after expansion is t=4 only
    assert [kc.vol_exhaust(line, t, p) for t in range(6)] == [False, False, False, False, True, False]


if __name__ == "__main__":
    unittest.main()
