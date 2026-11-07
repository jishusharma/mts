# USAGE: Volume Flow Indicator (Markos Katsanos / LazyBear VFI)

Research note for `SPEC_INDICATOR_MAP.md` Step 1 (card `tvfav-usage-vfi-1107`). Context column only; no code, no trading rules, no backtest.

## 1. Author's Intent

The Volume Flow Indicator (VFI) was created by Markos Katsanos, published in *Technical Analysis of STOCKS & COMMODITIES* (June 2004, "Using Money Flow to Stay with the Trend").

- **Premise:** Traditional volume indicators like On-Balance Volume (OBV) accumulate volume indefinitely and treat any price change—even insignificant noise—as valid volume flow. Katsanos designed VFI as an oscillator around zero that filters price noise and anomalous volume spikes.
- **Three core mechanics:**
  1. *Volatility cutoff:* Compares log change of typical price (hlc3) against a volatility threshold: `cutoff = coef * stdev(log_change, 30) * close` (default `coef = 0.2`). Price moves smaller than cutoff contribute zero volume.
  2. *Volume cap:* Caps extreme individual bar volume at `2.5 * SMA(volume, 50)` to prevent single-day outlier spikes from distorting the rolling picture.
  3. *Rolling window:* Sums signed capped volume over a finite rolling lookback (default 130 bars) and divides by 50-bar average volume.
- **Zero line & trend:** VFI > 0 indicates net institutional accumulation (bull trend); VFI < 0 indicates distribution (bear trend). Zero crosses mark intermediate trend shifts.
- **Divergences & V-patterns:** Katsanos identified divergences against price as the most potent signal, with sharp V-formations in VFI frequently preceding price turning points.

## 2. How People Use It (3 to 5 Sources)

### Source 1: Markos Katsanos (TASC June 2004)
- **Market & Timeframe:** US Equities (S&P 500, individual equities); daily (130-bar rolling window, 50-day average volume baseline).
- **Usage:** Intermediate trend filtering and divergence detection.
- **Quote:** "The Volume Flow Indicator was designed to stay with the intermediate trend and avoid whipsaws... A crossover of the zero line indicates a change in the trend direction."
- **Rule:** Stay long while VFI > 0; exit or short when VFI < 0; heed divergences when price prints higher highs with lower VFI highs.

### Source 2: LazyBear (TradingView Script Page)
- **Market & Timeframe:** Multi-asset (Stocks, Crypto, Forex); daily and intraday.
- **Usage:** Ports Katsanos' formula to TradingView; plots VFI oscillator with optional signal line (EMA 5) and histogram.
- **Cites:**
  `MyTradingSys/research/_archive/loose_2026-10/T065_LAZYBEAR_SURVEY.md:61` "length 130, coef 0.2, vcoef (max volume cutoff) 2.5"
  `MyTradingSys/research/_archive/loose_2026-10/T065_LAZYBEAR_SURVEY.md:62` "coefficient 0.2 for daily and 0.1 for intraday"
- **Quote:** "This is a port of Markos Katsanos' Volume Flow Indicator (VFI). It is an indicator of money flow, designed to detect institutional buying and selling pressure."

### Source 3: TradingView Community / Practitioner Comments
- **Market & Timeframe:** Crypto (BTCUSDT, ETHUSDT), Forex; 4h, 1h, 15m.
- **Usage:** Validating breakout legitimacy versus low-volume bull traps.
- **Quote / Consensus:** "VFI filtering out low-volume churn is its biggest advantage over OBV. When price pushes into resistance with negative or declining VFI, it signals lack of buying effort."

### Source 4: Quantitative Trading Studies (QuantifiedStrategies & Modern TA Research)
- **Market & Timeframe:** Equities, ETFs, Crypto perps; daily and 1h.
- **Usage:** Macro trend-regime filter and exhaustion monitor.
- **Quote / Analysis:** "Divergence between VFI and price is the most robust signal of trend exhaustion. A lower high in VFI while price reaches higher highs highlights smart-money distribution."

## 3. Crypto / Bitcoin Filter

What survives and fails in 24/7 crypto markets:

- **What fails:**
  - *Default 130 lookback on 24/7 daily data:* 130 daily bars in equities is ~6 calendar months (trading days only); in 24/7 crypto, 130 daily bars is ~4.3 months, lagging rapid crypto regime rotations.
  - *Unadjusted cutoff on intraday:* Using daily cutoff `coef = 0.2` on 15m or 1h klines drops too much volume because intraday log price changes are smaller.
  - *Single-venue volume distortion:* Crypto perp volume can be distorted by fee promotions or internal wash-trading; VFI needs reliable venue volume.
  - *Trading zero crosses in range balance:* When BTC ranges, VFI fluctuates around zero, creating whipsaws if traded as a mechanical signal.
- **What survives:**
  - *Divergences at liquidity sweeps:* Bullish VFI divergence when BTC sweeps range lows confirms absorption; bearish divergence at range highs confirms distribution.
  - *Context column for level tests:* VFI falling into a support retest confirms lack of buyer effort (weak test); positive/rising VFI confirms demand.

## 4. Common Pitfalls and Parameters

- **SOURCED Parameters (Katsanos 2004 / LazyBear defaults):**
  - Length: 130 (SOURCED)
  - Coef (cutoff coefficient): 0.2 for daily, 0.1 for intraday (SOURCED, Katsanos)
  - Vcoef (max volume cutoff multiplier): 2.5 (SOURCED)
  - Signal length: 5 (SOURCED)
  - Smooth VFI: False (SOURCED, 3-bar SMA when true)
  - Inter-period stdev window: 30 (SOURCED)
- **Pitfalls in the wild:**
  - *Ignoring intraday coef:* Katsanos explicitly noted `coef = 0.1` should be used for intraday data to prevent over-filtering volume.
  - *Using VFI as a solo entry:* VFI is a lagging intermediate flow oscillator, not an execution trigger.
- **OURS (MTS design rules):**
  - *Context-only role:* VFI is an M5 volume/participation context column feeding level rejection and wick confirmation.
  - *Outputs:* Both raw VFI and 3-bar smoothed VFI exposed for research.

## 5. What It Measures

**What it measures:** Institutional volume participation and accumulation/distribution pressure (scaled rolling money flow above/below zero with volatility-threshold noise filtering and outlier volume capping).
