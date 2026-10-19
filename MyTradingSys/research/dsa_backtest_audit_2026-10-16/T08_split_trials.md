# T08: split integrity and trial inventory

Timestamp and trial metadata were checked without inspecting protected returns.
The orderflow runner still defaults to incompatible calendar phases; consolidated trial coverage also remains incomplete.
Historical input reconstruction is blocked, so this audit cannot certify how much untouched out-of-sample data remains.

**Verdict: BLOCKED for full historical coverage; FIX-FIRST for the confirmed default-run risk. UNCHECKED C2 result pending cross-vendor review.**

## Scope and reproduction

Base SHA `6d79774920946049f61b322d739e29817644608a`. Run from repository root:

```
python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T08/audit_metadata.py.txt
python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T08/split_probe.py.txt
python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T08/build_report.py.txt
```

| Check | Method and evidence | Result |
|---|---|---|
| Static split inventory | R1: tracked Python source search, `out/split_map.csv` | 527 matching lines across backtest/research; candidate inventory, not proof every date filter was found |
| Artifact timestamps | R1: CSV timestamp/phase projection only, `out/artifact_windows.csv` | 67 window groups; these are output-event bounds, not loader bounds |
| Floating splits | R2: actual split function AST applied to copied timestamp buckets | 13 runner/timeframe combinations; zero outcome computation |
| Historical trials | R1: every committed revision of 19 trial CSVs, identity projection | `out/trial_history.csv`; lower bounds, not an exact independent-test count |
| Seal candidates | R1: CSV dates and outcome column names only | 11 lexical candidates, all use publication/run `date`; none alone proves market HOLDOUT exposure |
| JSON/binary/Markdown outcomes | Not opened for protected values | BLOCKED: safe metadata projection and source-run manifests required |

No raw footprint file was opened, so no footprint exposure row was added. Existing exposure-ledger metadata was read.

## Findings

| ID | Severity / status | Evidence and reproduction | Effect and size | Fix / card |
|---|---|---|---|---|
| T08-F1 | S1 CONFIRMED implementation risk; no new protected return run | `orderflow_views_2026-10-14/study.py:215-221,240,252,287`; R3 AST phase probe `out/orderflow_phase_probe.json` | Without OFV_DEV_ONLY=1, December 2024 is DEV and August 2025 is VAL; main phases are VALIDATION and HOLDOUT. Default execution evaluates all phases and writes results.json. Prior DEV rerun did not remove this default. Verdict impact not recomputed. | Default fail-closed DEV cutoff; protected phases need explicit authorized entry point. `t08-orderflow-default-dev-guard` |
| T08-F2 | S3 CONFIRMED coverage gap (no measured verdict change) | `scripts/dev/trial_ledger.py:31-34,83-88`; R1 trial inventory vs built ledger study identities | Eight lowercase trials.csv files contain 176 rows and their studies are absent from both global ledgers. Some rows are count-only; 176 is not 176 independent outcome trials. Gap G6 shipped its nine-registry scope correctly; this is the uncovered extension. | Add schema-aware lowercase-trial adapters and complete variant keys. `t08-ledger-lowercase-trial-coverage` |
| T08-F3 | S3 CONFIRMED provenance limitation | R2 `out/split_probe.json`; default input roots absent, raw inputs ignored; R1 holdout_reads.csv header only | Original runner input endpoints and authorizations cannot be reconstructed from this checkout. Existing ledger documents historical protected exposure; an empty new skeleton is not proof of no reads. | Retrieve timestamp-only manifests and authorization provenance, never returns. `t08-original-input-window-provenance` |

F1 adds a remaining unsafe default, rather than repeating the already-known historical orderflow exposure. F2 does not claim the old eight-row central ledger remains current: it now has 29 rows; the built ledger has 1,279 rows from nine registries.

## Lead L2: narrower than the original suspicion

CONFIRMED unguarded floating split, but not the claim that its first OOS bar necessarily lies in HOLDOUT.
The copied dataset has 2,501,280 rows, 2,491,200 unique timestamps, 2022-01-01T00:00:00+00:00 through 2026-09-26T23:59:00+00:00.
On this timestamp set, OOS starts in main VALIDATION and extends into HOLDOUT. This does not prove any historical result used these exact inputs.

| Runner | Timeframe | Copied timestamp buckets | First OOS timestamp UTC |
|---|---|---|---|
| t055 | 1m | 2491200 | 2025-04-26T00:00:00+00:00 |
| t055 | 5m | 498240 | 2025-04-26T00:00:00+00:00 |
| t055 | 15m | 166080 | 2025-04-25T23:45:00+00:00 |
| rsi | 15m | 166080 | 2025-04-25T23:45:00+00:00 |
| rsi | 60m | 41520 | 2025-04-25T23:00:00+00:00 |
| rsi | 240m | 10380 | 2025-04-25T20:00:00+00:00 |
| rsi | 1440m | 1730 | 2025-04-26T00:00:00+00:00 |
| fabio | 5m | 498240 | 2025-04-26T00:00:00+00:00 |
| fabio | 15m | 166080 | 2025-04-25T23:45:00+00:00 |
| fabio | 60m | 41520 | 2025-04-25T23:00:00+00:00 |
| cryptocred | 15m | 166080 | 2025-04-25T23:45:00+00:00 |
| cryptocred | 60m | 41520 | 2025-04-25T23:00:00+00:00 |
| cryptocred | 240m | 10380 | 2025-04-25T20:00:00+00:00 |

Default roots `Dumps/backtest/raw_1m_2022/klines` and `Dumps/backtest/raw/klines` are absent. **Today's default-loader endpoint: BLOCKED for all four runners. Historical endpoint at publication: BLOCKED for all four.** This probe preserves the actual split function, but buckets timestamps independently; it does not claim to execute each original resampler, loader, or candidate-specific root selection (T055 C1 uses raw only).

## Dynamic coverage by original brief study

| Study | Timestamp evidence available | Actual per-phase loader / historical endpoint |
|---|---|---|
| gross_effect_screen | ledger 2022-01-17..2024-06-30, 1,440 rows | BLOCKED: wrapper not run; output bounds only |
| opr_preopen_tops | ledger 2022-01-06..2024-06-26, 308 rows | BLOCKED: wrapper not run |
| mal_bb_mid_engulf | ledger 2022-01-03..2024-06-30, 1,179 rows | BLOCKED: wrapper not run |
| opr_bb_mtf_center | ledger 2022-01-03..2024-06-29, 476 rows | BLOCKED: wrapper not run |
| opr_weekly_low_round_sweep | event ledger 2022-01-01..2024-06-26, 1,060 rows | BLOCKED: wrapper not run |
| wlow_bounce_bbrsi60 | trigger timestamps 2022-01-11..2024-04-18, 32 variant-event rows | BLOCKED: wrapper not run; rows are not unique trades |
| krown_malkan | first/last metadata ends by 2024-06-30 | BLOCKED: wrapper not run; count-only study |
| qriptal calls | publication dates 2026-04-15..2026-09-22 | BLOCKED: publication is not execution date |
| candle_close | trial identities, no event timestamp column | BLOCKED |
| levels_sizing | footprint range stated in source probe.py:153 | BLOCKED: no footprint opened |
| levels_hold LC1 | caller-supplied bars; levels_hold.py:73 | BLOCKED: no footprint opened |
| orderflow_views | split_of extracted and tested; exposure ledger records original all-phase publication | BLOCKED for actual data endpoints; no protected outcomes read |
| eur_low_us_sweep | no tracked event timestamps establishing input bounds | BLOCKED |
| mfe_exit | fires carry upstream split labels; study.py-equivalent mfe_exit_study.py:186 | BLOCKED: original fires snapshot absent |
| published_strats | run_pub.py:17,24: DEV 2021-01..2023-06; VAL 2023-07..2024-06; HOLD 2024-07..2025-06 | BLOCKED for actual loader bounds; HOLD is main VALIDATION, not main HOLDOUT |
| tom_fabio_guidance | output matrix has no event timestamps | BLOCKED |

## Contamination calendar and exposure coverage

`out/contamination_calendar.csv` expands observed event min/max bounds by month and phase. It explicitly marks bounds-only months; it does not claim every intervening month had a trade. Publication dates are excluded.
The observed return-bearing CSV event groups end by 2024-06-30. This narrow scan does **not** clear other formats or original untracked data.

| Window / study | Main phase overlap | Existing metadata evidence |
|---|---|---|
| Footprint track 2024-12-02..2025-03-31 | VALIDATION | gross screen EXPOSURE_LEDGER.csv:5 records G3 selection (no outcome read); levels sizing registry declares the same footprint window, but global exposure ledger has no levels_sizing row. Complete run-by-run footprint coverage UNKNOWN. |
| orderflow original calendar phases | 2024H2 VALIDATION in its DEV; 2025H2 HOLDOUT in its VAL | gross screen EXPOSURE_LEDGER.csv:3 explicitly logs DEV+VAL+HOLDOUT exposure; already known, not a new breach |
| imbalance Qriptal original design/check | main VALIDATION/HOLDOUT | its EXPOSURE_LEDGER.csv records this overlap explicitly; historical exposure already acknowledged |
| copied floating OOS | 2025-04 onward: VALIDATION then HOLDOUT | counterfactual timestamp probe, not proof of an executed historical read |
| published strategies HOLD window | main VALIDATION | static source run_pub.py:24; label HOLD alone must not be equated to sealed HOLDOUT |

`holdout_reads.csv` has zero data rows. It was introduced as a skeleton by Gap G6; it does not supersede the older exposure ledgers. No conclusion about untouched data is possible until these histories are reconciled.

## HOLDOUT seal

`out/seal_candidates.csv` gives file, timestamp-column, minimum/maximum dates, outcome column names, latest modifying commit and author. Every lexical candidate uses `date` in a registry or verdict publication. **All 11 require semantic rejection as direct market-date breach evidence.** A 2026 publication of DEV results is ordinary.
Other CSV event timestamp columns checked here have no recognized outcome-bearing group after the main cutoff. `out/schema_gaps.csv` lists 53 CSVs without recognized timestamp columns. JSON, binary, historical deleted artifacts and Markdown result tables remain BLOCKED for a complete seal audit. Candidate authorship is the latest file modification, not proof that author generated the result. No return/PnL cell was printed or used.

## Trial count and haircut lower bounds

Identity union uses named parameter/arm columns, across all committed revisions. Repeated dates/phases are not treated as independent trials. Missing parameter columns can merge distinct trials; reruns are not automatically new hypotheses. Therefore these are **lower bounds**, not the true N or an authorization to change a bar.
The requested sqrt(2 ln N) is an exploratory maximum-statistic heuristic, not a replacement for the frozen t/DIFF/Holm/PBO gates. The G5 screen's t>=2 bar is stated in AUDIT_BRIEF.md section 1a; larger numbers below indicate where a proper family-level review matters, without reopening returns.

| Registry | Current distinct keys | Historical key-union lower bound | sqrt(2 ln N) lower bound |
|---|---|---|---|
| TRIAL_LEDGER.csv | 29 | 29 | 2.595109 |
| TRIAL_LEDGER_BUILT.csv | 414 | 414 | 3.47156 |
| candle_patterns_2026-10-04/TRIAL_REGISTRY.csv | 131 | 131 | 3.122562 |
| context_factors_2026-10-16/trials.csv | 52 | 56 | 2.837376 |
| context_factors_pit_2026-10-16/trials.csv | 8 | 8 | 2.039334 |
| eur_low_us_sweep_followups_2026-10-18/trials.csv | 3 | 3 | 1.482304 |
| fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv | 34 | 34 | 2.655696 |
| fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY_SMOKE.csv | 64 | 64 | 2.884054 |
| imbalance_qriptal_2026-10-16/filter/trials.csv | 30 | 30 | 2.60814 |
| layer_lab/candle_close_2026-10-14/TRIAL_REGISTRY.csv | 126 | 126 | 3.110075 |
| levels_sizing_2026-10-14/TRIAL_REGISTRY.csv | 8 | 8 | 2.039334 |
| mal_bb_mid_engulf_2026-10-16/trials.csv | 39 | 39 | 2.706866 |
| mfe_exit_2026-10-13/TRIAL_REGISTRY.csv | 51 | 51 | 2.80422 |
| mfe_exit_2026-10-13/rerun_dev_2026-10-17/TRIAL_REGISTRY.csv | 51 | 51 | 2.80422 |
| opr_bb_mtf_center_2026-10-16/trials.csv | 6 | 6 | 1.893018 |
| opr_preopen_tops_2026-10-16/trials.csv | 26 | 26 | 2.552684 |
| opr_weekly_low_round_sweep_2026-10-16/trials.csv | 12 | 12 | 2.229308 |
| published_strats_2026-10-13/TRIAL_REGISTRY.csv | 62 | 62 | 2.873024 |
| volume_2026-10-09/TRIAL_REGISTRY.csv | 556 | 556 | 3.555494 |

The context-factor history has 56 distinct definitions versus 52 current rows. These are count-only definitions and do not establish four hidden outcome trials. Volume keys merge/expand different documented windows and cannot be called an independent hypothesis count without the pre-registration history. The full git diff of PRE_REG/params and outcome execution provenance is **BLOCKED / not completed**, so true N remains UNKNOWN. This is explicitly carried by the provenance follow-up.

## Decisions, limits, bridge log and handover

DECISION (OURS): inspect only timestamp/schema/identity metadata across protected dates; no protected outcomes, indicators, signals or price statistics.
DECISION (OURS): apply split functions to a copied timestamp inventory as a labelled counterfactual; never substitute it for missing default or historical inputs.
DECISION (OURS): do not change verdicts, frozen bars, ledgers or study code. Report unsupported completeness as BLOCKED, not zero.

Native tools were used; no AIBridge calls were made. R1 = metadata inventory, R2 = split probe, R3 = report/phase probe. R1 and R2 completed; R3 asserts both calendar-phase mismatches. An initial combined brief read was truncated; the complete applicable sections 5-7 and T08 were read separately before conclusions. One stale Windows wildcard command failed; explicit paths recovered it. Worked best: persist metadata tables and print counts. Rule for next chat: preserve market-date versus publication-date semantics and never infer execution history from today's raw copy.

Top fix: default orderflow to the main DEV boundary.
File: research/orderflow_views_2026-10-14/study.py:215-252.
Test: unset OFV_DEV_ONLY and pass synthetic boundary timestamps; no protected phase may be evaluated or written.
Risk: old all-phase output is overwritten by a default rerun and protected outcomes are reopened.
After fix: synthetic fail-first tests and DEV-only checks; obtain timestamp-only original-input manifests separately. This report is not a clean bill of health or a claim that the full audit is complete.
