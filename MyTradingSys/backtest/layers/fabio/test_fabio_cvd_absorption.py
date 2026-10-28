import unittest

from MyTradingSys.backtest.layers.fabio.fabio_cvd_absorption import (
    cumulative_cvd,
    cvd_absorption_events,
)


def bar(t, o, c, v, tbv):
    return {"t": t, "o": o, "c": c, "v": v, "tbv": tbv}


class TestCumulativeCvd(unittest.TestCase):
    def test_basic_running_sum(self):
        bars = [
            {"v": 10, "tbv": 5},   # delta = 2*5-10 = 0
            {"v": 20, "tbv": 4},   # delta = 2*4-20 = -12
            {"v": 5, "tbv": 10},   # delta = 2*10-5 = 15
        ]
        self.assertEqual(cumulative_cvd(bars), [0.0, -12.0, 3.0])

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            cumulative_cvd([])


# Hand-verified fixture (see 087-fabio-cvd-absorption.md packed spec):
# find_swings(left=1,right=1,use_body=True) on this series yields exactly two
# "low" swings: i=1 (price=95, confirmed_i=2) and i=4 (price=94.98, confirmed_i=5).
# Cumulative CVD at those bars: cvd[1]=-5.0, cvd[4]=-16.0 (verified independently
# by running cc_structure.find_swings and the delta formula in a scratch script).
def _bullish_fixture():
    return [
        bar(0, 100, 105, 20, 12.5),   # delta=5
        bar(1, 95, 110, 20, 5),       # delta=-10 ; swing low i=1, price=95
        bar(2, 98, 115, 20, 8.5),     # delta=-3
        bar(3, 97, 120, 20, 9),       # delta=-2
        bar(4, 94.98, 125, 20, 7),    # delta=-6 ; swing low i=4, price=94.98
        bar(5, 98, 130, 20, 10.5),    # delta=1
        bar(6, 100, 135, 20, 11),     # delta=2
    ]


class TestCvdAbsorptionEvents(unittest.TestCase):
    def test_bullish_absorption_fires_on_cvd_lower_low_price_holds(self):
        bars = _bullish_fixture()
        events = cvd_absorption_events(bars, left=1, right=1, use_body=True, price_tolerance=0.001)
        self.assertEqual(len(events), 1)
        ev = events[0]
        self.assertEqual(ev["side"], "long")
        self.assertEqual(ev["kind"], "bullish_absorption")
        self.assertEqual(ev["i"], 5)          # confirmed_i of the i=4 swing
        self.assertEqual(ev["swing_i"], 4)
        self.assertEqual(ev["t"], bars[5]["t"])
        self.assertAlmostEqual(ev["cvd_prev"], -5.0)
        self.assertAlmostEqual(ev["cvd_cur"], -16.0)
        self.assertEqual(ev["price_prev"], 95)
        self.assertEqual(ev["price_cur"], 94.98)

    def test_no_event_when_price_also_makes_a_deep_new_low(self):
        # Same shape as the bullish fixture but the second low breaks price by
        # far more than price_tolerance (94.98 -> 90), so condition (b) fails.
        bars = _bullish_fixture()
        bars[4] = bar(4, 90, 125, 20, 7)
        events = cvd_absorption_events(bars, left=1, right=1, use_body=True, price_tolerance=0.001)
        self.assertEqual(events, [])

    def test_negative_price_tolerance_raises(self):
        bars = _bullish_fixture()
        with self.assertRaises(ValueError):
            cvd_absorption_events(bars, left=1, right=1, price_tolerance=-0.01)

    def test_fewer_than_two_same_kind_swings_yields_no_events(self):
        # Monotonic series: at most one swing of either kind can ever confirm.
        bars = [bar(i, 100 + i, 100 + i, 10, 5) for i in range(5)]
        events = cvd_absorption_events(bars, left=1, right=1)
        self.assertEqual(events, [])


if __name__ == "__main__":
    unittest.main()
