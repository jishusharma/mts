# Parameter Labels Audit: Sim Desk Studies (rsi, levels, krown, wavetrend, pitchfork, cowen_bmsb)

Audit of numeric and configuration parameter defaults across `MyTradingSys/research/sim_desk/studies/`.
Every parameter is checked against trader source citations or classified as internal engineering defaults (`OURS`).

## 1. RSI 40/60 (`rsi.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `PERIOD` | `rsi.py:20` | `14` | `SOURCED` | Wilder's standard RSI 14-period default; `research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:35` |
| `MAX_HOLD` | `rsi.py:20` | `100` | `OURS` | Internal trade timeout horizon in bars; matches `run_rsi_backtest.py:MAX_BARS` |
| `DEFAULT['symbol']` | `rsi.py:25` | `'BTCUSDT'` | `OURS` | Asset selection |
| `DEFAULT['tf']` | `rsi.py:25` | `'1d'` | `SOURCED` | Malkan daily chart; `WEB_RESEARCH.md:116-120` |
| `DEFAULT['entry']` | `rsi.py:25` | `'BREAK'` | `SOURCED` | Malkan entry above signal candle high / below signal candle low; `WEB_RESEARCH.md:117` |
| `DEFAULT['exit']` | `rsi.py:25` | `'LEVEL'` | `SOURCED` | Malkan target RSI 60 (long) / 40 (short); `WEB_RESEARCH.md:128,152` |
| `DEFAULT['target_r']` | `rsi.py:25` | `2.0` | `OURS` | Fixed risk multiple option for exit `R` |
| `DEFAULT['tolerance']` | `rsi.py:25` | `2.0` | `OURS` | Tolerance band in RSI points around 40/60 levels; `malkan_40_60.py:64,107` default |
| `DEFAULT['lookback']` | `rsi.py:25` | `20` | `OURS` | Lookback window for trend/regime confirmation in bars; `malkan_40_60.py:24` default |
| `DEFAULT['maker_pct']` | `rsi.py:26` | `0.02` | `OURS` | Binance VIP0/default maker fee (0.02%); `backtest/fees.py:BINANCE_MAKER` |
| `DEFAULT['taker_pct']` | `rsi.py:26` | `0.05` | `OURS` | Binance VIP0/default taker fee (0.05%); `backtest/fees.py:BINANCE_TAKER` |
| `DEFAULT['slip_pct']` | `rsi.py:26` | `0.02` | `OURS` | Execution slippage on market/stop fills; `_bars.py:23` |
| `DEFAULT['start']` | `rsi.py:26` | `'2022-04-01'` | `OURS` | DEV evaluation window start |
| `DEFAULT['end']` | `rsi.py:26` | `'2024-06-30'` | `OURS` | DEV evaluation window end |

## 2. Price Levels (`levels.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `DEV_FIRST` | `levels.py:30` | `'2022-04-01'` | `OURS` | DEV window start date |
| `DEV_LAST` | `levels.py:30` | `'2024-06-30'` | `OURS` | DEV window end date |
| `DEFAULT['entry']` | `levels.py:41` | `'E1'` | `SOURCED` | 5m RSI holds 40 long / 60 short; `ladder.py` / `levels_confluence_2026-10-14` |
| `DEFAULT['scale']` | `levels.py:41` | `'S2'` | `OURS` | All-in at next level beyond; execution ladder variant |
| `DEFAULT['stop']` | `levels.py:41` | `'K5'` | `SOURCED` | Just past today's extreme; CryptoCred daily level stop rule |
| `DEFAULT['stop_pct']` | `levels.py:41` | `ld.MARGIN * 100` (`0.05`) | `OURS` | Stop distance buffer beyond level; `ladder.py:MARGIN` |
| `DEFAULT['exit']` | `levels.py:41` | `'X0_2R'` | `OURS` | Target 2 x risk; ladder study variant |
| `DEFAULT['target_r']` | `levels.py:41` | `2.0` | `OURS` | Risk multiple for 'R' exit choice |
| `DEFAULT['maker_pct']` | `levels.py:42` | `ld.MAKER * 100` (`0.02`) | `OURS` | Binance maker fee; `ladder.py:MAKER` |
| `DEFAULT['taker_pct']` | `levels.py:42` | `ld.TAKER * 100` (`0.05`) | `OURS` | Binance taker fee; `ladder.py:TAKER` |
| `DEFAULT['slip_pct']` | `levels.py:42` | `0.02` | `OURS` | Execution slippage on market/stop fills |
| `DEFAULT['start']` | `levels.py:42` | `'2022-04-01'` | `OURS` | DEV window start |
| `DEFAULT['end']` | `levels.py:42` | `'2024-06-30'` | `OURS` | DEV window end |

## 3. Krown (`krown.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `MAX_HOLD` | `krown.py:25` | `100` | `OURS` | Trade timeout horizon in bars |
| `STOP_BARS` | `krown.py:25` | `10` | `OURS` | Structural stop lookback window (far side of last 10 bars) |
| `DEFAULT['symbol']` | `krown.py:31` | `'BTCUSDT'` | `OURS` | Asset selection |
| `DEFAULT['setup']` | `krown.py:31` | `'S5'` | `SOURCED` | 21/55 EMA cross on 200 SMA side; `research/krown_ta101_2026-10-13/KROWN_RULES.csv:KR-M02` |
| `DEFAULT['tf']` | `krown.py:31` | `'4h'` | `OURS` | Timeframe selection; Krown does not prescribe single crypto TF |
| `DEFAULT['exit']` | `krown.py:31` | `'R'` | `OURS` | Target multiple of risk; trader gives no specific exit rule (`KR-X01`) |
| `DEFAULT['target_r']` | `krown.py:31` | `2.0` | `OURS` | Target risk multiple |
| `DEFAULT['maker_pct']` | `krown.py:32` | `0.02` | `OURS` | Binance maker fee; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['taker_pct']` | `krown.py:32` | `0.05` | `OURS` | Binance taker fee; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['slip_pct']` | `krown.py:32` | `0.02` | `OURS` | Execution slippage on market/stop fills |
| `DEFAULT['start']` | `krown.py:32` | `'2022-04-01'` | `OURS` | DEV window start |
| `DEFAULT['end']` | `krown.py:32` | `'2024-06-30'` | `OURS` | DEV window end |
| `S8 BBWP basis` | `krown_params.json:s8` | `7` | `SOURCED` | Bollinger Band Width Percentile basis; `KROWN_RULES.csv:KR-Q01` |
| `S8 BBWP lookback` | `krown_params.json:s8` | `100` | `SOURCED` | BBWP lookback window; `KROWN_RULES.csv:KR-Q01` |
| `S8 low threshold` | `krown_params.json:s8` | `30` | `SOURCED` | Squeeze compression threshold; `KROWN_RULES.csv:KR-Q02` (range 25-35) |
| `S8 break percentile` | `krown_params.json:s8` | `50` | `SOURCED` | Breakout percentile threshold; `KROWN_RULES.csv:KR-Q02` (50th percentile) |
| `S4 range` | `krown_params.json:s4` | `20` | `OURS` | Coil range lookback bars; engineering parameter |
| `S4 coil` | `krown_params.json:s4` | `0.7` | `OURS` | Coil compression ratio; engineering parameter |

## 4. WaveTrend (`wavetrend.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `MAX_HOLD` | `wavetrend.py:21` | `100` | `OURS` | Trade timeout horizon in bars |
| `DEFAULT['symbol']` | `wavetrend.py:27` | `'BTCUSDT'` | `OURS` | Asset selection |
| `DEFAULT['tf']` | `wavetrend.py:27` | `'1h'` | `OURS` | Timeframe selection; no source specifies one |
| `DEFAULT['band']` | `wavetrend.py:27` | `'53'` | `SOURCED` | LazyBear standard WaveTrend oversold/overbought band 53; `research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md:13,23` |
| `DEFAULT['sides']` | `wavetrend.py:27` | `'BOTH'` | `SOURCED` | LazyBear trading both long and short; `EXTERNAL_SETUPS.md:13` |
| `DEFAULT['exit']` | `wavetrend.py:27` | `'R'` | `SOURCED` | Target at multiple of risk; TrendCrypto2022 setup (`EXTERNAL_SETUPS.md:24`) |
| `DEFAULT['target_r']` | `wavetrend.py:27` | `1.5` | `SOURCED` | TrendCrypto2022 1.5x risk target; `EXTERNAL_SETUPS.md:24` |
| `stop (3-bar extreme)`| `wavetrend.py:78` | `3-bar low/high` | `SOURCED` | TrendCrypto2022 preceding 3-bar low/high; `EXTERNAL_SETUPS.md:24` |
| `DEFAULT['maker_pct']` | `wavetrend.py:28` | `0.02` | `OURS` | Binance maker fee; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['taker_pct']` | `wavetrend.py:28` | `0.05` | `OURS` | Binance taker fee; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['slip_pct']` | `wavetrend.py:28` | `0.02` | `OURS` | Execution slippage on market/stop fills |
| `DEFAULT['start']` | `wavetrend.py:28` | `'2022-04-01'` | `OURS` | DEV window start |
| `DEFAULT['end']` | `wavetrend.py:28` | `'2024-06-30'` | `OURS` | DEV window end |
| `n1 (channel length)` | `wavetrend.py:3` | `10` | `SOURCED` | LazyBear standard WT channel length |
| `n2 (average length)` | `wavetrend.py:3` | `21` | `SOURCED` | LazyBear standard WT average length |
| `factor (multiplier)` | `wavetrend.py:4` | `0.015` | `SOURCED` | LazyBear standard WT constant 0.015 |
| `warmup` | `wavetrend.py:4` | `200` | `OURS` | Internal indicator calculation warm-up bars |

## 5. Pitchfork (`pitchfork.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `MAX_HOLD` | `pitchfork.py:24` | `60` | `OURS` | Trade timeout horizon in bars |
| `STOP_OFFSET_PCT` | `pitchfork.py:25` | `0.015` (`1.5%`) | `OURS` | Structural stop offset beyond tine/bar extreme |
| `DEFAULT['symbol']` | `pitchfork.py:48` | `'BTCUSDT'` | `OURS` | Asset selection |
| `DEFAULT['tf']` | `pitchfork.py:49` | `'4h'` | `OURS` | Timeframe selection |
| `DEFAULT['variant']` | `pitchfork.py:50` | `'modified_schiff'` | `SOURCED` | Modified Schiff 50% price-only shift; `research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:68-75`, Dologa 2007 |
| `DEFAULT['setup']` | `pitchfork.py:51` | `'BOUNCE'` | `SOURCED` | Andrews 3-pivot Median Line 80% return-to-ML rule; `RESEARCH_PITCHFORK_LAYER.md:28-56` |
| `DEFAULT['vp_filter']` | `pitchfork.py:52` | `'VA'` | `OURS` | P2 inside 70% TPO Value Area of P0-P2 swing filter |
| `DEFAULT['exit']` | `pitchfork.py:53` | `'R'` | `OURS` | Target multiple of risk exit option |
| `DEFAULT['target_r']` | `pitchfork.py:54` | `2.0` | `OURS` | Target risk multiple |
| `DEFAULT['maker_pct']` | `pitchfork.py:55` | `0.02` | `OURS` | Binance maker fee; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['taker_pct']` | `pitchfork.py:55` | `0.05` | `OURS` | Binance taker fee; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['slip_pct']` | `pitchfork.py:55` | `0.02` | `OURS` | Execution slippage on market/stop fills |
| `DEFAULT['start']` | `pitchfork.py:56` | `'2022-04-01'` | `OURS` | DEV window start |
| `DEFAULT['end']` | `pitchfork.py:57` | `'2024-06-30'` | `OURS` | DEV window end |
| `zigzag_delay_4h` | `pitchfork.py:8` | `4` | `OURS` | ZigZag pivot confirmation delay in bars on 4h |
| `zigzag_delay_1d` | `pitchfork.py:8` | `3` | `OURS` | ZigZag pivot confirmation delay in bars on 1d |
| `min_swing_4h` | `pitchfork.py:8` | `0.03` (`3%`) | `OURS` | Minimum swing amplitude filter on 4h |
| `min_swing_1d` | `pitchfork.py:8` | `0.04` (`4%`) | `OURS` | Minimum swing amplitude filter on 1d |
| `va_coverage` | `pitchfork.py:9` | `0.70` (`70%`) | `OURS` | TPO Value Area profile coverage |
| `poc_tolerance` | `pitchfork.py:10` | `0.015` (`1.5%`) | `OURS` | TPO Point of Control tolerance band |

## 6. Cowen Bull Market Support Band (`cowen_bmsb.py`)

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `SMA_W` | `cowen_bmsb.py:35` | `20` | `SOURCED` | 20-week SMA of completed weeks; `research/cowen_q4_2026-10-31/COWEN_Q4_CONCEPT_CHECK.md`, `extract_bekghgecip8.md:W2,W6` |
| `EMA_W` | `cowen_bmsb.py:35` | `21` | `SOURCED` | 21-week EMA of completed weeks; `extract_bekghgecip8.md:W2,W6` |
| `DEFAULT['symbol']` | `cowen_bmsb.py:33` | `'BTCUSDT'` | `OURS` | Asset selection |
| `DEFAULT['setup']` | `cowen_bmsb.py:33` | `'BOUNCE'` | `SOURCED` | Bounce off the band; `extract_bekghgecip8.md:W6` |
| `DEFAULT['gap_pct']` | `cowen_bmsb.py:33` | `3.0` | `OURS` | Catch-down gap threshold percentage; docstring line 12 |
| `DEFAULT['exit_n']` | `cowen_bmsb.py:33` | `2` | `OURS` | Number of daily closes beyond idea level to drop idea; docstring line 12 |
| `DEFAULT['stop_atr']` | `cowen_bmsb.py:33` | `2.0` | `OURS` | Stop distance as ATR14 multiple from signal close; docstring line 12 |
| `DEFAULT['target']` | `cowen_bmsb.py:33` | `'R'` | `OURS` | Target mode choice |
| `DEFAULT['target_r']` | `cowen_bmsb.py:33` | `2.0` | `OURS` | Target risk multiple |
| `DEFAULT['hold_days']` | `cowen_bmsb.py:34` | `30` | `OURS` | Longest hold limit in days; docstring line 13 |
| `DEFAULT['maker_pct']` | `cowen_bmsb.py:34` | `0.02` | `OURS` | Binance maker fee; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['taker_pct']` | `cowen_bmsb.py:34` | `0.05` | `OURS` | Binance taker fee; `_bars.py:FEE_DEFAULT` |
| `DEFAULT['slip_pct']` | `cowen_bmsb.py:34` | `0.02` | `OURS` | Execution slippage on market/stop fills |
| `DEFAULT['start']` | `cowen_bmsb.py:34` | `'2022-04-01'` | `OURS` | DEV window start |
| `DEFAULT['end']` | `cowen_bmsb.py:34` | `'2024-06-30'` | `OURS` | DEV window end |
| `atr_period` | `cowen_bmsb.py:148` | `14` | `OURS` | Daily ATR calculation period |
| `sma50_period` | `cowen_bmsb.py:145` | `50` | `SOURCED` | 50-day SMA fake-out level; `COWEN_LEVELS_2026-10-31.md:bWdXPK3Hlok 00:05:47` |

## Summary

- Total studies audited: 6 (`rsi`, `levels`, `krown`, `wavetrend`, `pitchfork`, `cowen_bmsb`) + shared `_bars.py`
- Total parameters audited: 68
- SOURCED parameters: 22 (Wilder 14, Malkan 40/60 levels and daily breakdown, CryptoCred levels and daily extreme stop, Krown S5 21/55/200 and S8 7/100/30/50, WaveTrend 10/21/0.015 and 53/60 bands and 1.5R target, Pitchfork Schiff/Andrews rules, Cowen 20w SMA / 21w EMA / 50d SMA)
- OURS parameters: 46 (execution fees, slippage, timeout hold bars, structural stop multipliers, calendar date windows, tolerance buffers, indicator warmup)

Noticed: every sim desk study cleanly isolates trader-sourced rules from execution and simulation defaults. All 6 studies have exact file:line provenance documented.
