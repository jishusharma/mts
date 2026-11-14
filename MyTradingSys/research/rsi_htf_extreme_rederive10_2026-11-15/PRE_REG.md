# PRE-REG: re-derive HTF RSI extreme (next bar closes above, stop = extreme low) on 10 symbols, fee-net OOS 2024+ (rederive-rsi-htf-extreme-1115)

Written before any trade outcome of this 10-symbol run is computed. Parent: rsi_htf_extreme_2026-11-13 (20 coins, 0/40 PASS, 1 BH-significant cell with n 21). Only the BTC daily regime mix (a property of daily closes, identical to the parent's) was looked at first.

## Hypothesis (operator rule, 2026-11-13)
RSI(14) on a closed 4h / 8h / 12h bar reaches an extreme (red bar); if the NEXT bar of that timeframe closes above the extreme bar's close, long at that close with the stop at the extreme bar's low has positive fee-net expectancy, more so with daily RSI < 30. Question here: does the parent's picture (VALIDATION positive, DEV negative, 0 PASS) survive on the 10 most liquid symbols only, with the same rules, code and cost model?

## Context
Regime: no regime filter; the daily RSI < 30 gate (4 cells) is the only conditioner. DEV is bull/bear mixed, VALIDATION bull-leaning.
Phase: counter-trend long entries in sold-off conditions (capitulation, mostly below the daily 200d SMA).
Session: not filtered (TF bars cover all sessions).
Entry: close of the confirming bar. Prior tests of this family: edge-rsi-extreme-confirm-1113 (0/384), edge3-rsi-deep-extreme-grid-1113 (0/60), rsi_htf_extreme_2026-11-13 (0/40, 20 coins), rsi_htf_power_2026-11-13 (new-data power test).
Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %, else range): DEV (2020-2023) bull 51 % / bear 40 % / range 10 %; VALIDATION (2024-now) bull 56 % / bear 30 % / range 15 % (same BTC series as the parent; re-checked in RESULT).

## Data and splits
Bybit v5 public linear klines (1h, 1D), 2020-01-01..now. Universe (10, fixed now, top by liquidity, chosen without looking at outcomes): BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX (a strict subset of the parent's 20). Folding, Wilder RSI and daily-RSI lookup are the parent's code (htf_lib.py, rsi_grid_lib.py copied unchanged). Splits by ENTRY (confirm close): DEV 2020-01-01..2023-12-31, VALIDATION (out of sample) 2024-01-01..now. Verdicts use VALIDATION only.

## Rules (SOURCED = operator's words; OURS = our choice)
- Signal (SOURCED): TF RSI(14) <= T on a closed red bar; T for 4h in {20, 15, 12}; 8h and 12h in {25, 20, 15}. First touch per episode, re-arm after RSI(TF) closes > 30 (OURS).
- Confirm (SOURCED): next contiguous TF bar closes above the signal bar's close; entry = that close.
- Stop (SOURCED): low of the signal bar; fill = min(stop, bar open); same-bar stop+target = stop first; 1h forward walk, entry bar never read.
- Exits: targets +1R/+2R/+3R (SOURCED), cap 20 TF bars (OURS); time exit = close of 10th TF bar (SOURCED 10 bars). Stop active in all.
- Costs (OURS, conservative): per side fees.BINANCE_TAKER (5 bp) + fees.SLIPPAGE_RT_S13/2 (1 bp), imported from MyTradingSys/backtest/fees.py. Net R = (gross return - round-trip cost) / stop distance. No funding (limitation).
- Trades need a full 20-TF-bar forward window.

## Cells (40, fixed now, same grid as the parent)
A. 9 TF/T combos x 4 exits = 36 ungated. B. (4h, T=12) with daily RSI < 30 x 4 exits = 4.
Primary metric: fee-net mean R per trade. Also reported, not in the verdict: day-cluster mean/CI, median R, daily-RSI band split.

## Statistics and PASS (unchanged)
Week-block bootstrap (2000) on VALIDATION; placebo 100 draws (same coin, same ISO week, same stop distance); PASS = VAL mean > 0, CI lower > 0, VAL n >= 30, placebo p <= 0.05, BH 10 % over the 40 VALIDATION p-values. VAL n < 30 = UNDERPOWERED. No edge claim unless PASS. Extra rule fixed now: a cell must also have DEV mean >= 0 or its sign flip is stated; day-cluster CI lower > 0 is reported next to the verdict and a PASS with day CI crossing 0 is called FRAGILE (not an edge claim).

## Limits stated now
10 coins are strongly correlated (week-block and day view both matter); fewer signals than the parent so more cells UNDERPOWERED is expected, in particular the daily<30 gate; no funding; tiny stop distances inflate R; cells share entries across exits so BH is approximate; placebo of random same-week longs is weak.
