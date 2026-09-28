"""
MLK-GAP1: the full 5-star setup is multi-timeframe (Monthly/Weekly gate + Daily entry)
... the multi-timeframe grandfather-father-son gate is out of scope [of malkan_40_60.py] and must be
composed later by a caller that runs this module once per timeframe and combines the results.

This file implements the MLK-GAP1 multi-timeframe composer: Monthly and Weekly `malkan_regime` states
gate a Daily `malkan_setup_bull`/`malkan_setup_bear` signal, reconstructing the full Malkan 5-star setup
from the single-timeframe pieces `malkan_40_60.py` already implements per timeframe.

This module performs NO new RSI/regime computation itself: monthly and weekly `rsi`/`malkan_regime`
values must already have been computed by running `rsi_core`/`malkan_regime` once per timeframe (via the
D1 timeframe layer) before calling here; this file only aligns and gates.

The "most recently CLOSED higher-timeframe bar as of the daily timestamp" lookback semantics of `state_asof`
are critical: a daily bar is gated by the most recently CLOSED higher-timeframe bar, never a future one.
This prevents information leakage into backtests.
"""

from MyTradingSys.backtest.layers.rsi.malkan_40_60 import malkan_setup_bull, malkan_setup_bear


def state_asof(times: list, values: list, t: int):
    """
    Return the value from the LATEST entry in `times` whose value is `<= t`.
    
    `times` is a list of bar-open timestamps for one (higher) timeframe, ascending, same length as
    `values` (its regime string at each of those times, e.g. "BULL"/"BEAR"/"RANGE"/None).
    
    Return the value from the LATEST entry in `times` whose value is `<= t` (the higher-timeframe bar
    that was already open/closed at or before the daily timestamp `t` — a daily bar is gated by the most
    recently CLOSED higher-timeframe bar, never a future one). Return `None` if `times` is empty or every
    entry in `times` is `> t` (no higher-timeframe state exists yet at time `t`).
    
    Raise `ValueError` if `len(times) != len(values)`.
    """
    if len(times) != len(values):
        raise ValueError("times and values must have the same length")
        
    if not times:
        return None
        
    # Find the rightmost index where times[i] <= t
    i = len(times) - 1
    while i >= 0 and times[i] > t:
        i -= 1
        
    if i < 0:
        return None
        
    return values[i]


def malkan_mtf_bull(bars: list, rsi: list, daily_regime: list, weekly_times: list, weekly_regime: list, monthly_times: list, monthly_regime: list, level: float = 40.0, tolerance: float = 2.0, require_bullish_candle: bool = True) -> list:
    """
    Multi-timeframe bull setup (MLK-S1-MTF): Daily regime BULL + rsi_events "support" @ 40 + bullish entry candle,
    gated by Weekly and Monthly RSI regimes both being BULL.
    
    Call malkan_setup_bull to get base signals, then gate them with weekly and monthly regime states.
    """
    ts = [b["t"] for b in bars]
    base = malkan_setup_bull(bars, rsi, daily_regime, level=level, tolerance=tolerance, require_bullish_candle=require_bullish_candle)
    
    signals = []
    for signal in base:
        w = state_asof(weekly_times, weekly_regime, signal["t"])
        m = state_asof(monthly_times, monthly_regime, signal["t"])
        
        # Keep only if both higher timeframes are BULL
        if w == "BULL" and m == "BULL":
            new_signal = signal.copy()
            new_signal["weekly_regime"] = w
            new_signal["monthly_regime"] = m
            new_signal["rule_id"] = "MLK-S1-MTF"
            signals.append(new_signal)
            
    return signals


def malkan_mtf_bear(bars: list, rsi: list, daily_regime: list, weekly_times: list, weekly_regime: list, monthly_times: list, monthly_regime: list, level: float = 60.0, tolerance: float = 2.0, require_bearish_candle: bool = True) -> list:
    """
    Multi-timeframe bear setup (MLK-S2-MTF): Daily regime BEAR + rsi_events "resistance" @ 60 + bearish entry candle,
    gated by Weekly and Monthly RSI regimes both being BEAR.
    
    Call malkan_setup_bear to get base signals, then gate them with weekly and monthly regime states.
    """
    ts = [b["t"] for b in bars]
    base = malkan_setup_bear(bars, rsi, daily_regime, level=level, tolerance=tolerance, require_bearish_candle=require_bearish_candle)
    
    signals = []
    for signal in base:
        w = state_asof(weekly_times, weekly_regime, signal["t"])
        m = state_asof(monthly_times, monthly_regime, signal["t"])
        
        # Keep only if both higher timeframes are BEAR
        if w == "BEAR" and m == "BEAR":
            new_signal = signal.copy()
            new_signal["weekly_regime"] = w
            new_signal["monthly_regime"] = m
            new_signal["rule_id"] = "MLK-S2-MTF"
            signals.append(new_signal)
            
    return signals

