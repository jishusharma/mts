# Rule book: Session levels (Asia/London/NY highs and lows, sweeps)

Sources: CRAB = Toby Crabel, *Day Trading with Short-Term Price Patterns and Opening Range Breakout* (1990) (SOURCED via https://quantpedia.com/strategies/opening-range-breakout-strategy-in-individual-stocks/ fetched 2026-11-14); HUD = Michael J. Huddleston (Inner Circle Trader / ICT), 2022 YouTube Mentorship & Implementing The Asian Range (SOURCED via https://innercircletrader.net fetched 2026-11-14); TOM = Tom Vorwald transcripts (`MyTradingSys/items/T087_session_levels_observation_layer.md:23`, `MyTradingSys/research/fast_track_2026-09-27/BTC_SESSION_SWEEPS_2026-10-04.md:84-89`); FAB = Fabio Valentini transcripts (`MyTradingSys/research/fast_track_2026-09-27/BTC_SESSION_SWEEPS_2026-10-04.md:91-95`); KRO = Eric Krown TA 101 (`MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md:8`); FORM = `MyTradingSys/backtest/layers/FORMULAS.md:379` (`layers/session/session_momentum.py`); CODE = `MyTradingSys/backtest/layers/session_levels/session_levels.py:8-25`; LIVE = `MyTradingSys/tools/live_aid/tf_strip.js:106-123`; T087 = `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md`; SWP = `MyTradingSys/research/fast_track_2026-09-27/BTC_SESSION_SWEEPS_2026-10-04.md`.

**Result: Session levels establish temporal support/resistance boundaries from regional trading sessions (Asia, London, NY) and prior-day extremes; on BTC, naive failed-break or sweep-reclaim entries exhibit zero fee-net edge across all sessions, functioning strictly as contextual location filters rather than standalone directional triggers.**

## 1. What it measures
Horizontal price extremes (absolute high and absolute low) etched across defined temporal trading sessions:
- Asia session (Tokyo/Sydney/HK window: 00:00–08:00 UTC [OURS default] or 19:00–00:00 EST / 00:00–05:00 UTC [ICT definition]).
- London / European session (08:00–13:00/14:00 UTC [OURS default] or 07:00–13:30 UTC [standard cash]).
- New York / US session (13:30/14:00–20:00/21:00 UTC).
- Prior UTC day extremes (Previous Day High PDH, Previous Day Low PDL).
A session sweep measures a price probe that temporarily breaches a prior session extreme or prior day extreme by >= 1 tick, followed by a failure to hold acceptance and an immediate reclaim back inside the prior session boundary.
- Formula pointer: `MyTradingSys/backtest/layers/FORMULAS.md:379` Section 15 ("T055 C2 - intraday session momentum", `layers/session/session_momentum.py`). Causal failed-break event logic is implemented in `MyTradingSys/backtest/layers/session_levels/session_levels.py:8-25`.
- Verification status: `NOT VERIFIED-TV` (built from custom causal timestamp partitioning on Binance 1m klines, no TradingView Pine reference script on trunk).
- Code module: `MyTradingSys/backtest/layers/session_levels/session_levels.py`, `MyTradingSys/backtest/layers/alerts/live_session_levels.py`, and `MyTradingSys/tools/live_aid/tf_strip.js:106-123`.

## 2. Developer's own rules (SOURCED)
- **Toby Crabel (1990) — Opening Range Breakout (ORB) Foundations:**
  - *Origin:* Toby Crabel, *Day Trading with Short-Term Price Patterns and Opening Range Breakout* (1990) [SOURCED: https://quantpedia.com/strategies/opening-range-breakout-strategy-in-individual-stocks/].
  - *Definition:* The Opening Range is the high and low established during a fixed initial time window (e.g., 5m, 15m, 30m, 60m) following the official market open.
  - *The Stretch:* Calculated buffer added to ORH or subtracted from ORL (10-day average distance from open to nearest extreme) to prevent false breakout whipsaws.
  - *Directional Trigger:* Buy stop at ORH + stretch; sell stop at ORL - stretch.
  - *Volatility Prerequisite:* Breakouts are valid only following market contraction—specifically Narrow Range 7 (NR7: day's range is narrowest of the last 7 sessions) or Inside Days; trading breakouts after wide expansion days produces false breaks.
- **Michael J. Huddleston (ICT, 2022) — Asian Range & Session Liquidity Sweeps:**
  - *Origin:* Michael J. Huddleston, 2022 YouTube Mentorship & Implementing The Asian Range [SOURCED: https://innercircletrader.net].
  - *Asian Range Timeframe:* 19:00 to 00:00 NY time (or 20:00–00:00 / 00:00–05:00 UTC); characterized as the institutional "Accumulation" phase of the Power of 3 (AMD: Accumulation, Manipulation, Distribution) model.
  - *Liquidity Pools:* Asian High holds Buy-Side Liquidity (BSL, stops of early shorts & breakout longs); Asian Low holds Sell-Side Liquidity (SSL, stops of early longs & breakout shorts).
  - *The Judas Swing (Manipulation):* During the London open (02:00–05:00 NY time / 07:00–10:00 UTC) or NY open, interbank algorithms engineer a deliberate false breakout (liquidity raid/sweep) beyond the Asian high or low.
  - *Reclaim & Reversal Rule:* Price wicks beyond the Asian level, fails to sustain candle body closes outside, and produces a rapid Market Structure Shift (MSS) on lower timeframes (1m/5m) back inside the range. Entry is taken on a retracement to a Fair Value Gap (FVG) or Order Block targeting the opposing session extreme.

## 3. What the internet and crypto traders say
| Claim | Source URL | Evidence grade |
|---|---|---|
| Opening Range Breakout (ORB): buying above the opening range high or selling below the opening range low captures intraday momentum; adding Crabel stretch and NR7 contraction filters significantly improves Sharpe ratio | https://quantpedia.com/strategies/opening-range-breakout-strategy-in-individual-stocks/ | measured (quantitative index/equity backtest sample, though no crypto/perps fee accounting) [SOURCED] |
| ICT Asian Range Sweep: London open sweeps Asian Session High/Low to trigger retail stops before reversing into the true daily trend; confirmation requires lower-timeframe Market Structure Shift (MSS) and Fair Value Gap (FVG) retracement | https://innercircletrader.net | anecdote (pedagogical video mentorship, cherry-picked chart diagrams, zero costed trade ledger or quantitative sample) [SOURCED] |
| Asia session high/low breakouts in Forex/Crypto: sweeping the Asian range during London Killzone (02:00-05:00 NY time) provides high-probability mean reversion targeting the opposite side of the range | https://r2ftrading.com | anecdote (blog post, rule description without statistical trade log) [SOURCED] |
| TradingView Asian Range indicators automatically box 19:00-00:00 NY session and trigger alerts when wicks sweep liquidity pools | https://luxalgo.com | anecdote (vendor software documentation, no performance data) [SOURCED] |
| Tom Vorwald: "It's not true that there's any kind of stop hunting going on." Rejects ICT smart money conspiracy; views price excursions beyond prior-day levels as auction mechanics seeking two-sided liquidity | `MyTradingSys/research/fast_track_2026-09-27/BTC_SESSION_SWEEPS_2026-10-04.md:89` | anecdote (professional trader perspective, index futures focus) [SOURCED] |
| YouTube ICT Asian Sweep models on crypto claim 70-80% win rate when trading London sweeps of Asian lows | https://youtube.com (generic ICT crypto trading channels) | UNVERIFIED (promotional marketing claims, zero audited PnL or fee-net data) |

## 4. What our analysts say (extracts)
| Analyst | Their rule in plain words | File pointer |
|---|---|---|
| Tom | Large participants "usually have a readiness to act up here when a market shoots past the previous day's highs"; market "likes to run from liquidity to liquidity". Opening range size classifies the day: narrow opening range indicates trend day; very large opening range won't hold. Rejects ICT "stop hunt" narrative as conspiracy (`RwQBdF9TSvc:13`). | `MyTradingSys/items/T087_session_levels_observation_layer.md:23`, `MyTradingSys/research/fast_track_2026-09-27/BTC_SESSION_SWEEPS_2026-10-04.md:84-89` |
| Fabio | Defines Initial Balance (IB) as high/low of the first 30 minutes of regular cash trading. Trades "book sweeping" near range highs/lows or NY session highs as asymmetric risk entries, but strictly requires L2 order flow / footprint absorption. Notes London session is "not worth to trade for me" based on his own historical stats. | `MyTradingSys/research/fast_track_2026-09-27/BTC_SESSION_SWEEPS_2026-10-04.md:91-95` |
| Krown | BTC trades 24/7 so "daily close 00:00 UTC; 24/7 so no session." Defines market structure through dominant pivot highs and lows on daily/weekly charts, not intraday session brackets. No session-level sweep setups in TA 101. | `MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md:8` |
| NK (StockTalk) | NSE stock/index rules anchor on market opening bar; porting to 24/7 BTC: "a session open would stand in for the NSE open; untested". | `MyTradingSys/research/nk_stocktalk_1113/review/CHECKLIST.md:301` |
| CryptoCred | Support and resistance are derived horizontally from old highs and lows: "if in doubt sr it out works quite well so by definition horizontal support resistance is derived from old highs and lows". | `MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:378` |
| Rumers (Doug & Sylvia) | Looks for sucker-move red candles pushing into support/resistance boundaries: "First, I want to see a few red candlesticks in a row pushing straight into our lower magic line. I call that pattern the sucker move." | `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_3.md:149` |
| CCU | No extract mentions session levels or sweeps (focuses strictly on 50/200 MA, Stoch RSI, WaveTrend on 2D/1W macro charts). | `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md:1-35` |
| Habib / CBP | Sunday weekly plan: "The sweep of the low is optional"; no mechanical session-level rules. | `MyTradingSys/research/wiring_audit_2026-10/WIRING_TOM_FABIO_HABIB.csv:445` |
| Malkan | Every Malkan setup requires strictly OHLC price bars to compute Wilder RSI(14) on close; no session levels used. | `MyTradingSys/research/malkan_extract_2026-10-15/PRE_REG_MALKAN_GFS_BTC.md:64` |

## 5. OUR measurements
Pointers to our studies found by repository grep (study folder, no numbers per task instruction):
- `MyTradingSys/research/t087_session_levels_2026-10-09/` (`RESULT.md`, `summary.json`): Systematic evaluation of failed first break of prior-day high/low before 14:00 UTC on BTCUSDT 1m (2022–2026), testing Asia and EU session extreme targets versus spike stops with taker fees.
- `MyTradingSys/research/fast_track_2026-09-27/` (`BTC_SESSION_SWEEPS_2026-10-04.md`): T054 & T058 research study evaluating BTC session-open sweeps, DST-dependent volume peaks, London sweeps of Asia high/low, and opening-range predictive validity on multi-year 1m data.
- `MyTradingSys/research/session_sweeps/` (`session_open_study.py`, `results_2026-10-04.json`): Execution runner and underlying trial results for pre-US sweeps and session open directional persistence.
- `MyTradingSys/research/pre_us_failed_break_2026-10/` (`RESULT.md`): Pre-US failed-break short with 4-tranche scale-in on BTCUSDT 1m DEV dataset.
- `MyTradingSys/research/setup_alpha_beta_2026-10-10/` (`BETA_RESULTS.md`): 15m/1h liquidity sweep combined with CVD absorption and 5m market structure shift entry on Binance BTCUSDT perp.
- `MyTradingSys/research/layer_lab/session_levels_event_table/` (`REPORT.md`, `event_table.py`, `test_event_table.py`): Tabulation of failed break events across DEV 1m klines, recording touch/fail times, spike distance, and forward MFE/MAE.

## 6. How to read it now on Live Aid
- **Panel:** **Levels** and **Timeframe strip** (`MyTradingSys/tools/live_aid/live_aid.html`).
- **Where it appears:**
  - In the **Timeframe strip** header and levels engine (`MyTradingSys/tools/live_aid/tf_strip.js:106-123`), the system computes dynamic session reference marks from 1m klines:
    - Prior day high, Prior day low, Prior day close
    - Prior VAH, Prior VAL, Prior POC
    - Asia high, Asia low (Asia 00:00–08:00 UTC)
    - London high, London low (London 08:00–13:00 UTC)
    - Day VWAP (from 00:00 UTC)
  - In the **Levels** panel (`#p-levels`), nearest session extremes above and below the live price are displayed along with distance points and percentage offset.
  - In the **Map** view (`#playbook`, `map.js`), session tags indicate the active market window (`Asia 00-08Z`, `Europe 07-13Z`, `US 13-21Z`) with countdown chips to the next session open.

## 7. Confluence role
**LEVEL**
- What it adds confidence to: Provides horizontal structural reference lines for session-anchored liquidity mapping. Useful as an execution boundary where other confluence layers (e.g. Volume Profile Value Area edge, CVD order-flow absorption, or extreme RSI/WaveTrend divergence) must align before entering a mean-reversion fade or continuation breakout.
- Rule: Session levels and session sweeps are **never an entry by themselves** (no fee-net out-of-sample edge exists in repo testing; all raw failed-break rules fail or are inconclusive). They serve strictly as **Context / Level Location Filters** requiring independent structural and flow confirmation.

## 8. Open tests
- Card `edge-session-sweep-reclaim-1113` (not filed): Europe-low sweep then reclaim on BTC, ETH, and SOL using multi-asset pooled verification and explicit fee-net hurdle.
- Card `session-sweep-cvd-absorption` (not filed): Testing session level sweeps (Asia H/L swept in London, London H/L swept in NY) strictly gated by passive CVD absorption (divergent delta) and limit execution.
- Card `crabel-nr7-session-orb` (not filed): Testing Toby Crabel's NR7 volatility contraction filter prior to London/NY session opening range breakouts on BTC 15m.
