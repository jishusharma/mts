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
All rows OURS, copied from the named file. BTCUSDT 1m. No levels or prices quoted.
| Study folder | What was tested | n | Fee-net result | Verdict |
|---|---|---|---|---|
| `research/t087_session_levels_2026-10-09/RESULT.md` | Failed first break of the prior-day high/low before 14:00 UTC, close back through within 60 min, entry at that close, stop at the spike, target Asia or EU session extreme, net of 2 x 0.05% taker. Window 2022-01-01..2026-10-07 with NO DEV / VALIDATION / HOLDOUT cut (file's own note), so treat as base rate, not evidence | 913 events (466 high, 447 low); asia_target all touch sessions 911 | asia_target both sides net -0.036% (t -1.72), target 24% / stop 63% / neither 13%; high -0.023% (n 466), low -0.049% (n 445); 2025 -0.077% (t -2.45), 2026 -0.087%. eu_target both 269, net -0.049% (n < 300) | 1m: DO NOT USE (file: no edge; VERDICTS.csv INCONCLUSIVE, no cut) |
| `research/pre_us_failed_break_2026-10/RESULT.md` | Pre-US (07:00-13:00 UTC) failed break of PDH / early-session high / 5-day swing high, short, 4 tranches, DEV 2022-01-01..2024-06-30, taker 5 bp + 2 bp slippage | 176 episodes (228 signals) | mean net -0.0173% of K (SE 0.0520, t -0.33); win rate 61.4%; 154 of 176 days hit the time cap (sum -14.41% of K), 22 target days (+11.36% of K) | 1m: UNDERPOWERED (n 176 < 250; mean negative) |
| same file, regime mix | DEV 130 weeks | | bull 25 (19%), bear 0, range 105 (81%) | |
| `research/fast_track_2026-09-27/BTC_SESSION_SWEEPS_2026-10-04.md` | Pre-US sweeps (London sweeps Asia range, pre-US sweeps prior day high/low), US session direction, gross, no fee-net figure | not stated in the quoted bottom line (F6 n 59) | US session closes up 46-49% after such sweeps vs 48% base; first 30 min after a pre-US range sweep: 52% up either way; Tom opening-range rule: trend days 29% / 31% / 33% for small / mid / large range | CONTEXT ONLY (no direction edge; gross; DEV cut NOT_MEASURED in that file) |
| `research/layer_lab/session_levels_event_table/REPORT.md` | Failed-break event table, DEV through 2024-06-30, 4h forward MFE/MAE in R | 445 events (225 high, 220 low) | none: construction only, no fees or outcome | UNTESTED |
| `research/setup_alpha_beta_v2_2026-10/RESULT.md` (PDH/PDL sweep, 15m) | Plain sweep S0 and CVD arm S1, 1.5R / 90 min bracket, taker fees | S0 DEV 344 / VAL 148 | S0 mean R net DEV -0.470 (t -7.19), VAL -0.669 (t -4.82) | 15m: DO NOT USE |
Sweep-reclaim "0 of 12" (INDEX verdict, side-notes `edge-session-sweep-reclaim-1113_RESULTS.md`): file not in the repo, NOT_MEASURED here. Weekly/monthly levels, Asia high/low as a standalone level: NOT_MEASURED.

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
