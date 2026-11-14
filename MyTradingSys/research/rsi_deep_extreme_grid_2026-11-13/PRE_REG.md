# PRE-REG: deep RSI extreme + confirming candle, event table and grid (edge3-rsi-deep-extreme-grid-1113)

Written and committed before any outcome (stop/target/return) is computed. Only the regime mix (a property of BTC daily closes, not of any trade) was computed first.

## Hypothesis (operator rule, 2026-11-13 17:00Z)
When RSI(14) on a timeframe TF closes at a deep extreme (<= T), and the NEXT TF bar is green and closes above the signal bar's close, buying at that close with the stop at the signal bar's low has positive fee-net expectancy, more so when the daily RSI is also very low. Sanity example (verified before the study): BTC 1h bar opened 2026-11-13 05:00Z, red, close 68106.7, RSI 9.2, low 67468.4; next bar green, close 69034.8 = entry; stop 67468.4 = 2.27 % away.

## Context
Prior test of this family (edge-rsi-extreme-confirm-1113): 0 of 384 cells passed, but stops were fixed-% / ATR and entry was the next open. This study uses the operator's own stop (signal-bar low) and entry (confirm-bar close), adds 4h/8h/12h, a daily-RSI split, a layer split and an exit-location table. Deep extremes are rare (BTC 1h RSI <= 10: ~6 episodes since 2020), so most cells will be UNDERPOWERED; part A is descriptive and is the main deliverable.
Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %): DEV bull 57 % / bear 34 % / range 9 %; VALIDATION bull 62 % / bear 11 % / range 27 %; RECENT bull 36 % / bear 54 % / range 10 %.

## Data and splits
Bybit v5 public linear klines, 1h and 1D, 2020-01-01..now, 10 coins: BTC ETH SOL BNB XRP DOGE ADA LINK AVAX LTC (from listing). Bybit 1h open interest for layer 3 (missing history stays blank). The still-forming bar is dropped. 4h/8h/12h are folded from 1h, UTC epoch anchored (8h opens 00/08/16, 12h 00/12), incomplete groups dropped. RSI = Wilder 14 on the TF closes.
Splits by ENTRY (confirm close) time: DEV 2020-01-01..2024-06-30, VALIDATION 2024-07-01..2025-06-30, RECENT 2025-07-01..now.

## Rules (SOURCED = operator's words; OURS = our choice)
- Signal: TF in {1h, 4h, 8h, 12h}, T in {10, 12, 15, 20} (T=10, 15, 20 and 12 are OURS around his 9.2 example). First touch per episode; re-arm only after RSI(TF) closes > 30 (OURS).
- Confirm (SOURCED): next TF bar green (close > open) AND close > signal bar close. Entry = that close. No confirm = no trade (row kept in part A with confirm = no). A confirm bar whose low is under the signal low is kept and flagged `undercut` (stop was not yet live).
- Stop (SOURCED): signal bar low. Stop fill = min(stop, bar open) (gap), same-bar stop and target = stop first. No slippage term (limitation).
- All forward walks run on 1h bars starting at the first hour after the entry close (the entry bar itself is never read). Window 168 h.
- Fees: 2 x BINANCE_TAKER imported from MyTradingSys/backtest/fees.py, charged on entry price, divided by stop distance to get R. Funding not modelled (limitation, small for <= 72h holds).

## Part A (descriptive, no pass/fail)
Per episode: date, coin, TF, T, daily RSI (last closed daily bar at the signal close), confirm yes/no, stop distance % = (entry - signal low)/entry, from the entry: max favourable and max adverse move over the next 6/24/72 wall-clock hours (raw, ignoring the stop), whether the signal low broke before +1R, +2R, +3R (reached first / stop first / neither in 72 h), hours until the signal low broke (within 168 h), forward return at 24h/72h/7d, RSI(TF) at the TF bar holding the highest 1h high of the next 72 h. BTC row by row; counts pooled per coin.

## Part B (tested cells: 60)
Cells = (TF, T) x exit: (1h,10) (1h,15) (1h,20) (4h,10) (4h,15) (4h,20) (8h,15) (8h,20) (12h,15) (12h,20) = 10 combos, times 6 exits = 60. T=12 and (8h,10) (12h,10) appear in part A only. Exits: +1R, +2R, +3R target (72 h cap, exit at close of the 72nd hour), exit when RSI(TF) closes > 50 (168 h cap), time stop 24 h, time stop 72 h; the stop is active in every exit. Trades with a full 168 h of forward data only. Primary metric: fee-net mean R per trade.
Universe: 10-coin pooled is the decision universe (n counts per split); BTC alone is reported but underpowered. Daily RSI bands {<=20, 20-25, 25-30, 30-40, >40} are a descriptive split of each cell (n stated), not extra tested cells.
Bootstrap: week-block (ISO week of entry, all coins in a week share a block), 2000 resamples; CI = 2.5/97.5 percentiles of the mean; one-sided p = share of resampled means <= 0.
Placebo: per cell, 100 draws; each real trade is replaced by a random TF-bar close of the same coin in the same ISO week with the same stop distance (stop = entry x (1 - real stop distance)), same exit rule; for the RSI>50 exit placebo entries are drawn only from bars with RSI(TF) <= 35 (else the exit fires at once). Placebo p = share of draw means >= the real mean.
PASS (all): VALIDATION fee-net mean > 0, bootstrap CI lower bound > 0, n >= 30, placebo p <= 0.05, and BH-significant at 10 % over the 60 VALIDATION p-values. ROBUST adds DEV mean > 0 and RECENT mean > 0. Fewer than 30 trades in VALIDATION = UNDERPOWERED. Verdict wording: PASS / FAIL / UNDERPOWERED; no edge claim unless PASS.

## Part C (layers, descriptive)
On pooled confirm-yes events, per TF at T=20 (superset of deeper T), n per cell, cells with n < 30 marked THIN: (1) daily close above/below 200d SMA; (2) daily ADX(14) >= 25 with -DI > +DI vs not; (3) open interest over the last 4 TF bars into the signal fell vs rose (blank when OI history missing); (4) signal-bar volume >= 2x the mean of the previous 20 bars vs not; (5) session of the signal bar open (UTC 0-8 Asia, 8-16 Europe, 16-24 US) and weekday vs weekend. Measures: win rate = share reaching +1R before the stop within 72 h, mean net R of the +2R-target exit.

## Part D (where to sell, descriptive)
On confirm-yes events (pooled, per TF, T=20): median max favourable move (R and %) within 24 h / 72 h; share reaching +1R/+2R/+3R before the stop; share where the signal low is broken within 7 days ("new low, sell it" case); all split by daily trend (above/below 200d SMA).

## Limits stated now
No slippage, no funding, daily-bucket and layer splits are small-n, 10 coins are highly correlated (week blocks handle part of it), the last 7 days of data are excluded from tested trades but are used for the live-trade check.
