# PRE-REG: Cowen band, daily event study, BTC 2017-08 .. 2024-06 (written 2026-10-31, before any run)

Card: cowen-bmsb-daily-event-study. Registry: ../COWEN_Q4_CONCEPT_CHECK.md section 3 (the desk window of 2022-04..2024-06 gave 3 to 10 trades per idea: NOT ENOUGH DATA).
This study only measures. It adds no rule, gate, layer or trading code. Nothing here is a trade rule.

## Data
Public Binance spot BTCUSDT and ETHUSDT daily klines (data.binance.vision monthly files), months 2017-08 to 2024-06 only, into the gitignored folder `event_study/data/`.
Data after 2024-06-30 is never fetched or loaded (the loader drops and asserts). Daily bars are UTC.

## Band (SOURCED: extract bekghgecip8 W2, W6)
Top and bottom = max and min of the 20-week SMA and the 21-week EMA of weekly closes (Monday to Sunday, UTC). COMPLETED weeks only: the signal on a day uses weeks that ended before that day's week.
EMA seed = SMA of the first 21 weekly closes, alpha 2/22. Same function as `sim_desk/studies/cowen_bmsb.py` `band`. The first band exists after 21 weeks (about January 2018).

## Four ideas (signal on the daily close of day i, shapes as in cowen_bmsb.py `signals`)
- BOUNCE long: previous close above band top, low of day i <= band top, close of day i >= band bottom.
- LOSE short: previous close >= band bottom and close of day i < band bottom (first close below).
- FAKEOUT short: close crosses below the 50-day SMA (previous close >= previous SMA50, close < SMA50) while close > band top.
- CATCHDOWN short (BTC): ETH low <= ETH band top (ETH "at its band") and BTC close > BTC band top x 1.03; first day of that state only.
Parameters are OURS (the 3 % gap, the 50-day, ETH as the "everything else"); nothing is tuned: one setting each, run once, the numbers in RESULT.md are the single run.

## Trade (OURS, NO-SOURCE measurement choices, one setting, not tuned; FORMULAS 18.5 adapted to daily bars)
R = ATR14 of daily bars (mean of the true range of the 14 days ending at the signal day). Entry at the OPEN of day i+1. Stop at 1 R against, target at 2 R in favour, both measured from the entry price.
Hold limit H = 30 daily bars (exit at the close of bar entry+29). Each bar from the entry bar on: if the bar's open is beyond the stop, the exit is the open; else if the stop is touched, the stop price; else if the target is touched, the target price; stop is tested first when a bar holds both.
One open event per idea at a time: a signal is skipped while the previous trade of that idea is still open (its exit bar >= the entry bar). Events whose 30-bar horizon would run past 2024-06-30 are dropped (by horizon, not by outcome).
Fees: from `MyTradingSys/backtest/fees.py` only, all-taker `BINANCE_TAKER` on entry and exit, no slippage constant: `net_R = (side*(exit-entry) - fee*entry - fee*exit) / R`. No cost constant is defined in this folder.

## Statistics (FORMULAS 18.7)
Per idea: n, hit (share of exits at target), stop %, timeout %, wins (net_R > 0), mean gross R, mean net R, per-year split (year of entry). 95 % range of the mean = day-block bootstrap: events grouped by UTC entry date, days resampled with replacement, 2000 resamples, `numpy.random.default_rng(20261009)`, statistic = sum R over resampled days / number of events in them; percentiles 2.5 and 97.5.

## Placebo (FORMULAS 18.6 adapted)
Same idea, same trade rules, but the band top and bottom are both shifted by `d * ATR14(daily)` where `d` cycles through (-3, -2, -1, -0.5, +0.5, +1, +2, +3) by `(week index) mod 8` (the band is refreshed weekly). For CATCHDOWN only BTC's band is shifted, ETH's stays. Difference = real mean net R minus placebo mean net R, 95 % range by the same day-block bootstrap with both streams on the same resampled days.

## Verdict rule (fixed now)
- n < 30 events: NOT ENOUGH DATA (30-event floor). Result still reported with its range.
- n >= 30 and the 95 % range of mean net R is entirely above 0 AND the 95 % range of the placebo difference is entirely above 0: BAND SIGNAL (a lead for a new pre-registration on sealed data, never a rule).
- n >= 30 and the range of mean net R is entirely below 0: NEGATIVE.
- otherwise: NO EDGE SHOWN.
Negative or underpowered results are reported as such. No parameter is changed after seeing results; any variant is a new pre-registration.
