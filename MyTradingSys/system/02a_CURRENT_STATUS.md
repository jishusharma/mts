> **SUPERSEDED (2026-10-08).** Frozen history from the September build. For current state read
> `MyTradingSys/research/STATUS.md`, then `MyTradingSys/system/LESSONS_LEARNED.md` (entry order is in CLAUDE.md).
> Where this file disagrees with CLAUDE.md or SURFACE_POLICY.md, those win.

# FILE: 02a_CURRENT_STATUS.md
# READ ORDER: 3 of 8
# PURPOSE: System health, active components, current file inventory
# LAST UPDATED: 2026-09-14
# SIZE: ~9KB
# NEXT FILE: 02b_DECISIONS_LOG.md
# PREVIOUS FILE: 01_AI_BEHAVIOR.md
# ---

# CURRENT STATUS — MTS v4.2.0-p5
# GOAL: Single source of truth for "what is working right now."
# Updated: 2026-09-14
# Cleanup 2026-09-14: 12 .old archived to archive/cleanup-2026-09-13/.
#   .pytest_cache/, empty tests/, mts/visual/, "=" deleted.
#   Playbook L/M/N removed; 11 stale refs (state.md/core_engine.md) replaced.
# Build 2026-09-14: Build-Check.ps1 + test_integrity.py.
#   Dump_All.ps1 chains to Build-Check. The session prompt prepends BUILD_REPORT.
#   CAPABILITIES.md created (trigger -> module map).
# Rule 38 (2026-09-14): coordinator prompts must contain real file content.
#   Workers correctly BLOCK on placeholders.
# Architecture: 3-Layer (Math → Judgment → Formatter) — MATH COMPILED.
#   check_scalp_preconditions + check_invalidation in mts_math.py.
#   NOT WIRED — Worker F pending.
# Session Management: COORDINATOR + WORKERS (session_log.json ledger)

---

## FILE MAP — ACTIVE SYSTEM FILES

### MTS CONDITION FILES (7 files)
| # | File | Size | Status | Purpose |
|---|------|------|--------|---------|
| 1 | mts/conditions/market_state_rules.md | ~20KB | COMPLETE | Balance/trend taxonomy, state workflow, state->setup matrix |
| 2 | mts/conditions/zone_identification_rules.md | ~25KB | COMPLETE | 9 zone types, workflow, negative rules |
| 3 | mts/conditions/setup_type_rules.md | ~30KB | COMPLETE | 4 execution modes, idea+proof framework, trader DNA |
| 4 | mts/conditions/proof_requirements_formatted.md | ~58KB | COMPLETE | 14 proof categories, cross-cutting layer |
| 5 | mts/conditions/risk_protocol.md | ~20KB | COMPLETE | Stops, sizing, R:R, targets, re-entry, drawdown |
| 6 | mts/conditions/entry_timing_triggers.md | ~25KB | COMPLETE | Trigger taxonomy, 4 modes, 4 tiers, 10 negative rules, 13 gaps |
| 7 | mts/conditions/session_timing_rules.md | ~8KB | COMPLETE | Session-specific timing rules, volatility rankings |

### RUNTIME FILES (6 files)
| # | File | Size | Status | Purpose |
|---|------|------|--------|---------|
| 8 | mts/runtime/compiled_engine.md | ~24.8KB | ACTIVE v4.2.0-p5 | All decision tables from 6 condition files, stripped. 94% token reduction. SOLE RUNTIME. Patched 2026-08-28. 9 fabrications stripped, 20 over-systematizations demoted to [PRINCIPLE]. |
| 9 | mts/runtime/v4.2.0_optimization_spec.md | ~7.7KB | REFERENCE | Design doc for ENGINE_OPT_002. Not loaded at runtime. |
| 10 | mts/runtime/mts_math.py | ~3.5KB | ACTIVE — COMPILED | 9 pure math functions: distance, substate, cap, tier, trigger validity, gross/net R:R, sanity, confluence. Zero side effects. All system parameters tagged. 64/64 unit tests pass. |
| 11 | mts/runtime/math_object_builder.py | ~6.5KB | ACTIVE — COMPILED | DSA snapshot → math_object compiler. Consumes JSON, produces compiled math_object for judgment layer. 34/34 unit tests pass. |
| 12 | mts/runtime/current_market_state.md | ~1.6KB | ACTIVE | Persistent slow-moving structural state per asset. (SSOT - btcusdt_market_session.md deprecated 2026-09-10) |

### CARD SPEC (1 file)
| # | File | Size | Status | Purpose |
|---|------|------|--------|---------|
| 1 | mts/cards/trading_card_generator.md | ~25KB | COMPLETE v4.2.0 | 6-step pipeline, 9-section card, verdict tree. C+ template added. |

### RESEARCH FILES (4 files — cleaned 2026-08-29)
| # | File | Size | Status | Purpose |
|---|------|------|--------|---------|
| 11 | mts/research/htf_structure_audit_2026-08-28.md | ~27KB | COMPLETE | HTF structure audit: 47 extracts, 28 claims, 8 engine gaps, 9 DSA schema changes |
| 12 | mts/research/validation_prompt_gpt.md | ~8KB | REFERENCE | GPT validation prompt template |
| 13 | mts/research/validation_prompt_grok.md | ~7KB | REFERENCE | Grok validation prompt template |
| 14 | mts/research/unclear_extractions.md | ~2KB | ACTIVE | Parking lot for extractions not ready for engine integration
| 15 | mts/research/visual_validation_protocol_vvp001.md | ~9KB | ACTIVE | Screenshot reading protocol: cursor rules, indicator tiers, proof detection, cross-TF conflict resolution. Created 2026-08-31. |

**Archived (moved to mts/archive/):** session_timing_evidence, session_timing_recommendations, validation_run_2026-08-27, compiled_engine_validation_2026-08-28, multi_tf_rule_redesign_2026-08-28, consolidated_task_list_2026-08-29, data_driven_revalidation_report_2026-08-29.

### DATA / DSA TASKS (4 files)
| # | File | Size | Status | Purpose |
|---|------|------|--------|---------|
| 20 | runtime_data/data_schema_v1.0.md | ~12KB | ACTIVE v1.2.0 | DSA JSON schema — all fields documented |
| 21 | runtime_data/dsa_task_007_htf_alignment.md | ~4KB | COMPLETE | HTF structure schema alignment task |
| 22 | runtime_data/dsa_task_008_lean_request.md | ~4KB | CANCELLED | Gap concept rejected after research |
| 23 | runtime_data/dsa_task_009_liquidation_investigation.md | ~4KB | REVISED | Visual validation protocol (no DSA changes) |
| 24 | runtime_data/dsa_task_012_setup_candidates.md | ~15KB | ACTIVE | Pre-computed setup_candidates module. APPROVED 2026-09-04. ~14h dev. v1.3.0.

### TEST FILES (6 files) |

### TEST FILES (6 files)
| # | File | Size | Status | Purpose |
|---|------|------|--------|---------|
| 1 | mts/tests/UNIT_TEST_PLAN.md | ~3KB | ACTIVE v4.0.0 | 15 compiled functions, 98 pytest cases, 2 test files. Replaces v3.0.0 fantasy spec. |
| 2 | mts/tests/compiled_code_opportunities.md | ~51KB | ACTIVE | Maps every compiled_engine.md function to compileable vs AI-reasoning. 51 compile, 2 AI-only, 2 hybrid. |
| 3 | mts/tests/regression_log.md | ~1KB | ACTIVE | Patch smoke test history |
| 4 | mts/tests/test_mts_math.py | ~5KB | ACTIVE | 64 unit tests: determinism, edge cases, all 9 math functions |
| 5 | mts/tests/test_math_object_builder.py | ~4KB | ACTIVE | 34 unit tests: determinism, schema, zone fields, R:R logic, confluence, hard stops |
| 6 | mts/tests/TEST_PLAN.md | ~4KB | ARCHIVED v2.0.0 (superseded by UNIT_TEST_PLAN.md) | 3-check minimal testing: Integrity, Schema spot-check, Patch smoke test |

### TRADING CARDS GENERATED (13 cards)
| # | File | Timestamp | Verdict |
|---|------|-----------|---------|
| 1 | mts/cards/BTCUSDT_2026-08-26_0915.md | 09:15 UTC | WAIT C (55/100) |
| 2 | mts/cards/BTCUSDT_2026-08-26_1003.md | 10:03 UTC | WAIT C (60/100) |
| 3 | mts/cards/BTCUSDT_2026-08-26_1100.md | 11:00 UTC | WAIT C (60/100) |
| 4 | mts/cards/BTCUSDT_2026-08-26_1100_compact.md | 11:00 UTC | WAIT C (60/100) — compact format test |
| 5 | mts/cards/BTCUSDT_2026-08-26_1108.md | 11:08 UTC | WAIT C (55/100) |
| 6 | mts/cards/BTCUSDT_2026-08-26_1303.md | 13:03 UTC | WAIT C (60/100) |
| 7 | mts/cards/BTCUSDT_2026-08-26_1343.md | 13:43 UTC | WAIT C (55/100) |
| 8 | mts/cards/BTCUSDT_2026-08-27_1923.md | 19:23 UTC | WAIT C (55/100) — validation run |
| 9 | mts/cards/BTCUSDT_2026-08-28_0444.md | 04:44 UTC | WAIT C (55/100) — v4.1.4 patch validation |
| 10 | mts/cards/BTCUSDT_2026-08-28_0809.md | 08:09 UTC | WAIT C — v4.2.0 optimization validation |
| 11 | mts/cards/BTCUSDT_2026-08-31_0727.md | 07:27 UTC | C+ (60/100) Scalp Short at VWAP +2s |
| 12 | mts/cards/BTCUSDT_2026-08-31_2127.md | 21:27 UTC | C+ (58/100) CT Short at post-funding VAH cluster |
| 13 | mts/cards/BTCUSDT_2026-09-01_0521.md | 05:21 UTC | C+ (65/100) CT Short at 4H VAH cluster 78,997-79,128 |

---

## SYSTEM STATUS — COMPONENTS

| Component | Status | Notes |
|-----------|--------|-------|
| MTS Runtime System | ACTIVE v4.2.0-p5 | compiled_engine.md (~25KB) is sole runtime. **ENGINE_OPT_002:** (1-6) as before. **GAP_FIX_001:** (1-3) as before. **HTF_PATCH_001 LIVE:** (1) Single Print = Target/Exit; (2) Double Distribution breakdown target; (3) Acceleration mode; (4) VPOC Migration [ACTIVATED 2026-08-29]; (5) Exhaustion Gate [ACTIVATED 2026-08-29]; (6) Prior Day Close as Zone. All 6 patches LIVE. DSA_TASK_007 COMPLETE. BUG #4+#5 CLOSED 2026-08-31. |
| Trigger Engine | ACTIVE v4.1.1 | 4-tier hierarchy. 10 negative rules. 13 gaps. 45-line runtime quickref. |
| Performance | OPTIMAL | ~8,500 tokens saved. <1s analysis. JSON-only resolution validated. |
| Core analyst | Tom Vorwald | 47 videos extracted. All concepts embedded. Malkans RSI 40/60 integrated. |
| Rule extraction | COMPLETE | All Tom rules extracted, categorized, cross-referenced. |
| Setup library | COMPLETE | 4 execution modes (CT/TC/BO/SC) defined with full conditionality. |
| Decision engine | ACTIVE v4.2.0 | Embedded in 01_AI_BEHAVIOR.md Section 14 + compiled_engine.md (19.4KB). |
| Math layer | ACTIVE — COMPILED | mts_math.py (9 functions) + math_object_builder.py. 98/98 tests pass. AI never recomputes distance, R:R, tier, or confluence. |
| Risk engine | COMPLETE | Stops, sizing, R:R, targets, drawdown, re-entry all defined. |
| Visual validation | ACTIVE | Screenshot analysis proven on 8+ live charts. Footprint interpretation validated. **VVP-001 protocol created 2026-08-31** — cursor position rules, indicator tiers, proof detection, cross-TF conflict resolution. First live test: BTCUSDT 2026-08-31 (3 screenshots, 4 errors caught, protocol established). |
| Real-time mode | TESTED | Screenshot workflow proven. CT Short at VAH identified but missed due to latency. |
| Architecture | v4.2.0 — Compiled Engine + AI Reasoning | 2-3 calls per JSON. Compact cards. Full cards on disk. No MTS_CACHE. |
| Protocol System | ACTIVE v1.2 | 19 protocols across 5 categories. P-COMPLY-001 mandatory. |
| Paper trade log | PENDING | Template needed for Phase 5. |
| Performance analytics | PENDING | Phase 5 candidate. |
| Session timing research | VALIDATED — INTEGRATED | Grok + GPT validation complete. 10 SR rules: 1 approved (SR-007 funding), 9 rejected/reformulated. DSA v1.2.0 emits 4 session fields. No hard rules in engine. |
| DSA enhancement pack | COMPLETE v1.2.0 | DSA_TASK_004a implemented and verified. Minimal JSON (~52 fields), fixed 8-session framework, DST-correct US open, internal computations. Screener version 1.2.0. |
| DSA integration | COMPLETE v1.2.0 → v1.3.0 PENDING | DSA_TASK_007 COMPLETE. 4 fields confirmed live. Schema v1.2.0. DSA_TASK_008 COMPLETE (0 fields approved). DSA_TASK_010 STALE (cross-trader Phase 1 complete). DSA_TASK_012 ACTIVE — pre-computed setup_candidates module APPROVED 2026-09-04. ~14h dev work. No other pending DSA tasks. |
| File index hygiene | CLEANED 2026-08-29 | Ghost card removed. Missing research + test files added. Archive updated. Temp: ephemeral images purged. Test plan updated v4.0.0 for v4.2.0-p5 (15 compiled functions, 98 cases). |

---

## PROJECT GOALS

| # | Goal | Status | How Verified |
|---|------|--------|-------------|
| 1 | Complete Phase 1: FRESH extract ALL organized transcripts (47 videos) | COMPLETE | 47/47 FRESH extracted. |
| 2 | Complete Phase 2: Build master cross-reference index of all rules | COMPLETE | Cross-reference embedded in all Phase 3 files. |
| 3 | Complete Phase 3: Build condition files from emergent clusters | COMPLETE | 7 files built, ~370+ claims, 91 gaps, 0 fabrication. |
| 4 | Complete Phase 4: Build integration/runtime layer | COMPLETE | Content merged into 01_AI_BEHAVIOR.md Section 14. 4 corrupted files deleted. |
| 5 | Test JSON-to-card pipeline with live DSA snapshots | COMPLETE | 10 live cards generated. Pipeline validated. |
| 6 | Output trade plans: entry, stop, target, invalidation, confidence | COMPLETE | Generated for all snapshots. R:R auto-calculated. |
| 7 | Track performance per setup for continuous improvement | PENDING | Paper trade log template needed. |
| 8 | Never execute trades - Jishu decides | LOCKED | playbook.md Part A |

---

## OPERATIONAL PARAMETERS — LOCKED

| Parameter | Value |
|-----------|-------|
| Assets | BTCUSDT (P0), ETHUSDT (P1) |
| Primary Source | CoinGlass (aggregates Binance+Bybit+OKX) |
| Timeframes | 1W/1D (macro), 4H (context), 1H (setup), 15m (entry), 5m/1m (scalp) |
| Sessions | UTC Day, Asian, London, NY, Funding Reset (00:00/08:00/16:00 UTC) |
| Daily Loss Limit | -3% of capital = STOP trading for the day |
| Max Drawdown | -10% of capital = SYSTEM HALT, full re-evaluation |
| Min R:R (NET) | 2:1 after 25% friction haircut |
| Friction | 25% haircut on all R:R calculations |

---

## NEXT SESSION

**Context to load:** 00_START_HERE.md → 01_AI_BEHAVIOR.md → 02a_CURRENT_STATUS.md
**Workflow:** Paste JSON → math_object_builder compiles → judgment layer generates card. OR upload screenshot with cursor at RIGHT EDGE + Fixed Range VP.
**Current market context:**
- Last price: 78,784.5 (05:21 UTC)
- Last verdict: C+ CT Short at Upper VAH Cluster 78,866-78,947 (65/100) — Trigger UNCONFIRMED
- Funding: 7-day 1.8:1 longs pay, OI $16.45B
- Monitor 4H VAH cluster 78,997-79,128 for fresh trigger, or break below 4H VAL 78,705 for balance breakdown.

**Session end logs archived:** See `system/session_end_logs.md` for all historical session logs.

---

- **D1 CLOSED 2026-09-12** — `/fapi/v1/allForceOrders` 404. REST path + LiquidationClusterBuilder.java deleted. BinanceClient dead methods removed. Compile clean.
- **D2 CLOSED 2026-09-12** — engine confirmed zero liquidation reads. Schema marks liquidation.* / liquidation_warning.* DEPRECATED.

**Dev lane closed 2026-09-12.** W1 and W2 lanes archived. W3 (MTF design) continues standalone. Session pivots to trade-ready state tracking.

# END## LIVE VALIDATION HISTORY

**2026-08-29 v4.2.0-p2:** Price 77,541.8 — NO TRADE. 0 bugs, 2 refinements. See 02b_DECISIONS_LOG.md.

**2026-08-28 17:33:** Price 77,965.1 — C+ SETUP FORMING (58/100). See 02b_DECISIONS_LOG.md entry 2026-08-28.

---

## LIVE VALIDATION — BTCUSDT @ 77,965.1 | 2026-08-28 17:33 UTC

**DSA Snapshot:** Price 77,965.1 | Weekly VAL 78,119.30 (0.20% away) | Post-funding VAL 78,008.84 (0.02% away)
**State:** Balance (VP shapes all B, price 0.20% below weekly VAL — below 0.3% breakdown threshold, no override)
**Directional filter:** Standard reversion (price < POC -> evaluate lower zones for LONGS)
**Zones within cap:** Post-funding VAL 78,008.84 (0.02%, cap 0.4% PASS), Weekly VAL 78,119.30 (0.20%, cap 0.5% PASS)
**Confluence:** Post-funding VAL + Weekly VAL = 0.14% apart -> +10 confidence
**R:R (Post-funding VAL):** Stop 77,625.6 (5m swing low) | Target 79,284.54 (weekly POC) | Gross 3.33:1 | NET 2.50:1
**Proof:** B profile (daily+weekly), trade_flow positive (0.734), CVD flat + aligned
**Trigger:** Missing — price 0.056% below zone, needs retest with rejection
**Verdict:** C+ — SETUP FORMING (~58/100) | CT Long at Post-funding VAL 78,008.84 | Alert + pull 15m footprint on approach

**Patch behavior verified:**
- Patch 1: Price 0.20% below weekly VAL (<0.3%) -> NO override, Balance correctly maintained. At 77,625 (0.67%) would have overridden to Trend. [PASS]
- Patch 2: No breakout -> standard reversion-only filter applied. At 77,625 would have expanded to BOTH directions. [PASS]
- Patch 3: speed_picking_up = false -> caps unchanged. If true, weekly cap would expand to 1.0%. [PASS]

**v4.2.0-p2 Output:** C+ — SETUP FORMING (58/100) — actionable conditional setup with alert
**v4.2.0 (unpatched) Output:** Same result for this snapshot (patches are conditional, no false triggers)

---

## CROSS-TRADER EXTRACTION STATUS

### Workflow Change (2026-08-30)
**Previous workflow:** Extract + tag vs Tom's engine in same session (discarded).
**New workflow:** 4-phase integration plan (see mts/research/cross_trader_integration_plan.md).
- Phase 1: Pure extraction (Source GPS + quotes only) — COMPLETE
- Phase 2: Consolidation (group, dedupe, catalog) — COMPLETE
- Phase 3: Integration Planning (5-step check per rule) — COMPLETE
- Phase 4: Integration (3-snapshot validation) — COMPLETE

**Why changed:** Premature tagging during extraction was methodologically unsound. AI memory of compiled_engine.md unreliable. Produced false CONFIRM/DUPLICATE tags. All 4 existing extracts reprocessed to pure format.

### Extracted (7/7 — ALL REPROCESSED TO PURE FORMAT)
| Analyst | Video ID | Title | Rules | Status |
|---------|----------|-------|-------|--------|
| The Flow Horse | Oy2Z-FQ77NM | Most Traders Misread Volume Profile | 11 | PURE — reprocessed 2026-08-30 |
| The Flow Horse | zMM9QgxfEFI | The Bitcoin Setup Changed | 8 | PURE — reprocessed 2026-08-30 |
| CryptoCred | BHwoN7VPrBE | Market Structure | 15 | PURE — reprocessed 2026-08-30 |
| CryptoCred | inqHN8q57X4 | Retests | 12 | PURE — reprocessed 2026-08-30 |
| CryptoCred | _ndAoizXy64 | Trade Management | 13 | PURE — extracted 2026-08-30 |
| CryptoCred | XeQV2ECtZVQ | Risk Management | 13 | PURE — extracted 2026-08-30 |
| CryptoCred | Yp0k8HD5xro | First Trouble Area | 13 | PURE — extracted 2026-08-30 |

### Pending Upload (0/7)
| Analyst | Video ID | Title | Status |
|---------|----------|-------|--------|
| The Flow Horse | UcPp0gFI5M8 | Market Profile: Course Introduction | Awaiting upload — BACKUP ONLY |

### Missing (need direct URLs)
| Analyst | Title | Status |
|---------|-------|--------|
| The Flow Horse | Mapping Environments Base Part 1 | Not found by search |
| The Flow Horse | Mapping Environments Base Part 2 | Not found by search |
| The Flow Horse | Order Flow Intro: Passive and Active Order Flow | Not found by search |
| The Flow Horse | Market Profile: Anomalies — Ledges | Not found by search |
| CrypNuevo | Liquidity Heatmap/Liquidity Sweeps (4f8GneAu_-0) | No subtitles available |

**Policy:** NO INTEGRATION until all 7 transcripts extracted and Phase 2-4 complete per Integration Plan.

### Files Created / Modified This Session
| File | Purpose |
|------|---------|
| `mts/research/cross_trader_integration_plan.md` | NEW — 4-phase integration workflow with 5-step check + Appendix A rule catalog (CT-001 to CT-046) |
| `mts/extracts/the_flow_horse/extracted/extract_Oy2Z-FQ77NM.md` | REPROCESSED — pure format, tags removed |
| `mts/extracts/the_flow_horse/extracted/extract_zMM9QgxfEFI.md` | REPROCESSED — pure format, tags removed |
| `mts/extracts/cryptocred/extracted/extract_BHwoN7VPrBE.md` | REPROCESSED — pure format, tags removed |
| `mts/extracts/cryptocred/extracted/extract_inqHN8q57X4.md` | REPROCESSED — pure format, tags removed |
| `mts/extracts/cryptocred/extracted/extract__ndAoizXy64.md` | NEW — pure format, 13 rules, CT-047 to CT-059 |
| `mts/extracts/cryptocred/extracted/extract_XeQV2ECtZVQ.md` | NEW — pure format, 13 rules, CT-060 to CT-072 |
| `mts/extracts/cryptocred/extracted/extract_Yp0k8HD5xro.md` | NEW — pure format, 13 rules, CT-073 to CT-085 |

---

## PENDING TASKS — NEXT SESSION

### Task 1: HTF Structure Audit (HIGH PRIORITY) — COMPLETE 2026-08-28
**Trigger:** 4H BTCUSDT double top → breakdown revealed engine blindness to weekly VP structure
**Status:** COMPLETE — audit file written, 8 engine gaps identified, 8 patch recommendations, 9 DSA schema changes
**Output:** `mts/research/htf_structure_audit_2026-08-28.md` (~27KB)
**Key findings:**
- Engine blind to single prints (target areas, NOT entries) — Gap #1
- Engine blind to double distributions (two balance areas = range expansion) — Gap #2
- Engine blind to VPOC migration (rising/falling = trend strength) — Gap #3
- Engine has no exhaustion gate for CT (volume spike + break below balance) — Gap #7
- Engine missing prior_day.close as zone — Gap #8
**Next:** All patches implemented. Audit file retained for reference.

### Task 2: Post-Breakdown Retest Rule (MEDIUM PRIORITY) — FLAGGED, NOT READY
**Trigger:** Bounce from 76,853 → retest of broken weekly VAL at ~77,900
**Status:** FLAGGED — EXTRACTION UNCLEAR. NOT READY FOR ENGINE INTEGRATION.
**Why:** This concept was AI-derived from extractions, not a clear Tom rule. No extracted video defines: (a) what TF tracks the breakdown, (b) what defines "breakdown" vs "retest", (c) what setup type applies on retest, (d) what invalidates the flag. Without these, any engine rule would be AI interpolation, not Tom-validated.
**Action:** Store in `mts/research/unclear_extractions.md`. Revisit when new extractions provide clarity. Do NOT patch engine until validated against 3 live snapshots per Rule 35.

### Task 3: Prior Day H/L + London Range in DSA (MEDIUM PRIORITY) — CANCELLED
**Status:** CANCELLED — same reason as DSA_TASK_008.
**Why:** `prior_day.high` and `prior_day.low` are already in the schema (confirmed live in DSA v1.2.0). `london_range` is NOT a Tom-validated concept — no extracted video defines "London range" as a trading level. Tom uses session timing (Asian, London, NY) for volatility context, not range boundaries as structural zones. No DSA task doc was ever created (DSA_TASK_005 does not exist). No JISHU bandwidth was allocated.
**Action:** Removed from pending tasks. If future extractions reveal Tom uses prior day H/L as explicit zones, revisit. London range stays OUT — not a Tom concept.

### Task 0: Extract Math Layer to Compiled Code (HIGH PRIORITY) — COMPLETE 2026-08-31
**Status:** COMPLETE — 9 pure functions extracted to mts_math.py, math_object_builder.py created.
**Output:** mts_math.py (~3.5KB, 9 functions), test_mts_math.py (~5KB, 64 tests), math_object_builder.py (~6.5KB), test_math_object_builder.py (~4KB, 34 tests)
**Tests:** 64/64 test_mts_math.py + 34/34 test_math_object_builder.py = 98/98 PASS
**Hard rule established:** AI never recomputes distance, R:R, tier, or confluence. Receives compiled values from math_object and applies principles contextually.
**Architecture:** DSA Snapshot → math_object_builder → math_object → AI Judgment Layer → Formatter → Card

### Task 4: Implement HTF Structure Patches (HIGH PRIORITY)
**Status:** ALL 6 PATCHES LIVE
**Source:** `mts/research/htf_structure_audit_2026-08-28.md` Section 7
**Patches queued:**
| # | Patch | Status | Complexity | DSA Fields |
|---|-------|--------|------------|------------|
| 1 | Single Print = Target, Not Entry | LIVE | LOW | None |
| 2 | VPOC Migration Trend | LIVE [ACTIVATED 2026-08-29] | MEDIUM | `weekly_vp.prior_week_poc`, `weekly_vp.two_week_ago_poc` |
| 3 | Double Distribution Breakdown Target | LIVE | MEDIUM | None (visual flag) |
| 4 | Exhaustion Gate for CT | LIVE [ACTIVATED 2026-08-29] | MEDIUM | `volume_spike_at_level` |
| 5 | Prior Day Close as Zone | LIVE | LOW | `prior_day.close` |
| 6 | Acceleration on Break Below VAL | LIVE | LOW | `speed_picking_up` (exists) |

### Task 5: DSA Schema v1.2.0 Update (MEDIUM PRIORITY)
**Status:** COMPLETE — data_schema_v1.0.md updated 2026-08-29. sample_btc_snapshot.json updated to v1.2.0. All DSA_TASK_007 fields confirmed live.
**Fields LIVE:**
- `weekly_vp.prior_week_poc` (float) — CONFIRMED
- `weekly_vp.two_week_ago_poc` (float) — CONFIRMED
- `prior_day.close` (float) — CONFIRMED
- `volume_spike_at_level` (boolean) — CONFIRMED
**Fields BLOCKED:**
- `weekly_vp.distribution_count` (int) — blocked by VP histogram API
- `weekly_vp.single_print_areas` (array) — blocked by VP histogram API

### Task 6: Engine v4.2.0-p2 Live Validation (HIGH PRIORITY)
**Status:** COMPLETE 2026-08-29 — 0 BUGS FOUND, 2 REFINEMENTS ADDED

### Task 7: Cross-Trader Rule Extraction (HIGH PRIORITY)
**Status:** PHASE 4 COMPLETE — 3 conflicts resolved, 16 NEW entries integrated into compiled_engine.md v4.2.0-p3. DSA_TASK_008 COMPLETE.
**Integrated:**
- Conflict resolutions: Sec 2.8 (retest clarification: C07-E01 vs C07-E02/C06-E02), Sec 3 (cut-and-reverse trap: C10-E03 vs C10-E05)
- P0 Post-Entry Management: NEW Section 12 (10 subsections: C12-E01 through C12-E08, C13-E01, C14-E01-E02, C15-E01-E03)
- P1 Pre-Trade Enhancement: Sec 1 (C05-E03 post-breakout balance, C08-E01 MSB definition, C08-E06 early warning), Sec 2.7 (C06-E02 first test best test), Sec 3 (C05-E02 shallow pullback), Sec 4 (C03-E01 absorption)
**Validation:** Rule 32 adapted for [PRINCIPLE] entries (Rule 32-B). 18 snapshots traced, 13/18 meaningful context shifts (72%). All 6 P1 entries VALIDATED. Zero harmful effects.
**Source:** CryptoCred (Market Structure, Retests, Risk, First Trouble Area, Trade Management), The Flow Horse (MP Course Intro + Tier 2), CrypNuevo (Liquidity/Liquidation — Tier 2 match)
**Method:** Phase 1: Pure extraction. Phase 2: Consolidation. Phase 3: Integration Planning. Phase 4: Integration with 3-snapshot validation. See cross_trader_integration_plan.md.
**Remaining:** 5 GAP entries RESOLVED via DSA_TASK_008 (4 PERMANENTLY BLOCKED, 1 DEFERRED). 11 REJECT entries documented. 28 CONFIRMED entries validate existing engine logic.
**Next action:** New transcript extraction OR live trading card generation. No pending DSA tasks.
**DSA_TASK_008 result:** Zero new fields approved. All 5 GAP entries resolved with documented justification. See `runtime_data/dsa_task_008_gap_fields.md`.
**Parallel sessions:** DSA_TASK_008 COMPLETE. BUG #4 CLOSED 2026-08-31. BUG #5 RECLASSIFIED 2026-09-03. DSA task audit COMPLETE 2026-09-03: 10 of 11 task numbers were ghosts. Cleaned up 2026-09-04. Only active task: DSA_TASK_012 (pre-computed setup_candidates module, APPROVED).
**NOTE:** Workflow corrected 2026-08-30. Previous premature tagging approach discarded. All 4 existing extracts reprocessed.
**Fixes validated:**
| # | Fix | File | Result |
|---|-----|------|--------|
| 1 | JSON path mismatch (VPOC fields) | compiled_engine.md | PASS — paths resolve correctly |
| 2 | prior_day.close false blocker removed | compiled_engine.md | PASS — included in zone map, 0.4% cap |
| 3 | Clustered zone target override | compiled_engine.md | PASS — skips to next major level when reward < 2x risk |
| 4 | Swing cluster stop buffer | compiled_engine.md | PASS — stops below entire cluster, not inside |
| 5 | Funding reset contradiction resolved | entry_timing_triggers.md | PASS — informational only, not hard stop |
| 6 | Schema updated to DSA 1.2.0+ | data_schema_v1.0.md | PASS — all fields documented |
**Patches activated:** VPOC Migration + Exhaustion Gate now LIVE
**Output:** `runtime_data/test_snapshot_v4.2.0-p2_validation.json` (regression test data)
**Archived:** `mts/tests/validation_run_2026-08-29.md` → `mts/archive/validation_run_2026-08-29_ARCHIVED.md` (violates "no new docs" rule — learnings embedded in compiled_engine.md + 00_START_HERE.md instead)

---
## SESSION END LOG

**Date:** 2026-09-02 (Sequenced task list prepared for next session)
**Protocol:** I-07 (JSON Input) + I-03 (Research/Implementation)
**Actions completed:**
| # | Action | Result |
|---|--------|--------|
| 1 | COMPILED_DECISIONS.md created | 56 decisions across 9 categories, single-page reference |
| 2 | COMPILED_DECISIONS_TEST_PLAN.md created | 76 tests across 5 suites (22 quick + 54 full) |
| 3 | Option B activated | Pre-validated screenshot workflow — skip VVP, go straight to analysis |
| 4 | 04_NEXT_SESSION_PROMPT.md fixed | Was stale (2026-09-01). Updated to v4.2.0-p5 with current context |
| 5 | 02b_DECISIONS_LOG.md updated | 2 new entries logged |
| 6 | 03_FILE_INDEX.md updated | +2 files, +1 test file |

**Next session task sequence:**
1. JSON upload → verdict card (immediate)
2. COMPILED_DECISIONS quick check (22 tests, ~25s)
3. COMPILED_DECISIONS full validation (76 tests, ~5min)
4. Chart layout fix instructions (VP Fixed Range, cursor right edge, BB label)
5. Paper trade log template
6. VVP-001 revisions (4 recommendations)

**User says:** "Paste JSON to start Task 1. I will execute the full sequence in order."

---


---

## SPEED GAPS - DEFERRED (added 2026-09-10)

Six gaps identified during the speed concept research. Documentation-only; no engine changes.

| ID | Gap | Tom source | Engine status |
|---|---|---|---|
| GAP-SPEED-MAINT | Speed maintaining for trend continuation | yWO8hVpRXeY T1 | Absent (engine has only "picking up") |
| GAP-SPEED-DECEL | Speed decelerating = pullback warning | G0CiJcuXCRs T4 | Absent |
| GAP-SPEED-BASE | Per-instrument speed baseline | G0CiJcuXCRs T5, YVUcLTsCOZI T5 | Absent (engine uses fixed 1.5x) |
| GAP-SPEED-ZONE | Speed is zone-specific | G0CiJcuXCRs T1 | Absent (engine uses global flag) |
| GAP-SPEED-ABSORB | Speed + absorption compound signal | YVUcLTsCOZI T1 | Absent (proof types separate) |
| GAP-TREND-CLASS | Fast / normal / creeping trend subtypes | 3JqMyzE8jIQ T1 | Absent (state classifier flat) |

## DSA TASKS - SPEED (added 2026-09-10)

| ID | Action | Prerequisite |
|---|---|---|
| DSA_TASK_013 | Emit order-book tick rate | **COMPLETE 2026-09-10.** `order_flow` block added to MarketDataSnapshot. Fields: trades_per_sec, volume_per_sec, baseline_trades_per_sec, baseline_volume_per_sec, trades_ratio, volume_ratio, speed_state, confidence. Three states: accelerating/maintaining/decelerating. Thresholds provisional. Engine does NOT yet read this field (Rule 32 validation required before integration). |
| DSA_TASK_014 | Emit per-instrument speed baseline | **COMPLETE 2026-09-10.** Persisted to `runtime_data/speed_baselines/{symbol}_speed_baseline.json`. Rolling 30d window, max 100 samples, median-based. Fields: historical_baseline_trades_per_sec, historical_baseline_volume_per_sec, historical_baseline_samples, historical_baseline_confidence (HIGH>=20/MEDIUM>=5/LOW<5), speed_vs_historical. First sample: 1 (LOW confidence expected). |

## DSA HYGIENE - SETUP_CANDIDATES (added 2026-09-10)

| ID | Issue | File |
|---|---|---|
| DSA-HYG-001 | ExtraSetupBuilder does not set `rank` field on FVG candidates | SetupCandidatesBuilder.java has it; ExtraSetupBuilder missing |
| DSA-HYG-002 | ExtraSetupBuilder does not filter `rr_sanity=false` candidates | SetupCandidatesBuilder filters; ExtraSetupBuilder does not |
| DSA-HYG-003 | Two speed_picking_up formulas (top-level and candidate-level) use different definitions; consumer must be told which to read | MarketDataSnapshot.java vs SetupCandidatesBuilder.java |
| DSA-HYG-004 | Extract metadata format is not uniform. `| Channel |` table row present in only 12 of 50 extracts; others use header-style `# Channel handle:` or omit the field entirely. Automated attribution audits must handle both formats. | All 50 extracts |

## DSA_TASK_013 IMPLEMENTATION NOTE (added 2026-09-10)

Field: `order_flow` (top-level, every snapshot)
Source: Binance `/fapi/v1/aggTrades` (current 1000 trades) + `/fapi/v1/aggTradesRange` (baseline 20-15 min ago).
Method: trades/sec and volume/sec normalized against a baseline window. Three-state classifier (accelerating / maintaining / decelerating).
Caveat: current window is fixed-count (last 1000 trades); baseline window is fixed-time (5 min). Units are comparable (both rate/sec) but sampling shape is asymmetric. Acceptable for v1; refine if/when production consumption begins.
Engine status: NOT YET READ by compiled_engine.md. Any rule that consumes `order_flow.speed_state` requires Rule 32 (3-snapshot) validation first. Interim: `speed_picking_up` proxy remains the engine's active signal, tagged `[CRYPTO HACK - PROXY, NOT TOM]` in Sec 2.6.



# END OF SPEED APPEND


---

## SESSION SUMMARY - 2026-09-10 - SPEED RESEARCH + DSA_TASK_013/014

**Duration:** Full session. 7 files edited (playbook, behavior, DSA prompt, compiled_engine, 02a, extract banner x2), 2 Java patches (DSA_TASK_013/014), 1 Python patch (BUG-007), 1 schema doc, 2 guest banners, 1 nested attribution note.

**Speed research conclusions:**
- Tom's "speed" = order-book / bid-ask tick interaction rate (not candle range)
- Tom provides no numeric threshold; requires per-instrument baselines
- Three speed states (accelerating, maintaining, decelerating); engine had only 1
- Both prior `speed_picking_up` definitions tagged `[CRYPTO HACK - PROXY, NOT TOM]`

**Files edited:**
| # | File | Change |
|---|------|--------|
| A1 | methodology/playbook.md | Part I Step 3a - Vocabulary Mining loop |
| A2 | system/01_AI_BEHAVIOR.md | Rule 36 |
| A3 | system/01_AI_BEHAVIOR.md | M-032 |
| A4 | DSA_SESSION_PROMPT.md | Keyword-harvesting rule |
| B1 | mts/runtime/compiled_engine.md | [SSOT] speed_picking_up block + Sec 6 row 4 BUG-007 fix |
| C+D | system/02a_CURRENT_STATUS.md | 6 gaps + 2 DSA tasks + 4 hygiene items |
| E1 | extracts/fresh/extract_4P5WAxyPCis_fresh.md | GUEST CONTENT banner |
| E2 | extracts/fresh/extract_RwQBdF9TSvc_fresh.md | GUEST CONTENT banner |
| E3 | extracts/fresh/extract_Vd83oo_geMk_fresh.md | NESTED ATTRIBUTION footnote |
| — | src/main/java/datafeed/BinanceClient.java | aggTradesRange method |
| — | src/main/java/datafeed/MarketDataSnapshot.java | order_flow block + computeFlowStats + updateAndApplyHistoricalBaseline + median |
| — | mts/runtime/math_object_builder.py | BUG-007 split flags |
| — | mts/tests/test_math_object_builder.py | 4 new tests + legacy test update |
| — | runtime_data/data_schema_v1.2.0.md | order_flow section |

**Tests:** 102/102 PASS (up from 98; +4 BUG-007 tests).

**Bugs found & fixed:**
- BUG-007: `hard_stops_compiled.rr_below_threshold` fired on any zone, not top candidate. Split into `any_zone_rr_below_threshold` (advisory) + `top_candidate_rr_below_threshold` (gate).

**Tasks completed:** DSA_TASK_013 (order-flow tick rate), DSA_TASK_014 (per-instrument baseline).

**Tasks logged, not started:**
- Engine integration of `order_flow.speed_state` — requires Rule 32 (3-snapshot) validation
- DSA-HYG-001 (ExtraSetupBuilder missing rank)
- DSA-HYG-002 (ExtraSetupBuilder not filtering rr_sanity)
- DSA-HYG-003 (two speed formulas - consumer must know which)
- DSA-HYG-004 (extract metadata format inconsistency)


---

## SESSION SUMMARY - 2026-09-11 - FIXES + STATE UPDATER + DIVERGENCE MONITOR

**Duration:** Full session. ~20 files touched. Two research cycles (Net Delta definitions; CVD gap root cause), 6 AI responses compared.

**Code fixes landed — status per fix:**

| Fix | Status | Verified? |
|---|---|---|
| BUG-007 hard_stops split (any_zone vs top_candidate) | Live | Verified — checker shows top_candidate_rr_below_threshold correctly |
| BUG-008 proof direction check | Live | 1 of 3 Rule 32 evidence — fired on 06:14 snapshot with `finished_auction=BUY vs SHORT` |
| BUG-009 session label decimal hour | Live | Verified — output shows `us_core` at 16:19 UTC |
| DSA-HYG-001 ExtraSetupBuilder rank | Live | Verified — FVG candidate showed rank=11 |
| DSA-HYG-002 ExtraSetupBuilder rr_sanity filter | Live | **UNVERIFIED — candidate with rr_sanity=false observed in 06:14 output. Filter formula may differ from emitted field. Investigate.** |
| DSA-HYG-006 CVD session scope | Live | Fix landed. Later root cause found to be CoinGlass anchor difference, not our scope. Our scope is correct; cross-platform numeric comparison invalid. |
| net_delta multi-window (1m/5m/15m/1h) | Live | 4 windows present in JSON; legacy net_delta removed |
| cvd_aligned uses nd1m | Patched | **Not re-verified after patch** |

**New tools:**
- `mts/runtime/update_market_state.py` — reads latest snapshot, diffs state, writes current_market_state.md (atomic tmp+rename). Closed ~22h 45min stale gap.
- `divergence_monitor.py` — flags PRICE-CVD DIV, SHORT COVERING, NEW LONGS, LONG CAPIT, SILENT ACCUMULATION from snapshot history. 10-min filter + cross-session skip.

**Research conclusions (confidence levels stated):**
- **Net Long / Net Short** formulas = T2 confirmed. Source: coinglass.com/learn/net-long-short-en (Net Long = Long Openings − Long Closings; Net Short = Short Openings − Short Closings).
- **Net Delta** = T3 proxy only. Best available: `Net Longs − Net Shorts` from Leviathan TradingView script. CoinGlass has no public formula.
- **Volume Delta** = taker buy − taker sell per bar. T2 confirmed.
- **CVD** = cumulative Volume Delta. T2 confirmed.
- Our `net_delta_*` = Volume Delta over N bars, NOT CoinGlass Net Delta. Naming collision documented in schema, not renamed (no external contract).
- CoinGlass chart CVD anchor = **inferred** to be leftmost visible bar (from 3 screenshots at different zooms showing different values). Not documented publicly. Our anchor = 00:00 UTC session, deterministic.

**Extract hygiene:**
- 2 guest banners added (`4P5WAxyPCis`, `RwQBdF9TSvc`)
- 1 nested attribution footnote (`Vd83oo_geMk`)

**Protocol additions (this session):**
- Vocabulary Mining loop — playbook Part I Step 3a
- Rule 36 — vocabulary mining mandatory for corpus searches
- M-032 — intuition-keyword failure logged

**Open items for next session (priority order):**
1. Wire `update_market_state.py` into snapshot workflow (manual → automated)
2. BUG-008 needs 2 more live contradiction snapshots for Rule 32
3. **DSA-HYG-002 investigation** — filter formula vs emitted field mismatch
4. `cvd_aligned` — verify boolean changes correctly after nd1m patch
5. net_delta_* same-minute chart comparison vs CoinGlass Volume Delta
6. State-code emitter (A/B/C/D codes, every minute) — new build
7. Malkans momentum integration — requires research first

**Tests:** 102/102 passing after every change.

---

## DSA-HYG-007 - RECLASSIFIED (2026-09-11 closeout)

Surface observation: 09:09 UTC snapshot showed cvd.slope=falling while
cvd_recent.slope_1h=rising. Investigated over four turns; final verdict:

NOT A BUG. Two fields, two formulas, two meanings - by design.
  cvd.slope = avg-of-avg over 40 bars = acceleration (2nd deriv)
  cvd_recent.slope_1h = endpoint diff over 60 bars = direction (1st deriv)

compiled_engine.md Sections 336-345 explicitly rely on the difference
between the two (three-state reconciliation: recent_shift /
cumulative_dominant / pause). Collapsing formulas would break that logic.

External research (3 AI responses) agreed no vendor standardizes "CVD
slope"; the research preference is for method-explicit names. That is a
naming-clarity item, not a defect. Optional future improvement: add
cvd.slope_method and cvd_recent.slope_1h_method to the snapshot.
Not urgent. Not this session.

Rule 37 does NOT apply (no intended behavior was broken).

---

## SESSION CLOSE - 2026-09-11 evening

### Pipeline architecture (locked this session)

- Java (BinanceDataFeed) is the SOLE Binance client.
  Polls REST for snapshots, streams WebSocket for live data.
- Python (mts_math.py, math_object_builder.py) reads JSON files only.
  Never calls Binance. Never runs a second WebSocket.
- File-based interface: Java writes, Python reads. One-way. No sockets or
  RPC between processes.
- Atomic writes on all runtime files: tmp file + rename.
- Staleness guard: every Java-written file carries written_utc.
- Runtime files whitelisted in DSA_SESSION_PROMPT.md: current_market_state.md,
  session_end_logs.md, state_code.json.

Rationale: two independent Binance feeds would double rate-limit risk and
create sync problems. One producer, one consumer, filesystem as the contract.

### Snapshot workflow (two commands, order matters)

  1. mvn -q exec:java "-Dexec.mainClass=datafeed.Main" "-Dexec.args=snapshot BTCUSDT"
  2. python .\MyTradingSys\runtime\update_market_state.py

Updater reads the newest snapshot file. Run snapshot first, updater second.
No alias, no hook - manual two-command pattern is intentional.

### Phase 2 - StateCodeEmitter (Java)

- Committed: StateCodeEmitter.java (19029 bytes), Main.java +statemachine
  branch, design doc addendums.
- Compile: clean. Never run. Smoke test in flight at session close.
- Next: 90s smoke test -> confirm state_code.json writes -> 24h observation
  -> Rule 32 threshold validation.

### Session length observation (for future planning)

Sessions exceeding ~8 hours showed increased error rate - flip-flopping on
verdicts, over-correction, retractions of verified claims. Plan shorter
blocks or insert explicit verification passes after 6h.

### BUG-008 status

2 of 3 Rule 32 evidence collected. Evidence #3 pending normal cadence -
self-collects on next contradiction snapshot. Do not force it.


---

## 2026-09-13 SESSION — APPARATUS + SSOT + RESEARCH

**Duration:** ~10h. **Files touched:** ~20. **Tests:** 98/98 existing + 8 new (session_state).

### Landed
| # | Fix | Status |
|---|---|---|
| Rule 37 | DSA reads closed bars only (dropFormingBar) | LIVE |
| BUG-011 | math_object_builder reads net_rr_sanity (>=2.0 NET) | LIVE |
| — | mode.ps1 lock check | LIVE |
| — | STATE_CODE STALE >90s flag (live mode) | LIVE |
| — | Materiality gate + firePopup restricted | LIVE |
| — | Lock file `PID TS`, stale>600s auto-clear | LIVE |
| — | Trend override: below_val + CVD falling vs LONG -> WAIT_RR | LIVE (2/3 Rule 32) |
| — | Popup TopMost=false + kill-prior-popup | LIVE |

### New components
| File | Purpose |
|---|---|
| `mts/runtime/session_state.py` | SSOT helper |
| `mts/runtime/session_state.json` | Thesis + watch levels |
| `mts/runtime/session_log.json` | Append-only decisions |
| `mts/runtime/log_decision.py` | One-line logger |
| `mts/runtime/outcome_labeler.py` | Forward-return labeler |
| `mts/runtime/build_mo_cli.py` | Proof-direction helper |
| `DSA_SESSION_PROMPT.md` | First-read entry doc for new sessions |
| `mts/research/apparatus_fixes.md` | Fix log + |
| `mts/research/event_probability_layer_DESIGN.md` | 4-AI research, parked |
| `start_trading_day.ps1` | Apparatus loop |
| `mode.ps1`, `stop_day.ps1`, `show_alert.ps1` | Process control |
| `mts/tests/test_session_state.py` | 8 unit tests, all pass |

### Open
- needs 3rd Rule 32 snapshot (2/3 collected).
- (alignment_pass field unused) parked.
- (proof_direction_details empty in some cards) cosmetic.
- Event probability layer parked until 500+ outcome labels (currently 154).

### Architecture rules reaffirmed
- Java DSA = sole Binance client. Python reads JSON only.
- Candle-close alignment mandatory. Mid-candle reads are category error.
- Deterministic gates stay hard (structure, risk, invalidation).
- Probabilistic layer deferred until data prerequisite met.
