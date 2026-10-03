# FILE: 03_FILE_INDEX.md
# READ ORDER: 6 of 8
# PURPOSE: Hierarchical index of all active files in MyTradingSys/
# LAST UPDATED: 2026-10-03
# SIZE: ~41.5KB
# NEXT FILE: 04_PER_JSON_GUIDE.md
# PREVIOUS FILE: 02b_DECISIONS_LOG.md
# ---

# FILE INDEX - MTS Project v4.2.0-p5
# Purpose: Authoritative index of live files. Hierarchical structure.
# NOTE: Files in archive/ and *.old files are EXCLUDED from active counts.
# See 05_NORMS.md for conventions.

---

## SYSTEM/ - AI Session Orchestration

| File | Size | Purpose |
|------|------|---------|
| 00_START_HERE.md | ~21KB | Methodology reference. Entry point deprecated - see DSA_SESSION_PROMPT.md |
| 01_AI_BEHAVIOR.md | ~34KB | Behavior rules, mistake history, Section 14 JSON workflow, Rules 31-36 |
| 02a_CURRENT_STATUS.md | ~42KB | System status, component health, operational parameters |
| 02b_DECISIONS_LOG.md | ~39KB | Append-only decision history |
| 02c_SESSION_END_SIGNOFF.md | ~18KB | Historical session end sign-offs (append-only) |
| 03_FILE_INDEX.md | ~10.4KB | This file |
| 04_NEXT_SESSION_PROMPT.md | ~19KB | Current session handoff prompt |
| 04_PER_JSON_GUIDE.md | ~2.4KB | Per-JSON load order + abbreviations |
| 05_NORMS.md | ~3KB | Folder conventions, naming rules, archival rules |
| 06_SESSION_END_CHECKLIST.md | ~7KB | Mandatory validation checklist before closing session |
| COMPILED_DECISIONS.md | ~11KB | Single-page reference of all 56 system decisions |
| session_end_logs.md | ~49KB | Archived session end logs (append-only history) |
| session_handoff_btcusdt_mts_2026-09-07.md | ~13KB | Session handoff document (historical) |

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
| MyTradingSys/system/CLOUD_INBOX.md | inbox | Tasks for Cloud sessions (Cloud sees only pushed git refs). Desktop appends, commits, pushes. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
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
| scripts/dev/testnet_canary.py | tool | Read-only liveness + new-code canary for the testnet stack: processes, loop/log freshness, unconsumed Tom alerts, brake files (existence only), commits on live/Tom/Fabio paths; --run-gates; prints RESTART NEEDED (supervisor only). Exit 0/1/2 = GREEN/WARN/RED -> research/testnet_status/CANARY_<date>.md. Never restarts. | MTS-2026-10-02-1050Z-CLI-SUP-direction | 2026-10-02 |
| scripts/dev/test_testnet_canary.py | test | 20 pytest cases for testnet_canary (fail-closed proc query, brake files never opened, restart-needed via temp git repo). | MTS-2026-10-02-1050Z-CLI-SUP-direction | 2026-10-02 |
| MyTradingSys/research/DIRECTION_REVIEW_2026-10-02.md | report | Direction review: testnet down, Tom/Fabio 0 trades, NO-SOURCE gates still live, re-ordered priorities P0-P8, 4 operator decisions. | MTS-2026-10-02-1050Z-CLI-SUP-direction | 2026-10-02 |
| MyTradingSys/research/fast_track_2026-09-27/PROVENANCE_AUDIT_TOM.md | research | Provenance audit of the Tom core path (74 rows): 2 TOM-SOURCED, 33 concept-only, 36 NO-SOURCE, 3 plumbing; 2:1 net miscited to qLnQan0KGmQ; safety rules X1-X8 listed unjudged. | MTS-2026-09-30-1005Z-CLD-ANA-connected-system | 2026-09-30 |
| MyTradingSys/research/AUDIT_REVIEW_2026-10-01.md | review | DSA review of the Tom/Fabio provenance work: 10 sections, verdict tally, impact ranks, method gaps (no pre-registration, single reader, no falsification), backtest-stat defects (H1-H2, M7-M9), six ranked alternatives, scientific-method gap list. | MTS-2026-10-01-1431Z-DSA-COO | 2026-10-01 |
| MyTradingSys/research/REVALIDATION_REQUEST_2026-10-01.md | review | DSA revalidation request for Claude: 10 scientific methods (DSR, PBO, CPCV, White/Hansen SPA, Romano-Wolf, BH-FDR, stationary bootstrap, kappa, purged CV, pre-registration) with proof paths, source citations, and what to check. | MTS-2026-10-01-1431Z-DSA-COO | 2026-10-01 |
| MyTradingSys/research/HANDOFF_FOR_CLAUDE_2026-10-01.md | review | Handoff to Claude: 6 second-iteration findings (single-reader count, counterfactual gap, support-not-falsification search, section 10 omissions, no Fabio audit, defective adoption gate) + 8 work items W1-W8 with input/task/output/gate. | MTS-2026-10-01-1431Z-DSA-COO | 2026-10-01 |
| MyTradingSys/system/AIBRIDGE_LANE.md | system | One-page lane contract: what AIBridge is, allowed MTS calls over loopback, caps, hard limits (no MTS repo writes), how MTS uses it with DSA, tuning surface is MTS-side only. | MTS-2026-10-01-1431Z-DSA-COO | 2026-10-01 |
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
| scripts/dev/alert_rate_check.py | tool | Alert-rate check. Updated 2026-10-02: TF_MIN gains 3m and 1d for the RSI observation block. | MTS-2026-10-02-0930Z-CLI-BLD-tfmap | 2026-10-02 |
| MyTradingSys/execution/auto_trader.py | execution | Layer/tom alert orchestrator. Updated 2026-10-02: TF_SECONDS gains 3m (1d already present). Live-path; loop was down at promotion. | MTS-2026-10-02-0930Z-CLI-BLD-tfmap | 2026-10-02 |
| MyTradingSys/research/CC_PROMPT_FABIO_V3_CORE_2026-10-02.md | prompt | CC brief: finish Fabio v3 core. Review staged, write engine.py, 7 test files, README. Cap 3 subagents, batch 1, Ultracode off. | MTS-2026-10-01-1755Z-DSA-COO | 2026-10-02 |
| MyTradingSys/research/CL_PROMPT_FABIO_V3_CORE_2026-10-02.md | prompt | CL brief: Fabio v3 engine.py only. 1 percent budget, no subagents, save-work checkpoints, stop-early rules. | MTS-2026-10-01-1755Z-DSA-COO | 2026-10-02 |
| MyTradingSys/research/CL_PROMPT_FABIO_V3_TESTS_2026-10-02.md | prompt | CL brief: one test file per session (test_signals.py.new). Fail-first proof, one pytest run, no git. | MTS-2026-10-01-1755Z-DSA-COO | 2026-10-02 |
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
