import unittest, tempfile, os
from pathlib import Path
import bt_data as d
H = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"
def row(t, c, v=10, tbv=7): return f"{t},{c},{c+1},{c-1},{c},{v},{t+59999},0,1,{tbv},0,0\n"
class C(unittest.TestCase):
    def test_all(self):
        with tempfile.TemporaryDirectory() as td:
            k = Path(td, "klines"); k.mkdir()
            (k / "a.csv").write_text(H + row(120000, 3) + row(0, 1))
            (k / "b.csv").write_text(row(60000, 2) + row(120000, 3) + row(240000, 5))
            bars = d.load_klines(td)
            self.assertEqual([b["t"] for b in bars], [0, 60000, 120000, 240000])
            self.assertEqual(len({b["t"] for b in bars}), 4)
            self.assertEqual(d.cvd_delta({"v": 10.0, "tbv": 7.0}), 4.0)
            self.assertEqual(d.check_gaps(bars), [(120000, 240000)])
            self.assertEqual([b["t"] for b in d.load_klines(td, start_ms=60000, end_ms=240000)], [60000, 120000])
            m = Path(td, "metrics"); m.mkdir()
            (m / "x.csv").write_text("create_time,symbol,sum_open_interest,sum_open_interest_value,a,b,c,e\n2026-01-01 00:05:00,BTCUSDT,1.5,2.5,0,0,0,0\n")
            ms = d.load_metrics(td); self.assertEqual(ms[0]["t"], 1767225900000); self.assertEqual(ms[0]["oi"], 1.5)
            f = Path(td, "fundingRate"); f.mkdir()
            (f / "y.csv").write_text("calc_time,funding_interval_hours,last_funding_rate\n1000,8,0.0001\n2000,8,0.0002\n")
            fr = d.load_funding(td)
            self.assertEqual(d.funding_rate_at(fr, 500), 0.0); self.assertEqual(d.funding_rate_at(fr, 1500), 0.0001)
def _mk(td, text):
    k = Path(td, "klines"); k.mkdir(exist_ok=True)
    (k / "a.csv").write_text(text)
class Hard(unittest.TestCase):
    def test_micro(self):
        with tempfile.TemporaryDirectory() as td:
            _mk(td, row(1700000000000000, 1) + row(1700000060000000, 2))
            rp = {}
            bars = d.load_klines(td, report=rp)
            self.assertEqual([b["t"] for b in bars], [1700000000000, 1700000060000])
            self.assertEqual(rp["micro"], 2)
    def test_dup_identical(self):
        with tempfile.TemporaryDirectory() as td:
            _mk(td, row(0, 1) + row(0, 1) + row(60000, 2))
            rp = {}
            self.assertEqual(len(d.load_klines(td, report=rp)), 2)
            self.assertEqual(rp["dups"], 1)
    def test_dup_conflicting_raises(self):
        with tempfile.TemporaryDirectory() as td:
            _mk(td, row(0, 1) + row(0, 9))
            with self.assertRaises(ValueError):
                d.load_klines(td)
    def test_gap_reported(self):
        with tempfile.TemporaryDirectory() as td:
            _mk(td, row(0, 1) + row(60000, 2) + row(240000, 3))
            rp = {}
            d.load_klines(td, report=rp)
            self.assertEqual(rp["gaps"], [(60000, 240000)])
    def test_unsorted_warns_counted(self):
        with tempfile.TemporaryDirectory() as td:
            _mk(td, row(120000, 3) + row(0, 1) + row(60000, 2))
            rp = {}
            with self.assertWarns(UserWarning):
                bars = d.load_klines(td, report=rp)
            self.assertEqual([b["t"] for b in bars], [0, 60000, 120000])
            self.assertEqual(rp["unsorted"], 1)
    def test_funding_dir_order_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(FileNotFoundError):
                d.resolve_funding_dir(td)
            with self.assertRaises(FileNotFoundError):
                d.load_funding_strict(td)
            raw = Path(td, "raw", "fundingRate"); raw.mkdir(parents=True)
            rf = Path(td, "raw_fund", "fundingRate"); rf.mkdir(parents=True)
            hdr = "calc_time,funding_interval_hours,last_funding_rate\n"
            (raw / "a.csv").write_text(hdr + "1000,8,0.0005\n")
            (rf / "a.csv").write_text(hdr + "1000,8,0.0001\n2000,8,0.0002\n")
            self.assertEqual(d.resolve_funding_dir(td), rf)
            self.assertEqual(d.load_funding_strict(td), [(1000, 0.0001), (2000, 0.0002)])
            self.assertEqual(d.load_funding_strict(td, end_ms=2000), [(1000, 0.0001)])
    def test_funding_cost_sign_window(self):
        fr = [(1000, 0.0001), (2000, -0.0002), (3000, 0.0003)]
        long_ = d.funding_cost_pct(fr, [999, 1000, 999], [3000, 3000, 1000], [1, 1, 1])
        self.assertTrue(all(abs(a - b) < 1e-12 for a, b in zip(long_, [0.02, 0.01, 0.01])))   # (entry, exit]: entry==settlement excluded
        self.assertAlmostEqual(float(d.funding_cost_pct(fr, 999, 3000, -1)), -0.02)         # short receives
    def test_funding_boundary_jitter(self):
        """Archive calc_time is 1-31 ms after the 8h boundary: snapped to the second, so entry-on-boundary is exempt, exit-on-boundary charged."""
        B = 28800000
        fr = [(B + 5, 0.0001)]
        self.assertAlmostEqual(float(d.funding_cost_pct(fr, B, B + 3600000, 1)), 0.0)    # entry on boundary: not charged
        self.assertAlmostEqual(float(d.funding_cost_pct(fr, B - 3600000, B, 1)), 0.01)   # exit on boundary: charged
        self.assertAlmostEqual(float(d.funding_cost_pct(fr, B - 1000, B + 1000, 1)), 0.01)
if __name__ == "__main__": unittest.main()
