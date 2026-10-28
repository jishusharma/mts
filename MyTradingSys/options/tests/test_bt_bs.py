"""Tests for bs.py (Black-76, r=0, F=index; BT_SPEC "Conventions"). Expected values: textbook constants and an inline
erf-based re-derivation, never the implementation under test."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bt_testutil as U  # noqa: E402

import bs as BS  # noqa: E402


def _n(x):
    """Standard normal CDF via erf, inline on purpose (independent of the implementation and of bt_testutil)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _hand_b76_usd(F, K, iv_pct, T, is_call):
    s = iv_pct / 100.0
    d1 = (math.log(F / K) + 0.5 * s * s * T) / (s * math.sqrt(T))
    d2 = d1 - s * math.sqrt(T)
    return F * _n(d1) - K * _n(d2) if is_call else K * _n(-d2) - F * _n(-d1)


# adapters: the only lines that know the implementation's names
# (API.md: bs.price_usd(F, K, T, iv_pct, is_call); tests below keep the (F, K, iv, T, call) order of the hand formulas)
def price_usd(F, K, iv_pct, T, is_call):
    return BS.price_usd(F, K, T, iv_pct, is_call)


def price_btc(F, K, iv_pct, T, is_call):
    return BS.price_btc(F, K, T, iv_pct, is_call)


def delta(F, K, iv_pct, T, is_call):
    return BS.delta(F, K, T, iv_pct, is_call)


class Textbook(unittest.TestCase):
    def test_hand_calc_matches_known_constants(self):
        # S=K=100, sigma=0.2, T=1, r=0: d1=0.1, call=put=100*erf(0.1/sqrt2)=7.9655674554 ; N(0.1)=0.539828
        self.assertAlmostEqual(_hand_b76_usd(100, 100, 20, 1, True), 7.9655674554, places=9)
        self.assertAlmostEqual(_hand_b76_usd(100, 100, 20, 1, False), 7.9655674554, places=9)
        self.assertAlmostEqual(_n(0.1), 0.539828, places=6)

    def test_atm_call_and_put_prices(self):
        self.assertAlmostEqual(price_usd(100, 100, 20, 1, True), 7.9655674554, places=8)
        self.assertAlmostEqual(price_usd(100, 100, 20, 1, False), 7.9655674554, places=8)

    def test_atm_deltas(self):
        self.assertAlmostEqual(delta(100, 100, 20, 1, True), 0.539828, places=6)
        self.assertAlmostEqual(delta(100, 100, 20, 1, False), 0.539828 - 1.0, places=6)

    def test_btc_price_is_usd_price_over_forward(self):
        F, K, iv, T = 80000.0, 80000.0, 50.0, 40.0 / 8760.0          # T = 40 hours in years of 365 days
        self.assertAlmostEqual(price_btc(F, K, iv, T, True), 0.01347837, places=8)     # independent calc: 1078.2696 / 80000
        self.assertAlmostEqual(price_btc(F, K, iv, T, False), 0.01347837, places=8)
        self.assertAlmostEqual(price_btc(F, K, iv, T, True), _hand_b76_usd(F, K, iv, T, True) / F, places=12)

    def test_otm_and_itm_btc_scale_cases(self):
        F, iv, T = 80000.0, 50.0, 40.0 / 8760.0
        self.assertAlmostEqual(price_btc(F, 82000.0, iv, T, True), 0.00463687, places=8)    # 370.9495 / 80000
        self.assertAlmostEqual(price_btc(F, 78000.0, iv, T, False), 0.00438061, places=8)   # 350.4491 / 80000
        self.assertAlmostEqual(price_btc(F, 78000.0, iv, T, True), 0.02938061, places=8)    # ITM call
        self.assertAlmostEqual(delta(F, 82000.0, iv, T, True), 0.237632, places=6)
        self.assertAlmostEqual(delta(F, 78000.0, iv, T, False), -0.221769, places=6)
        self.assertAlmostEqual(delta(F, 80000.0, iv, T, True), 0.506739, places=6)

    def test_put_call_parity_in_usd_with_r_zero(self):
        for F, K, iv, T in ((80000, 82000, 50, 40 / 8760), (80000, 70000, 65, 0.25), (100, 90, 30, 2.0), (100, 120, 80, 0.01)):
            c, p = price_usd(F, K, iv, T, True), price_usd(F, K, iv, T, False)
            self.assertAlmostEqual(c - p, F - K, places=6, msg=(F, K, iv, T))

    def test_delta_call_minus_delta_put_is_one_and_bounded(self):
        for K in (60000, 75000, 80000, 85000, 120000):
            dc, dp = delta(80000, K, 55, 0.1, True), delta(80000, K, 55, 0.1, False)
            self.assertAlmostEqual(dc - dp, 1.0, places=12)
            self.assertTrue(0.0 <= dc <= 1.0 and -1.0 <= dp <= 0.0)

    def test_matches_independent_formula_on_a_grid(self):
        for F in (50000.0, 80000.0):
            for K in (0.8 * F, F, 1.2 * F):
                for iv in (30.0, 60.0, 120.0):
                    for T in (1 / 365, 7 / 365, 0.5):
                        for call in (True, False):
                            self.assertAlmostEqual(price_usd(F, K, iv, T, call), _hand_b76_usd(F, K, iv, T, call),
                                                   places=6, msg=(F, K, iv, T, call))
                            self.assertAlmostEqual(price_btc(F, K, iv, T, call), _hand_b76_usd(F, K, iv, T, call) / F,
                                                   places=12, msg=(F, K, iv, T, call))

    def test_monotone_in_vol_and_time(self):
        a = price_btc(80000, 82000, 40, 0.02, True)
        b = price_btc(80000, 82000, 60, 0.02, True)
        c = price_btc(80000, 82000, 60, 0.05, True)
        self.assertLess(a, b)
        self.assertLess(b, c)


class Payoff(unittest.TestCase):
    """Inverse option settlement payoff per contract in BTC: call max(0,S-K)/S ; put max(0,K-S)/S."""

    def test_call_itm_otm_atm(self):
        self.assertAlmostEqual(BS.payoff_btc(True, 86000.0, 90000.0), 4000.0 / 90000.0, places=12)   # 0.0444444
        self.assertEqual(BS.payoff_btc(True, 86000.0, 80000.0), 0.0)
        self.assertEqual(BS.payoff_btc(True, 86000.0, 86000.0), 0.0)

    def test_put_itm_otm_atm(self):
        self.assertAlmostEqual(BS.payoff_btc(False, 86000.0, 80000.0), 6000.0 / 80000.0, places=12)  # 0.075
        self.assertEqual(BS.payoff_btc(False, 86000.0, 90000.0), 0.0)
        self.assertEqual(BS.payoff_btc(False, 86000.0, 86000.0), 0.0)

    def test_payoff_in_btc_is_usd_payoff_over_settlement_price(self):
        for S in (50000.0, 79999.0, 120000.0):
            self.assertAlmostEqual(BS.payoff_btc(True, 80000.0, S), max(0.0, S - 80000.0) / S, places=14)
            self.assertAlmostEqual(BS.payoff_btc(False, 80000.0, S), max(0.0, 80000.0 - S) / S, places=14)

    def test_put_payoff_is_bounded_by_strike_over_settlement(self):
        # a put cannot pay more than K/S BTC; a call cannot pay 1 BTC or more (S-K < S for K > 0)
        self.assertLess(BS.payoff_btc(True, 1.0, 1e6), 1.0)
        self.assertAlmostEqual(BS.payoff_btc(False, 80000.0, 1.0), 79999.0, places=6)


class Time(unittest.TestCase):
    def test_years_to_expiry_uses_365_day_years(self):
        t0, t1 = U.ms(2026, 10, 7, 16), U.ms(2026, 10, 9, 8)                                         # 40 hours
        self.assertAlmostEqual(BS.years_to_expiry(t0, t1), 40.0 / 8760.0, places=14)
        self.assertAlmostEqual(BS.years_to_expiry(U.ms(2026, 1, 1), U.ms(2027, 1, 1)), 1.0, places=14)   # 365 d exactly
        self.assertEqual(BS.years_to_expiry(t1, t0), 0.0)                                           # past expiry floors at 0


class Degenerate(unittest.TestCase):
    def test_expired_option_is_intrinsic(self):
        self.assertAlmostEqual(price_usd(82000.0, 80000.0, 50.0, 0.0, True), 2000.0, places=9)
        self.assertAlmostEqual(price_usd(78000.0, 80000.0, 50.0, 0.0, False), 2000.0, places=9)
        self.assertEqual(price_usd(78000.0, 80000.0, 50.0, 0.0, True), 0.0)


if __name__ == "__main__":
    unittest.main()
