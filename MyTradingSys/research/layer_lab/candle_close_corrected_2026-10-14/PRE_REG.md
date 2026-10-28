# Corrected BTC candle-close study: frozen before new outcomes

2026-10-14. Operator explicitly authorised repeating the same test with corrected scope. All new numerical choices are OURS. This is a corrected exploratory DEV experiment, not pristine independent evidence: the original DEV results and subgroup tables have already been inspected. No original output is overwritten.

## Method note and question
Estimate whether a completed close signature adds predictive information at a comparable level encounter in a causally identifiable phase. Use identical encounter/decision timing for signals and controls, uncertainty by calendar blocks, all registered phase cells and costs/funding scenarios. Local reactions and one-day low/high persistence are measurable here; full swing/cycle-bottom detection remains outside the empirical scope, not silently represented by a one-hour return.

## Data and unchanged components
- Same Binance USDT-M BTCUSDT 1m archives, January 2022-June 2024, 30 exchange-verified monthly files. Minute data is loaded only from the original manifest and rehashed; require ordered unique contiguous minute timestamps and valid OHLC. No later prices, validation or holdout are opened.
- Same UTC epoch-aligned 1/2/3/5/15/30/60m triggers, prior completed 4h/day/UTC-Monday-week high/low levels, six exact signature definitions in the original METHOD.md (rejection, break, acceptance, reclaim, retest proxy, strong break). Current definitions are OURS; this is not anonymous YouTube-trader replication.
- Historical funding: public monthly fundingRate archives for the same 30 months, with exchange SHA256 verification. Missing rate coverage means NOT_IN_DATA and blocks a cost-screen candidate; never substitute zero. No account/API credentials.

## Phase identification, before the encounter starts
Use only fully completed parent candles available at encounter open. A missing period/history produces UNKNOWN; no carrying an older complete level across an invalid parent period. Require 31 complete daily candles for legacy 30-day momentum metadata. Those labels are named UP_MOMENTUM/DOWN_MOMENTUM/NEUTRAL, not bull/bear cycle facts.

For each 4h and 1h parent, use the latest 21 closes and latest 20 OHLC bars. A = arithmetic mean of true range across those 20 bars, with the preceding close for each. E = abs(last close - close 20 bars earlier) / sum(abs(the 20 close changes)). Let U/B be max high/min low over the 20 bars; old/recent extrema use the first/last ten bars.
- UP_TREND: E>=0.40, positive net close change, recent high > old high +0.5A AND recent low > old low +0.5A.
- DOWN_TREND: E>=0.40, negative net change, both recent extrema < old extrema -0.5A.
- BOUNDED_RANGE: E<=0.30, U-B>=2A, absolute old/recent high difference<=0.75A and low difference<=0.75A, with at least two separated touches of each boundary. Touch: high>=U-0.5A / low<=B+0.5A; retained touch indexes must be >=2 bars apart. This is a causal operational range hypothesis, not a guaranteed true market state.
- TRANSITION: complete history but none of the preceding definitions. UNKNOWN: missing data or nonpositive/nonfinite A.
- Volatility ratio V = latest 4h A/close divided by median of the preceding 180 completed 4h A/close observations, excluding the current observation. V>=1.5 elevated; V<0.75 quiet; otherwise ordinary. No full-sample quantiles.

Joint primary context is assigned for each proposed trade side at encounter open:
1. TREND_ALIGNED: 4h trend agrees with side AND 1h trend agrees with side.
2. TREND_CONFLICT: 4h is trending but the preceding alignment condition fails. Keep exact 4h/1h directions and with/against-side flags in rows; this bucket does not assert that all conflicts are equivalent.
3. RANGE_EDGE: 4h bounded range and level lies in [B-0.5A,B+0.25(U-B)] or [U-0.25(U-B),U+0.5A].
4. RANGE_INTERIOR: 4h bounded range and level lies between those edge bands.
5. TRANSITION_HIGH_VOL: all remaining cases, V>=1.5.
6. TRANSITION_OTHER: remaining cases.
UNKNOWN is recorded as rejected eligibility, not forced into a tradable state. Base phase, exact local trend, volatility, momentum, range position, side and context are retained jointly. We test every signature in each context; context labels alone never authorise a trade.

## Common encounter and decision ledger
- For each trigger TF, level family and high/low identity, retain the first bar that trades through a known level in each UTC day. Levels are known at bar open; the first contact's value is frozen for the whole episode. The real-time known approach is the sign of previous close minus level (fallback current open if equal); unknown approach is excluded and counted.
- The contact bar is bar 1. Decision is the close of bar 3 (two more complete consecutive trigger bars). Every encounter gets this same fixed wait, whether it produces a signature or fails. Patterns are evaluated on the last three closes/current wick at that decision against the frozen encounter level. No selecting an earlier best signal. Both long/short orientations are recorded.
- Entry reference is the next minute open at the decision boundary, not a retrospectively available close. Candidate low/high is the min/max across the three already closed encounter bars. Keep encounters with no signature and late/failed closes as controls. No post-encounter phase relabeling.
- No requirement that decision close remains within the original 0.25% band: distance is measured and matched instead of selectively dropping displacement closes.
- One fixed placebo line per parent level: at that parent availability time, use the then-known minute open P, d=abs(real level-P); placebo=P+random_sign*d*U(0.75,1.25). Seed 20261014, chronological family/edge order. This is an approximate distance-matched random-line control (within 25%), not exact distance equality. d=0 is ineligible for placebo. Placebo values use no later bar. The same first-contact and decision rules apply.

## Comparable controls
For each real signature event, eligible controls are real encounters WITHOUT that signature, same TF/family/high-or-low identity, trade side, approach and joint context, excluding its entire UTC day. For the separate level-skill arm, compare all real encounters with placebo encounters, same exact strata, excluding same UTC day. Both kinds use identical three-bar decision timing and endpoint/fill conventions.
- Past/current decision covariates: signed distance from level / frozen 4h A; log(V); UTC time cyclic sine/cosine. Controls must have decision close on the same side of level, distance difference<=0.5A, log-vol difference<=ln(2), circular clock difference<=3h. Choose nearest by squared distance in these four features; time sine/cosine each weighted 0.5.
- Keep at most 10 nearest controls, one per distinct calendar day; require at least five distinct control days. Uniform weights. Failed matching is NOT_MATCHED, not a zero return. Report matching coverage for every cell and covariate imbalance. A candidate needs >=80% of eligible signal episodes matched and max absolute standardized difference<=0.25 across distance, log-vol and clock covariates. These are fixed diagnostic gates, not tuned on outcomes.
- Matching is based on features only. Matching across DEV is an offline conditional association test, not a deployable fitted forecast or causal effect. No fallback/coarsening after viewing coverage or results.

## Outcomes, costs and inference
- Primary horizons: 60 and 1440 minutes after reference entry. Signed open-to-open return and positive-price-return probability; partial paths/endpoints are right-censored and counted. Entire minute path must exist.
- Fee/slippage scenarios: subtract 14bp (5bp fee +2bp slippage per side) and 20bp (5+5 per side). Funding uses archived settlement rates in (entry,exit], multiplied by settlement trade-price/entry-price and trade side. This is a trade-price proxy for funding notional, not exact historical mark-price/account P&L. Financing at an entry exactly on settlement is assumed post-settlement. Show gross, funding and cost screen separately. No passive queue, mark-price stop/liquidation, portfolio compounding or discretionary execution claim.
- Secondary 24h outcomes: MFE/MAE; +/-1A first passage from entry (report both-touch one-minute ambiguity as lower/upper bounds); frozen candidate extreme survives within 0.25A for the full horizon AND +1A target is reached. For shorts mirror high retention. This is one-day candidate-extreme persistence, not a confirmed swing/cycle bottom. Unknown/right-censored is separate from failure.
- Registered primary family: (6 signatures +1 real-vs-placebo level arm) x7 TF x3 level families x6 joint contexts x2 horizons =1764 cells. Two primary candidate metrics per cell (probability lift and 14bp funding-adjusted mean) plus two secondary probability views per 24h cell: conservative adjustment family=5292. All zero/underpowered/unmatched cells remain in the registry. Prior lineage >=264 arms remains disclosed; secondary/matching diagnostics are not unlogged tuning opportunities.
- 1000 circular seven-calendar-day block bootstrap draws, seed 20261014; common sampled days for all metrics/cells. Allocate signal outcome contributions to signal day and weighted control contributions to control days; resampling includes uncertainty in both sides, holding the feature-based match graph fixed. Re-matching uncertainty and longer dependence remain limitations. Report pointwise 95% intervals plus normal-bootstrap Bonferroni screening bounds across 5292 planned metrics; no OOS significance claim.
- Candidate screen: >=100 matched events, >=30 signal days, matching coverage>=80%, covariate gate above, positive Bonferroni lower bound for both probability lift and mean 14bp/funding screen. Report 20bp stress separately; failure at stress prevents any adoption claim. No DEV candidate is automatically promoted, and no validation run is authorised by this study.
- Power: 912 calendar days before warmup/censoring; at most two side orientations per encounter, correlated. 100 iid events have about +/-9.8pp precision near 50%; detecting a 5pp lift against a known baseline at 80% power needs about 784 independent events, more with matching/episodes/multiplicity. Many joint cells will be underpowered. Zero matching or too few days means INCONCLUSIVE.

## Verification and readiness
1. Home: OURS BTC perpetual close-sequence conditional event study, seven TFs, 60min/24h outcomes; no trader replication.
2. Source trade ledger: anonymous trader NOT_IN_DATA. Synthetic definitions/chronological encounter ledger are ground truth for this OURS hypothesis.
3. Recall/fire rate: synthetic fixtures first; report all encounters, no-signature encounters, unmatched and censored counts. No source-trade recall claim.
4. Inputs: price/volume archive plus historical funding coverage; no OI/aggressor/order-book substitution.
5. Parity: independent raw-row phase, level, encounter decision, control selection and funding checks; verify all inference arithmetic against independent scalar resampling fixtures.
6. Economics: scenario costs and historical funding-notional proxy explicitly labeled; no exact executable P&L claim.
7. Fills: common next-minute reference prices, no passive orders. Touch/trade-through queue tests not applicable to this event study.
8. Management: fixed endpoints and separately labeled one-day path outcomes; not a trader's exit policy.
9. Null: common encounter/decision rules and feature-only matched nonsignature/placebo controls above.
10. Power: above; per-cell episodes/day counts, uncertainty and missing matching coverage required.
11. Holdout: forbidden. Same previously inspected DEV; trial ledger includes all extensions. Frozen document/code hashes required before outcome run.
12. Stratification: primary joint contexts, raw phase/local direction/vol/side retained. All cells registered with their own inference; no selecting only favourable phases.

Before results: fail-first tests for range/trend/UNKNOWN fixtures, mirrored definitions, phase availability, control day exclusion/calipers, bootstrap contributions and censoring; full future-input perturbation preserves past decision features. Missing pandas must be reported explicitly; a broken application import must fail. The explicit research gate requires pipeline tests to execute, not skip.
