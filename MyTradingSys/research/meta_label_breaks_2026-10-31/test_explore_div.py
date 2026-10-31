"""explore_div.py: an event counts at entry only when known by the entry time; an exit uses only events known after it;
an event stamped on bar k is known at the close of bar k."""
import os
import sys
import unittest

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import explore_div as X  # noqa: E402


class Timing(unittest.TestCase):
    def test_any_in_is_half_open(self):
        times = np.array([100, 200, 300], np.int64)
        self.assertTrue(X.any_in(times, 150, 200))     # known exactly at entry counts
        self.assertFalse(X.any_in(times, 200, 299))    # known at the window start does not
        self.assertFalse(X.any_in(times, 300, 400))

    def test_first_after_skips_event_known_at_entry(self):
        times = np.array([100, 200, 300], np.int64)
        self.assertEqual(X.first_after(times, 200), 300)
        self.assertIsNone(X.first_after(times, 300))

    def test_event_known_at_close_of_stamp_bar(self):
        # closes 10, 8, 9, 7, 9: lows at bars 1 and 3 (price lower low); RSI rising there -> bullish, stamped on bar 4
        c = np.array([10, 8, 9, 7, 9, 10.0])
        b = pd.DataFrame(dict(t=np.arange(6, dtype=np.int64) * 3600, c=c, v=np.full(6, 10.0), tbv=np.full(6, 5.0)))
        orig = X.S.rsi
        X.S.rsi = lambda x: np.array([50, 20, 40, 30, 50, 60.0])
        try:
            ev = X.div_events(b, 60)
        finally:
            X.S.rsi = orig
        self.assertEqual(ev[('rsi', 'bullish')].tolist(), [4 * 3600 + 3600])


if __name__ == '__main__':
    unittest.main()
