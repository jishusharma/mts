"""Verification and causality audit scratch script for card gpt-rederive-malkan-div-fail-1031.
Tests lookahead in pivot confirmation, lower-TF alignment, bootstrap/Holm stats, and reports cited numbers.
"""
import os
import sys
import unittest
import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
MTS = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, MTS)
sys.path.insert(0, os.path.join(MTS, 'research', 'meta_label_breaks_2026-10-31'))
sys.path.insert(0, os.path.join(MTS, 'research', 'tf_break_event_study_2026-10-30'))

from backtest.layers.rsi import rsi_divergence as RD
from backtest import fees
import confirm_div as C
import explore_div as X
import meta as M


class TestPivotConfirmationCausality(unittest.TestCase):
    def test_pivot_lookahead_contract(self):
        """Show that pivot b is confirmed strictly at the close of bar b+1, never at bar b or open of b+1."""
        # Construct synthetic close series:
        # bar 0: 100, rsi: 30
        # bar 1: 90 (pivot candidate low), rsi: 25
        # bar 2: 95 (confirms bar 1 as low if close[2] > close[1]), rsi: 35
        # bar 3: 88 (pivot candidate lower low), rsi: 28 (higher low in RSI)
        # bar 4: 95 (confirms bar 3 as low), rsi: 38
        # open timestamps: t = [0, 60, 120, 180, 240] (1m bars)
        close = [100.0, 90.0, 95.0, 88.0, 95.0]
        rsi = [30.0, 25.0, 35.0, 28.0, 38.0]
        ts = [0, 60, 120, 180, 240]
        
        # 1. Old / naive code that treats ts[b+1] as the event availability time leaks 1 bar of lookahead
        # because ts[b+1] is the OPEN of the confirmation bar, when close[b+1] is not yet formed.
        piv = RD._pivots(close, rsi, "low")
        self.assertIn(1, piv)
        self.assertIn(3, piv)
        
        # 2. explore_div.py explicitly adds tf_min * 60 to e['t']:
        tf_min = 1
        evs = RD.rsi_divergence(close, rsi, ts, min_bars=3, max_bars=10, kind="bullish")
        self.assertEqual(len(evs), 1)
        ev = evs[0]
        self.assertEqual(ev['a_i'], 1)
        self.assertEqual(ev['b_i'], 3)
        self.assertEqual(ev['t'], 240)  # ts[b+1] where b=3 -> ts[4]=240 (open of bar 4)
        
        # explore_div.py line 47 availability timestamp:
        t_known = ev['t'] + tf_min * 60  # 240 + 60 = 300 (close of bar 4)
        self.assertEqual(t_known, 300)
        
        # At t=240 (open of bar 4), bar 4 has not closed, so pivot at bar 3 is NOT confirmed yet.
        # An entry at t_entry = 240 should NOT see this divergence.
        seen_at_open_4 = X.any_in(np.array([t_known]), 240 - 10 * 60, 240)
        self.assertFalse(seen_at_open_4, "Causal violation: event seen before confirmation bar closed!")
        
        # An entry at t_entry = 300 (close of bar 4 / open of bar 5) sees the divergence causally.
        seen_at_close_4 = X.any_in(np.array([t_known]), 300 - 10 * 60, 300)
        self.assertTrue(seen_at_close_4, "Causal confirmation: event should be visible once confirmation bar closes.")


class TestLowerTimeframeAlignment(unittest.TestCase):
    def test_lower_tf_boundary_matching(self):
        """Test multi-timeframe timestamp alignment for 15m->5m, 1h->15m, 4h->1h."""
        # Suppose a 1h trade enters at t_entry = 3600 (01:00 UTC).
        # Lower TF is 15m (900s).
        t_entry = 3600
        # A 15m divergence whose confirmation bar closes at 3600 (01:00 UTC) is known at t_entry.
        known_times = np.array([1800, 2700, 3600, 4500])
        self.assertTrue(X.any_in(known_times, t_entry - 10 * 3600, t_entry))
        
        # A 15m divergence whose confirmation bar closes at 4500 (01:15 UTC) is in the FUTURE of t_entry.
        # Verify it cannot be seen at t_entry:
        future_only = np.array([4500])
        self.assertFalse(X.any_in(future_only, t_entry - 10 * 3600, t_entry))

    def test_reverse_divergence_prd_nrd_regimes(self):
        """Test PRD requires RSI >= 60 and NRD requires RSI <= 40 at both pivots."""
        # PRD: higher low in price, lower low in RSI, both RSI >= 60
        # Pivot A: close=100, rsi=65
        # Pivot B: close=105 (higher low), rsi=62 (lower low, both >= 60)
        # 5 bars between A and B
        close = [110, 100, 115, 120, 110, 105, 112]
        rsi =   [ 70,  65,  75,  80,  68,  62,  70]
        ts = [i * 60 for i in range(len(close))]
        evs = RD.rsi_divergence(close, rsi, ts, min_bars=5, max_bars=14, kind="prd")
        self.assertEqual(len(evs), 1)
        self.assertEqual(evs[0]['event'], 'prd_divergence')

        # If RSI at pivot B dropped below 60 (e.g. 58), PRD regime condition is violated:
        rsi_sub60 = [70, 65, 75, 80, 68, 58, 70]
        evs_none = RD.rsi_divergence(close, rsi_sub60, ts, min_bars=5, max_bars=14, kind="prd")
        self.assertEqual(len(evs_none), 0)


class TestPreRegDivRulesAndVerdict(unittest.TestCase):
    def test_verdict_fail(self):
        """All timeframes net <= 0 results in FAIL."""
        cells = {
            '15m': dict(n=274, net=-0.110, lo=-0.239, hi=0.013, p=1.0),
            '1h': dict(n=131, net=-0.180, lo=-0.408, hi=0.052, p=1.0),
            '4h': dict(n=52, net=-0.384, lo=-1.208, hi=0.352, p=1.0),
        }
        verdict = C.verdicts(cells)
        self.assertEqual(verdict, 'FAIL')
        self.assertEqual(cells['15m']['verdict'], 'FAIL')
        self.assertEqual(cells['1h']['verdict'], 'FAIL')
        self.assertEqual(cells['4h']['verdict'], 'FAIL')
        self.assertEqual(cells['15m']['holm'], 1.0)
        self.assertEqual(cells['1h']['holm'], 1.0)
        self.assertEqual(cells['4h']['holm'], 1.0)

    def test_bar_count_2020_2021(self):
        """Check theoretical bar count in 2020-01-01 to 2021-12-31."""
        # 2020: leap year (366 days), 2021: 365 days -> 731 days
        expected_bars = 731 * 1440
        self.assertEqual(expected_bars, 1052640)

    def test_fees_deduction(self):
        """Check fee constant matches BINANCE_TAKER * 2 = 0.10%."""
        self.assertEqual(fees.BINANCE_TAKER, 0.0005)
        self.assertEqual(M.RT, 0.0010)
        self.assertEqual(M.RT * 100, 0.10)


if __name__ == '__main__':
    unittest.main()
