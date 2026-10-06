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
        # long pays positive funding: rate 0.001 at t=MIN, close of that bar 102 -> 0.001*102/100 of notional
        # = 0.00102 of entry = 0.102R at risk 1% -> net_r drops by 0.102, nofund unchanged
        tr = R.build_trades([one_signal(0)], self.bars, [(MIN, 0.001)], "all_taker", MIN)[0]
        self.assertAlmostEqual(tr["net_nofund_r"], 1.899, places=9)
        self.assertAlmostEqual(tr["net_r"], 1.899 - 0.102, places=9)

    def test_signal_entry_is_moved_to_end_of_signal_bar(self):
        # 1h signal bar at t=0; a 1m bar inside that hour must not be used for stop/target
        bars = [bar(i * MIN, 100, 100, 100, 100) for i in range(60)]
        bars[10] = bar(10 * MIN, 100, 103, 100, 103)  # would hit target inside the signal bar
        bars.append(bar(60 * MIN, 100, 100, 98, 98.5))  # stop after the signal bar closed
        tr = R.build_trades([one_signal(0)], bars, [], "all_taker", 3600000)
        self.assertEqual(tr[0]["exit_reason"], "stop")


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
