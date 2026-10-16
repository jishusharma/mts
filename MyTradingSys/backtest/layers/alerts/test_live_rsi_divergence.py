"""Tests for alerts/live_rsi_divergence.py. Expected values come from a hand-built close series (pivots read off
by hand, see FIXTURE comment), not from running the detector; the RSI numbers were checked against the
Wilder definition in the rsi_core docstring."""
import math
import random
import unittest

from MyTradingSys.backtest.layers.alerts import live_rsi_divergence as m

H = 3600000
T0 = 1790000000000 - (1790000000000 % H)

# FIXTURE: 15 bars of 100/101 chop, then a slide to 95 (idx 19), bounce to 99 (idx 22), second slide to 94 (idx 25),
# recovery. Low pivots of the close: idx 19 (95) and idx 25 (94), bars = 25-19+1 = 7 (inside 3..10).
# Wilder RSI(14) at those: 34.52 then 36.75 -> price lower low, RSI higher low = bullish divergence, confirmed by the
# bar after the second pivot = idx 26. High pivots: only idx 22 (one) -> no bearish. Mirror (200 - close) flips RSI to
# 100 - rsi, so the same indices give a bearish divergence.
CLOSES = [100, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100,
          99, 98, 97, 96, 95, 96, 98, 99, 97, 95, 94, 95, 96, 97, 98]


def mk(closes, t0=T0, step=H):
    return [{"t": t0 + i * step, "o": c, "h": c + 0.5, "l": c - 0.5, "c": float(c), "v": 1.0, "tbv": 0.5}
            for i, c in enumerate(closes)]


def walk(seed, n=120):
    r = random.Random(seed)
    p, out = 100.0, []
    for _ in range(n):
        p = max(1.0, p + r.uniform(-2, 2))
        out.append(p)
    return out


class TestRsiDivLive(unittest.TestCase):
    def test_bullish_fixture_long(self):
        ev = m.adapter(mk(CLOSES))
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["t"], e["event"], e["side"], e["bars"], e["chain"]),
                         (T0 + 26 * H, "rsi_div_bull", "long", 7, 1))
        self.assertEqual((e["close_a"], e["close_b"]), (95.0, 94.0))
        self.assertAlmostEqual(e["rsi_a"], 34.52, places=1)
        self.assertAlmostEqual(e["rsi_b"], 36.75, places=1)
        self.assertTrue(e["sampling"])

    def test_bearish_mirror_short(self):
        ev = m.adapter(mk([200 - c for c in CLOSES]))
        self.assertEqual([(e["t"], e["event"], e["side"]) for e in ev], [(T0 + 26 * H, "rsi_div_bear", "short")])

    def test_empty_and_short(self):
        self.assertEqual(m.adapter([]), [])
        self.assertEqual(m.adapter(mk(CLOSES[:14])), [])
        self.assertEqual(m.adapter(mk(CLOSES[:15])), [])

    def test_no_lookahead_truncation_fixture(self):
        bars = mk(CLOSES)
        self.assertEqual(m.adapter(bars[:26]), [])      # confirming bar 26 not yet present
        self.assertEqual(m.adapter(bars[:27]), m.adapter(bars))

    def test_no_lookahead_truncation_random(self):
        for seed in range(8):
            bars = mk(walk(seed))
            full = m.adapter(bars)
            for k in range(0, len(bars) + 1, 7):
                want = [e for e in full if e["t"] <= bars[k - 1]["t"]] if k else []
                self.assertEqual(m.adapter(bars[:k]), want, (seed, k))

    def test_restart_same_output(self):
        bars = mk(walk(3))
        self.assertEqual(m.adapter(bars), m.adapter([dict(b) for b in bars]))

    def test_nan_bar_no_crash_no_event_on_it(self):
        bars = mk(CLOSES)
        bars[5]["c"] = float("nan")
        bars[5]["h"] = float("nan")
        ev = m.adapter(bars)
        self.assertTrue(all(math.isfinite(e["rsi_b"]) for e in ev))
        self.assertNotIn(bars[5]["t"], [e["t"] for e in ev])
        bad = mk(CLOSES)
        for b in bad:
            b["c"] = float("nan")
        self.assertEqual(m.adapter(bad), [])

    def test_side_mapping(self):
        self.assertEqual(m.SIDE, {"bullish": "long", "bearish": "short"})


if __name__ == "__main__":
    unittest.main()
