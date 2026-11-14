"""Synthetic-bar tests for T8 (no real data is read). Run: python -m pytest test_t8_core.py -q  (or python test_t8_core.py)."""
import sys
import pathlib
import unittest
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t8_core as core  # noqa: E402
import t8_stats as st  # noqa: E402

DAY = core.DAY
T0 = core._ms(2021, 1, 4)          # a Monday


def make_rows(closes, opens=None, hi_pad=0.002, lo_pad=0.002, t0=T0, bar=DAY):
    c = np.asarray(closes, float)
    o = np.r_[c[0], c[:-1]] if opens is None else np.asarray(opens, float)
    h = np.maximum(o, c) * (1 + hi_pad)
    l = np.minimum(o, c) * (1 - lo_pad)
    ts = t0 + np.arange(len(c)) * bar
    return np.c_[ts, o, h, l, c]


def make_seg(closes, tf="1d", gate=True, alive=True, **kw):
    rows = make_rows(closes, bar=core.CELLS[tf]["bar"], **kw)
    s = core.Seg("TST", tf, rows, is_final=True, ended=False)
    if gate:
        s.gate[:] = True
    if alive:
        s.alive[:] = True
    return s


def dip_series(n_flat=40, dip=0.80, flat=100.0):
    """Flat-ish noise, then a drop below the lower band at one bar and a close back inside."""
    rng = np.random.default_rng(5)
    c = list(flat * (1 + 0.04 * rng.standard_normal(n_flat)))      # wide enough bands (width > 10%)
    return c


class TestIndicators(unittest.TestCase):
    def test_bollinger_worked_example(self):
        mid, up, lo = core.bollinger(np.array([8, 10, 10, 12, 14, 12.0]), n=4, k=2)
        self.assertAlmostEqual(up[5], 14.828427, places=5)
        self.assertAlmostEqual(lo[5], 9.171573, places=5)
        self.assertAlmostEqual(up[3], 12.828427, places=5)
        self.assertTrue(np.isnan(up[2]))

    def test_adx_hand_toy(self):
        H = np.array([10, 11, 12, 11, 13, 14, 13, 12, 11, 12, 13, 15, 14, 13, 12, 11, 12, 14, 15, 14.0])
        L = np.array([8, 9, 10, 9, 10, 12, 11, 10, 9, 10, 11, 12, 12, 11, 10, 9, 10, 11, 13, 12.0])
        C = np.array([9, 10, 11, 10, 12, 13, 12, 11, 10, 11, 12, 14, 13, 12, 11, 10, 11, 13, 14, 13.0])
        a = core.adx_wilder(H, L, C, n=3)
        self.assertAlmostEqual(a[5], 58.586, places=2)
        self.assertAlmostEqual(a[6], 47.301, places=2)
        self.assertAlmostEqual(a[19], 34.938, places=2)
        self.assertTrue(np.isnan(a[4]))

    def test_atr_wilder(self):
        c = np.array([10.0, 11, 12, 11, 13, 12, 14, 13, 15, 14, 16, 15, 17, 16, 18])
        h, l = c + 1, c - 1
        a = core.wilder_atr(h, l, c, n=3)
        pc = np.r_[c[0], c[:-1]]
        tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
        self.assertAlmostEqual(a[2], tr[:3].mean())
        self.assertAlmostEqual(a[3], (a[2] * 2 + tr[3]) / 3)

    def test_range30(self):
        c = np.full(40, 100.0)
        h, l = c + 5, c - 5
        r = core.range30(h, l, c)
        self.assertAlmostEqual(r[39], 0.10)
        self.assertTrue(np.isnan(r[28]))


class TestSignalAndEntry(unittest.TestCase):
    def setUp(self):
        # 30 noisy bars, a crash bar below the lower band, then a close back above it
        rng = np.random.default_rng(11)
        base = 100 * (1 + 0.035 * rng.standard_normal(40))
        base[-1] = 100.0
        self.closes = list(base) + [70.0, 98.0, 99.0, 100.0, 101.0, 102.0]
        self.seg = make_seg(self.closes)

    def test_first_reentry_only_and_entry_at_next_open(self):
        seg = self.seg
        lo = seg.lo
        self.assertTrue(seg.c[40] < lo[40])                     # outside close
        self.assertTrue(seg.c[41] > lo[41])                     # back inside
        sig = [s["t"] for s in core.find_signals(seg, 1)]
        self.assertIn(41, sig)
        self.assertNotIn(42, sig)                               # second bar inside: not the first re-entry
        plan, why = core.make_entry(seg, 41, 1)
        self.assertEqual(plan["e"], 42)
        self.assertEqual(plan["entry"], float(seg.o[42]))

    def test_lookahead_signals_use_bars_through_t_only(self):
        rng = np.random.default_rng(3)
        c = 100 * np.exp(np.cumsum(0.03 * rng.standard_normal(600)))
        full = make_seg(c)
        for side in (1, -1):
            full_sig = {s["t"] for s in core.find_signals(full, side)}
            for T in (150, 301, 444):
                part = make_seg(c[:T])
                part_sig = {s["t"] for s in core.find_signals(part, side)}
                self.assertEqual(part_sig, {t for t in full_sig if t < T})
        self.assertTrue(len(full_sig) > 5)

    def test_lookahead_check_catches_a_leaky_variant(self):
        """Mutation check: a variant that peeks at close[t+1] changes when the NEXT bar changes, the real one does not."""
        rng = np.random.default_rng(3)
        c = 100 * np.exp(np.cumsum(0.03 * rng.standard_normal(300)))
        a = make_seg(c)
        t = int(np.where(a.raw_reentry(1))[0][0])
        c2 = c.copy()
        c2[t + 1] = c[t] * (0.5 if c[t + 1] > c[t] else 1.5)       # flip the next bar's direction
        b = make_seg(c2)
        self.assertEqual(bool(a.raw_reentry(1)[t]), bool(b.raw_reentry(1)[t]))        # honest: unaffected by bar t+1

        def leaky(seg):
            r = seg.raw_reentry(1).copy()
            r[:-1] &= seg.c[1:] > seg.c[:-1]                    # peeks at the next close
            return r
        self.assertNotEqual(bool(leaky(a)[t]), bool(leaky(b)[t]))                     # the check would catch the leak

    def test_cooldown(self):
        seg = self.seg
        n = seg.n
        # force the raw signal on bars 41 and 45 (same side); cooldown 10 keeps only the first
        seg._raw[1] = np.zeros(n, bool)
        seg._raw[1][[31, 35, 42]] = True
        seg.width[:] = 0.2
        seg.atr[:] = 1.0
        got = [s["t"] for s in core.find_signals(seg, 1)]
        self.assertEqual(got, [31, 42])

    def test_width_filter_blocks_narrow_bands(self):
        seg = self.seg
        seg._raw[1] = np.zeros(seg.n, bool)
        seg._raw[1][41] = True
        seg.atr[:] = 1.0
        seg.width[:] = 0.099
        self.assertEqual(core.find_signals(seg, 1), [])
        seg.width[:] = 0.101
        self.assertEqual([s["t"] for s in core.find_signals(seg, 1)], [41])

    def test_gate_and_alive_required(self):
        seg = self.seg
        seg._raw[1] = np.zeros(seg.n, bool)
        seg._raw[1][41] = True
        seg.atr[:] = 1.0
        seg.width[:] = 0.2
        seg.gate[:] = False
        self.assertEqual(core.find_signals(seg, 1), [])
        seg.gate[:] = True
        seg.alive[:] = False
        self.assertEqual(core.find_signals(seg, 1), [])

    def test_stop_floor_and_target_frozen(self):
        seg = self.seg
        plan, _ = core.make_entry(seg, 41, 1)
        self.assertLessEqual(plan["stop"], plan["entry"] * (1 - 0.015) + 1e-12)
        self.assertEqual(plan["target"], float(seg.up[41]))
        # stop = min(lowest low from the outside close through t - 0.5 ATR, floor)
        raw = float(seg.l[40:42].min()) - 0.5 * float(seg.atr[41])
        self.assertAlmostEqual(plan["stop"], min(raw, plan["entry"] * 0.985))

    def test_target_behind_is_skipped(self):
        seg = self.seg
        seg.o[42] = seg.up[41] * 1.01
        plan, why = core.make_entry(seg, 41, 1)
        self.assertIsNone(plan)
        self.assertEqual(why, "TARGET_BEHIND")


class TestSimulator(unittest.TestCase):
    def mk(self, ohlc):
        a = np.array([[T0 + i * DAY, *r] for i, r in enumerate(ohlc)], float)
        return core.Seg("TST", "1d", a)

    def test_stop_wins_ties(self):
        # entry bar 1 open 100; bar 1 touches both stop 95 and target 105
        s = self.mk([(100, 100, 100, 100), (100, 106, 94, 100), (100, 100, 100, 100)])
        k, px, why = core.simulate(s, 1, 1, 100.0, 95.0, 105.0, 2)
        self.assertEqual((why, px), ("STOP", 95.0))
        k, px, why = core.simulate(s, 1, -1, 100.0, 105.0, 95.0, 2)
        self.assertEqual((why, px), ("STOP", 105.0))

    def test_mutant_target_first_would_fail(self):
        s = self.mk([(100, 100, 100, 100), (100, 106, 94, 100), (100, 100, 100, 100)])

        def target_first(seg, e, side, entry, stop, target, last):
            for k in range(e, last + 1):
                if seg.h[k] >= target:
                    return k, target, "TARGET"
                if seg.l[k] <= stop:
                    return k, stop, "STOP"
            return last, seg.c[last], "TIME"
        self.assertEqual(target_first(s, 1, 1, 100.0, 95.0, 105.0, 2)[2], "TARGET")
        self.assertNotEqual(core.simulate(s, 1, 1, 100.0, 95.0, 105.0, 2)[2], "TARGET")

    def test_target_fill_and_gap_stop(self):
        s = self.mk([(100, 100, 100, 100), (100, 103, 99, 102), (102, 106, 101, 105)])
        self.assertEqual(core.simulate(s, 1, 1, 100.0, 95.0, 105.0, 2)[:3], (2, 105.0, "TARGET"))
        g = self.mk([(100, 100, 100, 100), (100, 101, 99, 100), (90, 91, 88, 89)])
        k, px, why = core.simulate(g, 1, 1, 100.0, 95.0, 110.0, 2)
        self.assertEqual((why, px), ("STOP_GAP", 90.0))                  # gap fills at the open, worse than the stop

    def test_time_exit_at_last_close(self):
        s = self.mk([(100, 100, 100, 100), (100, 101, 99, 100.5), (100.5, 101, 100, 100.7)])
        self.assertEqual(core.simulate(s, 1, 1, 100.0, 90.0, 110.0, 2), (2, 100.7, "TIME"))


class TestCosts(unittest.TestCase):
    def test_fee_constant_comes_from_fees_py(self):
        self.assertAlmostEqual(core.FEE_RT, 2 * core.fees.BINANCE_TAKER + core.fees.SLIPPAGE_RT_S13)
        self.assertAlmostEqual(core.FEE_RT, 0.0012, places=9)

    def test_fee_in_r_equals_fee_over_stop_pct(self):
        seg = TestSignalAndEntry()
        seg.setUp()
        trs = core.trades_for_seg(seg.seg, None)
        self.assertTrue(len(trs) >= 1)
        for t in trs:
            self.assertAlmostEqual(t["fee_R"], 0.0012 / t["stop_pct"])
            self.assertAlmostEqual(t["gross_R"] - t["fee_R"], t["nofund_R"])
            self.assertAlmostEqual(t["net_R"], t["net"] / t["stop_pct"])

    def test_funding_sign_window_and_no_imputation(self):
        ts = np.array([T0 + k * 8 * 3600000 for k in range(1, 20)], float)
        f = core.Funding(ts, np.full(19, 0.001))
        s, cov = f.sum_rate(T0 + 8 * 3600000, T0 + 32 * 3600000)   # prints 16h,24h,32h inside (entry, end]
        self.assertTrue(cov)
        self.assertAlmostEqual(s, 0.003)
        self.assertEqual(core.funding_part(f, T0 + 8 * 3600000, T0 + 32 * 3600000, 1)[0], s)       # long pays
        self.assertEqual(core.funding_part(f, T0 + 8 * 3600000, T0 + 32 * 3600000, -1)[0], -s)     # short receives
        s2, cov2 = f.sum_rate(T0, T0 + 24 * 3600000)             # first print (8h) is later than the entry: not covered
        self.assertEqual((s2, cov2), (0.0, False))
        s3, cov3 = f.sum_rate(T0 + 400 * 24 * 3600000, T0 + 401 * 24 * 3600000)
        self.assertEqual((s3, cov3), (0.0, False))               # not covered: 0, flagged, never imputed
        self.assertEqual(core.funding_part(None, T0, T0 + 1, 1), (0.0, False))

    def test_mirror_is_reflected_distances(self):
        seg = TestSignalAndEntry()
        seg.setUp()
        plan, _ = core.make_entry(seg.seg, 41, 1)
        plan["side"] = 1
        last, _ = core.window_status(seg.seg, plan["e"])
        m = core.run_leg(seg.seg, plan, -1, last, None)
        self.assertAlmostEqual(m["stop"], plan["entry"] * (1 + plan["stop_pct"]))
        self.assertAlmostEqual(m["target"], plan["entry"] * (1 - plan["tgt_pct"]))


class TestWindows(unittest.TestCase):
    def test_window_status(self):
        s = make_seg(np.linspace(100, 101, 100))
        self.assertEqual(core.window_status(s, 10), (29, "OK"))
        self.assertEqual(core.window_status(s, 95)[1], "INCOMPLETE")
        s.ended = True
        self.assertEqual(core.window_status(s, 95), (99, "ENDED"))
        s.is_final = False
        self.assertEqual(core.window_status(s, 95)[1], "GAP_SPAN")

    def test_luna_hole(self):
        n = 40
        t0 = core._ms(2022, 5, 1)
        rows = make_rows(np.full(n, 10.0), t0=t0)
        s = core.Seg("LUNA", "1d", rows)
        self.assertTrue(core.hole_hit(s, 5, 25))                         # spans 05-13
        self.assertFalse(core.hole_hit(s, 0, 8))
        s2 = core.Seg("BTC", "1d", rows)
        self.assertFalse(core.hole_hit(s2, 5, 25))

    def test_segments_split_on_gaps(self):
        rows = make_rows(np.linspace(1, 2, 30))
        rows = np.delete(rows, [10], axis=0)
        segs = core.build_segments("X", "1d", rows, universe_end_ms=int(rows[-1, 0]) + DAY)
        self.assertEqual([s.n for s in segs], [10, 19])
        self.assertFalse(segs[0].is_final)
        self.assertTrue(segs[1].is_final)

    def test_week_index_sunday_is_old_week(self):
        mon = core._ms(2023, 1, 2)                       # Monday
        sun = mon - DAY
        self.assertEqual(core.week_index(mon), core.week_index(sun) + 1)
        self.assertEqual(core.week_index(mon + 6 * DAY + 86399000), core.week_index(mon))
        self.assertEqual(core.iso_week_of(mon), "2023-W01")
        self.assertEqual(core.iso_week_of(sun), "2022-W52")

    def test_4h_day_map_uses_last_completed_day(self):
        t0 = core._ms(2023, 3, 1)
        rows = make_rows(np.full(12, 10.0), t0=t0, bar=core.HOUR4)
        s = core.Seg("X", "4h", rows)
        d1 = t0 // DAY
        core.attach_day_map(s, {d1 - 1: (True, True), d1: (False, True)})
        # bars of day d1 (opens 00..20h): close of the last bar (20h) is at the next midnight => completed day = d1
        self.assertTrue(s.gate[0] and s.gate[4])         # bar 0..4 close <= d1 + 20h: last completed is d1-1
        self.assertFalse(s.gate[5])                      # bar 5 (opens 20h) closes at midnight: day d1 completed -> False

    def test_smooth_cycle_needs_ten_days(self):
        raw = ["BASE"] * 12 + ["BULL"] * 5 + ["BASE"] * 3 + ["BULL"] * 10
        out = core.smooth_cycle(raw)
        self.assertEqual(out[8], "NA")
        self.assertEqual(out[9], "BASE")
        self.assertEqual(out[14], "BASE")                 # only 3 BULL days so far, prior state holds
        self.assertEqual(out[-1], "BULL")


# ---------------------------------------------------------------- planted edge / no edge on bars
SUB = 24


def ou_ohlc(n, kappa, sig, seed, mid=100.0):
    """Daily OHLC from SUB sub-steps per bar (continuous-looking paths so stop/target fills are not biased by jumps).
    Log price follows an OU process with per-bar mean reversion kappa and per-bar sd sig."""
    rng = np.random.default_rng(seed)
    k, sg = kappa / SUB, sig / np.sqrt(SUB)
    x = 0.0
    o = np.empty(n)
    h = np.empty(n)
    l = np.empty(n)
    c = np.empty(n)
    for i in range(n):
        path = np.empty(SUB)
        for j in range(SUB):
            x = x * (1 - k) + sg * rng.standard_normal()
            path[j] = x
        px = mid * np.exp(path)
        o[i] = mid * np.exp(path[0] - sg * 0.0) if i == 0 else c[i - 1]
        c[i] = px[-1]
        h[i] = max(px.max(), o[i])
        l[i] = min(px.min(), o[i])
    return np.c_[T0 + np.arange(n) * DAY, o, h, l, c]


def ou_seg(n, kappa, sig, seed):
    s = core.Seg("TST", "1d", ou_ohlc(n, kappa, sig, seed))
    s.gate[:] = True
    s.alive[:] = True
    return s


class TestEdgeDetection(unittest.TestCase):
    def all_trades(self, seg):
        return core.trades_for_seg(seg, None)

    def test_planted_mean_reversion_edge_is_detected(self):
        trs = []
        for sd in range(20, 28):
            trs += self.all_trades(ou_seg(1500, 0.25, 0.045, sd))
        self.assertGreater(len(trs), 200)
        g = np.array([t["gross_R"] for t in trs])
        d = np.array([t["net_R"] - t["m_net_R"] for t in trs])
        self.assertGreater(g.mean() / (g.std(ddof=1) / np.sqrt(len(g))), 3.0)
        self.assertGreater(d.mean(), 0.0)

    def test_no_edge_random_walk_reads_about_zero(self):
        trs = []
        for sd in range(40, 52):
            trs += self.all_trades(ou_seg(1500, 0.0, 0.03, sd))
        self.assertGreater(len(trs), 200)
        g = np.array([t["gross_R"] for t in trs])
        se = g.std(ddof=1) / np.sqrt(len(g))
        self.assertLess(abs(g.mean()), 3.2 * se)
        net = np.array([t["net_R"] for t in trs])
        self.assertLess(net.mean(), g.mean())            # costs only subtract

    def test_block_bootstrap_planted_and_null(self):
        rng = np.random.default_rng(1)
        wk = np.repeat(np.arange(200), 5)
        edge = rng.standard_normal(len(wk)) + 0.5
        res = st.block_boot(wk, edge, 600)
        self.assertGreater(res["ci_low"], 0.0)
        null = rng.standard_normal(len(wk))
        res0 = st.block_boot(wk, null, 600)
        self.assertLess(res0["ci_low"], 0.0 + 1e-9 + 0.2)
        self.assertLess(abs(res0["mean"]), 0.2)
        self.assertLess(res0["ci_low"], 0.0 + res0["ci_high"])

    def test_block_bootstrap_keeps_empty_weeks_and_is_deterministic(self):
        a = st.block_boot([0, 0, 5, 9], [1.0, 2.0, 3.0, 4.0], 300)
        b = st.block_boot([0, 0, 5, 9], [1.0, 2.0, 3.0, 4.0], 300)
        self.assertEqual(a, b)
        self.assertEqual(a["weeks"], 3)
        self.assertAlmostEqual(a["mean"], 2.5)

    def test_placebo_candidates_exclude_signal_and_respect_window_and_split(self):
        seg = ou_seg(1500, 0.0, 0.03, 9)
        trs = core.trades_for_seg(seg, None)
        tr = [t for t in trs if t["split"] == "DEV"][3]
        cands = st.candidate_bars(tr, window=True)
        self.assertNotIn(tr["sig_t"], cands)
        self.assertTrue(all(abs(seg.ms[i] - seg.ms[tr["sig_t"]]) <= 56 * DAY for i in cands))
        self.assertTrue(all(seg.ms[i] < core.DEV_END_MS for i in cands))
        g = st.candidate_bars(tr, window=False)
        self.assertTrue(len(g) >= len(cands))

    def test_placebo_null_excess_near_zero_on_random_walk(self):
        trs = []
        for sd in range(60, 66):
            seg = ou_seg(1500, 0.0, 0.03, sd)
            seg.ms = seg.ms + core._ms(2024, 1, 1) - T0       # put every bar in VAL
            trs += [t for t in core.trades_for_seg(seg, None)]
        for t in trs:
            t["split"] = "VAL"
        funds = {}
        r = st.placebo_eval(trs, funds, True, True, 1114, 300)
        self.assertGreater(r["n"], 100)
        self.assertLess(abs(r["excess"]), 0.15)
        self.assertLessEqual(r["p"], 1.0)


class TestVerdict(unittest.TestCase):
    base = dict(bar1=True, bar2=True, bar3=True, bar4=True, bar5=True, bar6=True, bar7=True, bar8=True, mirror_pos=True,
                sides_pos=True, worst_week_ok=True, kill_val_le0=False, kill_mirror_le0=False, kill_placebo=False)

    def v(self, **kw):
        b = dict(self.base)
        b.update(kw)
        return st.assemble_verdict(b)

    def test_vocabulary(self):
        self.assertEqual(self.v(), "PASS")
        self.assertEqual(self.v(holm_adj=0.2), "PASS MULTIPLICITY-FLAGGED")
        self.assertEqual(self.v(bar1=False, kill_val_le0=True), "UNDERPOWERED")      # never FAIL when underpowered
        self.assertEqual(self.v(kill_val_le0=True), "FAIL")
        self.assertEqual(self.v(mirror_pos=False, kill_mirror_le0=True), "FAIL")
        self.assertEqual(self.v(sides_pos=False), "SIDE-SPLIT")
        self.assertEqual(self.v(bar7=False), "FRAGILE")
        self.assertEqual(self.v(worst_week_ok=False), "FRAGILE")
        self.assertEqual(self.v(bar4=False), "FAIL")

    def test_holm(self):
        adj = st.holm({"a": 0.01, "b": 0.04})
        self.assertAlmostEqual(adj["a"], 0.02)
        self.assertAlmostEqual(adj["b"], 0.04)


if __name__ == "__main__":
    unittest.main(verbosity=1)
