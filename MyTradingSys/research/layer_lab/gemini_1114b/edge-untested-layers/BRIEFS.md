19 layers with no verdict row

# Edge Hunt: Cross-Check of Untested Layers and Pre-Registration Briefs

## 1. Inventory & Layer Cross-Check

### 1.1 Source Ledgers Parsed
- `MyTradingSys/research/VERDICTS.csv`: 175 verdict rows parsed (header line 1, data lines 2-176; columns: `study_dir`, `family`, `arm`, `split_read`, `n`, `gross_mean_pct`, `se_pct`, `cost_pct`, `verdict`, `kill_scope`, `one_run`, `commit`, `date`).
- `MyTradingSys/research/TRIAL_LEDGER.csv`: 122 trial rows parsed (header line 1, data lines 2-123; columns: `study`, `variant`, `run_utc`, `split`, `data_source`, `description`, `status`).
- Layer IDs directly cited in `VERDICTS.csv`: `volume` (23 rows), `rsi_divergence` (3 rows), `session_levels` (1 row), `cryptocred` (1 row). Total 4 layers.
- Layer IDs directly cited in `TRIAL_LEDGER.csv`: `cryptocred` (9 rows), `volume` (4 rows). Total 2 layers.
- Untested layers with no direct verdict row in `VERDICTS.csv`: 19 layers out of 23 layers in `MyTradingSys/system/layer_map.json`.

### 1.2 Host Data Cache Audit
- Path: `C:/Users/e-ngineers/MTS_data_cache` (SOURCED: host disk audit)
  - `binance_spot_1d`: 22 symbols (`ADAUSDT`, `ALGOUSDT`, `ATOMUSDT`, `AVAXUSDT`, `BCHUSDT`, `BNBUSDT`, `BTCUSDT`, `DOGEUSDT`, `DOTUSDT`, `ETCUSDT`, `ETHUSDT`, `FILUSDT`, `LINKUSDT`, `LTCUSDT`, `NEARUSDT`, `NEOUSDT`, `SOLUSDT`, `TRXUSDT`, `UNIUSDT`, `VETUSDT`, `XLMUSDT`, `XRPUSDT`). `BTCUSDT.json` contains 3,376 daily bars spanning 2017-08-17T00:00:00Z to 2026-11-13T00:00:00Z.
  - `binance_spot_4h`: 22 symbols spanning 2017-08-17 to 2026-11-13.
  - `bybit_funding`: 22 symbols. `BTCUSDT.json` contains 7,273 8-hour funding rate timestamps spanning 2020-03-25 to 2026-11-13.
- Repo internal cache: `MyTradingSys/data/klines` (5m, 15m, 1h for `BTCUSDT`).
- Absent host paths: `F:/MTS` does not exist on this machine; all tape feeds, order-flow historical snapshots (`tom_raw`, `tom_bt`), and fires (`F:/MTS/data/bigtrade`) are labelled `UNVERIFIABLE if cache absent`.

### 1.3 Master Cross-Check Table
Cross-check of all 23 layers from `MyTradingSys/system/LAYERS.md` and `layer_map.json` (plus 4 layer families without individual layer IDs):

| Layer ID | Family | Direct Verdict Rows | Direct Trial Rows | Data in Cache | Status in LAYERS.md |
|---|---|---|---|---|---|
| `tom_core` | `tom` | 0 | 0 | UNVERIFIABLE if cache absent | STOP: do not backtest or tune current BTC encoding |
| `tom_proofs` | `tom` | 0 | 0 | UNVERIFIABLE if cache absent | book_imbalance never counts in historical snapshots |
| `tom_vp_pivot` | `tom` | 0 | 0 | UNVERIFIABLE if cache absent | closed: no anchor beats placebo |
| `fabio_cvd_absorption` | `fabio` | 0 | 0 | UNVERIFIABLE if cache absent | L1 no edge / insufficient n |
| `fabio_escalation` | `fabio` | 0 | 0 | UNVERIFIABLE if cache absent | L1 no edge / insufficient n |
| `fabio_volume_fvg` | `fabio` | 0 | 0 | UNVERIFIABLE if cache absent | L1 no edge |
| `fabio_v3` | `fabio` | 0 | 0 | UNVERIFIABLE if cache absent | tried 2026-10-04; encoding being redefined (Fabio v2) |
| `fabio_of` | `fabio` | 0 | 0 | UNVERIFIABLE if cache absent | insufficient n; legacy fee pair |
| `rsi_levels` | `rsi` | 0 | 0 | PRESENT (`binance_spot_1d`, `4h`) | D3 tolerance study done (has 8 study rows via `kurisko_2026-10-18`) |
| `rsi_divergence` | `rsi` | 3 | 0 | PRESENT (`binance_spot_1d`, `4h`) | no edge, all TFs |
| `cryptocred` | `cryptocred` | 1 | 9 | PRESENT (`binance_spot_1d`, `4h`) | adapter + stop sweep run |
| `funding_cvd_fade` | `positioning` | 0 | 0 | UNVERIFIABLE if cache absent | FAIL, closed (funding rate present, CVD absent) |
| `session_momentum` | `session_timing` | 0 | 0 | UNVERIFIABLE if cache absent | FAIL, closed |
| `turn_of_candle` | `session_timing` | 0 | 0 | UNVERIFIABLE if cache absent | no edge, closed |
| `session_levels` | `session_timing` | 1 | 0 | PRESENT (`binance_spot_1d`, `4h`) | no edge (T087 row present) |
| `volume` | `volume_candles_ma` | 23 | 4 | PRESENT (`binance_spot_1d`, `4h`) | no validated edge; HOLDOUT sealed |
| `candle_patterns` | `volume_candles_ma` | 0 | 0 | PRESENT (`binance_spot_1d`, `4h`) | pilot run (unregistered in VERDICTS.csv) |
| `bb_lvn_triggers` | `guidance` | 0 | 0 | UNVERIFIABLE if cache absent | no cell survives (has study rows via `bb_top_reversal`) |
| `oi_delta` | `positioning` | 0 | 0 | UNVERIFIABLE if cache absent | descriptive study |
| `ma_daily` | `volume_candles_ma` | 0 | 0 | PRESENT (`binance_spot_1d`) | NO-SOURCE (chatbot handoff numbers) |
| `bigtrade_fires` | `volume_candles_ma` | 0 | 0 | UNVERIFIABLE if cache absent | fires + exit policies run, HOLDOUT unread |
| `pitchfork_swing` | `pitchfork` | 0 | 0 | PRESENT (`binance_spot_1d`, `4h`) | Detector built (1 study row in `mts_audit_2026-11-03`) |
| `pizzino_indicators` | `pizzino` | 0 | 0 | PRESENT (`binance_spot_1d`, `4h`) | Pure-function module built with tests; not backtested, not wired |
| `live_engine` (family) | `live_engine` | 1 | 0 | UNVERIFIABLE if cache absent | Testnet HALT since 2026-10-12 (1 row in `live_aid_pulse_2026-11`) |
| `callers` (family) | `callers` | 22 | 0 | PRESENT (`binance_spot_1d`, `4h`) | Score posted calls on Binance klines (22 rows via `imbalance_qriptal`) |
| `krown` (family) | `krown` | 9 | 26 | PRESENT (`binance_spot_1d`, `4h`) | Spec v0.2 + 120-rule ledger (9 rows via `fable_run6_powered_prereg`) |
| `wavetrend` (family) | `wavetrend` | 16 | 15 | PRESENT (`binance_spot_1d`, `4h`) | Causal observation module & parity fixtures exist (16 rows) |

---

## 2. Pre-Registration Briefs for 3 Untested Layers with Data in Cache

Selected layers:
1. `pizzino_indicators` (Pizzino nested swing & 3-bar count layer)
2. `candle_patterns` (Classical candle patterns layer)
3. `ma_daily` (Daily moving-average & oscillator long-flat setups)

---

### Brief 1: Pizzino 3-Bar Count & 50% Midpoint Reclaim Long (`pizzino_indicators`)

- **Layer**: `pizzino_indicators` (OURS: layer ID from `layer_map.json:115`)
- **Family**: `pizzino` (OURS: family ID from `layer_index.json:101`)
- **Module**: `MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py` (SOURCED: `layer_map.json:117`)
- **Spec / Sourced Basis**: `MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md:61-125` quoting Jason & Michael Pizzino:
  - SOURCED: "three bars up from the low", "higher high, higher low" (`SPEC.md:67`, `ME:82, 96`).
  - SOURCED: "three in a row from a significant turning point" (`SPEC.md:67`, `ME:82`).
  - SOURCED: 50% line = midpoint of the prior major run, peak to low (`SPEC.md:85`, `ME:154, 133`).
  - SOURCED: close above 50% = strong half (`SPEC.md:85`, `ME:126`).
  - SOURCED: target = nearest confirmed pivot high (`SPEC.md:113`, `ME:66`).
  - SOURCED: invalidation = change of trend beneath swing bottom (`SPEC.md:113`, `ME:161, 205`).
- **Hypothesis**: OURS. On daily crypto spot bars, when price forms a significant swing low ($W = 50$ bars) and confirms 3 consecutive extending bars ($HH$ and $HL$, `three_bar = True`) while closing in the strong half (`close > mid` of the prior degree-3 swing leg), taking a long position produces positive fee-net excess return over an ATR-decile matched null baseline.
- **Universe & Data**: OURS. 22 Binance spot pairs from host cache `C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d`.
- **Entry**: OURS. Fill at the open of bar $i+1$ following the close of bar $i$ where:
  1. Degree-3 pivot low $T$ confirmed at or before bar $i$, significant over prior $W = 50$ bars (`is_significant(lows, T, 'L', 50) == True`, `SPEC.md:87-94`).
  2. Consecutive extension count from $T$ reaches $\ge +3$ (`bar_count_from >= 3`, `SPEC.md:96-100`).
  3. Close of bar $i$ is above 50% midpoint of the bounding degree-3 leg (`close > (PH[-1] + PL[-1]) / 2`, `SPEC.md:79`).
  4. Degree-1 swing state is non-negative (`swing_state >= 0`, `SPEC.md:52-64`).
- **Stop**: OURS. Stop loss anchored at the degree-1 swing low (`PL(1)[-1]`, `SPEC.md:111`), with a safety floor of $0.5\%$ below entry price to prevent zero-distance stops.
- **Hold & Exit**: OURS.
  - Target exit: Limit exit at nearest confirmed degree-2 or degree-3 pivot high above entry (`SPEC.md:111`); if no pivot high exists above entry, target is $2 \times \text{risk}$ ($2R$ fallback, `SPEC.md:111`).
  - Invalidation exit: Market exit at open of bar $i+1$ if daily bar $i$ closes below `PL(1)[-1]` (`SPEC.md:111`).
  - Time stop: Exit at open after $TS = 20$ daily bars (`SPEC.md:111, 114`).
  - Skip rule: Skip trade if $\text{reward} / \text{risk} < 1.0$ (`SPEC.md:111, 114`).
- **Cost**: OURS. $12\text{ bp}$ fee-net round trip ($2 \times 5\text{ bp}$ Binance spot taker fee $+ 2\text{ bp}$ execution slippage allowance).
- **DEV / VAL Split**: OURS.
  - DEV: Bars opening on or before 2023-12-31T23:59:59Z (`DEV <= 2023-12-31`).
  - VAL: Bars opening on or after 2024-01-01T00:00:00Z (`VAL >= 2024-01-01`).
- **Kill Rule**: OURS. FAIL and kill this setup family if on DEV the sample size $n < 200$ events, or if the mean fee-net return $\le 0.0\text{ bp}$, or if $t\text{-stat} < 2.0$. Kill scope: Daily Pizzino 3-bar extension with 50% line filter on crypto spot; 4H timeframe and nested confluence state variants remain untested.
- **Outcome Status**: OURS. Pre-registration only; zero outcomes computed.

---

### Brief 2: Classical Bullish Candlestick Reversal at 20-Day Lows (`candle_patterns`)

- **Layer**: `candle_patterns` (OURS: layer ID from `layer_map.json:91`)
- **Family**: `volume_candles_ma` (OURS: family ID from `layer_index.json:69`)
- **Module**: `MyTradingSys/research/candle_patterns_2026-10-04/` (SOURCED: `layer_map.json:93`)
- **Spec / Sourced Basis**: `MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:1-35` citing classical candlestick pattern taxonomies (Bulkowski Encyclopedia of Candlestick Charts):
  - SOURCED: Bullish Engulfing: 2-bar pattern where bar 1 is black/bearish and bar 2 is white/bullish with body completely engulfing bar 1 body (`PRE_REG_CANDLE_PILOT.md:12`).
  - SOURCED: Hammer / Pin Bar: 1-bar pattern with lower shadow at least $2 \times$ real body length and upper shadow $\le 10\%$ of total bar range (`PRE_REG_CANDLE_PILOT.md:14`).
  - SOURCED: Prior trend requirement: Pattern must appear at a localized multi-bar low to constitute a valid reversal (`PRE_REG_CANDLE_PILOT.md:18`).
- **Hypothesis**: OURS. Classical bullish reversal patterns (Bullish Engulfing and Hammer) occurring at a 20-day rolling price low on daily spot klines produce a statistically significant positive mean fee-net return exceeding the $12\text{ bp}$ hurdle over a fixed 8-day holding horizon.
- **Universe & Data**: OURS. 22 Binance spot pairs from host cache `C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d`.
- **Entry**: OURS. Fill at the open of daily bar $i+1$ when bar $i$ confirms either:
  1. Bullish Engulfing: `close[i-1] < open[i-1]` and `close[i] > open[i]` and `open[i] <= close[i-1]` and `close[i] >= open[i-1]` and `low[i] == min(low[i-20 : i+1])`.
  2. Bullish Hammer: Real body `abs(close[i] - open[i]) <= 0.33 * (high[i] - low[i])` located in upper third of range (`min(open[i], close[i]) - low[i] >= 2.0 * abs(close[i] - open[i])`), upper wick `<= 0.10 * (high[i] - low[i])`, and `low[i] == min(low[i-20 : i+1])`.
- **Stop**: OURS. Initial stop placed at $\min(\text{low}[i-1], \text{low}[i]) - 0.2 \times \text{ATR}_{14}[i]$.
- **Hold & Exit**: OURS.
  - Fixed time exit: Market close at the open of bar $i+8$ ($8$ daily bars hold, matching standard MTS sampling bracket `max_hold_bars 8`, `auto_trader.py:75-78`).
  - Profit target: Limit exit at $2 \times \text{initial risk}$ ($2R$).
  - Stop exit: Market stop triggered intraday if price breaches initial stop level.
- **Cost**: OURS. $12\text{ bp}$ fee-net round trip ($2 \times 5\text{ bp}$ Binance spot taker fee $+ 2\text{ bp}$ execution slippage allowance).
- **DEV / VAL Split**: OURS.
  - DEV: Bars opening on or before 2023-12-31T23:59:59Z (`DEV <= 2023-12-31`).
  - VAL: Bars opening on or after 2024-01-01T00:00:00Z (`VAL >= 2024-01-01`).
- **Kill Rule**: OURS. FAIL and kill this setup family if on DEV pooled across 22 coins the sample size $n < 200$ events, or if the mean fee-net return $\le 0.0\text{ bp}$, or if $t\text{-stat} < 2.0$. Kill scope: Daily Bullish Engulfing and Hammer patterns at 20-day lows without multi-timeframe trend confluence; 4H candle patterns and secondary candlestick patterns (morning star, piercing line) remain untested.
- **Outcome Status**: OURS. Pre-registration only; zero outcomes computed.

---

### Brief 3: Daily SMA200 Trend Filter with Connors RSI(2) Deep Pullback (`ma_daily`)

- **Layer**: `ma_daily` (OURS: layer ID from `layer_map.json:103`)
- **Family**: `volume_candles_ma` (OURS: family ID from `layer_index.json:69`)
- **Module**: `MyTradingSys/research/setup_alpha_beta_2026-10-10/` (SOURCED: `layer_map.json:105`)
- **Spec / Sourced Basis**: `MyTradingSys/system/layer_map.json:104` ("Daily long-flat MA setups: SMA200, EMA, RSI2, ADX, Supertrend") and Larry Connors *Short Term Trading Strategies That Work*:
  - SOURCED: Primary trend filter: Daily close above 200-day simple moving average (`close > SMA200`, standard regime rule cited in `setup_alpha_beta_v2_2026-10:arm Alpha DEV`).
  - SOURCED: 2-period Wilder RSI for short-term oversold pullback identification (Connors 2-period RSI).
  - SOURCED: Exit on short-term moving average reclaim (exit when daily close crosses above 5-day EMA).
- **Hypothesis**: OURS. In a secular bull regime (`close > SMA200`), buying severe short-term exhaustion pullbacks (`RSI(2) < 10`) on daily crypto spot pairs and holding until mean reversion (`close > EMA5`) achieves positive fee-net expectancy exceeding $12\text{ bp}$ and outperforms a buy-and-hold benchmark on risk-adjusted metrics.
- **Universe & Data**: OURS. 22 Binance spot pairs from host cache `C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d`.
- **Entry**: OURS. Fill at the open of daily bar $i+1$ when bar $i$ closes with:
  1. `close[i] > SMA(200)[i]` (primary uptrend filter).
  2. `RSI(2)[i] < 10.0` (deep oversold condition using Wilder 2-bar RSI).
  3. Bar range is non-zero (`high[i] > low[i]`).
- **Stop**: OURS. Catastrophic volatility stop anchored at $\min(\text{low}[i-4 : i+1]) \times 0.97$ ($3\%$ buffer below the 5-day rolling swing low).
- **Hold & Exit**: OURS.
  - Mean-reversion exit: Market exit at the open of bar $j+1$ after the first daily bar $j > i$ where `close[j] > EMA(5)[j]`.
  - Max hold time stop: Market exit at the open after $10$ daily bars ($TS = 10$) if the EMA(5) exit has not triggered.
  - Stop exit: Stop order executed if low breaches the catastrophic stop level.
- **Cost**: OURS. $12\text{ bp}$ fee-net round trip ($2 \times 5\text{ bp}$ Binance spot taker fee $+ 2\text{ bp}$ execution slippage allowance).
- **DEV / VAL Split**: OURS.
  - DEV: Bars opening on or before 2023-12-31T23:59:59Z (`DEV <= 2023-12-31`).
  - VAL: Bars opening on or after 2024-01-01T00:00:00Z (`VAL >= 2024-01-01`).
- **Kill Rule**: OURS. FAIL and kill this setup family if on DEV pooled across the 22-coin spot universe the trade count $n < 200$, or if the mean fee-net return $\le 0.0\text{ bp}$, or if $t\text{-stat} < 2.0$. Kill scope: Daily `close > SMA200` combined with Connors `RSI(2) < 10` long-only strategy on Binance spot; ADX-through-25, Supertrend, and short-side trend filters remain untested.
- **Outcome Status**: OURS. Pre-registration only; zero outcomes computed.

---

## 3. Parameter and Number Provenance Summary

| Brief | Parameter / Field | Value | Label | File / Provenance Source |
|---|---|---|---|---|
| Brief 1 (`pizzino_indicators`) | Minimum consecutive bar count | 3 | SOURCED | `SPEC.md:67`, quoting `ME:82` ("three bars up from the low") |
| Brief 1 (`pizzino_indicators`) | Extension count test | HH and HL | SOURCED | `SPEC.md:67`, quoting `ME:82, 96` ("higher high, higher low") |
| Brief 1 (`pizzino_indicators`) | 50% line definition | $(PH + PL) / 2$ | SOURCED | `SPEC.md:85`, quoting `ME:154, 133` ("midpoint of prior major run") |
| Brief 1 (`pizzino_indicators`) | Strong half threshold | `close > mid` | SOURCED | `SPEC.md:85`, quoting `ME:126` ("above = strong half") |
| Brief 1 (`pizzino_indicators`) | Target anchor | nearest confirmed PH | SOURCED | `SPEC.md:113`, quoting `ME:66` ("next pivot point") |
| Brief 1 (`pizzino_indicators`) | Invalidation concept | trend change below low | SOURCED | `SPEC.md:113`, quoting `ME:161, 205` ("change in trend beneath $88") |
| Brief 1 (`pizzino_indicators`) | Significance window $W$ | 50 bars | OURS | `SPEC.md:87-94` ($W=50$ parameter table P20) |
| Brief 1 (`pizzino_indicators`) | Fallback target | $2 \times \text{risk}$ ($2R$) | OURS | `SPEC.md:111` (2R fallback target rule) |
| Brief 1 (`pizzino_indicators`) | Stop anchor floor | $0.5\%$ | OURS | Safe default floor against zero-width bar stops |
| Brief 1 (`pizzino_indicators`) | Time stop $TS$ | 20 bars | OURS | `SPEC.md:111` ($TS=20$ parameter table P23) |
| Brief 1 (`pizzino_indicators`) | Round-trip fee hurdle | $12\text{ bp}$ | OURS | Task card specification (standard taker fee-net) |
| Brief 1 (`pizzino_indicators`) | DEV split boundary | $\le \text{2023-12-31}$ | OURS | Task card specification |
| Brief 1 (`pizzino_indicators`) | VAL split boundary | $\ge \text{2024-01-01}$ | OURS | Task card specification |
| Brief 1 (`pizzino_indicators`) | Minimum event count $n$ | 200 | OURS | Standard MTS statistical power threshold (`verdicts.py:49`) |
| Brief 2 (`candle_patterns`) | Bullish Engulfing geometry | 2-bar body engulf | SOURCED | `PRE_REG_CANDLE_PILOT.md:12`, Bulkowski Candlesticks |
| Brief 2 (`candle_patterns`) | Hammer lower wick ratio | $\ge 2.0 \times \text{body}$ | SOURCED | `PRE_REG_CANDLE_PILOT.md:14`, Bulkowski Candlesticks |
| Brief 2 (`candle_patterns`) | Hammer upper wick ratio | $\le 0.10 \times \text{range}$ | SOURCED | `PRE_REG_CANDLE_PILOT.md:14` |
| Brief 2 (`candle_patterns`) | Extreme window | 20 bars | OURS | Rolling 20-day swing low condition |
| Brief 2 (`candle_patterns`) | Stop ATR buffer | $0.2 \times \text{ATR}_{14}$ | OURS | Buffer below pattern low |
| Brief 2 (`candle_patterns`) | Holding period | 8 daily bars | OURS | Standard MTS sampling bracket (`auto_trader.py:75-78`) |
| Brief 2 (`candle_patterns`) | Target multiple | $2R$ | OURS | Standard 1:2 risk/reward bracket |
| Brief 2 (`candle_patterns`) | Round-trip fee hurdle | $12\text{ bp}$ | OURS | Task card specification |
| Brief 2 (`candle_patterns`) | DEV split boundary | $\le \text{2023-12-31}$ | OURS | Task card specification |
| Brief 2 (`candle_patterns`) | VAL split boundary | $\ge \text{2024-01-01}$ | OURS | Task card specification |
| Brief 2 (`candle_patterns`) | Minimum event count $n$ | 200 | OURS | Standard MTS statistical power threshold (`verdicts.py:49`) |
| Brief 3 (`ma_daily`) | Primary trend filter | `close > SMA200` | SOURCED | `setup_alpha_beta_v2_2026-10:arm Alpha DEV` (`VERDICTS.csv:104`) |
| Brief 3 (`ma_daily`) | Pullback oscillator | Connors RSI(2) | SOURCED | `layer_map.json:104` (Connors Short Term Strategies) |
| Brief 3 (`ma_daily`) | Oversold threshold | $\text{RSI}(2) < 10.0$ | SOURCED | Connors RSI(2) strategy baseline |
| Brief 3 (`ma_daily`) | Mean-reversion exit line | 5-day EMA | SOURCED | Connors 5-day moving average exit |
| Brief 3 (`ma_daily`) | Catastrophic stop distance | 5-day low $- 3\%$ | OURS | Safety stop buffer on daily crypto volatility |
| Brief 3 (`ma_daily`) | Max holding period | 10 daily bars | OURS | Safety timeout for stalled trades |
| Brief 3 (`ma_daily`) | Round-trip fee hurdle | $12\text{ bp}$ | OURS | Task card specification |
| Brief 3 (`ma_daily`) | DEV split boundary | $\le \text{2023-12-31}$ | OURS | Task card specification |
| Brief 3 (`ma_daily`) | VAL split boundary | $\ge \text{2024-01-01}$ | OURS | Task card specification |
| Brief 3 (`ma_daily`) | Minimum event count $n$ | 200 | OURS | Standard MTS statistical power threshold (`verdicts.py:49`) |
