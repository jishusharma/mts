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

    def test_split_clusters_and_every_third(self):
        g = {"T1": {"2026-01-01"}, "T2": {"2026-01-02"}, "T3": {"2026-01-03", "2026-01-04"},
             "T4": {"2026-01-04"}, "T5": {"2026-01-09"}, "T6": set()}
        cl, design, check, undated = h.split(g)
        self.assertEqual([c[0] for c in cl], [["T1"], ["T2"], ["T3", "T4"], ["T5"]])
        self.assertEqual(check, ["T2"])
        self.assertEqual(design, ["T1", "T3", "T4", "T5"])
        self.assertEqual(undated, ["T6"])


if __name__ == "__main__":
    unittest.main()
