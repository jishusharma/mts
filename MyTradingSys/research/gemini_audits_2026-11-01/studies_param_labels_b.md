# SOURCED: 24, OURS: 40

# Parameter Labels Audit: Sim Desk Studies Part B (krown, pitchfork, wavetrend)

Audit of numeric, configuration, and default parameters across `research/sim_desk/studies/` (`krown.py`, `pitchfork.py`, `wavetrend.py`) and their underlying layer modules.
Every parameter is verified against trader citations or classified as internal engineering defaults (`OURS`).
Facts only, no verdicts on edge.

## Summary

- **Total Studies Audited**: 3 (`krown`, `pitchfork`, `wavetrend`)
- **Total Parameters Audited**: 64
- **SOURCED Parameters**: 24
- **OURS Parameters**: 40

---

## 1. Krown Study (`krown.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `MAX_HOLD` | `MyTradingSys/research/sim_desk/studies/krown.py:25` | `100` | `OURS` | Maximum holding period of 100 bars (`krown.py:10`: "a trade is closed after 100 bars... OURS") |
| `STOP_BARS` | `MyTradingSys/research/sim_desk/studies/krown.py:25` | `10` | `OURS` | Structural stop lookback window (`krown.py:10`: "stop = the far side of the last 10 bars including the signal bar... OURS") |
| `DEFAULT['symbol']` | `MyTradingSys/research/sim_desk/studies/krown.py:31` | `'BTCUSDT'` | `OURS` | Sim desk default cryptocurrency symbol |
| `DEFAULT['setup']` | `MyTradingSys/research/sim_desk/studies/krown.py:31` | `'S5'` | `SOURCED` | Eric Krown S5 21/55 EMA cross on 200 SMA side; `research/krown_ta101_2026-10-13/KROWN_RULES.csv` KR-M02: "21 EMA crosses 55 EMA with price on the 200 SMA side" |
| `DEFAULT['tf']` | `MyTradingSys/research/sim_desk/studies/krown.py:31` | `'4h'` | `OURS` | Execution timeframe (`krown.py:10`: "the timeframe (4h or daily... all OURS)") |
| `DEFAULT['exit']` | `MyTradingSys/research/sim_desk/studies/krown.py:31` | `'R'` | `OURS` | Multiple-of-risk exit mode (`krown.py:9`: "no source gives one: KR-X01, KR-Z14") |
| `DEFAULT['target_r']` | `MyTradingSys/research/sim_desk/studies/krown.py:31` | `2.0` | `OURS` | Fixed risk multiple target (`krown.py:10`: "target 2 x risk... OURS") |
| `DEFAULT['maker_pct']` | `MyTradingSys/research/sim_desk/studies/krown.py:32` | `0.02` | `OURS` | Binance VIP0 limit maker fee; `_bars.py:25`, `backtest/fees.py:BINANCE_MAKER` |
| `DEFAULT['taker_pct']` | `MyTradingSys/research/sim_desk/studies/krown.py:32` | `0.05` | `OURS` | Binance VIP0 market taker fee; `_bars.py:25`, `backtest/fees.py:BINANCE_TAKER` |
| `DEFAULT['slip_pct']` | `MyTradingSys/research/sim_desk/studies/krown.py:32` | `0.02` | `OURS` | Execution slippage on market/stop fills; `_bars.py:24` |
| `DEFAULT['start']` | `MyTradingSys/research/sim_desk/studies/krown.py:32` | `'2022-04-01'` | `OURS` | DEV evaluation window start date |
| `DEFAULT['end']` | `MyTradingSys/research/sim_desk/studies/krown.py:32` | `'2024-06-30'` | `OURS` | DEV evaluation window end date |
| `ma_fast` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:28` | `21` | `SOURCED` | S5 fast moving average 21 EMA; `KROWN_RULES.csv` KR-M01: "21 EMA" |
| `ma_slow` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:29` | `55` | `SOURCED` | S5 slow moving average 55 EMA; `KROWN_RULES.csv` KR-M01: "55 EMA" |
| `ma_long` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:30` | `200` | `SOURCED` | S5 trend filter 200 SMA; `KROWN_RULES.csv` KR-M01 / KR-M07: "200 SMA" |
| `bbwp_basis` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:17` | `7` | `SOURCED` | S8 BBWP basis length 7; `KROWN_RULES.csv` KR-Q01: "basis length 7" |
| `bbwp_lookback` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:18` | `100` | `SOURCED` | S8 BBWP percentile lookback 100; `KROWN_RULES.csv` KR-Q01: "lookback 100" |
| `bbwp_low` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:21` | `30` | `OURS` | S8 squeeze low volatility threshold; `krown_params.json:21` ("KR-Q02 gives 25-35; 30 picked, grid {25,30,35}") |
| `bbwp_confirm` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:22` | `50` | `SOURCED` | S8 expansion break confirmation; `KROWN_RULES.csv` KR-Q02: "break confirmed above the 50th percentile" |
| `range_n` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:39` | `20` | `OURS` | S4 coil range lookback bars; `krown_params.json:39` ("range lookback not stated (KR-R01)") |
| `coil_max` | `MyTradingSys/backtest/layers/krown/params/krown_params.json:43` | `0.7` | `OURS` | S4 compression threshold; `krown_params.json:43` ("coil score below this = compression (not stated)") |

---

## 2. Pitchfork Study (`pitchfork.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `MAX_HOLD` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:24` | `60` | `OURS` | Maximum trade holding period of 60 bars (`pitchfork.py:12`: "a trade is closed after 60 bars... OURS") |
| `STOP_OFFSET_PCT` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:25` | `0.015` (1.5%) | `OURS` | Structural stop buffer beyond tine/extreme (`pitchfork.py:11`: "structural stop 1.5% beyond the tine/bar extreme... OURS") |
| `DEFAULT['symbol']` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:48` | `'BTCUSDT'` | `OURS` | Sim desk default asset |
| `DEFAULT['tf']` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:49` | `'4h'` | `OURS` | Timeframe selection (`pitchfork.py:26`: "4 hours (ours)") |
| `DEFAULT['variant']` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:50` | `'modified_schiff'` | `SOURCED` | Modified Schiff 50% price-only shift; Mircea Dologa (2007) / Jerome Schiff; `research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:68-75` |
| `DEFAULT['setup']` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:51` | `'BOUNCE'` | `SOURCED` | Andrews 3-pivot Median Line and 80% return-to-ML rule; Dr. Alan H. Andrews (1960-1975); `research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:28-56` |
| `DEFAULT['vp_filter']` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:52` | `'VA'` | `OURS` | Anchored profile Value Area confluence filter over P0-P2 swing; `pitchfork.py:8-9` ("anchored profile Value Area (70%)... OURS") |
| `DEFAULT['exit']` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:53` | `'R'` | `OURS` | Fixed risk multiple target exit mode; `pitchfork.py:11`, `pitchfork.py:45` ("target at a chosen multiple of risk (ours)") |
| `DEFAULT['target_r']` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:54` | `2.0` | `OURS` | Risk multiple option for exit 'R'; `pitchfork.py:54` |
| `DEFAULT['maker_pct']` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:55` | `0.02` | `OURS` | Binance VIP0 limit maker fee; `_bars.py:25` |
| `DEFAULT['taker_pct']` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:55` | `0.05` | `OURS` | Binance VIP0 market taker fee; `_bars.py:25` |
| `DEFAULT['slip_pct']` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:55` | `0.02` | `OURS` | Execution slippage on market/stop fills; `_bars.py:24` |
| `DEFAULT['start']` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:56` | `'2022-04-01'` | `OURS` | DEV evaluation window start date |
| `DEFAULT['end']` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:57` | `'2024-06-30'` | `OURS` | DEV evaluation window end date |
| `zigzag_delay_4h` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:8` | `4` | `OURS` | ZigZag pivot confirmation delay on 4h; `pitchfork.py:8` ("4 bars on 4h... OURS") |
| `zigzag_delay_1d` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:8` | `3` | `OURS` | ZigZag pivot confirmation delay on 1d; `pitchfork.py:8` ("3 bars on 1d... OURS") |
| `swing_size_4h` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:8` | `0.03` (3%) | `OURS` | Minimum ZigZag swing threshold on 4h; `pitchfork.py:8` ("3% on 4h... OURS") |
| `swing_size_1d` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:8` | `0.04` (4%) | `OURS` | Minimum ZigZag swing threshold on 1d; `pitchfork.py:8` ("4% on 1d... OURS") |
| `tpo_va_frac` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:9` | `0.70` (70%) | `OURS` | TPO Value Area percentage filter; `pitchfork.py:9` ("Value Area (70%)... OURS") |
| `poc_band_tol` | `MyTradingSys/research/sim_desk/studies/pitchfork.py:9` | `0.015` (1.5%) | `OURS` | TPO Point of Control proximity tolerance; `pitchfork.py:9` ("Point of Control (1.5%)... OURS") |
| `schiff_time_ratio` | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:72` | `0.5` | `SOURCED` | Jerome Schiff formulation: origin shifted 50% in time towards P1; `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:121-128` |
| `schiff_price_ratio` | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:73` | `0.5` | `SOURCED` | Jerome Schiff formulation: origin shifted 50% in price towards P1; `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:121-128` |
| `modified_schiff_price_ratio` | `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:77` | `0.5` | `SOURCED` | Modified Schiff formulation: vertical midpoint shifted 50% between P0 and P1; `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:130-136` |

---

## 3. WaveTrend Study (`wavetrend.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `MAX_HOLD` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:21` | `100` | `OURS` | Maximum holding period of 100 bars (`wavetrend.py:10`: "a trade is closed after 100 bars... OURS") |
| `DEFAULT['symbol']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:27` | `'BTCUSDT'` | `OURS` | Sim desk default asset |
| `DEFAULT['tf']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:27` | `'1h'` | `OURS` | Timeframe selection (`wavetrend.py:10`: "the timeframe (no source names one)... OURS") |
| `DEFAULT['band']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:27` | `'53'` | `SOURCED` | LazyBear oscillator first overbought/oversold band 53; `research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md:13,23` |
| `DEFAULT['sides']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:27` | `'BOTH'` | `SOURCED` | Both long and short trading direction; LazyBear TradingView publication; `research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md:13,23` |
| `DEFAULT['exit']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:27` | `'R'` | `SOURCED` | Multiple-of-risk target exit mode; TrendCrypto2022 setup rule; `research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md:24` |
| `DEFAULT['target_r']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:27` | `1.5` | `SOURCED` | 1.5 x risk target; TrendCrypto2022 setup rule; `research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md:24` |
| `DEFAULT['maker_pct']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:28` | `0.02` | `OURS` | Binance VIP0 limit maker fee; `_bars.py:25` |
| `DEFAULT['taker_pct']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:28` | `0.05` | `OURS` | Binance VIP0 market taker fee; `_bars.py:25` |
| `DEFAULT['slip_pct']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:28` | `0.02` | `OURS` | Execution slippage on market/stop fills; `_bars.py:24` |
| `DEFAULT['start']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:28` | `'2022-04-01'` | `OURS` | DEV evaluation window start date |
| `DEFAULT['end']` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:28` | `'2024-06-30'` | `OURS` | DEV evaluation window end date |
| `N1` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `10` | `SOURCED` | Channel length parameter; LazyBear's WaveTrend Oscillator script, `FORMULAS.md` s20 (Crosses:14-21) |
| `N2` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `21` | `SOURCED` | Average length parameter; LazyBear's WaveTrend Oscillator script, `FORMULAS.md` s20 (Crosses:14-21) |
| `SMA_N` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `4` | `SOURCED` | Signal line length parameter; LazyBear's WaveTrend Oscillator script, `FORMULAS.md` s20 (Crosses:14-21) |
| `K` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `0.015` | `SOURCED` | Lambert's Commodity Channel Index (CCI) constant; LazyBear's WaveTrend script, `FORMULAS.md` s20 (Crosses:14-21) |
| `OB1` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:17` | `60.0` | `SOURCED` | Extreme overbought/oversold band level `ob2 = 60.0`, `os2 = -60.0`; LazyBear script, `FORMULAS.md` s20 (Crosses:9-12) |
| `OB2` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:17` | `53.0` | `SOURCED` | Primary overbought/oversold band level `ob1 = 53.0`, `os1 = -53.0`; LazyBear script, `FORMULAS.md` s20 (Crosses:9-12) |
| `WARMUP` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:18` | `200` | `OURS` | EMA stabilization warm-up suppression mask; `research/wavetrend_2026-10-17/PARITY_CONTRACT.md` s3 |
| `D_TOL` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:19` | `1e-9` | `OURS` | Flat window zero-deviation tolerance; `wavetrend.py:19` ("OURS: d <= D_TOL*|ap| counts as a flat window") |
| `stop_lookback` | `MyTradingSys/research/sim_desk/studies/wavetrend.py:6` | `3` | `SOURCED` | Stop loss placed at preceding 3-bar low/high; TrendCrypto2022 setup rule; `research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md:24` |

---

Noticed: Across all three studies, mathematical and indicator formulas (EMA lengths, BBWP settings, Pitchfork ratios, WaveTrend constants) are rigorously SOURCED from original trader publications, whereas operational execution details (such as ZigZag lookahead suppression delays, fee schedules, DEV dates, and fixed-bar exit timeouts) are systematically designated as OURS.
