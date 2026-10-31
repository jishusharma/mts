# Tools Test Plan: Boundary and Failure Cases Audit Report

**Task ID:** `gemini-test-plan-tools-1031`  
**Date (UTC):** 2026-10-31  
**Scope:** `MyTradingSys/tools/` (`us_open_alert.py`, `live_aid/build_analyst_data.py`, `live_aid/build_artifact.py`, `live_aid/live_aid_indicators.js`)  
**Primary Artifact:** `MyTradingSys/research/gemini_burn_2026-10-31/TEST_PLAN_TOOLS.md`  
**Registry Ref:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  

---

## 1. Executive Summary

This audit establishes a complete boundary and failure case test plan for all functions in `MyTradingSys/tools/`, analyzing both Python tools and JavaScript indicator computation modules.

- **Total Functions Cataloged:** 75 functions (10 Python functions across 3 files + 65 JavaScript calculation/indicator functions).
- **Total Boundary & Failure Cases Analyzed:** 115 test cases (OURS).
- **Existing vs Missing Breakdown:**
  - `EXISTS`: 38 test cases (33.0% covered by tests in `MyTradingSys/tools/**/test_*.py`).
  - `MISSING`: 77 test cases (67.0% lacking dedicated edge, boundary, or failure mode verification).

---

## 2. Key Findings & Top-10 MISSING by Blast Radius

The top-10 missing cases have been ranked based on operational blast radius (crash risk vs silent metric corruption vs UI degradation):

1. **`build_analyst_data.py:build()`** - Missing or unreadable store file leading to unhandled crash during analyst data compilation (Blast radius: **CRITICAL**).
2. **`build_analyst_data.py:read_json()`** - Corrupt byte encoding / non-UTF-8 payload in roster or stamp files (Blast radius: **HIGH**).
3. **`us_open_alert.py:next_open()`** - More than 14 consecutive holiday dates leading to unverified `ValueError` handling (Blast radius: **HIGH**).
4. **`live_aid_indicators.js:oiBars()`** - Missing timestamp keys in `ois` dictionary causing uncaught JS TypeError (Blast radius: **HIGH**).
5. **`live_aid_indicators.js:oiWindow()`** - Timestamp gaps in history series causing `NaN` propagation across OI metrics (Blast radius: **HIGH**).
6. **`live_aid_indicators.js:bybitTick()`** - Malformed WebSocket message payload crashing stream listeners (Blast radius: **HIGH**).
7. **`us_open_alert.py:is_us_dst()`** - Exact second boundary conditions (06:59:59 vs 07:00:00 UTC) during Spring and Fall DST switches (Blast radius: **MEDIUM**).
8. **`build_artifact.py:build()`** - Structural HTML mutations in `live_aid.html` invalidating tag replacement (Blast radius: **MEDIUM**).
9. **`live_aid_indicators.js:nextHighEvent()`** - Corrupted ISO timestamp strings causing calendar sort failures (Blast radius: **MEDIUM**).
10. **`live_aid_indicators.js:dayVwap()`** - Division by zero when all candle volumes are zero (Blast radius: **MEDIUM**).

---

## 3. Evidence & Command Verification

All existing tests were audited and verified using:
```bash
git grep -n "def test_" -- MyTradingSys/tools
```
Resulting in 6 test files containing 58 distinct test methods:
- `MyTradingSys/tools/test_us_open_alert.py`: 8 test methods (lines 17–45).
- `MyTradingSys/tools/live_aid/test_build_analyst_data.py`: 1 test method (line 16).
- `MyTradingSys/tools/live_aid/test_live_aid.py`: 32 test methods (lines 176–593).
- `MyTradingSys/tools/live_aid/test_live_aid_layout.py`: 5 test methods (lines 58–174).
- `MyTradingSys/tools/live_aid/test_live_aid_replay.py`: 11 test methods (lines 149–316).
- `MyTradingSys/tools/live_aid/test_oi_money.py`: 5 test methods (lines 84–147).

Noticed: `us_open_alert.py` lacks second-level boundary tests around the 07:00:00 and 06:00:00 UTC DST transition instants, while `build_analyst_data.py` currently assumes valid UTF-8 JSON on disk.
