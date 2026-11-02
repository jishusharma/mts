# SOURCED: 11, OURS: 51

# Parameter Labels Audit: eagle_eyes_picture preus_pullback.py and c30_validation.py

Audit of numeric constants, indicator settings, simulation windows, preflight test parameters, and operational defaults across:
1. `MyTradingSys/research/eagle_eyes_picture_2026-10-28/preus_pullback.py`
2. `MyTradingSys/research/eagle_eyes_picture_2026-10-28/c30_validation.py`

Every parameter is verified against cited trader literature / statutory specifications (`SOURCED`) or classified as internal engineering / desk design choices (`OURS`). Facts only, no verdicts on edge.

## Summary

- **Total Scripts Audited**: 2
- **Total Parameters Audited**: 62
- **SOURCED Parameters**: 11
- **OURS Parameters**: 51

---

## 1. preus_pullback.py (`MyTradingSys/research/eagle_eyes_picture_2026-10-28/preus_pullback.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `ts_micro_cutoff` | `preus_pullback.py:8` | `1e14` | `OURS` | Microsecond timestamp detection threshold; internal data ingestion heuristic separating microseconds from milliseconds |
| `ts_ms_div` | `preus_pullback.py:8,9` | `1000` | `OURS` | Timestamp millisecond-to-second divisor (`t // 1000`); internal time normalization |
| `seconds_per_day` | `preus_pullback.py:10,14` | `86400` | `OURS` | Solar day duration in seconds (24 * 3600); calendar engineering constant |
| `bar_step_sec` | `preus_pullback.py:11` | `60` | `OURS` | 1-minute kline sampling step in seconds (`range(a, b, 60)`); engineering cadence for 1m bars |
| `overnight_end_sec` | `preus_pullback.py:14,15,16` | `13 * 3600 (46800s)` | `OURS` | Overnight window end and P0 open price timestamp (13:00 UTC); `preus_pullback.py:1`: "OURS: overnight window 00:00-12:59Z (H,L); P0 = 13:00Z open" |
| `us_end_sec` | `preus_pullback.py:14` | `20 * 3600 (72000s)` | `OURS` | US session window outcome evaluation end timestamp (20:00 UTC); `preus_pullback.py:2`: "Outcomes in US window 13:00-19:59Z... close 20:00Z vs P0"; desk proxy for US equity cash session close |
| `min_overnight_bars` | `preus_pullback.py:15` | `700` | `OURS` | Minimum required 1m bars in 13h overnight window (700 of 780 bars = 89.7% coverage); internal data completeness filter |
| `min_us_bars` | `preus_pullback.py:15` | `380` | `OURS` | Minimum required 1m bars in 7h US window (380 of 420 bars = 90.5% coverage); internal data completeness filter |
| `epoch_base_date` | `preus_pullback.py:18,29` | `dt.date(1970, 1, 1)` | `OURS` | Unix epoch reference date for ordinal calendar conversion; engineering baseline |
| `late_high_sec` | `preus_pullback.py:23` | `3 * 3600 (10800s)` | `OURS` | Overnight high cutoff time (03:00 UTC = 3h after 00:00Z) to qualify as a "late" high; `preus_pullback.py:1`: "Event: H made after 03:00Z" |
| `ret_base_offset` | `preus_pullback.py:23` | `1` | `OURS` | Arithmetic return subtraction offset in R = C / P0 - 1; financial rate-of-return formula |
| `event_giveback_thr` | `preus_pullback.py:25` | `0.5 (50%)` | `OURS` | Minimum giveback ratio (H - P0) / (H - L) >= 0.5 required to trigger event; `preus_pullback.py:1`: "giveback (H-P0)/(H-L) >= 0.5" |
| `pct_multiplier` | `preus_pullback.py:28` | `100` | `OURS` | Percentage conversion scaling multiplier for reporting summary statistics |
| `ret_pos_thr` | `preus_pullback.py:28` | `0` | `OURS` | Directional return sign boundary separating winning and losing sessions (ret > 0) |
| `monday_weekday` | `preus_pullback.py:30` | `0` | `OURS` | Monday weekday index in ISO 8601 / Python `weekday()` specification (Monday = 0); desk filter for Monday setups |
| `severe_giveback_thr` | `preus_pullback.py:31` | `0.8 (80%)` | `OURS` | Deep giveback ratio threshold (H - P0) / (H - L) >= 0.8; `preus_pullback.py:31`, `EAGLE_EYES_BIBLE.md:96` |

---

## 2. c30_validation.py (`MyTradingSys/research/eagle_eyes_picture_2026-10-28/c30_validation.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `MS_PER_SEC` | `c30_validation.py:9,102` | `1000` | `OURS` | Milliseconds per second conversion divisor/multiplier; engineering time scale |
| `WARM` | `c30_validation.py:10` | `MS(2024, 4, 1)` | `OURS` | Indicator warm-up window start date (3 months prior to VALIDATION); `PRE_REG_C30.md:36` ("with warm-up bars taken from before 2024-07-01"), `c30_validation.py:3` |
| `START` | `c30_validation.py:10` | `MS(2024, 7, 1)` | `SOURCED` | Pre-registered VALIDATION split start date; `backtest/splits.py:35` (`VALIDATION_START = DEV_END = 2024-07-01`), `OPERATOR_DECISIONS.md:899`, `PRE_REG_C30.md:35` |
| `END` | `c30_validation.py:10` | `MS(2025, 7, 1)` | `SOURCED` | Pre-registered VALIDATION split exclusive end date / HOLDOUT start boundary; `backtest/splits.py:36-37` (`VALIDATION_END = HOLDOUT_START = 2025-07-01`), `OPERATOR_DECISIONS.md:899`, `PRE_REG_C30.md:35` |
| `MID` | `c30_validation.py:10` | `MS(2025, 1, 1)` | `OURS` | Sub-period midpoint dividing VALIDATION window into two equal 6-month halves; `PRE_REG_C30.md:38` |
| `PAGE_LIMIT` | `c30_validation.py:19` | `1000` | `SOURCED` | Binance Public Spot REST API klines endpoint maximum limit per call; Binance Spot API Documentation (`https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data`: "Default 500; max 1000.") |
| `PAGE_STEP_MS` | `c30_validation.py:19,25` | `1` | `OURS` | Millisecond timestamp pagination adjustment (+1 ms step); internal data fetch pagination logic |
| `HTTP_TIMEOUT` | `c30_validation.py:20` | `30` | `OURS` | HTTP socket request timeout in seconds; network engineering parameter |
| `STUB_OHLC` | `c30_validation.py:33` | `1.0` | `OURS` | Synthetic 1-bar price stub placeholder to satisfy module import cache checks; test fixture parameter |
| `BAR_15M_MS` | `c30_validation.py:40,73` | `900000` | `OURS` | 15-minute timeframe bar duration in milliseconds (15 * 60 * 1000 ms); desk resolution choice for H2 |
| `AGG_15M_RATIO` | `c30_validation.py:41,46,67` | `3` | `OURS` | 5m-to-15m candle aggregation factor (15 / 5 = 3 bars); candle aggregation ratio |
| `AGG_30M_RATIO` | `c30_validation.py:46,67` | `6` | `OURS` | 5m-to-30m candle aggregation factor (30 / 5 = 6 bars); candle aggregation ratio |
| `WT_OS_THR` | `c30_validation.py:47` | `-53` | `SOURCED` | LazyBear WaveTrend oversold boundary wt1 <= -53; `FORMULAS.md` s20.2 ("os1 <= -53"), `PRE_REG_C30.md:25` ("SOURCED band, OURS level choice") |
| `TF_H1_MIN` | `c30_validation.py:48,70,90` | `30` | `OURS` | Timeframe resolution in minutes for H1 hypothesis; desk choice selected on DEV (`PRE_REG_C30.md:15`) |
| `TF_H2_MIN` | `c30_validation.py:48,70,90` | `15` | `OURS` | Timeframe resolution in minutes for H2 hypothesis; desk choice selected on DEV (`PRE_REG_C30.md:16`) |
| `EXIT_RULE_IDX` | `c30_validation.py:49,94` | `0` | `OURS` | Exit rule index 0 selecting Exit X1 (centre cross wt1 > 0); `PRE_REG_C30.md:15,30` ("Exit X1 centre cross: first bar k > i with wt1[k] > 0, filled at open of k+1; cap 60 bars") |
| `MIN_SAMPLE_STAT` | `c30_validation.py:54,115` | `2` | `OURS` | Minimum sample size required for sample standard deviation degrees of freedom (df = n - 1 >= 1); statistical implementation floor |
| `SE_SQRT_POW` | `c30_validation.py:57` | `0.5` | `OURS` | Square root exponent (n^0.5) for standard error of sample mean SE = SD / sqrt(n); numerical implementation parameter |
| `HILL_DIV_4` | `c30_validation.py:59` | `4` | `SOURCED` | Cornish-Fisher expansion first-order correction divisor (4 * df); G. W. Hill (1970), "Algorithm 395: Student's t-distribution", CACM 13(10):617-619 |
| `HILL_DIV_2` | `c30_validation.py:59` | `2` | `SOURCED` | Cornish-Fisher expansion second-order correction divisor (2 * df); G. W. Hill (1970), "Algorithm 395: Student's t-distribution", CACM 13(10):617-619 |
| `ERFC_SCALE` | `c30_validation.py:59` | `0.5` | `OURS` | Scale factor converting complementary error function to standard normal tail probability P(Z > z) = 0.5 * erfc(z / sqrt(2)); numerical implementation factor |
| `ERFC_SQRT2` | `c30_validation.py:59` | `2` | `OURS` | Square root argument sqrt(2) scaling complementary error function; numerical implementation constant |
| `CI_Z_95` | `c30_validation.py:61` | `1.96` | `SOURCED` | Two-sided 95% standard normal critical value z_0.025 = 1.95996; `PRE_REG_C30.md:38` ("95 % CI (normal, mean +/- 1.96 SE)") |
| `STAT_PCT_SCALE` | `c30_validation.py:61,82` | `100` | `OURS` | Percentage conversion multiplier (100%); numerical display factor |
| `BAR_5M_MS` | `c30_validation.py:68` | `300000` | `OURS` | 5-minute bar duration in milliseconds (5 * 60 * 1000 ms); base bar sampling duration |
| `SPAN_FENCEPOST` | `c30_validation.py:68` | `1` | `OURS` | Fencepost adjustment (+1) for discrete interval bar count; numerical counting offset |
| `P1_COVERAGE_MIN` | `c30_validation.py:69` | `0.995 (99.5%)` | `OURS` | Preflight P1 bar coverage completeness gate; `bt_preflight.py:31`, `C30_VALIDATION.md:4` |
| `P2B_SEED` | `c30_validation.py:71` | `5` | `OURS` | Deterministic pseudo-random seed for P2b prefix cut point selection; `bt_preflight.py:50`, `c30_validation.py:71` |
| `P2B_CUTS` | `c30_validation.py:71` | `15` | `OURS` | Number of random prefix cut points evaluated in P2b preflight test; `bt_preflight.py:46` |
| `P2B_WARMUP_SKIP` | `c30_validation.py:72` | `2000` | `OURS` | Warmup bars skipped before sampling prefix test cut points; indicator stabilization buffer |
| `BAR_1M_MS` | `c30_validation.py:73` | `60000` | `OURS` | 1-minute bar duration in milliseconds (60 * 1000 ms); time unit conversion factor |
| `TOL_PREFIX_RSI` | `c30_validation.py:75` | `1e-9` | `OURS` | Floating-point parity tolerance for prefix RSI equivalence; `FORMULAS.md` s20.4 |
| `BULL_DIV_SIDE` | `c30_validation.py:75,94` | `1` | `OURS` | Directional side indicator for bullish divergence / long trades (+1); `wt_rsi_div.py:31` |
| `FEE_ROUNDTRIP` | `c30_validation.py:82` | `WD.FEE (0.10%)` | `SOURCED` | Binance VIP0 spot taker fee schedule: 0.05% per leg, 2 x 0.05% = 0.10% round trip; `fees.py:36`, `PRE_REG_C30.md:32`, `wt_rsi_div.py:15` |
| `TOL_FEE_IDENTITY` | `c30_validation.py:83` | `1e-6` | `OURS` | Numerical precision tolerance for P6 fee identity verification; `bt_preflight.py:10` |
| `P7_MAX_OVERLAP` | `c30_validation.py:85` | `0` | `OURS` | Maximum allowed concurrent overlapping trades for P7 preflight check; `PRE_REG_C30.md:31` ("One trade at a time: a new signal is ignored while a trade is open") |
| `P8_DRAWS` | `c30_validation.py:89` | `30` | `OURS` | Number of random entry draws for P8 baseline significance test; `PRE_REG_C30.md:37`, `C30_VALIDATION.md:12` |
| `TREND_ANY_NEED` | `c30_validation.py:90` | `0` | `OURS` | Unrestricted trend condition flag for H1 hypothesis (0 = any trend); `PRE_REG_C30.md:15` |
| `P8_WARMUP_SKIP` | `c30_validation.py:91` | `100` | `OURS` | Warmup bars skipped before sampling random entry candidates in P8 test |
| `P8_SEED` | `c30_validation.py:92` | `11` | `OURS` | Deterministic pseudo-random seed for P8 Monte Carlo draws; `c30_validation.py:92` |
| `P8_MIN_SAMPLE` | `c30_validation.py:103` | `5` | `OURS` | Minimum trade sample count required to execute P8 random entry baseline test; `bt_preflight.py:7` |
| `HOLM_FAMILY_M` | `c30_validation.py:112` | `2` | `SOURCED` | Multiple hypothesis testing family size (m = 2 for H1 and H2); Sture Holm (1979), Scandinavian Journal of Statistics, 6(2):65-70; `PRE_REG_C30.md:39` ("Holm-adjusted (m = 2)") |
| `PROB_CAP` | `c30_validation.py:112` | `1.0` | `SOURCED` | Probability axiom upper bound P(E) <= 1.0 for Holm p-value adjustment |
| `VERDICT_FAIL_MEAN` | `c30_validation.py:115` | `0` | `OURS` | Fee-net return threshold for automatic FAIL verdict (mean <= 0); `PRE_REG_C30.md:40` ("FAIL: mean <= 0") |
| `VERDICT_PASS_N` | `c30_validation.py:115` | `15` | `OURS` | Minimum sample size required for PASS verdict gate (n >= 15); `PRE_REG_C30.md:39` ("PASS (per hypothesis): n >= 15") |
| `VERDICT_PASS_ALPHA` | `c30_validation.py:115` | `0.05` | `SOURCED` | Statistical significance threshold (alpha = 0.05) after Holm adjustment; Neyman-Pearson hypothesis testing standard; `PRE_REG_C30.md:39` ("Holm-adjusted (m = 2) one-sided p < 0.05") |
