"""
KROWN-CONFLUENCE: generic hidden RSI divergence. NOT part of the Malkan layer.

Operator rule 2026-10-28: the Malkan RSI 40-60 layer computes divergence only as Malkan says it (PRD / NRD with the
trend condition, rsi_divergence.py). The textbook "hidden divergence" with NO trend condition is a Krown concept
(third-party definition: MyTradingSys/research/DIVERGENCE_RESEARCH_2026-10-09.md s2). It is kept here as a separate
confluence feed that any layer may consume.

hidden_bullish = price close HIGHER low, RSI LOWER low; hidden_bearish = price LOWER high, RSI HIGHER high.
Same swing points (strict local extremes of the close), same causal stamp ts[b+1], same bars window and
min_rsi_diff semantics as rsi_divergence. The bars window (default 3..10 at the call site) is OURS; no level or trend
filter at all (that is exactly what makes it generic).
"""
from MyTradingSys.backtest.layers.rsi.rsi_divergence import _pivots

KROWN_KINDS = ("hidden_bullish", "hidden_bearish")


def krown_hidden_divergence(close: list, rsi: list, ts: list, min_bars: int, max_bars: int,
                            kind: str = "hidden_bullish", min_rsi_diff: float = 0.0) -> list:
    if kind not in KROWN_KINDS:
        raise ValueError("kind must be one of %s" % (KROWN_KINDS,))
    if not (len(close) == len(rsi) == len(ts)):
        raise ValueError("close, rsi and ts must have the same length")
    if min_bars < 3 or max_bars < min_bars:
        raise ValueError("need 3 <= min_bars <= max_bars")
    if min_rsi_diff < 0:
        raise ValueError("min_rsi_diff must be >= 0")
    sign = 1 if kind == "hidden_bullish" else -1
    piv = _pivots(close, rsi, "low" if sign == 1 else "high")
    events = []
    chain = 0
    for k in range(1, len(piv)):
        a, b = piv[k - 1], piv[k]
        bars = b - a + 1
        price_ok = sign * close[b] > sign * close[a]
        rsi_ok = sign * rsi[a] - sign * rsi[b] > min_rsi_diff
        if price_ok and rsi_ok and min_bars <= bars <= max_bars:
            chain += 1
            events.append({
                "t": ts[b + 1], "i": b + 1, "event": kind + "_divergence", "source": "KROWN-CONFLUENCE",
                "a_i": a, "b_i": b, "a_t": ts[a], "b_t": ts[b], "bars": bars,
                "close_a": close[a], "close_b": close[b],
                "rsi_a": rsi[a], "rsi_b": rsi[b], "chain": chain,
            })
        else:
            chain = 0
    return events
