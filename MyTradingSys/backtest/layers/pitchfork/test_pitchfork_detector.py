"""Unit tests for the Pitchfork Detector and Geometric Channel Engine.

Verifies:
- Standard, Schiff, and Modified Schiff geometric calculations.
- Parallel line equidistant spacing and slope accuracy.
- Median Line reach evaluation (Rule 1: 80% rule).
- Hagopian failure detection (Rule 4).
- Warning lines and quartile line calculations.
- ZigZag pivot extraction.
"""

import unittest
from MyTradingSys.backtest.layers.pitchfork.pitchfork_detector import (
    PitchforkVariant,
    PitchforkPivot,
    PitchforkChannel,
    construct_pitchfork,
    find_pivots_zigzag,
)


class TestPitchforkDetector(unittest.TestCase):

    def setUp(self):
        # Canonical ascending pitchfork pivots
        # P0 at t=0, p=100
        # P1 at t=10, p=150 (swing high)
        # P2 at t=20, p=110 (swing low)
        self.p0 = PitchforkPivot(index=0, price=100.0, is_high=False)
        self.p1 = PitchforkPivot(index=10, price=150.0, is_high=True)
        self.p2 = PitchforkPivot(index=20, price=110.0, is_high=False)

    def test_standard_pitchfork_geometry(self):
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.STANDARD)

        # Midpoint of P1 (10, 150) and P2 (20, 110) -> t_m = 15, p_m = 130
        self.assertEqual(pf.t_m, 15.0)
        self.assertEqual(pf.p_m, 130.0)

        # Slope = (130 - 100) / (15 - 0) = 30 / 15 = 2.0 price units / bar
        self.assertEqual(pf.slope, 2.0)
        self.assertTrue(pf.is_ascending())

        # Check Median Line at t=0, t=15, t=30
        self.assertEqual(pf.get_ml(0.0), 100.0)
        self.assertEqual(pf.get_ml(15.0), 130.0)
        self.assertEqual(pf.get_ml(30.0), 160.0)

        # At t=10: ML = 100 + 2 * 10 = 120. P1 = 150. Offset UML = +30
        # At t=20: ML = 100 + 2 * 20 = 140. P2 = 110. Offset LML = -30
        self.assertEqual(pf.offset_uml, 30.0)
        self.assertEqual(pf.offset_lml, -30.0)
        self.assertEqual(pf.channel_width, 60.0)
        self.assertEqual(pf.half_width, 30.0)

        # Check UML and LML values
        self.assertEqual(pf.get_uml(10.0), 150.0)
        self.assertEqual(pf.get_lml(20.0), 110.0)
        self.assertEqual(pf.get_uml(30.0), 160.0 + 30.0)
        self.assertEqual(pf.get_lml(30.0), 160.0 - 30.0)

    def test_schiff_pitchfork_geometry(self):
        # Schiff shifts P0 50% in time and price towards P1
        # P0=(0, 100), P1=(10, 150) -> Schiff P0' = (5, 125)
        # Midpoint M = (15, 130)
        # dt = 15 - 5 = 10. dp = 130 - 125 = 5. Slope = 5 / 10 = 0.5
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.SCHIFF)
        self.assertEqual(pf.t0, 5.0)
        self.assertEqual(pf.p0, 125.0)
        self.assertEqual(pf.slope, 0.5)

    def test_modified_schiff_geometry(self):
        # Modified Schiff shifts P0 50% in price only:
        # P0' = (0, 125). Midpoint M = (15, 130)
        # dt = 15 - 0 = 15. dp = 130 - 125 = 5. Slope = 5 / 15 = 1/3 (0.333...)
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.MODIFIED_SCHIFF)
        self.assertEqual(pf.t0, 0.0)
        self.assertEqual(pf.p0, 125.0)
        self.assertAlmostEqual(pf.slope, 5.0 / 15.0, places=5)

    def test_warning_and_quarter_lines(self):
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.STANDARD)
        # At t=30: ML=160, UML=190, LML=130, half_width=30
        # WL1_upper = UML + 30 = 220
        # WL1_lower = LML - 30 = 100
        # Quarter upper (75%) = ML + 15 = 175
        # Quarter lower (25%) = ML - 15 = 145
        self.assertEqual(pf.get_upper_warning_line(30.0, level=1), 220.0)
        self.assertEqual(pf.get_lower_warning_line(30.0, level=1), 100.0)
        self.assertEqual(pf.get_upper_quarter_line(30.0), 175.0)
        self.assertEqual(pf.get_lower_quarter_line(30.0), 145.0)

    def test_median_line_reach_evaluation(self):
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.STANDARD)
        self.assertFalse(pf.has_reached_ml)

        # Bar at t=21: Low=112, High=125, Close=120. ML at t=21 is 100 + 2*21 = 142
        res1 = pf.eval_bar(21, high=125.0, low=112.0, close=120.0)
        self.assertFalse(res1.reached_ml)
        self.assertEqual(res1.status, "tracking")

        # Bar at t=25: ML = 100 + 2*25 = 150. High=155, Low=145 -> touches ML!
        res2 = pf.eval_bar(25, high=155.0, low=145.0, close=152.0)
        self.assertTrue(res2.reached_ml)
        self.assertEqual(res2.status, "reached_ml")
        self.assertTrue(pf.has_reached_ml)

    def test_hagopian_failure_detection(self):
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.STANDARD)

        # Price bounces from P2 (t=20, p=110, LML=110, ML=140)
        # Bar 21: price rallies to 125 (moves toward ML, ML is 142, LML is 112)
        res1 = pf.eval_bar(21, high=126.0, low=115.0, close=125.0)
        self.assertFalse(res1.reached_ml)
        self.assertFalse(res1.hagopian_triggered)

        # Price stalls and rolls over without reaching ML
        # Bar 22: drops to 114 (LML is 114)
        pf.eval_bar(22, high=120.0, low=113.0, close=114.0)

        # Bar 23: Slices through LML! ML=146, LML=116. Close=105 -> Hagopian failure!
        res3 = pf.eval_bar(23, high=114.0, low=103.0, close=105.0)
        self.assertTrue(res3.hagopian_triggered)
        self.assertEqual(res3.status, "hagopian_failure")

    def test_auto_schiff_switch(self):
        # Construct an extremely steep pitchfork: P0=(0, 100), P1=(2, 200), P2=(4, 180)
        # Midpoint M=(3, 190). Slope = 90 / 3 = 30 per bar. Half-width = 10.
        # Steepness = 30 * 2 / 10 = 6.0 > 3.0 threshold
        p0_steep = PitchforkPivot(index=0, price=100.0, is_high=False)
        p1_steep = PitchforkPivot(index=2, price=200.0, is_high=True)
        p2_steep = PitchforkPivot(index=4, price=180.0, is_high=False)

        pf = construct_pitchfork(p0_steep, p1_steep, p2_steep, auto_schiff=True)
        # Should be auto-promoted to MODIFIED_SCHIFF
        self.assertEqual(pf.variant, PitchforkVariant.MODIFIED_SCHIFF)
        self.assertEqual(pf.p0, 150.0)

    def test_zigzag_pivot_finder(self):
        highs = [100, 105, 120, 115, 110, 95, 90, 85, 95, 110, 130, 125, 120]
        lows = [95, 100, 110, 105, 100, 90, 85, 80, 88, 105, 120, 115, 110]
        pivots = find_pivots_zigzag(highs, lows, lookback=2, min_change_pct=0.10)
        self.assertTrue(len(pivots) >= 2)
        # Ensure alternating high/low
        for i in range(1, len(pivots)):
            self.assertNotEqual(pivots[i].is_high, pivots[i - 1].is_high)

    def test_zigzag_higher_high_update(self):
        # Peak 1 at idx 3 (100), continues up to Peak 2 at idx 7 (120)
        # Without qualifying intermediate low, Peak 2 should replace Peak 1
        highs = [80, 85, 95, 100, 95, 94, 98, 120, 115, 105, 95, 90, 85, 80, 75, 70, 72, 71]
        lows = [78, 83, 93, 98, 93, 92, 96, 118, 113, 103, 93, 88, 83, 78, 73, 68, 70, 69]
        pivots = find_pivots_zigzag(highs, lows, lookback=2, min_change_pct=0.10)
        self.assertEqual(len(pivots), 2)
        self.assertEqual(pivots[0].index, 7)
        self.assertEqual(pivots[0].price, 120.0)
        self.assertTrue(pivots[0].is_high)
        self.assertEqual(pivots[1].index, 15)
        self.assertEqual(pivots[1].price, 68.0)
        self.assertFalse(pivots[1].is_high)

    def test_descending_pitchfork_hagopian_failure(self):
        # Descending pitchfork: P0=(0, 200), P1=(10, 140) Low, P2=(20, 180) High
        p0 = PitchforkPivot(index=0, price=200.0, is_high=True)
        p1 = PitchforkPivot(index=10, price=140.0, is_high=False)
        p2 = PitchforkPivot(index=20, price=180.0, is_high=True)
        pf = PitchforkChannel(p0, p1, p2, variant=PitchforkVariant.STANDARD)

        self.assertFalse(pf.is_ascending())
        self.assertFalse(pf.p2_is_lower)  # P2 is on UML

        # Bar 21: drops toward ML (ML = 160 - 2*1 = 158), moves downwards
        pf.eval_bar(21, high=178.0, low=165.0, close=166.0)
        self.assertFalse(pf.has_reached_ml)

        # Bar 22: reverses before reaching ML, rockets above UML (UML at 22 is ~176)
        res = pf.eval_bar(22, high=195.0, low=172.0, close=192.0)
        self.assertTrue(res.hagopian_triggered)
        self.assertEqual(res.status, "hagopian_failure")

    def test_logarithmic_pitchfork(self):
        # BTC macro scale: P0=3000, P1=60000, P2=15000
        p0 = PitchforkPivot(index=0, price=3000.0, is_high=False)
        p1 = PitchforkPivot(index=10, price=60000.0, is_high=True)
        p2 = PitchforkPivot(index=20, price=15000.0, is_high=False)

        pf = construct_pitchfork(p0, p1, p2, variant=PitchforkVariant.STANDARD, log_scale=True)
        ml_20 = pf.get_ml(20.0)
        uml_20 = pf.get_uml(20.0)
        lml_20 = pf.get_lml(20.0)

        # In log space, ML and tines must be strictly positive and ordered: lml < ml < uml
        self.assertTrue(0 < lml_20 < ml_20 < uml_20)

        # Eval bar at t=25: reaches ML
        ml_25 = pf.get_ml(25.0)
        res = pf.eval_bar(25, high=ml_25 * 1.05, low=ml_25 * 0.95, close=ml_25 * 1.01)
        self.assertTrue(res.reached_ml)

    def test_pitchfork_vp_poc_confluence(self):
        from MyTradingSys.backtest.vp_pivot_probe import build_profile

        # Synthetic swing bars from P0 (100) to P1 (150) to P2 (110)
        # Heavy volume concentrated around 110 (the support node)
        lows = [100.0, 110.0, 125.0, 140.0, 148.0, 135.0, 120.0, 110.0, 109.5, 110.5]
        highs = [102.0, 115.0, 130.0, 145.0, 150.0, 140.0, 125.0, 114.0, 112.0, 113.0]
        # Bimodal volume: standard volume along trend, massive volume cluster around 110
        volumes = [500.0, 600.0, 700.0, 800.0, 1200.0, 900.0, 800.0, 5000.0, 6500.0, 4800.0]

        vp = build_profile(lows, highs, volumes, w=1.0)
        self.assertIsNotNone(vp)
        poc = vp["poc_price"]
        val = vp["val"]
        vah = vp["vah"]

        # POC must be in the high-volume cluster around 110.0 - 111.0
        self.assertGreaterEqual(poc, 109.0)
        self.assertLessEqual(poc, 112.0)

        # Pitchfork P2 at 110.0 is inside Value Area [VAL, VAH] and within 1% of POC
        p2_price = 110.0
        self.assertTrue(val <= p2_price <= vah)
        poc_error = abs(p2_price - poc) / poc
        self.assertLessEqual(poc_error, 0.015)

    def test_pitchfork_tine_retest_limit_fill(self):
        # Modified Schiff pitchfork: P0=(0, 100), P1=(10, 150), P2=(20, 110)
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.MODIFIED_SCHIFF)
        is_long = (not self.p2.is_high)
        self.assertTrue(is_long)

        # Bar 24: price tests the LML tine
        t = 24
        lml_val = pf.get_lml(float(t))
        # Bar wraps around LML: low <= LML <= high
        bar_low = lml_val - 2.0
        bar_high = lml_val + 3.0
        self.assertTrue(bar_low <= lml_val <= bar_high)

        # Simulated limit fill at lml_val
        entry_price = lml_val
        stop_price = entry_price * 0.985
        ml_val = pf.get_ml(float(t))

        # Reward to risk ratio at tine entry towards ML
        potential_reward = ml_val - entry_price
        risk = entry_price - stop_price
        rr_ratio = potential_reward / risk
        self.assertGreaterEqual(rr_ratio, 2.0)  # Tine entry guarantees favorable R:R >= 2:1


if __name__ == "__main__":
    unittest.main()
