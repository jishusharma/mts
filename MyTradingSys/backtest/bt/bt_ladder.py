"""
MyTradingSys/backtest/bt/bt_ladder.py - ladder entry fills on 1m bars (T051 L4). Opus 5.5, 2026-09-27.
(NUC draft 013 rejected: required the signal bar to be present, ignored rungs filled in the stop bar, and popped
the wrong rung; see _nuc_rejected/.) Conventions: bars with t > signal_t only; long rung fills when low <= price,
at the open if the bar opened at/through it; rungs filling in the stop bar count (then stopped); no fills after.
Queue position is ignored (optimistic) - use through_ticks > 0 as the BACKTEST_PROTOCOL §4 stress.
"""


def fill_ladder(side, rungs, bars, signal_t, deadline_bars, stop=None, through_ticks=0.0):
    if side not in ("long", "short"):
        raise ValueError("side must be long or short")
    long_ = side == "long"
    open_rungs = list(rungs)
    filled, stopped, scanned = [], False, 0
    for b in bars:
        if b["t"] <= signal_t:
            continue
        if scanned >= deadline_bars:
            break
        scanned += 1
        for price, size in list(open_rungs):
            hit = (b["l"] <= price - through_ticks) if long_ else (b["h"] >= price + through_ticks)
            if hit:
                gapped = (b["o"] <= price) if long_ else (b["o"] >= price)
                filled.append((b["t"], b["o"] if gapped else price, size))
                open_rungs.remove((price, size))
        if stop is not None and ((b["l"] <= stop) if long_ else (b["h"] >= stop)):
            stopped = True
            break
        if not open_rungs:
            break
    fs = sum(s for _, _, s in filled)
    return {"filled": filled, "filled_size": fs,
            "avg_price": (sum(p * s for _, p, s in filled) / fs) if fs else None,
            "first_fill_t": filled[0][0] if filled else None, "last_fill_t": filled[-1][0] if filled else None,
            "unfilled": open_rungs, "stopped_during_entry": stopped}
