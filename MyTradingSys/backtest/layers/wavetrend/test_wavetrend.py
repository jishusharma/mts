"""WaveTrend observation tests. Expected numbers come from FORMULAS.md section 20 (hand values) and from
golden_wt_btcusdt_1h_dev_2022-01.csv (make_golden.py, pandas), never from wavetrend.py output."""
import csv
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import wavetrend as wt  # noqa: E402

HERE = Path(__file__).parent
H = 3600000


def flat_bars(prices, tf=H, t0=0):
    return [(t0 + i * tf, p, p, p) for i, p in enumerate(prices)]


def load_bars():
    with open(HERE / "fixture_btcusdt_1h_dev_2022-01.csv", newline="") as f:
        return [(int(r["open_time"]), float(r["high"]), float(r["low"]), float(r["close"])) for r in csv.DictReader(f)]


def load_golden():
    with open(HERE / "golden_wt_btcusdt_1h_dev_2022-01.csv", newline="") as f:
        return [(float(r["wt1"]) if r["wt1"] else math.nan, float(r["wt2"]) if r["wt2"] else math.nan, int(r["event"]))
                for r in csv.DictReader(f)]


class TestGolden(unittest.TestCase):
    def test_values_match_golden_after_warmup(self):
        rows = wt.compute(load_bars(), H)
        gold = load_golden()
        self.assertEqual(len(rows), len(gold))
        for i in range(wt.WARMUP, len(rows)):
            self.assertAlmostEqual(rows[i].wt1, gold[i][0], delta=1e-9, msg=f"wt1 bar {i}")
            self.assertAlmostEqual(rows[i].wt2, gold[i][1], delta=1e-9, msg=f"wt2 bar {i}")

    def test_events_match_golden_after_warmup(self):
        rows = wt.compute(load_bars(), H)
        gold = load_golden()
        got = [r.event for r in rows[wt.WARMUP + 1:]]
        exp = [g[2] for g in gold[wt.WARMUP + 1:]]
        self.assertEqual(got, exp)
        self.assertGreater(sum(1 for e in exp if e), 10)  # the series really contains crosses

    def test_warmup_outputs_are_nan(self):
        rows = wt.compute(load_bars(), H)
        for r in rows[:wt.WARMUP]:
            self.assertTrue(math.isnan(r.wt1) and math.isnan(r.wt2))
            self.assertIsNone(r.zone)
            self.assertEqual(r.event, 0)
        self.assertFalse(math.isnan(rows[wt.WARMUP].wt1))

    def test_available_at_is_bar_close(self):
        rows = wt.compute(load_bars(), H)
        for r in rows:
            self.assertEqual(r.available_at, r.open_time + H)


class TestHandFixtures(unittest.TestCase):
    def test_two_bar_hand_value(self):
        # FORMULAS.md 20.3: ap [10, 12] -> ci[0] NaN (d=0), ci[1] = 5.5/0.015 = 366.6667 = first wt1
        rows = wt.compute(flat_bars([10.0, 12.0]), H, warmup=0)
        self.assertTrue(math.isnan(rows[0].wt1))
        self.assertAlmostEqual(rows[1].wt1, 5.5 / 0.015, delta=1e-9)
        self.assertTrue(math.isnan(rows[1].wt2))

    def test_sma4_hand_values(self):
        self.assertEqual(wt.sma([10, 20, 30, 40, 50], 4)[3:], [25.0, 35.0])
        self.assertTrue(math.isnan(wt.sma([10, 20, 30, 40], 4)[2]))

    def test_flat_input_is_nan_never_zero_or_inf(self):
        rows = wt.compute(flat_bars([100.0] * 60), H, warmup=0)
        for r in rows:
            self.assertTrue(math.isnan(r.wt1) and math.isnan(r.wt2))
            self.assertEqual(r.event, 0)
            self.assertIsNone(r.zone)

    def test_nan_bar_drops_state_and_warms_up_again(self):
        bars = load_bars()[:260]
        bars[230] = (bars[230][0], math.nan, math.nan, math.nan)
        rows = wt.compute(bars, H)
        self.assertTrue(all(math.isnan(r.wt1) for r in rows[230:230 + wt.WARMUP]))
        self.assertFalse(math.isnan(rows[229].wt1))

    def test_time_gap_treated_as_missing(self):
        bars = load_bars()[:260]
        shifted = bars[:230] + [(t + 3 * H, h, l, c) for t, h, l, c in bars[230:]]  # 3 bars missing at 230
        rows = wt.compute(shifted, H)
        self.assertTrue(math.isnan(rows[230].wt1) and math.isnan(rows[259].wt1))
        self.assertEqual(rows[230].event, 0)

    def test_tie_conventions(self):
        sides = lambda *s: wt.cross_events([1.0 * a for a in s], [0.0] * len(s))  # wt1 vs wt2=0 -> side = sign
        self.assertEqual(sides(1, 0, 1), [0, 0, 0])      # above-tie-above: no cross
        self.assertEqual(sides(1, 0, -1), [0, 0, -1])    # through a tie bar: one down-cross, at the first strict bar
        self.assertEqual(sides(-1, 1), [0, 1])           # plain up-cross
        self.assertEqual(sides(-1, 0, 0, 1), [0, 0, 0, 1])  # tie run then move away counts once
        self.assertEqual(sides(1, math.nan, -1), [0, 0, 0])  # NaN resets the side: no event across the hole

    def test_zone_boundaries(self):
        z = wt.zone
        self.assertEqual([z(v) for v in (60, 59.99, 53, 52.99, 0)], ["ob2", "ob1", "ob1", "mid", "mid"])
        self.assertEqual([z(v) for v in (-52.99, -53, -59.99, -60)], ["mid", "os1", "os1", "os2"])
        self.assertIsNone(z(math.nan))


class TestLookAhead(unittest.TestCase):
    def test_planted_future_spike_changes_nothing_before_it(self):
        bars = load_bars()
        base = wt.compute(bars, H)
        k = 300
        spiked = list(bars)
        t, h, l, c = spiked[k]
        spiked[k] = (t, h * 1.5, l, c * 1.4)
        alt = wt.compute(spiked, H)
        for i in range(k):
            for a, b in zip((base[i].wt1, base[i].wt2), (alt[i].wt1, alt[i].wt2)):
                self.assertTrue(a == b or (math.isnan(a) and math.isnan(b)), f"bar {i} moved")
            self.assertEqual(base[i].event, alt[i].event)
        self.assertNotEqual(base[k].wt1, alt[k].wt1)  # the spike is visible at its own bar

    def test_htf_uses_last_closed_bar_only(self):
        # 4h bars open at 0,4h,8h...; an hourly bar opening 10:00 closes 11:00 -> 4h bar [04:00,08:00) is the last closed
        self.assertEqual(wt.htf_index(11 * H, 4 * H, [0, 4 * H, 8 * H]), 1)
        # hourly bar opening 11:00 closes 12:00 == close of 4h bar [08:00,12:00): usable
        self.assertEqual(wt.htf_index(12 * H, 4 * H, [0, 4 * H, 8 * H]), 2)
        # before any HTF bar closed
        self.assertIsNone(wt.htf_index(3 * H, 4 * H, [0, 4 * H]))


if __name__ == "__main__":
    unittest.main()
