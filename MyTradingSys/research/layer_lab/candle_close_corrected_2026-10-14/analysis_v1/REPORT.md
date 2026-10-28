# Corrected phase-first BTC candle study

RESULT (2026-10-14, JIS-NUC): **0 of 1,764 registered cells pass the frozen candidate screen. Phase applicability remains unproven.**

The repeat now implements joint causal phase contexts, a common first-encounter ledger and confirmation time, matched nonsignature controls, random-line level controls, cell-level uncertainty, historical funding-rate coverage and one-hour/one-day/path outcomes. It preserves the original run and the sealed validation/holdout. It is exploratory reuse of already inspected DEV, not an out-of-sample confirmation.

## What changed

- The same six signature equations and seven trigger timeframes remain. Sampling deliberately changes from the first pattern anywhere in a day to the first known level encounter per family/high-low identity/day, followed by a fixed three-candle decision. Signal and control share that wait. This changes the population and event count; old/new win rates are not directly comparable.
- Four-hour structure distinguishes uptrend, downtrend, bounded range, transition and unknown. A bounded range requires stable old/recent boundaries and repeated separated boundary contacts, in addition to low efficiency. One-hour structure, trade orientation, range location and past-relative volatility form six joint contexts. Daily 30-day momentum is retained only as accurately named metadata.
- Each signature is compared with up to ten feature-matched nonsignature encounters from at least five different days. Matching uses phase, approach, level identity, decision-side/location, volatility and clock, and excludes the signal day. Coverage and covariate balance can disqualify a cell. A separate real-versus-placebo arm tests level skill using the same encounter mechanics.
- Outcomes include 60min and 24h directional price returns; 24h +/-1ATR first passage with ambiguous-minute bounds; and whether the candidate extreme survives and produces a favourable move. These are local outcomes, not cycle-bottom labels or a complete managed trading strategy.
- Funding covers all 2,736 nominal settlements, verified across 30 exchange files. The funding amount uses a settlement trade-price notional proxy; 14/20bp fee/slippage assumptions remain scenarios. No claim of exact mark-price/account P&L.

## Data and counting

Same 1,313,280 minute bars, 2022-01-01 through 2024-06-30. 41,093 first contacts across real/placebo level sets and seven TF views; 1,506 rejected for insufficient/unknown context. 19,564 eligible real contacts and 20,023 placebo contacts each receive both side orientations, giving 79,174 ledger rows. These overlapping views are not independent trades.

83,385 signature/horizon match records reuse those encounters. Matching coverage across valid signal opportunities is about 76.8% overall. Every one of the 1,764 cells remains in TRIAL_REGISTRY.csv, including empty/unmatched/censored cells. The 5,292 planned metric family governs screening bounds; previous lineage includes at least 264 arms, not the entire MTS search.

## Results by joint context

Counts include six signature arms and the level-placebo arm, at both horizons. A positive mean alone is an exploratory observation; the quality columns do not assert a trading edge.

| Context | Cells with matches | Cells with N>=100 | Pass sample/coverage/balance checks | Positive 14bp/funding mean cells | Full candidates |
|---|---:|---:|---:|---:|---:|
| RANGE_EDGE | 46 | 0 | 0 | 22 | 0 |
| RANGE_INTERIOR | 104 | 0 | 0 | 23 | 0 |
| TRANSITION_HIGH_VOL | 138 | 14 | 0 | 53 | 0 |
| TRANSITION_OTHER | 294 | 124 | 64 | 56 | 0 |
| TREND_ALIGNED | 8 | 0 | 0 | 2 | 0 |
| TREND_CONFLICT | 242 | 14 | 0 | 93 | 0 |

Interpretation:

- 832 cells have matched observations; 680 of these have fewer than 100 matched events. Another 724 cells have eligible signals but no qualifying controls; 208 have no eligible signal. These are not 932 demonstrated failures.
- 152 cells have >=100 matched events and >=30 signal days. Requiring >=80% matching coverage leaves 110; requiring max standardized covariate difference <=0.25 leaves 64, all TRANSITION_OTHER. None has a positive adjusted lower bound for its 14bp/funding mean.
- 249 matched cells have a positive point mean after the 14bp/funding screen (71 at one hour, 178 at one day). Only five of the 64 sample/coverage/balance-qualified cells have a positive point mean; none survives the confidence screen. This supports continued investigation, not selecting a profitable-looking cell.
- No trend-aligned or bounded-range cell has 100 matched events. Trend-conflict/elevated-transition cells with that count still fail coverage or covariate balance. Their phase-specific edge is INCONCLUSIVE because adequate comparable evidence is absent.
- Thus the result is not "no phase works". It is "no candidate demonstrated an edge under this frozen phase/encounter/matching design; most named phase cells are sparse or poorly comparable".

## A familiar example, now scoped correctly

For the 2m reclaim at prior-day levels, TRANSITION_OTHER has 29 matched events on 29 days. One-hour favourable-return rate is 27.6% and mean after the 14bp/funding screen is -43.06bp; 24h favourable-return rate is 51.7%, but the screened mean remains -42.23bp. Neither has N>=100. Other contexts have at most five matches or no match. This differs from the old 760-event, 53.2% example because it is a different common-encounter population and fixed confirmation time, not because the original file was overwritten.

The old example cannot be carried forward as a phase-specific forecast. A local reaction, an eventual favourable close and retention of the candidate low/high are separate outcomes. Full event/path columns are preserved in encounters.csv.gz; no best-case examples were selected as strategies.

## Verification and repairs

- Twelve numerical tests execute with no skips in research_gate.py. They check structural/mirrored/range/unknown cases, matching exclusions/calipers/distinct days, control-day uncertainty, funding arithmetic/jitter, path ambiguity/censoring, an independently known inference fixture, and whole-future-truncation invariance.
- The original test-import bug is fixed and reproduced fail-first: missing optional pandas may skip explicitly; a broken application import must fail. The main CI still lacks pandas, so it executes pure-numpy phase/control tests and the import guard while pipeline cases are explicitly skipped. The separate research gate fails on any skip and was actually run locally. A general CI green badge is not claimed to execute every numerical pipeline case.
- Independent verifier PASS: 30 price hashes +30 funding hashes; 126 raw phase/level/context/signature/return/funding reconstructions; 126 control selections independently reproduced; all 1,764 cell counts/means checked; ten actual CI/bound reconstructions across the five highest-count cells. It does not independently replicate every interval or validate the phase classifier against human chart annotations.
- Two problems were stopped before corrected outcomes: future-length-dependent random placebo allocation, fixed with per-level-availability seeds; and millisecond jitter in reported funding timestamps, normalized to the nominal 8h slot with a bounded check. PRE_OUTCOME_FIXES.md and FROZEN_ATTEMPT1.json preserve the history. The first funding attempt produced no outcome table.
- Full offline quick gate passed during this run. Statistical outputs and code hashes are frozen; no post-result parameter tuning or fallback matching was performed.

## Limits and next decision

The classifier is a transparent OURS operational model, not a proven universal market-phase detector. It uses 20-bar structure windows and fixed thresholds. Joint filters and the three-bar decision can be restrictive; confirmation delay differs with trigger TF (3min to 3h). Phase is frozen at the encounter start and can change during that wait. The original six-pattern retest remains a local proxy, not the full discretionary break-and-retest sequence.

Matching fails for many events and does not guarantee causal identification. Confidence calculations resample signal/control outcome contributions but hold the feature-based match graph fixed; full rematching uncertainty and dependence longer than seven days are not modeled. Random placebo distances are approximate (within +/-25%), not exact equality. One realization is not an exhaustive random-level experiment.

There is no validation, portfolio/execution backtest, mark-price risk, source-faithful YouTube ledger or calibrated macro-bottom probability. At most five non-overlapping 180-day blocks fit the current DEV; cycle-scale odds remain underpowered. No Tom/Fabio or live layer was changed.

Next move: keep this run frozen. Benchmark causal phase labels on charts whose future is hidden, and design a smaller next experiment with sufficient episode/common-control support. Obtain new eligible historical/forward evidence under a fresh registered data-lineage plan. Do not loosen classifiers/calipers now to manufacture winners, and do not consume the sealed validation window while fixing design. No current candidate is promoted.

## Artifacts and reproduction

PRE_REG.md + PRE_OUTCOME_FIXES.md: exact scope/equations. FROZEN.json and results.json: executed hashes. TRIAL_REGISTRY.csv: all cells. PHASE_SUMMARY.csv: context readout. encounters.csv.gz: every eligible real/placebo side and path. matches.csv.gz: exact control graph. verification.json: check scope. Original study directory remains unchanged except its import guard repair and design-pointer document.

Run research_gate.py before any statistical run; it refuses skipped checks. engine.py refuses existing results. verify.py reproduces checks from the existing local archives without rerunning strategy outcomes. Numerical dependencies: numpy/pandas; funding checksum verification uses public network access. All prices/funding are restricted to DEV.
