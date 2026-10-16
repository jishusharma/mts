"""Tests for live_levels_confluence (W2a): point-in-time levels, first touch, Q79 side, restart determinism, DEV counts."""
import collections
import csv
import random
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.alerts import live_levels_confluence as m

DAY = m.DAY_MS
D0 = 20000 * DAY          # a Monday 00:00 UTC? (epoch day 20000 % 7 == 3; irrelevant: tests use relative days)
RESEARCH = Path(__file__).resolve().parents[3] / "research" / "levels_confluence_2026-10-14" / "event_table.csv"
KLINES = Path("F:/MTS/data/tom_raw")
DEV_FIRST_DAY, DEV_LAST_DAY = 20058, 20178   # 2024-12-01 .. 2025-03-31 (LC1 DEV window)


def bar(t, o, h, l, c, v=1.0):
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": v, "tbv": v / 2}


def walk(days, seed=7, start_day=20000):
    """Deterministic random-walk 1m bars, `days` full UTC days."""
    rng = random.Random(seed)
    px, out = 50000.0, []
    for k in range(days * 1440):
        o = px
        px += rng.uniform(-25, 25)
        out.append(bar((start_day * 1440 + k) * 60000, o, max(o, px) + rng.uniform(0, 8),
                       min(o, px) - rng.uniform(0, 8), px, rng.uniform(1, 5)))
    return out


def two_day(day1_bars):
    """Day 0: range 100..200 (flat 150 bars with one 200 high and one 100 low); then caller's day-1 bars."""
    day0 = [bar(D0 + i * 60000, 150, 150, 150, 150) for i in range(1440)]
    day0[10] = bar(D0 + 10 * 60000, 150, 200, 150, 150)
    day0[20] = bar(D0 + 20 * 60000, 150, 150, 100, 150)
    return day0 + day1_bars


class TestLevels(unittest.TestCase):
    def test_prior_day_level_absent_before_close(self):
        bars = two_day([])
        self.assertEqual(m.build_levels(m._by_day(bars), D0 // DAY), [])          # day 0: no prior day at all
        self.assertEqual(m.detect_events(bars), [])
        lv = {x["family"]: x["price"] for x in m.build_levels(m._by_day(bars), D0 // DAY + 1)}
        self.assertEqual((lv["prior_day_high"], lv["prior_day_low"]), (200.0, 100.0))

    def test_levels_ignore_same_day_bars(self):
        d1 = [bar(D0 + DAY + i * 60000, 150, 151, 149, 150) for i in range(60)]
        a = m.build_levels(m._by_day(two_day(d1)), D0 // DAY + 1)
        d1[30] = bar(D0 + DAY + 30 * 60000, 150, 9999, 1, 150)
        self.assertEqual(a, m.build_levels(m._by_day(two_day(d1)), D0 // DAY + 1))

    def test_no_events_before_level_exists(self):
        # a touch of 200 on day 0 itself is not an event: the level only exists from day 1 00:00
        bars = two_day([])
        self.assertTrue(all(r["day"] != D0 // DAY for r in m.detect_events(bars)))


class TestTouchSide(unittest.TestCase):
    def day1(self, prev_close, touch_close):
        # bar0 opens 150; for prev_close > 200 bar0 gaps there (no touch of 200 before the touch bar)
        b = [bar(D0 + DAY, prev_close, prev_close + 1, prev_close - 1, prev_close) if prev_close > 200 else bar(D0 + DAY, 150, 151, 149, 150), bar(D0 + DAY + 60000, prev_close, prev_close, prev_close, prev_close),
             bar(D0 + DAY + 120000, prev_close, 210, 199, touch_close)]
        return two_day(b)

    def ev200(self, bars):
        return [r for r in m.detect_events(bars) if r["family"] == "prior_day_high" and r["level"] == 200.0]

    def test_side_from_previous_close_not_touch_bar(self):
        below = self.ev200(self.day1(190, 195))      # previous close below, touch bar closes below
        below_up = self.ev200(self.day1(190, 215))   # previous close below, touch bar closes ABOVE: side must not change
        above = self.ev200(self.day1(205, 195))      # previous close above, touch bar closes below
        above_dn = self.ev200(self.day1(205, 202))
        self.assertEqual([r["side"] for r in below], [-1])
        self.assertEqual([r["side"] for r in below_up], [-1])
        self.assertEqual([r["side"] for r in above], [1])
        self.assertEqual([r["side"] for r in above_dn], [1])

    def test_first_touch_only(self):
        bars = self.day1(190, 195) + [bar(D0 + DAY + 180000 + i * 60000, 195, 205, 195, 196) for i in range(5)]
        self.assertEqual(len(self.ev200(bars)), 1)
        self.assertEqual(self.ev200(bars)[0]["t"], D0 + DAY + 120000)

    def test_adapter_shape(self):
        ev = m.levels_confluence_layer(self.day1(190, 195))
        hi = [e for e in ev if e["family"] == "prior_day_high"]
        self.assertEqual(hi[0]["side"], "short")
        self.assertEqual(hi[0]["t"], D0 + DAY + 120000)
        for e in ev:
            self.assertIn(e["side"], ("long", "short"))
            self.assertTrue(e["sampling"])
        self.assertEqual(len({(e["t"], e["event"]) for e in ev}), len(ev))


class TestNoLookAhead(unittest.TestCase):
    def test_truncation_matches_full_run(self):
        bars = walk(16)
        full = m.detect_events(bars)
        self.assertGreater(len(full), 20)
        for cut in (len(bars) - 1, len(bars) - 700, 1440 * 12 + 333, 1440 * 13):
            part = m.detect_events(bars[:cut])
            self.assertEqual(part, [r for r in full if r["t"] <= bars[cut - 1]["t"]], cut)

    def test_future_bars_do_not_change_past_events(self):
        bars = walk(16)
        t_cut = bars[1440 * 14]["t"]
        base = [r for r in m.detect_events(bars) if r["t"] < t_cut]
        mutated = [dict(b) for b in bars]
        for b in mutated[1440 * 14:]:
            b["h"], b["l"], b["c"] = 70000.0, 30000.0, 70000.0
        self.assertEqual(base, [r for r in m.detect_events(mutated) if r["t"] < t_cut])


class TestRestartAndInput(unittest.TestCase):
    def test_restart_determinism_and_window(self):
        bars = walk(18)
        a = m.levels_confluence_layer(bars)
        self.assertEqual(a, m.levels_confluence_layer([dict(b) for b in bars]))
        shuffled = bars[:] ; random.Random(1).shuffle(shuffled)
        self.assertEqual(a, m.levels_confluence_layer(shuffled + bars[:50]))     # order / duplicate bars irrelevant
        window = [b for b in bars if b["t"] >= bars[-1]["t"] // DAY * DAY - 14 * DAY]
        self.assertEqual(a, m.levels_confluence_layer(window))                    # 14-day window restart gives same output

    def test_empty_and_nan(self):
        self.assertEqual(m.levels_confluence_layer([]), [])
        self.assertEqual(m.levels_confluence_layer(None), [])
        self.assertEqual(m.detect_events([]), [])
        nan = float("nan")
        bars = walk(3)
        bad = [dict(b) for b in bars]
        bad[500]["h"] = nan
        bad[900]["c"] = nan
        bad[1000] = {"t": bars[1000]["t"]}
        self.assertIsInstance(m.levels_confluence_layer(bad), list)
        self.assertEqual(m.levels_confluence_layer([{"t": 0, "o": nan, "h": nan, "l": nan, "c": nan, "v": nan}]), [])


@unittest.skipUnless(RESEARCH.exists() and (KLINES / "klines").exists(), "DEV klines or research event_table.csv absent")
class TestDevCounts(unittest.TestCase):
    def test_counts_match_research_event_table(self):
        from MyTradingSys.backtest.bt.bt_data import load_klines
        bars = load_klines(str(KLINES), "klines", 1732147200000, 1743465600000)   # 2024-11-21 .. 2025-03-31 (DEV + seed)
        ours = collections.Counter((r["day"], r["family"]) for r in m.detect_events(bars))
        with RESEARCH.open(newline="", encoding="utf-8") as f:                      # day/family columns only: counts, no outcomes
            ref = collections.Counter((int(x["day"]), x["family"]) for x in csv.DictReader(f))
        self.assertEqual(ours, ref)
        dev = sum(n for (d, _), n in ours.items() if DEV_FIRST_DAY <= d <= DEV_LAST_DAY)
        self.assertEqual(dev, sum(n for (d, _), n in ref.items() if DEV_FIRST_DAY <= d <= DEV_LAST_DAY))
        self.assertEqual(sum(ours.values()), 1278)


if __name__ == "__main__":
    unittest.main()
