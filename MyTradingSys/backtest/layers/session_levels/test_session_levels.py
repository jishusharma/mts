"""Tests for session_levels.py (T087). Expected numbers hand-derived from the module docstring spec."""
import unittest

from MyTradingSys.backtest.layers.session_levels import session_levels as sl

MIN = 60000
DAY = 1440 * MIN


def flat_day(d, o=99.0, h=99.2, lo=98.8):
    return [{"t": d * DAY + m * MIN, "o": o, "h": h, "l": lo, "c": o} for m in range(1440)]


def setd(bars, d, m, **kw):
    bars[d * 1440 + m].update(kw)


def scenario():
    """day0 prior high = 100.0. day1: Asia low 98.0 (01:00), EU low 98.5 (08:20), touch 10:00 (h 100.5, c 100.2),
    fail 10:01 (c 99.7)."""
    bars = flat_day(0) + flat_day(1)
    setd(bars, 0, 700, h=100.0)
    setd(bars, 1, 60, l=98.0)
    setd(bars, 1, 500, l=98.5)
    setd(bars, 1, 600, h=100.5, c=100.2)
    setd(bars, 1, 601, h=100.3, l=99.5, c=99.7)
    return bars


class FailedBreak(unittest.TestCase):
    def test_touch_fail_levels(self):
        ev = sl.failed_break_events(scenario(), "high")
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual(e["level"], 100.0)
        self.assertEqual(e["touch_min"], 600)
        self.assertEqual(e["fail_min"], 601)
        self.assertEqual(e["touch_session"], "eu")
        self.assertEqual(e["entry"], 99.7)
        self.assertEqual(e["spike"], 100.5)
        self.assertEqual(e["asia_low"], 98.0)
        self.assertEqual(e["eu_low"], 98.5)

    def test_targets_taken_before_stop(self):
        bars = scenario()
        setd(bars, 1, 700, l=98.4)    # EU low 98.5 taken
        setd(bars, 1, 800, l=97.9)    # Asia low 98.0 taken
        e = sl.failed_break_events(bars, "high")[0]
        self.assertEqual(e["eu"]["first"], "target")
        self.assertEqual(e["asia"]["first"], "target")
        fee = 0.0005
        self.assertAlmostEqual(e["eu"]["net"], (99.7 - 98.5) / 99.7 - 2 * fee, places=9)
        self.assertAlmostEqual(e["asia"]["net"], (99.7 - 98.0) / 99.7 - 2 * fee, places=9)

    def test_stop_first(self):
        bars = scenario()
        setd(bars, 1, 650, h=100.6)    # spike high 100.5 exceeded before any target
        setd(bars, 1, 700, l=98.4)
        e = sl.failed_break_events(bars, "high")[0]
        self.assertEqual(e["eu"]["first"], "stop")
        self.assertAlmostEqual(e["eu"]["net"], (99.7 - 100.5) / 99.7 - 2 * 0.0005, places=9)

    def test_same_bar_counts_stop(self):
        bars = scenario()
        setd(bars, 1, 650, h=100.6, l=98.4)
        e = sl.failed_break_events(bars, "high")[0]
        self.assertEqual(e["eu"]["first"], "stop")

    def test_neither_exits_at_us_open_close(self):
        e = sl.failed_break_events(scenario(), "high")[0]
        self.assertEqual(e["eu"]["first"], "neither")
        # last bar before 14:00 is minute 839, close 99.0
        self.assertAlmostEqual(e["eu"]["net"], (99.7 - 99.0) / 99.7 - 2 * 0.0005, places=9)

    def test_touch_after_us_open_is_no_event(self):
        bars = flat_day(0) + flat_day(1)
        setd(bars, 0, 700, h=100.0)
        setd(bars, 1, 900, h=100.5, c=100.2)
        setd(bars, 1, 901, c=99.7)
        self.assertEqual(sl.failed_break_events(bars, "high"), [])

    def test_no_fail_within_window_is_no_event(self):
        bars = flat_day(0) + flat_day(1)
        setd(bars, 0, 700, h=100.0)
        for m in range(600, 700):
            setd(bars, 1, m, h=100.5, c=100.2)
        self.assertEqual(sl.failed_break_events(bars, "high"), [])

    def test_first_touch_only(self):
        bars = scenario()
        setd(bars, 1, 620, h=100.4, c=100.1)
        setd(bars, 1, 621, c=99.6)
        self.assertEqual(len(sl.failed_break_events(bars, "high")), 1)

    def test_target_not_below_entry_skipped(self):
        bars = scenario()
        setd(bars, 1, 601, c=96.0, l=96.0)     # fail bar closes on its own low: lows equal entry, no target below it
        e = sl.failed_break_events(bars, "high")[0]
        self.assertIsNone(e["eu"])
        self.assertIsNone(e["asia"])

    def test_first_day_has_no_prior(self):
        bars = flat_day(0)
        setd(bars, 0, 600, h=100.5, c=100.2)
        self.assertEqual(sl.failed_break_events(bars, "high"), [])

    def test_incomplete_prior_day_skipped(self):
        bars = scenario()
        del bars[0:100]          # prior day lacks bars
        self.assertEqual(sl.failed_break_events(bars, "high"), [])

    def test_mirror_low_side(self):
        # mirror of scenario about 0: prior low = -(100.0) ... build directly with prices around 200-x
        base = scenario()
        mir = [{"t": b["t"], "o": 200 - b["o"], "h": 200 - b["l"], "l": 200 - b["h"], "c": 200 - b["c"]} for b in base]
        e = sl.failed_break_events(mir, "low")[0]
        self.assertEqual(e["level"], 100.0)
        self.assertEqual(e["entry"], 200 - 99.7)
        self.assertEqual(e["spike"], 200 - 100.5)
        self.assertEqual(e["asia_low"], 200 - 98.0)     # key keeps its name: the opposite session extreme
        self.assertEqual(e["touch_session"], "eu")


class Levels(unittest.TestCase):
    def test_day_levels(self):
        bars = scenario()
        lv = sl.day_levels(bars)
        self.assertEqual(lv[0]["high"], 100.0)
        self.assertEqual(lv[1]["asia_low"], 98.0)
        self.assertEqual(lv[1]["asia_high"], 99.2)


if __name__ == "__main__":
    unittest.main()
