# Cleanup 2026-10-08 (wiring ledger)

Moved here with `git mv` (history kept; `git log --follow` finds the old path). Nothing was deleted.

| moved | why |
|---|---|
| src_main_java_datafeed/SetupScreener.java + src_test_java_datafeed/SetupScreenerTest.java | S01-S05 screener never called by Main or any builder; T035 closed DEFER (no Tom source). Only its own test used it. |
| fabio_of_model/run_of_model.py, run_of_model_v2.py | Fabio conditional-model drivers; result was "no edge" (backtest/layers/fabio/FABIO_L1_REPORT.md), superseded by fabio/v3 (L3-FAIL, PRE_REG_FABIO_V3.md). |
| p1_p4_research_scripts/* | Six generations of the same P1/P4 scripts. Their notes carry INVALID/superseded banners (metric bug; wrong quarter-hour definition). The corrected P4 needs a new script from PRE_REG_P4_CORRECTED_2026-10-06.md. |
| research_notes/* | P1 FULL (3,247 bp metric bug), P4 first run and P4 INCOMPLETE: superseded notes already bannered as invalid. |
| scripts/qwen_decommission*.py, update_prompt.py | One-shot scripts, job done (Qwen lane decommissioned 2026-10-01); no references in code. |
