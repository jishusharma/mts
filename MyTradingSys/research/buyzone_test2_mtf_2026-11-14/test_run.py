"""Placebo fast path must equal the reference simulator (lib.simulate with fixed hold). Mechanics only, no aggregation."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402
import run  # noqa: E402


def test_fast_candidate_matches_reference():
    co = lib.Coin("ETH")
    cd = run.candidates(co)
    rng = np.random.default_rng(0)
    for side in (1, -1):
        d = cd[side]
        for i in rng.integers(0, len(d["t"]), 40):
            j = int(np.searchsorted(co.t, d["t"][i])) - 1
            for h in (1, 7, 60):
                ref = lib.simulate(co, j, side, hold=h)
                fast = d["stopR"][i] if d["stop_off"][i] < h else d["openR"][i, h]
                assert abs(ref["gross_R"] - fast) < 1e-4, (side, i, h)
