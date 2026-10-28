# WaveTrend: outside evidence, then MTS application

2026-10-17. Operator-requested research and priority handoff for Claude. Research only; no trading implementation changed.

## Decision

Move WaveTrend forward as a source-faithful observation layer and a **BTC-specific study of behavior in context and confluence**. The internet inventory supplies possible mechanisms to investigate, not the place to decide whether an edge exists. No defensible universal best setting was established. The inspected MTS work is a parked design without an identified implementation or backtest.

The most useful finding is that people trade several different systems under the same name. Reversal crosses at extremes, trend pullbacks, divergence, and squeeze breakouts have different economic assumptions. Combining them into one generic WaveTrend score would make both provenance and testing harder.

## Operator clarification: behavior and conditional discoverability come first

After the initial research, the operator clarified that applying an indicator indiscriminately is the wrong objective. Discovery must come from a specific asset, data range, timeframe, structure and confluence. This supersedes any reading of the original draft as a request to run generic WaveTrend strategies across everything. The standalone module is a software boundary; it does not mean standalone signals are the intended trading method.

The next empirical deliverable should be a **BTC WaveTrend behavior atlas**, before picking a complete trading strategy. Recommendations below are OURS research design, not LazyBear prescriptions:

| Behavior to discover | What to record causally | Conditional outcome to measure |
|---|---|---|
| Upper/lower band approach, entry and overshoot | First arrival, maximum WT excursion so far, dwell, repeated crosses, slope and WT1-WT2 separation; price/volatility at that moment | Further continuation versus reversal; price MFE/MAE and time to reaction, separately for each side |
| Shallow versus deep turns | Whether WT turns inside, at or beyond the bands; prior confirmed swing context | Which depths behave differently within the same BTC timeframe/regime; event counts and uncertainty |
| Centerline region | Approach from above/below, cross, rejection or return; time since last extreme | Whether center acts as continuation, reset or failed reversal in each context; do not assume the center is support/resistance |
| Divergence and internal structure | Regular/hidden divergence, WT higher lows/lower highs, price higher/lower swings, pivot confirmation time | Price response after the pattern actually becomes knowable, not after a retrospective marker |
| Cross-timeframe structure | Last closed higher-timeframe state plus the entry-timeframe pattern | Whether alignment or disagreement changes the conditional response, including delayed and missed trades |
| Confluence | Explicit, timestamped price location/structure and companion state available at the event | Outcome frequency and return-path improvement over the same context without WT and WT without the companion |

Describe the sampled date range, source contract and regime coverage first. Study BTC timeframes separately; do not pool them as if one oscillator event has the same meaning everywhere. Mark trend/range, volatility and location using information available at event time. Discover candidate excursion ranges and contextual distinctions on DEV only; freeze their numerical definitions before validation. A full excursion's eventual maximum, later price reversal or later regime label is an outcome, never an entry feature.

For each context/confluence cell report eligible events, actual signal count, outcome definition, success/failure count and rate with uncertainty, MFE/MAE, horizon, time-to-response and cost-adjusted return when a complete executable strategy exists. Report WT alone, context/companion alone, and their conjunction on a common event universe. Distinguish an indicator correctly describing momentum from a trade earning net returns. Count overlapping events and show effective independent episodes; show empty/underpowered cells and failures as well as attractive ones.

Use matched historical charts to understand mechanisms, with the decision-time view separated from the subsequent outcome. Examples illustrate the distribution; they cannot replace the full event ledger. A confluence merits further testing when it adds stable conditional information and sufficient opportunity, not simply because its selected examples have a high hit rate. Internet popularity ranks investigation leads only.

## How this sample was collected

The outside pass was blind to MTS. GPT-6-sol researched setup definitions; GPT-6-astra searched for efficacy evidence and failure mechanisms; the primary agent inspected MTS and reconciled the reports. Different models provide contrasting analysis, not independent empirical validation. The two separate viewpoints are retained as `EXTERNAL_SETUPS.md` and `EVIDENCE_REVIEW.md` (subsequent edits corrected evidence labels, not findings).

The setup report records 20 successfully opened pages, including 14 author script pages. The skeptical report adds first-party backtest/audit examples and statistical methodology. The primary agent adds two opened community discussions and venue/platform checks. These counts overlap; they are not a unique combined source total or a count of reviews. This is a broad, finite, search-ranked sample, not an exhaustive census of every language, video or private trading group. Queries, dates, access failures and source tables are in the component reports. Every source was checked on 2026-10-17; public backtests were not rerun.

## What people actually trade

See the external inventory's A-J table for author links, settings and exact limitations. All are T3 setup definitions unless explicitly marked otherwise; none is promoted here as an effective strategy.

| Setup family | Why traders use it | Main way it can mislead | MTS disposition |
|---|---|---|---|
| Cross after an extreme | Time a possible momentum reversal | Persistent trends produce repeated premature fades | First source-faithful hypothesis |
| Cross with a price stop and R multiple | Turn an oscillator trigger into a complete trade | Results depend heavily on stop, target and fill ordering | Retain the sampled BTC author's long-only formulation as a distinct candidate |
| Slow trend state with fast pullback trigger | Enter with broad momentum after a retracement | Lag, whipsaw and redundant trend signals | Compare as a separate trend-following family |
| Regular divergence | Price makes a new extreme while WT weakens | Divergence can persist; pivots are recognized late | Later candidate, causal pivot ledger required |
| Hidden divergence | Seek continuation after a pullback | Mixing it with regular divergence obscures trade direction | Separate trial identity |
| Divergence at support/resistance or pivots | Add a location for the reaction | Subjective hindsight in drawing levels | Only after location and availability rules are explicit |
| Volume or VWMA confirmation | Add participation or trend/exposure context | Volume seasonality; sizing can manufacture better absolute returns | Test incremental value before variable sizing |
| Squeeze, breakout, Supertrend | Suppress flat conditions or align direction | Many filters reduce sample size and hide selection | Deferred until simple models have a fair comparison |
| Higher-timeframe alignment | Use slower state for faster entries | Using an unfinished higher-timeframe candle leaks availability | Closed-bar-only candidate |
| Cipher-style composites and alert packages | Bundle WT, money flow, RSI/Stoch RSI and divergences | Multiple correlated votes, wrapper bugs, unclear component names | Decompose before evaluating; no composite admission yet |

## What is usually paired with it

The sampled publications repeatedly pair WT with **trend context (EMA, a slower WT, VWMA, Supertrend), price location, divergence, volume, or Squeeze Momentum**. Cipher-style variants add money flow, RSI and Stoch RSI. Community replies also mention MACD and discretionary order blocks/FVGs. This establishes observed usage, not a statistically measured ranking of the most common pairings.

My judgement: begin with one interpretable companion that answers a different question, such as trend direction or price location. EMA, RSI and MACD all derive from price; agreement among them should not be counted as three independent confirmations. Treat actual volume/flow or location as potentially different information, but require an ablation against the same WT candidate events. These are OURS research recommendations, not rules attributed to LazyBear.

## What the evidence says, including disagreement

The evidence review found encouraging hourly FX results and losing crypto futures/spot implementations. The crypto-futures example illustrates that a high win rate can coexist with a losing strategy. None establishes untouched chronological OOS plus credible perpetual funding and execution for BTC. Negative examples are implementation-specific; positive FX findings cannot be transferred to BTC without testing. Full dates, trade/order distinctions, cost assumptions and exact publisher URLs are in `EVIDENCE_REVIEW.md`.

The primary agent spot-checked the published FX trade-count/fill assumptions, crypto-futures result and timeframe warning against opened publisher pages. TradingView original/setup pages opened for the setup agent but subsequent parent opens were restricted; the accessible attributed Pine mirror was checked independently. This uneven accessibility is a provenance limitation, not independent replication of those scripts.

## Reviews, popularity and trader experience

There is no reliable total of WaveTrend reviews. The source register preserves visible TradingView counter strings, but their text rendering did not reliably expose labels. They must not be renamed reviews, verified users or profitable traders. The inspected code mirror visibly has two stars and one fork; those are repository engagement, not strategy reviews. This extra mirror check is [directly inspectable](https://gist.github.com/marketcalls/f9c795c7d5ba0f988761).

The small community sample includes praise for divergence and convenient alerts, plus warnings about lower-timeframe false signals. Discussion votes are recorded separately in `METHOD_AND_MTS.md`; they are not independent trader records. The sources are self-selected and overlap across forks. No percentage-positive sentiment, outcome-weighted review score or verified live BTC track record is justified by this sample.

## Tweaks and the search for a magic number

The baseline parameter set already recorded in T061 matches the attributed mirror's formula. Derivatives use different lengths, smoothing, thresholds and trend periods. Preserve their identities rather than silently replacing the original settings with whichever chart looks best.

There is no demonstrated special economic status for a particular length or band. Shortening smoothing trades less lag for more crossings; stronger extreme requirements trade fewer events for a different conditional sample. Altering normalization also changes the meaning of every fixed band. A good-looking isolated optimum is evidence of selection risk, not a discovery. Test modest, predeclared sensitivity only on development data, count every attempted setting, and require stability and a later untouched test. Never use holdout to choose the magic number.

## Applying this carefully to MTS

MTS has already done useful definition and audit work: T061, the T065 survey, and ER-07. The current board still parks WaveTrend while Tom/Fabio are redefined; the operator's new priority request should now drive a bounded next task. Keep it independent of Tom and distinguish source parity, useful observation, and profitable trading as three different acceptance claims.

1. **Source and parity first.** Prefer `backtest/layers/wavetrend/` from T061 as the proposed owner; Claude records the final choice. Pin original-versus-Crosses version, attribution/source terms, initialization, missing/flat input, zero denominator, warm-up and equality semantics. The mirror helps recover the formula but does not establish source rights or exact live Pine behavior. Obtain golden chart/export values and availability timestamps; do not declare parity from a Python self-comparison.
2. **Observation port.** Emit continuous WT values, zones and cross events with bar-close/availability timestamps and data-quality tags. No inferred trade direction or execution routing. Existing T061 timeframes are proposed scope, not five statistically validated trading markets.
3. **Discover BTC behavior before choosing strategy rules.** Build the conditional behavior atlas above from DEV, including bands, overshoots, centerline, structure, divergence and confluence by timeframe/regime. Plain cross and original extreme rules are controls, not a recommendation to trade every signal. Select complete strategy candidates only after recording these conditional distributions and freezing contextual hypotheses. Keep every new boundary or conjunction in the trial ledger.
4. **Use the actual MTS study discipline.** Inspect verdict aliases and prior data exposure; follow current chronological split policy rather than T061's old 70/30 shorthand. Use the Binance research contract and a separate Deribit execution check where applicable. Include realistic fees, spread/slippage, funding exposure, linear/inverse accounting, gap fills and same-bar stop/target ambiguity. Funding and fee assumptions require current venue verification. Published gross moves or a fixed 0.10% cost alone cannot settle the question.
5. **Admit only what passes.** Compare WT alone against each companion on the same eligible events, with exposure/turnover-matched baselines. Report net expectancy and uncertainty, drawdown, trade count, side/regime, costs and missed opportunities. Control multiple trials and overlapping observations; use power checks and selection-aware analysis. Read validation once after DEV selection, preserve holdout integrity, then collect forward paper/testnet evidence. Insufficient data means inconclusive, not fail or pass.

Added by the parity card (CLAUDE_VERIFY D1-D2): every DEV read of the atlas is logged in `research/gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv`, and every cell carries a random-clock control arm besides "context alone". Source pin and conventions: PARITY_CONTRACT.md; event/outcome definitions: ATLAS_STUDY_SPEC.md.

The priority-1 SONNET task `wavetrend-priority-source-parity` is ready and references this research. It delivers the source/parity/study contract and a bounded implementation task. This research does not supply an invented economic pass threshold or claim deployment readiness.

## Package and limitations

- `EXTERNAL_SETUPS.md`: blind setup survey, ten families, author source register and popularity observations.
- `EVIDENCE_REVIEW.md`: blind skeptical review, empirical examples, tier/method limitations and excluded leads.
- `METHOD_AND_MTS.md`, `REPO_CHECK_RECEIPT.md`: research protocol, repo findings and checks.
- `CLAUDE_HANDOFF.md`: short operator-priority handoff; queue task is the actionable pickup.

No source snapshot, chart fixture, WaveTrend implementation or new strategy backtest is claimed complete. Priority means resolving those dependencies and producing testable progress, while evidence determines eventual trading admission.
