"""band(): a 100-level book at tick 0.1 does not reach the 1 % band; a book that does reach it is summed the snapshot way."""
import importlib.util
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("depth_band_check", os.path.join(HERE, "depth_band_check.py"))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def book(mid, step, n, qty=1.0):
    bids = [["%.1f" % (mid - step * (i + 1)), str(qty)] for i in range(n)]
    asks = [["%.1f" % (mid + step * (i + 1)), str(qty)] for i in range(n)]
    return {"bids": bids, "asks": asks}


class T(unittest.TestCase):
    def test_tick_book_100_levels_spans_a_hundredth_of_a_percent(self):
        r = M.band(book(78000.0, 0.1, 100))
        self.assertGreater(r["deepest_bid_pct"], -0.02)
        self.assertLess(r["deepest_ask_pct"], 0.02)
        self.assertEqual(r["levels"], 100)

    def test_wide_book_sums_only_inside_one_percent(self):
        d = book(80000.0, 100.0, 20)  # levels 100 USD apart: 8 inside 1 %, 12 outside, each side
        r = M.band(d)
        self.assertAlmostEqual(r["bid_base"], 8.0)
        self.assertAlmostEqual(r["ask_base"], 8.0)
        self.assertLess(r["deepest_bid_pct"], -2.0)

    def test_imbalance_matches_ratio(self):
        d = book(80000.0, 100.0, 8)
        d["bids"] = [[p, "2"] for p, _ in d["bids"]]  # bids twice the asks
        r = M.band(d)
        self.assertAlmostEqual(r["imbalance"], (r["ratio"] - 1) / (r["ratio"] + 1), places=9)
        self.assertGreater(r["imbalance"], 0.3)


if __name__ == "__main__":
    unittest.main()
