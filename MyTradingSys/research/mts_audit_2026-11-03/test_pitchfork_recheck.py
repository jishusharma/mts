"""Hand-worked cases for pitchfork_recheck.py (audit 2026-11-03)."""
import numpy as np

from pitchfork_recheck import causal_setups, final_setups, walk_1m


def _series():
    # Piecewise-linear path, no ties: low 95 at bar 4, high 110 at 10, low 100 at 16, a 2 % bounce to 102 at 19 (under the 3 % gate),
    # lower low 97 at 22 (replaces the low at 16), high 109 at 28, low 99 at 34.
    knots = [(0, 100.0), (4, 95.0), (10, 110.0), (16, 100.0), (19, 102.0), (22, 97.0), (28, 109.0), (34, 99.0), (44, 104.0)]
    path = list(np.interp(range(45), [k[0] for k in knots], [k[1] for k in knots]))
    return [p + 0.1 for p in path], [p - 0.1 for p in path]


def test_causal_list_keeps_a_triplet_the_final_list_erases():
    highs, lows = _series()
    final = {(s.p0.index, s.p1.index, s.p2.index) for s in final_setups(highs, lows)}
    causal = {(s.p0.index, s.p1.index, s.p2.index) for s in causal_setups(highs, lows)}
    # A long from the low at 16 was a real, knowable setup at bar 20. It failed: price made a lower low at 22.
    # The final list has rewritten that low to 22, so the losing setup is gone from the record.
    assert (4, 10, 22) in final
    assert (4, 10, 16) not in final
    assert (4, 10, 16) in causal
    assert final <= causal


def test_stop_wins_inside_one_minute():
    ts = np.array([0, 60_000], dtype=np.int64)
    hi = np.array([102.0, 102.0])
    lo = np.array([98.0, 98.0])
    cl = np.array([100.0, 100.0])
    r = walk_1m(ts, hi, lo, cl, 0, True, 100.0, 0.015, lambda _t: 101.0, 120_000)
    assert r == -0.015


def test_target_then_close_out():
    ts = np.array([0, 60_000], dtype=np.int64)
    hi = np.array([100.5, 101.2])
    lo = np.array([99.9, 100.0])
    cl = np.array([100.2, 101.0])
    assert abs(walk_1m(ts, hi, lo, cl, 0, True, 100.0, 0.015, lambda _t: 101.0, 120_000) - 0.01) < 1e-12
    assert abs(walk_1m(ts, hi, lo, cl, 0, True, 100.0, 0.015, lambda _t: 110.0, 120_000) - 0.01) < 1e-12
    # Short side: time exit at the last close (101), 1 % against.
    assert abs(walk_1m(ts, hi, lo, cl, 0, False, 100.0, 0.015, lambda _t: 90.0, 120_000) + 0.01) < 1e-12
