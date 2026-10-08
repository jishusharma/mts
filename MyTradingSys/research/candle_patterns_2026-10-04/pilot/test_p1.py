"""Tests for run_p1.py. Expected values are hand-derived from PRE_REG_CANDLE_PILOT.md sections 2, 4, 5 (not from the code)."""
import sys
sys.dont_write_bytecode = True
import math
import random
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_p1  # noqa: E402
import stats_lite  # noqa: E402
import cdata  # noqa: E402

D = 86400000
H8 = 8 * 3600000


def mk(opens, step=D):
    return [{"t": k * step, "o": o, "h": o + 1, "l": o - 1, "c": o} for k, o in enumerate(opens)]


class TestTrade(unittest.TestCase):
    def test_entry_exit_indexing(self):
        # signal at i=1; entry open(2)=110; h=3 -> exit open(5)=150. Not close(i), not open(i+h).
        bars = mk([100, 105, 110, 120, 130, 150, 160, 170])
        fwd = run_p1.forward_return(bars, 1, 3)
        self.assertAlmostEqual(fwd, math.log(150.0 / 110.0), places=12)
        self.assertAlmostEqual(run_p1.forward_return(bars, 1, 1), math.log(120.0 / 110.0), places=12)

    def test_funding_window_and_sign(self):
        bars = mk([100, 100, 110, 110])          # signal i=0, entry open(1)=t=D, h=1 exit open(2)=t=2D
        rows = [(D, 0.5), (D + H8, 1e-4), (D + 2 * H8, 1e-4), (2 * D, 1e-4), (2 * D + H8, 9.0)]
        f = cdata.Funding(rows)
        fund = run_p1.window_funding(bars, 0, 1, f)
        # (t_entry, t_exit] : excludes the settlement at entry (0.5) and anything after exit (9.0)
        self.assertAlmostEqual(fund, 3e-4, places=12)
        fwd = math.log(1.1)
        self.assertAlmostEqual(run_p1.net_trade(+1, fwd, fund), fwd - 0.0014 - 3e-4, places=12)
        self.assertAlmostEqual(run_p1.net_trade(-1, fwd, fund), -fwd - 0.0014 + 3e-4, places=12)   # short receives funding

    def test_cost_is_14bps_round_trip(self):
        self.assertAlmostEqual(run_p1.net_trade(+1, 0.0, 0.0), -0.0014, places=12)
        self.assertAlmostEqual(run_p1.net_trade(-1, 0.0, 0.0), -0.0014, places=12)


class TestInference(unittest.TestCase):
    def test_bh_hand_example(self):
        q = stats_lite.bh_qvalues([0.01, 0.04, 0.03, 0.005])
        for a, b in zip(q, [0.02, 0.04, 0.04, 0.02]):
            self.assertAlmostEqual(a, b, places=12)

    def test_bh_insufficient_counted_as_trials(self):
        # 2 live p-values + 2 INSUFFICIENT-N (p=1) -> m=4 : q = [0.02*... ] hand: sorted .01,.03,1,1 ; q(.03)=min(1*4/4..)=.03*4/2=.06,q(.01)=.01*4/1=.04->min(.04,.06)=.04
        res = run_p1.bh_over_trials([0.01, 0.03, None, None])
        self.assertAlmostEqual(res[0], 0.04, places=12)
        self.assertAlmostEqual(res[1], 0.06, places=12)
        self.assertIsNone(res[2])
        self.assertIsNone(res[3])

    def _family(self, planted, seed=7):
        rng = random.Random(seed)
        m = 1500
        val = [rng.gauss(0, 0.01) for _ in range(m)]
        items = []
        for k in range(6):
            ev = [1 if rng.random() < 0.1 else 0 for _ in range(m)]
            v = list(val)
            if planted and k == 0:
                v = [x + (0.02 if e else 0.0) for x, e in zip(v, ev)]   # +2 percent on events, 2 sd
            items.append({"name": "k%d" % k, "ev": ev, "val": v if (planted and k == 0) else val, "sign": 1, "min_n": 20})
        return stats_lite.block_boot_family(items, m, 10, reps=400, seed=12345)

    def test_rc_null_false_positive_rate(self):
        # pure noise, 12 independent datasets: family-wise rejection at 0.05 should be rare (nominal 5 percent; allow <= 3 of 12)
        hits = sum(1 for sd in range(100, 112) if min(r["p_adj"] for r in self._family(False, sd)) < 0.05)
        self.assertLessEqual(hits, 3)

    def test_rc_planted_effect_found(self):
        res = self._family(True)
        self.assertLess(res[0]["p_adj"], 0.01)
        self.assertEqual(min(res, key=lambda r: r["p_adj"])["name"], "k0")

    def test_block_ci_constant(self):
        m = 200
        ev = [1 if i % 3 == 0 else 0 for i in range(m)]
        lo, hi = run_p1.block_ci_mean(ev, [0.0123] * m, 10, reps=200, seed=1)
        self.assertAlmostEqual(lo, 0.0123, places=12)
        self.assertAlmostEqual(hi, 0.0123, places=12)

    def test_block_ci_brackets_known_mean(self):
        rng = random.Random(3)
        m = 3000
        net = [rng.gauss(0.002, 0.01) for _ in range(m)]
        ev = [1] * m
        lo, hi = run_p1.block_ci_mean(ev, net, 10, reps=500, seed=1)
        mu = sum(net) / m
        self.assertLess(lo, mu)
        self.assertGreater(hi, mu)
        self.assertLess(hi - lo, 0.0015)      # sd/sqrt(n)*3.9 = 0.0007


class TestLabelsAndTriage(unittest.TestCase):
    def test_insufficient_n(self):
        self.assertTrue(run_p1.is_insufficient(19, "1d"))
        self.assertFalse(run_p1.is_insufficient(20, "1d"))
        self.assertTrue(run_p1.is_insufficient(99, "1h"))
        self.assertFalse(run_p1.is_insufficient(100, "1h"))

    def test_triage_requires_all_four(self):
        ok = {"n": 50, "mean_net": 0.001, "ci_lo": 0.0001, "p_adj": 0.05, "stat": 0.002}
        self.assertEqual(run_p1.triage(ok, "1d"), "PASS")
        for k, v in (("n", 19), ("mean_net", -0.001), ("ci_lo", -0.0001), ("p_adj", 0.10), ("stat", -0.001)):
            bad = dict(ok)
            bad[k] = v
            if k == "mean_net":
                bad["ci_lo"] = -0.002
            self.assertNotEqual(run_p1.triage(bad, "1d"), "PASS", k)
        self.assertEqual(run_p1.triage(dict(ok, n=19), "1d"), "INSUFFICIENT-N")


if __name__ == "__main__":
    unittest.main()
