"""Tests for live_confluence_feed (cards krown-hidden-divergence-confluence-feed + rsi-cross-unmapped-and-pivot-stack).

The feed turns RSI 40/60 events and Malkan / Krown divergence flags into alert-only confluence inputs.
Live-path rules: restart/reset state (stateless, prefix-equal), non-trade balance moves (no side, no size, never reaches
the order path), API errors / bad bars (fail closed to []), Malkan pinned to regular + PRD/NRD only.
"""
import random
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.alerts import live_confluence_feed as m

HOUR = 3600000
FLAGS_CSV = Path(__file__).resolve().parents[3] / "research" / "malkan_div_flags_2026-10-28" / "BTCUSDT_divergences.csv"


def walk(n, seed=3, t0=0, step=HOUR):
    rng = random.Random(seed)
    px, out = 50000.0, []
    for i in range(n):
        o = px
        px += rng.uniform(-400, 400)
        out.append({"t": t0 + i * step, "o": o, "h": max(o, px) + 50, "l": min(o, px) - 50, "c": px, "v": 10.0, "tbv": 5.0})
    return out


class FeedTests(unittest.TestCase):
    def test_events_exist_and_are_alert_only(self):
        ev = m.confluence_feed_layer(walk(400))
        self.assertTrue(ev)
        for e in ev:
            self.assertNotIn("side", e)                      # fail closed: never a trade side
            self.assertTrue(e["collection_only"])
            self.assertIn(e["code"].split("_")[0], ("RSI", "R-BULL", "R-BEAR", "PRD", "NRD", "K-HBULL", "K-HBEAR"))
            self.assertIsInstance(e["t"], int)

    def test_rsi_cross_40_60_present_and_unmapped_by_auto_trader(self):
        ev = [e for s in range(1, 30) for e in m.confluence_feed_layer(walk(600, seed=s))]
        crosses = [e for e in ev if e["event"].startswith("cf_rsi_cross_")]
        self.assertTrue(any(e["event"].endswith("_40") for e in crosses))
        self.assertTrue(any(e["event"].endswith("_60") for e in crosses))
        # layer_side pinning lives in MyTradingSys/execution/test_auto_trader.py (layers must not import execution)
        self.assertFalse([e for e in ev if "side" in e])

    def test_all_four_malkan_codes_and_krown_labelled(self):
        codes = set()
        for seed in range(1, 40):
            codes |= {e["code"] for e in m.confluence_feed_layer(walk(500, seed=seed))}
        self.assertTrue({"R-BULL", "R-BEAR"} <= codes)
        self.assertTrue(codes & {"K-HBULL", "K-HBEAR"})
        for e in m.confluence_feed_layer(walk(500, seed=2)):
            if e["code"].startswith("K-"):
                self.assertEqual(e["source"], "KROWN-CONFLUENCE")
                self.assertEqual(e["label"], "OURS")
            if e["code"] in ("R-BULL", "R-BEAR", "PRD", "NRD"):
                self.assertEqual(e["source"], "MALKAN")
                # d-malkan-window-label-1105: the 12/18 window has no Malkan source, so it is OURS
                self.assertIn("OURS window 12/18", e["label"])
                self.assertNotIn("SOURCED window", e["label"])

    def test_restart_is_stateless_and_prefix_equal(self):
        bars = walk(300, seed=9)
        full = m.confluence_feed_layer(bars)
        self.assertEqual(full, m.confluence_feed_layer(list(bars)))
        k = 220
        part = m.confluence_feed_layer(bars[:k])
        cut = bars[k - 1]["t"]
        self.assertEqual(part, [e for e in full if e["t"] <= cut])      # no look-ahead

    def test_bad_bars_fail_closed(self):
        bars = walk(200)
        bars[50]["c"] = float("nan")
        bars[60] = {"t": bars[60]["t"]}                                  # missing keys
        ev = m.confluence_feed_layer(bars)
        bad_t = {bars[50]["t"], bars[60]["t"]}
        self.assertFalse([e for e in ev if e["t"] in bad_t])
        self.assertEqual(m.confluence_feed_layer([]), [])
        self.assertEqual(m.confluence_feed_layer(walk(10)), [])
        self.assertEqual(m.confluence_feed_layer(None), [])

    def test_malkan_pinned_to_regular_and_reverse_only(self):
        self.assertEqual(set(m.MALKAN_KINDS), {"bullish", "bearish", "prd", "nrd"})
        self.assertFalse([k for k in m.MALKAN_KINDS if "hidden" in k])
        here = Path(__file__).resolve().parent
        for p in (here.parent / "rsi" / "run_divergence_mtf.py", here / "live_rsi_divergence.py"):
            src = p.read_text(encoding="utf-8").lower()
            self.assertNotIn("hidden_bull", src)
            self.assertNotIn("krown_hidden", src)
        from MyTradingSys.backtest.layers.alerts import live_rsi_divergence as lrd
        self.assertFalse([e for s in range(1, 15) for e in lrd.adapter(walk(300, seed=s)) if "hidden" in e["event"]])


class WindowSpecTests(unittest.TestCase):
    """Operator spec d-malkan-divergence-window-1104: close-based, window 12 STRONG / 18 OK / >18 WEAK."""

    def test_window_class_boundaries(self):
        self.assertEqual([m.window_class(n) for n in (3, 12, 13, 18, 19, 40)],
                         ["STRONG", "STRONG", "OK", "OK", "WEAK", "WEAK"])
        self.assertEqual((m.WINDOW_STRONG, m.WINDOW_MAX), (12, 18))

    def test_primary_events_carry_class_and_never_exceed_18(self):
        prim = [e for s in range(1, 25) for e in m.confluence_feed_layer(walk(500, seed=s))
                if e["source"] == "MALKAN" and e.get("column") == "primary"]
        self.assertTrue(prim)
        for e in prim:
            self.assertEqual(e["basis"], "close")
            self.assertLessEqual(e["bars"], 18)
            self.assertEqual(e["window_class"], m.window_class(e["bars"]))
            self.assertNotEqual(e["window_class"], "WEAK")
        self.assertIn("OK", {e["window_class"] for e in prim})        # 13..18 bars now fire (old cap was 10)
        self.assertIn("STRONG", {e["window_class"] for e in prim})

    def test_legacy_column_is_comparison_only_with_old_windows(self):
        ev = [e for s in range(1, 25) for e in m.confluence_feed_layer(walk(500, seed=s)) if e.get("column") == "legacy"]
        self.assertTrue(ev)
        for e in ev:
            self.assertTrue(e["code"].endswith("_OLD"))
            self.assertEqual(e["label"][:4], "OURS")
            self.assertLessEqual(e["bars"], 14 if e["code"].startswith(("PRD", "NRD")) else 10)
        feed = [e for e in ev]
        out = m.annotate_levels_events([{"t": e["t"] + HOUR, "event": "x"} for e in feed[:3]], feed[:3], HOUR)
        self.assertTrue(all(o["confluence"] and o["confluence"][0].endswith("_OLD") for o in out))

    def test_wick_only_divergence_does_not_fire(self):
        # Price CLOSES keep making a higher low pattern-free zigzag; only the wicks (low / high) are rewritten to
        # fabricate a lower-low-with-higher-RSI picture. Output must equal the output on the untouched wicks.
        import copy
        rng = random.Random(11)
        for seed in range(1, 12):
            bars = walk(300, seed=seed)
            wild = copy.deepcopy(bars)
            for b in wild:
                b["l"] = b["l"] - rng.uniform(0, 3000)
                b["h"] = b["h"] + rng.uniform(0, 3000)
            self.assertEqual(m.confluence_feed_layer(bars), m.confluence_feed_layer(wild))

    def test_wick_only_synthetic_case(self):
        # closes: steady rise (no swing low pair at all); wicks dip to a lower low at bar 40 vs bar 30 => wick-only
        bars = [{"t": i * HOUR, "o": 100 + i, "h": 101 + i, "l": 99 + i, "c": 100.5 + i, "v": 1.0} for i in range(80)]
        bars[30]["l"], bars[40]["l"] = 60.0, 55.0
        bars[31]["l"], bars[41]["l"] = 62.0, 58.0
        ev = [e for e in m.confluence_feed_layer(bars) if e["source"] == "MALKAN" and e["code"] in ("R-BULL", "PRD")]
        self.assertEqual(ev, [])


class AnnotateTests(unittest.TestCase):
    def test_annotate_uses_only_closed_feed_bars(self):
        feed = [{"t": 10 * HOUR, "code": "PRD"}, {"t": 20 * HOUR, "code": "R-BULL"}]
        lv = [{"t": 11 * HOUR - 1, "event": "lc_x"}, {"t": 11 * HOUR, "event": "lc_y"}, {"t": 21 * HOUR, "event": "lc_z"}]
        out = m.annotate_levels_events(lv, feed, window_ms=2 * HOUR, feed_tf_ms=HOUR)
        self.assertEqual(out[0]["confluence"], [])               # feed bar at 10h only closes at 11h
        self.assertEqual(out[1]["confluence"], ["PRD"])
        self.assertEqual(out[2]["confluence"], ["R-BULL"])
        self.assertNotIn("confluence", lv[0])                    # input not mutated

    def test_annotate_never_adds_side_and_fails_closed(self):
        out = m.annotate_levels_events([{"t": 5, "event": "e"}], None, 10, HOUR)
        self.assertNotIn("side", out[0])
        self.assertEqual(out[0]["confluence"], [])
        with self.assertRaises(ValueError):
            m.annotate_levels_events([], [], -1, HOUR)

    def test_flags_csv_consumed_with_known_on_causal(self):
        rows = m.load_flags_csv(FLAGS_CSV)
        self.assertGreater(len(rows), 10)
        r = rows[0]
        self.assertEqual((r["code"], r["tf"]), ("K-HBEAR", "1d"))
        self.assertEqual(r["t"], 1769644800000)                  # 2026-01-29 00:00 UTC, bar that confirms
        self.assertEqual(r["usable_from"], r["t"] + 86400000)    # closes a day later
        self.assertTrue(all(x["usable_from"] > x["t"] for x in rows))

    def test_flags_csv_missing_or_garbled_is_empty(self):
        self.assertEqual(m.load_flags_csv(FLAGS_CSV.with_name("nope.csv")), [])


if __name__ == "__main__":
    unittest.main()
