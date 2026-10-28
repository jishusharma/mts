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

REVERSE divergence, Malkan's own definition (operator 2026-10-28: the Malkan layer computes divergence ONLY as he says it).
Glossary: MyTradingSys/research/setup_catalog_2026-10-15/malkan/MALKAN_DIVERGENCE_GLOSSARY.md s2.5-2.6 (sources Hindi
A-CQiV_UFB4 and English GbXnw_tNMtw). Kinds "prd" and "nrd":
- PRD (positive reverse divergence), SOURCED: price HIGHER low, RSI LOWER low, inside an UPTREND, continuation up
  (glossary :205-:215; GbXnw_tNMtw_raw.txt:379 "uptrend you're going to compare the lows ... RSI is lower price is higher
  that calls for positive reverse divergence").
- NRD (negative reverse divergence), SOURCED: price LOWER high, RSI HIGHER high, inside a DOWNTREND, continuation down
  (glossary :310-:347; extract_A-CQiV_UFB4.md:334, GbXnw_tNMtw_raw.txt:498).
- Trend condition = RSI regime, his own marker: "When did the trend start? It went above 60"
  (extract_A-CQiV_UFB4.md:247) and "both the point should be about sixty if it's a positive ... divergence and ... a
  negative reverse divergence it should be below forty" (GbXnw_tNMtw_raw.txt:460). So PRD needs RSI at BOTH swing
  points >= 60, NRD needs RSI at BOTH <= 40. A shape-correct pair outside that regime is NOT a PRD/NRD (it is a plain
  pullback, not a trend). 60/40 SOURCED (his words: "about sixty"); strict >=60 / <=40 compare = OURS, conservative.
- Bars between the points: SOURCED words conflict (glossary conflict C1): "within seven eight bars" good, "dilutes ...
  more than fifteen twenty" (:352), "less than 15" (:379), "between five to fifty" (:460). Default 5..14 inclusive of A
  and B (lower bound from :460, upper bound from :379 "less than 15") = OURS, UNVERIFIED as a set;
  params/malkan_divergence_default.json block "reverse".
- 3/5/7 star grades: conditions withheld by the trader, UNVERIFIED, NOT implemented.
- Same swing points (strict local extremes of the CLOSE), same causal stamp ts[b+1], same min_rsi_diff as regular.
Generic "hidden divergence" (no trend condition) is a KROWN concept, not Malkan's: it lives in
krown_hidden_divergence.py as a separate confluence feed any layer can consume. It is deliberately NOT in this file.
Not here: candle confirmation, entry, stop, target (backtest step), intrabar/wick RSI (he says close to close).
"""


KINDS = ("bullish", "bearish", "prd", "nrd")
# Reverse-divergence RSI regime levels (SOURCED "about sixty" / "below forty", GbXnw_tNMtw_raw.txt:460).
PRD_MIN_RSI = 60.0
NRD_MAX_RSI = 40.0


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
                   kind: str = "bullish", min_rsi_diff: float = 0.0, rsi_level: float = None) -> list:
    if kind not in KINDS:
        raise ValueError("kind must be one of %s" % (KINDS,))
    if not (len(close) == len(rsi) == len(ts)):
        raise ValueError("close, rsi and ts must have the same length")
    if min_bars < 3 or max_bars < min_bars:
        raise ValueError("need 3 <= min_bars <= max_bars")
    if min_rsi_diff < 0:
        raise ValueError("min_rsi_diff must be >= 0")
    reverse = kind in ("prd", "nrd")
    base = {"prd": "bullish", "nrd": "bearish"}.get(kind, kind)   # which swing kind is compared
    sign = 1 if base == "bullish" else -1
    piv = _pivots(close, rsi, "low" if base == "bullish" else "high")
    if reverse and rsi_level is None:
        rsi_level = PRD_MIN_RSI if kind == "prd" else NRD_MAX_RSI
    events = []
    chain = 0
    for k in range(1, len(piv)):
        a, b = piv[k - 1], piv[k]
        bars = b - a + 1
        if reverse:   # price less extreme, RSI more extreme, AND trend regime (RSI level) at both points
            price_ok = sign * close[b] > sign * close[a]
            rsi_ok = sign * rsi[a] - sign * rsi[b] > min_rsi_diff
            if kind == "prd":
                rsi_ok = rsi_ok and rsi[a] >= rsi_level and rsi[b] >= rsi_level
            else:
                rsi_ok = rsi_ok and rsi[a] <= rsi_level and rsi[b] <= rsi_level
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
