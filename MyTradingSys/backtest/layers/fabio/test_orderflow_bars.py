import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from MyTradingSys.backtest.layers.fabio import orderflow_bars as ob

MIN = 60000
# (agg_id, price, qty, first_id, last_id, ts_ms, is_buyer_maker); maker=True -> SELL aggressor
TRADES = [
    (1, 100.0, 1.0, 1, 1, 0 * MIN + 1000, False),
    (2, 104.0, 3.0, 2, 4, 0 * MIN + 2000, True),
    (3, 112.0, 2.0, 5, 5, 0 * MIN + 3000, False),
    (4, 101.0, 0.5, 6, 6, 0 * MIN + 4000, True),
    (5, 200.0, 2.5, 7, 7, 1 * MIN + 5000, False),
]


class TestAggregate(unittest.TestCase):
    def setUp(self):
        self.rows = ob.aggregate_day(TRADES, thr99=2.5, thr999=3.0, thr_days=7)

    def test_minute_zero_hand_computed(self):
        r = self.rows[0]
        self.assertEqual(r["t"], 0)
        self.assertEqual((r["o"], r["h"], r["l"], r["c"]), (100.0, 112.0, 100.0, 101.0))
        self.assertEqual((r["buy_vol"], r["sell_vol"], r["delta"], r["cvd_day"]), (3.0, 3.5, -0.5, -0.5))
        self.assertEqual((r["n_agg"], r["n_trades"], r["max_trade"]), (4, 6, 3.0))
        # big99 = qty >= 2.5 -> only the 3.0 sell; big999 = qty >= 3.0 -> same
        self.assertEqual((r["b99_buy_vol"], r["b99_sell_vol"], r["b99_buy_n"], r["b99_sell_n"]), (0.0, 3.0, 0, 1))
        self.assertEqual((r["b999_buy_vol"], r["b999_sell_vol"], r["b999_buy_n"], r["b999_sell_n"]), (0.0, 3.0, 0, 1))
        # footprint 10 USD bins: [100,110) buy 1 / sell 3.5 (POC), [110,120) buy 2
        self.assertEqual((r["poc_price"], r["poc_delta"], r["poc_vol"]), (100.0, -2.5, 4.5))
        self.assertEqual((r["thr99"], r["thr999"], r["thr_days"]), (2.5, 3.0, 7))

    def test_minute_one_and_cvd_carry(self):
        r = self.rows[1]
        self.assertEqual(r["t"], MIN)
        self.assertEqual((r["buy_vol"], r["sell_vol"], r["delta"], r["cvd_day"]), (2.5, 0.0, 2.5, 2.0))
        self.assertEqual((r["b99_buy_vol"], r["b99_buy_n"], r["b999_buy_n"]), (2.5, 1, 0))
        self.assertEqual((r["poc_price"], r["poc_delta"]), (200.0, 2.5))

    def test_poc_tie_goes_to_lower_bin(self):
        tr = [(1, 105.0, 1.0, 1, 1, 0, False), (2, 115.0, 1.0, 2, 2, 1, True)]
        r = ob.aggregate_day(tr, 9, 9)[0]
        self.assertEqual((r["poc_price"], r["poc_delta"]), (100.0, 1.0))

    def test_full_footprint_column(self):
        self.assertEqual(ob.parse_fp(self.rows[0]["fp"]), [(100.0, 1.0, 3.5), (110.0, 2.0, 0.0)])
        self.assertEqual(ob.parse_fp(self.rows[1]["fp"]), [(200.0, 2.5, 0.0)])

    def test_delta_identity(self):
        for r in self.rows:
            self.assertAlmostEqual(r["delta"], r["buy_vol"] - r["sell_vol"])


class TestHistAndThresholds(unittest.TestCase):
    def test_bin_edges(self):
        self.assertEqual(ob.qty_bin(1.0), 300)
        self.assertEqual(ob.qty_bin(10.0), 400)
        self.assertEqual(ob.bin_lower(300), 1.0)

    def test_percentile_threshold(self):
        h = {300: 99, 400: 1}  # 99 trades of qty 1, one of qty 10
        self.assertEqual(ob.threshold_from_hist(h, 0.99), 1.0)
        self.assertEqual(ob.threshold_from_hist(h, 0.995), 10.0)
        with self.assertRaises(ValueError):
            ob.threshold_from_hist({}, 0.99)

    def test_rolling_is_causal_and_falls_back_to_own_day(self):
        with tempfile.TemporaryDirectory() as td:
            hd = Path(td)
            day = date(2026, 8, 10)
            own = {500: 10}
            t99, t999, n = ob.rolling_thresholds(hd, day, own)
            self.assertEqual(n, 0)
            self.assertAlmostEqual(t99, ob.bin_lower(500))
            # prior day (D-1) counts, the day itself and D-31 must not
            (hd / "2026-08-09.json").write_text(json.dumps({"300": 5}))
            (hd / "2026-08-10.json").write_text(json.dumps({"700": 999}))
            (hd / "2026-07-10.json").write_text(json.dumps({"700": 999}))
            t99, t999, n = ob.rolling_thresholds(hd, day, own)
            self.assertEqual(n, 1)
            self.assertAlmostEqual(t99, 1.0)
            self.assertAlmostEqual(t999, 1.0)


class TestIO(unittest.TestCase):
    def test_parse_header_and_microseconds(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.csv"
            p.write_text("agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker\n"
                         "5,100.5,0.25,10,12,1700000000000,true\n"
                         "6,100.6,0.5,13,13,1700000000000000,false\n", newline="")
            rows = list(ob.parse_agg_csv(p))
            self.assertEqual(rows[0], (5, 100.5, 0.25, 10, 12, 1700000000000, True))
            self.assertEqual(rows[1][5], 1700000000000)
            self.assertFalse(rows[1][6])

    def test_write_load_roundtrip_stitches_cvd(self):
        with tempfile.TemporaryDirectory() as td:
            d1 = ob.aggregate_day(TRADES, 2.5, 3.0)
            ob.write_rows(Path(td) / "2026-08-01.csv.gz", d1)
            ob.write_rows(Path(td) / "2026-08-02.csv.gz", d1)
            bars = ob.load_days(td)
            self.assertEqual(len(bars), 4)
            self.assertEqual(bars[0]["t"], 0)
            self.assertAlmostEqual(bars[1]["cvd"], 2.0)
            self.assertAlmostEqual(bars[2]["cvd"], 2.0 - 0.5)   # day 2 restarts at its own cvd_day, offset by carry 2.0
            self.assertAlmostEqual(bars[3]["cvd"], 4.0)
            self.assertIsInstance(bars[0]["n_agg"], int)


if __name__ == "__main__":
    unittest.main()
