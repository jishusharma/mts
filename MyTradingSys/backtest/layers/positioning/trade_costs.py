"""
T055 shared cost model for candidates C1 (funding_cvd_fade), C2 (session_momentum) and
C3 (turn_of_candle). Binance USDT-M perp taker fee 10 bps round trip, plus a slippage allowance,
plus perpetual funding: a long pays a positive funding rate and a short receives it.
Funding is charged as a fraction of ENTRY notional (documented simplification).
Nothing here places orders.
"""

from bisect import bisect_right


def funding_paid(side: str, t_in: int, t_out: int, funding: list) -> float:
    """Calculate funding paid or received for a trade."""
    if side == "long":
        sgn = 1.0
    elif side == "short":
        sgn = -1.0
    else:
        raise ValueError("side must be 'long' or 'short'")
    
    if t_out < t_in:
        raise ValueError("t_out must not be less than t_in")
        
    if not funding:
        return 0.0  # explicit "no funding model" (net_nofund variant); NOT a coverage claim
    if t_in < funding[0][0] or t_out > funding[-1][0]:
        # B103: fail closed - (t_in, t_out] must lie inside the loaded records' span
        raise ValueError(f"funding records cover [{funding[0][0]}, {funding[-1][0]}] but trade window is "
                         f"({t_in}, {t_out}]; load funding for the whole hold")

    # Find the index of the last funding record before or at t_in
    idx = bisect_right([x[0] for x in funding], t_in) - 1
    if idx < 0:
        start_idx = 0
    else:
        start_idx = idx + 1

    # Sum up all funding rates where t_in < t <= t_out
    total_rate = 0.0
    for i in range(start_idx, len(funding)):
        t, rate = funding[i]
        if t > t_out:
            break
        if t > t_in:
            total_rate += rate

    return sgn * total_rate


def net_return(side: str, p_in: float, p_out: float, t_in: int, t_out: int, funding: list,
               fee_rt: float = 0.0010, slip_rt: float = 0.0002) -> float:
    """Calculate net return of a trade after fees, slippage and funding."""
    if p_in <= 0:
        raise ValueError("p_in must be positive")
    
    if side == "long":
        sgn = 1.0
    elif side == "short":
        sgn = -1.0
    else:
        raise ValueError("side must be 'long' or 'short'")
        
    gross = sgn * (p_out - p_in) / p_in
    fee = fee_rt
    slip = slip_rt
    fund_cost = funding_paid(side, t_in, t_out, funding)
    
    return gross - fee - slip - fund_cost
