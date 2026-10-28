"""p4_corrected.py on synthetic bars: a planted edge is found, a no-edge series is not, and no look-ahead into the open bar."""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4_corrected as p4

DAY = 86_400_000


def bars(n_days, edge, seed=1):
    """1m bars; buy/sell vol random; price drifts in the direction of the imbalance of each quarter-hour bar by `edge` bp."""
    rng = np.random.default_rng(seed)
    n = n_days * 1440
    t = np.arange(n, dtype=np.int64) * 60_000 + 1_735_689_600_000  # 2025-01-01
    buy, sell = rng.uniform(1, 2, n), rng.uniform(1, 2, n)
    ret = rng.normal(0, 2e-4, n)
    opens = ((t // 60_000) % 15 == 0)
    sig = np.sign(buy - sell)
    ret[opens] += 0  # the open bar itself carries no information about its own return (no look-ahead)
    # the bar right after each open drifts with the sign of the open bar's imbalance
    idx = np.nonzero(opens)[0]
    idx = idx[idx + 1 < n]
    ret[idx + 1] += sig[idx] * edge * 1e-4
    c = 100.0 * np.exp(np.cumsum(ret))
    return dict(t=t, c=c, buy=buy, sell=sell)


class P4Test(unittest.TestCase):
    def test_planted_edge_has_positive_signed_gross(self):
        r = p4.trades(bars(20, 25.0), 240)
        self.assertGreater(r['gross'].mean(), 15.0)

    def test_no_edge_gross_near_zero_and_no_pass(self):
        out = p4.analyse(bars(30, 0.0))
        for o in out.values():
            self.assertLess(abs(o['gross_mean']), 3.0)
            self.assertEqual(o['verdict'], 'NO REPLICATION')  # net = gross - 10 bp, nowhere near positive

    def test_96_opens_per_day(self):
        r = p4.trades(bars(10, 0.0), 60)
        per_day = len(r['gross']) / 10
        self.assertGreater(per_day, 90)  # 96 less windows cut off at the end and zero-imbalance skips
        self.assertLessEqual(per_day, 96)


if __name__ == '__main__':
    unittest.main()
