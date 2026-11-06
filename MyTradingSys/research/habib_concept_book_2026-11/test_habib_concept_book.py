"""Spec tests for the Habib concept book helpers (card habib-plan-scoring-not-trades-1104 and habib_watch.py).
Run: python MyTradingSys/research/habib_concept_book_2026-11/test_habib_concept_book.py   (offline, no network)
Expected numbers are computed by hand in the comments, not taken from the code under test.
"""
import csv
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import habib_common as hc  # noqa: E402
import calls_score as cs  # noqa: E402

M = 60_000


def bar(i, o, h, l, c, v=1.0):
    return [i * M, o, h, l, c, v]


class TestCandleReading(unittest.TestCase):
    def test_rel_volume_uses_prior_median_only(self):
        # 50 bars of volume 10, then one bar of 25: median of prior 50 = 10 -> 2.5; the first 50 bars have no baseline
        rows = [[i, 1, 1, 1, 1, 10.0] for i in range(50)] + [[50, 1, 1, 1, 1, 25.0]]
        rv = hc.rel_volume(rows)
        self.assertTrue(all(x is None for x in rv[:50]))
        self.assertAlmostEqual(rv[50], 2.5)

    def test_body_and_wick_classes(self):
        small = [0, 100.0, 110.0, 90.0, 101.0, 1]      # body 1 of range 20 = 5 %
        large = [0, 90.0, 110.0, 90.0, 105.0, 1]       # body 15 of 20 = 75 %, lower wick 0 %, upper wick 25 %
        self.assertEqual(hc.body_class(small), "small")
        self.assertEqual(hc.body_class(large), "large")
        self.assertEqual(hc.wick_label(large), "wickless-bottom")
        u, l = hc.wicks(small)
        self.assertAlmostEqual(u, 9 / 20)              # high 110 - max(open, close) 101 = 9
        self.assertAlmostEqual(l, 10 / 20)             # min(open, close) 100 - low 90 = 10

    def test_value_area_poc_on_50_usd_bins(self):
        # typical price 100 (bin 2) volume 5; typical 160 (bin 3) volume 1: POC bin = 2 * 50 = 100; 70 % of 6 = 4.2 <= 5
        bars = [[0, 100, 100, 100, 100, 5.0], [M, 160, 160, 160, 160, 1.0]]
        va = hc.value_area(bars)
        self.assertEqual(va["poc"], 100.0)
        self.assertEqual((va["val"], va["vah"]), (100.0, 150.0))

    def test_prior_day_levels_fail_closed_on_a_day_with_holes(self):
        day = 86_400_000
        full = [[day + i * M, 100 + i * 0.01, 101 + i * 0.01, 99, 100, 1.0] for i in range(1440)]
        now = 2 * day + 5 * M
        lv = hc.prior_day_levels(full, now)
        self.assertEqual(lv["Prior day low"], 99)
        self.assertIn("Prior POC", lv)
        self.assertEqual(hc.prior_day_levels(full[:1000], now), {})   # fewer than 1380 bars: absent, never guessed


class TestPlanPath(unittest.TestCase):
    def test_short_fills_then_hits_target_and_records_adverse_move(self):
        bars = [bar(0, 100, 100.5, 99.5, 100), bar(1, 100, 101.0, 100, 100.5), bar(2, 100.5, 100.8, 98.9, 99), bar(3, 99, 99.2, 94.9, 95)]
        p = cs.fill_and_path(bars, "short", 101.0, 95.0, 0)
        self.assertEqual(p["fill"], 1 * M)
        self.assertEqual(p["hit"], 3 * M)
        self.assertAlmostEqual(p["mae"], 0.0)            # high never went above the entry 101 after the fill bar

    def test_stop_and_target_in_the_same_minute_resolve_to_the_stop(self):
        bars = [bar(0, 100, 100.2, 99.9, 100), bar(1, 100, 101.2, 94.0, 96)]
        p = cs.fill_and_path(bars, "short", 100.1, 95.0, 0, stop=101.0)
        self.assertTrue(p["stopped_first"])

    def test_no_fill_inside_24h_returns_none(self):
        bars = [bar(0, 100, 100.2, 99.9, 100), bar(1500, 100, 105, 99, 104)]   # minute 1500 is after 24 h
        self.assertIsNone(cs.fill_and_path(bars, "short", 104.0, 90.0, 0))


class TestShippedNumbers(unittest.TestCase):
    def test_scored_csv_covers_the_ledger_and_the_preregistered_counts(self):
        led = [r["call_id"] for r in csv.DictReader(open(HERE.parent / "habib_plan_imbalance_2026-10-20" / "PLAN_LEDGER.csv", encoding="utf-8"))]
        rows = list(csv.DictReader(open(HERE / "CALLS_SCORED.csv", encoding="utf-8")))
        self.assertEqual([r["call_id"] for r in rows], led)
        by = {}
        for r in rows:
            by[r["status"]] = by.get(r["status"], 0) + 1
        self.assertEqual(by, {"full": 1, "miss": 8})     # pre-reg rule 24 h / 7 d, run 2026-11-07

    def test_every_plan_is_named_in_the_calls_document(self):
        lines = (HERE / "CALLS_VS_BOOK.md").read_text(encoding="utf-8").splitlines()
        for r in csv.DictReader(open(HERE / "CALLS_SCORED.csv", encoding="utf-8")):
            vid, suffix = r["call_id"][4:-3], r["call_id"][-2:]
            self.assertTrue(any(l.startswith("| `") and vid[:3] in l.split("|")[1] and "-" + suffix in l.split("|")[1] for l in lines), r["call_id"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
