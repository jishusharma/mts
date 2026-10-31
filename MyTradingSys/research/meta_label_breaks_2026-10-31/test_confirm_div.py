"""confirm_div.py: the fresh window is enforced, the flag is PRD-with OR NRD-with, and the verdict follows PRE_REG_DIV.md."""
import os
import sys
import unittest

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import confirm_div as C  # noqa: E402


class Window(unittest.TestCase):
    def test_bar_in_2022_is_refused(self):
        ok = pd.Timestamp('2021-12-31 23:59', tz='UTC').timestamp()
        bad = pd.Timestamp('2022-01-01', tz='UTC').timestamp()
        C.check_window(np.array([ok], np.int64))
        with self.assertRaises(ValueError):
            C.check_window(np.array([ok, bad], np.int64))
        with self.assertRaises(ValueError):
            C.check_window(np.array([pd.Timestamp('2019-12-31', tz='UTC').timestamp()], np.int64))


class Flag(unittest.TestCase):
    def test_either_side(self):
        T = pd.DataFrame({C.FLAG[0]: [1.0, 0, 0], C.FLAG[1]: [0, 1.0, 0]})
        self.assertEqual(C.flagged(T).tolist(), [True, True, False])


class Verdict(unittest.TestCase):
    def test_pass_needs_1h_or_4h(self):
        cells = {'15m': dict(n=100, net=0.2, lo=0.1, p=0.001), '1h': dict(n=100, net=-0.1, lo=-0.3, p=0.8),
                 '4h': dict(n=20, net=0.5, lo=0.1, p=0.001)}
        self.assertEqual(C.verdicts(cells), 'INCONCLUSIVE')
        self.assertEqual(cells['15m']['verdict'], 'PASS')
        self.assertEqual(cells['4h']['verdict'], 'INCONCLUSIVE (too few)')

    def test_holm_applies(self):
        cells = {'15m': dict(n=50, net=0.1, lo=0.01, p=0.03), '1h': dict(n=50, net=0.1, lo=0.01, p=0.03),
                 '4h': dict(n=50, net=0.1, lo=0.01, p=0.03)}
        self.assertEqual(C.verdicts(cells), 'INCONCLUSIVE')  # 0.03 x 3 = 0.09 > 0.05

    def test_all_negative_is_fail(self):
        cells = {k: dict(n=50, net=-0.1, lo=-0.2, p=0.9) for k in ('15m', '1h', '4h')}
        self.assertEqual(C.verdicts(cells), 'FAIL')

    def test_boot_p(self):
        t = np.arange(40, dtype=np.int64) * 86400
        lo, hi, p = C.boot(np.full(40, 1.0), t)
        self.assertEqual(p, 0.0)
        self.assertGreater(lo, 0)


class SimExportDiv(unittest.TestCase):
    def test_tables_and_verdict(self):
        import sim_export_div as E
        text = '\n'.join([
            '## 1h (DEV trades 9; x)', '| exit | trades |', '|---|---|', '| fixed 4 bars | 9 | -0.1 | a | 50 | 0.9 | -0.2 | 4 |',
            'At entry (x)', '| divergence | role |', '|---|---|', '| RSI prd, lower TF | with | 5 % | 13 % | +0.121 | 65 | -0.062 |',
            '| RSI prd, lower TF | against | 2 % | 1 % | -0.230 | 34 | -0.049 |'])
        ex = dict(not_flag_net=-0.1, long_net=0.1, long_n=3, short_net=-0.5, short_n=2, y2020_net=0.2, y2020_n=2,
                  y2021_net=-0.3, y2021_n=3, all_net=-0.16)
        C = dict(card='FAIL', cells={'1h': dict(n=131, net=-0.18, lo=-0.4, hi=0.05, holm=1.0, verdict='FAIL')}, extra={'1h': ex})
        d = E.doc(text, C)
        self.assertEqual(d['verdict']['label'], 'FAIL')
        self.assertEqual([len(x.get('rows', [])) for x in d['examples']], [1, 1, 1, 1, 0])
        self.assertEqual(d['examples'][2]['rows'][0], ['1h', 'PRD (longs)', '65', '+0.121', '-0.062'])
        self.assertTrue(all(w['label'] in ('SOURCED', 'OURS') for w in d['what']))


if __name__ == '__main__':
    unittest.main()
