AGREE=14 | DISAGREE=2 | NOT_IN_DATA=33

# Independent recheck: MTS alignment audit, 2026-11-03

## Method and provenance

I implemented the loader, 4H aggregation, causal pivot replay, Modified Schiff coordinates, VA filter, order timing, stop handling, 1m walk, statistics, and placebo independently in `recheck.py`. I read the permitted fork geometry and pivot rules, but did not import or call the producer's trade, stop, walk, or placebo functions. The five hand checks are callable with `python recheck.py --checks-only`; the full command is the task card's `python MyTradingSys/research/layer_lab/mts_audit_recheck_1103/recheck.py`.

The loader admits monthly filenames only from 2020-01 through 2024-06 before opening them, then applies the timestamp cutoff 2024-07-01 exclusive. It builds 4H bars from those minutes. Observed: 54 admitted files, 2,365,920 minute bars, 9,858 4H bars, zero duplicate or conflicting minute timestamps, zero missing minute slots, and zero incomplete 4H buckets. No VALIDATION/HOLDOUT bars were read. Full counts, seeds, and all 100 placebo run means are in `recheck_results.json`.

Provenance: zigzag lookback 4, 3% reversal, 1.5% stop, 60-bar timeout, and Modified Schiff + VA are the audit/study encoding under review; they are not trader-sourced settings and remain OURS as trading parameters. Fee rates 2bp maker + 5bp taker come from `MyTradingSys/backtest/fees.py:36-37`; the extra 2bp slippage is an OURS assumption inherited from the study's cost expression, making 9bp total. The 4H study-style and CAUSAL arms deliberately retain target-before-stop and no fill-bar stop semantics; EXACT uses next-bar order activation, a moving median-line target, and stop-first within each minute. The bootstrap implementation follows the producer script's calendar-month resampling convention, independently implemented; the audit text itself does not specify its CI method.

## Section 2: independent numerical replay

All means and CIs are net percent per filled trade. CIs use 2,000 calendar-month block bootstrap draws, seed 7, and the same order-statistic endpoints as the audited method.

| Arm | n | Mean | 95% CI | PF | Finding |
|---|---:|---:|---:|---:|---|
| STUDY rules: final pivots, 4H walk | 205 | +0.748% | +0.241..+1.418 | 1.77 | AGREE; matches `AUDIT.md:21` |
| CAUSAL pivots, 4H fills | 276 | +0.336% | -0.062..+0.890 | 1.32 | AGREE; matches `AUDIT.md:22` |
| EXACT: causal, next-bar, 1m stop-first | 272 | -0.011% | -0.336..+0.416 | 0.99 | AGREE; matches `AUDIT.md:23` |
| Random-entry placebo, 100 runs | 100 | -0.104% mean of run means | p95 +0.124 | n/a | DISAGREE with audit's -0.109 / +0.116 (`AUDIT.md:24`) |

The placebo is ours: one random 4H bar open per matched sample, in the same calendar year, matching exact-trade side, 1.5% stop and entry-to-target distance; seed 11; 100 runs. The producer's `pitchfork_recheck.py:271` enters at the first minute close while its walk also tests that minute's high/low, mixing a later close with earlier extrema. That mismatch explains why the placebo numbers are not directly comparable. The independent EXACT result is inside our placebo distribution (26/100 placebo means are at least -0.011%); it supports the same no-edge conclusion. This is not a p-value.

The cutoff-safe source contract is independently verified by the sentinel test, and the five hand checks pass: excluded-month path rejected before open; profile fixture returns the inclusive upper bin edge; stop wins a same-minute stop/target collision; mirrored long/short returns agree; EXACT activation is the bar after confirmation. See `recheck.py` and `recheck_results.json`.

## Claims in sections 1 and 3–7

`NOT_IN_DATA` means this pass did not independently reproduce the cited underlying study, runtime state, commit classification, or archived result. “AGREE” is limited to the stated claim/evidence, not an upgrade of a registry-only result into measured trading evidence.

| Section | Claim checked | Finding | Proof |
|---|---|---|---|
| 1 | No promoted setup | AGREE | `MyTradingSys/execution/promoted_setups.json:1-3` has an empty entries list. |
| 1 | Audit's 117-row verdict count was its as-of snapshot | AGREE | Current `MyTradingSys/research/VERDICTS.csv` has 118 rows: 55 FAIL, 40 INCONCLUSIVE, 13 UNPARSED, 8 BLOCKED, 2 PASS. The task card note says the audit counted 117 before its subsequent register update (`MyTradingSys/system/tasks/mts-audit-1103-independent-recheck.json: note`). |
| 1 | Both PASS rows are carry rows | AGREE | `MyTradingSys/research/VERDICTS.csv:26-27`; both are carry basis, n=911. |
| 1 | S0 exit failed because ready cards exceeded the <=15 cap | DISAGREE as current status | D7 says on 2026-11-03 that S0 parking ended and the 15-card cap no longer applies (`MyTradingSys/research/v1_plan_2026-10-20/D7_ROADMAP.md:10`). S0 is still the displayed stage (`:14`); the old cap cannot establish today's exit status. |
| 1 | No signed q-v1-bar / q-v1-layers decision | NOT_IN_DATA | Search for those exact IDs returned no matches, but this does not rule out an equivalent signed decision under another heading. |
| 1 | Seven S3 run states | NOT_IN_DATA | The referenced individual run records were not re-audited in this replay. |
| 1 | Seven-day commit categories and counts | NOT_IN_DATA | The 2,468-commit classification was not independently regenerated. |
| 3 | Blind-read/Argon comparison proves audits check transcription more than method | NOT_IN_DATA | The cited cross-vendor batch and Argon source records were not independently replayed. |
| 3 | Pitchfork lacked a VERDICTS row at audit time | NOT_IN_DATA | The current row exists, and section 7 says it was added; this pass did not compare the pre-audit register blob to prove the historical absence. |
| 3 | Most of 98 reverts were lint or cost-inventory trips | NOT_IN_DATA | No independent commit classification was run. |
| 3 | 94% live time exits / 71% turn_of_candle alerts | NOT_IN_DATA | No runtime/order data was read; those values remain register claims. |
| 3 | No PASS without verdict row, causal replay, and another model's trade-loop rerun | AGREE as policy | D7 records this rule (`D7_ROADMAP.md:11`); the causal pivot test is present at `MyTradingSys/research/mts_audit_2026-11-03/test_pitchfork_recheck.py:7-24`. |
| 4 | Pitchfork has no supported edge | AGREE for this encoding | Independent EXACT is -0.011%, CI crosses zero, PF 0.99; `MyTradingSys/system/LAYERS.md:249,253`. |
| 4 | Live Pitchfork receives 3 bars but requires 15 | NOT_IN_DATA | Not runtime-checked; no live tree or process was accessed. |
| 4 | Four-oscillator/Kurisko readiness and fee claims | NOT_IN_DATA | Its underlying study was not rechecked. |
| 4 | Malkan RSI readiness claim | NOT_IN_DATA | Its underlying study was not rechecked. |
| 4 | RSI deep-buy drift/readiness claim | NOT_IN_DATA | Its underlying study was not rechecked. |
| 4 | Krown recall and DEV status | NOT_IN_DATA | Its underlying study was not rechecked. |
| 4 | WaveTrend trigger/OB claims | NOT_IN_DATA | Its underlying study was not rechecked. |
| 4 | Tom setup disposition claims | NOT_IN_DATA | Its underlying study was not rechecked. |
| 4 | Fabio v3 and Model C status claims | NOT_IN_DATA | Its underlying study was not rechecked. |
| 4 | Levels confluence status | NOT_IN_DATA | Its underlying study was not rechecked. |
| 4 | CryptoCred status | NOT_IN_DATA | Its underlying study was not rechecked. |
| 4 | Pizzino status | NOT_IN_DATA | Its underlying study was not rechecked. |
| 4 | C26 regime-fade candidate claim | NOT_IN_DATA | Its underlying study was not rechecked. |
| 4 | Carry is positive but non-directional | AGREE as register description | `VERDICTS.csv:26-27` records the two positive carry-only rows; no directional inference is made. |
| 4 | Rumers/Jala/Michael/Habib/callers remain extraction or first-count work | NOT_IN_DATA | The individual source studies were not rechecked. |
| 5 | DAX chain is abandoned, not disproven | NOT_IN_DATA | No DAX records were examined. |
| 5 | RSI divergence archive disposition | NOT_IN_DATA | No cited RSI runs were independently examined. |
| 5 | CVD divergence archive disposition | NOT_IN_DATA | No cited CVD runs were independently examined. |
| 5 | OI-next-direction archive disposition | NOT_IN_DATA | No cited OI runs were independently examined. |
| 5 | Ladders/martingale archive disposition | NOT_IN_DATA | No cited runs were independently examined. |
| 5 | Tom VP/old BTC archive disposition | NOT_IN_DATA | No cited holdout records were independently examined. |
| 5 | Q33/funding-CVD/session/turn-of-candle/candle-close archive disposition | NOT_IN_DATA | No cited studies or exit parity records were independently examined. |
| 5 | Chronos/fractal archive disposition | NOT_IN_DATA | No cited DEV studies were independently examined. |
| 6 | Probability-layer code/owner/evidence and prior data blocker status | NOT_IN_DATA | `MyTradingSys/backtest/prob_table.py` and its ready card exist, but the claimed prior BB-map run and state ownership were not reconstructed here. |
| 6 | The unification steps are explicitly a proposal, with a falsifier | AGREE as framing only | `AUDIT.md:68-78` labels the section OPINION and states a pooled log-loss/EV falsifier; proposal validity is untested. |
| 6 | 25.8% drift and 53.2% hit-rate example | NOT_IN_DATA | The cited base tables were not re-run. |
| 7 | Pitchfork VERDICTS row added | AGREE for current state | `MyTradingSys/research/VERDICTS.csv:119` records the 272-trade exact causal recheck as FAIL / UNPARSED. This does not establish the exact time it was added. |
| 7 | Layer map/index row relabelled | AGREE | The layer-map entry withdraws PASS (`MyTradingSys/system/layer_map.json:1501-1503`) and the Pitchfork index says the 4H PASS was withdrawn (`MyTradingSys/system/LAYERS.md:249,253`). The remaining 734/64.85% effects text is the original study record, not a replacement exact result. |
| 7 | All result cards corrected | NOT_IN_DATA | I did not inspect every result card's before/after state. |
| 7 | DEV confluence permission and PASS rule added | AGREE | `D7_ROADMAP.md:10-11` records both operator changes. |
| 7 | Named blockers lifted and DAX cards dropped | NOT_IN_DATA | Those individual task transitions were not reconstructed. |
| 7 | Six new raw cards were created in that turn | NOT_IN_DATA | Card files exist now, but their same-turn creation and historical raw states were not proven. |
| 7 | Testnet, fee-net, pre-registration, single VALIDATION read, sealed HOLDOUT retained | AGREE as documented policy | `CLAUDE.md` hard rules and `D7_ROADMAP.md:11` preserve the testnet/mainnet and validation guards. |

## Disagreements and missed items

1. The current `VERDICTS.csv:119` row records gross mean +0.079% and cost 0.09%; its net is -0.011%, matching the independent replay. Its CI field remains UNPARSED, so the register does not itself contain the confidence interval. Historical before/after state and all result-card edits remain unverified.
2. The audit's S0 threshold finding is stale under the same-day D7 update that removed the ready-card cap.
3. The exact replay agrees with all three listed arm statistics after independent implementation. The placebo mean/95th percentile differ under an open-price entry and matched-side/target walk; the producer uses first-minute close with that minute's high/low, a timing inconsistency.

The audit's central conclusion is supported: this exact BTC 4H encoding does not show fee-net edge. Operator-drawn forks and the other archive studies remain untested here. No post-2024-06-30 candles were opened.

Loader caveat: the producer's `load_1m` enumerates and opens every matching monthly file before applying the timestamp cutoff (`pitchfork_recheck.py:70-81`); its 4H CSV loader likewise opens the mixed-window file and then filters rows (`:61-67`). This pass did not run that loader. My loader filters filenames before opening, and builds only the cutoff-safe 4H aggregates from those minutes. This source distinction does not alter the exact replay result above.
