import math
import statistics
import itertools
from typing import List, Tuple

def sharpe(x: List[float]) -> float:
    """Calculate Sharpe ratio using population standard deviation."""
    if not x:
        return 0.0
    mean = sum(x) / len(x)
    pstdev = statistics.pstdev(x) if len(x) > 1 else 0.0
    return mean / pstdev if pstdev != 0.0 else 0.0

def ref_pbo_cscv(M: List[List[float]], S: int = 16) -> Tuple[float, List[float], List[float]]:
    """
    Compute PBO using Cross-Sectional Cross-Validation (CSCV).
    
    Args:
        M: List of T rows, each a list of N variant returns
        S: Number of blocks (must be even)
        
    Returns:
        Tuple of (pbo, log_odds_list, w_list)
    """
    if S < 2 or S % 2 != 0:
        raise ValueError("S must be even and >= 2")
    
    T = len(M)
    N = len(M[0]) if T > 0 else 0
    if T < 2 or N < 1:
        raise ValueError("matrix must have >= 2 rows and >= 1 column")
    if any(len(r) != N for r in M):
        raise ValueError("ragged matrix")
    if T < S:
        raise ValueError("T must be >= S")
    
    # Keep only the first (T//S)*S rows
    keep_rows = (T // S) * S
    M_subset = M[:keep_rows]
    T_subset = len(M_subset)
    
    # Split into S equal contiguous blocks
    block_size = T_subset // S
    blocks = [M_subset[i*block_size:(i+1)*block_size] for i in range(S)]
    
    # Generate all combinations of S/2 block indices
    half_S = S // 2
    combinations = list(itertools.combinations(range(S), half_S))
    
    log_odds_list = []
    w_list = []
    
    for combo in combinations:
        # IS blocks are those in combo, OOS blocks are the rest
        is_blocks = [blocks[i] for i in combo]
        oos_blocks = [blocks[i] for i in range(S) if i not in combo]
        
        # Flatten blocks to get rows
        is_rows = [row for block in is_blocks for row in block]
        oos_rows = [row for block in oos_blocks for row in block]
        
        # Compute Sharpe for each variant on IS and OOS
        is_sharpe = []
        oos_sharpe = []
        for n in range(N):
            is_returns = [row[n] for row in is_rows]
            oos_returns = [row[n] for row in oos_rows]
            
            is_sharpe.append(sharpe(is_returns))
            oos_sharpe.append(sharpe(oos_returns))
        
        # Find n_star (index of max IS sharpe)
        max_is_sharpe = max(is_sharpe)
        n_star = is_sharpe.index(max_is_sharpe)
        
        # Compute w
        oos_n_star = oos_sharpe[n_star]
        count_less = sum(1 for s in oos_sharpe if s < oos_n_star)
        w = (count_less + 1) / (N + 1)
        
        # Compute log_odds
        log_odds = math.log(w / (1 - w)) if 0 < w < 1 else float('-inf') if w == 0 else float('inf')
        
        log_odds_list.append(log_odds)
        w_list.append(w)
    
    # PBO is fraction of combinations with log_odds <= 0
    pbo = sum(1 for lo in log_odds_list if lo <= 0) / len(combinations)
    
    return (pbo, log_odds_list, w_list)

def iid_noise_experiment(T: int = 320, N: int = 10, S: int = 8, seeds: range = range(50)) -> List[float]:
    """
    Run iid noise experiment to test PBO computation.
    
    Args:
        T: Number of time periods
        N: Number of variants
        S: Number of blocks
        seeds: Range of random seeds
        
    Returns:
        List of PBO values for each seed
    """
    import random
    
    results = []
    for seed in seeds:
        rng = random.Random(seed)
        M = [[rng.gauss(0, 1) for _ in range(N)] for _ in range(T)]
        pbo, _, _ = ref_pbo_cscv(M, S)
        results.append(pbo)
    
    return results
