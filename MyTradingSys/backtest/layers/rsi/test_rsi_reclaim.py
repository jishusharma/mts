import unittest

from MyTradingSys.backtest.layers.rsi.rsi_reclaim import rsi_reclaim_events, rsi_retest


def _ts(rsi):
    return list(range(len(rsi)))


class TestReclaim(unittest.TestCase):
    """Expected values hand-walked from the rule text in rsi_reclaim.py, not taken from the code."""

    def test_case_a_one_bar_below_then_pops_back(self):
        # level 40, clearance 1: below < 39, band 39..41, above > 41
        rsi = [45, 43, 38, 40.5, 42, 44]
        ev = rsi_reclaim_events(rsi, _ts(rsi), 40, 1)
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["t"], e["dwell_below"], e["band_bars"], e["direct"]), (4, 1, 1, False))
        self.assertAlmostEqual(e["depth"], 2.0)

    def test_case_b_long_dwell_direct_cross(self):
        # 38,37,35,34,36,38.5 are all < 39 (6 bars, idx 1..6); 43 > 41 reclaims directly at idx 7
        rsi = [50, 38, 37, 35, 34, 36, 38.5, 43]
        e = rsi_reclaim_events(rsi, _ts(rsi), 40, 1)[0]
        self.assertEqual((e["t"], e["dwell_below"], e["band_bars"], e["direct"], e["run_start_t"]),
                         (7, 6, 0, True, 1))
        self.assertAlmostEqual(e["depth"], 6.0)

    def test_band_pop_splits_run(self):
        rsi = [30, 30, 40, 30, 50]            # 40 is in the band, so the second run restarts at idx 3
        e = rsi_reclaim_events(rsi, _ts(rsi), 40, 1)[0]
        self.assertEqual((e["dwell_below"], e["run_start_t"], e["band_bars"]), (1, 3, 0))

    def test_no_event_without_prior_below(self):
        rsi = [50, 55, 45, 52]
        self.assertEqual(rsi_reclaim_events(rsi, _ts(rsi), 40, 1), [])

    def test_none_bars_carry_state(self):
        rsi = [30, None, None, 30, 50]
        e = rsi_reclaim_events(rsi, _ts(rsi), 40, 1)[0]
        self.assertEqual((e["dwell_below"], e["t"]), (2, 4))

    def test_clearance_zero_exactly_on_level_is_band(self):
        e = rsi_reclaim_events([35, 40, 41], [0, 1, 2], 40, 0)
        self.assertEqual((e[0]["t"], e[0]["band_bars"]), (2, 1))

    def test_second_reclaim_needs_a_new_below_run(self):
        rsi = [30, 50, 45, 50, 30, 50]
        ev = rsi_reclaim_events(rsi, _ts(rsi), 40, 1)
        self.assertEqual([e["t"] for e in ev], [1, 5])

    def test_down_mirror(self):
        # level 60, clearance 1: "above" = > 61, band 59..61, back below = < 59 is not needed; reclaim = < 59
        rsi = [55, 62, 65, 60.5, 58]
        e = rsi_reclaim_events(rsi, _ts(rsi), 60, 1, direction="down")[0]
        self.assertEqual((e["t"], e["dwell_below"], e["band_bars"], e["direction"]), (4, 2, 1, "down"))
        self.assertAlmostEqual(e["depth"], 5.0)

    def test_bad_args(self):
        with self.assertRaises(ValueError):
            rsi_reclaim_events([1], [1], 40, -1)
        with self.assertRaises(ValueError):
            rsi_reclaim_events([1, 2], [1], 40, 1)
        with self.assertRaises(ValueError):
            rsi_reclaim_events([1], [1], 40, 1, direction="x")


class TestRetest(unittest.TestCase):
    def _ev(self, rsi, level=40, clearance=1, direction="up"):
        return rsi_reclaim_events(rsi, _ts(rsi), level, clearance, direction)

    def test_support(self):
        rsi = [35, 36, 44, 41, 39.5, 43]       # reclaim idx 2, band at 3 and 4, above at 5
        r = rsi_retest(rsi, self._ev(rsi), 40, 1, within=5)[0]
        self.assertEqual((r["status"], r["touch_i"], r["resolve_i"], r["bars_after"]), ("support", 3, 5, 3))

    def test_fail(self):
        rsi = [35, 44, 41, 37, 45]
        r = rsi_retest(rsi, self._ev(rsi), 40, 1, within=5)[0]
        self.assertEqual((r["status"], r["resolve_i"]), ("fail", 3))

    def test_none_outside_window(self):
        rsi = [35, 44, 45, 46, 40, 44]         # touch only at idx 4, window ends at idx 3
        r = rsi_retest(rsi, self._ev(rsi), 40, 1, within=2)[0]
        self.assertEqual(r["status"], "none")

    def test_down_support(self):
        rsi = [65, 56, 59.5, 56]               # reclaim down idx 1, band at 2, below again at 3
        ev = self._ev(rsi, level=60, direction="down")
        r = rsi_retest(rsi, ev, 60, 1, within=3, direction="down")[0]
        self.assertEqual((r["status"], r["resolve_i"]), ("support", 3))

    def test_within_validation(self):
        with self.assertRaises(ValueError):
            rsi_retest([1], [], 40, 1, within=0)


if __name__ == "__main__":
    unittest.main()
