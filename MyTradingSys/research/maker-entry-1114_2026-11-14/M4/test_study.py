"""Tests for M4 study (run: python -I test_study.py ; also run with STUDY_BUG=1 to see the naive variant fail)."""
import os, sys, unittest, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study as st  # noqa: E402

MIN = 60000
T = 1_700_000_000_000 - (1_700_000_000_000 % 3600000)   # anchor (signal bar closes here)
E = T + 600 * MIN


def mk(bars, t0):
    a = np.array(bars, float)
    return dict(t_ms=t0 + MIN * np.arange(len(a), dtype=float), o=a[:, 0], h=a[:, 1], l=a[:, 2], c=a[:, 3])


def flat(n, px):
    return [(px, px + 0.05, px - 0.05, px)] * n


def order(sd=1, close_prev=100.0, open_T=100.6, a1=0.1):
    return st.build_order(sd, float(T), close_prev, open_T, a1, float(E))


class M4(unittest.TestCase):
    def test_limit_is_signal_bar_close_not_next_open(self):
        o = order()
        self.assertEqual(o["L"], 100.0)               # naive variant (L = next open 100.6) fails here
        self.assertEqual(o["signal_close_ms"], float(T))
        self.assertAlmostEqual(o["stop"], 100.0 - 0.5)  # 0.5% floor binds (0.6*0.1 < 0.5)

    def test_signal_bar_itself_never_fills(self):
        # bars BEFORE T dip through L (the signal bar); after T price stays above L -> must be a miss
        before = [(100.5, 100.6, 99.9, 100.2)] * 15            # signal bar region, trades through 100.0
        after = flat(600, 101.0)
        m1 = mk(before + after, T - 15 * MIN)
        r = st.run_order(order(), m1, tick=0.01)
        self.assertFalse(r["filled"])                         # naive variant (reads from T-15m) fills here

    def test_touch_not_fill_and_through_fills(self):
        touch = flat(5, 101.0) + [(101.0, 101.0, 100.00, 101.0)] + flat(594, 101.0)
        self.assertFalse(st.run_order(order(), mk(touch, T), tick=0.01)["filled"])
        thr = flat(5, 101.0) + [(101.0, 101.0, 99.99, 101.0)] + flat(594, 101.0)
        r = st.run_order(order(), mk(thr, T), tick=0.01)
        self.assertTrue(r["filled"])
        self.assertEqual(r["entry_px"], 100.0)               # fill at L, never better

    def test_order_expires_after_15m_and_hold_to_0800(self):
        late = flat(20, 101.0) + [(101.0, 101.0, 99.0, 100.0)] + flat(579, 101.0)   # dip at minute 20: expired
        self.assertFalse(st.run_order(order(), mk(late, T), tick=0.01)["filled"])
        ok = flat(5, 101.0) + [(101.0, 101.0, 99.99, 100.4)] + flat(600, 101.2)
        r = st.run_order(order(), mk(ok, T), tick=0.01)
        self.assertEqual(r["exit_type"], "time")             # no target in this idea: hold to E
        self.assertEqual(r["exit_ms"], float(E))

    def test_matched_direction_gate(self):
        self.assertEqual(st.matched_side(True, False, 1), 1)
        self.assertEqual(st.matched_side(True, False, -1), 0)   # long in DOWN = control, not traded
        self.assertEqual(st.matched_side(False, True, 0), -1)
        self.assertEqual(st.matched_side(False, True, 1), 0)


if __name__ == "__main__":
    unittest.main()
