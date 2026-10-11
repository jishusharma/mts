"""Fabio v3 calendar, windows and day rules (spec sections 2 and 6). Expected values from the spec test plan."""
import datetime as dt
import unittest

from MyTradingSys.backtest.layers.fabio.v3 import (aggregate_day_r, asia_open_utc, ci_halfwidth, day_gate_open, day_type,
                                                   entry_allowed, first_leg_allowed, first_leg_risk, london_open_utc,
                                                   ny_open_utc, window_bars)

D = dt.date


def hm(x):
    return None if x is None else (x.hour, x.minute)


class TestFabioV3DayGates(unittest.TestCase):
    def ap(self, a, b, places=6):
        self.assertAlmostEqual(a, b, places=places)

    def test_t41_ny_open_dst_aware(self):
        for d, want in [(D(2024, 12, 2), (14, 30)), (D(2025, 3, 7), (14, 30)), (D(2025, 3, 10), (13, 30)),
                        (D(2025, 10, 31), (13, 30)), (D(2025, 11, 3), (14, 30)), (D(2026, 3, 9), (13, 30)),
                        (D(2026, 10, 30), (13, 30)), (D(2026, 11, 2), (14, 30))]:
            self.assertEqual(hm(ny_open_utc(d)), want, msg=str(d))

    def test_t41_weekend_has_no_ny_open(self):
        self.assertIsNone(ny_open_utc(D(2025, 3, 8)))
        self.assertIsNone(ny_open_utc(D(2025, 3, 9)))

    def test_t63_us_closed_and_neighbours(self):
        for d in [D(2024, 12, 25), D(2025, 1, 9), D(2025, 4, 18), D(2025, 7, 3), D(2025, 7, 4), D(2025, 11, 27),
                  D(2025, 11, 28), D(2025, 12, 24), D(2026, 4, 3), D(2026, 7, 3)]:
            self.assertIsNone(ny_open_utc(d), msg=str(d))
        self.assertEqual(hm(ny_open_utc(D(2025, 12, 26))), (14, 30))
        self.assertEqual(hm(ny_open_utc(D(2025, 7, 7))), (13, 30))

    def test_t63_london_open_bst(self):
        self.assertEqual(hm(london_open_utc(D(2025, 3, 28))), (8, 0))
        self.assertEqual(hm(london_open_utc(D(2025, 3, 31))), (7, 0))
        self.assertEqual(hm(london_open_utc(D(2025, 10, 24))), (7, 0))
        self.assertEqual(hm(london_open_utc(D(2025, 10, 27))), (8, 0))
        self.assertIsNone(london_open_utc(D(2025, 3, 29)))

    def test_asia_open_is_midnight_utc(self):
        self.assertEqual(hm(asia_open_utc(D(2025, 3, 10))), (0, 0))

    def test_t42_entry_cutoff_open_plus_330(self):
        self.assertTrue(entry_allowed(329, 0))
        self.assertFalse(entry_allowed(330, 0))
        self.assertTrue(entry_allowed(1329, 1000))
        self.assertFalse(entry_allowed(1330, 1000))

    def test_t43_day_r_and_risk_u(self):
        trades = [{"day": "d1", "net_r": 2.0, "risk_u": 0.5}, {"day": "d1", "net_r": -1.1}]       # T61
        result = aggregate_day_r(["d1", "d2"], trades)
        for a, b in zip(result, [-0.1, 0.0]):
            self.ap(a, b)
        t = [{"day": 1, "net_r": 2.0}, {"day": 1, "net_r": 0.6}, {"day": 3, "net_r": -1.2}]       # T43 shape
        result = aggregate_day_r([1, 2, 3], t)
        for a, b in zip(result, [2.6, 0.0, -1.2]):
            self.ap(a, b)

    def test_t44_first_leg_rules(self):
        self.assertTrue(first_leg_allowed([-1.2]))
        self.assertTrue(first_leg_allowed([-2.4]))
        self.assertFalse(first_leg_allowed([-3.6]))
        self.assertFalse(first_leg_allowed([-3.0]))          # daily stop -3R (P29)
        self.assertFalse(first_leg_allowed([-1.2, 1.5]))     # stop after recovery (P28)
        self.assertTrue(first_leg_allowed([-0.5, 0.6]))
        self.assertFalse(first_leg_allowed([], n_first_legs=10))
        self.assertTrue(first_leg_allowed([], n_first_legs=9))   # P30

    def test_t60_floor_and_carry(self):
        self.assertFalse(first_leg_allowed([1.0, -1.0]))     # peak 1, C 0
        self.assertTrue(first_leg_allowed([1.0, -0.5]))
        self.ap(first_leg_risk([1.0, -0.5]), 0.5)
        self.ap(first_leg_risk([2.0]), 1.0)
        self.ap(first_leg_risk([], carry=0.6), 0.6)
        self.assertFalse(first_leg_allowed([-0.6], carry=0.6))
        self.ap(first_leg_risk([], carry=-0.4), 1.0)
        self.assertFalse(first_leg_allowed([1.5], carry=-1.2))    # P 0, -1.2, 0.3
        self.ap(first_leg_risk([-0.5, 0.6]), 0.1)
        self.assertEqual(first_leg_risk([]), 1.0)
        self.assertEqual(first_leg_risk([-1.2, -1.2]), 1.0)
        self.assertEqual(first_leg_risk([-1.2] * 3), 0.0)

    def test_t45_day_gate(self):
        prior = [500, 450, 600]                                                        # median 500
        self.assertTrue(day_gate_open(60, 400, prior, 0.8))
        self.assertFalse(day_gate_open(60, 390, prior, 0.8))
        self.assertTrue(day_gate_open(10, 1, prior, "off"))
        self.assertFalse(day_gate_open(59, 10000, prior, 0.8))                         # before open+60
        self.assertFalse(day_gate_open(60, 400, [], 0.8))                              # fail closed: no history

    def test_ci_halfwidth_spec_example(self):                                              # spec 8: n 30, SD 1.5 -> 0.537R
        self.ap(ci_halfwidth(1.5, 30), 0.53677, places=5)

    def test_day_type_trend_vs_balance(self):                                              # spec 6: |c_last-o_first|/range >= 0.6
        def b(o, h, l, c):
            return {"o": o, "h": h, "l": l, "c": c}
        self.assertEqual(day_type([b(100, 101, 99, 100), b(100, 111, 100, 110)]), "trend")
        self.assertEqual(day_type([b(100, 110, 90, 100), b(100, 105, 95, 101)]), "balance")

    def test_t48_window_exclusions(self):
        def _window(op, n=390, skip=(), thr=1):
            t0 = int(op.timestamp() * 1000)
            return [{"t": t0 + k * 60000, "thr_days": thr} for k in range(n) if k not in skip]

        d = D(2025, 3, 10)
        op = ny_open_utc(d)
        self.assertEqual(len(window_bars(_window(op), d)), 390)
        self.assertEqual(len(window_bars(_window(op, skip=range(5)), d)), 385)     # 5 missing kept
        self.assertIsNone(window_bars(_window(op, skip=range(6)), d))              # 6 missing excluded
        self.assertIsNone(window_bars(_window(op, thr=0), d))                      # thr_days 0 excluded
        self.assertIsNone(window_bars(_window(op), D(2025, 3, 9)))                 # Sunday


if __name__ == "__main__":
    unittest.main()
