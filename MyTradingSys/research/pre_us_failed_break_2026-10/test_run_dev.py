"""Tests for run_dev.py (fail before run_dev.py exists). Hand values are written here from fees.py, not read from the code under test."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from MyTradingSys.backtest import fees  # noqa: E402

_sp = importlib.util.spec_from_file_location("run_dev_under_test", HERE / "run_dev.py")
rd = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(rd)

DAYMIN = 1440
TS0 = rd.TS0


def flat_days(ndays):
    """Every hour: high 100.5, low 99.5, open and close 100 (hourly TR = 1.0, ATR = 1.0)."""
    O = np.full(ndays * DAYMIN, 100.0)
    C = O.copy()
    H = np.full(ndays * DAYMIN, 100.0)
    L = np.full(ndays * DAYMIN, 100.0)
    for k in range(ndays * 24):
        H[k * 60] = 100.5
        L[k * 60 + 1] = 99.5
    return {"O": O, "H": H, "L": L, "C": C}


def day7_failed_break(A, d=7, hit_low=98.4, extra=None):
    d0 = d * DAYMIN
    b = d0 + 8 * 60 + 10                 # 08:10 break bar: high 101.0 (> PDH 100.5 + 0.1 ATR), close 99.9 (< PDH)
    A["H"][b], A["C"][b] = 101.0, 99.9
    A["O"][b + 1] = 100.0               # entry bar open
    j = b + 6
    A["L"][j] = hit_low                 # target 100 - 1.5 ATR = 98.5, trade-through needs low <= 98.4
    if extra:
        extra(A, b)
    return b


class LoaderGuard(unittest.TestCase):
    def test_loader_refuses_bar_dated_2024_07_01(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.csv"
            p.write_text("open_time,open,high,low,close\n1719792000000,1,2,0.5,1.5\n", encoding="utf-8")   # 2024-07-01 00:00 UTC
            with self.assertRaises(ValueError):
                rd.load_dev([p])

    def test_loader_accepts_last_dev_minute(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.csv"
            p.write_text("open_time,open,high,low,close\n1719791940000,1,2,0.5,1.5\n", encoding="utf-8")   # 2024-06-30 23:59
            A = rd.load_dev([p])
            self.assertEqual(A["C"][-1], 1.5)


class OneDayFixture(unittest.TestCase):
    def run_it(self, funding, **kw):
        A = flat_days(9)
        day7_failed_break(A, **kw)
        return rd.run(A, funding, ndays=9, first_day=5)

    def test_one_episode_net_equals_hand_value(self):
        r = self.run_it([(TS0 + 7 * 86400000 + 8 * 3600000, 0.0001)])          # settlement 08:00 is before the 08:11 entry: not held across
        self.assertEqual(len(r["episodes"]), 1)
        e = r["episodes"][0]
        self.assertEqual(e["exit"], "target")
        self.assertEqual(e["n_tr"], 1)
        gross = (100.0 - 98.5) / 100.0 * 1e4                                    # 150 bps on the tranche
        cost = (fees.BINANCE_TAKER * 1e4 + 2.0) + fees.BINANCE_MAKER * 1e4      # taker in + 2 bp slip, maker target out
        hand = 0.25 * (gross - cost)                                            # 4 tranches, one filled, K = 1
        self.assertAlmostEqual(e["net_bps"], hand, places=6)
        self.assertAlmostEqual(hand, 35.25, places=6)

    def test_no_fill_on_touch(self):
        """Tranche 2 limit is 100.5; a bar whose high only touches 100.5 does not fill it (needs 100.6)."""
        def touch(A, b):
            A["H"][b + 3] = 100.5
        r = self.run_it([(0, 0.0)], extra=touch)
        self.assertEqual(r["episodes"][0]["n_tr"], 1)

    def test_trade_through_fills_tranche_two(self):
        def through(A, b):
            A["H"][b + 3] = 100.6
        r = self.run_it([(0, 0.0)], extra=through)
        e = r["episodes"][0]
        self.assertEqual(e["n_tr"], 2)
        gross = 0.25 * (100.0 - 98.5) / 100.0 * 1e4 + 0.25 * (100.5 - 98.5) / 100.5 * 1e4
        cost = 0.25 * ((fees.BINANCE_TAKER * 1e4 + 2.0) + fees.BINANCE_MAKER * 1e4) + 0.25 * (2 * fees.BINANCE_MAKER * 1e4)
        self.assertAlmostEqual(e["net_bps"], gross - cost, places=6)

    def test_gap_through_target_fills_at_open(self):
        def gap(A, b):
            A["O"][b + 4] = 97.0
            A["L"][b + 4] = 96.0
            A["L"][b + 6] = 100.0
        r = self.run_it([(0, 0.0)], hit_low=100.0, extra=gap)
        e = r["episodes"][0]
        self.assertEqual(e["exit"], "target")
        self.assertEqual(e["exit_price"], 97.0)

    def test_time_cap_taker_exit_and_funding_straddle(self):
        """No target hit: closed at the 13:00 open, taker + 2 bp slip. Funding: settlement 16:00 is after the cap -> none; a 08:11..13:00 span has none."""
        A = flat_days(9)
        day7_failed_break(A, hit_low=99.5)
        r = rd.run(A, [(TS0 + 7 * 86400000 + 16 * 3600000, 0.0005)], ndays=9, first_day=5)
        e = r["episodes"][0]
        self.assertEqual(e["exit"], "cap")
        self.assertEqual(e["fund_bps"], 0.0)
        gross = 0.0                                                             # entry 100, cap open 100
        cost = 0.25 * 2 * (fees.BINANCE_TAKER * 1e4 + 2.0)
        self.assertAlmostEqual(e["net_bps"], gross - cost, places=6)

    def test_funding_booked_when_held_across_settlement(self):
        """Settlement 10:00 between entry 08:11 and cap 13:00; short receives a positive rate: net rises by 0.25 * rate * 1e4 bps."""
        A = flat_days(9)
        day7_failed_break(A, hit_low=99.5)
        base = rd.run(A, [(0, 0.0)], ndays=9, first_day=5)["episodes"][0]["net_bps"]
        r = rd.run(A, [(TS0 + 7 * 86400000 + 10 * 3600000, 0.0004)], ndays=9, first_day=5)["episodes"][0]
        self.assertAlmostEqual(r["net_bps"] - base, 0.25 * 0.0004 * 1e4, places=6)

    def test_no_signal_without_failure(self):
        A = flat_days(9)
        b = 7 * DAYMIN + 8 * 60 + 10
        for k in range(b, 7 * DAYMIN + 13 * 60):
            A["H"][k], A["C"][k] = 101.0, 101.0              # breaks and holds above the level
        r = rd.run(A, [(0, 0.0)], ndays=9, first_day=5)
        self.assertEqual(r["episodes"], [])

    def test_dead_level_no_signal(self):
        A = flat_days(9)
        b = 7 * DAYMIN + 8 * 60 + 10
        A["H"][b], A["C"][b] = 103.0, 99.9                   # excursion 2.5 ATR > 1.5 ATR: dead
        r = rd.run(A, [(0, 0.0)], ndays=9, first_day=5)
        self.assertEqual(r["episodes"], [])

    def test_signal_outside_window_ignored(self):
        A = flat_days(9)
        b = 7 * DAYMIN + 14 * 60                             # 14:00 is outside the 07-13 window
        A["H"][b], A["C"][b] = 101.0, 99.9
        r = rd.run(A, [(0, 0.0)], ndays=9, first_day=5)
        self.assertEqual(r["episodes"], [])


if __name__ == "__main__":
    unittest.main()
