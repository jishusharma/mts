"""
Regular RSI/price divergence, Malkan rules (extracts/processed/malkan/, quotes verified):
- close to close ("What do we have to compare? Close to close. Because RSI is based on closing price.")
- two swing points A then B with B - A + 1 bars between min_bars and max_bars inclusive
  (Malkan: minimum three candles; "between three and 10"; 15-50 diluted). min_bars/max_bars are arguments,
  the sourced values live in params/malkan_divergence_default.json.
- decimals count: any strictly lower price close with a strictly higher RSI is a divergence (min_rsi_diff=0).
Bullish: price close lower low, RSI higher low. Bearish: price higher high, RSI lower high (mirror via sign).

Swing point = strict local extreme of the CLOSE: close[i] < both neighbours (low) or > both (high). It is only
known one bar later, so the event time is ts[i+1] (causal: never uses a bar after the one it is stamped on).
A and B are CONSECUTIVE swing points of the same kind (v1 limit: a divergence against an older, non-adjacent
swing is not detected). A swing point with RSI None is skipped as if absent.
`chain` counts how many consecutive A->B pairs ending at this B were divergences (1 = single, 2 = double...):
Malkan's "multiple divergences".
HIDDEN divergence (kinds "hidden_bullish" / "hidden_bearish", added 2026-10-28, OURS window, third-party definition:
DIVERGENCE_RESEARCH_2026-10-09.md s2; Malkan names "reverse divergence" but his transcripts hold no definition):
hidden_bullish = price close HIGHER low, RSI LOWER low; hidden_bearish = price LOWER high, RSI HIGHER high. Same swing
points, same causal stamp, same bars window and min_rsi_diff as regular (mirror: only the two comparisons flip).
Not here: candle confirmation, entry, stop, target (backtest step), intrabar/wick RSI (he says close to close).
"""


KINDS = ("bullish", "bearish", "hidden_bullish", "hidden_bearish")


def _pivots(vals, rsi, kind):
    sign = 1 if kind == "low" else -1
    out = []
    for i in range(1, len(vals) - 1):
        if rsi[i] is None:
            continue
        a, b, c = sign * vals[i - 1], sign * vals[i], sign * vals[i + 1]
        if b < a and b < c:
            out.append(i)
    return out


def rsi_divergence(close: list, rsi: list, ts: list, min_bars: int, max_bars: int,
                   kind: str = "bullish", min_rsi_diff: float = 0.0) -> list:
    if kind not in KINDS:
        raise ValueError("kind must be one of %s" % (KINDS,))
    if not (len(close) == len(rsi) == len(ts)):
        raise ValueError("close, rsi and ts must have the same length")
    if min_bars < 3 or max_bars < min_bars:
        raise ValueError("need 3 <= min_bars <= max_bars")
    if min_rsi_diff < 0:
        raise ValueError("min_rsi_diff must be >= 0")
    hidden = kind.startswith("hidden_")
    base = kind[len("hidden_"):] if hidden else kind
    sign = 1 if base == "bullish" else -1
    piv = _pivots(close, rsi, "low" if base == "bullish" else "high")
    events = []
    chain = 0
    for k in range(1, len(piv)):
        a, b = piv[k - 1], piv[k]
        bars = b - a + 1
        if hidden:   # mirror of regular: price less extreme, RSI more extreme
            price_ok = sign * close[b] > sign * close[a]
            rsi_ok = sign * rsi[a] - sign * rsi[b] > min_rsi_diff
        else:
            price_ok = sign * close[b] < sign * close[a]
            rsi_ok = sign * rsi[b] - sign * rsi[a] > min_rsi_diff
        if price_ok and rsi_ok and min_bars <= bars <= max_bars:
            chain += 1
            events.append({
                "t": ts[b + 1], "i": b + 1, "event": kind + "_divergence",
                "a_i": a, "b_i": b, "a_t": ts[a], "b_t": ts[b], "bars": bars,
                "close_a": close[a], "close_b": close[b],
                "rsi_a": rsi[a], "rsi_b": rsi[b], "chain": chain,
            })
        else:
            chain = 0
    return events
