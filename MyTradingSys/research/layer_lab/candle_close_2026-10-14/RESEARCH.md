# What the BTC candle-close question actually requires

Research date: 2026-10-14. Verdict: no validated evidence found in this source review for a universal BTC 1m/2m/3m cycle-bottom signature. Close sequences around levels are testable hypotheses. They are not established trading probabilities.

## Interpret the question correctly
Estimate P(outcome by horizon | level, completed-close sequence, higher-timeframe context, market phase), and its improvement over the same context without that sequence. A candle's colour or name alone omits most of the proposed information.

Separate three clocks: the level timeframe (e.g. prior week low), the trigger timeframe (e.g. 2m reclaim), and the outcome horizon (e.g. next hour versus next month). A 2m close above a weekly low does not constitute a weekly close above that low. The weekly candle is unfinished until its boundary. Multiple timeframes built from the same minutes are correlated evidence, not independent confirmations.

## Candidate signatures and their actual meaning

| Signature | Real-time observation | Hypothesis, not established probability |
|---|---|---|
| Wick rejection | Trades through a known level but closes back on its original side | Local defence; compare with simple touches and equally sized wicks away from levels |
| Close-through break | Completed close crosses the level | Continuation; compare against wick-only crossing |
| Acceptance | A second close remains beyond the level | Reduced false-break frequency, possibly offset by later/worse entry |
| Failed break / reclaim | Closes beyond a level, then back inside | Trapped-breakout reversal; include failed reclaims, not just successful examples |
| Retest hold | After moving to the far side, returns to the level and closes on the new side | Role reversal; distinguish immediate retest, delayed retest and no retest |
| Strong close | Large body and close near directional extreme, conditional on crossing | Displacement versus exhaustion; a large candle can mean either depending on context |
| Sweep, reclaim, higher low, structure close | Sequence around a previously confirmed swing, followed by close past the last lower high (mirror tops) | More demanding reversal evidence; each confirmation has latency and missed-trade cost |

First six have explicit OURS definitions in METHOD.md and runnable code. The final structure sequence is a research extension, not silently approximated by the pilot's retest. Volume/absorption/OI/funding may later add information, but OHLC cannot tell whether shorts were liquidated or passive buyers absorbed sells.

## Phase-specific questions

- Bull + local uptrend: does resistance acceptance continue better than reclaiming support? Count late-breakout failures too.
- Bear + local downtrend: are support breaks persistent and resistance reclaims short-lived? Mirror tests must be measured; BTC long/short symmetry is not assumed.
- Range: do failed edge breaks revert more reliably than accepted edge breaks trend? Range boundaries must exist before the signal, not be fitted to the completed chart.
- Transition/high volatility: does the pattern survive spread/slippage and larger invalidation distance? A high win rate can still have negative expectancy.
- Mixed scales: a 4h bounce inside a daily bear state is a distinct cell. Do not call every local rally a new bull market.

The pilot uses backward-looking daily bull/bear/neutral and efficiency-based trend/range proxies plus 4h direction. It does not identify economic regimes or use retrospectively dated bull/bear cycle boundaries. Subgroup tables are exploratory; a strong-looking cell needs its own frozen validation, not promotion from the same DEV table.

## Bottom/top labels: avoid the principal hindsight trap

At a candidate bottom, record the earliest observable alert, confirmation time, price already missed, invalidation and all failed candidates. The eventual lowest low is an outcome label; using it to place a support level or choose the alert bar leaks the future. A fractal pivot becomes usable only after its right-hand bars close. A retrospective ZigZag can label outcomes but cannot be a real-time input in its final repainted form.

Use separate tasks for (a) local reversal over hours, (b) swing reversal over days/weeks and (c) cycle reversal over months. Pre-register a forward window and adverse/favourable barriers, plus timeout and ambiguous-path handling. Report precision (how many alerts worked), recall (how many reversals had an advance alert), lead/confirmation lag, calibration and base-rate lift. Millions of 1m rows around one 2022 low remain one cycle-low episode. Leave-one-cycle-out evidence will have wide uncertainty with BTC's small cycle count; report that honestly.

The anonymous YouTube source is NOT_IN_DATA: no URLs were supplied. Krown is a relevant existing MTS source, not assumed to be the person the operator watched. For exact replication, collect all prospectively timestamped calls in a fixed period, including losses and unedited follow-through, and split design/check examples before rule encoding. Retrospectively narrated charts and selected live winners cannot estimate a hit rate.

## Verified external sources (opened 2026-10-14)

| Source | Tier / method quality / confidence | What it supports and does not support |
|---|---|---|
| Carol L. Osler, *Support for Resistance: Technical Analysis and Intraday Exchange Rates*, FRBNY Economic Policy Review, July 2000, pp.53-68. https://www.newyorkfed.org/medialibrary/media/research/epr/00v06n2/0007osle.pdf | T1; six firms' advance levels, three FX pairs, Jan 1996-Mar 1998, minute quotes and bootstrap comparisons; H for scope, L for transfer to BTC | A model for testing predetermined levels against random alternatives. It studies trend interruption, not a complete BTC fee-net strategy or macro-bottom predictor. |
| Carol L. Osler, *Currency Orders and Exchange-Rate Dynamics: Explaining the Success of Technical Analysis*, Staff Report 125, April 2001. https://www.newyorkfed.org/research/staff_reports/sr125.html | T1 institutional working paper; opened abstract/publication metadata; M mechanism, L BTC transfer | Order clustering offers a mechanism for reactions and acceleration around levels. Published version listed as Journal of Finance 58(5), 2003, pp.1791-1819; this session did not verify the full journal text. |
| Bailey, Borwein, Lopez de Prado, Zhu, *The Probability of Backtest Overfitting*, revised Feb 27 2015. https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf | T2 opened author manuscript; disclosed CSCV method; H for methodological relevance | Searching many variants creates selection bias; count trials and assess selection. Not empirical evidence that any candle pattern works. |
| Binance, *Public Data README*, undated living documentation. https://github.com/binance/binance-public-data/blob/master/README.md | T2 exchange docs; schema, archive intervals/checksums, no predictive study; H mechanics | 1m raw data and integrity checks; build UTC-aligned 2m candles explicitly. A checksum establishes file integrity, not economic validity or fill realism. |

No BTC-specific T1/T2 study establishing the requested conditioned minute-to-cycle probabilities was verified in this bounded search. This is not a claim that none exists anywhere.

## MTS primary source evidence

- `research/krown_ta101_2026-10-13/extracts/extract_qEfES84jwwo.md:152-160`: completed close through a zone, then wait for its far-side test. Line 270 explicitly records that the closing timeframe is unspecified. Verified against timed transcript by verify_extract_quotes.py, 0 problems.
- `research/krown_ta101_2026-10-13/extracts/extract_14bxwxC8gBQ.md:214-216`: reversal confirmation requires a close past the last lower high (opposite for uptrends). Quote gate 0 problems. This defines structure, not BTC success rates.
- `research/candle_patterns_2026-10-04/p1_results.json`: independently parse the complete 54 daily and 54 hourly rows before repeating its negative triage finding. Do not substitute these stand-alone shape tests for level-conditioned tests.

Paths in this document are relative to MyTradingSys. Krown sources are T3, educational/discretionary, no OOS cost-controlled sample; H confidence for quoted mechanics, L for predictive efficacy. All our thresholds are OURS. Original videos are linked in the extracts; no new transcript fetched.

## Critical-decision review

1. Reuse versus repeat: existing candle work tested shapes, not the full conditional hypothesis. New study measures incremental information around levels.
2. Split audit: late 2024 data is validation for the old candle family even though LC uses it as DEV. Preserve the stricter reservation; use 2022-Jun 2024 only.
3. Definitions: sources leave thresholds/TF unspecified. Label those OURS; never imply a faithful trader replication.
4. Data integrity: first load rejected gaps before outcomes; DATA_AMENDMENT.md records fail-first test and causal exclusions.
5. Economics: next-open directional probability is not stop/target win rate or net executable profitability. A fee screen cannot replace historical funding and execution modeling.
6. Selection: 126 arms plus descriptive subgroup looks; no best-cell probability used as a forecast. Final result must report all arms and independent-day counts.
7. Macro inference: no extrapolation from an hour's positive return to cycle-bottom recognition.

## Excluded source once, with reason

Lo/Mamaysky/Wang, NBER w7613: search metadata found, landing/PDF open failed (403/internal error). Not used as evidence in this report. Search-engine snippets, copied CryptoCred articles, marketing win rates and community assertions were not used as predictive evidence.
