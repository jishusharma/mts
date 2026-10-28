"""Tests for instruments.py: instrument-name parsing (1- and 2-digit days, expiry = 08:00 UTC), date helpers and the
delivery-price loader. Expected epoch values come from calendar.timegm (bt_testutil.ms), not from the implementation."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bt_testutil as U  # noqa: E402
from bt_testutil import HOUR, DAY, ms  # noqa: E402

import instruments as I  # noqa: E402

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


class Parse(unittest.TestCase):
    def test_one_digit_day_put(self):
        i = I.parse_instrument("BTC-9OCT26-86000-P")
        self.assertEqual(i.underlying, "BTC")
        self.assertEqual(i.expiry_ms, ms(2026, 10, 9, 8))
        self.assertEqual(i.strike, 86000)
        self.assertFalse(i.is_call)
        self.assertEqual(i.name, "BTC-9OCT26-86000-P")

    def test_two_digit_day_call(self):
        i = I.parse_instrument("BTC-27NOV26-88000-C")
        self.assertEqual(i.expiry_ms, ms(2026, 11, 27, 8))
        self.assertEqual(i.strike, 88000)
        self.assertTrue(i.is_call)

    def test_expiry_is_0800_utc_not_midnight(self):
        i = I.parse_instrument("BTC-9OCT26-86000-P")
        self.assertEqual(i.expiry_ms % DAY, 8 * HOUR)
        self.assertEqual(i.expiry_ms - ms(2026, 10, 9), 8 * HOUR)

    def test_every_month_and_day_width(self):
        for m, mon in enumerate(MONTHS, start=1):
            for day in (1, 9, 10, 28):
                for year in (2021, 2026, 2027):
                    name = "BTC-%d%s%02d-50000-C" % (day, mon, year % 100)
                    i = I.parse_instrument(name)
                    self.assertIsNotNone(i, name)
                    self.assertEqual(i.expiry_ms, ms(year, m, day, 8), name)

    def test_year_boundary_and_leap_day(self):
        self.assertEqual(I.parse_instrument("BTC-1JAN27-100000-C").expiry_ms, ms(2027, 1, 1, 8))
        self.assertEqual(I.parse_instrument("BTC-29FEB24-60000-P").expiry_ms, ms(2024, 2, 29, 8))
        self.assertEqual(I.parse_instrument("BTC-31DEC21-45000-P").expiry_ms, ms(2021, 12, 31, 8))

    def test_expiry_weekday_is_utc_monday_zero(self):
        # 2026-10-09 is a Friday, 10-10 Saturday, 10-11 Sunday, 10-12 Monday (UTC)
        self.assertEqual(I.parse_instrument("BTC-9OCT26-86000-P").expiry_weekday, 4)
        self.assertEqual(I.parse_instrument("BTC-10OCT26-86000-P").expiry_weekday, 5)
        self.assertEqual(I.parse_instrument("BTC-11OCT26-86000-P").expiry_weekday, 6)
        self.assertEqual(I.parse_instrument("BTC-12OCT26-86000-P").expiry_weekday, 0)

    def test_expiry_date_string(self):
        self.assertEqual(I.parse_instrument("BTC-9OCT26-86000-P").expiry_date, "2026-10-09")
        self.assertEqual(I.parse_instrument("BTC-27NOV26-88000-C").expiry_date, "2026-11-27")

    def test_not_an_option_gives_none(self):
        for bad in ("BTC-PERPETUAL", "BTC-9OCT26", "BTC-9OCT26-86000-X", "BTC-9XXX26-86000-C", "BTC-31FEB26-80000-C",
                    "", None, "garbage"):
            self.assertIsNone(I.parse_instrument(bad), bad)

    def test_many_strikes_same_expiry_share_expiry_ms(self):
        a, b = I.parse_instrument("BTC-9OCT26-70000-P"), I.parse_instrument("BTC-9OCT26-90000-C")
        self.assertEqual(a.expiry_ms, b.expiry_ms)
        self.assertNotEqual(a.strike, b.strike)


class DateHelpers(unittest.TestCase):
    def test_ymd_roundtrip(self):
        self.assertEqual(I.ymd_to_ms("2026-10-09"), ms(2026, 10, 9))
        self.assertEqual(I.ms_to_ymd(ms(2026, 10, 9, 23, 59, 59)), "2026-10-09")
        self.assertEqual(I.ms_to_ymd(ms(2026, 10, 10, 0, 0, 0)), "2026-10-10")
        self.assertEqual(I.ms_to_ymd(I.ymd_to_ms("2024-02-29")), "2024-02-29")

    def test_weekday_of_ms(self):
        self.assertEqual(I.weekday_of_ms(ms(2026, 10, 9, 8)), 4)             # Friday
        self.assertEqual(I.weekday_of_ms(ms(2026, 10, 9, 23, 59, 59)), 4)
        self.assertEqual(I.weekday_of_ms(ms(2026, 10, 10, 0, 0, 0)), 5)      # Saturday starts at 00:00 UTC
        self.assertEqual(I.weekday_of_ms(ms(2026, 10, 5, 12)), 0)            # Monday


class DeliveryLoader(unittest.TestCase):
    def test_loads_date_to_price_and_ignores_bad_rows(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "delivery_prices.csv"
            p.write_text("ts_ms,date,delivery_price\n1791244800000,2026-10-06,85123.45\n1791331200000,2026-10-07,not_a_number\n"
                         "1791417600000,2026-10-08,86000\n", encoding="utf-8", newline="\n")
            got = I.load_delivery_prices(p)
            self.assertEqual(got, {"2026-10-06": 85123.45, "2026-10-08": 86000.0})

    def test_missing_file_gives_empty_dict(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(I.load_delivery_prices(Path(d) / "nope.csv"), {})


if __name__ == "__main__":
    unittest.main()
