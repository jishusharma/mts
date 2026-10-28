import unittest
from ref_pbo import ref_pbo_cscv, iid_noise_experiment, sharpe

class TestRefPBO(unittest.TestCase):
    
    def test_sharpe(self):
        # Test normal case
        self.assertAlmostEqual(sharpe([1.0, 2.0, 3.0]), 2.449489742783178, places=9)

        # Test zero std dev
        self.assertEqual(sharpe([1.0, 1.0, 1.0]), 0.0)  # expectation fixed per spec 020 line 16
        
        # Test zero std dev with zero mean
        self.assertEqual(sharpe([0.0, 0.0, 0.0]), 0.0)
        
        # Test empty list
        self.assertEqual(sharpe([]), 0.0)
    
    def test_ref_pbo_cscv_odd_S(self):
        # S must be even, so odd should raise ValueError
        M = [[1.0, 2.0], [3.0, 4.0]]
        with self.assertRaises(ValueError):
            ref_pbo_cscv(M, S=3)
    
    def test_ref_pbo_cscv_normal_case(self):
        # Simple test case
        M = [
            [1.0, 0.0],
            [2.0, 0.0],
            [3.0, 0.0],
            [4.0, 0.0]
        ]
        pbo, log_odds_list, w_list = ref_pbo_cscv(M, S=2)
        
        # Should have 2 combinations (C(2,1))
        self.assertEqual(len(log_odds_list), 2)
        self.assertEqual(len(w_list), 2)
        
        # PBO should be between 0 and 1
        self.assertGreaterEqual(pbo, 0.0)
        self.assertLessEqual(pbo, 1.0)
    
    def test_ref_pbo_cscv_with_noise(self):
        # Create a matrix where variant 0 is consistently better than others
        M = []
        for t in range(100):
            row = [1.0 + 0.1 * (t % 2) + 0.1 * (t % 3) if n == 0 else 
                   0.1 * (t % 2) + 0.1 * (t % 3) for n in range(5)]
            M.append(row)
        
        pbo, log_odds_list, w_list = ref_pbo_cscv(M, S=4)
        
        # Should have 6 combinations (C(4,2))
        self.assertEqual(len(log_odds_list), 6)
        self.assertEqual(len(w_list), 6)
        
        # All w values should be strictly between 0 and 1
        for w in w_list:
            self.assertGreater(w, 0.0)
            self.assertLess(w, 1.0)
            
        # PBO should be less than 0.5 (since variant 0 is better)
        self.assertLess(pbo, 0.5)
    
    def test_iid_noise_experiment(self):
        # Test that it returns correct number of results
        results = iid_noise_experiment(seeds=range(3))
        self.assertEqual(len(results), 3)
        
        # All results should be in [0,1]
        for pbo in results:
            self.assertGreaterEqual(pbo, 0.0)
            self.assertLessEqual(pbo, 1.0)

class TestRefPBOBoundary(unittest.TestCase):
    """Degenerate-input contract (FORMULAS.md section 10, DECISION OURS)."""

    def _ok(self, T=8, N=2):
        return [[float(t + n * (t % 3)) for n in range(N)] for t in range(T)]

    def test_ref_pbo_rejects_T_less_than_S(self):
        with self.assertRaises(ValueError):
            ref_pbo_cscv(self._ok(T=4), S=8)

    def test_rejects_S_below_2_and_odd(self):
        for S in (0, 1, 3, -2):
            with self.assertRaises(ValueError):
                ref_pbo_cscv(self._ok(), S=S)

    def test_rejects_ragged_matrix(self):
        M = self._ok()
        M[3] = M[3][:1]
        with self.assertRaises(ValueError):
            ref_pbo_cscv(M, S=2)

    def test_rejects_empty_and_singleton(self):
        with self.assertRaises(ValueError):
            ref_pbo_cscv([], S=2)
        with self.assertRaises(ValueError):
            ref_pbo_cscv([[1.0, 2.0]], S=2)
        with self.assertRaises(ValueError):
            ref_pbo_cscv([[], []], S=2)


if __name__ == '__main__':
    unittest.main()
