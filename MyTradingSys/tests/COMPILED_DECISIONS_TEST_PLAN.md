# COMPILED_DECISIONS TEST PLAN — v1.0.0
# Purpose: Validate all 56 system decisions across 9 categories
# Date: 2026-09-02
# Status: ACTIVE
# Canonical path: /mnt/agents/output/upload_mirror/mts/tests/COMPILED_DECISIONS_TEST_PLAN.md
# ---

# PRINCIPLE: Every decision in COMPILED_DECISIONS.md must be testable.
#            A decision without a test is a decision without enforcement.
#            Tests are deterministic: same input = same output, always.

---

## TEST ARCHITECTURE

### Three Test Types

| Type | Purpose | Scope | Frequency |
|------|---------|-------|-----------|
| **Consistency Tests** | Verify decisions are consistent across all files | Cross-file reference checks | Every session |
| **Implementation Tests** | Verify decisions are implemented in engine/code | Engine logic, math layer, schema | After every engine edit |
| **Enforcement Tests** | Verify hard rules are enforced by AI behavior | Behavior rules, output format | Random spot-checks |

---

## SUITE 1: CONSISTENCY TESTS (Cross-File Validation)

### TEST 1.1: Decision Count Match
**Purpose:** COMPILED_DECISIONS.md count matches actual decisions in 02b_DECISIONS_LOG.md

| Test | Action | Expected | Why |
|------|--------|----------|-----|
| 1.1.1 | Count entries in 02b_DECISIONS_LOG.md (2026-08-26 to 2026-09-02) | 10 entries | All decisions logged |
| 1.1.2 | Sum category counts in COMPILED_DECISIONS.md | 56 total | 6+7+7+6+6+6+6+7+5 |
| 1.1.3 | Verify each 02b entry appears in COMPILED_DECISIONS.md | 100% match | No orphan decisions |
| 1.1.4 | Verify each COMPILED decision has 02b source | 100% match | No fabricated decisions |

**Fail condition:** Any mismatch = decision tracking broken. Fix 02b or COMPILED first.

### TEST 1.2: Version Consistency
**Purpose:** All files reference same engine version

| Test | File | Expected Version | Field |
|------|------|-----------------|-------|
| 1.2.1 | 00_START_HERE.md | v4.2.0-p5 | Status line |
| 1.2.2 | 02a_CURRENT_STATUS.md | v4.2.0-p5 | Header |
| 1.2.3 | 03_FILE_INDEX.md | v4.2.0-p5 | Header |
| 1.2.4 | compiled_engine.md | v4.2.0-p5 | First line |
| 1.2.5 | COMPILED_DECISIONS.md | v4.2.0-p5 | Header |
| 1.2.6 | 02b_DECISIONS_LOG.md (latest) | v4.2.0-p5 | Reference |

**Fail condition:** Any version mismatch = partial deployment. All files must match.

### TEST 1.3: Bug Status Consistency
**Purpose:** Bug status is consistent across all files

| Test | File | Expected | Field |
|------|------|----------|-------|
| 1.3.1 | 00_START_HERE.md | "0 open bugs" | Status line |
| 1.3.2 | 02a_CURRENT_STATUS.md | "0 open bugs" | Task 7 |
| 1.3.3 | COMPILED_DECISIONS.md | All 6 bugs CLOSED | Bug Resolutions table |
| 1.3.4 | compiled_engine.md | No BUG markers | Search for "BUG #" |

**Fail condition:** Any file shows open bug = status tracking broken.

### TEST 1.4: Cross-Trader Status Consistency
**Purpose:** Cross-trader completion status is consistent

| Test | File | Expected | Field |
|------|------|----------|-------|
| 1.4.1 | 02a_CURRENT_STATUS.md | "Phases 1-4 COMPLETE" | Task 7 |
| 1.4.2 | cross_trader_integration_plan.md | "Phase 4: COMPLETE" | Status table |
| 1.4.3 | COMPILED_DECISIONS.md | "Phases 1-4 COMPLETE" | Cross-Trader table |
| 1.4.4 | 00_START_HERE.md | "Cross-trader: Phases 1-4 COMPLETE" | Status line |

**Fail condition:** Any file shows incomplete = integration tracking broken.

### TEST 1.5: Math Test Count Consistency
**Purpose:** Math test count is consistent

| Test | File | Expected | Field |
|------|------|----------|-------|
| 1.5.1 | 02a_CURRENT_STATUS.md | "98/98 PASS" | Tests line |
| 1.5.2 | 00_START_HERE.md | "98/98 tests" | Math layer line |
| 1.5.3 | COMPILED_DECISIONS.md | "98/98 PASS" | Performance table |
| 1.5.4 | Actual test run | 98 PASS | pytest output |

**Fail condition:** Documentation says 98 but actual run shows different = drift.

---

## SUITE 2: IMPLEMENTATION TESTS (Engine & Code)

### TEST 2.1: Architecture Decisions Implemented

| Decision | Test | How to Verify | Expected |
|----------|------|-------------|----------|
| A1: Scanner retired | 2.1.1 | Check mts/runtime/ for scanner.py | File does NOT exist |
| A2: 3-layer architecture | 2.1.2 | Check math_object_builder.py exists | File exists, imports mts_math |
| A3: Compiled engine | 2.1.3 | wc -l compiled_engine.md | ~7.3KB (not 164KB) |
| A4: Navigation overhaul | 2.1.4 | ls system/0*.md | 00, 01, 02a, 02b, 02c, 03, 04, 05 exist |
| A5: 93% compileable | 2.1.5 | Check compiled_code_opportunities.md | 51/55 functions mapped |
| A6: Math layer extracted | 2.1.6 | Run pytest test_mts_math.py + test_math_object_builder.py | 98/98 PASS |

### TEST 2.2: Engine Decisions Implemented

| Decision | Test | How to Verify | Expected |
|----------|------|-------------|----------|
| E1: ENGINE_OPT_001 | 2.2.1 | grep "Multi-TF Zone Priority" compiled_engine.md | Found |
| E2: ENGINE_OPT_002 | 2.2.2 | grep "Directional Filter" compiled_engine.md | Found |
| E3: HTF_PATCH_001 | 2.2.3 | grep "Single Print" compiled_engine.md | Found as target rule |
| E4: Malkans RSI | 2.2.4 | grep "RSI" compiled_engine.md | Found in Section 9 |
| E5: BUG #4 fix | 2.2.5 | grep "recent_shift" compiled_engine.md | Found |
| E6: Post-entry management | 2.2.6 | grep "Post-Entry Management" compiled_engine.md | Section 12 found |
| E7: Cross-trader integration | 2.2.7 | grep "C06-E02\|C12-E01\|C05-E03" compiled_engine.md | All found |

### TEST 2.3: Data/DSA Decisions Implemented

| Decision | Test | How to Verify | Expected |
|----------|------|-------------|----------|
| D1: DSA v1.2.0 | 2.3.1 | grep "v1.2.0" data_schema_v1.0.md | Found |
| D2: cvd_recent | 2.3.2 | grep "cvd_recent" data_schema_v1.0.md | DATA BLOCK found |
| D3: 4 HTF fields | 2.3.3 | grep "prior_week_poc\|two_week_ago_poc" data_schema_v1.0.md | Both found |
| D4: DSA_TASK_008 cancelled | 2.3.4 | grep "DAX gap" 02b_DECISIONS_LOG.md | REJECT found |
| D5: GAP fields resolved | 2.3.5 | grep "PERMANENTLY BLOCKED\|DEFERRED" cross_trader_integration_plan.md | 4 blocked, 1 deferred |
| D6: BUG #5 documented | 2.3.6 | grep "limit=100\|0.12%" data_schema_v1.0.md | Found |
| D7: Session timing | 2.3.7 | grep "session_timing" data_schema_v1.0.md | DATA BLOCK found |

### TEST 2.4: Hard Rules Enforced in Code

| Rule | Test | How to Verify | Expected |
|------|------|-------------|----------|
| H1: AI never picks levels | 2.4.1 | Search AI output for hardcoded prices | None found (except from math_object) |
| H2: AI never recomputes math | 2.4.2 | Check math_object_builder.py | All math functions in code, not AI |
| H3: Validate before fix | 2.4.3 | Check 02b for "validated first" pattern | Found in multiple entries |
| H4: 3-snapshot proof | 2.4.4 | Check cross_trader_integration_plan.md | Rule 32 references found |
| H5: Cross-market research | 2.4.5 | Check DSA_TASK_008 rejection reasons | "Not Tom-validated" pattern |
| H6: Tom-only source | 2.4.6 | Check extract files for Source GPS | All have video ID + timestamp |
| H7: No fabrication | 2.4.7 | Check 02b for "FLAG and SET ASIDE" | Found in 2026-08-30 entry |

---

## SUITE 3: ENFORCEMENT TESTS (AI Behavior)

### TEST 3.1: Hard Rule Enforcement — Output Analysis

**Method:** Analyze last N AI outputs for rule violations.

| Rule | Test | Check | Expected | Fail Condition |
|------|------|-------|----------|----------------|
| H1 | 3.1.1 | Last 5 card outputs: any price level NOT from math_object? | 0 violations | Any hardcoded price |
| H2 | 3.1.2 | Last 5 card outputs: any recomputed R:R? | 0 violations | AI-calculated R:R |
| H3 | 3.1.3 | Last 5 bug reports: validated before fix? | 5/5 validated | Any fix without validation |
| H4 | 3.1.4 | Last 3 engine patches: 3-snapshot proof? | 3/3 proven | Any patch without proof |
| H6 | 3.1.5 | Last 5 zone references: Source GPS present? | 5/5 with GPS | Any zone without source |

### TEST 3.2: Option B Pre-Validated Screenshot

**Method:** Test the new workflow.

| Test | Input | Expected Behavior | Time Target |
|------|-------|-------------------|-------------|
| 3.2.1 | Screenshot uploaded | Skip VVP-001 10-check validation | <30s to first analysis |
| 3.2.2 | Screenshot with cursor wrong | Still skip VVP (Option B assumes correct) | <30s |
| 3.2.3 | Screenshot with VP=VPVR | Still skip VVP (Option B assumes Fixed Range) | <30s |
| 3.2.4 | User says "validate VVP" | Run full VVP-001 10-check validation | ~2-3 min |
| 3.2.5 | First screenshot of session | Run full VVP (override Option B) | ~2-3 min |

**Fail condition:** Option B takes >60s = not actually faster.

---

## SUITE 4: DECISION DIAMOND INTEGRITY

### TEST 4.1: Decision Dependencies

**Purpose:** Verify decision dependencies are satisfied.

| Decision | Depends On | Test | Expected |
|----------|-----------|------|----------|
| A6 (Math layer) | A3 (Compiled engine) | 4.1.1 | Engine compiled before math extracted |
| E5 (BUG #4 fix) | A6 (Math layer) | 4.1.2 | cvd_recent field exists in math_object |
| E7 (Cross-trader) | C5 (Phase 4) | 4.1.3 | Integration plan shows COMPLETE |
| D5 (GAP fields) | C4 (Phase 3) | 4.1.4 | Planning shows 5 GAP entries |
| P6 (Option B) | E2 (ENGINE_OPT_002) | 4.1.5 | Optimization spec exists |

### TEST 4.2: Decision Conflicts

**Purpose:** Verify no two decisions contradict each other.

| Test | Decision A | Decision B | Check | Expected |
|------|-----------|-----------|-------|----------|
| 4.2.1 | A1: Scanner retired | A5: 93% compileable | Scanner retired but code still compileable? | Yes — engine is compiled, not scanner |
| 4.2.2 | H1: AI never picks levels | E7: Cross-trader integration | Cross-trader adds new levels? | No — cross-trader adds rules, not levels |
| 4.2.3 | D4: DAX gap rejected | D7: Session timing approved | Both are session-related, why different? | DAX = equity-specific, session = universal |
| 4.2.4 | E5: BUG #4 fix (CVD/flow) | E2: Directional filter | Does fix conflict with filter? | No — fix enhances filter logic |

**Fail condition:** Any contradiction = decision framework broken.

---

## SUITE 5: REGRESSION TESTS

### TEST 5.1: Previous Verdicts Still Valid

**Purpose:** Engine changes don't break historical verdicts.

| Snapshot | Date | Verdict | Re-Run Test | Expected |
|----------|------|---------|-------------|----------|
| test_snapshot_v4.2.0-p2_validation.json | 2026-08-29 | WAIT C (55/100) | 5.1.1 | Same band (C or C+) |
| BTCUSDT_2026-08-31_2127 | 2026-08-31 | C+ (58/100) | 5.1.2 | CT Short at VAH |
| BTCUSDT_2026-08-31_2204 | 2026-08-31 | C+ (65/100) | 5.1.3 | CT Short at 4H VAH |
| BTCUSDT_2026-09-01_0521 | 2026-09-01 | C+ (56/100) | 5.1.4 | CT Short at upper VAH |
| BTCUSDT_2026-09-01_1047 | 2026-09-01 | C- (40/100) | 5.1.5 | WAIT — no trigger |

**Fail condition:** Any verdict band changes = regression. Investigate before proceeding.

### TEST 5.2: Math Object Stability

**Purpose:** Same snapshot = same math_object always.

| Test | Input | Run | Expected |
|------|-------|-----|----------|
| 5.2.1 | BASE_SNAPSHOT fixture | Run 3x | Identical output all 3 times |
| 5.2.2 | 2026-09-01_1047 snapshot | Run 3x | Identical output all 3 times |
| 5.2.3 | Random snapshot from history | Run 3x | Identical output all 3 times |

**Fail condition:** Any variance = non-determinism. Critical bug.

---

## TEST EXECUTION SCHEDULE

### Quick Check (every session start, ~30 sec)
| Suite | Tests | Time |
|-------|-------|------|
| 1.1: Decision count | 4 checks | 5 sec |
| 1.2: Version consistency | 6 checks | 5 sec |
| 1.3: Bug status | 4 checks | 5 sec |
| 1.4: Cross-trader status | 4 checks | 5 sec |
| 1.5: Math test count | 4 checks | 5 sec |
| **Total** | **22 checks** | **~25 sec** |

### Full Validation (weekly or before major change, ~5 min)
| Suite | Tests | Time |
|-------|-------|------|
| 1.x: All consistency | 22 checks | 25 sec |
| 2.1: Architecture | 6 checks | 30 sec |
| 2.2: Engine | 7 checks | 30 sec |
| 2.3: Data/DSA | 7 checks | 30 sec |
| 2.4: Hard rules | 7 checks | 30 sec |
| 3.1: Enforcement | 5 checks | 2 min |
| 3.2: Option B | 5 checks | 2 min |
| 4.1: Dependencies | 5 checks | 30 sec |
| 4.2: Conflicts | 4 checks | 30 sec |
| 5.1: Regression | 5 checks | 1 min |
| 5.2: Stability | 3 checks | 30 sec |
| **Total** | **76 checks** | **~5 min** |

---

## PASS/FAIL CRITERIA

### Quick Check Pass
- All 22 consistency checks match
- Version consistent across all files
- Bug count = 0
- Cross-trader = COMPLETE
- Math tests = 98/98

### Quick Check Fail
- Any version mismatch
- Any bug still open
- Decision count mismatch
- Math test count drift

### Full Validation Pass
- All 76 checks pass
- No decision conflicts
- No regression in historical verdicts
- Math object is deterministic
- Option B workflow <60s

### Full Validation Fail
- Any decision not implemented
- Any hard rule violated in output
- Any regression in verdict band
- Non-deterministic math_object
- Option B slower than 60s

---

## COMPLIANCE WITH PROJECT RULES

| Rule | Compliance |
|------|-----------|
| Rule 31 (Validate before fix) | Test plan validates decisions before claiming they're implemented |
| Rule 32 (3-snapshot proof) | Regression tests use 5 historical snapshots |
| Rule 33 (Lean DSA) | Tests verify DSA v1.2.0 fields, no new fields added |
| Rule 34 (Research cross-market) | N/A — tests existing decisions only |
| Rule 35 (Validate before extracting) | N/A — no new extractions |

---
# END
