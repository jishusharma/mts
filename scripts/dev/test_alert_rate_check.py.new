import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import alert_rate_check as a

class T(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(a.classify(0, 10.0), "DEAD")
        self.assertEqual(a.classify(1, 10.0), "DEAD")   # 1 < 20% of 10
        self.assertEqual(a.classify(2, 10.0), "OK")     # exactly 20%
        self.assertEqual(a.classify(0, 1.0), "QUIET")   # too few expected to call dead
        self.assertEqual(a.classify(0, 0.0), "OK")

    def test_aggregate_complete_buckets_only(self):
        m = [{"t": k * 60000, "o": k, "h": k + 1, "l": k - 1, "c": k + .5, "v": 1, "tbv": .5} for k in range(35)]
        out = a.aggregate(m, 15)
        self.assertEqual([b["t"] for b in out], [0, 900000])  # bucket 30..34 incomplete, dropped
        self.assertEqual((out[0]["o"], out[0]["h"], out[0]["l"], out[0]["c"], out[0]["v"]), (0, 15, -1, 14.5, 15))

    def test_tf_map_covers_live_runner_default_tfs(self):
        # 2026-09-30: runner gained 5m, TF_MIN did not -> KeyError crash. Read the default as text (no live import).
        import re
        src = (pathlib.Path(__file__).resolve().parents[2] / "MyTradingSys/backtest/layers/alerts/live_runner_cli.py"
               ).read_text(encoding="utf-8")
        m = re.search(r'"--tfs",\s*default="([^"]+)"', src)
        self.assertIsNotNone(m)
        for tf in m.group(1).split(","):
            self.assertIn(tf, a.TF_MIN)

    # ---- 2026-10-02: 3m and 1d in TF_MIN ------------------------------------------------------------------------
    # Why: ARCHITECTURE_TWO_CORES_2026-10-01.md:39 wants RSI keys 1m,3m,15m,1h,4h,1d; expected_per_day() does
    # aggregate(m1, TF_MIN[tf]) (alert_rate_check.py:88) so a registered 3m/1d layer would KeyError without them.
    # Expected values are hand-computed from the bar construction below, not read from the code under test.
    @staticmethod
    def _bars(ks):
        # 1m bar k opens at k*60000 ms; o=k h=k+1 l=k-1 c=k+0.5 v=1 tbv=0.5
        return [{"t": k * 60000, "o": k, "h": k + 1, "l": k - 1, "c": k + .5, "v": 1, "tbv": .5} for k in ks]

    def test_tf_map_has_3m_and_1d_in_minutes(self):
        self.assertEqual(a.TF_MIN.get("3m"), 3)       # 3 minutes
        self.assertEqual(a.TF_MIN.get("1d"), 1440)    # 24 h * 60 min
        self.assertEqual(a.TF_MIN.get("4h"), 240)     # unchanged

    def test_aggregate_3m_buckets_via_tf_map(self):
        # bars k=0..6 -> buckets {0,1,2} {3,4,5}; k=6 alone is incomplete and dropped
        out = a.aggregate(self._bars(range(7)), a.TF_MIN["3m"])
        self.assertEqual([b["t"] for b in out], [0, 180000])
        # bucket 0: o=0, h=max(1,2,3)=3, l=min(-1,0,1)=-1, c=2.5, v=3, tbv=1.5
        self.assertEqual((out[0]["o"], out[0]["h"], out[0]["l"], out[0]["c"], out[0]["v"], out[0]["tbv"]), (0, 3, -1, 2.5, 3, 1.5))
        # bucket 1: o=3, h=max(4,5,6)=6, l=min(2,3,4)=2, c=5.5, v=3, tbv=1.5
        self.assertEqual((out[1]["o"], out[1]["h"], out[1]["l"], out[1]["c"], out[1]["v"], out[1]["tbv"]), (3, 6, 2, 5.5, 3, 1.5))

    def test_aggregate_1d_bucket_via_tf_map(self):
        # bars k=0..1449: bucket 0 = k 0..1439 (1440 bars, complete); k 1440..1449 = 10 bars, incomplete, dropped
        out = a.aggregate(self._bars(range(1450)), a.TF_MIN["1d"])
        self.assertEqual([b["t"] for b in out], [0])
        # o=0, h=max(k+1)=1440, l=min(k-1)=-1, c=1439.5, v=1440, tbv=1440*0.5=720
        self.assertEqual((out[0]["o"], out[0]["h"], out[0]["l"], out[0]["c"], out[0]["v"], out[0]["tbv"]), (0, 1440, -1, 1439.5, 1440, 720.0))

    def test_aggregate_1d_misaligned_start_yields_no_complete_bucket(self):
        # bars k=100..1539 (1440 bars) straddle the day boundary at k=1440: 1340 bars + 100 bars, both incomplete
        self.assertEqual(a.aggregate(self._bars(range(100, 1540)), a.TF_MIN["1d"]), [])

if __name__ == "__main__":
    unittest.main()
