"""Tests for htf_lib: confirm rule, stop/target walk, net R arithmetic."""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import htf_lib as H  # noqa: E402

HR = H.HOUR


class T(unittest.TestCase):
    def test_signal_needs_red_bar_and_higher_close(self):
        ft = np.array([0, 4, 8, 12]) * HR
        fo = np.array([100, 100, 90, 90.0])
        fc = np.array([99, 90, 95, 95.0])   # bar1 red (close 90 < open 100), bar2 close 95 > 90
        fl = np.array([98, 88, 89, 89.0])
        rsi = np.array([50, 10, 40, 60.0])
        ev = H.signal_events(ft, fo, fo, fl, fc, rsi, 12, 4)
        self.assertEqual(len(ev), 1)
        s, entry, stop, ect = ev[0]
        self.assertEqual((s, entry, stop, ect), (1, 95.0, 88.0, 12 * HR))
        fc2 = fc.copy()
        fc2[2] = 89.0  # next close not above signal close: no trade
        self.assertEqual(H.signal_events(ft, fo, fo, fl, fc2, rsi, 12, 4), [])

    def test_exit_walk_stop_target_and_cost(self):
        entry, stop = np.array([100.0]), np.array([98.0])
        O = np.array([[100, 100, 100, 100.0]])
        Hh = np.array([[101, 104, 100, 100.0]])
        Lo = np.array([[99, 99, 99, 99.0]])
        C = np.array([[100, 100, 100, 100.0]])
        r = H.fwd_exit_r(entry, stop, O, Hh, Lo, C, "tgt", 2.0, 4, 0.0)
        self.assertAlmostEqual(r[0], 2.0)               # target 104 hit at hour 2, risk 2
        Lo2 = np.array([[99, 97, 99, 99.0]])
        Hh2 = np.array([[101, 104, 100, 100.0]])
        r2 = H.fwd_exit_r(entry, stop, O, Hh2, Lo2, C, "tgt", 2.0, 4, 0.0)
        self.assertAlmostEqual(r2[0], -1.0)             # same bar stop and target: stop first
        r3 = H.fwd_exit_r(entry, stop, O, Hh, Lo, C, "time", 0, 4, 0.02)
        self.assertAlmostEqual(r3[0], -0.02 / 0.02)     # flat exit, 2 % cost on a 2 % stop = -1R

    def test_bh(self):
        sig = H.bh(np.array([0.001, 0.5, 0.9]), 0.10)
        self.assertEqual(sig.tolist(), [True, False, False])


if __name__ == "__main__":
    unittest.main()
