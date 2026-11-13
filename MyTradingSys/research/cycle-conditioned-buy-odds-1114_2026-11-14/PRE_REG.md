# PRE_REG: cycle-conditioned buy odds (cycle-conditioned-buy-odds-1114)

Written and committed before any forward return, MAE or analog result was computed (only data fetch + availability checks done).

## Context
Question: how good is buying BTC now (close ~68-71k, ~400 days after the 2025-10-06 ATH 126,199) versus any other day, given cycle position. Descriptive/understanding study; "now" is labelled provisional (2026-11-13 intraday snapshot, last complete day 2026-11-12).
Regime mix of the sample is reported (below). Phase labels use only data known at the time:
- bull: drawdown from running ATH > -20%
- bear (post-peak): drawdown <= -20% and close < 200-day SMA
- base/recovery: drawdown <= -20% and close >= 200-day SMA

## Data
Daily high/low/close: repo btc_cycles_2026-11/btc_daily.csv (blockchain.info -> Binance) to 2026-11-06, Binance data-api tail 2026-11-07..13 (F:\MTS\data_cache\binance_1d). No daily open exists, so returns are close-to-close. MVRV: CoinMetrics community CapMVRVCur (free). Early (2010-2013) bars are thin; the 1400-day SMA starts ~2014-06, so the sample start = first day with all features (~mid-2014). The user's "since 2013" is cut by this warm-up; stated in RESULT.

## Features (computed at each daily close t, no lookahead)
1. days since last halving (2012-11-28, 2016-07-09, 2020-05-11, 2024-04-20)
2. days since running ATH (closing high basis uses daily high)
3. drawdown = close / running-ATH-high - 1
4. red-week streak: consecutive weeks (Mon-Sun UTC) whose close < previous week close; the running week counts if today's close < last completed week close
5. dist200w = close / SMA(1400 daily closes) - 1 (= 200-week SMA)
6. dist50w = close / SMA(350 daily closes) - 1
7. weekly RSI(14, Wilder) on completed weekly closes
8. weekly WaveTrend (LazyBear n1=10, n2=21, hlc3, wt1) on completed weekly bars
9. MVRV (CoinMetrics, value for day t, published same day; secondary: reported in a separate neighbour variant, not in primary)

## Outcomes
Forward return h = close[t+h]/close[t]-1 for h in 30/90/180; MAE_h = min(low[t+1..t+h])/close[t]-1. Only days with full horizon. Round-trip fee 24 bp (12 bp per side) subtracted from returns reported as "net".

## Neighbour rule (PRIMARY, fixed)
- Primary feature vector: features 2,3,4,5,6,7,8 and 1 (eight features, equal weight), each z-scored with the mean/std of all eligible days; days-since-peak and days-since-halving enter as log1p(days).
- Euclidean distance to the query day. Analogs = greedy selection of the 15 nearest days subject to a +/-30-day exclusion around every already-chosen day (so analogs are ~independent episodes), taken from days with full horizon for the horizon in question.
- Variant V2 = primary + MVRV (9 features). Variant V3 = only features 3,5,7 (drawdown, 200w distance, weekly RSI). Variants are reported alongside, no selection of the best.
- Headline = primary rule, horizon 90d. CI = bootstrap over the 15 analogs (10,000 resamples, 2.5/97.5%).

## Bins (fixed, all reported)
B1 dist200w <= +10%; B2 days since ATH in [350,450]; B3a drawdown in [-35%,-20%] (operator wording); B3b drawdown in [-50%,-40%] (today's band); B12 = B1 and B2; B1b = B1 and drawdown <= -40%. Each reported with n days, n independent episodes (30-day greedy), and each split by phase.

## Headline statistic
Percentile rank of today's analog median 90d return among all eligible days' 90d returns; same for analog median 90d MAE. Plus P(90d return > 0) and P(MAE90 < -20%) for analogs vs all days.

## Tests
- Placebo: 10,000 random draws of 15 independent days (same 30d exclusion) from all eligible days; p = share of placebo medians >= analog median (and for MAE).
- DEV <= 2023-12-31, VALIDATION 2024+: walk-forward. For each validation day t, analogs come only from days with date <= t-90 (outcome known) using the primary rule with z-scoring on history to t. Prediction = analog median 90d return. Validation test: realised 90d return of the top-third vs bottom-third predicted days (mean difference, bootstrap CI over 90-day blocks). Power is low (two years of overlapping windows); reported as understanding only, no pass/fail gate.
- Honest limits: ~4 cycles, 15 analogs span at most 3-4 episodes; any CI is optimistic.
