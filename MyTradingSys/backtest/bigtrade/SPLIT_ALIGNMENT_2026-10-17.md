# bigtrade split alignment (2026-10-17)

## History found
- `SPLITS` entered with `e31bc290` (2026-10-11, first commit of the bigtrade harness); no earlier commit changes it (history search for the SPLITS string).
- Source comment: "PLAN section 4": `research/bigtrade_2026-10-09/PLAN.md:53`, TRAIN 2022-01..2024-12, VALIDATE 2025-01..2025-06, HOLDOUT 2025-07..2026-09. PLAN.md was written by worker session MTS-2026-10-08-1933Z-APP-ANA-bigtrade-bt. The only operator text it cites is the 2026-10-09 directive allowing tuning; no operator decision on the split boundaries exists in OPERATOR_DECISIONS.md, TRIALS.md or any PRE_REG. The repo split (DEV to 2024-06-30, VALIDATION 2024-07-01..2025-06-30) is the documented one.
- DECISION (OURS): no documented operator decision supports the old split, so it is aligned to the repo split.

## What scripts/dev/verdicts.py does
Its `split_of(*texts)` (line 129) is a different function: a regex over RESULT.md/PRE_REG.md text ("DEV only", "on DEV", "DEV ... VAL ... HOLD") that fills the `split_read` column. It does not import fires_kline and computes no dates. Scope: all studies, but only as a text label; it is unaffected by SPLITS. No verdicts.py change or test needed. No VERDICTS.csv row is bigtrade-derived (study_dirs: b154_stratified, context_factors, eur_low_us_sweep, gross_effect_screen, imbalance_qriptal(+filter), mal_bb_mid_engulf, no_source_sweep, opr_*, orderflow_views, published_strats, rsi_divergence_mtf, t087, t090, transcript_inventory, wlow_bounce); that CSV's `split_read` is text-parsed and was not re-derived from any SPLITS.
- Real importers of fires_kline: parity_kline.py (no split use), layer_lab/bigtrade_event_table (fixed in 5b1bdc27). `research/orderflow_views_2026-10-14/study.py` has its own year-based `split_of` (DEV = year <= 2024), not fires_kline.

## Fix
- `fires_kline.py` SPLITS: TRAIN 2022-01-01..2024-07-01, VALIDATE 2024-07-01..2025-07-01, HOLDOUT unchanged. Label names kept (fire CSV column and mfe_exit read TRAIN/VALIDATE/HOLDOUT).
- `exit_policies.py` TRAIN_END (had its own hardcoded 2025-01-01) -> 2024-07-01.
- Tests (`test_fires_kline.py`): pinned `test_split_labels` updated; new `test_repo_split_2024_07_01_is_not_train`, `test_exit_policies_train_end_matches_repo_split`. Against HEAD copies of fires_kline.py and exit_policies.py: 3 failed (these two plus test_split_labels), 35 passed; against the fix 38 passed.
- Not done: existing fire CSVs on F:/MTS/data/bigtrade/fires still carry the old `split` column (gitignored data, not rewritten). Regenerating them is a separate card; consumers must re-label by `t_fire_ms` or regenerate before reuse.

## Counts (existing fires, no outcome analysis)
Old TRAIN fires 153,685 (19 files), of which 25,607 are 2024-07..12. mfe_exit: turn_of_candle_1m 17,658 of 105,190; sr_flip_15m 631 of 3,911; rsi_events_5m 550 of 3,234 (tradable).

## Affected (marked `CONTAMINATED (DEV read VALIDATION 2024-07..12)`)
- research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md (TRAIN column; its VALIDATE column is 2025-01..06 only)
- research/bigtrade_2026-10-09/FIRES_B1_REPORT.md (split column)
- research/mfe_exit_2026-10-13/REPORT.md, results.json, TRIAL_REGISTRY.csv (rule choice on TRAIN; VALIDATE 2025-01..06 not contaminated by it, VALIDATION 2024-07..12 is no longer a clean check)
- research/orderflow_views_2026-10-14 (own year-based DEV; VERDICTS.csv row says DEV, FAIL)
- bigtrade_event_table: already marked in DEV_BOUNDARY_FIX_2026-10-17.md.
Other bigtrade artifacts using the fires split column (CAPTURE_MATRIX*, BIGMOVES) were checked: no split use found by grep. Not rerun: HOLDOUT untouched; no recompute done (full reruns exceed the cheap budget). Logged in layer_lab/TRIALS.md.
