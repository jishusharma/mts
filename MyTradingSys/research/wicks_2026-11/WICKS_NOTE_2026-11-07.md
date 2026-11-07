# Wicks: how MTS buys and sells into them (research note + plan, 2026-11-07, Lead C)

Operator ask (voice, 2026-11-07, "VIX" = wicks): understand how wicks form on 5m/15m, where they form in the recent trend
(5 weeks down), the price-and-time idea (Steve, Jason: "something has to give, price or time"), the Friday 15m wick that
swept the 74,900 low (first attempt, bought back), what support really is there (confluence, first try, volume, CVD, order
flow), and the context gap: a falling knife (news sell-off, no retracement) is not a wick to buy. "MTS has to find a way."
Status: PROPOSAL. Measurement below is descriptive (5 weeks, one venue, no fees). Nothing enters a layer yet.

## 1. Definitions (OURS, in `wick_census.py`)
| Term | Rule |
|---|---|
| single-bar wick | wick >= 60 % of the bar range, range >= 1.5 x median range of the previous day |
| sweep | bar low < lowest low of the previous 20 bars and the close back above it (mirror for highs) |
| V-sweep (multi-bar) | low below the 20-bar low, a close back above it within 3 bars: on 5m a wick is usually 2-4 bars, one bar on 15m |
| outcome, R = 1 | enter at the close, stop at the wick extreme, target one wick length beyond the close, 4 h (15m) / 2 h (5m) window |
| knife (context) | 12 bars before the wick: fall >= 2 % from the highest high with the largest counter-move < 25 % of the fall |
| session (UTC) | ASIA 00-08, EU 08-13, US 13-21, LATE 21-24 |

## 2. Friday 2026-11-06, the 74,900 wick, as the data saw it (Bybit perp, 5m)
| UTC | O | H | L | C | vol |
|---|---|---|---|---|---|
| 14:55 | 75,692 | 75,704 | 75,280 | 75,511 | 1,862 |
| 15:00 | 75,511 | 75,568 | 74,929 | 75,046 | 2,702 |
| 15:05 | 75,046 | 75,378 | **74,810** | 75,290 | 3,005 |
| 15:10 | 75,290 | 75,820 | 75,194 | 75,809 | 1,654 |

On 15m it is one bar (15:00: low 74,810, close 75,809, wick 0.93 %, range 4.0 x median, volume 12 x median). On 5m it is a
two-bar V: the sweep bar and the reclaim bar, volume 15.7 x median, the Sep-15 low (74,961) swept by 150 USD and reclaimed
inside 10 minutes. R = 1 from the V close (75,290, stop 74,810) was hit in the next bar. What made this one different from
the 60-odd other lower wicks of the five weeks: (1) a daily level, the Sep-15 low, first touch since the September rise
(first try); (2) the CBP cluster at 75,000 (Krown weekly line, Michael, Qriptal, Cowen 74,900) sat on it; (3) effort 12-16 x
median volume on the sweep; (4) rejection speed: reclaim within 2 bars (Tom: "rejection speed" is proof, CONCEPTS.md).
Not a knife: the fall from 76,137 (14:50) had counter-moves; the knife flag is false.

## 3. The five-week census (2026-10-03 .. 11-07, BTCUSDT perp, outputs `CENSUS_15m_*.md`, `CENSUS_5m_*.md`)
| Kind | n | target first at R = 1 | note |
|---|---|---|---|
| 15m lower single-bar wick, all | 66 | 38 % | blind buying of wicks = below coin-flip, before fees |
| 15m lower wick that is a sweep | 29 | 45 % | vs 32 % when not a sweep (n 37) |
| 15m lower V-sweep (multi-bar) | 62 | 51 % | ASIA 68 % (n 19), US 40 % (n 20) |
| 15m upper wick, sweep / not | 24 / 42 | 46 % / 48 % | no sweep effect on the upside in a falling market |
| 5m lower V-sweep | 243 | 47 % | by week 34-59 %, no trend |
| 5m upper V-sweep | 230 | 48 % | |
| knife-context wicks | 1-2 per table | too rare to test | the knife is a live rule, not a fitted one |

Reading: a wick by itself is not an entry. The sweep of a 20-bar low adds about 13 points on 15m; the Friday case adds what
no 5-week census can count: a daily level, first touch, CBP cluster, 15 x volume. Those are the columns the plan adds.
Weeks: lower wicks per week fell from 17 (10-05) to 8 (11-02) while the median wick grew (0.23 % to 0.28-0.35 %): fewer,
larger wicks as the fall aged.

## 4. What the repo already found (Haiku survey, 2026-11-07; paths under MyTradingSys/)
| Concept | Where | Verdict |
|---|---|---|
| turn-of-candle, wlow bounce, weekly-low round sweep, EUR-low/US sweep, tf_break wick-sweep arm | backtest/layers/turn_of_candle, research/wlow_bounce_*, sim_desk st-opr_weekly_low_round_sweep, eur_low_us_sweep_2026-10-14, tf_break_event_study_2026-10-30 | NO-EDGE / FAIL / INCONCLUSIVE |
| first break of prior-day high/low (t087), pre-US first break held to 4h close 52 % | research/t087_session_levels_2026-10-09, pre_us_squeeze_2026-10-29 | NO-EDGE / descriptive |
| break speed (fast break short / slow break long) | VERDICTS.csv OPR-PREOPEN-TOPS | INCONCLUSIVE |
| CVD divergence, absorption (U8 reversed), funding/CVD fade | fabio_cvd_2026-10-30, orderflow_views_2026-10-14, T055 | NO-EDGE |
| LVN detector (shadow), volume-profile real FVG, live POC confluence | fabio/v3/signals.py lvn_levels, fabio_volume_fvg.py, alerts/live_levels_confluence.py | built, no outcome test |
| footprint model | fabio/FABIO_OF_REPORT.md | no edge, fee bug B081, rerun needed |
| live footprint writer | fabio/orderflow_live.py, runtime/orderflow_live/*.csv | CSVs end 2026-10-03: not running |
| 1m range vs ATR "speed" | runtime SetupCandidatesBuilder.java | computed, unused |
| falling knife, time-at-level, L2 depth history | none | GAP |

## 5. Price and time, what it means for us
- Steve's legs (section 1 of PLAN_ADX_DI_VOLUME): 36 % in "a little over a month" (about 1.0 %/day), 37 % in "a little less
  than a month" (about 1.3 %/day), then 26 %. Later legs are faster and shallower: speed up, depth down = exhaustion. The ADX
  census (card adx-di-2d-cross-census-1107) gets a %/day column per leg (M2).
- Public sources (practitioner only, no empirical study found): time and price are the two inputs; a trade has a price
  target and a time window, and "stop losses save us when we don't get the price right within our given time frame"
  (SeeItMarket). The Gann line "time is more important than price" is secondhand (mql5 forum). "Something has to give" is
  the same idea in one sentence: a move has a price budget and a time budget. Price arriving early = climactic (that is a
  wick: price runs through a low-volume node fast, Tom's "where there is no volume the market moves quickly", and is thrown
  back); time running out without price = the move is failing (a time stop).
- For a level approach MTS needs two numbers it does not record today: speed-in (% per bar over the last 12 bars) and
  time-at-level (bars inside 0.2 % of the level before the reaction). Fast in + no time at the level + reclaim = wick;
  fast in + time at the level + no reclaim = acceptance (Tom) = the knife continues.

## 6. The context gate (the gap the operator named)
| Context | Rule (OURS) | Action |
|---|---|---|
| knife | fall >= 2 % in 12 bars, counter-moves < 25 % of it | no wick buying; wait for the first close above the previous bar's high (first retracement) |
| phase | 5-week trend down (2d DI red, weekly lower highs) | sell upper wicks at resistance with the trend; buy lower wicks only at an HTF level with first touch |
| level quality | HTF level (daily/weekly low, naked POC, CBP cluster within 0.3 %) + first touch | needed for a lower-wick buy in a downtrend |
| effort | sweep-bar volume >= 5 x median | needed; 1-3 x = no climax |
| rejection speed | reclaim of the level within 2 bars (5m) / same bar (15m) | needed |
| news | no feed; the knife rule is the proxy | |

## 7. Plan (W1-W6; nothing starts before the operator's go)
| # | Piece | Builds on | Who |
|---|---|---|---|
| W1 | wick / V-sweep detector as a layer (5m, 15m), census script to the repo (done here), FORMULAS section | wick_census.py | Haiku S |
| W2 | context columns per wick event on 2022-2026 DEV: HTF level within 0.3 %, first-touch flag, CBP cluster, rel volume, speed-in, time-at-level, rejection speed, knife, phase; hit rate R = 1 and R = 2 fee-net per cell, n printed | trendlines first_touch, live_levels_confluence POC, analyst_levels store, 1m data | Sonnet session after the reset |
| W3 | testnet flag from day 1 for the one phase-valid cell: lower V-sweep at an HTF level, first touch, volume >= 5 x, reclaim in 2 bars, no knife; upper wicks at resistance with the trend. Alert first, then operator-called testnet (cotrade) | W1 + live_levels_confluence | Sonnet S |
| W4 | restart the live footprint writer (orderflow_live, CSVs end 10-03) so W2 can add delta and bid/ask columns live | live tree: coordinator deploy | card |
| W5 | price-and-time: %/day per leg in the ADX census; time-at-level and speed-in as live columns | M2 | Haiku |
| W6 | CBP: Jason Pizzino to the Monday wave for his time-and-price quotes (captions, verify_extract_quotes) | cbp_run.py | Haiku |

Verification (operator 2026-11-07): computed values are cross-checked on his TradingView / Binance charts through Claude in
Chrome (a Haiku worker reads 3 dated bars); first on the ADX/DI engine, then on W1's wick flags for Friday 15:00.

## 8. Questions for the operator (defaults in brackets)
1. W1-W3 after the Monday reset on login C [yes], or W1 now on the API credit (about 5 USD left after the ADX job)?
2. The with-trend side first: sell upper wicks at resistance in the downtrend [yes], buys only at HTF levels?
3. Knife rule numbers (2 % in 12 bars, < 25 % retrace) [take as OURS, tune on W2]?

Sources: SeeItMarket "Understanding and Respecting Time and Price Analysis" (https://seeitmarket.com/?p=17128); mql5 forum
on Gann (https://mql5.com/en/forum/194594); The Right Trader on high/low volume nodes
(https://therighttrader.com/learn/volume-and-order-flow/high-and-low-volume-nodes); Flux Charts Liquidity Sweep Profiler
(TradingView script LM4xxgfj); CONCEPTS.md (Tom, Fabio); PLAN_ADX_DI_VOLUME_2026-11-07.md.
