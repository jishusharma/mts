import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paired_inference as pi  # noqa: E402


def test_day_contrasts_hand():
    ev = [2, 4, 5, 1, 4, 9]
    ed = [1, 1, 2, 3, 4, 5]
    cv = [1, 1, 2, 4, 3, 5]
    cd = [1, 1, 2, 3, 4, 6]
    # day1 3-1=2 ; day2 5-mean(2)... c day2 = 2 -> 3 ; day3 1-4=-3 ; day4 4-3=1 ; day5 event only, day6 control only
    days, d, dropped = pi.day_contrasts(ev, ed, cv, cd)
    assert list(days) == [1, 2, 3, 4]
    assert np.allclose(d, [2, 3, -3, 1])
    assert dropped == 2


def test_signflip_p_hand_computed():
    # contrasts +2,+2,-2,+2: mean 1; |sum|>=4 in 1+4+4+1=10 of 16 sign patterns -> p = 0.625
    ev = [3, 5, 1, 4]
    ed = [1, 2, 3, 4]
    cv = [1, 3, 3, 2]
    r = pi.paired_day_inference(ev, ed, cv, ed, seed=3)
    assert r["n_days"] == 4 and r["dropped_days"] == 0
    assert abs(r["contrast"] - 1.0) < 1e-12
    assert abs(r["p_two_sided"] - 0.625) < 1e-12


def test_within_day_clustering_not_pseudoreplicated():
    ev = [10] * 100 + [0]
    ed = [1] * 100 + [2]
    r = pi.paired_day_inference(ev, ed, [0, 0], [1, 2])
    assert abs(r["contrast"] - 5.0) < 1e-12


def test_ci_deterministic_and_degenerate():
    ed = [1, 2, 3, 4]
    a = pi.paired_day_inference([3, 3, 3, 3], ed, [1, 1, 1, 1], ed, seed=7)
    b = pi.paired_day_inference([3, 3, 3, 3], ed, [1, 1, 1, 1], ed, seed=7)
    assert a == b and a["ci"] == (2.0, 2.0)


def test_no_common_days():
    r = pi.paired_day_inference([1], [1], [1], [2])
    assert r["n_days"] == 0 and r["dropped_days"] == 2
