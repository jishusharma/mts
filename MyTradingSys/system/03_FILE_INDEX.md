# FILE: 03_FILE_INDEX.md
# NOT MAINTAINED since 2026-10-15. Partial (about a third of the files have a row; some rows name files that are gone).
# A new file does not need a row. The map is the tree: git ls-files, LAYERS.md (layers), PROJECT_MAP.md (groups).
# SIZE: computed (never hand-edited; test_4 enforces a ceiling)
# ---

# FILE INDEX - MTS Project v4.2.0-p5
# Purpose: Partial index of live files (not maintained). Hierarchical structure.
# NOTE: Files in archive/ and *.old files are EXCLUDED from active counts.

---

## SYSTEM/ - AI Session Orchestration

| File | Size | Purpose |
|------|------|---------|
| 01_AI_BEHAVIOR.md | ~34KB | Behavior rules, mistake history, Section 14 JSON workflow, Rules 31-36 |
| 03_FILE_INDEX.md | ~10.4KB | This file |
| 04_NEXT_SESSION_PROMPT.md | ~19KB | Current session handoff prompt |
| COMPILED_DECISIONS.md | ~11KB | Single-page reference of all 56 system decisions |
| session_end_logs.md | ~49KB | Archived session end logs (append-only history) |

## METHODOLOGY/ - Research Protocols & Domain Theory

| File | Size | Purpose |
|------|------|---------|
| playbook.md | ~27KB | Research gate (Part I), extraction rules (Part J), archive protocol (Part K), architecture (Part L) |
| extraction.md | ~5.5KB | Extraction lifecycle: 4 phases + Safeguards 2, 3. TRIGGER: new transcript |
| crypto_adaptations.md | ~5KB | Tom-rule vs crypto-hack classification |
| grounded_theory_protocol.md | ~9KB | Original 4-phase workflow + 5 Safeguards. SUPERSEDED - kept for provenance |
| reflexivity_log.md | ~5.5KB | Reflexive discipline log (Safeguard 4) |

## MTS/CONDITIONS/ - Full Rule Documentation

| File | Size | Purpose |
|------|------|---------|
| market_state_rules.md | ~16.5KB | Balance/trend taxonomy, state workflow, state->setup matrix |
| zone_identification_rules.md | ~28KB | 9 zone types, workflow, negative rules |
| setup_type_rules.md | ~34KB | 4 execution modes, idea+proof framework, trader DNA |
| proof_requirements_formatted.md | ~16.5KB | 14 proof categories, cross-cutting layer |
| risk_protocol.md | ~27KB | Stops, sizing, R:R, targets, re-entry, drawdown |
| entry_timing_triggers.md | ~35KB | Trigger taxonomy, 4 modes, 4 tiers, 10 negative rules |
| session_timing_rules.md | ~26KB | Session-specific timing, volatility rankings |

## MTS/CARDS/ - Trading Cards & Templates (20 files)

| File | Size | Purpose |
|------|------|---------|
| trading_card_generator.md | ~30KB | Card generation spec |
| BTCUSDT_2026-08-26_0915.md | ~5KB | Live card |
| BTCUSDT_2026-08-26_1003.md | ~7KB | Live card |
| BTCUSDT_2026-08-26_1100.md | ~9KB | Live card |
| BTCUSDT_2026-08-26_1100_compact.md | ~5KB | Compact format test |
| BTCUSDT_2026-08-26_1108.md | ~11KB | Live card |
| BTCUSDT_2026-08-26_1303.md | ~6KB | Live card |
| BTCUSDT_2026-08-26_1343.md | ~7KB | Live card |
| BTCUSDT_2026-08-27_1923.md | ~6KB | Live card |
| BTCUSDT_2026-08-28_0444.md | ~7KB | Live card |
| BTCUSDT_2026-08-28_0809.md | ~8KB | Live card |
| BTCUSDT_2026-08-31_0727.md | ~14KB | Live card |
| BTCUSDT_2026-08-31_1034_handoff.md | ~6KB | Live card + handoff |
| BTCUSDT_2026-08-31_2127.md | ~9KB | Live card |
| BTCUSDT_2026-08-31_2204.md | ~10KB | Live card |
| BTCUSDT_2026-09-01_0521.md | ~11KB | Live card |
| BTCUSDT_2026-09-02_1032.md | ~9KB | Live card |
| BTCUSDT_2026-09-09_1419.md | ~1.5KB | Live card (brief) |
| sample_pipeline_output.md | ~17KB | Sample output |
| trading_card_btc_sample.md | ~10KB | Sample card |

## MTS/RUNTIME/ - Decision Engine + State

| File | Size | Purpose |
|------|------|---------|
| compiled_engine.md | ~67KB | Runtime decision engine (SOLE AUTHORITY) |
| mts_math.py | ~19KB | Pure math: 9 functions + state management (16 total) |
| math_object_builder.py | ~18KB | DSA snapshot -> math_object compiler |
| update_market_state.py | ~3KB | Reads latest snapshot, diffs state, writes current_market_state.md |
| current_market_state.md | ~1.7KB | Persistent structural state (SSOT) |
| session_state.py | ~3.9KB | Session SSOT helper |
| session_state.json | ~1.4KB | AI-authored thesis + watch levels |
| session_log.json | ~3.5KB | Append-only decision log |
| log_decision.py | ~1.1KB | One-line decision logger |
| outcome_labeler.py | ~3.4KB | Forward-return labeler |
| quad_classify.py | ~4.3KB | Price x CVD x OI quadrant classifier |
| build_mo_cli.py | ~0.4KB | Proof-direction helper CLI |
| state_code.json | ~0.6KB | State machine output (runtime) |
| v4.2.0_optimization_spec.md | ~11KB | REFERENCE - design doc, not loaded at runtime |

## MTS/EXECUTION/ - Deribit Order Execution Layer

| File | Size | Purpose |
|------|------|---------|
| README.md | ~1.1KB | Execution layer overview and setup notes |
| deribit_client.py | ~2.6KB | Low-level Deribit API HTTP/WS client |
| deribit_orders.py | ~9.6KB | Order placement, amend, cancel wrappers |
| deribit_read.py | ~4.2KB | Read-only account/position/order-book calls |
| executor.py | ~9.9KB | Trade-plan executor: places orders, manages protective stop |
| journal.py | ~3.9KB | Execution journal / trade log writer |
| plan_compiler.py | ~11.2KB | Compiles a trade plan into concrete order instructions |
| reconciler.py | ~5.1KB | Reconciles local state against exchange state |
| trade_plan_schema.json | ~6.3KB | JSON schema for a trade plan |
| trade_plan_validator.py | ~11.5KB | Validates a trade plan against the schema |
| examples/ | 8 files, ~3.9KB total | Sample valid/invalid trade plan JSON files (folder) |
| .secrets/ | - | API credential storage, gitignored (folder) |

## MTS/BACKTEST/ - Replay & Parity Harness

| File | Size | Purpose |
|------|------|---------|
| snapshots.py | ~1.4KB | Shared archived-snapshot loader for parity.py and replay.py |
| verdict.py | ~5.1KB | Python port of Compute-Verdict + proof_dir_of, parity-guarded |
| parity.py | ~1.7KB | Checks verdict.py against live-logged verdicts |
| replay.py | ~1.9KB | Replays archived snapshots through verdict.py |
| sim.py | ~5.3KB | Backtest simulation driver |
| fetch_bars.py | ~3.2KB | Fetches historical kline bars for backtesting |

## MTS/RESEARCH/ - Active Research (15 files)

| File | Size | Purpose |
|------|------|---------|
| apparatus_fixes.md | ~5KB | Apparatus fix log (frozen). Open items moved to BUGS.md 2026-09-17 |
| BUGS.md | ~7KB | Single source of truth for defects. Rules block + table. Validated at every boot. |
| event_probability_layer_DESIGN.md | ~3KB | 4-AI research, PARKED |
| manual_patterns.md | ~2KB | Working notes: footprint patterns (Rule 32 pending) |
| mtf_flow_alignment_design_2026-09-12.md | ~5KB | MTF alignment design (inert until Rule 32) |
| state_machine_design_2026-09-11.md | ~7KB | State code emitter design |
| SESSION_STATE_SCHEMA.md | ~1.4KB | SSOT schema |
| cross_trader_consolidated.md | ~103KB | Cross-trader 85 rules consolidated |
| cross_trader_integration_plan.md | ~39KB | 4-phase integration workflow |
| dsa_developer_implementation_tasks.md | ~18KB | DSA developer task list |
| visual_validation_protocol_vvp001.md | ~10KB | Screenshot protocol v1 |
| visual_validation_protocol_vvp002.md | ~12KB | Screenshot protocol v2 (extends v1) |
| unclear_extractions.md | ~2KB | Parking lot for unclear extractions |
| validation_prompt_gpt.md | ~8KB | GPT validation prompt template |
| validation_prompt_grok.md | ~7KB | Grok validation prompt template |
| whale_positioning_evidence_2026-09-12.md | ~3KB | 4-AI whale research |
| session_anchor_options_note.md | ~5KB | Session anchor options A/B/C + evidence + constraints (2026-09-18) |
| P1_COST_FLOOR_FULL_20261006_CORRECTED.md | ~2.5KB | P1 analysis: passive limit order adverse selection (PASS: 0.02 bp mean) |
| P1_BREAKDOWNS_20261006.md | ~3KB | P1 breakdowns: discrepancy analysis vs operator 4.7-day run |
| P2_FABIO_V3_HOLDOUT_STATUS.md | ~2.5KB | P2 verification: Fabio v3 holdout L3-FAIL (code unchanged, single OOS read) |
| P4_QUARTER_HOUR_IMBALANCE_20261006_FINAL.md | ~3KB | P4 analysis: Kim & Hansen replication partial (8h PASS, 4h/12h fail sign stability) |
| imbalance_2026-10-10/RESEARCH.md | ~7.5KB | OBI research: free data sources (Binance/8 venues), 3 T1 papers, 1 T2 arXiv, T3 practitioners; no net-of-cost OBI strategy validated |

## MTS/TESTS/ - Test System (9 files)

| File | Size | Purpose |
|------|------|---------|
| UNIT_TEST_PLAN.md | ~3KB | 22 compiled functions, 98 pytest cases |
| test_mts_math.py | ~19KB | 64 unit tests for math functions |
| test_math_object_builder.py | ~16KB | 34 unit tests for math object builder |
| test_session_state.py | ~2.5KB | 8 tests for SSOT helper |
| compiled_code_opportunities.md | ~17KB | Maps engine functions to compileable vs AI-reasoning |
| COMPILED_DECISIONS_TEST_PLAN.md | ~13KB | Test plan for system decisions |
| compiled_decisions_validation_2026-09-02.md | ~11KB | Decision validation report |
| regression_log.md | ~1.7KB | Patch smoke test history |
| state_signal_prototype.py | ~5.4KB | State-code emitter prototype |

## DATA/ - Schemas, Task Specs (MyTradingSys/market_data/)

| File | Size | Purpose |
|------|------|---------|
| data_schema_v1.2.0.md | ~32KB | JSON schema documentation |
| dsa_task_012_setup_candidates.md | ~23KB | DSA_TASK_012 spec |
| sample_btc_snapshot.json | ~6KB | Sample JSON snapshot |
| test_snapshot_v4.2.0-p2_validation.json | ~6KB | Validation snapshot |
| data_state_document.md | ~11KB | Data inventory + gaps |
| DIRECTORY_AUDIT.md | ~2.4KB | Data directory audit |

## EXTRACTS/FRESH/ - 50 Tom Transcript Extractions

All files: extract_[VIDEOID]_fresh.md. Count: 50.

## MTS/EXTRACTS/ - Cross-Trader Extracts (8 files)

| Folder | Files | Status |
|--------|-------|--------|
| cryptocred/extracted/ | 5 extracts | PURE |
| the_flow_horse/extracted/ | 3 extracts | PURE |

## MTS/ARCHIVE/ - Superseded Research (14 files)

Files moved from research/ after their findings were integrated or superseded:
- binance_api_integration_recommendations.md (~53KB)
- binance_api_research_brief.md (~11KB)
- bug_004_investigation.md (~7KB)
- chart_layout_implementation_guide.md (~4KB)
- htf_structure_audit_2026-08-28.md (~27KB)
- indicator_audit_table.md (~21KB)
- indicator_selection_task.md (~4KB)
- questionnaire_for_parallel_session.md (~10KB)
- structural_simplification_research.md (~14KB)
- vvp_test_protocol.md (~3KB)
- vvp_test_results_20260831.md (~15KB)
- vvp_sc_01_15m.png (~326KB)
- vvp_sc_02_3m.png (~231KB)
- vvp_sc_03_6h.png (~232KB)

## ARCHIVE/ (top-level) - Migration Cleanup

| Subfolder | Contents |
|-----------|----------|
| cleanup-2026-09-13/ | 12 .old files from 2026-09-13 cleanup |

## PROJECT ROOT (BinanceDataFeed/)

| File | Size | Purpose |
|------|------|---------|
| pom.xml | ~2.3KB | Maven build |
| DSA_SESSION_PROMPT.md | ~13KB | AI behavior contract for DSA sessions |
| COMMANDS.md | ~6KB | Daily/process/diagnostic commands |
| start_trading_day.ps1 | ~22KB | Apparatus loop |
| mode.ps1 | ~1.5KB | Mode switcher (prep/armed/live) |
| stop_day.ps1 | ~2.3KB | Clean process stop |
| show_alert.ps1 | ~3.4KB | Popup form |
| launch_alert.vbs | ~0.2KB | Alert launcher |
| check_snapshot.py | ~1.5KB | Snapshot check utility |
| divergence_monitor.py | ~4.3KB | Divergence flagger |

## RUNTIME DATA (BinanceDataFeed/runtime_data/)

| Path | Purpose |
|------|---------|
| snapshots/ | BTCUSDT + ETHUSDT JSON snapshots (~1/min) |
| speed_baselines/ | DSA_TASK_014 per-instrument baselines |
| naked_pocs/ | Naked POC tracker state |
| historical/ | Historical snapshot validation |
| apparatus_log.txt | Verdict + alert log |
| apparatus.lock | Singleton lock (PID TS) |
| alert_counter.txt | Monotonic alert ID |
| last_alert.json | Latest alert payload |
| outcome_labels.json | Forward returns per snapshot |
| screening_results.csv | Historical screening output |

## SESSION 2026-09-16 OUTPUTS - MTS/RESEARCH/

| File | Size | Purpose |
|------|------|---------|
| SESSION_LEARNINGS_2026-09-16.md | ~8KB | Full session record. Trade, sweep finding, OI correction, research finding. |
| EVIDENCE_2026-09-16.md | ~2KB | Rule 32 snapshot 1 of 3. Six counter-trade setups with levels and ratios. |
| RESEARCH_2026-09-16_oi_pattern.md | ~3.5KB | Grok and Claude responses on OI/CVD/price pattern. Primary source. |
| zone_map_2026-09-17.md | ~1.6KB | Prepared zones for next session. Short zones above, long zones below. |

## QUICK STATS

| Metric | Value |
|--------|-------|
| Total active files | 149 |
| system/ | 13 |
| methodology/ | 5 |
| mts/conditions/ | 7 |
| mts/cards/ | 20 |
| mts/runtime/ | 14 |
| mts/research/ | 15 |
| mts/tests/ | 9 |
| runtime_data/ | 6 |
| extracts/fresh/ | 50 |
| mts/extracts/ | 8 |
| mts/archive/ | 14 |
| archive/cleanup-2026-09-13/ | 12 |
| Canonical path | C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\ |

---
CLAUDE_MANAGER_SPEC.md | MyTradingSys/research/ | 130 lines | manager spec, front door for all Claude sessions
| MyTradingSys/research/PROMPT_FAILURE_ANALYSIS_2026-10-03.md | report | DSA prompt-composition failure analysis. Eight defects this session; six repeat the 2026-10-02 LESSONS entry. Structural finding: LESSONS_LEARNED.md tail-40 read misses the 2026-10-02 entries. Source for B083. | MTS-2026-10-03-0430Z-DSA-COO | 2026-10-03 |
| MyTradingSys/items/B083_prompt_check_gate.md | item doc | B083 item doc. prompt_check.ps1 gate warns on disk-verification failures in composed prompts. Warn-only; no stop; operator decides. | MTS-2026-10-03-0430Z-DSA-COO | 2026-10-03 |
| MyTradingSys/items/B084_book_imbalance_zero_origin.md | item doc | B084 item doc. Origin of book_imbalance 0.0 in the Python proof block unverified; 13295c8 WIP-partial load-bearing. | MTS-2026-10-03-0430Z-DSA-COO | 2026-10-03 |
| MyTradingSys/items/B085_tom_bt_proof5_skew.md | item doc | B085 item doc. Proof-5 pool skew 215 short : 105 long unexplained; second contradiction path (last_3_delta) affects longs. | MTS-2026-10-03-0430Z-DSA-COO | 2026-10-03 |
| MyTradingSys/items/B086_dispatcher_second_writer.md | item doc | B086 item doc. Dispatcher smoke test launched a second CL writer; one-writer-per-file-set violated. Claude decides fix. | MTS-2026-10-03-0430Z-DSA-COO | 2026-10-03 |
| MyTradingSys/items/B087_pick_task_repick.md | item doc | B087 item doc. pick_task re-picks same row each wake; plus size-header edit and mts go naming. Claude decides fixes. | MTS-2026-10-03-0430Z-DSA-COO | 2026-10-03 |
| MyTradingSys/research/CLOUD_CREDIT_ROADMAP_2026-10-03.md | plan | Cloud credit split plan for awgp account. Boundary is file set, not account. C1-C8 cloud queue. Local lane today: fix-dispatcher prompt, then push. Never touches gitignored files, live trees, restarts, HALT. | MTS-2026-10-03-1120Z-CL-BLD-fix-dispatcher | 2026-10-03 |
# END

| MyTradingSys/research/TOM_VERBATIM_INDEX.md | research | Verbatim Tom quote index. Points to corpus. Rules in conditions/ carry [TOM-NNN] or [SCREENER]. |
| MyTradingSys/research/INDICATOR_IMPLEMENTATION_HANDOFF.md | research | Nine CoinGlass derivative indicator panels. Five-phase implementation plan. Source doc for T032-T035. | MTS-2026-09-18-0848Z | 2026-09-19 |
| MyTradingSys/research/INDICATOR_IMPLEMENTATION_HANDOFF.md | research | Nine CoinGlass derivative indicator panels. Five-phase implementation plan. Source doc for T032-T035. | MTS-2026-09-18-0848Z | 2026-09-19 |
| scripts/tools/verify_rule_citations.ps1 | tool | Checks rule tags resolve to index quotes. |
| scripts/tools/VerifyScbEdits.java | tool | Unit verifier for SetupCandidatesBuilder state gate and tc_long path. 12 checks. | MTS-2026-09-18-1600Z | 2026-09-18 |
| scripts/tools/VerifyStateCodeCvd.java | tool | Reflection verifier for StateCodeEmitter CVD ring day-change reset. 4 checks. Closes T028. | MTS-2026-09-19-0507Z | 2026-09-19 |
| MyTradingSys/research/PROCESS_MANAGEMENT_AUDIT_2026-09-17.md | Process audit: supervisor singleton gap, grace race, lock TOCTOU | MTS-2026-09-17-1142Z | 2026-09-17 |
| MyTradingSys/runtime/live_session_log.md | runtime | RETIRED 2026-09-17. Superseded by live_session_journal.md. Backup: backup_session/live_session_log.md.retired-20260917. | MTS-2026-09-17-1241Z | 2026-09-17 |
| MyTradingSys/runtime/live_session_journal.md | runtime | Append-only session journal. QUOTE / REQ / OBS / DECISION / LANDED / READ. Everything no other file holds. | MTS-2026-09-17-1241Z | 2026-09-17 |
| scripts/live/tape-watch.ps1 | tool | Sidecar watcher. Divergence classifier every 30s. Reads snapshot + state_code. Read-only on loop. | MTS-2026-09-17-1241Z | 2026-09-17 |
| scripts/live/mts-watch.ps1 | tool | CANONICAL live feed (mts-live). v1.1.1. Compiled-layer blocks: MTS-HSTOP, MTS-PROOF, MTS-CAND, MTS-DELTA + state, flow, cycles, slow. See MTS_DICTIONARY.md LIVE FEED NAMES. | MTS-2026-09-17-1241Z | 2026-09-17 |
| MyTradingSys/methodology/chart_read_protocol.md | methodology | Six-layer chart read method. Catches single-pass errors. | MTS-2026-09-18-0848Z | 2026-09-18 |
| MyTradingSys/research/fyi_archive/2026-09-18/01_report_1040Z_from_1624Z.md | archive | FYI report from 1624Z session. H1-H4, M1-M4, L1-L2. | MTS-2026-09-18-0848Z | 2026-09-18 |
| MyTradingSys/research/fyi_archive/2026-09-18/02_consolidated_handoff_0456Z_0848Z.md | archive | Consolidated handoff. Nine blocks, pending decisions, verify list. | MTS-2026-09-18-0848Z | 2026-09-18 |
| MyTradingSys/research/fyi_archive/2026-09-18/03_session_handoff_report_0456Z_0848Z.md | archive | Session handoff report. Fire condition, extraction audit, frame-view gap. | MTS-2026-09-18-0848Z | 2026-09-18 |
| MyTradingSys/research/fyi_archive/2026-09-18/04_final_report_corrected_diagnosis.md | archive | Corrected diagnosis. Supersedes FRAME GATING. determineSetupType defect. Steps 1-6. | MTS-2026-09-18-1600Z | 2026-09-18 |
| MyTradingSys/methodology/live_session_protocol.md | methodology | AI-side checks before any live tape claim. Mistake ledger 2026-09-17. Read at session boot. | MTS-2026-09-17-1241Z | 2026-09-17 |
| MyTradingSys/runtime/SESSION_MANIFEST.json | runtime | Boot manifest. Drives start-session.ps1 SESSION_PASTE.txt generation. | MTS-2026-09-18-1600Z | 2026-09-18 |
| scripts/live/mts-dashboard.ps1 | tool | dashboard command, one-shot and -Watch | MTS-2026-09-17-1757Z | 2026-09-17 |
| scripts/tools/harvest_tom_quotes.py | tool | Harvests Tom quotes from Source GPS lines in condition files. Writes Dumps/tom_harvest.json. Part of T017 pipeline. | MTS-2026-09-18-1726Z | 2026-09-19 |
| scripts/tools/verify_harvest_vs_corpus.py | tool | Verifies harvested quotes against raw_transcripts_canonical/*.txt. Drops untraceable quotes. Writes tom_harvest_verified.json. | MTS-2026-09-18-1726Z | 2026-09-19 |
| scripts/tools/rebuild_tom_index_and_tag.py | tool | Rebuilds TOM_VERBATIM_INDEX.md from verified harvest and applies [TOM-NNN] tags to 6 condition files. Closes T017. | MTS-2026-09-18-1726Z | 2026-09-19 |
| MyTradingSys/research/JISHU_METHOD_2026-09-20.md | 30 | 8E2AB6E6 | 2026-09-20 | jishu_method |

| MyTradingSys/research/MODEL_ALIGNMENT_2026-09-21.md | research | Model alignment carry-forward. Five issues + pre-committed chain. DISK vs UNVERIFIED-WEB tags. | MTS-2026-09-21-0721Z | 2026-09-21 |
| MyTradingSys/research/DIVERGENCE_AUDIT_AND_RESEARCH.md | research | Divergence audit of MTS handling + GOLAS A-D research. Five sections. UNVERIFIED-WEB tags for external claims. | MTS-2026-09-21-1328Z | 2026-09-21 |
| MyTradingSys/research/BACKTEST_METHOD_2026-09-21.md | research | Backtest planning doc. Seven sections. Chosen method is replay of Compute-Verdict over snapshots joined to outcome labels. | MTS-2026-09-21-0729Z | 2026-09-21 |
| MyTradingSys/research/GOLAS_CD_WEB_2026-09-21.md | research | Web reinforcement for GOLAS-C and GOLAS-D. T1/T3 tier tags. States 9-day data cap. | MTS-2026-09-21-1328Z | 2026-09-21 |
| scripts/live/mts-paste.ps1 | tool | Continuous live snapshot writer. Reads log, lock, state_code, regime, latest snapshot, tape, position. Writes Dumps/LIVE_PASTE.txt atomic. LF, no BOM. Stops on runtime_data/live_paste_stop.flag. | MTS-2026-09-21-1328Z | 2026-09-21 |
| MyTradingSys/runtime/backtest_oi_delta_4state.py | 136 | - | 2026-09-21 | backtest |
| MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md | - | - | 2026-09-21 | research |
| MyTradingSys/items/B063_divergence.md | item | Per-item doc for B063. Verbatim ask + chronological updates. | MTS-2026-09-22-1215Z | 2026-09-22 |
| MyTradingSys/items/ | item_dir | One doc per open item. Named by register ID. | MTS-2026-09-22-1215Z | 2026-09-22 |
| MyTradingSys/items/T040_tick_delta_layer.md | item | Per-item doc for T040. Verbatim ask + chronological updates. | MTS-2026-09-22-1215Z | 2026-09-22 |
| MyTradingSys/PROJECT_VISION.md | direction | Direction ledger + locked architecture doctrine (2026-09-23): Tom is core, everything else modular; four gap classes. | MTS-2026-09-23-1236Z | 2026-09-23 |
| operator_reminders.md | methodology | Operator paste-ready reminder card. Machine-aware (desktop vs laptop). A-G prompts, F commands. At repo root for convenience. | MTS-2026-09-23-1236Z | 2026-09-23 |
| MyTradingSys/items/T042_schema_gap.md | item | Per-item doc for T042. Schema gap: snapshot has no 4h/daily/weekly structure, no OI/CVD peak reference. | MTS-2026-09-23-0831Z | 2026-09-23 |
| MyTradingSys/research/PARKED_2026-09-23_T041_TREND_RESEARCH.md | research | Parked T041 trend research + reframe. Resume point: operator intent question. | MTS-2026-09-23-0831Z | 2026-09-23 |
| MyTradingSys/items/T043_traceability_gap.md | item | Per-item doc for T043. Source-to-code traceability mechanism absent. | MTS-2026-09-23-0831Z | 2026-09-23 |
| MyTradingSys/items/B065_stale_swing_consumer.md | item | Per-item doc for B065. Stale swing flag has no consumer; zones built from invalidated swings. | MTS-2026-09-23-0831Z | 2026-09-23 |
| MyTradingSys/items/INDEX.md | index | Boot-loaded one-line-per-item index. Item id, status, filename, state. Read full item doc only when its row is the active task. | MTS-2026-09-24-0639Z | 2026-09-24 |
| scripts/worker/queue_tool.py | tool | SUPERSEDED 2026-10-01: Qwen NUC decommissioned. Historical: NUC queue pack/verify/deploy. T049. | MTS-2026-09-25-2100Z | 2026-09-25 |
| scripts/worker/nuc-worker.ps1 | tool | SUPERSEDED 2026-10-01: Qwen NUC decommissioned. T049. | MTS-2026-09-25-2100Z | 2026-09-25 |
| scripts/worker/nuc-launcher.ps1 | tool | SUPERSEDED 2026-10-01: Qwen NUC decommissioned. T049. | MTS-2026-09-25-2100Z | 2026-09-25 |
| scripts/worker/setup-desktop.ps1 | tool | SUPERSEDED 2026-10-01: Qwen NUC decommissioned. T049. | MTS-2026-09-25-2100Z | 2026-09-25 |
| scripts/worker/setup-nuc.ps1 | tool | SUPERSEDED 2026-10-01: Qwen NUC decommissioned. T049. | MTS-2026-09-25-2100Z | 2026-09-25 |
| MyTradingSys/items/T049_nuc_worker_v2.md | item | Closed 2026-10-01: Qwen NUC decommissioned. Historical design record. | MTS-2026-09-25-2100Z | 2026-09-25 |
| Dumps/workers/NUC-QUEUE/README.md | protocol | SUPERSEDED 2026-10-01: Qwen NUC decommissioned. T049. | MTS-2026-09-25-2100Z | 2026-09-25 |
| MyTradingSys/system/DEVICES.md | reference | Hostnames, IPs, roles, shared paths and accounts for every machine in the pipeline. T049. | MTS-2026-09-26-1520Z | 2026-09-26 |
| MyTradingSys/system/SURFACE_POLICY.md | policy | Surfaces, reach, task ownership, handoff inboxes, budget thresholds, session/branch/lane naming, legacy aliases. Boot file for every surface. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/system/sessions/README.md | registry | Session registry rules + record template. One record file per session; predecessor lookup by -SURF-ROLE. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/system/sessions/MTS-2026-09-30-1005Z-CLD-ANA-connected-system.md | session | First registry record: Cloud analyst session that wrote the connected-system docs. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/MISSING_PIECES_2026-09-30.md | research | Opus applied readings (Fabio jasv3L-d8ZE, Tom yRvMW6lgN1o), why rule synthesis fails, H1 wider stop / H2 adverse-add ladders / H3 narrow-window protocol (model results, no market data). | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/T054_US_SESSION_BRIEF.md | research | T054 brief from on-disk research: US session / correlation / news claims on BTC, verified vs unverified, gaps needing sources. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/TOM_RULEBOOK_MERGE_999.md | research | Redo of lost DSA task 999: 16 new Tom T- rules vs conditions/ master; 4 NEW, 12 MATCH, 2 CONFLICT (stop placement R5, re-acceptance exit R8). | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/CROSS_TRADER_RULEBOOK.md | research | CryptoCred (47 rows) + Flow Horse (32 rows) rulebook in FABIO_RULEBOOK format with built-as-layer column and trade-sequence gaps. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/nuc_specs/2101-2113 (13 files) | spec | DSA-lane trade-reconstruction specs (runner-agnostic): one per Fabio/Tom video, template MISSING_PIECES 3.2. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_REVIEW_2026-09-30.md | research | Method review of Tom core BT: 17 defects (2 HIGH: live rule undiagnosed/all-short, null not like-for-like). | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/FORMULA_AUDIT_2026-09-30.md | research | FORMULAS.md vs code, 43 rows: 39 MATCH, 2 MISMATCH (MSB, executor loss est.), 2 UNTESTABLE; fee duplicates listed. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py | tool | Backtest driver malkan_40_60 / malkan_mtf / rsi_ma_events: IS/OOS 70/30, PBO, sim.py fees. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/backtest/layers/run_bracket_grid.py | tool | Q1 per-layer bracket grid: 6 stops x 3 targets x 3 time exits, IS/OOS, PBO, frozen bracket or default stands. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md | spec | Fabio v3 layer spec: S1-S8, models A (LVN pullback) / B (failed-breakout reclaim) / C (IVB), fills, management, sim.py costs, day gates, grid 97-103 trials, tests T01-T50. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/backtest/layers/fabio/pending_test_fabio_v3.py | test | 52 spec-derived tests for Fabio v3 (written before the implementation); rename to test_fabio_v3.py when fabio_v3*.py land. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/nuc_specs/2201-2203 (3 files) | spec | Runner-agnostic task specs (Qwen decommissioned 2026-10-01): fabio_v3_signals.py, fabio_v3_exec.py, fabio_v3.py. Execute via AIBridge or DSA. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/ANGLE_TRADER_SOURCES.md | research | Web angle on Tom/Fabio public methods: 0 sources opened (cloud egress blocked); unopened leads + pages to open from an unrestricted network. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/ANGLE_ELICITATION_RESEARCH.md | research | Method angle: expert knowledge elicitation (CDM, RPD, protocol analysis) -> incident-record extraction, hindsight tags, labeled-trade confusion matrix. 0 sources opened (egress blocked); all UNVERIFIED. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/FABIO_LINE_BY_LINE_fZlNGWvd2Ko.md | research | Opus line-by-line reading of Fabio fZlNGWvd2Ko (first long trade read): 30-row decision log vs FABIO_V3_SPEC, extract audit, 10 missing pieces, 8 spec change proposals. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/EXTRACTION_METHOD_V2_FABIO.md | method | Fabio extraction method v2 for weaker models: decision rows, trade/day blocks, 14-item miss checklist, worked example. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/ANGLE_TRADE_CATALOG.md | research | Ground-truth catalog of trades actually taken in 102 transcripts: 30 (Tom 21: 15 short / 6 long; Fabio 9), 0 on BTC, instruments DAX/NQ/crude/stock; recurring setup vocabulary. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/ANGLE_HYPOTHESES.md | research | Competing hypotheses with falsifiers + 3 code tests: E-001 book_imbalance 0.0 demotes all longs (confirmed), E-002 TWOPEAK label is a heuristic, E-003 Tom trade cannot pass SetupCandidatesBuilder gates; experiment log format. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/TOM_LINE_BY_LINE_4MoNjEQ2Dd8.md | research | Opus: no-longs code trace (book 0.0 veto; TWOPEAK label always true) + line-by-line reading of Tom live long 4MoNjEQ2Dd8; 5 engine missing pieces. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/fast_track_2026-09-27/EXTRACTION_METHOD_V2.md | method | Extraction method v2 for workers: decision rows in order, trade blocks, before/after-proof entry flag, 15-item miss checklist, long/short symmetry rules; Fabio appendix in EXTRACTION_METHOD_V2_FABIO.md. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| scripts/dev/testnet_status.py | tool | Daily sanitized testnet status (per family x account: alerts, entries, closes, P/L, skips, brakes; 0-trade flags) -> MyTradingSys/research/testnet_status/. Gate step 3s. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| scripts/dev/funnel_report.py | tool | Read-only L4 funnel: per UTC day x source, alerts -> rejected/skipped -> attempts -> filled -> closed, wins, net P/L, from auto_trades.jsonl + trade_ledger.jsonl + runtime/alerts. Stdout only; --day/--days. Gate step 3f. | MTS-2026-10-03-1314Z-CLI-BLD-tf2-per-source-live | 2026-10-03 |
| scripts/dev/test_funnel_report.py | test | Hand-counted fixtures for funnel_report.py (counts, ledger dedupe, open trades, bad lines, read-only). | MTS-2026-10-03-1314Z-CLI-BLD-tf2-per-source-live | 2026-10-03 |
| scripts/dev/testnet_canary.py | tool | Read-only liveness + new-code canary for the testnet stack: processes, loop/log freshness, unconsumed Tom alerts, brake files (existence only), commits on live/Tom/Fabio paths; --run-gates; prints RESTART NEEDED (supervisor only). Exit 0/1/2 = GREEN/WARN/RED -> research/testnet_status/CANARY_<date>.md. Never restarts. | MTS-2026-10-02-1050Z-CLI-SUP-direction | 2026-10-02 |
| scripts/dev/test_testnet_canary.py | test | 20 pytest cases for testnet_canary (fail-closed proc query, brake files never opened, restart-needed via temp git repo). | MTS-2026-10-02-1050Z-CLI-SUP-direction | 2026-10-02 |
| MyTradingSys/research/DIRECTION_REVIEW_2026-10-02.md | report | Direction review: testnet down, Tom/Fabio 0 trades, NO-SOURCE gates still live, re-ordered priorities P0-P8, 4 operator decisions. | MTS-2026-10-02-1050Z-CLI-SUP-direction | 2026-10-02 |
| MyTradingSys/research/fast_track_2026-09-27/PROVENANCE_AUDIT_TOM.md | research | Provenance audit of the Tom core path (74 rows): 2 TOM-SOURCED, 33 concept-only, 36 NO-SOURCE, 3 plumbing; 2:1 net miscited to qLnQan0KGmQ; safety rules X1-X8 listed unjudged. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/AUDIT_REVIEW_2026-10-01.md | review | DSA review of the Tom/Fabio provenance work: 10 sections, verdict tally, impact ranks, method gaps (no pre-registration, single reader, no falsification), backtest-stat defects (H1-H2, M7-M9), six ranked alternatives, scientific-method gap list. | MTS-2026-10-01-1431Z-DSA-COO | 2026-10-01 |
| MyTradingSys/research/REVALIDATION_REQUEST_2026-10-01.md | review | DSA revalidation request for Claude: 10 scientific methods (DSR, PBO, CPCV, White/Hansen SPA, Romano-Wolf, BH-FDR, stationary bootstrap, kappa, purged CV, pre-registration) with proof paths, source citations, and what to check. | MTS-2026-10-01-1431Z-DSA-COO | 2026-10-01 |
| MyTradingSys/research/HANDOFF_FOR_CLAUDE_2026-10-01.md | review | Handoff to Claude: 6 second-iteration findings (single-reader count, counterfactual gap, support-not-falsification search, section 10 omissions, no Fabio audit, defective adoption gate) + 8 work items W1-W8 with input/task/output/gate. | MTS-2026-10-01-1431Z-DSA-COO | 2026-10-01 |
| MyTradingSys/system/AIBRIDGE_LANE.md | system | Lane contract, rewritten 2026-10-08 for DSA direct mode: bridge policy (roots = project working tree, delete allowed, deny list, caps, ACL option), acceptance checks, open items. | MTS-2026-10-08-0806Z-APP-BLD-dsa-direct-mode | 2026-10-08 |
| MyTradingSys/research/_archive/purge_2026-10-03/PROMPT_CONFORMANCE_CHECKLIST.md.deprecated | archived | Removed 2026-10-03 by operator directive. Was a DSA prompt conformance gate; superseded by decide-and-log per USER.md. | MTS-2026-10-02-2055Z-DSA-COO | 2026-10-03 |
| MyTradingSys/research/ARCHITECTURE_TWO_CORES_2026-10-01.md | spec | Architecture doctrine: Tom core and Fabio core, each compiled and independently flagged; modules never gate core; consensus row at alert time is observation only. | MTS-2026-10-01-1755Z-DSA-COO | 2026-10-01 |
| MyTradingSys/research/CLOUD_PROMPT_TWO_CORES_2026-10-01.md | prompt | Cloud Sonnet brief: three tables (wiring, test gap, revalidation), fix pass, two-core scaffold. Budget-tier branch, real live_runner path, ownership claim, index row, verify block. | MTS-2026-10-01-1755Z-DSA-COO | 2026-10-01 |
| MyTradingSys/research/CLOUD_PROMPT_W3_KAPPA_2026-10-02.md | prompt | CC second session: W3 kappa clean reader. Blind to PROVENANCE_AUDIT_TOM until CSV committed. No inbox edits (collision-avoid). | MTS-2026-10-01-1755Z-DSA-COO | 2026-10-02 |
| MyTradingSys/research/W3_KAPPA_READER_2026-10-01.csv | data | Blind second reader's 74 provenance verdicts (id,verdict) for the W3 kappa. | MTS-2026-10-01-1900Z-CLD-ANA-w3-kappa | 2026-10-01 |
| MyTradingSys/research/W3_KAPPA_FIRST_2026-10-01.csv | data | First reader's 74 verdicts copied from PROVENANCE_AUDIT_TOM section 2-6 (id,verdict). | MTS-2026-10-01-1900Z-CLD-ANA-w3-kappa | 2026-10-01 |
| MyTradingSys/research/W3_KAPPA_REPORT_2026-10-01.md | report | W3 kappa result: 0.446 (< 0.6), confusion table, 24 disagreeing rows, per-row citations; the 36 NO-SOURCE count is reader-dependent. | MTS-2026-10-01-1900Z-CLD-ANA-w3-kappa | 2026-10-01 |
| MyTradingSys/system/sessions/MTS-2026-10-01-1900Z-CLD-ANA-w3-kappa.md | session | Session record for the W3 kappa clean-reader cloud session. | MTS-2026-10-01-1900Z-CLD-ANA-w3-kappa | 2026-10-01 |
| MyTradingSys/research/TWO_CORES_READINESS_2026-10-01.md | review | Two cores readiness: wiring table (11 rows + extras), T037 test-gap inventory, W1-W8 revalidation status, merged priority list, top-5 fix proposals with acceptance checks. | MTS-2026-10-01-1858Z-CLD-BLD-two-cores | 2026-10-01 |
| MyTradingSys/research/TWO_CORES_SCAFFOLD_2026-10-01.md | spec | Two-core scaffold spec: current state of Tom/Fabio, compiled-core changes, consensus writer, RSI observation block, switchability config, migration order; file:line cited. | MTS-2026-10-01-1858Z-CLD-BLD-two-cores | 2026-10-01 |
| MyTradingSys/system/sessions/MTS-2026-10-01-1858Z-CLD-BLD-two-cores.md | system | Session record for the cloud two-cores build session (budget 85 assumed, no subagents, fix pass queued). | MTS-2026-10-01-1858Z-CLD-BLD-two-cores | 2026-10-01 |
| MyTradingSys/research/CLOUD_PROMPT_TWO_CORES_INTEGRATION_2026-10-02.md | prompt | CC integration: readiness fix pass, Fabio v3 core compile, consensus writer, RSI observation, switchability spec, desktop runbook. | MTS-2026-10-01-1755Z-DSA-COO | 2026-10-02 |
| MyTradingSys/research/CL_PROMPT_BOOK_IMBALANCE_2026-10-02.md | prompt | CL one-file brief: promote book_imbalance 0.0 guard in math_object_builder.py. Fail-first + four-step proof + Build-Check. | MTS-2026-10-01-1755Z-DSA-COO | 2026-10-02 |
| MyTradingSys/system/CLOUD_ACCOUNTS.md | system | Cloud account identity, credits pools, expiry, GitHub wiring options (collaborator vs shared credential). | MTS-2026-10-01-1755Z-DSA-COO | 2026-10-02 |
| MyTradingSys/tests/test_book_imbalance_nodata.py | test | Fail-first for book_imbalance 0.0 guard: 0.0 (no data) must not fire ask-heavy vs LONG. 11 cases. | MTS-2026-10-02-0910Z-CLI-BLD-bookimbal | 2026-10-02 |
| MyTradingSys/tests/test_proof_direction.py | test | Proof-direction cases. Updated 2026-10-02: book=0.0 is aligned, not contradiction. | MTS-2026-10-02-0910Z-CLI-BLD-bookimbal | 2026-10-02 |
| MyTradingSys/tests/test_tom_golden.py | test | Tom golden-scenario translation tests (L2): 14 scenarios from 4MoNjEQ2Dd8 v2 + catalog rows through auto_trader.tom_signal; 6 known gaps skip with reason (MTS_TOM_GOLDEN_STRICT=1 fails them); MTS_TOM_GOLDEN_TARGET points at a staged copy. | MTS-2026-10-03-1659Z-CLI-BLD-tf6-tom-golden-scena | 2026-10-03 |
| scripts/dev/alert_rate_check.py | tool | Alert-rate check. Updated 2026-10-02: TF_MIN gains 3m and 1d for the RSI observation block. | MTS-2026-10-02-0930Z-CLI-BLD-tfmap | 2026-10-02 |
| MyTradingSys/execution/auto_trader.py | execution | Layer/tom alert orchestrator. Updated 2026-10-02: TF_SECONDS gains 3m (1d already present). Live-path; loop was down at promotion. | MTS-2026-10-02-0930Z-CLI-BLD-tfmap | 2026-10-02 |
| MyTradingSys/research/CC_PROMPT_FABIO_V3_CORE_2026-10-02.md | prompt | CC brief: finish Fabio v3 core. Review staged, write engine.py, 7 test files, README. Cap 3 subagents, batch 1, Ultracode off. | MTS-2026-10-01-1755Z-DSA-COO | 2026-10-02 |
| MyTradingSys/research/CL_PROMPT_FABIO_V3_CORE_2026-10-02.md | prompt | CL brief: Fabio v3 engine.py only. 1 percent budget, no subagents, save-work checkpoints, stop-early rules. | MTS-2026-10-01-1755Z-DSA-COO | 2026-10-02 |
| MyTradingSys/research/CL_PROMPT_FABIO_V3_TESTS_2026-10-02.md | prompt | CL brief: one test file per session (test_signals.py.new). Fail-first proof, one pytest run, no git. | MTS-2026-10-01-1755Z-DSA-COO | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/tests/test_fabio_golden.py | test | Fabio golden-scenario translation tests (L2) on the v3 engine: 20 scenarios from fZlNGWvd2Ko line-by-line + FABIO_TRADE_MODEL (0jM5Y31YJak, 8CWKfoSJu3c) with hand-derived order-flow-bar fixtures; 2 known gaps skip with reason (MTS_FABIO_GOLDEN_STRICT=1 fails them). 18 pass; gated by PYTEST_LAYER_PATHS. | MTS-2026-10-03-1714Z-CLI-BLD-tf7-fabio-golden-sce | 2026-10-03 |
| MyTradingSys/backtest/layers/fabio/v3/__init__.py | code | Fabio v3 package exports (re-exports costs, day_gates, fill, manage, models, signals). 17 lines. Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/costs.py | code | Fabio v3 costs: fees from backtest/fees.py (B081), slippage, funding, leg_r. 66 lines. Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/day_gates.py | code | Fabio v3 day rules: NY/London/Asia windows, first-leg gates, day gate, CI half-width. 185 lines. Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/engine.py | code | Fabio v3 top-level run(bars, config). 165 lines, 6 unknown markers (L61, 80, 90, 102, 135, 162). Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/fill.py | code | Fabio v3 fill mechanics: find_fill, taker_fill, missed_winner. 46 lines. Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/manage.py | code | Fabio v3 trade management: BE, trail, opp_stop, adds, walk_trade. 221 lines. Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/models.py | code | Fabio v3 models A-D scanners and trade builders. 465 lines. Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/README.md | doc | Fabio v3 package README. 46 lines. Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/signals.py | code | Fabio v3 signals S1-S9 (balance, pressure, big push, breakout, effort/result, VA/LVN, exhaustion). 443 lines. Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/tests/test_costs_fill.py | test | Fabio v3 costs and fill tests (14 tests). Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/tests/test_day_gates.py | test | Fabio v3 day-gate tests (13 tests). Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/tests/test_manage.py | test | Fabio v3 management tests (15 tests). Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/tests/test_models_engine.py | test | Fabio v3 models A-D and engine run() tests (28 tests). Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/layers/fabio/v3/tests/test_signals.py | test | Fabio v3 S1-S9 signal tests (23 tests). Promoted from .new 2026-10-02; pytest 93 passed (v3/tests), run_all_tests --quick PASS; not in the gate yet. | MTS-2026-10-02-1035Z-CLI-SUP-plan-promote-v3 | 2026-10-02 |
| MyTradingSys/backtest/tom_bt_diag.py | script | Replays the proof>=5 snapshots with verdict reason logged (cache path tom_bt.py:101-105 + stage attribution); writes F:/MTS/data/tom_bt/allshorts.diag.jsonl. Read-only on repo. | MTS-2026-10-02-1422Z-CLI-BLD-tom-diag | 2026-10-02 |
| MyTradingSys/research/TOM_BT_SHORT_DIAGNOSIS_2026-10-02.md | research | Why all 19 Tom core SETUP_FORMING are short: book_imbalance 0.0 contradicted every proof-5 long (fixed in 13295c8, cache stale); 215:105 proof-5 skew unexplained. | MTS-2026-10-02-1422Z-CLI-BLD-tom-diag | 2026-10-02 |
| MyTradingSys/research/MARKET_ANALYSIS_2026-10-02.md | research | Independent tape analysis 2026-10-01T13:30Z..2026-10-02T15:50Z vs Tom verdict gates and Fabio reports: 1 SETUP_FORMING (10-01 short, scalp-suppressed), 0 on 10-02; net_rr 2.0 floor blocked the proof-5 daily-VAH short at the day high; v3 not runnable (no OF bars, NS-grid). | MTS-2026-10-02-1530Z-CLI-ANA-tom-fabio-session | 2026-10-02 |
| MyTradingSys/system/runner_min_distance.json | config | Runner min-distance config. Key runner_min_distance_pct = 0.25 (percent of target). NO-SOURCE, operator Ruling 2026-10-03 delegates value to judgment. Read by RunnerMinDistance.java and runtime/runner_min_distance.py. | MTS-2026-10-02-2055Z-CLI-SUP-r2-promote | 2026-10-03 |
| MyTradingSys/runtime/runner_min_distance.py | code | Single Python reader of runner_min_distance.json. Fail-closed on missing/unparsable/negative value. Used by math_object_builder.pick_target via runner_min_pct parameter. | MTS-2026-10-02-2055Z-CLI-SUP-r2-promote | 2026-10-03 |
| src/main/java/datafeed/RunnerMinDistance.java | code | Single Java reader of runner_min_distance.json. NaN on bad file. Used by SetupCandidatesBuilder.pickTarget 6-arg overload; 5-arg overload keeps min 0. | MTS-2026-10-02-2055Z-CLI-SUP-r2-promote | 2026-10-03 |
| MyTradingSys/backtest/layers/fabio/orderflow_live.py | code | R3 live order-flow bar writer. Polls Binance USD-M aggTrades by id, writes closed minutes to MyTradingSys/runtime/orderflow_live/YYYY-MM-DD.csv in the offline 27-column schema. Restart-safe (resumes by id). Big-trade thresholds use only prior days. | MTS-2026-10-03-2245Z-CLI-BLD-r3-orderflow-bars | 2026-10-03 |
| MyTradingSys/research/OPERATOR_DIRECTIVE_2026-10-03-historical-testing.md | directive | Operator directive: historical testing authorized for module-layer parameters; operator-supplied values labeled OPERATOR-EXPERIMENT; all pending tasks move into one continuous build-and-test workflow. Three operator statements verbatim. | MTS-2026-10-03-0328Z-DSA-COO | 2026-10-03 |
| MyTradingSys/runtime/BUILD_PIPELINE.md | queue | Single queue for all pending work. Waves 0-7. Same T0-T5 contract per item; gate on tests + Build-Check. Status: QUEUED / IN-FLIGHT / GATED / LANDED / BLOCKED / PARKED. | MTS-2026-10-03-0328Z-DSA-COO | 2026-10-03 |
| MyTradingSys/research/CICD_PIPELINE_2026-10-03.md | research | End-to-end CI/CD design: intake, pre-commit, build, contract, artifact-hash, live-path, release and post-close stages. Names runner and receipt per stage; no stage stops. States what the cloud can and cannot verify. Design only, no code. | MTS-2026-10-03-0500Z-CL-BLD-cicd-pipeline | 2026-10-03 |
| MyTradingSys/research/WORK_REVIEW_2026-10-03.md | research | Review of every open item across BUGS, INDEX, pipeline, apparatus_fixes and both handoffs: stale, orphan, merge, dead lists, critical three, rank bands. Disk-verified. | MTS-2026-10-03-0500Z-CL-BLD-cicd-pipeline | 2026-10-03 |
| scripts/dev/cicd_run.py | tool | End-to-end CI/CD runner, stages 2.1-2.9 (intake, pre-commit, build, contract, artifact hash, live-path, release, post-close, failure handling); profiles desktop, precommit, postclose, cloud. Advisory: no stage stops the run; one JSONL row per stage to runtime/cicd_run_<date>.jsonl; exit 0/1/2 is data; --write-baseline seeds critical_files.json. Design: research/CICD_PIPELINE_2026-10-03.md. | MTS-2026-10-03-0600Z-CL-BLD-registry-and-cicd | 2026-10-03 |
| MyTradingSys/system/critical_files.json | config | Hash baseline for the nine critical files (DSA_SESSION_PROMPT section 6): path, git blob id (hash-object), sha256_8, eol, approved_by. Values OBSERVED 2026-10-03; first approval is the operator's. Read by cicd_run stage 2.5. | MTS-2026-10-03-0600Z-CL-BLD-registry-and-cicd | 2026-10-03 |
| MyTradingSys/tests/test_cicd_run.py | test | 25 pytest cases for cicd_run: one per stage 2.1-2.9 plus runner mechanics (CRASH row, exit code, unwritable receipt) and baseline shape. Temp repos, faked mvn, no live-tree write. | MTS-2026-10-03-0600Z-CL-BLD-registry-and-cicd | 2026-10-03 |
| scripts/dev/prompt_check.ps1 | tool | B083 advisory prompt check: paths resolve, file:line is a real line, UPPER_SNAKE tokens present in the cited file, do-not/never/cap clauses tagged OPERATOR-SET, no invented capability limit. PASS/FAIL table and STATUS line; exit 0 always; one row per check to runtime/prompt_check_log.jsonl. | MTS-2026-10-03-0600Z-CL-BLD-registry-and-cicd | 2026-10-03 |
| scripts/dev/test_prompt_check.ps1 | test | Four fixtures for prompt_check.ps1 (fake path, clean prompt, untagged do-not, absent token) plus a tagged-clause control, in a temp dir. | MTS-2026-10-03-0600Z-CL-BLD-registry-and-cicd | 2026-10-03 |
| MyTradingSys/system/sessions/MTS-2026-10-03-0600Z-CL-BLD-registry-and-cicd.md | session | Session record: registry repair (T062, B075 receipt, T053-T058 rows, B077-B079 INDEX), CI/CD runner build, prompt_check build; receipts and T0-T5. | MTS-2026-10-03-0600Z-CL-BLD-registry-and-cicd | 2026-10-03 |
| scripts/sched/pick_task.py | tool | Queue dispatcher: reads BUILD_PIPELINE.md plus BUGS-only OPEN ids swept into wave max+1 (B089), picks the first pickable QUEUED row (wave order), one session-id builder (CLI, B088), writes next_task.txt/.json and pick_log.jsonl under runtime/queue; archives the prior pick; prints PICK or IDLE. | MTS-2026-10-03-1300Z-CL-BLD-queue-dispatcher | 2026-10-03 |
| MyTradingSys/tests/test_pick_task.py | test | Twenty-two pytest fixtures for pick_task.py (14-16 B088 surface code + cooldown source, 17-22 B089 sweep incl. two live-tree reads) (empty, one row, BLOCKED, operator blocker, BUGS CLOSED, wave-only slug without file, prior pick renamed; B087 hold, cooldown expiry, landed drop, corrupt state, recompose, slug cap) against temp roots. | MTS-2026-10-03-1300Z-CL-BLD-queue-dispatcher | 2026-10-03 |
| MyTradingSys/system/sessions/MTS-2026-10-03-1300Z-CL-BLD-queue-dispatcher.md | session | Session record: queue dispatcher build, T0 contract quotes, fail-before proof, live runs, deviations. | MTS-2026-10-03-1300Z-CL-BLD-queue-dispatcher | 2026-10-03 |
| scripts/sched/go.py | tool | Body of mts go: dry run inside a Claude Code session or with --dry, live launch from the operator terminal; derives the session name from a kebab slug via pick_task.session_id; legacy -CL- names launch as -CLI-. B086, B087c, B088. | MTS-2026-10-03-1145Z-CL-BLD-fix-dispatcher | 2026-10-03 |
| MyTradingSys/tests/test_go.py | test | Nine fixtures for go.py (8-9 B088) with a fake claude executable: dry guard, live launch, slug naming, bad slug, IDLE, mts.ps1 delegation. | MTS-2026-10-03-1145Z-CL-BLD-fix-dispatcher | 2026-10-03 |
| MyTradingSys/system/sessions/MTS-2026-10-03-1145Z-CL-BLD-fix-dispatcher.md | session | Session record: B086 and B087 closed (dispatcher one-writer guard, re-pick hold, computed SIZE header, slug session names). | MTS-2026-10-03-1145Z-CL-BLD-fix-dispatcher | 2026-10-03 |
| MyTradingSys/research/TOM_FABIO_REVIEW_2026-10-03.md | research | 7-day review of Tom/Fabio extraction-to-trade work: live funnel since R1/R2, why trades die (execution not audited), 4-level test plan, other-layer status, session plan, CI/CD rows TF1-TF8 + LY1-LY5. | MTS-2026-10-03-1035Z-CL-SUP-tf-review | 2026-10-03 |
| MyTradingSys/system/sessions/MTS-2026-10-03-1035Z-CL-SUP-tf-review.md | session | Session record: Tom/Fabio 7-day review, pipeline rows added (wave 1 TF*, wave 8 LY*, R7 requeued). | MTS-2026-10-03-1035Z-CL-SUP-tf-review | 2026-10-03 |
| MyTradingSys/system/sessions/MTS-2026-10-03-1230Z-CLI-BLD-fix-b088-b089.md | session | Session record: B088 (surface code CLI, cooldown sourced) and B089 (BUGS sweep, shape A) closed; T0 quotes, T3 queue decision, fail-before proof, deviations. | MTS-2026-10-03-1230Z-CLI-BLD-fix-b088-b089 | 2026-10-03 |
| scripts/dev/test_run_all_tests.py | test | Gate coverage: run_all_tests.py runs Fabio v3 + orderflow_live + htf_context_live pytest paths (TF1, E7). | MTS-2026-10-03-1059Z-CLI-BLD-tf1-gate-fabio-v3 | 2026-10-03 |
| MyTradingSys/system/sessions/MTS-2026-10-03-1059Z-CLI-BLD-tf1-gate-fabio-v3.md | session | Session record: TF1 gate of Fabio v3 + live-writer tests, fail-before proof, deviations. | MTS-2026-10-03-1059Z-CLI-BLD-tf1-gate-fabio-v3 | 2026-10-03 |
| MyTradingSys/backtest/layers/fabio/of_backfill.py | code | TF3 collection-only backfill of finished days into runtime/orderflow_live (live schema) from the aggTrades archive; never touches _state.json or the live writer day. | MTS-2026-10-03-1329Z-CLI-BLD-tf3-fabio-v3-live | 2026-10-03 |
| MyTradingSys/backtest/layers/fabio/test_of_backfill.py | test | Tests for of_backfill.py: schema/values, state untouched, live-day refusal, no overwrite, no-causal-threshold refusal. | MTS-2026-10-03-1329Z-CLI-BLD-tf3-fabio-v3-live | 2026-10-03 |
| MyTradingSys/system/sessions/MTS-2026-10-03-1329Z-CLI-BLD-tf3-fabio-v3-live.md | session | Session record: TF3 diagnosis (Saturday, not volume_tier), backfill, fail-before, deviations. | MTS-2026-10-03-1329Z-CLI-BLD-tf3-fabio-v3-live | 2026-10-03 |
| MyTradingSys/research/EXEC_PROVENANCE_AUDIT.md | doc | TF4 execution provenance audit, Tom + Fabio: 24 rows (entry order type, limit wait, time exit, size/50-50, runner distance, max age, break-even, stop, target; entry-before-proof per v2 extract), quotes verified, ranked fix list for TF5. Read-only audit. | MTS-2026-10-03-1444Z-CLI-BLD-tf4-execution-proven | 2026-10-03 |
| MyTradingSys/system/sessions/MTS-2026-10-03-1444Z-CLI-BLD-tf4-execution-proven.md | session | Session record: TF4 execution provenance audit, checks run, deviations. | MTS-2026-10-03-1444Z-CLI-BLD-tf4-execution-proven | 2026-10-03 |
| MyTradingSys/research/CC_TASK_LIST_2026-10-03.md | doc | Follow-on task list from the TF5 lines: 6 batches (TF5 promote, fail-closed config load, one-instant basis, measure TF5 values, H5 items 4-6 rows, CL composer), file:line, gate, independence, surface; dedupe table. Read-only. | MTS-2026-10-03-1620Z-CLI-BLD-tf5-tom-exec | 2026-10-03 |
| MyTradingSys/research/CL_PROMPT_TEMPLATE_REVIEW_2026-10-03.md | doc | CL prompt template review: composer shape and est. token cost per block, redundancy vs CLAUDE.md/SURFACE_POLICY/DSA prompt, 5-line proposed template, savings, 30-line cap kept. Read-only. | MTS-2026-10-03-1620Z-CLI-BLD-tf5-tom-exec | 2026-10-03 |
| MyTradingSys/system/sessions/MTS-2026-10-03-1620Z-CLI-BLD-tf5-tom-exec.md | session | Session record: TF5 staged execution fixes (E1 basis + wait, E3 size/split, E2 flat time exit), gates, deviations. | MTS-2026-10-03-1620Z-CLI-BLD-tf5-tom-exec | 2026-10-03 |
| MyTradingSys/system/sessions/MTS-2026-10-03-1659Z-CLI-BLD-tf6-tom-golden-scena.md | session | Session record: TF6 Tom golden-scenario tests, gap list, gate, deviations. | MTS-2026-10-03-1659Z-CLI-BLD-tf6-tom-golden-scena | 2026-10-03 |
| MyTradingSys/backtest/layers/fabio/run_v3_l3.py | code | Fabio v3 L3 runner (PRE_REG_FABIO_V3.md): IS grid 112 cells, frozen selection, OOS, stress, DSR/PBO; OOS wiring hangs (B099). Not live-imported. | MTS-2026-10-03-1759Z-CLI-BLD-tf8-fabio-v3-histori | 2026-10-04 |
| MyTradingSys/backtest/layers/fabio/test_run_v3_l3.py | test | 8 spec-derived tests for run_v3_l3 (grid counts 48/24/16/24, N=139, split excludes holdout, summ, week_boot). Not yet in PYTEST_LAYER_PATHS. | MTS-2026-10-03-1759Z-CLI-BLD-tf8-fabio-v3-histori | 2026-10-04 |
| MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md | doc | Pre-registration for the Fabio v3 L3 backtest (metric, thresholds, stop rule, N=139); result block: none, BLOCKED B099. | MTS-2026-10-03-1759Z-CLI-BLD-tf8-fabio-v3-histori | 2026-10-04 |
| MyTradingSys/items/B099_v3_l3_pool_hang.md | doc | Bug: run_v3_l3 OOS pass hangs in ProcessPoolExecutor, no fail-closed path. | MTS-2026-10-03-1759Z-CLI-BLD-tf8-fabio-v3-histori | 2026-10-04 |
| MyTradingSys/system/sessions/MTS-2026-10-03-1759Z-CLI-BLD-tf8-fabio-v3-histori.md | session | Session record: TF8 pre-reg, runner, tests, B099 block. | MTS-2026-10-03-1759Z-CLI-BLD-tf8-fabio-v3-histori | 2026-10-04 |
| MyTradingSys/tests/test_b070_fee_parity.py | test | Java taker-fee constant equals backtest/fees.py; mts_math default is the same number. | MTS-2026-10-03-1845Z-CLI-BLD-b070-demote-utc-00 | 2026-10-04 |
| src/test/java/datafeed/CvdAnchorDisplayOnlyTest.java | test | B070: CVD value follows session bars; slope/last_3_delta ignore the UTC anchor. | MTS-2026-10-03-1845Z-CLI-BLD-b070-demote-utc-00 | 2026-10-04 |
| MyTradingSys/tests/test_b091_build_check_tiers.py | test | B091: Build-Check -Quick skips math tests; -ReadOnly leaves BUILD_REPORT.md untouched; guarded against self-recursion. | MTS-2026-10-04-0200Z-CLI-BLD-b091-buildcheck-speed | 2026-10-04 |
| MyTradingSys/system/sessions/MTS-2026-10-04-0200Z-CLI-BLD-b091-buildcheck-speed.md | session | Session record: B091 Build-Check quick and read-only tiers. | MTS-2026-10-04-0200Z-CLI-BLD-b091-buildcheck-speed | 2026-10-04 |
| MyTradingSys/tests/test_b076_setup_confirmed_unreachable.py | test | B076: verdict ladders (Python + PowerShell) never emit SETUP_CONFIRMED; proof thresholds 3/5; compiled_engine sec 8 note present. | MTS-2026-10-03-2114Z-CLI-BLD-b076-setup-confirmed | 2026-10-04 |
| MyTradingSys/system/sessions/MTS-2026-10-03-2114Z-CLI-BLD-b076-setup-confirmed.md | session | Session record: B076 verdict-path trace. | MTS-2026-10-03-2114Z-CLI-BLD-b076-setup-confirmed | 2026-10-04 |
| MyTradingSys/system/sessions/MTS-2026-10-03-1845Z-CLI-BLD-b070-demote-utc-00.md | session | Session record: B070 fee model + UTC anchor display-only. | MTS-2026-10-03-1845Z-CLI-BLD-b070-demote-utc-00 | 2026-10-04 |
| MyTradingSys/items/B116_unsourced_stop_floor_and_fallback.md | doc | Bug B116: Unsourced 0.1 percent minimum stop floor and 0.2 percent fallback stop are still live in SetupCandidatesBui. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/items/B117_unsourced_proof_bands.md | doc | Bug B117: Unsourced proof bands 3 and 5 gate WAIT_PROOF, WATCH and SETUP_FORMING in start-trading-day.ps1. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/items/B118_layer_bracket_unsourced.md | doc | Bug B118: Layer bracket in auto_trader.py is a fixed unsourced stop_pct 1.0, targets 2, size 100 for every layer alert. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/items/B119_desktop_operator_gated_revalidation.md | doc | Bug B119: Revalidation items gated on desktop or operator: 9 papers unopened, W3 kappa has no clean reader, T2 run ne. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/items/B120_provenance_audit_doc_followups.md | doc | Bug B120: Tom provenance audit doc follow-ups from W3 and revalidation not delivered. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/items/B121_poll_cadence_defaults.md | doc | Bug B121: Bar-aligned polling and 5 s auto_trader poll not landed; live_runner_cli 60 s and auto_trader 20 s defaults. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/items/B122_reject_text_event_fallback.md | doc | Bug B122: auto_trader.py reject text uses alert.get('event') instead of the fallback key. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/items/B123_zero_trade_and_quiet_families.md | doc | Bug B123: Zero-trade and QUIET family follow-ups from the 2026-09-30 maintainer report: Tom main and fabio jishu_3 af. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/items/B124_journal_dir_open_plan_check.md | doc | Bug B124: No check that execution/journal holds a file for each open plan; testnet_canary has no journal check. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/items/B125_consensus_writer_staged_only.md | doc | Bug B125: Consensus writer exists only as staged writer.py.new and test_writer.py.new; not promoted, so not live. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/items/B126_supervisor_inbox_consumption.md | doc | Bug B126: Cloud to SUP inbox consumption cannot be verified; SUPERVISOR_LOG.md:203 is still the last inbox line. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/items/B127_partial_code_no_test.md | doc | Bug B127: audit PARTIAL (e) code exists, test missing. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/items/B128_partial_code_partial_no_test.md | doc | Bug B128: audit PARTIAL (f) code partial, no test. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/system/sessions/MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup.md | session | Session record: audit-reconcile follow-up, 45 NOT rows grouped a-d, 31 PARTIAL rolled into B127/B128. | MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup | 2026-10-04 |
| MyTradingSys/research/T053_TWO_ACCOUNT_HEDGE_RESEARCH.md | doc | T053 research: method note, tiers, tagged findings, REJECT list, operator questions on two-account hedge scalping; no validated evidence for hedge loops. | MTS-2026-10-04-1010Z-APP-ANA-t053-hedge-research | 2026-10-04 |
| MyTradingSys/tests/test_b074_rule_order.py | test | B074 verdict rule-order pin and B069 wrapper log/exit-code test; runs real start-trading-day.ps1 text under pwsh. | MTS-2026-10-04-1034Z-APP-BLD-b074-b069-wrapper | 2026-10-04 |
| MyTradingSys/system/sessions/MTS-2026-10-04-1034Z-APP-BLD-b074-b069-wrapper.md | session | Session record: B074 rule order + B069 wrapper log fix. | MTS-2026-10-04-1034Z-APP-BLD-b074-b069-wrapper | 2026-10-04 |
| MyTradingSys/items/B129_b074_test_harness_fragility.md | doc | Bug B129: test_b074_rule_order.py extraction depends on line layout; fail-before fires on parser error, not assertion. | MTS-2026-10-04-0916Z-DSA-COO | 2026-10-04 |
| src/test/java/datafeed/MarketDataSnapshotTest.java | test | T037: promoted skeleton; OI delta four-state helper test live, 15 body tests @Disabled until a BinanceClient seam exists. | MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage | 2026-10-04 |
| src/test/java/datafeed/SetupScreenerTest.java | test | T037: SetupScreener S01-S05 hand-summed scores, caps, visual-validation flags, JSON output. | MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage | 2026-10-04 |
| src/test/java/datafeed/ExtraSetupBuilderMomentumTest.java | test | T037: ExtraSetupBuilder momentum short/long, stop/target/RR hand maths, rejection paths. | MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage | 2026-10-04 |
| src/test/java/datafeed/SetupCandidatesBuilderRulesTest.java | test | T037: SetupCandidatesBuilder state, directions, distance caps, setup-type map, pickTarget. | MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage | 2026-10-04 |
| src/test/java/datafeed/StateCodeEmitterTest.java | test | T037: StateCodeEmitter state table, five signal helpers, trigger names, UTC helpers; never connects or writes. | MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage | 2026-10-04 |
| MyTradingSys/tests/test_quad_classify.py | test | Promoted from runtime/*.new (T037): quad_classify six canonical states from sourced documents. | MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage | 2026-10-04 |
| MyTradingSys/tests/test_regime_classifier.py | test | Promoted from runtime/*.new (T037): regime votes and 3-cycle debounce from TREND_REGIME_DETECTOR_SPEC. | MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage | 2026-10-04 |
| MyTradingSys/tests/test_t037_quad_classify.py | test | T037: quad_classify wiring (None returns, snapshot discovery, one-line output); thresholds not pinned. | MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage | 2026-10-04 |
| MyTradingSys/tests/test_t037_regime_classifier.py | test | T037: regime_classifier votes and main() state-file cycle; MEDIUM/HIGH streaks not pinned. | MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage | 2026-10-04 |
| MyTradingSys/tests/test_t037_update_market_state.py | test | T037: update_market_state atomic write, latest-snapshot pick, main() wiring with stubbed mts_math. | MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage | 2026-10-04 |
| MyTradingSys/system/sessions/MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage.md | session | Session record: T037 test coverage for 8 engine files + Build-Check mvn test tier. | MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage | 2026-10-04 |
| MyTradingSys/system/sessions/MTS-2026-10-04-1105Z-APP-BLD-b129-harness.md | session | Session record: B129 AST-based extraction fix. | MTS-2026-10-04-1105Z-APP-BLD-b129-harness | 2026-10-04 |
| MyTradingSys/items/B130_execution_tests_not_gated.md | doc | Bug B130: execution/tests not collected by run_all_tests.py; phase 3 deribit tests invisible to the gate. | MTS-2026-10-04-0916Z-DSA-COO | 2026-10-04 |
| MyTradingSys/system/sessions/MTS-2026-10-04-1120Z-APP-BLD-b104-prompt-gate.md | session | Session record: B104 prompt_check.ps1 blocking + checks 6-10. | MTS-2026-10-04-1120Z-APP-BLD-b104-prompt-gate | 2026-10-04 |
| MyTradingSys/research/testnet_status/T050_PHASE3_2026-10-04.md | testnet | T050 phase 3 live exit criterion: T1a limit place/list/cancel, T1b market sell + close_position, both PASS on test.deribit.com. | MTS-2026-10-04-1141Z-DSA-COO-t050-phase3-live | 2026-10-04 |
| MyTradingSys/system/sessions/MTS-2026-10-04-1141Z-DSA-COO-t050-phase3-live.md | session | Session record: T050 phase 3 live testnet run. | MTS-2026-10-04-1141Z-DSA-COO-t050-phase3-live | 2026-10-04 |
| MyTradingSys/items/B131_tom_pool_skew_upstream.md | doc | Bug B131: Tom proof-5 candidate pool 2:1 short at SetupCandidatesBuilder, upstream of proof-direction. | MTS-2026-10-04-0916Z-DSA-COO | 2026-10-04 |
| MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md | research | LY1 provenance audit of non-core layer parameters (rsi, cryptocred, positioning, session, turn_of_candle, tick, consensus): 81 rows, 17 SOURCED, 34 CONCEPT-ONLY, 30 NO-SOURCE; no sourced exit in any layer; REJECT list and 11 open questions. | MTS-2026-10-04-1230Z-APP-BLD-ly1-layer-provenance | 2026-10-04 |
| MyTradingSys/items/B132_dsa_does_quick_wins.md | doc | Bug B132: DSA dispatches work it can do itself; codify DSA-does list + CC prompt names DSA unblock work. | MTS-2026-10-04-0916Z-DSA-COO | 2026-10-04 |
| MyTradingSys/tests/test_run_all_tests_paths.py | test | B130 guard: PYTEST_LAYER_PATHS in scripts/dev/run_all_tests.py must include MyTradingSys/execution/tests. | MTS-2026-10-04-0916Z-DSA-COO | 2026-10-04 |
| MyTradingSys/items/B133_dsa_default_cli_over_app.md | doc | Bug B133: DSA defaults to CLI or ships the mts go launch block when the App is the correct surface; policy at d36ec97. | MTS-2026-10-04-1325Z-DSA-COO | 2026-10-04 |
| MyTradingSys/items/B134_compose_surface_marker.md | doc | Bug B134: compose() emits prose surface line, not the SURFACE marker prompt_check check 13 requires. | MTS-2026-10-04-1325Z-DSA-COO | 2026-10-05 |
| MyTradingSys/items/B135_b131_threshold_recheck.md | doc | Bug B135: B131 follow-up, ps1 proof-count thresholds and allshorts parity re-run. | MTS-2026-10-04-1325Z-DSA-COO | 2026-10-05 |
| MyTradingSys/research/OPERATOR_ASKS_2026-10-05.md | research | Operator asks 1-5 (stop-run/OI flush, TF confirmation, LazyBear, My charts, alerts), chart cross-check, ordered Desktop/Cloud task list. | MTS-2026-10-05-1500Z-APP-ANA-operator-asks | 2026-10-05 |
| MyTradingSys/items/B136_oi_endpoint_path.md | doc | Bug B136: /futures/data endpoints broken since 09-24, OI fail-open. | MTS-2026-10-05-1500Z-APP-ANA-operator-asks | 2026-10-05 |
| MyTradingSys/items/T063_stop_run_oi_flush_signature.md | doc | T063: sweep + OI flush + CVD event study (operator obs). | MTS-2026-10-05-1500Z-APP-ANA-operator-asks | 2026-10-05 |
| MyTradingSys/items/T064_timeframe_selection_confirmation.md | doc | T064: TF choice + confirmation, Tom/Fabio extract. | MTS-2026-10-05-1500Z-APP-ANA-operator-asks | 2026-10-05 |
| MyTradingSys/items/T065_lazybear_survey.md | doc | T065: LazyBear survey + shortlist. | MTS-2026-10-05-1500Z-APP-ANA-operator-asks | 2026-10-05 |
| MyTradingSys/items/T066_my_charts_module.md | doc | T066: My charts module (operator TradingView layouts). | MTS-2026-10-05-1500Z-APP-ANA-operator-asks | 2026-10-05 |
| MyTradingSys/items/T067_alert_improvements.md | doc | T067: alert improvements incl. buy detection. | MTS-2026-10-05-1500Z-APP-ANA-operator-asks | 2026-10-05 |
| MyTradingSys/research/T064_TF_CONFIRMATION_EXTRACT.md | doc | T064: 35 Tom+Fabio quotes (TF/confirmation/stop-run/retrace). | MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch | 2026-10-05 |
| MyTradingSys/research/T065_LAZYBEAR_SURVEY.md | doc | T065: LazyBear survey, shortlist of 4. | MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch | 2026-10-05 |
| MyTradingSys/research/T063_STOP_RUN_OI_FLUSH.md | doc | T063: pre-reg + arm A0 result. | MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch | 2026-10-05 |
| MyTradingSys/research/REPLAY_2026-10-04_05.md | doc | G1/M1/M2 partial document-based replay 10-04/05. | MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch | 2026-10-05 |
| MyTradingSys/research/T067_ALERT_SPEC.md | doc | T067: sweep+OI + zone absorption alert spec. | MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch | 2026-10-05 |
| MyTradingSys/research/t063_event_study.py | tool | T063 event-study harness. | MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch | 2026-10-05 |
| MyTradingSys/research/replay_2026_10_04_05.py | tool | 10-04/05 candidate replay tool. | MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch | 2026-10-05 |
| MyTradingSys/research/t067/test_alert_patterns.py.spec | tool | T067 failing-first test spec, 29 tests. | MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch | 2026-10-05 |
| MyTradingSys/runtime/oi_live/oi_recorder.py | tool | 1m OI sampler + 5m backfill writer. | MTS-2026-10-05-1600Z-APP-BLD-desktop-haiku-batch | 2026-10-05 |
| MyTradingSys/runtime/oi_live/oi_1m.csv | data | Live 1m OI samples. | MTS-2026-10-05-1600Z-APP-BLD-desktop-haiku-batch | 2026-10-05 |
| MyTradingSys/runtime/oi_live/oi_5m_30d.csv | data | 30d 5m OI backfill (8,640 rows). | MTS-2026-10-05-1600Z-APP-BLD-desktop-haiku-batch | 2026-10-05 |
| scripts/live/feed-watchdog.ps1 | tool | D4: snapshot+state_code age logger; starts htf_context_live if absent. | MTS-2026-10-05-1650Z-APP-BLD-desktop-sonnet-finish | 2026-10-05 |
| my_charts/README.md | doc | T066: read operator TradingView layouts via Claude in Chrome. | MTS-2026-10-05-1650Z-APP-BLD-desktop-sonnet-finish | 2026-10-05 |
| runtime_data/feed_watchdog.log | data | D4 watchdog output. | MTS-2026-10-05-1650Z-APP-BLD-desktop-sonnet-finish | 2026-10-05 |
| MyTradingSys/research/TOM_FABIO_STORY_2026-10-05.md | doc | Tom+Fabio story; TOM-091 citation fix at L117,L175. | MTS-2026-10-05-1650Z-APP-BLD-desktop-sonnet-finish | 2026-10-05 |
| MyTradingSys/queue/cbp_adapter.py | code | CBP -> MTS adapter: validate pending.json, write CANDIDATE_UNTESTED rows (B139). | MTS-2026-10-06-2122Z-APP-COO-registry-fix | 2026-10-06 |
| MyTradingSys/queue/cbp_contract_v1.schema.json | config | CBP queue contract v1 schema (B139). | MTS-2026-10-06-2122Z-APP-COO-registry-fix | 2026-10-06 |
| MyTradingSys/tests/test_cbp_adapter.py | test | cbp_adapter validation and ingest tests (B139). | MTS-2026-10-06-2122Z-APP-COO-registry-fix | 2026-10-06 |
| MyTradingSys/items/B139_cbp_adapter.md | doc | B139 item doc: CBP adapter registration and real-queue run. | MTS-2026-10-06-2122Z-APP-COO-registry-fix | 2026-10-06 |
| MyTradingSys/system/sessions/MTS-2026-10-06-2122Z-APP-COO-registry-fix.md | doc | Session record: registry and doc corrections. | MTS-2026-10-06-2122Z-APP-COO-registry-fix | 2026-10-06 |
| MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md | research | CryptoCred setups rerun with resting-limit fill: all three FAIL; b3dbe74 PASS was fill bias. | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md | research | T055 C1/C2 rerun on all 7305 funding records: both FAIL; 10-06 reruns superseded. | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md | research | Tom core BT rerun on current Java (run tom_core_20261007): live rule 0 signals, no edge. | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06_full.md | research | Full generated Tom core BT report of the rerun (306 lines). | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/research/AUDIT_CLOSEOUT_2026-10-07.md | research | Closeout matrix: audit findings validated, why-stuck, operator decisions. | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/tests/test_b127_fetch_archive_funding.py | test | fetch_binance_archive funding URL, plan, checksum tests (B127 B103-F2). | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/tests/test_b127_declutter_backups.py | test | declutter_backups move-not-delete, manifest, exclude tests (B127). | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/tests/test_b127_fabio_v3_isolation.py | test | Fabio v3 package import isolation (B127 TC-TOP5-2). | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/tests/test_b128_cc_range_noise_filter.py | test | classify_msb filter_range_noise tests (B128 TC-W1-6). | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/items/B142_extrasetupbuilder_1m_stop_unsourced.md | doc | B142 item doc: ExtraSetupBuilder 1m stop NO-SOURCE. | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md | doc | B143 item doc: CryptoCred 0.1 pct stop and 1.5R target NO-SOURCE. | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/items/B144_exhaustion_proxy_unsourced_params.md | doc | B144 item doc: exhaustion proxy 2x/240 NO-SOURCE (SCREENER). | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/system/sessions/MTS-2026-10-07-1002Z-APP-BLD-research-closeout.md | doc | Session record: research closeout. | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-07 |
| MyTradingSys/items/B145_cc_range_noise_live_neutrality.md | doc | B145 item doc: stopped-loop neutrality test before filter_range_noise goes live. | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-08 |
| _archive/2026-10-15-scripts-dev/diff_tom_rows.py | tool | Month-by-month verdict-count diff of two Tom core BT row directories (read-only). | MTS-2026-10-07-1002Z-APP-BLD-research-closeout | 2026-10-08 |
| scripts/dev/bridge_selftest.ps1 | tool | Direct-mode end-to-end probe run through AIBridge: write/read/delete, sync.py news, paste pipeline parse, python; prints SELFTEST line, denial probes, and a numbered big-output block that measures the output cap. | MTS-2026-10-08-0806Z-APP-BLD-dsa-direct-mode | 2026-10-08 |
| MyTradingSys/tests/test_dsa_direct_mode.py | test | Guards DSA direct mode: prompt section 0, no split rule, paste and news pipeline intact, sync.py news works in a live tree, size alarms above 250 KB, lane doc contract. | MTS-2026-10-08-0806Z-APP-BLD-dsa-direct-mode | 2026-10-08 |
| scripts/dev/dsa_eval.py | tool | Scores DSA chat replies against 12 fixed failure scenarios (sheet/template/score); history in research/dsa_eval_history.jsonl. | MTS-2026-10-09-slim-boot-dsa-eval | 2026-10-09 |
| scripts/dev/dsa_eval_scenarios.py | tool | The 12 DSA eval scenarios from B083/B101/B104/B132/B133 and LESSONS, with good and bad fixture replies. | MTS-2026-10-09-slim-boot-dsa-eval | 2026-10-09 |
| MyTradingSys/tests/test_dsa_eval.py | test | Tests that every eval scenario's good reply passes and bad reply fails. | MTS-2026-10-09-slim-boot-dsa-eval | 2026-10-09 |

| MyTradingSys/research/PRE_REG_OI_DIVERGENCE_2026-10-10.md | doc | Pre-registration for OI divergence, rule fixed before data, result appended (NO REPLICATION). | MTS-2026-10-10-1608Z-DSA-COO | 2026-10-10 |
| MyTradingSys/research/oi_divergence_v2_2026-10-10.py | tool | Pre-registered OI divergence run: 15m bars, metrics OI, cost wiring, regime labels, 3-fold walk-forward. | MTS-2026-10-10-1608Z-DSA-COO | 2026-10-10 |
| MyTradingSys/research/OI_DIVERGENCE_V2_2026-10-10.md | doc | Result: 2350 events, 24 cells, all negative after costs, NO REPLICATION. | MTS-2026-10-10-1608Z-DSA-COO | 2026-10-10 |
| MyTradingSys/research/OI_DIVERGENCE_2026-10-10.md | doc | First OI divergence pass (state table, no cost model), kept as record of the failed method. | MTS-2026-10-10-1608Z-DSA-COO | 2026-10-10 |
| MyTradingSys/research/OI_EVENT_STUDY_2026-10-10.md | doc | Second OI pass (drift-subtracted event study), kept as record. | MTS-2026-10-10-1608Z-DSA-COO | 2026-10-10 |
| MyTradingSys/items/B171_snapshot_oi_quantized.md | doc | B171 item doc: snapshot OI is a 0.01 gauge; full-precision series unread; Claude decides consumer or display-only. | MTS-2026-10-10-1608Z-DSA-COO | 2026-10-10 |
| MyTradingSys/research/PRE_REG_VPIN_PROXY_2026-10-10.md | doc | Pre-registration for the VPIN proxy, result and day-clustered confirmation appended (PASS). | MTS-2026-10-10-1608Z-DSA-COO | 2026-10-10 |
| MyTradingSys/research/vpin_proxy_2026-10-10.py | tool | VPIN proxy: 1m kline volume buckets, taker-buy imbalance, rolling toxicity, spike conditional test. | MTS-2026-10-10-1608Z-DSA-COO | 2026-10-10 |
| MyTradingSys/research/VPIN_PROXY_2026-10-10.md | doc | Result: 2530 spikes; spike vs baseline abs 1h +0.185 pct, adverse 60 bars +0.315 pct; PASS as risk gate. | MTS-2026-10-10-1608Z-DSA-COO | 2026-10-10 |
| MyTradingSys/research/vpin_dayclustered_2026-10-10.py | tool | Day-clustered t rerun on the VPIN spikes (removes the Welch-only deviation). | MTS-2026-10-10-1608Z-DSA-COO | 2026-10-10 |
| MyTradingSys/research/VPIN_DAYCLUSTERED_2026-10-10.md | doc | Day-clustered t: abs 1h +7.14, abs 4h +4.97, adverse +7.02; VPIN proxy pass holds. | MTS-2026-10-10-1608Z-DSA-COO | 2026-10-10 |
| scripts/dev/dsa.py | tool | One-call helper CLI for DSA over AIBridge: host (this machine's facts + BUILD_REPORT host match), boot, begin (own worktree + claim), put/edit (safe file writes from stdin), commit (Result + MTS-Session, no mirror), end (release + remove worktree). | MTS-2026-10-14-1530Z-NB-dsatool | 2026-10-14 |
| scripts/dev/test_dsa.py | test | Tests dsa.py against temp bare-origin repos: put/edit EOL and refusals, commit exclusions and live-tree refusal, begin/end worktree + claim, host build_report match. Gate step 3ds. | MTS-2026-10-14-1530Z-NB-dsatool | 2026-10-14 |
