"""Tests: chain snapshot (ticker-subset selection, record shape, fail-closed, gz append, loop). Offline, fake HTTP."""
import calendar
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import opt_testutil as T  # noqa: E402
from opt_testutil import C  # noqa: E402
import deribit_opt_snapshot as S  # noqa: E402


def fake_with_chain(**kw):
    f = T.FakeDeribit(**kw)
    f.summary = T.make_chain()
    f.dvol["60"] = [[T.NOW - 120000, 40.0, 40.1, 39.9, 40.05], [T.NOW - 60000, 40.05, 40.2, 40.0, 40.15]]
    return f


class ParseAndSelect(unittest.TestCase):
    def test_parse_instrument_expiry_is_0800_utc(self):
        exp, strike, cp = S.parse_instrument("BTC-27NOV26-88000-C")
        self.assertEqual(exp, calendar.timegm((2026, 11, 27, 8, 0, 0)) * 1000)
        self.assertEqual((strike, cp), (88000, "C"))
        self.assertEqual(S.parse_instrument("BTC-9OCT26-65000-P")[0], calendar.timegm((2026, 10, 9, 8, 0, 0)) * 1000)

    def test_parse_rejects_non_btc_and_garbage(self):
        for bad in ("ETH-27NOV26-3000-C", "BTC-PERPETUAL", "BTC-27XXX26-88000-C", "BTC-27NOV26-88000-X", ""):
            self.assertIsNone(S.parse_instrument(bad), bad)

    def test_parse_matches_every_recorded_instrument(self):
        for r in T.fixture("book_summary.json"):
            self.assertIsNotNone(S.parse_instrument(r["instrument_name"]), r["instrument_name"])

    def test_subset_is_atm_pm_n_strikes_within_dte_and_excludes_expired(self):
        names = S.select_ticker_subset(T.make_chain(), T.NOW, atm_n=8, max_dte=90)
        by_exp = {}
        for n in names:
            exp, k, cp = S.parse_instrument(n)
            by_exp.setdefault(n.split("-")[1], set()).add((k, cp))
        # 9OCT26, 30OCT26, 25DEC26 qualify; 8OCT26 expired at 08:00 today; 26MAR27 is 169 d out
        self.assertEqual(sorted(by_exp), ["25DEC26", "30OCT26", "9OCT26"])
        for exp, items in by_exp.items():
            strikes = sorted({k for k, _ in items})
            self.assertEqual(strikes, list(range(74000, 90001, 1000)), exp)  # 82000 +- 8 strikes of 1000
            self.assertEqual(len(items), 34, exp)  # 17 strikes x call+put
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(names, sorted(names))

    def test_subset_atm_follows_each_expirys_forward_price(self):
        rows = T.make_chain()
        for r in rows:
            if "30OCT26" in r["instrument_name"]:
                r["underlying_price"] = 90000.0  # a far expiry with a much higher forward
        names = S.select_ticker_subset(rows, T.NOW, atm_n=2, max_dte=90)
        k30 = sorted({S.parse_instrument(n)[1] for n in names if "30OCT26" in n})
        k9 = sorted({S.parse_instrument(n)[1] for n in names if "-9OCT26-" in n})
        self.assertEqual(k30, [88000, 89000, 90000, 91000, 92000])
        self.assertEqual(k9, [80000, 81000, 82000, 83000, 84000])

    def test_subset_handles_atm_at_the_edge_of_the_strike_grid(self):
        rows = T.make_chain(underlying=60500.0)
        names = S.select_ticker_subset(rows, T.NOW, atm_n=8, max_dte=90)
        ks = sorted({S.parse_instrument(n)[1] for n in names if "-9OCT26-" in n})
        # 60500 is equidistant from 60000 and 61000 (first wins); the window is clipped at the bottom of the grid
        self.assertEqual(ks, list(range(60000, 69000, 1000)))


class Snapshot(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_snapshot_record_shape_and_ticker_merge(self):
        fake = fake_with_chain()
        snap = S.take_snapshot(fake.client(), atm_n=8, max_dte=90, workers=1, clock_ms=lambda: T.NOW)
        self.assertEqual(snap["ts_ms"], T.NOW)
        self.assertEqual(snap["n_rows"], len(fake.summary))
        self.assertEqual(len(snap["rows"]), len(fake.summary))
        self.assertEqual(snap["n_ticker"], 102)
        self.assertEqual(snap["n_ticker_fail"], 0)
        self.assertEqual(snap["index"], fake.index_price["index_price"])
        self.assertEqual(snap["dvol"], 40.15)
        self.assertEqual(snap["dvol_ts"], T.NOW - 60000)
        with_greeks = [r for r in snap["rows"] if r.get("delta") is not None]
        self.assertEqual(len(with_greeks), 102)
        for k in ("gamma", "vega", "theta", "rho", "bid_iv", "ask_iv", "t_ts", "t_mark_iv"):
            self.assertIn(k, with_greeks[0])
        outside = [r for r in snap["rows"] if "delta" not in r]
        self.assertEqual(len(outside), len(fake.summary) - 102)
        self.assertTrue(all("mark_iv" in r and "instrument_name" in r for r in outside))
        self.assertNotIn("creation_timestamp", snap["rows"][0])
        self.assertEqual(fake.n_calls("public/ticker"), 102)
        self.assertEqual(fake.n_calls("public/get_book_summary_by_currency"), 1)

    def test_only_public_methods_are_called(self):
        fake = fake_with_chain()
        S.take_snapshot(fake.client(), workers=1, clock_ms=lambda: T.NOW)
        self.assertTrue(all(m.startswith("public/") for m, _ in fake.calls))
        self.assertEqual({m for m, _ in fake.calls}, {"public/get_index_price", "public/get_book_summary_by_currency",
                                                      "public/get_volatility_index_data", "public/ticker"})

    def test_threaded_fetch_gives_same_rows_as_serial(self):
        a = S.take_snapshot(fake_with_chain().client(), workers=1, clock_ms=lambda: T.NOW)
        b = S.take_snapshot(fake_with_chain().client(), workers=4, clock_ms=lambda: T.NOW)
        self.assertEqual(a["rows"], b["rows"])

    def test_one_failed_ticker_is_recorded_not_fatal(self):
        fake = fake_with_chain()
        victim = "BTC-9OCT26-82000-C"
        fake.ticker_fail.add(victim)
        snap = S.take_snapshot(fake.client(), workers=1, clock_ms=lambda: T.NOW)
        self.assertEqual(snap["n_ticker_fail"], 1)
        self.assertEqual(snap["n_ticker"], 101)
        row = next(r for r in snap["rows"] if r["instrument_name"] == victim)
        self.assertNotIn("delta", row)
        self.assertEqual(len(snap["rows"]), len(fake.summary))

    def test_dvol_failure_is_recorded_not_fatal(self):
        fake = fake_with_chain()
        fake.dvol.clear()
        snap = S.take_snapshot(fake.client(), workers=1, clock_ms=lambda: T.NOW)
        self.assertIsNone(snap["dvol"])

    def test_fail_closed_when_book_summary_is_empty_nothing_written(self):
        fake = fake_with_chain()
        fake.summary = []
        with self.assertRaises(C.DeribitError):
            S.take_snapshot(fake.client(), workers=1, clock_ms=lambda: T.NOW)
        rc = S.main(["--data-dir", str(self.data), "--workers", "1"], client=fake.client())
        self.assertEqual(rc, 1)
        self.assertFalse((self.data / "chain").exists())

    def test_write_appends_one_line_per_snapshot_to_the_utc_day_file(self):
        fake = fake_with_chain()
        s1 = S.take_snapshot(fake.client(), workers=2, clock_ms=lambda: T.NOW)
        s2 = S.take_snapshot(fake.client(), workers=2, clock_ms=lambda: T.NOW + 900000)
        p1 = S.write_snapshot(self.data, s1)
        p2 = S.write_snapshot(self.data, s2)
        self.assertEqual(p1, p2)
        self.assertEqual(p1.name, "2026-10-08.jsonl.gz")
        with gzip.open(p1, "rt", encoding="utf-8") as f:
            recs = [json.loads(x) for x in f]
        self.assertEqual([r["ts_ms"] for r in recs], [T.NOW, T.NOW + 900000])
        self.assertEqual(len(recs[0]["rows"]), len(fake.summary))
        self.assertEqual(recs[0]["rows"], s1["rows"])

    def test_snapshot_after_midnight_goes_to_the_next_day_file(self):
        fake = fake_with_chain()
        late = C.date_to_ms("2026-10-09") + 1000
        snap = S.take_snapshot(fake.client(), workers=1, clock_ms=lambda: late)
        self.assertEqual(S.write_snapshot(self.data, snap).name, "2026-10-09.jsonl.gz")

    def test_main_end_to_end_writes_a_readable_file(self):
        fake = fake_with_chain()
        rc = S.main(["--data-dir", str(self.data), "--workers", "2", "--atm-strikes", "1"], client=fake.client())
        self.assertEqual(rc, 0)
        files = list((self.data / "chain").glob("*.jsonl.gz"))
        self.assertEqual(len(files), 1)
        self.assertEqual(C.gz_scan(files[0])[1:], (1, True))


class Loop(unittest.TestCase):
    def test_runs_on_a_fixed_grid_without_drift(self):
        clk = T.FakeClock(0.0)
        starts = []

        def run_once():
            starts.append(clk.t)
            clk.advance(70.0)  # each snapshot takes 70 s

        rc = S.loop(900, run_once, max_cycles=4, sleep=clk.sleep, clock=clk.clock, log=lambda m: None)
        self.assertEqual(rc, 0)
        self.assertEqual(starts, [0.0, 900.0, 1800.0, 2700.0])

    def test_overrun_skips_missed_slots_instead_of_bursting(self):
        clk = T.FakeClock(0.0)
        starts = []
        durations = iter([2000.0, 10.0, 10.0])

        def run_once():
            starts.append(clk.t)
            clk.advance(next(durations))

        S.loop(900, run_once, max_cycles=3, sleep=clk.sleep, clock=clk.clock, log=lambda m: None)
        self.assertEqual(starts, [0.0, 2700.0, 3600.0])

    def test_survives_isolated_failures_and_stops_after_five_in_a_row(self):
        clk = T.FakeClock(0.0)
        n = {"i": 0}

        def flaky():
            n["i"] += 1
            if n["i"] in (1, 3):
                raise C.DeribitError("m", 1, "x")

        self.assertEqual(S.loop(10, flaky, max_cycles=5, sleep=clk.sleep, clock=clk.clock, log=lambda m: None), 0)
        self.assertEqual(n["i"], 5)

        n["i"] = 0

        def always():
            n["i"] += 1
            raise C.DeribitError("m", 1, "x")

        self.assertEqual(S.loop(10, always, max_cycles=50, sleep=clk.sleep, clock=clk.clock, log=lambda m: None), 2)
        self.assertEqual(n["i"], 5)


if __name__ == "__main__":
    unittest.main()
