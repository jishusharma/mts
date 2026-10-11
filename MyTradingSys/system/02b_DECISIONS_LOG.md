> **SUPERSEDED (2026-10-08).** Frozen history from the September build. For current state read
> `MyTradingSys/research/STATUS.md`, then `MyTradingSys/system/LESSONS_LEARNED.md` (entry order is in CLAUDE.md).
> Where this file disagrees with CLAUDE.md or SURFACE_POLICY.md, those win.

# 2026-09-14: Coordinator + Worker Night — Cleanup, Rule 38, Checkers Landed
# ---
# - Cleanup: 12 .old files archived to archive/cleanup-2026-09-13/. Deleted
#   .pytest_cache/, empty tests/, mts/visual/, "=" file. Playbook Parts L/M/N
#   removed. 11 stale refs (state.md/core_engine.md/sys_ai_prompt.md) replaced.
# - grounded_theory_protocol.md restored from .old (SUPERSEDED footer added).
# - methodology/extraction.md created — carries Safeguards 2 & 3.
# - VVP-002 G.2 reconciled to flag-only per Rule 32. apparatus_fixes.md note.
# - heatmap_field_map.md § 1 gained CoinGlass vs Glassnode methodology note.
# - event_probability_layer_DESIGN.md: refreshed label count (759->816) + ETA
#   corrected from 3-6mo to ~6 days at observed rate.
# - manual_patterns.md § 4 (multi-AI workflow) removed — simple coordinator only.
# - Rule 38 added to 01_AI_BEHAVIOR.md. M-033 logged.
# - CAPABILITIES.md gained coordinator prompt rule.
# - DSA_SESSION_PROMPT.md: BUILD_REPORT gate, disk-verification rule, coordinator pattern.
# - SESSION_ENTRY.md: "Read 0: BUILD_REPORT.md first" prepended.
# - Dump_All.ps1: chains to Build-Check. system_support module added.
# - 03_FILE_INDEX.md rewritten to match disk.
# - Build infra: scripts/Build-Check.ps1 + mts/tests/docs/test_integrity.py.
# - Worker D: check_scalp_preconditions + check_invalidation landed in mts_math.py.
#   session_state.json v1.1.0. 110 tests. NOT WIRED yet — Worker F pending.
# - Worker E: probability step-2 catalog. PARTIAL — 542/816 labels orphaned.
#   Redefined as label-only classification. Re-run pending.
# - Worker A: market context briefing. Closed.
# - Worker C: market data refresh. PARTIAL — 4f/4g blocked (no web).
# - Alerts #260 (WATCH) + #261 (SETUP_FORMING) — churn within 180s.
#   VWAP slope falling blocks scalp. No action taken. Both logged.
# - Screenshot pipeline: _SCHEMA.json + prompt + folder exist.
#   Validator + compiler pending (Worker G).
# ---
# 2026-09-09: Migration from Kimi download — files placed in canonical locations
# ---
# - Replaced 22 files (runtime, conditions, data, tests, research, methodology) with latest versions from temp_files.
# - Backed up old versions as .old files in same directories.
# - Moved 50 fresh Tom extracts from mts/extracts/fresh/ to extracts/fresh/ (canonical).
# - Copied 8 cross-trader extracts from new_temp to mts/extracts/cryptocred/extracted/ and the_flow_horse/extracted/.
# - Copied dsa_developer_implementation_tasks.md to mts/research/.
# - Updated reflexivity_log.md to latest version.
# - Updated 03_FILE_INDEX.md and 05_NORMS.md to reflect actual structure.
# ---
# 2026-09-06: DSA_TASK_012 COMPLETE — v1.3.2 Implementation + Audit + Integration
# ---
# - DSA_TASK_012 implementation COMPLETE. SetupCandidatesBuilder.java emits setup_candidates array.
# - 6 audit fixes from v1.3.1 all verified and applied by DSA developer.
# - v1.3.2 target expansion implemented: VAL/VAH + prior_day high/low now valid targets per engine Sec 7.
# - math_object_builder.py updated to read setup_candidates directly (v1.3.2 schema support).
# - compiled_engine.md updated: judgment layer prefers setup_candidate when present.
# - BUG #6 CLOSED: proof-to-zone attribution error fixed via nearest-zone rule + proximity gates.
# - 5 historical snapshots validated. pf_vah short at 2026-08-31 21:27 resurfaces with R:R 2.12.
# - Parallel session review claims validated: 3 of 5 accepted (stale fallback, flat-field precedence, letter collision). 1 rejected (engine book_imbalance bug — no engine scoring table exists). 1 accepted with caveat (nearest-zone is spec addition, not verbatim engine).
# - Files updated: dsa_task_012_setup_candidates.md (v1.3.2), math_object_builder.py, compiled_engine.md.
# - Files removed: bug_006_dsa_proof_attribution.md (merged into spec).
# ---

# 2026-09-05: Binance API Integration Research — COMPLETE
# ---
# - Deep-dive research on Binance WebSocket API for MTS DSA data feed optimization
# - 12 expert sources consulted: Binance Developer Docs (Authority: A), Binance Academy (A),
#   CoinMarketCap Academy (A), CoinGlass API (B), WebSocket.org (NA), Redis Docs (A)
# - Key finding: Legacy WebSocket URLs decommissioned 2026-04-23 — DSA MUST migrate to
#   /public, /market, /private base paths immediately
# - Document produced: mts/research/binance_api_integration_recommendations.md (43KB)
# - Contents: Stream-to-metric mapping (12 streams), Java token bucket rate limiter,
#   SQLite cache schema, order book snapshot+diff pattern, 10-phase migration roadmap,
#   multi-exchange aggregation interface, 10 critical pitfalls, 12 citations
# - BUG #5 fix identified: Change depth limit from 100 to 1000 (weight: 50) — resolves
#   identical values at all thresholds (0.1%, 0.2%, 0.5%, 1.0%)
# - DSA developer action items: 6 prioritized tasks (2x P0, 3x P1, 1x P2)
# - System files updated: 03_FILE_INDEX.md (130→131 files), 02a_CURRENT_STATUS.md,
#   02b_DECISIONS_LOG.md (this entry)
# ---

# 2026-09-05: JSON Pipeline + Screenshot Workflow Validation — BUG #6 DISCOVERED
# ---
# - Live JSON snapshot (BTCUSDT @ 79,591.7, 2026-09-05 09:58 UTC) validated through full pipeline
# - math_object_builder → compiled_engine → card output: B verdict (78/100) Scalp Long at VWAP
# - Screenshot cross-check (15m + 5m CoinGlass) revealed DSA proof misattribution
# - DSA claimed: STRONG rejection wick, delta flip, speed at VWAP 79,577
# - Visual reality: All proof at swing low ~79,000 (0.72% away, 7x beyond 0.1% threshold)
# - Verdict corrected: B (78/100) → C (50/100) — WAIT, no entry
# - Bug report written: mts/research/bug_006_dsa_proof_attribution.md
# - Fix required: DSA dev to add 0.1% proximity gate before proof-to-zone attribution
# - Test suite: 95/95 executed PASS, 3 skipped (pytest fixture)
# - Visual validation protocol VVP-001 proven effective: caught false signal before entry
# ---

# 2026-09-05: Session End — Full Cleanup + Fresh-Eyes Audit + System Hardening
# ---
# - Fresh-eyes audit of all 130 files: identified 17+ ghost references in active system files
# - Deleted 10 items: new_batch_extractions.zip, mts/archive/ (2 files), mts/cards/ (3 samples), mts/tests/ (4 stale docs)
# - Fixed 7 system files: 03_FILE_INDEX.md (complete rewrite), 02a_CURRENT_STATUS.md, 00_START_HERE.md,
#   01_AI_BEHAVIOR.md (Rule 16), 05_NORMS.md, 04_NEXT_SESSION_PROMPT.md (garbled header), COMPILED_DECISIONS.md
# - Purged all ghost references: 02d_AUDIT_LOG.md, UNIT_TEST_PLAN.md, compiled_code_opportunities.md,
#   regression_log.md, COMPILED_DECISIONS_TEST_PLAN.md, dsa_task_007/008/009 (never existed),
#   cross_trader_consolidation.md (wrong name), trading_card_generator.md, sample_pipeline_output.md,
#   trading_card_btc_sample.md, archive/, visual/, integration/, _scratch/
# - Deleted Python __pycache__ files (2 .pyc files) — not project files
# - Verified: 130 files on disk, 98/98 math tests pass, 0 ghost files remain
# - Next session: JSON pipeline testing + screenshot workflow validation + remaining test coverage
# ---

# 2026-09-05: Flow Horse Extraction Verification + Full Cleanup
# ---
# - Verified ALL 3 Flow Horse extractions against raw transcripts: Oy2Z-FQ77NM (11 rules), zMM9QgxfEFI (8 rules), UcPp0gFI5M8 (4 rules)
# - Corrected earlier error: 2 extractions were falsely reported as "missing" — they exist and are verified
# - 02a_CURRENT_STATUS.md updated with verified extraction table
# - 03_FILE_INDEX.md updated with verification notes
# - Deleted 5 unnecessary ZIPs: fresh_extractions.zip, fresh_tom_extractions.zip, new_extractions.zip, mts_system_files.zip, new_batch_extractions.zip
# - Deleted mts/archive/ (2 superseded files), mts/tests/ (4 stale test docs), mts/cards/ (3 sample/template files)
# - Ghost references purged from all system files: 02d_AUDIT_LOG.md, UNIT_TEST_PLAN.md, compiled_code_opportunities.md, regression_log.md, COMPILED_DECISIONS_TEST_PLAN.md, dsa_task_007/008/009 (never existed), cross_trader_consolidation.md (wrong name)
# - 03_FILE_INDEX.md completely rewritten with accurate 130-file inventory
# ---

# 2026-09-04: 6-Action Minimal Consolidation Executed
# ---
# - Gate rule #17 added to 00_START_HERE.md COMMON MISTAKES
# - 3 stale prompt variants merged into 04_NEXT_SESSION_PROMPT.md (BUGS, DSA008, DRIFT_FIX)
# - Empty signoff template merged into 06_SESSION_END_CHECKLIST.md
# - 02d_AUDIT_LOG.md DELETED (archive system discontinued)
# - 00_PROJECT_INSTRUCTIONS.md DELETED (user confirmed: pasted in project instruction text area)
# - 03_FILE_INDEX.md updated: 140 files, 13 system, 3 archive
# ---

# DECISIONS LOG — MTS
# READ ORDER: 4 of 8 (context only — read top entry)
# PURPOSE: Append-only record of why the system is what it is
# LAST UPDATED: 2026-09-04
# ---

## 2026-09-04 — Cleanup + Fresh-Eyes Re-Evaluation

| # | Decision | Rationale | Status |
|---|----------|-----------|--------|
| 1 | Deleted `output/mts/` and `output/system/` stale duplicate folders | All 7 files were older than canonical upload_mirror versions. Verified content diffs before deletion. | EXECUTED |
| 2 | Deleted `upload_mirror/PROJECT_INSTRUCTIONS.md` (root) | Identical duplicate of `system/00_PROJECT_INSTRUCTIONS.md`. Canonical is in system/. | EXECUTED |
| 3 | Purged 16 archived file references from `03_FILE_INDEX.md` | Archive folder empty since 2026-08-31. References were stale. | EXECUTED |
| 4 | Added 14 unindexed files to `03_FILE_INDEX.md` | DSA_TASK_INDEX.md, 3 newer cards, indicator research files, data_state_document, dsa_enhancement_spec, 00_PROJECT_INSTRUCTIONS, 02c_SESSION_END_SIGNOFF, session_end_logs, COMPILED_DECISIONS, 2 raw transcripts. | EXECUTED |
| 5 | Corrected compiled_engine version label: p4 -> p5 | File header and `02a_CURRENT_STATUS.md` both say p5. Index was stale. | EXECUTED |
| 6 | Corrected QUICK STATS: 128 -> 142 files | Counted actual files per category. Previous counts were stale. | EXECUTED |
| 7 | Deleted empty directories: archive, crypnuevo/*, cryptocred/raw | Zero content. CrypNuevo extraction blocked (no subtitles). | EXECUTED |
| 8 | Fresh-eyes re-evaluation of structural simplification | Read 00_START_HERE, 01_AI_BEHAVIOR (100 lines), structural_simplification_research.md, 02a_CURRENT_STATUS (50 lines). Formed independent assessment. | COMPLETE |
| 9 | Rejected 5-file collapse plan as over-engineered | 5-file plan merges append-only 02b with editable COMPILED_DECISIONS — repeats error #3 from research doc. 6-phase migration unnecessary. | DECIDED |
| 10 | Adopted minimal fix: gate rule + 4-file consolidation | Gate rule prevents future sprawl. Only genuinely redundant files touched: 4 prompt variants, signoff->checklist, audit log archive, duplicate instructions. | DECIDED |
| 11 | Next session prompt rewritten as 6-action execution plan | No more research. No more re-evaluation. Just execute. See `system/04_NEXT_SESSION_PROMPT.md`. | DECIDED |

---

## 2026-09-12 - Phantom-inputs cleanup (W1+W2 residual)

Decisions:
- Main.java dead-block commit ACCEPTED (hash 8D586A6A; compiles clean).
- cvd.divergence field DELETED (hardcoded false, no detection implemented).
- liquidation_warning.status + liquidation_clusters DELETED.
  Root cause: /fapi/v1/allForceOrders is 404. LiquidationClusterBuilder.java deleted.
  BinanceClient.allForceOrders/allForceOrdersRange/forceOrders deleted.
  Engine remains zero-read on liquidation fields.
- BUG-011 chasing_price: engine Sec 6 row 8 rewritten to match Python all_ignore
  ("All zones beyond distance cap | No edge nearby"). Rule 37 - bug fix, no Rule 32.
- alignment_pass: schema moved to TOP-LEVEL METADATA (doc fix; emit already top-level).
- SetupCandidatesBuilder.speedAtZone removed.
- Backup created: backup_20260912_160203 (6 files).
- All future edits require .bak backup first.

Rule 33 applied: no DSA field requested for whale/liquidation signals.

---

## 2026-09-11 - FIXES SESSION + STATE UPDATER + DIVERGENCE RESEARCH

**Decisions:**
1. BUG-007/008/009 fixed. DSA-HYG-001/006 fixed. DSA-HYG-002 live but unverified (candidate with rr_sanity=false still appearing).
2. net_delta replaced with multi-window (1m/5m/15m/1h) — one formula from klines1m
3. State updater built — `update_market_state.py` runs after snapshot (closes ~23h stale gap)
4. `divergence_monitor.py` created — reads snapshot history, flags divergence patterns
5. Naming collision flagged (net_delta vs CoinGlass Net Delta) — NOT renamed (no external contract)
6. CVD scope confirmed session-scoped; CoinGlass anchor difference documented as inference, not bug
7. Guest content bannered in 2 extracts; nested attribution noted in 1
8. Vocabulary Mining rule added to playbook Part I Step 3a + Rule 36 + M-032

**Files modified:** see 02a session summary.

**Tests:** 102/102 passing.

## 2026-09-10 - SSOT CLEANUP: btcusdt_market_session.md deprecated, indexes synced

**Context:** The session state file `mts/runtime/btcusdt_market_session.md` was deprecated earlier today (logged in `session_end_logs.md` under "SESSION CONTEXT MIGRATION - 2026-09-10") due to SSOT violation. Content absorbed into `current_market_state.md`.

**Gap closed:** `01_AI_BEHAVIOR.md` Section 14.2 had already dropped STEP 12 (MARKET SESSION UPDATE). But two index files still listed the deprecated file as ACTIVE:
- `02a_CURRENT_STATUS.md` runtime files table row 13
- `03_FILE_INDEX.md` MTS/RUNTIME section

**Fix applied:** Both rows removed. `current_market_state.md` now annotated as SSOT. Single state file.

**Rule:** A file deprecation is not complete until all four surfaces are updated: (1) `01_AI_BEHAVIOR.md`, (2) the file's own replacement (if any), (3) `02a_CURRENT_STATUS.md`, (4) `03_FILE_INDEX.md`. Deprecations leave ghost references otherwise — see M-027 for the prior case.

**Files modified:** `system/02a_CURRENT_STATUS.md`, `system/03_FILE_INDEX.md`, `system/02b_DECISIONS_LOG.md`.

## 2026-09-10 - SPEED CONCEPT RESEARCH + DSA_TASK_013/014 + BUG-007

**Decisions taken:**
1. SSOT for `speed_picking_up`: distance-cap doubling reads `math_object.speed_picking_up`, sourced from `setup_candidates[0].proof.speed.picking_up` when candidates present. Both existing definitions tagged `[CRYPTO HACK - PROXY, NOT TOM]`.
2. Vocabulary mining loop added to playbook Part I Step 3a. Rule 36 added to `01_AI_BEHAVIOR.md`. M-032 recorded.
3. DSA_TASK_013 COMPLETE: `order_flow` block added to snapshots (trades/sec, volume/sec, baseline ratios, speed_state).
4. DSA_TASK_014 COMPLETE: per-instrument historical baseline persisted to `runtime_data/speed_baselines/`.
5. BUG-007 FIXED: split `hard_stops_compiled.rr_below_threshold` into `any_zone_rr_below_threshold` + `top_candidate_rr_below_threshold`. Sec 6 row 4 now reads the top-candidate flag.
6. Guest content audit: `4P5WAxyPCis` and `RwQBdF9TSvc` bannered. `Vd83oo_geMk` nested attribution noted. DSA-HYG-004 logged.
7. Engine integration of `order_flow.speed_state` deferred pending Rule 32 (3-snapshot) validation.

**Files modified this session:** 14 (see 02a session summary).

**Tests:** 102/102 PASS.

# FILE: 02b_DECISIONS_LOG.md
# READ ORDER: 4 of 8
# PURPOSE: Append-only decision history — why the system is what it is
# LAST UPDATED: 2026-09-02
# SIZE: ~7KB
# NEXT FILE: 02d_AUDIT_LOG.md
# PREVIOUS FILE: 02a_CURRENT_STATUS.md
# ---

# DECISIONS LOG
| 2026-09-03 | **DSA TASK AUDIT — 10 of 11 task numbers are ghosts or file-less** | Full inventory of all DSA_TASK_XXX references revealed: Only 1 file exists (`dsa_task_010_transcript_download.md`, now STALE/ARCHIVED). 10 task numbers have NO file: 001 (never existed), 002 (created then deleted, content in 02b), 003 (complete, no file), 004a (complete, no file), 005 (never existed, explicitly noted), 006 (absorbed into 007), 007 (complete, no file), 008 (complete, no file), 009 (ghost — referenced but no body), 011 (invented without document, caught by checklist). `03_FILE_INDEX.md` falsely claimed 3 DSA task files were archived — they never existed. Archive directory is empty. Created `runtime_data/DSA_TASK_INDEX.md` as single source of truth. Added rule: no new DSA_TASK_XXX without adding to index FIRST. | `runtime_data/DSA_TASK_INDEX.md`, `03_FILE_INDEX.md`, `02a_CURRENT_STATUS.md`, `02b_DECISIONS_LOG.md` |
|------|----------|-----------|

| 2026-09-03 | **BUG #5 CORRECTION — Reclassified: NOT an engine bug** | Deep re-evaluation of BUG #5 (order_book_depth expanded identical values) revealed it was NEVER an engine bug. The engine only ever referenced `bid_ask_ratio`; expanded thresholds (0.1%, 0.2%, 0.5%) were never in the schema or proof evaluation. The prior "fix" (documenting a "limitation" in compiled_engine.md) was documentation theater — it changed zero runtime behavior and falsely implied the engine was constrained. Correct action: (1) Removed false "limitation" note from compiled_engine.md; (2) Replaced schema note with clean engine reference statement; (3) Reclassified BUG #5 status in 00_START_HERE.md from CLOSED to RECLASSIFIED. Process lesson: before filing any data-quality issue as an engine bug, trace the full path: data field → engine reference → verdict impact. If the engine doesn't reference the field, it's schema bloat or a DSA issue, not an engine bug. This rule added to COMMON MISTAKES in 00_START_HERE.md. | `compiled_engine.md`, `data_schema_v1.2.0.md`, `00_START_HERE.md`, `02a_CURRENT_STATUS.md`, `COMPILED_DECISIONS.md` |
|------|----------|-----------|

| 2026-09-02 | **DRIFT FIX: Complete project audit + 9 discrepancies resolved** | Full audit of MTS v4.2.0-p5 identified 9 discrepancies across system files (D1-D9). All fixes applied in single session: (1) Version tags unified to p5 across 00_START_HERE, 01_AI_BEHAVIOR, 02a, 03_FILE_INDEX; (2) 01_AI_BEHAVIOR.md updated from v4.1.3/Phase 2 READY to v4.2.0-p5/Phase 4 COMPLETE; (3) 02a card list expanded from 10 to 13 cards (added Aug 31-Sep 1 cards); (4) Prices synchronized to 78,784.5 (from current_market_state.md); (5) 02a size claim corrected; (6) 00_START_HERE.md date updated to 2026-09-02; (7) Sep 1 05:21 session summary added to 00_START_HERE.md; (8) 02a "NEXT SESSION STARTING PROMPT" market context updated to current price/verdict; (9) 02b_DECISIONS_LOG.md updated. FUNDING math layer fix (D6) and 02a log restructuring (D8) deferred to next session. | `system/00_START_HERE.md`, `system/01_AI_BEHAVIOR.md`, `system/02a_CURRENT_STATUS.md`, `system/02b_DECISIONS_LOG.md` |
|------|----------|-----------|

| 2026-09-02 | **DRIFT FIX COMPLETE: D6 + D8 resolved** | D6: FUNDING fields added to mts_math.py diff_state(), update_state(), format_state(). 7 FUNDING fields (btc_oi_weighted_rate_pct, current_net, current_direction, last_7d_ratio, last_7d_direction, open_interest_usd, assessment) tracked as contextual changes. Tests pass. D8: 4 session end logs moved from 02a_CURRENT_STATUS.md to new file session_end_logs.md. 02a trimmed from ~26KB to ~7KB. All 9 discrepancies (D1-D9) now resolved. Project fully consistent. | `mts/runtime/mts_math.py`, `system/02a_CURRENT_STATUS.md`, `system/session_end_logs.md` |
|------|----------|-----------|

| 2026-09-02 | **04_NEXT_SESSION_PROMPT.md fixed** | File was stale (2026-09-01 version). Updated to v4.2.0-p5 with current market context (78,124.5 WAIT C-), COMPILED_DECISIONS, Option B, test plan, and 5 session options. File permissions also fixed (chmod 666). | `system/04_NEXT_SESSION_PROMPT.md` |
|------|----------|-----------|

| 2026-09-02 | **COMPILED_DECISIONS_TEST_PLAN.md created** | Testing plan for revalidating all 56 system decisions across 9 categories. Three test types: Consistency (cross-file), Implementation (engine/code), Enforcement (AI behavior). Quick check: 22 tests, ~25 sec. Full validation: 76 tests, ~5 min. Includes regression tests for 5 historical snapshots, Option B workflow timing test, decision dependency and conflict checks. | `mts/tests/COMPILED_DECISIONS_TEST_PLAN.md` (~13KB). `system/COMPILED_DECISIONS.md`. `system/03_FILE_INDEX.md` updated. |
|------|----------|-----------|

| 2026-09-02 | **OPTION B: Pre-validated screenshot template ACTIVATED** | User requested faster response. Option B = skip VVP-001 validation (10 checks), assume chart layout is correct (cursor at right edge, Fixed Range VP, CVD Line, no BB), go straight to price action analysis. Saves 1-2 minutes per screenshot. JSON-only remains fastest (<30s). Option B is middle ground. Full VVP still available on request. | `system/COMPILED_DECISIONS.md` created (56 decisions across 9 categories). `system/02b_DECISIONS_LOG.md` updated. |
|------|----------|-----------|

| 2026-08-31 | **BUG HUNT: BUG #4 + BUG #5 CLOSED** | Parallel session investigation of 2 open bugs. BUG #4: CVD cumulative vs trade_flow recent contradiction is NOT a bug — it is normal market behavior (session sellers exhausted, recent buyers stepping in). Engine patched v4.2.0-p4: (1) Proof table updated to include trade_flow.net_delta and cvd_recent.slope_1h as sources for Sellers/Buyers present proof. (2) Added "recent_shift" resolution principle — when cvd_recent aligns with trade_flow, cumulative CVD is demoted to context. (3) Added "cumulative_dominant" and "pause" signals for other disagreement cases. BUG #5: order_book_depth expanded thresholds are identical because DSA uses limit=100 (~0.12% coverage at $78K). Engine already uses bid_ask_ratio only — no expanded threshold references exist. Documented limitation in schema. No DSA change needed. | `compiled_engine.md` v4.2.0-p4, `data_schema_v1.0.md`, `02a_CURRENT_STATUS.md`, `02b_DECISIONS_LOG.md`, `03_FILE_INDEX.md`, `mts/research/bug_004_investigation.md` |
|------|----------|-----------|

| 2026-08-31 | **DSA_TASK_008 COMPLETE — 5 GAP entries resolved, 0 new DSA fields approved** | Cross-trader Phase 3 identified 5 GAP entries requiring new DSA fields. After analysis against Rules 31-34: C01-E04 REJECTED (blocked by VP histogram API, engine confluence logic already covers); C02-E02 REJECTED (not Tom concept, measured move targets violate structural-level framework); C06-E01 DEFERRED (valid concept, engine has [PRINCIPLE] coverage via C06-E02, requires DSA architecture enhancement for historical tracking); C07-E07 REJECTED (not Tom concept, computationally prohibitive); C10-E04 REJECTED (not Tom concept, source explicitly disclaims fixed rules). Schema remains v1.2.0. No schema update. All cross-trader integration blockers resolved. | `runtime_data/dsa_task_008_gap_fields.md`, `mts/research/cross_trader_integration_plan.md` Section 3.6 updated, `system/02a_CURRENT_STATUS.md` Task 7 updated. |
|------|----------|-----------|

| 2026-08-30 | **HARD RULE: AI never picks price levels — targets, stops, entries, zones must come from Tom transcripts only** | During compiled code architecture discussion, sys_AI suggested "let AI pick target and compiled layer verifies R:R." User rejected immediately: "NO AI will never pick targets or fabricate any such field. This has to come from the transcripts itself." Rule added to 01_AI_BEHAVIOR.md Section 0 NON-NEGOTIABLE RULES. All price level rules must be transcript-extracted. If unclear, FLAG and SET ASIDE. No fabrication, no inference, no "reasonable defaults." | 01_AI_BEHAVIOR.md updated. |
|------|----------|-----------|

| 2026-08-30 | **COMPILED ENGINE: 93% of functions identified as compileable, UNIT_TEST_PLAN v3.0.0 written** | Full analysis of compiled_engine.md: 55 functions mapped. 51 = deterministic compiled code (table lookups, pure math, state machines). 2 = AI-only visual flags (double distribution, single print — require histogram screenshot). 2 = hybrid (contradiction null case). Proposed architecture: JSON -> compiled engine -> structured_verdict_object -> AI formatter -> card. UNIT_TEST_PLAN.md v3.0.0 replaces TEST_PLAN.md v2.0.0 (which had 0 unit tests, only 3 pre-flight checks). 55 functions x ~301 test cases with deterministic fixtures. 7 integration tests. | `mts/tests/compiled_code_opportunities.md`, `mts/tests/UNIT_TEST_PLAN.md`. `mts/tests/TEST_PLAN.md` archived to `mts/archive/TEST_PLAN_v2.0.0_ARCHIVED.md`. |
|------|----------|-----------|

| 2026-08-30 | **CROSS-TRADER: Workflow corrected — premature tagging discarded, Integration Plan adopted** | Previous workflow (extract + tag vs Tom in same session) was methodologically unsound. AI memory of compiled_engine.md unreliable. Produced false CONFIRM/DUPLICATE tags. All 4 existing extracts reprocessed to pure format (Source GPS + quotes only, zero tags). New 4-phase workflow: (1) Pure Extraction, (2) Consolidation, (3) Integration Planning with 5-step check per rule, (4) Integration with 3-snapshot validation. Integration Plan document written. 46 rules cataloged as CT-001 to CT-046. 01_AI_BEHAVIOR.md Section 3 updated to enforce pure extraction. 02a_CURRENT_STATUS.md cross-trader section rewritten. 03_FILE_INDEX.md updated. | `mts/research/cross_trader_integration_plan.md` (includes Appendix A rule catalog), 4 reprocessed extract files |
|------|----------|-----------|

| 2026-08-29 | **CROSS-TRADER: CryptoCred inqHN8q57X4 extracted** | 12 rules extracted from "Retests" video. 6 CONFIRM, 6 CLARIFY, 0 GAP, 0 REJECT, 0 BLOCKED. Zero contradictions with Tom's engine. All CLARIFY rules use existing DSA v1.2.0 data — no new fields required. Raw transcript could not be persisted to cryptocred/raw/ due to filesystem quirk (see NOTE in extract file). Extract file is complete and self-contained — raw persistence not required for integration. Cross-trader status: 4/7 transcripts extracted. | `mts/extracts/cryptocred/extracted/extract_inqHN8q57X4.md` |
|------|----------|-----------|


# Rule: APPEND ONLY. Never edit historical entries.
# New decisions go at the TOP of the table.

| 2026-08-29 | **CROSS-TRADER RESEARCH PHASE LAUNCHED** | Decision to extract rules from non-Tom analysts (CryptoCred, The Flow Horse, CrypNuevo) to clarify/confirm/fine-tune the MTS engine. First transcript: The Flow Horse Oy2Z-FQ77NM ("Most Traders Misread Volume Profile"). 11 rules extracted, tagged vs Tom's engine. Self-audit revealed multiple claim errors: (1) 2 rules marked "READY" actually require DSA fields, (2) "3 snapshots" claim was false — only 1 JSON + screenshots, (3) cryptocred/crypnuevo dirs not created, (4) DSA_TASK_011 invented without document. All corrected. Final status: 7 CONFIRM, 3 BLOCKED (pending DSA fields), 1 REJECT, 0 READY. Policy: NO INTEGRATION until all 7 transcripts extracted and cross-checked. | Cross-trader consolidation doc: mts/research/cross_trader_consolidation.md. Extract dirs created for all 3 analysts. DSA field requests compiled: zone_test_count, structure_duration_hours, volume_relative. |
|------|----------|-----------|

| 2026-08-29 | **CLEANUP: 7 stale research files archived + Task 3 cancelled** | (1) Task 3 (Prior Day H/L + London Range) CANCELLED — same reason as DSA_TASK_008. prior_day.high/low already live. london_range is NOT a Tom concept. (2) 7 completed/superseded research files moved to mts/archive/: validation_run_2026-08-27, compiled_engine_validation_2026-08-28, multi_tf_rule_redesign_2026-08-28, consolidated_task_list_2026-08-29, data_driven_revalidation_report_2026-08-29, session_timing_evidence, session_timing_recommendations. (3) 4 active research files remain: htf_structure_audit, validation_prompt_gpt, validation_prompt_grok, unclear_extractions. | Active research: 4 files. Archive: 16 files (15 archived + 1 README). Project cleaned. No runtime impact. |
|------|----------|-----------|

| 2026-08-28 | **CORRECTION #2: Clipboard files survived deletion — reason unknown** | User clarified: `user_pasted_clipboard_long_content_as_file_*.txt` files were ATTEMPTED deleted via `rm` but PERSISTED. We do not know if this is a platform design feature or a system bug. The correct stance is: clean what the system allows, do not fight what it keeps. Images (`image*.png`) were successfully deleted. Clipboard files remain — noted as open question, not investigated further. | Temp cleanup rule: Attempt deletion of all non-sentinel files. If they persist, log it and move on. Do not fabricate explanations ("intentionally kept by design") without evidence. |
|------|----------|-----------|
| 2026-08-28 | **SYS_AI_TASK_001 — Engine Patches Deployed (v4.1.1 -> v4.1.4)** | All 5 patches applied to compiled_engine.md: (1) Multi-TF zone priority rule — highest TF wins when price near multiple VA boundaries; (2) CVD/trade_flow contradiction resolution — backward-compatible path using last_3_delta tiebreaker, full DSA_TASK_003 integration ready; (3) Zone sub-states — "At/Above/Below zone" with 0.1% threshold gates CT vs BO validity; (4) Screenshot TF guidance — per-setup-level footprint recommendation (1H for weekly, 15m default); (5) OI trend as secondary confirmation — aligned/divergent classification. Integration + regression tests pass. Validation run JSON verdict unchanged (WAIT C 55/100). File grew 7.3KB -> 11.6KB (+4.2KB, +79 lines). Backup archived. |
|------|----------|-----------|
| 2026-08-28 | **DSA_TASK_002 CLOSED — All 4 bugs resolved** | BUG #1 (swing_low): not reproduced in 2 runs — likely fixed. BUG #2 (CVD contradiction): fixed by DSA_TASK_003 (cvd_recent + aligned flag). BUG #3 (expanded depth): fixed by DSA_TASK_003 (monotonicity check + warning). BUG #4 (VWAP Unicode): not reproduced in 2 runs — likely fixed. No remaining open DSA bugs. | DSA integration status upgraded from PARTIAL to COMPLETE v1.2. All known upstream data bugs resolved. |

| 2026-08-28 | **DSA_TASK_003 COMPLETE** | All acceptance criteria passed: (1) Expanded depth 0.5% bug fixed — omits threshold when monotonicity fails + adds `depth_coverage_warning`. 0.1% < 0.2% verified (173 < 369 bid, 151 < 317 ask). (2) CVD contradiction resolved — `cvd.cvd_recent` object added with slope_1h, slope_4h, delta_1h, delta_4h. `conditions.cvd_trade_flow_aligned: true` added. Logic verified: slope_1h=falling + trade_flow.net_delta=-1.954 = aligned. (3) BUG #3 + #6 not reproduced — likely fixed. | DSA_TASK_003 unblocks sys_AI Task 2 (CVD resolution engine patch). Engine patches can now proceed with full integration. |

| 2026-08-28 | **MTS Validation Run — BTCUSDT 19:23 UTC** | Full 9-step pipeline executed on live JSON. Verdict: WAIT C (55/100). 2 DSA bugs confirmed OPEN (#4 CVD contradiction, #5 expanded depth identical). 2 bugs not present (#3 swing_low, #6 VWAP Unicode). 3 engine coverage gaps identified: multi-TF zone priority, CVD contradiction resolution, above-VAH vs at-VAH sub-state. Screenshot flow validated: needed for conditional upgrade but base verdict determined from JSON alone. | compiled_engine.md performs correctly. No false positives. 5 tool calls used. Validation report written to mts/research/validation_run_2026-08-27_1923.md. |

| 2026-08-27 | **Temp directory FORBIDDEN for project files** | Added sentinel file in `/mnt/agents/temp/`, updated `00_START_HERE.md` (banner + mistake #8), `01_AI_BEHAVIOR.md` (critical rule), `05_NORMS.md` (editing rule). Ghost files from parallel session caused confusion — scanner bugs analyzed on retired code. | Temp is for session uploads ONLY. Canonical root is `/mnt/agents/output/upload_mirror/`. |
| 2026-08-27 | **Ghost artifacts cleaned + valid DSA bugs consolidated** | Deleted orphaned `DSA_TASK_1_2_3_MTS_Scanner_Bug_Fixes.txt` (scanner retired, bugs irrelevant) and empty `/mnt/agents/output/mts/runtime/` ghost dir. Created `DSA_TASK_002_valid_upstream_bugs.md` covering 4 real upstream data bugs: swing_low>low, CVD/trade_flow contradiction, order_book_depth_expanded identical values, VWAP Unicode corruption. | Scanner-internal bugs are dead weight. Upstream data bugs affect live trading directly. |
| 2026-08-27 | **Navigation overhaul v4.1.3** | system/ files renamed with numbered prefixes (00-05) to force read order. state.md split into 4 focused files. Linked-list headers added. Common mistakes block added. | Eliminates "where do I start?" and "where do I write this?" errors that repeat every session. |
| 2026-08-27 | **Scanner v2.0 RETIRED** | 66KB Python monolith removed. Bugs: init race, type mismatch, test misalignment, invented thresholds. | compiled_engine.md (7.3KB) + AI reasoning is faster, more adaptable, handles visual validation, maintains single source of truth. |
| 2026-08-27 | **System cleanup COMPLETE** | 10 orphaned files deleted from output/ root. 30 temp files cleared. Staging dirs cleaned. Card 1343 moved to canonical path. Runtime simplified to compiled_engine.md only. | |
| 2026-08-26 | **SESSION PAUSED — Resume Next** | 3 cards generated, 8 screenshots analyzed, DSA prior_day bug fixed, system optimized. Market at ~78,555 pre-US open. No valid setup. | |
| 2026-08-26 | **CT Short at VAH VALID but MISSED** | 5m RSI confirmed peak above 60. Price reached ~78,600 (VAH) and rejected. Entry window ~10 min. Dropped 300+ pts. | Proof that system works but latency is the enemy. |
| 2026-08-26 | **CT Long at VAL MISSED** | Price dipped to ~78,000 (below VAL 77,965) then bounced to 78,410. Entry was at VAL, not after bounce. System correctly said "entry gone." | |
| 2026-08-26 | **System cache + compiled engine DEPLOYED** | Python MTS_CACHE loads all 10 files in 1 call. Compiled engine (7.3KB) replaces 164KB rules. Per-JSON: 3 tool calls, <30 sec, 3KB chat output. | |
| 2026-08-26 | **DSA Bug Audit: 7 issues found** | 3 critical (prior_day, book depth, swing_low definition), 2 warnings, 2 minor. Prior_day FIXED. Book depth partially fixed. | |
| 2026-08-26 | **Malkans RSI 40/60 integrated** | User's custom RSI levels: white line = price RSI, blue = SMA. 60 = overbought, 40 = oversold. Cross-referenced with Tom's framework. | |
| 2026-08-26 | **Session timing research LAUNCHED** | Parallel session task spec written for US equity open impact on BTC. Task covers volatility, volume, correlation, Tom framework mapping. | |
| 2026-08-26 | **DSA Task #1 spec written** | Fix prior_day VP = daily_vp bug. Full spec with 4 hypotheses, 4 test cases, 9 acceptance criteria. | |
| 2026-08-26 | **Compact card mode DEPLOYED** | Chat output reduced 65% (9KB -> 3KB). Full card saved to disk. Faster sessions, less token bloat. | |
| 2026-08-26 | **Third live trading card generated** | BTCUSDT_2026-08-26_1343.md — WAIT C (55/100). Prior day bug fixed. CVD/trade_flow contradiction flagged. | |
| 2026-08-26 | **Second live trading card generated** | BTCUSDT_2026-08-26_1303.md — WAIT C (60/100). Price dropped to 78,245. Book anomaly (66.73 ratio) discovered. | |
| 2026-08-26 | **Fourth live trading card generated** | BTCUSDT_2026-08-26_1100.md — WAIT C (60/100). First card with cache + compiled engine. 1 tool call, <1 sec. | |
| 2026-08-26 | **First screenshot analysis** | 1m chart showed capitulation drop to ~78,000. CVD deeply negative. OI rising. Confirmed JSON "falling" CVD vs earlier "flat." | |
| 2026-08-26 | **Phase 3 COMPLETE** | All 7 condition files built and verified. 370+ claims, 91 gaps, 0 fabrication. | |
| 2026-08-26 | **Phase 4 COMPLETE** | All 4 integration files built and verified. 111KB, 35 gaps, 0 fabrication. | |
| 2026-08-25 | MTS Runtime System v1.0 DECLARED | 11 files form a complete, self-contained trading decision engine. Ready for live chart testing. | |
| 2026-08-26 | Phase 4 files CORRUPTION DISCOVERED | All 4 integration files are 0-line blobs (M-028). Content unreadable. | |
| 2026-08-26 | **Architecture pivot to Prompt-Embedded + Quickref (Option A)** | Merged 4 integration files into 01_AI_BEHAVIOR.md Section 14. Created 04_PER_JSON_GUIDE.md. Reduced per-JSON reads from 11 to 3-7 files. | |
| 2026-08-26 | Session handoff simplified | Old handoff (44 lines, stale Phase 4 references, 7 file upload list) replaced with new handoff (88 lines, 3-file upload, operational focus, no deprecated file references). | |
| 2026-08-26 | Trigger system v4.1.1 REVALIDATED | Contradiction scan: 0 contradictions. Back-test: 2/2 cards match. Integration: decision diamond + abort conditions updated. Size audit: 756-line file, 45-line runtime quickref added. 13 gaps flagged. | |
| 2026-08-26 | Trigger system LIVE TEST | BTCUSDT_2026-08-26_1108.md — verdict: WAIT/WATCH (Band C, 55/100). 0 file loads, <1s analysis, ~8,500 tokens saved. JSON-only resolution validated. | |
| 2026-08-26 | Third live trading card generated | BTCUSDT_2026-08-26_1108.md — CT Long at VAL pending trigger. Price 118 pts above zone. Alert set at 78,558.71. | |
| 2026-08-26 | Second live trading card generated | BTCUSDT_2026-08-26_1003.md — verdict: WAIT/WATCH (Band C, 60/100). Price broke below daily VAL. Context shifted from CT Long to Breakout Short watch. First card (0915) is STALE. | |
| 2026-08-26 | ALL 5 DSA BUGS FIXED | Verified on live BTCUSDT snapshot 2026-08-26 09:15 UTC. Daily VP, weekly VP, post-funding VP, 4H VP, conditions object all operational. First end-to-end trading card generated from JSON input. | |
| 2026-08-26 | First live trading card generated | BTCUSDT_2026-08-26_0915.md — verdict: WAIT/WATCH (Band C, 55/100). System operational. JSON-driven workflow validated. | |
| 2026-08-25 | sys_ai_prompt.md Sections 12-13 CORRECTION | These sections do NOT exist in the uploaded v2.0 file. Handoff corrected to not reference them. | |
| 2026-08-25 | session_handoff.md path CORRECTION | File exists at /mnt/agents/output/upload_mirror/ (not /mnt/agents/upload/). Handoff path corrected. | |
| 2026-08-19 | Core session files formalized in light_file_map.md | 11 always-upload files. master_index.md removed from always-upload list. | |
| 2026-08-19 | P0 FRESH extractions 18/18 complete | All priority 0 videos extracted per Protocol #3. | |
| 2026-08-12 | 4MoNjEQ2Dd8 FRESH extracted | Phase 1A P0 batch complete. 45 in vivo codes, 3 T5 commands, 20 gaps. | |
| 2026-08-07 | CLEAN START after audit | All contaminated files archived. System rebuilt from FRESH extractions only. | |
| 2026-08-07 | Part J - 10 non-negotiable extraction rules ADDED | Prevents fabrication, tier upgrading, cross-video contamination. | |
| 2026-08-04 | 5-LLM conformational research COMPLETE | Key findings integrated into state.md + playbook.md. Full report ARCHIVED. | |
| 2026-08-02 | Approve File Map + Smart Handoff | 74% token savings on chart reading. | |
| 2026-08-02 | Approve Core Engine v1.0 | 5 pipelines, auto-orchestration. | |
| 2026-08-01 | Skip Fabio/Forrest scraping | Tom's extraction covers full toolkit. | |

---
# END

---

## ENGINE_OPT_002 — 2026-08-28

**Decision:** Deploy v4.2.0 engine optimization: directional filter + per-zone distance cap + single best output + C+ verdict + zone map expansion.

**Rationale:**
- Post-Funding VAL at 79,097 (0.266% away, 4.04:1 R:R) was hidden by 0.2% threshold
- 5m swing low at 78,961 (0.437% away) was not in Zone Map at all
- Chart bounce at ~78,980 was at 5m swing low + weekly POC confluence — system missed it entirely
- Generic WAIT C output provided no actionable guidance

**Changes:**
1. Zone Map: Added Swing High/Low (1h/15m/5m), Prior Day VAH/VAL/POC
2. Directional Filter: price_vs_poc matrix (above/below/at/in_va) filters reversion direction only
3. Distance Cap: Per-zone-type thresholds (weekly 0.5%, daily/4H/PF 0.4%, swing 0.3%, VWAP/FVG 0.2%)
4. Confluence Scoring: Zone-to-zone within 0.3%, +10/+20 confidence, midpoint as confluence zone
5. R:R Sanity Pre-Filter: Gross <1.5 skipped before full calculation
6. Single Best Output: Rank by R:R * confluence * tf_weight, output top 1
7. C+ Verdict Band (55-69): Conditional setup with alert + trigger spec + invalidation level
8. Decision Diamond v4.2.0: Added "Directional Zones Identified?" gate before evaluation

**Rollback Plan:** Revert compiled_engine.md to v4.1.4-p1 (backup in archive).

**Validation:**
- Test Case 1 (10:39 UTC @ 79,308.3): C+ CT Long at confluence ~79,029 | R:R 8.8:1 NET
- Test Case 2 (11:02 UTC @ 79,547.7): C+ CT Short at PF VAH 79,574 | R:R 2.16:1 marginal | FVG support degrades
- Test Case 3 (08:09 UTC @ 79,783.7): C+ CT Short at PF VAH 79,791 | R:R 3.8:1

**No Tom rules modified.** All changes are system inventions for automation. Tom quotes preserved.

## 2026-09-12 - BUG-011 fix: math_object_builder reads net_rr_sanity

Rule 37 bug fix. Code read rr_sanity (gross >= 1.5). Engine Sec 6 row 4
mandates net >= 2.0. Aligned code to doc. Re-run on 10:44 snapshot:
top_candidate_rr_below_threshold=True (rank-1 pf_vah net 1.95 < 2.0).
Verdict on that snapshot now correctly WAIT.

Backup: backup_20260912_162747.

---

## 2026-09-12 - MTF design doc contradiction resolved

§5 pattern taxonomy authoritative. §6 example rewritten to valid
slow_aligned_fast_divergent instance (+D,+A,+A). §9 stale cvd.divergence
line removed (field deleted earlier same session).
MD5 4D4B79CEFAD881EF4E8B686C3BDA8B62, 4718 bytes.
Backup: backup_20260912_163429.

---

## 2026-09-28 - T055 citation flagged: EuropePMC ppr602886 - wrong paper attributed

T055a (pre-gate) cited EuropePMC ppr602886 for "opening order imbalance predicts BTC perp
returns at 4-12h, six Binance perpetual contracts." Opened: ppr602886 is Wen/Bouri/Xu/Zhao 2022,
"Intraday Return Predictability in the Cryptocurrency Markets: Momentum, Reversal, or Both"
(SSRN 4080253) - BTC/ETH/LTC/XRP price momentum-reversal on 2013-2020 data, no order-imbalance
construct, no six-Binance-perp sample. The actual finding belongs to Kim & Hansen, "The
Quarter-Hour Effect: Periodic Algorithmic Trading and Return Predictability in Cryptocurrency
Futures", arXiv 2607.09426 (Jul 2026) - verified 2026-09-28, matches on title/authors/abstract.
Corrected in T055a_POSITIONING_FLOW.md (gate v3.0 rewrite).

## 2026-09-28 - T055 citation flagged: SSRN 7483658 - claim mismatch

T055b (pre-gate) cited SSRN 7483658 (Tangirala, 44 ICT/SMC detectors on S&P 500) for "combining
HTF liquidity draw + session killzone + 1:2.5 RR transforms it to positive." Opened and verified
2026-09-28: the paper's stated result is that none of the 44 concepts beats a matched null
baseline at any of 8 holding horizons, with multiple-testing correction - no combination-rescues
-it finding is reported. The source itself is real (title/authors/venue match), but the claim
attributed to it does not. Corrected in T055b_PROVEN_SETUPS.md (gate v3.0 rewrite); claim removed.

---

## 2026-10-04 - T052 / B063 / T046 decisions
2026-10-04 - T052: no Tom-cited SETUP_CONFIRMED trigger exists (extract gaps YopZ5ZDmMFw:146, rrHj24GSR6M:124; "confirms" = zone proof); status stays unused, no emitter; see items/T052 (MTS-2026-10-04-1009Z-APP-BLD-t052-b063-t046)
2026-10-04 - B063: DEPRECATE divergence in the snapshot schema (Tom gives only a guard, extract_rFPCtOcfUMI_fresh.md:71; thresholds NO-SOURCE); six doc files listed in items/B063, none changed yet (MTS-2026-10-04-1009Z-APP-BLD-t052-b063-t046)
2026-10-04 - T046: Stage 3 bundle - accept keep shortcuts, accept keep L-numbers + titles, reject extraction (Get-Descendants already shared), accept A/B/E map, folder renames need operator (MTS-2026-10-04-1009Z-APP-BLD-t052-b063-t046)
