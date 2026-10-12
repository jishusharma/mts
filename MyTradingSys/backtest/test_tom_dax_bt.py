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
from unittest.mock import patch
from array import array
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fees as F  # noqa: E402
import tom_bt as T  # noqa: E402
import tom_dax_bt as D  # noqa: E402


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
        self.td = tempfile.TemporaryDirectory()
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
        # Null fills at minute 1, expires at 41 (closed), stops at real minute 42.
        b.real[1] = 1
        with patch.object(D, "draw_real_minute", return_value=0):
            real, p, null = D.random_entry_null([dict(row, filled=True, reason="timeout", gross_r=0., zone_tf="5m")] * 30,
                                               b, n_perm=1)
        self.assertEqual((real, p, null), (0., .5, -3.))

    def test_missing_download_is_rejected_before_archive_read(self):
        # Completed empty days are coverage evidence; absent files are not closures.
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td)
            start, end = dt.date(2026, 1, 1), dt.date(2026, 1, 3)
            for d in (start, end):
                (raw / (d.isoformat() + ".bi5")).write_bytes(b"")
            with self.assertRaisesRegex(SystemExit, "missing .*2026-01-02.bi5"):
                D.require_download_coverage(raw, start, end)
            (raw / "2026-01-02.bi5").write_bytes(b"")
            D.require_download_coverage(raw, start, end)
            with patch.object(D, "DAX_RAW", raw), patch.object(T, "load_bars_1m") as load:
                with self.assertRaisesRegex(SystemExit, "incomplete DAX download coverage"):
                    D.build_report(SimpleNamespace(months=["2026-01"], shifts=[0], read_holdout=False))
                load.assert_not_called()


# ------------------------------------------------------------------ c) market-open filter
class TestOpenFilter(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
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
    def test_daxfee_sets_net_to_gross_on_every_candidate(self):
        a = cand(1, "long", "daily_poc", "daily_poc", proof_node("MODERATE", False, None, False, True, False), 1, gross=3.0, net=1.0)
        b = cand(2, "long", "vwap", "vwap_band", proof_node(), 0, gross=2.5, net=0.7)
        s = snap([a, b])
        D.daxfee(s)
        self.assertEqual([c["math"]["net_rr"] for c in s["setup_candidates"]], [3.0, 2.5])

    def test_pair_differs_when_net_is_below_floor(self):
        # gross 3.0 but net 1.0 (< any floor in net_rr_floor.json): as coded WAIT_RR; DAX-fee passes the RR gate,
        # proof 1 + shift 2 = 3 -> WATCH (proof >= 3, < 5); a synthetic extension, not a tuned arm.
        a = cand(1, "long", "daily_poc", "daily_poc", proof_node("MODERATE", False, None, False, True, False), 1, gross=3.0, net=1.0)
        s = snap([a])
        r0 = D.rows_for_snapshot(copy.deepcopy(s), parse_ts, aligned, shifts=(0, 2))
        self.assertEqual(r0["coded/2"]["verdict"], "WAIT_RR")
        self.assertEqual(r0["daxfee/2"]["verdict"], "WATCH")
        self.assertEqual(r0["daxfee/0"]["verdict"], "WAIT_PROOF")   # proof 1 < 3
        self.assertEqual(r0["daxfee/2"]["net_rr"], 3.0)
        self.assertEqual(r0["coded/2"]["net_rr"], 1.0)
        self.assertEqual(r0["daxfee/2"]["proof"], 3)

    def test_inputs_not_mutated(self):
        a = cand(1, "long", "daily_poc", "daily_poc", proof_node("MODERATE", True, None, False, True, False), 2, net=1.0)
        s = snap([a])
        before = copy.deepcopy(s)
        D.rows_for_snapshot(s, parse_ts, aligned)
        self.assertEqual(s, before)


# ------------------------------------------------------------------ f) driver helpers
class TestDriver(unittest.TestCase):
    def test_current_rows_written_reused_and_loaded(self):
        # Synthetic current-Java input only; no archive or holdout loader.
        with tempfile.TemporaryDirectory() as td, patch.object(D, "WORK", Path(td)):
            out_dir = Path(td) / "rows_btc"
            out_dir.mkdir()
            source = Path(td) / "2026-01.jsonl.gz"
            s = snap([cand(1, "short", "vwap", "vwap_band", proof_node(spike=True), 0)])
            with gzip.open(source, "wt", encoding="utf-8") as fh:
                fh.write(json.dumps(s) + "\n")
            job = ("btc", source, out_dir, (0,), D.MASK_OF, None)
            self.assertEqual(D._rows_month(job)[1]["rows"], 1)
            self.assertEqual(D._rows_month(job), ("2026-01", None))
            self.assertEqual(D.load_rows("btc", "coded/0")[0]["proof"], 0)
            out = out_dir / "2026-01.rows.jsonl"
            row = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(row.pop("proof_count_schema"), D.PROOF_COUNT_SCHEMA)
            out.write_text(json.dumps(row) + "\n", encoding="utf-8", newline="\n")
            # Even valid metadata cannot bless an old row envelope.
            with self.assertRaisesRegex(ValueError, "proof-count schema"):
                D.load_rows("btc", "coded/0")
            with self.assertRaisesRegex(ValueError, "proof-count schema"):
                D._rows_month(job)

    def test_old_rows_rejected_on_load_and_cache_reuse(self):
        with tempfile.TemporaryDirectory() as td, patch.object(D, "WORK", Path(td)):
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
        with tempfile.TemporaryDirectory() as td:
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
        with tempfile.TemporaryDirectory() as td:
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
        # one UTC day-aligned archive: real bars only in minutes 600..659; a null entry must never land elsewhere
        with tempfile.TemporaryDirectory() as td:
            day0 = 1_700_006_400_000 - (1_700_006_400_000 % 86400000)
            rows = [(day0 + (600 + i) * 60000, 100 + i % 3, 101 + i % 3, 99, 100.5, 1.0) for i in range(60)]
            write_klines(Path(td) / "a.csv", rows)
            b = T.load_bars_1m(td, fill_gaps=True)
            import random
            rng = random.Random(1)
            for _ in range(200):
                k = D.draw_real_minute(b, day0 // 1000, rng)
                self.assertEqual(b.real[k], 1)
                self.assertEqual(b.real[k + 1], 1)                 # next-bar-open fill needs a real next bar


if __name__ == "__main__":
    unittest.main()
