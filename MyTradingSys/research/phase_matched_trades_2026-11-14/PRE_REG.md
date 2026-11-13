# PRE_REG: phase-matched trade types (slug edge9-phase-matched-trades-1114)

Written and committed BEFORE any outcome is computed. Only the raw data download (fetch_bybit.py) has run.

## Hypothesis
Operator principle, 2026-11-13 20:15Z (SOURCED: operator): context decides everything. In a downtrend look for shorts, in an uptrend shorts are foolish (buy dips), ranges need range trades. Today's 14 failed tests mostly ran one rule across all phases. Claim tested: each trade type has positive fee-net expectancy in its matching phase and clearly less (or negative) in the mismatched phases. Phase labels and trade-type definitions are OURS; the pairing (downtrend short rallies and breakdowns, uptrend buy dips, range edge fades) is the operator's, SOURCED. Bible (research/mts_bible/BIBLE.md) gives the cycle clock only, no daily-phase rule, so the classifier below is OURS.

## Context
Regime: the phase classifier below IS the context gate (decided at each daily close, no look-ahead).
Phase: UP / DOWN / RANGE per coin per day (OURS). Cycle phase of BTC (Bible: cycle clock) is not used; the Regime mix line reports phase shares and BTC's phase today.
Session: none; 24h market, entry hour not filtered.
Entry: always the open of the 1h bar after the signal bar closes.

## Data
- Bybit v5 public linear USDT klines, 1h and 1d, 20 coins: BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT TRX BCH ATOM NEAR UNI APT ARB OP SUI, from listing (>= 2020-01-01) to download time; funding history from the same API. The last unfinished bar is dropped. Raw data in runtime_data (git-ignored). Coins listed late simply contribute fewer days.
- Fees (SOURCED: fees.py BINANCE_TAKER 5 bp, same value used by prior studies): 5 bp per side. Slippage 2 bp per side, OURS. Round trip 12 bp. Funding settled while held (entry open < settlement <= exit bar close): long pays rate, short receives it.
- Splits by entry bar time: DEV 2020-01-01..2023-12-31, VALIDATION 2024-01-01..download time. Nothing is tuned on DEV; DEV is reported for stability only.

## Phase classifier (OURS, one fixed definition, per coin, daily bars)
At the close of UTC day d (daily bar open + 24 h), using only bars up to and including day d:
- MA20 = simple 20-day mean of closes. ADX(14), +DI, -DI: Wilder smoothing (SOURCED: Wilder 1978, n = 14).
- UP: close > MA20 and MA20(d) > MA20(d-5) and ADX >= 20 and +DI > -DI.
- DOWN: close < MA20 and MA20(d) < MA20(d-5) and ADX >= 20 and -DI > +DI.
- RANGE: everything else. Needs 20 + 14 bars of history; earlier days are unlabelled and unused.
- Application: the label of day d applies to 1h bars whose open is >= the close of day d, i.e. all bars of day d+1. A signal bar and its entry are labelled by the phase in force at the SIGNAL bar's close (day d+1 bars carry the day-d label). Never the same day's label.
- Reported: share of days per phase (pooled, per coin, BTC), and BTC's phase at its last closed day.

## Trade types (all 1h; entry at open of bar S+1 after signal bar S closes; stop-first inside one bar; a gap beyond the stop fills at the open; one position per (type, coin, phase cell) at a time)
Indicators: RSI(14) Wilder (rsi_core, unchanged), EMA(20) of 1h closes (SOURCED: operator), prior day high/low = the last completed UTC day before bar S's day (PDH, PDL).
- T1 short the rally (matched: DOWN). Signal bar S: RSI(S) >= 60 AND (high(S) >= PDH OR [close(S-1) < EMA(S-1) AND high(S) >= EMA(S)]). Short at open(S+1). Rally high RH = max high of bars S-5..S (6 bars, OURS). Stop = RH x 1.001. Exits: primary 2R; also 1R and PDL (only if PDL < entry, else the trade is skipped for that variant). Time stop 24 bars (close of the 24th bar).
- T2 buy the dip (matched: UP), mirror. RSI(S) <= 40 AND (low(S) <= PDL OR [close(S-1) > EMA(S-1) AND low(S) <= EMA(S)]). Long. Dip low = min low S-5..S. Stop = dip low x 0.999. Exits: primary 2R; also 1R and PDH (if above entry). Time stop 24.
- T3 fade the range edges (matched: RANGE). Range = highest high and lowest low of the 20 completed days before S's day (H, L); require (H-L)/L >= 4% (OURS, so the mid target clears costs). Short: high(S) >= 0.99 H and close(S) < open(S) and upper wick >= body (rejection close). Long: low(S) <= 1.01 L and close(S) > open(S) and lower wick >= body. Stop = H x 1.005 (short) or L x 0.995 (long) (SOURCED: operator 0.5 %); skip if entry is already beyond the stop. Target = mid (H+L)/2 (primary and only), skip if mid is not on the profit side. Time stop 72 bars (OURS).
- T4 breakdown continuation (matched: DOWN). Short when close(S) < PDL and close(S-1) >= PDL (first 1h close below). Stop = most recent confirmed 1h swing high before S (pivot: high higher than the 3 bars either side, confirmed by S, searched 48 bars back, OURS) and above entry, else no trade. Primary exit 2R; time stop 24.
- Each trade type is run in all three phases; phase = phase at signal. Matched cells: T1/DOWN, T2/UP, T3/RANGE, T4/DOWN. The other 8 cells are the mismatched controls (same rule, other phase).
- Primary exit per matched row is the one marked primary (2R, 2R, mid, 2R). Other exits (1R, PDL/PDH) are descriptive and not in the BH family.

## Metric and gates
- Net R per trade = (direction x (exit/entry - 1) - 0.0012 - direction x funding) / (|entry - stop| / entry). Also win rate, mean net %, trade counts per split.
- Matrix: phase x trade type of VALIDATION mean net R (primary exit), with n and win rate; DEV matrix alongside.
- Gates per matched row (all must hold; PASS = all):
  1. VALIDATION n >= 100 (else UNDERPOWERED, never "no edge").
  2. VALIDATION mean R > 0 with 95 % bootstrap CI lower bound > 0 on the per-trade view (2000 draws) AND on the day-cluster view (resampling UTC days, 2000 draws; all coins of a day are one cluster).
  3. Beats random entries: same coin, same phase, VALIDATION period, same side, same holding time in bars as each observed trade, random 1h entry bar, exit at the close of the held bar (no stop/target), same costs and funding. Compare mean net % per trade; p = share of 1000 resampled random means >= the observed mean; need p < 0.05.
  4. BH at 10 % over the 4 matched rows, on one-sided day-clustered normal p-values of mean R > 0 (VALIDATION).
  5. Positive without the best 5 days: drop the 5 UTC days with the largest summed R in VALIDATION; remaining mean R > 0.
- Extra descriptive: BTC alone per cell; matched minus best mismatched cell mean R for each trade type (day-clustered diff); 14 bp cost sensitivity not run.
- Verdict: PASS if any matched row passes all gates; FAIL if none and every matched row has VALIDATION n >= 100; UNDERPOWERED if a failing row has n < 100 and nothing passes. State plainly whether the matched cell beats the mismatched cells (the operator's principle) irrespective of the pass verdict.

## Test requirement
test_engine.py: phase lookup uses the previous day's label for all bars of a day; a deliberately wrong version (phase of the same day used for earlier bars of that day) must fail the test at least once (recorded in RESULT).
