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
        from MyTradingSys.execution import auto_trader as at
        cfg = {"layer_rules": {"rsi:support": "long"}}
        for e in ev:
            self.assertIsNone(at.layer_side({"layer": "confluence_feed", **e}, cfg))
        # the raw RSI cross stays unmapped on purpose: no source gives it a side (RSI_CROSS_UNMAPPED.md)
        self.assertIsNone(at.layer_side({"layer": "rsi", "sub": "rsi_events", "event": "cross", "level_value": 50.0,
                                         "direction": "up"}, cfg))

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
