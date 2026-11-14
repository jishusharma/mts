import sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cap_core as cc

class T(unittest.TestCase):
    def test_atr_pct_constant_range(self):
        n = 40
        c = np.full(n, 100.0); h = c + 1; l = c - 1
        a = cc.atr_pct(h, l, c)
        self.assertAlmostEqual(a[-1], 0.02, places=9)
        self.assertTrue(np.isnan(a[5]))

    @unittest.skipUnless(cc.CACHE.exists(), "needs F:\ caches")
    def test_counts_gate_blocks(self):
        import research_kit as rk
        r = rk.power_check(21, 13.0, 3.0, cost=rk.TAKER_RT_PCT)
        self.assertFalse(r["proceed"])
        self.assertEqual(len(cc.signals("BTC")) > 0, True)

if __name__ == "__main__":
    unittest.main()
