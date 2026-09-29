import unittest

from MyTradingSys.backtest.layers.positioning.funding_cvd_fade import (
    funding_percentiles,
    funding_pct_at,
    cvd_price_divergence,
    funding_cvd_fade_events,
)

# Expected numbers hand-computed from FORMULAS.md section 14 (T055 C1).
H = 3600000


def bars_from(closes, deltas):
    # v=10, tbv chosen so that 2*tbv - v == delta
    return [
        {"t": i * H, "c": c, "v": 10.0, "tbv": 5.0 + d / 2.0}
        for i, (c, d) in enumerate(zip(closes, deltas))
    ]


BEAR = bars_from([10, 11, 12, 13, 14, 15], [5, 5, 5, 5, -5, -5])   # cvd 5,10,15,20,15,10
BULL = bars_from([15, 14, 13, 12, 11, 10], [-5, -5, -5, -5, 5, 5])  # cvd -5,-10,-15,-20,-15,-10


class TestFundingPercentiles(unittest.TestCase):
    def test_values(self):
        f = [(i * 8 * H, r) for i, r in enumerate([0.0001, 0.0002, 0.0003, 0.0004, 0.0001])]
        s = funding_percentiles(f, 4)
        self.assertEqual([t for t, _ in s], [3 * 8 * H, 4 * 8 * H])
        self.assertAlmostEqual(s[0][1], 1.0)
        self.assertAlmostEqual(s[1][1], 0.25)

    def test_too_short_and_bad_lookback(self):
        self.assertEqual(funding_percentiles([(0, 0.1)], 2), [])
        with self.assertRaises(ValueError):
            funding_percentiles([(0, 0.1)], 0)


class TestFundingPctAt(unittest.TestCase):
    def test_lookup(self):
        s = [(100, 1.0), (200, 0.25)]
        self.assertIsNone(funding_pct_at(s, 99))
        self.assertEqual(funding_pct_at(s, 100), 1.0)
        self.assertEqual(funding_pct_at(s, 199), 1.0)
        self.assertEqual(funding_pct_at(s, 200), 0.25)


class TestDivergence(unittest.TestCase):
    def test_bearish(self):
        self.assertEqual(cvd_price_divergence(BEAR, 3),
                         [{"i": 4, "kind": "bearish"}, {"i": 5, "kind": "bearish"}])

    def test_bullish(self):
        self.assertEqual(cvd_price_divergence(BULL, 3),
                         [{"i": 4, "kind": "bullish"}, {"i": 5, "kind": "bullish"}])

    def test_errors(self):
        with self.assertRaises(ValueError):
            cvd_price_divergence([], 3)
        with self.assertRaises(ValueError):
            cvd_price_divergence(BEAR, 0)


class TestEvents(unittest.TestCase):
    def test_merged_short(self):
        # lookback=2: k=1 window [0.0001, 0.0005], r=0.0005 -> 2/2 = 1.0, known from t=4h
        f = [(0, 0.0001), (4 * H, 0.0005)]
        ev = funding_cvd_fade_events(BEAR, f, lookback=2, n=3, hi=0.95, lo=0.05)
        self.assertEqual([(e["i"], e["side"]) for e in ev], [(4, "short"), (5, "short")])
        self.assertAlmostEqual(ev[0]["funding_pct"], 1.0)
        self.assertEqual(ev[0]["div"], "bearish")

    def test_merged_no_event_when_funding_not_extreme(self):
        # k=1 window [0.0001, 0.00005], r=0.00005 -> 1/2 = 0.5
        f = [(0, 0.0001), (4 * H, 0.00005)]
        self.assertEqual(funding_cvd_fade_events(BEAR, f, lookback=2, n=3, hi=0.95, lo=0.05), [])

    def test_bullish_needs_low_funding(self):
        # k=1 window [0.0003, 0.0001], r=0.0001 -> 1/2 = 0.5 ; with lo=0.5 it triggers long
        f = [(0, 0.0003), (4 * H, 0.0001)]
        ev = funding_cvd_fade_events(BULL, f, lookback=2, n=3, hi=0.95, lo=0.5)
        self.assertEqual([(e["i"], e["side"]) for e in ev], [(4, "long"), (5, "long")])

    def test_funding_only(self):
        # records at 1h, 3h, 5h ; lookback 2: k=1 pct 0.5 (no event), k=2 window [0.0001, 0.0009] -> 1.0
        f = [(1 * H, 0.0003), (3 * H, 0.0001), (5 * H, 0.0009)]
        ev = funding_cvd_fade_events(BEAR, f, lookback=2, n=3, hi=0.95, lo=0.05, use_divergence=False)
        self.assertEqual([(e["i"], e["side"]) for e in ev], [(5, "short")])
        self.assertIsNone(ev[0]["div"])

    def test_no_series(self):
        self.assertEqual(funding_cvd_fade_events(BEAR, [(0, 0.1)], lookback=2, n=3), [])


if __name__ == "__main__":
    unittest.main()
