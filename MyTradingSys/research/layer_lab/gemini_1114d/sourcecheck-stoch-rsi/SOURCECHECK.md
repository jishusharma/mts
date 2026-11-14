6 CONFIRMED / 4 CONTRADICTED / 2 NOT FETCHED

# Primary-Source Check: STOCH_RSI Rule Book

Target: `MyTradingSys/research/indicator_rulebooks/STOCH_RSI.md` (70 lines; read-only, not edited).
Scope: `MyTradingSys/research/layer_lab/gemini_1114d/sourcecheck-stoch-rsi/SOURCECHECK.md`.

## 1. Inventory of Rule Lines in STOCH_RSI.md

| Line(s) | Section | Rule / Claim Summary | Label in Rule Book | Cited Source |
|---|---|---|---|---|
| 10 | 1. What it measures | StochRSI formula & defaults `3, 3, 14, 14` | `VERIFIED-TV 2026-10-17` | `FORMULAS.md` s23 (`MyTradingSys/backtest/layers/FORMULAS.md:562`) |
| 11 | 1. What it measures | Code module pointers | (pointer) | `scripts/dev/chart_verify.py`, `MyTradingSys/backtest/layers/kurisko/stoch_core.py` |
| 16 | 2. Developer's own rules | Who: Chande & Kroll, *The New Technical Trader* (Wiley, 1994) | `SOURCED` | `INV_DEF`, `SC_DEF` |
| 17 | 2. Developer's own rules | Core premise: raw RSI fluctuates 30-70; stochastic formula increases sensitivity | `SOURCED` | `INV_DEF`, `SC_DEF` |
| 18 | 2. Developer's own rules | Scale & levels: 0.00-1.00 (or 0-100); OB 0.80 (80), OS 0.20 (20) | `SOURCED` | `SC_DEF`, `INV_DEF` |
| 19 | 2. Developer's own rules | Buy signal: drops below 0.20 and crosses back above 0.20 | `SOURCED` | `SC_DEF` |
| 20 | 2. Developer's own rules | Sell signal: rises above 0.80 and crosses back down below 0.80 | `SOURCED` | `SC_DEF` |
| 21 | 2. Developer's own rules | Centerline rule: crosses above/below 0.50 indicate bullish/bearish confirmation | `SOURCED` | `SC_DEF` |
| 22 | 2. Developer's own rules | Warnings & cautions: pinned in strong trends; counter-trend whipsaws; needs filters | `SOURCED` | `SC_DEF`, `INV_DEF` |
| 27 | 3. Internet / crypto traders | TradingView default (3, 3, 14, 14) K/D SMA smoothing, timing & crossover alerts | `SOURCED` (anecdote) | `https://www.tradingview.com/support/solutions/43000502334-stochastic-rsi/` |
| 28 | 3. Internet / crypto traders | StochRSI >0.80 / <0.20 false signals in isolation without MA/trend filters | `SOURCED` (anecdote) | `https://www.investopedia.com/terms/s/stochrsi.asp` |
| 29 | 3. Internet / crypto traders | Short-term swing failures and centerline (50) pullbacks in equity and index trading | `SOURCED` (anecdote) | `https://school.stockcharts.com/doku.php?id=technical_indicators:stochrsi` |
| 30 | 3. Internet / crypto traders | John Kurisko Quad Rotation: (9,3), (14,3), (40,4), (60,10) < 20, fast turns up | `SOURCED` (anecdote) | Apple Podcasts ep 472 (`KURISKO_SPEC.md` line 27) |
| 31 | 3. Internet / crypto traders | 4-RSI variant of Kurisko Quad Rotation (operator memory hypothesis) | `NO-SOURCE; unverified operator hypothesis` | `KURISKO_SPEC.md` line 15 |
| 36 | 4. Our analysts | CCU: HTF Stoch RSI >80 top, <20 bottom, Monthly <16 bear pocket | (extract) | `CCU_RULES_2026-10-31.md` lines 20-22, 86-88 (Video `OGAIlXwmV1Q`) |
| 37 | 4. Our analysts | CCU: Bull confirmation Rule 2 higher low on cross down, Rule 3 higher high on cross up | (extract) | `CCU_RULES_2026-10-31.md` lines 34-36, 142-148 (Video `OGAIlXwmV1Q`) |
| 38 | 4. Our analysts | CCU: Watch ~65 swing high on Monthly Stoch RSI as resistance | (extract) | `CCU_RULES_2026-10-31.md` lines 38, 158-160 (Video `OGAIlXwmV1Q`) |
| 39 | 4. Our analysts | Krown: redundant oscillators (RSI and Stochastic together) create noise | (extract) | `extract_INOCBmqQupc.md` line 392 |
| 40 | 4. Our analysts | Kurisko: Quad Rotation four stochastic lines under 20, fast turns up, exit >80 | (extract) | `extracts/processed/kurisko/QUAD_ROTATION.md` lines 8-17 |
| 41-46 | 4. Our analysts | Tom, Fabio, Malkan, NK, CryptoCred, Habib: no extract mentions StochRSI | (negative claim) | `none found` |
| 53-55 | 5. OUR measurements | Study pointers (`kurisko_2026-10-18`, `kurisko_quad_1103`, `rsi_kurisko_2026-10-09`) | `OURS` / `BLOCKED` / `CONTEXT ONLY` | Local study folders |
| 58-59 | 6. Live Aid | Panel not shown in `live_aid.html` | `OURS` (inspection) | `MyTradingSys/tools/live_aid/live_aid.html` |
| 62-65 | 7. Confluence role | Role: TIMING; context only, no fee-net OOS edge | `OURS` | (internal synthesis) |

## 2. Primary-Source Check (Rules Lacking Quotes or Marked UNVERIFIED / NO-SOURCE)

| ID | Rule Book Line | Status | Primary Source Checked | Verbatim Quote or NOT FETCHED | Notes |
|---|---|---|---|---|---|
| S2.1 | Line 16 (Who) | **CONFIRMED** | `https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi` (moved from `SC_DEF`) | "Developed by Tushar Chande and Stanley Kroll, StochRSI is an oscillator that measures the level of RSI relative to its high-low range over a set time period." | Also confirms 1994 book *The New Technical Trader*; publisher/subtitle not on page; `INV_DEF` returned HTTP 403. |
| S2.2 | Line 17 (Core premise) | **CONFIRMED** | `https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi` | "In their 1994 book, The New Technical Trader, Chande and Kroll explain that RSI can oscillate between 80 and 20 for extended periods without reaching extreme levels. Notice that 80 and 20 are used for overbought and oversold instead of the more traditional 70 and 30. Traders looking to enter a stock based on an overbought or oversold reading in RSI might find themselves continuously on the sidelines. Chande and Kroll developed StochRSI to increase sensitivity and generate more overbought/oversold signals." | Core premise confirmed; caveat: StockCharts says Chande & Kroll cited 80 and 20 rather than 30 and 70. |
| S2.3 | Line 18 (Scale & levels) | **CONFIRMED** | `https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi` | "The result is an oscillator that fluctuates between 0 and 1." / "A move above .80 is considered overbought, while a move below .20 is considered oversold." | 0-1 scale and .80/.20 levels confirmed; 0-100 chart scaling not stated on `SC_DEF` or `TV_HELP`. |
| S2.4 | Line 19 (Buy signal) | **CONTRADICTED** | `https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi` | "However, oversold is not the same thing as bullish; oversold conditions instead serve as a warning to watch for a bounce. A catalyst is still needed to solidify the low and signal an actual upturn. In this example, chartists could look for prices to break above the 10-day SMA or for StochRSI to break above .50, its centerline." | `SC_DEF` does not state crossing back above 0.20 as the buy signal; it cites breaking above .50 or the 10-day SMA. |
| S2.5 | Line 20 (Sell signal) | **CONTRADICTED** | `https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi` | "StochRSI moved above .80 in mid-October and early November (red arrows). These overbought readings suggested that the oversold bounce could end soon. Confirmation came when StochRSI moved back below .50 (red dotted lines). Chartists could also look for the stock to break back below its 10-day SMA to signal a short-term downturn." | `SC_DEF` cites moving back below .50 (centerline) or 10-day SMA for confirmation, not crossing back down below 0.80. |
| S2.6 | Line 21 (Centerline rule) | **CONFIRMED** | `https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi` | "As a bound oscillator, the centerline is at .50. StochRSI reflects an uptrend when consistently above .50 and a downtrend when consistently below .50." | Also: "The gap and moving average cross above .50 were short-term bullish signals." |
| S2.7 | Line 22 (Warnings & cautions) | **CONFIRMED** | `https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi` | "There will be whipsaws, even when using a 5-day SMA with 20-day StochRSI." / "This means it is important to use StochRSI with other aspects of technical analysis for confirmation." | Counter-trend caution also confirmed by `TV_HELP`: "Using Stoch RSI to make trades that go against the underlying trend is a dangerous proposition." |
| S3.1 | Line 27 (TV defaults) | **CONFIRMED** | `https://in.tradingview.com/support/solutions/43000502333-stochastic-rsi-stoch-rsi/` | "That being said, as a range bound indicator, the Stoch RSI's primary function is identifying crossovers as well as overbought and oversold conditions." / "The time period to be used in calculating the %K. 3 is the default." | Cited URL `43000502334-stochastic-rsi/` returned HTTP 404; live page `43000502333` confirms K=3, D=3 defaults and crossovers, but does not state 14,14 defaults or alerts. |
| S3.2 | Line 28 (Investopedia false signals) | **NOT FETCHED** | `https://www.investopedia.com/terms/s/stochrsi.asp` | NOT FETCHED (HTTP 403 Forbidden) | Cited URL unreachable; `SC_DEF` and `TV_HELP` independently confirm false signals without trend/confirmation tools. |
| S3.3 | Line 29 (SC swing failures / index) | **CONTRADICTED** | `https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi` | "Second, it can be used to identify the short-term trend. As a bound oscillator, the centerline is at .50. StochRSI reflects an uptrend when consistently above .50 and a downtrend when consistently below .50." | Cited `SC_DEF` does not mention "swing failures" or "index trading" (all chart examples are US equities: Boeing, FLR, CVX, Yahoo!). |
| S3.4 | Line 30 (Kurisko podcast) | **NOT FETCHED** | `https://podcasts.apple.com/us/podcast/472-the-3-scalping-setups-that-make-me-a-living-john-kurisko/id1037685976` | NOT FETCHED (Apple Podcasts HTML shell contains no transcript/rule text) | Audio-only page; local YouTube transcript extract (`QUAD_ROTATION.md`) covers the same interview. |
| S3.5 | Line 31 (4-RSI hypothesis) | **CONTRADICTED** | `extracts/processed/kurisko/QUAD_ROTATION.md` & `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md` | "It is four STOCHASTIC oscillators, not four RSIs. No source I opened ties Kurisko to RSI." | Confirmed NO-SOURCE in `KURISKO_SPEC.md` and 0 occurrences of RSI in the 8,940-word transcript (`QUAD_ROTATION.md`). |

## 3. Cited Local Quotes & Citations Not Found in Their File

1. `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md:20-22,86-88` (cited at `STOCH_RSI.md` line 36):
   - **Wrong video ID**: `STOCH_RSI.md` cites `Video OGAIlXwmV1Q`, whereas lines 20-22 and 86-88 are Video `FlDFTA4s7XE` (`"The stochastic RSI measures our momentum."`).
   - **Missing claim at cited lines**: the rulebook's Monthly Stoch RSI <16 bear market pocket claim is NOT in lines 20-22 or 86-88; it is in `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md:37,154-156` (Video `RxyY3WAntg4`: `"Bear Market Pocket on Stochastic RSI"`).
2. `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md:34-36,142-148` (cited at `STOCH_RSI.md` line 37):
   - **Wrong video ID**: `STOCH_RSI.md` cites `Video OGAIlXwmV1Q`, whereas lines 34-35 and 142-148 are Video `iwMbayybIVg` (`"Bull Market Confirmation Rule 2: Higher Low on Stoch RSI Cross Down"`).
   - **Off-by-one line cite**: line 36 is `"Altcoin Stated Entry Rule"` (`NOT_IN_DATA`), not Rule 2/3.
3. `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md:38,158-160` (cited at `STOCH_RSI.md` line 38):
   - **Wrong video ID**: `STOCH_RSI.md` cites `Video OGAIlXwmV1Q`, whereas lines 38 and 158-160 are Video `RxyY3WAntg4` (`"Monthly Stoch RSI Swing High Resistance Level"`).
4. `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_INOCBmqQupc.md:392` (cited at `STOCH_RSI.md` line 39):
   - **Paraphrase not found in file**: `STOCH_RSI.md` states `"running redundant oscillators (RSI and Stochastic together) creates noise without independent edge"` and cites `[00:00:13]`. Line 392 actually reads `"I've seen many technical analysis using MACD's, using stochastic RSIs, using whatever to effectively just wait for a cross and then enter into a longer or short position depending upon which direction it crossed. That will not work."` (timestamp `t=00:00:07` on line 393). The redundant-oscillators/noise claim does not appear in `extract_INOCBmqQupc.md`.
5. `extracts/processed/kurisko/QUAD_ROTATION.md:8-17` (cited at `STOCH_RSI.md` line 40):
   - **Partial line mismatch**: lines 8-17 define the four stochastic bands (Four stochastic bands on one chart, built on different lookbacks), whereas `"under 20"` is at `extracts/processed/kurisko/QUAD_ROTATION.md:31-37` (`"Quad rotation = all four bands under 20 at the same time"`), not lines 8-17.

## 4. Verified Local Pointers (Found as Cited)

- `MyTradingSys/backtest/layers/FORMULAS.md:562`: `"Chosen definition (TradingView \"Stoch RSI\" defaults 3, 3, 14, 14):"` and `"raw[t] = 100*(r[t] - min(r over the last stoch_len values)) / (max - min) over the same window"` — found.
- `scripts/dev/chart_verify.py:6,54`: `"Formulas: MyTradingSys/backtest/layers/FORMULAS.md s1 (RSI), s22 (Bollinger), s23 (StochRSI)."` and `"def stochrsi(closes, rsi_len=14, stoch_len=14, k_len=3, d_len=3):"` — found.
- `MyTradingSys/backtest/layers/kurisko/stoch_core.py:1`: `"Stochastic lines for the Kurisko quad rotation. Pure functions of closed bars, stdlib only."` — found.
- `MyTradingSys/research/kurisko_2026-10-18/RESULT.md:1-4` and `MyTradingSys/research/kurisko_2026-10-18/BLOCKED.md:1-5`: `"REFUSED: PRE_REG freezes 0 cells: nothing may be run"` — found.
- `MyTradingSys/research/layer_lab/kurisko_quad_1103/PRE_REG.md:3`: `"Status: **0 of 24 cells pass the count gate**."` — found.
- `MyTradingSys/tools/live_aid/live_aid.html:357,1088`: `"One momentum table: RSI, %B and WaveTrend zone/cross always"` — StochRSI absent as stated.
