# GOLAS-A: how practitioners compute divergence per indicator (ledger P0-02, B063)

Date 2026-10-30. Builder, card ask-p0-02-golas-divergence-method. Tier bar: T1 = exchange/platform docs, books, papers; T2 = platform education pages; anything lower is not accepted as proof and is marked NOT_IN_DATA. Quotes were pulled from the live pages on this date (the fetch tool truncates quotes at about 125 chars, so some are split). Prior work read first: B063_divergence.md (said no T1/T2 source existed), GOLAS_CD_WEB_2026-09-21.md (T3 only, not reused as proof).

## Result table (one row per indicator)

| Indicator | What the source gives (pivot rule / lookback / confirmation) | Source URL | Verbatim quote | Tier |
|---|---|---|---|---|
| RSI | Definition only: price new low + RSI higher low (bullish), price new high + RSI lower high (bearish). Pivot rule, lookback, min RSI gap: NOT_IN_DATA. Use is confirmation, not a reversal call. | https://www.tradingview.com/support/solutions/43000502338-relative-strength-index-rsi/ | "Bullish RSI Divergence - When price makes a new low but RSI makes a higher low." / "Bearish RSI Divergence - When price makes a new high but RSI makes a lower high." / "Divergence should be used as a way to confirm trends" "and not necessarily anticipate reversals." | T2 |
| MACD | Definition only: peaks/dips of MACD against price direction "might" signal exhaustion. Which MACD series (line or histogram), pivot rule, lookback: NOT_IN_DATA. | https://www.tradingview.com/support/solutions/43000502344-moving-average-convergence-divergence-macd/ | "falling peaks in the MACD as the price rises might indicate the exhaustion of an uptrend." / "rising dips in the MACD while the price drops might signal the exhaustion of a downtrend." | T2 |
| CVD | CVD definition found; divergence only as vocabulary (price vs CVD disagree). Pivot rule, lookback, venue and bar size: NOT_IN_DATA at T1/T2. The one page that checks the literature says the academic papers do not test the retail divergence rule. The page is a T3 education site, kept as a negative finding only, not as method proof. | https://realbacktesting.com/academy/cumulative-volume-delta-cvd-explained.html | "a running total of signed volume intended to represent buying pressure minus selling pressure" / "Divergence describes disagreement between price and CVD" / "Neither paper tests the retail rule" | T3 (below bar) |
| OI | NOT_IN_DATA. No exchange, CME or book source retrieved giving a rule for OI/price divergence (CME page timed out twice; Binance Academy RSI and MACD pages failed to load; search returned only blogs and indicator scripts). | NOT_IN_DATA | NOT_IN_DATA | none |

## Shared mechanics (pivot confirmation), platform docs

Not indicator-specific: how scripts that implement the tests above find swing points. No TradingView doc retrieved states a divergence lookback.

| Item | What the source gives | Source URL | Verbatim quote | Tier |
|---|---|---|---|---|
| Pivot window | Pivot high is set by N bars left and M bars right; known only M bars late (doc example 15 and 5) | https://www.tradingview.com/pine-script-docs/visuals/fills/ | "The number bars to the left of a detected pivot." / "The number bars to the right for pivot confirmation." / "ta.pivothigh(LEFT_BARS, RIGHT_BARS)" | T1 |
| Late confirmation | Pivots return na except on confirmed bars; plots must shift back by the same delay | https://www.tradingview.com/pine-script-docs/faq/visuals/ | "The functions ta.pivotlow() and ta.pivothigh() return na for all bars except those with identified pivots." / "so the script must offset the plotted lines by the same number of bars." | T1 |

## What is NOT in any T1/T2 source (flags)

- RSI, MACD, CVD, OI: lookback window, minimum pivot gap, minimum indicator difference. The 3-10 bar RSI window and 60/40 reverse thresholds in the repo are Malkan video-extract values (labelled in gemini_audits_2026-10-30/rsi_param_labels.md), not institutional.
- Wilder's own text (New Concepts in Technical Trading Systems, 1978) and Appel's MACD book were not retrievable here: NOT_IN_DATA, not claimed.
- CVD and OI: no exchange-documented divergence algorithm found. Any CVD/OI divergence rule in MTS stays OURS (consistent with the B063 2026-10-04 DEPRECATE decision).
- Evidence that any of these divergences predicts returns: NOT_IN_DATA (GOLAS-D is the separate backtest item; T089 covers RSI only, commit 1157dbe6).

DECISION (OURS): blog and vendor guides were rejected as proof per the tier bar rather than lowering it.
