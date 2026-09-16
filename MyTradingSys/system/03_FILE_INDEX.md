# FILE: 03_FILE_INDEX.md
# READ ORDER: 6 of 8
# PURPOSE: Hierarchical index of all active files in MyTradingSys/
# LAST UPDATED: 2026-09-13
# SIZE: ~10.6KB
# NEXT FILE: 04_PER_JSON_GUIDE.md
# PREVIOUS FILE: 02b_DECISIONS_LOG.md
# ---

# FILE INDEX вЂ” MTS Project v4.2.0-p5
# Purpose: Authoritative index of live files. Hierarchical structure.
# NOTE: Files in archive/ and *.old files are EXCLUDED from active counts.
# See 05_NORMS.md for conventions.

---

## SYSTEM/ вЂ” AI Session Orchestration

| File | Size | Purpose |
|------|------|---------|
| 00_START_HERE.md | ~21KB | Methodology reference. Entry point deprecated вЂ” see DSA_SESSION_PROMPT.md |
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

## METHODOLOGY/ вЂ” Research Protocols & Domain Theory

| File | Size | Purpose |
|------|------|---------|
| playbook.md | ~27KB | Research gate (Part I), extraction rules (Part J), archive protocol (Part K), architecture (Part L) |
| extraction.md | ~5.5KB | Extraction lifecycle: 4 phases + Safeguards 2, 3. TRIGGER: new transcript |
| crypto_adaptations.md | ~5KB | Tom-rule vs crypto-hack classification |
| grounded_theory_protocol.md | ~9KB | Original 4-phase workflow + 5 Safeguards. SUPERSEDED вЂ” kept for provenance |
| reflexivity_log.md | ~5.5KB | Reflexive discipline log (Safeguard 4) |

## MTS/CONDITIONS/ вЂ” Full Rule Documentation

| File | Size | Purpose |
|------|------|---------|
| market_state_rules.md | ~16.5KB | Balance/trend taxonomy, state workflow, state->setup matrix |
| zone_identification_rules.md | ~28KB | 9 zone types, workflow, negative rules |
| setup_type_rules.md | ~34KB | 4 execution modes, idea+proof framework, trader DNA |
| proof_requirements_formatted.md | ~16.5KB | 14 proof categories, cross-cutting layer |
| risk_protocol.md | ~27KB | Stops, sizing, R:R, targets, re-entry, drawdown |
| entry_timing_triggers.md | ~35KB | Trigger taxonomy, 4 modes, 4 tiers, 10 negative rules |
| session_timing_rules.md | ~26KB | Session-specific timing, volatility rankings |

## MTS/CARDS/ вЂ” Trading Cards & Templates (20 files)

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

## MTS/RUNTIME/ вЂ” Decision Engine + State

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
| v4.2.0_optimization_spec.md | ~11KB | REFERENCE вЂ” design doc, not loaded at runtime |

## MTS/RESEARCH/ вЂ” Active Research (15 files)

| File | Size | Purpose |
|------|------|---------|
| apparatus_fixes.md | ~5KB | Apparatus fix log + open items |
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

## MTS/TESTS/ вЂ” Test System (9 files)

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

## DATA/ вЂ” Schemas, Task Specs (MyTradingSys/data/)

| File | Size | Purpose |
|------|------|---------|
| data_schema_v1.2.0.md | ~32KB | JSON schema documentation |
| dsa_task_012_setup_candidates.md | ~23KB | DSA_TASK_012 spec |
| sample_btc_snapshot.json | ~6KB | Sample JSON snapshot |
| test_snapshot_v4.2.0-p2_validation.json | ~6KB | Validation snapshot |
| data_state_document.md | ~11KB | Data inventory + gaps |
| DIRECTORY_AUDIT.md | ~2.4KB | Data directory audit |

## EXTRACTS/FRESH/ вЂ” 50 Tom Transcript Extractions

All files: extract_[VIDEOID]_fresh.md. Count: 50.

## MTS/EXTRACTS/ вЂ” Cross-Trader Extracts (8 files)

| Folder | Files | Status |
|--------|-------|--------|
| cryptocred/extracted/ | 5 extracts | PURE |
| the_flow_horse/extracted/ | 3 extracts | PURE |

## MTS/ARCHIVE/ вЂ” Superseded Research (14 files)

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

## ARCHIVE/ (top-level) вЂ” Migration Cleanup

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

## RUNTIME DATA (BinanceDataFeed/data/)

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
| data/ | 6 |
| extracts/fresh/ | 50 |
| mts/extracts/ | 8 |
| mts/archive/ | 14 |
| archive/cleanup-2026-09-13/ | 12 |
| Canonical path | C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\ |

---
# END
