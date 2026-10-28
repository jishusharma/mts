# FILE: MyTradingSys/tests/UNIT_TEST_PLAN.md
# READ ORDER: After compiled_code_opportunities.md
# PURPOSE: Map ACTUAL compiled functions to test coverage. No fantasy specs.
# Date: 2026-09-27
# Status: ACTIVE v5.0.0 - REPLACES v4.0.0 (stale counts, mojibake)
# ---

# UNIT TEST PLAN - v5.0.0
# Reality check (recounted 2026-09-27, task A1 of core_readiness_2026-09-27
# plan): 130 pytest cases across 4 files, plus 1 new file (test_proof_direction.py,
# 1 case covering 15 sub-checks) adopted from the core-readiness harness. 131 total.
# v4.0.0 (2026-09-02) claimed 125 across 2 files; test_session_state.py (8) and
# tests/docs/test_integrity.py (5) existed on disk but were never folded into
# the count. This version is the single source of test counts - update it
# whenever a test file is added or a function count changes, do not let it drift again.

## Test Summary
| File | Test Count | Coverage |
|------|-----------|----------|
| test_mts_math.py | 79 | mts_math.py math + state-management functions |
| test_math_object_builder.py | 38 | build_math_object + schema/zone validation |
| test_session_state.py | 8 | session_state.py read/write/log roundtrip |
| docs/test_integrity.py | 5 | doc integrity checks (see that file for scope) |
| test_proof_direction.py | 1 | L2 proof-direction check (BUG-008), 14 pinned cases + 1 no-candidates case, adopted from research/core_readiness_2026-09-27/harness/proof_direction_cases.py |
| **Total** | **131** | |

## AI-Judgment Functions (NOT unit-testable)
These live in compiled_engine.md as [PRINCIPLE - NOT ALGORITHM] entries.
Validated via 3-snapshot rule (Rule 35), not pytest.
Examples: classify_state, check_breakdown_override, apply_exhaustion_gate, get_valid_setups

## Running Tests
```bash
cd MyTradingSys/tests
pytest -q                                 # 131 tests total
pytest test_mts_math.py -v                # 79 tests
pytest test_math_object_builder.py -v     # 38 tests
pytest test_session_state.py -v           # 8 tests
pytest docs/test_integrity.py -v          # 5 tests
pytest test_proof_direction.py -v         # 1 test, 15 sub-checks
```

## NOTE ON L1/L2 COVERAGE (2026-09-27)
Everything above tests mts_math.py (Python zone math) and math_object_builder.py
(L2 proof-direction/aligned-contradiction). Neither is the live decision path's
L1: the Java Tom core (SetupCandidatesBuilder.java, ExtraSetupBuilder.java) has
no pytest coverage (Python cannot import it) and had zero regression tests
before 2026-09-27. That gap is covered separately by
research/core_readiness_2026-09-27/harness/java/ReplayScbSteps1to8.java
(replays L1 from archived snapshots; not part of this pytest suite; see
core_check.ps1). See CORE_READINESS_PLAN.md for the full layer map.

# END
