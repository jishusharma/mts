# PRE-REG: confirmation of two 4h RSI-extreme exits on 40 coins the parent never saw (edge5-rsi-4h-exits-newcoins-1113)

Written and committed before any outcome is computed. Only the BTC-daily regime mix and the coin list (volume rank + listing date) were computed first.

## Hypothesis
Parent (edge4-rsi-confirm-exits-1113, rsi_confirm_exits_2026-11-13/): on set S3 (4h RSI(14) <= 20, next 4h candle green and closing above the extreme candle's close = long at that confirm close, stop = extreme-candle low) two exits came close on 20 coins but did not pass: time8 (net +0.196R, win 68 %, CI [-0.07,+0.40]) and confstop_2R (net +0.264R, CI [-0.12,+0.66]); DEV was negative for both. Question: do they hold on 40 other coins? Pure confirmation, no tuning.

## Context
Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %, else range), 2021-01-01..2026-11: bull 51 % / bear 36 % / range 12 %; 2024-01-01..now: bull 56 % / bear 30 % / range 15 %.
Phase: oversold-bounce / mean-reversion long into a 4h capitulation candle on alts, any regime (regime split descriptive only). Session: any (24h). Entry: close of the confirming 4h candle (market, taker); the entry bar is never read forward; closed bars only.

## Universe (fixed now, SOURCED = rule, OURS = the 90-day-history-style cut)
Bybit v5 public SPOT USDT pairs ranked by 24h turnover on 2026-11-13 (tickers endpoint). Excluded: the parent's 20 coins, stablecoins, wrapped/staked/commodity/stock-token symbols. OURS filter: first monthly kline on or before 2023-01-01 (>= ~3 y of history; a pure volume rank returns mostly 2025-26 listings with no history). Top 40 that pass, in rank order:
GRAM INJ QNT IMX HBAR ICP APEX MANA XDC SHIB STX FLR CRV OP BAT APT GALA TWT LDO HNT ALGO BONK APE GRT ZEN RUNE GMX DYDX CAKE THETA SAND WAVES CHZ MINA MPLX ENS AR XTZ NEXO JASMY.
(Survivorship caveat: the list is chosen by CURRENT volume, so coins that died are absent.)
Data: Bybit v5 public spot 1h klines from 2020-01-01 (from listing, spot begins ~2021); still-forming bar dropped; 4h folded from 1h UTC-anchored (only full groups). RSI = Wilder 14. Code reused unchanged from the parent: rsi_grid_lib.py (fold, wilder_rsi, episodes, confirm_info), exits_lib.py (fwd_sim exit engine); study.py only swaps the universe, trade set, stats.

## Test set
The whole new-coin set is the test set (no DEV/VALIDATION split, nothing tuned). Trades need 168 h of forward 1h data after entry (as in the parent). Also reported: 2024-01-01-onward slice and per-year means.

## Cells (EXACTLY two)
- time8: S3 entry, exit at the close of the 8th 1h bar after entry; stop = signal-candle low live throughout (stop-first on any bar, fills at min(stop, open)).
- confstop_2R: S3 entry, stop = low of the confirm candle, target +2R of that risk, cap 72 h, stop-first, target fills at its price.
Entry rule S3 (identical to parent): first touch per episode of 4h RSI <= 20, re-arm after RSI > 30, confirm = next 4h candle green AND close > signal close; no confirm = no trade.

## Costs (net R)
fee = 2 x fees.BINANCE_TAKER (imported; 5 bp/side) + fees.SLIPPAGE_RT_S13 (2 bp round trip) of entry price, divided by the stop distance (same R). No funding (<= 72 h holds). No stop-distance filter.

## Pass rule (per cell; ALL must hold)
1. Fee-net mean R > 0. 2. 95 % bootstrap CI lower bound > 0 on the per-trade view (week-block bootstrap by ISO week of entry, as parent, 2000 resamples). 3. Same on the day-cluster view: signals of the same entry date averaged to one value per day, then bootstrapped (a plain resample of days AND the week-block of days; both lower bounds must be > 0). 4. n >= 100. 5. Placebo: 200 draws, each real trade replaced by a random 4h-aligned close of the same coin in the same ISO week, keeping the real stop distance, same exit; placebo p = (1 + #draws with mean >= real)/(201). 6. Bonferroni over 2 cells: placebo p <= 0.025 and the per-trade bootstrap one-sided p (share of resampled means <= 0) <= 0.025. n < 100 = UNDERPOWERED. Verdict PASS / FAIL / UNDERPOWERED.
Concentration (reported, not a gate): share of the cell's total net R from its best 5 signal days, and mean net R with those 5 days removed (a PASS whose mean-without-top-5 is <= 0 is flagged FRAGILE).

## Parameter labels
RSI period 14, threshold 20, re-arm 30, confirm rule: OURS (the operator's rule, taken from the parent). time8 / confstop_2R / 72 h cap: OURS (picked from the parent's 16 exits, the two nearest to passing; selection bias is exactly why this is a held-out test). Fees 5 bp/side, slippage 2 bp: repo constants (SOURCED fees.py). Bootstrap/placebo design: parent's.

## Limits stated now
Current-volume universe (survivorship); alts are highly correlated (day and week views handle part); no funding; spot instead of the parent's perp klines (different venue series, same Bybit API); 1h bar cannot resolve intrabar order (stop-first is pessimistic); the test period is bull-heavy.
