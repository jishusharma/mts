"""T06-F3 canary tests. Run: python -m pytest MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T06/test_fill_canary.py
Expected prices are worked by hand: stop 99.00, gap open = 99.00 * 0.99 = 98.01.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fill_canary as C  # noqa: E402


class FillCanary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = C.run_canary()

    def get(self, prefix, scen):
        return [r for r in self.rows if r["engine"].startswith(prefix) and r["scenario"] == scen]

    def test_tom_fills_at_open_on_fill_bar_and_canary_reports_it(self):
        r = self.get("tom_bt", "F")[0]
        self.assertAlmostEqual(r["fill"], 98.01, places=9)
        self.assertTrue(r["at_open"] and not r["at_stop"])
        self.assertNotIn("tom_bt.sim_limit_trade [F]", C.verdict(self.rows))   # worse fill is not flagged optimistic

    def test_fabio_fill_bar_fills_at_stop_price(self):
        r = self.get("fabio", "F")[0]
        self.assertAlmostEqual(r["fill"], 99.0, places=9)
        self.assertTrue(r["at_stop"])

    def test_post_fill_gap_fills_at_open_for_engines_that_scan_forward(self):
        for p in ("bt_engine", "run_rsi", "fabio", "tom_bt"):
            self.assertAlmostEqual(self.get(p, "P")[0]["fill"], 98.01, places=9, msg=p)

    def test_sim_modes(self):
        by = {r["engine"]: r["fill"] for r in self.rows if r["engine"].startswith("sim.run")}
        self.assertAlmostEqual(by["sim.run (--stops observed)"], 98.01, places=9)
        self.assertAlmostEqual(by["sim.run (--stops ideal)"], 99.0, places=9)

    def test_no_default_slippage_anywhere(self):
        for r in self.rows:
            self.assertIn(r["slip"], (None, 0.0), r["engine"])

    def test_verdict_counts_two_engines(self):
        v = C.verdict(self.rows)
        self.assertEqual(sorted(v), ["fabio v3 manage.walk_trade [F]", "sim.run (--stops ideal) [P]"])
        self.assertIn("**Verdict: 2 engine(s)", C.render(self.rows))

    def test_signature_change_fails_the_canary(self):
        fns = C._fns(C._load())
        C.check_signatures(fns)                       # unchanged: passes

        def changed(bars, fill_idx, s, entry, D, stop, slippage=0.0):
            pass
        fns["fabio_v3.walk_trade"] = changed
        with self.assertRaises(RuntimeError):
            C.check_signatures(fns)


if __name__ == "__main__":
    unittest.main()
