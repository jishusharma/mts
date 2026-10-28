"""
Wilder RSI and MalkanView 40/60 RSI regime classifier (research only).

RSI is Tier 3 per COMPILED_DECISIONS E4 (superseded 2026-09-18) until a backtest validates it.
MalkanView rule: bull markets hold RSI above ~40 and reach 60+, bear markets stay below ~60 and reach 40-.

Functions:
- rsi_wilder(closes, period=14): computes Wilder RSI
- rsi_regime(rsi, lo=40.0, hi=60.0, lookback=20): classifies market regime
"""

def rsi_wilder(closes: list, period: int = 14) -> list:
    """
    Compute Wilder's RSI.
    
    Args:
        closes: list of closing prices
        period: RSI period (default 14)
        
    Returns:
        List of RSI values, same length as closes; entries before index `period` are None
        
    Raises:
        ValueError: if period < 1 or len(closes) <= period
    """
    if period < 1:
        raise ValueError("period must be >= 1")
    if len(closes) <= period:
        raise ValueError("len(closes) must be > period")
        
    rsi = [None] * len(closes)
    
    # Compute first changes
    changes = [closes[i] - closes[i-1] for i in range(1, period+1)]
    
    # Seed averages
    gains = [c for c in changes if c > 0]
    losses = [-c for c in changes if c < 0]
    
    if not gains:
        avg_gain = 0.0
    else:
        avg_gain = sum(gains) / period
        
    if not losses:
        avg_loss = 0.0
    else:
        avg_loss = sum(losses) / period
        
    # Compute RSI for index period
    if avg_loss == 0:
        if avg_gain == 0:
            rsi[period] = 50.0
        else:
            rsi[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi[period] = 100 - 100 / (1 + rs)
        
    # Compute subsequent RSI values using Wilder smoothing
    for i in range(period+1, len(closes)):
        change = closes[i] - closes[i-1]
        gain = max(0.0, change)
        loss = max(0.0, -change)
        
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        
        if avg_loss == 0:
            if avg_gain == 0:
                rsi[i] = 50.0
            else:
                rsi[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi[i] = 100 - 100 / (1 + rs)
            
    return rsi


def rsi_regime(rsi: list, lo: float = 40.0, hi: float = 60.0, lookback: int = 20) -> list:
    """
    Classify market regime based on RSI values using MalkanView rule.
    
    Args:
        rsi: list of RSI values (can contain None)
        lo: lower threshold (default 40.0)
        hi: upper threshold (default 60.0)
        lookback: number of periods to consider for regime classification (default 20)
        
    Returns:
        List of regime labels ("BULL", "BEAR", "RANGE") or None where insufficient data
        
    Raises:
        ValueError: if thresholds invalid or lookback < 1
    """
    if not (0 < lo < hi < 100):
        raise ValueError("Invalid thresholds: must satisfy 0 < lo < hi < 100")
    if lookback < 1:
        raise ValueError("lookback must be >= 1")
        
    regime = [None] * len(rsi)
    
    for i in range(len(rsi)):
        # Collect non-None values ending at i
        window = []
        for j in range(i, max(-1, i - lookback), -1):
            if rsi[j] is not None:
                window.append(rsi[j])
            if len(window) == lookback:
                break
                
        # Not enough data
        if len(window) < lookback:
            continue
            
        # Classify regime
        min_rsi = min(window)
        max_rsi = max(window)
        
        if min_rsi >= lo and max_rsi >= hi:
            regime[i] = "BULL"
        elif max_rsi <= hi and min_rsi <= lo:
            regime[i] = "BEAR"
        else:
            regime[i] = "RANGE"
            
    return regime
