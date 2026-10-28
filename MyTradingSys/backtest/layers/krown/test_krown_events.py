"""Krown events tests: schema, flag default OFF, causality, fire counts, setup mappings. Hand values: FORMULAS.md section 21."""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import krown_core as kc  # noqa: E402
import krown_events as ke  # noqa: E402


def series(n=500, seed=5):
    rng = random.Random(seed)
    px = 100.0
    o, h, l, c, v = [], [], [], [], []
    for i in range(n):
        drift = 0.4 if (i // 90) % 2 == 0 else -0.4
        op = px
        px = max(5.0, px + drift + rng.gauss(0, 2.5))
        hi = max(op, px) + abs(rng.gauss(0, 1.2))
        lo = min(op, px) - abs(rng.gauss(0, 1.2))
        o.append(op)
        h.append(hi)
        l.append(lo)
        c.append(px)
        v.append(1000 * (1 + (3 if rng.random() < 0.06 else 0) + rng.random()))
    return o, h, l, c, v


class TestEvents(unittest.TestCase):
    def test_default_off_and_forced_on(self):
        o, h, l, c, v = series(300)
        self.assertEqual(ke.build_events(o, h, l, c, v), [])
        self.assertIsInstance(ke.build_events(o, h, l, c, v, enabled=True), list)

    def test_schema(self):
        o, h, l, c, v = series()
        ev = ke.build_events(o, h, l, c, v, enabled=True)
        self.assertGreater(len(ev), 0)
        for e in ev:
            self.assertEqual(set(e), {"i", "side", "setup", "tags"})
            self.assertIn(e["side"], ("long", "short"))
            self.assertIn(e["setup"], ke.SETUPS)
            self.assertIsInstance(e["tags"], list)
            self.assertTrue(0 <= e["i"] < len(c))

    def test_runner_compatible(self):
        sys.path.insert(0, str(Path(__file__).parent.parent))
        import runner  # noqa: E402
        o, h, l, c, v = series()
        ev = ke.build_events(o, h, l, c, v, enabled=True)
        out = runner.forward_return_stats(ev, c)
        self.assertIn(1, out)

    def test_causal_prefix_invariance(self):
        o, h, l, c, v = series()
        full = ke.build_events(o, h, l, c, v, enabled=True)
        for t in (180, 260, 399):
            part = ke.build_events(o[:t + 1], h[:t + 1], l[:t + 1], c[:t + 1], v[:t + 1], enabled=True)
            self.assertEqual(part, [e for e in full if e["i"] <= t], t)

    def test_fire_counts(self):
        ev = [{"i": 1, "side": "long", "setup": "S2", "tags": []}, {"i": 5, "side": "short", "setup": "S2", "tags": []},
              {"i": 9, "side": "long", "setup": "S6", "tags": []}]
        got = ke.fire_counts(ev, 100)
        self.assertEqual(got["S2"], {"n": 2, "per_10_bars": 0.2})
        self.assertEqual(got["S6"], {"n": 1, "per_10_bars": 0.1})
        self.assertEqual(got["S1"], {"n": 0, "per_10_bars": 0.0})
        self.assertEqual(ke.over_ceiling(got, 0.1), ["S2"])

    def test_s6_maps_leash(self):
        ev = ke.setup_s6([(5, "long", 4), (9, "short", 3)])
        self.assertEqual(ev, [{"i": 5, "side": "long", "setup": "S6", "tags": ["leash=4"]},
                              {"i": 9, "side": "short", "setup": "S6", "tags": ["leash=3"]}])

    def test_s9_is_a_sell_signal(self):
        ev = ke.setup_s9([7, 20])
        self.assertEqual([(e["i"], e["side"], e["setup"]) for e in ev], [(7, "short", "S9"), (20, "short", "S9")])

    def test_s8_compression_breakout(self):
        # bbwp <= 30 inside the last 5 bars, now > 50 and rising, close breaks the prior 3-bar high
        bbwp = [None, 20, 25, 28, 40, 55, 60]
        c = [10, 10, 10, 10.1, 10.2, 11, 11.5]
        h = [10.2, 10.2, 10.2, 10.3, 10.4, 11.1, 11.6]
        l = [9.8] * 7
        p = dict(kc.load_params(), s8_break_n=3, s8_recent=5)
        ev = ke.setup_s8(bbwp, h, l, c, p)
        self.assertEqual([(e["i"], e["side"]) for e in ev], [(5, "long")])

    def test_s5_cross_with_200_context(self):
        cross = [None, "up", None, "down"]
        c = [10, 10, 10, 10]
        sma200 = [9, 9, 9, 11]
        ev = ke.setup_s5(cross, c, sma200)
        self.assertEqual([(e["i"], e["side"]) for e in ev], [(1, "long"), (3, "short")])
        self.assertEqual(ke.setup_s5(["up", None], [10, 10], [11, 11]), [])  # up-cross below the 200: filter says wait


if __name__ == "__main__":
    unittest.main()
