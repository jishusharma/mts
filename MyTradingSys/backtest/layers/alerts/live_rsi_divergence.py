"""
Live adapter (wave W1a): regular RSI/price divergence -> alert events. SAMPLING layer, no claimed edge.

Wraps rsi/rsi_divergence.py:32 rsi_divergence on RSI(14) (rsi_core). fn(bars) -> [event], pure and causal:
an event is stamped on the bar that CONFIRMS the swing (b+1), uses only bars up to it, so events on bars[:k]
equal the prefix of events on all bars. Re-running on the same bars gives the same output (no state).
Params copied from rsi/run_divergence_mtf.py:54 (RSI_PERIOD = 14) and rsi/params/malkan_divergence_default.json
(min_bars 3, max_bars 10, min_rsi_diff 0.0; run_divergence_mtf.py:195 passes them to rsi_divergence).
Side: bullish -> long, bearish -> short (the run_divergence_mtf.py:17 outcome convention).
Timeframe: 1h first. RSI-DIV-MTF FAILED (31 of 32 net negative), so events carry "sampling": True.
Event "t" = bar OPEN time of the confirming bar (live_layers.py convention); name unique per (t, kind).
DECISION (OURS): bars with a non-finite o/h/l/c are dropped before the maths (Wilder state would be poisoned
forever by one NaN); no event is ever stamped on a dropped bar. Fewer than 15 usable bars -> [].
Proposed size 20/2 (OURS).
"""
import math

from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence

RSI_PERIOD = 14
MIN_BARS = 3
MAX_BARS = 10
MIN_RSI_DIFF = 0.0
SIDE = {"bullish": "long", "bearish": "short"}
NAME = {"bullish": "rsi_div_bull", "bearish": "rsi_div_bear"}


def _clean(bars):
    out = []
    for b in bars:
        try:
            if all(math.isfinite(float(b[k])) for k in ("o", "h", "l", "c")):
                out.append(b)
        except (KeyError, TypeError, ValueError):
            continue
    return out


def rsi_divergence_layer(bars):
    bars = _clean(bars)
    if len(bars) <= RSI_PERIOD:
        return []
    closes = [float(b["c"]) for b in bars]
    ts = [b["t"] for b in bars]
    rsi = rsi_core(closes, RSI_PERIOD)
    out = []
    for kind in ("bullish", "bearish"):
        for e in rsi_divergence(closes, rsi, ts, MIN_BARS, MAX_BARS, kind, MIN_RSI_DIFF):
            out.append({"t": e["t"], "event": NAME[kind], "side": SIDE[kind], "sampling": True,
                        "bars": e["bars"], "chain": e["chain"], "close_a": e["close_a"], "close_b": e["close_b"],
                        "rsi_a": e["rsi_a"], "rsi_b": e["rsi_b"]})
    out.sort(key=lambda x: (x["t"], x["event"]))
    return out


adapter = rsi_divergence_layer
