"""Tests for measure_1113.py: the ADX numbers must be the ones adx.py gives, events must follow the stated rules."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "backtest", "layers", "adx"))
import measure_1113 as m  # noqa: E402
from adx import adx_di  # noqa: E402


def series(n=60):
    bars = []
    p = 100.0
    for i in range(n):
        p += 1.5 if i < 35 else -2.0     # up leg then down leg
        p += 0.7 * ((-1) ** i)
        bars.append({"h": p + 1.0, "l": p - 1.0, "c": p})
    return bars


class MeasureTests(unittest.TestCase):
    def test_compute_equals_adx_py(self):
        b = series()
        got = m.compute(b)
        want = adx_di([x["h"] for x in b], [x["l"] for x in b], [x["c"] for x in b], 14)
        self.assertEqual(got, want)
        self.assertIsNone(got[2][13])       # ADX first defined at index 2n-1 = 27
        self.assertIsNotNone(got[2][27])

    def test_uptrend_has_plus_di_leading_and_high_adx(self):
        dip, dim, adx = m.compute(series())
        self.assertGreater(dip[34], dim[34])
        self.assertGreater(adx[34], 25.0)

    def test_events_follow_rules(self):
        dip = [None, None, 10, 12, 20, 25, 25, 20]
        dim = [None, None, 15, 14, 18, 10, 10, 30]
        adx = [None, None, 18, 21, 24, 26, 41, 38]
        ev = m.events(dip, dim, adx)
        self.assertEqual(ev["L_cross"], [4])    # +DI crosses above -DI at 4, ADX 24 > 20
        self.assertEqual(ev["L_adx25"], [5])    # ADX 24 -> 26, +DI>-DI
        self.assertEqual(ev["S_cross"], [7])    # -DI crosses above +DI at 7, ADX 38 > 20
        self.assertEqual(ev["peak40"], [7])     # ADX peaks 41 at 6, turns down at 7

    def test_fwd_net_of_fee(self):
        c = [100.0, 101.0, 102.0, 103.0]
        self.assertAlmostEqual(m.fwd(c, 0, 3, 1, 0.0004), 0.03 - 0.0004)
        self.assertAlmostEqual(m.fwd(c, 0, 3, -1, 0.0), -0.03)
        self.assertIsNone(m.fwd(c, 2, 3, 1, 0.0))


if __name__ == "__main__":
    unittest.main()
