# SOURCED: 21, OURS: 47

# Parameter Labels Audit: reclaim.py, ladder_math.py, us_window_stats.py, analyze.py, features.py

Audit of numeric constants, configuration defaults, and operational parameters across:
1. `MyTradingSys/research/reclaim_close_stop_2026-11/reclaim.py`
2. `MyTradingSys/research/testnet_cotrade_2026-10-31/ladder_math.py`
3. `MyTradingSys/research/testnet_cotrade_2026-10-31/us_window_stats.py`
4. `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/features.py`
5. `MyTradingSys/research/meta_label_tom_fabio_2026-10-31/analyze.py`

Every parameter is verified against trader citations or classified as internal engineering defaults (`OURS`). Facts only, no verdicts on edge.

## Summary

- **Total Scripts Audited**: 5
- **Total Parameters Audited**: 68
- **SOURCED Parameters**: 21
- **OURS Parameters**: 47

---

## 1. reclaim.py (`MyTradingSys/research/reclaim_close_stop_2026-11/reclaim.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `CAP['4h']` | `reclaim.py:19` | `6` | `OURS` | Trade horizon cap in 4h bars (`reclaim.py:19`: "OURS horizon cap in bars after the reclaim bar"; `PRE_REG.md:13`) |
| `CAP['1D']` | `reclaim.py:19` | `5` | `OURS` | Trade horizon cap in daily bars (`reclaim.py:19`: "OURS horizon cap in bars after the reclaim bar"; `PRE_REG.md:13`) |
| `CFG['4h'][0]` | `reclaim.py:20` | `240` | `OURS` | 4-hour timeframe resolution in minutes; engineering selection (`PRE_REG.md:8`, `study.py:20`) |
| `CFG['4h'][1]` | `reclaim.py:20` | `3` | `OURS` | Fractal swing lookback half-width L=3 bars; engineering choice (`PRE_REG.md:9`, `study.py:20`) |
| `CFG['4h'][2]` | `reclaim.py:20` | `6` | `OURS` | Reclaim scan window N=6 bars after break; engineering choice (`PRE_REG.md:11`, `study.py:20`) |
| `CFG['1D'][0]` | `reclaim.py:20` | `1440` | `OURS` | 1-day timeframe resolution in minutes; engineering selection (`PRE_REG.md:8`, `study.py:20`) |
| `CFG['1D'][1]` | `reclaim.py:20` | `3` | `OURS` | Fractal swing lookback half-width L=3 bars; engineering choice (`PRE_REG.md:9`, `study.py:20`) |
| `CFG['1D'][2]` | `reclaim.py:20` | `3` | `OURS` | Reclaim scan window N=3 bars after break; engineering choice (`PRE_REG.md:11`, `study.py:20`) |
| `atr_period` | `reclaim.py:49` | `14` | `SOURCED` | J. Welles Wilder Jr. (1978) standard 14-period True Range rolling window; `FORMULAS.md` s12, `PRE_REG.md:10` ("ATR14(SMA)") |
| `side_symmetry` | `reclaim.py:51` | `(-1, 1)` | `OURS` | Symmetric long/short directional evaluation (-1 low break, +1 high break); `PRE_REG.md:12` ("both sides pooled, symmetric") |
| `warmup_skip` | `reclaim.py:55` | `30` | `OURS` | Initial bars skipped for indicator and swing stability; engineering buffer |
| `break_buf` | `reclaim.py:63` | `0.1` | `OURS` | Minimum ATR penetration threshold for genuine break vs wick sweep (0.1 x ATR14); `PRE_REG.md:10` |
| `fee_net` | `reclaim.py:70` | `2 * BINANCE_TAKER (0.001)` | `SOURCED` | Binance VIP0 USDT-M default taker fee (0.05% x 2 = 0.10% round trip); `backtest/fees.py:36`, `PRE_REG.md:15` |

---

## 2. ladder_math.py (`MyTradingSys/research/testnet_cotrade_2026-10-31/ladder_math.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `X` | `ladder_math.py:6` | `100` | `SOURCED` | Operator-specified base order unit in USD; `DESIGN.md:3-4` ("short 100 here / buy here with a double"), `ladder_math.py:1-2` |
| `P0` | `ladder_math.py:6` | `100000.0` | `OURS` | Benchmark starting price level (100k USD) for scale illustration; `DESIGN.md:24` |
| `SPACING` | `ladder_math.py:6` | `0.004 (0.4%)` | `OURS` | Geometric grid rung distance between limit orders; `DESIGN.md:24` ("one rung every +0.4%") |
| `STOP_GAP` | `ladder_math.py:6` | `0.004 (0.4%)` | `OURS` | Protective stop distance beyond final rung; `DESIGN.md:24` ("one stop 0.4% above the last rung") |
| `k_rungs` | `ladder_math.py:8` | `7` | `SOURCED` | Doubling progression sequence steps generating multipliers [1, 2, 3, 6, 12, 24, 48]; `DESIGN.md:4` ("doubles the total (X, 2X, 3X, 6X ...)") |
| `n_steps_range` | `ladder_math.py:12` | `range(1, 8)` | `OURS` | Cumulative fill step evaluation range (1 to 7 rungs filled); `DESIGN.md:26-31` |
| `margin_10x` | `ladder_math.py:22` | `10` | `OURS` | Account initial margin leverage divisor 10x; `DESIGN.md:27` |
| `margin_20x` | `ladder_math.py:22` | `20` | `OURS` | Account initial margin leverage divisor 20x; `DESIGN.md:27` |

---

## 3. us_window_stats.py (`MyTradingSys/research/testnet_cotrade_2026-10-31/us_window_stats.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `us_open_hour` | `us_window_stats.py:55` | `9` | `SOURCED` | Regular US equity cash market session open hour 09:30 America/New_York; NYSE/NASDAQ trading hours, `us_window_stats.py:4`, `DESIGN.md:52` |
| `us_open_min` | `us_window_stats.py:55` | `30` | `SOURCED` | Regular US equity cash market session open minute 09:30 America/New_York; NYSE/NASDAQ trading hours, `us_window_stats.py:4`, `DESIGN.md:52` |
| `pre60_bars` | `us_window_stats.py:57` | `60` | `SOURCED` | Pre-open observation window (60 minutes = 08:30 ET economic release to 09:30 ET cash open); `us_window_stats.py:5`, `DESIGN.md:50,53` |
| `us4h_bars` | `us_window_stats.py:57` | `240` | `OURS` | Post-open tracking window (240 1m bars = 4 hours); `us_window_stats.py:6`, `DESIGN.md:57` |
| `first30_bars` | `us_window_stats.py:69` | `30` | `SOURCED` | Initial balance / opening range window (first 30 minutes of regular cash session); `us_window_stats.py:6`, `DESIGN.md:59`, Fabio IB definition `extracts/v2/fabio/LQvv5xgy_ik_v2.md:312` |
| `dst_offset_sec` | `us_window_stats.py:68` | `-4 * 3600 (-14400s)` | `SOURCED` | US Eastern Daylight Time UTC offset (-4 hours EDT = 13:30Z open); 15 U.S. Code s 260a, `DESIGN.md:52` |
| `two_sided_thresh` | `us_window_stats.py:71` | `0.5 (0.5%)` | `OURS` | Symmetrical excursion threshold for two-sided "both ways" session (+0.5% high and -0.5% low from open); `us_window_stats.py:9`, `DESIGN.md:58` |
| `us4h_quantiles` | `us_window_stats.py:79` | `(.25, .5, .75, .9)` | `OURS` | Quantile probability grid (p25, p50, p75, p90) for distribution statistics; `DESIGN.md:57` |
| `up_dn_quantiles` | `us_window_stats.py:80,81` | `(.5, .9)` | `OURS` | Directional excursion quantiles (median and 90th percentile); `DESIGN.md:58` |
| `one_way_thresh` | `us_window_stats.py:86` | `2.0 (2%)` | `OURS` | Large directional run threshold (at least 2.0% one-way move from open); `DESIGN.md:35,86` |

---

## 4. features.py (`MyTradingSys/research/meta_label_tom_fabio_2026-10-31/features.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `H1` | `features.py:25` | `60 * 60000 (3,600,000 ms)` | `OURS` | Higher timeframe 1-hour bar duration in milliseconds; `PRE_REG.md:18` ("Bar timeframes (OURS): 1h for BBWP, RSI, WaveTrend, relative volume") |
| `D1` | `features.py:25` | `24 * 60 * 60000 (86,400,000 ms)` | `SOURCED` | Higher timeframe daily bar duration in milliseconds (1 standard calendar day = 24 hours UTC); `PRE_REG.md:18`, `backtest/splits.py` |
| `FUND_FIRST` | `features.py:27` | `'2022-01'` | `SOURCED` | DEV window start month for funding rate series; `backtest/splits.py:4` (`DEV_START = 2022-01-01`), `PRE_REG.md:18` |
| `FUND_LAST` | `features.py:27` | `'2024-06'` | `SOURCED` | DEV window end month for funding rate series; `backtest/splits.py:6` (`DEV_END = 2024-07-01`), `PRE_REG.md:18` |
| `WT_ZONE['os2']` | `features.py:28` | `-2` | `SOURCED` | Extreme oversold zone score wt1 <= -60; `FORMULAS.md` s20.2, LazyBear WaveTrend bands |
| `WT_ZONE['os1']` | `features.py:28` | `-1` | `SOURCED` | Moderate oversold zone score wt1 <= -53; `FORMULAS.md` s20.2, LazyBear WaveTrend bands |
| `WT_ZONE['mid']` | `features.py:28` | `0` | `SOURCED` | Neutral WaveTrend zone score -53 < wt1 < 53; `FORMULAS.md` s20.2 |
| `WT_ZONE['ob1']` | `features.py:28` | `1` | `SOURCED` | Moderate overbought zone score wt1 >= 53; `FORMULAS.md` s20.2, LazyBear WaveTrend bands |
| `WT_ZONE['ob2']` | `features.py:28` | `2` | `SOURCED` | Extreme overbought zone score wt1 >= 60; `FORMULAS.md` s20.2, LazyBear WaveTrend bands |
| `bbwp_basis` | `features.py:71` | `7` | `SOURCED` | S8 BBWP basis length 7 SMA; Eric Krown `research/krown_ta101_2026-10-13/KROWN_RULES.csv` KR-Q01: "basis length 7", `FORMULAS.md` s21.5 |
| `bbwp_lookback` | `features.py:71` | `100` | `SOURCED` | S8 BBWP percentile lookback window 100 bars; Eric Krown `KROWN_RULES.csv` KR-Q01: "lookback 100", `FORMULAS.md` s21.5 |
| `rsi_period` | `features.py:72` | `14` | `SOURCED` | J. Welles Wilder Jr. (1978) standard 14-period RSI; `FORMULAS.md` s1, `PRE_REG.md:18` ("rsi_core (Wilder 14)") |
| `relvol_lookback` | `features.py:75` | `24` | `OURS` | Rolling lookback window for baseline volume (24 1h bars = 24 hours); `PRE_REG.md:29` ("mean volume of the 24 closed 1h bars before it") |
| `cowen_top_side` | `features.py:97` | `1.0` | `OURS` | Discrete directional flag when daily close exceeds Cowen 20w SMA / 21w EMA band top; `PRE_REG.md:24`, `FORMULAS.md` s26 |
| `cowen_bot_side` | `features.py:97` | `-1.0` | `OURS` | Discrete directional flag when daily close falls below Cowen 20w SMA / 21w EMA band bottom; `PRE_REG.md:24`, `FORMULAS.md` s26 |
| `eu_hour_start` | `features.py:112` | `7` | `SOURCED` | European regular financial session start hour (07:00 UTC); `PRE_REG.md:26` ("EU 07-13"), `extracts/v2/tom/Of_wlv3xaZo_v2.md:14` |
| `eu_hour_end` | `features.py:112` | `13` | `SOURCED` | European regular financial session transition hour (13:00 UTC); `PRE_REG.md:26` ("EU 07-13") |
| `us_hour_start` | `features.py:113` | `13` | `SOURCED` | US regular cash market open alignment window start (13:00 UTC / 13:30Z); `PRE_REG.md:26` ("US 13-21"), `extracts/v2/tom/Of_wlv3xaZo_v2.md:14` |
| `us_hour_end` | `features.py:113` | `21` | `SOURCED` | US regular cash market close alignment window end (21:00 UTC); `PRE_REG.md:26` ("US 13-21") |
| `rsi_ob_level` | `features.py:114` | `60` | `SOURCED` | Malkan bull regime upper RSI threshold (RSI >= 60 = +1); `PRE_REG.md:27` ("40/60 = the Malkan layer bands"), `malkan_40_60.py:64` |
| `rsi_os_level` | `features.py:114` | `40` | `SOURCED` | Malkan bear regime lower RSI threshold (RSI <= 40 = -1); `PRE_REG.md:27` ("40/60 = the Malkan layer bands"), `malkan_40_60.py:107` |
| `bbwp_scale` | `features.py:115` | `100.0` | `OURS` | BBWP normalization scale factor mapping percentile [0, 100] to unit interval [0, 1]; `PRE_REG.md:22` ("bbwp/100") |

---

## 5. analyze.py (`MyTradingSys/research/meta_label_tom_fabio_2026-10-31/analyze.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `SEED` | `analyze.py:18` | `20261031` | `OURS` | Fixed PRNG seed for bootstrap resampling and label shuffling reproducibility; `PRE_REG.md:39,40` |
| `K_FOLDS` | `analyze.py:18` | `6` | `OURS` | Number of contiguous cross-validation blocks partitioned by week; `PRE_REG.md:37` ("DEV trades are cut into K = 6 contiguous blocks") |
| `LAM` | `analyze.py:18` | `1.0` | `OURS` | Ridge L2 regularization penalty multiplier lambda = 1.0 applied to standardized features; `PRE_REG.md:36` ("L2 ridge lambda = 1.0") |
| `B_BOOT` | `analyze.py:18` | `2000` | `OURS` | Bootstrap resample iterations for confidence interval estimation; `PRE_REG.md:39` ("2000 draws, seed 20261031") |
| `MIN_TOP` | `analyze.py:18` | `100` | `OURS` | Minimum sample size threshold in top tercile required for statistical conclusiveness; `PRE_REG.md:44` ("fewer than 100 trades in the top tercile") |
| `N_FEATURES` | `analyze.py:20` | `8` | `OURS` | Total distinct layer features evaluated for Bonferroni multiple testing adjustment; `PRE_REG.md:18,59` |
| `DAY` | `analyze.py:21` | `86400000` | `OURS` | Standard calendar day duration in milliseconds (24 x 3,600,000 ms); engineering time constant |
| `iters` | `analyze.py:25` | `50` | `OURS` | Maximum IRLS (Newton-Raphson) logistic regression solver iterations; `PRE_REG.md:36` ("IRLS (Newton), 50 iterations max") |
| `logit_clip` | `analyze.py:31` | `(-30, 30)` | `OURS` | Logistic link argument clipping bounds preventing floating-point overflow; numerical engineering parameter |
| `weight_floor` | `analyze.py:32` | `1e-6` | `OURS` | Variance weight floor p(1-p) preventing numerical singularity; numerical engineering parameter |
| `ridge_diag_eps` | `analyze.py:34` | `1e-9` | `OURS` | Hessian diagonal damping term ensuring strict positive definiteness; numerical engineering parameter |
| `irls_tol` | `analyze.py:37` | `1e-8` | `OURS` | Newton step convergence tolerance (|delta_beta|_inf < 1e-8); numerical engineering parameter |
| `embargo_purge_w` | `analyze.py:49,81` | `1` | `OURS` | Embargo and purge buffer window around test block (1 week before and after); `PRE_REG.md:37` ("within 1 week ... purged") |
| `tercile_cuts` | `analyze.py:63` | `[33.333, 66.667]` | `OURS` | Equal tercile partition percentiles (100/3 and 200/3); `PRE_REG.md:38` ("equal-size thirds by score rank") |
| `ci_alpha_grid` | `analyze.py:127,134` | `(2.5, 97.5)` | `OURS` | Standard two-sided 95% bootstrap confidence interval percentile bounds; `PRE_REG.md:39` ("95 % CI") |
| `power_factor` | `analyze.py:148` | `7.849` | `OURS` | Independent two-sided two-sample normal power constant (z_0.975 + z_0.80)^2 = (1.96 + 0.8416)^2 = 7.849; `PRE_REG.md:47` |
| `bbwp_low_thr` | `analyze.py:166` | `30` | `OURS` | Single-feature split compression cutoff for BBWP; `PRE_REG.md:59` ("compression <= 30"), `FORMULAS.md` s21.5 |
| `bbwp_high_thr` | `analyze.py:166` | `85` | `SOURCED` | Single-feature split expansion cutoff for BBWP; Eric Krown `KROWN_RULES.csv` KR-Q02: "85 or above", `FORMULAS.md` s21.5 |
| `d1_trend_thr` | `analyze.py:167` | `0` | `SOURCED` | Paul Tudor Jones 200 SMA / 50 SMA trend sign indicator threshold (close - SMA50 > 0); `PRE_REG.md:23`, `FORMULAS.md` s16 |
| `rsi_low_thr` | `analyze.py:171` | `40` | `SOURCED` | Malkan bear regime lower RSI threshold; `PRE_REG.md:27,59` ("RSI < 40"), `malkan_40_60.py:107` |
| `rsi_high_thr` | `analyze.py:171` | `60` | `SOURCED` | Malkan bull regime upper RSI threshold; `PRE_REG.md:27,59` ("RSI > 60"), `malkan_40_60.py:64` |
| `wt_os_thr` | `analyze.py:172` | `-1` | `SOURCED` | LazyBear WaveTrend oversold regime condition (wt <= -1 corresponds to wt1 <= -53); `PRE_REG.md:28,59`, `FORMULAS.md` s20.2 |
| `wt_ob_thr` | `analyze.py:172` | `1` | `SOURCED` | LazyBear WaveTrend overbought regime condition (wt >= 1 corresponds to wt1 >= 53); `PRE_REG.md:28,59`, `FORMULAS.md` s20.2 |
| `min_split_sample` | `analyze.py:191,255` | `30` | `OURS` | Minimum sample size required to compute descriptive split bootstrap CI; small sample heuristic |
| `placebo_n` | `analyze.py:214,350` | `300` | `OURS` | Number of label permutations for placebo significance test; `PRE_REG.md:40` ("300 shuffles (seed 20261031)") |
| `placebo_pct` | `analyze.py:219` | `95` | `OURS` | 95th percentile threshold on placebo spread distribution; `PRE_REG.md:40` ("exceed the placebo 95th percentile") |
| `ci975_grid` | `analyze.py:222` | `(1.25, 98.75)` | `OURS` | Two-sided 97.5% bootstrap confidence interval bounds for secondary robustness; `analyze.py:222` |
| `delta_lift_target` | `analyze.py:229` | `0.30` | `OURS` | Minimum meaningful effect size target (0.30 R lift) for post-hoc sample adequacy calculation; `analyze.py:229` |
| `split_date_2023` | `analyze.py:236` | `19358` | `OURS` | Ordinal day index for 2023-01-01 partitioning sub-period stability (2022 vs 2023-2024); engineering calendar split |
| `bonferroni_grid` | `analyze.py:260` | `(0.3125, 99.6875)` | `OURS` | Bonferroni multiple testing adjustment for 8 single-feature tests (1 - 0.05/8 = 99.375%, two-sided tails 0.3125% and 99.6875%); `PRE_REG.md:59` |
| `tom_vp_accept_n` | `analyze.py:358` | `6` | `OURS` | Tom VP setup choice: acceptance threshold 6 5m closes outside value area; `PRE_REG.md:11` ("accept_n 6"), `tom_vp.py:36` |
| `tom_vp_stop_atr` | `analyze.py:358` | `1.0` | `OURS` | Tom VP setup choice: structural stop distance 1.0 x ATR14 (1h); `PRE_REG.md:11` ("stop 1 ATR"), `tom_vp.py:36` |
| `fabio_c_m` | `analyze.py:359` | `15` | `OURS` | Fabio Model C setup choice: push window m=15 1m candles; `PRE_REG.md:12` ("m 15"), `fabio_v3.py:48` |
| `fabio_c_f_pct` | `analyze.py:359` | `0.5` | `OURS` | Fabio Model C setup choice: stop floor f=0.5% of entry; `PRE_REG.md:12` ("f 0.5%"), `fabio_v3.py:48` |
