import unittest
from bt_engine import simulate_trade as sim

def B(t, o, h, l, c): return {"t": t, "o": o, "h": h, "l": l, "c": c}
T = [(102.0, 0.5), (104.0, 0.5)]
M = 60000

class TestEngine(unittest.TestCase):
    def test01_targets(self):
        r = sim("long", 100, 0, 99, T, [B(M, 100, 102.5, 99.5, 102), B(2*M, 102, 104.5, 101, 104)], taker_fee=0)
        self.assertEqual(r["exit_reason"], "targets"); self.assertAlmostEqual(r["gross_r"], 3.0, places=9)
    def test02_stop(self):
        r = sim("long", 100, 0, 99, T, [B(M, 100, 100.5, 98.8, 99)])
        self.assertAlmostEqual(r["gross_r"], -1.0, places=9); self.assertEqual(r["exit_reason"], "stop")
    def test03_ambiguous(self):
        bars = [B(M, 100, 102.5, 98.5, 100)]
        r = sim("long", 100, 0, 99, T, bars, stop_first=True)
        self.assertAlmostEqual(r["gross_r"], -1.0, places=9); self.assertEqual(r["ambiguous_bars"], 1)
        r = sim("long", 100, 0, 99, T, bars, stop_first=False)
        self.assertAlmostEqual(r["gross_r"], 0.5, places=9); self.assertEqual(r["exit_reason"], "mixed")
    def test04_gap(self):
        r = sim("long", 100, 0, 99, T, [B(M, 98, 98.5, 97.5, 98)])
        self.assertAlmostEqual(r["gross_r"], -2.0, places=9)
    def test05_no_lookahead(self):
        r = sim("long", 100, M, 99, T, [B(M, 100, 100, 90, 95), B(2*M, 100, 104.5, 100, 104)])
        self.assertEqual(r["exit_reason"], "targets")
    def test06_mark_stop(self):
        r = sim("long", 100, 0, 99, T, [B(M, 100, 100.5, 98.9, 100), B(2*M, 100, 104.5, 100, 104)],
                mark_bars={M: {"h": 100.4, "l": 99.2}})
        self.assertEqual(r["exit_reason"], "targets")
    def test07_short(self):
        r = sim("short", 100, 0, 101, [(98.0, 0.5), (96.0, 0.5)], [B(M, 100, 100.5, 97.5, 98), B(2*M, 98, 99, 95.5, 96)])
        self.assertEqual(r["exit_reason"], "targets"); self.assertAlmostEqual(r["gross_r"], 3.0, places=9)
    def test08_funding(self):
        bars = [B(M, 100, 100.5, 99.5, 100), B(2*M, 100, 104.5, 100, 104)]
        f = [(M + 30000, 0.0001)]
        rl = sim("long", 100, 0, 99, T, bars, funding=f)
        self.assertAlmostEqual(rl["funding_paid_pct"], 0.01, places=9)
        rs = sim("short", 100, 0, 101, [(98.0, 0.5), (96.0, 0.5)], [B(M, 100, 100.5, 99.5, 100), B(2*M, 100, 100, 95, 96)], funding=f)
        self.assertAlmostEqual(rs["funding_paid_pct"], -0.01, places=9)
    def test09_bad_fractions(self):
        with self.assertRaises(ValueError): sim("long", 100, 0, 99, [(102, 0.5), (104, 0.4)], [])
    def test10_timeout(self):
        bars = [B(i*M, 100, 100.5, 99.5, 100 + i/10) for i in range(1, 6)]
        r = sim("long", 100, 0, 99, T, bars, max_bars=3)
        self.assertEqual(r["exit_reason"], "timeout"); self.assertEqual(r["exit_t"], 3*M)
        self.assertAlmostEqual(r["gross_r"], 0.3, places=9)
    def test11_fees(self):
        r = sim("long", 100, 0, 99, T, [B(M, 100, 100.5, 98.8, 99)], taker_fee=0.0005)
        self.assertAlmostEqual(r["net_r"], -1.0 - 0.0005*100 - 0.0005*99, places=9)
    def test12_open_at_end(self):
        r = sim("long", 100, 0, 99, T, [B(M, 100, 100.5, 99.5, 100)])
        self.assertEqual(r["exit_reason"], "open_at_end"); self.assertIsNone(r["net_r"])

    def test13_target_touch_does_not_fill_with_target_through(self):
        # B151: a resting target limit fills only when price trades THROUGH it by the tick; touch leaves the trade open
        bars = [B(M, 100, 102.0, 99.5, 101), B(2*M, 101, 102.05, 100.5, 101)]
        touch = sim("long", 100, 0, 99, [(102.0, 1.0)], bars, taker_fee=0, target_through=0.1)
        self.assertEqual(touch["exit_reason"], "open_at_end")
        bars2 = bars + [B(3*M, 101, 102.1, 100.5, 101)]
        thru = sim("long", 100, 0, 99, [(102.0, 1.0)], bars2, taker_fee=0, target_through=0.1)
        self.assertEqual(thru["exit_reason"], "targets"); self.assertAlmostEqual(thru["gross_r"], 2.0, places=9)
        # default 0.0 keeps the old touch rule
        self.assertEqual(sim("long", 100, 0, 99, [(102.0, 1.0)], bars, taker_fee=0)["exit_reason"], "targets")
    def test14_short_target_through(self):
        bars = [B(M, 100, 100.5, 98.0, 99), B(2*M, 99, 99.5, 97.95, 99)]
        self.assertEqual(sim("short", 100, 0, 101, [(98.0, 1.0)], bars, taker_fee=0, target_through=0.1)["exit_reason"], "open_at_end")
        bars.append(B(3*M, 99, 99.5, 97.9, 99))
        self.assertEqual(sim("short", 100, 0, 101, [(98.0, 1.0)], bars, taker_fee=0, target_through=0.1)["exit_reason"], "targets")

if __name__ == "__main__":
    unittest.main()
