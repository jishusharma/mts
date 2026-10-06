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


if __name__ == "__main__":
    unittest.main()
