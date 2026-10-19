"""
MyTradingSys/backtest/layers/cryptocred/cc_bt_adapter.py - D7 row 075 adapter (T051 L3).
Cryptocred adapter: cc_setups trades -> bt_engine + layers/runner.py.
Stdlib only. This module is a thin, mechanical wiring layer with no trading logic of its own:
- all the logic lives in cc_setups.py, bt_engine.py and layers/runner.py
- this file only translates between their different shapes:
  * cc_setups' {side,entry_price,entry_t,stop,targets,meta} signal dict
  * bt_engine's simulate_trade(**kwargs) call
  * runner's {"i": index, "side"} event dict

The module works for any of the three cc_setups functions (setup1_sr_flip, setup2_fib_pullback,
setup3_failed_msb_reversal) since they all share the same signal contract.
"""
from MyTradingSys.backtest.bt.bt_engine import simulate_trade


def signals_to_trades(signals: list, bars: list, mark_bars: list = None, funding: list = (), taker_fee: float = 0.0005, maker_fee: float = 0.0, max_bars: int = 1440, stop_first: bool = True, target_through: float = 0.0) -> list:
    """
    Convert cc_setups signals into bt_engine trade simulations.
    
    Args:
        signals: List of signal dicts from cc_setups (with meta)
        bars: List of bar dicts {t,o,h,l,c} for time lookup
        mark_bars: Optional list of mark bars for stop/target timing
        funding: funding records [(t, rate)] covering the hold; () / [] = explicit no-funding model; None raises (B103)
        taker_fee: Taker fee rate
        maker_fee: Maker fee rate
        max_bars: Maximum bars to simulate
        stop_first: Whether stop takes whole size if hit same bar as entry
        
    Returns:
        List of {"signal_meta": signal.get("meta", {}), "trade_result": result} dicts
    """
    if not signals:
        return []
        
    results = []
    for signal in signals:
        # Build call kwargs by dropping meta (bt_engine doesn't want it)
        call_kwargs = {k: v for k, v in signal.items() if k != "meta"}
        result = simulate_trade(
            bars=bars,
            mark_bars=mark_bars,
            funding=funding,
            taker_fee=taker_fee,
            maker_fee=maker_fee,
            max_bars=max_bars,
            stop_first=stop_first,
            target_through=target_through,
            **call_kwargs
        )
        results.append({"signal_meta": signal.get("meta", {}), "trade_result": result})
        
    return results


def signals_to_events(signals: list, bars: list) -> list:
    """
    Convert cc_setups signals into runner.py events (index-based).
    
    Args:
        signals: List of signal dicts from cc_setups (with meta)
        bars: List of bar dicts {t,o,h,l,c} for time lookup
        
    Returns:
        List of {"i": index, "side": side} dicts matching runner's expected format
        Signals with no matching bar in bars are silently skipped.
    """
    if not signals:
        return []
        
    # Build timestamp -> index lookup once for efficiency
    ts_to_idx = {bar["t"]: i for i, bar in enumerate(bars)}
    
    events = []
    for signal in signals:
        entry_t = signal["entry_t"]
        idx = ts_to_idx.get(entry_t)
        if idx is not None:
            events.append({"i": idx, "side": signal["side"]})
            
    return events
