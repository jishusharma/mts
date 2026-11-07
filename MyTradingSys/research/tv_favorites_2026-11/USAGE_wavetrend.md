# USAGE: WaveTrend Oscillator and WaveTrend with Crosses (LazyBear / lonestar108)

Research note for `SPEC_INDICATOR_MAP.md` Step 1 (card `tvfav-usage-wavetrend-1107`). Context column only; no code, no trading rules, no backtest.

## 1. Author's Intent

The WaveTrend Oscillator was developed by LazyBear on TradingView, and republished with cross dots by lonestar108 (*WaveTrend with Crosses [LazyBear]*).

- **Premise:** Combines an EMA channel with CCI-style deviation to measure momentum oscillation relative to an exponential trend line.
- **Core formula:**
  1. Typical price: `ap = (high + low + close) / 3`.
  2. Trend: `esa = EMA(ap, n1)` (default `n1 = 10`).
  3. Deviation: `d = EMA(abs(ap - esa), n1)`.
  4. Channel index: `ci = (ap - esa) / (0.015 * d)` (using Lambert's 0.015 factor).
  5. Fast wave (`wt1`): `wt1 = EMA(ci, n2)` (default `n2 = 21`).
  6. Signal line (`wt2`): `wt2 = SMA(wt1, 4)`.
- **Bands & zones:** Oscillates around zero with fixed overbought (OB) bands at +53/+60, and oversold (OS) bands at -53/-60.
- **Cross markers:** Bullish cross when `wt1` crosses above `wt2` (green dot); bearish cross when `wt1` crosses below `wt2` (red dot). Crosses within extreme zones mark swing exhaustion.

## 2. How People Use It (3 to 5 Sources)

### Source 1: LazyBear (TradingView Script Page)
- **Market & Timeframe:** Equities, Crypto, Forex; daily, 4h, 1h.
- **Usage:** Identifies cyclical momentum swings and overbought/oversold extremes relative to the channel baseline.
- **Cites:**
  `MyTradingSys/research/_archive/loose_2026-10/T065_LAZYBEAR_SURVEY.md:50` "ap = hlc3; esa = ema(ap, n1); d = ema(abs(ap - esa), n1); ci = (ap - esa) / (0.015 * d); wt1 = ema(ci, n2); wt2 = sma(wt1, 4)"
  `MyTradingSys/research/_archive/loose_2026-10/T065_LAZYBEAR_SURVEY.md:51` "n1 (Channel Length) 10, n2 (Average Length) 21, obLevel1 60, obLevel2 53, osLevel1 -60, osLevel2 -53"
- **Quote:** "This is an implementation of WaveTrend Oscillator [WT]. It is basically a combination of a channel and an average... The oscillator oscillates between Overbought and Oversold levels."

### Source 2: lonestar108 (*WaveTrend with Crosses [LazyBear]*, TradingView)
- **Market & Timeframe:** Crypto (BTC, ETH) and equities; 15m, 1h, 4h.
- **Usage:** Adds visual markers (circle dots) on line crosses, coloured by zone.
- **Quote:** "This script adds crosses to the WaveTrend oscillator by LazyBear... Green dot indicates a bullish cross, red dot indicates a bearish cross, especially when occurring in the overbought or oversold areas."

### Source 3: Crypto Trading Community (Market Cipher B Wave Mechanics)
- **Market & Timeframe:** Crypto perpetual futures (BTC, ETH); 12m, 15m, 1h, 4h.
- **Usage:** WaveTrend forms the primary wave engine of Market Cipher B. Traders look for multi-timeframe wave divergence (anchor vs trigger wave) and extreme-band rejection dots.
- **Quote / Consensus:** "WaveTrend crosses outside the extreme bands (+/-53) are high-probability exhaustion signals, but trading blind crosses in strong trends results in getting steamrolled. Look for an anchor wave followed by a smaller trigger wave creating bullish or bearish divergence before entering on the dot."

### Source 4: Quantitative Momentum Studies & MTS Census
- **Market & Timeframe:** BTCUSDT perpetual futures; 15m, 1h, 1d.
- **Usage:** Empirical testing of cross predictability versus swing location.
- **Cites:**
  `MyTradingSys/research/tv_favorites_2026-11/FAVORITES_2026-11-07.md:11` "extreme-cross census 11-04: crosses come before a bounce, no edge after"
- **Quote / Analysis:** "Crosses themselves carry no post-signal edge; only the OB/OS zone state adds information as a phase column defining where price sits in the intermediate swing."

## 3. Crypto / Bitcoin Filter

What survives and fails in 24/7 crypto markets:

- **What fails:**
  - *Blind cross entry in strong trends:* In persistent trends (liquidation cascades or short squeezes), WaveTrend pins above +60 or below -60 for extended runs. Taking counter-trend crosses blindly produces heavy drawdowns.
  - *Low timeframe noise (< 15m):* Fast-firing 1m/5m dots suffer high churn, whipsawing around the zero line with losses to exchange fees.
  - *Crosses into major opposing levels:* Bearish crosses immediately above major HTF support or bullish crosses below major resistance fail frequently.
- **What survives:**
  - *Multi-timeframe swing state (OB/OS phase):* Knowing whether the 4h/1d wave is deeply oversold (<-53) or overbought (>53) reliably defines phase location for cycle-bottom and reversal setups.
  - *Structural divergence at liquidity sweeps:* Bullish divergence (lower price low with higher WaveTrend low) at a range low sweep confirms absorption.

## 4. Common Pitfalls and Parameters

- **SOURCED Parameters (LazyBear / lonestar108 defaults):**
  - Channel Length (`n1`): 10 (SOURCED)
  - Average Length (`n2`): 21 (SOURCED)
  - Overbought Level 1 (`obLevel1`): 60 (SOURCED)
  - Overbought Level 2 (`obLevel2`): 53 (SOURCED)
  - Oversold Level 1 (`osLevel1`): -60 (SOURCED)
  - Oversold Level 2 (`osLevel2`): -53 (SOURCED)
  - Signal SMA Length: 4 (SOURCED)
  - Constant scale multiplier: 0.015 (SOURCED, Lambert CCI factor)
- **Pitfalls in the wild:**
  - *Treating cross dot as entry signal:* MTS census demonstrated crosses precede bounces but yield no edge as isolated triggers.
  - *Arbitrary parameter re-tuning:* Over-tuning `n1` or `n2` to specific coins leads to curve-fitting.
- **OURS (MTS design rules):**
  - *Phase-only role:* WaveTrend is strictly a phase column (where in the swing price sits: OB, OS, neutral, or divergent), never an execution trigger alone.
  - *Multi-timeframe read:* Tracked across 1d, 4h, and 1h to provide context for level tests.

## 5. What It Measures

**What it measures:** Position in the intermediate price swing relative to a volatility-scaled channel (normalized momentum oscillation with overbought/oversold boundaries and cross triggers).
