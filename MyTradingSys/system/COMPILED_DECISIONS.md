# COMPILED DECISIONS — MTS v4.2.0-p5
# Purpose: Single-page reference of all system decisions by category
# Date: 2026-09-05
# Canonical: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\system/COMPILED_DECISIONS.md
# ---

## TABLE OF CONTENTS
1. Architecture Decisions
2. Engine Decisions
3. Data/DSA Decisions
4. Cross-Trader Decisions
5. Bug Resolutions
6. Performance Decisions
7. Workflow Decisions
8. Hard Rules (Non-Negotiable)
9. Active Options (On the Table)

---

## 1. ARCHITECTURE DECISIONS

| # | Date | Decision | Why | Status |
|---|------|----------|-----|--------|
| A1 | 2026-08-26 | **Scanner v2.0 RETIRED** | 66KB Python monolith had init race, type mismatch, invented thresholds. compiled_engine.md (7.3KB) + AI reasoning is faster, more adaptable, handles visual validation. | LIVE |
| A2 | 2026-08-26 | **Architecture: Prompt-Embedded + Quickref** | Merged 4 integration files into 01_AI_BEHAVIOR.md Section 14. Reduced per-JSON reads from 11 to 3-7 files. | LIVE |
| A3 | 2026-08-26 | **3-Layer Architecture** | DSA Snapshot → math_object_builder → math_object → AI Judgment Layer → Formatter → Card. AI never recomputes math. | LIVE |
| A4 | 2026-08-27 | **Navigation overhaul v4.1.3** | system/ files renamed 00-05 to force read order. state.md split into 4 focused files. Linked-list headers added. | LIVE |
| A5 | 2026-08-30 | **Compiled engine: 93% compileable** | 55 functions mapped. 51 = deterministic compiled code. 2 = AI-only visual flags. 2 = hybrid. Test plan written then superseded by compiled math layer. | REFERENCE |
| A6 | 2026-08-31 | **Math layer extracted** | mts_math.py (9 functions) + math_object_builder.py. 98/98 tests PASS. AI never recomputes distance, R:R, tier, or confluence. | LIVE |

---

## 2. ENGINE DECISIONS

| # | Date | Decision | Impact | Status |
|---|------|----------|--------|--------|
| E1 | 2026-08-28 | **ENGINE_OPT_001: 5 patches deployed** | Multi-TF zone priority, CVD contradiction resolution, zone sub-states, screenshot TF guidance, OI trend confirmation. | LIVE |
| E2 | 2026-08-28 | **ENGINE_OPT_002: v4.2.0 optimization** | Directional filter + per-zone distance cap + confluence scoring + R:R pre-filter + single best output + C+ verdict band (55-69). | LIVE |
| E3 | 2026-08-28 | **HTF_PATCH_001: 6 patches** | Single Print = Target, VPOC Migration, Double Distribution, Exhaustion Gate, Prior Day Close, Acceleration on VAL break. | LIVE |
| E4 | 2026-08-29 | **Malkans RSI 40/60 integrated** | White line = price RSI, blue = SMA. 60 = overbought, 40 = oversold. Cross-referenced with Tom. | SUPERSEDED 2026-09-18: VVP-001 Tier 3 demoted RSI; removed from default layout. RSI is not Tom-validated. |
| E5 | 2026-08-31 | **BUG #4 fix: CVD/flow resolution** | "recent_shift" principle — when cvd_recent aligns with trade_flow, cumulative CVD demoted to context. Proof table updated. | LIVE |
| E6 | 2026-08-31 | **Post-entry management (Section 12)** | 10 subsections: evidence-based management, timeframe, both sides, level performance, time expiry, acceptance = failure, dead zone, dynamic R:R, profit taking, BE stop skepticism. | LIVE |
| E7 | 2026-08-31 | **Cross-trader integration** | 16 NEW entries integrated: 3 conflict resolutions + 10 P0 post-entry + 6 P1 pre-trade. Traceability matrix 18 rows. | LIVE |

---

## 3. DATA / DSA DECISIONS

| # | Date | Decision | Impact | Status |
|---|------|----------|--------|--------|
| D1 | 2026-08-26 | **DSA v1.2.0 deployed** | Minimal JSON (~52 fields), fixed 8-session framework, DST-correct US open, internal computations. | LIVE |
| D2 | 2026-08-28 | **DSA_TASK_003 COMPLETE** | cvd_recent object added (slope_1h, slope_4h, delta_1h, delta_4h). cvd_trade_flow_aligned flag. Depth monotonicity check. | LIVE |
| D3 | 2026-08-28 | **DSA_TASK_007 COMPLETE** | 4 fields confirmed live: prior_week_poc, two_week_ago_poc, prior_day.close, volume_spike_at_level. | LIVE |
| D4 | 2026-08-29 | **DSA_TASK_008 CANCELLED** | DAX gap concept rejected — spot crypto trades 24/7, no closure = no gap mechanism. | CLOSED |
| D5 | 2026-08-31 | **DSA_TASK_008 (GAP fields) COMPLETE** | 5 GAP entries: 4 PERMANENTLY BLOCKED, 1 DEFERRED. 0 new fields approved. Schema stays v1.2.0. | CLOSED |
| D6 | 2026-09-03 | **BUG #5 RECLASSIFIED** | NOT an engine bug. Expanded depth thresholds never referenced by engine. Prior "documentation" fix was theater — removed. Process rule added: trace data field → engine reference → verdict impact before filing. | RECLASSIFIED |
| D7 | 2026-08-29 | **Session timing research VALIDATED** | 10 SR rules: 1 approved (SR-007 funding), 9 rejected. DSA v1.2.0 emits 4 session fields. No hard rules in engine. | LIVE |

---

## 4. CROSS-TRADER DECISIONS

| # | Date | Decision | Impact | Status |
|---|------|----------|--------|--------|
| C1 | 2026-08-29 | **Cross-trader research LAUNCHED** | Extract from CryptoCred, The Flow Horse, CrypNuevo to clarify/confirm/fine-tune MTS engine. | COMPLETE |
| C2 | 2026-08-30 | **Workflow corrected** | Premature tagging discarded. New 4-phase: Pure Extraction → Consolidation → Integration Planning → Integration. | LIVE |
| C3 | 2026-08-30 | **7/7 transcripts extracted** | 85 rules (CT-001 to CT-085). All reprocessed to pure format (Source GPS + quotes only, zero tags). | COMPLETE |
| C4 | 2026-08-31 | **Phase 3 COMPLETE** | 80 entries classified: 28 CONFIRMED, 33 NEW, 5 GAP, 3 CONFLICT, 11 REJECT. | COMPLETE |
| C5 | 2026-08-31 | **Phase 4 COMPLETE** | 16 entries integrated (10 P0 + 6 P1). 3 conflicts resolved. Rule 32-B: 13/18 meaningful context shifts (72%). | COMPLETE |
| C6 | 2026-08-31 | **Hard rule: AI never picks price levels** | Targets, stops, entries, zones must come from Tom transcripts only. No fabrication, no inference. | LIVE |

---

## 5. BUG RESOLUTIONS

| # | Bug | Date | Resolution | Status |
|---|-----|------|------------|--------|
| B1 | prior_day = daily_vp | 2026-08-26 | FIXED — Prior day now shows correct date (POC 80,810) vs daily (POC 78,330). | CLOSED |
| B2 | Book depth 66.73 vs ~7.24 | 2026-08-28 | PARTIAL FIX — DSA changed to limit=1000 + mid_price. Standard ratio now 3.41. Expanded still identical. | CLOSED |
| B3 | swing_low > low | 2026-08-28 | CLOSED — Definition resolved. swing_low is structural (swing TF matched to zone precision), not candle low. | CLOSED |
| B4 | CVD vs trade_flow contradiction | 2026-08-31 | CLOSED — Normal market behavior, not bug. Engine patched: "recent_shift" principle added. | CLOSED |
| B5 | order_book_depth identical | 2026-08-31 | CLOSED — limit=100 covers ~0.12%. Engine uses bid_ask_ratio only. Documented in schema. | CLOSED |
| B6 | VWAP band label Unicode | 2026-08-28 | CLOSED — Engine reads band keys generically. No runtime impact. | CLOSED |

---

## 6. PERFORMANCE DECISIONS

| # | Date | Decision | Metric | Status |
|---|------|----------|--------|--------|
| P1 | 2026-08-26 | **Compact card mode** | Chat output reduced 65% (9KB → 3KB). Full card saved to disk. | LIVE |
| P2 | 2026-08-26 | **Compiled engine** | 164KB rules → 7.3KB compiled. Per-JSON: 3 tool calls, <30 sec. | LIVE |
| P3 | 2026-08-26 | **JSON-only resolution** | 0 file loads, <1s analysis, ~8,500 tokens saved. | LIVE |
| P4 | 2026-08-26 | **System cache** | MTS_CACHE loads all 10 files in 1 call. | LIVE |
| P5 | 2026-08-31 | **Math layer compiled** | 98/98 tests PASS. AI never recomputes math. | LIVE |
| P6 | 2026-09-01 | **Option B: Pre-validated screenshot** | Skip VVP validation (assume layout correct). Go straight to price action analysis. Saves 1-2 min per screenshot. | **ON TABLE** |

---

## 7. WORKFLOW DECISIONS

| # | Date | Decision | Impact | Status |
|---|------|----------|--------|--------|
| W1 | 2026-08-26 | **Session handoff simplified** | Old handoff (44 lines, stale refs) → new handoff (88 lines, 3-file upload, operational focus). | LIVE |
| W2 | 2026-08-27 | **Temp directory FORBIDDEN** | Canonical root is C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\. Temp is for session uploads ONLY. | LIVE |
| W3 | 2026-08-27 | **File index hygiene** | Ghost files removed. 7 stale research files archived. 4 active remain. | CLEAN |
| W4 | 2026-08-28 | **No new docs for fixes** | Do NOT write validation reports. Fix compiled_engine.md directly. Update 02a for status. | LIVE |
| W5 | 2026-08-30 | **4-phase cross-trader workflow** | Pure Extraction → Consolidation → Integration Planning (5-step check) → Integration (3-snapshot validation). | LIVE |
| W6 | 2026-08-31 | **Parallel session prompts** | BUG HUNT + DSA_TASK_008 prompts created then merged into 04_NEXT_SESSION_PROMPT.md archived sections. | ARCHIVED |

---

## 8. HARD RULES (NON-NEGOTIABLE)

H1, H6 and H7 are SUPERSEDED 2026-10-13 (operator): numbers may be OURS (our judgement or tuned on DEV, checked once out of sample); see PROJECT_VISION DIRECTION UPDATE 2026-10-13.

| # | Rule | Source | Date |
|---|------|--------|------|
| H1 | **AI never picks price levels** | User rejection of sys_AI suggestion | 2026-08-30 |
| H2 | **AI never recomputes math** | math_object_builder deployment | 2026-08-31 |
| H3 | **Validate before fixing** | Rule 31 — test current system before claiming bugs | 2026-08-29 |
| H4 | **No new rule without 3-snapshot proof** | Rule 32 — must change verdict on 1+ of 3 live snapshots | 2026-08-29 |
| H5 | **Research before importing cross-market concepts** | Rule 34 — DAX gaps, equity sessions don't apply to crypto 24/7 | 2026-08-29 |
| H6 | **Tom transcripts = sole source of truth** | All price levels, rules, thresholds from extracted videos only | 2026-08-07 |
| H7 | **No fabrication, no inference, no reasonable defaults** | If unclear, FLAG and SET ASIDE | 2026-08-30 |

---

## 9. ACTIVE OPTIONS (ON THE TABLE)

| # | Option | Description | Trigger |
|---|--------|-------------|---------|
| O1 | **Paste JSON snapshot** | Fresh DSA JSON → math_object_builder → verdict. Fastest. | User pastes JSON |
| O2 | **Pre-validated screenshot (Option B)** | Skip VVP validation. Assume cursor at right edge + Fixed Range VP + CVD Line. Go straight to price action. | User uploads image |
| O3 | **Paper trade log template** | Create `mts/cards/paper_trade_log_template.md` for Phase 5 tracking. | User says "paper trade log" |
| O4 | **VVP-001 revisions** | Implement 4 protocol recommendations from test results. | User says "revise VVP" |
| O5 | **New transcript extraction** | Upload raw transcript → pure format extraction. | User uploads .txt |

---

## DECISION COUNT SUMMARY

| Category | Count |
|----------|-------|
| Architecture | 6 |
| Engine | 7 |
| Data/DSA | 7 |
| Cross-Trader | 6 |
| Bug Resolutions | 6 |
| Performance | 6 |
| Workflow | 6 |
| Hard Rules | 7 |
| Active Options | 5 |
| **TOTAL** | **56** |

---
# END
