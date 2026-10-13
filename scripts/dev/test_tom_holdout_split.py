"""tom-holdout-clean-split: hand-computed dropped days and design/check split on a fixture."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tom_holdout_split as h  # noqa: E402

DAYS = ["2026-05-11", "2026-05-12", "2026-05-13", "2026-05-14", "2026-05-15", "2026-05-18", "2026-05-19", "2026-05-20"]


class T(unittest.TestCase):
    def test_drops_day_and_neighbours(self):
        _, dropped, rem = h.clean_holdout(["2026-05-12"], DAYS)
        self.assertEqual(sorted(dropped), ["2026-05-11", "2026-05-12", "2026-05-13"])
        self.assertEqual(rem, ["2026-05-14", "2026-05-15", "2026-05-18", "2026-05-19", "2026-05-20"])

    def test_weekend_candidate_drops_adjacent_trading_days(self):
        _, dropped, _ = h.clean_holdout(["2026-05-16"], DAYS)
        self.assertEqual(sorted(dropped), ["2026-05-15", "2026-05-18"])

    def test_sunday_session_bars_go_with_dropped_monday(self):
        days = ["2026-05-14", "2026-05-15", "2026-05-17", "2026-05-18", "2026-05-19", "2026-05-20"]
        _, dropped, _ = h.clean_holdout(["2026-05-18"], days)
        self.assertEqual(sorted(dropped), ["2026-05-15", "2026-05-17", "2026-05-18", "2026-05-19"])

    def test_outside_window_ignored(self):
        _, dropped, _ = h.clean_holdout(["2026-03-19"], DAYS)
        self.assertEqual(dropped, {})

    def test_neighbour_in_dev_not_counted(self):
        days = ["2026-04-09", "2026-04-10", "2026-04-13", "2026-04-14"]
        _, dropped, _ = h.clean_holdout(["2026-04-13"], days)
        self.assertEqual(sorted(dropped), ["2026-04-13", "2026-04-14"])

    def test_split_is_spec_section_7(self):
        self.assertEqual(h.flat("design"), ["T1", "T2", "T2b", "T3", "T3b", "T5", "T6", "T7"])
        self.assertEqual(h.flat("check"), ["T11", "T12"])
        self.assertEqual(h.flat("family_c_in_neither_set"), ["T4"])
        self.assertFalse(set(h.flat("design")) & set(h.flat("check")))

    def test_dev_window_dropping(self):
        days = ["2026-03-17", "2026-03-18", "2026-03-19", "2026-03-20", "2026-03-23"]
        _, dropped, _ = h.clean_holdout(["2026-03-19"], days, h.DEV_START, h.DEV_END)
        self.assertEqual(sorted(dropped), ["2026-03-18", "2026-03-19", "2026-03-20"])


if __name__ == "__main__":
    unittest.main()
