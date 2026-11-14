"""M1 tests. Run: python test_study.py. Includes naive-variant detectors (fill on touch; uses the signal bar)."""
import os, sys, unittest
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study as S
import maker_fill as MF

H = 3600000


def mk_m1(rows, t0):
    """rows: list of (o,h,l,c) 1m bars starting at t0."""
    a = np.array(rows, float)
    return dict(t_ms=t0 + np.arange(len(a)) * 60000.0, o=a[:, 0], h=a[:, 1], l=a[:, 2], c=a[:, 3])


def mk_D(n=12):
    """flat 1h bars at 100; levels P=100.5 (short limit above close), nearest level below = S1 90."""
    a = np.zeros((n, 6))
    a[:, 0] = np.arange(n) * H
    a[:, 1] = a[:, 4] = 100.0
    a[:, 2] = 100.2
    a[:, 3] = 99.8
    lv = {k: np.full(n, v) for k, v in dict(S3=80., S2=85., S1=90., P=100.5, R1=108., R2=115., R3=120.).items()}
    return dict(a=a, lv=lv, ph=np.full(n, -1), valid=np.ones(n, bool), atr=np.full(n, 0.2), sym="X")


class T(unittest.TestCase):
    def test_mapping_levels(self):
        D = mk_D()
        L, stop, tgt = S.limit_order(D, 5)
        self.assertEqual(L, 100.5)                           # limit = pivot P
        self.assertAlmostEqual(stop, 100.5 + 0.005 * 100.5)  # min 0.5% beats swing / ATR
        self.assertEqual(tgt, 90.0)                          # nearest level below L
        self.assertGreater(stop, L)

    def test_touch_is_not_a_fill(self):
        D = mk_D()
        t0 = D["a"][5, 0] + H
        rows = [(100, 100.5, 99.9, 100.0)] * 60 + [(100, 100, 100, 100)] * 400    # high == L exactly: touch
        r = S.maker_trade(D, 5, mk_m1(rows, t0), tick=0.01)
        self.assertFalse(r["filled"])                        # naive 'fill on touch' would fill here
        rows[3] = (100, 100.51, 99.9, 100.0)                 # one tick through
        r = S.maker_trade(D, 5, mk_m1(rows, t0), tick=0.01)
        self.assertTrue(r["filled"])
        self.assertEqual(r["entry_px"], 100.5)               # fill at L, never better

    def test_signal_bar_not_used(self):
        D = mk_D()
        t0 = D["a"][5, 0]                                    # data begins INSIDE the signal bar
        rows = [(100, 101.0, 99.9, 100.0)] * 60 + [(100, 100.2, 99.9, 100.0)] * 460   # signal bar spikes through L
        r = S.maker_trade(D, 5, mk_m1(rows, t0), tick=0.01)
        self.assertFalse(r["filled"])                        # naive variant (reads signal bar) would fill

    def test_order_expires_after_one_bar(self):
        D = mk_D()
        t0 = D["a"][5, 0] + H
        rows = [(100, 100.2, 99.9, 100.0)] * 61 + [(100, 101.0, 99.9, 100.0)] * 400   # spike at minute 61
        r = S.maker_trade(D, 5, mk_m1(rows, t0), tick=0.01)
        self.assertFalse(r["filled"])

    def test_target_is_maker_exit(self):
        D = mk_D()
        t0 = D["a"][5, 0] + H
        rows = [(100, 100.6, 99.9, 100.0)] * 3 + [(100, 100, 89.9, 90.0)] * 60
        r = S.maker_trade(D, 5, mk_m1(rows, t0), tick=0.01)
        self.assertTrue(r["filled"])
        self.assertEqual(r["exit_type"], "target")
        risk = 100.5 * 0.005
        self.assertAlmostEqual(r["fee_R"], (0.0003 + 0.0003) * 100.5 / risk)

    def test_orig_signal_loop_matches_original_run_trades(self):
        import nk2_orig as O
        a = np.zeros((200, 6)); a[:, 0] = np.arange(200) * 3600000.0
        rng = np.random.default_rng(1)
        c = 100 + np.cumsum(rng.normal(0, 0.6, 200)); a[:, 4] = c; a[:, 1] = np.r_[c[0], c[:-1]]
        a[:, 2] = np.maximum(a[:, 1], c) + 0.2; a[:, 3] = np.minimum(a[:, 1], c) - 0.2
        lv = {k: np.full(200, v) for k, v in dict(S3=80., S2=85., S1=90., P=100., R1=108., R2=115., R3=120.).items()}
        D = dict(a=a, lv=lv, ph=np.zeros(200, int), valid=np.ones(200, bool), atr=np.full(200, 0.5), sym="X")
        mine = S.orig_signals(D)
        ref = O.run_trades(D, -1, "P", 4, (-1, 0), 24)
        self.assertEqual(len(mine), len(ref))
        for m, r in zip(mine, ref):
            self.assertEqual((m[4], m[1]), (r[0], r[1]))


if __name__ == "__main__":
    unittest.main()
