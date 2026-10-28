import math
import random
import statistics
from itertools import combinations

def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)

def bootstrap_mean_ci(x, n_boot=10000, alpha=0.05, seed=12345):
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        resample = [rng.choice(x) for _ in x]
        means.append(statistics.mean(resample))
    means.sort()
    lower_idx = int(alpha / 2 * n_boot)
    upper_idx = int((1 - alpha / 2) * n_boot) - 1
    return (means[lower_idx], means[upper_idx])

def moments(x):
    if not x:
        raise ValueError("Empty list")
    n = len(x)
    m = statistics.mean(x)
    sd = math.sqrt(sum((xi - m)**2 for xi in x) / n)
    if sd == 0:
        skew = 0.0
        kurt = 3.0
    else:
        skew = sum(((xi - m) / sd)**3 for xi in x) / n
        kurt = sum(((xi - m) / sd)**4 for xi in x) / n
    return (m, sd, skew, kurt)

def sharpe(x):
    """mean/pstdev; NaN for zero variance or a single observation (section 10 policy)."""
    mean, sd, _, _ = moments(x)
    if sd == 0 or len(x) < 2:
        return float('nan')
    return mean / sd

def _sharpe_or_zero(x):
    """Internal to pbo_cscv: a constant variant ranks as Sharpe 0 (unchanged arithmetic)."""
    s = sharpe(x)
    return 0.0 if s != s else s

def psr(x, sr_star=0.0):
    sr = sharpe(x)
    if sr != sr:
        return float('nan')
    T = len(x)
    _, _, g3, g4 = moments(x)
    numerator = (sr - sr_star) * math.sqrt(T - 1)
    denominator = math.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr * sr)
    if denominator == 0:
        return 0.5
    z = numerator / denominator
    return statistics.NormalDist().cdf(z)

def expected_max_sr(var_sr, n_trials):
    if n_trials < 2:
        raise ValueError("n_trials must be >= 2")
    gamma = 0.5772156649
    term1 = (1 - gamma) * statistics.NormalDist().inv_cdf(1 - 1 / n_trials)
    term2 = gamma * statistics.NormalDist().inv_cdf(1 - 1 / (n_trials * math.e))
    return math.sqrt(var_sr) * (term1 + term2)

def dsr(x, n_trials, var_sr):
    sr_star = expected_max_sr(var_sr, n_trials)
    return psr(x, sr_star)

def pbo_cscv(M, S=16):
    T = len(M)
    N = len(M[0]) if M else 0
    if T < 2 or N < 1 or S < 2 or S % 2 != 0 or T < S:
        raise ValueError("Invalid input")
    if any(len(r) != N for r in M):
        raise ValueError("Ragged matrix")
    block_size = T // S
    if block_size == 0:
        raise ValueError("Not enough data for specified S")
    truncated_T = block_size * S
    blocks = [M[i:i+block_size] for i in range(0, truncated_T, block_size)]
    log_odds_list = []
    total_combinations = 0
    valid_combinations = 0
    for is_blocks in combinations(range(S), S // 2):
        is_indices = list(is_blocks)
        oos_indices = [i for i in range(S) if i not in is_indices]
        is_data = [blocks[i] for i in is_indices]
        oos_data = [blocks[i] for i in oos_indices]
        is_returns = [[row[i] for row in sum(is_data, [])] for i in range(N)]
        oos_returns = [[row[i] for row in sum(oos_data, [])] for i in range(N)]
        is_sharpes = [_sharpe_or_zero(returns) for returns in is_returns]
        oos_sharpes = [_sharpe_or_zero(returns) for returns in oos_returns]
        n_star = is_sharpes.index(max(is_sharpes))
        w = (sum(1 for s in oos_sharpes if s < oos_sharpes[n_star]) + 1) / (N + 1)
        log_odds = math.log(w / (1 - w)) if w > 0 and w < 1 else float('-inf') if w == 0 else float('inf')
        log_odds_list.append(log_odds)
        total_combinations += 1
        if log_odds <= 0:
            valid_combinations += 1
    pbo = valid_combinations / total_combinations if total_combinations > 0 else 0.0
    return (pbo, log_odds_list)
