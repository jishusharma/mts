"""Tests for b141_htf_stage2.py. Expected values are hand arithmetic from the pre-registration section 5.2
(FR = (max high - min low over next H bars) / (sqrt(H) * ATR); D = median(FR|bal) - median(FR|not bal); H1 predicts D < 0).
Ramp: c_j = j, h = j+1, l = j-1. Forward 4 bars after i=2 are bars 3..6: max h = 7, min l = 2, range 5; atr 2 -> 5/(sqrt(4)*2) = 1.25."""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import b141_htf_stage2 as s2

MIN = 60000


def ramp(n):
    c = np.arange(n, dtype=float)
    return {"t": np.arange(n, dtype=np.int64) * MIN, "h": c + 1, "l": c - 1, "c": c, "v": np.ones(n)}


def synth(n, lo_for_balanced, shuffle_label=False):
    """n closes alternating balanced / not (ER 0.01 / 0.9), 3 closes per day, 3 years, vol cycling through 3 levels."""
    rows = []
    for k in range(n):
        bal = k % 2 == 0
        fr = (lo_for_balanced if bal else 2.0) + 0.001 * (k % 7)
        if shuffle_label:
            fr = 1.5 + 0.001 * (k % 7) + (0.3 if (k // 2) % 2 else 0.0)
        rows.append({"st": {"er": 0.01 if bal else 0.9}, "fr": fr, "i": k * 100, "day": k // 3,
                     "year": 2022 + (k * 3) // n, "vol": 0.001 * (1 + (k // 2) % 3)})
    return rows


class Stage2Test(unittest.TestCase):
    def test_forward_ratio_value(self):
        self.assertAlmostEqual(s2.forward_ratio(ramp(10), 2, 4, 2.0), 1.25)

    def test_forward_ratio_none_cases(self):
        K = ramp(10)
        self.assertIsNone(s2.forward_ratio(K, 6, 4, 2.0))          # needs bar 10, data ends at 9
        self.assertIsNone(s2.forward_ratio(K, 2, 4, 0.0))          # atr 0
        K["t"][5:] += MIN                                          # one missing minute inside the forward window
        self.assertIsNone(s2.forward_ratio(K, 2, 4, 2.0))

    def test_weighted_median(self):
        v = np.array([1.0, 2.0, 3.0])
        self.assertEqual(s2.wmedian(v, np.array([1.0, 1.0, 1.0])), 2.0)
        self.assertEqual(s2.wmedian(v, np.array([0.0, 0.0, 5.0])), 3.0)
        self.assertTrue(np.isnan(s2.wmedian(v, np.zeros(3))))

    def test_effective_n(self):
        self.assertEqual(s2.effective_n([0, 5, 10, 12, 30], 10), 3)   # kept: 0, 10, 30

    def test_terciles_three_groups(self):
        t = s2.terciles(np.arange(9, dtype=float))
        self.assertEqual(sorted(set(t.tolist())), [0, 1, 2])
        self.assertEqual(int((t == 0).sum()), 3)

    def test_real_effect_passes(self):
        r = s2.evaluate(synth(600, 1.0), "B", {"e": 0.1}, "4H")
        self.assertAlmostEqual(r["D"], -1.0, places=2)             # 1.0 vs 2.0 plus <= 0.006 jitter
        self.assertLess(r["ci95"][1], 0)
        self.assertTrue(r["year_sign_ok"])
        self.assertTrue(r["placebo_beaten"])
        self.assertTrue(r["pass_"])

    def test_no_effect_fails(self):
        r = s2.evaluate(synth(600, 1.0, shuffle_label=True), "B", {"e": 0.1}, "4H")
        self.assertFalse(r["pass_"])

    def test_reversed_effect_fails(self):
        r = s2.evaluate(synth(600, 3.0), "B", {"e": 0.1}, "4H")     # balanced has the LARGER forward range
        self.assertGreater(r["D"], 0)
        self.assertFalse(r["pass_"])

    def test_small_class_not_evaluated(self):
        rows = synth(40, 1.0)
        r = s2.evaluate(rows, "B", {"e": 0.1}, "4H")
        self.assertFalse(r["pass_"])
        self.assertIsNone(r["D"])

    def test_select_best_ci_then_coverage(self):
        a = {"pass_": True, "ci95": [-0.5, -0.2], "coverage": 0.5}
        b = {"pass_": True, "ci95": [-0.5, -0.3], "coverage": 0.2}
        c = {"pass_": True, "ci95": [-0.5, -0.3], "coverage": 0.65}
        d = {"pass_": False, "ci95": [-0.9, -0.8], "coverage": 0.7}
        self.assertIs(s2.select([a, b, c, d]), c)
        self.assertIsNone(s2.select([d]))


if __name__ == "__main__":
    unittest.main()
