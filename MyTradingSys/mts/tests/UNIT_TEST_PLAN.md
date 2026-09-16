# FILE: mts/tests/UNIT_TEST_PLAN.md
# READ ORDER: After compiled_code_opportunities.md
# PURPOSE: Map ACTUAL compiled functions to test coverage. No fantasy specs.
# Date: 2026-09-02
# Status: ACTIVE v4.0.0 вЂ” REPLACES v3.0.0 fantasy spec
# Canonical: /mnt/agents/output/upload_mirror/mts/tests/UNIT_TEST_PLAN.md
# ---

# UNIT TEST PLAN вЂ” v4.0.0
# Reality check: 22 compiled functions, 125 pytest cases, 2 test files.
# Previous v3.0.0 claimed 55 functions / ~408 cases вЂ” that was a fantasy spec.

## Compiled Functions (22 total)

### mts_math.py вЂ” 16 functions (9 public math + 7 state management)
| Function | Type | Tests | File |
|----------|------|-------|------|
| calculate_distance | public math | 4 | test_mts_math.py |
| get_zone_substate | public math | 4 | test_mts_math.py |
| get_distance_cap | public math | 5 | test_mts_math.py |
| get_tier | public math | 5 | test_mts_math.py |
| check_trigger_validity | public math | 6 | test_mts_math.py |
| calculate_gross_rr | public math | 4 | test_mts_math.py |
| calculate_net_rr | public math | 3 | test_mts_math.py |
| calculate_rr_sanity | public math | 3 | test_mts_math.py |
| detect_confluence | public math | 6 | test_mts_math.py |
| parse_state | public state | 2 | test_mts_math.py |
| diff_state | public state | 5 | test_mts_math.py |
| update_state | public state | 3 | test_mts_math.py |
| format_state | public state | 0* | test_mts_math.py |
| write_state | public state | 1 | test_mts_math.py |
| _cast | private helper | 3 | test_mts_math.py |
| _get_snapshot_value | private helper | 2 | test_mts_math.py |

### math_object_builder.py вЂ” 6 functions (1 public + 5 private)
| Function | Type | Tests | File |
|----------|------|-------|------|
| build_math_object | public | 1 (determinism) | test_math_object_builder.py |
| _is_old_schema | private | 1 | test_math_object_builder.py |
| _normalize_snapshot | private | 7 (schema detection) | test_math_object_builder.py |
| _extract_zones | private | 14 (zone fields, R:R, confluence, hard stops) | test_math_object_builder.py |
| _swing_tf_for_zone | private | 0* | test_math_object_builder.py |
| _pick_stop_target | private | 0* | test_math_object_builder.py |

*Functions marked 0* are tested indirectly through build_math_object integration.

## Test Summary
| File | Test Count | Coverage |
|------|-----------|----------|
| test_mts_math.py | 64 | All 16 mts_math.py functions |
| test_math_object_builder.py | 34 | build_math_object + schema/zone validation |
| **Total** | **125** | **22 compiled functions** |

## AI-Judgment Functions (NOT unit-testable)
These live in compiled_engine.md as [PRINCIPLE вЂ” NOT ALGORITHM] entries.
Validated via 3-snapshot rule (Rule 35), not pytest.
Examples: classify_state, check_breakdown_override, apply_exhaustion_gate, get_valid_setups

## Running Tests
```bash
cd /mnt/agents/output/upload_mirror/mts/tests
pytest test_mts_math.py -v          # 64 tests
pytest test_math_object_builder.py -v  # 34 tests
pytest -v                              # 125 tests total
```

# END
