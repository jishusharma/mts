"""Core checks for the layers study: BH step-up, closed-data lookups, fwd_exit stop/target arithmetic."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "backtest")))
import rsi_grid_lib as L  # noqa: E402
from study import bh, last_idx  # noqa: E402


def test_bh_stepup():
    # m=4, q=0.10: thresholds .025 .05 .075 .10; p sorted .01 .04 .30 .9 -> first two rejected
    m = bh([0.9, 0.01, 0.30, 0.04])
    assert m.tolist() == [False, True, False, True]
    assert not bh([np.nan, 0.5]).any()


def test_last_idx_uses_only_closed():
    t = np.array([10, 20, 30])
    assert last_idx(t, 20) == 1 and last_idx(t, 19) == 0 and last_idx(t, 5) == -1


def test_fwd_exit_stop_and_target():
    entry = np.array([100.0, 100.0])
    stop = np.array([98.0, 98.0])  # R = 2
    n = 168
    O = np.full((2, n), 100.0); H = np.full((2, n), 101.0); Lo = np.full((2, n), 99.0); C = np.full((2, n), 100.0)
    H[0, 3] = 102.5            # +1R (102) hit on bar 3, stop never touched
    Lo[1, 2] = 97.0; O[1, 2] = 99.0  # stop hit on bar 2, fills at stop 98
    r = L.fwd_exit(entry, stop, O, H, Lo, C, np.zeros_like(O), "tgt", 1.0, 0.0)
    assert abs(r["net_r"][0] - 1.0) < 1e-9 and abs(r["net_r"][1] + 1.0) < 1e-9
