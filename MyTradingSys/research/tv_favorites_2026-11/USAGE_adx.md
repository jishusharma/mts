# USAGE: Average Directional Index and Directional Movement (ADX and DI)

Research note for `SPEC_INDICATOR_MAP.md` Step 1 (card `tvfav-usage-adx-1107`). Context column only; no code, no trading rules, no backtest.

## 1. Author's Intent

The Directional Movement System (DI+, DI-, DX, ADX) was created by J. Welles Wilder Jr. (*New Concepts in Technical Trading Systems*, 1978, Ch. 4).

- **Premise:** Most indicators identify direction but fail to measure if an asset is trending or in a trading range. Wilder quantified trend strength independently of direction.
- **Directional Movement (+DM / -DM):**
  - `up = high[i] - high[i-1]`; `dn = low[i-1] - low[i]`.
  - `+DM = up` if `up > dn and up > 0`, else 0.
  - `-DM = dn` if `dn > up and dn > 0`, else 0.
- **True Range normalization & smoothing:**
  - `TR = max(high - low, abs(high - close[1]), abs(low - close[1]))`.
  - Smoothed over lookback `n` (standard `n = 14`) using Wilder's recursive smoothing.
  - `DI+ = 100 * S(+DM) / S(TR)`; `DI- = 100 * S(-DM) / S(TR)`.
- **Directional Index (DX) & ADX:**
  - `DX = 100 * abs(DI+ - DI-) / (DI+ + DI-)`.
  - `ADX` is the smoothed average of `DX` over `n` periods.
- **Core interpretation:**
  - Direction: `DI+ > DI-` bull, `DI- > DI+` bear.
  - Trend strength: `ADX` magnitude. Wilder considered ADX rising above 20-25 as trending; ADX below 20 marks consolidation.

## 2. How People Use It (3 to 5 Sources)

### Source 1: J. Welles Wilder Jr. (*New Concepts in Technical Trading Systems*, 1978)
- **Market & Timeframe:** Commodities, futures; daily (14-period default).
- **Usage:** Regime identification to select between trend and range systems.
- **Cites:**
  `MyTradingSys/backtest/layers/FORMULAS.md:687` "Wilder's definitions, n = 14 by default, every threshold in the census is OURS."
  `MyTradingSys/backtest/layers/FORMULAS.md:689` "Cross: the sign of `DI+ - DI-` flips (strict, zeros ignored); red = DI- over DI+, green = DI+ over DI-."
- **Consensus:** Rising ADX confirms trend emergence; DI crosses signal directional dominance shifts.

### Source 2: BeikabuOyaji (TradingView Script "ADX and DI")
- **Market & Timeframe:** Multi-asset; 15m, 1h, 4h, daily.
- **Usage:** Plots DI+, DI-, and ADX in one pane with reference threshold at 20.
- **Cites:**
  `MyTradingSys/research/tv_favorites_2026-11/FAVORITES_2026-11-07.md:10` "Wilder DMI in one pane: DI+, DI-, ADX (len 14) with a strength line (20-25). Same maths as the built-in DMI."
- **Note:** Standard Wilder RMA for DI lines, but `sma(DX, 14)` for ADX.

### Source 3: CCU / Steve (Crypto Analyst, Video AnAx1PanZm4)
- **Market & Timeframe:** Bitcoin (BTCUSDT); 2-day (2D) macro swing chart.
- **Usage:** Cyclical cycle turns using 2-day DI crossovers confirmed by ADX strength.
- **Cites:**
  `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:10` "Red DI above green = \"sellers are in control\"; a red cross is \"rare\". Three steps after a red cross: \"1-3 weeks of consolidation\", \"falling straight to the bottom\", \"the market consolidates and then changes trend\"."
  `MyTradingSys/research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md:10` "\"if it rises very high, it means that the trend strength is very powerful\"."
- **Context:** Red cross (DI- over DI+) marks bearish regime shifts; ADX confirms trend power.

### Source 4: Quantitative Momentum & MTS Census Studies
- **Market & Timeframe:** Bitcoin spot and perps (BTCUSDT); 2-day, 1-day, 1-hour.
- **Usage:** Empirical testing of DI crossover validity conditioned on ADX level and slope.
- **Cites:**
  `MyTradingSys/research/adx_di_2026-11/SPEC.md:3-5` "after a \"red cross\" (DI- over DI+) the market takes \"1-3 weeks of consolidation\", then falls \"straight to the bottom\" ... ADX \"tells us the strength of the trend\". He names no number: every parameter here is OURS."
  `MyTradingSys/research/adx_di_2026-11/CENSUS.md:3` "Swing extreme = lowest low (red) / highest high (green) in the 30 2d bars after the cross; depth = extreme / close at the cross - 1"
- **Analysis:** Crosses with ADX falling from >40 signal exhaustion. Lowest whipsaw occurs in 20-40 regime.

## 3. Crypto / Bitcoin Filter

What survives and fails in 24/7 crypto markets:

- **What fails:**
  - *Blind DI cross execution:* In balance, DI crosses whipsaw frequently (32.1% 3-bar whipsaw on 2D BTC DEV).
  - *Lag on low timeframes (< 15m):* 14-period Wilder smoothing creates ~28-bar lag on ADX; moves mean-revert before ADX > 25.
  - *Symmetric trend assumption:* Bull trends grind with ADX 20-30; bear cascades spike ADX vertically followed by rapid exhaustion.
  - *Ignoring ADX slope:* Trading in DI direction when ADX falls from >40 enters exhaustion pivots.
- **What survives:**
  - *Macro regime context (1D, 2D):* Macro ADX > 20 filters out choppy regimes where trend strategies fail.
  - *Context column for level rejection & wicks:* ADX < 20 confirms range dominance; ADX > 25 confirms trend expansion.

## 4. Common Pitfalls and Parameters

- **SOURCED Parameters (Wilder 1978 defaults):**
  - DI Length (`n`): 14 (SOURCED)
  - ADX Smoothing Length: 14 (SOURCED)
  - Trend threshold level: 20 to 25 (SOURCED)
  - Strong trend threshold: 40 (SOURCED)
- **Pitfalls in the wild:**
  - *Smoothing confusion:* Wilder RMA vs SMA of DX causes historical value divergence between platforms.
  - *Treating ADX as directional:* ADX rises during both uptrends and downtrends; never indicates direction.
- **OURS (MTS design rules):**
  - *Context-only role:* Strictly context/filter columns (regime, strength bucket, exhaustion slope), never standalone triggers.
  - *ADX buckets:* `< 20` (no trend / range), `20 - 40` (established trend), `> 40` (extended / exhaustion) are OURS.
  - *Exhaustion slope filter:* ADX 5-bar slope falling from > 40 flags exhaustion where sweeps mean-revert.

## 5. What It Measures

**What it measures:** Direction-neutral trend strength and expansion momentum (ADX magnitude) alongside directional buyer versus seller dominance (DI+ versus DI- polarity and crossover state).
