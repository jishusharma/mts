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

if __name__ == "__main__":
    unittest.main()
