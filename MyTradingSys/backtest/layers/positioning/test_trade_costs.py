import unittest

from MyTradingSys.backtest.layers.positioning.trade_costs import funding_paid, net_return

# Expected numbers hand-computed from FORMULAS.md section 13 (T055 shared cost model).
FUNDING = [(0, 0.0009), (28800000, 0.0001), (57600000, 0.0003)]


class TestFundingPaid(unittest.TestCase):
    def test_long_excludes_entry_instant_includes_exit(self):
        self.assertAlmostEqual(funding_paid("long", 0, 57600000, FUNDING), 0.0004, places=12)

    def test_short_receives(self):
        self.assertAlmostEqual(funding_paid("short", 0, 57600000, FUNDING), -0.0004, places=12)

    def test_exit_before_first_record_in_window(self):
        self.assertEqual(funding_paid("long", 0, 28799999, FUNDING), 0.0)

    def test_window_outside_loaded_span_raises(self):
        # B103: was silently 0.0 / partial sum
        with self.assertRaises(ValueError):
            funding_paid("long", -1, 28800000, FUNDING)        # starts before first record
        with self.assertRaises(ValueError):
            funding_paid("long", 0, 57600001, FUNDING)         # ends after last record
        with self.assertRaises(ValueError):
            funding_paid("long", 100000000, 110000000, FUNDING)  # wholly after the span
        with self.assertRaises(ValueError):
            net_return("long", 100, 101, 100000000, 110000000, FUNDING)

    def test_empty_funding(self):
        self.assertEqual(funding_paid("long", 0, 100, []), 0.0)

    def test_bad_side_and_reversed_times(self):
        with self.assertRaises(ValueError):
            funding_paid("flat", 0, 10, FUNDING)
        with self.assertRaises(ValueError):
            funding_paid("long", 10, 0, FUNDING)


class TestNetReturn(unittest.TestCase):
    def test_long(self):
        # 0.01 - 0.0010 - 0.0002 - 0.0004
        self.assertAlmostEqual(net_return("long", 100, 101, 0, 57600000, FUNDING), 0.0084, places=12)

    def test_short(self):
        # 0.01 - 0.0012 + 0.0004
        self.assertAlmostEqual(net_return("short", 100, 99, 0, 57600000, FUNDING), 0.0092, places=12)

    def test_no_funding_custom_fees(self):
        # long 200 -> 202: gross 0.01; fee 0.0004 + slip 0 -> 0.0096
        self.assertAlmostEqual(
            net_return("long", 200, 202, 0, 10, [], fee_rt=0.0004, slip_rt=0.0), 0.0096, places=12)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            net_return("long", 0, 1, 0, 1, [])
        with self.assertRaises(ValueError):
            net_return("x", 1, 1, 0, 1, [])


if __name__ == "__main__":
    unittest.main()
