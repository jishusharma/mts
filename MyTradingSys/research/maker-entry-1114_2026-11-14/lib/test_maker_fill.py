"""Tests for maker_fill (run: python -I -m unittest test_maker_fill from this folder, or python test_maker_fill.py)."""
import os
import sys
import unittest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maker_fill as mf  # noqa: E402

MIN = 60000
T0 = 1_700_000_000_000 - (1_700_000_000_000 % 3600000)  # a signal close on an hour boundary
TICK = 0.01


def mk(bars, t0=T0):
    """bars: list of (o,h,l,c) 1m bars starting at t0."""
    a = np.array(bars, float)
    return dict(t_ms=t0 + MIN * np.arange(len(a), dtype=float), o=a[:, 0], h=a[:, 1], l=a[:, 2], c=a[:, 3])


def flat(n, px=101.0):
    return [(px, px + 0.05, px - 0.05, px)] * n


def sim(side, L, stop, target, bars, tf=60 * MIN, ts=None, close_basis=False, **kw):
    m1 = mk(bars)
    return mf.simulate_maker(side, L, stop, target, T0, tf, ts, close_basis, m1, tick=TICK, **kw)


class FillRules(unittest.TestCase):
    def test_touch_without_through_is_not_fill(self):
        bars = flat(10) + [(100.5, 100.6, 100.00, 100.5)] + flat(49)   # low == L exactly
        r = sim("long", 100.0, 99.0, 102.0, bars)
        self.assertFalse(r["filled"])
        self.assertEqual(r["reason_missed"], "no_through")
        self.assertEqual(r["net_R"], 0.0)
        # short mirror
        bars = flat(10, 99) + [(99.5, 100.00, 99.4, 99.5)] + flat(49, 99)
        r = sim("short", 100.0, 101.0, 98.0, bars)
        self.assertFalse(r["filled"])

    def test_one_tick_through_fills(self):
        bars = flat(10) + [(100.5, 100.6, 99.99, 100.5)] + flat(49)
        r = sim("long", 100.0, 99.0, 102.0, bars)
        self.assertTrue(r["filled"])
        bars = flat(10, 99) + [(99.5, 100.01, 99.4, 99.5)] + flat(49, 99)
        self.assertTrue(sim("short", 100.0, 101.0, 98.0, bars)["filled"])

    def test_fill_price_is_L_never_better_incl_gap_through(self):
        # first bar opens far below L (gap through): still fills at exactly L
        bars = [(98.0, 100.5, 97.9, 100.2)] + flat(59, 100.2)
        r = sim("long", 100.0, 97.0, None, bars, ts=T0 + 120 * MIN)
        self.assertTrue(r["filled"])
        self.assertEqual(r["entry_px"], 100.0)
        # gross computed from L, not from the better open: exit at open of bar at time stop (price 100.2)
        bars = [(98.0, 100.5, 97.9, 100.2)] + flat(119, 100.2)
        r = sim("long", 100.0, 97.0, None, bars, ts=T0 + 120 * MIN)
        self.assertAlmostEqual(r["gross_R"], (r["exit_px"] - 100.0) / 3.0)
        # short: open gaps above L, fills at L
        bars = [(102.0, 102.3, 99.8, 99.9)] + flat(119, 99.9)
        r = sim("short", 100.0, 103.0, None, bars, ts=T0 + 120 * MIN)
        self.assertEqual(r["entry_px"], 100.0)

    def test_stop_before_fill_cancels(self):
        # stop one half tick under L: bar touches the stop but does not trade a full tick through L -> cancel
        bars = flat(5) + [(100.2, 100.3, 99.995, 100.1)] + [(100.0, 100.0, 99.5, 99.6)] + flat(53)
        r = sim("long", 100.0, 99.995, 102.0, bars)
        self.assertFalse(r["filled"])
        self.assertEqual(r["reason_missed"], "stop_before_fill")

    def test_same_bar_fill_and_stop_is_a_loss(self):
        bars = flat(5) + [(100.5, 100.6, 98.9, 99.2)] + flat(54)       # fills and stops in one bar
        r = sim("long", 100.0, 99.0, 102.0, bars)
        self.assertTrue(r["filled"])
        self.assertEqual(r["exit_type"], "stop")
        self.assertAlmostEqual(r["gross_R"], -1.0)

    def test_same_bar_stop_and_target_is_stop(self):
        bars = flat(5) + [(100.5, 100.6, 99.9, 100.2)] + [(100.2, 102.5, 98.9, 100.0)] + flat(53)
        r = sim("long", 100.0, 99.0, 102.0, bars)
        self.assertEqual(r["exit_type"], "stop")
        self.assertAlmostEqual(r["gross_R"], -1.0)
        bars = flat(5, 99) + [(99.5, 100.1, 99.4, 99.6)] + [(99.8, 101.1, 97.5, 99.0)] + flat(53, 99)
        r = sim("short", 100.0, 101.0, 98.0, bars)
        self.assertEqual(r["exit_type"], "stop")

    def test_target_needs_tick_through(self):
        bars = flat(5) + [(100.5, 100.6, 99.9, 100.2)] + [(100.2, 102.00, 100.0, 100.5)] + flat(53, 100.5)
        r = sim("long", 100.0, 99.0, 102.0, bars, ts=T0 + 90 * MIN)
        self.assertNotEqual(r["exit_type"], "target")      # touch of target is not enough
        bars[6] = (100.2, 102.01, 100.0, 100.5)
        r = sim("long", 100.0, 99.0, 102.0, bars, ts=T0 + 90 * MIN)
        self.assertEqual(r["exit_type"], "target")

    def test_fees_by_exit_type(self):
        risk = 1.0
        # maker entry + maker target = 6 bp
        bars = flat(5) + [(100.5, 100.6, 99.9, 100.2)] + [(100.2, 102.5, 100.0, 102.0)] + flat(53)
        r = sim("long", 100.0, 99.0, 102.0, bars)
        self.assertEqual(r["exit_type"], "target")
        self.assertAlmostEqual(r["fee_R"], 0.0006 * 100.0 / risk)
        self.assertAlmostEqual(r["gross_R"], 2.0)
        self.assertAlmostEqual(r["net_R"], 2.0 - 0.06)
        # maker entry + stop = 9 bp
        bars = flat(5) + [(100.5, 100.6, 98.9, 99.5)] + flat(54)
        r = sim("long", 100.0, 99.0, 102.0, bars)
        self.assertAlmostEqual(r["fee_R"], 0.0009 * 100.0 / risk)
        self.assertAlmostEqual(r["net_R"], -1.0 - 0.09)
        # maker entry + time stop = 9 bp (taker exit)
        bars = flat(5) + [(100.5, 100.6, 99.9, 100.2)] + flat(114, 100.5)
        r = sim("long", 100.0, 99.0, 102.0, bars, ts=T0 + 100 * MIN)
        self.assertEqual(r["exit_type"], "time")
        self.assertAlmostEqual(r["fee_R"], 0.0009 * 100.0 / risk)
        self.assertAlmostEqual(r["exit_ms"], T0 + 100 * MIN)

    def test_close_basis_stop_exits_at_close(self):
        # intrabar low pierces stop but close recovers -> NOT stopped; later close under stop -> exit at that close
        bars = flat(5) + [(100.5, 100.6, 99.9, 100.2)] + [(100.2, 100.3, 98.0, 99.5)] + [(99.5, 99.6, 98.2, 98.4)] + flat(52, 98.4)
        r = sim("long", 100.0, 99.0, 103.0, bars, close_basis=True)
        self.assertEqual(r["exit_type"], "stop_close")
        self.assertEqual(r["exit_px"], 98.4)
        self.assertAlmostEqual(r["gross_R"], -1.6)

    def test_order_life_one_bar_of_entry_tf(self):
        thr = (100.5, 100.6, 99.9, 100.2)
        for tf, n in ((60 * MIN, 60), (15 * MIN, 15)):
            ok = flat(n - 1) + [thr] + flat(200)             # last allowed 1m bar
            late = flat(n) + [thr] + flat(200)               # first bar after expiry
            self.assertTrue(sim("long", 100.0, 99.0, 102.0, ok, tf=tf)["filled"])
            r = sim("long", 100.0, 99.0, 102.0, late, tf=tf)
            self.assertFalse(r["filled"])
            self.assertEqual(r["reason_missed"], "no_through")

    def test_no_use_of_bars_at_or_before_signal_close(self):
        # bars before signal close trade through L; bars after never do -> must be a miss
        pre = [(100.5, 100.6, 99.0, 100.2)] * 5
        post = flat(60)
        t0 = T0 - 5 * MIN
        m1 = mk(pre + post, t0=t0)
        r = mf.simulate_maker("long", 100.0, 98.0, 102.0, T0, 60 * MIN, None, False, m1, tick=TICK)
        self.assertFalse(r["filled"])
        # the bar whose open time == signal close IS the first usable bar
        m1 = mk(pre + [(100.5, 100.6, 99.9, 100.2)] + flat(59), t0=t0)
        r = mf.simulate_maker("long", 100.0, 98.0, 102.0, T0, 60 * MIN, None, False, m1, tick=TICK)
        self.assertEqual(r["fill_ms"], T0) if r["filled"] else self.fail("first bar after close must be usable")

    def test_truncation_and_pre_signal_invariance(self):
        rng = np.random.default_rng(3)
        n = 3000
        c = 100 + np.cumsum(rng.normal(0, 0.05, n))
        o = np.r_[c[0], c[:-1]]
        h = np.maximum(o, c) + np.abs(rng.normal(0, 0.03, n))
        l = np.minimum(o, c) - np.abs(rng.normal(0, 0.03, n))
        m1 = dict(t_ms=T0 - 1000 * MIN + MIN * np.arange(n, dtype=float), o=np.round(o, 2), h=np.round(h, 2),
                  l=np.round(l, 2), c=np.round(c, 2))
        tot = 0
        for k in range(60):
            sc = T0 + (k * 20) * MIN
            i = int(np.searchsorted(m1["t_ms"], sc))
            L = float(m1["c"][i - 1]) + 0.03
            args = ("long", L, L - 0.4, L + 0.6, sc, 60 * MIN, sc + 240 * MIN, False)
            r = mf.simulate_maker(*args, m1, tick=TICK)
            # (a) corrupt every bar before the signal close
            m2 = {k_: v.copy() for k_, v in m1.items()}
            for key in ("o", "h", "l", "c"):
                m2[key][:i] = 1e6 * (k % 2 * 2 - 1)
            self.assertEqual(r, mf.simulate_maker(*args, m2, tick=TICK))
            # (b) truncate data right after the (known) exit bar
            if r["filled"] and r["exit_type"] != "time":
                j = int(np.searchsorted(m1["t_ms"], r["exit_ms"])) + 1
                m3 = {k_: v[:j] for k_, v in m1.items()}
                self.assertEqual(r, mf.simulate_maker(*args, m3, tick=TICK))
                tot += 1
        self.assertGreater(tot, 5)

    def test_planted_series_long_and_short(self):
        # long: no fill (low touches 100.00), fill bar 2 (low 99.9), target bar 4 -> +2R gross
        bars = [(100.5, 100.8, 100.00, 100.4), (100.4, 100.6, 99.90, 100.3), (100.3, 100.9, 100.2, 100.8),
                (100.8, 101.5, 100.7, 101.4), (101.4, 102.20, 101.3, 102.0)] + flat(60, 102.0)
        r = sim("long", 100.0, 99.0, 102.0, bars)
        self.assertTrue(r["filled"])
        self.assertEqual(r["fill_ms"], T0 + 1 * MIN)
        self.assertEqual(r["exit_ms"], T0 + 4 * MIN)
        self.assertAlmostEqual(r["gross_R"], 2.0)
        self.assertAlmostEqual(r["net_R"], 1.94)
        # short: stop 1.0 above, target 3.0 below, filled at bar 1, stopped bar 3
        bars = [(99.5, 99.9, 99.4, 99.6), (99.6, 100.05, 99.5, 99.9), (99.9, 100.3, 99.8, 100.1),
                (100.1, 101.2, 100.0, 101.0)] + flat(60, 101.0)
        r = sim("short", 100.0, 101.0, 97.0, bars)
        self.assertEqual(r["exit_type"], "stop")
        self.assertAlmostEqual(r["gross_R"], -1.0)
        self.assertAlmostEqual(r["fee_R"], 0.0009 * 100.0)

    def test_fill_bar_target_switch(self):
        bars = flat(3) + [(100.5, 102.5, 99.9, 101.2)] + flat(60, 101.0)   # fill + target in the same bar
        self.assertEqual(sim("long", 100.0, 99.0, 102.0, bars)["exit_type"], "target")
        r = sim("long", 100.0, 99.0, 102.0, bars, fill_bar_target=False, ts=T0 + 30 * MIN)
        self.assertEqual(r["exit_type"], "time")

    def test_invalid_levels_raise(self):
        with self.assertRaises(ValueError):
            sim("long", 100.0, 101.0, 102.0, flat(5))
        with self.assertRaises(ValueError):
            sim("short", 100.0, 101.0, 102.0, flat(5))


class Tick(unittest.TestCase):
    def test_estimate_tick(self):
        m1 = mk([(100.01, 100.05, 100.00, 100.03), (100.03, 100.10, 100.02, 100.07)])
        self.assertAlmostEqual(mf.estimate_tick(m1, use_cache=False), 0.01)
        m1 = mk([(0.1234, 0.1240, 0.1230, 0.1236), (0.1236, 0.1241, 0.1233, 0.1238)])
        self.assertAlmostEqual(mf.estimate_tick(m1, use_cache=False), 0.0001)


class Stats(unittest.TestCase):
    def _res(self, nets, days, filled=True):
        return [dict(filled=filled, net_R=x, gross_R=x + 0.06, fee_R=0.06, fill_ms=d * 86400000.0 + 1) for x, d in zip(nets, days)]

    def test_summarize_known_values(self):
        res = self._res([1.0, -1.0, 2.0, 0.0], [1, 2, 3, 4]) + [mf._miss("no_through") | dict(signal_close_ms=5 * 86400000.0)] * 4
        s = mf.summarize(res, n_boot=500, n_cluster=500)
        self.assertEqual((s["n_signals"], s["n_filled"], s["fill_rate"]), (8, 4, 0.5))
        self.assertAlmostEqual(s["mean_net_R_filled"], 0.5)
        self.assertAlmostEqual(s["per_signal_R"], 2.0 / 8)           # misses count as 0
        self.assertAlmostEqual(s["mean_gross_R_filled"], 0.56)
        self.assertFalse(s["thin"])
        self.assertLess(s["ci_trade"][0], 0.5)
        self.assertGreater(s["ci_trade"][1], 0.5)

    def test_thin_and_empty(self):
        res = self._res([1.0], [1]) + [mf._miss("no_through")] * 9
        self.assertTrue(mf.summarize(res, n_boot=50, n_cluster=50)["thin"])
        s = mf.summarize([mf._miss("no_through")] * 3, n_boot=50, n_cluster=50)
        self.assertEqual(s["n_filled"], 0)

    def test_ex_best5_days_and_cluster(self):
        # 5 huge days + 30 small slightly-negative days: mean positive overall, negative after dropping top-5
        nets = [10.0] * 5 + [-0.1] * 30
        res = self._res(nets, list(range(35)))
        s = mf.summarize(res, n_boot=300, n_cluster=300)
        self.assertGreater(s["mean_net_R_filled"], 0)
        self.assertAlmostEqual(s["ex_best5_days"], -0.1)
        self.assertEqual(mf.gates(s, 0.01, True)["failed"], [1, 6])  # n<100 and ex-best5<0; gates 2,4,5 ok

    def test_day_cluster_wider_than_trade_when_clustered(self):
        rng = np.random.default_rng(1)
        nets, days = [], []
        for d in range(40):
            shock = rng.normal(0, 1)
            for _ in range(25):
                nets.append(shock + rng.normal(0, 0.1)); days.append(d)
        s = mf.summarize(self._res(nets, days), n_boot=1000, n_cluster=1000)
        self.assertGreater(s["ci_day"][1] - s["ci_day"][0], 3 * (s["ci_trade"][1] - s["ci_trade"][0]))

    def test_deterministic_seed(self):
        res = self._res(list(np.random.default_rng(0).normal(0.1, 1, 200)), list(range(200)))
        self.assertEqual(mf.summarize(res, n_boot=200, n_cluster=200), mf.summarize(res, n_boot=200, n_cluster=200))

    def test_benjamini_hochberg(self):
        # classic example: m=6, q=0.05 -> reject the 3 smallest (0.001*6/1, 0.008*6/2=.024, 0.02*6/3=.04 ; 0.04*6/4=.06 no)
        p = [0.04, 0.001, 0.2, 0.02, 0.008, 0.9]
        rej, adj = mf.benjamini_hochberg(p, 0.05)
        self.assertEqual(rej, [False, True, False, True, True, False])
        self.assertAlmostEqual(adj[1], 0.006)
        self.assertAlmostEqual(adj[4], 0.024)
        self.assertAlmostEqual(adj[3], 0.04)
        self.assertAlmostEqual(adj[0], 0.06)

    def test_placebo_helpers(self):
        off = mf.signal_offsets_atr(np.array([1, -1]), [99.0, 101.0], [100.0, 100.0], [2.0, 2.0])
        np.testing.assert_allclose(off, [0.5, 0.5])
        self.assertAlmostEqual(mf.placebo_limit("long", 100.0, 2.0, 0.5), 99.0)
        self.assertAlmostEqual(mf.placebo_limit("short", 100.0, 2.0, 0.5), 101.0)

    def test_placebo_pvalue_uses_runner_and_formula(self):
        calls = []

        def run_one(cand, off):
            calls.append((cand, off))
            return dict(filled=(cand % 2 == 0), net_R=0.0 if cand % 2 == 0 else 5.0)
        p, d = mf.placebo_pvalue(0.1, run_one, list(range(10)), [0.0, 0.5], n_filled=20, n_draws=50, seed=7)
        self.assertEqual(len(d), 50)
        self.assertTrue(np.all(d == 0.0))                              # only filled trades count; misses never enter
        self.assertAlmostEqual(p, 1 / 51)                              # none >= observed -> (1+0)/(50+1)
        p2, _ = mf.placebo_pvalue(-0.1, run_one, list(range(10)), [0.0], n_filled=5, n_draws=20, seed=7)
        self.assertAlmostEqual(p2, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
