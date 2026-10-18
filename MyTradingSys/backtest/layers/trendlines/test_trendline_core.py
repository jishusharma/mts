"""
Tests for trendline_core.py. Expected numbers are hand-derived from TRENDLINE_CONTRACT.md and
layers/FORMULAS.md section 19 (not from the module). Synthetic bars only: no market data, no VALIDATION/HOLDOUT.

Fixture (hand-built): every bar has range 10 (high = low + 10, close = low + 5) and consecutive lows move
by at most 5, so TR = 10 on every bar and ATR(14) = 10 from bar 14 on. Hence for a line made at ib:
ATR_b = 10, touch tolerance 0.25*10 = 2.5, poke/penetration tolerance 0.10*10 = 1.0, reset distance 10.
Support line (linear): anchors (ia=15, 100) and (ib=27, 106), so L(j) = 100 + 0.5*(j-15); pivot b is
available at the close of bar ib+3 = 30. Bars between anchors sit 4 above the line.
"""
import math
import random
import unittest

from MyTradingSys.backtest.layers.trendlines.trendline_core import (
    TrendlineDetector, atr_sma, detect, line_price, resample_closed)

HOUR = 3600000


def L(j, ia=15):
    return 100 + 0.5 * (j - ia)


def T(off, h=None, c=None):
    """Tail bar given as offsets from the line: (low, high, close); high/close default low+10 / low+5."""
    return (off, h, c)


MAIN_TAIL = [
    T(4), T(4), T(4),            # 28,29,30 (b available at 30)
    T(1), T(2), T(2.5),          # 31,32,33 contact cluster (33 is exactly on the 0.25*ATR boundary)
    T(3),                        # 34 gap bar (2.5 < 3 <= 10): episode stays open
    T(11),                       # 35 low > L+10: reset -> arm A eligible here
    T(1),                        # 36 new contact: episode 2
    T(-1.5),                     # 37 poke (1.5 > 0.1*ATR) with close above the line: contact, not a break
    T(-6, h=4, c=-1),            # 38 close below line: break
    T(-6, h=-1, c=-3),           # 39 high within 2.5 of line from below: retest; close still below
    T(-2, h=3, c=1),             # 40 close back above: reclaim
]


def scenario(ia=15, tail=MAIN_TAIL, vol=None, extra_low=None):
    """Bars 0..ib+len(tail). extra_low: {bar: absolute low} overrides between the anchors."""
    vol = vol or {}
    extra_low = extra_low or {}
    ib = ia + 12
    lows = []
    for j in range(ib + 1 + len(tail)):
        if j < ia - 1:
            low = 105.0
        elif j == ia:
            low = 100.0
        elif j == ib:
            low = float(L(ib, ia))
        elif j <= ib:
            low = L(j, ia) + 4
        else:
            low = L(j, ia) + tail[j - ib - 1][0]
        low = extra_low.get(j, low)
        lows.append(low)
    bars = []
    for j, low in enumerate(lows):
        h, c = low + 10, low + 5
        if j > ib:
            _, ho, co = tail[j - ib - 1]
            h = L(j, ia) + ho if ho is not None else h
            c = L(j, ia) + co if co is not None else c
        bars.append({"t": j * HOUR, "o": c, "h": h, "l": low, "c": c, "v": vol.get(j, 100)})
    return bars


def run(bars, **kw):
    kw.setdefault("transform", "linear")
    return detect(bars, **kw)


def line_events(det, lid):
    return [e for e in det.events if e["line"] == lid]


MAIN_ID = "1h|support|wick|linear|15|27"


class TestFormulas(unittest.TestCase):
    def test_line_price_linear_and_log(self):
        # FORMULAS 19.2: linear L(25)=100+10*15/10=115; log 100*1.21^1.5=133.1 vs linear 131.5
        self.assertAlmostEqual(line_price("linear", 10, 100, 20, 110, 25), 115.0)
        self.assertAlmostEqual(line_price("log", 0, 100, 2, 121, 3), 133.1, places=9)
        self.assertAlmostEqual(line_price("linear", 0, 100, 2, 121, 3), 131.5)

    def test_atr_plain_sma_of_tr(self):
        bars = scenario()
        self.assertIsNone(atr_sma(bars, 13))   # needs 14 TRs: first at bar 14
        self.assertAlmostEqual(atr_sma(bars, 14), 10.0)
        self.assertAlmostEqual(atr_sma(bars, 27), 10.0)

    def test_slope_values(self):
        det = run(scenario())
        ln = det.lines[MAIN_ID]
        self.assertAlmostEqual(ln["atr_b"], 10.0)
        self.assertAlmostEqual(ln["slope_atr"], 0.05)    # (106-100)/12/10
        self.assertAlmostEqual(ln["slope_log"], math.log(1.06) / 12)   # 0.0582689/12 = 0.00485574
        self.assertAlmostEqual(ln["slope_log"], 0.00485574, places=8)


class TestPivots(unittest.TestCase):
    @staticmethod
    def lows_to_bars(lows):
        return [{"t": i * HOUR, "o": x + 1, "h": x + 1, "l": x, "c": x + 1, "v": 1} for i, x in enumerate(lows)]

    def support(self, det):
        return [(p["i"], p["available_at"]) for p in det.pivots if p["side"] == "support"]

    def test_case1_pivot_available_only_at_close_of_i_plus_k(self):
        bars = self.lows_to_bars([9, 8, 7, 5, 6, 7, 8])    # FORMULAS 19.1: bar 3 pivot, available at bar 6
        self.assertEqual(self.support(run(bars[:6])), [])
        self.assertEqual(self.support(run(bars[:7])), [(3, 6)])

    def test_case2_tie_gives_no_pivot_and_is_logged(self):
        det = run(self.lows_to_bars([9, 8, 7, 5, 5, 7, 8, 9]))   # FORMULAS 19.1 tie example
        self.assertEqual(self.support(det), [])
        self.assertEqual(sorted(r["i"] for r in det.rejects if r["reject"] == "tie" and r["side"] == "support"),
                         [3, 4])

    def test_series_edges_never_pivots(self):
        det = run(self.lows_to_bars([5, 9, 9, 9, 9, 9, 9, 9, 5]))
        self.assertEqual(self.support(det), [])

    def test_case9_empty_and_short_series(self):
        for n in (0, 1, 6, 13):
            det = run(self.lows_to_bars(list(range(n, 0, -1))))
            self.assertEqual(det.lines, {})

    def test_close_arm_uses_close_series(self):
        bars = self.lows_to_bars([9, 8, 7, 5, 6, 7, 8])
        # closes = lows+1 -> the close-arm swing low is bar 3 at price 6 (the wick arm would use 5)
        det = run(bars, price_arm="close")
        self.assertEqual(self.support(det), [(3, 6)])
        self.assertEqual([p["price"] for p in det.pivots if p["side"] == "support"], [6])

    @staticmethod
    def oracle(lows, k):
        n = len(lows)
        out = []
        for i in range(k, n - k):
            if all(lows[i] < lows[j] for j in list(range(i - k, i)) + list(range(i + 1, i + k + 1))):
                out.append((i, i + k))
        return out

    def test_matches_batch_oracle_on_random_series(self):
        for seed in range(5):
            rnd = random.Random(seed)
            x, lows = 100.0, []
            for _ in range(200):
                x += rnd.choice([-2, -1, 0, 1, 2]) * 0.5
                lows.append(x)
            for k in (2, 3, 5):
                det = run(self.lows_to_bars(lows), k=k)
                self.assertEqual(self.support(det), self.oracle(lows, k), (seed, k))


class TestLineLifecycle(unittest.TestCase):
    def test_main_scenario_events(self):
        det = run(scenario())
        got = [(e["state"], e["bar"], e["known_at"], e.get("arm") or e.get("episode")) for e in line_events(det, MAIN_ID)]
        self.assertEqual(got, [
            ("proposed", 30, 30, None),
            ("touched", 31, 31, 1),       # 31,32,33 are one contact episode
            ("eligible", 34, 34, "B"),    # bar 31 is itself a swing low exactly on the line (c, ic=31), known at 34
            ("eligible", 35, 35, "A"),    # at the reset bar, not at the contact bar
            ("touched", 36, 36, 2),
            ("poke", 37, 37, None),
            ("broken", 38, 38, None),     # first close beyond the line
            ("retested", 39, 39, None),
            ("reclaimed", 40, 40, None),
        ])
        ln = det.lines[MAIN_ID]
        self.assertEqual(ln["episodes"], 2)
        self.assertEqual(ln["broken_at"], 38)

    def test_case7_arm_a_eligibility_at_reset_not_contact(self):
        bars = scenario()
        self.assertNotIn("A", run(bars[:35]).lines[MAIN_ID]["eligible"])
        self.assertIn("A", run(bars[:36]).lines[MAIN_ID]["eligible"])

    def test_case5_boundary_contact_and_gap_bar(self):
        det = run(scenario(tail=MAIN_TAIL[:6]))   # through bar 33 (low = L+2.5 exactly): still the first episode
        self.assertEqual(det.lines[MAIN_ID]["episodes"], 1)
        det = run(scenario(tail=MAIN_TAIL[:5] + [T(2.6)]))   # 2.6 > 2.5: not a contact
        self.assertEqual(det.lines[MAIN_ID]["episodes"], 1)   # only bars 31, 32 touched
        self.assertTrue(det.lines[MAIN_ID]["open_episode"])

    def test_case3_break_does_not_rewrite_the_old_line_row(self):
        bars = scenario()
        before = run(bars[:38])
        after = run(bars)
        prior = [e for e in after.events if e["line"] == MAIN_ID and e["known_at"] < 38]
        self.assertEqual(prior, [e for e in before.events if e["line"] == MAIN_ID])
        self.assertEqual([e["state"] for e in after.events if e["line"] == MAIN_ID and e["bar"] == 38], ["broken"])

    def test_close_equal_to_line_is_not_a_break(self):
        tail = MAIN_TAIL[:9] + [T(-6, h=4, c=0)]   # bar 37: close == L(37): no break
        det = run(scenario(tail=tail))
        self.assertIsNone(det.lines[MAIN_ID]["broken_at"])

    def test_case6_atr_b_fixed_after_later_spike(self):
        bars = scenario()
        base = run(bars).lines[MAIN_ID]["slope_atr"]
        spiked = [dict(b) for b in bars]
        spiked.append({"t": len(bars) * HOUR, "o": 120, "h": 400, "l": 100, "c": 120, "v": 100})
        det = run(spiked)
        self.assertEqual(det.lines[MAIN_ID]["slope_atr"], base)
        self.assertEqual(det.lines[MAIN_ID]["atr_b"], 10.0)
        self.assertGreater(det.atr[-1], 10.0)

    def test_penetration_rejects_line_but_boundary_passes(self):
        # bar 20: L(20)=102.5. low 101.0 = L-1.5 (> 0.1*ATR_b=1.0 through the line): rejected
        det = run(scenario(extra_low={20: 101.0}))
        self.assertNotIn(MAIN_ID, det.lines)
        self.assertIn({"reject": "penetration", "known_at": 30, "side": "support", "ia": 15, "ib": 27}, det.rejects)
        # low 101.5 = L-1.0 exactly: allowed
        det = run(scenario(extra_low={20: 101.5}))
        self.assertIn(MAIN_ID, det.lines)

    def test_spacing_below_minimum_rejected(self):
        bars = scenario()
        det = run(bars, min_spacing=13)
        self.assertNotIn(MAIN_ID, det.lines)
        self.assertTrue(any(r["reject"] == "spacing" and r["ia"] == 15 and r["ib"] == 27 for r in det.rejects))

    def test_flat_pair_goes_to_control_family(self):
        bars = scenario(extra_low={27: 102.0})   # |pb - pa| = 2 <= 2.5: horizontal, no line
        det = run(bars)
        self.assertNotIn(MAIN_ID, det.lines)
        self.assertTrue(any(r["reject"] == "flat" and r["ia"] == 15 and r["ib"] == 27 for r in det.rejects))

    def test_age_cap_retires_line_and_no_cap_arm_keeps_it(self):
        tail = MAIN_TAIL[:3] + [T(4)] * 8
        det = run(scenario(tail=tail), max_age=5)    # ib=27: retired when t-ib > 5, i.e. at bar 33
        self.assertEqual([(e["state"], e["bar"]) for e in line_events(det, MAIN_ID)][-1], ("retired", 33))
        det = run(scenario(tail=tail), max_age=None)
        self.assertNotIn("retired", [e["state"] for e in line_events(det, MAIN_ID)])

    def test_case8_log_and_linear_ids_never_collapse(self):
        bars = scenario()
        lin, lg = run(bars), run(bars, transform="log")
        self.assertIn("|linear|15|27", MAIN_ID)
        self.assertIn("1h|support|wick|log|15|27", lg.lines)
        self.assertNotIn("1h|support|wick|log|15|27", lin.lines)
        # geometries differ: at bar 40 log L = 100*1.06^(25/12) vs linear 112.5
        self.assertNotAlmostEqual(lg._L(lg.lines["1h|support|wick|log|15|27"], 40), 112.5, places=2)
        self.assertAlmostEqual(lg._L(lg.lines["1h|support|wick|log|15|27"], 40), 100 * 1.06 ** (25 / 12), places=9)


class TestEligibilityArms(unittest.TestCase):
    def test_arm_b_third_pivot_within_tolerance(self):
        # pivot c at bar 40: low = L(40)+1 = 113.5 (|diff| 1 <= 2.5); neighbours at +4. Available at 43.
        tail = [T(4)] * 12 + [T(1)] + [T(4)] * 3 + [T(4)]
        det = run(scenario(tail=tail))
        ev = [e for e in line_events(det, MAIN_ID) if e["state"] == "eligible" and e["arm"] == "B"]
        self.assertEqual([(e["bar"], e["known_at"], e["ic"]) for e in ev], [(43, 43, 40)])

    def test_arm_b_third_pivot_outside_tolerance(self):
        tail = [T(4)] * 12 + [T(3)] + [T(4)] * 4     # |diff| 3 > 2.5
        det = run(scenario(tail=tail))
        self.assertFalse([e for e in line_events(det, MAIN_ID) if e["state"] == "eligible" and e["arm"] == "B"])

    def test_case4_third_pivot_does_not_alter_earlier_rows(self):
        tail = [T(4)] * 12 + [T(1)] + [T(4)] * 4
        full = run(scenario(tail=tail))
        cut = run(scenario(tail=tail)[:42])
        self.assertEqual(cut.events, full.visible_events(41))
        self.assertEqual(full.lines[MAIN_ID]["ia"], 15)
        self.assertEqual(full.lines[MAIN_ID]["ib"], 27)

    def test_arm_v_volume_double_of_prior_20_bars(self):
        # ia=25, ib=37. Bar 25 (volume 200) sits inside the 20 bars before ib, so that mean is
        # (19*100+200)/20 = 105: 210 = 2.0 x passes exactly, 209 fails. Before ia the mean is 100 (FORMULAS 19.7)
        lid = "1h|support|wick|linear|25|37"
        det = run(scenario(ia=25, vol={25: 200, 37: 210}))
        self.assertEqual([(e["bar"], e["arm"]) for e in line_events(det, lid) if e["state"] == "eligible" and e["arm"] == "V"],
                         [(40, "V")])
        det = run(scenario(ia=25, vol={25: 200, 37: 209}))
        self.assertFalse([e for e in line_events(det, lid) if e["state"] == "eligible" and e["arm"] == "V"])

    def test_nearest_selector_prefers_closest_then_newer(self):
        det = run(scenario(tail=MAIN_TAIL[:9]))     # through bar 36: line eligible (A) since bar 35
        ln = det.nearest("support", "A")
        elig = [x for x in det.lines.values() if "A" in x["eligible"] and x["broken_at"] is None and not x["retired"]]
        close = det.bars[-1]["c"]
        want = min(elig, key=lambda x: (abs(close - line_price("linear", x["ia"], x["pa"], x["ib"], x["pb"], 36)),
                                        -x["ib"], -x["ia"]))
        self.assertEqual(ln["id"], want["id"])
        self.assertIsNone(det.nearest("resistance", "A"))
        self.assertIsNone(det.nearest("support", "V"))


class TestCausality(unittest.TestCase):
    """Lines built on data cut at t equal those built on all data and read at t (every t)."""

    def assert_truncation(self, bars, **kw):
        full = detect(bars, **kw)
        for t in range(len(bars)):
            cut = detect(bars[:t + 1], **kw)
            self.assertEqual(cut.events, full.visible_events(t), "events at t=%d" % t)
            self.assertEqual(cut.pivots, [p for p in full.pivots if p["available_at"] <= t], "pivots at t=%d" % t)
            self.assertEqual(cut.rejects, [r for r in full.rejects if r["known_at"] <= t], "rejects at t=%d" % t)
        return full

    def test_truncation_on_main_scenario_every_bar(self):
        full = self.assert_truncation(scenario(), transform="linear")
        self.assertTrue(full.events)

    def test_truncation_on_random_walks_non_vacuous(self):
        total = 0
        for seed in range(3):
            rnd = random.Random(100 + seed)
            x, bars = 100.0, []
            for i in range(130):
                x += rnd.uniform(-1.0, 1.1)
                bars.append({"t": i * HOUR, "o": x, "h": x + rnd.uniform(0.2, 1.5), "l": x - rnd.uniform(0.2, 1.5),
                             "c": x, "v": rnd.randint(50, 250)})
            for kw in ({"transform": "log"}, {"transform": "linear", "price_arm": "close"}):
                total += len(self.assert_truncation(bars, **kw).events)
        self.assertGreater(total, 0)

    def test_update_never_reads_beyond_current_bar(self):
        det = TrendlineDetector(transform="linear")
        for b in scenario():
            det.update(b)
            self.assertEqual(len(det.bars), len(det.atr))
            self.assertTrue(all(e["known_at"] <= len(det.bars) - 1 for e in det.events))


class TestResample(unittest.TestCase):
    def test_resample_closed_only_full_buckets(self):
        bars = [{"t": i * 60000, "o": i, "h": i + 1, "l": i - 1, "c": i, "v": 1} for i in range(150)]
        out = resample_closed(bars, "1h")
        self.assertEqual([b["t"] for b in out], [0, HOUR])   # 150 minutes: only 2 closed hours


if __name__ == "__main__":
    unittest.main()
