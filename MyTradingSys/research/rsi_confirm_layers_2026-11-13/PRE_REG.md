# PRE-REG: layers on the operator's RSI-extreme + confirm-candle long (edge4-rsi-confirm-layers-1113)

Written and committed before any outcome (stop/target/return) is computed. Only the BTC regime mix (a property of BTC daily closes, not of any trade) was computed first.

## Hypothesis (operator, "apply different layers")
The bare rule (RSI(14) on 1h or 4h closes <= 20; next bar green and closing above the signal close = entry at that close; stop = signal-bar low) fails alone (base study edge3-rsi-deep-extreme-grid-1113: 1h RSI<=20 pooled 545 trades, 41 % reach 1R, signal low broken within 7 days in 82 %). Hypothesis: ONE closed-data layer measured at the signal bar separates winners from losers well enough to give positive fee-net expectancy out of sample.

## Context
Regime: the layers (trend state, ADX) are the regime question itself; no outer regime gate.
Phase: the rule is a counter-trend dip buy (long into an oversold flush), so the layers ask which kind of flush (trend state, capitulation volume, positioning unwind, funding, time of day, depth) is a bounce rather than a continuation.
Session: all 24 h; session of the signal bar is itself a layer.
Entry: close of the confirming bar (SOURCED, operator). Prior family result: 0 of 60 grid cells passed (edge3) and 0 of 384 (edge-rsi-extreme-confirm); this study only adds filters to the same trades and cannot create new ones.
Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %): DEV 2020-01-01..2023-12-31 bull 51 % / bear 40 % / range 10 %; VALIDATION 2024-01-01..now bull 56 % / bear 30 % / range 15 % (first 18 months bull 74 % / bear 7 %; from 2025-07 bull 36 % / bear 54 %).

## Data, universe, splits
Bybit v5 public linear (USDT perps), 20 coins from listing: BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM NEAR UNI TRX BCH ETC FIL APT ARB. 1h and 1D klines, funding history (8 h), 1h open interest. Still-forming bar dropped; last 7 days excluded from tested trades (need 168 h of forward data).
Splits by ENTRY (confirm close) time: DEV 2020-01-01..2023-12-31, VALIDATION 2024-01-01..data end (operator's split; overrides the brief's default dates). No RECENT cut.

## Base trade set (SOURCED = operator words, OURS = our choice)
- Signal bar s on TF in {1h, 4h}: Wilder RSI(14) of TF closes <= 20 (OURS, the base study's widest, so deeper T are subsets), first touch per episode, re-arm after RSI > 30 (OURS). 4h folded from 1h, UTC-anchored.
- Confirm (SOURCED): bar s+1 green (close > open) and close > close of s. Entry = close of s+1. Stop = low of s (SOURCED; "red candle low"). No confirm = no trade. Long only.
- Exits (two only, OURS): target +1R and target +2R, R = entry - stop; 72 h cap exit at close of 72nd hour; stop active; stop fill = min(stop, bar open); same-bar stop+target = stop. Forward walk on 1h bars after the entry bar.
- Fees: 2 x BINANCE_TAKER from MyTradingSys/backtest/fees.py (10 bp round trip, taker both legs; conservative against the brief's 4 bp/side), charged on entry price, divided by stop distance = R. No extra slippage constant (fees.py has none; limitation). Funding not charged (<= 72 h holds; limitation).
- Four base sets: (1h,+1R) (1h,+2R) (4h,+1R) (4h,+2R). Pooled over 20 coins.

## Layers: 14 pre-registered splits (each = the filtered subset, complement reported descriptively, not tested). All use data CLOSED at or before the signal bar's close.
1. dADX<20: daily ADX(14) (Wilder, last closed daily bar) < 20.
2. dADX 20-25: 20 <= daily ADX < 25.
3. dADX>25: daily ADX > 25 (>= 25 for the boundary is not used).
4. dDI-down: daily -DI > +DI (downtrend).
5. 4hADX>=40: ADX(14) of the last closed 4h bar (for the 4h base: the signal bar itself) >= 40.
6. OI-unwind: open interest at signal close / 24 h earlier - 1 <= -3 % (Bybit 1h OI; trades without OI history are excluded from this split and n is reported).
7. VolCap: signal-bar volume >= 3 x mean volume of the 50 bars before it (same TF).
8. BTC>200MA: BTC daily close above its 200-day SMA (last closed daily bar).
9. BTC/ETH: the coin is BTC or ETH (vs the 18 alts).
10. Asia: signal bar opens 00-08 UTC.
11. US: signal bar opens 16-24 UTC (Europe 08-16 is the leftover, descriptive only).
12. FundNeg: last funding rate settled at or before signal close < 0.
13. Deep: signal RSI <= 10 (vs 10-20).
14. SmallR: stop distance (entry-low)/entry in the lowest tercile of all base trades of that TF (terciles computed on DEV trades only, applied to all).
Tested units: 4 base sets x 14 splits = 56. Also descriptive only: Europe, RSI 10-15 / 15-20, R tercile 2/3, complements.
Layer "helps" = ALL of, on VALIDATION: filtered n >= 30; fee-net mean R > 0; week-block bootstrap (ISO week of entry, 2000 resamples, seed fixed) 95% CI lower bound > 0; filtered mean > unfiltered base mean on the same split; beats a random-subset placebo (1000 random subsets of the unfiltered VALIDATION base trades of the same n; placebo p = share of subset means >= filtered mean; need p <= 0.05); Benjamini-Hochberg 10 % over the 56 bootstrap one-sided p-values (share of resampled means <= 0). Fewer than 30 = UNDERPOWERED (never PASS).
DEV screen (for pairs only): n >= 30, mean R > 0 and > DEV base mean.

## Pairs (stage 2)
Only layers passing the DEV screen. At most 3 pairs, chosen on DEV only (highest DEV mean R of the intersection with n >= 30, over base sets, no more than one pair per base set unless fewer than 3 base sets qualify). Judged on VALIDATION with the same rule, BH 10 % over the pairs tested. If fewer than 2 layers pass the DEV screen, no pairs are run.

## Metrics
Win% = share of trades with net R > 0 (target hit before stop, after fees). Mean net R per trade, bootstrap CI, n per split reported for DEV and VALIDATION.

## Limits stated now
Trades overlap across 20 correlated coins (week blocks handle part); no slippage, no funding; VALIDATION is mostly bull regime; OI history starts mid-2020 and by coin listing; 56 tests at n=30..300 means low power: most cells will be UNDERPOWERED/FAIL and no edge claim is made unless all conditions hold.
