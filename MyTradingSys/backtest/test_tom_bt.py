import sys
sys.dont_write_bytecode = True
"""Tests for tom_bt.py. Expected numbers are derived by hand from the stated rules (module docstring), not from the code."""
import os
import tempfile
import unittest
from array import array
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tom_bt as T  # noqa: E402


def mk(bars, t0=0):
    """bars: list of (o,h,l,c). Volumes 1, taker-buy 0.5."""
    o, h, l, c, v, tbv = (array("d") for _ in range(6))
    for a, b, d, e in bars:
        o.append(a); h.append(b); l.append(d); c.append(e); v.append(1.0); tbv.append(0.5)
    return T.Bars1m(t0, o, h, l, c, v, tbv)


LONG = dict(side="long", entry=100.0, stop=99.0, target=103.0)


def sim(bars, fees=T.FEES_DERIBIT, **kw):
    a = dict(LONG)
    a.update({k: kw.pop(k) for k in list(kw) if k in a})
    return T.sim_limit_trade(mk(bars), 0, a["side"], a["entry"], a["stop"], a["target"],
                             kw.get("fill_window", 5), kw.get("hold", 5), fees, kw.get("stop_first", True),
                             kw.get("slip", 0.0), through_ticks=kw.get("through_ticks", 0.0))


class TestSim(unittest.TestCase):
    def test_through_ticks_entry_and_target(self):
        # EXPECT: entry and target require the requested excursion beyond the limit.
        touch_entry = [(100.2, 100.5, 100.0, 100.3)]
        self.assertTrue(sim(touch_entry, through_ticks=0)["filled"])
        self.assertFalse(sim(touch_entry, through_ticks=1)["filled"])

        through_entry = [(100.2, 100.5, 99.0, 100.3), (100.3, 103.5, 100.1, 103.0)]
        self.assertTrue(sim(through_entry, stop=90.0, target=110.0, through_ticks=0)["filled"])
        self.assertTrue(sim(through_entry, stop=90.0, target=110.0, through_ticks=1)["filled"])

        # Entry trades through at 99; target touches 103 on bar 1, then trades through at 104 on bar 2.
        touch_target = [(99.9, 100.5, 99.0, 100.1), (100.1, 103.0, 100.0, 102.5),
                        (102.5, 104.0, 102.0, 103.5)]
        r = sim(touch_target, stop=90.0, through_ticks=1)
        self.assertEqual(r["reason"], "target")
        self.assertEqual(r["exit_i"], 2)

    def test_default_through_ticks_preserves_golden_result(self):
        bars = [(100.2, 100.5, 99.9, 100.3), (100.3, 103.5, 100.1, 103.0)]
        self.assertEqual(sim(bars), dict(filled=True, reason="target", gross_r=3.0, net_r=3.0,
                                          fee_r=0.0, fill_i=0, exit_i=1, bars_held=1, ambiguous=0))

    def test_long_target_fees(self):
        bars = [(100.2, 100.5, 99.9, 100.3), (100.3, 103.5, 100.1, 103.0)]
        r = sim(bars)
        self.assertEqual(r["reason"], "target")
        self.assertAlmostEqual(r["gross_r"], 3.0)
        self.assertAlmostEqual(r["net_r"], 3.0)  # maker entry + maker target = 0
        r2 = sim(bars, fees=T.FEES_ALL_TAKER)
        self.assertAlmostEqual(r2["net_r"], 3.0 - (0.0005 * 100 + 0.0005 * 103) / 1.0)  # 2.8985

    def test_stop_first_and_target_first(self):
        bars = [(100.2, 100.5, 99.9, 100.3), (100.3, 103.5, 98.9, 100.0)]
        r = sim(bars)
        self.assertEqual(r["reason"], "stop")
        self.assertAlmostEqual(r["gross_r"], -1.0)
        self.assertAlmostEqual(r["net_r"], -1.0 - 0.0005 * 99.0)  # -1.0495, taker stop
        self.assertEqual(r["ambiguous"], 1)
        r2 = sim(bars, stop_first=False)
        self.assertEqual(r2["reason"], "target")
        self.assertAlmostEqual(r2["gross_r"], 3.0)

    def test_gap_through_stop_fills_at_open(self):
        bars = [(100.2, 100.5, 99.9, 100.3), (98.0, 98.5, 97.5, 98.2)]
        r = sim(bars)
        self.assertEqual(r["reason"], "stop")
        self.assertAlmostEqual(r["gross_r"], -2.0)

    def test_timeout_exit_at_close(self):
        bars = [(100.2, 100.5, 99.9, 100.3), (100.3, 101.0, 99.5, 100.5), (100.5, 102.0, 99.6, 101.0),
                (101.0, 110.0, 90.0, 105.0)]
        r = sim(bars, hold=2)
        self.assertEqual(r["reason"], "timeout")
        self.assertAlmostEqual(r["gross_r"], 1.0)
        self.assertAlmostEqual(r["net_r"], 1.0 - 0.0005 * 101.0)
        self.assertEqual(r["bars_held"], 2)

    def test_fill_bar_stop_is_conservative(self):
        bars = [(100.2, 104.0, 98.5, 103.5)]  # touches E, stop and target in the fill bar -> stop
        r = sim(bars)
        self.assertEqual(r["reason"], "stop")
        self.assertEqual(r["exit_i"], 0)
        self.assertAlmostEqual(r["gross_r"], -1.0)

    def test_unfilled_no_fill_and_ran(self):
        bars = [(101.0, 101.5, 100.5, 101.2)] * 5
        r = sim(bars, fill_window=2)
        self.assertFalse(r["filled"])
        self.assertEqual(r["reason"], "no_fill")
        r2 = sim([(101.0, 103.5, 101.0, 103.0)])  # target reached without touching E
        self.assertFalse(r2["filled"])
        self.assertEqual(r2["reason"], "ran")

    def test_short_mirror(self):
        bars = [(99.8, 100.2, 99.5, 99.6), (99.6, 99.7, 96.9, 97.0)]
        r = sim(bars, side="short", stop=101.0, target=97.0)
        self.assertEqual(r["reason"], "target")
        self.assertAlmostEqual(r["gross_r"], 3.0)
        bars2 = [(99.8, 100.2, 99.5, 99.6), (99.6, 101.5, 99.5, 101.2)]
        r2 = sim(bars2, side="short", stop=101.0, target=97.0)
        self.assertEqual(r2["reason"], "stop")
        self.assertAlmostEqual(r2["gross_r"], -1.0)

    def test_slippage_on_stop(self):
        bars = [(100.2, 100.5, 99.9, 100.3), (100.3, 100.4, 98.9, 99.0)]
        r = sim(bars, slip=0.001)
        self.assertAlmostEqual(r["gross_r"], (99.0 - 0.001 * 99.0 - 100.0) / 1.0)  # -1.099

    def test_bad_geometry(self):
        r = sim([(100, 101, 99, 100)], stop=101.0)
        self.assertFalse(r["filled"])
        self.assertEqual(r["reason"], "bad_geometry")


def row(t, verdict="SETUP_FORMING", proof=5, d="long", zone="daily_val", zp=100.0, ztype="daily_val"):
    return dict(t=t, verdict=verdict, proof=proof, dir=d, setup="ct_long", zone=zone, zprice=zp, ztype=ztype,
                stop=99.0, target=103.0)


class TestSignals(unittest.TestCase):
    def test_episode_dedupe_and_break(self):
        rows = [row(0), row(900), row(1800), row(2700, verdict="WATCH"), row(3600), row(4500, zp=101.0)]
        ep = T.signals(rows, "episode")
        self.assertEqual([r["t"] for r in ep], [0, 3600, 4500])  # same key continues; WATCH breaks; new zone price = new
        self.assertEqual(len(T.signals(rows, "A")), 5)
        wl = T.signals(rows, "watch_episode")
        self.assertEqual([r["t"] for r in wl], [0, 4500])  # WATCH row continues the episode
        gap = [row(0), row(3000)]  # missing rows (> 1.5 steps) break the episode
        self.assertEqual(len(T.signals(gap, "episode")), 2)

    def test_p4_variant(self):
        rows = [row(0, verdict="WATCH", proof=3), row(900, verdict="WATCH", proof=4)]
        self.assertEqual([r["t"] for r in T.signals(rows, "p4_episode")], [900])


class TestRunVariant(unittest.TestCase):
    def test_one_at_a_time(self):
        # 1h zone (weekly_) -> fill window 480 bars; a fill on bar 0 then target on bar 1 frees the book at bar 1
        bars = [(100.2, 100.5, 99.9, 100.3), (100.3, 103.5, 100.1, 103.0)] + [(103, 104, 102, 103)] * 3
        b = mk(bars)
        s1 = row(0, ztype="weekly_poc")
        s2 = row(0.0, ztype="weekly_poc")  # same bar -> blocked
        s3 = row(120.0, ztype="weekly_poc")  # bar 2, after exit at bar 1 -> allowed (never touches E -> unfilled)
        tr = T.run_variant([s1, s2, s3], b)
        self.assertEqual(len(tr), 2)
        self.assertEqual(tr[0]["reason"], "target")
        self.assertEqual(tr[0]["zone_tf"], "1h")


class TestHelpers(unittest.TestCase):
    def test_zone_tf(self):
        self.assertEqual(T.zone_tf("weekly_vah"), "1h")
        self.assertEqual(T.zone_tf("prior_day_close"), "15m")
        self.assertEqual(T.zone_tf("vwap_band_+1"), "5m")
        self.assertEqual(T.zone_tf("1h_swing_low"), "1h")
        self.assertEqual(T.zone_tf("mystery"), "15m")

    def test_wilson_boot(self):
        lo, hi = T.wilson(5, 10)
        self.assertAlmostEqual(lo, 0.2366, places=3)
        self.assertAlmostEqual(hi, 0.7634, places=3)
        self.assertEqual(T.boot_ci([2.0] * 20, n_boot=50), (2.0, 2.0))

    def test_diff_ci(self):
        d = T.diff_ci([1.0, 1.0, 1.0], [0.0, 0.0, 0.0], n_boot=50)
        self.assertEqual(d, (1.0, 1.0, 1.0))
        d = T.diff_ci([2.0, 4.0], [1.0], n_boot=200)
        self.assertAlmostEqual(d[0], 2.0)
        self.assertTrue(d[1] <= 2.0 <= d[2])

    def test_fabio_tag(self):
        ev = [(600000, "long", 300000), (900000, "short", 300000), (1100000, "long", 300000)]
        self.assertTrue(T.fabio_tag(ev, 1000, "long", 2))    # avail 600000, 400000 <= 600000
        self.assertFalse(T.fabio_tag(ev, 1000, "long", 1))   # 400000 > 300000; later long event not yet available
        self.assertTrue(T.fabio_tag(ev, 1000, "short", 1))   # 100000 <= 300000
        self.assertFalse(T.fabio_tag([], 1000, "long", 5))

    def test_resample(self):
        bars = [(1, 2, 0.5, 1.5), (1.5, 3, 1, 2), (2, 2.5, 1.5, 2.2), (2.2, 2.4, 1.9, 2.0), (2.0, 2.1, 1.0, 1.1),
                (1.1, 1.2, 1.0, 1.15)]
        d = T.resample_dicts(mk(bars, t0=0), 5)
        self.assertEqual(len(d), 1)  # second bucket incomplete
        self.assertEqual((d[0]["o"], d[0]["h"], d[0]["l"], d[0]["c"], d[0]["v"], d[0]["tbv"]), (1, 3, 0.5, 1.1, 5.0, 2.5))

    def test_regime(self):
        n = 50000
        b = mk([(1000 + k * 0.01,) * 2 + (1000 + k * 0.01,) * 2 for k in range(n)], t0=0)
        rf = T.regime_features(b, (n - 1) * 60)  # last closed bar index n-2? idx=(n-1), i=n-2
        i = n - 2
        self.assertAlmostEqual(rf[0], (1000 + i * 0.01) / (1000 + (i - 43200) * 0.01) - 1.0)
        self.assertIsNone(T.regime_features(b, 100 * 60))
        self.assertEqual(T.trend_tag(0.10), "trend_up")
        self.assertEqual(T.trend_tag(-0.10), "trend_down")
        self.assertEqual(T.trend_tag(0.0), "range")
        self.assertEqual(T.vol_tag(0.1, (0.2, 0.4)), "vol_low")
        self.assertEqual(T.vol_tag(0.5, (0.2, 0.4)), "vol_high")

    def test_loader_rejects_gap(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "x.csv"), "w", newline="\n") as f:
                f.write("open_time,open,high,low,close,volume,close_time,qv,count,tbv,tbqv,ignore\n")
                for t in (0, 60000, 180000):
                    f.write("%d,1,2,0.5,1.5,10,%d,1,1,4,1,0\n" % (t, t + 59999))
            with self.assertRaises(ValueError):
                T.load_bars_1m(d)
            with open(os.path.join(d, "x.csv"), "w", newline="\n") as f:
                for t in (0, 60000, 120000):
                    f.write("%d,1,2,0.5,1.5,10,%d,1,1,4,1,0\n" % (t, t + 59999))
            b = T.load_bars_1m(d)
            self.assertEqual((b.n, b.tbv[0]), (3, 4.0))

    def test_snapshot_to_row_pd_only_when_needed(self):
        calls = []

        def cv(s, pd):
            return dict(verdict=s["v"], proof=4, top=dict(setup_type="x", zone=dict(name="z", type="daily_val", price=1.0),
                        math=dict(stop=0.9, target=1.2, gross_rr=2, net_rr=1.8, tier="trigger_ready")), direction="long")

        def pdf(s, fail_closed=False):
            calls.append(fail_closed)
            return "aligned"

        s = dict(timestamp_utc="t", current_price="1.0", v="WATCH")
        r = T.snapshot_to_row(s, lambda x: 5.0, cv, pdf)
        self.assertEqual(calls, [True])  # fail-closed proof direction
        self.assertEqual((r["verdict"], r["zprice"], r["stop"], r["ztype"]), ("WATCH", 1.0, 0.9, "daily_val"))
        s["v"] = "WAIT_RR"
        T.snapshot_to_row(s, lambda x: 5.0, cv, pdf)
        self.assertEqual(len(calls), 1)  # not called for WAIT_*


class TestSummarize(unittest.TestCase):
    def test_summary(self):
        tr = [dict(filled=True, reason="target", gross_r=3.0, net_r=3.0), dict(filled=True, reason="stop", gross_r=-1.0, net_r=-1.05),
              dict(filled=True, reason="stop", gross_r=-1.0, net_r=-1.05), dict(filled=False, reason="no_fill")]
        s = T.summarize(tr)
        self.assertEqual((s["n_signals"], s["n_filled"]), (4, 3))
        self.assertAlmostEqual(s["fill_rate"], 0.75)
        self.assertAlmostEqual(s["win"], 1 / 3)
        self.assertAlmostEqual(s["mean_gross"], 1 / 3)
        self.assertAlmostEqual(s["mean_net"], (3.0 - 2.1) / 3)


if __name__ == "__main__":
    unittest.main()


class TestReportAdapterLine(unittest.TestCase):
    def test_adapter_line_uses_promoted_sources(self):
        # 3fdf8cb promoted ArchiveHistoricalSource/MarketDataSnapshot from .new to tracked .java; the report must not need .new files
        import tempfile
        from pathlib import Path
        import tom_bt_report as TR
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "src/main/java/datafeed"
            d.mkdir(parents=True)
            (d / "ArchiveHistoricalSource.java").write_bytes(b"a")
            (d / "MarketDataSnapshot.java").write_bytes(b"m")
            line = TR.adapter_line(td)
        self.assertIn("ArchiveHistoricalSource.java ", line)
        self.assertIn("MarketDataSnapshot.java ", line)

