"""
Tests for run_cc_setups.py. Synthetic bars only; no real data. Expected numbers are hand-computed
from bt_engine's documented accounting (R = |entry - stop|, fee_r = fee * price / risk per leg).
"""
import contextlib
import io
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from MyTradingSys.backtest.layers.cryptocred import run_cc_setups as R

MIN = 60000


def bar(t, o, h, l, c):
    return {"t": t, "o": o, "h": h, "l": l, "c": c}


def ms(year, month=6, day=1):
    return int(datetime(year, month, day, tzinfo=timezone.utc).timestamp() * 1000)


def one_signal(t0):
    # long, entry 100, stop 99 (risk 1), single target 102 (2R)
    return {"side": "long", "entry_price": 100.0, "entry_t": t0, "stop": 99.0,
            "targets": [(102.0, 1.0)], "meta": {"setup": "x"}}


def target_bars(t0):
    return [bar(t0, 100, 100, 100, 100), bar(t0 + MIN, 100, 102.5, 99.5, 102), bar(t0 + 2 * MIN, 102, 102, 102, 102)]


def mk(t, pct):
    return {"t": t, "net_pct": pct, "net_r": pct * 100, "net_nofund_pct": pct, "net_nofund_r": pct * 100,
            "gross_r": 0.0}


class TestSplit(unittest.TestCase):
    def test_bars_split_is_chronological_70_30(self):
        bars = [bar(i * MIN, 1, 1, 1, 1) for i in range(10)]
        a, b, n_is = R.chronological_split(bars)
        self.assertEqual((len(a), len(b), n_is), (7, 3, 7))
        self.assertLess(a[-1]["t"], b[0]["t"])
        self.assertEqual(a + b, bars)

    def test_trades_split_on_time_not_order(self):
        trades = [mk(500, 0.01), mk(100, 0.01), mk(300, 0.01), mk(299, 0.01)]
        tis, toos = R.split_trades(trades, 300)
        self.assertEqual(sorted(t["t"] for t in tis), [100, 299])
        self.assertEqual(sorted(t["t"] for t in toos), [300, 500])

    def test_run_setup_uses_first_70pct_as_is(self):
        bars = [bar(i * MIN, 100, 100, 100, 100) for i in range(100)]
        res = R.run_setup("stub", bars, bars, [], MIN, setup_fn=lambda b: [])
        self.assertEqual(res["split_t"], 70 * MIN)
        self.assertIsNone(res["pbo"])
        self.assertIn("N/A", res["pbo_note"])


class TestFees(unittest.TestCase):
    def setUp(self):
        self.t0 = 0
        self.bars = target_bars(self.t0)

    def test_all_taker_fee_is_exactly_hand_computed(self):
        # gross 2R. Entry taker 0.0005*100/1 = 0.05R, target 0.0005*102/1 = 0.051R -> net 1.899R
        tr = R.build_trades([one_signal(self.t0)], self.bars, [], "all_taker", MIN)
        self.assertEqual(len(tr), 1)
        self.assertAlmostEqual(tr[0]["gross_r"], 2.0, places=12)
        self.assertAlmostEqual(tr[0]["net_r"], 1.899, places=12)
        self.assertAlmostEqual(tr[0]["gross_r"] - tr[0]["net_r"], 0.101, places=12)
        self.assertAlmostEqual(tr[0]["net_pct"], 1.899 * 0.01, places=12)  # risk/entry = 1%
        self.assertAlmostEqual(tr[0]["net_nofund_r"], tr[0]["net_r"], places=12)

    def test_maker_entry_variant_pays_no_fee_on_entry_or_target(self):
        tr = R.build_trades([one_signal(self.t0)], self.bars, [], "maker_entry", MIN)
        self.assertAlmostEqual(tr[0]["net_r"], 2.0, places=12)  # Deribit maker = 0

    def test_stop_exit_pays_taker_in_both_variants(self):
        bars = [bar(0, 100, 100, 100, 100), bar(MIN, 100, 100, 98.9, 99)]  # gap-free stop hit at 99
        a = R.build_trades([one_signal(0)], bars, [], "all_taker", MIN)[0]
        m = R.build_trades([one_signal(0)], bars, [], "maker_entry", MIN)[0]
        self.assertAlmostEqual(a["gross_r"], -1.0, places=12)
        self.assertAlmostEqual(a["net_r"], -1.0 - 0.05 - 0.0495, places=12)
        self.assertAlmostEqual(m["net_r"], -1.0 - 0.0495, places=12)

    def test_funding_reduces_net_but_not_nofund(self):
        # long pays positive funding: rate 0.001 inside the hold (MIN, 2*MIN], close of that bar 102 -> 0.001*102/100 of
        # notional = 0.00102 of entry = 0.102R at risk 1% -> net_r drops by 0.102, nofund unchanged.
        # The settlement sits mid-bar, not on the entry instant (t_in < s, T03-F2); zero-rate records at 0 and 3*MIN
        # make the records span the hold (B103 fail closed) without charging anything.
        tr = R.build_trades([one_signal(0)], self.bars, [(0, 0.0), (MIN + MIN // 2, 0.001), (3 * MIN, 0.0)], "all_taker", MIN)[0]
        self.assertAlmostEqual(tr["net_nofund_r"], 1.899, places=9)
        self.assertAlmostEqual(tr["net_r"], 1.899 - 0.102, places=9)

    def test_signal_entry_is_moved_to_end_of_signal_bar(self):
        # 1h signal bar at t=0; a 1m bar inside that hour must not be used for stop/target
        bars = [bar(i * MIN, 100, 100, 100, 100) for i in range(60)]
        bars[10] = bar(10 * MIN, 100, 103, 100, 103)  # would hit target inside the signal bar
        bars.append(bar(60 * MIN, 100, 100, 98, 98.5))  # stop after the signal bar closed
        tr = R.build_trades([one_signal(0)], bars, [], "all_taker", 3600000)
        self.assertEqual(tr[0]["exit_reason"], "stop")


TF5 = 5 * MIN  # HTF bar = 5 one-minute bars in these tests


def limit_signal(setup="sr_flip"):
    # long limit at level 100, stop 99 (risk 1), target 101.5 (1.5R). Confirm bar = HTF bar 0
    # (t 0..5min, known at 5min); retest HTF bar = t 5min; limit valid through HTF bar at 10min.
    return {"side": "long", "entry_price": 100.0, "entry_t": TF5, "stop": 99.0,
            "targets": [(101.5, 1.0)],
            "meta": {"setup": setup, "placed_t": 0, "valid_until_t": 2 * TF5, "target_r": 1.5}}


def confirm_bars():
    # minutes 0-4 (the confirm bar): trades at 101, dips to 99.5 in minute 2 BEFORE the setup is known
    b = [bar(i * MIN, 101, 101.2, 100.8, 101) for i in range(5)]
    b[2] = bar(2 * MIN, 101, 101, 99.5, 100.9)
    return b


class TestLimitFill(unittest.TestCase):
    def test_first_minute_touch_then_rally_fills_at_level_not_after_close(self):
        # Retest HTF bar (min 5-9): touches 100.0 in its FIRST minute, then rallies to 102.5 and closes
        # far above. Old runner: entry booked at 100 at the END of this bar (min 9) with the rally
        # already known; the following bar then falls to 98.5 -> stop -> about -1.1R.
        # Fixed: filled at 100 in minute 5, minute 6 high 101.6 >= 101.5 -> target.
        bars = confirm_bars() + [
            bar(5 * MIN, 100.5, 100.6, 99.9, 100.4),
            bar(6 * MIN, 100.4, 101.6, 100.4, 101.5),
            bar(7 * MIN, 101.5, 102.0, 101.4, 102.0),
            bar(8 * MIN, 102.0, 102.4, 101.9, 102.3),
            bar(9 * MIN, 102.3, 102.5, 102.2, 102.5),
            bar(10 * MIN, 102.5, 102.5, 98.5, 98.6),
        ] + [bar((11 + i) * MIN, 98.6, 98.6, 98.6, 98.6) for i in range(10)]
        tr = R.build_trades([limit_signal()], bars, [], "all_taker", TF5)
        self.assertEqual(len(tr), 1)
        t = tr[0]
        self.assertEqual(t["exit_reason"], "targets")  # old runner: "stop" (entry booked after the rally)
        self.assertEqual(t["fill_t"], 5 * MIN)         # first minute of the retest bar
        self.assertAlmostEqual(t["entry_price"], 100.0, places=12)
        self.assertAlmostEqual(t["gross_r"], 1.5, places=12)
        # fees: entry 0.0005*100/1 = 0.05R, target 0.0005*101.5/1 = 0.05075R
        self.assertAlmostEqual(t["net_r"], 1.5 - 0.05 - 0.05075, places=12)
        m = R.build_trades([limit_signal()], bars, [], "maker_entry", TF5)[0]
        self.assertAlmostEqual(m["net_r"], 1.5, places=12)  # maker 0 on limit entry and target

    def test_dip_before_placement_does_not_fill(self):
        # price never returns to 100 after the setup is known (min 5 onward all >= 100.2)
        bars = confirm_bars() + [bar((5 + i) * MIN, 100.5, 100.8, 100.2, 100.5) for i in range(15)]
        st = {}
        tr = R.build_trades([limit_signal()], bars, [], "all_taker", TF5, stats=st)
        self.assertEqual(tr, [])
        self.assertEqual((st["signals"], st["filled"], st["unfilled"]), (1, 0, 1))

    def test_touch_after_validity_window_does_not_fill(self):
        # window = placement (5min) .. close of the HTF bar opened at 10min (= 15min)
        bars = confirm_bars() + [bar((5 + i) * MIN, 100.5, 100.8, 100.2, 100.5) for i in range(10)]
        bars.append(bar(15 * MIN, 100.5, 100.5, 99.9, 100.1))
        st = {}
        self.assertEqual(R.build_trades([limit_signal()], bars, [], "all_taker", TF5, stats=st), [])
        self.assertEqual(st["unfilled"], 1)

    def test_fill_bar_can_only_stop_never_target(self):
        # fill minute trades 100 .. 98.9 .. 101.6: stop (99) hit in the fill bar -> stop_first, no target
        bars = confirm_bars() + [bar(5 * MIN, 100.5, 101.6, 98.9, 101.0)] + \
            [bar((6 + i) * MIN, 101, 101, 101, 101) for i in range(5)]
        t = R.build_trades([limit_signal()], bars, [], "all_taker", TF5)[0]
        self.assertEqual(t["exit_reason"], "stop")
        self.assertAlmostEqual(t["gross_r"], -1.0, places=12)
        self.assertAlmostEqual(t["net_r"], -1.0 - 0.05 - 0.0495, places=12)

    def test_fill_bar_high_does_not_credit_target(self):
        # fill minute high 101.6 (above target) but no stop: target must wait for a LATER bar
        bars = confirm_bars() + [bar(5 * MIN, 100.5, 101.6, 99.9, 101.0),
                                 bar(6 * MIN, 101, 101, 100.9, 101),
                                 bar(7 * MIN, 101, 101.7, 100.9, 101.4)]   # one tick through (B151)
        t = R.build_trades([limit_signal()], bars, [], "all_taker", TF5)[0]
        self.assertEqual(t["exit_reason"], "targets")
        self.assertEqual(t["fill_t"], 5 * MIN)
        # exits at the later bar (min 7); gross still 1.5R at limit price 101.5
        self.assertAlmostEqual(t["gross_r"], 1.5, places=12)

    def test_gap_bar_below_level_fills_at_open(self):
        # whole minute below the level (h 99.8 < 100): fill at its open 99.8, not at 100
        bars = confirm_bars() + [bar(5 * MIN, 99.8, 99.8, 99.4, 99.6),
                                 bar(6 * MIN, 99.6, 101.7, 99.6, 101.5)]   # high one tick through the 101.5 target (B151)
        t = R.build_trades([limit_signal()], bars, [], "all_taker", TF5)[0]
        self.assertAlmostEqual(t["entry_price"], 99.8, places=12)
        # risk 0.8; gross (101.5-99.8)/0.8 = 2.125; fees 0.0005*99.8/0.8 + 0.0005*101.5/0.8
        self.assertAlmostEqual(t["gross_r"], 2.125, places=12)
        self.assertAlmostEqual(t["net_r"], 2.125 - 0.062375 - 0.0634375, places=12)

    def test_short_limit_fills_on_high(self):
        sig = {"side": "short", "entry_price": 100.0, "entry_t": TF5, "stop": 101.0,
               "targets": [(98.5, 1.0)],
               "meta": {"setup": "fib_pullback", "placed_t": 0, "valid_until_t": 2 * TF5, "target_r": 1.5}}
        bars = [bar(i * MIN, 99, 99.2, 98.8, 99) for i in range(5)]
        bars[1] = bar(MIN, 99, 100.5, 98.8, 99)  # pre-placement spike through 100: must not fill
        bars += [bar(5 * MIN, 99.5, 99.9, 99.4, 99.6), bar(6 * MIN, 99.6, 100.1, 99.5, 99.7),
                 bar(7 * MIN, 99.7, 99.7, 98.4, 98.5)]
        t = R.build_trades([sig], bars, [], "all_taker", TF5)[0]
        self.assertEqual(t["fill_t"], 6 * MIN)
        self.assertAlmostEqual(t["entry_price"], 100.0, places=12)
        self.assertAlmostEqual(t["gross_r"], 1.5, places=12)

    def test_touch_of_level_does_not_fill_trade_through_does(self):
        # B151: BACKTEST_PROTOCOL needs a trade-through by 1 tick. Low == level (touch) must NOT fill.
        base = confirm_bars()
        touch = base + [bar((5 + i) * MIN, 100.5, 100.8, 100.2, 100.5) for i in range(3)] +             [bar(8 * MIN, 100.5, 100.6, 100.0, 100.4)] +             [bar((9 + i) * MIN, 100.4, 100.6, 100.2, 100.4) for i in range(6)]
        st = {}
        self.assertEqual(R.build_trades([limit_signal()], touch, [], "all_taker", TF5, stats=st), [])
        self.assertEqual(st["unfilled"], 1)
        through = list(touch)
        through[8] = bar(8 * MIN, 100.5, 100.6, 99.9, 100.4)  # one tick through
        st = {}
        t = R.build_trades([limit_signal()], through, [], "all_taker", TF5, stats=st)
        self.assertEqual((st["filled"] + st["open_at_end"], st["unfilled"]), (1, 0))
        if t:
            self.assertEqual(t[0]["fill_t"], 8 * MIN)

    def test_target_needs_trade_through_in_build_trades(self):
        # B151: engine targets are resting limits too; a bar whose high only touches the target must not take profit
        sig = {"side": "long", "entry_price": 100.0, "entry_t": 0, "stop": 99.0, "targets": [(101.5, 1.0)], "meta": {}}
        mk = lambda hi: [bar(i * MIN, 100, 100.2, 99.8, 100) for i in range(3)] + [bar(3 * MIN, 100, hi, 99.8, 100)] +             [bar((4 + i) * MIN, 100, 100.2, 99.8, 100) for i in range(3)]
        touch = R.build_trades([sig], mk(101.5), [], "all_taker", MIN, max_bars=4)
        through = R.build_trades([sig], mk(101.6), [], "all_taker", MIN, max_bars=4)
        self.assertGreater(through[0]["gross_r"], 1.4)   # target taken: +1.5 R
        self.assertLess(touch[0]["gross_r"], 1.0)        # touch only: left open, closed at the timeout

    def test_report_prints_open_at_end(self):
        bars = confirm_bars() + [bar((5 + i) * MIN, 100.5, 100.8, 100.2, 100.5) for i in range(15)]
        res = R.run_setup("stub", bars, bars, [], TF5, setup_fn=lambda b: [limit_signal()])
        for v in res["variants"].values():
            self.assertIn("n_open_at_end", v)
        meta = {"tf": "5m", "n_bars": len(bars), "n_is_bars": 1, "n_oos_bars": 1, "n_funding": 0}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.md"
            R.write_markdown([res], meta, p)
            self.assertIn("open at end", p.read_text(encoding="utf-8"))

    def test_run_setup_reports_unfilled(self):
        bars = confirm_bars() + [bar((5 + i) * MIN, 100.5, 100.8, 100.2, 100.5) for i in range(15)]
        res = R.run_setup("stub", bars, bars, [], TF5, setup_fn=lambda b: [limit_signal()])
        for v in res["variants"].values():
            self.assertEqual((v["n_trades"], v["n_unfilled"]), (0, 1))


class TestSetup3EntryAtClose(unittest.TestCase):
    def sig(self, entry_price):
        # short, stop 101, target_r 2; signal bar = HTF bar at t=0 (minutes 0-4)
        return {"side": "short", "entry_price": entry_price, "entry_t": 0, "stop": 101.0,
                "targets": [(entry_price - 2 * (101.0 - entry_price), 1.0)],
                "meta": {"setup": "failed_msb_reversal", "target_r": 2.0}}

    def bars(self):
        b = [bar(i * MIN, 100.4, 100.6, 100.0, 100.4) for i in range(5)]
        b[4] = bar(4 * MIN, 100.4, 100.5, 100.1, 100.2)  # last 1m close = HTF close 100.2
        return b + [bar(5 * MIN, 100.2, 100.2, 98.5, 98.6)]

    def test_entry_equals_last_1m_close(self):
        # risk 0.8, target 100.2 - 1.6 = 98.6 hit in minute 5 (low 98.5). fees 0.0005*100.2/0.8, 0.0005*98.6/0.8
        t = R.build_trades([self.sig(100.2)], self.bars(), [], "all_taker", TF5)[0]
        self.assertAlmostEqual(t["entry_price"], 100.2, places=12)
        self.assertAlmostEqual(t["gross_r"], 2.0, places=12)
        self.assertAlmostEqual(t["net_r"], 2.0 - 0.062625 - 0.061625, places=12)

    def test_stale_entry_price_is_snapped_to_close_and_target_recomputed(self):
        t = R.build_trades([self.sig(100.0)], self.bars(), [], "all_taker", TF5)[0]
        self.assertAlmostEqual(t["entry_price"], 100.2, places=12)
        self.assertAlmostEqual(t["gross_r"], 2.0, places=12)  # target moved to 98.6 (2R from 100.2)


class TestVerdict(unittest.TestCase):
    def split_eval(self, is_list, oos_list):
        return R.evaluate(is_list + oos_list, 1000, "net")

    def good(self):
        is_l = [mk(i, 0.01) for i in range(5)]
        oos = [mk(ms(2024) + i, 0.02 if i % 2 else 0.005) for i in range(15)]
        oos += [mk(ms(2025) + i, 0.02 if i % 2 else 0.005) for i in range(15)]
        return is_l, oos

    def test_pass(self):
        e = self.split_eval(*self.good())
        self.assertEqual(e["verdict"], "PASS", e["criteria"])
        self.assertEqual(e["oos"]["n"], 30)

    def test_fail_n_below_30(self):
        is_l, oos = self.good()
        e = self.split_eval(is_l, oos[:-1])
        self.assertEqual(e["verdict"], "FAIL")
        self.assertFalse(e["criteria"]["oos_n>=30"])

    def test_fail_negative_oos_mean(self):
        is_l, oos = self.good()
        e = self.split_eval(is_l, [mk(t["t"], -t["net_pct"]) for t in oos])
        self.assertFalse(e["criteria"]["oos_mean_net>0"])
        self.assertFalse(e["criteria"]["same_sign_is_oos"])
        self.assertEqual(e["verdict"], "FAIL")

    def test_fail_low_sharpe(self):
        is_l, _ = self.good()
        # mean 0.001, sd ~0.0345 -> sharpe ~0.03 < 0.3
        oos = [mk(ms(2024 if i < 15 else 2025) + i, 0.035 if i % 2 else -0.033) for i in range(30)]
        e = self.split_eval(is_l, oos)
        self.assertGreater(e["oos"]["mean_pct"], 0)
        self.assertFalse(e["criteria"]["oos_net_sharpe>=0.3"])
        self.assertEqual(e["verdict"], "FAIL")

    def test_fail_is_oos_sign_differs(self):
        _, oos = self.good()
        e = self.split_eval([mk(i, -0.01) for i in range(5)], oos)
        self.assertFalse(e["criteria"]["same_sign_is_oos"])
        self.assertEqual(e["verdict"], "FAIL")

    def test_fail_only_one_positive_year(self):
        is_l, oos = self.good()
        oos = [t if t["t"] < ms(2025) else mk(t["t"], -0.0001) for t in oos]  # 2025 year negative
        # keep overall mean>0 and sharpe fine: 2024 mean strongly positive
        oos = [mk(t["t"], 0.2 if (t["t"] < ms(2025) and t["t"] % 2) else t["net_pct"]) for t in oos]
        e = self.split_eval(is_l, oos)
        self.assertFalse(e["criteria"][">=2_positive_oos_years"])
        self.assertEqual(e["verdict"], "FAIL")

    def test_per_year_sign_reported(self):
        _, oos = self.good()
        y = R.yearly(oos)
        self.assertEqual({k: v["sign"] for k, v in y.items()}, {2024: "+", 2025: "+"})
        self.assertEqual(y[2024]["n"], 15)

    def test_summary_numbers(self):
        s = R.summarize([mk(0, 0.01), mk(1, -0.01), mk(2, 0.03)])
        self.assertEqual(s["n"], 3)
        self.assertAlmostEqual(s["mean_pct"], 100 * 0.03 / 3, places=12)
        self.assertAlmostEqual(s["hit"], 2 / 3, places=12)


class TestEndToEndStub(unittest.TestCase):
    def test_nofund_label_when_no_funding(self):
        bars = target_bars(0) + [bar(i * MIN, 102, 102, 102, 102) for i in range(3, 20)]
        res = R.run_setup("stub", bars, bars, [], MIN, setup_fn=lambda b: [one_signal(0)])
        v = res["variants"]["all_taker"]
        self.assertIn("NO funding", v["headline_basis"])
        self.assertFalse(res["funding_included"])
        self.assertEqual(v["n_trades"], 1)
        self.assertAlmostEqual(v["is"]["mean_r"], 1.899, places=9)

    def test_markdown_and_json_written_outside_repo(self):
        bars = target_bars(0) + [bar(i * MIN, 102, 102, 102, 102) for i in range(3, 20)]
        res = R.run_setup("stub", bars, bars, [], MIN, setup_fn=lambda b: [one_signal(0)])
        meta = {"tf": "1m", "n_bars": 20, "n_is_bars": 14, "n_oos_bars": 6, "n_funding": 0}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.md"
            R.write_markdown([res], meta, p)
            txt = p.read_text(encoding="utf-8")
            self.assertIn("NOT AVAILABLE", txt)
            self.assertIn("all_taker", txt)
            self.assertNotIn("\r", txt)


class TestRefusals(unittest.TestCase):
    def run_main(self, argv):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as cm:
            R.main(argv)
        return cm.exception.code, err.getvalue()

    def test_missing_data_path_exits_nonzero_with_message(self):
        with tempfile.TemporaryDirectory() as d:
            code, msg = self.run_main(["--data-root", str(Path(d) / "nope"), "--out", str(Path(d) / "out")])
        self.assertNotEqual(code, 0)
        self.assertIn("data path missing", msg)
        self.assertIn("nope", msg)

    def test_out_inside_repo_refused(self):
        code, msg = self.run_main(["--out", str(R.REPO / "MyTradingSys" / "x_out")])
        self.assertNotEqual(code, 0)
        self.assertIn("inside the repo", msg)

    def test_unknown_setup_refused(self):
        with tempfile.TemporaryDirectory() as d:
            code, msg = self.run_main(["--setups", "bogus", "--out", d])
        self.assertNotEqual(code, 0)
        self.assertIn("unknown setup", msg)


if __name__ == "__main__":
    unittest.main()
