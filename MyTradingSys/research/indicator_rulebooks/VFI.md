# Rule book: Volume Flow Indicator (LazyBear after Katsanos, "VFI_LB")

Sources: FORM = `backtest/layers/FORMULAS.md` s32; USG = `research/tv_favorites_2026-11/USAGE_vfi.md`; ST = `research/tv_favorites_2026-11/VFI_STATE.md`; ENG = `backtest/layers/vfi/vfi.py`; LA = `tools/live_aid/home.js`:103-121, 282-297; IND = `tools/live_aid/indread.js`:13, 79-80, 100-107; KAT = Markos Katsanos, "Using Money Flow to Stay with the Trend", *Technical Analysis of STOCKS & COMMODITIES*, June 2004, and author website https://mkatsanos.com/; LB = LazyBear, "Volume Flow Indicator [LazyBear]", TradingView script `VFI_LB` (URL https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/); QS = QuantifiedStrategies, "Volume Flow Indicator (VFI) Backtest", https://www.quantifiedstrategies.com/volume-flow-indicator-vfi/. All paths under `MyTradingSys/` unless noted.

**Result: VFI is a volume-flow trend and institutional participation oscillator filtering price noise and volume spikes. The developer uses zero-line crosses and divergences for intermediate trend; our tests have no outcome study yet (UNTESTED). Use as a FLOW context column, not an execution trigger.**

## 1. What it measures
Institutional money flow and accumulation/distribution pressure over a rolling lookback window. Katsanos engineered VFI to resolve defects of On-Balance Volume (OBV) by substituting typical price `(H+L+C)/3` for close, filtering minor price changes below a volatility threshold (`cutoff = coef * stdev(ln(typ/typ[1]), 30) * close`), capping anomalous volume spikes at `2.5 * SMA(volume, 50)` (in LazyBear: `vcoef * SMA(volume, length)[1]`), and summing signed volume over a finite lookback (130 bars) scaled by average volume.
- Formula pointer: `backtest/layers/FORMULAS.md` section 32.
- TradingView parity: `VERIFIED-TV 2026-11-07`, login C (4/4 daily bars on BYBIT:BTCUSDT.P match within 1 decimal display: 2026-10-04 0.6 vs +0.641, 2026-10-08 -0.7 vs -0.736, 2026-10-09 1.4 vs +1.436, 2026-11-06 8.5 vs +8.518; `backtest/layers/FORMULAS.md`:716).
- Code module: `backtest/layers/vfi/vfi.py`.

## 2. Developer's own rules (SOURCED)
| Item | What is stated | Source |
|---|---|---|
| Who | Markos Katsanos (creator, mechanical systems designer), June 2004 *Technical Analysis of STOCKS & COMMODITIES* article "Using Money Flow to Stay with the Trend" (USG:7-8, KAT); ported to TradingView Pine Script by LazyBear (shorttitle `VFI_LB`, script `MhlDpfdS`, LB) | USG:7-8, KAT, LB |
| Defaults | Lookback length 130 bars; volatility cutoff coefficient `coef = 0.2` (daily); max volume cap multiplier `vcoef = 2.5`; inter-period log-return stdev length 30; signal length 5 (EMA); smooth VFI false (3-bar SMA when enabled) | SOURCED (USG:58-64, LB, KAT, FORM s32.1) |
| Intraday coef | Katsanos explicitly notes `coef = 0.1` should be used for intraday charts because intraday price log-changes are smaller | SOURCED (USG:30, 60, 66, KAT) |
| Stated use: Zero line | Zero acts as the divider between institutional accumulation and distribution: VFI > 0 indicates net buying / bull trend; VFI < 0 indicates net distribution / bear trend. A cross of zero indicates an intermediate trend shift | SOURCED (USG:14, 22-23, KAT) |
| Stated use: Signal line | LazyBear script includes a 5-period EMA signal line (`vfima`) and histogram of `vfi - vfima` for entry/exit triggers | SOURCED (USG:27, LB) |
| Stated use: Divergence & Patterns | Divergences between VFI and price are the primary signal of exhaustion/reversal (lower VFI high while price makes higher high = distribution). Sharp "V" patterns in VFI frequently precede price turns | SOURCED (USG:15, 23, 41, KAT) |
| Timeframe | Designed for intermediate daily trend on US equities (130 trading days ≈ 6 calendar months). Intraday requires adjusted coef (0.1) | SOURCED (USG:20, KAT) |
| Warnings | The page states no mechanical stop-loss, position sizing, or profit targets; designed to stay with the intermediate trend, not trade noise | SOURCED (USG:22, KAT, LB) |

## 3. What the internet and crypto traders say
| Claim | Source URL | Evidence grade |
|---|---|---|
| Zero-line crossover strategy yields low win rate (40-45%) but high payoff ratio by staying with multi-month institutional trends; high drawdown if traded without stops | QuantifiedStrategies (https://www.quantifiedstrategies.com/volume-flow-indicator-vfi/) [fetched] | measured (equities/ETFs historical data, no crypto fee model) |
| Macro trend filter: trading long only when VFI > 0 above 200 SMA prevents chop and improves win rate compared to bare oscillator crosses | QuantifiedStrategies (https://www.quantifiedstrategies.com/volume-flow-indicator-vfi/) [fetched] | measured (long-term backtest, costed sample unspecified) |
| Crypto 24/7 distortion: default 130 daily bars in crypto is ~4.3 calendar months vs ~6 calendar months in equities; unadjusted daily coef (0.2) on 15m/1h crypto klines over-filters volume churn | USAGE_vfi.md (USG:48-50) | anecdote (MTS practitioner note, T3) |
| Divergence at liquidity sweeps: bullish VFI divergence when BTC sweeps range lows confirms absorption; bearish divergence at highs confirms distribution | USAGE_vfi.md (USG:53-54); TradingView community | anecdote |
| VFI filtering of low-volume churn is superior to OBV when price tests support/resistance; negative or declining VFI during resistance tests signals lack of buyer effort | USAGE_vfi.md (USG:36); TradingView practitioner consensus | anecdote |
| Signal line crossover (VFI cross 5 EMA) generates early swing entry triggers | TradingView script comments (https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/) | UNVERIFIED |

## 4. What our analysts say (extracts)
Grep across our canonical extract repositories (`research/**/extract_*.md`, `research/krown_ta101_2026-10-13/*.md`, `research/nk_stocktalk_1113/*.md`, `research/yt_feed_2026-10-31/*.md`):
| Analyst | Rule in plain words | Pointer |
|---|---|---|
| Eric Krown | No extract mentions Volume Flow Indicator or VFI (Krown uses CVD, OBV, 21/55 EMA, SMA200, Squeeze, WaveTrend) | none found |
| Tom (The Trader) | No extract mentions VFI (Tom uses VWAP, Value Area, Session Levels, Volume Profile) | none found |
| Fabio | No extract mentions VFI (Fabio uses CVD absorption, footprint, FVG, tape delta) | none found |
| Malkan | No extract mentions VFI (Malkan uses trendlines, swing breaks, multi-timeframe candle counts) | none found |
| NK (StockTalk) | No extract mentions VFI (NK uses Hilega Milega / modified RSI+MA+WMA) | none found |
| CCU (Crypto Crew University) | No extract mentions VFI (CCU uses 50/200 MA, WaveTrend, Stoch RSI on 2d/12d) | none found |
| Habib / CBP | No extract mentions VFI (Habib uses CVD divergences, delta clusters, order book liquidity) | none found |
| CryptoCred | No extract mentions VFI (CryptoCred uses HTF support/resistance retests, market structure) | none found |

## 5. OUR measurements
All studies below are descriptive or baseline state evaluations only. VFI itself has no outcome study and no fee-net performance run in our repository:
| Study folder | What was tested | n | Fee-net result | Verdict |
|---|---|---|---|---|
| `research/tv_favorites_2026-11/VFI_STATE.md` | Descriptive state evaluation of Bybit BTCUSDT linear public klines over 90 days (2026-08-09 to 2026-11-07), raw VFI (130, 0.2, 2.5, 30, 3): 1d zero crosses (n=6), 15m zero crosses (n=310), and behavior leading into 2026-11-06 15:00Z sweep bar (n=19); descriptive only, no trade simulation, no fees | 1d n=90 bars, 15m n=8640 bars | No trade rules or fees simulated; descriptive baseline | UNTESTED |
| `research/tv_favorites_2026-11/USAGE_vfi.md` | Specification and usage mapping note for VFI engine context columns (`SPEC_ENGINES.md` B); no backtest run | n/a | No backtest run | UNTESTED |
| `backtest/layers/FORMULAS.md` s32 | Toy unit test and TradingView golden series parity check (`backtest/layers/vfi/test_vfi.py`); verified parity against BYBIT:BTCUSDT.P 1d on 4 bars | 4 bars | Golden test pass (no trading outcome) | UNTESTED |

Regime mix: No regime-stratified backtest exists. Per timeframe:
- 1m, 5m, 15m, 1h, 4h, 1d: UNTESTED.

## 6. How to read it now on Live Aid
VFI is integrated into Live Aid as a money flow context gauge across two dashboard locations:
1. **Indicator Readings Table / Voting Grid (`tools/live_aid/indread.js`:13, 79-80; `tools/live_aid/live_aid.html`):**
   - Row `vfi` ("Volume flow"): Evaluated across timeframes using closed bars (`h, l, c, v, 130, 0.2, 2.5, 30, 3`).
   - Requires at least 263 bars (`max(30, 130) + 130 + 3`) to calculate; if fewer, displays `"needs 263 bars"`.
   - Cell displays smoothed VFI value with sign and slope: e.g., `+4.8 ↑` (green if `f > 0`, red if `f < 0`, grey if 0).
   - Live Aid combines VFI slope with CVD delta: when 15m price rises and both VFI is rising and buyers lead, reports `"15m rise is backed by volume"`; if volume/flow does not confirm, warns of `"pullback risk"` (`indread.js`:104-107).
2. **Home / Dashboard Overview Cards (`tools/live_aid/home.js`:113-121, 282-297):**
   - Under the **Volume** card (`volRead()`), displays `"Money flow (VFI):"` badge chips for `15m`, `1h`, `4h` showing state `in` (above zero), `out` (below zero), or `flat`, with `▲` (rising) or `▼` (falling) arrows.
   - Under the **Who is winning** card (`indCard()`), VFI serves as one of the 6 voting closed-bar readings (Volume Flow, Squeeze, ADX/DI, WaveTrend, RSI, buy-vs-sell volume) where a lead of 2 or more votes decides whether buyers, sellers, or mixed are winning on that timeframe.

## 7. Confluence role: FLOW
VFI is assigned the role **FLOW**.
- **Role rule:** May add confidence to a level test, breakout, or sweep setup by confirming whether institutional volume flow agrees with price direction (VFI > 0 and rising confirms buyer commitment; VFI < 0 and falling confirms distribution). May veto a long breakout when price pushes higher on negative or declining VFI (exhaustion / volume divergence).
- **Execution constraint:** VFI is never an entry trigger by itself; no fee-net out-of-sample edge exists. Status today: **context only**.

## 8. Open tests
| Card / Study | What is tested | Rule fixed before run |
|---|---|---|
| not filed | VFI zero-line filter on 1h BTC trend-following setups | Enter long only when 1h VFI > 0; short only when 1h VFI < 0; test incremental fee-net Sharpe vs unfiltered |
| not filed | Intraday cutoff calibration (`coef = 0.1` vs `0.2`) on 15m and 1h BTC klines | Measure volume filtering percentage and lag difference between 0.1 and 0.2 on BTCUSDT perpetuals |
| not filed | VFI bullish / bearish divergence at key liquidity sweeps (15m/1h) | Enter on sweep-and-reclaim only when confirmed by VFI divergence (lower price low with higher VFI low); 0.10% taker fee round-trip |
| not filed | 24/7 crypto lookback sensitivity (80, 100, 130 bars) | Test whether shorter lookback (e.g. 90-100 bars) better matches crypto 24/7 velocity compared to equities 130 bars |
