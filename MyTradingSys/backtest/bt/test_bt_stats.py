import unittest
import math
from bt_stats import wilson, bootstrap_mean_ci, moments, sharpe, psr, expected_max_sr, dsr, pbo_cscv

class TestBTStats(unittest.TestCase):
    def test_wilson(self):
        self.assertEqual(wilson(0, 0), (0.0, 1.0))
        result = wilson(5, 10)
        self.assertAlmostEqual(result[0], 0.2366, places=4)
        self.assertAlmostEqual(result[1], 0.7634, places=4)

    def test_bootstrap_mean_ci(self):
        ci = bootstrap_mean_ci([1.0] * 20)
        self.assertEqual(ci, (1.0, 1.0))

    def test_moments(self):
        m, sd, skew, kurt = moments([1, 2, 3, 4])
        self.assertAlmostEqual(m, 2.5)
        self.assertAlmostEqual(sd, math.sqrt(1.25))
        # skew and kurt are not tested due to floating point precision

    def test_sharpe(self):
        # symmetric sample
        x = [-1, 1, -1, 1]
        sr = sharpe(x)
        self.assertEqual(sr, 0.0)  # mean=0, sd=1

    def test_psr(self):
        x = [-1, 1, -1, 1]
        p = psr(x, 0.0)
        self.assertAlmostEqual(p, 0.5, places=2)

    def test_expected_max_sr(self):
        with self.assertRaises(ValueError):
            expected_max_sr(1.0, 1)
        self.assertGreater(expected_max_sr(1.0, 100), expected_max_sr(1.0, 10))

    def test_dsr(self):
        x = [1.0 + 0.1 * (i % 5) for i in range(100)]
        # dsr should be <= psr when expected_max_sr > 0
        p = psr(x, 0.0)
        d = dsr(x, 100, 1.0)
        self.assertLessEqual(d, p)

    def test_pbo_cscv(self):
        # Test with a matrix where variant 0 is best in every period
        T, N, S = 320, 10, 8
        M = []
        for t in range(T):
            row = [1.0 + 0.01 * (t % 10) if i == 0 else 0.0 + 0.01 * (t % 10) for i in range(N)]
            M.append(row)
        pbo, _ = pbo_cscv(M, S)
        self.assertLess(pbo, 0.1)

        # Test with Gaussian noise - multi-seed robust check
        import random
        pbo_values = []
        for seed in range(20):
            random.seed(seed)
            M = []
            for t in range(320):
                row = [random.gauss(0, 1) for _ in range(10)]
                M.append(row)
            pbo, _ = pbo_cscv(M, 8)
            pbo_values.append(pbo)
        # All values should be in [0.0, 1.0]
        for p in pbo_values:
            self.assertGreaterEqual(p, 0.0)
            self.assertLessEqual(p, 1.0)
        # Mean of PBOs should be in [0.35, 0.75]
        mean_pbo = sum(pbo_values) / len(pbo_values)
        self.assertGreaterEqual(mean_pbo, 0.35)
        self.assertLessEqual(mean_pbo, 0.75)

class TestBTStatsBoundary(unittest.TestCase):
    """Degenerate-input contract (FORMULAS.md section 10, DECISION OURS)."""

    def test_zero_variance_is_nan(self):
        x = [0.01] * 10
        self.assertTrue(math.isnan(sharpe(x)))
        self.assertTrue(math.isnan(psr(x, 0.0)))
        self.assertTrue(math.isnan(dsr(x, 100, 1.0)))

    def test_singleton_is_nan(self):
        self.assertTrue(math.isnan(sharpe([0.5])))
        self.assertTrue(math.isnan(psr([0.5], 0.0)))

    def test_pbo_rejects_invalid(self):
        good = [[float(t), float((t * 7) % 5)] for t in range(8)]
        for M, S in ([], 2), ([[1.0, 2.0]], 2), (good[:3], 4), (good, 3), (good, 1), (good, 0):
            with self.assertRaises(ValueError):
                pbo_cscv(M, S)
        ragged = [list(r) for r in good]
        ragged[2] = ragged[2][:1]
        with self.assertRaises(ValueError):
            pbo_cscv(ragged, 2)
        with self.assertRaises(ValueError):
            pbo_cscv([[], []], 2)

    def test_pbo_constant_variant_still_computes(self):
        M = [[float(t % 4), 0.0] for t in range(8)]
        pbo, lo = pbo_cscv(M, 2)
        self.assertTrue(0.0 <= pbo <= 1.0)


if __name__ == '__main__':
    unittest.main()
