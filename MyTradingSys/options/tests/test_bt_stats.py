"""Tests for stats.py (BT_SPEC "stats.py"): summarize, equity/drawdown, seeded bootstrap, period split and pbo_cscv.
All expected numbers are hand-derived (binary fractions so float arithmetic is exact) or computed here independently."""
import itertools
import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bt_testutil as U  # noqa: E402
from bt_testutil import DAY, ms  # noqa: E402

import stats as ST  # noqa: E402


def trade(exit_ts, pnl, spot_exit=80000.0, spot_entry=80000.0, entry_ts=None):
    return {"entry_ts": exit_ts - 2 * DAY if entry_ts is None else entry_ts, "exit_ts": exit_ts, "legs": [],
            "pnl_btc": pnl, "spot_entry": spot_entry, "spot_exit": spot_exit}


PNL4 = [0.125, -0.25, 0.0625, -0.125]          # exact binary fractions
T4 = [trade(ms(2026, 1, 5 + 7 * i, 8), p) for i, p in enumerate(PNL4)]


class PboCscv(unittest.TestCase):
    def test_config_best_in_every_slice_has_zero_pbo(self):
        rnd = random.Random(11)
        n_cfg, n_per = 5, 16
        m = [[rnd.uniform(-0.3, 0.3) for _ in range(n_per)] for _ in range(n_cfg)]
        m[2] = [1.0 + 0.01 * (j % 3) for j in range(n_per)]          # config 2 beats every config in every period
        self.assertEqual(ST.pbo_cscv(m, n_slices=8), 0.0)
        self.assertEqual(ST.pbo_cscv(m, n_slices=4), 0.0)
        self.assertEqual(ST.pbo_cscv(m), 0.0)                        # default n_slices (8)

    def test_in_sample_winner_is_always_out_of_sample_loser_gives_pbo_one(self):
        v = [-4, -2, -4, -6, 4, 3, 8, 1]       # sums to 0 and no 4-subset sums to 0 (no ties in any IS/OOS split)
        self.assertEqual(sum(v), 0)
        self.assertTrue(all(sum(v[i] for i in c) != 0 for c in itertools.combinations(range(8), 4)))
        m = [[float(x) for x in v], [float(-x) for x in v]]          # B = -A: whoever wins IS loses OOS
        self.assertAlmostEqual(ST.pbo_cscv(m, n_slices=8), 1.0, places=12)

    def test_pure_noise_is_bounded(self):
        for seed in (1, 2, 3):
            rnd = random.Random(seed)
            m = [[rnd.gauss(0, 1) for _ in range(32)] for _ in range(6)]
            p = ST.pbo_cscv(m, n_slices=8)
            self.assertGreaterEqual(p, 0.0)
            self.assertLessEqual(p, 1.0)

    def test_deterministic(self):
        rnd = random.Random(5)
        m = [[rnd.gauss(0, 1) for _ in range(24)] for _ in range(4)]
        self.assertEqual(ST.pbo_cscv(m, n_slices=8), ST.pbo_cscv(m, n_slices=8))


if __name__ == "__main__":
    unittest.main()
