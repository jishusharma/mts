"""Window test (PRE_REG_EXT.md section 5): no bar at or after 2022-04-01 is read. Run: python test_dev_ext_window.py"""
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ext_window as W  # noqa: E402

APR1 = 1_648_771_200_000      # 2022-04-01 00:00 UTC, computed independently (days since epoch 19083 x 86400000)


class Window(unittest.TestCase):
    def test_cut_constant(self):
        self.assertEqual(W.CUT_MS, APR1)

    def test_no_bar_at_or_after_cut(self):
        a6, a5 = W.load_window()
        self.assertLess(a6[:, 0].max(), APR1)
        self.assertEqual(a5[:, 0].max(), a6[:, 0].max())
        self.assertGreaterEqual(a6[:, 0].min(), W.EXT_START_MS)
        self.assertEqual(a6[:, 0].max(), APR1 - 60000)          # the last minute of 2022-03-31 is present

    def test_window_one_bar_too_wide_is_caught(self):
        a6, _ = W.load_window()
        wide = np.r_[a6[:, 0], APR1]                            # one bar too wide: the 2022-04-01 00:00 bar
        with self.assertRaises(ValueError):
            W.guard(wide, 'wide')
        W.guard(a6[:, 0], 'ok')

    def test_funding_inside_window(self):
        t, _ = W.load_funding()
        self.assertLess(t.max(), APR1)

    def test_installed_studies_see_only_window(self):
        a6, a5 = W.load_window()
        W.install(a6, a5)
        import _bars
        self.assertLess(_bars.load_1m()[:, 0].max(), APR1)


if __name__ == '__main__':
    unittest.main()
