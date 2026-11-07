"""copy_fork: the operator's copy-paste fork keeps slope and width at a new anchor.

Expected numbers by hand: P0 (0,100) P1 (10,150) P2 (20,110), Standard.
Midpoint (15,130), slope 30/15 = 2; ML at t=10 is 120 so UML offset +30, ML at t=20 is 140 so LML offset -30.
Pasted with P0 on (100,200): ML(110) = 220, UML(110) = 250, LML(110) = 190, width 60.
"""

import math
import unittest

from MyTradingSys.backtest.layers.pitchfork.pitchfork_detector import (
    PitchforkChannel,
    PitchforkPivot,
    PitchforkVariant,
    LogPitchforkChannel,
    copy_fork,
)


class TestCopyFork(unittest.TestCase):

    def setUp(self):
        self.p0 = PitchforkPivot(index=0, price=100.0, is_high=False)
        self.p1 = PitchforkPivot(index=10, price=150.0, is_high=True)
        self.p2 = PitchforkPivot(index=20, price=110.0, is_high=False)

    def test_copy_keeps_slope_and_width_at_new_anchor(self):
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.STANDARD)
        cp = copy_fork(pf, anchor_index=100, anchor_price=200.0)
        self.assertAlmostEqual(cp.slope, 2.0)
        self.assertAlmostEqual(cp.channel_width, 60.0)
        self.assertAlmostEqual(cp.get_ml(100), 200.0)
        self.assertAlmostEqual(cp.get_ml(110), 220.0)
        self.assertAlmostEqual(cp.get_uml(110), 250.0)
        self.assertAlmostEqual(cp.get_lml(110), 190.0)
        self.assertTrue(cp.p2_is_lower)

    def test_schiff_copy_is_a_pure_translation(self):
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.SCHIFF)
        cp = copy_fork(pf, anchor_index=100, anchor_price=200.0)  # dt=+100, dp=+100
        for t in (20.0, 35.0, 60.0):
            self.assertAlmostEqual(cp.get_ml(t + 100), pf.get_ml(t) + 100.0)
            self.assertAlmostEqual(cp.get_uml(t + 100), pf.get_uml(t) + 100.0)
            self.assertAlmostEqual(cp.get_lml(t + 100), pf.get_lml(t) + 100.0)

    def test_copy_of_copy_returns_to_source(self):
        pf = PitchforkChannel(self.p0, self.p1, self.p2, variant=PitchforkVariant.MODIFIED_SCHIFF)
        back = copy_fork(copy_fork(pf, 57, 333.0), 0, 100.0)
        for t in (5.0, 30.0):
            self.assertAlmostEqual(back.get_ml(t), pf.get_ml(t))
            self.assertAlmostEqual(back.get_uml(t), pf.get_uml(t))

    def test_log_copy_keeps_percent_width(self):
        pf = LogPitchforkChannel(self.p0, self.p1, self.p2)
        cp = copy_fork(pf, anchor_index=100, anchor_price=1000.0)  # 10x the source handle
        self.assertTrue(cp.log_scale)
        self.assertAlmostEqual(cp.get_ml(100), pf.get_ml(0) * 10.0)
        for t in (15.0, 40.0):
            self.assertAlmostEqual(cp.get_uml(t + 100) / cp.get_lml(t + 100), pf.get_uml(t) / pf.get_lml(t))
            self.assertAlmostEqual(cp.get_ml(t + 100), pf.get_ml(t) * 10.0, places=6)


if __name__ == "__main__":
    unittest.main()
