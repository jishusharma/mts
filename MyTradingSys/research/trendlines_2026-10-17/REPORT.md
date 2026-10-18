# Trend lines: BTC context study and daily chart observation

2026-10-17 | Research and build proposal; no backtest performed, no live rule adopted.

## Operator direction and priority

The operator asks Claude to prioritize this work: how lines are drawn is the first problem, followed by conditional behavior around touches, breaks and retests across timeframes, slopes, environments and phases. Include a daily check of lines being formed and followed in published charts, with appropriate analyst/source channels. Popular or viral charts can reveal conventions to investigate; they cannot establish edge. The operator's earlier WaveTrend clarification applies: discover specific BTC contexts and incremental confluence rather than apply a generic setup everywhere.

The deliverable is a causal line-definition contract, an observation ledger and a bounded BTC event study. “Proven” must mean a reproducible, cost-aware out-of-sample result for the relevant definition and context. This search found no validated evidence for a universal angle-based BTC perpetual breakout rule. Starting priorities below rank testability and source clarity, not established profitability.

## External first pass: definitions worth distinguishing

These are practitioner definitions (T3, low confidence in predictive claims). No source below supplies a replicated BTC perpetual study with disclosed costs and untouched validation. Verified/opened 2026-10-17 IST. Method note was written before searching.

| Family | Definition and use | Source |
|---|---|---|
| Swing support/resistance | Join rising lows or falling highs; a break warns of a possible change, requiring confirmation | [Fidelity, Basic concepts of trend](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/basic-concepts-trend) |
| Two-anchor / third-touch line | Two points propose a line; a later touch validates it. Spacing and chart scale matter. Internal lines tolerate spikes; keep these separate from strict outer lines | [StockCharts, Trend Lines](https://chartschool.stockcharts.com/table-of-contents/chart-analysis/trend-lines) |
| Parallel channel | Main swing line plus parallel opposite boundary; failure to reach the opposite side and a boundary break are different events | [StockCharts, Price Channel](https://chartschool.stockcharts.com/table-of-contents/chart-analysis/chart-patterns/price-channel) |
| Trend-following bounce | Trade around a projected swing line with structure-based placement; published FX pip offsets are asset-specific, not BTC defaults | [IG Analyst, 2018-09-12](https://bts.ig.com/uk/trading-opportunities/what-are-trendlines-and-how-do-you-use-them--180912) |
| Breakout with companions | Momentum, volume and retest are candidate confirmations; RSI/MACD are commonly taught companions, not demonstrated incremental edge | [IG Academy, Measuring breakout strength](https://www.ig.com/uk/learn-to-trade/ig-academy/breakout-trading/measuring-breakout-strength-and-managing-risk) |
| Algorithmic pivot line | Platform example connects recent confirmed pivots; illustrates implementability, not the optimal line selector | [TradingView Pine FAQ, Visuals](https://www.tradingview.com/pine-script-docs/faq/visuals/) |
| Chart angle | Platform angle drawing expresses chart geometry; store price/time coordinates for research | [TradingView, Trend angle drawing tool](https://www.tradingview.com/support/solutions/43000791602-trend-angle-drawing-tool/) |

StockCharts explicitly notes chart size/data display changes apparent angle and that steep-line breaks can be difficult to trade. Its internal-line convention permits ignoring spikes; that conflicts with a strict no-cut-through approach. Keep both definitions named rather than silently redrawing the same line. These are educational chart examples, not statistical validation.

Searches included institutional definitions, slope/scaling, channels, breakout companions and BTC trendline backtests. A BTC trend-following paper surfaced but was not used to support diagonal swing-line trading: trend following is a broader family. This is a bounded source sample, not an exhaustive literature review. No reliable global review count or representative trader consensus was established.

## MTS already has Krown definitions, but no identified line detector

Read `research/krown_ta101_2026-10-13/extracts/extract_14bxwxC8gBQ.md`, `KROWN_LAYER_SPEC.md`, `STATE.md`, and `KROWN_SETUP_CATALOG.md` (KR-S10/S11). The extract identifies Krown @ECKrown and the video “Your Trend Lines Keep Breaking Because They Were Never Real. Here Are the 2 Rules.” (2026-09-12, video 14bxwxC8gBQ). These are existing extracted transcript sources, not newly fetched video or independently reverified captions in this session.

| Krown source locator in that extract | Sourced concept | Missing mechanical choice |
|---|---|---|
| TRL-04/05, 00:04:18 / 00:04:27 | Confirmed swing highs/lows; lows with higher lows on both sides | Swing window, equal pivots, confirmation time |
| TRL-06/07, 00:08:34 / 00:09:33 | Line-chart inspection; swing importance depends on timeframe | Close-based versus wick-based construction |
| TRL-08, 00:06:17 / 00:06:31 | Two points propose; three touches establish a trend | Touch tolerance, separation and reaction threshold |
| TRL-09, 00:06:51 / 00:07:01 | Two heavy-volume turning points can qualify early; volume about double recent bars | Baseline length; intraday seasonal adjustment |
| TRL-11/12, 00:13:13 / 00:14:15 | Reaction at volume anchors; first-pass scalp | Entry, stop, target and horizon not specified |
| TRL-13/14, 00:07:50 / 00:10:46 | Avoid bent-to-fit lines; distinguish follow-through from snapback | Allowed penetration; follow-through is initially an outcome |
| TRL-15/19, 00:11:38 / 00:18:26 | Broken line may support higher lows / become resistance | Retest and higher-low confirmation timing |
| TRL-16, 00:17:35 / 00:17:44 | Steeper trends described as shorter lived; four-to-five-degree example | Chart scaling unspecified: angle unusable as a numerical rule |
| TRL-17, 00:16:10 | Symmetry of fast advance/decline as a mental model | No empirical symmetry distribution |
| TRL-22/23/24, 00:24:11 / 00:25:44 / 00:26:26 | Horizontal structure matters; close beyond major swing confirms structural change | Mechanical dominant-swing selection |

All above T3, descriptive-source confidence medium; predictive confidence low. Sourced counts or volume ratios do not make a profitable strategy. No new transcript quotations are reproduced here. Exact text and GPS remain in the extract. KR-S10 and KR-S11 catalogue entries explicitly have zero trades in a ledger and missing stop/target definitions. Reuse them; do not create duplicate Krown setups.

The current checkout has no `backtest/layers/krown/` folder. Filename inventory across 197 Git refs found zero `.py/.java/.pine` paths containing `trendline` or `trend_line`. This does not exclude differently named code or remote untracked work. Before building, inspect existing pivot/level functions and open claims. The registered Krown family and spec exist; “nothing around this” would overstate the implementation gap. Do not equate the layer board's spec status with a working detector.

Current playbook says layers can combine/filter each other based on results. No fixed core or mandatory WT/Tom dependency is assumed. Trend-line geometry should be reusable and Krown provenance retained. Research family registration and timeframe maps must be reconciled before any engine integration.

## First deliverable: exactly how we draw the lines (OURS proposal)

1. Freeze venue, instrument, candle source, timezone, linear-price versus log-price transform and timeframe. Start with actual OHLCV candles; spot and perpetual lines are separately tagged. No synthetic candles for execution claims.
2. Detect pivots using closed bars. A pivot at bar i requiring k right-hand bars becomes available only at close(i+k). k and tie policy are OURS, not Krown numbers. An unfinished ZigZag leg is provisional and cannot anchor a historical signal.
3. On each new confirmed pivot, propose same-side anchor pairs under declared spacing and age rules. Rising low pairs create support, falling high pairs resistance. Flat pairs belong to horizontal controls. Baseline strict lines must pass a stated intervening-penetration test. Close-based and wick-based arms stay separate. Invalid lines and their rejection reasons remain in the ledger.
4. Define each candidate by immutable anchors, transform, equation, creation/availability timestamp and version. No moving an old line to rescue it. New anchors create a new version with forward-only effects. State transitions: proposed, eligible, touched, broken, retested, reclaimed, retired. Historical state remains append-only.
5. Treat anchors separately from later tests. Two anchors are not two independent post-creation confirmations. Count distinct contact episodes with a declared distance-away reset; a candle cluster riding the line is one episode, not many touches. Validation by a confirmed pivot/reaction becomes knowable later than first contact. Never credit that validation to an earlier entry.
6. Predeclare line selection: nearest eligible boundary on the relevant side, with deterministic ties, is one possible primary selector (OURS). Retain all candidates for coverage. Do not choose the line whose subsequent break looks best. Compare this selector with an analyst-labelled sample before freezing it.
7. Record residuals/fit, anchor spacing, age, observed contact count, contact reaction size, penetration history, and anchor volume. “Obviousness” requires reproducibility: independent drawings on charts cut off at the decision timestamp, disagreement rates, and explicit uncertain/no-line labels. Agreement alone is not evidence of edge.
8. Show actual point-in-time charts for every deterministic sample selection: formed line, upcoming interaction, failed break and no-response cases. Overlay wick/close and log/linear variants without concealing discrepancies. Human labels use future-hidden panels.

Primary construction families: strict external wick line, close-pivot line, and volume-anchored Krown variant. Add internal spike-tolerant lines only after defining their permitted violations; regression fits are a separate benchmark and must not be called Krown lines. Parallel channels require a confirmed opposite-side anchor for their offset; do not move the channel using future highs/lows. Wedges/triangles have two independently known boundaries. Accelerating nested lines have distinct IDs; breaking a steep inner line while the outer line holds is its own context.

## Slope and “clear break” contract (OURS, not frozen parameters)

For anchor prices p1,p2 at elapsed times t1,t2, a linear line is L(t)=p1+(p2-p1)*(t-t1)/(t2-t1). A log-price line is L(t)=exp(log(p1)+(log(p2)-log(p1))*(t-t1)/(t2-t1)). These are different geometries, not interchangeable drawings.

Store signed log return per elapsed hour, percent change per bar, duration and volatility-normalized price slope. One candidate normalized measure is linear price change per bar divided by ATR known at line creation, with that denominator fixed for the line version; also retain current volatility separately. ATR definition/length is OURS and belongs in FORMULAS.md before implementation. Compare slope within each timeframe first: percent per bar and volatility per bar do not make 1m and daily equivalent. A mathematical arctangent can be computed only after defining dimensionless axes; it does not recover Krown's visual degrees. No magic 45-degree threshold.

At a closed-bar break of descending resistance, record close above L(t), prior-side state, distance beyond line normalized by known volatility, candle body/range, close location, volume versus prior same-slot baseline, and distance to the nearest overhead horizontal zone. Mirror for support. Also distinguish line drift across a flat price from decisive price movement through the line. Wick penetration, close-through, persistence, retest and reclaim are separate event types.

“Clean candle”, “follow-through” and “held retest” need numerical contracts before testing. If a setup waits for another close or confirmed higher low, its signal and fill move to that later time. The baseline cannot look into future follow-through to decide which breaks counted. Outcome labels may describe later persistence; entry features may not.

## BTC context and test sequence

Study three initial questions: first-return reaction to a legitimate line; break of a countertrend pullback line within an intact higher-timeframe trend; break/retest of a major trend line near horizontal structure. Keep standalone break as a control. Extend to failed-break/reclaim, compression boundary, channel acceleration versus primary-boundary reversal only after the initial definitions work. These extensions are hypotheses, not proven setups.

For each question stratify by closed higher-timeframe trend/range state, volatility/compression/expansion, proximity and side of horizontal support/resistance, slope, line age, contact count and spacing, anchor volume, breakout candle behavior, approach speed, and space to the next obstacle. Start with a bounded shortlist, not a Cartesian product. Funding/OI/orderflow are optional later hypotheses only with point-in-time coverage. A 1m execution signal inside an hourly/daily line is a different study from a 1m line; store line timeframe and trigger timeframe separately. Include 1m, 1h and daily in the discovery plan requested by the operator; finalize actual coverage from available data and power, not arbitrary pooling.

Channel/symmetry measures use information available before the break: opposite-boundary distance, past oscillation amplitude, normalized excursion, contact timing, failure to reach the opposite boundary and support/resistance alternation. Post-break mirror symmetry is an outcome. Do not force equal legs or use an eventual channel width as a feature.

Measure signed forward returns, MFE/MAE, time to response, reclaim probability and conditional survival to break. “How often does it work?” requires a predeclared success threshold/horizon, all eligible opportunities, counts and intervals, not selected winning charts. Contact-count comparisons require survival/risk-set analysis: a five-touch line already survived the earlier tests. If the third successful reaction establishes eligibility, assess outcomes after that eligibility time; do not also count that reaction as subsequent success. Control for age, slope and regime; do not interpret a raw count comparison causally. The study estimates prospective conditional association, not proof that the line causes moves or that large players defend it.

Compare line alone, context alone, context+line, and horizontal structure alone on compatible event opportunities. Add momentum/volume/WT only as declared incremental arms. Count opportunities excluded and retests that never arrive. Use elapsed-time horizons plus timeframe-native horizons explicitly. Cluster uncertainty by day/episode and handle overlapping lines/events; report effective sample size and underpowered cells. Match non-line trend moves and shifted/placebo line encounters preserving regime/time structure, with declared invalidation rules.

Discover candidate ranges only on declared DEV. Freeze line construction, selection, primary question, costs, outcome horizon and context before VALIDATION. Track all inspected variants; check VERDICTS.csv for overlap and run current prereg/MDE gates before a freeze. Then validate once; retain holdout access policy. Do not silently treat already-exposed data as fresh. Repository verdict query `trendline diagonal channel` returned no match (needs two normalized terms); this is a lexical check, not proof that overlapping S/R studies do not exist.

Research tape follows the current repo's Binance BTCUSDT perpetual target. Any Deribit execution claim needs its separate execution check. Recheck current fees and funding against the selected instrument/date before a run. A descriptive reaction study is not a trading P&L claim. An executable test needs entry after information availability, explicit protective stop/exit, trade-through for resting fills, spread/slippage/funding, same-bar ordering policy and cost stress. No borrowing missing stops/targets from an unrelated strategy.

## Daily channel: published-line watch, not hindsight chart collection

Recommended source channel starts with Krown's existing public-source corpus and timestamped TradingView BTC ideas; operator may supply named analyst accounts. Keep the report destination in this task and the shared research ledger; Claude receives the priority implementation handoff through the repo desk board. Source channel, analytical layer and notification channel are distinct choices. Analyst authorship/identity is verified per captured post, not inferred from a similar handle.

Daily observation protocol:

- Check the fixed source roster and log each source checked, timestamp, query, access result and the full eligible-result denominator. Use a stable sampling rule declared before outcomes. Keep all previously tracked live lines, including invalidated/unpopular ones. A search result is only a discovery lead until the original post/chart opens.
- Capture author, permalink, original publication and observed times, symbol/venue, chart timeframe, price transform, visible anchors, line equation where recoverable, prior touches, stated scenario and popularity metric with its actual label/time. Record unknowns; never invent exact coordinates from an unreadable image. Link to the original; respect source access restrictions.
- Separate prospective lines published before the tested interaction, already-broken retrospective examples, and reposts/edits. Save a lawful immutable metadata/text/annotation snapshot and content hash; later edits get a new version. Today's likes cannot be used as yesterday's selection variable. Viral examples are discovery-only and marked selection-biased; followers/views/comments are not reviews or independent confirmations.
- Reconstruct the line on matching venue candles. Score confirmed-anchor availability, no forced fit, later unchanged-line contacts, break/retest status and consistency with the published scenario. Missing chart access or coordinates is NOT_IN_DATA, not a line failure. Human-drawn and automated line agreement is a drawing-quality readout, not a profit result.
- Append today's state for every tracked line without changing its old anchors. Revisit at declared outcome horizons. Include formed lines with no touch, touches with no break, failures and removals. Intraday lines may form and break between daily checks: this monitor observes public posts, it is not a real-time detector.
- Summarize newly observed definitions, reproducible prospective lines and material access/data blockers. Keep a coverage log even when no qualifying chart appears. Notify only on meaningful additions, completion, failure or required input; no trading alerts or orders.

Daily monitoring is a separate prospective stream from historical DEV discovery. Lock each observation before reading its subsequent outcome. Public consensus cannot prove that large players defend a line; it measures visibility at most. No claim that the daily watch is operational in MTS until a scheduled run writes and verifies the ledger.

Access exclusions: direct TradingView trendlines and BTCUSDT idea feeds could not be opened by the web tool in this session; no chart/example/engagement claim is made from them. Daily runs must record that limitation and use accessible original posts rather than claim coverage. No paid/private material or unavailable Krown videos was inferred. Unopened broad trend-following and no-cost profit snippets were not used as diagonal-line efficacy evidence.

## Acceptance and handoff

Priority 1: a spec with exact line lifecycle, source/OURS table, future-hidden drawing fixtures, analyst/algorithm disagreement, and a causal replay test plan. Priority 2: build descriptive detector and daily line ledger before economics. Priority 3: one bounded BTC context event study after data audit and prereg checks. This report authorizes research scoping, not live deployment or a claim that any setup is already proven. See CLAUDE_HANDOFF.md and task `trendline-priority-drawing-contract`.
