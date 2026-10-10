import sys
sys.dont_write_bytecode = True
"""Tests for tom_probe_diag.py. Expected numbers are derived by hand from the stated rules, not from the code.

Rules under test (module docstring):
- MFE counts bars AFTER the fill bar (fill-bar order of high vs fill is unknown); MAE counts the fill bar too (the
  simulator assumes the stop comes after the fill). R = excursion / |entry - stop|.
- A stopped trade's exit bar is excluded from MFE (stop-first convention), included in MAE.
- Sessions are local-time opens converted with zoneinfo (DST-correct).
"""
import datetime as dt
import unittest
from array import array
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tom_bt as T  # noqa: E402
import tom_probe_diag as D  # noqa: E402


def mk(bars, t0=0):
    o, h, l, c, v, tbv = (array("d") for _ in range(6))
    for a, b, d, e in bars:
        o.append(a); h.append(b); l.append(d); c.append(e); v.append(1.0); tbv.append(0.5)
    return T.Bars1m(t0, o, h, l, c, v, tbv)


def utc(y, m, d, hh, mm):
    return dt.datetime(y, m, d, hh, mm, tzinfo=dt.timezone.utc).timestamp()


# Long, entry 100, stop 90 -> risk 10. Bar 0 is the fill bar: its high (130) must NOT count for MFE; its low (97) counts for MAE.
LONG_BARS = [
    (100, 130, 97, 100),   # 0 fill bar
    (100, 104, 98, 103),   # 1
    (103, 108, 99, 107),   # 2
    (107, 110, 96, 100),   # 3  lowest low 96 -> MAE 0.4 R
    (100, 112, 99, 111),   # 4
    (111, 118, 105, 117),  # 5
    (117, 125, 110, 120),  # 6  highest high 125 -> MFE 2.5 R
    (120, 121, 108, 109),  # 7
    (109, 115, 104, 110),  # 8
    (110, 112, 102, 105),  # 9  timeout exit here
]


class TestExcursions(unittest.TestCase):
    def test_long_ten_bars_mfe_2_5_mae_0_4(self):
        b = mk(LONG_BARS)
        r = D.excursions(b, fill_i=0, exit_i=9, reason="timeout", side="long", entry=100.0, stop=90.0, window=240)
        self.assertAlmostEqual(r["mfe_exit"], 2.5, places=9)
        self.assertAlmostEqual(r["mae_exit"], 0.4, places=9)

    def test_short_mirror(self):
        mirror = [(200 - o, 200 - l, 200 - h, 200 - c) for o, h, l, c in LONG_BARS]  # short entry 100, stop 110
        b = mk(mirror)
        r = D.excursions(b, 0, 9, "timeout", "short", 100.0, 110.0, 240)
        self.assertAlmostEqual(r["mfe_exit"], 2.5, places=9)
        self.assertAlmostEqual(r["mae_exit"], 0.4, places=9)

    def test_stopped_trade_exit_bar_excluded_from_mfe_included_in_mae(self):
        bars = [(100, 101, 99, 100), (100, 102, 98, 100),   # 0 fill, 1: high 102 -> MFE 0.2
                (100, 150, 89, 90)]                          # 2: stop bar (low 89 <= 90); its 150 high must not count
        b = mk(bars)
        r = D.excursions(b, 0, 2, "stop", "long", 100.0, 90.0, 240)
        self.assertAlmostEqual(r["mfe_exit"], 0.2, places=9)
        self.assertAlmostEqual(r["mae_exit"], 1.1, places=9)  # gap/slip through the stop: low 89 = 1.1 R

    def test_four_hour_window_runs_past_exit_and_pre_stop_truncates_at_stop(self):
        # stop at bar 2; afterwards price rallies to 130 (3 R) inside the 4 h window.
        bars = [(100, 101, 99, 100), (100, 103, 98, 100), (100, 100, 89, 90), (90, 130, 90, 128)]
        b = mk(bars)
        r = D.excursions(b, 0, 2, "stop", "long", 100.0, 90.0, 240)
        self.assertAlmostEqual(r["mfe_4h"], 3.0, places=9)           # bar 3 high 130 counts in the plain window
        self.assertAlmostEqual(r["mfe_4h_pre_stop"], 0.3, places=9)  # stop touched at bar 2 -> only bar 1 (103) counts
        self.assertFalse(r["win_complete"])                          # series ends before 240 bars

    def test_window_complete_flag(self):
        bars = [(100, 100.5, 99.5, 100)] * 300
        b = mk(bars)
        r = D.excursions(b, 0, 10, "timeout", "long", 100.0, 90.0, 240)
        self.assertTrue(r["win_complete"])


class TestSessions(unittest.TestCase):
    def test_us_open_july_1330z_and_january_1430z(self):
        for ts in (utc(2026, 7, 15, 13, 30), utc(2026, 1, 14, 14, 30)):
            label, open_ts, hrs = D.session_of(ts)
            self.assertEqual(label, "US_open", ts)
            self.assertEqual(open_ts, ts)
            self.assertAlmostEqual(hrs, 0.0)

    def test_january_1330z_is_not_us_open(self):
        label, _, hrs = D.session_of(utc(2026, 1, 14, 13, 30))  # NY 08:30 EST: before the open
        self.assertEqual(label, "DAX/London")  # DAX 09:00 CET = London 08:00 GMT = 08:00Z
        self.assertAlmostEqual(hrs, 5.5)

    def test_dax_and_london_open_coincide_in_both_dst_regimes(self):
        self.assertEqual(D.session_of(utc(2026, 7, 15, 7, 0))[0], "DAX/London")   # 09:00 CEST = 08:00 BST = 07:00Z
        self.assertEqual(D.session_of(utc(2026, 1, 14, 8, 0))[0], "DAX/London")   # 09:00 CET = 08:00 GMT = 08:00Z

    def test_asia_open_and_us_close(self):
        self.assertEqual(D.session_of(utc(2026, 7, 15, 0, 0))[0], "Asia")        # 09:00 JST = 00:00Z, no DST in Japan
        self.assertEqual(D.session_of(utc(2026, 7, 15, 20, 0))[0], "US_close")   # 16:00 EDT = 20:00Z
        self.assertEqual(D.session_of(utc(2026, 1, 14, 21, 0))[0], "US_close")   # 16:00 EST = 21:00Z
        label, _, hrs = D.session_of(utc(2026, 1, 14, 23, 30))
        self.assertEqual(label, "US_close")
        self.assertAlmostEqual(hrs, 2.5)

    def test_hours_since_bucket(self):
        self.assertEqual(D.hour_bucket(0.0), "0-2h")
        self.assertEqual(D.hour_bucket(1.99), "0-2h")
        self.assertEqual(D.hour_bucket(2.0), "2-4h")
        self.assertEqual(D.hour_bucket(4.0), "later")

    def test_weekend_flag_utc(self):
        self.assertEqual(D.day_kind(utc(2026, 10, 10, 12, 0)), "weekend")  # Saturday
        self.assertEqual(D.day_kind(utc(2026, 10, 11, 23, 59)), "weekend")  # Sunday
        self.assertEqual(D.day_kind(utc(2026, 10, 12, 0, 0)), "weekday")    # Monday

    def test_windows_membership_overlaps(self):
        # 14:00Z in January: DAX/London 08:00Z +6h (outside), US open 14:30Z not yet -> in no 0-4h window
        self.assertEqual(D.windows_of(utc(2026, 1, 14, 14, 0), 4.0), [])
        # 15:00Z January: US open +0.5h -> US_open 0-2h
        self.assertEqual(D.windows_of(utc(2026, 1, 14, 15, 0), 4.0), [("US_open", "0-2h")])
        # 09:30Z January: DAX 1.5h and London 1.5h share the instant -> reported once as DAX/London
        self.assertEqual(D.windows_of(utc(2026, 1, 14, 9, 30), 4.0), [("DAX/London", "0-2h")])


if __name__ == "__main__":
    unittest.main()
