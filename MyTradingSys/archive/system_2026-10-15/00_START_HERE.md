> **SUPERSEDED (2026-10-08).** Frozen history from the September build. For current state read
> `MyTradingSys/research/STATUS.md`, then `MyTradingSys/system/LESSONS_LEARNED.md` (entry order is in CLAUDE.md).
> Where this file disagrees with CLAUDE.md or SURFACE_POLICY.md, those win.

# [BLOCKED] /mnt/agents/temp/ IS FORBIDDEN FOR PROJECT FILES
# The canonical project root is: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\
# Temp contains ephemeral session uploads — ignore everything there.
# ---

# FILE: 00_START_HERE.md
# READ ORDER: 1 of 8 (MUST READ FIRST — NO EXCEPTIONS)
# PURPOSE: Entry point for every new session. One-page quickstart.
# LAST UPDATED: 2026-09-09
# SIZE: ~3KB
# NEXT FILE: 01_AI_BEHAVIOR.md
# PREVIOUS: (none — this is the start)
# ---

# START HERE — MTS v4.2.0-p5
# Date: 2026-09-14
# Status: v4.2.0-p5. Build infra live: Build-Check.ps1 + 5 doc tests + Dump_All chained. CAPABILITIES.md router live. Rule 38 (coordinator prompts need real content). Worker D: check_scalp_preconditions + check_invalidation in mts_math.py, session_state.json v1.1.0, 110 tests. NOT WIRED - Worker F pending. Worker E: probability step-2, 542/816 labels orphaned, redefined label-only, re-run pending. Worker G pending: screenshot validator + compiler. 12 .old archived. Playbook L/M/N removed.
# Canonical path: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\system/00_START_HERE.md

## Boot order: see DSA_SESSION_PROMPT.md section 3
It contains: current read order, apparatus state, SSOT, active thesis, .
This file is now METHODOLOGY REFERENCE only. Section below is stale.


---

## SESSION PROTOCOL — START AND END

### START (Every Session)
1. Read THIS file (00_START_HERE.md)
2. Read 01_AI_BEHAVIOR.md
3. Read 02a_CURRENT_STATUS.md
4. Read 02b_DECISIONS_LOG.md (top entry only — context)
5. Begin work

### END (Every Session — MANDATORY)
1. Read 06_SESSION_END_CHECKLIST.md (includes sign-off template)
2. Run all 7 validation sections
3. Fill the sign-off block
4. If ANY section FAILED → fix errors before closing
5. If ALL PASSED → session clear to close

**No session closes without completing 06_SESSION_END_CHECKLIST.md.**
This prevents the claim errors, fabricated validations, and missing files
that occurred in the 2026-08-29 cross-trader session.

---

## [BLOCKED] COMMON MISTAKES — DO NOT REPEAT

Every new session MUST read this block. These errors corrupt files.

| # | Mistake | Prevention |
|---|---------|------------|
| 1 | Writing files to `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\` instead of `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\` | ALWAYS use the mirror path. The upload/ dir is read-only for raw transcripts. |
| 2 | Using `write_file` or `append` for `.md` files | These tools STRIP NEWLINES (bug M-028). Use ONLY Python `open(path, 'w', encoding='utf-8')` for ALL .md writes. |
| 3 | Forgetting to update `03_FILE_INDEX.md` after creating new files | Every new file MUST be added to the index. Check the index before and after every file creation. |
| 4 | Reading stale `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\` files instead of canonical mirror | The mirror is the ONLY source of truth. Upload/ may contain old versions. |
| 6 | Skipping the numbered read order (00 -> 01 -> 02a -> ...) | The system/ files are numbered for a reason. Read them in order. |
| 8 | Using `/mnt/agents/temp/` for ANY project file | Temp is for session uploads ONLY. It is ephemeral, untracked, and contains stale files from other sessions. ALWAYS use `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\`. |
| 7 | Creating files without checking `05_NORMS.md` naming conventions | All files use snake_case, no spaces, descriptive names. |
| 9 | **Claiming engine bugs without tracing FULL decision path** | The engine uses GENERIC descriptions ("swing_low", "+1sigma"). Schema mismatches are usually NOT runtime bugs. ALWAYS trace: state → zone → entry → stop → target → R:R for 3+ zones before calling anything a bug. |
| 10 | **Treating per-TF structure as a bug** | `structure.1h/15m/5m.swing_low` is INTENTIONAL — better than flat. Match swing TF to zone precision: daily zone → 1h swing, 4H zone → 15m swing, scalp → 5m swing. |
| 11 | **Creating documents instead of fixing source** | Do NOT write validation reports or analysis docs. Fix `compiled_engine.md` directly. Update `02a_CURRENT_STATUS.md` for status. Embed learnings in `00_START_HERE.md`. One source of truth. |
| 12 | **Validate before you fix** | Before claiming a bug or requesting a DSA field, test the CURRENT system against a live snapshot. If it already produces the correct verdict, the "fix" is bloat. (Rule 31) |
| 13 | **No new rule without 3-snapshot proof** | Any proposed engine rule must change a verdict on at least 1 of 3 live snapshots. Rules that pass all 3 unchanged = documentation bloat. Reject them. (Rule 32) |
| 14 | **Research before importing cross-market concepts** | DAX gaps, equity session patterns, forex carry — research whether they apply to crypto 24/7 spot markets BEFORE adding. If the market doesn't close, the concept doesn't transfer. (Rule 34) |
| 15 | **Filing data-quality issues as engine bugs without engine trace** | Before calling ANY data issue an engine bug, trace: data field → engine reference → verdict impact. If the engine doesn't reference the field, it's schema bloat or a DSA issue, NOT an engine bug. BUG #5 was never an engine bug — expanded depth thresholds were never referenced. |
| 16 | **Hardcoding test counts in multiple files** | Test counts are SINGLE SOURCE OF TRUTH: see `mts/tests/UNIT_TEST_PLAN.md` ONLY. Do NOT write "X/Y tests pass" in any other file. When test counts change, update UNIT_TEST_PLAN.md and nowhere else. All other files must reference it indirectly (e.g., "math layer compiled — see UNIT_TEST_PLAN.md for current count"). This prevents the drift that corrupted 9 files in 2026-09-02. |
| 17 | **Creating a new file before searching existing files** | Before creating ANY file, search existing files for the topic. If it exists, edit that file. Only create new files for genuinely new topics. |

---

## WHERE TO WRITE WHAT — CHEAT SHEET

| If you need to... | Write to... | Update index? |
|-------------------|-------------|---------------|
| Generate trading card | `mts/cards/BTCUSDT_YYYY-MM-DD_HHMM.md` | Yes — `03_FILE_INDEX.md` |
| Log a system decision | `system/02b_DECISIONS_LOG.md` (append to TOP) | No |
| Update what's working now | `system/02a_CURRENT_STATUS.md` | No |
| Add new trading rule | `mts/conditions/[name]_rules.md` | Yes — `03_FILE_INDEX.md` + `02a` |
| Record DSA bug | `runtime_data/data_schema_v1.0.md` (update schema doc) | Yes — `03_FILE_INDEX.md` |
| End session notes | `system/00_START_HERE.md` (update date + next focus) | No |
| Research finding | `mts/research/[topic]_evidence.md` or `_recommendations.md` | Yes — `03_FILE_INDEX.md` |
| Archive superseded file | `mts/archive/[name]_ARCHIVED.md` | Yes — `03_FILE_INDEX.md` + `02b` |

---

## START NEXT SESSION — READ THESE FILES FIRST

| # | File | Why | Read Order |
|---|------|-----|------------|
| 1 | `system/00_START_HERE.md` | This file — entry point | 1 of 8 |
| 2 | `system/01_AI_BEHAVIOR.md` | Behavior rules + Section 14 JSON workflow | 2 of 8 |
| 3 | `system/02a_CURRENT_STATUS.md` | System status, what's working, active bugs | 3 of 8 |
| 4 | `mts/runtime/compiled_engine.md` | 19.4KB decision tables — all rules cached | Load per JSON |
| 5 | `mts/runtime/math_object_builder.py` | DSA snapshot → math_object compiler | Load per JSON |

**After reading these:** Paste JSON or screenshot. math_object_builder compiles → judgment layer generates card from compiled_engine.md + math_object (2-3 tool calls, <30 sec). AI never recomputes math.

---

## LAST SESSION SUMMARY (2026-08-31 — VVP-001 Test)

**What happened:** VVP-001 Visual Validation Protocol test suite executed against 3 live screenshots (15m, 3m, 6H BTCUSDT). 20 tests across 5 sections (A-E) evaluated. 54 total evaluations.
- **31 PASS:** Cursor position rules (A1-A5), CVD/Delta/OI presence (B3-B5), RSI presence (B6), clutter limits (E1-E2).
- **12 FAIL:** VWAP missing from ALL screenshots (B1 x3), VP missing from 3m/6H (B2 x2), no proof patterns visible (C1-C4).
- **11 CANNOT TEST/CONFIRM/NA:** Historical cursor position (A2), cross-TF CVD summation (D1 — protocol error, CVD is cumulative), missing 1H screenshot (D2), missing DSA JSON (D3), 6H too coarse for proof detection (C1-C4).
- **Critical finding:** VWAP is Tier 1 essential per VVP-001 but missing from all screenshots. Volume Profile missing from 3m and 6H. No zone markings (POC/VAH/VAL) on any chart — blocks proof detection.
- **6 issues logged:** VWAP missing (CRITICAL), VP missing (HIGH), no zone markings (MEDIUM), test D1 technically incorrect (MEDIUM), BB is Tier 4 (LOW), insufficient screenshots (LOW).
- **4 protocol revisions recommended:** Add Section 2.6 (zone markings required), revise test D1 (compare trend direction not sum), add Tier 1.5 (zone annotations), clarify C1-C4 scope.
- **Files created:** vvp_test_results_20260831.md (326 lines), vvp_sc_01_15m.png, vvp_sc_02_3m.png, vvp_sc_03_6h.png.
- **03_FILE_INDEX.md updated:** +7 research entries.
- **No engine modifications.** No DSA changes. No new bugs.

**Current state:** v4.2.0-p4, VVP-001 Phase 1.0.0 test COMPLETE, 6 patches LIVE, 0 open bugs, math layer COMPILED, cross-trader Phase 3 COMPLETE / Phase 4 READY.

**For full details:** See `mts/research/vvp_test_results_20260831.md`.

---

## LAST SESSION SUMMARY (2026-08-31)

**What happened:** Cross-Trader Phase 3: Integration Planning COMPLETE. All 80 consolidated entries (C01-E01 through C20-E01) classified via 5-step check against compiled_engine.md. Revalidation confirmed zero reclassifications needed.
- **28 CONFIRMED:** Already covered by engine logic (descriptive VP, structure vs flow, retest mechanics, MSB context, confluence, swing quality, R:R trade-offs, invalidation linkage, LVN zones).
- **33 NEW:** Genuinely new concepts ready for Phase 4 integration. Largest cluster: post-entry trade management (C12-C15) — engine currently stops at entry verdict. Also: absorption detection, pullback depth, compression signals, MSB definition, FTA framework, dynamic R:R.
- **5 GAP:** Require new DSA fields (composite profiles, balance duration, test count, historical behavior, Fibonacci retracements).
- **3 CONFLICT:** Require human resolution before integration (retest confirmation myth vs. entry preference; cut-and-reverse trap vs. failed MSB reversal).
- **11 REJECT:** Out of engine scope (psychology, portfolio, position sizing, leverage, platform variance).
- **Key finding:** Post-entry trade management is the engine's largest functional gap. 14 of 33 NEW entries are management-related.
- **No engine modifications made.** No new bugs found. No DSA changes needed.
- Status files updated: 02a_CURRENT_STATUS.md, 00_START_HERE.md, cross_trader_integration_plan.md (Phase 3 section appended).

**Current state:** v4.2.0-p3, 6 patches LIVE, 2 open bugs, 0 open DSA tasks, math layer COMPILED, cross-trader Phase 3 COMPLETE.

**For full details:** See `system/02a_CURRENT_STATUS.md` (system status) and `mts/research/cross_trader_integration_plan.md` Section 3 (Phase 3 output).

---

## LAST SESSION SUMMARY (2026-08-29)

**What happened:** CryptoCred inqHN8q57X4 (Retests) extracted — 12 rules, 6 CONFIRM, 6 CLARIFY, 0 BLOCKED. Raw transcript filesystem quirk documented in extract file NOTE. Cross-trader status: 4/7. 0 bugs found.
- Added validation discipline to COMMON MISTAKES (#12-14): validate before fix, 3-snapshot proof, research cross-market concepts.
- BUG #3 and #6 marked CLOSED (were false alarms — engine handles them correctly).
- Task 2 (Post-Breakdown Retest) reclassified: NOT "pending patch" but "EXTRACTION UNCLEAR — parked in `unclear_extractions.md`."
- Task 3 (Prior Day H/L + London Range) CANCELLED — same reason as DSA_TASK_008 (not a Tom concept).
- DSA_TASK_008 CANCELLED: DAX gap concept does not apply to 24/7 crypto.
- 7 stale research files archived. 4 active research files remain.
- M-029, M-030 documented.

**Current state:** 6 patches LIVE, 0 bugs, 0 open DSA tasks. Engine validated on 10 live snapshots.

**For full details:** See `system/04_NEXT_SESSION_PROMPT.md` (session handoff) and `system/02a_CURRENT_STATUS.md` (system status).

---

## WHAT HAPPENED LAST SESSION (2026-08-28)

### 6 Immediate Fixes Deployed (FIX_006)
| # | Fix | File | Impact |
|---|-----|------|--------|
| 1 | JSON path mismatch | compiled_engine.md | VPOC fields now read `weekly_vp.prior_week_poc` / `two_week_ago_poc` |
| 2 | prior_day.close false blocker | compiled_engine.md | Added to zone map with 0.4% cap — data already live |
| 3 | Clustered zone target override | compiled_engine.md | If next POC < 2x stop distance → skip to next major level |
| 4 | Swing cluster stop buffer | compiled_engine.md | If swing lows within 0.1% → stop below entire cluster |
| 5 | Funding reset contradiction | entry_timing_triggers.md | Hard Stop #3 → "degrades confidence, does NOT abort" |
| 6 | Schema v1.0 updated | data_schema_v1.0.md | Added conditions, trade_flow, structure, weekly_vp updates, prior_day.close, cvd_recent, volume_spike_at_level |

### HTF Structure Audit COMPLETE (HTF_PATCH_001)
| Patch | Status | Tom Basis |
|-------|--------|-----------|
| Single Print = Target, Not Entry | LIVE | "single prints are target areas... they exit the market. But they don't enter." (Fj4FDZQxw0I T5) |
| Double Distribution Breakdown Target | LIVE (visual flag) | "What information does this double distribution give me?" (-dMWA_bbm3o T4) |
| Acceleration on Break Below VAL | LIVE | "Very often it accelerates at first." (YmygDgtoxO8 T1) |
| VPOC Migration Trend | LIVE [ACTIVATED 2026-08-29] | "Rising VPOCs indicate stable bullish structure." (KEe_CWHyuSg T1) |
| Exhaustion Gate for CT | LIVE [ACTIVATED 2026-08-29] | "absolute exhaustion is seen with a volume spike." (KEe_CWHyuSg T4) |
| Prior Day Close as Zone | LIVE | "yesterday's closing price" (rrHj24GSR6M T4) |

**Audit output:** `mts/research/htf_structure_audit_2026-08-28.md` (~27KB, 47 extracts searched, 28 claims, 8 engine gaps, 9 DSA schema changes)
**DSA task completed:** DSA_TASK_007 — All 4 fields confirmed live: prior_week_poc, two_week_ago_poc, prior_day.close, volume_spike_at_level

### Engine Optimization v4.2.0 Deployed (ENGINE_OPT_002)

| Optimization | Before | After | Status |
|-------------|--------|-------|--------|
| **Directional filter** | Evaluated all zones both directions | Reversion-only based on price vs POC | [COMPLETE] LIVE |
| **Distance cap** | Flat 0.3% | Per-zone-type: weekly 0.5%, daily/4H/PF 0.4%, swing 0.3%, VWAP/FVG 0.2% | [COMPLETE] LIVE |
| **Zone-to-zone confluence** | Cluster within $100 of price | Zones within 0.3% of EACH OTHER, +10/+20 confidence | [COMPLETE] LIVE |
| **R:R sanity pre-filter** | Full calc for all zones | Gross <1.5 skipped before full calc | [COMPLETE] LIVE |
| **Single best output** | Multiple or generic WAIT | Rank by R:R * confluence * tf_weight, output top 1 | [COMPLETE] LIVE |
| **C+ verdict band** | C (40-69) only | C+ (55-69) for conditional setups with alerts + trigger spec | [COMPLETE] LIVE |
| **Zone map expansion** | 6 zone types | 11 zone types: added swing highs/lows, prior day VAH/VAL/POC | [COMPLETE] LIVE |

### DSA Bugs Found & Status

| Bug | Status | Impact |
|-----|--------|--------|
| **BUG #1: prior_day = daily_vp** | **FIXED** [OK] | Prior day now shows 2026-08-25 data (POC 80,810) vs daily (POC 78,330) |
| **BUG #2: Book depth 66.73 vs ~7.24** | **PARTIAL FIX** [WARN] | DSA changed to `limit=1000` + `mid_price`. Standard ratio now 3.41. Expanded still identical values. |
| **BUG #3: swing_low > low** | **CLOSED** [OK] | Definition resolved — `swing_low` is structural (swing TF matched to zone precision), not candle low. Engine handles correctly. |
| **BUG #4: CVD vs trade_flow contradiction** | **CLOSED** [OK] | Engine patched v4.2.0-p4: Proof table now references trade_flow.net_delta + cvd_recent.slope_1h. Added "recent_shift" resolution principle. Full analysis in `mts/research/bug_004_investigation.md`. |
| **BUG #5: order_book_depth_expanded identical** | **RECLASSIFIED** [INFO] | NOT an engine bug. Expanded depth thresholds are dead schema weight — engine uses `bid_ask_ratio` only. Never referenced in proof evaluation. Correct action: remove from schema or leave as DSA debug. No engine change needed. |
| **BUG #6: VWAP band label Unicode** | **CLOSED** [OK] | Engine reads band keys generically (not by label). DSA output format stable. No runtime impact. |

**Note:** 0 bugs remain open. All prior bugs resolved. |

### Trading Cards Generated (13 total)

| # | File | Timestamp | Verdict |
|---|------|-----------|---------|
| 1 | BTCUSDT_2026-08-26_0915.md | 09:15 UTC | WAIT C (55/100) |
| 2 | BTCUSDT_2026-08-26_1003.md | 10:03 UTC | WAIT C (60/100) |
| 3 | BTCUSDT_2026-08-26_1100.md | 11:00 UTC | WAIT C (60/100) |
| 4 | BTCUSDT_2026-08-26_1100_compact.md | 11:00 UTC | WAIT C (60/100) — compact format test |
| 5 | BTCUSDT_2026-08-26_1108.md | 11:08 UTC | WAIT C (55/100) |
| 6 | BTCUSDT_2026-08-26_1303.md | 13:03 UTC | WAIT C (60/100) |
| 7 | BTCUSDT_2026-08-26_1343.md | 13:43 UTC | WAIT C (55/100) |
| 8 | BTCUSDT_2026-08-27_1923.md | 19:23 UTC | WAIT C (55/100) — validation run |
| 9 | BTCUSDT_2026-08-28_0444.md | 04:44 UTC | WAIT C (55/100) — v4.1.4 patch validation |
| 10 | BTCUSDT_2026-08-28_0809.md | 08:09 UTC | WAIT C — v4.2.0 optimization validation |
| 11 | BTCUSDT_2026-08-31_0727.md | 07:27 UTC | C+ (60/100) Scalp Short at VWAP +2s |
| 12 | BTCUSDT_2026-08-31_2127.md | 21:27 UTC | C+ (58/100) CT Short at post-funding VAH cluster |
| 13 | BTCUSDT_2026-09-01_0521.md | 05:21 UTC | C+ (65/100) CT Short at 4H VAH cluster 78,997-79,128 |

---

## SESSION TRANSFER MECHANISM

### When Closing:
1. AI outputs: "Session closing. Modified files: [list]"
2. AI outputs: "Next session: read 00_START_HERE.md FIRST, then 01_AI_BEHAVIOR.md, then 02a_CURRENT_STATUS.md"
3. AI updates: `00_START_HERE.md` date + status line, `02a_CURRENT_STATUS.md` if components changed, `02b_DECISIONS_LOG.md` if decisions made, `03_FILE_INDEX.md` if files added/removed

### When Starting New Session:
1. AI reads: `00_START_HERE.md` FIRST (this file — 1 page, <1 sec)
2. AI reads: `01_AI_BEHAVIOR.md` SECOND (behavior rules + Section 14 workflow)
3. AI reads: `02a_CURRENT_STATUS.md` THIRD (system status + active bugs)
4. JISHU pastes: JSON snapshot from DSA or screenshot
5. AI loads: `04_PER_JSON_GUIDE.md` + condition files on-demand per analysis
6. AI generates: trading card

Rule files (5 conditions + 1 card) are NOT read at session start.
They are loaded on-demand per the workflow in 01_AI_BEHAVIOR.md Section 14.
This keeps startup to 3 reads + 1 JSON paste.

---

## QUICK REFERENCE — .SYSTEM/ FILE CHAIN

| Order | File | One-Line Purpose |
|-------|------|------------------|
| 1 | 00_START_HERE.md | Entry point + common mistakes + where to write |
| 2 | 01_AI_BEHAVIOR.md | Behavior bible + mistake history + JSON workflow |
| 3 | 02a_CURRENT_STATUS.md | System health + active components + file inventory |
| 4 | 02b_DECISIONS_LOG.md | Why the system is what it is — append only |
| 5 | 03_FILE_INDEX.md | Hierarchical map of ALL project files |
| 6 | 04_PER_JSON_GUIDE.md | Per-JSON load order + abbreviations |
| 7 | 05_NORMS.md | Folder conventions, naming rules, archival rules |
| 18 | **PowerShell interpolation trap** (`dump_$mod.md`) | Use `${mod}` or `$($mod)` in double-quoted strings. |
| 19 | **Python backslash warnings in strings** | Prefix Windows paths with `r` or use forward slashes. |
| 20 | **Manual long pastes causing truncation** | Generate modular dumps and paste `dump_core.md` instead of individual files. |
| 21 | **Editing prompts with PowerShell heredocs** | Use Python `open(...).write(...)` instead of PowerShell multi-line strings. |

---

---

## LAST SESSION SUMMARY (2026-09-09)

**What happened:** Migration from Kimi download completed.
- Replaced 22 files (runtime, conditions, data, tests, research, methodology) with latest versions.
- Backed up old versions as .old files in the same directories.
- Moved 50 fresh Tom extracts from mts/extracts/fresh/ to extracts/fresh/ (canonical).
- Copied 8 cross-trader extracts to mts/extracts/cryptocred/extracted/ and the_flow_horse/extracted/.
- Copied dsa_developer_implementation_tasks.md to mts/research/.
- Updated reflexivity_log.md.
- Updated 03_FILE_INDEX.md, 05_NORMS.md, 02a_CURRENT_STATUS.md, 02b_DECISIONS_LOG.md.
- Math tests verified: 98/98 pass.

**Current state:** v4.2.0-p5, 0 open bugs, 0 open DSA tasks, math layer COMPILED.

# END
