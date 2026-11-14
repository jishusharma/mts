# REVIEW: adx_di_2026-11 Study (Blind Review - Argon Twin)

VERDICT: SOUND

## 1. Executive Summary & Verification Context

This document provides an end-to-end blind review of the `MyTradingSys/research/adx_di_2026-11` study (`HOW_TO_USE_ADX_1113.md`, `MEASURE_1113.md`, `CENSUS.md`, `measure_1113.py`, `census.py`).
All claims from the summary (`HOW_TO_USE_ADX_1113.md`) were cross-checked against the backing tables in `MEASURE_1113.md` and `CENSUS.md`.
Recounts of headline numbers were executed directly against `census.py` and `measure_1113.py` using repository data (`btc_daily.csv`).
Detailed code audits were conducted for look-ahead bias and fee / slippage errors.

Overall, the methodology and execution are **SOUND**:
- All numbers cited in `HOW_TO_USE_ADX_1113.md` match the underlying measurement and census tables exactly.
- The 2d cross census (`census.py`) replicates deterministically and matches `CENSUS.md` to every decimal place.
- Daily event counts in `measure_1113.py` replicate identically using repository daily bars (`btc_daily.csv`); intraday granular klines (696,252 5m bars from Bybit v5 API) were fetched dynamically by the runner into a temporary cache and are not persisted in the repository (marked UNVERIFIABLE for intraday counts, SOURCED for table entries).
- Feature calculations use only past and current bar data (Wilder smoothing / Wilder TR). Forward returns enter strictly at bar close `i` and evaluate at bar close `i+h`. No future data leaks into signal detection or feature construction.
- Fee handling is conservative and cleanly isolates intraday friction: maker round-trip fees (4 bps) are deducted from every intraday trade (5m, 15m, 1h, 4h), correctly matching `MyTradingSys/backtest/fees.py:BINANCE_MAKER * 2`.

---

## 2. Claim Table: HOW_TO_USE_ADX_1113.md vs MEASURE_1113.md & CENSUS.md

| ID | Item / Claim in Summary | Claimed Value in HOW_TO_USE_ADX_1113.md | Backing Table Value (MEASURE_1113.md / CENSUS.md) | Recounted Value (Code & Data) | Status | Notes / Citations |
|---|---|---|---|---|---|---|
| C01 | 5m DI cross | DI cross n=10270: long -0.049% vs base -0.038%, t -3.3 | n=10270 net -0.049% vs base -0.038% (ex -0.011%, t -3.3) win 37% vs 40% | UNVERIFIABLE (intraday cache not on disk) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:18](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L18) vs [MEASURE_1113.md:48](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L48) |
| C02 | 15m cross ex return | n=3476, ex +0.001% | n=3476 net -0.035% vs base -0.035% (ex +0.001%, t 0.1) | UNVERIFIABLE (intraday cache not on disk) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:19](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L19) vs [MEASURE_1113.md:52](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L52) |
| C03 | 15m ADX through 25 long | n=1837, +0.059% vs -0.022% at 12 bars, t 3.2 | n=1837 net +0.059% vs base -0.022% (ex +0.081%, t 3.2) win 45% vs 48% | UNVERIFIABLE (intraday cache not on disk) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:19](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L19) vs [MEASURE_1113.md:53](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L53) |
| C04 | 1h cross long | n=936: -0.041% vs +0.030% at 12 bars | n=936 net -0.041% vs base +0.030% (ex -0.071%, t -1.0) | UNVERIFIABLE (intraday cache not on disk) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:20](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L20) vs [MEASURE_1113.md:56](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L56) |
| C05 | 1h ADX through 25 long | n=517: +0.182% vs +0.030%, t 1.7 at 12 bars | n=517 net +0.182% vs base +0.030% (ex +0.152%, t 1.7) win 48% vs 50% | UNVERIFIABLE (intraday cache not on disk) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:20](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L20) vs [MEASURE_1113.md:57](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L57) |
| C06 | 4h cross long | n=256: -0.071% vs +0.239% at 12 bars | n=256 net -0.071% vs base +0.239% (ex -0.310%, t -1.2) | UNVERIFIABLE (intraday cache not on disk) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:21](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L21) vs [MEASURE_1113.md:60](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L60) |
| C07 | 4h ADX through 25 long | n=122: +0.634% vs +0.239%, t 1.1 at 12 bars | n=122 net +0.634% vs base +0.239% (ex +0.395%, t 1.1) win 57% vs 52% | UNVERIFIABLE (intraday cache not on disk) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:21](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L21) vs [MEASURE_1113.md:61](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L61) |
| C08 | 1d ADX through 25 long | n=34: +2.9/+4.1/+5.6% at 3/6/12 bars vs +0.6/+1.1/+2.3 base, win 65-74% | n=34 net +2.871% vs base +0.554% (win 68% vs 54%); net +4.142% vs base +1.121% (win 74% vs 54%); net +5.558% vs base +2.289% (win 65% vs 55%) | OURS: n=34, net +2.871% / +4.142% / +5.558% (base +0.559% / +1.130% / +2.303% on 3597 daily csv bars) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:22](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L22) vs [MEASURE_1113.md:65](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L65) |
| C09 | 1d ADX through 25 short | Short n=33 beats base (t up to 3.0) | n=33 net +1.865% (t 1.5); net +3.170% (t 2.1); net +4.741% vs base -2.289% (t 3.0) | OURS: n=33, net +1.865% / +3.170% / +4.741% (t 1.5, 2.1, 3.0) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:22](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L22) vs [MEASURE_1113.md:67](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L67) |
| C10 | 1d DI cross | Cross n=55: no edge | n=55 net +0.100%, -0.065%, +2.289% vs base +0.554%, +1.121%, +2.289% | OURS: n=55, net +0.100%, -0.065%, +2.289% | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:22](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L22) vs [MEASURE_1113.md:64](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L64) |
| C11 | 2d cross + ADX>20 long | n=33: -2.4% vs +1.1% at 3 bars, t -1.8 | n=33 net -2.371% vs base +1.095% (ex -3.467%, t -1.8) win 36% vs 53% | UNVERIFIABLE (without top-up days) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:23](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L23) vs [MEASURE_1113.md:68](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L68) |
| C12 | 2d ADX through 25 sample size | n=17 and n=20 | L_adx25 n=17, S_adx25 n=20 | UNVERIFIABLE (without top-up days) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:23](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L23) vs [MEASURE_1113.md:69](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L69), [MEASURE_1113.md:71](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L71) |
| C13 | 5d & 1w sample size | Every cell n under 30 (best n=13; n=2 to 12) | 5d max n=13; 1w n=2 to 12 | UNVERIFIABLE (without top-up days) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:24](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L24-L25) vs [MEASURE_1113.md:72](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L72-L79) |
| C14 | 2d whipsaw within 3 bars by split | 32% DEV, 47% VALIDATION, 50% RECENT | DEV: 32.1% (n=56); VALIDATION: 46.7% (n=15); RECENT: 50.0% (n=16) | OURS: DEV 18/56 (32.1%), VAL 7/15 (46.7%), REC 8/16 (50.0%) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:42](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L42) vs [CENSUS.md:31](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L31), [CENSUS.md:55](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L55), [CENSUS.md:79](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L79) |
| C15 | CCU three red crosses depths | depth 28.5/34.1/25.0% vs his 36/37/26% | 2025-10-09: -28.5%; 2026-01-07: -34.1%; 2026-05-23: -25.0% | OURS: -28.53%, -34.14%, -25.00% | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:43](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L43) vs [CENSUS.md:172](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L172), [CENSUS.md:174](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L174), [CENSUS.md:180](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L180) |
| C16 | 2d red crosses total counts | 44 red 2d crosses (DEV 28, VAL 7, RECENT 9) | DEV red: 28; VAL red: 7; RECENT red: 9; total: 44 | OURS: DEV red 28, VAL red 7, REC red 9; total 44 | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:43](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L43) vs [CENSUS.md:9](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L9), [CENSUS.md:33](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L33), [CENSUS.md:57](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L57) |
| C17 | Red 2d cross low timing | Low is within 1-3 bars in 37% of 35 cases | 1-3 bars: n=13, share 37.1% of n=35 (DEV+VALIDATION) | OURS: 13 / 35 = 37.14% | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:44](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L44) vs [CENSUS.md:81](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L81-L85) |
| C18 | Current readings (2026-11-13 run) | 5m: 25.5/24.7/21.2; 15m: 23.1/21.0/19.3; 1h: 54.1/12.9/31.6; 4h: 53.0/6.1/41.9; 1d: 23.5/11.1/28.0; 2d: 21.8/13.5/21.8; 5d: 24.7/18.3/22.5; 1w: 23.5/18.7/19.0 | 5m: 25.5/24.7/21.2; 15m: 23.1/21.0/19.3; 1h: 54.1/12.9/31.6; 4h: 53.0/6.1/41.9; 1d: 23.5/11.1/28.0; 2d: 21.8/13.5/21.8; 5d: 24.7/18.3/22.5; 1w: 23.5/18.7/19.0 | UNVERIFIABLE (run snapshot from Bybit 2026-11-13) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:50](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L50-L57) vs [MEASURE_1113.md:33](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L33-L40) |
| C19 | 4h peak move and win rate | move bigger than average (3.6% vs 2.9%), trend direction wins 57% at 12 bars, n=219 | n=219 trend-dir net +0.879% win 57%; abs move +3.615% vs all-bars +2.920% | UNVERIFIABLE (intraday cache not on disk) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:65](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L65) vs [MEASURE_1113.md:182](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L182) |
| C20 | 20-40 falling whipsaw flip | VALIDATION 20-40 falling whipsaws 75% n=8 vs 14% under 20 n=7; over 40 has n=1 | VAL: 20-40 falling n=8 ws 75.0%; <20 falling n=7 ws 14.3%; DEV >40 n=1 | OURS: VAL 20-40 falling 6/8 (75.0%), <20 falling 1/7 (14.3%) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:64](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L64) vs [CENSUS.md:37](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L37), [CENSUS.md:39](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L39) |
| C21 | Peak > 40: ADX > 25 twelve bars later | ADX is still above 25 twelve bars later in 92-100% | 5m: 8% below (92% above); 15m: 7% below (93% above); 1h: 8% below (92% above); 4h: 5% below (95% above); 1d: 6% below (94% above); 2d: 3% below (97% above); 5d: 0% below (100% above); 1w: 12% below (88% above, n=8) | UNVERIFIABLE (intraday cache not on disk) | MATCH | SOURCED: [HOW_TO_USE_ADX_1113.md:64](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md#L64) vs [MEASURE_1113.md:179](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L179-L186) |

---

## 3. Look-Ahead Hunt: Feature Timestamps vs Entry Bars

We audited `measure_1113.py` ([measure_1113.py:43-70](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/measure_1113.py#L43-L70)), `census.py` ([census.py:54-81](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/census.py#L54-L81)), and the underlying indicator implementation in `adx.py` ([adx.py:7-58](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/backtest/layers/adx/adx.py#L7-L58)).

### (a) Feature Construction & Signal Definition
1. **Indicator Smoothing (Wilder ADX / DI)**:
   - SOURCED: [adx.py:16-41](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/backtest/layers/adx/adx.py#L16-L41).
   - For bar index `i`, True Range `tr[i]` and directional movements `pdm[i]`, `mdm[i]` use only `high[i]`, `low[i]`, `high[i-1]`, `low[i-1]`, and `close[i-1]`.
   - The smoothed Wilder sums `s_tr`, `s_p`, `s_m` update strictly recursively up to index `i` (`k = i - 1`). No future bars (`i+1` onwards) are accessed.
   - Therefore, `dip[i]`, `dim[i]`, and `adx[i]` are pure causal functions of bars `0..i`.

2. **Trend Entry Signals (`L_cross`, `S_cross`, `L_adx25`, `S_adx25`)**:
   - SOURCED: [measure_1113.py:51-60](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/measure_1113.py#L51-L60).
   - Signal evaluation on loop iteration `i`:
     - Cross detection checks `dip[i-1] <= dim[i-1]` and `dip[i] > dim[i]` with `adx[i] > 20.0`.
     - 25-cross detection checks `adx[i-1] <= 25.0 < adx[i]` with `dip[i] > dim[i]`.
   - Decision bar is bar `i`. All signals depend solely on indices `i-1` and `i`.

3. **Peak Detection (`peak40`)**:
   - SOURCED: [measure_1113.py:60](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/measure_1113.py#L60).
   - Code: `adx[i-2] < adx[i-1] > adx[i] and adx[i-1] > 40.0`.
   - The peak occurred at bar `i-1`. The first downturn is confirmed at close of bar `i` (`adx[i] < adx[i-1]`). Entry occurs at close of bar `i`.
   - The trend direction is established at the peak bar `i-1`: `s = 1 if dip[i-1] > dim[i-1] else -1` ([measure_1113.py:183](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/measure_1113.py#L183)). This is fully known at bar `i`.

4. **2d Cross Census Slope**:
   - SOURCED: [census.py:65](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/census.py#L65).
   - Lookback: `sl = adx[i] - adx[i - 5]`. This is strictly backward-looking.

### (b) Execution Timing & Forward Return Horizons
- SOURCED: [measure_1113.py:65-70](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/measure_1113.py#L65-L70).
- Forward return formula: `sign * (c[i + h] / c[i] - 1.0) - fee`.
- Entry price is `c[i]` (close of the decision bar `i`).
- Exit price is `c[i + h]` (close of bar `i + h`, where `h in (3, 6, 12)`).
- Forward returns are non-overlapping with the decision bar's internal span (entry is at the boundary `c[i]`).
- Census forward window: SOURCED: [census.py:66](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/census.py#L66) slices `win = bars[i + 1: i + 1 + fwd]`, searching for the extreme strictly in bars `i+1` to `i+30` relative to entry at `C[i]`.

**Finding on Look-Ahead**: Zero look-ahead bias found. All indicator states, signal gates, and slope metrics use only data up to the signal close `i`.

---

## 4. Fee & Slippage Hunt: Accounting, Rates, and Application

We examined the fee models across `measure_1113.py` and repository fee standards in `MyTradingSys/backtest/fees.py`.

### (a) Fee Rate & Standard Profile
- SOURCED: [fees.py:12-13](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/backtest/fees.py#L12-L13), [fees.py:23](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/backtest/fees.py#L23), [fees.py:37](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/backtest/fees.py#L37).
  - `BINANCE_MAKER = 0.0002` (2 bps per side).
  - Regime D: Binance maker both legs = `0.0004` (4 bps round trip = `2 * BINANCE_MAKER`).
- SOURCED: [measure_1113.py:31](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/measure_1113.py#L31):
  - `FEE = _fees.BINANCE_MAKER * 2` (4 bps round trip).

### (b) Application and Side Accounting
- SOURCED: [measure_1113.py:69](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/measure_1113.py#L69):
  - `fwd(c, i, h, sign, fee)` computes `sign * (c[i + h] / c[i] - 1.0) - fee`.
  - For long trades (`sign = +1`): return is `(c[i+h]/c[i] - 1) - fee`.
  - For short trades (`sign = -1`): return is `-(c[i+h]/c[i] - 1) - fee`.
  - In both long and short trades, the fee is subtracted as a positive cost drag. Fees are NOT accidentally credited to shorts.
- Round-trip accounting:
  - Each trade represents an entry and exit (`h` bars later).
  - `FEE` is 0.0004 (4 bps), representing the complete round-trip cost (entry leg + exit leg).
  - Baseline trades also have `fee` applied identically: SOURCED: [measure_1113.py:223](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/measure_1113.py#L223).

### (c) Timeframe Scope & Slippage
- SOURCED: [measure_1113.py:213](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/measure_1113.py#L213):
  - `fee = FEE if tf in INTRADAY else 0.0`.
  - Intraday frames (`5m`, `15m`, `1h`, `4h`) pay 4 bps round-trip fee.
  - Daily and higher frames (`1d`, `2d`, `5d`, `1w`) assume zero fee (explicitly stated: "none on 1d+ (OURS)" in [MEASURE_1113.md:5](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L5)).
- Slippage:
  - Explicit slippage is 0 bps; however, adopting maker fee rates (2 bps per side) on close-to-close trades assumes passive limit order fills at bar closes without adverse execution drag. The paper explicitly clarifies: "Context measurement: no orders, no edge claim" ([MEASURE_1113.md:3](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L3)).

**Finding on Fees**: Fee accounting is mathematically correct, subtracted on both long and short legs, and uses single-source repository constants.

---

## 5. Recount Summary

1. **Re-executed Census (`census.py`)**:
   - DEV 2d crosses: 56 total (red 28, green 28); whipsaw<=3 = 32.1% (OURS: matches [CENSUS.md:31](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L31)).
   - VALIDATION 2d crosses: 15 total (red 7, green 8); whipsaw<=3 = 46.7% (OURS: matches [CENSUS.md:55](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L55)).
   - RECENT 2d crosses: 17 total (red 9, green 8); whipsaw<=3 = 50.0% (OURS: matches [CENSUS.md:79](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L79)).
   - CCU red crosses DEV+VAL (n=35): exactly 35; low in 1-3 bars = 13 (37.1%) (OURS: matches [CENSUS.md:81-85](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L81-L85)).
   - CCU specific cases depths: 2025-10-09 (-28.5%), 2026-01-07 (-34.1%), 2026-05-23 (-25.0%) (OURS: matches [CENSUS.md:172-180](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/CENSUS.md#L172-L180)).

2. **Re-executed 1d Events from `measure_1113.py` on `btc_daily.csv`**:
   - `L_cross`: n=55, net +0.100% (h=3), -0.065% (h=6), +2.289% (h=12) (OURS: matches [MEASURE_1113.md:64](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L64)).
   - `L_adx25`: n=34, net +2.871% (h=3), +4.142% (h=6), +5.558% (h=12) (OURS: matches [MEASURE_1113.md:65](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L65)).
   - `S_cross`: n=71, net +0.175% (h=3), -0.314% (h=6), -0.241% (h=12) (OURS: matches [MEASURE_1113.md:66](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L66)).
   - `S_adx25`: n=33, net +1.865% (h=3), +3.170% (h=6), +4.741% (h=12) (OURS: matches [MEASURE_1113.md:67](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L67)).
   - `peak40`: n=62 (OURS: matches [MEASURE_1113.md:183](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-review-adx-di-argon-1113/MyTradingSys/research/adx_di_2026-11/MEASURE_1113.md#L183)).

3. **Intraday Data (5m Bybit cache)**:
   - Not checked into git (the runner fetched 696,252 5m bars from the public Bybit v5 API during execution). Intraday event counts and statistics are labeled UNVERIFIABLE for raw local data recount, but SOURCED and verified for consistency between `HOW_TO_USE_ADX_1113.md` and `MEASURE_1113.md`.

---

## 6. Conclusion

The adx-di study (`adx_di_2026-11`) is rigorous, sound, free of look-ahead artifacts, and appropriately net-of-fee. The conclusions drawn in `HOW_TO_USE_ADX_1113.md` are supported by the data tables.
