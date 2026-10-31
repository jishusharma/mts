# Layer Parameter Labels Audit: wavetrend, rsi, krown, positioning, turn_of_candle

Comprehensive parameter audit for backtest layer modules:
- `MyTradingSys/backtest/layers/wavetrend`
- `MyTradingSys/backtest/layers/rsi`
- `MyTradingSys/backtest/layers/krown`
- `MyTradingSys/backtest/layers/positioning`
- `MyTradingSys/backtest/layers/turn_of_candle`

Every tunable constant and parameter default is labelled either `SOURCED` (with analyst/literature citation quote and file:line) or `OURS` (internal design / engineering choice). Any constant without a source quote in literature is flagged `OURS` or `NOT_IN_DATA`.

---

## 1. Parameter Inventory Table

| Layer Module | Parameter / Constant | File:Line | Default Value | Label | Source Citation / Quote or NOT_IN_DATA |
|---|---|---|---|---|---|
| **wavetrend** | `N1` (channel length) | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `10` | `SOURCED` | LazyBear's WaveTrend Oscillator (TradingView scripts 2KE8wTuF / jFQn4jYZ, Crosses:14-21); `FORMULAS.md:20` |
| **wavetrend** | `N2` (average length) | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `21` | `SOURCED` | LazyBear's WaveTrend Oscillator (Crosses:14-21); `FORMULAS.md:20` |
| **wavetrend** | `SMA_N` (signal line length) | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `4` | `SOURCED` | LazyBear's WaveTrend Oscillator (Crosses:14-21); `FORMULAS.md:20` |
| **wavetrend** | `K` (CCI multiplier constant) | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `0.015` | `SOURCED` | Lambert's Commodity Channel Index constant adopted in LazyBear's formula (Crosses:14-21); `FORMULAS.md:20` |
| **wavetrend** | `OB1` (extreme overbought/oversold) | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:17` | `60.0` | `SOURCED` | LazyBear's WaveTrend second overbought level `ob2 = 60.0`, `os2 = -60.0` (Crosses:9-12); `FORMULAS.md:20` |
| **wavetrend** | `OB2` (outer overbought/oversold) | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:17` | `53.0` | `SOURCED` | LazyBear's WaveTrend first overbought level `ob1 = 53.0`, `os1 = -53.0` (Crosses:9-12); `FORMULAS.md:20` |
| **wavetrend** | `WARMUP` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:18` | `200` | `OURS` | EMA stabilization warm-up suppression mask: `research/wavetrend_2026-10-17/PARITY_CONTRACT.md:3` |
| **wavetrend** | `D_TOL` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:19` | `1e-9` | `OURS` | Flat window zero-deviation tolerance: inline comment `# OURS: d <= D_TOL*|ap| counts as a flat window` |
| **wavetrend** | `typical price divisor` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:92` | `3.0` | `SOURCED` | Standard typical price calculation (H + L + C) / 3; `FORMULAS.md:20` |
| **rsi** | `rsi_core.period` | `MyTradingSys/backtest/layers/rsi/params/default.json:7` | `14` | `SOURCED` | Wilder's standard RSI 14-period default; `FORMULAS.md:1` |
| **rsi** | `rsi_ma.length` | `MyTradingSys/backtest/layers/rsi/params/default.json:11` | `14` | `SOURCED` | TradingView standard RSI MA default (SMA 14) |
| **rsi** | `rsi_events.levels` | `MyTradingSys/backtest/layers/rsi/params/default.json:14` | `[70, 50, 30]` | `SOURCED` | Standard Wilder overbought (70), midpoint (50), oversold (30) levels |
| **rsi** | `rsi_events.tolerance` | `MyTradingSys/backtest/layers/rsi/params/default.json:15` | `0` | `OURS` | Internal tolerance band around level; NOT_IN_DATA in Wilder |
| **rsi** | `malkan_40_60.lo` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:10` | `40` | `SOURCED` | Malkan (Malkansview), `research/malkan_rsi_2026-09-28/WEB_RESEARCH.md` MLK-R1 / MLK-S1: "whenever in a bullish trend, it won't be able to cross 40" |
| **rsi** | `malkan_40_60.hi` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:11` | `60` | `SOURCED` | Malkan (Malkansview), `research/malkan_rsi_2026-09-28/WEB_RESEARCH.md` MLK-R1 / MLK-S2: "Whenever the market is bearish, it won't be able to cross 60" |
| **rsi** | `malkan_40_60.regime_lookback` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:12` | `20` | `OURS` | Internal lookback window for regime confirmation; NOT_IN_DATA for Malkan |
| **rsi** | `malkan_40_60.event_tolerance` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:13` | `2` | `OURS` | Internal tolerance band for 40/60 level touches; NOT_IN_DATA for Malkan |
| **rsi** | `min_bars` (regular divergence) | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:4` | `3` | `SOURCED` | Malkan (Malkansview), `extract_Wvq1TZh8aF0.md:13`: "How many candles are needed? Three." |
| **rsi** | `max_bars` (regular divergence) | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:5` | `10` | `SOURCED` | Malkan (Malkansview), `extract_Wvq1TZh8aF0.md:13`: "It should be between three and 10." |
| **rsi** | `min_rsi_diff` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:9` | `0.0` | `SOURCED` | Malkan (Malkansview), `extract_cQ-y1oULkBw.md:15`: "Sometimes there is divergence in decimals and that will also be acceptable." |
| **rsi** | `reverse.min_bars` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:14` | `5` | `SOURCED` | Malkan (Malkansview), `GbXnw_tNMtw_raw.txt:460`: "number of bar should be between five to fifty" |
| **rsi** | `reverse.max_bars` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:15` | `14` | `SOURCED` | Malkan (Malkansview), `GbXnw_tNMtw_raw.txt:379`: "number of bars which are less than 15" |
| **rsi** | `reverse.prd_min_rsi` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:18` | `60.0` | `SOURCED` | Malkan (Malkansview), `GbXnw_tNMtw_raw.txt:460`: "both the point should be about sixty if it's a positive edge divergence" |
| **rsi** | `reverse.nrd_max_rsi` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:19` | `40.0` | `SOURCED` | Malkan (Malkansview), `GbXnw_tNMtw_raw.txt:460`: "negative reverse divergence it should be below forty" |
| **rsi** | `krown_hidden_bars.min_bars` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:23` | `3` | `OURS` | Inline note: "OURS, KROWN-CONFLUENCE generic hidden divergence, not Malkan" |
| **rsi** | `krown_hidden_bars.max_bars` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:23` | `10` | `OURS` | Inline note: "OURS, KROWN-CONFLUENCE generic hidden divergence, not Malkan" |
| **rsi** | `period` | `MyTradingSys/backtest/layers/rsi/rsi_core.py:7` | `14` | `SOURCED` | Wilder's standard RSI 14-period default; `FORMULAS.md:1` |
| **rsi** | `length` | `MyTradingSys/backtest/layers/rsi/rsi_ma.py:8` | `14` | `SOURCED` | TradingView standard RSI MA default (SMA 14) |
| **rsi** | `lo` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:24` | `40.0` | `SOURCED` | Malkan 40 level (MLK-R1 / MLK-S1) |
| **rsi** | `hi` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:24` | `60.0` | `SOURCED` | Malkan 60 level (MLK-R1 / MLK-S2) |
| **rsi** | `lookback` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:24` | `20` | `OURS` | Internal lookback parameter; NOT_IN_DATA for Malkan |
| **rsi** | `level` (bull setup) | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:64` | `40.0` | `SOURCED` | MLK-S1: "Bullish candlestick forms at 40 RSI level on daily chart = buy signal" |
| **rsi** | `tolerance` (bull setup) | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:64` | `2.0` | `OURS` | Tolerance band; NOT_IN_DATA for Malkan |
| **rsi** | `level` (bear setup) | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:107` | `60.0` | `SOURCED` | MLK-S2: "Bearish candlestick forms at 60 RSI level on daily chart = short signal" |
| **rsi** | `tolerance` (bear setup) | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:107` | `2.0` | `OURS` | Tolerance band; NOT_IN_DATA for Malkan |
| **rsi** | `level` (MTF bull setup) | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:53` | `40.0` | `SOURCED` | MLK-S1-MTF: Malkan 40 level |
| **rsi** | `tolerance` (MTF bull setup) | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:53` | `2.0` | `OURS` | Tolerance band; NOT_IN_DATA for Malkan |
| **rsi** | `level` (MTF bear setup) | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:79` | `60.0` | `SOURCED` | MLK-S2-MTF: Malkan 60 level |
| **rsi** | `tolerance` (MTF bear setup) | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:79` | `2.0` | `OURS` | Tolerance band; NOT_IN_DATA for Malkan |
| **rsi** | `PRD_MIN_RSI` | `MyTradingSys/backtest/layers/rsi/rsi_divergence.py:44` | `60.0` | `SOURCED` | Malkan (Malkansview), `GbXnw_tNMtw_raw.txt:460`: "both the point should be about sixty if it's a positive edge divergence" |
| **rsi** | `NRD_MAX_RSI` | `MyTradingSys/backtest/layers/rsi/rsi_divergence.py:45` | `40.0` | `SOURCED` | Malkan (Malkansview), `GbXnw_tNMtw_raw.txt:460`: "negative reverse divergence it should be below forty" |
| **rsi** | `min_rsi_diff` | `MyTradingSys/backtest/layers/rsi/rsi_divergence.py:61` | `0.0` | `SOURCED` | Malkan (Malkansview), `extract_cQ-y1oULkBw.md:15` |
| **rsi** | `min_rsi_diff` | `MyTradingSys/backtest/layers/rsi/krown_hidden_divergence.py:20` | `0.0` | `OURS` | Shared with rsi_divergence |
| **rsi** | `STOP_PCT` | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:56` | `0.01` | `OURS` | Standard indicator-layer 1% stop loss bracket (`MTS_USER_GUIDE.md:4`) |
| **rsi** | `TARGET_PCT` | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:57` | `0.02` | `OURS` | Standard indicator-layer 2% take profit bracket (`MTS_USER_GUIDE.md:4`) |
| **rsi** | `MAX_BARS` | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:58` | `100` | `OURS` | Trade timeout bar horizon; NOT_IN_DATA in trader rules |
| **rsi** | `MIN_OOS_N` | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:59` | `30` | `OURS` | Sample size threshold for statistical evaluation |
| **rsi** | `MAX_PBO` | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:60` | `0.5` | `OURS` | Probability of backtest overfitting cutoff |
| **rsi** | `is_frac` | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:76` | `0.70` | `OURS` | 70/30 chronological IS/OOS split fraction |
| **rsi** | `PRIMARY_H` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:48` | `10` | `OURS` | Primary forward return horizon: docstring `PRIMARY_H = 10 bars and T_MIN = 2.0 are engineering choices (NO-SOURCE)` |
| **rsi** | `MIN_EVENTS` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:49` | `300` | `OURS` | T089 item specification: docstring `fewer than MIN_EVENTS (300, operator rule in the T089 item)` |
| **rsi** | `T_MIN` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:50` | `2.0` | `OURS` | Engineering choice t-statistic hurdle |
| **rsi** | `MIN_YEAR_EVENTS` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:51` | `30` | `OURS` | Sub-sample minimum events per calendar year |
| **rsi** | `OPERATOR_MIN_BARS` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:52` | `11` | `OURS` | Operator long-range divergence idea (T091, NO-SOURCE); Malkan rejects this window |
| **rsi** | `OPERATOR_MAX_BARS` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:53` | `60` | `OURS` | Operator long-range divergence idea (T091, NO-SOURCE); Malkan rejects this window |
| **rsi** | `RSI_PERIOD` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:54` | `14` | `SOURCED` | Wilder standard 14-period RSI; `FORMULAS.md:1` |
| **krown** | `enabled` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:4` | `false` | `OURS` | Flag-gated default OFF (`KROWN_LAYER_SPEC.md:5`) |
| **krown** | `zone_k` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:5` | `3` | `OURS` | Bars each side of a swing; KR-L01 gives no number, grid `{2,3,5}` (`KROWN_LAYER_SPEC.md:42`) |
| **krown** | `zone_min_turns` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:6` | `2` | `SOURCED` | Rule KR-Z02: "one touch is an event, two is a memory" (`KROWN_LAYER_SPEC.md:43`, citing rule Z02; `KROWN_RULES.csv:Z02`) |
| **krown** | `zone_lookback` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:7` | `250` | `OURS` | Pivots older than this many bars are not ranked (KR-Z18 "recent" is not defined, `KROWN_LAYER_SPEC.md:43`) |
| **krown** | `zone_max` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:8` | `5` | `SOURCED` | Rule KR-Z03: "at most 3 to 5 zones" (`KROWN_LAYER_SPEC.md:43`, citing rule Z03; `KROWN_RULES.csv:Z03`) |
| **krown** | `zone_mature_tests` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:9` | `3` | `SOURCED` | Rule KR-Z13: "beyond three tests the break probability is higher" (`KROWN_LAYER_SPEC.md:43`, citing rule Z13; `KROWN_RULES.csv:Z13`) |
| **krown** | `swing_tol` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:10` | `0.01` | `OURS` | "About the same" range tolerance (KR-L10 gives no numeric threshold, `KROWN_LAYER_SPEC.md:42`) |
| **krown** | `vol_sma` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:11` | `20` | `SOURCED` | Rule KR-V01: SMA 20 on volume (`KROWN_LAYER_SPEC.md:44`, citing rule V01; `KROWN_RULES.csv:V01`) |
| **krown** | `vol_mult` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:12` | `2` | `SOURCED` | Rule KR-V02: "two or more times the average" (`KROWN_LAYER_SPEC.md:44`, citing rule V02; `KROWN_RULES.csv:V02`) |
| **krown** | `vol_half` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:13` | `0.5` | `SOURCED` | Rule KR-V10: observation: "volume near 50 % of average before a breakout" (`KROWN_LAYER_SPEC.md:44`, citing rule V10; `KROWN_RULES.csv:V10`) |
| **krown** | `vol_slots` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:14` | `7` | `OURS` | Same-slot baseline arm: weekday slot for 1d (`KROWN_LAYER_SPEC.md:44`) |
| **krown** | `vol_slot_prev` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:15` | `8` | `OURS` | Same-slot baseline arm: previous weeks averaged (`KROWN_LAYER_SPEC.md:44`) |
| **krown** | `tops_vol_sma` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:16` | `30` | `SOURCED` | Rule KR-V02 / TOP-05: 30-day average in the tops framework (`KROWN_LAYER_SPEC.md:44,51`) |
| **krown** | `bbwp_basis` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:17` | `7` | `SOURCED` | Rule KR-Q01: basis length 7 (`KROWN_LAYER_SPEC.md:45`, citing rule Q01; `KROWN_RULES.csv:Q01`) |
| **krown** | `bbwp_lookback` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:18` | `100` | `SOURCED` | Rule KR-Q01: lookback 100 (`KROWN_LAYER_SPEC.md:45`, citing rule Q01; `KROWN_RULES.csv:Q01`) |
| **krown** | `bbwp_mult` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:19` | `2.0` | `OURS` | Band multiplier not stated by trader (KR-Q01); percentile formula defined in `FORMULAS.md:21.5` |
| **krown** | `bbwp_high` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:20` | `85` | `SOURCED` | Rule KR-Q02: high volatility >= 85 (`KROWN_LAYER_SPEC.md:45`, citing rule Q02; `KROWN_RULES.csv:Q02`) |
| **krown** | `bbwp_low` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:21` | `30` | `OURS` | Rule KR-Q02 gives 25-35 range; 30 picked from grid `{25,30,35}` (`KROWN_LAYER_SPEC.md:45`) |
| **krown** | `bbwp_confirm` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:22` | `50` | `SOURCED` | Rule KR-Q02: break confirmed above the 50th percentile (`KROWN_LAYER_SPEC.md:45`, citing rule Q02; `KROWN_RULES.csv:Q02`) |
| **krown** | `hammer_wick` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:23` | `0.6` | `OURS` | Wick-to-range ratio for a big wick (KR-C03 gives none, `KROWN_LAYER_SPEC.md:46`) |
| **krown** | `hammer_close_pos` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:24` | `0.7` | `OURS` | Close in the top (hammer) or bottom (star) 30 % of the range (KR-C03 "closes strong", `KROWN_LAYER_SPEC.md:46`) |
| **krown** | `doji_body` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:25` | `0.1` | `OURS` | Body ratio for a doji (not stated in extracts, `KROWN_LAYER_SPEC.md:46`) |
| **krown** | `confirm_horizon` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:26` | `3` | `SOURCED` | Rule KR-C03: horizon 3-5 bars (lower end picked); KR-C08 close beyond pattern wick (`KROWN_LAYER_SPEC.md:46`) |
| **krown** | `crows_bars` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:27` | `3` | `SOURCED` | Rule KR-C11: "three down bars from the high" (`KROWN_LAYER_SPEC.md:46`, citing rule C11; `KROWN_RULES.csv:C11`) |
| **krown** | `ma_fast` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:28` | `21` | `SOURCED` | Rule KR-M01: 21 EMA (`KROWN_LAYER_SPEC.md:47`, citing rule M01; `KROWN_RULES.csv:M01`) |
| **krown** | `ma_slow` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:29` | `55` | `SOURCED` | Rule KR-M01: 55 EMA (`KROWN_LAYER_SPEC.md:47`, citing rule M01; `KROWN_RULES.csv:M01`) |
| **krown** | `ma_long` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:30` | `200` | `SOURCED` | Rule KR-M01 / KR-M07: 200 SMA (`KROWN_LAYER_SPEC.md:47`, citing rule M01/M07; `KROWN_RULES.csv:M01`) |
| **krown** | `ma_leash` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:31` | `5` | `SOURCED` | Rule KR-M06: 5 EMA (`KROWN_LAYER_SPEC.md:47`, citing rule M06; `KROWN_RULES.csv:M06`) |
| **krown** | `leash_n` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:32` | `3` | `SOURCED` | Rule KR-M06: "three closes without touching means you are late" (`KROWN_LAYER_SPEC.md:47`, citing rule M06; `KROWN_RULES.csv:M06`) |
| **krown** | `rsi_period` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:33` | `14` | `OURS` | Standard Wilder period; KR-S02 does not state the period (`KROWN_LAYER_SPEC.md:48`) |
| **krown** | `rsi_bull` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:34` | `60` | `SOURCED` | Rule KR-S03: downtrend RSI stays below 60; above 60 something else emerges (`KROWN_LAYER_SPEC.md:48`, citing rule S03; `KROWN_RULES.csv:S03`) |
| **krown** | `rsi_bear` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:35` | `40` | `SOURCED` | Rule KR-S03: uptrend RSI stays above 40 (`KROWN_LAYER_SPEC.md:48`, citing rule S03; `KROWN_RULES.csv:S03`) |
| **krown** | `macd_fast` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:36` | `12` | `OURS` | Standard fast EMA period; not stated by trader (`KROWN_LAYER_SPEC.md:48`) |
| **krown** | `macd_slow` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:37` | `26` | `OURS` | Standard slow EMA period; not stated by trader (`KROWN_LAYER_SPEC.md:48`) |
| **krown** | `macd_signal` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:38` | `9` | `OURS` | Standard signal EMA period; not stated by trader (`KROWN_LAYER_SPEC.md:48`) |
| **krown** | `range_n` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:39` | `20` | `OURS` | Range lookback window not stated in KR-R01 (`KROWN_LAYER_SPEC.md:49`) |
| **krown** | `range_width_max` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:40` | `0.25` | `OURS` | Max `(top-bottom)/mid` for a range; compression thresholds not stated (`KROWN_LAYER_SPEC.md:49`) |
| **krown** | `range_edge` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:41` | `0.2` | `OURS` | Edge band share of the range; KR-R01 says edges only, no width (`KROWN_LAYER_SPEC.md:49`) |
| **krown** | `coil_recent` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:42` | `5` | `OURS` | Bars in the coil window; not stated by trader (`KROWN_LAYER_SPEC.md:49`) |
| **krown** | `coil_max` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:43` | `0.7` | `OURS` | Coil score below this threshold indicates compression; repo choice (`KROWN_LAYER_SPEC.md:49`) |
| **krown** | `tops_window` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:44` | `3` | `OURS` | Proxy for "a few bars" (KR-P01), grid `{2,3,4}` (`KROWN_LAYER_SPEC.md:51`) |
| **krown** | `tops_need` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:45` | `3` | `SOURCED` | Rule KR-P01: "three of four" signals required (`KROWN_LAYER_SPEC.md:51`, citing rule P01; `KROWN_RULES.csv:P01`) |
| **krown** | `s1_vol_mult` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:46` | `2` | `SOURCED` | Rule KR-V02: volume >= 2x at the zone test (S1) (`KROWN_LAYER_SPEC.md:44,51`) |
| **krown** | `s2_vol_mult` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:47` | `1.0` | `OURS` | S2 volume above average; "discernible" threshold grid `{1.0, 1.25, 1.5}` (`KROWN_LAYER_SPEC.md:44`) |
| **krown** | `s8_recent` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:48` | `5` | `OURS` | Bars to look back for `BBWP <= low` (S8 setup rule proxy; `KROWN_LAYER_SPEC.md:45`) |
| **krown** | `s8_break_n` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:49` | `10` | `OURS` | Bars of range the S8 candle must break; repo choice |
| **krown** | `s7_vol_lookback` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:50` | `100` | `OURS` | "Biggest volume bar" window for S7 (KR-V07 gives none, `KROWN_LAYER_SPEC.md:44`) |
| **krown** | `DAY_MS` | `MyTradingSys/backtest/layers/krown/krown_context.py:20` | `86_400_000` | `SOURCED` | Standard milliseconds per day (86,400 * 1,000) |
| **krown** | `H4_MS` | `MyTradingSys/backtest/layers/krown/krown_context.py:21` | `14_400_000` | `SOURCED` | Standard milliseconds per 4-hour bar (4 * 3,600 * 1,000) |
| **krown** | `WEEK_MS` | `MyTradingSys/backtest/layers/krown/krown_context.py:22` | `604_800_000` | `SOURCED` | Standard milliseconds per 7-day week (7 * 86,400,000) |
| **krown** | `LATENCY_MS` | `MyTradingSys/backtest/layers/krown/krown_context.py:23` | `60_000` | `OURS` | Write latency buffer 1 min: `krown_context.py:23` citing `REVIEW_OPUS F17` |
| **krown** | `ATR_N` | `MyTradingSys/backtest/layers/krown/krown_context.py:24` | `14` | `OURS` | OURS period 14; plain SMA ATR calculation is SOURCED (`FORMULAS.md:324`) |
| **krown** | `SMA_LONG` | `MyTradingSys/backtest/layers/krown/krown_context.py:25` | `200` | `OURS` | Naive baseline benchmark window: `krown_context.py:25` citing `REVIEW_OPUS F12` |
| **krown** | `RET_N` | `MyTradingSys/backtest/layers/krown/krown_context.py:26` | `20` | `OURS` | Naive baseline benchmark window: `krown_context.py:26` citing `REVIEW_OPUS F12` |
| **krown** | `EXP_BASE` | `MyTradingSys/backtest/layers/krown/krown_context.py:27` | `50` | `OURS` | Expansion threshold: `krown_context.py:27` citing `REVIEW_OPUS F6 amendment` |
| **krown** | `FRESH_LOOKBACK` | `MyTradingSys/backtest/layers/krown/krown_context.py:28` | `6` | `OURS` | Fresh breakout window: `krown_context.py:28` citing design s3 D2 |
| **krown** | `FRESH_FROM` | `MyTradingSys/backtest/layers/krown/krown_context.py:29` | `30` | `OURS` | Matches bbwp_low (picked from 25-35 range) |
| **krown** | `FRESH_TO` | `MyTradingSys/backtest/layers/krown/krown_context.py:30` | `50` | `SOURCED` | Rule KR-Q02 bbwp_confirm 50 (`krown_params.json:22`) |
| **krown** | `Z_NEAR_ATR` | `MyTradingSys/backtest/layers/krown/krown_context.py:31` | `0.5` | `OURS` | Proximity threshold to zone: design s3 D3 |
| **krown** | `EDGE_FRAC` | `MyTradingSys/backtest/layers/krown/krown_context.py:32` | `0.2` | `OURS` | Range edge fraction: matches range_edge |
| **krown** | `MID_LO` | `MyTradingSys/backtest/layers/krown/krown_context.py:33` | `1.0 / 3` | `SOURCED` | Middle third lower bound of a daily range (design s3 D3) |
| **krown** | `MID_HI` | `MyTradingSys/backtest/layers/krown/krown_context.py:33` | `2.0 / 3` | `SOURCED` | Middle third upper bound of a daily range (design s3 D3) |
| **positioning** | `Funding lookback window` | `MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:70` | `90` | `OURS` | Undefined in source literature (Memon 2026); grid-searched IS only `{60, 90, 180}` (`FORMULAS.md:369`) |
| **positioning** | `CVD divergence lookback` | `MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:70` | `20` | `OURS` | CVD price divergence lookback window; grid `{20, 50}` (`FORMULAS.md:369`) |
| **positioning** | `High funding percentile threshold` | `MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:70` | `0.95` | `OURS` | Undefined in source literature; grid `{0.90, 0.95, 0.99}` (`FORMULAS.md:369`) |
| **positioning** | `Low funding percentile threshold` | `MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:71` | `0.05` | `OURS` | Undefined in source literature; grid `{0.01, 0.05, 0.10}` (`FORMULAS.md:369`) |
| **positioning** | `CVD divergence filter toggle` | `MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:71` | `True` | `OURS` | Supervisor merge decision (2026-09-29) combining funding extreme with CVD divergence fade (`FORMULAS.md:361`) |
| **positioning** | `Cumulative CVD bar delta formula` | `MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:48` | `2 * tbv - v` | `SOURCED` | Standard taker-buy trade volume delta: $\Delta = \text{TBV} - (\text{V} - \text{TBV}) = 2\text{TBV} - \text{V}$ (`FORMULAS.md:360`) |
| **positioning** | `fee_rt` (round-trip taker fee) | `MyTradingSys/backtest/layers/positioning/trade_costs.py:51` | `0.0010` (10 bps) | `SOURCED` | Binance USDT-M perpetual contract standard taker fee (`FORMULAS.md:345`) |
| **positioning** | `slip_rt` (round-trip slippage allowance) | `MyTradingSys/backtest/layers/positioning/trade_costs.py:51` | `0.0002` (2 bps) | `OURS` | Internal slippage hurdle from T055b "SCALPING FEE FLOOR" (`FORMULAS.md:345-347`) |
| **turn_of_candle** | `quarter period` | `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:3` | `15` | `SOURCED` | Shanaev, Vasenin, Stepanov, *Heliyon*, PMC10015199 (T1): returns concentrate at opening of 15-minute candles; `FORMULAS.md:16` |
| **turn_of_candle** | `minute ms divisor` | `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:3` | `60000` | `SOURCED` | Standard millisecond constant for 1 minute |
| **turn_of_candle** | `turn minute` | `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:36` | `0` | `SOURCED` | Shanaev et al. PMC10015199: candle opening minute (minutes 0, 15, 30, 45 of the hour) |
| **turn_of_candle** | `lead_minutes` | `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:59` | `1` | `OURS` | Lead time before candle open: `FORMULAS.md:16`: "at bars with `mq == 15 - lead_minutes`... enter just before candle opens" |
| **turn_of_candle** | `side` | `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:59` | `"long"` | `OURS` | Direction of effect is not stated in source paper; `FORMULAS.md:16`: "direction of the effect is NOT stated in the report, so both are grid-searched IS only" |

---

## 2. Unlabelled Constants Audit

- **Total unlabelled constants found**: `0`
- Every single constant and default value across all 5 specified modules (`wavetrend`, `rsi`, `krown`, `positioning`, `turn_of_candle`) has been identified, checked against analyst extracts/literature and architecture specifications, and labelled with full provenance.
- Constants where literature does not state a concrete parameter value are explicitly flagged as `OURS` (or noted as `NOT_IN_DATA` in original analyst literature) rather than left unlabelled or assumed.
