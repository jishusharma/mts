"""Tests: historical backfill (pagination, resume cursors, trade day shards, depth probe). Offline, fake HTTP."""
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import opt_testutil as T  # noqa: E402
from opt_testutil import C, HOUR, DAY, NOW  # noqa: E402
import deribit_opt_backfill as B  # noqa: E402

QUIET = dict(log=lambda m: None)
FOREVER = 1e18


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name)
        self.hist = self.data / "hist"
        self.hist.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def walk(self, name, fetch, now=NOW, deadline=FOREVER, clock=None):
        fn, cols = B.SERIES[name]
        kw = dict(QUIET)
        if clock:
            kw["clock"] = clock
        return B.walk_series(name, B.SeriesStore(self.hist / fn, cols), B.Cursors(self.hist / "_cursors.json"), fetch,
                             now, deadline, **kw)

    def stored(self, name):
        fn, cols = B.SERIES[name]
        return B.SeriesStore(self.hist / fn, cols).load()


class SeriesStoreIO(Base):
    def test_roundtrip_lf_only_sorted_and_header_checked(self):
        st = B.SeriesStore(self.hist / "x.csv", ("ts_ms", "a", "b"))
        st.add([[3, 1.5, 2], [1, 0.1, None]])
        st.save()
        raw = (self.hist / "x.csv").read_bytes()
        self.assertEqual(raw, b"ts_ms,a,b\n1,0.1,\n3,1.5,2\n")
        self.assertEqual(sorted(B.SeriesStore(self.hist / "x.csv", ("ts_ms", "a", "b")).load().rows), [1, 3])
        with self.assertRaises(ValueError):
            B.SeriesStore(self.hist / "x.csv", ("ts_ms", "other", "b")).load()

    def test_add_replaces_same_timestamp_and_counts_only_new(self):
        st = B.SeriesStore(self.hist / "x.csv", ("ts_ms", "v"))
        self.assertEqual(st.add([[1, 10], [2, 20]]), 2)
        self.assertEqual(st.add([[2, 21], [3, 30]]), 1)
        self.assertEqual(st.rows[2], ["2", "21"])


class DvolPagination(Base):
    def make(self, n=2500):
        fake = T.FakeDeribit(dvol_page=1000)
        self.first = NOW - (n - 1) * HOUR
        fake.dvol["3600"] = T.make_ohlc(self.first, n, HOUR)
        return fake

    def test_continuation_pagination_collects_every_point_once(self):
        fake = self.make()
        st = self.walk("dvol_1h", B.make_dvol_fetch(fake.client(), "3600"))
        self.assertEqual(st["pages"], 3)
        self.assertEqual(st["reason"], "exhausted")
        self.assertTrue(st["complete_back"])
        rows = self.stored("dvol_1h")
        self.assertEqual(sorted(rows.rows), [self.first + i * HOUR for i in range(2500)])
        ends = [int(p["end_timestamp"]) for _, p in fake.calls]
        self.assertEqual(ends, [NOW, self.first + 1499 * HOUR, self.first + 499 * HOUR])
        self.assertTrue(all(p["start_timestamp"] == "0" and p["resolution"] == "3600" for _, p in fake.calls))
        self.assertEqual(B.Cursors(self.hist / "_cursors.json").get("dvol_1h")["complete_back"], True)
        self.assertEqual(rows.rows[self.first][1:], [repr(40.0), repr(41.0), repr(39.0), repr(40.5)])

    def test_deadline_stops_cleanly_then_resume_continues_below_the_stored_block(self):
        fake = self.make()
        clock = lambda: 0 if fake.n_calls() < 1 else 10  # noqa: E731 - deadline passes after the first page
        st1 = self.walk("dvol_1h", B.make_dvol_fetch(fake.client(), "3600"), deadline=5, clock=clock)
        self.assertEqual((st1["pages"], st1["reason"], st1["complete_back"]), (1, "deadline", False))
        self.assertEqual(len(self.stored("dvol_1h")), 1000)
        n1 = len(fake.calls)
        st2 = self.walk("dvol_1h", B.make_dvol_fetch(fake.client(), "3600"))
        self.assertTrue(st2["complete_back"])
        self.assertEqual(len(self.stored("dvol_1h")), 2500)
        run2 = fake.calls[n1:]
        # call 1 = newer-gap check (overlaps the stored latest), call 2 resumes BELOW the stored earliest - never re-walks
        self.assertEqual(int(run2[0][1]["end_timestamp"]), NOW)
        self.assertEqual(int(run2[1][1]["end_timestamp"]), self.first + 1500 * HOUR - 1)
        self.assertEqual(len(run2), 3)

    def test_complete_series_needs_one_call_and_picks_up_new_points(self):
        fake = self.make()
        self.walk("dvol_1h", B.make_dvol_fetch(fake.client(), "3600"))
        n1 = len(fake.calls)
        fake.dvol["3600"] += T.make_ohlc(NOW + HOUR, 7, HOUR)
        st = self.walk("dvol_1h", B.make_dvol_fetch(fake.client(), "3600"), now=NOW + 7 * HOUR)
        self.assertEqual(len(fake.calls) - n1, 1)
        self.assertEqual(st["added"], 7)
        self.assertEqual(len(self.stored("dvol_1h")), 2507)
        n2 = len(fake.calls)
        st = self.walk("dvol_1h", B.make_dvol_fetch(fake.client(), "3600"), now=NOW + 7 * HOUR)
        self.assertEqual((len(fake.calls) - n2, st["added"]), (1, 0))

    def test_partial_last_candle_is_overwritten_on_the_next_run(self):
        fake = self.make(50)
        self.walk("dvol_1h", B.make_dvol_fetch(fake.client(), "3600"))
        fake.dvol["3600"][-1] = [NOW, 1.0, 2.0, 0.5, 1.5]  # the in-progress candle closed differently
        self.walk("dvol_1h", B.make_dvol_fetch(fake.client(), "3600"))
        self.assertEqual(self.stored("dvol_1h").rows[NOW][1:], ["1.0", "2.0", "0.5", "1.5"])

    def test_error_midway_keeps_progress_and_next_run_finishes(self):
        fake = self.make()

        def boom(method, params):
            if fake.n_calls() == 2:
                raise T.ApiError(-32000, "server exploded")
        fake.on_call = boom
        with self.assertRaises(C.DeribitError):
            self.walk("dvol_1h", B.make_dvol_fetch(fake.client(), "3600"))
        self.assertEqual(len(self.stored("dvol_1h")), 1000)  # page 1 survived the crash
        fake.on_call = None
        self.walk("dvol_1h", B.make_dvol_fetch(fake.client(), "3600"))
        self.assertEqual(len(self.stored("dvol_1h")), 2500)

    def test_non_decreasing_continuation_cannot_loop_forever(self):
        pages = []

        def fetch(end):
            pages.append(end)
            return [[end - 5, 1, 1, 1, 1]], end + 100  # server keeps pointing forward
        st = self.walk("dvol_1h", fetch)
        self.assertEqual(st["reason"], "no_progress")
        self.assertEqual(len(pages), 1)


class PerpAndFunding(Base):
    def test_tradingview_windows_cover_history_and_stop_on_empty_windows(self):
        fake = T.FakeDeribit()
        first = NOW - 11999 * HOUR
        fake.perp["60"] = T.make_perp(first, 12000, HOUR)
        st = self.walk("perp_1h", B.make_perp_fetch(fake.client(), "60", HOUR))
        self.assertEqual(len(self.stored("perp_1h")), 12000)
        self.assertEqual(st["pages"], 5)  # 3 windows with data + 2 empty ones
        self.assertTrue(st["complete_back"])
        row = self.stored("perp_1h").rows[first]
        self.assertEqual(row, [str(first), repr(100.0), repr(101.0), repr(99.0), repr(100.5), repr(1000.0), repr(10.0)])
        for _, p in fake.calls:
            self.assertEqual(p["instrument_name"], "BTC-PERPETUAL")
            self.assertLessEqual(int(p["end_timestamp"]) - int(p["start_timestamp"]), 5000 * HOUR)

    def test_tradingview_stops_at_perp_launch_floor(self):
        fake = T.FakeDeribit()
        floor_day = B.TV_FLOOR_MS + 10 * DAY
        fake.perp["1D"] = T.make_perp(floor_day, 40, DAY)
        now = floor_day + 39 * DAY
        st = self.walk("perp_1d", B.make_perp_fetch(fake.client(), "1D", DAY), now=now)
        self.assertEqual(len(self.stored("perp_1d")), 40)
        self.assertTrue(st["complete_back"])
        self.assertEqual(len(fake.calls), 1)  # one 5000-day window already reaches below the floor

    def test_funding_30_day_windows(self):
        fake = T.FakeDeribit()
        first = NOW - 1999 * HOUR
        fake.funding = T.make_funding(first, 2000)
        st = self.walk("funding", B.make_funding_fetch(fake.client()))
        self.assertEqual(len(self.stored("funding")), 2000)
        self.assertEqual(st["pages"], 6)  # 721 + 720 + 559 rows, then 3 empty windows
        self.assertTrue(st["complete_back"])
        self.assertEqual(self.stored("funding").rows[first][0:2], [str(first), repr(0.0)])
        for _, p in fake.calls:
            self.assertLessEqual(int(p["end_timestamp"]) - int(p["start_timestamp"]), 30 * DAY)
        n1 = len(fake.calls)
        self.walk("funding", B.make_funding_fetch(fake.client()))
        self.assertEqual(len(fake.calls) - n1, 1)


class DeliveryAndInstruments(Base):
    def make_delivery(self, n):
        base = C.date_to_ms("2026-10-08")
        return [{"date": C.utc_date(base - i * DAY), "delivery_price": 80000.0 + i} for i in range(n)]

    def run_delivery(self, fake):
        return B.backfill_delivery(fake.client(), self.hist, B.Cursors(self.hist / "_cursors.json"), FOREVER, **QUIET)

    def test_offset_pagination_and_cheap_rerun(self):
        fake = T.FakeDeribit()
        fake.delivery = self.make_delivery(250)
        st = self.run_delivery(fake)
        self.assertEqual((st["pages"], st["rows"]), (3, 250))
        self.assertEqual([p["offset"] for _, p in fake.calls], ["0", "100", "200"])
        st = B.SeriesStore(self.hist / "delivery_prices.csv", ("ts_ms", "date", "delivery_price")).load()
        self.assertEqual(st.rows[C.date_to_ms("2026-10-08")], [str(C.date_to_ms("2026-10-08")), "2026-10-08", "80000.0"])
        n1 = len(fake.calls)
        again = self.run_delivery(fake)
        self.assertEqual((len(fake.calls) - n1, again["added"], again["reason"]), (1, 0, "overlap"))

    def test_new_day_is_added_and_history_not_refetched(self):
        fake = T.FakeDeribit()
        fake.delivery = self.make_delivery(250)
        self.run_delivery(fake)
        n1 = len(fake.calls)
        fake.delivery.insert(0, {"date": "2026-10-09", "delivery_price": 99999.0})
        st = self.run_delivery(fake)
        self.assertEqual(st["rows"], 251)
        self.assertEqual(len(fake.calls) - n1, 2)

    def test_expired_instruments_merge_is_idempotent_and_keeps_first_seen(self):
        fake = T.FakeDeribit()
        r1 = B.merge_expired_instruments(fake.client(), self.hist, 111, **QUIET)
        self.assertEqual((r1["new"], r1["rows"]), (3, 3))
        r2 = B.merge_expired_instruments(fake.client(), self.hist, 222, **QUIET)
        self.assertEqual((r2["new"], r2["rows"]), (0, 3))
        extra = dict(fake.expired[0])
        extra["instrument_name"] = "BTC-9OCT26-99000-C"
        fake.expired = fake.expired + [extra]
        r3 = B.merge_expired_instruments(fake.client(), self.hist, 333, **QUIET)
        self.assertEqual((r3["new"], r3["rows"]), (1, 4))
        recs = [json.loads(x) for x in C.read_gz_lines(self.hist / "instruments_expired.jsonl.gz")]
        seen = {r["instrument_name"]: r["_first_seen_ms"] for r in recs}
        self.assertEqual(seen["BTC-9OCT26-99000-C"], 333)
        self.assertEqual(sorted(set(v for k, v in seen.items() if k != "BTC-9OCT26-99000-C")), [111])


class TradeShards(Base):
    D0 = C.date_to_ms("2026-10-07")

    def fetch_day(self, fake, count, **kw):
        tmp = self.hist / "t.tmp"
        meta = B.fetch_day(fake.client(), self.D0, count, tmp, kw.pop("hard", FOREVER), **kw)
        with gzip.open(tmp, "rt", encoding="utf-8") as f:
            ids = [json.loads(x)["trade_id"] for x in f]
        return meta, ids

    def trades(self, spec):
        return [T.make_trade(self.D0 + off, tid) for off, tid in spec]

    def test_same_millisecond_trades_split_across_pages_are_neither_lost_nor_doubled(self):
        fake = T.FakeDeribit()
        # id 1 alone, ids 2,3,4 share one millisecond, then 5 and 6; page size 3 cuts the shared ms in half
        fake.trades = self.trades([(1000, 1), (5000, 2), (5000, 3), (5000, 4), (9000, 5), (9500, 6)])
        meta, ids = self.fetch_day(fake, 3)
        self.assertEqual(ids, ["1", "2", "3", "4", "5", "6"])
        self.assertEqual(meta["n_trades"], 6)

    def test_boundary_dedupe_when_the_shared_ms_is_at_the_page_end(self):
        fake = T.FakeDeribit()
        fake.trades = self.trades([(1000, 1), (5000, 2), (5000, 3), (5000, 4), (9000, 5), (9500, 6)])
        meta, ids = self.fetch_day(fake, 4)
        self.assertEqual(ids, ["1", "2", "3", "4", "5", "6"])
        self.assertEqual(meta["calls"], 3)

    def test_exactly_one_page_and_empty_day(self):
        fake = T.FakeDeribit()
        fake.trades = self.trades([(i * 1000, i + 1) for i in range(10)])
        meta, ids = self.fetch_day(fake, 10)
        self.assertEqual((meta["calls"], len(ids)), (1, 10))
        fake.trades = []
        meta, ids = self.fetch_day(fake, 10)
        self.assertEqual((meta["n_trades"], meta["first_ts"], ids), (0, None, []))

    def test_many_pages_exact_order_and_request_shape(self):
        fake = T.FakeDeribit()
        fake.trades = self.trades([(i * 2000, i + 1) for i in range(95)])
        meta, ids = self.fetch_day(fake, 10)
        self.assertEqual(ids, [str(i + 1) for i in range(95)])
        self.assertEqual(meta["calls"], 11)  # 10 new trades on page 1, then 9 new per page (the boundary trade repeats)
        for m, p in fake.calls:
            self.assertEqual(m, "public/get_last_trades_by_currency_and_time")
            self.assertEqual((p["currency"], p["kind"], p["sorting"], p["count"]), ("BTC", "option", "asc", "10"))
            self.assertLessEqual(int(p["end_timestamp"]), self.D0 + DAY - 1)

    def test_internal_matching_engine_fields_are_dropped_other_fields_kept(self):
        fake = T.FakeDeribit()
        fake.trades = self.trades([(1000, 1)])
        tmp = self.hist / "t.tmp"
        B.fetch_day(fake.client(), self.D0, 10, tmp, FOREVER)
        with gzip.open(tmp, "rt", encoding="utf-8") as f:
            rec = json.loads(f.readline())
        self.assertNotIn("starbase_match_id", rec)
        self.assertNotIn("starbase_timestamp", rec)
        for k in ("timestamp", "trade_id", "instrument_name", "price", "amount", "direction", "iv", "index_price", "mark_price"):
            self.assertIn(k, rec)

    def test_real_recorded_page_shape_parses(self):
        page = T.fixture("trades_page_history.json")
        fake = T.FakeDeribit()
        fake.trades = [dict(t) for t in page["trades"]]
        day = C.date_to_ms(C.utc_date(page["trades"][0]["timestamp"]))
        meta = B.fetch_day(fake.client(), day, 10000, self.hist / "r.tmp", FOREVER)
        self.assertEqual(meta["n_trades"], len(page["trades"]))


class TradeBackfill(Base):
    DATES = ["2026-10-03", "2026-10-04", "2026-10-05", "2026-10-06", "2026-10-07"]
    PER_DAY = [0, 7, 25, 3, 12]

    def make_fake(self):
        fake = T.FakeDeribit()
        tid = 0
        self.expected = {}
        for d, n in zip(self.DATES, self.PER_DAY):
            base = C.date_to_ms(d)
            self.expected[d] = []
            for i in range(n):
                tid += 1
                name = "BTC-27NOV26-%d-%s" % (80000 + (i % 3) * 1000, "C" if i % 2 else "P")
                fake.trades.append(T.make_trade(base + 60000 + i * 1000, tid, name))
                self.expected[d].append(str(tid))
        return fake

    def go(self, fake, **kw):
        args = dict(date_from=self.DATES[0], date_to=self.DATES[-1], workers=3, count=10, soft_deadline=FOREVER,
                    hard_deadline=FOREVER)
        args.update(kw)
        return B.backfill_trades(fake.client(), self.hist, args.pop("date_from"), args.pop("date_to"), args.pop("workers"),
                                 args.pop("count"), args.pop("soft_deadline"), args.pop("hard_deadline"), **QUIET, **args)

    def shard_ids(self, date):
        with gzip.open(self.hist / "trades" / (date + ".jsonl.gz"), "rt", encoding="utf-8") as f:
            return [json.loads(x)["trade_id"] for x in f]

    def test_all_days_sharded_manifest_matches_files_and_empty_day_has_no_shard(self):
        fake = self.make_fake()
        tally = self.go(fake)
        self.assertEqual(tally["days_done"], 5)
        self.assertEqual(tally["trades"], sum(self.PER_DAY))
        for d, n in zip(self.DATES, self.PER_DAY):
            if n:
                self.assertEqual(self.shard_ids(d), self.expected[d], d)
            else:
                self.assertFalse((self.hist / "trades" / (d + ".jsonl.gz")).exists())
        man = B.Manifest(self.hist / "trades" / "_manifest.jsonl")
        self.assertEqual(sorted(man.done), self.DATES)
        self.assertEqual([man.done[d]["n_trades"] for d in self.DATES], self.PER_DAY)
        self.assertEqual(list((self.hist / "trades").glob("*.tmp")), [])

    def test_rerun_makes_no_requests(self):
        fake = self.make_fake()
        self.go(fake)
        n1 = len(fake.calls)
        tally = self.go(fake)
        self.assertEqual(len(fake.calls), n1)
        self.assertEqual((tally["days_done"], tally["days_already"]), (0, 5))

    def test_interrupted_day_is_refetched_alone_and_stale_tmp_removed(self):
        fake = self.make_fake()
        self.go(fake)
        mf = self.hist / "trades" / "_manifest.jsonl"
        keep = [x for x in mf.read_text(encoding="utf-8").splitlines() if "2026-10-05" not in x]
        mf.write_text("\n".join(keep) + "\n", encoding="utf-8", newline="\n")
        (self.hist / "trades" / "2026-10-05.jsonl.gz").write_bytes(b"truncated garbage")  # crashed mid-publish
        (self.hist / "trades" / "2026-10-05.jsonl.gz.tmp").write_bytes(b"half")
        n1 = len(fake.calls)
        tally = self.go(fake)
        self.assertEqual(tally["days_done"], 1)
        self.assertEqual(len(fake.calls) - n1, 3)  # 25 trades / 10 per page
        self.assertEqual(self.shard_ids("2026-10-05"), self.expected["2026-10-05"])
        self.assertEqual(list((self.hist / "trades").glob("*.tmp")), [])

    def test_soft_deadline_in_the_past_starts_nothing(self):
        fake = self.make_fake()
        tally = self.go(fake, soft_deadline=-1)
        self.assertEqual((len(fake.calls), tally["days_done"], tally["skipped_deadline"]), (0, 0, 5))

    def test_hard_deadline_discards_the_unfinished_day(self):
        fake = self.make_fake()
        clock = lambda: len(fake.calls)  # noqa: E731 - "time" advances one unit per request
        tally = self.go(fake, date_from="2026-10-05", date_to="2026-10-05", workers=1, hard_deadline=1.5, clock=clock)
        self.assertEqual(tally["aborted"], 1)
        self.assertEqual(tally["days_done"], 0)
        self.assertEqual(list((self.hist / "trades").iterdir()), [])  # no shard, no manifest, no tmp

    def test_newest_day_first_and_failed_day_is_not_marked_done(self):
        fake = self.make_fake()
        order = []

        def hook(method, params):
            order.append(C.utc_date(int(params["start_timestamp"])))
            if params["start_timestamp"] == str(C.date_to_ms("2026-10-06")) and len(order) < 50:
                raise T.ApiError(-32000, "boom")
        fake.on_call = hook
        tally = self.go(fake, workers=1, max_fail_streak=99)
        self.assertEqual(order[0], "2026-10-07")
        self.assertEqual(tally["days_failed"], 1)
        man = B.Manifest(self.hist / "trades" / "_manifest.jsonl")
        self.assertNotIn("2026-10-06", man.done)
        self.assertEqual(sorted(man.done), ["2026-10-03", "2026-10-04", "2026-10-05", "2026-10-07"])

    def test_derive_instruments_matches_independent_count(self):
        fake = self.make_fake()
        self.go(fake)
        out = B.derive_instruments(self.hist, **QUIET)
        self.assertEqual(out["shards"], 4)
        want = {}
        for t in fake.trades:
            w = want.setdefault(t["instrument_name"], [t["timestamp"], t["timestamp"], 0])
            w[0], w[1], w[2] = min(w[0], t["timestamp"]), max(w[1], t["timestamp"]), w[2] + 1
        import csv
        with open(self.hist / "instruments_from_trades.csv", newline="", encoding="utf-8") as f:
            got = {r["instrument_name"]: [int(r["first_trade_ms"]), int(r["last_trade_ms"]), int(r["n_trades"])]
                   for r in csv.DictReader(f)}
        self.assertEqual(got, want)


class DepthProbe(Base):
    def test_live_host_depth_vs_history_depth(self):
        trades = [T.make_trade(NOW - k * 6 * HOUR, 1000 - k) for k in range(161)]
        live = T.FakeDeribit(trade_floor_ms=NOW - 23 * HOUR - 30 * 60000)
        hist = T.FakeDeribit()
        live.trades, hist.trades = trades, trades
        rep = B.probe_depth(live.client(), hist.client(C.HISTORY_BASE), NOW, self.hist, **QUIET)
        self.assertEqual(rep["history_earliest_trade"]["ts_ms"], NOW - 160 * 6 * HOUR)
        self.assertEqual(rep["live_www_earliest_trade"]["ts_ms"], NOW - 18 * HOUR)
        self.assertEqual(rep["live_www_trades_in_1h_window_by_age_hours"],
                         {"6": 1, "12": 1, "18": 1, "23": 0, "24": 0, "25": 0, "30": 0, "48": 0, "168": 0, "720": 0})
        self.assertEqual(json.loads((self.hist / "_depth_report.json").read_text(encoding="utf-8")), rep)


class EndToEnd(Base):
    def test_main_runs_every_phase_and_report_reads_the_files(self):
        real = C.now_ms()  # main() uses the real clock for "now", so the synthetic data is built relative to it
        today = C.date_to_ms(C.utc_date(real))
        live, hist = T.FakeDeribit(), T.FakeDeribit()
        live.dvol["3600"] = T.make_ohlc(real - 2499 * HOUR, 2500, HOUR)
        live.dvol["1D"] = T.make_ohlc(today - 99 * DAY, 100, DAY)
        live.perp["60"] = T.make_perp(real - 599 * HOUR, 600, HOUR)
        live.perp["1D"] = T.make_perp(today - 99 * DAY, 100, DAY)
        live.funding = T.make_funding(real - 999 * HOUR, 1000)
        live.delivery = [{"date": "2026-10-%02d" % d, "delivery_price": 80000.0 + d} for d in range(8, 0, -1)]
        d1 = today - DAY  # yesterday UTC: the newest complete day main() will fetch
        hist.trades = [T.make_trade(d1 + 1000 * i, i + 1) for i in range(23)]
        argv = ["--data-dir", str(self.data), "--trades-from", C.utc_date(d1), "--trade-count", "10", "--workers", "2",
                "--max-seconds", "600"]
        rc = B.main(argv, clients=(live.client(), hist.client(C.HISTORY_BASE)))
        self.assertEqual(rc, 0)
        rep = B.report(self.data)
        self.assertEqual(rep["series"]["dvol_1h"]["rows"], 2500)
        self.assertEqual(rep["series"]["dvol_1d"]["rows"], 100)
        self.assertEqual(rep["series"]["perp_1h"]["rows"], 600)
        self.assertEqual(rep["series"]["perp_1d"]["rows"], 100)
        self.assertEqual(rep["series"]["funding"]["rows"], 1000)
        self.assertEqual(rep["series"]["delivery_prices"]["rows"], 8)
        self.assertEqual(rep["series"]["instruments_expired"]["rows"], 3)
        self.assertEqual(rep["trades"]["trades_in_shards"], 23)
        self.assertEqual(rep["trades"]["manifest_trades_sum"], 23)
        self.assertEqual(rep["trades"]["shard_files"], 1)
        self.assertEqual(rep["series"]["instruments_from_trades"]["rows"], 1)
        # second run: every complete series costs one call, the finished trade day costs none
        nl, nh = len(live.calls), len(hist.calls)
        rc = B.main(argv, clients=(live.client(), hist.client(C.HISTORY_BASE)))
        self.assertEqual(rc, 0)
        self.assertEqual(len(hist.calls) - nh, 1)  # only the depth probe's single earliest-trade request
        self.assertEqual(len(live.calls) - nl, 1 + 1 + 2 + 2 + 1 + 11)  # instruments, delivery, dvol x2, perp x2, funding, probe
        self.assertEqual(B.report(self.data)["trades"]["trades_in_shards"], 23)
        for m, _ in live.calls + hist.calls:
            self.assertTrue(m.startswith("public/"))


if __name__ == "__main__":
    unittest.main()
