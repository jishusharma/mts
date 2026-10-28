"""Tests for intrabar_bounds.py. Expected numbers are hand-derived: long entry 100, stop 99 (risk 1 = 1R), target 102 (2R);
the planted bar (o 100, h 102.5, l 98.5, c 100) holds both. Zero fees, so net R = gross R: stop-first -1, target-first +2.
Shorts mirror: entry 100, stop 101, target 98, bar (100, 101.5, 97.5, 100)."""
import sys
import unittest
from array import array
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import intrabar_bounds as B  # noqa: E402

ZERO = dict(entry=0.0, stop=0.0, target=0.0, timeout=0.0)


def tom_bars(rows):
    o, h, l, c, v, tbv = (array("d") for _ in range(6))
    for a, b, d, e in rows:
        o.append(a); h.append(b); l.append(d); c.append(e); v.append(1.0); tbv.append(0.5)
    import tom_bt as T
    return T.Bars1m(0, o, h, l, c, v, tbv)


class PlantedBar(unittest.TestCase):
    def test_tom_long(self):
        b = tom_bars([(100, 100.2, 99.9, 100), (100, 102.5, 98.5, 100)])
        s = B.tom_trade(b, 0, "long", 100.0, 99.0, 102.0, "stop", fees=ZERO)
        t = B.tom_trade(b, 0, "long", 100.0, 99.0, 102.0, "target", fees=ZERO)
        self.assertEqual((s["reason"], round(s["net_r"], 9), s["ambiguous"]), ("stop", -1.0, 1))
        self.assertEqual((t["reason"], round(t["net_r"], 9)), ("target", 2.0))

    def test_tom_short(self):
        b = tom_bars([(100, 100.1, 99.8, 100), (100, 101.5, 97.5, 100)])
        s = B.tom_trade(b, 0, "short", 100.0, 101.0, 98.0, "stop", fees=ZERO)
        t = B.tom_trade(b, 0, "short", 100.0, 101.0, 98.0, "target", fees=ZERO)
        self.assertEqual(round(s["net_r"], 9), -1.0)
        self.assertEqual(round(t["net_r"], 9), 2.0)

    def test_bt_engine(self):
        bars = [{"t": 60000, "o": 100, "h": 102.5, "l": 98.5, "c": 100}]
        kw = dict(side="long", entry_price=100.0, entry_t=0, stop=99.0, targets=[(102.0, 1.0)], bars=bars,
                  funding=[], taker_fee=0.0, maker_fee=0.0)
        self.assertEqual(round(B.engine_trade("stop", **kw)["net_r"], 9), -1.0)
        self.assertEqual(round(B.engine_trade("target", **kw)["net_r"], 9), 2.0)

    def test_fabio_manage_and_installed_models(self):
        from MyTradingSys.backtest.layers.fabio.v3 import manage, models
        bars = [{"t": 0, "o": 100, "h": 100.2, "l": 99.9, "c": 100}, {"t": 60000, "o": 100, "h": 102.5, "l": 98.5, "c": 100}]
        kw = dict(bars=bars, fill_idx=0, s=1, entry=100.0, D=1.0, stop=99.0, target=102.0, end_idx=1)
        self.assertEqual(round(manage.simulate_trade(stop_first=True, **kw)["gross_r"], 9), -1.0)
        self.assertEqual(round(manage.simulate_trade(stop_first=False, **kw)["gross_r"], 9), 2.0)
        orig = models.simulate_trade
        try:
            B.install_fabio("target")
            self.assertEqual(round(models.simulate_trade(**kw)["gross_r"], 9), 2.0)
            B.install_fabio("stop")
            self.assertEqual(round(models.simulate_trade(**kw)["gross_r"], 9), -1.0)
        finally:
            models.simulate_trade = orig

    def test_unforced_default_is_stop_first(self):
        """Not forcing the resolver leaves the shipped stop-first result, so a target-first bound needs the force."""
        b = tom_bars([(100, 100.2, 99.9, 100), (100, 102.5, 98.5, 100)])
        import tom_bt as T
        d = T.sim_limit_trade(b, 0, "long", 100.0, 99.0, 102.0, 5, 5, ZERO)
        self.assertEqual(round(d["net_r"], 9), -1.0)
        self.assertNotEqual(round(d["net_r"], 9), 2.0)

    def test_bad_mode_fails_closed(self):
        with self.assertRaises(ValueError):
            B.stop_first_of("maybe")


class Rows(unittest.TestCase):
    def test_sign_flip_and_gap(self):
        line, flip = B.row("x", 10, 3, dict(n=10, mean=-0.1), dict(n=10, mean=0.2))
        self.assertTrue(flip)
        self.assertIn("+0.3000", line)
        _, flip = B.row("x", 10, 3, dict(n=10, mean=-0.1), dict(n=10, mean=-0.05))
        self.assertFalse(flip)
        _, flip = B.row("x", 0, 0, dict(n=0, mean=None), dict(n=0, mean=None))
        self.assertFalse(flip)


if __name__ == "__main__":
    unittest.main()
