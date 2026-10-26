"""T093 tests, derived from items/T093 (the spec) and hand-worked numbers, not from the code:
  - buy = taker_buy_volume, sell = volume - taker_buy_volume; imbalance = (buy - sell) / (buy + sell)
  - opens are 1m bars at :00/:15/:30/:45 UTC; entry at that bar's CLOSE; exit at the close W minutes later (W = 240/480/720)
  - gross bp = sign(imbalance) * (exit/entry - 1) * 1e4; net = gross - 10 (taker 0.0005 x 2 legs)
  - a year run counts only opens inside that year; the exit bar may fall in the next year's data
  - the per-year parts, combined, give the same numbers as one run over all years
"""
import csv
import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t093_toc_imbalance_klines as t93

MIN = 60_000
Y2023 = 1_672_531_200_000   # 2023-01-01T00:00Z
Y2024 = 1_704_067_200_000   # 2024-01-01T00:00Z


def write_month_csv(path, rows):
    """rows: (open_time, close, volume, taker_buy_volume); other columns are filler in the Binance kline layout."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count",
                    "taker_buy_volume", "taker_buy_quote_volume", "ignore"])
        for t, c, v, tb in rows:
            w.writerow([t, c, c, c, c, v, t + 59999, v * c, 1, tb, tb * c, 0])


class TestBuySell(unittest.TestCase):
    def test_sell_is_volume_minus_taker_buy_and_imbalance(self):
        buy, sell = t93.buy_sell(np.array([10.0]), np.array([7.0]))
        self.assertEqual((buy[0], sell[0]), (7.0, 3.0))
        self.assertAlmostEqual((buy[0] - sell[0]) / (buy[0] + sell[0]), 0.4)


class TestYearPart(unittest.TestCase):
    def series(self, start, n, buy_share, c0, c_at):
        """n 1m bars from start; every bar has volume 10, taker buy buy_share*10; close = c0, except bars in c_at {minute_index: close}."""
        return [(start + i * MIN, c_at.get(i, c0), 10.0, 10.0 * buy_share) for i in range(n)]

    def test_long_signal_gross_and_net_hand_worked(self):
        # open bar index 0 (2023-01-01 00:00): close 100, buy share 0.7 -> imbalance +0.4 -> long; exit 240 bars later closes 101
        rows = self.series(Y2023, 241, 0.7, 100.0, {240: 101.0})
        d = t93.arrays(rows)
        r = t93.year_trades(d, 240, 2023)
        i0 = list(r["t"]).index(Y2023)
        self.assertAlmostEqual(r["gross"][i0], 100.0, places=6)     # +1 % = 100 bp
        self.assertAlmostEqual(r["gross"][i0] - t93.FEE_BP, 90.0, places=6)

    def test_short_signal_profits_from_a_fall(self):
        rows = self.series(Y2023, 241, 0.3, 100.0, {240: 99.0})       # imbalance -0.4 -> short; price -1 %
        r = t93.year_trades(t93.arrays(rows), 240, 2023)
        i0 = list(r["t"]).index(Y2023)
        self.assertAlmostEqual(r["gross"][i0], 100.0, places=6)

    def test_zero_imbalance_is_skipped_and_missing_exit_is_dropped(self):
        rows = self.series(Y2023, 241, 0.5, 100.0, {})                # buy == sell: no signal
        self.assertEqual(len(t93.year_trades(t93.arrays(rows), 240, 2023)["gross"]), 0)
        rows = self.series(Y2023, 100, 0.7, 100.0, {})                # data ends before any 240-min exit
        self.assertEqual(len(t93.year_trades(t93.arrays(rows), 240, 2023)["gross"]), 0)

    def test_only_opens_inside_the_year_count_but_exit_may_cross_the_year_end(self):
        start = Y2024 - 120 * MIN                                      # 2 h before the year end, 6 h of bars
        rows = self.series(start, 360, 0.7, 100.0, {})
        d = t93.arrays(rows)
        r23 = t93.year_trades(d, 240, 2023)
        r24 = t93.year_trades(d, 240, 2024)
        # opens in 2023 with an exit bar present: those 2023 opens whose +240 bar exists (start..start+119 -> exit start+240..)
        self.assertTrue(len(r23["gross"]) > 0)
        self.assertTrue(all(t < Y2024 for t in r23["t"]))
        self.assertTrue(all(t >= Y2024 for t in r24["t"]))
        # the 2023 open at 22:00 has its exit at 02:00 on 2024-01-01: present, so it must be counted
        self.assertIn(start, list(r23["t"]))


class TestLoaderAndCombine(unittest.TestCase):
    def test_loader_reads_binance_layout_dedups_and_sorts(self):
        with tempfile.TemporaryDirectory() as d:
            write_month_csv(os.path.join(d, "BTCUSDT-1m-2023-01.csv"),
                            [(Y2023 + MIN, 101.0, 10.0, 7.0), (Y2023, 100.0, 10.0, 3.0), (Y2023, 100.0, 10.0, 3.0)])
            a = t93.load_klines(d, [2023])
            self.assertEqual(list(a["t"]), [Y2023, Y2023 + MIN])
            self.assertEqual(list(a["buy"]), [3.0, 7.0])
            self.assertEqual(list(a["sell"]), [7.0, 3.0])

    def test_loader_includes_the_next_january_for_exits(self):
        with tempfile.TemporaryDirectory() as d:
            write_month_csv(os.path.join(d, "BTCUSDT-1m-2023-12.csv"), [(Y2024 - MIN, 100.0, 10.0, 7.0)])
            write_month_csv(os.path.join(d, "BTCUSDT-1m-2024-01.csv"), [(Y2024, 101.0, 10.0, 7.0)])
            write_month_csv(os.path.join(d, "BTCUSDT-1m-2024-03.csv"), [(Y2024 + 60 * 24 * MIN * 70, 120.0, 10.0, 7.0)])
            a = t93.load_klines(d, [2023])
            self.assertEqual(list(a["t"]), [Y2024 - MIN, Y2024])     # 2024-01 yes (exit carry-over), 2024-03 no

    def test_combined_parts_equal_one_run(self):
        rng = np.random.default_rng(7)
        n = 3 * 1440
        t = Y2023 + np.arange(n, dtype=np.int64) * MIN
        c = 100 * np.exp(np.cumsum(rng.normal(0, 2e-4, n)))
        d = dict(t=t, c=c, buy=rng.uniform(1, 2, n), sell=rng.uniform(1, 2, n))
        whole = t93.analyse_parts([t93.part_arrays(d, 2023)])
        halves = t93.analyse_parts([t93.part_arrays(d, 2023), t93.part_arrays({k: v[:0] for k, v in d.items()}, 2024)])
        for w in whole:
            self.assertEqual(whole[w]["n"], halves[w]["n"])
            self.assertAlmostEqual(whole[w]["net_mean"], halves[w]["net_mean"], places=9)

    def test_fee_is_ten_bp_round_trip_taker_both_legs(self):
        self.assertEqual(t93.FEE_BP, 10.0)
        self.assertEqual(t93.WINDOWS, {"4h": 240, "8h": 480, "12h": 720})

    def test_no_edge_series_is_not_a_pass(self):
        rng = np.random.default_rng(3)
        n = 20 * 1440
        t = Y2023 + np.arange(n, dtype=np.int64) * MIN
        c = 100 * np.exp(np.cumsum(rng.normal(0, 2e-4, n)))
        d = dict(t=t, c=c, buy=rng.uniform(1, 2, n), sell=rng.uniform(1, 2, n))
        for o in t93.analyse_parts([t93.part_arrays(d, 2023)]).values():
            self.assertEqual(o["verdict"], "NO REPLICATION")


if __name__ == "__main__":
    unittest.main()
