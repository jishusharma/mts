# PRE-REG: where to sell the RSI-extreme + confirming-candle long (edge4-rsi-confirm-exits-1113)

Written and committed before any exit outcome is computed. Only the regime mix (a property of BTC daily closes) was computed first.

## Hypothesis
Base study (edge3-rsi-deep-extreme-grid-1113): the operator's entry (1h RSI(14) <= T, next bar green and closing above the signal close, buy at that close, stop = signal-bar low) fails with fixed R targets: ~41 % reach +1R, the signal low breaks within 7 d in 82 % of cases. Open question: is there an EXIT (earlier / adaptive) that makes the same entries fee-net positive?

## Context
Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %): DEV (2020-01-01..2023-12-31) bull 51 % / bear 40 % / range 10 %; VALIDATION (2024-01-01..now) bull 56 % / bear 30 % / range 15 %.
Regime: no regime gate; the regime split (see Regime mix) is descriptive only.
Phase: oversold-bounce / mean-reversion long into a capitulation bar, any regime (regime split is descriptive only).
Session: any (24h).
Entry: close of the confirming bar (market order, taker); the entry bar is never read forward.

## Data, universe, splits
Bybit v5 public linear 1h + 1D klines from 2020-01-01 (from listing), 20 coins: BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT TRX ATOM UNI FIL NEAR BCH ETC XLM AAVE. Still-forming bar dropped; closed bars only. 4h folded from 1h (UTC anchored). RSI = Wilder 14.
Splits by ENTRY time: DEV 2020-01-01..2023-12-31; VALIDATION 2024-01-01..now. Trades need a full 168 h of forward 1h data (so the last 7 days are excluded).

## Trade sets (entries, identical to base: first touch per episode, re-arm after RSI > 30, confirm = next bar green AND close > signal close, no confirm = no trade, stop = signal-bar low, entry = confirm close)
- S1 (PRIMARY, the only set whose verdicts are the headline): 1h, RSI <= 20.
- S2: 1h, RSI <= 15.  S3: 4h, RSI <= 20 (entry = 4h confirm close; all exits walk 1h bars after it).
S2/S3 are replications, each with its own BH over its 16 rules; no edge claim from them unless S1 also passes.

## Part 1 (descriptive, no pass/fail)
Per set, all dates pooled: raw MFE and MAE in R (R = entry - signal low) after 1,2,4,8,12,24,48 hourly bars (max high / min low, ignoring the stop; median); share reaching +0.5R/+1R/+2R before the stop within 72 h; median hours to the peak (highest high before the stop is hit, within 72 h); share that first reach +0.5R and are later stopped out within 72 h (before reaching +1R).

## Part 2: 16 exit rules, fixed now (stop always live; walk = 1h bars after entry; closed bars; stop checked before any target/exit within the same bar = conservative; stop fills at min(stop, bar open); target fills at the target price; every other exit fills at the bar close unless stated)
 1. time2: exit at close of the 2nd bar.  2. time4.  3. time8.
 4. tgt0.5R (cap 72 h, then close).  5. tgt0.75R (cap 72 h).
 6. rsi30: exit at the close of the first 1h bar with 1h RSI > 30 (cap 168 h).  7. rsi40.  8. rsi50.
 9. ma20touch: exit when a bar's high reaches the 20-bar SMA of 1h closes as of the PRIOR bar close (fill max(level, open)); cap 168 h. (Bollinger mid-band of a 20-bar BB is exactly this SMA20, so (d) is one level.)
10. ma20close: exit at the first 1h bar CLOSING above its own 20-bar SMA (cap 168 h).
11. be_tgt2: after a bar's high >= +0.5R the stop moves to entry from the NEXT bar; target +2R; cap 72 h.
12. trail: after a bar's high >= +0.5R the stop trails: from the next bar on, stop = max(previous stop, prior bar's low); cap 168 h.
13. half_trail: at +0.5R sell half at the 0.5R price (stop checked first in that bar); the other half then trails exactly as rule 12; cap 168 h. R = blended.
14. confstop_1R: stop = low of the confirm candle (the confirming TF bar) instead of the signal low; target +1R of that (smaller) risk; cap 72 h.
15. confstop_2R: same stop, target +2R of that risk; cap 72 h. (extra variant of (h), kept inside the 16.)
16. base_1R: signal-low stop, +1R target, cap 72 h (reference; reproduces the base finding).
Order of ties within a bar: stop > target/exit. RSI exits use 1h RSI even for S3.

## Costs (net R)
fee = 2 x fees.BINANCE_TAKER (imported; 5 bp/side in the repo, i.e. slightly above the 4 bp mentioned in the brief) + fees.SLIPPAGE_RT_S13 (2 bp round trip) of entry price, divided by the stop distance in the same R. Gross = no costs. Net = the pass-rule number. No funding (holds <= 7 d). Small targets are punished harshly by cost/stop-distance; both columns are shown. Tiny stop distances are NOT filtered (the operator's rule has no filter); median R and %-return mean are reported next to the mean.

## Pass rule (per exit rule, set S1; VALIDATION only)
ALL of: (1) VALIDATION mean net R > 0; (2) week-block bootstrap (ISO week of entry, 2000 resamples, seed fixed) 95 % CI lower bound > 0 on the trade-level mean; (3) same CI lower bound > 0 on the day-cluster view (same-day signals across coins averaged to one value per entry day, then week-block bootstrap of the day means); (4) n >= 30 trades; (5) placebo p <= 0.05; (6) Benjamini-Hochberg at 10 % over the 16 VALIDATION one-sided p-values (trade-level bootstrap p = share of resampled means <= 0). n < 30 = UNDERPOWERED. ROBUST additionally needs DEV mean net R > 0. Verdicts: PASS / FAIL / UNDERPOWERED.
Placebo: 30 draws; each real trade is replaced by a random 1h bar close of the same coin in the same ISO week (for S3: a random 4h-aligned close), keeping the real trade's stop distance (stop = entry x (1 - stopdist)); same exit rule. For RSI and MA exits (6-10) draws are restricted to bars with close < SMA20 and 1h RSI <= 40 (otherwise the exit fires at once). Placebo p = share of draw means >= the real mean (+1/+1 smoothing), computed on VALIDATION trades.

## Limits stated now
10 of the 20 coins join the universe by listing date; coins are highly correlated (week blocks and the day view handle part); no funding; one placebo draw design; the 1h bar cannot resolve intrabar order (stop-first is pessimistic); VALIDATION is a single regime stretch (2024+: bull 56 %).
