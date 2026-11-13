# PRE-REGISTRATION: bear-trap reclaim, LONG day trade, only in a downtrend (frozen 2026-11-14, before any outcome)

Code: `study.py`, tests `test_study.py`, fetch `fetch.py`. Written and committed before study.py was run on any data.

## Hypothesis
After a long decline, price that sweeps below a prior low (a bear trap) and is reclaimed within 6 hours has flushed the stops under that low; going long at the next bar open earns a positive fee-net R over the next 24 h, beating a random entry in the same coin, hour and hold. The edge, if any, is concentrated in a downtrend context.

## Context
- Why now: operator order 2026-11-13 20:05Z: long edges after a long decline (bear traps and retests); BTC has 6 red weeks in a row.
- Phase/regime: the filter below IS the regime spec; the unfiltered rows are the control. RESULT.md prints `Regime mix:` (share of events and of all hourly bars that pass the filter, and by year).
- Earlier studies, and how this one differs (read, not repeated): `eur_low_sweep_reclaim_pooled_2026-11-13` (Europe-session low swept in the US window, 5m, BTC/ETH/SOL, long and short, FAIL: VAL means -0.23 to +0.1 R) and `reclaim_close_stop_2026-11` (BTC 4h/1D, stop = close back below, DEV only, INCONCLUSIVE). This study differs on: levels (prior day low and prior WEEK low, not session lows), timeframe (1h), pool (20 coins), a trend-context filter with an unfiltered control (neither earlier study had a context gate), a stop below the sweep low (not close-based), a prior-day-high target, an open-interest flush variant, and day-cluster inference. `v_recovery_low_sweep_2026-11-04` (5-day low + 50% win-back) was BLOCKED before any outcome and is not the same rule.

## Rule (SOURCED = operator order, OURS = chosen here before any outcome)
| Item | Value | Label |
|---|---|---|
| Data | Bybit v5 public `kline` category linear, interval 60 (1h), 20 USDT perps: BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM TRX BCH ETC UNI NEAR FIL XLM AAVE; full history to fetch time (list fixed here, same as sibling studies) | SOURCED (order: 20 coins, Bybit) / list OURS |
| 15m | NOT used: signal and exits are defined on 1h; 15m would only refine intrabar order and the 20-coin 15m download is the stated bottleneck. Same-bar stop/target ties resolve to the STOP (pessimistic) | OURS (order allowed a cut) |
| Open interest | Bybit `open-interest` intervalTime 1h; used only for the flush variant; OI history may start later than klines, flush rows use only events where both OI points exist | SOURCED (order) |
| Levels | PDL = low of the previous completed UTC day; PWL = low of the previous completed UTC week (Mon 00:00Z start). Level is valid for the day / week that follows | SOURCED (order) |
| Sweep | first 1h bar s in the level's period with low <= L x (1 - 0.001) | SOURCED (0.1 %) |
| Reclaim | first later bar r, s < r <= s+6, in the same period, with close > L. Signal = bar r close; entry = OPEN of bar r+1. One event per level per period (the first sweep only; if it does not reclaim within 6 bars the period has no event) | SOURCED (6 bars) / one-event rule OURS |
| Stop | min low over bars s..r, times (1 - 0.001); R = entry - stop. Skip event if R/entry < 0.2 % or > 10 % | stop SOURCED; skip band OURS |
| Targets (one row each) | 1R; 2R; PDH = high of the previous completed UTC day relative to the entry bar (skip the trade in that row if PDH <= entry x 1.001) | SOURCED |
| Time stop | exit at the open of bar entry+24 (24 h) | SOURCED |
| Fills | bar scan from the entry bar: stop if low <= stop (gap below: fill at open), target if high >= target (gap above: fill at open); both in one bar = stop | OURS |
| Costs | round trip = 2 x taker (`fees.py` DERIBIT_TAKER/BINANCE_TAKER = 5 bp each, imported) + `SLIPPAGE_RT_S13` (2 bp) = 12 bp of entry price, taken in R as 0.0012 x entry / R. No funding | SOURCED (order, fees.py) |
| Downtrend filter (point of the study) | at the signal bar close: the coin's last completed daily close < SMA20 of its last 20 completed daily closes AND that SMA20 < the SMA20 one day earlier; OR BTC last 3 completed UTC weeks all red (close < open). All data completed before the signal bar | SOURCED (order) |
| Flush variant | OI at timestamp r (start of reclaim bar) / OI at timestamp s (start of sweep bar) - 1 <= -1 %. Reclaim bar itself excluded, so no look-ahead | SOURCED (1 %) / timing OURS |
| Split | DEV = entry before 2024-01-01; VALIDATION = entry 2024-01-01 onward. All parameters frozen above; DEV is reported descriptively and nothing is tuned on it | SOURCED |

## Rows (24, all pre-registered)
level {PDL, PWL} x target {1R, 2R, PDH} x filter {downtrend, control = no filter} x OI {none, flush}. Per row: trades DEV / VAL, win rate (fee-net R > 0), mean fee-net R VAL.

## Inference and gates (VALIDATION only; per row)
1. Mean R > 0 with 95 % bootstrap CI (2000 resamples, seed 9114) lower bound > 0 on BOTH per-trade and day-cluster (cluster = UTC entry date across coins) views.
2. n VAL >= 100, else UNDERPOWERED.
3. Placebo: for each VAL trade, a random entry in the same coin, same UTC hour of day, VALIDATION period, same holding time (bars the real trade was held), same R width, same cost, and for downtrend rows also drawn only from bars passing the same filter. 2000 draws of the row mean; one-sided p = share of draws with mean >= actual; require p < 0.05.
4. Benjamini-Hochberg 10 % over the 24 placebo p-values.
5. Mean R still > 0 after dropping the 5 best entry days (by summed R).
Verdict PASS only if 1-5 all hold; UNDERPOWERED if n < 100; else FAIL. A PASS on the control rows only (not the downtrend rows) means the filter adds nothing and is reported as such. No row is selected post hoc; best cells are descriptive.

## Not tested
Short side, 15m, maker entries, funding, other levels (session, 5-day), tick-level order of stop vs target.
