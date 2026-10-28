"""
The ONLY Wilder RSI implementation any other MTS layer or consumer may import.
D2 isolation rule: the 40/60 numbers are private to malkan_40_60. No other module imports them.
"""
from typing import List, Optional

def rsi_core(closes: List[float], period: int = 14) -> List[Optional[float]]:
    """
    Wilder RSI: returns a list the same length as `closes`; entries before index `period` are `None`.
    Seed avg_gain/avg_loss as sum(positive_deltas)/period and sum(negative_deltas)/period over the first period deltas (FORMULAS s1 steps 2-3; always divided by period, never by count of nonzeros).
    RSI at index `period`: if `avg_loss == 0`, `50.0` if `avg_gain == 0` else `100.0`; otherwise `100 - 100/(1 + avg_gain/avg_loss)`.
    For `i > period`: Wilder-smooth `avg_gain = (avg_gain*(period-1) + gain)/period`, `avg_loss = (avg_loss*(period-1) + loss)/period` where `gain = max(0, closes[i]-closes[i-1])`, `loss = max(0, closes[i-1]-closes[i])`, then the same RSI formula.
    Raise `ValueError` if `period < 1` or `len(closes) <= period`.
    """
    if period < 1:
        raise ValueError("Period must be >= 1")
    if len(closes) <= period:
        raise ValueError("Not enough data points for the given period")

    result = [None] * len(closes)
    
    # Compute deltas
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    
    # Seed values from first period
    gains = [max(0.0, delta) for delta in deltas[:period]]
    losses = [max(0.0, -delta) for delta in deltas[:period]]
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    # Handle case where avg_loss is 0
    if avg_loss == 0:
        rsi_val = 100.0 if avg_gain > 0 else 50.0
    else:
        rs = avg_gain / avg_loss
        rsi_val = 100 - 100 / (1 + rs)
    
    result[period] = rsi_val
    
    # Recursive smoothing for subsequent values
    for i in range(period + 1, len(closes)):
        gain = max(0.0, closes[i] - closes[i-1])
        loss = max(0.0, closes[i-1] - closes[i])
        
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        
        if avg_loss == 0:
            rsi_val = 100.0 if avg_gain > 0 else 50.0
        else:
            rs = avg_gain / avg_loss
            rsi_val = 100 - 100 / (1 + rs)
            
        result[i] = rsi_val
        
    return result
