import unittest
import random
from ref_pbo import sharpe, pbo_cscv, pbo_cscv_ranks

class TestRefPbo(unittest.TestCase):
    def test_sharpe_wilson_free(self):
        # Test that sharpe matches manual computation to 9 decimal places
        x = [1, 2, 3, 4]
        computed = sharpe(x)
        mean_x = sum(x) / len(x)
        sd_x = (sum((xi - mean_x)**2 for xi in x) / len(x))**0.5
        expected = mean_x / sd_x if sd_x != 0 else 0.0
        self.assertAlmostEqual(computed, expected, places=9)

    def test_pbo_cscv_overfitting_case(self):
        # Create a matrix where variant 0 has returns 1.0 plus noise and others have 0.0 + same noise
        T, N, S = 64, 5, 8
        random.seed(42)
        r = random.Random(42)
        
        M = []
        for i in range(T):
            row = [1.0 + r.gauss(0, 1) if n == 0 else r.gauss(0, 1) for n in range(N)]
            M.append(row)
            
        pbo, _ = pbo_cscv(M, S)
        self.assertLess(pbo, 0.15)

    def test_pbo_cscv_iid_noise(self):
        # Test with pure iid Gaussian noise
        T, N, S = 320, 10, 8
        random.seed(7)
        r = random.Random(7)
        
        M = []
        for i in range(T):
            row = [r.gauss(0, 1) for _ in range(N)]
            M.append(row)
            
        pbo, log_odds = pbo_cscv(M, S)
        self.assertGreaterEqual(pbo, 0.0)
        self.assertLessEqual(pbo, 1.0)
        # Check that we have the right number of combinations
        import math
        expected_combinations = math.comb(S, S//2)
        self.assertEqual(len(log_odds), expected_combinations)

    def test_pbo_cscv_ranks_iid_noise(self):
        # Test ranks function on iid noise
        T, N, S = 320, 10, 8
        random.seed(7)
        r = random.Random(7)

        M = []
        for i in range(T):
            row = [r.gauss(0, 1) for _ in range(N)]
            M.append(row)

        result = pbo_cscv_ranks(M, S)
        import math  # expectation fixed per spec 020 line 25
        expected_combinations = math.comb(S, S//2)
        self.assertEqual(len(result), expected_combinations)
        
        for item in result:
            self.assertIn("n_star", item)
            self.assertIn("is_sharpes", item)
            self.assertIn("oos_sharpes", item)
            self.assertIn("oos_rank_of_n_star", item)
            self.assertIn("w", item)
            self.assertIn("log_odds", item)
            
            # Check ranges
            self.assertLessEqual(item["n_star"], N - 1)
            self.assertGreaterEqual(item["n_star"], 0)
            self.assertEqual(len(item["is_sharpes"]), N)
            self.assertEqual(len(item["oos_sharpes"]), N)
            self.assertLessEqual(item["oos_rank_of_n_star"], N)
            self.assertGreaterEqual(item["oos_rank_of_n_star"], 1)

    def test_pbo_cscv_odd_S_raises(self):
        T, N = 16, 5
        M = [[0.0] * N for _ in range(T)]
        with self.assertRaises(ValueError):
            pbo_cscv(M, S=3)  # odd

    def test_pbo_cscv_T_less_than_S_raises(self):
        T, N, S = 10, 5, 16
        M = [[0.0] * N for _ in range(T)]
        with self.assertRaises(ValueError):
            pbo_cscv(M, S=S)

if __name__ == '__main__':
    unittest.main()
