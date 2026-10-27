UNLABELED count: 0

# Argon-medium: numeric parameter default labels for krown, wavetrend, and rsi (`file:line` sweep)

Date: 2026-10-27  
Card: `argon-med-param-label-sweep`  
Goal: Sweep the detector and study code of three layer families (`krown`, `wavetrend`, `rsi`) and list each numeric parameter default with its label (`SOURCED` with quote and file path, `OURS`, or `UNLABELED`), so the layer review can see what is borrowed and what is invented. Facts with `file:line` citations; no verdicts.

## Summary

- **Total numeric parameter default rows swept**: 115 (across detector modules, json parameter registries, and sim desk studies)
- **SOURCED count**: 52
- **OURS count**: 59
- **OPERATOR-HYPOTHESIS count**: 4 (in Kurisko stochastic/RSI candidate arms, explicitly non-trader hypotheses)
- **UNLABELED count**: 0

---

## 1. Sim Desk Studies (`MyTradingSys/research/sim_desk/studies/`)

### 1.1 Study: `studies/krown.py` (Krown desk study)

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `krown` | `MAX_HOLD` | `MyTradingSys/research/sim_desk/studies/krown.py:25` | `100` | OURS | Choice for desk simulation run; `krown.py:10-11` notes "a trade is closed after 100 bars... all OURS". |
| `krown` | `STOP_BARS` | `MyTradingSys/research/sim_desk/studies/krown.py:25` | `10` | OURS | Lookback for protective stop; `krown.py:9-10` notes "stop = the far side of the last 10 bars including the signal bar... all OURS". |
| `krown` | `DEFAULT['target_r']` | `MyTradingSys/research/sim_desk/studies/krown.py:31,52` | `2.0` | OURS | Risk multiple target; `krown.py:10` notes "target 2 x risk... all OURS". |

### 1.2 Study: `studies/wavetrend.py` (WaveTrend desk study)

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `wavetrend` | `MAX_HOLD` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:21` | `100` | OURS | Choice for desk simulation run; `wavetrend.py:9-10` notes "a trade is closed after 100 bars; the timeframe (no source names one)". |
| `wavetrend` | `DEFAULT['band']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:24,27` | `53` | SOURCED | Quote: `"obLevel2 = input(53, 'Over Bought Level 2') ... osLevel2 = input(-53, 'Over Sold Level 2')"` in `MyTradingSys/research/wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt:11-12`; `studies/wavetrend.py:4,24`. |
| `wavetrend` | `DEFAULT['target_r']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:27,37` | `1.5` | SOURCED | Quote: `"stop at the preceding three-bar low, target 1.5 times initial risk"` in `MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md:24` (TrendCrypto2022 BTC strategy); `studies/wavetrend.py:6-7`. |
| `wavetrend` | Stop lookback bars | `MyTradingSys/research/sim_desk/studies/wavetrend.py:101` | `3` | SOURCED | Quote: `"stop at the preceding three-bar low"` in `MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md:24` (TrendCrypto2022 BTC strategy); `studies/wavetrend.py:6-7,101`. |

### 1.3 Study: `studies/rsi.py` (RSI desk study)

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `rsi` | `PERIOD` | `MyTradingSys/research/sim_desk/studies/rsi.py:20,84` | `14` | OURS | Standard Wilder RSI period, but unquoted by practitioner Malkan; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:50` (audit R01: "Period: 14 (RSI 14) is a researcher bullet, no Malkan quote"). |
| `rsi` | `MAX_HOLD` | `MyTradingSys/research/sim_desk/studies/rsi.py:20,108` | `100` | OURS | Desk simulation hold limit; `studies/rsi.py:8` notes "a trade is closed after 100 bars (run_rsi_backtest.py MAX_BARS)". |
| `rsi` | `DEFAULT['target_r']` | `MyTradingSys/research/sim_desk/studies/rsi.py:25,34` | `2.0` | OURS | Fixed risk-multiple target; `studies/rsi.py:8` notes "a fixed-R target" is OURS. |
| `rsi` | `DEFAULT['tolerance']` | `MyTradingSys/research/sim_desk/studies/rsi.py:25,35` | `2.0` | OURS | RSI points tolerance around levels 40 and 60; `studies/rsi.py:7` notes "band around 40/60 (2 points) ... = the layer module's defaults" (OURS). |
| `rsi` | `DEFAULT['lookback']` | `MyTradingSys/research/sim_desk/studies/rsi.py:25,36` | `20` | OURS | Regime check window; `studies/rsi.py:7` notes "trend-check length (20 bars) = the layer module's defaults" (OURS). |
| `rsi` | Target level (long) | `MyTradingSys/research/sim_desk/studies/rsi.py:109` | `60` | SOURCED | Quote: `"Target is 60 RSI level on daily chart"` in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:128`; `studies/rsi.py:6`. |
| `rsi` | Target level (short) | `MyTradingSys/research/sim_desk/studies/rsi.py:109` | `40` | SOURCED | Quote: `"Target: RSI reaching 40 level"` in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:152`; `studies/rsi.py:6`. |

### 1.4 Shared Desk Parameters: `studies/_bars.py`

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| Shared | `SLIP_DEFAULT` | `MyTradingSys/research/sim_desk/studies/_bars.py:23` | `0.02` | OURS | Slippage against market and stop fills; `_bars.py:23` explicitly states `(ours)`. |
| Shared | `BINANCE_MAKER` | `MyTradingSys/backtest/fees.py:28` via `_bars.py:24` | `0.02` (0.0002) | SOURCED | Quote: `"Binance USDT-M perpetual, default tier. maker 0.0002 (4 bps RT)"` in `MyTradingSys/backtest/fees.py:12-14` (citing exchange schedule `T055b_PROVEN_SETUPS.md:22-23`). |
| Shared | `BINANCE_TAKER` | `MyTradingSys/backtest/fees.py:27` via `_bars.py:24` | `0.05` (0.0005) | SOURCED | Quote: `"Binance USDT-M perpetual, default tier. ... taker 0.0005 (10 bps RT)"` in `MyTradingSys/backtest/fees.py:12-14` (citing exchange schedule `T055b_PROVEN_SETUPS.md:22-23`). |

---

## 2. Family: `wavetrend` Layer Code and Specifications

### 2.1 Code Module: `MyTradingSys/backtest/layers/wavetrend/wavetrend.py`

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `wavetrend` | `N1` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `10` | SOURCED | Quote: `"n1 = input(10, 'Channel Length')"` in `MyTradingSys/research/wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt:14`; `PARITY_CONTRACT.md:18`; `FORMULAS.md:513`. |
| `wavetrend` | `N2` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `21` | SOURCED | Quote: `"n2 = input(21, 'Average Length')"` in `MyTradingSys/research/wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt:15`; `PARITY_CONTRACT.md:18`; `FORMULAS.md:513`. |
| `wavetrend` | `SMA_N` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `4` | SOURCED | Quote: `"wt2 = sma(wt1,4)"` in `MyTradingSys/research/wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt:21`; `PARITY_CONTRACT.md:18`; `FORMULAS.md:513`. |
| `wavetrend` | `K` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `0.015` | SOURCED | Quote: `"ci = (ap - esa) / (0.015 * d)"` in `MyTradingSys/research/wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt:18`; `PARITY_CONTRACT.md:18`; `FORMULAS.md:513`. |
| `wavetrend` | `OB1` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:17` | `60.0` | SOURCED | Quote: `"obLevel1 = input(60, 'Over Bought Level 1')"` in `MyTradingSys/research/wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt:9`; `PARITY_CONTRACT.md:18`; `FORMULAS.md:511`. |
| `wavetrend` | `OB2` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:17` | `53.0` | SOURCED | Quote: `"obLevel2 = input(53, 'Over Bought Level 2')"` in `MyTradingSys/research/wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt:11`; `PARITY_CONTRACT.md:18`; `FORMULAS.md:511`. |
| `wavetrend` | `WARMUP` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:18` | `200` | OURS | Startup bar suppression; `PARITY_CONTRACT.md:23` notes "output is used only after WARMUP = 200 bars from series start or from any gap (OURS)". |
| `wavetrend` | `D_TOL` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:19` | `1e-9` | OURS | Tolerance for flat series zero division; `PARITY_CONTRACT.md:24` notes "ci = NaN when d <= 1e-9*abs(ap) (OURS tolerance)". |

---

## 3. Family: `rsi` Layer Code and Specifications

### 3.1 Code Module: `MyTradingSys/backtest/layers/rsi/rsi_core.py`

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `rsi` | `rsi_core(period)` | `MyTradingSys/backtest/layers/rsi/rsi_core.py:7` | `14` | OURS | Standard Wilder RSI period, but unquoted by practitioner Malkan; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:50` (audit R01: "Period: 14 (RSI 14) is a researcher bullet, no Malkan quote"). |

### 3.2 Code Module: `MyTradingSys/backtest/layers/rsi/malkan_40_60.py`

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `rsi` | `malkan_regime(lo)` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:24` | `40.0` | SOURCED | Quote: `"When the market is bearish, it won't be able to cross 60, and whenever in a bullish trend, it won't be able to cross 40."` in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:45`; `LAYER_PROVENANCE_AUDIT.md:57` (audit R08). |
| `rsi` | `malkan_regime(hi)` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:24` | `60.0` | SOURCED | Quote: `"When the market is bearish, it won't be able to cross 60, and whenever in a bullish trend, it won't be able to cross 40."` in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:45`; `LAYER_PROVENANCE_AUDIT.md:58` (audit R09). |
| `rsi` | `malkan_regime(lookback)` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:24` | `20` | OURS | Regime evaluation window; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:60` (audit R11: "Regime lookback 20 bars - (no window in WR) CONCEPT-ONLY"). |
| `rsi` | `malkan_setup_bull(level)` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:64` | `40.0` | SOURCED | Quote: `"Bullish candlestick forms at 40 RSI level on daily chart = buy signal"` in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:120`; `malkan_40_60.py:8`. |
| `rsi` | `malkan_setup_bull(tolerance)` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:64` | `2.0` | OURS | Band tolerance around level; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:61` (audit R12: "Band tolerance around 40/60 2.0 RSI pts WR:116 'at or near Daily RSI 40' (bullet)"). |
| `rsi` | `malkan_setup_bear(level)` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:107` | `60.0` | SOURCED | Quote: `"Bearish candlestick forms at 60 RSI level on daily chart = short signal"` in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:144`; `malkan_40_60.py:9`. |
| `rsi` | `malkan_setup_bear(tolerance)` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:107` | `2.0` | OURS | Band tolerance around level; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:61` (audit R12: "Band tolerance around 40/60 2.0 RSI pts WR:116 'at or near Daily RSI 40' (bullet)"). |

### 3.3 Code Module: `MyTradingSys/backtest/layers/rsi/rsi_ma.py`

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `rsi` | `rsi_ma(length)` | `MyTradingSys/backtest/layers/rsi/rsi_ma.py:8` | `14` | OURS | Smoothing line length; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:51` (audit R02: "no Malkan text mentions an RSI MA... default.json:3 'source': 'operator'"). |

### 3.4 Code Module: `MyTradingSys/backtest/layers/rsi/rsi_divergence.py`

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `rsi` | `rsi_divergence(min_rsi_diff)` | `MyTradingSys/backtest/layers/rsi/rsi_divergence.py:33` | `0.0` | SOURCED | Quote: `"Sometimes there is divergence in decimals and that will also be acceptable."` in `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:10` citing Malkan transcript extracts `extract_Wvq1TZh8aF0.md` / `extract_cQ-y1oULkBw.md`. |

### 3.5 Parameter Files: `MyTradingSys/backtest/layers/rsi/params/`

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `rsi` | `default.json -> rsi_core.period` | `MyTradingSys/backtest/layers/rsi/params/default.json:7` | `14` | OURS | `default.json:3` notes `"source": "operator"`; `LAYER_PROVENANCE_AUDIT.md:50`. |
| `rsi` | `default.json -> rsi_ma.length` | `MyTradingSys/backtest/layers/rsi/params/default.json:11` | `14` | OURS | `default.json:3` notes `"source": "operator"`; `LAYER_PROVENANCE_AUDIT.md:51`. |
| `rsi` | `default.json -> rsi_events.levels` | `MyTradingSys/backtest/layers/rsi/params/default.json:14` | `[70, 50, 30]` | OURS | Standard generic reading levels chosen by operator; `LAYER_PROVENANCE_AUDIT.md:52` (audit R03). |
| `rsi` | `default.json -> rsi_events.tolerance` | `MyTradingSys/backtest/layers/rsi/params/default.json:15` | `0` | OURS | Chosen by operator; `LAYER_PROVENANCE_AUDIT.md:53` (audit R04). |
| `rsi` | `malkan_40_60_default.json -> rsi_core.period` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:7` | `14` | OURS | Researcher bullet, no Malkan quote; `LAYER_PROVENANCE_AUDIT.md:50`. |
| `rsi` | `malkan_40_60_default.json -> malkan_40_60.lo` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:10` | `40` | SOURCED | Quote: `"When the market is bearish, it won't be able to cross 60, and whenever in a bullish trend, it won't be able to cross 40."` in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:45`. |
| `rsi` | `malkan_40_60_default.json -> malkan_40_60.hi` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:11` | `60` | SOURCED | Quote: `"When the market is bearish, it won't be able to cross 60, and whenever in a bullish trend, it won't be able to cross 40."` in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:45`. |
| `rsi` | `malkan_40_60_default.json -> malkan_40_60.regime_lookback` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:12` | `20` | OURS | Regime lookback window; `LAYER_PROVENANCE_AUDIT.md:60` (audit R11). |
| `rsi` | `malkan_40_60_default.json -> malkan_40_60.event_tolerance` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:13` | `2` | OURS | Tolerance band around levels; `LAYER_PROVENANCE_AUDIT.md:61` (audit R12). |
| `rsi` | `malkan_divergence_default.json -> min_bars` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:4` | `3` | SOURCED | Quote: `"How many candles are needed? Three."` in `malkan_divergence_default.json:6` citing `extract_Wvq1TZh8aF0.md:D1-D4`. |
| `rsi` | `malkan_divergence_default.json -> max_bars` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:5` | `10` | SOURCED | Quote: `"It should be between three and 10."` in `malkan_divergence_default.json:7` citing `extract_Wvq1TZh8aF0.md:D1-D4`. |
| `rsi` | `malkan_divergence_default.json -> min_rsi_diff` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:9` | `0.0` | SOURCED | Quote: `"Sometimes there is divergence in decimals and that will also be acceptable."` in `malkan_divergence_default.json:10` citing `extract_cQ-y1oULkBw.md:D1-D2`. |

### 3.6 Kurisko Stochastic / RSI Candidate Layer: `kurisko_default.json` (`layer_index.json:232-244`)

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `rsi` / Kurisko | `bands[0]` | `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:5` | `[9, 3]` | SOURCED | Quote: `"Deep dive on stochastics (9-3, 14-3, 44, 60-10)"` in `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:29,43` (citing S3/S4). |
| `rsi` / Kurisko | `bands[1]` | `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:5` | `[14, 3]` | SOURCED | Quote: `"Deep dive on stochastics (9-3, 14-3, 44, 60-10)"` in `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:29,44` (citing S3/S4). |
| `rsi` / Kurisko | `bands[2]` | `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:5` | `[40, 4]` | SOURCED | Quote: `"Fast Stoch (40,4)"` on slide S4 and spoken `"40 candles"` (char 21291) in `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:30,45`. |
| `rsi` / Kurisko | `bands[3]` | `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:5` | `[60, 10]` | SOURCED | Quote: `"These are 40 candles and these are 60 candles"` (char 21291) and `"6010 is the five minute time frame"` in `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:46`. |
| `rsi` / Kurisko | `level_lo` | `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:7` | `20` | SOURCED | Quote: `"all of these bands get oversold below 20"` (char 20846) in `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:41,47` (rule R2). |
| `rsi` / Kurisko | `level_hi` | `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:8` | `80` | SOURCED | Quote: `"Oversold < 20, overbought > 80"` in `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:47` (citing S4, S2). |
| `rsi` / Kurisko | `rsi_bands[0]` | `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:11` | `[9, 0]` | OPERATOR-HYPOTHESIS | Quote: `"4 RSI with params stays NO-SOURCE... 'RSI' occurs 0 times in S8"` in `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:15,66`. |
| `rsi` / Kurisko | `rsi_bands[1]` | `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:11` | `[14, 0]` | OPERATOR-HYPOTHESIS | Quote: `"4 RSI with params stays NO-SOURCE... 'RSI' occurs 0 times in S8"` in `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:15,66`. |
| `rsi` / Kurisko | `rsi_bands[2]` | `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:11` | `[40, 0]` | OPERATOR-HYPOTHESIS | Quote: `"4 RSI with params stays NO-SOURCE... 'RSI' occurs 0 times in S8"` in `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:15,66`. |
| `rsi` / Kurisko | `rsi_bands[3]` | `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:11` | `[60, 0]` | OPERATOR-HYPOTHESIS | Quote: `"4 RSI with params stays NO-SOURCE... 'RSI' occurs 0 times in S8"` in `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:15,66`. |

---

## 4. Family: `krown` Layer Code and Specifications

### 4.1 Parameter File: `MyTradingSys/backtest/layers/krown/params/krown_params.json`

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `krown` | `zone_k` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:5` | `3` | OURS | Quote: `"bars each side of a swing; KR-L01 gives no number, grid {2,3,5}"` in `krown_params.json:5`; `KROWN_LAYER_SPEC.md:42`. |
| `krown` | `zone_min_turns` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:6` | `2` | SOURCED | Quote: `"one touch is an event, two is a memory"` (rule KR-Z02) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:6`. |
| `krown` | `zone_lookback` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:7` | `250` | OURS | Quote: `"pivots older than this many bars are not ranked (KR-Z18 'recent' is not defined)"` in `krown_params.json:7`. |
| `krown` | `zone_max` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:8` | `5` | SOURCED | Quote: `"at most 3 to 5 zones"` (rule KR-Z03) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:8`. |
| `krown` | `zone_mature_tests` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:9` | `3` | SOURCED | Quote: `"beyond three tests the break probability is higher"` (rule KR-Z13) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:9`. |
| `krown` | `swing_tol` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:10` | `0.01` | OURS | Quote: `"'about the same' range tolerance (KR-L10 gives no number)"` in `krown_params.json:10`; `FORMULAS.md:535`. |
| `krown` | `vol_sma` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:11` | `20` | SOURCED | Quote: `"Put a simple moving average with a 20-period lookback on the volume bars"` (rule KR-V01) in `MyTradingSys/research/krown_ta101_2026-10-13/tools/build_ledger.py:189` and `krown_params.json:11`. |
| `krown` | `vol_mult` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:12` | `2` | SOURCED | Quote: `"two or more times the average"` (rule KR-V02) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:12`. |
| `krown` | `vol_half` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:13` | `0.5` | SOURCED | Quote: `"observation: volume near 50 % of average before a breakout"` (rule KR-V10) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:13`. |
| `krown` | `vol_slots` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:14` | `7` | OURS | Quote: `"same-slot baseline arm: weekday slot for 1d (spec C5/C10)"` in `krown_params.json:14`. |
| `krown` | `vol_slot_prev` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:15` | `8` | OURS | Quote: `"same-slot baseline arm: previous weeks averaged"` in `krown_params.json:15`. |
| `tops_vol_sma` | `tops_vol_sma` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:16` | `30` | SOURCED | Quote: `"30-day average in the tops framework"` (rule KR-V02 / TOP-05) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:16`. |
| `krown` | `bbwp_basis` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:17` | `7` | SOURCED | Quote: `"basis moving average length 7, lookback 100"` (rule KR-Q01) in `MyTradingSys/research/krown_ta101_2026-10-13/tools/build_ledger.py:441` and `krown_params.json:17`. |
| `krown` | `bbwp_lookback` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:18` | `100` | SOURCED | Quote: `"basis moving average length 7, lookback 100"` (rule KR-Q01) in `MyTradingSys/research/krown_ta101_2026-10-13/tools/build_ledger.py:441` and `krown_params.json:18`. |
| `krown` | `bbwp_mult` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:19` | `2.0` | OURS | Quote: `"band multiplier not stated (KR-Q01); percentile formula defined in FORMULAS.md 21.5"` in `krown_params.json:19`. |
| `krown` | `bbwp_high` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:20` | `85` | SOURCED | Quote: `"high volatility >= 85"` (rule KR-Q02) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:20`. |
| `krown` | `bbwp_low` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:21` | `30` | OURS | Quote: `"KR-Q02 gives 25-35; 30 picked, grid {25,30,35}"` in `krown_params.json:21`. |
| `krown` | `bbwp_confirm` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:22` | `50` | SOURCED | Quote: `"break confirmed above the 50th percentile"` (rule KR-Q02) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:22`. |
| `krown` | `hammer_wick` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:23` | `0.6` | OURS | Quote: `"wick-to-range ratio for a big wick (KR-C03 gives none)"` in `krown_params.json:23`. |
| `krown` | `hammer_close_pos` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:24` | `0.7` | OURS | Quote: `"close in the top (hammer) or bottom (star) 30 % of the range (KR-C03 'closes strong')"` in `krown_params.json:24`. |
| `krown` | `doji_body` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:25` | `0.1` | OURS | Quote: `"body ratio for a doji (not stated)"` in `krown_params.json:25`. |
| `krown` | `confirm_horizon` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:26` | `3` | SOURCED | Quote: `"horizon 3-5 bars (lower end); KR-C08 close beyond the pattern wick"` (rule KR-C03 / KR-C08) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:26`. |
| `krown` | `crows_bars` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:27` | `3` | SOURCED | Quote: `"three down bars from the high"` (rule KR-C11) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:27`. |
| `krown` | `ma_fast` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:28` | `21` | SOURCED | Quote: `"21 EMA"` (rule KR-M01) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:28`. |
| `krown` | `ma_slow` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:29` | `55` | SOURCED | Quote: `"55 EMA"` (rule KR-M01) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:29`. |
| `krown` | `ma_long` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:30` | `200` | SOURCED | Quote: `"200 SMA"` (rule KR-M01 / KR-M07) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:30`. |
| `krown` | `ma_leash` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:31` | `5` | SOURCED | Quote: `"5 EMA"` (rule KR-M06) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:31`. |
| `krown` | `leash_n` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:32` | `3` | SOURCED | Quote: `"three closes without touching means you are late"` (rule KR-M06) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:32`. |
| `krown` | `rsi_period` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:33` | `14` | OURS | Quote: `"KR-S02 does not state the period"` in `krown_params.json:33`. |
| `krown` | `rsi_bull` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:34` | `60` | SOURCED | Quote: `"downtrend RSI stays below 60; above 60 something else emerges"` (rule KR-S03) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:34`. |
| `krown` | `rsi_bear` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:35` | `40` | SOURCED | Quote: `"uptrend RSI stays above 40"` (rule KR-S03) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:35`. |
| `krown` | `macd_fast` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:36` | `12` | OURS | Quote: `"MACD periods not stated (KR-P01 names the cross only)"` in `krown_params.json:36`. |
| `krown` | `macd_slow` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:37` | `26` | OURS | Quote: `"MACD periods not stated (KR-P01)"` in `krown_params.json:37`. |
| `krown` | `macd_signal` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:38` | `9` | OURS | Quote: `"MACD periods not stated (KR-P01)"` in `krown_params.json:38`. |
| `krown` | `range_n` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:39` | `20` | OURS | Quote: `"range lookback not stated (KR-R01)"` in `krown_params.json:39`. |
| `krown` | `range_width_max` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:40` | `0.25` | OURS | Quote: `"max (top-bottom)/mid for a range; compression thresholds not stated"` in `krown_params.json:40`. |
| `krown` | `range_edge` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:41` | `0.2` | OURS | Quote: `"edge band share of the range; KR-R01 says edges only, no width"` in `krown_params.json:41`. |
| `krown` | `coil_recent` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:42` | `5` | OURS | Quote: `"bars in the coil window (not stated)"` in `krown_params.json:42`. |
| `krown` | `coil_max` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:43` | `0.7` | OURS | Quote: `"coil score below this = compression (not stated)"` in `krown_params.json:43`. |
| `krown` | `tops_window` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:44` | `3` | OURS | Quote: `"'a few bars' (KR-P01), grid {2,3,4}"` in `krown_params.json:44`. |
| `krown` | `tops_need` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:45` | `3` | SOURCED | Quote: `"three of four"` (rule KR-P01) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:45`. |
| `krown` | `s1_vol_mult` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:46` | `2` | SOURCED | Quote: `"volume >= 2x at the zone test (S1)"` (rule KR-V02) in `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv` and `krown_params.json:46`. |
| `krown` | `s2_vol_mult` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:47` | `1.0` | OURS | Quote: `"S2 volume above average (spec); 'discernible' threshold grid {1.0,1.25,1.5}"` in `krown_params.json:47`. |
| `krown` | `s8_recent` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:48` | `5` | OURS | Quote: `"bars to look back for BBWP <= low (S8)"` in `krown_params.json:48`. |
| `krown` | `s8_break_n` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:49` | `10` | OURS | Quote: `"bars of range the S8 candle must break (not stated)"` in `krown_params.json:49`. |
| `krown` | `s7_vol_lookback` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:50` | `100` | OURS | Quote: `"'biggest volume bar' window for S7 (KR-V07 gives none)"` in `krown_params.json:50`. |

### 4.2 Code Module: `MyTradingSys/backtest/layers/krown/krown_context.py`

| Family | Parameter / Constant | File:Line | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `krown` | `LATENCY_MS` | `MyTradingSys/backtest/layers/krown/krown_context.py:25` | `60000` | OURS | Execution pipeline write latency assumption; `krown_context.py:25` notes `OURS: REVIEW_OPUS F17 (write latency 1 min)`. |
| `krown` | `ATR_N` | `MyTradingSys/backtest/layers/krown/krown_context.py:26` | `14` | OURS | ATR period length; `krown_context.py:26` notes `OURS period; plain SMA ATR is SOURCED (FORMULAS.md:324, operator decision 2026-09-28)`. |
| `krown` | `SMA_LONG` | `MyTradingSys/backtest/layers/krown/krown_context.py:27` | `200` | OURS | Naive baseline parameter; `krown_context.py:27` notes `OURS naive baseline (REVIEW_OPUS F12)`. |
| `krown` | `RET_N` | `MyTradingSys/backtest/layers/krown/krown_context.py:28` | `20` | OURS | Naive baseline parameter; `krown_context.py:28` notes `OURS naive baseline (REVIEW_OPUS F12)`. |
| `krown` | `EXP_BASE` | `MyTradingSys/backtest/layers/krown/krown_context.py:29` | `50` | OURS | Baseline threshold; `krown_context.py:29` notes `OURS (REVIEW_OPUS F6 amendment: "BBWP_4h last <= 50"; PRE_REG_CONFLUENCE s0.1)`. |
| `krown` | `FRESH_LOOKBACK` | `MyTradingSys/backtest/layers/krown/krown_context.py:30` | `6` | OURS | Recency window; `krown_context.py:30` notes `OURS (design s3 D2: "rose from <= 30 within 6 bars")`. |
| `krown` | `FRESH_FROM` | `MyTradingSys/backtest/layers/krown/krown_context.py:31` | `30` | OURS | Recency start bound; `krown_context.py:31` notes `OURS (= bbwp_low)`. |
| `krown` | `FRESH_TO` | `MyTradingSys/backtest/layers/krown/krown_context.py:32` | `50` | SOURCED | Quote: `"break confirmed above the 50th percentile"` (rule KR-Q02) in `krown_context.py:32` citing `krown_params bbwp_confirm 50`. |
| `krown` | `Z_NEAR_ATR` | `MyTradingSys/backtest/layers/krown/krown_context.py:33` | `0.5` | OURS | Proximity tolerance in ATR units; `krown_context.py:33` notes `OURS default (design s3 D3)`. |
| `krown` | `EDGE_FRAC` | `MyTradingSys/backtest/layers/krown/krown_context.py:34` | `0.2` | OURS | Edge fraction of range; `krown_context.py:34` notes `OURS = params range_edge`. |
| `krown` | `MID_LO` | `MyTradingSys/backtest/layers/krown/krown_context.py:35` | `0.333333` | OURS | Middle range lower bound; `krown_context.py:35` notes `1.0 / 3 ... "middle third of a daily range" (design s3 D3)`. |
| `krown` | `MID_HI` | `MyTradingSys/backtest/layers/krown/krown_context.py:35` | `0.666667` | OURS | Middle range upper bound; `krown_context.py:35` notes `2.0 / 3 ... "middle third of a daily range" (design s3 D3)`. |

## Claude review 2026-10-27 (JIS-DESKTOP session, independent recount)
- Table rows recounted: 115; labels 52 SOURCED / 59 OURS / 4 OPERATOR-HYPOTHESIS / 0 UNLABELED: matches the header.
- file:line check: 112 of 115 cited code locations contain the named parameter within 3 lines. N1, N2, SMA_N, K cite wavetrend.py:16; they sit on line 15 (off by one).
- Quoted Pine lines exist in the source snapshot, but the cited line numbers are wrong (n1/n2 are lines 7/8, cited 14/15). Use the quotes, re-find the line numbers before relying on them. Trust stays UNCHECKED beyond this spot-check.
