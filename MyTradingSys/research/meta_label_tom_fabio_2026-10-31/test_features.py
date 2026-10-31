"""Causality tests for features.py: no feature may use a bar that closes after the entry time (PRE_REG section 7).

Perturbation test: every 1m bar at or after the entry time t0 is replaced with garbage and every raw feature at t0 must be
bit-identical. Meta-test: the same check must CATCH the leaky rule (a bar counts once it has opened).
Run: python test_features.py        (set META_LEAK=1 to run the perturbation test against the leaky rule: it must fail)
"""
import os
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import features as F  # noqa: E402

LEAK = os.environ.get('META_LEAK') == '1'
DAY = 86400000


def synth(days=180, seed=3):
    rng = np.random.default_rng(seed)
    n = days * 1440
    t = (19000 * DAY // 60000 + np.arange(n)) * 60000      # starts at a UTC midnight, 1m grid
    t = (19000 * DAY) + np.arange(n) * 60000
    c = 20000 * np.exp(np.cumsum(rng.normal(0, 0.0007, n)))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.0004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.0004, n))
    v = rng.uniform(1, 50, n) * (1 + 3 * (rng.uniform(size=n) > 0.99))
    return np.column_stack([t, o, h, l, c, v])


def fund_for(a):
    ts = np.arange(a[0, 0], a[-1, 0] + 8 * 3600000, 8 * 3600000)
    rs = np.random.default_rng(5).choice([-0.0001, 0.0001, 0.0002], len(ts))
    return ts.astype(np.int64), rs


def garbage_after(a, t0):
    b = a.copy()
    m = b[:, 0] >= t0
    g = np.random.default_rng(9)
    b[m, 1:5] = g.uniform(1000, 90000, (m.sum(), 4))
    b[m, 2] = b[m, 1:5].max(axis=1)
    b[m, 3] = b[m, 1:5].min(axis=1)
    b[m, 5] = g.uniform(1e5, 1e6, m.sum())
    return b


def features_at(a, f, t0, leak=False):
    ctx = F.build_context(a, f)
    r = F.raw_features(ctx, np.array([t0], np.int64), leak=leak)
    return {k: float(v[0]) for k, v in r.items()}


def causal_violations(a, f, t0s, leak):
    """Names of features that change when bars at or after t0 are replaced by garbage."""
    bad = set()
    for t0 in t0s:
        base = features_at(a, f, t0, leak)
        pert = features_at(garbage_after(a, t0), f, t0, leak)
        for k in base:
            x, y = base[k], pert[k]
            if not ((x != x and y != y) or x == y):
                bad.add(k)
    return bad


A = synth()
FUND = fund_for(A)
# mid-hour, just after midnight, mid-week, on the hour, last minute before a week turns
T0S = [int(A[0, 0]) + x for x in (160 * DAY + 7 * 3600000 + 35 * 60000, 165 * DAY + 5 * 60000, 169 * DAY + 13 * 3600000,
                                  172 * DAY + 3 * 3600000 + 59 * 60000, 175 * DAY + 20 * 3600000 + 25 * 60000)]


class Causal(unittest.TestCase):
    def test_no_feature_uses_a_bar_closing_after_entry(self):
        bad = causal_violations(A, FUND, T0S, LEAK)
        self.assertEqual(bad, set(), f'features that read bars closing after entry: {sorted(bad)}')

    def test_features_exist_at_the_probe_times(self):
        r = features_at(A, FUND, T0S[-1])
        for k in F.NAMES:
            self.assertFalse(np.isnan(r[k]), f'{k} not available at the probe time (synthetic data too short?)')

    def test_check_catches_the_leaky_rule(self):
        bad = causal_violations(A, FUND, T0S, True)
        self.assertTrue(bad & {'bbwp', 'rsi', 'wt', 'relvol'}, f'leaky rule not detected, flagged only {sorted(bad)}')

    def test_last_closed_boundary(self):
        opens = np.array([0, 3600000, 7200000])
        self.assertEqual(int(F.last_closed(opens, 3600000, 3600000)), 0)       # bar 0 closes exactly at 1h
        self.assertEqual(int(F.last_closed(opens, 3600000, 3599999)), -1)
        self.assertEqual(int(F.last_closed(opens, 3600000, 7200000 + 59 * 60000)), 1)
        self.assertEqual(int(F.last_closed(opens, 3600000, 7200000 + 59 * 60000, leak=True)), 2)

    def test_funding_settlement_at_entry_is_known_but_later_is_not(self):
        ctx = {'f_t': np.array([100, 200], np.int64), 'f_r': np.array([0.001, -0.001]),
               't1': np.array([0]), 'bbwp': np.array([1.0]), 'rsi': np.array([1.0]), 'wt': np.array([1.0]), 'relvol': np.array([1.0]),
               'td': np.array([0]), 'dclose': np.array([1.0]), 'sma50': np.array([1.0]), 'top': np.array([1.0]), 'bottom': np.array([1.0])}
        r = F.raw_features(ctx, np.array([199, 200], np.int64))
        self.assertEqual(r['fund'].tolist(), [1.0, -1.0])


if __name__ == '__main__':
    unittest.main()
