"""Tests for level_approach.py. Hand-built bar series, level 100, eps 0.1 % (arm line 99.9), k = 3 confirm closes.

Each series starts below the arm line (armed). Bars are (high, close); open is not used by the classifier.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import level_approach as la  # noqa: E402


def run(hc, level=100.0):
    h = np.array([x[0] for x in hc], float)
    c = np.array([x[1] for x in hc], float)
    return la.classify_approaches(h, c, np.full(len(h), level))


def test_near_miss():
    ev = run([(98, 97), (99.95, 99.5), (99, 98), (98, 97), (97, 96), (96, 95)])
    assert [(e.idx, e.cls) for e in ev] == [(1, "near_miss")]


def test_wick_back():
    ev = run([(98, 97), (100.5, 99.5), (99, 98), (98, 97)])
    assert [(e.idx, e.cls) for e in ev] == [(1, "wick_back")]


def test_close_then_fail_second_close():
    # bar 1 closes through, bar 2 holds above, bar 3 closes back below -> fail at the 2nd close after the through-close
    ev = run([(98, 97), (101.2, 101), (102, 101.5), (101, 99.5), (99, 98), (98, 97)])
    assert [(e.idx, e.cls, e.n_close) for e in ev] == [(1, "close_then_fail", 2)]


def test_close_then_fail_first_close():
    ev = run([(98, 97), (101.2, 101), (101, 99.5), (99, 98), (98, 97), (97, 96)])
    assert [(e.idx, e.cls, e.n_close) for e in ev] == [(1, "close_then_fail", 1)]


def test_accepted():
    ev = run([(98, 97), (101.2, 101), (102, 101.5), (103, 102), (104, 103), (103, 102)])
    assert [(e.idx, e.cls) for e in ev] == [(1, "accepted")]


def test_no_event_when_day_opens_above_and_rearm_needs_close_below():
    # starts above the line: not armed, nothing counted; after a close below the arm line it re-arms
    ev = run([(102, 101), (103, 102), (99, 98), (99.95, 99.5), (99, 98), (98, 97), (97, 96)])
    assert [(e.idx, e.cls) for e in ev] == [(3, "near_miss")]


def test_unresolved_through_close_dropped():
    # through-close at the very end: no k forward closes -> no event (never guess)
    ev = run([(98, 97), (101.2, 101), (102, 101.5)])
    assert ev == []


def test_levels_last_lower_high_and_prior_day_high():
    # daily highs / lows; lower low at day 11 (low 50 < min of the 10 days before); last lower high = max high day 11..i-1
    H = [100] * 11 + [90, 95, 92, 80]
    L = [60] * 11 + [50, 55, 54, 50]
    pdh, lh = la.daily_levels(np.array(H, float), np.array(L, float), lb=10)
    # day 14: pdh = H[13] = 92 ; latest lower low day <= 13 is day 11 (50 < 60); lh = max(H[11..13]) = 95
    assert pdh[14] == 92 and lh[14] == 95
    # day 12: pdh = H[11] = 90 ; ll day 11 -> lh = max(H[11..11]) = 90 == pdh -> nan (duplicate of prior-day high)
    assert pdh[12] == 90 and np.isnan(lh[12])