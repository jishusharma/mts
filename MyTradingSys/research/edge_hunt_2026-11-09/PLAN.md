# Edge hunt plan 2026-11-09 (card edge-hunt-plan-opus-1109, decision d-edge-hunt-credit-wave-1109)

**Answer: 0 setups are proven, but most "failures" tested our proxy (fixed 1R or N-bar exit, taker fees on tight stops, every phase pooled, BTC alone at a large m), not the operator's or the traders' read. This wave tests 15 pre-registered trials, fixed in TRIALS.md before any result, built from what the operator actually looks at on a chart: a marked level, a sweep and first touch, RSI at 40/60 on several timeframes at once, wick or swing divergence, the higher-timeframe RSI and the cycle clock. 11 workers (5 Haiku, 3 Sonnet, 2 Opus, 1 Fable) cost 33.5 USD at most (cap 36). A trial that passes goes to testnet forward, not to a longer backtest (d-phase-first-method-1106).**

Plan only: no backtest was run for this page, and no repo code changed. Every number below is quoted from the file named next to it.

## 1. What was tested, and why each test failed

Source: research/VERDICTS.csv (147 rows = 48 ideas; BACKTEST_MAP_2026-11-09.md), the Tom/Fabio census and its two reviews, and the RESULT.md of each study named here. Why-codes: **FRAME** = wrong timeframe, session or phase for the trader's trade; **PROXY** = the entry or exit is ours, not the trader's (fixed 1R or N-bar exit, market entry on a close); **DATA** = the input the rule needs is missing (no delta, no cash session, no bear weeks); **POWER** = too few events at the m used; **REAL** = the label truly carries no direction (large n, every year negative).

| Family (study) | Best number | Why it failed | Code |
|---|---|---|---|
| Tom/Fabio auction classifier (auction_census 1108) | 1h 7y FAST_REJECTION gross -0.010 R, net -0.087 R gate-pass, n=1871, all 8 years negative; 2R / 3R targets -0.035 / -0.023 R (REVIEW_FABLE a) | 1R bracket and 1h bars: the traders work 5m/15m in session, take 30-40 % at more than 3R (TOM-091), and Fabio reads delta, which klines lack (auction_context.py:604) | REAL at 1h/1R; FRAME, PROXY, DATA for the traders' trade |
| Same classifier, 5m window | 67 fades, 42 % target first, fee 0.925 R mean, 10 pass the fee gate | 5-15 bps stops against 10 bps taker fees | PROXY (taker on tight stops), POWER |
| Session split of the same 1h fades | 00-04 UTC -0.003 R (n=622); 12-16 UTC -0.180 R (n=526) | Fading at the US open fights continuation (Argon root cause 5) | FRAME |
| Imbalance (Qriptal), 22 rows | n=3271, gross -0.007 %, cost 0.14 % | single concept, no context, N-bar exit | PROXY |
| WaveTrend crosses (atlas, c30 retest, volmatch) | excess equals the ATR state; 0 of 4 focal cells pass vs an ATR null | volatility, not direction | REAL (as coded) |
| Bollinger range rules (bb_range_to_range, bb_long_window) | n=9008, gross +0.012 %, cost 0.14 % | 2:1 bracket on 15m, taker | PROXY, REAL |
| tf_break / meta-label | 15-feature logistic, 4-bar trades, gross +0.020 % | 4-bar exit | PROXY |
| Jala SMA crosses | -0.82 % net | slow trigger, 0.20 % RT | REAL |
| Pre-US failed-break short, 10 symbols | n=1393, -2.47 bps of K, t -0.56, win 60.7 % | powered, still nothing | REAL (as coded) |
| Malkan divergence, MTF gate | 0 bear weeks in 360 (the monthly RSI never closed at or below 40 since 2017-08); 15m aligned long n=482, -0.080 % | the bear gate never fires; 10-bar exit; Holm m=48 | DATA (regime label), POWER, PROXY |
| Malkan window bands | every (TF, band) BLOCKed by the power gate; 1h bearish S3_10 -0.246 % | 10-bar exit, m=238 | POWER, PROXY |
| RSI 40/60 line behaviour | hold +1.5 points over a random walk on average; **another TF at the same line: hold +7 (1h), +12 (4h), +18 (12h), +17 (1d) points, all CIs above 0**; HTF bias agreeing with the bounce: hold -10 to -14 points | descriptive; every play cell BLOCKed at m=6; the confluence factor was never coded as a trade | POWER; the effect is untested as a trade |
| Reclaim at the close, stop on a close back beyond the level (4h) | n=114, net +0.271 %, CI -0.253..0.805 | 114 events | POWER (leans positive) |
| Krown S8 squeeze break 4h (fable_run6) | gross +0.131 %, n=420 | power; now on testnet forward (d-krown-4h-testnet-forward-start-1109) | POWER |
| Wicks, 5 weeks (wicks_2026-11) | 15m lower wick 38 % at R=1; sweep 45 % vs 32 %; V-sweep in Asia 68 % (n=19) | descriptive, no fees, one 5-week bear window | POWER, FRAME |
| Order flow (CVD divergence, absorption, fabio_of) | positive before costs, about 0.45 R cost per trade on 0.15 % stops (d-carry-dropped-leverage-direction-1106) | stop size vs taker fees; the live footprint writer stopped on 2026-10-03 | PROXY, DATA |
| Candle flip engine | 7 cells beat the recalibrated null at m=48; the gains are tiny | context, never a signal | REAL (as a signal) |
| Chronos zero-shot, SMA200 long-flat, published strategies | negative | - | REAL |

Patterns across the failures:
1. **Exit shape (PROXY).** Most rows exit after N bars or at 1R. Neither trader claims a 1R edge: Tom wins 30-40 % at more than 3R (TOM-091), Fabio 30-35 % at a large RR (Is1HvdfQm5c:245), and Malkan claims 1:5 to 1:30 (SEVEN_STAR_CAPTIONS.md s3). Fixed 2R/3R did not rescue the 1h fade, so exit shape alone is not the fix. It is still the untested half of every other family.
2. **Taker fees on structural stops under 20 bps (PROXY).** On 5m every wick trade pays 0.5-1.7 R. The MTS venue model is maker entry and target at 0 (fees.py:48 FEES_DERIBIT); hardly any study used it.
3. **Pooled phases (FRAME).** Fades should win in ranges and lose in trends. Studies pooled 3-7 years, and research_kit's regime label has **0 bear weeks** in 479 (klines_history_2017/README.md), so "by regime" splits only bull vs range.
4. **Power (POWER).** BTC alone at 1h+ cannot reach power at m=6-238. Pooled symbols (pre-US, 10 symbols) did reach power, and the answer was no.
5. **Real absences.** Large-n, every-year-negative labels (the 1h auction fade, WaveTrend crosses, Bollinger brackets, pre-US failed break) are dead as coded. This wave does not re-run them.

## 2. What was never tested
| Idea | Status | Where in this wave |
|---|---|---|
| RSI 40/60 bounce when another timeframe sits at the same line (the only consistent factor found) | described, never traded | eh-s3 |
| The operator's 5-layer Malkan level short (level + wick/swing divergence or a lower-high sweep + RSI under its MA under 60 + WT + daily/weekly RSI failing at 60) | stack written, uncounted (card malkan-level-short-4h-count-1109, raw) | eh-s1 |
| Malkan 7-star spinning top (sourced conditions, XFO49JlODxI) | never coded | eh-h1 |
| Malkan 7-star / 5-star MTF RSI grades, PRD/NRD 5-50 bars | label only (malkan_mtf.seven_star) | eh-h2 |
| Wick at an HTF level on first touch, with effort volume and reclaim speed, knife excluded (W plan, WICKS_NOTE s6) | plan only | eh-s2, eh-h3 |
| Price and time: speed-in and time-at-level before the reaction | GAP (WICKS_NOTE s4-5) | eh-h4 |
| RSI crossing under its MA below 60 as the trigger (stack layer 3) | never coded | eh-h5 |
| Confluence count, dose-response (more layers = more net R?) | never | eh-o1 |
| A phase label from the operator's clocks (cycle clock, weekly/monthly RSI zone) in place of the 0-bear-week regime | never | eh-o2 |
| A testnet promote/kill design that works at BTC's sample sizes | partly (Krown R7 fail rules A/B/C) | eh-f1 |
| Node-to-node target plus break-even, 5m/15m in session, HTF ladder | running: census-5m-15m-7y-session-ladder-1109 (tf-real-frame) | **not duplicated**; input to eh-f1 |
| Tom/Fabio rulebook from beginner videos | running: tom-fabio-rebuild-from-beginner-videos-1109 | **not duplicated** |
| Delta at the level, NY-session value area | cards tf-delta-at-level-testnet-log-1109, tf-ny-session-va-profile-1109 | not duplicated (live/testnet) |
| Range laddering (the operator's martingale) | proposal only until he decides (d-ladder-discuss-first-1106) | excluded |
| News bias, big candles with OI/CVD, top-trader ratio | their own cards; history too short for a fee-net count | excluded |

## 3. OPERATOR_LENS: how the operator reads a chart, in his own words

| # | His words (source) | What he looks at | Coded so far? | Testable idea in this wave |
|---|---|---|---|---|
| L1 | "suppose there is 40 line or there is 60 line ... if price is coming from the top and resting on the 60 line, is it bouncing or not? ... What other time frames are doing when it is bouncing ... 4 hour, 12 hour, 1 hour can also bounce on 60 ... what phase the Bitcoin is in ... do we wait for it to break or bounce?" (OPERATOR_DECISIONS.md d-rsi-40-60-line-behaviour-1104) | RSI14 at 40/60 as a line with a cushion, other timeframes at the same line, the phase | described only (rsi_40_60_line_behaviour RESULT.md); the multi-TF effect was never traded | eh-s3 (confluence bounce), eh-o2 (phase) |
| L2 | decision record (Lead paraphrase of his voice note), "VIX" = wicks: "the Friday 74,900 sweep (first try, bought back), what support is really there (confluence, first try, volume, CVD, order flow) ... a falling knife (news sell-off, no retracement) is never a wick to buy"; "MTS has to find a way to buy and sell into wicks with the whole context" (d-wicks-research-plan-first-1107) | sweep of a level, first touch, effort volume, speed of the reclaim, the knife | census only (blind wicks: no edge); context gate W1-W6 never built | eh-s2, eh-h3 |
| L3 | price and time (Steve, Jason: "something has to give, price or time") (d-wicks-research-plan-first-1107; WICKS_NOTE s5) | speed into a level, time spent at it | GAP | eh-h4 |
| L4 | his five marked 4h shorts C1 08-28, C2 09-04, V1 09-23, V2 10-06, C3 10-21 "including the no-divergence C3" (d-malkan-level-shorts-read-1109; READING.md) | a red/green level that already rejected, divergence on the wick or swing to swing (15-19 bars on 4h), a lower high that sweeps the last swing high, RSI under its MA under 60, the daily/weekly RSI falling back under 60 | the repo rule caught 1 of 5 (3-10 bars, close to close) | eh-s1, eh-h5, eh-o1 |
| L5 | "the Malkan 7 star setup, because it is just two more stars, so two more settings that we have to understand" (operator_questions.py list, 2026-11-08T19:40Z) | star grades, HTF RSI with daily divergence, the spinning top | label only | eh-h1, eh-h2 |
| L6 | "keep this in your Bible": the four-year cycle, two clocks, double bottoms (d-mts-bible-1106; BIBLE.md s1-s5) | cycle clock (peak + 363-406 d), 200-week SMA, monthly 20 SMA | cycle_bottom_flag.py (testnet, operator-called); never used as a phase label for setups | eh-o2 |
| L7 | "an edge is judged by market phase and by patterns that hold now" (d-phase-first-method-1106) | the current range 75.4-80.9k (BIBLE s2) | method adopted; the old studies pooled phases | every brief: HOLDOUT (2025-07+) stays sealed, and a survivor goes to testnet forward |
| L8 | "A stop follows the trade: direction, leverage and the plan's invalidation point ... never a fixed percentage" (d-stops-follow-trade-1106) | structural stop | the census used it; older studies did not | every brief: structural stop, no floor |
| L9 | "leveraged directional trades": cycle-bottom longs, session trades on Tom/Fabio levels (d-carry-dropped-leverage-direction-1106) | direction, levels | partly | eh-s2, eh-o1 |
| L10 | "Why don't we also launch our own modules ... to find out the edge the correct way ... understand how I think, and perhaps you will find something else" (operator_questions.py list, 2026-11-08T20:02Z) | the whole lens | - | this wave |

Testable ideas he uses that no test has coded (the wave's core): **multi-timeframe RSI line confluence (L1), wick at a level on first touch with effort and reclaim speed (L2), speed-in and time-at-level (L3), divergence on the wick or swing to swing scaled to the timeframe, and the lower-high sweep at a defended level (L4), the HTF RSI falling back under 60 as a gate (L4/L1), the spinning top and the MTF star grades (L5), and a phase label from his clocks (L6).**

## 4. The wave: 11 workers
| Slug | Model | max_usd | Trials | Lens | Wave |
|---|---|---|---|---|---|
| eh-h1-spinning-top-7star | Haiku 5.5 | 1.40 | T01 | L5 | 1 |
| eh-h2-malkan-star-grades | Haiku 5.5 | 1.40 | T02, T03 | L5 | 1 |
| eh-h3-first-touch-sweep | Haiku 5.5 | 1.40 | T04 | L2 | 1 |
| eh-h4-speed-time-at-level | Haiku 5.5 | 1.40 | T05 | L3 | 1 |
| eh-h5-rsi-ma-cross-trigger | Haiku 5.5 | 1.40 | T06 | L4 | 2 |
| eh-s1-malkan-level-short-4h | Sonnet 5.5 | 3.50 | T07, T08 | L4 | 2 |
| eh-s2-wick-level-context | Sonnet 5.5 | 3.50 | T09, T10 | L2, L9 | 2 |
| eh-s3-rsi-line-confluence | Sonnet 5.5 | 3.50 | T11, T12 | L1 | 2 |
| eh-o1-confluence-dose-response | Opus 5.5 | 5.00 | T13 | L4, L1, L2 | 3 |
| eh-o2-phase-lens | Opus 5.5 | 5.00 | T14, T15 | L6, L1 | 3 |
| eh-f1-testnet-design | Fable 5.1 | 6.00 | none (design) | L7, L8 | 4 |
| **Total** | | **33.50** | **m = 15** | | |

Waves of at most 4 (d-edge-hunt-credit-wave-1109): wave 1 = four Haiku, wave 2 = H5 and the three Sonnet, wave 3 = the two Opus (they read the wave 1-2 results), wave 4 = Fable (reads everything, including census-5m-15m-7y-session-ladder-1109 if it has landed). Launch each worker with `python scripts/dev/api_job.py launch <slug> --prompt-file MyTradingSys/research/edge_hunt_2026-11-09/workers/<slug>.txt --model <id> --max-usd <cap> --engine api`. About 25 USD of the credit stays in reserve (expires 2026-11-17).

## 5. Rules shared by every brief
| Item | Rule | Label |
|---|---|---|
| Splits | DEV = data start .. 2024-06-30; VALIDATION = 2024-07-01 .. 2025-06-30, read once and only for a trial that passed the DEV screen; HOLDOUT = 2025-07-01 onward, never loaded | repo convention (MyTradingSys/backtest/splits.py); sealing the HOLDOUT as the current phase is OURS |
| Data | Binance USD-M futures monthly klines and fundingRate from data.binance.vision (from 2019-09) via `MyTradingSys/backtest/fetch_binance_archive.py`; spot 2017-08+ (`--spot-history`) where 4h/1d need history; cached outside the repo | public; DNS block affects api/fapi only (d-futures-data-every-station-1109) |
| Symbols | BTCUSDT primary; ETHUSDT pooled where the brief says so (power) | OURS |
| Fees | Market entries: regime A (taker 5 bps per side) plus 2 bps RT slippage (FORMULAS.md s13) plus funding records. Limit entries at a level: regime B (FEES_DERIBIT: maker entry and target 0, taker stop and timeout) plus slippage on taker legs; a fill only when a later bar trades strictly through the limit; unfilled = no trade, counted | SOURCED fees.py / FORMULAS s13; fill rule OURS |
| R | fee_r = cost in bps / stop distance in bps; net R = gross R - fee_r; stop wins a same-bar tie | census convention |
| Stops | structural (sweep extreme, swing beyond the level, the candle extreme where the source says so), no floor, no buffer unless sourced | d-stops-follow-trade-1106 |
| Statistics | SE clustered by UTC day (week for 4h/1d); DEV screen: n >= 30, mean net R > 0 and 95 % CI lower bound > 0; VALIDATION once: one-sided p, Holm across the wave at m = 15 (TRIALS.md); report the MDE | OURS (repo practice) |
| Verdicts | PASS = DEV screen and VALIDATION Holm-significant with mean > 0 -> file a testnet-forward raw card; FAIL = DEV mean <= 0 at adequate power; INCONCLUSIVE otherwise | OURS |
| Context | every PRE_REG and RESULT carries `## Context` and a `Regime mix:` line (d-context-retest-1104, PRE_REG_TEMPLATE.md) | SOURCED decision |
| Labels | each parameter SOURCED (file:line) or OURS; no invented trader conditions; OURS values are chosen once, never tuned | card scope_out |

## 6. DECISIONS (OURS) taken in this plan
- The card's steps, scope_in and tests field (caption fetch, malkan_level_shorts_2026-11-09/, verify_extract_quotes.py) came from the 7-star caption card (fe14e397755b), which had already shipped. This plan follows the goal, done_when and note instead and writes only into research/edge_hunt_2026-11-09/.
- HOLDOUT (2025-07+) stays sealed for every worker, including the current-phase months. The testnet run is the out-of-sample record (phase-first). The operator's hand-picked 2025-26 shorts are in the HOLDOUT anyway and would be biased.
- One primary trial per Haiku worker and at most two per Sonnet/Opus worker, so the wave's m stays at 15. Every other split is labelled exploratory and cannot promote.
- eh-s1 executes the existing raw card malkan-level-short-4h-count-1109 rather than duplicating it. If another session holds that card, the worker stops.
- Workers that need wave 1-2 outputs (O1, O2, F1) run later. If an input is missing, they compute their own events from the rule text in their brief.
