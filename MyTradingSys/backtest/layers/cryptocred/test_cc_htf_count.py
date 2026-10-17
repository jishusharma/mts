"""cc_htf_count must reproduce the existing runner's 1h signal count on a fixed fixture."""
import random
import unittest

from MyTradingSys.backtest.layers.cryptocred import cc_htf_count as C
from MyTradingSys.backtest.layers.cryptocred import run_cc_setups as R

MIN = 60000
H = 3600000


def fixture_1m(n_hours=3000, seed=7):
    import math
    rnd = random.Random(seed)
    out, t = [], 1640995200000
    px = 100.0
    for h in range(n_hours):
        target = 100.0 + 12.0 * math.sin(h / 18.0) + rnd.gauss(0, 1.0)
        px += rnd.gauss(0, 0.4)  # hourly open gap so body swings are not tied
        step = (target - px) / 60
        for m in range(60):
            o = px
            px = max(1.0, px + step + rnd.gauss(0, 0.05))
            out.append({"t": t, "o": o, "h": max(o, px) + 0.03, "l": min(o, px) - 0.03, "c": px})
            t += MIN
    return out


class TestHtfCount(unittest.TestCase):
    def test_1h_count_matches_runner(self):
        from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
        import json
        reg = json.loads(R.REGISTRY_PATH.read_text(encoding="utf-8"))
        m1 = fixture_1m()
        h1 = resample(m1, "1h", reg)
        sigs = C.count_signals(h1)
        total = 0
        for name in R.SETUPS:
            res = R.run_setup(name, h1, m1, [], H)
            self.assertEqual(len(sigs[name]), res["n_signals"], name)
            total += res["n_signals"]
        self.assertGreater(total, 0)  # fixture must exercise the setups

    def test_summary_fields(self):
        m1 = fixture_1m()
        from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
        import json
        reg = json.loads(R.REGISTRY_PATH.read_text(encoding="utf-8"))
        h1 = resample(m1, "1h", reg)
        for name, sigs in C.count_signals(h1).items():
            r = C.summarize(name, sigs, m1, H, 2.0)
            self.assertEqual(r["signals"], len(sigs))
            self.assertLessEqual(r["fills"], r["signals"])
            self.assertTrue(r["inconclusive"])  # N < 100 on the small fixture


if __name__ == "__main__":
    unittest.main()
