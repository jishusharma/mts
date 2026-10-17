# Phase-encounter preregistration: causal joint phases, opportunity-matched controls (design only)

2026-10-17. Card candle-close-phase-encounter-design. Answers audit A1-A3, A5-A7 (INDEPENDENT_AUDIT.md) and the 8 points of NEXT_EXPERIMENT.md. NO outcome run, NO price read, NO VALIDATION/HOLDOUT read happened for this document. Every number below is OURS (judgement, not any trader's rule, not yet tuned); none is SOURCED. Status: DESIGN FROZEN, EXECUTABLE BUILD BLOCKED by B1-B3 in section 11.

## 1. Data and lineage

- Binance USDT-M BTCUSDT 1m archive, 2022-01 through 2024-06, same files and SHA256 as download_manifest.json. Nothing dated 2024-07 or later is loaded (that is the existing candle VALIDATION reservation, unread, and stays unread). This window was already inspected by the 126-arm study, so any positive here is a DEV discovery and needs new evidence (section 10).
- Decision timeframe: 15m, UTC epoch-aligned, complete bars only, no forward fill, reject duplicates / missing minutes / incomplete buckets (study.py `aggregate` rules). Feature timeframes: 1h, 4h, 1d built the same way.
- Prior lineage carried: 130 candle trials and 8 levels-sizing arms (METHOD.md), the 126 pooled arms of CANDLE-CLOSE-DEV-20261014 (TRIAL_REGISTRY.csv), and the 44 views declared in section 8. Not claimed to be the complete MTS search history.

## 2. Features (decision time t = close of 15m bar; every input is a completed bar with close time <= t)

Common rule: a feature is evaluated at t from completed bars only. If any required bar is missing or warmup is short the value is `UNKNOWN`. UNKNOWN is a valid state, kept in the ledger, never imputed, never dropped, never forced into a neighbouring class. `transition` is a valid state where named. Existing study labels are kept as BASELINE features with accurate names (F0), not as phase claims.

| ID | Name | Equation (OURS) | Available at | UNKNOWN when |
|---|---|---|---|---|
| F0a | momentum30 (was "phase") | r=C_d/C_{d-30}-1 on completed daily closes; bull r>0.10, bear r<-0.10, else neutral | close of the last completed day | fewer than 31 completed days |
| F0b | efficiency30 (was "trend") | abs(C_d-C_{d-30})/sum_{k=0..29}abs(C_{d-k}-C_{d-k-1}); >=0.30 `trending`, else `choppy` (NOT "ranging") | close of the last completed day | fewer than 31 completed days |
| D | directional structure | Confirmed 1h pivots: pivot high at bar j iff H_j > max(H_{j-2},H_{j-1}) and H_j > max(H_{j+1},H_{j+2}) (strict; ties are not pivots), lows mirrored; usable only from the close of bar j+2. Take the 2 latest confirmed highs (PH1 older, PH2 newer) and 2 latest confirmed lows within the last 14 days. `up` if PH2>PH1 and PL2>PL1; `down` if PH2<PH1 and PL2<PL1; else `mixed` | close of 1h bar j+2 of the newest pivot used | fewer than 2 confirmed highs or 2 lows in 14 days |
| R | bounded range | Over the last 14 completed daily bars: U=max high, L=min low, W=U-L, ATR14d = simple mean true range of the last 14 completed days. `bounded` iff W <= 5*ATR14d AND >=2 distinct days have high >= U-0.10W AND >=2 distinct days have low <= L+0.10W; else `unbounded`. Also gives `range_pos`=(C_t-L)/W | close of the last completed day | fewer than 15 completed days |
| V | volatility state | q = mean TR of the last 6 completed 4h bars / mean TR of the last 120 completed 4h bars. Tercile of q against the q values at every 4h close in the previous 90 days (past-only rank, current value excluded): `low` < 1/3, `high` > 2/3, else `mid` | close of the last completed 4h bar | fewer than 90 days of q history |
| A | timeframe alignment | s4 = sign(C4h_last - C4h_{6 bars earlier}); sD = sign(Cd_last - Cd_{5 days earlier}); 1h state = D. `aligned_up` if s4=sD=+1 and D=`up`; `aligned_down` mirrored; `conflict` otherwise (zero sign counts as conflict) | close of the last completed 4h bar (daily and 1h parts earlier) | any component UNKNOWN |

All context labels are oriented to the trade side (below). For a short, D `up` and `down` swap, A `aligned_up` and `aligned_down` swap, and `range_pos` becomes 1-range_pos. Thresholds (0.10, 0.30, 5, 0.10, 6/120, 90 days, 14 days, 5 days, 6 bars) are OURS, frozen now, and not tuned on outcomes. The alternatives considered and rejected before any outcome look (a Kaufman efficiency on 4h; ADX; range width 4x/6x ATR; 60-day q history) are NOT run; running one later is a new counted trial.

## 3. Encounters, timing, censoring

- Levels: previous completed 4h and daily high/low, available only at the parent period's end (as METHOD.md). Weekly levels, developing levels, pivots, profile and round numbers are out of this study. Level families: `4h`, `day`.
- Side is fixed by the level edge: a low is support, trade side long; a high is resistance, side short. The wrong-way orientation of METHOD.md is dropped (OURS, halves the family). Mirror everything below for shorts; the text describes longs.
- Zone: [L(1-b), L(1+b)], b=0.0025 (same 0.25% as the first study).
- Encounter ID: `{family}|{edge}|{level_available_utc}|{k}`. An encounter OPENS at the first completed 15m bar whose high-low range intersects the zone while the previous completed bar's range did not (or the level only just became available and the bar intersects). Opening records start time s, approach direction (sign of the previous bar close minus L), the full feature vector at s, and ATR normaliser A (below).
- Candidate extreme B = lowest low since the encounter opened (frozen into the ledger at each decision bar; known at that time).
- Termination (earliest wins, all logged as the termination reason): (a) 96 bars (24h) after open; (b) a 15m close more than 1.0*A below L (wrong-way, "failed encounter", KEPT); (c) the parent period of the next level of the same family and edge becomes available (superseded, KEPT); (d) data end. 
- Re-entry: after termination a new encounter on the same level needs 16 consecutive bars fully outside the zone and then an intersecting bar; it gets ordinal k+1. Only k=1 enters any test (first eligible encounter); k>1 is logged and reported descriptively only.
- UNTRIGGERED and FAILED encounters stay in the ledger and in every denominator. The ledger is one row per encounter per 15m bar until termination (bar-level at-risk table), built from features and level geometry ONLY; it has no outcome column.
- Normaliser A: simple mean of TR=max(H-L, |H-prevC|, |L-prevC|) over the last 20 completed 4h bars at the decision bar. NOT_IN_DATA if history is short. (Same definition as CYCLE_DESIGN.md; must be added to FORMULAS.md before coding, B1.)

## 4. Signals, common decision timestamps, controls

Nested steps. Both are tested only through matched risk sets, never against "all eligible closes".

- Step 1, `reclaim`: decision bar tau is the first bar of an open encounter with C_{-2}>L, C_{-1}<L, C_0>L (study.py reclaim, side-mirrored). Entry reference E = next 15m open after tau (one-bar execution delay is real and counted). Controls are encounters that are still open and AT RISK at their own decision bar tau' (no reclaim yet, not terminated, not already used), see matching below.
- Step 2, `reclaim + higher-low`: after a reclaim, the confirmation is the first completed 1h close above the latest confirmed 1h pivot high (rule of section 2) while a confirmed 1h pivot low exists above B. Decision bar tau2 = that 1h close. Elapsed time since the reclaim (tau2 - tau) is recorded. Controls are encounters that had a reclaim, are still open and unconfirmed at the same elapsed-since-reclaim, matched like step 1. The confirmation lag and the cost of waiting are part of the result, not hidden.
- Common timestamp rule: signal and control are scored at a decision bar that has the same elapsed bars since encounter open (|d elapsed| <= 4 bars for step 1, since reclaim for step 2), the same UTC week block, the same 6h UTC slot. The reference E and all outcome windows start at the next bar open after the decision bar for both. Neither arm's decision bar is chosen from its outcome.
- Matching (exact then caliper, all values past-only): exact on side, level family, V class, D class, A class, R class, 6h UTC slot, UTC Monday-start week block; caliper |dist_signal - dist_control| <= 0.05 percentage points where dist=|C_tau/L-1|; nearest dist wins; 1:1 greedy in order of tau, without replacement. Unmatched signals are counted and reported (match rate is a mandatory output; below 60% the cell is flagged MATCH-THIN). Never match on future path, outcome or the confirmation that has not yet occurred.
- Level-skill isolation: a placebo level L' = L*(1+s*m*A/L), s random sign, m random from {1.0,1.5,2.0}, drawn with seed 20261017 once per real level, rejected if within 1.0*A of any real level of that family and edge; the identical pipeline is run on placebo levels. Randomisation is by whole encounter and inside the same UTC week block. A real-minus-placebo difference is the level-skill estimate.

## 5. Outcomes (two separate endpoints, nothing from the 60m screen is reused)

Using E, frozen B (support) and A at the decision bar (mirror for shorts):

- Primary, local reaction (24h = 96 bars): success if E+1.0A trades before B-0.25A; failure if B-0.25A trades first; `timeout` if neither inside 24h; `censored` if the window runs past the data end (not a failure). Both barriers inside one 1m bar: report lower and upper success bounds, resolve with trades before any strategy claim. Success rate difference signal minus matched control is the test statistic.
- Secondary, swing persistence (30 days): success if E+3.0A is reached and no low below B-0.25A occurs for the full 30 days; any earlier breach is failure; incomplete window is `censored`. Descriptive only, counted in the family. The 180-day persistence outcome stays NOT_TESTED (five disjoint 180-day blocks, CYCLE_DESIGN.md).
- Mandatory excursions per signal and control: MAE and MFE in A units, reached within 24h and 30d; entry-to-B distance; confirmation lag; share of reclaim encounters whose confirmation never arrives; share whose price already moved +1.0A before confirmation (missed-move rate, diagnostic only, never a selection variable).
- Censoring and purging: each decision has label interval [tau+1 bar, tau+horizon]. Decisions whose intervals overlap on the same side are one CLUSTER (union by overlap, plus a 24h embargo after label end). The independent unit is the cluster, never the minute or the signature row. Features and terciles use only completed past bars, so no model is fitted on outcomes and no label purge is needed inside this design; if a later card fits thresholds, it purges 30 days around each test cluster.
- Costs: report stop width S=(E-(B-0.25A))/E and the fee share 14bp/S (and 20bp/S) per decision; share of decisions with S>=0.40% (VISION taker rule, item 0a). Funding, spread variability, impact and fills are NOT_IN_DATA; no P&L, only an execution-feasibility readout.

## 6. Joint-context family (frozen before any outcome table exists)

Contexts (oriented to side, overlapping, all reported with their overlap counts):

| ID | Definition | Reason (OURS) |
|---|---|---|
| C0 | all matched encounters, no context | reference, not in the confirmatory family |
| C1 | D=`up` AND A=`aligned_up` | support reclaim inside an up-structure |
| C2 | R=`bounded` AND range_pos <= 0.25 | range-bottom reclaim |
| C3 | D=`down` AND V=`high` | capitulation-style reversal reclaim |
| C4 | A=`conflict` AND V=`low` | compression with no timeframe agreement |

UNKNOWN or `mixed`/`transition` in a defining feature excludes the encounter from that context only; it stays in C0 and in the ledger, and its count per context is reported. No other phase combination is evaluated. Adding a context is a new preregistration.

## 7. Null, uncertainty, inference

- Null: matched paired difference of local-reaction success (signal minus control) equals 0 within each cell. Placebo-level difference as in section 4.
- Unit and interval: clusters (section 5); paired difference per cluster; 1,000 circular moving-block bootstrap draws of 7 UTC days, seed 20261017, same sampled days for all cells; zero-event days retained; pointwise 95% and Bonferroni (m=16) intervals reported. Report independent cluster count, event-day count and match rate next to each interval.
- Screen (not promotion): a cell passes the DEV screen only if >=100 matched clusters, >=30 event days, the m=16 Bonferroni lower bound of the paired difference > 0, median S>=0.40% and the placebo-level difference also > 0. Passing means "request fresh evidence", never "edge".
- Full lineage and every cell, including failures and C0, are written to a TRIAL_REGISTRY-style table. No cell is dropped for being negative.

## 8. Trial family (all variants declared)

Decision TF 1 (15m) x level family 2 (4h, day) x side fixed to edge x outcome. Confirmatory: contexts C1-C4 (4) x families (2) x steps (2) x primary endpoint = **16** tests, Bonferroni m=16. Reference/descriptive: C0 x 2 x 2 = 4. Placebo-level: C0 x 2 x 2 = 4. Secondary swing endpoint: 5 contexts x 2 x 2 = 20 (exploratory, no inference claim). **Attempted family = 44 views.** Cumulative with prior lineage: 130 + 8 + 126 + 44 = 308 counted looks on BTC candle/levels questions. Features tried 5 (D, R, V, A plus baseline F0), context definitions 4; no thresholds swept.

## 9. Power (computed before any outcome; achieved counts decide the label)

Paired binary difference, sd of the paired difference <= 0.9 (OURS, worst-case-ish for p~0.4), n matched clusters: detectable difference at 80% power = (z_{1-alpha/2}+0.84)*sd/sqrt(n). alpha=0.05/16 -> z=2.96: n=300 -> 19.7pp; n=100 -> 34pp; 10pp needs ~1,170 clusters; 5pp ~4,680. Expected clusters: 912 days x ~2 encounters/day x 2 families, then context and reclaim and matching losses leave a few hundred per cell at best, so most cells will have a detectable difference of 15-30pp. Pre-declared: any cell whose detectable difference exceeds 15pp is labelled INCONCLUSIVE (UNDERPOWERED), never "no edge" (power_mde.py). The stage-0 ledger count (no outcomes) decides which cells are INCONCLUSIVE before outcomes are touched. A pooled C0 negative is not evidence about any context.

## 10. Verification, tests and promotion

- Spec audit (this card): MyTradingSys/research/layer_lab/candle_close_2026-10-14/test_pre_reg_spec.py checks that every feature has equation / availability / UNKNOWN, all 12 slots and 0a-0f are answered, signals and controls share timing, and the family count is internally consistent.
- Build-time tests (required, fail-closed): (1) future perturbation: delete or randomise all bars after t and require byte-identical features, encounter rows and decision timestamps for every t (outcomes may change, decisions may not); (2) independent recompute (separate code path) of D/R/V/A, controls, match rate, cluster construction and bootstrap CIs from raw rows, tolerance 1e-9; (3) episode completeness: every opened encounter has one termination row; (4) a real application-import failure must make the test run exit nonzero (A6: catch only the optional pandas import) and the harness runs in an environment with pandas installed; (5) synthetic fixtures for each feature including UNKNOWN edge cases and tie pivots.
- Promotion: the whole policy (feature classifier + signal + controls + costs) must pass the DEV screen of section 7. Only then may a separate, operator-authorised card spend a fresh window. The existing 2024-07+ candle VALIDATION window is not to be used to fix the classifier, controls or costs; whether it may be read once for a final check is an operator decision, default NO (logged below).

## 11. Pre-build gate (0a-0f) and the 12 readiness slots

| Slot | Answer |
|---|---|
| 0a Cost | Smallest stop used is S=(E-B)+0.25A; the share with S>=0.40% is a reported output. If the median S<0.40% the idea is NOT TRADABLE at taker cost and is reported so. Maker entry unsupported (no fills). |
| 0b Gross | The first study's 60m gross screen was 0/126 positive after 14bp; there is NO cheap check supporting 2x cost. This design measures barrier hits in A units, which may exceed the 60m move, but gross-vs-cost is unproven: WAIVED because this is a descriptive/matched-control design, not a trading build. |
| 0c Record | No trader ledger (anonymous, NOT_IN_DATA). Hypothesis, not a core. |
| 0d Data | OHLCV only; OI, funding, aggressor flow, book NOT_IN_DATA; not needed for the features above. |
| 0e Power | Section 9: most cells INCONCLUSIVE in advance. |
| 0f Kill | If no context passes the m=16 screen with placebo support, the phase-conditioned candle-at-level idea on BTC 15m DEV is closed. Redesigns allowed: 1 (a new preregistration with new data). |
| 1 Home | OURS BTC perpetual, 15m decision, 4h/day levels, all UTC sessions, 24h local and 30d swing horizons. |
| 2 Ledger | NOT_IN_DATA (no source trader). Mechanical event definitions above are ground truth; the encounter ledger is built first without outcomes. |
| 3 Recall/fire rate | Trader recall NOT_IN_DATA, blocks replication claims. Fire rate (encounters/day, reclaim rate, confirmation rate, miss rate) is a mandatory stage-0 output. |
| 4 Inputs | Section 2 uses OHLC only; absent inputs are NOT_IN_DATA, never 0. |
| 5 Parity | Independent raw-row recomputation of levels, features, matching and CIs (section 10 test 2); no profile approximations. |
| 6 Economics | S, 14bp/20bp fee share per decision; no funding, no P&L. |
| 7 Fills | None assumed. E = next 15m open reference; touch/trade-through P&L not applicable until an execution rule exists. Barrier ties within one minute give bounds. |
| 8 Exits | Fixed barrier measurement (1.0A target, 0.25A beyond B invalidation) is a measurement, not a management rule; stated as such. |
| 9 Null | Matched at-risk controls on the same timestamps plus placebo levels (sections 4, 7). |
| 10 Power | Section 9: detectable difference 19.7pp at n=300, INCONCLUSIVE if above 15pp. |
| 11 Holdout | Forbidden. 2024-07+ stays sealed. No existing window is spent to fix classifier, controls or costs. Trial count 44 now, 308 cumulative. |
| 12 Stratification | Contexts C0-C4 plus per-side, per-family and per-UTC-month tables next to every pooled number; no cell extrapolated to a cycle bottom. |

### Unresolved blockers before an executable build
- B1: add the pivot rule, ATR normaliser A, F0, D, R, V, A definitions to backtest/layers/FORMULAS.md (expected values computed independently, not from code).
- B2: independent audit of this document by a different session or model (this author is the same family as the prior run).
- B3: stage-0 ledger count (no outcomes) and `power_mde.py` run to label INCONCLUSIVE cells before outcomes are read.
- B4: CI/research runner with pandas so build-time tests actually execute (audit A6).
- B5: no fresh out-of-sample window exists (2022-01..2024-06 inspected, 2024-07+ reserved); promotion needs an operator decision. Default taken: NO read of the reserved window.
- B6: fees, funding and fills for any trading conclusion are NOT_IN_DATA.

## Defaults taken (no operator input)
Fixed side by edge, 15m decision TF only, weekly levels excluded, primary endpoint local reaction, seed 20261017, Bonferroni m=16, 2024-07+ stays unread.
