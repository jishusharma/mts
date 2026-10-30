"""Offline test for us_open_alert. Run: python -I MyTradingSys/tools/test_us_open_alert.py
Expected values come from the NYSE rule 09:30 ET (EDT=UTC-4, EST=UTC-5), worked by hand, not from the code."""
import sys
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import us_open_alert as u


def utc(*a):
    return datetime(*a, tzinfo=timezone.utc)


class T(unittest.TestCase):
    def test_summer_open_1330(self):
        self.assertEqual(u.open_utc(date(2026, 7, 15)), utc(2026, 7, 15, 13, 30))

    def test_winter_open_1430(self):
        self.assertEqual(u.open_utc(date(2026, 12, 15)), utc(2026, 12, 15, 14, 30))

    def test_dst_edges_2026(self):  # DST 2026: Mar 8 -> Nov 1
        self.assertEqual(u.open_utc(date(2026, 3, 6)), utc(2026, 3, 6, 14, 30))   # Fri before
        self.assertEqual(u.open_utc(date(2026, 3, 9)), utc(2026, 3, 9, 13, 30))   # Mon after
        self.assertEqual(u.open_utc(date(2026, 10, 30)), utc(2026, 10, 30, 13, 30))  # Fri before end
        self.assertEqual(u.open_utc(date(2026, 11, 2)), utc(2026, 11, 2, 14, 30))  # Mon after

    def test_line_text(self):
        self.assertEqual(u.us_open_line(utc(2026, 10, 30, 13, 0)), "US open in 30 min (13:30 UTC) - context only")
        self.assertEqual(u.us_open_line(utc(2026, 12, 15, 14, 0)), "US open in 30 min (14:30 UTC) - context only")

    def test_winter_time_not_summer(self):  # 13:00 UTC in winter is 90 min out: no line
        self.assertIsNone(u.us_open_line(utc(2026, 12, 15, 13, 0)))

    def test_outside_window_and_after_open(self):
        self.assertIsNone(u.us_open_line(utc(2026, 10, 30, 10, 0)))
        self.assertIsNone(u.us_open_line(utc(2026, 10, 30, 13, 30)))  # at the open: gone
        self.assertEqual(u.us_open_line(utc(2026, 10, 30, 13, 29, 30)), "US open in 1 min (13:30 UTC) - context only")

    def test_weekend_skips_to_monday(self):
        self.assertEqual(u.next_open(utc(2026, 10, 31, 13, 0)), utc(2026, 11, 2, 14, 30))
        self.assertIsNone(u.us_open_line(utc(2026, 10, 31, 13, 0)))

    def test_holiday_skip(self):
        h = {date(2026, 12, 25)}
        self.assertEqual(u.next_open(utc(2026, 12, 25, 10, 0), h), utc(2026, 12, 28, 14, 30))


if __name__ == "__main__":
    unittest.main()
