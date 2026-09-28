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
            (k / "b.csv").write_text(row(60000, 2) + row(120000, 99) + row(240000, 5))
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
if __name__ == "__main__": unittest.main()
