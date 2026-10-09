# RSI 2a / 2a' - operator ideas vs Malkan sources (2026-10-09)

Status: layer candidate only (separate layer, never a Tom filter). Nothing here is an MTS rule until the operator approves it and our own OOS backtest passes.
Provenance split: every parameter is tagged OPERATOR (his words, this session) or MALKAN (quote in extracts/processed/malkan/) or NO-SOURCE (do not tune).
Operator answer to the open questions: "these questions will be answered by Malkanviews extractions". Extractions done: 3 transcripts, quotes gate PASS.

## Operator input, verbatim (source tag OPERATOR)
2a: RSI cross above 40 (clearance 37-38 to 41-42) or RSI support at 40 after it crosses up and lands on the 40 line.
  Case A: RSI crosses below 40, closes exactly 1 candle below, pops back into neutral; price then returns to the same level or higher.
  Case B: RSI below 40 for more than 4-24 candles, then enters from under and crosses 40.
  HINT 1: divergence while RSI is below 40 (price lower lows, RSI higher lows); multiple divergences seen on 1m.
  HINT 2: RSI support on the RSI MA near 2a = better signal.
2a': mirror for shorts from above 60, with Bollinger Bands: price outside the BB plus resistance confluence (bearish divergence, CVD, OI).
  Bearish divergence = higher highs in price, lower highs in RSI. Trigger when RSI's low breaks its last low on candle close, unless price falls faster than
  the average speed at the tops (then do not wait for the close). Backtest to find which confluence combinations work.

## Answers from the Malkan extractions (T3, Indian equities D/W/M, not crypto, not intraday)
| Question | Answer | Quote file |
|---|---|---|
| Close or wick RSI for divergence? | Close to close | extract_Wvq1TZh8aF0 D1, extract_cQ-y1oULkBw D1 |
| Min bars between the two points | 3 | Wvq1 D2, cQ-y D2 |
| Max useful bars | up to ~10 ("between three and 10"); 15-50 diluted | Wvq1 D2, cQ-y D2 |
| Where is divergence strongest | bullish near 40, bearish near 60; at 20/80 reverse divergences negate it | Wvq1 D3 |
| Decimals | count (37.7 vs 38.89 accepted) | Wvq1 D4 |
| Confirmation | bullish candle after bullish div (bearish candle after bearish); entry on break of that candle; stop beyond its extreme | Wvq1 D5 |
| Target | point "C between A and B" (price level; exact definition NOT in the words, needs the video frame) | Wvq1 D6 |
| Exit | take 50% (caption says "50% to 35%") at target, trail the rest | Wvq1 D6 |
| Multiple divergences | second/third divergence = retry while monthly RSI > 60; "big U-turn" | Wvq1 D9, cQ-y D4 |
| Higher-TF stack | monthly > 60 + daily < 40 + divergence = best, double the target | Wvq1 D8 |
| Daily 40 re-cross | 5-star: monthly and weekly > 60, daily comes below 40 then crosses back up; entry above signal candle high, stop below its low (secondary source) | extract_-CBvFi40sIQ |
| Timeframe | daily/weekly/monthly only; he says to read one higher and one lower | cQ-y D5 |

## Not covered by Malkan (stay OPERATOR hypotheses; log, do not tune)
- Case A (exactly 1 candle below 40) and Case B dwell 4-24 candles. Bucket dwell in the analysis, pick no number.
- RSI MA support as confluence (existing `rsi_ma_events.ma_support`).
- Bollinger Bands, CVD, OI confluence; the speed-based early trigger; 1m/intraday use.
- Malkan's BB/"3x3 volatility" videos are not in the repo yet (WEB_RESEARCH.md gap list).

## Conflicts to flag
- Malkan's 2a gate is HTF-first (monthly/weekly > 60). The operator's 2a has no HTF gate. Test both; `malkan_mtf.py` already has the composition.
- Malkan exits at target C with a candle-based stop. The earlier RSI backtests used a generic 1%/2% bracket (RSI_HISTORY.md in the mts-rsi worktree), so their "no edge" verdict does not test Malkan's own exit.
- Operator 1m use vs Malkan daily-and-up: the 10-bar max rule may scale with timeframe or may not; test per timeframe.

## Build order (steps 1-3 DONE 2026-10-09; 27 tests; both mutation-checked)
1. `rsi_events` annotation: dwell bars below the level before the cross, depth of dip. Parameter-free; bucket later.
2. cross-then-support sequencer (Case C).
3. `rsi_divergence.py`: close-to-close swing points, 3..10 bars apart (MALKAN), decimals allowed, bullish only if RSI at the low is near 40 as a logged flag (not a filter). Tests derived from FORMULAS.md style hand-computed series.
4. Confluence flags logged per event (MA support, divergence count, HTF RSI state, BB position, CVD, OI).
5. Malkan-exit backtest (candle-break entry, stop beyond candle, target C) vs generic bracket, both reported.
6. Speed-based early trigger last (needs intrabar RSI; out of scope in rsi_events today).

## Built (backtest/layers/rsi/)
- `rsi_reclaim.py`: `rsi_reclaim_events` (dwell_below, band_bars, depth, direct; up for the 40 side, down for the 60 side) and `rsi_retest` (Case C: support / fail / none within N bars). Clearance and window are arguments with no default.
- `rsi_divergence.py`: close-to-close bullish/bearish divergence between consecutive swing closes, 3..10 bars inclusive (params/malkan_divergence_default.json, quotes cited), `chain` = multiple-divergence count. Event is stamped one bar after the second swing (causal).
- v1 limits: only consecutive swings are compared; no candle confirmation or target C yet (step 5).

## Corpus findings
- A 4th Malkan transcript existed, `2HcJ3NeZmEQ` (5-star sell setup: monthly < 40, weekly < 40, daily rises to 60). The inventory counted 3. Extracted (gate PASS) and the raw file added to git (it was untracked).
- WEB_RESEARCH.md lists ~8 more Malkan videos with no transcript in the repo (W1HrDl70Lhk, A-CQiV_UFB4, fgN6QBFY3Ss Bollinger father-son, kVIvcn7T44o, N7r3v7plqZM, FHEoMmD6xKM, dXxQOnK2jhQ, TYB7GJODt-k volatility divergence, WBByyLBp8-c). The Bollinger and volatility-divergence ones are the ones the 2a' short side needs. Downloading them needs operator approval.
