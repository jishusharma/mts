"""Tests for with_trend_census.py (Shape A). Synthetic bars only; no data cache needed."""
import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import with_trend_census as w  # noqa: E402


def bar(t, o, h, l, c):
    return dict(t=t, o=o, h=h, l=l, c=c, v=1.0, delta=0.0)


def ms(h, m=0, day=3):
    return int(dt.datetime(2024, 1, day, h, m, tzinfo=dt.UTC).timestamp() * 1000)


class SimTests(unittest.TestCase):
    def test_target_hit_long(self):
        r = w.simulate_trade(1, 100.0, 99.5, [bar(0, 100, 100.2, 99.9, 100), bar(1, 100, 101.2, 99.9, 101)])
        self.assertEqual(r["kind"], "target")
        self.assertAlmostEqual(r["gross_frac"], 0.01, places=6)
        self.assertAlmostEqual(r["gross_r"], 2.0, places=6)
        self.assertLess(r["net_r_T"], r["net_r_D"])  # taker costs more than maker-entry

    def test_same_bar_stop_wins(self):
        r = w.simulate_trade(1, 100.0, 99.5, [bar(0, 100, 101.5, 99.0, 100)])
        self.assertEqual(r["kind"], "stop")
        self.assertLess(r["net_r_T"], -1.0)  # -1 R minus costs

    def test_short_mirror(self):
        r = w.simulate_trade(-1, 100.0, 100.5, [bar(0, 100, 100.1, 98.9, 99)])
        self.assertEqual(r["kind"], "target")

    def test_stop_under_40bp_skipped(self):
        self.assertIsNone(w.simulate_trade(1, 100.0, 99.7, [bar(0, 100, 101, 99.9, 100)]))
        self.assertIsNotNone(w.simulate_trade(1, 100.0, 99.6, [bar(0, 100, 100.1, 99.9, 100)]))

    def test_time_stop_at_96_bars(self):
        flat = [bar(i, 100, 100.1, 99.9, 100.05) for i in range(200)]
        r = w.simulate_trade(1, 100.0, 99.5, flat)
        self.assertEqual(r["kind"], "time")
        self.assertAlmostEqual(r["gross_frac"], 0.0005, places=6)

    def test_costs_come_from_fees_module(self):
        c = w.cost_frac("T", "stop")
        self.assertAlmostEqual(c, w.fees.FEES_ALL_TAKER["entry"] + w.fees.FEES_ALL_TAKER["stop"] + w.fees.SLIPPAGE_RT_S13)


class EventTests(unittest.TestCase):
    def day(self, closes, start_h=8):
        return {w.ax.day_of(ms(start_h)): [bar(ms(start_h) + 900000 * i, c, c + 0.2, c - 0.2, c) for i, c in enumerate(closes)]}

    def test_four_closes_above_vah_long(self):
        db = self.day([99, 101, 101.5, 101.2, 101.4, 102])
        d = next(iter(db))
        ev = w.find_events(db, d, [("VAH", 100.0, "resistance"), ("VAL", 90.0, "support")], lambda x: True)
        self.assertEqual(len(ev), 1)
        direction, j, k, stop = ev[0]
        self.assertEqual((direction, j, k), (1, 1, 4))
        self.assertAlmostEqual(stop, 100.0)  # VAH is lower than the window lows (100.8..)

    def test_bias_blocks_event(self):
        db = self.day([101, 101.5, 101.2, 101.4])
        d = next(iter(db))
        ev = w.find_events(db, d, [("VAH", 100.0, "resistance")], lambda x: False)
        self.assertEqual(ev, [])

    def test_three_closes_not_enough_and_late_block_excluded(self):
        db = self.day([101, 101.5, 101.2, 99])
        d = next(iter(db))
        self.assertEqual(w.find_events(db, d, [("VAH", 100.0, "resistance")], lambda x: True), [])
        db2 = self.day([101, 101.5, 101.2, 101.4], start_h=22)
        d2 = next(iter(db2))
        self.assertEqual(w.find_events(db2, d2, [("VAH", 100.0, "resistance")], lambda x: True), [])

    def test_bias_needs_D_and_W(self):
        self.assertTrue(w.bias_fn({"D": 1, "W": 1})(1))
        self.assertFalse(w.bias_fn({"D": 1, "W": -1})(1))
        self.assertFalse(w.bias_fn({"D": 1})(1))

    def test_block_of(self):
        self.assertEqual([w.block_of(ms(h)) for h in (3, 9, 15, 22)], ["asia", "london", "ny", "late"])


class VerdictTests(unittest.TestCase):
    def test_small_n_inconclusive_never_pass(self):
        self.assertTrue(w.verdict(dict(n=50, net_T=1.0, se_T=0.1, net_D=1.0, ctrl_ge=0.0)).startswith("INCONCLUSIVE"))

    def test_fail_and_candidate(self):
        self.assertEqual(w.verdict(dict(n=500, net_T=-0.1, se_T=0.05, net_D=0.1, ctrl_ge=0.5)), "FAIL")
        self.assertEqual(w.verdict(dict(n=500, net_T=0.2, se_T=0.05, net_D=0.3, ctrl_ge=0.01)), "EDGE-CANDIDATE")
        self.assertEqual(w.verdict(dict(n=500, net_T=0.2, se_T=0.05, net_D=0.3, ctrl_ge=0.2)), "FAIL")


if __name__ == "__main__":
    unittest.main()
