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


if __name__ == "__main__":
    unittest.main()
