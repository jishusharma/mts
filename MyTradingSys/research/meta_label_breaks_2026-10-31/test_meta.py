"""meta.py: features use no bar after e (forcing test), the HTF last-closed rule, hand numbers for the CV blocks/purge,
the training-fold cut, the early-exit P&L, Holm/BH, and the logistic fit."""
import os
import sys
import unittest

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import meta as M  # noqa: E402


def bars(n, seed=0):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    o = np.r_[c[0], c[:-1]]
    v = rng.uniform(50, 150, n)
    return pd.DataFrame(dict(t=np.arange(n, dtype=np.int64) * 3600, o=o, h=np.maximum(o, c) * 1.002, l=np.minimum(o, c) * 0.998,
                             c=c, v=v, tbv=v * rng.uniform(0.3, 0.7, n)))


def fwd_shock(b, e):
    """the bars after e, changed on purpose (prices x1.5, volume x10)."""
    shocked = b.copy()
    shocked.loc[e + 1:, ['o', 'h', 'l', 'c']] *= 1.5
    shocked.loc[e + 1:, 'v'] *= 10
    return shocked


class FeaturesCausal(unittest.TestCase):
    def test_no_bar_after_e_changes_a_feature(self):
        b = bars(1600)
        e, i = 1400, 1394
        t_entry = int(b.t[e]) + 3600

        def feats(frame):
            h4 = M.htf_series(frame.iloc[::4].reset_index(drop=True))     # 4h bars stamped at their open
            dd = M.htf_series(frame.iloc[::24].reset_index(drop=True))
            s = M.series(frame)
            tv = dict(zip(s['t'].tolist(), s['v'].tolist()))
            return M.features_at(s, i, e, 1, 'H', 'low', 0.5, t_entry, h4, dd, tv)

        base = feats(b)
        after = feats(fwd_shock(b, e))
        for k in base:
            self.assertTrue(np.isclose(base[k], after[k], equal_nan=True), k)

    def test_htf_last_closed(self):
        htf = pd.DataFrame(dict(t=[0, 14400, 28800]))
        self.assertEqual(M.htf_last_closed(htf, 240, 14399), -1)   # first 4h bar not closed yet
        self.assertEqual(M.htf_last_closed(htf, 240, 14400), 0)
        self.assertEqual(M.htf_last_closed(htf, 240, 43199), 1)


class Hand(unittest.TestCase):
    def test_blocks_equal_time(self):
        self.assertEqual(M.blocks(None, 0, 60, 6)[1], (10.0, 20.0))

    def test_cut_from_training_fold(self):
        # training scores 0..8 -> 2/3 quantile 5.333; a test score of 5 is middle, 6 top
        s_tr = np.arange(9.0)
        c1, c2 = np.quantile(s_tr, [1 / 3, 2 / 3])
        self.assertAlmostEqual(c2, 16 / 3)
        self.assertAlmostEqual(c1, 8 / 3)

    def test_early_exit(self):
        # p1 -0.2 % -> exit there; p1 +0.1 % -> hold to +0.5 %; p1 0 -> exit (not in profit)
        g = np.array([0.004, 0.005, 0.003])
        pk = np.array([-0.002, 0.001, 0.0])
        self.assertTrue(np.allclose(M.early_gross(pk, g), [-0.002, 0.005, 0.0]))

    def test_holm_bh(self):
        p = [0.01, 0.04, 0.03]
        self.assertTrue(np.allclose(M.holm(p), [0.03, 0.06, 0.06]))
        self.assertTrue(np.allclose(M.bh(p), [0.03, 0.04, 0.04]))

    def test_logit_recovers_sign(self):
        rng = np.random.default_rng(3)
        X = rng.normal(size=(4000, 2))
        y = (rng.uniform(size=4000) < 1 / (1 + np.exp(-(1.5 * X[:, 0] - 1.0 * X[:, 1])))).astype(float)
        w = M.fit_logit(X, y, lam=0.0)
        self.assertAlmostEqual(w[1], 1.5, delta=0.15)
        self.assertAlmostEqual(w[2], -1.0, delta=0.15)

    def test_purge_drops_neighbours(self):
        # an event 3 days before a test block start is not used to train that block
        t = np.array([0, 10, 20]) * M.DAY
        lo, hi = 13 * M.DAY, 30 * M.DAY
        tr = (t < lo - M.PURGE) | (t >= hi + M.PURGE)
        self.assertEqual(tr.tolist(), [True, False, False])


class SimExport(unittest.TestCase):
    def test_overall_verdict_and_tables(self):
        import sim_export as X
        side = dict(n=10, net=0.01, lo=-0.1, hi=0.1)

        def cell(v):
            return dict(n_all=30, all=dict(net=-0.03), top=side, bottom=dict(net=-0.1), placebo_p=0.02, holm_p=0.06,
                        top_net_2022=0.1, top_net_2023=0.03, verdict=v)
        e = dict(hold_net=-0.03, early_net=-0.06, diff=-0.03, diff_lo=-0.07, diff_hi=0.01, winners_underwater=0.28,
                 losers_underwater=0.65, verdict='no difference')
        R = dict(rt_pct=0.1, meta={'15m': cell('FAIL'), '1h': cell('INCONCLUSIVE')}, early={'1h': {'k1': e}},
                 features={'1h': {'flow_e': dict(thirds=[dict(net=0.07, n=3), dict(net=0.0, n=3), dict(net=-0.1, n=3)])}})
        d = X.doc(R)
        self.assertEqual(d['verdict']['label'], 'INCONCLUSIVE')
        self.assertEqual([len(x.get('rows', [])) for x in d['examples']], [2, 1, 1, 0])
        self.assertTrue(all(w['label'] in ('SOURCED', 'OURS') for w in d['what']))
        R['meta']['1h']['verdict'] = 'FAIL'
        self.assertEqual(X.doc(R)['verdict']['label'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
