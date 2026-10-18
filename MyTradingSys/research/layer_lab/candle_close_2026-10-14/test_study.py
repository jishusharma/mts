import os
import subprocess
import sys
import unittest
import numpy as np
# CI image has no pandas. Skip the class, not the module: a module-level skip or sys.exit collects
# zero tests, pytest exits 5 and run_extra_tests.py reports FAIL.
try:
    import pandas as pd
except ImportError:
    pd = None
# Outside the optional-dependency catch: a broken application import must fail the run (audit A6).
if pd is None:
    study = None
else:
    import study


@unittest.skipIf(pd is None, 'pandas not installed')
class StudyTests(unittest.TestCase):
    def test_signatures_and_mirror(self):
        # close 99 -> 101 is a break, then 102 is acceptance.
        a = pd.DataFrame(dict(o=[101, 101, 99, 101], h=[102, 102, 102, 103],
                              l=[100, 98, 98, 100], c=[101, 99, 101, 102]))
        m = study.signatures(a, np.full(4, 100.), 1)
        self.assertTrue(m['break'][2])
        self.assertTrue(m['reclaim'][2])
        self.assertTrue(m['acceptance'][3])
        b = pd.DataFrame(dict(o=200-a.o, h=200-a.l, l=200-a.h, c=200-a.c))
        for key, value in m.items():
            np.testing.assert_array_equal(value, study.signatures(b, np.full(4, 100.), -1)[key])

    def test_wick_not_break_and_zero_range(self):
        a = pd.DataFrame(dict(o=[101, 101, 101], h=[101, 103, 101],
                              l=[101, 99, 101], c=[101, 102, 101]))
        m = study.signatures(a, np.full(3, 100.), 1)
        self.assertTrue(m['rejection'][1])
        self.assertFalse(m['break'][1])
        self.assertFalse(m['strong_break'][2])

    def test_complete_buckets_and_duplicate_rejected(self):
        a = self.bars(6)
        b = study.aggregate(a, 2)
        self.assertEqual(list(b.c), [102, 104, 106])
        self.assertEqual(b.index[0], a.index[0]+pd.Timedelta(minutes=2))
        self.assertEqual(len(study.aggregate(a.drop(a.index[1]), 2)), 2)
        with self.assertRaises(ValueError):
            study.validate(pd.concat([a, a.iloc[:1]]))

    def test_level_available_after_parent_close(self):
        a = self.bars(480)
        parent = study.aggregate(a, 240)
        t = pd.DatetimeIndex([a.index[239], a.index[240]])
        levels = study.known(parent.h, t)
        self.assertTrue(np.isnan(levels[0]))
        self.assertEqual(levels[1], 341.)
        # Mutating the future cannot change the first available level.
        changed = a.copy()
        changed.loc[changed.index>=a.index[240], 'h'] += 999
        np.testing.assert_equal(levels, study.known(study.aggregate(changed, 240).h, t))

    def test_next_open_outcome(self):
        a = self.bars(70)
        signal_end = a.index[5]
        # Entry open 105, exit open 165; no signal candle close fill.
        r = study.forward(a, pd.DatetimeIndex([signal_end]), 60)
        self.assertAlmostEqual(r[0], 165/105-1)
        self.assertTrue(np.isnan(study.forward(a, pd.DatetimeIndex([a.index[-1]]), 60)[0]))

    def test_guard_and_ohlc(self):
        with self.assertRaises(ValueError):
            study.check_month('2024-07')
        a = self.bars(2)
        a.loc[a.index[0], 'l'] = 10000
        with self.assertRaises(ValueError):
            study.validate(a)

    def test_gap_cannot_bridge_forward_window(self):
        a = self.bars(70)
        self.assertTrue(np.isnan(study.forward(a.drop(a.index[10]), pd.DatetimeIndex([a.index[5]]), 60)[0]))

    def test_full_synthetic_event_pipeline(self):
        a = self.bars(34*1440)
        op = 100+np.sin(np.arange(len(a))/100)
        a['o'], a['c'], a['h'], a['l'] = op, op+.05, op+.2, op-.2
        e = study.make_events(a)
        self.assertGreater(len(e), 0)
        self.assertTrue((e.time>=pd.Timestamp('2022-02-01', tz='UTC')).all())
        self.assertFalse(e[['gross', 'base_win', 'lift']].isna().any().any())

    @staticmethod
    def bars(n):
        op = np.arange(n)+100.
        return pd.DataFrame(dict(o=op, h=op+2, l=op-1, c=op+1, v=np.ones(n)),
                            index=pd.date_range('2022-01-01', periods=n, freq='min', tz='UTC'))



HOOK = """
import builtins, runpy
original = builtins.__import__
def hook(name, *args, **kwargs):
    if name == %r:
        raise ImportError('simulated import failure')
    return original(name, *args, **kwargs)
builtins.__import__ = hook
runpy.run_path('test_study.py', run_name='__main__')
"""


@unittest.skipIf(os.environ.get('CANDLE_IMPORT_GUARD_CHILD'), 'nested run')
class ImportGuardTests(unittest.TestCase):
    """Run test_study.py in a subprocess with one import forced to fail."""
    here = os.path.dirname(os.path.abspath(__file__))

    def run_hooked(self, blocked):
        return subprocess.run([sys.executable, '-c', HOOK % blocked], cwd=self.here,
                              capture_output=True, text=True, timeout=120,
                              env=dict(os.environ, CANDLE_IMPORT_GUARD_CHILD='1'))

    @unittest.skipIf(pd is None, 'pandas not installed')
    def test_broken_study_import_fails_closed(self):
        r = self.run_hooked('study')
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn('simulated import failure', r.stderr)

    @unittest.skipIf(pd is None, 'pandas not installed')
    def test_missing_pandas_is_explicit_skips(self):
        r = self.run_hooked('pandas')
        self.assertEqual(r.returncode, 0, r.stderr)
        dots = r.stderr.splitlines()[0]
        # Every test skipped (StudyTests and the nested-run ImportGuardTests), none executed.
        self.assertEqual(set(dots), {'s'}, r.stderr)
        self.assertEqual(len(dots), 10, r.stderr)


if __name__ == '__main__':
    unittest.main()
