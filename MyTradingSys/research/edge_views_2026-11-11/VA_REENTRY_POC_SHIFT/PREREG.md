# PREREG: prior-day value-area re-entry (R10) and two consecutive daily POC shifts (R6), written before any trade is computed

Card btc-value-area-reentry-and-poc-shift-prereg-1112. Sources: `9IliXww64uM` R10 and `VOiy8mAALWA` R6 in research/orderflow_extracts_1112/ORDERFLOW_RULES.md.
Analyst statements are context, never signals. This file is committed before any trade of either rule is computed.
Two rules, one frozen parameter set each, no sweep. Every number below is OURS unless it carries SOURCED (quote).

## Context
Regime: none as a gate, because neither video rule states a regime; DEV spans bear 2022, base 2023, run-up 2024 and the RESULT reports per-year and long/short rows.
Phase: none, because phase labels are not part of either video rule.
Session: none, because neither rule states a session; all UTC hours trade (rule 1 only needs the event inside one UTC day).
Entry: R1 next 15m bar open after the re-entry bar closes (market fill); R2 the 00:00 UTC 1m open of the day after the second shift (the POC of day d is known only once day d is complete).
Regime mix: DEV 2022-02-01..2024-05-31 (BTC daily close 38,680 -> 67,578, +75 %); descriptive day count, same window and same SMA50 definition as BAILEYS_SWEEP/PREREG.md, no trade involved: 832 DEV days with a 50-day SMA, 51.4 % close above it and 48.6 % below. VALIDATION (2024-07-01 on) is not touched.

## Sources (the idea only)
- R1 `9IliXww64uM` R10 "Failed breakout back inside". SOURCED (quote): "We had a very strong rejection with a lot of volume". Idea: price breaks out of the prior-day value area, closes back inside, trade toward the other edge. Bar size, break test, stop, target rule and time cap are OURS.
- R2 `VOiy8mAALWA` R6 "Daily POC shift rule". SOURCED (quote): "if they shift upward overlapping each other, stop doing counter trades"; R7 "for as long as the sustained shift in the VU app continues moving upwards for at least two consecutive days." The video uses the shift to stop counter-trading; measuring the with-shift return is OURS.

## Difference from what was tested (TESTED_MAP, btc_of_level_auction_1112)
- B1 (absorption at VAH/VAL/PDH/PDL, FAIL) needed a 5m volume/delta absorption bar AT a level and faded it; this rule has no order-flow bar: the trigger is a 15m CLOSE outside the value area followed by a 15m CLOSE back inside, the target is the OPPOSITE value-area edge (up to a whole value-area width away), and the stop is the excursion extreme. Different trigger, stop and target.
- Sweep fade (TESTED_MAP T04, -0.221 R, n 1150; -0.106 R, n 1,484) fades a wick through PDH/PDL/PWH/PWL and reclaim; this rule uses value-area edges from a volume profile and needs a full close outside, so a wick-only sweep never arms it. Overlap is not zero (both fade a failed break), so R1 is counted as a trial.
- R2 (daily POC shift persistence) has no counterpart in TESTED_MAP or btc_of_level_auction_1112 (checked by file listing; B2 is an unfinished auction at 24h extremes, not POC).
- Trial count: about 101 prior counted studies; these are trials ~102 and ~103. A pass is not an edge claim.

## Data
BTCUSDT 1m Binance perp klines, F:/MTS/data/tom_raw/klines/ (2022-01..2024-06 files read; 2022-01 and the days before 2022-02-01 only as warm-up for prior-day profiles). No downloads. A bar is usable only after its close (t + width). Daily profile and POC only from COMPLETED UTC days. Volume profile is built from 1m bars (OURS approximation: real trade-level profile is not available).

## Profile definition (shared)
For a completed UTC day: each 1m bar's volume goes to the bin of its typical price (high+low+close)/3. Bin width = 0.05 % of that day's close (OURS), bin index = floor(price / width). POC = the bin with the most volume (ties: lowest bin); POC price = bin center. Value area (OURS, the standard 70 % rule): start at the POC bin; repeatedly compare the volume of the next two bins above vs the next two bins below (a side with fewer than two bins left counts what exists); add the larger pair (tie: above); stop when the area holds >= 70 % of the day's volume. VAH = upper edge of the top bin, VAL = lower edge of the bottom bin. Empty bins inside the range are zero-volume bins.

## R1: value-area re-entry (15m bars, resampled from 1m UTC buckets)
Levels for UTC day D = VAH, VAL of day D-1. Short setup: a 15m bar i of day D closes above VAH while bar i-1 closed <= VAH (the break). The setup dies if any later bar closes below VAL, if no bar closes back inside by 24 bars (6 h) after i, or if the re-entry bar is not in day D. Re-entry = the first bar j > i with close <= VAH (and >= VAL). Entry = OPEN of bar j+1 (no look-ahead). Stop = highest high of bars i..j (excursion extreme, no buffer). Target = VAL. Skip if R/entry < 0.10 % (fee guard) or if target distance <= 0. Long setup = exact mirror (close below VAL, back inside, stop = lowest low, target VAH). Exit: stop or target on 15m bars from the entry bar; if one bar touches both the STOP counts; time cap 96 bars (24 h), exit at that bar close; fills at the stop/target price, no slippage. One position at a time; a setup arms only when flat. Net R = gross R - 0.001 x entry / R_dist (fee 10 bp round trip, from fees.BINANCE_TAKER x 2). Net bp = net R x R_dist/entry x 1e4.

## R2: two consecutive daily POC shifts (return study, not a stop/target trade)
POC_d = POC price of completed UTC day d. Up signal at the end of day d: POC_d > POC_{d-1} > POC_{d-2} (strict). Down signal = mirror. Entry = open of the first 1m bar of day d+1; direction = the shift direction. Horizon 1 (primary): exit at the open of day d+2. Horizon 3 (secondary): exit at the open of day d+4, using non-overlapping signals only (greedy: after a signal, skip signals until its exit). Net bp = side x (exit/entry - 1) x 1e4 - 10. Both horizons are judged by the same bar; the verdict that counts for R2 is Horizon 1, Horizon 3 is reported as secondary.

## Sample
DEV only: R1 entries and R2 signals' entry days 2022-02-01 00:00 UTC .. 2024-05-31 23:59 UTC. DEV halves split at the exact midpoint of that span (2023-04-02 UTC): both halves must be positive. Data after 2024-06-07 is not loaded (runoff to finish open trades only); VALIDATION (2024-07-01 on) is never read.

## Placebo (direction-matched; 500 draws, seed 1)
R1: per real trade a random 15m entry bar inside DEV, same side, same stop % and same target % distances, same 96-bar cap; fee same. R2: per real signal a random entry day inside DEV, same side and same horizon, same fee. Report the placebo mean (mean of draws) and the share of draws at or above the real mean. Direction match controls long-biased drift only through the side counts.

## Pass bar (fixed now)
PASS: fee-net mean > 0 (R1 net R per trade; R2 net bp per signal) and t >= 2 (t = mean / (sd / sqrt n)) and both DEV halves mean > 0. FAIL: mean <= 0. Otherwise INCONCLUSIVE (including n < 30). PASS is not an edge claim: it earns only a VALIDATION run in a separate pre-registered step and the trial-count correction.

## RESULT.md must hold
Per rule: n, win rate, mean net R (R2: net bp), t, both DEV halves, max drawdown (sum of R or bp, peak to trough), per-year and long/short rows from MyTradingSys/backtest/trade_sanity.py (log_sanity + year_side_lines), placebo row, a `Regime mix:` line, verdict in plain words.
Tests: test_va_poc.py with hand-computed profile, value-area and POC values.
