"""Edge-case tests for bt_rsi. Expected numbers hand-derived from FORMULAS.md section 1 (textbook Wilder)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bt_rsi


class TestRsiWilderEdges(unittest.TestCase):
    def test_formulas_md_worked_example_period3(self):
        # FORMULAS.md: closes [10,12,11,14] period 3 -> rsi[3] = 100 - 100/6 = 83.3333
        r = bt_rsi.rsi_wilder([10, 12, 11, 14], period=3)
        self.assertEqual(r[:3], [None, None, None])
        self.assertAlmostEqual(r[3], 500 / 6, places=9)

    def test_smoothing_step_after_seed(self):
        # append 13 (delta -1): avg_gain=(5/3*2+0)/3=10/9, avg_loss=(1/3*2+1)/3=5/9, rs=2 -> 100-100/3
        r = bt_rsi.rsi_wilder([10, 12, 11, 14, 13], period=3)
        self.assertAlmostEqual(r[4], 100 - 100 / 3, places=9)

    def test_formulas_md_seed_divides_by_period(self):
        # FORMULAS.md period=5 seed: deltas [2,-1,2,3,-1] -> avg_gain=1.4, avg_loss=0.4, rs=3.5
        r = bt_rsi.rsi_wilder([100, 102, 101, 103, 106, 105], period=5)
        self.assertAlmostEqual(r[5], 100 - 100 / 4.5, places=9)

    def test_all_down_is_zero(self):
        r = bt_rsi.rsi_wilder([5, 4, 3, 2, 1], period=3)
        self.assertEqual(r[3], 0.0)
        self.assertEqual(r[4], 0.0)

    def test_period_one_minimum(self):
        r = bt_rsi.rsi_wilder([1, 2, 1, 1], period=1)
        self.assertIsNone(r[0])
        self.assertEqual(r[1], 100.0)
        self.assertEqual(r[2], 0.0)      # avg_gain=(1*0+0)/1=0, avg_loss=1
        self.assertEqual(r[3], 50.0)     # gain 0, loss (1*0+0)/1=0 -> flat rule

    def test_len_equal_period_and_empty_raise(self):
        with self.assertRaises(ValueError):
            bt_rsi.rsi_wilder([1, 2, 3], period=3)
        with self.assertRaises(ValueError):
            bt_rsi.rsi_wilder([], period=14)


class TestRsiRegimeEdges(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(bt_rsi.rsi_regime([]), [])

    def test_shorter_than_lookback_all_none(self):
        self.assertEqual(bt_rsi.rsi_regime([50.0, 55.0], lookback=3), [None, None])

    def test_none_prefix_shortens_window(self):
        r = bt_rsi.rsi_regime([None, None, 45.0, 50.0, 65.0], lookback=3)
        self.assertEqual(r, [None, None, None, None, "BULL"])

    def test_bear_bull_range_and_boundaries(self):
        self.assertEqual(bt_rsi.rsi_regime([55.0, 50.0, 35.0], lookback=3)[2], "BEAR")   # max<=60, min<=40
        self.assertEqual(bt_rsi.rsi_regime([35.0, 50.0, 65.0], lookback=3)[2], "RANGE")  # min<40, max>60
        self.assertEqual(bt_rsi.rsi_regime([40.0, 50.0, 60.0], lookback=3)[2], "BULL")   # exact boundaries: bull rule first

    def test_bad_params_raise(self):
        with self.assertRaises(ValueError):
            bt_rsi.rsi_regime([50.0], lo=60.0, hi=40.0)
        with self.assertRaises(ValueError):
            bt_rsi.rsi_regime([50.0], lookback=0)


if __name__ == "__main__":
    unittest.main()
