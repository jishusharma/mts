"""Tests for panel.Panel (BT_SPEC "panel.py"): trade filtering, lazy per-day loading, last_obs / live_instruments /
first_fill semantics, liquidity rule and the no-lookahead guarantee. Offline: shards are built in a temp dir."""
import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bt_testutil as U  # noqa: E402
from bt_testutil import HOUR, DAY, ms, tr  # noqa: E402

import panel as P  # noqa: E402

NAME = "BTC-9OCT26-82000-C"
OTHER = "BTC-9OCT26-78000-P"
T0 = ms(2026, 10, 7, 16, 0)          # a decision time (Wed 16:00 UTC)


class PanelCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "trades"

    def tearDown(self):
        self.tmp.cleanup()

    def panel(self, trades, sort=True):
        U.write_shards(self.dir, trades, sort=sort)
        return P.Panel(self.dir)


class Filtering(PanelCase):
    def test_block_combo_and_liquidation_trades_are_excluded(self):
        trades = [
            tr(T0 - HOUR, NAME, "sell", 0.0050, iv=50.0, index=80000.0),                       # the only clean print
            tr(T0 - HOUR + 1000, NAME, "sell", 0.0090, block_trade_id="BLK-1"),
            tr(T0 - HOUR + 2000, NAME, "sell", 0.0091, combo_id="BTC-CALL-SPREAD"),
            tr(T0 - HOUR + 3000, NAME, "sell", 0.0092, liquidation="T"),
            tr(T0 - HOUR + 4000, OTHER, "buy", 0.0070, block_trade_id="BLK-2"),                 # OTHER: flagged prints only
            tr(T0 - HOUR + 5000, OTHER, "buy", 0.0071, liquidation="M"),
        ]
        p = self.panel(trades)
        o = p.last_obs(NAME, T0, 6 * HOUR)
        self.assertIsNotNone(o)
        self.assertEqual(o["price"], 0.0050)            # not 0.0092, the latest flagged print
        self.assertEqual(o["ts"], T0 - HOUR)
        self.assertEqual(p.live_instruments(T0, 6 * HOUR), {NAME})   # OTHER never traded on-market
        self.assertIsNone(p.last_obs(OTHER, T0, 6 * HOUR))

    def test_flagged_prints_never_fill_and_never_count_toward_liquidity(self):
        trades = [
            tr(T0 + 1000, NAME, "sell", 0.0040, amount=5.0, block_trade_id="BLK-9"),
            tr(T0 + 2000, NAME, "sell", 0.0041, amount=5.0, combo_id="C-1"),
            tr(T0 + 3000, NAME, "sell", 0.0042, amount=5.0, liquidation="MT"),
            tr(T0 + 4000, NAME, "sell", 0.0030, amount=0.5),                 # clean, but only 0.5 of the 1.0 needed
        ]
        p = self.panel(trades)
        self.assertIsNone(p.first_fill(NAME, "sell", T0, 2 * HOUR, 1.0))

    def test_tmp_shards_are_ignored(self):
        trades = [tr(T0 - HOUR, NAME, "sell", 0.0050)]
        U.write_shards(self.dir, trades)
        ghost = tr(T0 - 1000, "BTC-9OCT26-90000-C", "sell", 0.0001)
        # a half-written shard next to the real one, both naming styles, one with valid content and one garbage
        with gzip.open(self.dir / "2026-10-07.jsonl.gz.tmp", "wt", encoding="utf-8") as f:
            f.write(json.dumps(ghost) + "\n")
        (self.dir / "2026-10-06.jsonl.gz.tmp").write_bytes(b"\x1f\x8b not really gzip")
        (self.dir / "2026-10-05.tmp").write_bytes(b"garbage")
        p = P.Panel(self.dir)
        self.assertEqual(p.live_instruments(T0, 6 * HOUR), {NAME})
        self.assertIsNone(p.last_obs("BTC-9OCT26-90000-C", T0, 6 * HOUR))
        self.assertIsNone(p.last_obs(NAME, ms(2026, 10, 6, 12), 6 * HOUR))   # day with only a .tmp: behaves as missing

    def test_missing_days_return_nothing_and_do_not_raise(self):
        p = self.panel([tr(T0 - HOUR, NAME, "sell", 0.0050)])
        far = ms(2026, 12, 25, 12)
        self.assertIsNone(p.last_obs(NAME, far, 6 * HOUR))
        self.assertEqual(p.live_instruments(far, 6 * HOUR), set())
        self.assertIsNone(p.first_fill(NAME, "sell", far, HOUR, 1.0))


class LastObs(PanelCase):
    def test_fields_map_from_trade_columns(self):
        p = self.panel([tr(T0 - 1000, NAME, "buy", 0.0123, iv=47.5, index=81234.5)])
        o = p.last_obs(NAME, T0, HOUR)
        self.assertEqual((o["price"], o["iv"], o["index"], o["ts"]), (0.0123, 47.5, 81234.5, T0 - 1000))

    def test_latest_trade_at_or_before_ts_wins_and_is_inclusive(self):
        p = self.panel([tr(T0 - 3 * HOUR, NAME, "sell", 0.0010), tr(T0 - HOUR, NAME, "buy", 0.0020),
                        tr(T0, NAME, "sell", 0.0030)])
        self.assertEqual(p.last_obs(NAME, T0, 6 * HOUR)["price"], 0.0030)          # ts == decision ts is visible
        self.assertEqual(p.last_obs(NAME, T0 - 1, 6 * HOUR)["price"], 0.0020)
        self.assertEqual(p.last_obs(NAME, T0 - HOUR - 1, 6 * HOUR)["price"], 0.0010)

    def test_no_lookahead_future_trade_is_invisible(self):
        p = self.panel([tr(T0 + 1, NAME, "sell", 0.0099), tr(T0 + HOUR, NAME, "sell", 0.0088)])
        self.assertIsNone(p.last_obs(NAME, T0, 6 * HOUR))

    def test_lookback_limits_staleness(self):
        p = self.panel([tr(T0 - 5 * HOUR, NAME, "sell", 0.0010)])
        self.assertEqual(p.last_obs(NAME, T0, 6 * HOUR)["price"], 0.0010)
        self.assertIsNone(p.last_obs(NAME, T0, 4 * HOUR))                            # 5h old, lookback 4h

    def test_lookup_spans_midnight_between_day_shards(self):
        late = ms(2026, 10, 7, 23, 50)
        p = self.panel([tr(late, NAME, "sell", 0.0010)])
        o = p.last_obs(NAME, ms(2026, 10, 8, 0, 30), 2 * HOUR)       # query day has no shard of its own
        self.assertIsNotNone(o)
        self.assertEqual(o["ts"], late)

    def test_unsorted_shard_content_is_sorted_by_panel(self):
        rows = [tr(T0 - HOUR, NAME, "sell", 0.0020), tr(T0 - 3 * HOUR, NAME, "sell", 0.0010),
                tr(T0 - 2 * HOUR, NAME, "sell", 0.0015)]
        p = self.panel(rows, sort=False)
        self.assertEqual(p.last_obs(NAME, T0, 6 * HOUR)["price"], 0.0020)
        self.assertEqual(p.last_obs(NAME, T0 - 90 * 60000, 6 * HOUR)["price"], 0.0015)

    def test_many_days_with_small_cache_stay_correct(self):
        base = ms(2026, 9, 20, 12)
        rows = [tr(base + i * DAY, NAME, "sell", 0.001 * (i + 1)) for i in range(12)]
        p = self.panel(rows)
        for rnd in range(2):                                          # revisit early days after later ones evicted them
            for i in (0, 11, 3, 8, 0, 5):
                self.assertEqual(p.last_obs(NAME, base + i * DAY + 1, HOUR)["price"], 0.001 * (i + 1))


class LiveInstruments(PanelCase):
    def test_window_is_open_closed(self):
        a, b, c, d = "BTC-9OCT26-80000-C", "BTC-9OCT26-81000-C", "BTC-9OCT26-82000-C", "BTC-9OCT26-83000-C"
        rows = [tr(T0 - 6 * HOUR, a, "sell", 0.01),            # exactly ts - lookback: excluded
                tr(T0 - 6 * HOUR + 1, b, "sell", 0.01),        # just inside
                tr(T0, c, "sell", 0.01),                       # exactly ts: included
                tr(T0 + 1, d, "sell", 0.01)]                   # after ts: invisible
        p = self.panel(rows)
        self.assertEqual(p.live_instruments(T0, 6 * HOUR), {b, c})

    def test_returns_a_set_of_names_deduplicated(self):
        rows = [tr(T0 - i * 60000, NAME, "sell", 0.01) for i in range(1, 6)] + [tr(T0 - 1000, OTHER, "buy", 0.01)]
        out = self.panel(rows).live_instruments(T0, HOUR)
        self.assertIsInstance(out, (set, frozenset))
        self.assertEqual(set(out), {NAME, OTHER})


class FirstFill(PanelCase):
    def test_we_sell_needs_a_taker_sell_print(self):
        p = self.panel([tr(T0 + 1000, NAME, "buy", 0.0050, amount=3.0)])         # taker buy lifts the offer: we cannot sell
        self.assertIsNone(p.first_fill(NAME, "sell", T0, HOUR, 1.0))
        f = p.first_fill(NAME, "buy", T0, HOUR, 1.0)                             # but a WE-buy fill is possible
        self.assertIsNotNone(f)
        self.assertEqual(f["price"], 0.0050)

    def test_we_buy_needs_a_taker_buy_print(self):
        p = self.panel([tr(T0 + 1000, NAME, "sell", 0.0040, amount=3.0)])
        self.assertIsNone(p.first_fill(NAME, "buy", T0, HOUR, 1.0))
        self.assertEqual(p.first_fill(NAME, "sell", T0, HOUR, 1.0)["price"], 0.0040)

    def test_fill_dict_fields(self):
        p = self.panel([tr(T0 + 7000, NAME, "sell", 0.0042, amount=2.0, index=80555.5)])
        f = p.first_fill(NAME, "sell", T0, HOUR, 1.0)
        self.assertEqual((f["price"], f["ts"], f["index"]), (0.0042, T0 + 7000, 80555.5))

    def test_default_size_is_one_contract(self):
        p = self.panel([tr(T0 + 1000, NAME, "sell", 0.0040, amount=0.5)])
        self.assertIsNone(p.first_fill(NAME, "sell", T0, HOUR))                  # 0.5 < default 1.0
        p2 = P.Panel(self.dir)
        self.assertIsNotNone(p2.first_fill(NAME, "sell", T0, HOUR, 0.5))

    def test_liquidity_cumulative_amount_must_reach_size_fill_at_completing_print(self):
        rows = [tr(T0 + 1000, NAME, "sell", 0.0050, amount=0.25),
                tr(T0 + 2000, NAME, "buy", 0.0099, amount=9.0),         # wrong side: adds nothing
                tr(T0 + 3000, NAME, "sell", 0.0049, amount=0.5),
                tr(T0 + 4000, NAME, "sell", 0.0048, amount=0.5),        # cum 0.25+0.5+0.5=1.25 >= 1.0 completes here
                tr(T0 + 5000, NAME, "sell", 0.0047, amount=5.0)]
        p = self.panel(rows)
        f = p.first_fill(NAME, "sell", T0, HOUR, 1.0)
        self.assertEqual((f["price"], f["ts"]), (0.0048, T0 + 4000))             # price of the completing print, no averaging
        f = p.first_fill(NAME, "sell", T0, HOUR, 0.75)                           # 0.25 + 0.5 reaches 0.75 exactly
        self.assertEqual((f["price"], f["ts"]), (0.0049, T0 + 3000))
        f = p.first_fill(NAME, "sell", T0, HOUR, 0.25)
        self.assertEqual((f["price"], f["ts"]), (0.0050, T0 + 1000))             # first print already covers it

    def test_insufficient_liquidity_in_window_gives_no_fill(self):
        rows = [tr(T0 + 1000, NAME, "sell", 0.0050, amount=0.25), tr(T0 + 2000, NAME, "sell", 0.0049, amount=0.25),
                tr(T0 + 3000, NAME, "buy", 0.0060, amount=9.0)]
        self.assertIsNone(self.panel(rows).first_fill(NAME, "sell", T0, HOUR, 1.0))

    def test_prints_beyond_the_window_do_not_count(self):
        rows = [tr(T0 + 1000, NAME, "sell", 0.0050, amount=0.5),
                tr(T0 + 2 * HOUR, NAME, "sell", 0.0049, amount=5.0)]              # outside a 1h window
        p = self.panel(rows)
        self.assertIsNone(p.first_fill(NAME, "sell", T0, HOUR, 1.0))
        f = p.first_fill(NAME, "sell", T0, 3 * HOUR, 1.0)                        # widen the window: now it completes
        self.assertEqual(f["price"], 0.0049)

    def test_no_lookahead_print_before_decision_ts_never_fills(self):
        rows = [tr(T0 - 1, NAME, "sell", 0.0050, amount=50.0)]                  # 1 ms before the decision, huge size
        p = self.panel(rows)
        self.assertIsNone(p.first_fill(NAME, "sell", T0, 6 * HOUR, 1.0))
        self.assertIsNone(p.first_fill(NAME, "sell", T0, 6 * HOUR, 0.01))

    def test_print_before_decision_does_not_count_toward_cumulative_amount(self):
        rows = [tr(T0 - 5000, NAME, "sell", 0.0051, amount=0.75),               # before: must be ignored entirely
                tr(T0 + 1000, NAME, "sell", 0.0050, amount=0.5)]
        p = self.panel(rows)
        self.assertIsNone(p.first_fill(NAME, "sell", T0, HOUR, 1.0))            # 0.5 only; 1.25 if lookahead leaked
        self.assertEqual(p.first_fill(NAME, "sell", T0, HOUR, 0.5)["price"], 0.0050)

    def test_print_exactly_at_decision_ts_can_fill(self):
        p = self.panel([tr(T0, NAME, "sell", 0.0050, amount=1.0)])
        self.assertEqual(p.first_fill(NAME, "sell", T0, HOUR, 1.0)["ts"], T0)

    def test_other_instruments_are_isolated(self):
        rows = [tr(T0 + 1000, OTHER, "sell", 0.0050, amount=5.0), tr(T0 + 2000, NAME, "sell", 0.0030, amount=0.5)]
        p = self.panel(rows)
        self.assertIsNone(p.first_fill(NAME, "sell", T0, HOUR, 1.0))
        self.assertEqual(p.first_fill(OTHER, "sell", T0, HOUR, 1.0)["price"], 0.0050)

    def test_fill_search_crosses_midnight(self):
        t = ms(2026, 10, 7, 23, 30)
        p = self.panel([tr(ms(2026, 10, 8, 0, 20), NAME, "sell", 0.0050, amount=1.0)])
        self.assertEqual(p.first_fill(NAME, "sell", t, 2 * HOUR, 1.0)["price"], 0.0050)

    def test_slip_pct_is_adverse_and_defaults_to_zero(self):
        p = self.panel([tr(T0 + 1000, NAME, "sell", 0.0100, amount=2.0), tr(T0 + 1000, OTHER, "buy", 0.0100, amount=2.0)])
        self.assertAlmostEqual(p.first_fill(NAME, "sell", T0, HOUR, 1.0)["price"], 0.0100, places=12)
        sold = p.first_fill(NAME, "sell", T0, HOUR, 1.0, slip_pct=0.10)           # we sell: receive less
        bought = p.first_fill(OTHER, "buy", T0, HOUR, 1.0, slip_pct=0.10)         # we buy: pay more
        self.assertAlmostEqual(sold["price"], 0.0090, places=12)
        self.assertAlmostEqual(bought["price"], 0.0110, places=12)


if __name__ == "__main__":
    unittest.main()
