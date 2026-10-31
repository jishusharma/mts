"""Tests for the meta-label machinery and the two exported sim-desk results (PRE_REG section 7 and the operator's simple-view add-on).

test_export_has_exactly_the_three_parts and test_table_counts_sum_to_filled_trades check the committed results/desk-meta_label_*.json.
Run: python test_meta_label.py
"""
import json
import re
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402

RESULTS = HERE.parent / 'sim_desk' / 'results'
IDS = ['desk-meta_label_tom_vp', 'desk-meta_label_fabio_c']
LINE = re.compile(r'^Best third by filter: [+-]\d+\.\d{3} R \(range [+-]\d+\.\d{3}\.\.[+-]\d+\.\d{3}\) vs random third: [+-]\d+\.\d{3} R -> (PASSED|FAILED|NOT ENOUGH DATA)$')


def doc(i):
    return json.loads((RESULTS / f'{i}.json').read_text(encoding='utf-8'))


class Machinery(unittest.TestCase):
    def test_planted_signal_is_found_and_null_is_not(self):
        rng = np.random.default_rng(1)
        n = 1500
        X = rng.normal(size=(n, 4))
        week = np.arange(n) // 10
        folds = A.folds_of(week)
        y_sig = (X[:, 0] + 0.3 * rng.normal(size=n) > 0).astype(float)
        net = np.where(y_sig > 0, 1.0, -1.0)
        tc = A.terciles(A.oof_scores(X, y_sig, folds))
        self.assertGreater(A.spread_of(net, tc), 1.5)
        y_null = (rng.normal(size=n) > 0).astype(float)
        tc0 = A.terciles(A.oof_scores(X, y_null, folds))
        self.assertLess(abs(A.spread_of(np.where(y_null > 0, 1.0, -1.0), tc0)), 0.4)

    def test_folds_purge_one_week_each_side_and_cover_every_trade_once(self):
        week = np.repeat(np.arange(60), 3)
        folds = A.folds_of(week)
        tests = np.zeros(len(week), int)
        for test, train in folds:
            tests += test
            lo, hi = week[test].min(), week[test].max()
            self.assertFalse((train & (week >= lo - 1) & (week <= hi + 1)).any())
            self.assertFalse((train & test).any())
        self.assertTrue((tests == 1).all())

    def test_terciles_are_equal_thirds(self):
        tc = A.terciles(np.random.default_rng(2).normal(size=99))
        self.assertEqual([int((tc == k).sum()) for k in range(3)], [33, 33, 33])

    def test_holm_and_bh(self):
        self.assertEqual([round(x, 6) for x in A.holm([0.01, 0.04, 0.03])], [0.03, 0.06, 0.06])
        self.assertEqual([round(x, 6) for x in A.bh([0.01, 0.04, 0.03])], [0.03, 0.04, 0.04])

    def test_tercile_cuts_come_from_training_fold_only(self):
        rng = np.random.default_rng(4)
        X = rng.normal(size=(600, 3))
        y = (X[:, 0] > 0).astype(float)
        week = np.arange(600) // 6
        folds = A.folds_of(week)
        s1, b1 = A.oof_buckets(X, y, folds)
        X2 = X.copy()
        test = folds[0][0]
        X2[test] += 5.0                      # shift the test block: its own score distribution must not move the cut points
        s2, b2 = A.oof_buckets(X2, y, folds)
        self.assertGreater((b2[test] == 2).mean(), 0.5)          # with cuts from training, a shifted block lands mostly in one bucket
        self.assertEqual(sorted(set(b1.tolist())), [0, 1, 2])

    def test_power_formula(self):
        self.assertAlmostEqual(A.power(1.0, 785), 0.1, places=3)       # n = 7.849 (sd/delta)^2


class Export(unittest.TestCase):
    def test_export_has_exactly_the_three_parts(self):
        for i in IDS:
            d = doc(i)
            self.assertEqual(d['kind'], 'backtest')
            kinds = [e['kind'] for e in d['examples']]
            self.assertEqual(kinds, ['table', 'charts'], i)                       # table + winner/loser charts, nothing else
            self.assertEqual(d['examples'][0]['cols'], ['Layer reading', 'trades', 'win %', 'average R after fees'])
            self.assertEqual(len(d['why']), 1)
            self.assertRegex(d['why'][0], LINE)                                  # the one verdict line
            self.assertEqual(d['why'][0].rsplit('-> ', 1)[1], d['verdict']['label'])
            items = d['examples'][1]['items']
            self.assertTrue(items)
            self.assertTrue(all(it['kind'] in ('winner', 'loser') for it in items))
            self.assertTrue(any(it['note'].startswith('Best third by filter') for it in items))
            self.assertTrue(any(it['note'].startswith('Worst third by filter') for it in items))
            self.assertEqual([k['label'] for k in d['kpis']], ['filled trades'])

    def test_table_counts_sum_to_filled_trades(self):
        for i in IDS:
            d = doc(i)
            n = int(d['kpis'][0]['value'])
            by = {}
            for label, cnt, win, avg in d['examples'][0]['rows']:
                by.setdefault(label.split(': ')[0], []).append(int(cnt))
                self.assertTrue(0 <= float(win) <= 100)
            self.assertEqual(len(by), 8, 'one group of rows per layer feature')
            for feat, counts in by.items():
                self.assertEqual(sum(counts), n, f'{i}: {feat} rows sum to {sum(counts)}, filled trades {n}')

    def test_catalogue_has_the_two_rows(self):
        cat = json.loads((RESULTS / '_catalogue.json').read_text(encoding='utf-8'))
        ids = {r['id'] for r in cat['rows']}
        self.assertTrue(set(IDS) <= ids)
        self.assertEqual(cat['count'], len(cat['rows']))


if __name__ == '__main__':
    unittest.main()
