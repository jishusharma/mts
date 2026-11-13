# Indicator rule book index (operator order 2026-11-13, OPERATOR_DECISIONS.md)

One row per indicator or layer. Template: `TEMPLATE.md`. Status: DONE = file exists with all 8 sections; PARTIAL = concept or usage doc exists but not in the template (the pointer says where); MISSING = nothing yet, a Gemini card `gemini-rulebook-<name>-1113` fills sections 2-4, 6-8 and a Sonnet pass fills section 5. Roles: TREND GATE / EXHAUSTION / FLOW / LEVEL / TIMING (proposed, OURS; none is an entry, no fee-net out-of-sample pass exists for any row). The "Layers" column holds `layer:<folder>` tokens for every folder under `MyTradingSys/backtest/layers`; `scripts/dev/rulebook_check.py` fails when a folder has no token here. Verdicts are one-line copies of study results; read the pointer before quoting.

## Indicators

| Indicator | Developer | Role | Status | Measurement verdict (max 8 words) | Live Aid panel | Pointer | Layers |
|---|---|---|---|---|---|---|---|
| ADX / DI | Wilder 1978 | TREND GATE | DONE | Cross no edge; 1d through-25 Rule A FAIL | not shown (Momentum no ADX column) | `research/adx_di_2026-11/HOW_TO_USE_ADX_1113.md`; `research/adx_1d_through25_2026-11-13/REPORT.md` | `layer:adx` |
| RSI | Wilder 1978 | EXHAUSTION | PARTIAL | All tested rules 0 of 384 fee-net | Momentum, Timeframe strip | `research/indicator_rulebooks/RSI.md` (Wilder book not opened; card `gemini-rulebook-rsi-1113`) | `layer:rsi` |
| WaveTrend | LazyBear | EXHAUSTION | DONE | Bare dots lose; trend gate helps sells | Momentum (wt1, wt2, zone, cross) | `research/indicator_rulebooks/WAVETREND.md` | `layer:wavetrend` |
| VFI | LazyBear after Katsanos 2004 | FLOW | PARTIAL | No outcome study; UNTESTED | not shown | `research/tv_favorites_2026-11/USAGE_vfi.md`, `VFI_STATE.md`; FORMULAS s32 (VERIFIED-TV 4/4) | `layer:vfi` |
| Squeeze Momentum | LazyBear after Carter | TIMING | DONE | State descriptive; Krown S8 break INCONCLUSIVE | Momentum (squeeze in `indread.js`/home) | `research/indicator_rulebooks/SQUEEZE.md`; `research/tv_favorites_2026-11/USAGE_squeeze.md`, `SQUEEZE_STATE.md`; FORMULAS s31 (VERIFIED-TV 4/4); `research/fable_run6_powered_prereg` | `layer:squeeze` |
| Moving averages (21/55 EMA, 200 SMA/EMA) | Krown canon; SMA/EMA classic | TREND GATE | PARTIAL | SMA200 long-flat Alpha FAIL; display only | Moving averages | `research/ma_layer_2026-11/MA_CONCEPTS.md`; `research/btc_ma_2026-10-03/Q_ALL_ma_findings.md`; `research/setup_alpha_beta_v2_2026-10` | none |
| Bollinger Bands | Bollinger | LEVEL | DONE | Range-to-range 0 of 6 cells net positive | Timeframe strip (Bollinger), Momentum (%B, BBw) | `research/indicator_rulebooks/BOLLINGER.md`; `research/bollinger_2026-10-14/SOURCES.md`; `research/bb_range_to_range_2026-11-04/RESULT.md`; `research/bb_dance_2026-10-30/RESULT.md` | none |
| Stochastic RSI | Chande and Kroll (not opened) | TIMING | MISSING | Quad Rotation count-only, BLOCKED, no outcome | not shown (chart legend only) | FORMULAS s23; `research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md`; VERDICTS.csv `kurisko_2026-10-18` | `layer:kurisko` |
| VWAP and value area | Dalton / Tom (value area) | LEVEL | PARTIAL | 80% rule 44% on BTC; VWAP fade FAIL | Momentum (vs VWAP), Value area and acceptance | `research/value_area_acceptance_2026-11-05/RESULT.md`; VERDICTS.csv `rumers_2026-11-01` R3 | none |
| CVD / taker delta | Fabio and channel | FLOW | PARTIAL | Price-vs-CVD divergence negative on 1m/5m | Timeframe strip (CVD column) | `research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md`; `research/orderflow_views_2026-10-14/RESULT.md` | none |
| Open interest | exchange data; Krown/Tom use | FLOW | DONE | Flush 0/10, crowding 0/24, forced-move 0/128 | What the money is doing | `research/indicator_rulebooks/OPEN_INTEREST.md`; `research/oi_side_2026-10-30/OI_CONCEPTS.md` | `layer:positioning` |
| Funding and long/short ratio | exchange data | FLOW | PARTIAL | Funding fade FAIL; ratio fade 0 of 2 | Funding and premium | `research/flow_layers_concepts_2026-10-28/README.md`; `research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md`; side-notes `edge2-ratio-fade-wide-1113_RESULTS.md` | `layer:positioning` |
| Liquidations | CoinGlass model / exchange feeds | LEVEL | DONE | Forward ledger only; nothing measured yet | Liquidations, Forced selling on other exchanges | `research/indicator_rulebooks/LIQUIDATIONS.md`; `research/liquidation_layer_2026-10-28/README.md` | none |
| Footprint / large trades | Harnett 2003 / Fabio | FLOW | DONE | Exit policies negative; footprint check pending | Timeframe strip (12h, 15m/1h footprint tags) | `research/indicator_rulebooks/FOOTPRINT.md`; `research/footprint_12h_1112/CHECK.md`; `research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md` | none |
| Trend lines | Krown; Malkan | LEVEL | PARTIAL | Audit FIX-FIRST; no outcome run | Timeframe strip (active trend line) | `research/trendlines_2026-10-17/REPORT.md`, `AUDIT_2026-10-18.md` | `layer:trendlines` |
| Pitchfork | Andrews / Schiff / Morge | LEVEL | DONE | PASS withdrawn; 4h net -0.011% | not shown | `research/indicator_rulebooks/PITCHFORK.md`; `research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md`; `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md` | `layer:pitchfork` |
| Session levels | Tom / Fabio / Krown | LEVEL | DONE | T087 no edge; sweep-reclaim 0 of 12 | Levels | `research/indicator_rulebooks/SESSION_LEVELS.md`; `research/t087_session_levels_2026-10-09/RESULT.md` | `layer:session_levels`, `layer:session` |
| Hilega Milega | NK StockTalk | EXHAUSTION | PARTIAL | NK rules 0 of 42; flip fee-bleed | not shown | `research/layer_lab/gemini_edge_1113/hilega-formula/FORMULA.md` (Gemini, web quotes UNVERIFIED); side-notes `NK_RSI_RESULTS.md` (not in repo) | none |

## Other layer folders (plumbing, strategy families, not single indicators; rows keep the checker honest)

| Folder | What it is | Role | Status | Pointer | Layers |
|---|---|---|---|---|---|
| fabio | Fabio order-flow family (CVD absorption, escalation, FVG) | FLOW | n/a (family) | `backtest/layers/fabio/FABIO_L1_REPORT.md` | `layer:fabio` |
| alerts | live BB top-reversal and candle-close alert emitters | TIMING | n/a (family) | `backtest/layers/alerts/` (BB row above) | `layer:alerts` |
| consensus | consensus hook / writer | n/a (plumbing) | n/a | `backtest/layers/consensus/README.md` | `layer:consensus` |
| cryptocred | CryptoCred setups (HTF retest) | LEVEL | n/a (family) | `backtest/layers/cryptocred/TEST_PLAN.md` | `layer:cryptocred` |
| krown | Krown TA 101 context and events | TREND GATE | n/a (family) | `research/krown_ta101_2026-10-13/KROWN_CONSOLIDATED.md` | `layer:krown` |
| pizzino | Pizzino bar count and swing states | TIMING | n/a (family) | `backtest/layers/pizzino/pizzino_indicators.py` | `layer:pizzino` |
| promotion | layer promotion registry | n/a (plumbing) | n/a | `backtest/layers/promotion/` | `layer:promotion` |
| tick | tick extremes, OI extremes flagger | FLOW | n/a (family) | `backtest/layers/tick/` | `layer:tick` |
| timeframe | timeframe registry and resample | n/a (plumbing) | n/a | `backtest/layers/timeframe/TEST_PLAN.md` | `layer:timeframe` |
| turn_of_candle | turn-of-candle timing | TIMING | n/a (family) | `research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md` | `layer:turn_of_candle` |
| wlow_bounce | weekly-low break and bounce detector | LEVEL | n/a (family) | VERDICTS.csv `wlow_bounce_bbrsi60_2026-10-16` (n=8, INCONCLUSIVE) | `layer:wlow_bounce` |

Status counts (indicator table, 18 rows): DONE 2 (ADX, WaveTrend), PARTIAL 15, MISSING 1 (Stochastic RSI). Folder rows are families or plumbing, status n/a, no card.
Status counts (indicator table, 18 rows): DONE 3 (ADX, WaveTrend, Bollinger Bands), PARTIAL 14, MISSING 1 (Stochastic RSI). Folder rows are families or plumbing, status n/a, no card.
Status counts (indicator table, 18 rows): DONE 3 (ADX, WaveTrend, CVD), PARTIAL 14, MISSING 1 (Stochastic RSI). Folder rows are families or plumbing, status n/a, no card.
Status counts (indicator table, 18 rows): DONE 4 (ADX, WaveTrend, Bollinger Bands, Footprint / large trades), PARTIAL 13, MISSING 1 (Stochastic RSI). Folder rows are families or plumbing, status n/a, no card.
Status counts (indicator table, 18 rows): DONE 4 (ADX, WaveTrend, Bollinger Bands, Funding and long/short ratio), PARTIAL 13, MISSING 1 (Stochastic RSI). Folder rows are families or plumbing, status n/a, no card.
Status counts (indicator table, 18 rows): DONE 6 (ADX, WaveTrend, Bollinger Bands, Footprint / large trades, Hilega Milega, Moving averages), PARTIAL 11, MISSING 1 (Stochastic RSI). Folder rows are families or plumbing, status n/a, no card.
Status counts (indicator table, 18 rows): DONE 8 (ADX, WaveTrend, Bollinger Bands, Open interest, Liquidations, Footprint / large trades, Pitchfork, Session levels), PARTIAL 9, MISSING 1 (Stochastic RSI). Folder rows are families or plumbing, status n/a, no card.
Status counts (indicator table, 18 rows): DONE 9 (ADX, WaveTrend, Bollinger Bands, Open interest, Liquidations, Footprint / large trades, Pitchfork, Session levels, Squeeze Momentum), PARTIAL 8, MISSING 1 (Stochastic RSI). Folder rows are families or plumbing, status n/a, no card.
