import sys
sys.dont_write_bytecode = True
"""Tests for the DAX outcome backtest (card tom-dax-backtest): FEES_FDAX, the gap-filling loader, the market-open
filter, the verdict pair, the matched-proof masking, the holdout guard. Every expected number is worked out by hand in
the comment next to it from the rules in PRE_REG_DAX.md and SetupCandidatesBuilder.java (countSignals lines 568-585,
scoring lines 182-185), not from the code under test."""
import copy
import csv
import datetime as dt
import gzip
import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from array import array
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fees as F  # noqa: E402
import tom_bt as T  # noqa: E402
import tom_dax_bt as D  # noqa: E402

# Scratch dirs go to the system temp dir, never into MyTradingSys/backtest: step 4f's pytest collects under that folder at the same
# time as step 4e, and on Windows it lstat()s every entry beside the path it descends into (2026-10-16 CI run 38825784050 failed
# collecting "...\MyTradingSys\backtest\tmppuq59r8k" after this file removed it). Guard: MyTradingSys/tests/test_gate_scratch_outside_checkout.py.


def mk(bars, t0=0):
    o, h, l, c, v, tbv = (array("d") for _ in range(6))
    for a, b, d, e in bars:
        o.append(a); h.append(b); l.append(d); c.append(e); v.append(1.0); tbv.append(0.5)
    return T.Bars1m(t0, o, h, l, c, v, tbv)


def write_klines(path, rows):
    """rows: (open_ms, o, h, l, c, v). Binance layout; tbv = v/2."""
    with open(path, "w", newline="\n") as fh:
        w = csv.writer(fh, lineterminator="\n")
        for t, o, h, l, c, v in rows:
            w.writerow([t, o, h, l, c, v, t + 59999, v * c, 0, v / 2, v * c / 2])


# ------------------------------------------------------------------ a) fees
class TestFees(unittest.TestCase):
    def test_fdax_profile(self):
        self.assertEqual(F.FEES_FDAX, {"entry": 5e-6, "target": 5e-6, "stop": 5e-6, "timeout": 5e-6})

    def test_fdax_in_sim(self):
        # long 24000, stop 23990 (risk 10), target 24030: target hit -> gross 3.0R.
        # fee = 0.000005*24000 + 0.000005*24030 = 0.12 + 0.12015 = 0.24015 points = 0.024015 R
        b = mk([(24001, 24002, 23999, 24000.5), (24000.5, 24031, 24000, 24030)])
        r = T.sim_limit_trade(b, 0, "long", 24000.0, 23990.0, 24030.0, 5, 5, F.FEES_FDAX)
        self.assertEqual(r["reason"], "target")
        self.assertAlmostEqual(r["gross_r"], 3.0)
        self.assertAlmostEqual(r["fee_r"], 0.024015, places=9)
        self.assertAlmostEqual(r["net_r"], 3.0 - 0.024015, places=9)

    def test_slip_points(self):
        # long 100 / stop 99 (risk 1), stop hit in bar 2 (open 100.3 > stop): px 99 - 0.5 pt slip = 98.5 -> gross -1.5R
        b = mk([(100.2, 100.5, 99.9, 100.3), (100.3, 100.4, 98.9, 99.0)])
        r = T.sim_limit_trade(b, 0, "long", 100.0, 99.0, 103.0, 5, 5, T.FEES_DERIBIT, True, 0.0, slip_pts=0.5)
        self.assertEqual(r["reason"], "stop")
        self.assertAlmostEqual(r["gross_r"], -1.5)
        # short mirror: entry 100, stop 101, stop hit, slip 0.5 -> exit 101.5 -> -1.5R
        b2 = mk([(99.8, 100.1, 99.5, 99.7), (99.7, 101.2, 99.6, 101.0)])
        r2 = T.sim_limit_trade(b2, 0, "short", 100.0, 101.0, 97.0, 5, 5, T.FEES_DERIBIT, True, 0.0, slip_pts=0.5)
        self.assertAlmostEqual(r2["gross_r"], -1.5)
        # target legs get no slippage
        b3 = mk([(100.2, 100.5, 99.9, 100.3), (100.3, 103.5, 100.1, 103.0)])
        r3 = T.sim_limit_trade(b3, 0, "long", 100.0, 99.0, 103.0, 5, 5, T.FEES_DERIBIT, True, 0.0, slip_pts=0.5)
        self.assertAlmostEqual(r3["gross_r"], 3.0)


# ------------------------------------------------------------------ b) loader
class TestGapLoader(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory(prefix="mts_dax_bt_")
        self.dir = Path(self.td.name)
        t0 = 1_700_000_000_000 - (1_700_000_000_000 % 60000)
        self.t0 = t0
        # minutes 0,1 present, 2,3,4 closed, 5 present
        write_klines(self.dir / "a.csv", [(t0, 10, 11, 9, 10.5, 2.0), (t0 + 60000, 10.5, 12, 10, 11.0, 3.0),
                                          (t0 + 5 * 60000, 13, 14, 12, 13.5, 4.0)])

    def tearDown(self):
        self.td.cleanup()

    def test_btc_path_still_rejects_gaps(self):
        os.environ.pop("TOM_MARKET_CLOSES", None)
        with self.assertRaises(ValueError):
            T.load_bars_1m(self.dir)

    def test_fill_gaps_flat_bars_at_last_close(self):
        b = T.load_bars_1m(self.dir, fill_gaps=True)
        self.assertEqual(b.n, 6)                                  # minutes 0..5
        self.assertEqual(list(b.real), [1, 1, 0, 0, 0, 1])
        for i in (2, 3, 4):                                       # flat at the last close 11.0, volume 0
            self.assertEqual((b.o[i], b.h[i], b.l[i], b.c[i], b.v[i], b.tbv[i]), (11.0, 11.0, 11.0, 11.0, 0.0, 0.0))
        self.assertEqual((b.o[5], b.v[5]), (13.0, 4.0))
        self.assertEqual(b.idx(self.t0 + 5 * 60000), 5)

    def test_env_flag_selects_fill(self):
        os.environ["TOM_MARKET_CLOSES"] = "1"
        try:
            b = T.load_bars_1m(self.dir)
            self.assertEqual(b.n, 6)
        finally:
            os.environ.pop("TOM_MARKET_CLOSES", None)

    def test_btc_contiguous_has_no_real_mask(self):
        t0 = self.t0
        d2 = self.dir / "b"
        d2.mkdir()
        write_klines(d2 / "a.csv", [(t0, 1, 2, 0.5, 1.5, 1.0), (t0 + 60000, 1.5, 2, 1, 1.8, 1.0)])
        b = T.load_bars_1m(d2)
        self.assertEqual(b.n, 2)
        self.assertIsNone(b.real)

    def test_gap_through_stop_fills_at_reopen_open(self):
        # long entry 100 stop 99; bars: fill bar, one real bar, 3 closed (flat 100.3), reopen gaps to 97.0
        bars = [(100.2, 100.5, 99.9, 100.3), (100.3, 100.6, 100.1, 100.3)] + [(100.3, 100.3, 100.3, 100.3)] * 3 + \
               [(97.0, 97.5, 96.5, 97.2)]
        r = T.sim_limit_trade(mk(bars), 0, "long", 100.0, 99.0, 103.0, 5, 8, F.FEES_FDAX)
        self.assertEqual(r["reason"], "stop")
        self.assertEqual(r["exit_i"], 5)
        self.assertAlmostEqual(r["gross_r"], -3.0)                # (97 - 100) / 1

    def test_crossed_close(self):
        b = T.load_bars_1m(self.dir, fill_gaps=True)
        self.assertTrue(D.crossed_close(b, 1, 5))                 # bars 2..4 are closed minutes
        self.assertFalse(D.crossed_close(b, 0, 1))
        self.assertFalse(D.crossed_close(b, 5, 5))


class TestClosedExecutions(unittest.TestCase):
    def bars(self, side, first=(100.2, 100.5, 99.9, 100.0), reopen=(100.4, 100.6, 100.2, 100.5)):
        # Mirror around 100; filler is exactly the last real close.
        bars = [first, (first[3],) * 4, reopen]
        if side == "short":
            bars = [(200 - o, 200 - l, 200 - h, 200 - c) for o, h, l, c in bars]
        b = mk(bars)
        b.real = bytearray([1, 0, 1])
        return b

    def trade(self, b, side, i0=0, fill_window=1, hold_bars=1):
        sgn = 1 if side == "long" else -1
        return D.sim_limit_trade(b, i0, side, 100., 100. - sgn, 100. + 3 * sgn,
                                 fill_window, hold_bars, F.FEES_FDAX)

    def test_closed_market_executions(self):
        # EXPECT H4: real=[1,0,1]; pending clocks expire without a filler fill;
        # filled positions time out at the reopening open, or stop at its gap price.
        for side in ("long", "short"):
            with self.subTest(side=side, case="pending expires while closed"):
                r = self.trade(self.bars(side), side, i0=1)
                self.assertEqual(r, dict(filled=False, reason="no_fill"))
            with self.subTest(side=side, case="pending survives closure"):
                b = self.bars(side, reopen=(100.2, 100.5, 99.9, 100.3))
                r = self.trade(b, side, i0=1, fill_window=2)
                self.assertEqual(r["fill_i"], 2)
                self.assertEqual(r["reason"], "open_at_end")
            with self.subTest(side=side, case="timeout during closure"):
                r = self.trade(self.bars(side), side)
                self.assertEqual((r["fill_i"], r["exit_i"], r["reason"]), (0, 2, "timeout"))
                self.assertAlmostEqual(r["gross_r"], .4)  # reopening open, not its .5 close
                self.assertEqual(r["bars_held"], 2)
            with self.subTest(side=side, case="reopening gap through stop"):
                r = self.trade(self.bars(side, reopen=(97., 97.5, 96.5, 97.2)), side)
                self.assertEqual((r["fill_i"], r["exit_i"], r["reason"]), (0, 2, "stop"))
                self.assertAlmostEqual(r["gross_r"], -3.)

    def test_deferred_timeout_uses_open_before_intrabar_prices(self):
        for side in ("long", "short"):
            with self.subTest(side=side):
                b = self.bars(side, reopen=(100.4, 104., 98., 100.5))
                r = self.trade(b, side)
                self.assertEqual((r["reason"], r["exit_i"], r["ambiguous"]), ("timeout", 2, 0))
                self.assertAlmostEqual(r["gross_r"], .4)
                # Gap beyond target still executes the resting target at its limit.
                r = self.trade(self.bars(side, reopen=(104., 105., 103.5, 104.5)), side)
                self.assertEqual((r["reason"], r["exit_i"]), ("target", 2))
                self.assertAlmostEqual(r["gross_r"], 3.)

    def test_no_reopening_leaves_position_unresolved(self):
        for side in ("long", "short"):
            with self.subTest(side=side):
                b = self.bars(side)
                b.real[2] = 0
                self.assertEqual(self.trade(b, side), dict(filled=True, reason="open_at_end", fill_i=0))
                self.assertEqual(self.trade(b, side, i0=1), dict(filled=False, reason="no_fill"))

    def test_real_deadline_keeps_close_price_and_slippage(self):
        b = self.bars("long")
        b.real[1] = 1
        b.o[1], b.h[1], b.l[1], b.c[1] = 100.1, 100.8, 100.1, 100.7
        r = self.trade(b, "long")
        self.assertEqual((r["reason"], r["exit_i"]), ("timeout", 1))
        self.assertAlmostEqual(r["gross_r"], .7)
        for side, px in (("long", 99.9), ("short", 100.1)):
            with self.subTest(side=side):
                sgn = 1 if side == "long" else -1
                r = D.sim_limit_trade(self.bars(side), 0, side, 100., 100. - sgn,
                                      100. + 3 * sgn, 1, 1, F.FEES_FDAX, slip_pts=.5)
                self.assertEqual((r["reason"], r["exit_i"]), ("timeout", 2))
                self.assertAlmostEqual(r["gross_r"], -.1)
                self.assertAlmostEqual(r["fee_r"], .0005 + .000005 * px)
                self.assertAlmostEqual(r["net_r"], -.1 - (.0005 + .000005 * px))

    def test_strategy_and_null_use_real_bar_execution(self):
        # 5m zone => unchanged 8*5=40 elapsed minutes; deadline falls in closure.
        b = mk([(100.2, 100.5, 99.9, 100.)] + [(100.,) * 4] * 41 + [(97., 97.5, 96.5, 97.2)])
        b.real = bytearray([1] + [0] * 41 + [1])
        row = dict(t=0, verdict="SETUP_FORMING", setup="ct_long", dir="long", zone="vwap",
                   ztype="vwap_band", zprice=100., stop=99., target=103.)
        rows = [row, dict(row, t=60), dict(row, t=42 * 60)]
        trades = D.simulate("dax", rows, b, "A", F.FEES_FDAX, slip_pts=.5)
        self.assertEqual(len(trades), 1)  # busy through the deferred exit, including its bar
        self.assertEqual((trades[0]["fill_i"], trades[0]["exit_i"], trades[0]["reason"]), (0, 42, "stop"))
        self.assertAlmostEqual(trades[0]["gross_r"], -3.5)
        # Null uses the same passive limit at minute 0, including deferred exit.
        with patch.object(D.random.Random, "randrange", return_value=0):
            result = D.random_entry_null([row] * 30, b, n_perm=1,
                                        session=dict(timezone="UTC", start="00:00", end="01:00"))
        self.assertEqual(result["null_mean"], -3.)
        self.assertEqual(result["draws"][0]["filled"], 1)
        self.assertEqual(result["draws"][0]["busy_skipped"], 29)

    def test_missing_download_is_rejected_before_archive_read(self):
        # Completed empty days are coverage evidence; absent files are not closures.
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            raw = Path(td)
            start, end = dt.date(2026, 1, 1), dt.date(2026, 1, 3)
            for d in (start, end):
                (raw / (d.isoformat() + ".bi5")).write_bytes(b"")
            with self.assertRaisesRegex(SystemExit, "missing .*2026-01-02.bi5"):
                D.require_download_coverage(raw, start, end)
            (raw / "2026-01-02.bi5").write_bytes(b"")
            D.require_download_coverage(raw, start, end)
            manifest = raw / "split.json"
            manifest.write_text(json.dumps(dict(design_end_utc="2026-04-10T23:59:00Z",
                holdout_start_utc="2026-04-11T00:00:00Z", embargo_s=0)), encoding="utf-8", newline="\n")
            with patch.object(D, "DAX_RAW", raw), patch.object(T, "load_bars_1m") as load, \
                 patch.object(D, "load_null_session", return_value=dict(timezone="UTC", start="10:00", end="12:00")):
                with self.assertRaisesRegex(SystemExit, "incomplete DAX download coverage"):
                    D.build_report(SimpleNamespace(months=["2026-01"], shifts=[0], read_holdout=False,
                                                   split_manifest=manifest, readiness_manifest=readiness_fixture(raw)))
                load.assert_not_called()


# ------------------------------------------------------------------ c) market-open filter
class TestOpenFilter(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory(prefix="mts_dax_bt_")
        self.dir = Path(self.td.name)
        t0 = 1_700_000_040_000 - (1_700_000_040_000 % 60000)
        self.t0 = t0
        # real bars at minutes 0..9, closed 10..19, real again 20..21
        rows = [(t0 + i * 60000, 1, 2, 0.5, 1.5, 1.0) for i in list(range(10)) + [20, 21]]
        write_klines(self.dir / "a.csv", rows)
        self.b = T.load_bars_1m(self.dir, fill_gaps=True)

    def tearDown(self):
        self.td.cleanup()

    def at(self, minute):
        return (self.t0 + minute * 60000) / 1000.0

    def test_window_is_the_two_minutes_before_asof(self):
        # asOf at minute 11 looks at bars 9 and 10: bar 9 real -> keep
        self.assertTrue(D.is_open(self.b, self.at(11)))
        # asOf at minute 12 looks at bars 10 and 11: both closed -> drop
        self.assertFalse(D.is_open(self.b, self.at(12)))
        self.assertFalse(D.is_open(self.b, self.at(15)))
        # asOf at minute 5: bars 3,4 real
        self.assertTrue(D.is_open(self.b, self.at(5)))
        # asOf at minute 20 looks at bars 18,19: closed even though bar 20 itself is real (it opens AT asOf)
        self.assertFalse(D.is_open(self.b, self.at(20)))
        self.assertTrue(D.is_open(self.b, self.at(21)))

    def test_edges_outside_the_archive(self):
        self.assertFalse(D.is_open(self.b, self.at(-5)))
        self.assertFalse(D.is_open(self.b, self.at(500)))
        self.assertFalse(D.is_open(self.b, self.at(0)))           # bars -2,-1 do not exist


# ------------------------------------------------------------------ d)/e) verdict pair and masking
def proof_node(rw="NONE", absorption=False, fa=None, flip=False, spike=False, cvd=False):
    return {"rejection_wick": rw,
            "absorption": {"detected": absorption, "strength": "none", "candle_count": 0, "vol_ratio": 0.0},
            "finished_auction": {"detected": fa is not None, "direction": fa or "", "extreme_delta": 0.0,
                                 "reversal_delta": 0.0, "follow_through": False},
            "delta_flip": {"detected": flip, "from_negative": False, "at_zone": flip, "zone_level": 0.0, "candles_since": 0},
            "volume_spike": {"detected": spike, "magnitude": 3.0, "at_level": True, "level": 0.0},
            "speed": {"picking_up": True},
            "cvd_aligned": cvd, "book_imbalance": None}


def cand(rank, direction, zname, ztype, proof, pc, bonus=0, gross=3.0, net=1.0, tier="trigger_ready"):
    raw = min(95, 50 + 7 * pc + bonus)
    return {"rank": rank, "setup_type": "ct_long" if direction == "long" else "ct_short", "direction": direction,
            "zone": {"name": zname, "price": 100.0, "type": ztype},
            "math": {"tier": tier, "stop": 99.0 if direction == "long" else 101.0, "target": 103.0, "gross_rr": gross, "net_rr": net},
            "proof": proof, "score": {"raw": raw, "confidence": "B", "proof_count": pc, "confluence_bonus": bonus}}


def snap(cands, t="2026-01-05T10:00:00Z", price=100.0):
    return {"timestamp_utc": t, "current_price": price, "conditions": {"price_vs_va": "inside", "cvd_slope": "flat"},
            "setup_candidates": cands}


def parse_ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def aligned(s, fail_closed=False):
    return "aligned"


class TestMask(unittest.TestCase):
    def test_half_volume_order_flow_unavailable_long_short_parity(self):
        from verdict import build_math_object, proof_dir_of

        # EXPECT H6: dax_data.py:100-106 supplies half-volume placeholders.
        # MarketDataSnapshot.java:752-755 labels their zero delta negative.
        # Missing aggressor data must not contradict either mirrored candidate.
        bars = mk([(100., 101., 99., 100.)] * 3)
        deltas = [2 * buy - vol for buy, vol in zip(bars.tbv, bars.v)]
        self.assertEqual(deltas, [0., 0., 0.])
        labels = ["positive" if delta > 0 else "negative" for delta in deltas]
        rows = []
        for side in ("long", "short"):
            c = cand(1, side, "vwap", "vwap_band", proof_node("MODERATE"), 1, net=2.)
            c["math"]["target"] = 103. if side == "long" else 97.
            s = snap([c])
            s["cvd"] = dict(value=0., slope="flat", last_3_delta=labels[:])
            before = copy.deepcopy(s)
            adapted = []

            def checked_direction(snapshot, fail_closed=False):
                adapted.append(copy.deepcopy(snapshot))
                return proof_dir_of(snapshot, fail_closed=fail_closed)

            # Synthetic extension only: reach the five-proof verdict to expose
            # the latent WATCH cap; no production threshold/parameter is changed.
            row = D.rows_for_snapshot(s, parse_ts, checked_direction, shifts=(4,))["coded/4"]
            rows.append(row)
            self.assertEqual(s, before)  # adapter must not mutate source snapshots
            self.assertEqual(len(adapted), 1)
            output = adapted[0]
            with self.subTest(side=side, check="proof direction"):
                self.assertEqual(build_math_object(output)["proof_direction_status"], "aligned")
                self.assertEqual(row["pd"], "aligned")
            with self.subTest(side=side, check="unavailable delta"):
                self.assertFalse(set(output["cvd"]["last_3_delta"]) & {"negative", "positive"})
                self.assertEqual(output["cvd"]["availability"], "UNAVAILABLE")
                self.assertEqual(output["cvd"]["slope"], "unavailable")
                self.assertEqual(output["conditions"]["cvd_slope"], "unavailable")
            with self.subTest(side=side, check="verdict"):
                self.assertEqual(row["verdict"], "SETUP_FORMING")
        self.assertEqual([(r["pd"], r["verdict"]) for r in rows],
                         [("aligned", "SETUP_FORMING")] * 2)

    def test_unmasked_cvd_snapshot_is_preserved(self):
        s = snap([self.full()])
        s["cvd"] = dict(value=-3., slope="falling", last_3_delta=["negative"] * 3)
        s["conditions"]["cvd_slope"] = "falling"
        before = copy.deepcopy(s)
        D.rescore(s, mask=())
        self.assertEqual(s, before)

    def test_old_volume_spike_snapshot_rejected(self):
        s = snap([cand(1, "short", "vwap", "vwap_band", proof_node(spike=True), 1)])
        before = copy.deepcopy(s)
        with self.assertRaisesRegex(ValueError, "proof JSON gives 0, score.proof_count is 1"):
            D.rescore(s)
        self.assertEqual(s, before)

    def test_volume_spike_only_counts_zero_and_rescore_accepts(self):
        # EXPECT: SetupCandidatesBuilder.java:579 (B144) excludes volume_spike,
        # although toJson at 615-616 still emits detected=True.
        c = cand(1, "short", "vwap", "vwap_band", proof_node(spike=True), 0)
        with self.subTest("current Java count"):
            self.assertEqual(D.java_count(c), 0)
        with self.subTest("current Java snapshot accepted"):
            self.assertEqual(D.rescore(snap([c])), 0)
            self.assertEqual(c["score"]["proof_count"], 0)
            self.assertEqual(c["score"]["raw"], 50)

    def full(self):
        # Java:568-585: rejection + absorption + favouring auction + flip + cvd = 5; spike uncounted (B144).
        return cand(1, "long", "daily_poc", "daily_poc",
                    proof_node("MODERATE", True, "sell", True, True, True), 5)

    def test_java_count_parity(self):
        self.assertEqual(D.java_count(self.full()), 5)
        # finished_auction 'buy' does not favour a long: 1+1+0+1+1 = 4
        c = cand(1, "long", "daily_poc", "daily_poc", proof_node("WEAK", True, "buy", True, True, True), 4)
        self.assertEqual(D.java_count(c), 4)
        # short favours 'buy'; the JSON volume_spike.detected already includes at_level (java toJson), so a spike away from the
        # level is detected=False: rw(1) + fa buy(1) = 2
        p = proof_node("STRONG", False, "buy", False, False, False)
        self.assertEqual(D.java_count(cand(1, "short", "daily_poc", "daily_poc", p, 2)), 2)

    def test_mask_removes_only_order_flow_proofs(self):
        s = snap([self.full()])
        D.rescore(s)
        c = s["setup_candidates"][0]
        self.assertEqual(c["score"]["proof_count"], 1)             # only rejection wick counts
        self.assertEqual(c["score"]["raw"], 57)                    # 50 + 7*1
        self.assertFalse(c["proof"]["absorption"]["detected"])
        self.assertFalse(c["proof"]["finished_auction"]["detected"])
        self.assertEqual(c["proof"]["finished_auction"]["direction"], "")
        self.assertFalse(c["proof"]["delta_flip"]["detected"])
        self.assertFalse(c["proof"]["cvd_aligned"])
        self.assertEqual(c["proof"]["rejection_wick"], "MODERATE")
        self.assertTrue(c["proof"]["volume_spike"]["detected"])

    def test_uncounted_finished_auction_is_not_subtracted(self):
        # long + fa 'buy' (not counted) + rejection + cvd = 2; masking cvd only -> 1. fa must not be subtracted.
        c = cand(1, "long", "daily_poc", "daily_poc", proof_node("WEAK", False, "buy", False, False, True), 2)
        s = snap([c])
        D.rescore(s)
        self.assertEqual(s["setup_candidates"][0]["score"]["proof_count"], 1)

    def test_empty_mask_and_zero_shift_is_identity(self):
        s = snap([self.full()])
        before = copy.deepcopy(s)
        D.rescore(s, mask=(), shift=0)
        self.assertEqual(s, before)

    def test_shift_adds_to_every_candidate(self):
        s = snap([self.full()])
        D.rescore(s, shift=1)
        self.assertEqual(s["setup_candidates"][0]["score"]["proof_count"], 2)   # 1 + 1
        self.assertEqual(s["setup_candidates"][0]["score"]["raw"], 64)          # 50 + 14

    def test_parity_mismatch_fails_closed(self):
        c = self.full()
        c["score"]["proof_count"] = 6
        with self.assertRaises(ValueError):
            D.rescore(snap([c]))

    def test_rerank_by_masked_score_then_tf_rank(self):
        # A: full proof 5 -> raw 85 -> masked 57.
        # B: rejection only counts (spike emitted), bonus 10 -> raw 67; outranks A after masking.
        a = self.full()
        b = cand(2, "long", "15m_swing_low", "15m_swing_low", proof_node("MODERATE", False, None, False, True, False), 1, bonus=10)
        self.assertEqual((a["score"]["raw"], b["score"]["raw"]), (85, 67))
        s = snap([a, b])
        D.rescore(s)
        out = s["setup_candidates"]
        self.assertEqual([c["zone"]["name"] for c in out], ["15m_swing_low", "daily_poc"])
        self.assertEqual([c["rank"] for c in out], [1, 2])
        self.assertEqual([c["score"]["raw"] for c in out], [67, 57])

    def test_rerank_tie_broken_by_tf_rank(self):
        # both end at raw 57 (pc 1, bonus 0): higher tfRank first. Input order: 15m swing (3) then daily (9)
        a = cand(1, "long", "15m_swing_low", "15m_swing_low", proof_node("MODERATE", True, None, False, True, False), 2)
        b = cand(2, "long", "daily_poc", "daily_poc", proof_node("MODERATE", False, None, False, True, False), 1)
        self.assertEqual((a["score"]["raw"], b["score"]["raw"]), (64, 57))
        s = snap([a, b])
        D.rescore(s)
        self.assertEqual([c["zone"]["name"] for c in s["setup_candidates"]], ["daily_poc", "15m_swing_low"])

    def test_tf_rank_table(self):
        # SetupCandidatesBuilder.extractZones lines 274-315 and the naked POC block (tfRank 11)
        for name, typ, want in [("weekly_poc", "weekly_poc", 10), ("daily_val", "daily_val", 9), ("4h_vah", "4h_vah", 7),
                                ("vwap", "vwap_band", 6), ("vwap_band_+1", "vwap_band_+1", 6), ("prior_day_poc", "prior_day_poc", 5),
                                ("1h_swing_high", "1h_swing_high", 4), ("15m_swing_low", "15m_swing_low", 3),
                                ("5m_swing_low", "5m_swing_low", 2), ("fvg_nearest", "fvg", 1),
                                ("naked_poc_2026-01-02", "weekly_poc", 11)]:
            self.assertEqual(D.tf_rank(name, typ), want, name)

    def test_masking_changes_the_verdict(self):
        # full proof 5 -> SETUP_FORMING unmasked; masked 1 -> WAIT_PROOF
        s = snap([self.full()])
        s["setup_candidates"][0]["math"]["net_rr"] = 2.0
        un = D.rows_for_snapshot(copy.deepcopy(s), parse_ts, aligned, mask=(), kinds=("coded",))
        self.assertEqual(un["coded/0"]["verdict"], "SETUP_FORMING")
        mk_ = D.rows_for_snapshot(copy.deepcopy(s), parse_ts, aligned, kinds=("coded",))
        self.assertEqual(mk_["coded/0"]["verdict"], "WAIT_PROOF")
        self.assertEqual(mk_["coded/0"]["proof"], 1)


class TestVerdictPair(unittest.TestCase):
    def test_primary_rejects_ger40_gross_rr_at_floor(self):
        # EXPECT: FORMULAS.md:403-404 and ExecutionMathConstants.java:23-37:
        # cost = 2 * .000005 * 100 = .001; net = 1.249/1.001
        # = 1.247752247752... < frozen floor 1.25; gross = 1.25.
        from verdict import compute_verdict
        net = 1.249 / 1.001
        c = cand(1, "long", "daily_poc", "daily_poc",
                 proof_node("MODERATE", True, "sell", True, False, True),
                 5, gross=1.25, net=net)
        c["math"]["target"] = 101.25
        s = snap([c])
        s["symbol"] = "GER40"
        verdict = lambda s, pd: compute_verdict(s, pd, floor=1.25)
        rows = D.rows_for_snapshot(s, parse_ts, aligned, verdict, mask=())
        primary = rows[D.KINDS[0] + "/0"]
        self.assertEqual(primary["verdict"], "WAIT_RR")
        self.assertAlmostEqual(primary["net_rr"], net)

    def test_primary_preserves_net_on_every_candidate(self):
        a = cand(1, "long", "daily_poc", "daily_poc", proof_node("MODERATE", False, None, False, True, False), 1, gross=3.0, net=1.0)
        b = cand(2, "long", "vwap", "vwap_band", proof_node(), 0, gross=2.5, net=0.7)
        s = snap([a, b])
        seen = []
        from verdict import compute_verdict
        def capture(snapshot, pd):
            seen.extend(c["math"]["net_rr"] for c in snapshot["setup_candidates"])
            return compute_verdict(snapshot, pd, floor=1.25)
        D.rows_for_snapshot(s, parse_ts, aligned, capture)
        self.assertEqual(seen, [1.0, 0.7])

    def test_primary_rejects_net_below_floor_even_with_proof_shift(self):
        # Proof extension cannot bypass the primary net-RR gate.
        a = cand(1, "long", "daily_poc", "daily_poc", proof_node("MODERATE", False, None, False, True, False), 1, gross=3.0, net=1.0)
        s = snap([a])
        r0 = D.rows_for_snapshot(copy.deepcopy(s), parse_ts, aligned, shifts=(0, 2))
        self.assertEqual(r0["coded/2"]["verdict"], "WAIT_RR")
        self.assertEqual(r0["coded/0"]["verdict"], "WAIT_RR")
        self.assertEqual(set(r0), {"coded/0", "coded/2"})
        self.assertEqual(r0["coded/2"]["net_rr"], 1.0)
        self.assertEqual(r0["coded/2"]["proof"], 3)

    def test_inputs_not_mutated(self):
        a = cand(1, "long", "daily_poc", "daily_poc", proof_node("MODERATE", True, None, False, True, False), 2, net=1.0)
        s = snap([a])
        before = copy.deepcopy(s)
        D.rows_for_snapshot(s, parse_ts, aligned)
        self.assertEqual(s, before)


# ------------------------------------------------------------------ f) driver helpers
class TestHoldoutBoundaries(unittest.TestCase):
    def manifest(self, root, **changes):
        obj = dict(design_end_utc="2026-04-10T23:58:00Z",
                   holdout_start_utc="2026-04-11T00:00:00Z", embargo_s=0)
        obj.update(changes)
        p = Path(root) / "split.json"
        p.write_text(json.dumps(obj), encoding="utf-8", newline="\n")
        return p

    def test_development_outcomes_never_touch_holdout_and_count_real_rows(self):
        # Synthetic dates only. Signal fills at H-60; the first target is at H.
        # EXPECT: that unresolved dev outcome is dropped, never counted as a win.
        h = D.T_DAX_HOLD
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            root = Path(td)
            (root / "klines").mkdir()
            write_klines(root / "klines" / "synthetic.csv", [
                (int((h - 120) * 1000), 100, 100, 100, 100, 1),
                (int((h - 60) * 1000), 100, 100, 100, 100, 1),
                (int(h * 1000), 100, 102, 100, 101, 1),
                (int((h + 60) * 1000), 101, 102, 100, 101, 1)])
            manifest = root / "split.json"
            manifest.write_text(json.dumps(dict(
                design_end_utc="2026-04-10T23:59:00Z",
                holdout_start_utc="2026-04-11T00:00:00Z", embargo_s=0)),
                encoding="utf-8", newline="\n")
            row = dict(t=h-60, verdict="SETUP_FORMING", setup="ct_long", dir="long",
                       zone="vwap", ztype="vwap", zprice=100., stop=99., target=101.)
            rows = [row, dict(row, t=h), dict(row, t=h+60)]
            a = SimpleNamespace(read_holdout=False, shifts=[0, 1], months=None,
                                split_manifest=manifest, readiness_manifest=readiness_fixture(root), market="dax", smoke=True)
            seen = []
            summarize = T.summarize
            def capture(trades):
                seen.extend(trades)
                return summarize(trades)
            with patch.object(D, "DAX_ARCHIVE", root), patch.object(D, "DAX_SNAPS", root), \
                 patch.object(D, "WORK", root), patch.object(D, "require_download_coverage"), \
                 patch.object(D, "load_null_session", return_value=dict(timezone="UTC", start="23:00", end="01:00")), \
                 patch.object(D, "load_rows", return_value=rows), patch.object(T, "summarize", side_effect=capture):
                result = D.build_report(a)
            with self.subTest("outcome isolation"):
                self.assertFalse(any(t.get("filled") and
                                     h-120 + 60*t["exit_i"] >= h for t in seen), seen)
            with self.subTest("actual row count"):
                self.assertEqual(result[3]["dax"]["holdout_rows"], 2)  # rows, not arms or variants
            self.assertEqual(len(result[3]["null_draws"]), 8)  # 2 shifts x 4 variants
            self.assertTrue(all(arm["result"]["n_perm"] == 200 for arm in result[3]["null_draws"]))
            self.assertTrue(all(arm["result"]["p"] is None for arm in result[3]["null_draws"]))
            # Exercise report serialization with only synthetic, already computed
            # inputs. Git and hash probes are stubbed; outputs stay in this fixture.
            with patch.object(D, "build_report", return_value=result), \
                 patch.object(D, "WORK", root), \
                 patch.object(D, "git", return_value="synthetic"), patch.object(D, "sha", return_value="fixture"), \
                 patch.object(D, "REPORT", root/"report.md"), patch.object(D, "REGISTRY", root/"trials.csv"):
                D.cmd_report(a)
                text = D.REPORT.read_text(encoding="utf-8")
                self.assertIn("seed 7, 200 requested draws", text)
                self.assertIn("| sampled | submitted | busy skipped | filled |", text)
                self.assertIn("| coded/s0/A/dev | 1 | 199 |", text)
                self.assertNotIn("|\n\n| coded/", text)  # table rows stay contiguous

    def test_absent_manifest_refuses_before_data_read(self):
        a = SimpleNamespace(read_holdout=False, shifts=[0], months=None, market="dax", smoke=True)
        with patch.object(D, "require_download_coverage", side_effect=AssertionError("coverage read before manifest")), \
             patch.object(D, "load_readiness", return_value={}), \
             patch.object(T, "load_bars_1m", side_effect=AssertionError("data read before manifest")):
            with self.assertRaisesRegex((ValueError, SystemExit), "split manifest"):
                D.build_report(a)

    def test_invalid_manifest_and_forward_boundary(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            for changes in [dict(embargo_s=-1), dict(embargo_s=True), dict(embargo_s=float("nan")),
                            dict(embargo_s=121), dict(holdout_start_utc="2026-04-10T23:58:00Z"),
                            dict(design_end_utc="2026-04-10T23:58:00"),
                            dict(holdout_start_utc="2026-04-11T00:00:00+01:00")]:
                with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, "split manifest"):
                    D.load_split(self.manifest(td, **changes))
            split = D.load_split(self.manifest(td, design_end_utc="2026-10-12T00:00:00Z",
                holdout_start_utc="2026-11-01T00:00:00Z", embargo_s=86400))
            self.assertEqual(D.dax_period(D._ts(2026, 10, 30), split), "dev")
            self.assertEqual(D.dax_period(D._ts(2026, 10, 31), split), "embargo")
            self.assertEqual(D.dax_period(D._ts(2026, 11, 1), split), "holdout")

    def test_prices_after_cutoff_not_parsed_and_partial_minute_excluded(self):
        h = D.T_DAX_HOLD
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            p = Path(td) / "a.csv"
            write_klines(p, [(int((h-120)*1000), 100, 100, 100, 100, 1),
                             (int((h-60)*1000), 100, 102, 100, 101, 1)])
            with open(p, "a", encoding="utf-8", newline="\n") as fh:
                fh.write(str(int(h*1000)) + ",HOLDOUT_PRICE_MUST_NOT_BE_PARSED\n")
            split = D.load_split(self.manifest(td, embargo_s=30))
            b = D.load_development_bars(td, split["dev_end"])
            self.assertEqual(b.n, 1)  # H-60 bar extends beyond the H-30 cutoff
            full = mk([(100, 100, 100, 100)]*3, int((h-120)*1000))
            self.assertEqual(D.slice_bars(full, end_s=split["dev_end"]).n, 1)

    def test_real_row_envelopes_counted_without_loading_holdout_payload(self):
        h = D.T_DAX_HOLD
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td, patch.object(D, "WORK", Path(td)):
            split = D.load_split(self.manifest(td, embargo_s=60))
            out = Path(td) / "rows_dax"
            out.mkdir()
            p = out / "2026-04.rows.jsonl"
            envelopes = [dict(t=h-120, k={"coded/0": {"t": h-120}}),
                         dict(t=h-60, k={}), dict(t=h, k={}), dict(t=h+60, k={})]
            for e in envelopes:
                e["proof_count_schema"] = D.PROOF_COUNT_SCHEMA
            p.write_text("".join(json.dumps(e)+"\n" for e in envelopes), encoding="utf-8", newline="\n")
            p.with_name("2026-04.rows.meta.json").write_text(json.dumps(dict(
                proof_count_schema=D.PROOF_COUNT_SCHEMA)), encoding="utf-8", newline="\n")
            counts = {}
            # This test isolates timestamp selection; identity validation has its
            # own real-cache fixtures and must no longer accept this bare cache.
            for e in envelopes:
                e["input_id"] = "synthetic"
            p.write_text("".join(json.dumps(e)+"\n" for e in envelopes), encoding="utf-8", newline="\n")
            with patch.object(D, "validate_cache", return_value=dict(input_id="synthetic", inputs=dict(market="dax"))):
                self.assertEqual(D.load_rows("dax", "coded/0", split=split, counts=counts), [{"t": h-120}])
            self.assertEqual(counts, dict(dev=1, embargo=1, holdout=2))

    def test_pending_orders_dropped_and_resolved_dev_kept_in_stress(self):
        h = D.T_DAX_HOLD
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            split = D.load_split(self.manifest(td))
            r = dict(t=h-60, verdict="SETUP_FORMING", setup="ct_long", dir="long",
                     zone="vwap", ztype="vwap", zprice=100., stop=99., target=101.)
            for side, stop, target in [("long", 99., 101.), ("short", 101., 99.)]:
                row = dict(r, dir=side, stop=stop, target=target)
                # No development fill; a fill would occur only at H.
                px = 102 if side == "long" else 98
                b = mk([(px, px, px, px), (100, 100, 100, 100)], int((h-60)*1000))
                row["target"] = 104 if side == "long" else 96  # pending, not ran
                self.assertEqual(D.simulate("dax", [row], b, "A", F.FEES_FDAX, split=split), [])
            b = mk([(100, 100, 98, 99), (100, 102, 100, 101)], int((h-60)*1000))
            trades = D.simulate("dax", [r], b, "A", F.FEES_FDAX, slip_pts=1., split=split)
            self.assertEqual(len(trades), 1)
            self.assertEqual((trades[0]["reason"], trades[0]["exit_i"]), ("stop", 0))
            self.assertEqual(trades[0]["gross_r"], -2.)

    def test_full_dev_guard_and_failed_read_remains_reserved(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td, patch.object(D, "REPORT", Path(td)/"report.md"), \
             patch.object(D, "HOLDOUT_MARKER", Path(td)/"read.json"):
            path = self.manifest(td)
            split = D.load_split(path)
            a = SimpleNamespace(split_manifest=path, readiness_manifest=readiness_fixture(td),
                                read_holdout=True, shifts=[0], months=None, smoke=False)
            D.REPORT.write_text("A previous partial report", encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(SystemExit, "full development"):
                D.require_full_dev(a, split)
            D.REPORT.write_text("Full development completed for split " + split["identity"],
                                encoding="utf-8", newline="\n")
            a.months = ["2026-04"]
            with self.assertRaisesRegex(SystemExit, "full development"):
                D.require_full_dev(a, split)
            a.months = None
            def count(*args, counts, **kwargs):
                counts["holdout"] = 2
                return []
            with patch.object(D, "load_rows", side_effect=count), patch.object(D, "require_download_coverage"), \
                 patch.object(D, "load_null_session", return_value=dict(timezone="UTC", start="23:00", end="01:00")), \
                 patch.object(T, "load_bars_1m", side_effect=ValueError("synthetic outcome read failed")):
                with self.assertRaisesRegex(ValueError, "synthetic outcome read failed"):
                    D.build_report(a)
            saved = json.loads(D.HOLDOUT_MARKER.read_text(encoding="utf-8"))
            self.assertEqual(saved["holdout_rows"], 2)
            self.assertEqual(saved["split_identity"], split["identity"])
            with self.assertRaisesRegex(SystemExit, "already read"):
                D.require_full_dev(a, split)


class TestSessionNull(unittest.TestCase):
    def test_missing_or_invalid_session_refuses_before_data_read(self):
        b = mk([(100.,) * 4] * 100)
        with self.assertRaisesRegex(ValueError, "null session"):
            D.random_entry_null([], b)
        for session in [dict(timezone="invalid", start="10:00", end="12:00"),
                        dict(timezone="UTC", start="10:00", end="10:00"),
                        dict(timezone="UTC", start="25:00", end="12:00")]:
            with self.subTest(session=session), self.assertRaisesRegex(ValueError, "null session"):
                D.random_entry_null([], b, session=session)
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            p = Path(td)/"session.json"
            p.write_text(json.dumps(dict(timezone="UTC", start="10:00", end="12:00")),
                         encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(ValueError, "trader quote"):
                D.load_null_session(p)
        with patch.object(D, "load_split", return_value={}), \
             patch.object(D, "load_readiness", return_value={}), \
             patch.object(D, "require_download_coverage", side_effect=AssertionError("data read")):
            with self.assertRaisesRegex(ValueError, "null session manifest required"):
                D.build_report(SimpleNamespace(read_holdout=False))

    def test_timezone_dst_and_overnight_sessions(self):
        session = dict(timezone="Europe/Berlin", start="10:00", end="12:00")
        winter, summer = D._ts(2026, 1, 5), D._ts(2026, 7, 6)
        self.assertEqual(D.session_bounds(winter+540*60, session), (winter+540*60, winter+660*60))
        self.assertEqual(D.session_bounds(summer+480*60, session), (summer+480*60, summer+600*60))
        overnight = dict(timezone="UTC", start="23:00", end="01:00")
        self.assertEqual(D.session_bounds(winter+30*60, overnight), (winter-3600, winter+3600))

    def test_session_end_no_entry_fill_and_unresolved_order_blocks(self):
        b = mk([(100., 100.5, 99.5, 100.)]*60 + [(100., 100.5, 98.5, 100.)]*50)
        b.real = bytearray([1]*b.n)
        row = dict(t=59*60, verdict="SETUP_FORMING", setup="ct_long", dir="long",
                   zone="vwap", ztype="vwap_band", zprice=99., stop=98., target=105.)
        session = dict(timezone="UTC", start="00:00", end="01:00")
        with patch.object(D.random.Random, "randrange", return_value=59):
            result = D.random_entry_null([row], b, n_perm=1, session=session)
        self.assertEqual(result["draws"][0]["no_fill"], 1)
        self.assertEqual(result["real_counts"]["no_fill"], 1)
        # 20 available minutes cannot resolve a 40-minute order; it stays busy.
        short = mk([(100., 100.5, 99.5, 100.)]*20)
        trades, counts = D.run_dax_opportunities([dict(row, t=0), dict(row, t=60)], short, F.FEES_FDAX)
        self.assertEqual((counts["open_at_end"], counts["busy_skipped"]), (1, 1))
        self.assertEqual(trades[0]["reason"], "open_at_end")

    def test_ran_short_geometry_and_original_opportunities(self):
        b = mk([(200., 200.5, 199.5, 200.)]*1440)
        b.real = bytearray([1]*b.n)
        session = dict(timezone="UTC", start="10:00", end="12:00")
        row = dict(t=600*60, verdict="SETUP_FORMING", setup="ct_short", dir="short",
                   zone="vwap", ztype="vwap_band", zprice=202., stop=204., target=198.)
        # Original passive short offset 1%, stop +2, target -4 at price 200.
        b.o[610] = b.h[610] = b.l[610] = b.c[610] = 100.
        with patch.object(D.random.Random, "randrange", return_value=10):
            result = D.random_entry_null([row], b, n_perm=1, session=session)
        trade = result["draws"][0]["trades"][0]
        self.assertEqual((trade["dir"], trade["zprice"], trade["stop"], trade["target"]),
                         ("short", 101., 102., 99.))
        # Target is reached before entry: unfilled opportunity is still sampled.
        ran = dict(row, dir="long", zprice=198., stop=196., target=200.)
        result = D.random_entry_null([ran], b, n_perm=2, session=session)
        self.assertEqual(result["opportunities"], 1)
        self.assertEqual([d["ran"] for d in result["draws"]], [1, 1])
        self.assertEqual((result["nonempty_draws"], result["empty_draws"], result["p"]), (0, 2, None))
        with self.assertRaisesRegex(ValueError, "marketable"):
            D.random_entry_null([dict(row, zprice=199.)], b, session=session)

    def test_null_preserves_order_lifetime(self):
        b = mk([(100., 100.5, 99.5, 100.)] * 1440)
        b.real = bytearray([1] * b.n)
        row = dict(t=600*60, verdict="SETUP_FORMING", setup="ct_long",
                   dir="long", zone="vwap", ztype="vwap_band", zone_tf="5m",
                   zprice=100., stop=99., target=105., filled=True,
                   reason="timeout", gross_r=0.)
        with patch.object(D, "sim_limit_trade", wraps=D.sim_limit_trade) as sim:
            D.random_entry_null([row] * 30, b, n_perm=1,
                                session=dict(timezone="UTC", start="10:00", end="12:00"))
        self.assertTrue(sim.call_args_list)
        self.assertTrue(all(call.args[6] == 40 for call in sim.call_args_list),
                        [call.args[6] for call in sim.call_args_list])

    def test_session_limits_expiry_and_one_at_a_time(self):
        # Synthetic winter day: Berlin 10:00..12:00 = UTC minutes 540..659.
        day = D._ts(2026, 1, 5)
        b = mk([(100., 100.5, 99.5, 100.)] * 1440, int(day * 1000))
        b.real = bytearray([1] * b.n)
        session = dict(timezone="Europe/Berlin", start="10:00", end="12:00")
        base = dict(t=day+540*60, verdict="SETUP_FORMING", setup="ct_long",
                    dir="long", zone="vwap", ztype="vwap_band",
                    zprice=99., stop=98., target=105.)
        rows = [dict(base, t=base["t"]+i*60) for i in range(30)]
        # EXPECT: the passive 1% offset stays below every low; 40-minute
        # orders expire, even though the old next-open comparator always fills.
        result = D.random_entry_null(rows, b, n_perm=1, seed=7, session=session)
        draw = result["draws"][0]
        self.assertEqual(result["opportunities"], 30)
        self.assertEqual(draw["sampled"], 30)
        self.assertGreater(draw["submitted"], 0)
        self.assertEqual(draw["filled"], 0)
        self.assertEqual(draw["no_fill"], draw["submitted"])
        self.assertGreater(draw["busy_skipped"], 0)
        for trade in draw["trades"]:
            self.assertTrue(540 <= trade["signal_i"] < 660)
            self.assertEqual(trade["zprice"], 99.)
        self.assertEqual(result, D.random_entry_null(rows, b, n_perm=1, seed=7, session=session))
        # Same fixture with touching limits: positions last 40 minutes. Neither
        # a second position nor a pending order may overlap their occupied bars.
        touching = [dict(r, zprice=100., stop=99., target=105.) for r in rows]
        result = D.random_entry_null(touching, b, n_perm=1, seed=7, session=session)
        draw = result["draws"][0]
        self.assertGreater(draw["filled"], 0)
        self.assertGreater(draw["busy_skipped"], 0)
        for left, right in zip(draw["trades"], draw["trades"][1:]):
            self.assertGreater(right["fill_i"], left["exit_i"])
        self.assertTrue(all(540 <= t["fill_i"] < 660 for t in draw["trades"]))


class TestDriver(unittest.TestCase):
    def test_h8_generation_freezes_producer_and_refuses_changed_archive(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            root = Path(td)
            archive, snaps = root / "archive", root / "snaps"
            (archive / "klines").mkdir(parents=True)
            snaps.mkdir()
            data = archive / "klines" / "synthetic.csv"
            data.write_text("synthetic archive bytes\n", encoding="utf-8", newline="\n")
            gen_bars = mk([(100.,) * 4] * 3, 1767225600000)
            gen_bars.real = bytearray([1] * 3)
            def fake_run(command, **kwargs):
                if "dax_engine.py" not in str(command[2]):
                    return
                source = snaps / "2026-01.jsonl.gz"
                if not source.exists():
                    with gzip.open(source, "wt", encoding="utf-8") as fh:
                        fh.write('{}\n')
                    (snaps / "2026-01.meta.json").write_text('{"evaluated": 1}',
                        encoding="utf-8", newline="\n")
            split_path = root / "split.json"
            split_path.write_text(json.dumps(dict(design_end_utc="2026-02-01T00:00:00Z",
                holdout_start_utc="2026-06-01T00:00:00Z", embargo_s=0)), encoding="utf-8", newline="\n")
            a = SimpleNamespace(start=None, end=None, months=["2026-01"], shards=1, read_holdout=False,
                                split_manifest=split_path)
            with patch.object(D, "DAX_ARCHIVE", archive), patch.object(D, "DAX_SNAPS", snaps), \
                 patch.object(D, "DAX_RAW", root / "raw"), \
                 patch.object(D, "generation_environment", return_value={"synthetic-JDK-and-jars": "fixture"}), \
                 patch.object(D, "complete_months", return_value=["2026-01"]), \
                 patch.object(D, "load_development_bars", return_value=gen_bars), \
                 patch.object(D.subprocess, "run", side_effect=fake_run):
                D.cmd_gen(a)
                origin = json.loads((snaps / "2026-01.inputs.json").read_text(encoding="utf-8"))
                self.assertEqual(origin["bars"], D.bars_identity(gen_bars))   # R4: execution data bound at generation
                self.assertEqual(origin["codes"], D.generation_codes())
                self.assertEqual(origin["environment"], {"synthetic-JDK-and-jars": "fixture"})
                self.assertEqual(origin["data"][str(data)], D.file_hash(data))
                self.assertEqual(origin["snapshot_sha256"], D.file_hash(snaps / "2026-01.jsonl.gz"))
                D.cmd_gen(a)
                data.write_text("changed archive\n", encoding="utf-8", newline="\n")
                with self.assertRaisesRegex(ValueError, "provenance absent/stale"):
                    D.cmd_gen(a)

    def test_h8_cached_rows_refuse_changed_mask_shift_or_floor(self):
        import verdict  # establishes the existing runtime import path
        import net_rr_floor
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td, patch.object(D, "WORK", Path(td)):
            root = Path(td)
            out_dir = root / "rows_btc"
            out_dir.mkdir()
            source = root / "2026-01.jsonl.gz"
            s = snap([cand(1, "short", "vwap", "vwap_band", proof_node(spike=True), 0)])
            with gzip.open(source, "wt", encoding="utf-8") as fh:
                fh.write(json.dumps(s) + "\n")
            source.with_name("2026-01.inputs.json").write_text(json.dumps(dict(
                codes=D.generation_codes(), snapshot_sha256=D.file_hash(source), data={"synthetic": "fixture"})),
                encoding="utf-8", newline="\n")
            job = ("btc", source, out_dir, (0,), D.MASK_OF, None)
            with patch.object(net_rr_floor, "load_floor", return_value=1.25):
                D._rows_month(job)
                self.assertEqual(D._rows_month(job), ("2026-01", None))
                for changed in [(*job[:3], (0, 1), *job[4:]),
                                (*job[:4], (), job[5])]:
                    with self.subTest(job=changed), self.assertRaisesRegex(ValueError, "cache input"):
                        D._rows_month(changed)
            with patch.object(net_rr_floor, "load_floor", return_value=1.5):
                with self.assertRaisesRegex(ValueError, "cache input"):
                    D._rows_month(job)
                with self.assertRaisesRegex(ValueError, "cache input"):
                    D.load_rows("btc", "coded/0")
            with patch.object(net_rr_floor, "load_floor", return_value=1.25):
                codes = D.code_identity()
                codes["MyTradingSys/backtest/verdict.py"] = "changed-engine-fixture"
                with patch.object(D, "code_identity", return_value=codes):
                    with self.assertRaisesRegex(ValueError, "cache input"):
                        D._rows_month(job)
                    with self.assertRaisesRegex(ValueError, "cache input"):
                        D.load_rows("btc", "coded/0")
                original = source.read_bytes()
                with gzip.open(source, "wt", encoding="utf-8") as fh:
                    fh.write(json.dumps(dict(s, current_price=123.)) + "\n")
                with self.assertRaisesRegex(ValueError, "cache input"):
                    D._rows_month(job)
                source.write_bytes(original)
                meta = root / "2026-01.meta.json"
                meta.write_text('{"evaluated": 2}', encoding="utf-8", newline="\n")
                with self.assertRaisesRegex(ValueError, "cache input"):
                    D.load_rows("btc", "coded/0")
                meta.unlink()
                out = out_dir / "2026-01.rows.jsonl"
                row = json.loads(out.read_text(encoding="utf-8"))
                row["k"]["coded/0"]["proof"] = 999
                out.write_text(json.dumps(row) + "\n", encoding="utf-8", newline="\n")
                with self.assertRaisesRegex(ValueError, "cache input"):
                    D.load_rows("btc", "coded/0")

    def test_h8_dax_producer_and_development_bar_identity(self):
        from snapshots import parse_ts
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td, patch.object(D, "WORK", Path(td)):
            root = Path(td)
            out_dir = root / "rows_dax"
            out_dir.mkdir()
            source = root / "2026-01.jsonl.gz"
            s = snap([cand(1, "short", "vwap", "vwap_band", proof_node(spike=True), 0)])
            t = parse_ts(s["timestamp_utc"])
            b = mk([(100.,)*4]*3, int(t*1000)-60000)
            b.real = bytearray([1]*3)
            with gzip.open(source, "wt", encoding="utf-8") as fh:
                fh.write(json.dumps(s) + "\n")
            job = ("dax", source, out_dir, (0,), D.MASK_OF, t+120)
            with patch.object(D, "_BARS", b):
                with self.assertRaisesRegex(ValueError, "provenance missing"):
                    D._rows_month(job)
                origin = root / "2026-01.inputs.json"
                origin.write_text(json.dumps(dict(codes=D.generation_codes(),
                    snapshot_sha256=D.file_hash(source), data={"synthetic": "fixture"},
                    bars=D.bars_identity(b),
                    command=["py", "dax_engine.py", "gen", "--end", "2026-01-05T10:00:00Z"])),
                    encoding="utf-8", newline="\n")
                D._rows_month(job)
                self.assertEqual(D._rows_month(job), ("2026-01", None))
                with patch.object(D, "load_development_bars", return_value=b):
                    self.assertEqual(len(D.load_rows("dax", "coded/0")), 1)
                    b.real[1] = 0
                    with self.assertRaisesRegex(ValueError, "cache input|execution data differs"):
                        D.load_rows("dax", "coded/0")
                b.real[1] = 1
                with self.assertRaisesRegex(ValueError, "cache input"):
                    D._rows_month((*job[:5], t+60))
                origin.write_text('{}', encoding="utf-8", newline="\n")
                with self.assertRaisesRegex(ValueError, "producer mismatch"):
                    D._rows_month(job)

    def test_current_rows_written_reused_and_loaded(self):
        # Synthetic current-Java input only; no archive or holdout loader.
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td, patch.object(D, "WORK", Path(td)):
            out_dir = Path(td) / "rows_btc"
            out_dir.mkdir()
            source = Path(td) / "2026-01.jsonl.gz"
            s = snap([cand(1, "short", "vwap", "vwap_band", proof_node(spike=True), 0)])
            with gzip.open(source, "wt", encoding="utf-8") as fh:
                fh.write(json.dumps(s) + "\n")
            source.with_name("2026-01.inputs.json").write_text(json.dumps(dict(
                codes=D.generation_codes(), snapshot_sha256=D.file_hash(source), data={"synthetic": "fixture"})),
                encoding="utf-8", newline="\n")
            job = ("btc", source, out_dir, (0,), D.MASK_OF, None)
            self.assertEqual(D._rows_month(job)[1]["rows"], 1)
            self.assertEqual(D._rows_month(job), ("2026-01", None))
            self.assertEqual(D.load_rows("btc", "coded/0")[0]["proof"], 0)
            out = out_dir / "2026-01.rows.jsonl"
            row = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(row.pop("proof_count_schema"), D.PROOF_COUNT_SCHEMA)
            out.write_text(json.dumps(row) + "\n", encoding="utf-8", newline="\n")
            meta = out_dir / "2026-01.rows.meta.json"
            metadata = json.loads(meta.read_text(encoding="utf-8"))
            metadata["rows_sha256"] = D.file_hash(out)
            meta.write_text(json.dumps(metadata), encoding="utf-8", newline="\n")
            # Even valid metadata cannot bless an old row envelope.
            with self.assertRaisesRegex(ValueError, "proof-count schema"):
                D.load_rows("btc", "coded/0")
            with self.assertRaisesRegex(ValueError, "proof-count schema"):
                D._rows_month(job)

    def test_old_rows_rejected_on_load_and_cache_reuse(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td, patch.object(D, "WORK", Path(td)):
            out_dir = Path(td) / "rows_dax"
            out_dir.mkdir()
            out = out_dir / "2026-01.rows.jsonl"
            out.write_text(json.dumps({"t": 1, "k": {"coded/0": {"t": 1, "proof": 2}}}) + "\n",
                           encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(ValueError, "proof-count schema"):
                D.load_rows("dax", "coded/0")
            with self.assertRaisesRegex(ValueError, "proof-count schema"):
                D._rows_month(("dax", "2026-01.jsonl.gz", out_dir, (0,), D.MASK_OF, None))

    def test_complete_months(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            raw = Path(td)
            d = dt.date(2026, 1, 1)
            while d <= dt.date(2026, 2, 10):
                (raw / f"{d:%Y-%m-%d}.bi5").write_bytes(b"")
                d += dt.timedelta(1)
            (raw / "2026-01-15.bi5").unlink()
            self.assertEqual(D.complete_months(raw, dt.date(2026, 1, 1), dt.date(2026, 2, 28)), [])
            (raw / "2026-01-15.bi5").write_bytes(b"")
            self.assertEqual(D.complete_months(raw, dt.date(2026, 1, 1), dt.date(2026, 2, 28)), ["2026-01"])
            # a range that ends inside February needs only the days up to its end
            self.assertEqual(D.complete_months(raw, dt.date(2026, 1, 1), dt.date(2026, 2, 10)), ["2026-01", "2026-02"])
            # a range that starts mid-month needs only the days from its start
            self.assertEqual(D.complete_months(raw, dt.date(2026, 1, 20), dt.date(2026, 1, 31)), ["2026-01"])

    def test_contiguous_runs(self):
        self.assertEqual(D.contiguous_runs(["2026-01", "2026-02", "2026-04", "2026-05", "2026-06", "2027-01"]),
                         [("2026-01", "2026-02"), ("2026-04", "2026-06"), ("2027-01", "2027-01")])
        self.assertEqual(D.contiguous_runs([]), [])
        self.assertEqual(D.contiguous_runs(["2025-12", "2026-01"]), [("2025-12", "2026-01")])

    def test_periods(self):
        ts = lambda y, m, d: dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp()
        self.assertEqual(D.dax_period(ts(2024, 11, 4)), "dev")
        self.assertEqual(D.dax_period(ts(2026, 4, 10) + 86399), "dev")
        self.assertEqual(D.dax_period(ts(2026, 4, 11)), "holdout")
        self.assertEqual(D.dax_period(ts(2026, 10, 9)), "holdout")
        self.assertEqual(D.dax_period(ts(2024, 11, 3)), "warmup")
        self.assertEqual(D.btc_period(ts(2025, 8, 31)), "hist")
        self.assertEqual(D.btc_period(ts(2025, 9, 1)), "dev")
        self.assertEqual(D.btc_period(ts(2026, 6, 26)), "burned")

    def test_holdout_needs_flag_and_reads_once(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            marker = Path(td) / "HOLDOUT_READ_DAX.json"
            rows = [{"t": dt.datetime(2026, 3, 1, tzinfo=dt.timezone.utc).timestamp()},
                    {"t": dt.datetime(2026, 5, 1, tzinfo=dt.timezone.utc).timestamp()}]
            self.assertEqual([D.dax_period(r["t"]) for r in D.select_rows(rows, False, marker)], ["dev"])
            self.assertFalse(marker.exists())                      # nothing read, no marker
            got = D.select_rows(rows, True, marker)
            self.assertEqual([D.dax_period(r["t"]) for r in got], ["dev", "holdout"])
            self.assertFalse(marker.exists())                      # the marker is written when the read is complete
            D.mark_holdout_read(1, marker)
            self.assertTrue(marker.exists())
            with self.assertRaises(SystemExit):                    # second read refused
                D.select_rows(rows, True, marker)
            self.assertEqual([D.dax_period(r["t"]) for r in D.select_rows(rows, False, marker)], ["dev"])   # dev still fine

    def test_null_draws_only_real_minutes(self):
        # Real bars only in minutes 600..659; no next-bar-real requirement.
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            day0 = 1_700_006_400_000 - (1_700_006_400_000 % 86400000)
            rows = [(day0 + (600 + i) * 60000, 100 + i % 3, 101 + i % 3, 99, 100.5, 1.0) for i in range(60)]
            write_klines(Path(td) / "a.csv", rows)
            b = T.load_bars_1m(td, fill_gaps=True)
            row = dict(t=day0/1000+600*60, verdict="SETUP_FORMING", setup="ct_long",
                       dir="long", zone="vwap", ztype="vwap_band", zprice=100., stop=98., target=105.)
            result = D.random_entry_null([row], b, seed=1,
                                        session=dict(timezone="UTC", start="10:00", end="11:00"))
            for draw in result["draws"]:
                self.assertEqual(draw["sampled"], 1)
                for trade in draw["trades"]:
                    self.assertEqual(b.real[trade["signal_i"]], 1)
                    if trade["filled"]:
                        self.assertEqual(b.real[trade["fill_i"]], 1)


def readiness_fixture(root):
    """All twelve numbered PRE_REG_TEMPLATE headings; synthetic evidence only."""
    p = Path(root) / "readiness.json"
    p.write_text(json.dumps({"items": {str(i): dict(status="ANSWERED",
        answer="Synthetic protocol answer", evidence="synthetic.md:1")
        for i in range(1, 13)}}), encoding="utf-8", newline="\n")
    return p


class TestReadinessGate(unittest.TestCase):
    def test_h8_second_arm_same_day_is_counted_and_rerender_is_idempotent(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            root = Path(td)
            p = readiness_fixture(root)
            split = root / "split.json"
            split.write_text(json.dumps(dict(design_end_utc="2026-04-10T23:58:00Z",
                holdout_start_utc="2026-04-11T00:00:00Z", embargo_s=0)), encoding="utf-8", newline="\n")
            session = root / "session.json"
            session.write_text(json.dumps(dict(timezone="UTC", start="10:00", end="12:00",
                source="Synthetic quote, synthetic.md:1")), encoding="utf-8", newline="\n")
            b = mk([(100.,)*4]*2, int(D.T_DAX_START*1000))
            args = ["report", "--market", "dax", "--smoke", "--split-manifest", str(split),
                    "--null-session", str(session), "--readiness-manifest", str(p)]
            def synthetic_simulation(*args, **kwargs):
                self.assertTrue(list((root / "runs").glob("*.json")), "inputs must be durable before outcomes")
                return []
            with patch.object(D, "WORK", root), patch.object(D, "DAX_SNAPS", root), \
                 patch.object(D, "REPORT", root/"report.md"), patch.object(D, "REGISTRY", root/"trials.csv"), \
                 patch.object(D, "git", return_value="synthetic"), \
                 patch.object(D, "require_download_coverage"), \
                 patch.object(D, "load_development_bars", return_value=b), \
                 patch.object(D, "load_rows", return_value=[]), patch.object(D, "simulate", side_effect=synthetic_simulation):
                D.main(args + ["--shifts", "0"])
                D.main(args + ["--shifts", "1"])
                registry = root / "TRIAL_REGISTRY_SMOKE.csv"
                with registry.open(encoding="utf-8") as fh:
                    rows = list(csv.DictReader(fh))
                # EXPECT: four variants per look, two distinct identities today.
                self.assertEqual(len(rows), 8)
                self.assertEqual(len({r["run_id"] for r in rows}), 2)
                D.main(args + ["--shifts", "1"])
                with registry.open(encoding="utf-8") as fh:
                    self.assertEqual(list(csv.DictReader(fh)), rows)
                manifests = sorted((root / "runs").glob("*.json"))
                self.assertEqual(len(manifests), 2)
                frozen = json.loads(manifests[0].read_text(encoding="utf-8"))
                self.assertIn("MyTradingSys/system/net_rr_floor.json", frozen["codes"])
                self.assertEqual(frozen["seeds"]["bootstrap"], 12345)
                self.assertEqual(frozen["split"]["identity"], D.load_split(split)["identity"])
                D.main(args + ["--shifts", "1", "--look-id", "fresh-recall-design-look"])
                with registry.open(encoding="utf-8") as fh:
                    extra = list(csv.DictReader(fh))
                self.assertEqual((len(extra), len({r["run_id"] for r in extra})), (12, 3))
                # Editing an immutable manifest cannot bless an old result.
                manifests[0].write_text('{}\n', encoding="utf-8", newline="\n")
                shift = str(frozen["shifts"][0])
                with self.assertRaisesRegex(ValueError, "immutable run manifest"):
                    D.main(args + ["--shifts", shift])

    def test_missing_partial_or_unanswered_manifest_before_any_simulation(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            p = readiness_fixture(td)
            complete = json.loads(p.read_text(encoding="utf-8"))
            cases = [("missing", None), ("absent file", Path(td)/"absent.json")]
            for i in range(1, 13):
                obj = copy.deepcopy(complete)
                del obj["items"][str(i)]
                cases.append(("missing item %d" % i, obj))
                for changes in [dict(status="NOT_ANSWERED"), dict(answer="TODO"),
                                dict(evidence=""), dict(evidence="NOT_IN_DATA"),
                                dict(status="WAIVED", approver=" ")]:
                    obj = copy.deepcopy(complete)
                    obj["items"][str(i)].update(changes)
                    cases.append(("item %d %s" % (i, changes), obj))
            for label, obj in cases:
                with self.subTest(case=label):
                    path = obj
                    if isinstance(obj, dict):
                        p.write_text(json.dumps(obj), encoding="utf-8", newline="\n")
                        path = p
                    a = SimpleNamespace(readiness_manifest=path, read_holdout=False,
                                        shifts=[0], months=None, market="dax")
                    with patch.object(D, "load_split", return_value=dict(dev_end=D.T_DAX_HOLD)), \
                         patch.object(D, "load_null_session", return_value={}), \
                         patch.object(D, "require_download_coverage", side_effect=AssertionError("data accessed before readiness")) as coverage, \
                         patch.object(D, "load_development_bars") as bars, \
                         patch.object(D, "simulate") as sim, \
                         patch.object(D, "mark_holdout_read") as reservation:
                        with self.assertRaisesRegex(ValueError, "readiness manifest"):
                            D.build_report(a)
                        coverage.assert_not_called()
                        bars.assert_not_called()
                        sim.assert_not_called()
                        reservation.assert_not_called()

    def test_complete_manifest_and_dax_cli_with_btc_cache(self):
        # Exercise the real CLI -> cmd_report -> build_report path. All data,
        # report and registry paths are local fixtures; git is never executed.
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            root = Path(td)
            p = readiness_fixture(root)
            split = root/"split.json"
            split.write_text(json.dumps(dict(design_end_utc="2026-04-10T23:58:00Z",
                holdout_start_utc="2026-04-11T00:00:00Z", embargo_s=0)), encoding="utf-8", newline="\n")
            session = root/"session.json"
            session.write_text(json.dumps(dict(timezone="UTC", start="10:00", end="12:00",
                source="Synthetic quote, synthetic.md:1")), encoding="utf-8", newline="\n")
            (root/"rows_btc").mkdir()
            (root/"rows_btc"/"2026-01.rows.meta.json").write_text(
                '{"rows": 1, "mask_changed": 0, "cut": 0}', encoding="utf-8", newline="\n")
            b = mk([(100.,)*4]*2, int(D.T_DAX_START*1000))
            for waived in (False, True):
                obj = json.loads(p.read_text(encoding="utf-8"))
                if waived:
                    obj["items"]["5"] = dict(status="WAIVED", answer="Synthetic price-only scope",
                        evidence="synthetic-approval.md:1", approver="Synthetic Owner")
                    p.write_text(json.dumps(obj), encoding="utf-8", newline="\n")
                with self.subTest(waived=waived), \
                     patch.object(D, "WORK", root), patch.object(D, "DAX_SNAPS", root), \
                     patch.object(D, "REPORT", root/"report.md"), patch.object(D, "REGISTRY", root/"trials.csv"), \
                     patch.object(D, "git", return_value="synthetic"), patch.object(D, "sha", return_value="fixture"), \
                     patch.object(D, "require_download_coverage"), \
                     patch.object(D, "load_development_bars", return_value=b), \
                     patch.object(T, "load_bars_1m", side_effect=AssertionError("BTC data read")) as btc, \
                     patch.object(D, "load_rows", return_value=[]) as rows, \
                     patch.object(D, "simulate", return_value=[]) as sim:
                    D.main(["report", "--market", "dax", "--smoke", "--split-manifest", str(split),
                            "--null-session", str(session), "--readiness-manifest", str(p)])
                    self.assertEqual([c.args[0] for c in sim.call_args_list], ["dax"]*4)
                    self.assertEqual([c.args[0] for c in rows.call_args_list], ["dax"])
                    btc.assert_not_called()
                    self.assertIn("| DAX / coded / s0 / A |", D.REPORT.read_text(encoding="utf-8"))
                    text = D.REPORT.read_text(encoding="utf-8")
                    self.assertIn(D.load_readiness(p)["sha256"], text)
                    self.assertIn("Synthetic Owner" if waived else "Synthetic protocol answer", text)

    def test_malformed_manifest_and_no_holdout_reservation(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            p = readiness_fixture(td)
            complete = json.loads(p.read_text(encoding="utf-8"))
            cases = ["{", "null", "[]", '{}', '{"items": []}']
            for change in [dict(answer=None), dict(evidence=False), dict(status="NOT_IN_DATA"),
                           dict(status="WAIVED", approver="TODO"), dict(status="WAIVED", approver=7)]:
                obj = copy.deepcopy(complete)
                obj["items"]["3"].update(change)
                cases.append(json.dumps(obj))
            for raw in cases:
                with self.subTest(raw=raw):
                    p.write_text(raw, encoding="utf-8", newline="\n")
                    with patch.object(D, "require_full_dev") as full, \
                         patch.object(D, "load_rows") as rows, \
                         patch.object(D, "mark_holdout_read") as reserve:
                        with self.assertRaisesRegex(ValueError, "readiness manifest"):
                            D.build_report(SimpleNamespace(readiness_manifest=p, read_holdout=True))
                        full.assert_not_called()
                        rows.assert_not_called()
                        reserve.assert_not_called()


class TestPreprocessingIsolation(unittest.TestCase):
    """RV02 R1. Expected epochs are hand-derived: 2026-01-01Z = 1735689600 + 365*86400 = 1767225600;
    2026-06-01Z = that + (31+28+31+30+31)*86400 = 1780272000."""
    CUT = 1780272000

    @staticmethod
    def split_file(root, hold="2026-06-01T00:00:00Z"):
        path = Path(root) / "split.json"
        path.write_text(json.dumps(dict(design_end_utc="2026-02-01T00:00:00Z", holdout_start_utc=hold,
                                        embargo_s=0)), encoding="utf-8", newline="\n")
        return path

    def test_gen_without_manifest_touches_no_subprocess_or_data(self):
        with patch.object(D.subprocess, "run", side_effect=AssertionError("child process reached")) as run:
            with self.assertRaisesRegex(ValueError, "split manifest"):
                D.cmd_gen(SimpleNamespace(start=None, end=None, months=None, shards=1, read_holdout=False,
                                          split_manifest=None))
            with self.assertRaises(ValueError):
                D.main(["all", "--market", "dax"])
        run.assert_not_called()

    def test_gen_convert_and_engine_end_are_clipped_to_development(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            root = Path(td)
            calls = []
            a = SimpleNamespace(start=None, end=None, months=None, shards=1, read_holdout=False,
                                split_manifest=self.split_file(root))
            with patch.object(D, "DAX_ARCHIVE", root / "a"), patch.object(D, "DAX_SNAPS", root / "s"), \
                 patch.object(D, "DAX_RAW", root / "raw"), \
                 patch.object(D, "complete_months", return_value=["2026-05"]), \
                 patch.object(D, "generation_environment", return_value={"x": "y"}), \
                 patch.object(D, "load_development_bars", return_value=mk([(100.,) * 4] * 3, 0)), \
                 patch.object(D.subprocess, "run", side_effect=lambda c, **k: calls.append(c)):
                D.cmd_gen(a)
            convert, gen = calls[0], calls[1]
            self.assertEqual(convert[convert.index("--end-ms") + 1], str(self.CUT * 1000))
            self.assertEqual(gen[gen.index("--end") + 1], "2026-05-31T23:59:00Z")   # DAX_END is 2026-10-09

    def test_gen_end_never_passes_last_complete_minute(self):
        day = dt.date(2026, 1, 5)
        cut = 1767225600 + 4 * 86400 + 10 * 3600     # 2026-01-05T10:00:00Z
        self.assertEqual(D.gen_end(day, cut), "2026-01-05T09:59:00Z")
        self.assertEqual(D.gen_end(day, None), "2026-01-05T23:59:00Z")

    def test_future_snapshot_payload_is_not_decoded(self):
        from snapshots import parse_ts
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td, patch.object(D, "WORK", Path(td)):
            root = Path(td)
            out_dir = root / "rows_dax"
            out_dir.mkdir()
            source = root / "2026-01.jsonl.gz"
            good = snap([cand(1, "short", "vwap", "vwap_band", proof_node(spike=True), 0)])
            t = parse_ts(good["timestamp_utc"])
            b = mk([(100.,) * 4] * 3, int(t * 1000) - 60000)
            b.real = bytearray([1] * 3)
            with gzip.open(source, "wt", encoding="utf-8") as fh:
                fh.write(json.dumps(good) + "\n")
                fh.write('{"timestamp_utc": "2026-01-05T10:30:00Z", "payload": <<not json, future>>\n')
            source.with_name("2026-01.inputs.json").write_text(json.dumps(dict(
                codes=D.generation_codes(), snapshot_sha256=D.file_hash(source), data={"x": "y"},
                command=["py", "dax_engine.py", "gen", "--end", "2026-01-05T10:00:00Z"],
                bars=D.bars_identity(b))),
                encoding="utf-8", newline="\n")
            with patch.object(D, "_BARS", b):
                name, stats = D._rows_month(("dax", source, out_dir, (0,), D.MASK_OF, t + 120))
            self.assertEqual(stats["cut"], 1)
            self.assertEqual(stats["rows"], 1)

    def test_snapshot_produced_past_cutoff_is_refused(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td:
            source = Path(td) / "2026-01.jsonl.gz"
            with gzip.open(source, "wt", encoding="utf-8") as fh:
                fh.write("{}\n")
            origin = source.with_name("2026-01.inputs.json")
            for command, pattern in ((["gen", "--end", "2026-01-05T10:00:00Z"], "past the development cutoff"),
                                     ([], "producer end absent")):
                origin.write_text(json.dumps(dict(codes=D.generation_codes(), snapshot_sha256=D.file_hash(source),
                                                  command=command)), encoding="utf-8", newline="\n")
                with self.assertRaisesRegex(ValueError, pattern):
                    D.cache_inputs("dax", source, (0,), D.MASK_OF, 1767225600 + 4 * 86400 + 10 * 3600, 1.0)

    def test_month_scope_excludes_future_months_from_accounting_inputs(self):
        self.assertTrue(D.month_in_scope("2026-05.meta.json", self.CUT))
        self.assertFalse(D.month_in_scope("2026-06.meta.json", self.CUT))   # starts exactly at the cutoff
        self.assertFalse(D.month_in_scope("2026-09.rows.jsonl", self.CUT))
        self.assertTrue(D.month_in_scope("2099-01.meta.json", None))

    def test_load_rows_does_not_open_future_month_caches(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td, patch.object(D, "WORK", Path(td)):
            rows = Path(td) / "rows_dax"
            rows.mkdir()
            (rows / "2026-09.rows.jsonl").write_text("garbage", encoding="utf-8", newline="\n")
            split = D.load_split(self.split_file(td))
            self.assertEqual(D.load_rows("dax", "coded/0", split=split), [])


class TestCutoffBoundary(unittest.TestCase):
    def test_rows_at_cutoff_minus_equal_plus_one_ms(self):
        from snapshots import parse_ts
        cut = 1767225600 + 4 * 86400 + 10 * 3600     # 2026-01-05T10:00:00Z
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td, patch.object(D, "WORK", Path(td)):
            root = Path(td)
            out_dir = root / "rows_dax"
            out_dir.mkdir()
            source = root / "2026-01.jsonl.gz"
            stamps = ("2026-01-05T09:59:59.999000Z", "2026-01-05T10:00:00Z", "2026-01-05T10:00:00.001000Z")
            b = mk([(100.,) * 4] * 6, (cut - 120) * 1000)
            b.real = bytearray([1] * 6)
            with gzip.open(source, "wt", encoding="utf-8") as fh:
                for ts in stamps:
                    fh.write(json.dumps(snap([cand(1, "short", "vwap", "vwap_band", proof_node(spike=True), 0)], t=ts)) + "\n")
            source.with_name("2026-01.inputs.json").write_text(json.dumps(dict(
                codes=D.generation_codes(), snapshot_sha256=D.file_hash(source), data={"x": "y"},
                bars=D.bars_identity(b),
                command=["py", "gen", "--end", "2026-01-05T09:59:00Z"])), encoding="utf-8", newline="\n")
            with patch.object(D, "_BARS", b):
                _, stats = D._rows_month(("dax", source, out_dir, (0,), D.MASK_OF, cut))
            self.assertEqual((stats["rows"], stats["cut"]), (1, 2))
            kept = [json.loads(x)["t"] for x in (out_dir / "2026-01.rows.jsonl").read_text().splitlines()]
            self.assertEqual(kept, [parse_ts(stamps[0])])
            self.assertLess(kept[0], cut)


class TestProducerDataBinding(unittest.TestCase):
    """RV02 R4. Snapshots frozen at execution price 100, then the execution bars are revised to 200: fresh rows and
    reports must be refused until the snapshots are regenerated. Synthetic only; no archive or holdout bytes."""
    CUT_OFFSET = 120

    @staticmethod
    def bars(price, t):
        b = mk([(price,) * 4] * 3, int(t * 1000) - 60000)
        b.real = bytearray([1] * 3)
        return b

    def build(self, td, producer_price):
        from snapshots import parse_ts
        root = Path(td)
        out_dir = root / "rows_dax"
        out_dir.mkdir()
        source = root / "2026-01.jsonl.gz"
        s = snap([cand(1, "short", "vwap", "vwap_band", proof_node(spike=True), 0)])
        t = parse_ts(s["timestamp_utc"])
        with gzip.open(source, "wt", encoding="utf-8") as fh:
            fh.write(json.dumps(s) + "\n")
        origin = dict(codes=D.generation_codes(), snapshot_sha256=D.file_hash(source), data={"synthetic": "fixture"},
                      command=["py", "dax_engine.py", "gen", "--end", "2026-01-05T10:00:00Z"])
        if producer_price is not None:
            origin["bars"] = D.bars_identity(self.bars(producer_price, t))
        source.with_name("2026-01.inputs.json").write_text(json.dumps(origin), encoding="utf-8", newline="\n")
        return source, out_dir, t

    def test_revised_execution_bars_refuse_fresh_rows_until_regenerated(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td, patch.object(D, "WORK", Path(td)):
            source, out_dir, t = self.build(td, 100.)
            job = ("dax", source, out_dir, (0,), D.MASK_OF, t + self.CUT_OFFSET)
            with patch.object(D, "_BARS", self.bars(200., t)):
                with self.assertRaisesRegex(ValueError, "execution data differs"):
                    D._rows_month(job)
            self.assertEqual(list(out_dir.iterdir()), [])             # nothing was built
            with patch.object(D, "_BARS", self.bars(100., t)):
                self.assertEqual(D._rows_month(job)[1]["rows"], 1)    # same data passes
                self.assertEqual(D._rows_month(job), ("2026-01", None))
            with patch.object(D, "_BARS", self.bars(200., t)):         # reuse of an existing cache is refused too
                with self.assertRaisesRegex(ValueError, "execution data differs"):
                    D._rows_month(job)

    def test_producer_without_bars_identity_requires_regeneration(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td, patch.object(D, "WORK", Path(td)):
            source, out_dir, t = self.build(td, None)
            job = ("dax", source, out_dir, (0,), D.MASK_OF, t + self.CUT_OFFSET)
            with patch.object(D, "_BARS", self.bars(100., t)):
                with self.assertRaisesRegex(ValueError, "lacks the execution bars identity"):
                    D._rows_month(job)

    def test_report_stage_refuses_revised_bars_against_cached_rows(self):
        with tempfile.TemporaryDirectory(prefix="mts_dax_bt_") as td, patch.object(D, "WORK", Path(td)):
            source, out_dir, t = self.build(td, 100.)
            job = ("dax", source, out_dir, (0,), D.MASK_OF, t + self.CUT_OFFSET)
            with patch.object(D, "_BARS", self.bars(100., t)):
                D._rows_month(job)
            with patch.object(D, "load_development_bars", return_value=self.bars(100., t)):
                self.assertEqual(len(D.load_rows("dax", "coded/0")), 1)
            with patch.object(D, "load_development_bars", return_value=self.bars(200., t)):
                with self.assertRaisesRegex(ValueError, "execution data differs"):
                    D.load_rows("dax", "coded/0")


class TestExactNetRrGate(unittest.TestCase):
    """RV02 R2. Hand arithmetic (FORMULAS.md section 17, FDAX fee 0.000005/side, entry 100 so cost = 2*0.000005*100 = 0.001):
    target 101.25 -> (1.25-0.001)/(1+0.001) = 1249/1001 = 1.24775... (< 1.25, serialized as 1.25);
    target 101.26 -> (1.26-0.001)/1.001 = 1259/1001 = 1.25774... (>= 1.25)."""

    @staticmethod
    def boundary_row(direction, move, shift=4):
        from verdict import compute_verdict
        target = round(100.0 + move if direction == "long" else 100.0 - move, 2)
        stop = 99.0 if direction == "long" else 101.0
        exact = (move - 0.001) / 1.001
        c = cand(1, direction, "vwap", "vwap_band", proof_node("MODERATE"), 1, gross=move, net=round(exact, 2))
        c["math"]["target"] = target
        c["math"]["stop"] = stop
        c["math"]["net_rr_sanity"] = round(exact, 2) >= 1.25
        wire = json.loads(json.dumps(snap([c])))      # the real JSON producer/consumer boundary
        exact_v = D.rows_for_snapshot(wire, parse_ts, aligned,
            lambda s, pd: D.exact_rr_verdict(s, pd, 1.25, compute_verdict), shifts=(shift,))["coded/%d" % shift]["verdict"]
        old_v = D.rows_for_snapshot(wire, parse_ts, aligned,
            lambda s, pd: compute_verdict(s, pd, floor=1.25), shifts=(shift,))["coded/%d" % shift]["verdict"]
        return exact, round(exact, 2), exact_v, old_v

    def test_exact_value_matches_hand_arithmetic(self):
        c = cand(1, "long", "vwap", "vwap_band", proof_node("MODERATE"), 1)
        c["math"]["target"] = 101.25
        self.assertAlmostEqual(D.exact_net_rr(c), 1249 / 1001, places=12)
        c["math"]["target"] = 101.26
        self.assertAlmostEqual(D.exact_net_rr(c), 1259 / 1001, places=12)

    def test_below_floor_serialized_as_floor_stays_wait_rr_both_directions(self):
        for direction in ("long", "short"):
            exact, shown, exact_v, old_v = self.boundary_row(direction, 1.25)
            self.assertLess(exact, 1.25)
            self.assertEqual(shown, 1.25)                  # display rounding hides the shortfall
            self.assertEqual(exact_v, "WAIT_RR", direction)
            self.assertNotEqual(old_v, "WAIT_RR", direction)   # the pre-fix consumer let it through

    def test_at_or_above_floor_stays_eligible_both_directions(self):
        for direction in ("long", "short"):
            exact, shown, exact_v, old_v = self.boundary_row(direction, 1.26)
            self.assertGreater(exact, 1.25)
            self.assertEqual(exact_v, old_v, direction)
            self.assertNotEqual(exact_v, "WAIT_RR", direction)

    def test_input_snapshot_is_not_modified_and_bad_geometry_changes_nothing(self):
        from verdict import compute_verdict
        c = cand(1, "long", "vwap", "vwap_band", proof_node("MODERATE"), 1, gross=1.25, net=1.25)
        c["math"]["target"] = 101.25
        s = snap([c])
        before = json.dumps(s, sort_keys=True)
        D.exact_rr_verdict(s, "aligned", 1.25, compute_verdict)
        self.assertEqual(json.dumps(s, sort_keys=True), before)
        del c["math"]["stop"]
        self.assertIsNone(D.exact_net_rr(c))
        self.assertEqual(D.exact_rr_verdict(s, "aligned", 1.25, compute_verdict)["net_rr"], 1.25)

    def test_exact_equality_with_floor_is_eligible(self):
        from verdict import compute_verdict
        c = cand(1, "long", "vwap", "vwap_band", proof_node("MODERATE"), 1, gross=1.25, net=1.25)
        c["math"]["target"] = 101.25
        floor = D.exact_net_rr(c)                       # 1249/1001: exactly at the floor, so >= passes
        s = snap([c])
        v = D.exact_rr_verdict(s, "aligned", floor, compute_verdict)
        self.assertNotEqual(v["verdict"], "WAIT_RR")
        self.assertAlmostEqual(v["net_rr"], 1.25)       # not tightened: exact is not below the floor


if __name__ == "__main__":
    unittest.main()
