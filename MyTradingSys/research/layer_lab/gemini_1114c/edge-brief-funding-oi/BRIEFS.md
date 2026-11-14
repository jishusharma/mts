3 pre-registration briefs (funding and open-interest conditions with cached data and no verdict row)

# Edge Hunt: Funding and Open-Interest Pre-Registration Briefs

## 1. Ledger Inventory & Cache Audit

### 1.1 Source Ledgers Parsed
- `MyTradingSys/research/VERDICTS.csv`: 175 data rows (lines 2-176; header at line 1).
- `MyTradingSys/research/TRIAL_LEDGER.csv`: 122 data rows (lines 2-123; header at line 1).
- Funding and OI trials already in `MyTradingSys/research/VERDICTS.csv`:
  - `MyTradingSys/research/VERDICTS.csv:26-28`: `carry_basis_2026-10-18` (`CARRY_always_unlevered` PASS, `CARRY_switch_unlevered` PASS, `CARRY_always_margin3x` FAIL; delta-neutral funding carry basis).
  - `MyTradingSys/research/VERDICTS.csv:47`: `orderflow_views_2026-10-14` ("Price vs CVD divergence on 1m and 5m, with an OI split", DEV, FAIL).
  - `MyTradingSys/research/VERDICTS.csv:164-165` and `MyTradingSys/research/VERDICTS.csv:169-170`: `btc_orderflow_map_1112` (`A3_funding_15m` and `A3_funding_60m`, DEV, FAIL; duplicated rows in ledger).
- Funding and OI trials already in `MyTradingSys/research/TRIAL_LEDGER.csv`:
  - `MyTradingSys/research/TRIAL_LEDGER.csv:31`: `session_flow_context_2026-10-18` (`PRE_REG_primary`, `metrics 5m (2025-10-01..2026-02-28)`, descriptive state study, no trades, `read-INCONCLUSIVE`).
  - Zero directional funding-rate or daily OI pre-registration rows exist in `TRIAL_LEDGER.csv`.

### 1.2 Data Cache Listings & Date Ranges (Listings Only, No Outcomes)
- `C:/Users/e-ngineers/MTS_data_cache/bybit_funding/` (22 symbol JSON files, 8h funding prints):
  - Row counts: `5246` to `7273` prints per symbol.
  - Earliest start: `2020-03-25` (`BTCUSDT`); latest start: `2022-01-30` (`NEOUSDT`); all end `2026-11-13`.
  - Major symbols: `BTCUSDT` (`7273` rows, `2020-03-25 .. 2026-11-13`), `ETHUSDT` (`6644` rows, `2020-10-21 .. 2026-11-13`), `SOLUSDT` (`6251` rows, `2021-06-29 .. 2026-11-13`).
- `C:/Users/e-ngineers/mts_cache/buyzone_test4/*_fund.json` (22 symbol JSON files, 8h funding prints):
  - Row counts: `5246` to `7273` prints per symbol; `2020-03-25` (`BTC`) to `2026-11-13` (common 22-symbol overlap starts `2022-01-30`).
- `C:/Users/e-ngineers/mts_cache/buyzone_test4/*_oi.json` (22 symbol JSON files, daily OI snapshots):
  - Row counts: `1748` to `2292` daily rows per symbol.
  - Earliest start: `2020-08-05` (`BTC`, `2292` rows); latest start: `2022-01-31` (`NEO`); all end `2026-11-13`.
  - Major symbols: `BTC_oi.json` (`2292` rows, `2020-08-05 .. 2026-11-13`), `ETH_oi.json` (`2214` rows, `2020-10-22 .. 2026-11-13`), `SOL_oi.json` (`1963` rows, `2021-06-30 .. 2026-11-13`).
- `C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d/` and `binance_spot_4h/` (22 symbol JSON files each):
  - `1d`: `2221` to `3376` bars (`2017-08-17 .. 2026-11-13` for `BTCUSDT`, `ETHUSDT`; latest start `2020-10-15` for `FILUSDT`).
  - `4h`: `13322` to `20239` bars (`2017-08-17 .. 2026-11-13` for `BTCUSDT`, `ETHUSDT`; latest start `2020-10-15` for `FILUSDT`).
- Note: Long/short ratio feeds (`topLongShortPositionRatio`, `topLongShortAccountRatio`) are NOT present in the local data cache, so all 3 briefs below use cached funding (`bybit_funding` / `*_fund.json`) and daily OI (`*_oi.json`) paired with cached `binance_spot_4h` / `binance_spot_1d` klines.

---

## 2. Pre-Registration Briefs (Zero Outcomes Computed)

### Brief 1: Negative Funding Extreme Short-Squeeze Long (4h)
- **Condition & Verdict Gap**: Extreme negative 8h funding short-squeeze continuation/rebound across the 22-symbol cached universe (`bybit_funding` + `binance_spot_4h`). No verdict row exists in `MyTradingSys/research/VERDICTS.csv` (prior funding rows cover only delta-neutral carry at `MyTradingSys/research/VERDICTS.csv:26-28` and 15m/60m BTC order-flow map events at `MyTradingSys/research/VERDICTS.csv:164-165`).
- **Sourced Basis**:
  - SOURCED: "High negative funding means shorts are aggressive and paying longs, setting up short squeeze conditions." (`MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:28`).
  - SOURCED: Standard Binance baseline interest rate is `0.01%` per 8h (`MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:18`: "Standard baseline interest rate is 0.01% per 8h (0.03% daily) for USDT-margined contracts"), and `0.03%` per 8h (3x baseline) is the standard extreme threshold (`MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:59`: "3x baseline").
  - SOURCED: Settled discretely at 8h timestamps (`00:00`, `08:00`, `16:00` UTC) (`MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:19`: "Settled discretely at timestamps (standard 8h: 00:00, 08:00, 16:00 UTC; or accelerated 4h/1h).").
- **Hypothesis**: OURS. Across 22 cached crypto pairs on 4h bars, when an 8h funding print drops to an extreme negative level ($\le -0.03\%$ per 8h, the symmetric 3x mirror of the SOURCED `0.03%` extreme threshold, AND below the trailing 90-print 5th percentile) while price closes bullishly on the 4h bar containing the settlement timestamp, entering long at the next 4h bar open captures forced short-covering squeezes with positive mean fee-net return above `12 bp`.
- **Entry**: OURS. Long at the open of 4h bar $i+1$ when 4h bar $i$ (closing at an 8h funding settlement timestamp `00:00`, `08:00`, or `16:00` UTC) satisfies:
  1. Settled 8h funding rate $F_i \le -0.0003$ ($-0.03\%$ per 8h; symmetric mirror of SOURCED `0.03%` extreme in `MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:59`) AND $F_i \le Q_{0.05}(F_{i-90:i-1})$ (trailing 90-print 5th percentile; OURS).
  2. Bullish squeeze confirmation bar: `close[i] > open[i]` (OURS).
  3. Cooldown: no prior active trade or entry on the same symbol within the preceding `6` 4h bars (`24` hours; OURS).
- **Stop**: OURS. Initial stop at $\min(\text{low}[i-1], \text{low}[i]) - 0.5 \times \text{ATR}_{14}[i]$, floored at `0.5%` below entry price to prevent zero-width stops.
- **Hold**: OURS. Maximum holding period of `12` 4h bars (`48` hours), with a `2.0R` profit target limit order; exit at market on bar $i+12$ open if neither stop nor `2.0R` target is hit.
- **12 bp Fee-Net Cost**: OURS. `12 bp` (`0.12%`) round-trip taker + slippage cost (`2 x 5 bp` taker fee + `2 bp` execution slippage allowance), plus real signed 8h funding cash flows received/paid at settlement timestamps held (`side_sign * rate`, SOURCED `MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:11`).
- **DEV / VAL Split**: OURS.
  - `DEV <= 2023-12-31`: Bars opening on or before `2023-12-31T23:59:59Z`.
  - `VAL >= 2024-01-01`: Bars opening on or after `2024-01-01T00:00:00Z` (frozen; unread until DEV passes).
- **Kill Rule**: OURS. FAIL and kill this setup family if on DEV pooled across the 22 symbols the sample size $n < 200$ events, or if mean fee-net return $\le 0.0\text{ bp}$, or if $t\text{-stat} < 2.0$. Kill scope: 4h negative funding extreme ($\le -0.03\%$ and $\le$ 5th percentile) bullish-close long squeeze on 22 cached symbols; positive funding fades and other timeframes remain outside this kill scope.

---

### Brief 2: Daily Open-Interest Flush + Bullish Reclaim Long (`edge-oi-flush-1113` 1d Adaptation)
- **Condition & Verdict Gap**: Daily long-liquidation OI flush followed by a bullish reclaim bar across 22 cached symbols (`*_oi.json` + `binance_spot_1d`). No verdict row exists in `MyTradingSys/research/VERDICTS.csv` (the only OI-related verdict row is `MyTradingSys/research/VERDICTS.csv:47`, `orderflow_views_2026-10-14`, which tested 1m/5m price-vs-CVD divergence with an OI split; `edge-oi-flush-1113` is listed as pending in `MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md:77`).
- **Sourced Basis**:
  - SOURCED: CME canonical Price/OI state: "Price Down + OI Down (Long Liquidation, weak bear)" (`MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md:24`).
  - SOURCED: Krown deleveraging mechanic: "once the borrowed positions are gone there s nobody left who actually wanted to sell" (`MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:70`).
  - SOURCED: Murphy exhaustion rule: "declining OI during a trend warns of trend exhaustion and impending reversal" (`MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md:27`).
- **Hypothesis**: OURS. On daily bars across 22 cached crypto pairs, a sharp single-day deleveraging flush (daily price drop $\le -3.0\%$ paired with daily OI contraction $\le -5.0\%$) followed within `1` to `2` daily bars by a bullish reclaim close (`close > open` and `close > flush_bar_close`) signals exhausted forced selling and yields positive mean fee-net return above `12 bp`.
- **Entry**: OURS. Long at the open of daily bar $j+1$ when:
  1. Flush bar $f \in \{j-1, j\}$ (most recent 1-2 daily bars) had daily close-to-close return $\Delta p_f \le -3.0\%$ AND daily OI change $\Delta OI_f \le -5.0\%$ (OURS quantitative thresholds operationalizing SOURCED "Price Down + OI Down (Long Liquidation)" at `MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md:24`).
  2. Reclaim bar $j$ closes bullishly above the flush close: `close[j] > open[j]` and `close[j] > close[f]` (OURS).
  3. Cooldown: no active trade or prior entry on the same symbol within `5` daily bars (OURS).
- **Stop**: OURS. Initial stop placed at $\min(\text{low}[f], \text{low}[j]) - 0.25 \times \text{ATR}_{14}[j]$, floored at `1.0%` below entry price.
- **Hold**: OURS. Maximum holding period of `7` daily bars (`7` days), with a `2.0R` profit target limit order; exit at market on bar $j+7$ open if neither stop nor `2.0R` target is hit.
- **12 bp Fee-Net Cost**: OURS. `12 bp` (`0.12%`) round-trip taker + slippage cost (`2 x 5 bp` taker fee + `2 bp` slippage allowance).
- **DEV / VAL Split**: OURS.
  - `DEV <= 2023-12-31`: Bars opening on or before `2023-12-31T23:59:59Z`.
  - `VAL >= 2024-01-01`: Bars opening on or after `2024-01-01T00:00:00Z` (frozen; unread until DEV passes).
- **Kill Rule**: OURS. FAIL and kill this setup family if on DEV pooled across 22 symbols $n < 200$ events, or if mean fee-net return $\le 0.0\text{ bp}$, or if $t\text{-stat} < 2.0$. Kill scope: Daily OI flush ($\Delta p \le -3.0\%$, $\Delta OI \le -5.0\%$) + bullish reclaim long on 22 cached symbols; intraday 5m/1h flush studies and short-squeeze mirror setups remain outside this kill scope.

---

### Brief 3: Crowded Leverage Exhaustion Short (`funding_extreme_cascade_veto` / `edge-crowding-reversal-1113`)
- **Condition & Verdict Gap**: Joint extreme positive 8h funding + stacked daily OI z-score at 20-day highs followed by a bearish reversal close across 22 cached symbols (`*_fund.json` + `*_oi.json` + `binance_spot_1d`). No verdict row exists in `MyTradingSys/research/VERDICTS.csv`; both `funding_extreme_cascade_veto` (`MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:72`) and `edge-crowding-reversal-1113` (`MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md:78`) are listed as open/untested in the rulebooks.
- **Sourced Basis**:
  - SOURCED: Krown cascade potential energy: "open interest is potential energy high open interest plus hot funding doesn t tell you when the avalanche comes" / "it tells you the mountain is loaded with snow and that avalanche has a potential to come now" (`MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:42-44`).
  - SOURCED: Hot funding threshold: `>= 0.03%` per 8h (`3x` the `0.01%` baseline) (`MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:30,59`).
  - SOURCED: Stacked OI threshold: `rolling 30d OI z-score > 2.0` (`MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md:80`: "rolling 30d OI z-score > 2.0"; `MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:72`: "8h funding exceeds 0.03% and OI z-score > 2.0").
- **Hypothesis**: OURS. Across 22 cached crypto pairs on daily bars, when leverage is simultaneously crowded (`3`-print daily mean 8h funding $\ge +0.03\%$ AND rolling `30`-day OI z-score $> 2.0$) at a 20-day price high and price prints a bearish rejection close (`close < open`), shorting at the next daily open captures long-liquidation unwinds with positive mean fee-net return above `12 bp`.
- **Entry**: OURS. Short at the open of daily bar $i+1$ when daily bar $i$ satisfies:
  1. Daily mean of the 3 settled 8h funding prints on UTC day $i$ is $\bar{F}_i \ge +0.0003$ ($+0.03\%$ per 8h; SOURCED threshold `MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:59,72`).
  2. Rolling `30`-day OI z-score on day $i$ is $Z_{OI,30}[i] > 2.0$ (SOURCED threshold `MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md:80` / `MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:72`).
  3. Location & trigger: `high[i] == max(high[i-19 : i+1])` (20-day high) AND `close[i] < open[i]` (bearish rejection close; OURS).
  4. Cooldown: no active trade or prior entry on the same symbol within `5` daily bars (OURS).
- **Stop**: OURS. Initial stop placed at `high[i] + 0.25 * ATR_14[i]`, floored at `1.0%` above entry price.
- **Hold**: OURS. Maximum holding period of `7` daily bars (`7` days), with a `2.0R` profit target limit order; exit at market on bar $i+7$ open if neither stop nor `2.0R` target is hit.
- **12 bp Fee-Net Cost**: OURS. `12 bp` (`0.12%`) round-trip taker + slippage cost (`2 x 5 bp` taker fee + `2 bp` slippage allowance), plus real signed 8h funding cash flows received/paid during the hold (`side_sign * rate`, SOURCED `MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:11`).
- **DEV / VAL Split**: OURS.
  - `DEV <= 2023-12-31`: Bars opening on or before `2023-12-31T23:59:59Z`.
  - `VAL >= 2024-01-01`: Bars opening on or after `2024-01-01T00:00:00Z` (frozen; unread until DEV passes).
- **Kill Rule**: OURS. FAIL and kill this setup family if on DEV pooled across 22 symbols $n < 200$ events, or if mean fee-net return $\le 0.0\text{ bp}$, or if $t\text{-stat} < 2.0$. Kill scope: Daily stacked OI ($Z_{OI,30} > 2.0$) + hot funding ($\ge +0.03\%$/8h) + bearish 20-day-high rejection short on 22 cached symbols; using the same crowding gate strictly as a long-veto/sizing throttle (`KR-LQC02`) remains outside this kill scope.

---

## 3. Parameter & Number Provenance Table

| Brief | Item / Parameter | Value | Label | Source (`file:line` or rationale) |
|---|---|---|---|---|
| Inventory | `VERDICTS.csv` row count | `175` data rows | SOURCED | `MyTradingSys/research/VERDICTS.csv:2-176` (parsed count) |
| Inventory | `TRIAL_LEDGER.csv` row count | `122` data rows | SOURCED | `MyTradingSys/research/TRIAL_LEDGER.csv:2-123` (parsed count) |
| Brief 1 | Baseline 8h funding rate | `0.01%` per 8h | SOURCED | `MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:18` ("Standard baseline interest rate is 0.01% per 8h") |
| Brief 1 | Extreme funding magnitude | `0.03%` per 8h (`3x` baseline) | SOURCED | `MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:59` ("3x baseline") |
| Brief 1 | Negative extreme trigger | `<= -0.03%` & `<= Q_0.05(90)` | OURS | Symmetric negative mirror + trailing 90-print 5th percentile |
| Brief 1 | Stop / Hold / Target | `0.5 ATR` (min `0.5%`) / `12` x 4h / `2.0R` | OURS | Pre-registered execution parameters |
| Brief 2 | Long liquidation state | Price Down + OI Down | SOURCED | `MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md:24` ("Price Down + OI Down (Long Liquidation, weak bear)") |
| Brief 2 | Exhaustion mechanism | Forced sellers cleared | SOURCED | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md:70` ("once the borrowed positions are gone there s nobody left who actually wanted to sell") |
| Brief 2 | Flush thresholds | `dp <= -3.0%`, `dOI <= -5.0%` | OURS | Pre-registered daily flush cutoffs |
| Brief 2 | Stop / Hold / Target | `0.25 ATR` (min `1.0%`) / `7` x 1d / `2.0R` | OURS | Pre-registered execution parameters |
| Brief 3 | Hot funding threshold | `>= +0.03%` per 8h | SOURCED | `MyTradingSys/research/indicator_rulebooks/FUNDING_LS.md:72` ("8h funding exceeds 0.03% and OI z-score > 2.0") |
| Brief 3 | Stacked OI threshold | `30d OI z-score > 2.0` | SOURCED | `MyTradingSys/research/indicator_rulebooks/OPEN_INTEREST.md:80` ("rolling 30d OI z-score > 2.0") |
| Brief 3 | High lookback & trigger | `20`-day high + bearish close | OURS | Pre-registered rejection trigger |
| Brief 3 | Stop / Hold / Target | `0.25 ATR` (min `1.0%`) / `7` x 1d / `2.0R` | OURS | Pre-registered execution parameters |
| All 3 | Fee-net cost hurdle | `12 bp` (`0.12%`) round trip | OURS | Card specification (`2 x 5 bp` taker + `2 bp` slippage) |
| All 3 | DEV / VAL split | `DEV <= 2023-12-31`, `VAL >= 2024-01-01` | OURS | Card specification |
| All 3 | Power & pass gate | `n >= 200`, `mean > 0 bp`, `t >= 2.0` | OURS | Standard MTS pre-registration kill rule |
