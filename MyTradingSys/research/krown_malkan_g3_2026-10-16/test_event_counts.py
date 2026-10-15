"""Tests for event_counts.py: the DEV cut, the BBWP breakout detector, de-duplication, the as-of rule and the MDE wiring.
Run: python MyTradingSys/research/krown_malkan_g3_2026-10-16/test_event_counts.py
"""
import csv
import math
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import event_counts as ec  # noqa: E402
from MyTradingSys.backtest.power_mde import power_mde  # noqa: E402


def ms(y, m, d):
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)


class TestDevCut(unittest.TestCase):
    def test_bars_from_2024_07_01_never_loaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x.csv"
            with open(p, "w", newline="\n") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(["open_time_ms", "open", "high", "low", "close"])
                for day in (29, 30):
                    w.writerow([ms(2024, 6, day), 1, 2, 0.5, 1.5])
                for day in (1, 2):
                    w.writerow([ms(2024, 7, day), 9, 9, 9, 9])
            d = ec.load(p, ec.DAY)
        self.assertEqual(len(d["t"]), 2)
        self.assertEqual(max(d["c"]), 1.5)


class TestDedupe(unittest.TestCase):
    def test_close_events_on_one_side_merge_other_side_kept(self):
        ev = [{"i": 10, "side": "long"}, {"i": 12, "side": "long"}, {"i": 17, "side": "long"}, {"i": 11, "side": "short"}]
        out = ec.dedupe(ev, sep=5)
        self.assertEqual([(e["i"], e["side"]) for e in out], [(10, "long"), (11, "short"), (17, "long")])


class TestAsOf(unittest.TestCase):
    def test_uses_only_bars_closed_at_or_before_the_time(self):
        close_t, vals = [10, 20, 30], [1, 2, 3]
        self.assertIsNone(ec.asof_value(close_t, vals, 9))
        self.assertEqual(ec.asof_value(close_t, vals, 20), 2)
        self.assertEqual(ec.asof_value(close_t, vals, 29), 2)


class TestBbwpBreakout(unittest.TestCase):
    def synthetic(self):
        # 300 noisy bars, 60 flat bars (compression), then one big up bar: BBWP low then back above 50, close above the 10-bar range
        c = []
        for i in range(300):
            c.append(100 + 8 * math.sin(i * 0.9) + 5 * math.sin(i * 0.37))
        c += [100.0 + 0.02 * ((-1) ** i) for i in range(60)]
        c.append(130.0)
        t = [ms(2020, 1, 1) + i * ec.DAY for i in range(len(c))]
        return {"t": t, "o": c[:], "h": [x + 0.05 for x in c], "l": [x - 0.05 for x in c], "c": c, "step": ec.DAY}

    def test_flat_then_jump_gives_one_long_event_at_the_jump(self):
        d = self.synthetic()
        ev = ec.kr_s8(d, 252, False)
        self.assertEqual([(e["i"], e["side"]) for e in ev], [(360, "long")])
        self.assertGreater(ev[0]["risk_pct"], 0.0)

    def test_noise_only_series_gives_no_event(self):
        d = self.synthetic()
        n = 300
        d = {k: (v[:n] if isinstance(v, list) else v) for k, v in d.items()}
        self.assertEqual(ec.kr_s8(d, 252, False), [])


class TestMde(unittest.TestCase):
    def test_block_equals_power_mde_at_break_even_win_rate(self):
        ev = [{"i": i * 10, "side": "long", "risk_pct": 0.05} for i in range(100)]
        b = ec.mde_block(ev)
        cost_r = ec.FEE_RT / 0.05
        p0 = (1.0 + cost_r) / (ec.RR + 1.0)
        want = power_mde(p0, ec.RR, cost_r, 100)["mde_net_r"]
        self.assertAlmostEqual(b["mde_net_r"], want, places=12)
        self.assertEqual(b["n_eff"], 100)

    def test_fewer_events_means_larger_mde(self):
        mk = lambda n: ec.mde_block([{"i": i, "side": "long", "risk_pct": 0.05} for i in range(n)])["mde_net_r"]
        self.assertGreater(mk(10), mk(100))


if __name__ == "__main__":
    unittest.main()
