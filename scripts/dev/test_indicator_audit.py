"""Tests for indicator_audit_sample.py / indicator_audit_compare.py (card indicator-values-multi-model-audit).

Expected numbers are hand-computed from MyTradingSys/backtest/layers/FORMULAS.md (s1, s22, s23), never from the
scripts or the engine under audit.
"""
import json
import math
import pathlib
import random
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import indicator_audit_sample as smp  # noqa: E402
import indicator_audit_compare as cmp_  # noqa: E402


def synth_pool(seed=1):
    """Deterministic random-walk pool, 2 symbols x 3 timeframes x 1200 closes."""
    rnd = random.Random(seed)
    pool = {}
    for sym, start in (("BTCUSDT", 80000.0), ("ETHUSDT", 3000.0)):
        for tf, step in (("5m", 300_000), ("15m", 900_000), ("1h", 3_600_000)):
            c, closes, opens = start, [], []
            for i in range(1200):
                c *= 1 + rnd.uniform(-0.004, 0.004)
                closes.append(round(c, 2))
                opens.append(1_790_000_000_000 + i * step)
            pool[f"{sym}|{tf}"] = {"symbol": sym, "tf": tf, "open_times": opens, "closes": closes}
    return pool


class SamplerTests(unittest.TestCase):
    def test_same_seed_identical_other_seed_differs(self):
        pool = synth_pool()
        a = smp.draw(pool, 20261020)
        b = smp.draw(pool, 20261020)
        c = smp.draw(pool, 20261021)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertNotEqual(json.dumps(a, sort_keys=True), json.dumps(c, sort_keys=True))

    def test_coverage_and_window_length(self):
        pk = smp.draw(synth_pool(), 7)
        self.assertGreaterEqual(len(pk), 18)
        for ind in ("RSI", "BB", "STOCHRSI"):
            rows = [p for p in pk if p["indicator"] == ind]
            self.assertGreaterEqual(len(rows), 6, ind)
            self.assertGreaterEqual(len({p["tf"] for p in rows}), 2, ind)
        for p in pk:
            self.assertEqual(len(p["closes"]), 500)

    def test_packet_never_holds_engine_values_or_code(self):
        for p in smp.draw(synth_pool(), 7):
            blob = json.dumps(p).lower()
            for bad in ("engine", "rsi_core", "chart_verify", "def ", "import "):
                self.assertNotIn(bad, blob)
            self.assertEqual(p["sha256"], smp.window_sha256(p["closes"]))
            self.assertEqual(sorted(p["answer_keys"]), sorted(smp.ANSWER_KEYS[p["indicator"]]))

    def test_definition_text_comes_from_formulas_md(self):
        d = smp.definition_text("BB")
        self.assertIn("POPULATION standard deviation", d)
        self.assertNotIn(".py", d)
        self.assertIn("Wilder", smp.definition_text("RSI"))
        self.assertIn("raw[t]", smp.definition_text("STOCHRSI"))


class ComparatorTests(unittest.TestCase):
    # FORMULAS.md s22 worked example: closes [10,12,14,12] n=4 mult=2: mean 12, pop sd sqrt(2), upper 14.828427;
    # sample sd (n-1) gives upper 15.265986.
    def test_bollinger_sample_sd_variant_is_caught(self):
        eng = {"BB_up": 14.828427}
        ok = cmp_.compare_value("BB", eng, {"BB_up": 14.828427})
        bad = cmp_.compare_value("BB", eng, {"BB_up": 15.265986})
        self.assertTrue(all(r["ok"] for r in ok))
        self.assertFalse(bad[0]["ok"])
        self.assertAlmostEqual(bad[0]["diff"], 15.265986 - 14.828427, places=6)

    def test_bollinger_relative_tolerance_edge(self):
        eng = {"BB_mid": 80000.0}
        self.assertTrue(cmp_.compare_value("BB", eng, {"BB_mid": 80000.0 * (1 + 0.9e-6)})[0]["ok"])
        self.assertFalse(cmp_.compare_value("BB", eng, {"BB_mid": 80000.0 * (1 + 1.5e-6)})[0]["ok"])

    def test_rsi_off_by_half_point_is_caught(self):
        self.assertFalse(cmp_.compare_value("RSI", {"RSI": 63.0}, {"RSI": 63.5})[0]["ok"])
        self.assertTrue(cmp_.compare_value("RSI", {"RSI": 63.0}, {"RSI": 63.009})[0]["ok"])
        self.assertFalse(cmp_.compare_value("RSI", {"RSI": 63.0}, {"RSI": 63.011})[0]["ok"])

    def test_missing_or_nan_reply_is_a_mismatch(self):
        self.assertFalse(cmp_.compare_value("STOCHRSI", {"StochRSI_K": 10.0, "StochRSI_D": 20.0},
                                            {"StochRSI_K": 10.0})[1]["ok"])
        self.assertFalse(cmp_.compare_value("RSI", {"RSI": 50.0}, {"RSI": float("nan")})[0]["ok"])
        self.assertFalse(cmp_.compare_value("RSI", {"RSI": 50.0}, {"RSI": "fifty"})[0]["ok"])

    # Engine values on hand-computable 500-bar windows (FORMULAS.md s1, s22, s23).
    def test_engine_values_hand_windows(self):
        # strictly rising: avg_loss 0, avg_gain > 0 -> RSI 100 (s1 step 4); RSI constant 100 -> max == min -> raw 0
        # (s23, OURS) -> K = D = 0
        up = [100.0 + i for i in range(500)]
        self.assertAlmostEqual(cmp_.engine_values("RSI", up)["RSI"], 100.0, places=9)
        sr = cmp_.engine_values("STOCHRSI", up)
        self.assertEqual((sr["StochRSI_K"], sr["StochRSI_D"]), (0.0, 0.0))
        # strictly falling: avg_gain 0, avg_loss > 0 -> rs 0 -> RSI 0
        down = [1000.0 - i for i in range(500)]
        self.assertAlmostEqual(cmp_.engine_values("RSI", down)["RSI"], 0.0, places=9)
        # last 20 closes = ten 10s then ten 12s: mean 11, deviations +-1, population sd 1 -> 9 / 11 / 13
        bb = cmp_.engine_values("BB", [50.0] * 480 + [10.0] * 10 + [12.0] * 10)
        self.assertAlmostEqual(bb["BB_mid"], 11.0, places=9)
        self.assertAlmostEqual(bb["BB_up"], 13.0, places=9)
        self.assertAlmostEqual(bb["BB_low"], 9.0, places=9)
        # sample sd would be sqrt(20/19) = 1.0260604 -> upper 13.052121: must be flagged
        self.assertFalse(cmp_.compare_value("BB", bb, {"BB_up": 11 + 2 * math.sqrt(20 / 19)})[0]["ok"])

    def test_run_counts_mismatches(self):
        pk = [{"id": "p1", "indicator": "RSI", "closes": [100.0 + i for i in range(500)]},
              {"id": "p2", "indicator": "BB", "closes": [50.0] * 480 + [10.0] * 10 + [12.0] * 10}]
        replies = {"p1": {"RSI": 99.5}, "p2": {"BB_mid": 11.0, "BB_up": 13.0, "BB_low": 9.0}}
        res = cmp_.run(pk, replies)
        self.assertEqual(res["n_values"], 4)
        self.assertEqual(res["n_mismatch"], 1)
        self.assertEqual(res["mismatches"][0]["packet"], "p1")
        # a packet with no reply at all is counted, not skipped
        res2 = cmp_.run(pk, {"p2": replies["p2"]})
        self.assertEqual(res2["n_mismatch"], 1)

    def test_other_routes_agree_on_hand_windows_and_catch_a_difference(self):
        # rising window: every route gives RSI 100; last 20 closes 10 x ten, 12 x ten: pop sd 1 -> upper 13 everywhere
        pk = [{"id": "r", "indicator": "RSI", "closes": [100.0 + i for i in range(500)]},
              {"id": "b", "indicator": "BB", "closes": [50.0] * 480 + [10.0] * 10 + [12.0] * 10}]
        self.assertEqual(cmp_.other_routes(pk), [])
        # engine route on a flat window is 50 (FORMULAS.md s1 step 4)
        self.assertEqual(cmp_.engine_values("RSI", [5.0] * 500)["RSI"], 50.0)
        # a planted sample-sd copy of the wlow route (upper 11 + 2*sqrt(20/19) = 13.052121) must be reported
        from unittest import mock
        with mock.patch("MyTradingSys.backtest.layers.wlow_bounce.detector.bollinger_upper",
                        return_value=[13.052121]):
            self.assertEqual([d["packet"] for d in cmp_.other_routes(pk[1:])], ["b"])


if __name__ == "__main__":
    unittest.main()
