"""Tests for the Qriptal scorer (card qriptal-score-binance). Expected numbers are worked by hand from RULES.md and
FORMULAS.md section 17 (fee 0.05% per side), never taken from score_calls.py's own output:
  net per unit = side * (exit - entry) - 0.0005 * (entry + exit);  R = net / |entry - stop|;  pct = net / entry.
Run: python MyTradingSys/research/qriptal_2026-10-10/test_score_calls.py
"""
import sys
sys.dont_write_bytecode = True
import contextlib
import io
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score_calls as S  # noqa: E402

MIN = 60_000
T0 = datetime(2026, 5, 5, 11, 19, 12, tzinfo=timezone.utc)   # call time inside a minute
T0_MS = int(T0.timestamp() * 1000)
FIRST = (T0_MS // MIN + 1) * MIN                              # first candle that opens after the call: 11:20:00


def c(i, o, h, l, cl):
    """candle number i after the call: (open_time_ms, open, high, low, close)"""
    return (FIRST + i * MIN, o, h, l, cl)


def flat(i0, i1, price):
    return [c(i, price, price, price, price) for i in range(i0, i1)]


class TestWin(unittest.TestCase):
    # long, entry 100, stop 95, T1 110, last 120. Candle 0 does not reach 100, candle 1 touches it (fill),
    # candle 2 reaches T1, candle 3 reaches the last target.
    def setUp(self):
        self.candles = [c(0, 102, 103, 101, 102), c(1, 101, 101, 99.5, 100), c(2, 100, 111, 100, 110),
                        c(3, 110, 121, 109, 120)] + flat(4, 60, 120)
        self.res = S.score_call("long", 100.0, 95.0, [110.0, 120.0], T0, self.candles)

    def test_filled_at_the_posted_entry_in_the_touch_candle(self):
        self.assertEqual(self.res["status"], "SCORED")
        self.assertEqual(self.res["fill_time_ms"], FIRST + 1 * MIN)

    def test_primary_column_exits_all_at_t1(self):
        r = self.res["t1"]
        self.assertEqual((r["exit"], r["exit_price"]), ("TARGET", 110.0))
        # gross 10, fees 0.0005 * (100 + 110) = 0.105, net 9.895, R = 9.895 / 5
        self.assertAlmostEqual(r["net_pct"], 9.895 / 100.0, places=9)
        self.assertAlmostEqual(r["r_net"], 9.895 / 5.0, places=9)

    def test_second_column_exits_all_at_the_last_target(self):
        r = self.res["last"]
        self.assertEqual((r["exit"], r["exit_price"]), ("TARGET", 120.0))
        # gross 20, fees 0.0005 * 220 = 0.11, net 19.89, R = 19.89 / 5
        self.assertAlmostEqual(r["r_net"], 19.89 / 5.0, places=9)


class TestStop(unittest.TestCase):
    def test_short_stopped_out(self):
        # short entry 200, stop 210, target 180. Candle 0 touches 200 (fill), candle 1 reaches 210.
        candles = [c(0, 199, 200.5, 198, 199), c(1, 200, 211, 199, 205)] + flat(2, 30, 205)
        res = S.score_call("short", 200.0, 210.0, [180.0], T0, candles)
        for col in ("t1", "last"):
            r = res[col]
            self.assertEqual((r["exit"], r["exit_price"]), ("STOP", 210.0))
            # net = -(210 - 200) - 0.0005 * (200 + 210) = -10.205; R = -10.205 / 10
            self.assertAlmostEqual(r["r_net"], -1.0205, places=9)
            self.assertAlmostEqual(r["net_pct"], -10.205 / 200.0, places=9)

    def test_stop_and_target_in_one_candle_counts_as_stop(self):
        candles = [c(0, 199, 200.5, 198, 199), c(1, 200, 211, 179, 190)] + flat(2, 30, 190)
        res = S.score_call("short", 200.0, 210.0, [180.0], T0, candles)
        self.assertEqual(res["t1"]["exit"], "STOP")

    def test_stop_in_the_fill_candle_counts(self):
        # long entry 100 stop 95: one candle spans 100 and 94 -> filled then stopped
        candles = [c(0, 101, 101, 94, 96)] + flat(1, 30, 96)
        res = S.score_call("long", 100.0, 95.0, [110.0], T0, candles)
        self.assertEqual(res["t1"]["exit"], "STOP")

    def test_target_in_the_fill_candle_is_not_credited(self):
        # the order of entry and target inside one candle is unknown; only the stop is checked there
        candles = [c(0, 99, 112, 99, 111)] + flat(1, 7 * 24 * 60, 105)
        res = S.score_call("long", 100.0, 95.0, [110.0], T0, candles)
        self.assertEqual(res["status"], "SCORED")
        self.assertEqual((res["t1"]["exit"], res["t1"]["exit_price"]), ("TIMEOUT", 105.0))


class TestNeverFilled(unittest.TestCase):
    def test_limit_not_touched_within_24h(self):
        # price sits at 105 for 24 h + 10 min; a candle that would touch 100 comes only after the 24 h window
        candles = flat(0, 24 * 60, 105) + flat(24 * 60, 24 * 60 + 5, 105) + [c(24 * 60 + 5, 105, 105, 99, 100)]
        res = S.score_call("long", 100.0, 95.0, [110.0], T0, candles)
        self.assertEqual(res["status"], "NOT_FILLED")
        self.assertNotIn("t1", res)

    def test_candle_series_that_ends_early_is_no_data_not_not_filled(self):
        res = S.score_call("long", 100.0, 95.0, [110.0], T0, flat(0, 30, 105))
        self.assertEqual(res["status"], "NO_DATA")


class TestSevenDayClose(unittest.TestCase):
    def test_open_after_7_days_closes_at_market_and_later_candles_are_ignored(self):
        fill = [c(0, 101, 101, 100, 100)]                    # touches 100 -> filled in candle 0
        body = flat(1, 7 * 24 * 60, 101)                      # candles 1 .. 10079 (last opens 7 d minus 1 min after fill)
        late = [c(7 * 24 * 60, 101, 150, 101, 150)]           # opens exactly 7 d after the fill: must be ignored
        res = S.score_call("long", 100.0, 95.0, [110.0], T0, fill + body + late)
        r = res["t1"]
        self.assertEqual((r["exit"], r["exit_price"]), ("TIMEOUT", 101.0))
        # gross 1, fees 0.0005 * (100 + 101) = 0.1005, net 0.8995, R = 0.8995 / 5
        self.assertAlmostEqual(r["r_net"], 0.8995 / 5.0, places=9)


class TestInputChecks(unittest.TestCase):
    def test_stop_on_the_wrong_side_is_rejected(self):
        with self.assertRaises(ValueError):
            S.score_call("long", 100.0, 105.0, [110.0], T0, flat(0, 5, 100))

    def test_target_on_the_wrong_side_is_rejected(self):
        with self.assertRaises(ValueError):
            S.score_call("short", 100.0, 105.0, [110.0], T0, flat(0, 5, 100))


class TestParse(unittest.TestCase):
    def test_price_with_thousands_separator_and_trailing_words(self):
        self.assertEqual(S.parse_price("82,200 (sweep of 82.2, not of 82.8)"), 82200.0)
        self.assertEqual(S.parse_price("79,500 (loss of the level)"), 79500.0)
        self.assertEqual(S.parse_price("0.5"), 0.5)

    def test_targets_are_split_on_semicolons(self):
        self.assertEqual(S.parse_targets("73,000; 72,000"), [73000.0, 72000.0])

    def test_unparseable_price_raises(self):
        with self.assertRaises(ValueError):
            S.parse_price("NOT STATED")


class TestDataRule(unittest.TestCase):
    """Card: dev data only, no holdout reads (BACKTEST_PROTOCOL s2: holdout starts 2026-06-26)."""

    def test_call_whose_window_reaches_the_holdout_is_refused(self):
        S.guard_call_window(datetime(2026, 6, 18, 0, 0, 0, tzinfo=timezone.utc))            # 8 d later = 06-26 00:00: ok
        with self.assertRaises(S.HoldoutRefused):
            S.guard_call_window(datetime(2026, 6, 18, 0, 0, 1, tzinfo=timezone.utc))
        with self.assertRaises(S.HoldoutRefused):
            S.guard_call_window(datetime(2026, 9, 21, 7, 11, 25, tzinfo=timezone.utc))
        S.guard_call_window(datetime(2026, 9, 21, 7, 11, 25, tzinfo=timezone.utc), allow_holdout=True)

    def test_loader_never_returns_a_holdout_candle_by_default(self):
        holdout_ms = int(datetime(2026, 6, 26, tzinfo=timezone.utc).timestamp() * 1000)
        with tempfile.TemporaryDirectory() as d:
            lines = ["open_time,open,high,low,close,volume,close_time"]
            for k in range(-3, 3):
                t = holdout_ms + k * MIN
                lines.append(f"{t},1,2,0.5,1.5,10,{t + MIN - 1}")
            Path(d, "BTCUSDT-1m-2026-06.csv").write_bytes(("\n".join(lines) + "\n").encode())
            got = S.load_candles(holdout_ms - 10 * MIN, holdout_ms + 10 * MIN, Path(d))
            self.assertEqual([x[0] for x in got], [holdout_ms - 3 * MIN, holdout_ms - 2 * MIN, holdout_ms - MIN])
            both = S.load_candles(holdout_ms - 10 * MIN, holdout_ms + 10 * MIN, Path(d), allow_holdout=True)
            self.assertEqual(len(both), 6)

    def test_loader_reads_daily_files_and_dedupes_against_monthly(self):
        t = int(datetime(2026, 9, 1, tzinfo=timezone.utc).timestamp() * 1000)
        with tempfile.TemporaryDirectory() as d:
            row = lambda x: f"{x},1,2,0.5,1.5,10,{x + MIN - 1}"
            Path(d, "BTCUSDT-1m-2026-09-01.csv").write_bytes(
                ("open_time,open,high,low,close,volume,close_time\n" + row(t) + "\n" + row(t + MIN) + "\n").encode())
            got = S.load_candles(t, t + 5 * MIN, Path(d), allow_holdout=True)
            self.assertEqual([x[0] for x in got], [t, t + MIN])


class TestRunSplitsAndNeverReadsHoldout(unittest.TestCase):
    ledger = (
        "call_id,video_id,published_utc,direction,entry,stop,targets,eligible,window_split,reason\n"
        "A-1,vid,2026-05-05T11:19:12Z,long,\"100 (x)\",95,\"110; 120\",Y,DEV,ok\n"
        "A-2,vid,2026-09-21T07:11:25Z,short,\"82,200\",\"82,800\",\"73,000; 72,000\",Y,HOLDOUT,ok\n"
        "A-3,vid,2026-05-05T11:19:12Z,long,NOT STATED,NOT STATED,NOT STATED,N,DEV,no entry\n")

    def run_it(self, allow=False):
        asked = []

        def loader(start_ms, end_ms, kdir, allow_holdout=False):
            asked.append((start_ms, end_ms, allow_holdout))
            return [c(0, 101, 101, 99.5, 100), c(1, 100, 111, 100, 110)] + flat(2, 24 * 60 * 9, 110)

        with tempfile.TemporaryDirectory() as d:
            p = Path(d, "ledger.csv")
            p.write_bytes(self.ledger.encode())
            out = S.run(p, Path(d), allow_holdout=allow, loader=loader)
        return out, asked

    def test_only_dev_rows_are_scored_and_holdout_is_not_loaded(self):
        out, asked = self.run_it()
        self.assertEqual(out["counts"]["ledger_rows"], 3)
        self.assertEqual(out["counts"]["eligible"], {"DEV": 1, "HOLDOUT": 1})
        self.assertEqual(out["counts"]["scored"], 1)
        self.assertEqual([r["call_id"] for r in out["results"] if r["status"] == "SCORED"], ["A-1"])
        self.assertEqual([r["call_id"] for r in out["unscored_holdout"]], ["A-2"])
        self.assertEqual(len(asked), 1)           # the holdout row never reached the loader

    def test_win_rate_and_net_r_are_averages_over_scored_rows(self):
        out, _ = self.run_it()
        s = out["summary"]["t1"]
        self.assertEqual((s["n"], s["wins"], s["losses"]), (1, 1, 0))
        self.assertAlmostEqual(s["net_r_mean"], (10 - 0.0005 * 210) / 5.0, places=9)   # 1.979


class TestPower(unittest.TestCase):
    """Exact binomial, H0 p = 0.671 (his claim, wins / (wins + losses)), one-sided alpha 0.05, H1 p = 0.5.
    Hand values: n = 3: P(0 wins | p0) = 0.329^3 = 0.0356 <= 0.05 so reject at 0 wins, power = 0.5^3 = 0.125.
    n = 2: P(0 wins | p0) = 0.108 > 0.05, never rejects, power 0. Table from an independent math.comb sum."""

    def test_small_n(self):
        self.assertEqual(S.power(0), 0.0)
        self.assertEqual(S.power(2), 0.0)
        self.assertAlmostEqual(S.power(3), 0.125, places=9)

    def test_known_values(self):
        self.assertAlmostEqual(S.power(49), 0.7159, places=4)
        self.assertAlmostEqual(S.power(86), 0.9197, places=4)

    def test_first_n_with_80_percent_power(self):
        self.assertEqual(S.min_n_for_power(0.8), 56)


class TestCommittedLedger(unittest.TestCase):
    """The committed CALL_LEDGER.csv: 2 ELIGIBLE rows, both holdout, so the DEV score is n = 0 and no kline is read."""

    def test_dev_scored_n_is_zero_and_holdout_rows_are_listed_not_scored(self):
        def no_reads(*a, **k):
            raise AssertionError("the loader must not be called when no ELIGIBLE row is DEV")
        out = S.run(S.LEDGER, S.KLINE_DIR, loader=no_reads)
        self.assertEqual(out["counts"]["scored"], 0)
        self.assertEqual(out["counts"]["eligible"], {"DEV": 0, "HOLDOUT": 2})
        self.assertEqual(out["counts"]["rows_by_split"], {"DEV": 11, "HOLDOUT": 67, "NO_TIME": 3})
        self.assertEqual([x["call_id"] for x in out["unscored_holdout"]], ["QRP-ZPFK3ZsLwoo-05", "QRP-ZPFK3ZsLwoo-06"])

    def test_scorecard_matches_a_rerun(self):
        out = S.run(S.LEDGER, S.KLINE_DIR)
        self.assertEqual(S.read_committed_text(S.SCORECARD), S.render_scorecard(out))

    def test_crlf_checkout_of_the_scorecard_matches_but_a_content_change_does_not(self):
        # windows-latest checks the file out with core.autocrlf=true: same content, CRLF line ends
        want = S.render_scorecard(S.run(S.LEDGER, S.KLINE_DIR))
        tampered = want.replace("scored n = 0", "scored n = 1", 1)
        self.assertNotEqual(tampered, want)

        def check(content):
            """-> exit code of `score_calls.py check` against a SCORECARD.md holding `content`"""
            real = S.SCORECARD
            try:
                with tempfile.TemporaryDirectory() as d:
                    S.SCORECARD = Path(d, "SCORECARD.md")
                    S.SCORECARD.write_bytes(content.encode("utf-8"))
                    with contextlib.redirect_stdout(io.StringIO()):
                        return S.main(["score_calls.py", "check"])
            finally:
                S.SCORECARD = real

        self.assertEqual(check(want), 0)
        self.assertEqual(check(want.replace("\n", "\r\n")), 0)
        self.assertEqual(check(tampered.replace("\n", "\r\n")), 1)

    def test_claim_arithmetic(self):
        c = S.claimed()
        self.assertAlmostEqual(c["win_rate_excl_be"], 49 / 73, places=9)          # 0.6712 -> his 67.1%
        self.assertAlmostEqual(c["win_rate_incl_be"], 49 / 86, places=9)          # 0.5698
        self.assertAlmostEqual(c["expect_pct"], (49 * 3.99 - 24 * 0.63) / 86, places=9)   # 2.098% per setup
        self.assertAlmostEqual(c["fee_r"], 0.10 / 0.63, places=9)


if __name__ == "__main__":
    unittest.main(verbosity=2)
