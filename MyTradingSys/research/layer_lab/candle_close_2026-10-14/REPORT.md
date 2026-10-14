# BTC candle-close research: first LAB result

RESULT (2026-10-14, JIS-NUC): **0 of 126 pooled arms pass the frozen exploratory screen. No validated tradable edge established.**

The study answers a narrow but useful part of the operator request: do six close sequences around prior 4h/day/week highs and lows improve next-hour direction on BTC? It does not estimate cycle-bottom probabilities. Research and an executable DEV pilot are complete; swing/cycle label design is complete, while its outcome study, exact YouTube replication and out-of-sample strategy validation remain uncompleted.

Data: 1,313,280 Binance BTCUSDT perpetual 1m bars, January 2022-June 2024 (912 days); all 30 exchange archive hashes verified, zero missing minutes. 105,541 event rows across correlated arms, NOT that many independent trades. 31-day context warmup. Validation July 2024 onward and holdout were not opened.

Test matrix: 1/2/3/5/15/30/60m triggers x prior completed 4h/day/week levels x rejection/break/acceptance/reclaim/retest/strong break. Levels and daily phase/trend plus 4h direction are causal. First signal per day/side/family/signature/TF; measure from next minute open to open 60 minutes later.

Every pooled arm has negative mean after the fixed 14bp round-trip cost screen, ranging from -26.83 to -4.68 bp/event. This is a price-return screen, not historical fee/funding-adjusted P&L. No arm has a positive lower Bonferroni screening bound for incremental positive-return probability.

## The requested minute-close examples

Prior-day high/low levels, both directions pooled after sign adjustment. Positive = price ends favourably after 60 minutes, NOT stop/target win rate. CI = pointwise 95% seven-day block bootstrap; it is not multiplicity-adjusted. Selected below by timeframe and family for readability, not by performance.

| TF | Signature | Events / days | Positive % [95% CI] | Lift vs matched nearby closes, pp | Mean less 14bp, bp |
|---|---|---:|---:|---:|---:|
| 1m | rejection | 1089 / 612 | 47.8 [45.5, 50.0] | -5.5 | -15.53 |
| 1m | break | 1170 / 613 | 49.5 [47.7, 51.4] | -3.0 | -11.90 |
| 1m | acceptance | 1087 / 585 | 48.0 [45.9, 50.0] | -6.1 | -15.41 |
| 1m | reclaim | 901 / 509 | 50.3 [47.8, 52.9] | -4.2 | -13.52 |
| 1m | retest | 1030 / 598 | 48.2 [45.5, 50.7] | -4.9 | -17.44 |
| 1m | strong_break | 1034 / 555 | 49.0 [47.1, 50.9] | -3.7 | -13.61 |
| 2m | rejection | 1040 / 603 | 48.8 [45.9, 51.4] | -5.3 | -14.15 |
| 2m | break | 1107 / 590 | 50.0 [48.1, 51.9] | -3.2 | -12.81 |
| 2m | acceptance | 1007 / 555 | 49.5 [46.9, 51.9] | -5.8 | -11.95 |
| 2m | reclaim | 760 / 457 | 53.2 [50.4, 56.1] | -1.8 | -10.13 |
| 2m | retest | 969 / 575 | 49.9 [46.6, 53.3] | -4.1 | -15.43 |
| 2m | strong_break | 937 / 525 | 49.5 [47.0, 52.3] | -4.1 | -13.73 |
| 3m | rejection | 992 / 580 | 49.7 [46.7, 52.8] | -4.9 | -18.01 |
| 3m | break | 1084 / 585 | 49.0 [47.0, 50.9] | -4.1 | -13.76 |
| 3m | acceptance | 956 / 540 | 48.8 [46.1, 51.4] | -6.5 | -13.01 |
| 3m | reclaim | 703 / 427 | 50.4 [47.2, 53.5] | -3.5 | -15.85 |
| 3m | retest | 908 / 552 | 51.0 [47.6, 54.1] | -4.6 | -16.03 |
| 3m | strong_break | 884 / 511 | 48.1 [45.5, 50.7] | -5.6 | -12.21 |

A useful example of why win rate alone misleads: the 2m daily-level reclaim is positive 53.2% of the time, yet averages -10.13bp after the cost screen and does not beat its matched nearby-close probability. That is neither a trading recommendation nor evidence for a 53.2% cycle-bottom forecast.

## Phase readout example

Fixed illustration: 1m close-through break at prior-day levels. Phase labels are OURS backward-looking daily proxies, not retrospectively identified market cycles. These subgroup means have no standalone promotion gate.

| Daily phase | Events / days | Positive % | Lift, pp | Mean less 14bp, bp |
|---|---:|---:|---:|---:|
| bear | 249 / 130 | 51.4 | -0.9 | -7.83 |
| bull | 353 / 186 | 49.3 | -2.9 | -12.15 |
| neutral | 568 / 298 | 48.8 | -3.9 | -13.53 |

All arms and contexts are preserved in TRIAL_REGISTRY.csv, by_phase.csv, by_trend.csv, by_fourdir.csv, by_side.csv, by_slot.csv and by_month.csv. Phase, local trend and higher-timeframe direction are separate axes. Profitable-looking subgroup cells, if any, were not selected or validated.

## Checks and limitations

- Eight synthetic tests pass, including an end-to-end synthetic event-table check. Six initial tests failed before the implementation existed; gap-window and pandas-array regressions were each reproduced before correction.
- Independent verifier: 30 archive hashes, 126 randomly sampled events reconstructed directly from raw minute rows (level, OHLC sequence, timestamp, direction and forward return), and all 126 arm counts/means: PASS. The verifier does not establish statistical calibration of the null.
- Data audit correction: the first gap alarm was a pandas timestamp-resolution bug; actual gaps are zero. A second run stopped on a read-only array. Both failures preceded probabilities and are logged; no threshold or pattern was tuned after results.
- First-event signals are compared with all eligible nearby closes, so opportunity weighting and within-slot path dependence differ. Negative lift is descriptive; it does not prove the pattern causes worse outcomes. A first-opportunity comparator and random-level placebo are needed before interpreting level skill.
- Nearby controls match a 0.25% band, date, six-hour slot, level high/low, side and phase. They do not exactly match distance, volatility, candle size or within-slot trend. Seven-day bootstrap may miss longer dependence; normal-bootstrap Bonferroni bounds are approximate and not adoption evidence.
- N ranges 59-1761 per arm; 4 cells have fewer than 100 events. Rare-cell negatives are inconclusive. Repeated triggers across TFs/levels are not independent.
- Current family: 126 trial arms plus descriptive subgroup looks. Prior lineage includes 130 classical candle trials and eight sizing arms, at least 264 arms combined; this is not the total MTS search count.
- No funding, variable spread, latency, execution strategy, overlapping-position accounting, mark-price liquidation or calibrated stop/target probability. No PBO/DSR claim: those gates remain unmet, not passed by omission.
- A 60-minute endpoint can miss shorter reactions and later swings; only one horizon, one venue, fixed UTC anchors and three level families were tested. Requiring a close near the level excludes distant displacement closes. A wider family could behave differently but is a new registered search.
- Macro lows/highs and accumulation/distribution stages remain NOT_TESTED. A 2022-2024 sample is not enough independent BTC cycles to establish precise cycle-bottom odds.

## Direction after this result

Do not promote the six generic patterns to live rules and do not spend validation on a pooled candidate that failed DEV. The research conclusion is to test contextual, causal reversal sequences only as new preregistered hypotheses. No claim is made that all close-based trading fails.

1. Independent audit: verify opportunity-matched controls, timeframe anchors and phase-cell evidence. Freeze any additional hypotheses before testing; all subgroup discoveries count as selection.
2. Swing/cycle task: define local, swing and cycle outcomes separately; causal pivot confirmation and earliest alert timing; log every failed candidate. Count independent episodes, report recall/precision/base-rate lift and lead time, use leave-one-episode/cycle-out checks where feasible.
3. Source-specific replication: identify the watched channel/video and form a chronological design/check ledger from unedited examples. Current source identity is NOT_IN_DATA; Krown sources are relevant definitions only.
4. Only a surviving DEV candidate advances to a frozen out-of-sample execution study with actual costs, funding, fill/stop ambiguity, purging, placebo tests, calibration and the MTS adoption gates. Historical windows already used by any related study must be disclosed as contaminated, not reused as pristine holdout.

The independent audit is saved as a ready task card. The causal swing/cycle design is completed in CYCLE_DESIGN.md, including a 12-slot readiness check: current DEV provides at most five disjoint 180-day blocks, so precise macro odds are underpowered. No extension outcome run is reported. Existing LC1-LC4 tasks remain separate and unmodified.

## Reproduce / inspect

Research rationale and verified sources: RESEARCH.md. Frozen rules: METHOD.md (commit 273ca7c). Harness freeze: 7d46d7b with pre-outcome compatibility fixes documented in DATA_AMENDMENT.md; exact executed file hash in results.json. Full events: events.csv.gz. Input URLs/hashes: results.json manifest.

`python MyTradingSys/research/layer_lab/candle_close_2026-10-14/test_study.py`
`python MyTradingSys/research/layer_lab/candle_close_2026-10-14/verify_result.py`
`python MyTradingSys/research/layer_lab/candle_close_2026-10-14/study.py` refuses to overwrite existing results. Any fresh statistical run must be logged first. Python with numpy and pandas is required. Data download is public and DEV-only; no exchange account is accessed.

## Subsequent audit, 2026-10-14

INDEPENDENT_AUDIT.md identifies phase-model/application gaps, unequal control sampling, incomplete inference verification and a reproduced test-import skip defect. The original 126-arm outputs remain unchanged. Read that audit before interpreting phase-specific applicability; NEXT_EXPERIMENT.md records the required design correction before another outcome run.
