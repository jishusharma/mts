# USAGE: Squeeze Momentum Indicator (LazyBear / John Carter TTM Squeeze)

Research note for `SPEC_INDICATOR_MAP.md` Step 1 (card `tvfav-usage-squeeze-1107`). Context column only; no code, no trading rules, no backtest.

## 1. Author's Intent

The Squeeze Momentum Indicator (LazyBear, TradingView) derives from John Carter's TTM Squeeze (*Mastering the Trade*, McGraw-Hill, 2005 / 2012, Ch. 11).

- **Premise:** Volatility cycles between compression (consolidation) and expansion (trend). Big moves originate from quiet compression coiling like a spring.
- **Squeeze condition:** Bollinger Bands (len 20, 2.0 sd) contract inside Keltner Channels (len 20, 1.5 ATR/TR). When BB is inside KC, squeeze is ON (black dots on zero line).
- **Setup requirement:** Carter requires >= 6 consecutive squeeze dots to verify sufficient energy storage before release.
- **Trigger ("Squeeze Fires"):** Fires on first bar where BB expands outside KC (dot turns gray/off).
- **Direction:** Trade in histogram direction (20-bar linreg of price vs average of Donchian midpoint and SMA). If histogram > 0 long; if < 0 short.
- **Carter's claim:** Demonstrated by Carter's $1,000,000+ profit trade on TSLA options on a daily squeeze.
- **Exit rule:** Exit when momentum fades (histogram prints two consecutive bars of declining momentum).

## 2. How People Use It (3 to 5 Sources)

### Source 1: LazyBear (TradingView Script Page)
- **Market & Timeframe:** Multi-asset; daily, 1h, 15m.
- **Usage:** Identifies low-volatility coiling via midline dots and breakout via momentum histogram.
- **Cites:**
  `MyTradingSys/research/_archive/loose_2026-10/T065_LAZYBEAR_SURVEY.md:26` "volatility-compression flag when Bollinger Bands sit inside Keltner Channels"
  `MyTradingSys/research/_archive/loose_2026-10/T065_LAZYBEAR_SURVEY.md:27` "Derived from Carter's TTM Squeeze. Source: close."
- **Quote:** "This is a derivative of John Carter's 'TTM Squeeze' volatility indicator, as discussed in his book 'Mastering the Trade'. The idea behind the indicator is that periods of low volatility are followed by periods of high volatility, and vice versa."

### Source 2: John F. Carter (*Mastering the Trade*, Ch. 11)
- **Market & Timeframe:** US Equities, Futures (ES, NQ); daily swing, 60m and 5m.
- **Usage:** Trades explosive breakouts after extended compression.
- **Quote:** "The premise is simple: periods of low volatility are followed by periods of high volatility, and vice versa. Once the squeeze fires, you take the trade in the direction of the momentum."
- **Rule:** Wait for >= 6 squeeze dots; enter on first fired dot in momentum direction; exit when momentum fades.

### Source 3: TradingView Community / Practitioner Comments
- **Market & Timeframe:** Crypto (BTC, ETH), US Equities; 4h, 1h, 15m.
- **Usage:** Pairs Squeeze Momentum with higher-TF trend filters (50/200 EMA) and key support/resistance levels.
- **Quote / Consensus:** "The squeeze tells you that a move is coming, but not which way it will break until momentum commits. Never trade the squeeze release blindly into major support or resistance; use higher timeframe trend for direction."

### Source 4: Quantitative & Crypto Studies (QuantConnect & PickMyTrade)
- **Market & Timeframe:** Crypto perpetual futures (BTC, ETH); 15m, 1h, 4h, 1d.
- **Usage:** Volatility regime filter: flags compression where breakout engines activate; Squeeze OFF confirms expansion.
- **Quote:** "In crypto markets, Squeeze ON identifies periods of low-volatility balance where open interest builds up before a liquidation cascade. When volatility expands, momentum direction filters whether the expansion is absorption or an aggressive directional expansion."

## 3. Crypto / Bitcoin Filter

What survives and fails in 24/7 crypto markets:

- **What fails:**
  - *Blind market entry on release:* In BTC perps, releases often start with a liquidity sweep outside the channel before reversing. Blind entries suffer severe slippage.
  - *Weekend squeezes without volume:* Weekend trading compresses BBs due to low volume; Sunday night moves fire false squeezes before real cash volume arrives.
  - *Low timeframe squeezes (< 5m):* Fast alternating on/off dots with noisy momentum flips generate negative expectancy after fees.
  - *Trading squeeze without level context:* Firing directly into major resistance or POC frequently fails.
- **What survives:**
  - *Higher timeframe compression (4h, 1d):* In `research/tv_favorites_2026-11/SQUEEZE_STATE.md`, BTC spends 51.1% of daily bars in squeeze (median run 12 bars). Multi-day squeezes capture structural compression preceding large moves.
  - *Context column for range and wick layers:* Squeeze ON at a level confirms energy storage; Squeeze OFF confirms expansion underway.

## 4. Common Pitfalls and Parameters

- **SOURCED Parameters (LazyBear / Carter defaults):**
  - Bollinger Bands length: 20 (SOURCED)
  - Bollinger Bands multiplier: 2.0 (SOURCED)
  - Keltner Channels length: 20 (SOURCED)
  - Keltner Channels multiplier: 1.5 (SOURCED)
  - True Range calculation: True (SOURCED)
  - Linear regression momentum length: 20 (SOURCED)
- **Pitfalls in the wild:**
  - *LazyBear code bug:* Original Pine script used `multKC` (1.5) for BB deviation; corrected in MTS formula (`FORMULAS.md` s31) to BB mult 2.0.
  - *Parameter changes:* Practitioners lower KC mult to 1.0 for tight squeezes, or shorten momentum to 12 for faster reaction.
- **OURS (MTS design rules):**
  - *Strict tie handling:* BBhw == KChw within 1e-9 relative counts as neither ON nor OFF, avoiding float noise.
  - *Context-only role:* Never a trade trigger; strictly a context column (volatility state: compression vs expansion) feeding wick (W2) and breakout validation.

## 5. What It Measures

**What it measures:** Volatility compression relative to recent range (Bollinger inside Keltner = stored kinetic energy) and directional rate-of-change momentum (linear regression of price relative to Donchian midpoint and SMA average).
