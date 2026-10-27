"""Tests for plan_score.py. Expected values are worked by hand from the definition in its docstring."""
import sys
sys.dont_write_bytecode = True
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan_score as P  # noqa: E402

T0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)


def bars(spec):
    """spec: [(minutes_after_post, high, low)]"""
    return [(T0 + timedelta(minutes=m), hi, lo) for m, hi, lo in spec]


class TestScore(unittest.TestCase):
    def test_no_data_is_not_a_miss(self):
        with self.assertRaises(P.NoData):
            P.score_plan([], "short", 100, 90, T0)
        with self.assertRaises(P.NoData):  # candles exist but all before the post
            P.score_plan(bars([(-5, 101, 99)]), "short", 100, 90, T0)

    def test_short_full(self):
        self.assertEqual(P.score_plan(bars([(10, 101, 99), (60, 99, 89)]), "short", 100, 90, T0), "full")

    def test_short_partial_half_way(self):
        # entry 100 touched, low 95 = 5 of 10 = exactly half -> partial
        self.assertEqual(P.score_plan(bars([(10, 101, 99), (60, 99, 95)]), "short", 100, 90, T0), "partial")

    def test_short_miss_below_half(self):
        self.assertEqual(P.score_plan(bars([(10, 101, 99), (60, 99, 96)]), "short", 100, 90, T0), "miss")

    def test_entry_never_touched_is_miss(self):
        self.assertEqual(P.score_plan(bars([(10, 98, 80)]), "short", 100, 90, T0), "miss")

    def test_entry_after_fill_window_is_miss(self):
        self.assertEqual(P.score_plan(bars([(10, 98, 97), (25 * 60, 101, 99), (26 * 60, 99, 80)]), "short", 100, 90, T0), "miss")

    def test_target_before_entry_does_not_count(self):
        self.assertEqual(P.score_plan(bars([(10, 98, 89), (30, 101, 99), (60, 100, 97)]), "short", 100, 90, T0), "miss")

    def test_long_full(self):
        self.assertEqual(P.score_plan(bars([(5, 101, 99), (50, 111, 100)]), "long", 100, 110, T0), "full")


class TestLedger(unittest.TestCase):
    def test_price_parse(self):
        self.assertEqual(P.first_price("65,600 (sweep, short above)"), 65600.0)
        self.assertIsNone(P.first_price("NOT STATED (chart-relative)"))
        self.assertIsNone(P.first_price(""))

    def test_committed_ledger_matches_and_holdout_is_not_scored(self):
        rows = P.build_plan_ledger()
        self.assertEqual(len(rows), 9)
        self.assertEqual(sum(r["split"] == "DEV" for r in rows), 0)  # all priced plans are after 2026-06-26
        for r in rows:
            self.assertNotEqual(r["status"], "READY_DEV")
        self.assertEqual(P.OUT.read_bytes().decode("utf-8").replace("\r\n", "\n"), P.render(rows))


if __name__ == "__main__":
    unittest.main(verbosity=2)
