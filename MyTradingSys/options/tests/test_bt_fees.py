"""Tests for fees.py (BT_SPEC "Conventions"): trade fee min(0.0003, 12.5% of price) per contract per leg (0.0004 cap before
2020-08-24 UTC), delivery fee only for ITM options expiring on a Friday, perp taker fee 0.05% of notional."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bt_testutil as U  # noqa: E402
from bt_testutil import ms  # noqa: E402

import fees as F  # noqa: E402

TS = ms(2026, 10, 9, 16)
FRI_EXP = ms(2026, 10, 9, 8)           # Friday 08:00 UTC


class TradeFee(unittest.TestCase):
    def test_flat_cap_when_premium_is_large(self):
        self.assertAlmostEqual(F.trade_fee_btc(0.0100, TS), 0.0003, places=12)    # 12.5% = 0.00125 > cap
        self.assertAlmostEqual(F.trade_fee_btc(0.0500, TS), 0.0003, places=12)
        self.assertAlmostEqual(F.trade_fee_btc(0.0030, TS), 0.0003, places=12)    # 12.5% = 0.000375 > cap

    def test_premium_fraction_when_premium_is_small(self):
        self.assertAlmostEqual(F.trade_fee_btc(0.0010, TS), 0.000125, places=12)  # cap case: 12.5% of the price binds
        self.assertAlmostEqual(F.trade_fee_btc(0.0020, TS), 0.00025, places=12)
        self.assertAlmostEqual(F.trade_fee_btc(0.0001, TS), 0.0000125, places=12)
        self.assertAlmostEqual(F.trade_fee_btc(0.0005, TS), 0.0000625, places=12)

    def test_crossover_price_is_0_0024(self):
        self.assertAlmostEqual(F.trade_fee_btc(0.0024, TS), 0.0003, places=12)    # 0.125 * 0.0024 = 0.0003 exactly
        self.assertAlmostEqual(F.trade_fee_btc(0.0023, TS), 0.0002875, places=12)
        self.assertAlmostEqual(F.trade_fee_btc(0.0025, TS), 0.0003, places=12)

    def test_never_exceeds_either_bound(self):
        for px in (1e-5, 3e-4, 1e-3, 2.4e-3, 5e-3, 0.02, 0.2):
            fee = F.trade_fee_btc(px, TS)
            self.assertLessEqual(fee, 0.0003 + 1e-15)
            self.assertLessEqual(fee, 0.125 * px + 1e-15)

    def test_pre_2020_08_24_cap_is_0_0004(self):
        before = ms(2020, 8, 24) - 1                                              # 2020-08-23 23:59:59.999
        self.assertAlmostEqual(F.trade_fee_btc(0.0100, before), 0.0004, places=12)
        self.assertAlmostEqual(F.trade_fee_btc(0.0100, ms(2019, 1, 1)), 0.0004, places=12)
        self.assertAlmostEqual(F.trade_fee_btc(0.0100, ms(2020, 8, 24)), 0.0003, places=12)   # cutoff instant is NOT old
        self.assertAlmostEqual(F.trade_fee_btc(0.0100, ms(2020, 8, 24) + 1), 0.0003, places=12)
        self.assertAlmostEqual(F.trade_fee_btc(0.0010, before), 0.000125, places=12)          # premium fraction still applies


class DeliveryFee(unittest.TestCase):
    def test_friday_itm_large_payoff_hits_cap(self):
        self.assertAlmostEqual(F.delivery_fee_btc(4000.0 / 90000.0, FRI_EXP), 0.00015, places=12)

    def test_friday_itm_small_payoff_is_12_5_percent(self):
        pay = 100.0 / 86100.0                                                     # 0.0011614 -> 12.5% = 0.00014518 < cap
        self.assertAlmostEqual(F.delivery_fee_btc(pay, FRI_EXP), 0.125 * pay, places=14)
        self.assertLess(F.delivery_fee_btc(pay, FRI_EXP), 0.00015)

    def test_crossover_payoff_is_0_0012(self):
        self.assertAlmostEqual(F.delivery_fee_btc(0.0012, FRI_EXP), 0.00015, places=12)
        self.assertAlmostEqual(F.delivery_fee_btc(0.0011, FRI_EXP), 0.0001375, places=12)

    def test_friday_otm_is_free(self):
        self.assertEqual(F.delivery_fee_btc(0.0, FRI_EXP), 0.0)

    def test_only_friday_expiries_pay(self):
        pay = 0.05
        for day, expected in ((5, 0.0), (6, 0.0), (7, 0.0), (8, 0.0), (9, 0.00015), (10, 0.0), (11, 0.0)):   # Mon..Sun, Oct 2026
            self.assertAlmostEqual(F.delivery_fee_btc(pay, ms(2026, 10, day, 8)), expected, places=12, msg="2026-10-%02d" % day)

    def test_weekday_keyword(self):
        self.assertAlmostEqual(F.delivery_fee_btc(0.05, weekday=4), 0.00015, places=12)
        for wd in (0, 1, 2, 3, 5, 6):
            self.assertEqual(F.delivery_fee_btc(0.05, weekday=wd), 0.0)


class PerpFee(unittest.TestCase):
    def test_taker_fee_is_5_bps_of_notional(self):
        self.assertAlmostEqual(F.perp_fee_usd(100000.0), 50.0, places=9)
        self.assertAlmostEqual(F.perp_fee_usd(-100000.0), 50.0, places=9)         # sell side pays the same
        self.assertAlmostEqual(F.perp_fee_btc(100000.0, 80000.0), 50.0 / 80000.0, places=12)
        self.assertEqual(F.perp_fee_usd(0.0), 0.0)


if __name__ == "__main__":
    unittest.main()
