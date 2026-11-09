"""analyst_levels.py: CBP pointers become a price ladder, and a chart paste shows it (operator 2026-10-30: Michael's
78k/75k and Krown's 76-77k wick sat in CBP before the 10-29 break and no read showed them)."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyst_levels as al
import shot


def row(analyst, pointers, days_ago=1, symbols=("BTC",), vid="v1"):
    d = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return {"analyst": analyst, "video_id": vid, "published": d.date().isoformat(), "bias": "BEARISH",
            "symbols": list(symbols), "quotes": ["q"], "trades": [], "pointers": list(pointers), "quote_verified": True,
            "expires_at": (d + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")}


class Parse(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(al.parse_levels("Weakness below ~81k points to 78k, with main support at 75k"), [81000, 78000, 75000])
        self.assertEqual(al.parse_levels("Major support around $75,000"), [75000])
        self.assertEqual(al.parse_levels("expects wick in 76,000-77,000 range"), [76000, 77000])
        self.assertEqual(al.parse_levels("Upside next level 90-92k"), [90000, 92000])
        self.assertEqual(al.parse_levels("a decline to 78 thousand"), [78000])
        self.assertEqual(al.parse_levels("pullback between 77.5k and 78.5k"), [77500, 78500])

    def test_k_on_both_bounds(self):
        self.assertEqual(al.parse_levels("expects a wick into 76k-77k"), [76000, 77000])

    def test_counts_are_not_prices(self):
        self.assertEqual(al.parse_levels("100k liquidations today, then 75k is the level"), [75000])
        self.assertEqual(al.parse_levels("over 120k contracts liquidated near 80k"), [80000])

    def test_noise_dropped(self):
        self.assertEqual(al.parse_levels("13 EMA crossing 34 EMA on the 2-day, September 15th"), [])
        self.assertEqual(al.parse_levels("ETH range 2K to 4.5K"), [])

    def test_ladder_btc_only_sorted_one_per_video(self):
        rows = [row("Michael", ["main support at 75k", "75,000 again", "81k pivot"]),
                row("Habib", ["SOL 180"], symbols=("SOL",), vid="v2")]
        lv = al.ladder(rows)
        self.assertEqual([x["level"] for x in lv], [81000, 75000])
        self.assertEqual({x["analyst"] for x in lv}, {"Michael"})


class Symbols(unittest.TestCase):
    def test_ladder_eth_levels(self):
        rows = [row("Habib", ["ETH support at 2,350, then 2,250 below"], symbols=("ETH",), vid="e1"),
                row("Michael", ["BTC support 75k"], vid="b1")]
        lv = al.ladder(rows, symbol="ETH")
        self.assertEqual([x["level"] for x in lv], [2350, 2250])
        self.assertEqual({x["analyst"] for x in lv}, {"Habib"})

    def test_btc_unchanged_and_ignores_alt_rows(self):
        rows = [row("Habib", ["ETH support at 2,350"], symbols=("ETH",), vid="e1"),
                row("Michael", ["BTC support 75k"], vid="b1")]
        self.assertEqual([x["level"] for x in al.ladder(rows)], [75000])
        self.assertEqual(al.ladder(rows), al.ladder(rows, symbol="BTC"))

    def test_eth_formats_and_band(self):
        self.assertEqual(al.parse_levels("ETH 2350 and 2.5k, not 75k", "ETH"), [2350, 2500])
        self.assertEqual(al.parse_levels("in 2026 ETH holds 2,250", "ETH"), [2250])
        self.assertEqual(al.parse_levels("2,350", "BTC"), [])
        self.assertEqual(al.parse_levels("2,350", "DOGE"), [])

    def test_cli_symbol_flag(self):
        with tempfile.TemporaryDirectory() as d:
            store = os.path.join(d, "s.json")
            with open(store, "w", encoding="utf-8", newline="\n") as f:
                json.dump({"rows": [row("Habib", ["ETH support at 2,350 and 2,250"], symbols=("ETH",))]}, f)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                al.main(["--offline", "--symbol", "ETH", "--store", store])
            self.assertIn("2,350", buf.getvalue())
            self.assertIn("ETH rows", buf.getvalue())


class Defects(unittest.TestCase):
    def test_price_followed_by_ticker_kept(self):
        self.assertEqual(al.parse_levels("target 80k BTC"), [80000])
        self.assertEqual(al.parse_levels("support at 75,000 BTC"), [75000])
        self.assertEqual(al.parse_levels("ETH 2,350 ETH"), [])  # out of BTC band
        self.assertEqual(al.parse_levels("holds 2,350 ETH", "ETH"), [2350])

    def test_bare_eth_price_in_year_range_kept(self):
        self.assertEqual(al.parse_levels("ETH 2030 support", "ETH"), [2030])
        self.assertEqual(al.parse_levels("support 2,030 and 2,020", "ETH"), [2030, 2020])
        self.assertEqual(al.parse_levels("by 2030 and in 2026, October 2026", "ETH"), [])

    def test_klines_paginate_past_1000_cap(self):
        h = 3600
        t0 = 1_700_000_000
        pages = [[[ (t0 + i * h) * 1000, 0, 2.0, 1.0, 1.5 ] for i in range(1000)],
                 [[ (t0 + (1000 + i) * h) * 1000, 0, 2.0, 1.0, 9.0 ] for i in range(5)]]
        calls = []
        class R:
            def __init__(s, d): s.d = d
            def __enter__(s): return s
            def __exit__(s, *a): pass
            def read(s, *a): return json.dumps(s.d).encode()
        def fake(url, timeout=0):
            calls.append(url)
            return R(pages[len(calls) - 1])
        with mock.patch.object(al.urllib.request, "urlopen", fake), mock.patch.object(al.json, "load", lambda f: f.d):
            bars = al.spot_1h(datetime.fromtimestamp(t0, timezone.utc))
        self.assertEqual(len(bars), 1005)
        self.assertEqual(bars[-1][3], 9.0)
        self.assertEqual(len(calls), 2)

    def test_mark_empty_bars_raises_clear_error(self):
        with self.assertRaises(ValueError):
            al.mark([], [], datetime.now(timezone.utc))


class Hit(unittest.TestCase):
    def test_publish_day_bars_never_count(self):
        """Only the date is stored: a touch on the publish day may predate the video, so hit starts the next UTC day."""
        day = int(datetime(2026, 10, 29, tzinfo=timezone.utc).timestamp())
        bars = [(day + 3600 * k, 80_500.0, 79_500.0, 80_000.0) for k in range(24)]  # 10-29 only: 79.5k..80.5k
        bars += [(day + 86_400 + 3600 * k, 82_000.0, 81_000.0, 81_500.0) for k in range(24)]  # 10-30: 81k..82k
        lv = [dict(level=80_000.0, published="2026-10-29", expires_at=""), dict(level=81_500.0, published="2026-10-29", expires_at="")]
        al.mark(lv, bars, datetime(2026, 10, 31, tzinfo=timezone.utc))
        self.assertEqual([x["hit"] for x in lv], [False, True])
        self.assertEqual(al.hit_from("2026-10-29"), datetime(2026, 10, 30, tzinfo=timezone.utc))


class Notice(unittest.TestCase):
    def test_chart_paste_shows_analyst_levels(self):
        with tempfile.TemporaryDirectory() as d:
            store = os.path.join(d, "rows.json")
            json.dump({"schema": 1, "rows": [row("Michael", ["main support at 75k"])], "rejected": []}, open(store, "w"))
            real = al.recent_rows
            with mock.patch.object(al, "recent_rows", lambda days, now, store_=None: real(days, now, store)), \
                    mock.patch.object(al, "perp_1h", side_effect=OSError("offline")), mock.patch.object(al, "spot_1h", side_effect=OSError("offline")):
                out = shot.notice([{"id": "abc123", "ext": "png", "w": 10, "h": 10, "route": "paste"}], [])
        self.assertIn("ANALYST LEVELS", out)
        self.assertIn("75,000", out)
        self.assertIn("Michael", out)

    def test_chart_paste_rebuilds_live_aid_analyst_data(self):
        with mock.patch.object(shot, "refresh_live_aid_analysts") as ref, mock.patch.object(al, "hook_block", return_value=""):
            shot.notice([{"id": "abc123", "ext": "png", "w": 10, "h": 10, "route": "paste"}], [])
            shot.notice([], [])
        self.assertEqual(ref.call_count, 1)  # only when a new image landed

    def test_hook_block_never_raises(self):
        with mock.patch.object(al, "recent_rows", side_effect=RuntimeError("bad store")):
            self.assertEqual(al.hook_block(), "")


class MutationKills(unittest.TestCase):
    """Spec-derived (module docstring: prices 40k..200k, one level per video, hit = traded through, --offline = no network)."""

    def test_band_edges_inclusive(self):
        self.assertEqual(al.parse_levels("floor 40,000"), [40000])
        self.assertEqual(al.parse_levels("cap 200,000"), [200000])
        self.assertEqual(al.parse_levels("below 39,999"), [])
        self.assertEqual(al.parse_levels("above 200,001"), [])

    def test_same_level_two_videos_both_kept(self):
        rows = [row("Michael", ["support 75k"], vid="v1"), row("Krown", ["wick to 75k"], vid="v2")]
        lv = al.ladder(rows)
        self.assertEqual([(x["level"], x["analyst"]) for x in lv], [(75000, "Michael"), (75000, "Krown")])

    def test_hit_touch_on_bar_extreme_counts(self):
        t = int(datetime(2026, 10, 30, tzinfo=timezone.utc).timestamp())
        bars = [(t, 80_000.0, 79_000.0, 79_500.0)]  # next day after publish 10-29
        lv = [dict(level=lv_, published="2026-10-29", expires_at="") for lv_ in (80_000.0, 79_000.0, 80_100.0, 78_900.0)]
        al.mark(lv, bars, datetime(2026, 10, 31, tzinfo=timezone.utc))
        self.assertEqual([x["hit"] for x in lv], [True, True, False, False])

    def test_render_hit_vs_open_tag(self):
        base = dict(analyst="Michael", published="2026-10-29", bias="BEARISH", video_id="v1", said="s", expires_at="")
        hit = al.render([dict(base, level=75000.0, hit=True, dist_pct=-5.0)], price=79000.0)
        opn = al.render([dict(base, level=75000.0, hit=False, dist_pct=-5.0)], price=79000.0)
        self.assertIn("-5.00% HIT ", hit)
        self.assertNotIn("open", hit)
        self.assertIn("-5.00% open", opn)
        self.assertNotIn("HIT", opn)

    def test_main_offline_makes_no_network_call(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            store = os.path.join(d, "rows.json")
            json.dump({"schema": 1, "rows": [row("Michael", ["support 75k"])], "rejected": []}, open(store, "w"))
            buf = io.StringIO()
            with mock.patch.object(al, "perp_1h", side_effect=AssertionError("network")), mock.patch.object(al, "spot_1h", side_effect=AssertionError("network")), contextlib.redirect_stdout(buf):
                al.main(["--offline", "--json", "--store", store])
        out = json.loads(buf.getvalue())
        self.assertIsNone(out["price"])
        self.assertEqual([x["level"] for x in out["levels"]], [75000])
        self.assertNotIn("hit", out["levels"][0])


class Tolerance(unittest.TestCase):
    """Card level-touch-alerts-session-brief-1109: 11-08 21:55Z BTC spot low 73,510 never 'hit' the 73,500 zone."""
    T0 = int(datetime(2026, 11, 8, tzinfo=timezone.utc).timestamp())

    def bars(self):
        return [(self.T0 + 3600 * k, 73_900.0, 73_510.0, 73_700.0) for k in range(24)]

    def lv(self, level):
        return dict(level=level, published="2026-11-07", expires_at="")

    def test_touch_tol_is_one_constant(self):
        self.assertEqual(al.TOUCH_TOL, 0.0005)

    def test_1108_case_73500_vs_spot_low_73510_is_hit(self):
        lv = [self.lv(73_500.0)]
        al.mark(lv, self.bars(), datetime(2026, 11, 9, tzinfo=timezone.utc))
        self.assertTrue(lv[0]["hit"])

    def test_outside_tolerance_stays_open(self):
        lv = [self.lv(73_400.0)]  # 110 below the low = 0.15 %
        al.mark(lv, self.bars(), datetime(2026, 11, 9, tzinfo=timezone.utc))
        self.assertFalse(lv[0]["hit"])

    def test_touched_helper_both_sides(self):
        self.assertTrue(al.touched(73_500.0, 73_510.0, 73_900.0))
        self.assertTrue(al.touched(74_000.0, 73_500.0, 73_970.0))  # high 30 below = 0.04 %
        self.assertFalse(al.touched(74_000.0, 73_500.0, 73_900.0))


class Source(unittest.TestCase):
    def test_perp_first(self):
        t0 = datetime(2026, 11, 8, tzinfo=timezone.utc)
        with mock.patch.object(al, "perp_1h", return_value=[(1, 2.0, 1.0, 1.5)]),                 mock.patch.object(al, "spot_1h", side_effect=AssertionError("spot")):
            bars, src = al.bars_with_source(t0)
        self.assertEqual(src, "perp")
        self.assertEqual(bars, [(1, 2.0, 1.0, 1.5)])

    def test_spot_fallback_named(self):
        t0 = datetime(2026, 11, 8, tzinfo=timezone.utc)
        with mock.patch.object(al, "perp_1h", side_effect=OSError("blocked")),                 mock.patch.object(al, "spot_1h", return_value=[(1, 2.0, 1.0, 1.5)]):
            bars, src = al.bars_with_source(t0)
        self.assertEqual(src, "spot")

    def test_perp_url_is_usdm_futures_via_doh(self):
        seen = []

        class R:
            def __enter__(s): return s
            def __exit__(s, *a): return False
            def read(s): return b"[]"

        def fake(url, timeout=None):
            seen.append(url)
            return R()
        with mock.patch.object(al, "_urlopen", fake):
            al.perp_1h(datetime(2026, 11, 8, tzinfo=timezone.utc))
        self.assertIn("fapi.binance.com/fapi/v1/klines", seen[0])

    def test_main_prints_source(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            store = os.path.join(d, "cbp.json")
            json.dump({"rows": [row("Michael", ["support 75k"], days_ago=2)]}, open(store, "w"))
            bars = [(int(datetime.now(timezone.utc).timestamp()) - 3600, 76_000.0, 75_000.0, 75_500.0)]
            buf = io.StringIO()
            with mock.patch.object(al, "bars_with_source", return_value=(bars, "spot")), contextlib.redirect_stdout(buf):
                al.main(["--store", store])
        self.assertIn("source: spot", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
