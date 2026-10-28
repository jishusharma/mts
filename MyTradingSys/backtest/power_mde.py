"""Normal-approximation power and MDE for a net-R mean test.

The alternative is the two-point payoff +RR with probability p and -1 otherwise,
less fixed cost in R. The test declares an edge when its two-sided 95% CI
lower bound exceeds zero.
"""

from math import erf, sqrt
from statistics import NormalDist

_Z_975 = NormalDist().inv_cdf(0.975)
_Z_80 = NormalDist().inv_cdf(0.80)


def _cdf(value):
    return 0.5 * (1.0 + erf(value / sqrt(2.0)))


def power_mde(p, rr, cost_r, n):
    """Return mean net R, power, MDE, and N for 80% power.

    Args are win probability ``p``, gross reward/risk ``rr``, fixed per-trade
    cost in R ``cost_r``, and trade count ``n``. ``mde_net_r`` is the
    detectable mean effect at this N under the supplied two-point variance.
    """
    if not 0.0 < p < 1.0:
        raise ValueError("p must be strictly between 0 and 1")
    if rr <= 0.0:
        raise ValueError("rr must be positive")
    if cost_r < 0.0:
        raise ValueError("cost_r must be nonnegative")
    if n <= 0:
        raise ValueError("n must be positive")

    win_net = rr - cost_r
    loss_net = -1.0 - cost_r
    mean = p * win_net + (1.0 - p) * loss_net
    variance = p * (win_net - mean) ** 2 + (1.0 - p) * (loss_net - mean) ** 2
    sd = sqrt(variance)
    z = mean * sqrt(n) / sd
    # Reject H0 only when the sample mean is above +1.96 SE. The lower tail
    # is included for a genuinely two-sided test (negligible for positive mean).
    power = _cdf(z - _Z_975) + _cdf(-z - _Z_975)
    mde = (_Z_975 + _Z_80) * sd / sqrt(n)
    trades_80 = ((_Z_975 + _Z_80) * sd / mean) ** 2 if mean > 0.0 else float("inf")
    return {
        "mean_net_r": mean,
        "power": power,
        "mde_net_r": mde,
        "trades_for_80_power": trades_80,
    }
