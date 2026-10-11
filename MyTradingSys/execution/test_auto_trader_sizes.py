"""Offline tests for per-source size overrides (testnet calibration, operator 2026-10-07: "Use amounts ranging from
20 to 1000 $", base "$20"). No exchange, no subprocess.
Run: python -m pytest MyTradingSys/execution/test_auto_trader_sizes.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_trader as at  # noqa: E402
import test_auto_trader as _base  # noqa: E402

NOW, cfg, T15 = _base.NOW, _base.cfg, _base.LayerSignalTest.T15
SHIPPED = Path(__file__).resolve().parent / "auto_trader_config.json"


def arg(sig, flag):
    a = sig["plan_args"]
    return a[a.index(flag) + 1]


def alert(layer="rsi", sub="rsi_events", tf="15m"):
    return {"layer": layer, "sub": sub, "event": "support", "side": "long", "tf": tf, "t_close": T15}


class SizeOverrideTest(unittest.TestCase):
    def test_no_override_uses_layers_size(self):
        c = cfg()
        s = at.layer_signal(alert(), c, NOW)
        self.assertEqual(arg(s, "--size"), str(c["layers"]["size_usd"]))
        self.assertEqual(arg(s, "--max-loss"), str(c["layers"]["max_loss_usd"]))

    def test_override_sets_size_and_max_loss(self):
        c = cfg()
        c["size_overrides"] = {"layer:rsi:rsi_events:15m": {"size_usd": 500, "max_loss_usd": 10}}
        s = at.layer_signal(alert(), c, NOW)
        self.assertEqual((arg(s, "--size"), arg(s, "--max-loss")), ("500", "10"))

    def test_longest_prefix_wins(self):
        c = cfg()
        c["size_overrides"] = {"layer:rsi:": {"size_usd": 50, "max_loss_usd": 2},
                               "layer:rsi:rsi_events:15m": {"size_usd": 1000, "max_loss_usd": 20}}
        self.assertEqual(arg(at.layer_signal(alert(), c, NOW), "--size"), "1000")
        self.assertEqual(arg(at.layer_signal(alert(tf="1h", sub="malkan_bull"), c, NOW), "--size"), "50")

    def test_malformed_override_rejects_signal(self):
        for bad in ({"size_usd": 15, "max_loss_usd": 2},      # not a 10 USD contract multiple
                    {"size_usd": 0, "max_loss_usd": 2},
                    {"size_usd": 20000, "max_loss_usd": 2},   # above trade_plan_validator ceiling
                    {"size_usd": 100},                         # max loss missing
                    {"size_usd": 100, "max_loss_usd": -1},
                    "100"):
            c = cfg()
            c["size_overrides"] = {"layer:rsi:": bad}
            s = at.layer_signal(alert(), c, NOW)
            self.assertIn("reject", s, repr(bad))
            self.assertNotIn("plan_args", s)

    def test_malformed_override_table_rejects_signal(self):
        c = cfg()
        c["size_overrides"] = ["layer:rsi:"]
        self.assertIn("reject", at.layer_signal(alert(), c, NOW))

    def test_shipped_overrides_span_20_to_1000_and_cover_stop(self):
        c = at.load_config(SHIPPED)
        sizes = [v["size_usd"] for v in c["size_overrides"].values()]
        self.assertEqual((min(sizes), max(sizes)), (20, 1000))
        stop = c["layers"]["stop_pct"] / 100
        for prefix, v in c["size_overrides"].items():
            self.assertEqual(at.size_override(prefix, c), (v["size_usd"], v["max_loss_usd"]))
            self.assertGreaterEqual(v["max_loss_usd"], v["size_usd"] * stop * 1.5, prefix)   # stop + fees/slippage room


if __name__ == "__main__":
    unittest.main()
