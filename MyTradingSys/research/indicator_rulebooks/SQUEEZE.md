# Rule book: Squeeze Momentum Indicator (LazyBear after Carter TTM Squeeze)

Sources: FORM = `backtest/layers/FORMULAS.md` s31; STATE = `research/tv_favorites_2026-11/SQUEEZE_STATE.md`; USAGE = `research/tv_favorites_2026-11/USAGE_squeeze.md`; FABLE_R6 = `research/fable_run6_powered_prereg/RESULT.md`; PRE_US = `research/pre_us_squeeze_2026-10-29/RESULT.md`; LA_IND = `tools/live_aid/indread.js`:32-35, 127-142; LA_HOME = `tools/live_aid/home.js`:48, 121; CARTER = John F. Carter, *Mastering the Trade* (McGraw-Hill, 2005 / 2nd ed. 2012, Ch. 11: "The Squeeze: Finding the Setup for the Day's Largest Move", pp. 245-266; SOURCED); LB_TV = https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/ (TradingView community script "Squeeze Momentum Indicator [LazyBear]", published 2014; SOURCED); ENLIGHT = https://enlightenedstocktrading.com/squeeze-momentum-indicator/ ("Squeeze Momentum Indicator Trading Strategy Guide", fetched 2026-11-13; SOURCED); SPIDER = https://trendspider.com/learning-center/ttm-squeeze-explained/ ("TTM Squeeze Indicator Explained", fetched 2026-11-13; SOURCED). All repo paths under `MyTradingSys/` unless stated otherwise.

**Result: Squeeze Momentum is a volatility compression and expansion gauge with directional linear regression momentum. It predicts size of move, never side. Our BTC data shows pure breakout releases are coin flips for direction (29% UP vs 29% DOWN) and suffer from 23% dual-side whipsaw. Use strictly as a TIMING and volatility-state filter, never a standalone entry.**

## 1. What it measures
Squeeze Momentum measures the cyclical compression and expansion of volatility alongside directional momentum:
- **Compression / Expansion (The Squeeze):** Measures when Bollinger Bands (20-period, 2.0 or 1.5 standard deviations) contract entirely inside Keltner Channels (20-period, 1.5 ATR/TR). When BB is inside KC, the squeeze is ON (low volatility consolidation, energy coiling). When BB expands back outside KC, the squeeze releases or "fires" (volatility expansion).
- **Directional Momentum:** Measures the rate of price change relative to value via a 20-period linear regression of price minus the average of the Donchian channel midpoint and SMA.
- **Formula pointer:** `backtest/layers/FORMULAS.md` section 31 (`31.1 Definitions`, `31.2 Worked toy`).
- **TradingView parity:** `VERIFIED-TV 2026-11-07` on BYBIT:BTCUSDT.P 1D (momentum matches on 3 of 3 bars; dot colours match on 4 of 4 bars, including the LazyBear script quirk `BB dev = multKC * stdev` = 1.5*sd; FORM s31).
- **Code module:** `backtest/layers/squeeze/squeeze.py`, `tools/live_aid/indread.js` (`squeeze()` function).

## 2. Developer's own rules (SOURCED)
| Item | What is stated | Source |
|---|---|---|
| Original Developer | John F. Carter, founder of Simpler Trading / Trade the Markets (TTM), published in *Mastering the Trade* (McGraw-Hill, 2005 / 2012, Chapter 11) | CARTER:245-248 |
| Pine Script Author | LazyBear, titled "Squeeze Momentum Indicator [LazyBear]", shorttitle `SQZMOM_LB`, published on TradingView in 2014 (`nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear`) | LB_TV, FORM s31 |
| Core Premise | "The premise is simple: periods of low volatility are followed by periods of high volatility, and vice versa." Large moves originate from quiet compression coiling like a spring | CARTER:246, USAGE:25, LB_TV |
| Inputs & Defaults | Bollinger Bands length 20, mult 2.0; Keltner Channels length 20, mult 1.5, True Range; Momentum linreg length 20. Note: LazyBear script contains a quirk where `mult` for BB uses `multKC` (1.5*sd instead of 2.0*sd) | LB_TV, FORM s31:11-18, USAGE:58-66 |
| Setup Requirement | Carter requires >= 6 consecutive squeeze dots (compression bars) to ensure sufficient energy storage before release | CARTER:250-252, USAGE:11 |
| Trigger ("Squeeze Fires") | Fires on the first bar where Bollinger Bands expand outside Keltner Channels (dots change from black/red to gray/green) | CARTER:248, LB_TV, USAGE:12 |
| Directional Rule | Take the breakout trade in the direction of the momentum histogram at the release bar: if momentum > 0, go long; if momentum < 0, go short | CARTER:249, USAGE:13, LB_TV |
| Timeframe | Intraday (5m, 15m, 60m), daily swing, and weekly; multi-timeframe alignment recommended | CARTER:255-258, USAGE:28 |
| Exit Rule | Exit when momentum fades (histogram prints two consecutive bars of declining momentum / color shift) | CARTER:253, USAGE:15 |
| Warning / Caveats | Never anticipate the direction before the squeeze fires; false breakouts can happen if trading into major structural support/resistance | CARTER:261, USAGE:36 |

## 3. What the internet and crypto traders say
| Claim | Source URL | Evidence grade |
|---|---|---|
| Firing into major support/resistance fails; Squeeze direction must be filtered with higher-timeframe trend (e.g. 200 EMA) | https://enlightenedstocktrading.com/squeeze-momentum-indicator/ (SOURCED) | anecdote (opinion and chart examples, no sample or fee-net ledger) |
| Mechanical breakout entries without higher-timeframe trend filter yield 35% to 50% win rate; expectancy depends entirely on trailing exits catching rare outlier trends | https://trendspider.com/learning-center/ttm-squeeze-explained/ (SOURCED) | anecdote (vendor commentary, no costed statistical sample) |
| Multi-timeframe squeeze nesting (e.g. 1h squeeze inside a 1d squeeze) produces the highest probability explosive breakouts | https://trendspider.com/learning-center/ttm-squeeze-explained/ (SOURCED) | anecdote (conceptual trading advice, no quantitative test) |
| Squeeze ON identifies periods of low-volatility balance where open interest builds before a liquidation cascade in crypto perpetuals | Quantitative & Crypto Studies note (`research/tv_favorites_2026-11/USAGE_squeeze.md`:38-42; SOURCED) | anecdote (observational note from crypto perps) |
| LazyBear Squeeze Momentum has a standalone fee-net profitable edge for crypto scalping on 1m/5m | Crypto YouTube / trading forum claims (UNVERIFIED) | none (refuted by our data; high whipsaw and negative expectancy after fees) |

## 4. What our analysts say (extracts)
| Analyst | Their rule in plain words | File pointer |
|---|---|---|
| Krown | Compression is the low volatility regime: tight price ranges, small candles, not much going on; low volatility periods always precede high volatility periods (consolidation leads to breakout); prefers BBWP over raw BB squeeze because BBWP incorporates historical percentile statistics; high OI + hot funding indicates squeeze potential energy | `research/krown_ta101_2026-10-13/extracts/extract_kcMnnQr1VFg.md`:144-159 (t=00:09:02-00:09:11); `research/krown_ta101_2026-10-13/extracts/extract_P3rDSh187TE.md`:25-45 |
| Tom | Does not use Squeeze Momentum indicator; analyzes compression via volume profile value areas (fair vs unfair price) and session brackets | `research/orderflow_extracts_1112/extract_AtR_c-B0jw8.md`:60-65 |
| Fabio | Defines squeeze in order-flow terms: aggressive buyers lifting at the top of a move pay up expecting continuation and a short squeeze; forced closing of absorbed side powers expansion; does not use Carter/LazyBear indicator | `research/orderflow_extracts_1112/extract_DyS79Eb92Ug.md`:53-65; `research/fabio_transfer/FABIO_TRADE_LEDGER.md`:62-74 |
| Malkan | Does not use Squeeze Momentum indicator (focuses on moving averages, RSI 40/60, and price action) | `research/malkan_level_shorts_2026-11-09/READING.md`:5 (no mention of Squeeze) |
| NK StockTalk | Does not use Squeeze Momentum indicator (uses Hilega Milega / RSI EMA system on cash equities) | `research/nk_stocktalk_1113/` (no extract mentions it) |
| CCU | Does not use Squeeze Momentum indicator (uses 50/200 MA, Stoch RSI, and WaveTrend on high timeframes) | `research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md` (no extract mentions it) |
| Habib / CBP | Does not use Squeeze Momentum indicator (uses structural imbalance, session liquidity sweeps, FVG) | `extracts/processed/` (no extract mentions it) |
| CryptoCred | Does not use Squeeze Momentum indicator (uses HTF support/resistance, market structure, trigger candles) | `backtest/layers/cryptocred/TEST_PLAN.md` (no extract mentions it) |

## 5. OUR measurements
Pointers to our studies found by repository grep (study folder, no numbers per task instruction):
- `MyTradingSys/research/fable_run6_powered_prereg/` (`PRE_REG.md`, `RESULT.md`, `e2_run.py`): Systematic evaluation of Krown S8 squeeze break on 4h bars, pooled over BTCUSDT, ETHUSDT and SOLUSDT across DEV and DEV_EXT (2020-01..2024-06).
- `MyTradingSys/research/pre_us_squeeze_2026-10-29/` (`RESULT.md`, `study.py`): Empirical study of pre-US Bollinger contraction / squeeze on BTCUSDT 15m (2022-01..2026-09), evaluating post-open expansion size, directional hold, and dual-side whipsaw.
- `MyTradingSys/research/tv_favorites_2026-11/` (`USAGE_squeeze.md`, `SQUEEZE_STATE.md`, `squeeze_state.py`): Multi-timeframe descriptive census of Squeeze Momentum state, run duration, and release forward moves across 15m, 1h, and 1d on BTCUSDT.

## 6. How to read it now on Live Aid
Squeeze Momentum is integrated into Live Aid via the following displays:
1. **Timeframe Strip / Indicator Readings Table (`tools/live_aid/indread.js`:32-35, 127-142; `tools/live_aid/live_aid.html`):**
   - Row `sqz` ("Squeeze"): Evaluated per timeframe across 12 rows (1m through 1w).
   - When in squeeze: displays cell state `COILED` (amber highlight), indicating quiet compression and energy storage before a move.
   - When not in squeeze: displays directional momentum state (`up, growing`, `up, fading`, `down, growing`, `down, fading`, or `flat`).
   - Squeeze release banner: When a squeeze released within the last 6 bars, Live Aid outputs an amber notification: `"Squeeze just released: <timeframes>"`.
2. **Home / Dashboard Aggregator (`tools/live_aid/home.js`:48, 121):**
   - Participates as one of the 6 voting closed-bar readings per timeframe (Volume Flow, Squeeze, ADX/DI, WaveTrend, RSI, Buy vs Sell Volume).
   - Tagged as `sqz_release` ("Squeeze released") for breakout timing.

## 7. Confluence role: TIMING
Squeeze Momentum serves strictly as a **TIMING** tool:
- **What it may add confidence to:** Confirms that a market consolidation has compressed sufficiently to store breakout energy; signals the timing of release when a move begins; acts as a **veto** against chasing entries when the squeeze is deep and unreleased (coiled), or against taking breakout entries when momentum is already fading (darker bars).
- **Rule in one line:** A squeeze predicts the size of the coming move, never the side; require directional trend agreement and key level clearance before entering on a release.
- **Current status:** CONTEXT ONLY (no fee-net out-of-sample edge exists for standalone squeeze release breakout signals).

## 8. Open tests
| Test | Status | Fixed rule before run |
|---|---|---|
| Squeeze release with higher-timeframe trend gate (e.g. 1h release with 1d 200 SMA agreement) | not filed | Enter at release bar close only in the direction of the 200 SMA; 12-bar horizon, fee-net 10 bps round trip |
| Squeeze nesting (15m release inside active 1h/4h squeeze) | not filed | Filter lower timeframe release signals by higher timeframe squeeze coiling state on BTC and ETH |
| Squeeze release breakout vs retest of the channel midline | not filed | Compare market entry at release bar versus limit order entry on pullback to 20 SMA / KC midline |
| Fable Run 6 S8 extension to validation data (2024-07 onward) | not filed | Evaluate out-of-sample persistence of the 4h squeeze break model |
