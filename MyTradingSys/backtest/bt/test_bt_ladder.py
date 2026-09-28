import unittest
from bt_ladder import fill_ladder as F
def B(t, o, h, l, c): return {"t": t, "o": o, "h": h, "l": l, "c": c}
R = [(100, 1), (99, 1), (98, 2)]
class C(unittest.TestCase):
    def test_two_fills(self):
        r = F("long", R, [B(1, 101, 101, 99.5, 100), B(2, 100, 100, 98.5, 99)], 0, 10)
        self.assertEqual(r["filled_size"], 2); self.assertAlmostEqual(r["avg_price"], 99.5)
    def test_gap(self):
        r = F("long", R, [B(1, 97, 97.5, 96.5, 97)], 0, 10)
        self.assertIn((1, 97, 2), [tuple(x) for x in r["filled"]])
    def test_deadline_and_signal_bar(self):
        r = F("long", R, [B(0, 100, 100, 90, 95), B(1, 101, 101, 100.5, 101), B(2, 101, 101, 97, 98)], 0, 1)
        self.assertEqual(r["filled_size"], 0); self.assertIsNone(r["avg_price"])
    def test_short(self):
        r = F("short", [(100, 1), (101, 1)], [B(1, 99, 100.5, 99, 100)], 0, 10)
        self.assertEqual(r["filled_size"], 1)
    def test_stop(self):
        r = F("long", R, [B(1, 101, 101, 99.5, 100), B(2, 99, 99, 97.4, 98), B(3, 98, 98, 90, 91)], 0, 10, stop=97.5)
        self.assertTrue(r["stopped_during_entry"]); self.assertEqual(r["filled_size"], 4)
if __name__ == "__main__": unittest.main()
