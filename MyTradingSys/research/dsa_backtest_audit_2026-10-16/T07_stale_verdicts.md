# T07 Stale verdicts: do the published numbers still come out of today's code?

## 1. Summary
- Checked: for 16 published verdicts, which code made them and whether that code changed since; then reran 10 results on today's code and compared 2,000+ published numbers.
- Found: 8 of the 10 reruns reproduce every number exactly (7 are flagged STALE-CANDIDATE by code changes, but none moved a number); the 9th (mfe_exit, DEV-only rerun) does not reproduce, because today's fire files label a different TRAIN window; the 10th (published_strats) cannot be rerun on this machine (data folders absent).
- Changes: no verdict flips. One S2 card (mfe_exit rerun). Lead L9 is cleared (the three tests are gated now and CI installs pandas).

## 2. Scope
Worktree at fast-track 5879e97d3 (Python 3.14.6, numpy 2.5.3, pandas 3.0.6). Reruns ran from a sandbox copy in `%TEMP%/dsa_audit/T07/sandbox` (never over a result file), reading F:/MTS/data DEV bars only.

| Item | Window | Method | Result |
|---|---|---|---|
| Provenance, 16 verdicts of brief 1b | git history | `scripts/T07/t07_provenance.py`: last commit touching the result file, ast import walk, later commits to script or imports | `out/provenance.csv`, `out/provenance_commits.csv`; 7 STALE-CANDIDATE, 9 CURRENT |
| Rerun, 10 results | DEV (<2024-07-01) | `t07_rerun.py` + `t07_diff.py`; counts exact, returns 1e-6, words exact | `out/rerun_diff.csv` (2,100+ rows) |
| Determinism | DEV | mal_bb_mid_engulf run twice, sha256 of RESULT.md, ledger.csv, trials.csv | all 3 identical (`out/determinism.csv`) |
| CI (L9) | n/a | `.github/workflows/ci.yml`, `run_extra_tests.py`, gate discovery test | see section 5 |
| Doc drift | n/a | `t07_docdrift.py`: key numbers near the study name in 4 docs | `out/doc_drift.csv` (heuristic) |

### Provenance (STALE-CANDIDATEs)
| # | Study | Published at | Later commits to script or imports | Lines | Rerun |
|---|---|---|---|---|---|
| 1 | gross_effect_screen | b42cef1b8 (2026-10-16) | d55a90858 (ledger speed-up, 23), f068fd95f (refuse changed data manifest, 42) in screen.py | 65 | identical |
| 2-5 | opr_preopen_tops, mal_bb_mid_engulf, opr_bb_mtf_center, opr_weekly_low_round_sweep | ce92961d9, 3c097b2ba, 1318ef9e2, 0584b0353 | same two screen.py commits, reached through chart_read_g5/common.py `import screen` | 65 each | identical |
| 6 | wlow_bounce_bbrsi60 | 8bc4b9fae | 150840644 (rsi_core flat-window RSI 100 to 50) | 2 | identical |
| 7 | krown_malkan_g3 | c98a9925c | 150840644 (rsi_core) | 2 | identical |

Not stale by code: 8 qriptal (0 later commits to inputs), 9, 10, 11, 12, 13, 14, 15, 16 (9 of them have 0 later input commits after the latest result commit; 8, 11, 12, 14, 15 changed lines only before their latest result commit).

The walk resolves `sys.path` sibling inserts; the first version missed `import screen` inside common.py (fixed, see scripts).

### Testnet source verdicts
`auto_trader_config.json` `pre_pipeline_sources` has 27 keys; every reason reads "grandfathered pre-pipeline testnet calibration, operator decision pending", review_by 2026-10-23. There is no verdict file behind them, so provenance is empty by construction (matches brief 1b: none has a positive out-of-sample verdict). review_by 2026-10-23 is already past (today 2026-10-25).

## 3. Findings
| ID | Sev | Status | Evidence | Affects | Fix | Card |
|---|---|---|---|---|---|---|
| T07-F1 | S2 | CONFIRMED | `mfe_exit_study.py:186` loads fires by the file's `split` column; today's fire files label TRAIN through 2025-01-01. `out/rerun_diff.csv` rows `mfe_exit`: turn_of_candle_1m TRAIN fires 29,178 published (rerun_dev_2026-10-17) vs 35,065 now (+20%); 966 of 1,048 numbers differ | the 2026-10-17 "DEV only, new labels" rerun of mfe_exit (verdict "nothing survives" is not tested by it) | filter on `t_fire_ms < 2024-07-01` in the study, not on the file label; rerun | mfe-exit-dev-only-rerun-not-reproducible |
| T07-F2 | S2 | CONFIRMED (accidental) | the same rerun computed returns for fires 2024-07..12 (VALIDATION). Rule 2 breach by the audit, not by the study. Mitigation: all rerun return values for mfe_exit are replaced by WITHHELD in rerun_diff.csv, the sandbox results.json was deleted, only counts kept. A handful of numbers were visible in my console before I noticed | audit hygiene | none needed for the study; note for DEV-split guard | none |
| T07-F3 | S3 | CONFIRMED | published_strats cannot be rerun here: `run_pub.py:36` globs `Dumps/backtest/raw_1h/klines`, not on disk (PRE_REG.md:7 names raw_1h and raw_fund, both absent) | verdict 15 is unreproducible on JIS-NB | restore or document the data source | none (BLOCKED row) |
| T07-F4 | S3 | CONFIRMED | seven verdicts have changed inputs after publishing (65 lines in screen.py, 2 in rsi_core.py) but all rerun byte-identical in RESULT.md, ledger.csv, trials.csv. The ledger speed-up (d55a90858) and the manifest guard did not move a number | none | none | none |
| T07-F5 | S3 | CONFIRMED | `EXPOSURE_LEDGER.csv` rows hold a wall-clock stamp, so a rerun is never byte-identical there (only the stamp differs) | determinism checks must exclude it | keep excluded | none |
| T07-F6 | S3 | SUSPECTED | doc drift is only a heuristic: LAYERS.md (5 rows) and research_map.html (4 rows) do not show the published number next to the study name (`out/doc_drift.csv`, status NUMBER_NOT_NEAR_MENTION: gross_effect n 40, candle_close 126 arms, levels_sizing 117, Q33 336 cells, mal_bb A1 1179, weekly_low AS 525, bb_mtf AU 194). STATUS.md names none of the 10 studies by key. No contradicting pair of numbers was confirmed | docs, not verdicts | a hand read of the 9 rows | none |
| T07-F7 | S3 | CONFIRMED | CI runs Python 3.12 with unpinned numpy, pandas (`ci.yml:81,96`); here 3.14.6 / numpy 2.5.3 / pandas 3.0.6 | a pandas major bump could change a study without a code change | pin versions in CI | none |

All other published numbers: MATCH. Per result (rows compared, all MATCH): gross_effect_screen 70, opr_preopen_tops 634, mal_bb_mid_engulf 397, opr_bb_mtf_center 265, opr_weekly_low_round_sweep 244, wlow_bounce_bbrsi60 109, krown_malkan_g3 178, qriptal_scorecard 9, orderflow_views (DEV rerun json) 144; mfe_exit 82 MATCH and 966 DIFF.

## 4. Leads
- **L9 CLEARED.** The three tests (`krown_malkan_g3/test_event_counts.py`, `opr_bb_mtf_center/test_study.py`, `opr_weekly_low_round_sweep/test_study.py`) are now in `scripts/dev/run_extra_tests.py` EXTRA (lines 72, 75, 76), and `MyTradingSys/tests/test_gate_discovery_b150.py` passes. `chart_read_g5/common.py` imports pandas and CI installs pandas (`ci.yml:96`: pytest numpy pandas tzdata). The brief's premise (ci.yml:58) is out of date.
- Determinism: one study twice gives identical outputs; `git grep`/Grep over study.py, screen.py, common.py, probe.py, run_pub.py, mfe_exit_study.py found no unseeded random draw and no clock call (wlow uses SEED 20261016).

## 5. CI table
| Item | JIS-NB | CI |
|---|---|---|
| Python | 3.14.6 | 3.12 |
| numpy | 2.5.3 | latest, unpinned |
| pandas | 3.0.6 | latest, unpinned |
| study tests importing pandas | chart_read_g5 and the opr_* studies via common.py | pandas installed |
| tracked tests in no gate list | none found (discovery test passes) | gate test enforces |

## 6. Not checked
- levels_hold_lc1, levels_sizing, candle_close, eur_low_us_sweep, tom_fabio_q33: not rerun (footprint window needs an EXPOSURE_LEDGER row outside this card; candle_close needs network; eur_low and matrix_q33 read VALIDATION/HOLDOUT returns). They count as CURRENT by code only.
- published_strats: BLOCKED (F3).
- Testnet source verdicts: nothing to trace.

## 7. Decisions taken
- DECISION (OURS): the "latest commit touching the result file" is the publishing commit; "since first publication" is also stored in provenance.csv (`lines_since_first`).
- DECISION (OURS): only 7 STALE-CANDIDATEs exist and 6 are in the six newest studies, so the "four most-changed" slot was filled with krown_malkan_g3 (stale) plus the three feasible DEV reruns with the most lines changed since first publication: orderflow_views (DEV-only mode, published json 2026-10-17), mfe_exit (DEV-only mode), qriptal_scorecard (`run`, holdout refused). Ten = six + krown + orderflow + mfe + qriptal.
- DECISION (OURS): mfe_exit was run with a sandbox-only path patch `raw_fund/fundingRate` to `raw/fundingRate` (the data root the study names is absent; the same trap as lead L1).
- DECISION (OURS): qriptal DEV (2025-09..2026-06) overlaps the main HOLDOUT, but 0 calls are scored (the 2 eligible rows are holdout and refused), so no return was computed.
- DECISION (OURS): no footprint data read; no EXPOSURE_LEDGER row needed.

## 8. Bridge log
Not used (local reruns only, no bridge results). No bridge result # exists for these findings; scripts reproduce them.

## 9. Handover
1. Top fix: T07-F1, `MyTradingSys/research/mfe_exit_2026-10-13/mfe_exit_study.py:186`, filter on time not on the file label.
2. Test: rerun with `MFE_DEV_ONLY=1`, TRAIN fires must be 29,178 for turn_of_candle_1m and every fire < 2024-07-01.
3. Risk: the fire files may be rebuilt again; pin the cutoff in the study.
4. Rerun after: `python scripts/T07/t07_rerun.py mfe_exit a` then `t07_diff.py`, `pytest scripts/T07/test_rerun_diff.py`.
5. Registration needed: add `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T07/test_rerun_diff.py` to EXTRA in `scripts/dev/run_extra_tests.py`.
