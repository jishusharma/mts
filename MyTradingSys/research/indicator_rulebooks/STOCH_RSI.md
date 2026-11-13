# Rule book: Stochastic RSI (Chande and Kroll 1994, "StochRSI")

Sources: FORM = `MyTradingSys/backtest/layers/FORMULAS.md` s23; KURI = `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md`; QUAD = `extracts/processed/kurisko/QUAD_ROTATION.md`; CCU = `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md`; KROWN = `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_INOCBmqQupc.md`; TV_HELP = https://www.tradingview.com/support/solutions/43000502334-stochastic-rsi/ (fetched 2026-11-13; SOURCED); INV_DEF = https://www.investopedia.com/terms/s/stochrsi.asp (fetched 2026-11-13; SOURCED); SC_DEF = https://school.stockcharts.com/doku.php?id=technical_indicators:stochrsi (fetched 2026-11-13; SOURCED). All paths relative to repository root unless noted.

**Result: Stochastic RSI is a fast second-derivative momentum oscillator ("momentum of momentum") designed to reach boundaries when raw RSI is flat. In our repository, Kurisko Quad Rotation outcome runs are BLOCKED with zero trade outcomes, and the indicator is not shown on Live Aid. Use it as a short-term TIMING gate or context, never as an unconfirmed bare entry.**

## 1. What it measures
The Stochastic RSI measures where the current Relative Strength Index (RSI) stands relative to its high-low range over a specified lookback period. It applies George Lane's Stochastic oscillator formula to Welles Wilder's RSI values rather than to raw price closes.
Formula pointer: `MyTradingSys/backtest/layers/FORMULAS.md` section 23:
`raw[t] = 100 * (r[t] - min(r, stoch_len)) / (max(r, stoch_len) - min(r, stoch_len))` where `r = Wilder RSI(rsi_len)` from FORMULAS s1; `K = SMA(raw, k_len); D = SMA(K, d_len)`. Defaults `3, 3, 14, 14` (`rsi_len 14, stoch_len 14, k_len 3, d_len 3`). Verified against TradingView and CoinGlass (`VERIFIED-TV 2026-10-17`).
Code module: `scripts/dev/chart_verify.py` (formula 23 implementation); Kurisko stochastic variant in `MyTradingSys/backtest/layers/kurisko/stoch_core.py`.

## 2. Developer's own rules (SOURCED)
| Item | What is stated | Source |
|---|---|---|
| Who | Tushar S. Chande and Stanley Kroll; published in *The New Technical Trader: Boost Your Profit by Plugging into the Latest Indicators* (John Wiley & Sons, 1994) | SOURCED (INV_DEF, SC_DEF) |
| Core premise | Raw RSI frequently fluctuates between 30 and 70 for extended periods without reaching overbought or oversold extremes; applying the stochastic formula to RSI increases sensitivity and generates timely extreme signals | SOURCED (INV_DEF, SC_DEF) |
| Scale & levels | Bounded 0.00 to 1.00 (or 0 to 100 on standard charting packages). Overbought threshold at 0.80 (80); oversold threshold at 0.20 (20) | SOURCED (SC_DEF, INV_DEF) |
| Buy signal | Indicator drops below 0.20 (oversold) and subsequently crosses back above 0.20 | SOURCED (SC_DEF) |
| Sell signal | Indicator rises above 0.80 (overbought) and subsequently crosses back down below 0.80 | SOURCED (SC_DEF) |
| Centerline rule | Crosses above the 0.50 centerline indicate bullish momentum confirmation; crosses below 0.50 indicate bearish momentum confirmation | SOURCED (SC_DEF) |
| Warnings & cautions | In strong trends, StochRSI can become pinned at 0 or 100 (or above 80 / below 20) for extended intervals; trading counter-trend extremes directly can produce whipsaws, requiring trend filters or centerline confirmation | SOURCED (SC_DEF, INV_DEF) |

## 3. What the internet and crypto traders say
| Claim | Source URL | Evidence grade |
|---|---|---|
| TradingView default Stoch RSI (3, 3, 14, 14) with K and D SMA smoothing provides short-term reversal timing and crossover alerts | https://www.tradingview.com/support/solutions/43000502334-stochastic-rsi/ | anecdote (vendor definition, SOURCED) |
| StochRSI overbought (>0.80) and oversold (<0.20) signals reflect momentum of momentum, but generate false signals in isolation without moving average / trend filters | https://www.investopedia.com/terms/s/stochrsi.asp | anecdote (educational guide, SOURCED) |
| StochRSI can be used to identify short-term swing failures and centerline (50) pullbacks in equity and index trading | https://school.stockcharts.com/doku.php?id=technical_indicators:stochrsi | anecdote (charting guide, SOURCED) |
| John Kurisko Quad Rotation: four stochastic oscillators (9,3), (14,3), (40,4), (60,10) simultaneously dropping below 20 produce a high-probability reversal scalp when the fast line turns up | https://podcasts.apple.com/us/podcast/472-the-3-scalping-setups-that-make-me-a-living-john-kurisko/id1037685976 | anecdote (practitioner interview S1 in KURISKO_SPEC.md:27; SOURCED) |
| 4-RSI variant of Kurisko Quad Rotation (operator memory hypothesis) | `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:15` | none (NO-SOURCE; unverified operator hypothesis) |

## 4. What our analysts say (extracts)
| Analyst | Their rule in plain words | File pointer |
|---|---|---|
| CCU (Crypto Crew University) | On high timeframes (2-Month, Monthly), Stoch RSI >80 marks cycle top zone; cross downs mark cyclical peaks; <20 marks cyclical bottom zone. Monthly Stoch RSI <16 defines the bear market pocket | `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md:20-22,86-88` (Video OGAIlXwmV1Q, 2026-10-31) |
| CCU (Crypto Crew University) | Bull market confirmation rules: Rule 2 is a higher low in price when Stoch RSI crosses down; Rule 3 is a higher high in price when Stoch RSI crosses back up | `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md:34-36,142-148` (Video OGAIlXwmV1Q, 2026-10-31) |
| CCU (Crypto Crew University) | Watch the ~65 swing high level on Monthly Stoch RSI as structural resistance in bear market rallies | `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md:38,158-160` (Video OGAIlXwmV1Q, 2026-10-31) |
| Krown | Stated warning: Traders use MACDs, Stochastic RSIs, etc., to wait for crosses, but running redundant oscillators (RSI and Stochastic together) creates noise without independent edge | `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract_INOCBmqQupc.md:392` (Video INOCBmqQupc [00:00:13]) |
| Kurisko (via DayTradingRadio) | Quad Rotation: four stochastic lines (9,3 / 14,3 / 40,4 / 60,10) under 20 on 1m/5m; enter when the fast line turns up; exit on rotation above 80 | `extracts/processed/kurisko/QUAD_ROTATION.md:8-17` (Video PjigwAmhiT0 [13:22, 16:20]) |
| Tom | No extract mentions Stochastic RSI (focus is volume profile, value areas, and session VWAPs) | none found |
| Fabio | No extract mentions Stochastic RSI (focus is CVD absorption, footprints, and volume imprints) | none found |
| Malkan | No extract mentions Stochastic RSI (focus is Wilder 14-period RSI 40/60 momentum zones) | none found |
| NK (StockTalk) | No extract mentions Stochastic RSI (focus is Hilega Milega RSI/WMA/EMA setup) | none found |
| CryptoCred | No extract mentions Stochastic RSI (focus is support/resistance, market structure, and HTF ranges) | none found |
| Habib / CBP | No extract mentions Stochastic RSI (focus is orderbook liquidity and DOM positioning) | none found |

## 5. OUR measurements
Table of study pointers only (no numbers per task scope; numbers to be filled by Sonnet pass):

| Study folder | What was tested | Pointer to artifacts | Verdict |
|---|---|---|---|
| `MyTradingSys/research/kurisko_2026-10-18/` | Kurisko Quad Rotation event counts and execution feasibility on BTC 1m/5m | `PRE_REG.md`, `count_events.py`, `BLOCKED.md`, `RESULT.md` | UNDERPOWERED / BLOCKED (count-only, no outcome run) |
| `MyTradingSys/research/layer_lab/kurisko_quad_1103/` | Kurisko quad rotation multi-band stochastic preregistration and gate analysis | `PRE_REG.md`, `gate.csv`, `counts.csv` | UNTESTED / BLOCKED |
| `MyTradingSys/research/rsi_kurisko_2026-10-09/` | Sourced specification and verification of Kurisko Quad Rotation setup vs 4-RSI hypothesis | `KURISKO_SPEC.md`, `RSI_HISTORY.md` | CONTEXT ONLY (spec-only, no backtest run) |

## 6. How to read it now on Live Aid
Panel: not shown.
Inspection of `MyTradingSys/tools/live_aid/live_aid.html` confirms that Stochastic RSI is not rendered in any Live Aid panel (Momentum panel renders Wilder RSI 14, WaveTrend wt1/wt2, Bollinger Band %B/BBw, and Squeeze, but has no Stochastic RSI column; chart legend displays layout elements only).

## 7. Confluence role
Role: TIMING.
What it may add confidence to: Stoch RSI can act as an exhaustion timing filter on lower timeframes (e.g. 5m/15m) when price pulls back into a high-timeframe trend or value zone, or as a macro cycle exhaustion flag (>80 / <20 on 2M/Monthly per CCU).
Rule in one line: In an existing directional bias or regime, wait for Stochastic RSI to hook out of the extreme zone (<20 for longs, >80 for shorts) to trigger entry timing; never trade a raw cross against the trend.
Current repo status: Context only (no fee-net out-of-sample edge established).

## 8. Open tests
- `gemini-kurisko-outcome-1114` (or not filed): Backtest Kurisko Quad Rotation (9,3 / 14,3 / 40,4 / 60,10) fast-turn-up long entries on BTCUSDT 1m and 5m closed bars with taker fees (14 bps round trip) and 12-bar fixed exit; rule fixed before run.
- `stochrsi-cross-filter-1114` (not filed): Test TradingView default Stoch RSI (3, 3, 14, 14) K/D crossover in oversold (<20) and overbought (>80) zones on 15m and 1h BTCUSDT as an entry gate for 21/55 EMA trend-following setups vs bare EMA crosses.
- `ccu-stochrsi-pocket-1114` (not filed): Test CCU Monthly Stoch RSI bear-pocket rule (<16) and cycle top (>80 cross-down) on historical BTC monthly/weekly closes to assess multi-week drawdown forecasting.
