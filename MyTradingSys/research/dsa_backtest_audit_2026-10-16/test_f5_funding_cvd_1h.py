"""T09-F5 test: the 1h resample feeds funding_cvd_fade; DEV cut; net R by hand (FORMULAS.md s13).
Run: python -m pytest MyTradingSys/research/dsa_backtest_audit_2026-10-16/test_f5_funding_cvd_1h.py
"""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import f5_funding_cvd_1h as F  # noqa: E402

T0 = 1640995200000  # 2022-01-01 00:00 UTC
H = 3600000
HOUR_CLOSE = [100.0, 101.0, 100.5, 102.0, 100.98, 100.0]


def fixture_1m():
    """6 hours of 1m bars. Every minute of hour h closes at HOUR_CLOSE[h].
    v=60 every minute; tbv=40 in hours 0-2 (cvd +20/min) and 10 in hour 3+ (cvd -40/min)."""
    bars = []
    for h, c in enumerate(HOUR_CLOSE):
        for m in range(60):
            bars.append({"t": T0 + h * H + m * 60000, "o": c, "h": c, "l": c, "c": c, "v": 60.0,
                         "tbv": 40.0 if h < 3 else 10.0})
    return bars


FUNDING = [(T0 - 3 * H, 0.0001), (T0 - 2 * H, 0.0002), (T0 - H, 0.0003), (T0 + 10 * H, 0.0004)]


class TestF5(unittest.TestCase):
    def test_resample_1h_sums_tbv_and_closes(self):
        bars = F.to_tf(fixture_1m(), "1h")
        self.assertEqual(len(bars), 6)
        self.assertEqual(bars[1]["t"] - bars[0]["t"], H)
        self.assertEqual([b["c"] for b in bars], HOUR_CLOSE)
        self.assertEqual(bars[0]["tbv"], 40.0 * 60)
        self.assertEqual(bars[3]["tbv"], 10.0 * 60)

    def test_rule_fires_on_1h_bar_3_short(self):
        # hand: hourly cvd = sum(2*tbv - v): h0 +1200, cum h1 +2400, cum h2 +3600, cum h3 +1200.
        # close[3]=102 > max(101, 100.5) and cvd[3]=1200 < max(2400, 3600) -> bearish;
        # funding pct 1.0 >= 0.95 -> short
        bars = F.to_tf(fixture_1m(), "1h")
        ev = F.events_1h(bars, FUNDING, lookback=3, n=2, hi=0.95, lo=0.05)
        self.assertEqual([(e["i"], e["side"]) for e in ev], [(3, "short")])

    def test_net_r_hand_numbers(self):
        # short, entry 102 at close of bar 3, exit 1 bar later at 100.98: gross = (102-100.98)/102 = 0.01
        # net = 0.01 - 0.0010 fee - 0.0002 slip - 0 funding (no print inside the hold) = 0.0088; R = net/0.01 = 0.88
        bars = F.to_tf(fixture_1m(), "1h")
        ev = F.events_1h(bars, FUNDING, lookback=3, n=2, hi=0.95, lo=0.05)
        tr = F.score(ev, bars, 1, FUNDING)
        self.assertEqual(len(tr), 1)
        self.assertAlmostEqual(tr[0]["net"], 0.0088, places=9)
        self.assertAlmostEqual(tr[0]["r"], 0.88, places=7)

    def test_dev_cut_drops_validation_bars(self):
        b = [{"t": F.DEV_END_MS - 60000}, {"t": F.DEV_END_MS}, {"t": F.DEV_END_MS + 60000}]
        self.assertEqual(F.dev_slice(b), [{"t": F.DEV_END_MS - 60000}])
        self.assertEqual(F.DEV_END_MS, 1719792000000)  # 2024-07-01 00:00 UTC

    def test_ci_and_thinning(self):
        s = F.mean_ci([1.0, 2.0, 3.0, 4.0])
        # mean 2.5, sample sd = sqrt(5/3) = 1.2909944, se = sd/2 = 0.6454972, half = 1.96*se = 1.2651745
        self.assertAlmostEqual(s["mean"], 2.5)
        self.assertAlmostEqual(s["ci"][0], 2.5 - 1.2651745, places=5)
        tr = [{"i": 0}, {"i": 3}, {"i": 5}, {"i": 20}]
        self.assertEqual([t["i"] for t in F.thin(tr, 4)], [0, 5, 20])  # next entry only at i >= prev i + hold


if __name__ == "__main__":
    unittest.main()
