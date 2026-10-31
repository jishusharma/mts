import sys
sys.dont_write_bytecode = True
"""sim.py core unit tests (plan ranks 1, 2, 6, 8: research/gemini_burn_2026-10-31/BACKTEST_CORE_TEST_PLAN.md).

Expected numbers are worked by hand from FORMULAS.md 18.5 (gross_R = side*(exit-L)/R, fee in price terms), never from sim.py.
Fee rates are the fees.py values, passed explicitly: taker 0.0005, maker 0.0 (Deribit BTC-PERPETUAL, SOURCED fees.py:23-24).
Geometry long 100 / stop 99 / target 103 is OURS (risk 1, target 3R).

Hand arithmetic (fee_R = (taker + exit_fee) * entry / risk):
  target: gross +3.0; fee_R = (0.0005 + 0.0) * 100 / 1 = 0.05      -> net 2.95
  stop  : gross -1.0 (observed fill 99); fee_R = 0.001 * 100 / 1 = 0.10 -> net -1.10
Wilson 5/10, z 1.96: d = 1 + 3.8416/10 = 1.38416; c = 0.5 + 3.8416/20 = 0.69208;
  h = 1.96*sqrt(0.025 + 3.8416/400) = 1.96*0.186021 = 0.364601; lo = (0.69208-0.364601)/1.38416 = 0.23659, hi = 0.76341.
"""
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim  # noqa: E402

TAKER, MAKER = 0.0005, 0.0


def row(t, price, verdict="SETUP_FORMING", d="long", stop=99, target=103):
    return dict(ts="t%d" % t, t=t, setup="s", dir=d, price=price, stop=stop, target=target, verdict=verdict)


class TestSimCore(unittest.TestCase):
    def test_target_hit_net_r(self):
        tr = sim.run([row(0, 100), row(60, 101), row(120, 103)], "A", "observed", TAKER, MAKER)
        self.assertEqual(len(tr), 1)
        self.assertEqual(tr[0]["kind"], "target")
        self.assertAlmostEqual(tr[0]["gross"], 3.0, places=9)
        self.assertAlmostEqual(tr[0]["net"], 2.95, places=9)

    def test_stop_checked_before_target(self):
        # stop print (99) comes before the target print (103): the trade is a stop, never a target
        tr = sim.run([row(0, 100), row(60, 99), row(120, 103)], "A", "observed", TAKER, MAKER)
        self.assertEqual([x["kind"] for x in tr], ["stop"])
        self.assertAlmostEqual(tr[0]["gross"], -1.0, places=9)
        self.assertAlmostEqual(tr[0]["net"], -1.10, places=9)

    def test_geom_ok_rejects_stop_equal_entry(self):
        self.assertFalse(sim.geom_ok("long", 100, 100, 103))
        self.assertFalse(sim.geom_ok("short", 100, 100, 97))
        self.assertTrue(sim.geom_ok("long", 100, 99, 103))
        self.assertTrue(sim.geom_ok("short", 100, 101, 97))

    def test_zero_risk_row_opens_no_trade(self):
        rows = [row(0, 100, stop=100), row(60, 103)]
        self.assertEqual(sim.run(rows, "A", "observed", TAKER, MAKER), [])

    def test_run_rejects_out_of_order_rows(self):
        rows = [row(0, 100), row(120, 101), row(60, 103)]
        with self.assertRaises(ValueError):
            sim.run(rows, "A", "observed", TAKER, MAKER)

    def test_equal_timestamps_are_allowed(self):
        tr = sim.run([row(0, 100), row(0, 101), row(60, 103)], "A", "observed", TAKER, MAKER)
        self.assertEqual([x["kind"] for x in tr], ["target"])

    def test_wilson_k_greater_than_n_raises_clear_error(self):
        for k, n in ((5, 3), (-1, 3), (1, -2)):
            with self.assertRaises(ValueError) as cm:
                sim.wilson(k, n)
            self.assertIn("k=%d" % k, str(cm.exception))
            self.assertIn("n=%d" % n, str(cm.exception))

    def test_wilson_valid_values(self):
        self.assertEqual(sim.wilson(0, 0), (0.0, 0.0))
        lo, hi = sim.wilson(5, 10)
        self.assertAlmostEqual(lo, 0.23659, places=4)
        self.assertAlmostEqual(hi, 0.76341, places=4)


if __name__ == "__main__":
    unittest.main()
