import math
import statistics
import random
import itertools

def moments(x):
    """Compute mean, standard deviation, skewness, kurtosis of x.
    
    Returns:
        tuple: (mean, sd, skew, kurt)
    """
    n = len(x)
    if n == 0:
        return (0.0, 0.0, 0.0, 0.0)
    m = sum(x) / n
    if n == 1:
        return (m, 0.0, 0.0, 3.0)
    sd = math.sqrt(sum((xi - m)**2 for xi in x) / n)
    if sd == 0:
        return (m, 0.0, 0.0, 3.0)
    # skew
    z = [((xi - m) / sd) ** 3 for xi in x]
    skew = sum(z) / n
    # kurt
    z2 = [((xi - m) / sd) ** 4 for xi in x]
    kurt = sum(z2) / n
    return (m, sd, skew, kurt)

def sharpe(x):
    """Compute Sharpe ratio of x.
    
    Returns:
        float: mean/sd, or 0.0 if sd == 0
    """
    m, sd, _, _ = moments(x)
    if sd == 0:
        return 0.0
    return m / sd

def pbo_cscv(M, S=16):
    """Compute PBO using Cross-Sectional CV (CSCV).
    
    Args:
        M: list of T rows, each row a list of N strategy-variant returns for that period
        S: number of blocks to split into (must be even, >= 2)
        
    Returns:
        tuple: (pbo, log_odds) where pbo is fraction of combinations with log_odds <= 0,
                and log_odds is list of per-combination log_odds values
    """
    T = len(M)
    N = len(M[0]) if T > 0 else 0
    
    if S % 2 != 0 or S < 2:
        raise ValueError("S must be even and >= 2")
    if T < S:
        raise ValueError("T must be >= S")
        
    # Drop remainder rows
    drop = T % S
    if drop > 0:
        M = M[:-drop]
    T = len(M)
    
    # Split into S blocks
    block_size = T // S
    blocks = [M[i*block_size:(i+1)*block_size] for i in range(S)]
    
    # Generate combinations of S/2 blocks
    half_S = S // 2
    combinations = list(itertools.combinations(range(S), half_S))
    
    log_odds_list = []
    
    for combo in combinations:
        # IS = concatenated rows of those blocks
        is_blocks = [blocks[i] for i in combo]
        is_rows = [row for block in is_blocks for row in block]
        
        # OOS = concatenated rows of remaining blocks
        oos_blocks = [blocks[i] for i in range(S) if i not in combo]
        oos_rows = [row for block in oos_blocks for row in block]
        
        # Compute sharpe for each variant in IS and OOS
        is_sharpes = []
        oos_sharpes = []
        for n in range(N):
            is_returns = [row[n] for row in is_rows]
            oos_returns = [row[n] for row in oos_rows]
            
            is_sharpes.append(sharpe(is_returns))
            oos_sharpes.append(sharpe(oos_returns))
        
        # Find n_star (index of variant with highest IS sharpe)
        max_is_sharpe = max(is_sharpes)
        n_star = is_sharpes.index(max_is_sharpe)  # First occurrence on ties
        
        # Compute w = relative rank of n_star's OOS sharpe
        oos_sharpe_n_star = oos_sharpes[n_star]
        count_less = sum(1 for s in oos_sharpes if s < oos_sharpe_n_star)
        w = (count_less + 1) / (N + 1)
        
        # Compute log_odds
        if w == 0:
            log_odds = -1e9
        elif w == 1:
            log_odds = 1e9
        else:
            log_odds = math.log(w / (1 - w))
            
        log_odds_list.append(log_odds)
    
    # Compute PBO as fraction of combinations with log_odds <= 0
    pbo = sum(1 for lo in log_odds_list if lo <= 0) / len(log_odds_list)
    
    return (pbo, log_odds_list)

def pbo_cscv_ranks(M, S=16):
    """Compute PBO diagnostics including ranks.
    
    Returns:
        list of dicts: one per combination
    """
    T = len(M)
    N = len(M[0]) if T > 0 else 0
    
    if S % 2 != 0 or S < 2:
        raise ValueError("S must be even and >= 2")
    if T < S:
        raise ValueError("T must be >= S")
        
    # Drop remainder rows
    drop = T % S
    if drop > 0:
        M = M[:-drop]
    T = len(M)
    
    # Split into S blocks
    block_size = T // S
    blocks = [M[i*block_size:(i+1)*block_size] for i in range(S)]
    
    # Generate combinations of S/2 blocks
    half_S = S // 2
    combinations = list(itertools.combinations(range(S), half_S))
    
    result = []
    
    for combo in combinations:
        # IS = concatenated rows of those blocks
        is_blocks = [blocks[i] for i in combo]
        is_rows = [row for block in is_blocks for row in block]
        
        # OOS = concatenated rows of remaining blocks
        oos_blocks = [blocks[i] for i in range(S) if i not in combo]
        oos_rows = [row for block in oos_blocks for row in block]
        
        # Compute sharpe for each variant in IS and OOS
        is_sharpes = []
        oos_sharpes = []
        for n in range(N):
            is_returns = [row[n] for row in is_rows]
            oos_returns = [row[n] for row in oos_rows]
            
            is_sharpes.append(sharpe(is_returns))
            oos_sharpes.append(sharpe(oos_returns))
        
        # Find n_star (index of variant with highest IS sharpe)
        max_is_sharpe = max(is_sharpes)
        n_star = is_sharpes.index(max_is_sharpe)  # First occurrence on ties
        
        # Compute w = relative rank of n_star's OOS sharpe
        oos_sharpe_n_star = oos_sharpes[n_star]
        count_less = sum(1 for s in oos_sharpes if s < oos_sharpe_n_star)
        w = (count_less + 1) / (N + 1)
        
        # Compute log_odds
        if w == 0:
            log_odds = -1e9
        elif w == 1:
            log_odds = 1e9
        else:
            log_odds = math.log(w / (1 - w))
            
        # Compute OOS rank of n_star (1-based, where 1 = worst OOS sharpe)
        sorted_oos_sharpes = sorted(oos_sharpes, reverse=True)
        oos_rank_of_n_star = sorted_oos_sharpes.index(oos_sharpe_n_star) + 1
        
        result.append({
            "n_star": n_star,
            "is_sharpes": is_sharpes,
            "oos_sharpes": oos_sharpes,
            "oos_rank_of_n_star": oos_rank_of_n_star,
            "w": w,
            "log_odds": log_odds
        })
    
    return result
