# Structure Audit

Written: 2026-09-16
Method: read from disk. Every number below comes from the current tree.

## Current tree (top level, excluding .git, target, snapshots, .idea)

MyTradingSys                           229 files       3859294 bytes
raw_transcripts_canonical               89 files       1307401 bytes
extracts                                70 files       1058220 bytes
backup_session                          31 files        394291 bytes
Dumps                                   26 files       4075989 bytes
scripts                                 20 files         58488 bytes
src                                     12 files        176708 bytes
data                                    12 files       1732629 bytes
.pytest_cache                            5 files         10760 bytes
DSA_SESSION_PROMPT.md                    1 files         12060 bytes
Launch_alert.vbs                         1 files            14 bytes
.gitignore                               1 files           963 bytes
COMMANDS.md                              1 files          1806 bytes
pom.xml                                  1 files          2325 bytes
USER.md                                  1 files          2894 bytes
VERSION                                  1 files            22 bytes
session-start.ps1                        1 files          4466 bytes
docs                                     1 files          1487 bytes

## Duplicates

count 4 - MyTradingSys\research\monitor_20260915\D5_cadence_gaps.csv, MyTradingSys\research\monitor_20260915\D5_cycles_without_verdict.csv, MyTradingSys\runtime\locks\.gitkeep, MyTradingSys\tests\docs\__init__.py
count 2 - extracts\processed\tom\old_47\extract_T6hDJcHrVBM_fresh.md, MyTradingSys\extracts\fresh\extract_T6hDJcHrVBM_fresh.md
count 2 - extracts\processed\tom\old_47\extract_sQ_biBKhPVU_fresh.md, MyTradingSys\extracts\fresh\extract_sQ_biBKhPVU_fresh.md
count 2 - extracts\processed\tom\old_47\extract_rrHj24GSR6M_fresh.md, MyTradingSys\extracts\fresh\extract_rrHj24GSR6M_fresh.md
count 2 - extracts\processed\tom\old_47\extract_usho6UVLqkE_fresh.md, MyTradingSys\extracts\fresh\extract_usho6UVLqkE_fresh.md
count 2 - extracts\processed\tom\old_47\extract_ujedEcmvBMk_fresh.md, MyTradingSys\extracts\fresh\extract_ujedEcmvBMk_fresh.md
count 2 - extracts\processed\tom\old_47\extract_tS6ZEiHj8gQ_fresh.md, MyTradingSys\extracts\fresh\extract_tS6ZEiHj8gQ_fresh.md
count 2 - extracts\processed\tom\old_47\extract_OUM9LYwL8eA_fresh.md, MyTradingSys\extracts\fresh\extract_OUM9LYwL8eA_fresh.md
count 2 - extracts\processed\tom\old_47\extract_oa8kxSLLkAo_fresh.md, MyTradingSys\extracts\fresh\extract_oa8kxSLLkAo_fresh.md
count 2 - extracts\processed\tom\old_47\extract_NkQeOVDTAec_fresh.md, MyTradingSys\extracts\fresh\extract_NkQeOVDTAec_fresh.md
count 2 - extracts\processed\tom\old_47\extract_rFPCtOcfUMI_fresh.md, MyTradingSys\extracts\fresh\extract_rFPCtOcfUMI_fresh.md
count 2 - extracts\processed\tom\old_47\extract_qLnQan0KGmQ_fresh.md, MyTradingSys\extracts\fresh\extract_qLnQan0KGmQ_fresh.md
count 2 - extracts\processed\tom\old_47\extract_oYu9SBQved0_fresh.md, MyTradingSys\extracts\fresh\extract_oYu9SBQved0_fresh.md
count 2 - extracts\processed\tom\old_47\extract_v5EuDl9c0iI_fresh.md, MyTradingSys\extracts\fresh\extract_v5EuDl9c0iI_fresh.md
count 2 - extracts\processed\tom\old_47\extract_yRvMW6lgN1o_fresh.md, MyTradingSys\extracts\fresh\extract_yRvMW6lgN1o_fresh.md
count 2 - extracts\processed\tom\old_47\extract_YopZ5ZDmMFw_fresh.md, MyTradingSys\extracts\fresh\extract_YopZ5ZDmMFw_fresh.md
count 2 - extracts\processed\tom\old_47\extract_YmygDgtoxO8_fresh.md, MyTradingSys\extracts\fresh\extract_YmygDgtoxO8_fresh.md
count 2 - MyTradingSys\research\monitor_20260915\R1_session_state.json, MyTradingSys\runtime\session_state.json
count 2 - extracts\processed\tom\old_47\extract_zQTbdEweG3c_fresh.md, MyTradingSys\extracts\fresh\extract_zQTbdEweG3c_fresh.md
count 2 - extracts\processed\tom\old_47\extract_YVUcLTsCOZI_fresh.md, MyTradingSys\extracts\fresh\extract_YVUcLTsCOZI_fresh.md
count 2 - extracts\processed\tom\old_47\extract_VumVuGnCcFM_fresh.md, MyTradingSys\extracts\fresh\extract_VumVuGnCcFM_fresh.md
count 2 - extracts\processed\tom\old_47\extract_vl01TiVTuoQ_fresh.md, MyTradingSys\extracts\fresh\extract_vl01TiVTuoQ_fresh.md
count 2 - extracts\processed\tom\old_47\extract_vk0mkNPuhDc_fresh.md, MyTradingSys\extracts\fresh\extract_vk0mkNPuhDc_fresh.md
count 2 - extracts\processed\tom\old_47\extract_y67l86cSqb8_fresh.md, MyTradingSys\extracts\fresh\extract_y67l86cSqb8_fresh.md
count 2 - extracts\processed\tom\old_47\extract_WSCIURybK3U_fresh.md, MyTradingSys\extracts\fresh\extract_WSCIURybK3U_fresh.md
count 2 - extracts\processed\tom\old_47\extract_wPMiyJXL0zU_fresh.md, MyTradingSys\extracts\fresh\extract_wPMiyJXL0zU_fresh.md
count 2 - extracts\processed\tom\old_47\extract_3o1VVsfBmmU_fresh.md, MyTradingSys\extracts\fresh\extract_3o1VVsfBmmU_fresh.md
count 2 - extracts\processed\tom\old_47\extract_3JqMyzE8jIQ_fresh.md, MyTradingSys\extracts\fresh\extract_3JqMyzE8jIQ_fresh.md
count 2 - extracts\processed\tom\old_47\extract_1xBWnyr1qe4_fresh.md, MyTradingSys\extracts\fresh\extract_1xBWnyr1qe4_fresh.md
count 2 - extracts\processed\tom\old_47\extract_9eHZMVXilgc_fresh.md, MyTradingSys\extracts\fresh\extract_9eHZMVXilgc_fresh.md
count 2 - extracts\processed\tom\old_47\extract_4MoNjEQ2Dd8_fresh.md, MyTradingSys\extracts\fresh\extract_4MoNjEQ2Dd8_fresh.md
count 2 - extracts\processed\tom\old_47\extract_43JaKHRvxHk_fresh.md, MyTradingSys\extracts\fresh\extract_43JaKHRvxHk_fresh.md
count 2 - extracts\processed\tom\old_47\extract_-dMWA_bbm3o_fresh.md, MyTradingSys\extracts\fresh\extract_-dMWA_bbm3o_fresh.md
count 2 - backup_session\test_snapshot_v4.2.0-p2_validation.json.20260915_162352, MyTradingSys\market_data\sample_btc_snapshot.json
count 2 - backup_session\proof_requirements_formatted.md.20260915_162352, MyTradingSys\conditions\market_state_rules.md
count 2 - backup_session\DSA_SESSION_PROMPT.md.bak_final, MyTradingSys\archive\DSA_SESSION_PROMPT_superseded_2026-09-14.md
count 2 - extracts\processed\tom\new_selected_10\extract_yWO8hVpRXeY_fresh.md, MyTradingSys\extracts\fresh\extract_yWO8hVpRXeY_fresh.md
count 2 - extracts\processed\tom\new_selected_10\extract_UOBgXV20yCM_fresh.md, MyTradingSys\extracts\fresh\extract_UOBgXV20yCM_fresh.md
count 2 - extracts\processed\tom\new_selected_10\extract_qLCcwem5vWk_fresh.md, MyTradingSys\extracts\fresh\extract_qLCcwem5vWk_fresh.md
count 2 - extracts\processed\tom\old_47\extract_kXhIAug0Gh8_fresh.md, MyTradingSys\extracts\fresh\extract_kXhIAug0Gh8_fresh.md
count 2 - extracts\processed\tom\old_47\extract_KEe_CWHyuSg_fresh.md, MyTradingSys\extracts\fresh\extract_KEe_CWHyuSg_fresh.md
count 2 - extracts\processed\tom\old_47\extract_k0zm5NYn0IQ_fresh.md, MyTradingSys\extracts\fresh\extract_k0zm5NYn0IQ_fresh.md
count 2 - extracts\processed\tom\old_47\extract_n7ZSkjb7JXs_fresh.md, MyTradingSys\extracts\fresh\extract_n7ZSkjb7JXs_fresh.md
count 2 - extracts\processed\tom\old_47\extract_Ld1dhjGdTCA_fresh.md, MyTradingSys\extracts\fresh\extract_Ld1dhjGdTCA_fresh.md
count 2 - extracts\processed\tom\old_47\extract_l8RZrBfzvp4_fresh.md, MyTradingSys\extracts\fresh\extract_l8RZrBfzvp4_fresh.md
count 2 - extracts\processed\tom\old_47\extract_G0CiJcuXCRs_fresh.md, MyTradingSys\extracts\fresh\extract_G0CiJcuXCRs_fresh.md
count 2 - extracts\processed\tom\old_47\extract_dh-ysRR8f-M_fresh.md, MyTradingSys\extracts\fresh\extract_dh-ysRR8f-M_fresh.md
count 2 - extracts\processed\tom\old_47\extract_C9n_d91Uitc_fresh.md, MyTradingSys\extracts\fresh\extract_C9n_d91Uitc_fresh.md
count 2 - extracts\processed\tom\old_47\extract_BVpYGKz9PBU_fresh.md, MyTradingSys\extracts\fresh\extract_BVpYGKz9PBU_fresh.md
count 2 - extracts\processed\tom\old_47\extract_Fj4FDZQxw0I_fresh.md, MyTradingSys\extracts\fresh\extract_Fj4FDZQxw0I_fresh.md
count 2 - extracts\processed\tom\old_47\extract_e6Gm1n2h05M_fresh.md, MyTradingSys\extracts\fresh\extract_e6Gm1n2h05M_fresh.md
count 2 - extracts\processed\tom\old_47\extract_DVZVE9rXGtU_fresh.md, MyTradingSys\extracts\fresh\extract_DVZVE9rXGtU_fresh.md

## Orphan candidates in the research folder

A file is listed here only if its base name appears nowhere else in the repository.

what_is_next.md

## Ignore list - lines that match nothing

__pycache__/
*.new
.idea/
*.iml
target/
runtime_data/snapshots/*.json
runtime_data/snapshots/historical/
runtime_data/apparatus.lock
Dumps/*
backup_session/
MyTradingSys/runtime/locks/*
MyTradingSys/runtime/state_code.json
MyTradingSys/runtime/current_market_state.md
MyTradingSys/runtime/session_end_logs.md
MyTradingSys/system/session_end_logs.md
runtime_data/apparatus_log.txt
runtime_data/alert_counter.txt
runtime_data/last_alert.json
runtime_data/outcome_labels.json
runtime_data/_prob_label_enriched.json
runtime_data/speed_baselines/*.json
Dumps/SESSION_PASTE.txt

## Grouping candidates

- The data folder holds the vast majority of files. Almost all of them are snapshots. Snapshots are already ignored by the ignore list and are regenerated every cycle.
- The transcripts folders are two: raw transcripts, and the work folder of cleaned extracts. They do similar jobs and could merge under one name if the workflow allows.
- The research folder holds the deliverable documents. It is already the right home for them.

## Proposed target tree (for approval, nothing moved yet)

- data / snapshots - keep, already ignored
- transcripts_raw - keep raw inputs
- transcripts_work - keep cleaned extracts (currently two folders)
- research - keep all written findings here
- scripts / core and scripts / live - keep current split
- dumps - keep only the build report and a single current paste file

## Move plan

Folder moves are deferred by design. Each move touches many files. Do them in a single quiet window, one folder at a time, with a snapshot before each.

## Ignore list fixes

Lines to remove or correct: __pycache__/, *.new, .idea/, *.iml, target/, runtime_data/snapshots/*.json, runtime_data/snapshots/historical/, runtime_data/apparatus.lock, Dumps/*, backup_session/, MyTradingSys/runtime/locks/*, MyTradingSys/runtime/state_code.json, MyTradingSys/runtime/current_market_state.md, MyTradingSys/runtime/session_end_logs.md, MyTradingSys/system/session_end_logs.md, runtime_data/apparatus_log.txt, runtime_data/alert_counter.txt, runtime_data/last_alert.json, runtime_data/outcome_labels.json, runtime_data/_prob_label_enriched.json, runtime_data/speed_baselines/*.json, Dumps/SESSION_PASTE.txt

## End