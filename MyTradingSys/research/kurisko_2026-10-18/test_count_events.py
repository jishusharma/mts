"""Tests for count_events.py. Expected numbers are written by hand from FORMULAS.md section 24.5, not read from the module."""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import count_events as ce  # noqa: E402

MIN = 60_000
SMALL = ((2, 1), (3, 1), (4, 1), (5, 1))


def fixture(mirror=False):
    """FORMULAS 24.5: bars 0..5 fall one point each (close = low, high = low + 1), bar 6 = (97, 94.5, 96.5)."""
    hlc = [(100 - i + 1, 100 - i, 100 - i) for i in range(6)] + [(97, 94.5, 96.5)]
    if mirror:
        hlc = [(200 - l, 200 - h, 200 - c) for h, l, c in hlc]
    return [(i * MIN, h, l, c) for i, (h, l, c) in enumerate(hlc)]


class Events(unittest.TestCase):
    def test_long_event_and_stop(self):
        # hand: event at t=6, episode bar s=4, min low over bars 4..6 = 94.5, close 96.5 -> (96.5-94.5)/96.5 = 207.2539 bp
        rows = ce.count_events(fixture(), MIN, "stoch", SMALL)
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r["side"], r["t"], r["episode_start"]), ("long", 6, 4))
        self.assertAlmostEqual(r["stop_bp"], 207.25388601, places=5)

    def test_short_mirror_and_stop(self):
        # hand: h' = 200-l, so max high over 4..6 = 105.5, close 103.5 -> 2/103.5 = 193.2367 bp
        rows = ce.count_events(fixture(True), MIN, "stoch", SMALL)
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["side"], rows[0]["t"]), ("short", 6))
        self.assertAlmostEqual(rows[0]["stop_bp"], 193.23671498, places=5)

    def test_future_spike_moves_no_earlier_count(self):
        base = fixture()
        spiked = base + [(7 * MIN, 500.0, 1.0, 250.0)]
        a = [(r["t"], r["side"], round(r["stop_bp"], 9)) for r in ce.count_events(base, MIN, "stoch", SMALL)]
        b = [(r["t"], r["side"], round(r["stop_bp"], 9)) for r in ce.count_events(spiked, MIN, "stoch", SMALL) if r["t"] < 7]
        self.assertEqual(a, b)
        self.assertEqual(a, [(6, "long", 207.25388601)])

    def test_event_days_are_distinct_utc_days(self):
        rows = [{"side": "long", "t_close_ms": 10 * MIN, "stop_bp": 5.0},
                {"side": "long", "t_close_ms": 20 * MIN, "stop_bp": 7.0},
                {"side": "long", "t_close_ms": 86_400_000 + MIN, "stop_bp": 9.0},
                {"side": "short", "t_close_ms": 30 * MIN, "stop_bp": 100.0}]
        s = ce.summarise(rows, "long")
        self.assertEqual((s["events"], s["event_days"], s["median_stop_bp"]), (3, 2, 7.0))
        self.assertEqual(s["share_stop_ge_fee"], 0.0)


class MeanCost(unittest.TestCase):
    def test_mean_cost_is_mean_of_fee_over_stop_not_over_median(self):
        # hand: stops 5, 7, 9 bp; fee 14 bp -> (14/5 + 14/7 + 14/9) / 3 = (2.8 + 2 + 1.5556) / 3 = 2.1185 R
        # (14 / median 7 = 2.0 would understate it)
        rows = [{"side": "long", "t_close_ms": i * 60_000, "stop_bp": s} for i, s in enumerate((5.0, 7.0, 9.0))]
        s = ce.summarise(rows, "long")
        self.assertAlmostEqual(s["mean_cost_R"], 2.1185, places=3)
        self.assertEqual(s["sd_daily_mean_R"], "n/a: no outcome")
        self.assertTrue(s["mean_cost_R"] > ce.FEE_BP / s["median_stop_bp"])


class Loader(unittest.TestCase):
    def _csv(self, d, t_ms):
        p = Path(d) / "x.csv"
        p.write_text("open_time,open,high,low,close,volume\n%d,1,2,0.5,1.5,3\n" % t_ms, newline="\n")
        return p

    def test_refuses_bar_at_or_after_cutoff(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                ce.load_1m([self._csv(d, ce.CUTOFF_MS)], check_sha=False)

    def test_accepts_last_dev_bar(self):
        with tempfile.TemporaryDirectory() as d:
            bars = ce.load_1m([self._csv(d, ce.CUTOFF_MS - MIN)], check_sha=False)
            self.assertEqual(len(bars), 1)

    def test_resample_5m_drops_incomplete_bucket(self):
        # hand: minutes 0..4 full -> one bar (o first, h max, l min, c last); minutes 5..7 only 3 bars -> dropped
        one = [(i * MIN, 10 + i, 9 + i, 9.5 + i) for i in range(8)]
        b5 = ce.to_5m(one)
        self.assertEqual(b5, [(0, 14, 9, 13.5)])


if __name__ == "__main__":
    unittest.main()
