"""Tests for orderflow_live.py (R3 live order-flow bar writer). Fake fetch, temp dirs, no network.
Expected numbers are hand arithmetic from the schema in orderflow_bars.py (aggressor: is_buyer_maker true = SELL,
10 USD fp bins, big = qty >= threshold) - none computed by the code under test."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from MyTradingSys.backtest.layers.fabio import orderflow_live as ol

T0 = int(datetime(2026, 10, 3, 14, 0, tzinfo=timezone.utc).timestamp() * 1000)
DAY = datetime(2026, 10, 3, tzinfo=timezone.utc).date()


def raw(a, px, q, ts, maker):
    return {"a": a, "p": str(px), "q": str(q), "f": a * 10, "l": a * 10, "T": ts, "m": maker}


class FakeExchange:
    def __init__(self, trades, fail=False):
        self.trades, self.fail, self.calls = trades, fail, 0

    def __call__(self, symbol, start_ms=None, from_id=None, limit=1000):
        self.calls += 1
        if self.fail:
            raise OSError("boom")
        if from_id is not None:
            rows = [t for t in self.trades if t["a"] >= from_id]
        else:
            rows = [t for t in self.trades if t["T"] >= start_ms]
        return rows[:limit]


def prior_hist(d, n=100):
    """One prior day whose every row is qty 0.01 (bin 100) -> thr99 = thr999 = 0.01."""
    p = Path(d) / "_qhist"
    p.mkdir(parents=True, exist_ok=True)
    (p / "2026-10-02.json").write_text(json.dumps({"100": n}))


TRADES = [raw(1, 100.0, 0.5, T0 + 1000, False),   # minute 0 buy, big
          raw(2, 100.5, 0.001, T0 + 2000, True),  # minute 0 sell, small
          raw(3, 101.0, 0.2, T0 + 61000, True),   # minute 1 sell, big
          raw(4, 102.0, 0.3, T0 + 125000, False)]  # minute 2: still open at NOW


class TestWriter(unittest.TestCase):
    NOW = T0 + 125500

    def cycle(self, d, fx, **kw):
        kw.setdefault("hist_dirs", [Path(d) / "_qhist"])
        return ol.run_cycle(d, fx, now_ms=self.NOW, since_ms=T0, **kw)

    def test_closed_minutes_only_and_values(self):
        with tempfile.TemporaryDirectory() as d:
            prior_hist(d)
            r = self.cycle(d, FakeExchange(TRADES))
            self.assertEqual((r["rows"], r["error"], r["thr_days"]), (2, None, 1))
            bars = ol.load_live_bars(d)
            self.assertEqual([b["t"] for b in bars], [T0, T0 + 60000])  # open minute 2 not written
            b0, b1 = bars
            self.assertEqual((b0["o"], b0["h"], b0["l"], b0["c"]), (100.0, 100.5, 100.0, 100.5))
            self.assertEqual((b0["buy_vol"], b0["sell_vol"], b0["n_agg"]), (0.5, 0.001, 2))
            self.assertAlmostEqual(b0["delta"], 0.499)
            self.assertEqual((b0["b99_buy_vol"], b0["b99_sell_vol"], b0["b99_buy_n"]), (0.5, 0.0, 1))
            self.assertEqual((b0["thr99"], b0["thr_days"]), (0.01, 1))
            self.assertEqual(b0["fp"], "100:0.5:0.001")
            self.assertEqual((b1["sell_vol"], b1["b99_sell_vol"], b1["fp"]), (0.2, 0.2, "100:0.0:0.2"))
            self.assertAlmostEqual(b1["cvd_day"], 0.299)  # 0.499 - 0.2

    def test_restart_does_not_duplicate_or_skip(self):
        with tempfile.TemporaryDirectory() as d:
            prior_hist(d)
            self.cycle(d, FakeExchange(TRADES))
            r = ol.run_cycle(d, FakeExchange(TRADES), now_ms=self.NOW, hist_dirs=[Path(d) / "_qhist"])
            self.assertEqual(r["rows"], 0)  # same clock: nothing new
            later = T0 + 185000  # minute 2 now closed
            r = ol.run_cycle(d, FakeExchange(TRADES), now_ms=later, hist_dirs=[Path(d) / "_qhist"])
            self.assertEqual(r["rows"], 1)
            bars = ol.load_live_bars(d)
            self.assertEqual([b["t"] for b in bars], [T0, T0 + 60000, T0 + 120000])
            self.assertAlmostEqual(bars[2]["cvd_day"], 0.599)  # cvd carried across cycles: 0.299 + 0.3

    def test_fetch_error_writes_nothing_and_does_not_advance(self):
        with tempfile.TemporaryDirectory() as d:
            prior_hist(d)
            r = self.cycle(d, FakeExchange(TRADES, fail=True))
            self.assertIn("boom", r["error"])
            self.assertEqual(ol.load_live_bars(d), [])
            self.assertNotIn("next_ms", ol.load_state(d))
            r = self.cycle(d, FakeExchange(TRADES))  # recovers, nothing lost
            self.assertEqual(r["rows"], 2)

    def test_error_mid_backfill_keeps_fetched_minutes(self):
        """2026-10-07: a 15 h backfill hit HTTP 429 part way through every cycle and, all-or-nothing, never advanced.
        Pages fetched before the error are kept (whole minutes before the last fetched one); the rest retries."""
        with tempfile.TemporaryDirectory() as d:
            prior_hist(d)
            old = ol.PAGE
            ol.PAGE = 1

            class FailFourth(FakeExchange):   # pages 1-3 = trades 1-3 (minutes 0, 0, 1), page 4 fails
                def __call__(self, *a, **k):
                    if self.calls == 3:
                        self.calls += 1
                        raise OSError("HTTP Error 429: Too Many Requests")
                    return super().__call__(*a, **k)
            try:
                r = self.cycle(d, FailFourth(TRADES))
            finally:
                ol.PAGE = old
            self.assertIn("429", r["error"])
            self.assertEqual([b["t"] for b in ol.load_live_bars(d)], [T0])   # minute 0 complete; minute 1 retried
            self.assertEqual(ol.load_state(d)["next_ms"], T0 + 60000)
            r = self.cycle(d, FakeExchange(TRADES))
            self.assertEqual([b["t"] for b in ol.load_live_bars(d)], [T0, T0 + 60000])
            self.assertAlmostEqual(ol.load_live_bars(d)[1]["cvd_day"], 0.299)

    def test_minute_larger_than_page_budget_still_advances(self):
        """2026-10-14: one minute held 39,420 trades (> 25 pages); the chunk kept only minutes before the last fetched
        one, so it was empty forever and the writer never moved. The overflow budget completes that minute."""
        n = 7
        trades = [raw(i + 1, 80000, 0.01, T0 + i, bool(i % 2)) for i in range(n)] + [raw(n + 1, 80001, 0.01, T0 + 61000, False)]
        with tempfile.TemporaryDirectory() as d:
            prior_hist(d)
            old = (ol.PAGE, ol.MAX_PAGES, ol.OVERFLOW_PAGES)
            ol.PAGE, ol.MAX_PAGES, ol.OVERFLOW_PAGES = 1, 3, 12   # minute 0 = 7 trades > 3 pages
            try:
                r = self.cycle(d, FakeExchange(trades), max_pages=3)
            finally:
                ol.PAGE, ol.MAX_PAGES, ol.OVERFLOW_PAGES = old
            self.assertGreaterEqual(r["rows"], 1)
            self.assertGreater(ol.load_state(d)["next_ms"], T0)
            self.assertEqual(ol.load_live_bars(d)[0]["t"], T0)

    def test_default_page_budget_stays_under_binance_weight_limit(self):
        # aggTrades weight 20, limit 2400/min; one cycle every 20 s -> 3 cycles/min
        self.assertLessEqual(ol.MAX_PAGES * 20 * 3, 2400)

    def test_pagination_dedup(self):
        with tempfile.TemporaryDirectory() as d:
            prior_hist(d)
            old = ol.PAGE
            ol.PAGE = 2
            try:
                fx = FakeExchange(TRADES)
                r = self.cycle(d, fx)
            finally:
                ol.PAGE = old
            self.assertEqual(r["rows"], 2)
            self.assertGreaterEqual(fx.calls, 2)
            self.assertEqual(sum(b["n_agg"] for b in ol.load_live_bars(d)), 3)

    def test_thr_days_zero_without_prior_and_positive_with(self):
        with tempfile.TemporaryDirectory() as d:
            self.cycle(d, FakeExchange(TRADES))
            self.assertEqual({b["thr_days"] for b in ol.load_live_bars(d)}, {0})
        with tempfile.TemporaryDirectory() as d:
            prior_hist(d)
            self.cycle(d, FakeExchange(TRADES))
            self.assertEqual({b["thr_days"] for b in ol.load_live_bars(d)}, {1})

    def test_prior_day_in_second_dir_counts_once(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as d2:
            prior_hist(d)
            prior_hist(d2, 7)
            t99, _, n = ol.live_thresholds(DAY, [Path(d) / "_qhist", Path(d2) / "_qhist"])
            self.assertEqual((n, t99), (1, 0.01))

    def test_day_rollover_resets_cvd_and_flushes_hist(self):
        with tempfile.TemporaryDirectory() as d:
            prior_hist(d)
            nd = int(datetime(2026, 10, 4, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
            tr = [raw(1, 100.0, 0.5, nd - 30000, False), raw(2, 100.0, 0.25, nd + 5000, False)]
            ol.run_cycle(d, FakeExchange(tr), now_ms=nd + 70000, since_ms=nd - 60000, hist_dirs=[Path(d) / "_qhist"])
            days = sorted(p.name for p in Path(d).glob("????-??-??.csv"))
            self.assertEqual(days, ["2026-10-03.csv", "2026-10-04.csv"])
            bars = ol.load_live_bars(d)
            self.assertEqual([b["cvd_day"] for b in bars], [0.5, 0.25])  # reset at 00:00Z
            self.assertTrue((Path(d) / "_qhist" / "2026-10-03.json").exists())
            # the day-4 bar's threshold uses day 3's histogram (0.5 -> bin 269 .. ) and day 2's: thr_days 2
            self.assertEqual(bars[1]["thr_days"], 2)

    def test_load_live_bars_corrupt_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "2026-10-03.csv").write_text("t,o\nnot_a_number,1\n")
            self.assertEqual(ol.load_live_bars(d), [])
            self.assertEqual(ol.load_live_bars(Path(d) / "missing"), [])

    def test_columns_match_offline_schema(self):
        with tempfile.TemporaryDirectory() as d:
            prior_hist(d)
            self.cycle(d, FakeExchange(TRADES))
            header = (Path(d) / "2026-10-03.csv").read_text().splitlines()[0].split(",")
            self.assertEqual(header, ol.ob.COLUMNS)
            self.assertEqual(len(header), 27)
            for c in ("buy_vol", "sell_vol", "b99_buy_vol", "b99_sell_vol", "thr_days", "fp"):
                self.assertIn(c, header)


class FakeClock:
    """Synthetic wall clock: sleep() advances it, so the loop runs instantly."""

    def __init__(self):
        self.t, self.sleeps = 1000.0, []

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


class StallLoopTests(unittest.TestCase):
    def loop(self, d, fetch, clock, logs, **kw):
        kw.setdefault("stall_minutes", 15)
        since = kw.pop("since", T0)
        return ol.run_loop(d, fetch, "BTCUSDT", since, 10, 20, sleep=clock.sleep, clock=clock, log=logs.append, **kw)

    def test_fetch_failure_is_logged_with_exception(self):
        with tempfile.TemporaryDirectory() as d:
            clock, logs = FakeClock(), []
            code = self.loop(d, FakeExchange(TRADES, fail=True), clock, logs, max_cycles=2)
            self.assertEqual(code, 0)
            errs = [m for m in logs if m.startswith("ERROR")]
            self.assertEqual(len(errs), 2)
            self.assertIn("boom", errs[0])

    def test_429_backs_off_and_is_bounded(self):
        with tempfile.TemporaryDirectory() as d:
            clock, logs = FakeClock(), []
            self.loop(d, FakeExchange(TRADES, fail=True), clock, logs, max_cycles=12, stall_minutes=10 ** 6)
            self.assertEqual(clock.sleeps[:3], [40, 80, 160])
            self.assertEqual(max(clock.sleeps), ol.BACKOFF_MAX_S)

    def test_backoff_resets_after_success(self):
        self.assertEqual(ol.backoff_seconds(20, 0), 20)
        self.assertEqual(ol.backoff_seconds(20, 1), 40)
        self.assertEqual(ol.backoff_seconds(20, 99), ol.BACKOFF_MAX_S)

    def test_no_progress_for_15_min_takes_exit_path(self):
        with tempfile.TemporaryDirectory() as d:
            clock, logs = FakeClock(), []
            code = self.loop(d, FakeExchange(TRADES, fail=True), clock, logs)
            self.assertEqual(code, ol.STALL_EXIT_CODE)
            self.assertNotEqual(code, 0)
            self.assertTrue(any(m.startswith("STALL") for m in logs))
            self.assertLessEqual(clock.t - 1000.0, 15 * 60 + ol.BACKOFF_MAX_S)

    def test_state_rewrite_without_progress_does_not_reset_guard(self):
        """The 2026-10-15 symptom: _state.json is rewritten every cycle with next_ms unchanged."""
        with tempfile.TemporaryDirectory() as d:
            clock, logs = FakeClock(), []

            def stuck(out, fetch_fn, symbol, since_ms=None, keep_days=10):
                ol.save_state(out, {"next_ms": T0})
                return {"rows": 0, "next_ms": T0, "thr_days": None, "error": None}

            code = self.loop(d, None, clock, logs, cycle=stuck)
            self.assertEqual(code, ol.STALL_EXIT_CODE)

    def test_progress_resets_guard(self):
        g = ol.StallGuard(0, 15)
        self.assertTrue(g.update(100, 14 * 60))
        self.assertTrue(g.update(160, 28 * 60))   # advanced: guard restarted at 28 min
        self.assertTrue(g.update(160, 42 * 60))   # 14 min since progress
        self.assertFalse(g.update(160, 44 * 60))  # 16 min since progress

    def test_restart_resumes_from_state(self):
        with tempfile.TemporaryDirectory() as d:
            prior_hist(d)
            ol.save_state(d, {"next_ms": T0})
            ex = FakeExchange(TRADES)
            clock, logs = FakeClock(), []
            self.loop(d, ex, clock, logs, max_cycles=1)
            self.assertTrue(any(m.startswith("ok") for m in logs))
            self.assertGreater(ol.load_state(d)["next_ms"], T0)
            self.assertFalse(any(m.startswith("WARN") for m in logs))

    def test_corrupt_state_behaviour_unchanged_and_warned(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "_state.json").write_text("{not json")
            self.assertEqual(ol.load_state(d), {})
            clock, logs = FakeClock(), []
            self.loop(d, FakeExchange(TRADES), clock, logs, max_cycles=1, since=None, cycle=lambda *a, **k: {
                "rows": 0, "next_ms": T0, "thr_days": None, "error": None})
            self.assertTrue(any(m.startswith("WARN") for m in logs))


if __name__ == "__main__":
    unittest.main()
