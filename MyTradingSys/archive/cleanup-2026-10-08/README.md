# Cleanup 2026-10-08 (wiring ledger)

Moved here with `git mv` (history kept; `git log --follow` finds the old path). Nothing was deleted.

| moved | why |
|---|---|
| src_main_java_datafeed/SetupScreener.java + src_test_java_datafeed/SetupScreenerTest.java | S01-S05 screener never called by Main or any builder; T035 closed DEFER (no Tom source). Only its own test used it. |
| fabio_of_model/run_of_model.py, run_of_model_v2.py | Fabio conditional-model drivers; result was "no edge" (backtest/layers/fabio/FABIO_L1_REPORT.md), superseded by fabio/v3 (L3-FAIL, PRE_REG_FABIO_V3.md). |
| p1_p4_research_scripts/* | Six generations of the same P1/P4 scripts. Their notes carry INVALID/superseded banners (metric bug; wrong quarter-hour definition). The corrected P4 needs a new script from PRE_REG_P4_CORRECTED_2026-10-06.md. |
| research_notes/* | P1 FULL (3,247 bp metric bug), P4 first run and P4 INCOMPLETE: superseded notes already bannered as invalid. |
| scripts/qwen_decommission*.py, update_prompt.py | One-shot scripts, job done (Qwen lane decommissioned 2026-10-01); no references in code. |
| scripts_tools/check_snapshot.py | One-off debug print of the latest snapshot (hard-coded relative paths); no references in code or docs except an old file-index row. Wiring-ledger cleanup. |
| scripts_tools/harvest_tom_quotes.py, verify_harvest_vs_corpus.py, rebuild_tom_index_and_tag.py | One-shot T017/T030 pipeline (TOM_VERBATIM_INDEX rebuilt, 213 quotes, CLOSED 2026-09-19); quote checking is now scripts/dev/verify_extract_quotes.py. No code imports them. |
| core_readiness_harness/decision_matrices.py | One-shot D1/D3/D4 historical-effect run; no doc or code references it and core_check.ps1 does not run it. |
| fast_track_review/repro_ft2.py | Adversarial repros of FT-2 staged *.new files; findings fixed and promoted (FIX3_REPORT.md:58, "NOT REPRODUCED"), the staged inputs no longer exist. |
| backtest_xcheck/ref_pbo.py + test_ref_pbo.py | Duplicate copy of bt/ref_pbo.py (FORMULA_INVENTORY.md:66 "drift risk"); the promoted bt/ref_pbo.py is what runners import. |
| backtest_bt/bt_rsi.py + test_bt_rsi.py + test_bt_rsi_edge.py | Superseded by layers/rsi (rsi_core, malkan_40_60); SUPERVISOR_LOG.md:45 says "bt_rsi superseded by layers/rsi, do not promote". Removed from run_all_tests.py step 4. |
| backtest_layers_rsi/tolerance_sweep.py + test_tolerance_sweep.py | Tuning machinery, NO-SOURCE (LAYER_PROVENANCE_AUDIT.md R25/R26, lines 74-75; provenance rule: unsourced params are removed, not tuned). Nothing imports it. |
