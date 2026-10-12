import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "research", "mfe_exit_2026-10-13"))
import mfe_exit_study as M  # noqa: E402


def synth(n=400, seed=1):
    rng = np.random.default_rng(seed)
    c = 100 + np.cumsum(rng.normal(0, 0.3, n))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) + 0.1
    l = np.minimum(o, c) - 0.1
    v = rng.uniform(10, 20, n)
    tbv = v * rng.uniform(0.3, 0.7, n)
    t = (np.arange(n) * 60000).astype(np.int64)
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": v, "tbv": tbv}


class Causality(unittest.TestCase):
    def test_features_do_not_use_future(self):
        b = synth(400)
        cut = 250
        bc = {k: v[:cut] for k, v in b.items()}
        pairs = [(M.rsi(b["c"], 14), M.rsi(bc["c"], 14)), (M.stochrsi(b["c"], 14), M.stochrsi(bc["c"], 14)),
                 (M.bbpos(b["c"], 20), M.bbpos(bc["c"], 20)),
                 (M.cvdslope(b["v"], b["tbv"], 8), M.cvdslope(bc["v"], bc["tbv"], 8))]
        for full, part in pairs:
            np.testing.assert_allclose(full[:cut], part, equal_nan=True)

    def test_volratio_excludes_today(self):
        v = np.ones(1440 * 6)
        v[1440 * 5:] = 10.0                       # today 10x yesterday's same slots
        r = M.volratio(v, 1, 3)
        self.assertAlmostEqual(r[1440 * 5 + 7], 10.0)
        self.assertTrue(np.isnan(r[10]))

    def test_rule_fires_only_on_bar_after_condition(self):
        # RSI fast crosses below 50 at index 3 while slow stays above: signal at 3, not 2 or 4
        fast = np.array([60, 55, 52, 48, 47.0])
        slow = np.array([60, 60, 60, 60, 60.0])
        s = M.rule_signal("E1_momflip", [fast, slow], +1, None, None)
        self.assertEqual(list(np.nonzero(s)[0]), [3])
        s = M.rule_signal("E1_momflip", [fast, slow], -1, None, None)   # short: mirrored, no signal
        self.assertEqual(int(s.sum()), 0)


class TradeMatrix(unittest.TestCase):
    def setUp(self):
        n = (M.K + 6) * 5 + 40
        t = (np.arange(n) * 60000).astype(np.int64)
        c = 100.0 + np.arange(n) * 0.01
        self.k1 = {"t": t, "o": c.copy(), "h": c + 0.005, "l": c - 0.005, "c": c, "v": np.ones(n),
                   "tbv": np.ones(n)}
        self.ft, self.fc = np.array([], dtype=np.int64), np.array([0.0])

    def test_long_in_uptrend_gross_and_fee(self):
        fires = [(int(self.k1["t"][10]), 1, 0.5, "TRAIN")]
        tm = M.trade_matrix(self.k1, fires, 5, self.ft, self.fc)
        # expected (hand): exit offset k exits at o[10 + (k+1)*5]; gross = that/o[10] - 1
        k = 3
        exp = self.k1["o"][10 + (k + 1) * 5] / self.k1["o"][10] - 1
        self.assertAlmostEqual(tm["gross"][0, k], exp, places=12)
        self.assertAlmostEqual(tm["net"][0, k], exp - M.FEE_RT, places=12)

    def test_stop_hit_caps_loss_and_short_flips_sign(self):
        k1 = {k: v.copy() for k, v in self.k1.items()}
        k1["l"][12] = 90.0                        # long stop at 100.1-1.0 hit on 1m bar 12
        fires = [(int(k1["t"][10]), 1, 0.5, "TRAIN")]
        tm = M.trade_matrix(k1, fires, 5, self.ft, self.fc)
        e, stop = k1["o"][10], k1["o"][10] - M.STOP_ATR * 0.5
        self.assertAlmostEqual(tm["gross"][0, 0], stop / e - 1, places=12)   # exit open at 15 > stop bar 12
        fires = [(int(self.k1["t"][10]), -1, 0.5, "TRAIN")]
        tm = M.trade_matrix(self.k1, fires, 5, self.ft, self.fc)
        self.assertLess(tm["gross"][0, 3], 0)     # short in an uptrend loses

    def test_funding_sign(self):
        ft = np.array([int(self.k1["t"][20])], dtype=np.int64)
        fc = np.array([0.0, 0.001])
        for s, sign in ((1, 1), (-1, -1)):
            tm = M.trade_matrix(self.k1, [(int(self.k1["t"][10]), s, 5.0, "TRAIN")], 5, ft, fc)
            # offset 0 exits at 15 (before the 20 mark): no funding; offset 3 exits at 30: pays 0.001*s
            gross = tm["gross"][0]
            self.assertAlmostEqual(tm["net"][0, 0], gross[0] - M.FEE_RT, places=12)
            self.assertAlmostEqual(tm["net"][0, 3], gross[3] - M.FEE_RT - 0.001 * sign, places=12)


if __name__ == "__main__":
    unittest.main()
