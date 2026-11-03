# Lab Report: Cross-Vendor Re-Run of Research Kit Mutations (`gemini-mutation-rerun-research-kit-1103`)

- **Task**: `gemini-mutation-rerun-research-kit-1103` (SOURCED: `gemini-mutation-rerun-research-kit-1103.json:13`)
- **Producer of Audit Under Review**: GPT `gpt-6-luna` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md` at git commit `52ab3e0ca3b4`)
- **Reviewer**: Google Gemini (Google AI Flash Medium, Antigravity; vendor separation MET)
- **Target Module**: `MyTradingSys/backtest/research_kit.py` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:3`; 161 lines SOURCED `research_kit.py:161`)
- **Test Suite**: `MyTradingSys/tests/test_research_kit.py` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:4`; 30 passing tests OURS via `pytest MyTradingSys/tests/test_research_kit.py`)
- **Audit Table File**: `MyTradingSys/research/gemini_audits_2026-11-03/research_kit_mutation_rerun.md` (OURS)

---

## 1. Executive Summary

All 8 mutations from the GPT research kit mutation audit report (`2026-11-01_gpt-mutation-research-kit.md:9-18`) were re-implemented in scratch copies outside the repository (`git diff` clean: 0 lines changed OURS) and evaluated against `MyTradingSys/tests/test_research_kit.py`.

- **Total Mutations Re-run**: 8 (OURS)
- **FOUND (same killer test as GPT report)**: 8 (OURS)
- **DIFF (different or no killer test)**: 0 (OURS)
- **NOT_IN_DATA (mutation not reproducible from text)**: 0 (OURS)
- **Baseline Test Suite Pass Count**: 30 passed in 0.70s (OURS via `pytest MyTradingSys/tests/test_research_kit.py`; 30 expected SOURCED `gemini-mutation-rerun-research-kit-1103.json:7`)

---

## 2. Re-Run Audit Findings

| # | Mutation Description | Target Code Location | GPT Reported Killer Test | Gemini Rerun Killer Test | Status | Label |
|---|---|---|---|---|---|---|
| 1 | Holm running max dropped (`run = max(run, ...)`) | `research_kit.py:137-140` | `test_holm_hand` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:11`) | `test_holm_hand` (OURS: fails non-monotonic output at index 1: 0.04 vs 0.06) | FOUND | OURS |
| 2 | `cluster_mean_se` degrees of freedom ($n-1$ vs $n$) | `research_kit.py:48` | `test_cluster_mean_se_hand` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:12`) | `test_cluster_mean_se_hand` (OURS: SE 0.9428 vs expected 0.7071) | FOUND | OURS |
| 3 | `cluster_mean_se` NaN guard for single-day ($k < 2$) removed | `research_kit.py:45-46` | `test_cluster_mean_se_undefined_cases_are_nan` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:13`) | `test_cluster_mean_se_undefined_cases_are_nan` (OURS: returns 0.0 instead of NaN) | FOUND | OURS |
| 4 | `MDE_Z` multiplier changed ($2.8 \to 2.0$) | `research_kit.py:23` | `test_mde_is_2p8_se` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:14`) | `test_mde_is_2p8_se` (OURS: 0.10 vs expected 0.14) | FOUND | OURS |
| 5 | `cost_in_r` units error (divide cost % by 100 without stop %) | `research_kit.py:153` | `test_cost_in_r` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:15`) | `test_cost_in_r` (OURS: 0.0014 vs expected 0.28) | FOUND | OURS |
| 6 | `norm_p_two` sign error (drop `abs(t)`) | `research_kit.py:94` | `test_norm_p_two` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:16`) | `test_norm_p_two` (OURS: 1.9500 vs expected 0.04999) | FOUND | OURS |
| 7 | `holm_reject` boundary strictness (`<=` changed to `<`) | `research_kit.py:146` | `test_holm_reject_boundary_at_alpha` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:17`) | `test_holm_reject_boundary_at_alpha` (OURS: `[False]` vs expected `[True]`) | FOUND | OURS |
| 8 | `cluster_diff` union single-day NaN guard ($k < 2$) removed | `research_kit.py:67-68` | `test_cluster_diff_single_day_union_returns_nan_se` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:18`) | `test_cluster_diff_single_day_union_returns_nan_se` (OURS: `math.isnan(0.0)` is False) | FOUND | OURS |

---

## 3. Detailed Per-Mutation Verification

1. **Mutation 1 (`research_kit.py:137-140`)**:
   - GPT Report Claim: Killed by `test_holm_hand` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:11`).
   - Gemini Execution: Dropped `run = max(run, ...)`. On input `[0.01, 0.04, 0.03]`, adjusted $p$-values evaluate to `[0.03, 0.04, 0.06]`. `test_holm_hand` failed at index 1 (`0.04 != 0.06`) (OURS).
   - Additional Tests Killed: `test_holm_caps_at_one_and_larger_family`, `test_holm_reject` (OURS).

2. **Mutation 2 (`research_kit.py:48`)**:
   - GPT Report Claim: Killed by `test_cluster_mean_se_hand` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:12`).
   - Gemini Execution: Changed divisor from $n$ to $n-1$. In `test_cluster_mean_se_hand`, SE evaluated to 0.9428090415820635 instead of $\sqrt{8}/4 \approx 0.7071067811865476$ (OURS).
   - Additional Tests Killed: `test_cluster_mean_se_each_row_its_own_day`, `test_cluster_diff_disjoint_days_adds_variances`, `test_cluster_diff_shared_days_differs_from_independent` (OURS).

3. **Mutation 3 (`research_kit.py:45-46`)**:
   - GPT Report Claim: Killed by `test_cluster_mean_se_undefined_cases_are_nan` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:13`).
   - Gemini Execution: Removed `or k < 2`. Single-cluster inputs return SE of 0.0 instead of NaN, triggering `assert math.isnan(0.0)` failure (OURS).

4. **Mutation 4 (`research_kit.py:23`)**:
   - GPT Report Claim: Killed by `test_mde_is_2p8_se` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:14`).
   - Gemini Execution: Replaced `2.8` with `2.0`. In `test_mde_is_2p8_se`, $2.0 \times 0.05 = 0.10 \ne 0.14$ (OURS).
   - Additional Tests Killed: `test_mde_agrees_with_power_mde_win_rate_module`, `test_power_check_hand`, `test_require_power_refuses_and_passes`, `test_copy_mde_constants_in_screens_equal_kit` (OURS).

5. **Mutation 5 (`research_kit.py:153`)**:
   - GPT Report Claim: Killed by `test_cost_in_r` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:15`).
   - Gemini Execution: Divided cost % by 100 without stop %. `taker_cost_r(0.5)` evaluated to 0.0014 instead of 0.28 (OURS).
   - Additional Tests Killed: `test_copy_krown_cost_r_DISAGREES_fee_only` (OURS).

6. **Mutation 6 (`research_kit.py:94`)**:
   - GPT Report Claim: Killed by `test_norm_p_two` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:16`).
   - Gemini Execution: Dropped `abs(t)`. Negative $t = -1.96$ gave $p = 1.9500042$ instead of $0.0499958$, failing `assert K.norm_p_two(-1.96) == K.norm_p_two(1.96)` (OURS).

7. **Mutation 7 (`research_kit.py:146`)**:
   - GPT Report Claim: Killed by new test `test_holm_reject_boundary_at_alpha` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:17`).
   - Gemini Execution: Changed `<=` to `<`. At boundary $p = \alpha = 0.05$, `holm_reject([0.05], alpha=0.05)` evaluated to `[False]`, failing `assert [False] == [True]` (OURS).

8. **Mutation 8 (`research_kit.py:67-68`)**:
   - GPT Report Claim: Killed by new test `test_cluster_diff_single_day_union_returns_nan_se` (SOURCED: `2026-11-01_gpt-mutation-research-kit.md:18`).
   - Gemini Execution: Removed `if k < 2: return diff, float("nan")` from `cluster_diff`. Observations on 1 union day returned SE of 0.0 instead of NaN, failing `assert math.isnan(0.0)` (OURS).

---

## 4. Conclusion

All 8 mutations match the GPT audit findings with status **FOUND: 8, DIFF: 0, NOT_IN_DATA: 0** (OURS). No discrepancy was detected between vendor evaluations.

Noticed: Clustered sandwich variance estimators collapse to exactly zero when cluster count $k = 1$, making defensive $k < 2$ guards necessary for single-group and two-group difference estimators alike.
