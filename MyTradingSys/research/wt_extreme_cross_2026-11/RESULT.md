# WT extreme cross: bounce / drop size, 1m vs 5m vs 15m (DEV only)

Card wt-1m-extreme-cross-bounce-size-after-cr; EAGLE_EYES_BIBLE lesson 8. Code `study.py`, tests `test_wt_extreme_cross.py`,
cells `dev_cells.csv` (all 135 rows: tf x side x level x day tag x HTF).

**Result: the extreme crosses do mark a bounce, but it is only 0.01-0.04 % (1m) above the bounce you get from ANY bar; fee-net
expectancy at a 10-bar exit is about -0.14 % in every 1m and 5m cell (taker 0.14 % round trip eats it). No tradable edge as a
fixed-exit signal.**

## Context

- Window: DEV 2022-01-01 .. 2024-07-01 (exclusive), BTCUSDT Binance spot 1m, resampled to 5m / 15m. Nothing at or after DEV_END
  is loaded (`splits.assert_dev_only` on every scored bar; loader end = DEV_END). VALIDATION / HOLDOUT not read.
- Regime mix: 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%) (research_kit.regime_tag, as-of weekly).
- Descriptive study (bounce size by context), no survivor rule, no VALIDATION pass.

## Parameters

| name | value | label |
|---|---|---|
| buy event | wt1 crosses above wt2 with wt1 <= -50 | SOURCED card (operator) |
| sell event | wt1 crosses below wt2 with wt1 >= +40 | SOURCED card / bible lesson 8 |
| buy -60 sensitivity | wt1 <= -60 | SOURCED bible lesson 8 ("-60 zone") |
| K (outcome window) | 10 bars after the event bar close | SOURCED operator "within 5-10 bars"; upper end picked = OURS |
| cost | 0.14 % round trip | SOURCED research_kit.TAKER_RT_PCT |
| day type | trend iff abs(close - open) / (high - low) >= 0.6 on the UTC day | SOURCED-in-repo fabio v3 P41 (SIM) |
| HTF | daily close vs its MA (research_kit.regime_tag side): with / against the trade side | SOURCED-in-repo research_kit |
| baseline | same-side 10-bar MFE from every 7th bar close in DEV | OURS |

Day tags: `same_*` = the event's own UTC day (ex-post, what the operator described; NOT tradable). `prior_*` = previous UTC day (as-of).

## Table (all day types, all HTF)

MFE = best move in the trade's favour within 10 bars (%), the "bounce" / "drop". excess = MFE minus baseline MFE, day-clustered t.
net = close-to-close 10-bar return minus 0.14 %.

| tf | side | lvl | n | days | MFE mean / median % | median pts | base MFE % | excess % (t) | net % (t) | net hit |
|---|---|---|---|---|---|---|---|---|---|---|
| 1m | buy | -50 | 15936 | 912 | 0.161 / 0.104 | 32 | 0.148 | +0.013 (3.7) | -0.141 (-58.6) | 0.20 |
| 1m | buy | -60 | 7310 | 910 | 0.187 / 0.122 | 38 | 0.148 | +0.039 (8.2) | -0.140 (-35.6) | 0.22 |
| 1m | sell | +40 | 26580 | 912 | 0.145 / 0.094 | 29 | 0.149 | -0.005 (-1.7) | -0.141 (-79.7) | 0.18 |
| 5m | buy | -50 | 2938 | 832 | 0.387 / 0.248 | 79 | 0.348 | +0.038 (2.8) | -0.134 (-12.6) | 0.36 |
| 5m | buy | -60 | 1400 | 654 | 0.436 / 0.291 | 93 | 0.348 | +0.087 (4.3) | -0.128 (-7.2) | 0.40 |
| 5m | sell | +40 | 5130 | 904 | 0.340 / 0.219 | 69 | 0.352 | -0.012 (-1.6) | -0.140 (-18.2) | 0.33 |
| 15m | buy | -50 | 922 | 499 | 0.688 / 0.459 | 136 | 0.626 | +0.062 (1.9) | -0.128 (-3.8) | 0.46 |
| 15m | buy | -60 | 462 | 307 | 0.797 / 0.520 | 164 | 0.626 | +0.171 (3.3) | -0.089 (-1.7) | 0.49 |
| 15m | sell | +40 | 1636 | 693 | 0.630 / 0.433 | 143 | 0.632 | -0.001 (-0.1) | -0.152 (-6.3) | 0.42 |

## Day type and HTF split (buy -50 / sell +40)

| tf | side | split | n | MFE excess % (t) | net % (t) |
|---|---|---|---|---|---|
| 1m | buy | same_range / same_trend | 12066 / 3870 | +0.008 (2.0) / +0.029 (3.7) | -0.137 / -0.156 |
| 1m | buy | prior_range / prior_trend | 11969 / 3967 | +0.005 (1.2) / +0.038 (4.8) | -0.138 / -0.152 |
| 1m | buy | HTF with / against | 8502 / 7434 | -0.004 (-1.2) / +0.033 (5.4) | -0.133 / -0.152 |
| 1m | sell | same_range / same_trend | 19862 / 6718 | -0.009 (-3.1) / +0.010 (1.9) | -0.137 / -0.153 |
| 1m | sell | HTF with / against | 12626 / 13954 | +0.010 (2.2) / -0.018 (-6.0) | -0.138 / -0.143 |
| 5m | buy | prior_range / prior_trend | 2214 / 724 | +0.008 (0.6) / +0.129 (4.0) | -0.133 / -0.138 |
| 5m | buy | HTF with / against | 1516 / 1422 | -0.024 (-2.3) / +0.105 (4.3) | -0.134 / -0.133 |
| 15m | buy | same_range / same_trend | 634 / 288 | +0.088 (2.0) / +0.004 (0.1) | -0.033 (-0.9) / -0.336 (-5.2) |
| 15m | buy | prior_range / prior_trend | 678 / 244 | +0.001 (0.0) / +0.232 (3.3) | -0.145 / -0.079 (-1.0) |
| 15m | buy | HTF with / against | 445 / 477 | -0.093 (-3.3) / +0.207 (3.7) | -0.136 / -0.120 |
| 15m | sell | same_range / same_trend | 1168 / 468 | +0.026 (1.1) / -0.069 (-2.0) | -0.053 (-2.1) / -0.400 (-8.3) |

The only positive net cell in the 135: 15m buy -60, same_range day (ex-post tag), n 309, net +0.043 % (t 0.7): not significant,
and the tag needs the day's close, so it cannot be traded.

## Reading

1. Bounce size vs the operator's 11-02 picture: the 1m median bounce within 10 bars is 32 pts (-50) / 38 pts (-60), not 100-250.
   The 11-02 session was a high-volatility day; on DEV the typical bounce is a third of that.
2. The bounce is larger AGAINST the HTF trend (buy below the daily MA: +0.033 % excess on 1m, +0.21 % on 15m) and after a trend
   day (prior_trend +0.038 % 1m, +0.23 % 15m). Both are also high-volatility states and the baseline is not volatility-matched,
   so this is likely volatility, not a WT effect (next step below).
3. Sell (+40) never beats the baseline on any TF: the "push top" marks nothing extra.
4. Close-to-close the event is direction-neutral (1m ret mean -0.001 %): what the operator sees is the swing inside a range,
   which a fixed 10-bar exit with taker fees cannot harvest. A maker-in entry (0.09 % rt) does not change the sign either (1m net
   would be about -0.09 %).

Next: a volatility-matched baseline (ATR-decile of the event bar) for the HTF-against / prior-trend cells; if the excess survives,
a target-exit (take the bounce at a fraction of ATR) test with a pre-registration. Until then, no layer change.
