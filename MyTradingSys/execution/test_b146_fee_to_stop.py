"""B146: tom.max_fee_to_stop rejects Tom signals whose worst-case round-trip fee is too big a share of the stop distance.
Expected numbers hand-computed: entry 83537.3, stop 83704.37 -> distance 167.07; fee 0.0010 * 83537.3 = 83.5373 -> 0.500 R."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_trader as at  # noqa: E402
from test_auto_trader import NOW, cfg, tom_alert  # noqa: E402


class FeeToStopTest(unittest.TestCase):
    def sig(self, cut, **kw):
        c = cfg()
        if cut is not None:
            c["tom"]["max_fee_to_stop"] = cut
        return at.tom_signal(tom_alert(**kw), {"tom_last_alert_no": 0}, c, NOW)

    def test_default_is_off(self):
        self.assertNotIn("reject", self.sig(None))

    def test_wide_enough_stop_passes_and_tight_stop_rejects(self):
        self.assertNotIn("reject", self.sig(0.6))                    # 0.500 R <= 0.6
        self.assertIn("fee/stop 0.50 R > 0.3 R", self.sig(0.3)["reject"])

    def test_tiny_stop_rejected(self):
        # stop 7.7 away: fee 83.5373 / 7.7 = 10.85 R
        s = self.sig(0.3, stop=83545.0, target=82985.43, setup="ct_long", entry=83537.3)
        self.assertTrue(s["reject"].startswith("entry/stop/target not ordered") or "fee/stop" in s["reject"])
        s = self.sig(0.3, stop=83529.6, target=84000.0, setup="ct_long")
        self.assertIn("fee/stop 10.85 R", s["reject"])

    def test_shipped_config_has_the_gate_on_at_0_3(self):
        # operator decision D09 2026-10-09: "Switch on at 0.3". The code default stays off (test_default_is_off).
        cfg_file = Path(__file__).resolve().parent / "auto_trader_config.json"
        loaded = at.load_config(cfg_file)
        self.assertEqual(loaded["tom"].get("max_fee_to_stop"), 0.3)
        sig = at.tom_signal(tom_alert(stop=83529.6, target=84000.0, setup="ct_long"), {"tom_last_alert_no": 0}, loaded, NOW)
        self.assertIn("fee/stop", sig["reject"])

    def test_bad_cut_fails_closed(self):
        self.assertIn("misconfigured", self.sig("abc")["reject"])
        self.assertIn("misconfigured", self.sig(0)["reject"])


if __name__ == "__main__":
    unittest.main()
