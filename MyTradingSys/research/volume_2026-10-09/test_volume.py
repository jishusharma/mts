"""Tests for the volume study. Expected values are hand-derived from PRE_REG_VOLUME_2026-10-09.md and
backtest/layers/FORMULAS.md (RSI section 1, funding section 13), never from this study's own code.
Run: python MyTradingSys/research/volume_2026-10-09/test_volume.py
"""
import sys
sys.dont_write_bytecode = True
import math
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "candle_patterns_2026-10-04" / "pilot"))
import vdata  # noqa: E402
import vfeat  # noqa: E402
import vstats  # noqa: E402


def bars_from(c, v=None, tbv=None, spread=0.5, o=None):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]]) if o is None else np.asarray(o, dtype=float)
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    v = np.full(n, 100.0) if v is None else np.asarray(v, dtype=float)
    tbv = v * 0.5 if tbv is None else np.asarray(tbv, dtype=float)
    return {"t": np.arange(n, dtype=np.int64) * 86400000, "o": o, "h": h, "l": l, "c": c, "v": v, "tbv": tbv}


class TestRsi(unittest.TestCase):
    def test_formulas_period3_example(self):
        r = vfeat.rsi_wilder(np.array([10, 12, 11, 14.0]), 3)
        self.assertTrue(np.all(np.isnan(r[:3])))
        self.assertAlmostEqual(r[3], 100 - 100 / 6, places=4)           # 83.3333

    def test_formulas_period5_seed_and_first_smooth(self):
        c = np.array([100, 102, 101, 103, 106, 105, 107, 110, 108.0])
        r = vfeat.rsi_wilder(c, 5)
        self.assertAlmostEqual(r[5], 100 - 100 / (1 + 1.4 / 0.4), places=4)       # 77.7778, not the nonzero-count seed
        ag, al = (1.4 * 4 + 2) / 5, (0.4 * 4 + 0) / 5                             # delta[5] = 107 - 105 = +2
        self.assertAlmostEqual(r[6], 100 - 100 / (1 + ag / al), places=4)

    def test_flat_series_is_50_all_gain_is_100(self):
        self.assertAlmostEqual(vfeat.rsi_wilder(np.full(10, 5.0), 3)[5], 50.0)
        self.assertAlmostEqual(vfeat.rsi_wilder(np.arange(1.0, 11.0), 3)[5], 100.0)


class TestVolumeMeasures(unittest.TestCase):
    def test_rv_plain_hand(self):
        v = np.arange(1.0, 26.0)                    # i=20 -> v=21; median of v[0:20] = 1..20 = 10.5
        self.assertAlmostEqual(vfeat.rv_plain(v)[20], 21 / 10.5)
        self.assertTrue(np.isnan(vfeat.rv_plain(v)[19]))

    def test_rv_adj_1d_same_weekday(self):
        n = 100
        v = np.array([(i % 7 + 1) * 10.0 for i in range(n)])
        v[60] *= 2.0                                # i=60 has weekday key 60%7=4 -> baseline 50 over prior 8 same-weekday bars
        r = vfeat.rv_adj(v, "1d")
        self.assertAlmostEqual(r[60], 2.0)
        self.assertAlmostEqual(r[61], 1.0)
        self.assertTrue(np.isnan(r[55]))             # needs 7*8 = 56 prior bars
        self.assertAlmostEqual(r[56], 1.0)

    def test_rv_adj_4h_same_slot_removes_seasonality(self):
        n = 300
        v = np.array([(i % 6 + 1) * 100.0 for i in range(n)])   # strong time-of-day pattern
        r = vfeat.rv_adj(v, "4h")
        self.assertTrue(np.allclose(r[120:], 1.0))                # no spike once the slot pattern is removed
        self.assertGreater(vfeat.rv_plain(v)[250], 1.0 + 1e-9) if (250 % 6) == 5 else None
        v2 = v.copy(); v2[200] *= 3
        self.assertAlmostEqual(vfeat.rv_adj(v2, "4h")[200], 3.0)

    def test_delta_and_clv(self):
        b = bars_from(np.linspace(100, 110, 200), v=np.full(200, 10.0), tbv=np.full(200, 7.0), spread=0.0)
        f = vfeat.features(b, "1d")
        self.assertAlmostEqual(f["dp"][5], (2 * 7 - 10) / 10)     # 0.4
        # bar with o=100,c=104,l=99,h=105 -> clv = 5/6
        b2 = bars_from(np.linspace(100, 110, 200))
        b2["o"][50], b2["c"][50], b2["l"][50], b2["h"][50] = 100, 104, 99, 105
        self.assertAlmostEqual(vfeat.features(b2, "1d")["clv"][50], 5 / 6)

    def test_bollinger_hand(self):
        mid, up, lo = vfeat.bollinger(np.arange(1.0, 21.0))
        sd = math.sqrt((20 ** 2 - 1) / 12.0)                      # population std of 1..20
        self.assertAlmostEqual(mid[19], 10.5)
        self.assertAlmostEqual(up[19], 10.5 + 2 * sd, places=6)
        self.assertAlmostEqual(lo[19], 10.5 - 2 * sd, places=6)

    def test_squeeze_flags(self):
        down = np.linspace(1.0, 0.1, 300)
        self.assertTrue(vfeat.squeeze_flags(down)[120:].all())
        self.assertFalse(vfeat.squeeze_flags(down[::-1].copy())[120:].any())
        self.assertFalse(vfeat.squeeze_flags(down)[:120].any())

    def test_cvd_and_obv(self):
        b = bars_from([10, 11, 10, 12], v=[5, 5, 5, 5], tbv=[4, 4, 1, 3], spread=0)
        f = vfeat.features(b, "1d")
        self.assertTrue(np.allclose(f["cvd"], np.cumsum([3, 3, -3, 1])))        # 2*tbv - v
        self.assertTrue(np.allclose(f["obv"], np.cumsum([0, 5, -5, 5])))


def scenario(n=400, spike_at=300):
    """Quiet random-walk-free baseline (small alternating moves, constant volume), then hand-built events."""
    c = 100 + np.tile([0.0, 0.2], n // 2)[:n]
    b = bars_from(c, spread=0.1)
    return b


class TestEvents(unittest.TestCase):
    def test_buying_climax_and_breakaway(self):
        b = scenario()
        i = 300
        # buy-climax bar: spike volume, new 20-bar high, close in bottom third of the bar
        b["o"][i], b["h"][i], b["l"][i], b["c"][i] = 100.0, 103.0, 99.9, 100.2
        b["v"][i] = 350.0
        e = vfeat.events(b, vfeat.features(b, "1d"))
        self.assertTrue(e["BCLX"][i])
        self.assertFalse(e["BAWAY_UP"][i])
        self.assertTrue(e["SP3_UP"][i])                           # rvadj = 3.5 >= 3, up bar
        self.assertTrue(e["SP2_UP"][i])
        self.assertFalse(e["SP3_DN"][i])
        j = 320                                                    # breakaway: close in top third
        b["o"][j], b["h"][j], b["l"][j], b["c"][j] = 100.0, 105.0, 99.9, 104.9
        b["v"][j] = 250.0
        e = vfeat.events(b, vfeat.features(b, "1d"))
        self.assertTrue(e["BAWAY_UP"][j])
        self.assertFalse(e["BCLX"][j])
        self.assertFalse(e["SP3_UP"][j])                           # 2.5x: SP2 only
        self.assertTrue(e["SP2_UP"][j])

    def test_donchian_volume_split(self):
        b = scenario()
        for i, vol in ((300, 100.0), (330, 200.0)):
            b["o"][i], b["c"][i], b["h"][i], b["l"][i] = 100.0, 101.0 + (i - 300) * 0.01, 101.2 + (i - 300) * 0.01, 99.9
            b["v"][i] = vol
        e = vfeat.events(b, vfeat.features(b, "1d"))
        self.assertTrue(e["DON_UP_N"][300] and not e["DON_UP_V"][300])      # rvadj 1.0 < 1.5
        self.assertTrue(e["DON_UP_V"][330] and not e["DON_UP_N"][330])      # rvadj 2.0 >= 1.5

    def test_absorption_and_no_demand(self):
        n = 400
        c = np.concatenate([np.linspace(130, 100, 300), 100 + np.tile([0.0, 0.2], 50)])
        b = bars_from(c, spread=0.5)
        b["o"][300:] = c[299:-1]
        i = 330
        b["h"][i], b["l"][i] = b["c"][i] + 0.05, b["c"][i] - 0.05    # tiny range
        b["v"][i] = 300.0
        f = vfeat.features(b, "1d")
        self.assertLessEqual(f["rr"][i], 0.8)
        e = vfeat.events(b, f)
        self.assertFalse(e["ABS_LOW"][i])                            # context DOWN needs c[i-1] < c[i-11]: flat alternation -> no
        b["c"][i - 1] = 99.0                                          # c[i-1] below c[i-11] (about 100.0/100.2)
        e = vfeat.events(b, vfeat.features(b, "1d"))
        self.assertTrue(e["ABS_LOW"][i])

    def test_no_lookahead(self):
        rng = np.random.default_rng(7)
        c = 100 + np.cumsum(rng.normal(0, 1, 700))
        v = rng.lognormal(0, 0.5, 700) * 100
        tbv = v * rng.uniform(0.3, 0.7, 700)
        b = bars_from(c, v=v, tbv=tbv, spread=0.4)
        e1 = vfeat.events(b, vfeat.features(b, "4h"))
        f1 = vfeat.features(b, "4h")
        b2 = {k: x.copy() for k, x in b.items()}
        for k in ("o", "h", "l", "c", "v", "tbv"):
            b2[k][500:] = b2[k][500:] * rng.uniform(0.5, 2.0, 200)
        b2["h"][500:] = np.maximum(b2["h"][500:], np.maximum(b2["o"][500:], b2["c"][500:]))
        b2["l"][500:] = np.minimum(b2["l"][500:], np.minimum(b2["o"][500:], b2["c"][500:]))
        e2 = vfeat.events(b2, vfeat.features(b2, "4h"))
        for k in vfeat.EVENT_NAMES:
            self.assertTrue(np.array_equal(e1[k][:500], e2[k][:500]), k)
        self.assertGreater(sum(int(e1[k].sum()) for k in vfeat.EVENT_NAMES), 20)

    def test_warmup_blocks_early_events(self):
        b = scenario()
        b["v"][100] = 1000.0
        e = vfeat.events(b, vfeat.features(b, "1d"))
        self.assertFalse(e["SP3_UP"][:vfeat.W].any() or e["SP3_DN"][:vfeat.W].any())

    def test_rsi_cross_events(self):
        c = np.concatenate([np.linspace(100, 90, 200), [91, 92, 100, 111, 125, 140]])
        b = bars_from(c, spread=0.1)
        f = vfeat.features(b, "1d")
        e = vfeat.events(b, f)
        r = f["rsi"]
        i60 = int(np.argmax((np.concatenate([[np.nan], r[:-1]]) < 60) & (r >= 60) & (np.arange(len(r)) >= vfeat.W)))
        self.assertTrue(e["R60U_N"][i60] or e["R60U_V"][i60])
        self.assertEqual(int(e["R60U_N"][i60]) + int(e["R60U_V"][i60]), 1)   # exactly one volume bucket


class TestTimeKeys(unittest.TestCase):
    def test_keys(self):
        t = np.array([vdata.ms(2026, 10, 9) + 17 * vdata.HOUR, vdata.ms(2026, 10, 10), vdata.ms(2026, 10, 11) + 3 * vdata.HOUR])
        k = vfeat.slot_keys({"t": t}, "4h")
        self.assertEqual(list(k["weekday"]), [4, 5, 6])               # Fri, Sat, Sun
        self.assertEqual(list(k["weekend"]), [False, True, True])
        self.assertEqual(list(k["slot"]), [4, 0, 0])
        self.assertEqual(list(k["sg"]), [2, 0, 0])

    def test_resample_complete_buckets_only(self):
        h = 3600000
        t = np.array([i * h for i in range(8)] + [9 * h, 10 * h, 11 * h, 12 * h], dtype=np.int64)   # hour 8 missing
        x = np.arange(len(t), dtype=float)
        b = {"t": t, "o": x, "h": x + 1, "l": x - 1, "c": x + 0.5, "v": np.ones(len(t)), "tbv": np.ones(len(t)) * 0.5}
        r = vdata.resample(b, 4)
        self.assertEqual(list(r["t"]), [0, 4 * h])                    # bucket 8..11 incomplete (8 missing); 12.. incomplete
        self.assertEqual(r["v"][0], 4.0)
        self.assertEqual(r["h"][1], 8.0)                              # max of h over bars 4..7 = 7 + 1
        self.assertEqual(r["c"][0], 3.5)

    def test_funding_window_is_open_closed(self):
        F = vdata.Funding.__new__(vdata.Funding)
        F.times = [8, 16, 24]
        F.cum = [0.0, 0.1, 0.3, 0.6]
        self.assertAlmostEqual(F.sum(0, 8), 0.1)                       # settlement at t1 counts
        self.assertAlmostEqual(F.sum(8, 16), 0.2)                      # settlement at t0 does not
        self.assertAlmostEqual(F.sum(8, 8), 0.0)
        t = np.array([0, 8, 16, 24])
        self.assertAlmostEqual(float(F.window(t, np.array([1]), np.array([3]))[0]), 0.5)

    def test_holdout_sealed(self):
        with self.assertRaises(PermissionError):
            vdata.load_1d(end_ms=vdata.VALID_END_MS + 1)
        with self.assertRaises(PermissionError):
            vdata.load_4h(end_ms=vdata.ms(2026, 10, 1))


class TestStats(unittest.TestCase):
    def test_rc_matches_stats_lite(self):
        import stats_lite
        rng = np.random.default_rng(3)
        m = 600
        fwd = rng.normal(0, 1, m)
        ev1 = (rng.random(m) < 0.1)
        ev2 = (rng.random(m) < 0.2)
        fwd = fwd + 0.8 * ev1                                       # event 1 has a real +0.8 effect
        EV = np.array([ev1, ev2])
        VAL = np.stack([fwd[None, :], fwd[None, :]]).reshape(2, 1, m)
        r = vstats.rc_family(EV, VAL, block=10, min_n=5, reps=1000, seed=1)
        items = [{"name": "a", "ev": [int(x) for x in ev1], "val": list(fwd), "sign": 1, "min_n": 5},
                 {"name": "b", "ev": [int(x) for x in ev2], "val": list(fwd), "sign": 1, "min_n": 5}]
        ref = stats_lite.block_boot_family(items, m, 10, reps=1000, seed=1)
        for k in range(2):
            self.assertEqual(int(r["n"][k]), ref[k]["n"])
            self.assertAlmostEqual(float(r["stat"][k, 0]), ref[k]["stat"], places=9)
            self.assertAlmostEqual(float(r["sd"][k, 0]) / ref[k]["sd"], 1.0, delta=0.12)
        self.assertLess(r["p_raw_cont"][0, 0], 0.01)                # real effect detected
        self.assertGreater(r["p_raw_cont"][1, 0], 0.05)

    def test_rc_false_positive_rate_under_null(self):
        rng = np.random.default_rng(11)
        hits = 0
        trials = 30
        for s in range(trials):
            m = 400
            fwd = rng.normal(0, 1, (1, 3, m))
            fwd = np.repeat(fwd, 6, axis=0)
            EV = rng.random((6, m)) < rng.uniform(0.05, 0.3, (6, 1))
            r = vstats.rc_family(EV, fwd, block=8, min_n=10, reps=300, seed=s)
            if min(r["p_adj_cont"].min(), r["p_adj_rev"].min()) < 0.10:
                hits += 1
        self.assertLessEqual(hits / trials, 0.25)                   # nominal 0.10 (+ sampling noise at 30 trials)

    def test_contrast_detects_difference(self):
        rng = np.random.default_rng(5)
        m = 2000
        a = rng.random(m) < 0.1
        bb = (~a) & (rng.random(m) < 0.1)
        val = rng.normal(0, 1, m) + 1.0 * a
        r = vstats.contrast(a, bb, val, block=5, reps=500, seed=2)
        self.assertGreater(r["lo"], 0)
        self.assertLess(r["p_two"], 0.01)
        val0 = rng.normal(0, 1, m)
        r0 = vstats.contrast(a, bb, val0, block=5, reps=500, seed=2)
        self.assertLess(r0["lo"], 0)
        self.assertGreater(r0["hi"], 0)

    def test_pooled_contrast_matches_single_pair_and_pools_by_count(self):
        rng = np.random.default_rng(9)
        m = 1500
        a = rng.random(m) < 0.1
        bb = (~a) & (rng.random(m) < 0.1)
        val = rng.normal(0, 1, m) + 0.5 * a
        single = vstats.contrast(a, bb, val, block=5, reps=400, seed=3)
        pooled = vstats.pooled_contrast(a.astype(float), a * val, bb.astype(float), bb * val, 5, reps=400, seed=3)
        self.assertAlmostEqual(single["diff"], pooled["diff"], places=12)
        self.assertAlmostEqual(single["lo"], pooled["lo"], places=12)
        self.assertEqual(single["nA"], pooled["nA"])
        # pooling two pairs weights by instance counts: A1 (n=2, mean 1), A2 (n=1, mean 4) -> pooled mean A = (2*1+4)/3 = 2; B: (n=1, 0), (n=1, 2) -> 1
        cA = np.array([2.0, 1.0, 0, 0, 0, 0]); sA = np.array([2.0, 4.0, 0, 0, 0, 0])
        cB = np.array([0, 0, 1.0, 1.0, 0, 0]); sB = np.array([0, 0, 0.0, 2.0, 0, 0])
        r = vstats.pooled_contrast(cA, sA, cB, sB, 2, reps=50, seed=1)
        self.assertAlmostEqual(r["meanA"], 2.0)
        self.assertAlmostEqual(r["meanB"], 1.0)
        self.assertAlmostEqual(r["diff"], 1.0)

    def test_pooled_contrast_one_sided_p(self):
        rng = np.random.default_rng(10)
        m = 3000
        a = (rng.random(m) < 0.1).astype(float)
        bb = ((a == 0) & (rng.random(m) < 0.1)).astype(float)
        good = vstats.pooled_contrast(a, a * (rng.normal(0, 1, m) + 1.0), bb, bb * rng.normal(0, 1, m), 5, reps=500, seed=1)
        null = vstats.pooled_contrast(a, a * rng.normal(0, 1, m), bb, bb * rng.normal(0, 1, m), 5, reps=500, seed=1)
        self.assertLess(good["p_one"], 0.01)
        self.assertGreater(null["p_one"], 0.02)

    def test_mean_ci_and_bh(self):
        ev = np.ones(500, dtype=bool)
        val = np.full(500, 2.0)
        m, lo, hi = vstats.mean_ci(ev, val, 5, reps=200)
        self.assertEqual((m, lo, hi), (2.0, 2.0, 2.0))
        # sorted p .01,.03,.04,.5 (m=4): p*m/rank = .04, .06, .05333, .5; step-up min from the top -> .04, .05333, .05333, .5
        q = vstats.bh_qvalues([0.01, 0.04, 0.03, 0.5])
        self.assertTrue(np.allclose(q, [0.04, 0.16 / 3, 0.16 / 3, 0.5]))

    def test_mde(self):
        self.assertAlmostEqual(vstats.mde(1.0, 100), (1.645 + 0.8416) / 10, places=6)


class TestBoundaries(unittest.TestCase):
    def test_clv_thresholds_one_third_two_thirds(self):
        b = scenario()
        i = 300
        for clv, bclx, baway in ((0.30, True, False), (0.40, False, False), (0.60, False, False), (0.70, False, True)):
            bb = {k: x.copy() for k, x in b.items()}
            lo, hi = 99.9, 103.0
            bb["h"][i], bb["l"][i] = hi, lo
            bb["c"][i] = lo + clv * (hi - lo)
            bb["o"][i] = 100.0
            bb["v"][i] = 300.0
            e = vfeat.events(bb, vfeat.features(bb, "1d"))
            self.assertEqual(bool(e["BCLX"][i]), bclx, clv)
            self.assertEqual(bool(e["BAWAY_UP"][i]), baway, clv)

    def test_breakout_uses_band_of_previous_bar(self):
        found = False
        for jump in np.arange(0.2, 1.5, 0.02):
            b = scenario()
            i = 300
            b["c"][i] = 100.1 + jump
            b["h"][i] = b["c"][i] + 0.1
            b["o"][i] = 100.0
            f = vfeat.features(b, "1d")
            if f["up_prev"][i] < b["c"][i] < f["bb_up"][i]:       # above last bar's band, below its own band
                found = True
                self.assertTrue(vfeat.events(b, f)["BBALL_UP"][i])
                break
        self.assertTrue(found)

    def test_session_group_boundaries(self):
        t = np.array([s * 4 * 3600000 for s in range(6)], dtype=np.int64)
        self.assertEqual(list(vfeat.slot_keys({"t": t}, "4h")["sg"]), [0, 0, 1, 1, 2, 2])

    def test_rv_adj_uses_median_not_mean(self):
        n = 300
        v = np.full(n, 100.0)
        v[200 - 6 * 3] = 10000.0                                     # one outlier among the 20 same-slot priors of bar 200
        r = vfeat.rv_adj(v, "4h")
        self.assertAlmostEqual(r[200], 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
