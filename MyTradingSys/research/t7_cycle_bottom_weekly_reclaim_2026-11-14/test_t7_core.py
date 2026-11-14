"""Synthetic-bar tests for T7. Never read the data cache."""
import sys
import pathlib
import unittest
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import t7_core as core  # noqa: E402
import t7_stats as st  # noqa: E402

DAY = core.DAY
MON0 = 18267            # epoch day of Monday 2020-01-06
assert (MON0 + 3) % 7 == 0


def make_seg(closes, name="X", final=True, opens=None, highs=None, lows=None, start=MON0):
    c = np.asarray(closes, float)
    o = np.r_[c[0], c[:-1]] if opens is None else np.asarray(opens, float)
    h = np.maximum(o, c) * 1.005 if highs is None else np.asarray(highs, float)
    l = np.minimum(o, c) * 0.995 if lows is None else np.asarray(lows, float)
    ms = (start + np.arange(len(c))) * DAY
    rows = np.c_[ms, o, h, l, c]
    return core.Seg(name, rows, final=final, pull_ms=(start + len(c) + 5) * DAY)


def bottom_path(spike_at=None, spike_val=90.0, total=560, flat_until=None):
    """rise 100 -> 200 over 399 days, fall to 80 over 35 days, flat 80, optional one-day close at spike_at."""
    up = np.linspace(100, 200, 399)
    down = np.linspace(200, 80, 36)[1:]
    flat = np.full(total - len(up) - len(down), 80.0)
    c = np.r_[up, down, flat]
    if spike_at is not None:
        c[spike_at] = spike_val
    return c


# first Sunday index after the fall: day 399+35=434 is flat; weeks are Mon..Sun so Sundays are 6,13,...
SUN = 6 + 7 * 70         # Sunday index 496, inside the flat part
assert SUN % 7 == 6


class TestSignals(unittest.TestCase):
    def test_no_signal_without_cross(self):
        s = make_seg(bottom_path())
        self.assertEqual(core.events(s), [])

    def test_sunday_spike_signals_on_monday_never_on_sunday(self):
        # a one-day Sunday spike lifts the weekly close above SMA10: event for that week, entry the NEXT Monday
        s = make_seg(bottom_path(spike_at=SUN, spike_val=88.0))
        ev = core.events(s)
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]["s"], SUN)
        self.assertEqual(ev[0]["d0"], SUN + 1)
        self.assertEqual((int(s.ms[ev[0]["d0"]]) // DAY + 3) % 7, 0)   # entry bar is a Monday
        # the same spike on a Monday-Saturday day does not change that week's weekly close -> no event from it
        s2 = make_seg(bottom_path(spike_at=SUN - 3, spike_val=88.0))
        self.assertEqual(core.events(s2), [])
        # a spike on the Monday after the week (d0) cannot create an event for the week before it
        s3 = make_seg(bottom_path(spike_at=SUN + 1, spike_val=88.0))
        self.assertEqual([e for e in core.events(s3) if e["s"] == SUN], [])

    def test_no_lookahead_truncation(self):
        full = make_seg(bottom_path(spike_at=SUN, spike_val=88.0, total=560))
        trunc = make_seg(bottom_path(spike_at=SUN, spike_val=88.0, total=560)[:SUN + 1])
        ef = [e for e in core.events(full) if e["s"] <= SUN]
        et = core.events(trunc)          # truncated data has no Monday after SUN: cannot fire; all earlier agree
        self.assertEqual([e for e in ef if e["s"] < SUN], et)
        # and the event at SUN uses nothing after SUN: change every later bar, event at SUN unchanged
        c = bottom_path(spike_at=SUN, spike_val=88.0, total=560)
        c[SUN + 1:] *= 3.0
        ev = [e for e in core.events(make_seg(c)) if e["s"] == SUN]
        self.assertEqual(len(ev), 1)

    def test_entry_is_next_open_not_signal_close(self):
        c = bottom_path(spike_at=SUN, spike_val=88.0)
        o = np.r_[c[0], c[:-1]]
        o[SUN + 1] = 77.0
        s = make_seg(c, opens=o)
        t = core.trade_at(s, SUN + 1)
        self.assertEqual(t["entry_px"], 77.0)

    def test_dd_depth_threshold(self):
        # max close in the prior 730d is 200; 0.45 x 200 = 90
        c = bottom_path()
        s = make_seg(c)
        self.assertTrue(s.dd_state(SUN, 90.0))
        self.assertFalse(s.dd_state(SUN, 90.01))

    def test_alive_rule_365(self):
        s = make_seg(bottom_path())
        self.assertFalse(s.alive_at(363))
        self.assertTrue(s.alive_at(364))

    def test_cooldown_28_days(self):
        c = bottom_path(total=700)
        # two reclaim weeks 2 weeks apart: spikes on consecutive-but-one Sundays; weekly close falls back between
        a, b = SUN, SUN + 14
        c[a] = 88.0
        c[b] = 88.0
        ev = core.events(make_seg(c))
        self.assertEqual([e["s"] for e in ev], [a])
        # 5 weeks apart: both fire
        c2 = bottom_path(total=700)
        c2[a] = 88.0
        c2[a + 35] = 88.0
        ev2 = core.events(make_seg(c2))
        self.assertEqual([e["s"] for e in ev2], [a, a + 35])

    def test_gap_splits_segments_and_no_trade_spans_hole(self):
        import tempfile
        c = bottom_path(total=560)
        ms = (MON0 + np.arange(len(c))) * DAY
        rows = np.c_[ms, np.r_[c[0], c[:-1]], c * 1.005, c * 0.995, c]
        rows = np.delete(rows, np.arange(500, 520), axis=0)       # 20-day hole
        tmp = pathlib.Path(tempfile.mkdtemp()) / "HOLEUSDT.csv"
        with open(tmp, "w") as f:
            f.write("ts,open,high,low,close\n")
            for r in rows:
                f.write("%d,%f,%f,%f,%f\n" % tuple(r))
        segs = core.load_segments(tmp, "HOLE")
        self.assertEqual(len(segs), 2)
        self.assertTrue(segs[0].ended)             # the pre-hole segment ends at the hole
        self.assertEqual(segs[0].seg_id, 0)


class TestSimulator(unittest.TestCase):
    def flat_seg(self, n=420, px=100.0, **kw):
        return make_seg(np.full(n, px), **kw)

    def test_fee_arithmetic_from_fees_py(self):
        import fees
        self.assertAlmostEqual(core.FEE_RT, 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13)
        self.assertAlmostEqual(core.FEE_RT, 0.0012)
        s = self.flat_seg(h=None) if False else make_seg(np.full(420, 100.0), highs=np.full(420, 100.0),
                                                         lows=np.full(420, 100.0))
        t = core.trade_at(s, 300)
        self.assertAlmostEqual(t["gross"], 0.0)
        self.assertAlmostEqual(t["net"], -0.0012)
        self.assertAlmostEqual(t["risk"], 0.10)      # ATR 0 -> floor 10%
        self.assertAlmostEqual(t["fee_R"], 0.0012 / 0.10)
        self.assertAlmostEqual(t["net_R"], -0.012)
        self.assertEqual(t["days"], 28)
        self.assertEqual(t["exit_reason"], "TIME")

    def test_exit_is_close_of_day_27_after_entry(self):
        c = np.full(420, 100.0)
        c[300 + 27] = 110.0
        c[300 + 28] = 50.0
        s = make_seg(c, opens=np.full(420, 100.0), highs=np.full(420, 111.0), lows=np.full(420, 99.0))
        t = core.trade_at(s, 300)
        self.assertEqual(t["exit_px"], 110.0)
        self.assertAlmostEqual(t["gross"], 0.10)

    def test_stop_wins_tie(self):
        # day 305: low pierces the 10% stop (90) while the close is 120 and day 327 close would be +20%
        n = 420
        c = np.full(n, 100.0)
        o = np.full(n, 100.0)
        h = np.full(n, 100.5)
        l = np.full(n, 99.5)
        l[305] = 89.0
        c[305] = 120.0
        h[305] = 121.0
        c[327:] = 120.0
        s = make_seg(c, opens=o, highs=h, lows=l)
        t = core.trade_at(s, 300)
        self.assertEqual(t["exit_reason"], "STOP")
        self.assertAlmostEqual(t["exit_px"], 90.0)
        self.assertAlmostEqual(t["gross"], -0.10)
        self.assertAlmostEqual(t["net_R"], (-0.10 - core.FEE_RT) / 0.10)

    def test_stop_gap_fills_at_open(self):
        n = 420
        c, o, h, l = np.full(n, 100.0), np.full(n, 100.0), np.full(n, 100.5), np.full(n, 99.5)
        o[305], l[305], c[305], h[305] = 80.0, 79.0, 85.0, 86.0
        s = make_seg(c, opens=o, highs=h, lows=l)
        t = core.trade_at(s, 300)
        self.assertEqual(t["exit_reason"], "STOP-GAP")
        self.assertAlmostEqual(t["exit_px"], 80.0)

    def test_stop_wide_atr_beats_floor(self):
        n = 420
        c = np.full(n, 100.0)
        h = np.full(n, 112.0)
        l = np.full(n, 88.0)          # TR 24 each day -> ATR 24, 3 x ATR / 100 = 72% > 10%
        s = make_seg(c, opens=np.full(n, 100.0), highs=h, lows=l)
        t = core.trade_at(s, 300)
        self.assertAlmostEqual(t["risk"], 0.72, places=6)
        self.assertGreaterEqual(t["risk"], core.MIN_STOP)

    def test_incomplete_window_skipped_unless_ended(self):
        s = make_seg(np.full(420, 100.0))
        self.assertIsNone(core.trade_at(s, 410) if not s.ended else None)
        e = make_seg(np.full(420, 100.0), final=False)
        t = core.trade_at(e, 410)
        self.assertEqual(t["exit_reason"], "ENDED")
        self.assertEqual(t["exit_ts"], int(e.ms[-1]))

    def test_funding_window_and_not_in_data(self):
        s = make_seg(np.full(420, 100.0))
        e0 = int(s.ms[300])
        ts = np.arange(e0 - 3 * 28800000, e0 + 30 * DAY, 28800000)
        f = core.Funding(ts, np.full(len(ts), 0.0001))
        t = core.trade_at(s, 300, f)
        self.assertEqual(t["funding_rule"], "REAL")
        self.assertAlmostEqual(t["funding"], 0.0001 * 28 * 3)      # prints in (entry, end of day 27]
        t2 = core.trade_at(s, 300, None)
        self.assertEqual(t2["funding_rule"], "NOT_IN_DATA")
        self.assertEqual(t2["funding"], 0.0)


class TestStats(unittest.TestCase):
    def fake(self, vals, week0=2600):
        rows = []
        for i, v in enumerate(vals):
            wi = week0 + i // 3
            rows.append(dict(coin="C%d" % (i % 5), net_R=v, net=v * 0.1, week_i=wi, iso_week="2025-W%02d" % (wi % 52 + 1),
                             entry_ts=(wi * 7 - 3) * DAY, days=28))
        return rows

    def test_planted_edge_detected(self):
        rng = np.random.default_rng(5)
        rows = self.fake(0.6 + 0.5 * rng.standard_normal(300))
        b = st.block_bootstrap(rows, "net_R", 1000, 1114)
        self.assertGreater(b["ci_low"], 0.3)

    def test_no_edge_reads_about_zero(self):
        rng = np.random.default_rng(6)
        rows = self.fake(0.5 * rng.standard_normal(300))
        b = st.block_bootstrap(rows, "net_R", 1000, 1114)
        self.assertLess(abs(b["mean"]), 0.12)
        self.assertLess(b["ci_low"], 0.0)
        self.assertGreater(b["ci_high"], 0.0)

    def test_placebo_planted_and_null(self):
        real = [1.0] * 120
        null_c = [np.random.default_rng(i).standard_normal(20) * 0.2 for i in range(120)]
        p = st.placebo_from_candidates(real, null_c, 500, 1114)
        self.assertGreater(p["real_mean"], p["p975"])
        same = [np.random.default_rng(i).standard_normal(20) for i in range(120)]
        rv = [float(np.random.default_rng(1000 + i).standard_normal()) for i in range(120)]
        p2 = st.placebo_from_candidates(rv, same, 500, 1114)
        self.assertLess(abs(p2["excess"]), 0.3)

    def test_ex_best_weeks_and_episodes(self):
        rows = self.fake([5.0, 5.0, 5.0, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1])
        self.assertLess(st.ex_best_weeks(rows, 1)["mean"], 0.0)
        eps = st.episodes(rows)
        self.assertEqual(len(eps), 1)          # all within 28 days chain together

    def test_loyo_and_top_coin(self):
        rows = self.fake([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        for i, r in enumerate(rows):
            r["iso_week"] = ("2024" if i < 3 else "2025") + r["iso_week"][4:]
        self.assertTrue(all(x["mean"] > 0 for x in st.leave_one_year_out(rows).values()))
        self.assertEqual(len(st.top_coin_removal(rows, 3)), 3)

    def test_smoothing_needs_10_days(self):
        raw = [("d%02d" % i, "BASE") for i in range(12)] + [("e%02d" % i, "BEAR") for i in range(12)]
        sm = core.smooth_states(raw)
        self.assertEqual(sm["e00"], "BASE")
        self.assertEqual(sm["e08"], "BASE")
        self.assertEqual(sm["e09"], "BEAR")


if __name__ == "__main__":
    unittest.main()
