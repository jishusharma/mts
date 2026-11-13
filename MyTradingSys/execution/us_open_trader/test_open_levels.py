"""test_open_levels.py - offline tests for open_levels.py (fixtures only, no network, no secrets)."""
import datetime as dt
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import open_levels as levels  # noqa: E402

UTC = dt.timezone.utc
DAY = dt.date(2026, 11, 13)
NOW = dt.datetime(2026, 11, 13, 13, 10, tzinfo=UTC)
H, Q = 3_600_000, 900_000


def ms(y, m, d, h=0, mi=0):
    return int(dt.datetime(y, m, d, h, mi, tzinfo=UTC).timestamp() * 1000)


def fake_fetch(interval, start, end):
    """1h: flat 69000 +-10 bars, Europe high 69571 at 09Z and Europe low 68516 at 10Z on DAY.
    15m: 20 bars with range 100, then one bar with range 240 (all closes 69207 -> TR = range), then one still-open
    bar (range 1000) that must be ignored."""
    if interval == "1h":
        out, t = [], start
        while t < min(end, ms(2026, 11, 13, 13)):
            b = [t, 69000.0, 69010.0, 68990.0, 69000.0]
            if t == ms(2026, 11, 13, 9):
                b[2] = 69571.0
            if t == ms(2026, 11, 13, 10):
                b[3] = 68516.0
            out.append(tuple(b))
            t += H
        return out
    t0 = ms(2026, 11, 13, 7, 45)  # 21 closed bars end 13:00; the 22nd opens 13:00 and is still open at 13:10
    rows = [(t0 + i * Q, 69207.0, 69257.0, 69157.0, 69207.0) for i in range(20)]
    rows.append((t0 + 20 * Q, 69207.0, 69327.0, 69087.0, 69207.0))   # range 240
    rows.append((t0 + 21 * Q, 69207.0, 69707.0, 68707.0, 69207.0))   # open bar
    return rows


class AtrTest(unittest.TestCase):
    def test_wilder_by_hand(self):
        # 14 bars of true range 100 -> seed 100; one bar of TR 240 -> (100*13 + 240)/14 = 110
        bars = [(i, 1000, 1050, 950, 1000) for i in range(14)] + [(14, 1000, 1120, 880, 1000)]
        self.assertAlmostEqual(levels.atr(bars), 110.0)
        # one more bar of TR 100 -> (110*13 + 100)/14
        bars.append((15, 1000, 1050, 950, 1000))
        self.assertAlmostEqual(levels.atr(bars), (110 * 13 + 100) / 14)

    def test_gap_counts_in_true_range(self):
        # second bar gaps up: h-l = 10 but |h - prev close| = 60 is the true range
        bars = [(0, 100, 105, 95, 100)] * 1 + [(1, 150, 160, 150, 155)] * 14
        # TRs: 10, 60, then 10 x13 ; seed = mean of first 14 = (10+60+12*10)/14 = 190/14 ; last bar TR 10
        seed = (10 + 60 + 12 * 10) / 14
        self.assertAlmostEqual(levels.atr(bars), (seed * 13 + 10) / 14)

    def test_too_few_bars(self):
        self.assertIsNone(levels.atr([(0, 1, 2, 0, 1)] * 14))


class GatherTest(unittest.TestCase):
    def gather(self, analysts):
        return levels.gather(DAY, NOW, fetch=fake_fetch, analysts=analysts)

    def test_session_levels_atr_and_price(self):
        g = self.gather(lambda now: [])
        by = {l["name"]: l for l in g["levels"]}
        self.assertEqual(by["EU_HIGH"]["price"], 69571.0)
        self.assertEqual(by["EU_LOW"]["price"], 68516.0)
        self.assertEqual(by["EU_HIGH"]["source"], "session")
        self.assertAlmostEqual(g["atr15"], 110.0)   # the open 1000-range bar is excluded
        self.assertEqual(g["price"], 69207.0)
        self.assertGreater(g["atr1h"], 0)
        self.assertEqual([l["price"] for l in g["levels"]], sorted((l["price"] for l in g["levels"]), reverse=True))

    def test_analyst_cluster_added(self):
        rows = [{"level": 70000, "analyst": "A"}, {"level": 70000, "analyst": "B"}, {"level": 70050, "analyst": "C"},
                {"level": 65000, "analyst": "D"}]
        g = self.gather(lambda now: rows)
        an = [l for l in g["levels"] if l["source"] == "analyst"]
        self.assertEqual([l["price"] for l in an], [70000.0])   # 65000 is a single call, dropped
        self.assertIn("3 calls", an[0]["label"])

    def test_analyst_feed_down_still_builds(self):
        def boom(now):
            raise OSError("store missing")
        g = self.gather(boom)
        self.assertTrue(any(l["name"] == "EU_HIGH" for l in g["levels"]))
        self.assertIn("analyst feed unavailable", g["analyst_note"])

    def test_cluster_rules(self):
        rows = [{"level": 68000, "analyst": "K"}, {"level": 68100, "analyst": "J"}, {"level": 69000, "analyst": "B"}]
        cl = levels.analyst_clusters(rows, 69207)
        self.assertEqual(len(cl), 1)
        self.assertEqual(cl[0]["price"], 68050)
        self.assertEqual(cl[0]["calls"], 2)

    def test_too_few_bars_raises(self):
        with self.assertRaises(ValueError):
            levels.gather(DAY, NOW, fetch=lambda i, s, e: [], analysts=lambda n: [])


if __name__ == "__main__":
    unittest.main()
