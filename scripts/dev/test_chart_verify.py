import sys, pathlib, unittest, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import chart_verify as cv


def fixture40():
    rnd = random.Random(7)
    c, out = 100.0, []
    for _ in range(40):
        c += rnd.uniform(-2, 2)
        out.append(round(c, 4))
    return out


class T(unittest.TestCase):
    # FORMULAS.md s22 worked example (n=4, mult=2)
    def test_bb_hand_values(self):
        up, mid, lo = cv.bollinger([8, 10, 10, 12, 14, 12], n=4, mult=2.0)
        self.assertEqual(up[:3], [None] * 3)
        self.assertAlmostEqual(up[3], 12.828427, places=5)
        self.assertAlmostEqual(lo[3], 7.171573, places=5)
        self.assertAlmostEqual(mid[5], 12.0, places=9)
        self.assertAlmostEqual(up[5], 14.828427, places=5)
        self.assertAlmostEqual(lo[5], 9.171573, places=5)

    # FORMULAS.md s1 / 21.7 / s23: RSI period 2
    def test_rsi_hand_values(self):
        r = cv.rsi([10, 11, 10, 12, 11, 13], 2)
        self.assertAlmostEqual(r[2], 50.0, places=9)
        self.assertAlmostEqual(r[3], 83.33333, places=4)
        self.assertAlmostEqual(r[4], 50.0, places=9)
        self.assertAlmostEqual(r[5], 80.76923, places=4)

    # FORMULAS.md s23 worked example
    def test_stochrsi_hand_values(self):
        k, d = cv.stochrsi([10, 11, 10, 12, 11, 13], 2, 3, 1, 1)
        self.assertAlmostEqual(k[4], 0.0, places=9)
        self.assertAlmostEqual(k[5], 92.30769, places=4)
        k2, _ = cv.stochrsi([10, 11, 10, 12, 11, 13], 2, 3, 2, 1)
        self.assertAlmostEqual(k2[5], 46.15385, places=4)

    def test_rsi_40_bar_independent_wilder(self):
        c = fixture40()
        n = 14
        d = [c[i] - c[i - 1] for i in range(1, len(c))]
        ag = sum(max(x, 0) for x in d[:n]) / n
        al = sum(max(-x, 0) for x in d[:n]) / n
        exp = [100 - 100 / (1 + ag / al)]
        for x in d[n:]:
            ag = (ag * (n - 1) + max(x, 0)) / n
            al = (al * (n - 1) + max(-x, 0)) / n
            exp.append(100 - 100 / (1 + ag / al))
        r = cv.rsi(c, n)
        self.assertEqual(r[:n], [None] * n)
        for a, b in zip(r[n:], exp):
            self.assertAlmostEqual(a, b, places=9)

    def test_bb_40_bar_population_sd(self):
        import statistics
        c = fixture40()
        up, mid, lo = cv.bollinger(c)
        w = c[-20:]
        self.assertAlmostEqual(up[-1], statistics.fmean(w) + 2 * statistics.pstdev(w), places=9)
        self.assertAlmostEqual(lo[-1], statistics.fmean(w) - 2 * statistics.pstdev(w), places=9)

    def test_stochrsi_40_bar_in_range_and_warmup(self):
        k, d = cv.stochrsi(fixture40())
        first = 14 + 14 - 1 + 3 - 1
        self.assertEqual([i for i, v in enumerate(k) if v is not None][0], first)
        self.assertTrue(all(0 <= v <= 100 for v in k if v is not None))

    def test_compare_lines(self):
        calc = {"RSI": 69.2, "BB_up": 81146.6}
        lines = cv.compare(calc, {"RSI": 69.0, "BB_up": 81100.0}, tol_rsi=0.5, tol_stoch=1.0, tol_bb_pct=0.01)
        self.assertTrue(lines[0].endswith("MATCH") and "RSI" in lines[0])
        self.assertTrue(lines[1].endswith("MISMATCH"))


if __name__ == "__main__":
    unittest.main()
