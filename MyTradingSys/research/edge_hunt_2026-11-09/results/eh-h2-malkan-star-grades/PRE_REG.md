# PRE_REG: eh-h2-malkan-star-grades (Malkan 5-star and 7-star MTF RSI long grades)

Frozen before any return is computed. Trials T02 (7-star) and T03 (5-star) from TRIALS.md, frozen 2026-11-09 by edge-hunt-plan-opus-1109. No trial added, split or re-cut. Labels: S = SOURCED (file:line), O = OURS.

## Hypothesis
Malkan grades multi-timeframe RSI long setups as 5-star and 7-star. T02: monthly RSI14 >= 60 and daily RSI14 < 40 with a daily regular bullish divergence ending on the signal bar; target 4R. T03: monthly RSI14 > 60 and weekly RSI14 > 60, daily RSI pulls back to 40 and prints a green bar; target 2R. Question: is the long fee-net positive at his stated RR, and how often does each grade fire.

## Rules (frozen)
| Item | T02 7-star MTF long | T03 5-star MTF long | Label |
|---|---|---|---|
| Higher TF | last CLOSED monthly RSI14 >= 60 | last closed monthly RSI14 > 60 AND last closed weekly RSI14 > 60 | S (SEVEN_STAR_CAPTIONS / Wvq1TZh8aF0:8; 2HcJ3NeZmEQ:8, -CBvFi40sIQ:8) |
| Daily | daily RSI14 < 40 at the signal bar AND a daily regular bullish divergence ending on it (rsi_divergence kind=bullish, close to close, 3-10 bars, min_rsi_diff 0; params malkan_divergence_default.json) | daily RSI14 at the signal bar within 38..42 AND the bar closes green: close > open AND close > prior close | words S; 38..42 and green definition O; divergence params S (malkan_divergence_default.json, rsi_divergence.py) |
| Entry | next daily open (taker) | next daily open (taker) | O |
| Stop | lowest low over the divergence span (swing A bar through the signal bar) | the signal bar low | O (structural, d-stops-follow-trade-1106) |
| Target | 4R | 2R | 4R: S-derived ("stop loss unchanged, target doubled" over 5-star 1:2+); 2R: S ("1:2+") |
| Time stop | 40 daily bars, close of the 40th bar (taker) | same | O |
| Overlap | one trade at a time per symbol; a signal inside an open trade is skipped and counted | same | O |

Stop wins a same-bar tie. A signal whose next-open entry is at or below its stop is skipped and counted (invalid).

## OURS fills
- RSI: Wilder RSI14 (rsi_core.py, the only Wilder implementation per its header; checked).
- Higher-TF bars: monthly and weekly bars resampled from closed daily bars in UTC (weeks Monday 00:00). A higher-TF bar is usable on signal day d only if its close time (next period start 00:00 UTC) <= d+1 00:00 UTC (no lookahead; tested).
- Daily RSI and divergence are computed on daily closes; the signal bar is the bar whose close confirms the divergence (rsi_divergence event index i = b+1).
- Divergence span = swing A bar .. signal bar (inclusive); stop = min low over the span.
- Exploratory count (no trial, no returns): PRD/NRD reverse divergence, min 5 and max 50 bars, both swing points RSI > 60 (PRD) or < 40 (NRD) per GbXnw_tNMtw:456-465 (S), counted per year on DEV, via rsi_divergence kind prd/nrd with min_bars 5, max_bars 50 (the repo's reverse path, rsi_level default 60/40).
- Warm-up: monthly RSI14 needs 14 closed months after the 2017-08 start. Signals are counted from 2018-10-01 (first usable month). DECISION (OURS): the brief's DEV is 2017-08..2024-06-30 with the first 14 months as warm-up; repo splits.py has DEV_START 2022-01-01 and DEV_END 2024-07-01 (exclusive), which differ from the brief. We follow the brief for this worker and do not edit splits.py.

## Data and splits
- Spot 1d klines BTCUSDT, ETHUSDT from 2017-08-17 (fetch_binance_archive --spot-history). Perp fundingRate archive from 2019-09 (fetch_binance_archive --datasets fundingRate). Funding before 2019-09 = 0; spot-history trades before 2019-09 carry no funding and this is said in RESULT.
- DEV = 2017-08-17 .. 2024-06-30 (signals counted from 2018-10-01). VALIDATION = 2024-07-01 .. 2025-06-30, read once and only if the DEV screen passes. HOLDOUT = 2025-07-01 onward: never loaded. The loader refuses any bar at or after 2025-07-01 and a test shows it.
- Cache outside the repo: F:/MTS/Dumps/backtest/eh-h2-spot and eh-h2-fund.

## Fees, R, statistics
- Regime A: taker 0.0005 per side (fees.py DERIBIT_TAKER) on entry and exit = 10 bps round trip, plus 2 bps round-trip slippage (FORMULAS s13) = 12 bps round trip. fee_r = 12 bps / stop distance in bps.
- Funding R: sum of funding rates with calc_time in [entry, exit) times entry price / stop distance (long pays positive rate). Net R = gross R - fee_r - funding R.
- SE clustered by ISO week (daily trades). DEV screen: n >= 30 AND mean net R > 0 AND CI lower bound > 0. VALIDATION: one-sided p for mean net R > 0, Holm at m = 15 (TRIALS.md).
- Verdict: PASS = DEV screen passed and VALIDATION Holm passed with mean > 0. FAIL = DEV mean net R <= 0 with CI upper bound below the MDE (z 2.8 x SE). INCONCLUSIVE otherwise. A PASS files one raw testnet-forward card; the next step is testnet forward, never a longer backtest.
- Reported: n, hit rate, mean gross R, mean fee_r, mean net R, SE, CI, MDE, per-year table on DEV, list of every event (date, symbol, R).

## Trial ids
T02 (7-star), T03 (5-star). Exploratory: PRD/NRD event counts only.

## Context
- Regime: research_kit regime_tag (weekly, DEV) and Malkan RSI bands; counts in RESULT.
- Phase: DEV 2017-08..2024-06 pooled; not split by cycle phase (that is eh-o2's question).
- Session: daily bars, no session filter (UTC day).
- Entry: next daily open, taker, both symbols independently.
