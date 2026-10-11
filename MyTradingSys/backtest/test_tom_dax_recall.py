import sys
sys.dont_write_bytecode = True
"""Tests for tom_dax_recall.py. Expected numbers are computed by hand from the rules in its docstring."""
import datetime as dt
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tom_dax_recall as R  # noqa: E402


def cand(side, zone_price, proof, rank=1, gross=2.0, net=2.0):
    return {"rank": rank, "direction": side, "zone": {"name": "z", "price": zone_price},
            "math": {"tier": "trigger_ready", "gross_rr": gross, "net_rr": net}, "score": {"proof_count": proof}}


class TestBasis(unittest.TestCase):
    def test_fair_value(self):
        # 24229 * 0.02 * 38 / 365 = 50.449... (2026-05-12 -> 2026-06-19 is 38 days)
        self.assertAlmostEqual(R.basis(24229, dt.date(2026, 5, 12), "M6"), 50.4495, places=3)


class TestFindEntry(unittest.TestCase):
    def test_nearest_touch(self):
        t = dt.datetime(2026, 5, 12, 8, 0, tzinfo=dt.timezone.utc)
        ms = lambda k: int((t + dt.timedelta(minutes=k)).timestamp() * 1000)
        bars = {ms(-10): (100, 105, 99, 101), ms(-2): (100, 101, 99, 100), ms(3): (100, 104, 99, 100), ms(7): (100, 106, 99, 100)}
        self.assertEqual(R.find_entry(bars, t, "short", 104), t + dt.timedelta(minutes=3))   # -10 also touches but is farther
        self.assertEqual(R.find_entry(bars, t, "long", 99), t + dt.timedelta(minutes=-2))
        self.assertIsNone(R.find_entry(bars, t, "short", 200))


class TestClassify(unittest.TestCase):
    def snap(self, cands):
        return {"timestamp_utc": "2026-05-12T08:00:00Z", "current_price": 100.0, "setup_candidates": cands,
                "conditions": {}, "daily_vp": {}, "structure": {}}

    def test_rule_miss_wrong_side_or_far(self):
        cls, zone, *_ = R.classify([self.snap([cand("long", 100.0, 4)]), self.snap([cand("short", 120.0, 4)])], "short", 100.0, 1.0)
        self.assertEqual((cls, zone), ("MISS-RULE", False))

    def test_proof_miss(self):
        cls, zone, sc, sd, best = R.classify([self.snap([cand("short", 100.5, 1)])], "short", 100.0, 1.0)
        self.assertEqual((cls, zone, best["proof"]), ("MISS-PROOF", True, 1))


if __name__ == "__main__":
    unittest.main()
