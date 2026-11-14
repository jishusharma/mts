"""Run: python test_study.py  (passes on the real study) ; STUDY_BUG=1 python test_study.py (must FAIL: look-ahead pivots/phase)."""
import os, sys, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study


def synth(days=70, seed=3):
    rng = np.random.default_rng(seed)
    n = days * 96
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.004, n)))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + abs(rng.normal(0, 0.002, n)))
    l = np.minimum(o, c) * (1 - abs(rng.normal(0, 0.002, n)))
    t = 1577836800000 + np.arange(n) * 900000  # 2020-01-01 00:00 UTC
    return np.c_[t, o, h, l, c, np.ones(n)]


class T(unittest.TestCase):
    def test_pivot_formula(self):
        p = study.pivots(110.0, 90.0, 100.0)
        self.assertEqual((p["P"], p["R1"], p["S1"], p["R2"], p["S2"], p["R3"], p["S3"]), (100, 110, 90, 120, 80, 130, 70))

    def test_no_lookahead_truncation(self):
        a = synth()
        cut = 40 * 96 + 10
        full = study.day_tables(a)
        part = study.day_tables(a[:cut])
        sl = slice(40 * 96, cut)  # bars early in day 40: only day 39 data may be used
        self.assertTrue(full[2][sl].all() and part[2][sl].all(), "levels must be valid from prior day")
        for k in full[0]:
            np.testing.assert_allclose(full[0][k][sl], part[0][k][sl])
        np.testing.assert_array_equal(full[1][sl], part[1][sl])

    def _D(self, closes):
        n = len(closes)
        a = np.zeros((n, 6))
        a[:, 0] = np.arange(n) * 900000
        a[:, 1] = [100] * n
        a[:, 4] = closes
        a[:, 2] = np.maximum(a[:, 1], a[:, 4]) + 0.0
        a[:, 3] = np.minimum(a[:, 1], a[:, 4]) - 0.0
        lv = {k: np.full(n, v) for k, v in dict(S3=70., S2=80., S1=90., P=95., R1=103., R2=120., R3=130.).items()}
        return dict(a=a, lv=lv, ph=np.zeros(n, int), valid=np.ones(n, bool), atr=np.full(n, 0.3), sym="X")

    def test_target_and_stop(self):
        D = self._D([100, 100, 100, 100, 102, 102, 102, 102])
        D["a"][2, 3] = 99.0  # swing low in last 6 bars -> dist 1
        D["a"][4, 2] = 103.5  # touches R1=103
        r, df, xi, e = study.simulate(D, 2, 1, 24)
        self.assertAlmostEqual(r, 3.0)
        D = self._D([100, 100, 100, 100, 98.5, 100, 100, 100])
        D["a"][2, 3] = 99.0
        r, df, xi, e = study.simulate(D, 2, 1, 24)
        self.assertAlmostEqual(r, -1.5)  # close-basis stop exits at the close

    def test_entry_is_next_open(self):
        D = self._D([100, 100, 100, 100, 102, 102, 102, 102])
        D["a"][3, 1] = 100.5
        D["a"][2, 3] = 99.0
        D["a"][4, 2] = 103.5
        r, df, xi, e = study.simulate(D, 2, 1, 24)
        self.assertEqual(e, 100.5)


if __name__ == "__main__":
    unittest.main()
