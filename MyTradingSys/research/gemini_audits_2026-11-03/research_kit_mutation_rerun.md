# FOUND: 8, DIFF: 0, NOT_IN_DATA: 0 | test_research_kit.py PASS: 30

# Cross-Vendor Re-run Audit: Research Kit Mutation Kill Table

- **Target Module**: `MyTradingSys/backtest/research_kit.py` (SOURCED: "Target Module: `MyTradingSys/backtest/research_kit.py` (161 lines, unchanged, `git diff` empty)" `2026-11-01_gpt-mutation-research-kit.md:3`; 161 lines SOURCED `research_kit.py:161`)
- **Test File**: `MyTradingSys/tests/test_research_kit.py` (SOURCED: "Test File: `MyTradingSys/tests/test_research_kit.py` (30 passing tests)" `2026-11-01_gpt-mutation-research-kit.md:4`; 30 passed OURS `pytest MyTradingSys/tests/test_research_kit.py`)
- **Source Audit**: `MyTradingSys/research/layer_lab/reports/2026-11-01_gpt-mutation-research-kit.md` (SOURCED: commit 52ab3e0ca3b4)
- **Task ID**: `gemini-mutation-rerun-research-kit-1103`
- **Methodology**: Scratch copy mutation testing outside git repo (`git diff` clean: 0 lines changed OURS). Each of the 8 mutations re-executed and tested against `MyTradingSys/tests/test_research_kit.py`.

## Audit Summary

- Total mutations evaluated: 8 (OURS)
- **FOUND**: 8 (OURS)
- **DIFF**: 0 (OURS)
- **NOT_IN_DATA**: 0 (OURS)
- Unmutated suite pass count: 30 (OURS; 30 expected SOURCED `gemini-mutation-rerun-research-kit-1103.json:7`)

## 8 Mutation Re-run Results

| # | Mutation Description | Target Code Location | GPT Reported Killer Test | Gemini Rerun Killer Test | Status | Label |
|---|---|---|---|---|---|---|
| 1 | Holm running max dropped (`run = max(run, ...)`) | `research_kit.py:137-140` | `test_holm_hand` (fails non-monotonic order `[0.01, 0.04, 0.03]` expecting `.06` not `.04`) | `test_holm_hand` (also failed: `test_holm_caps_at_one_and_larger_family`, `test_holm_reject`) | FOUND | OURS |
| 2 | `cluster_mean_se` degrees of freedom ($n-1$ vs $n$) | `research_kit.py:48` | `test_cluster_mean_se_hand` (SE denominator mismatch) | `test_cluster_mean_se_hand` (also failed: `test_cluster_mean_se_each_row_its_own_day`, `test_cluster_diff_disjoint_days_adds_variances`, `test_cluster_diff_shared_days_differs_from_independent`) | FOUND | OURS |
| 3 | `cluster_mean_se` NaN guard for single-day ($k < 2$) removed | `research_kit.py:45-46` | `test_cluster_mean_se_undefined_cases_are_nan` (expects NaN for 1 cluster) | `test_cluster_mean_se_undefined_cases_are_nan` | FOUND | OURS |
| 4 | `MDE_Z` multiplier changed ($2.8 \to 2.0$) | `research_kit.py:23` | `test_mde_is_2p8_se` (asserts $2.8 \times 0.05 = 0.14$) | `test_mde_is_2p8_se` (also failed: `test_mde_agrees_with_power_mde_win_rate_module`, `test_power_check_hand`, `test_require_power_refuses_and_passes`, `test_copy_mde_constants_in_screens_equal_kit`) | FOUND | OURS |
| 5 | `cost_in_r` units error (divide cost % by 100 without stop %) | `research_kit.py:153` | `test_cost_in_r` (asserts $0.14 / 0.5 = 0.28 \text{ R}$) | `test_cost_in_r` (also failed: `test_copy_krown_cost_r_DISAGREES_fee_only`) | FOUND | OURS |
| 6 | `norm_p_two` sign error (drop `abs(t)`) | `research_kit.py:94` | `test_norm_p_two` (fails on negative $t = -1.96$) | `test_norm_p_two` | FOUND | OURS |
| 7 | `holm_reject` boundary strictness (`<=` changed to `<`) | `research_kit.py:146` | `test_holm_reject_boundary_at_alpha` | `test_holm_reject_boundary_at_alpha` (asserts `list(K.holm_reject([0.05], alpha=0.05)) == [True]`) | FOUND | OURS |
| 8 | `cluster_diff` union single-day NaN guard ($k < 2$) removed | `research_kit.py:67-68` | `test_cluster_diff_single_day_union_returns_nan_se` | `test_cluster_diff_single_day_union_returns_nan_se` (asserts `math.isnan(se)` when union has 1 distinct day) | FOUND | OURS |

## Detailed Breakdown of Audited Mutations

1. **Mutation 1 (`research_kit.py:137-140`)**:
   - Change: Omitted running maximum tracking `run = max(run, ...)`.
   - Result: In `test_holm_hand`, input $p = [0.01, 0.04, 0.03]$ yielded adjusted values $[0.03, 0.04, 0.06]$ instead of monotonic $[0.03, 0.06, 0.06]$. Killed by `test_holm_hand` (OURS). Status: FOUND.

2. **Mutation 2 (`research_kit.py:48`)**:
   - Change: Denominator changed from $n$ to $n - 1$ in `cluster_mean_se`.
   - Result: In `test_cluster_mean_se_hand`, standard error evaluated to 0.9428090415820635 instead of $\sqrt{8} / 4 \approx 0.7071067811865476$. Killed by `test_cluster_mean_se_hand` (OURS). Status: FOUND.

3. **Mutation 3 (`research_kit.py:45-46`)**:
   - Change: Guard `if n < 2 or k < 2:` reduced to `if n < 2:`.
   - Result: In `test_cluster_mean_se_undefined_cases_are_nan`, single cluster $[1, 2, 3]$ with days $[7, 7, 7]$ returned $\text{SE} = 0.0$ instead of `NaN`. Killed by `test_cluster_mean_se_undefined_cases_are_nan` (OURS). Status: FOUND.

4. **Mutation 4 (`research_kit.py:23`)**:
   - Change: Multiplier `MDE_Z = 2.8` replaced with `MDE_Z = 2.0`.
   - Result: In `test_mde_is_2p8_se`, `K.mde(0.05)` evaluated to 0.10 instead of 0.14. Killed by `test_mde_is_2p8_se` (OURS). Status: FOUND.

5. **Mutation 5 (`research_kit.py:153`)**:
   - Change: `cost_in_r` returned `cost_pct / 100.0` omitting division by `stop_pct`.
   - Result: In `test_cost_in_r`, `K.taker_cost_r(0.5)` evaluated to 0.0014 instead of 0.28. Killed by `test_cost_in_r` (OURS). Status: FOUND.

6. **Mutation 6 (`research_kit.py:94`)**:
   - Change: `norm_p_two` dropped `abs(t)`.
   - Result: In `test_norm_p_two`, `K.norm_p_two(-1.96)` evaluated to 1.9500042097035593 instead of 0.049995790296440745. Killed by `test_norm_p_two` (OURS). Status: FOUND.

7. **Mutation 7 (`research_kit.py:146`)**:
   - Change: `holm_reject` changed `<=` to `<`.
   - Result: In `test_holm_reject_boundary_at_alpha`, `list(K.holm_reject([0.05], alpha=0.05))` evaluated to `[False]` instead of `[True]`. Killed by `test_holm_reject_boundary_at_alpha` (OURS). Status: FOUND.

8. **Mutation 8 (`research_kit.py:67-68`)**:
   - Change: Removed `if k < 2: return diff, float("nan")` in `cluster_diff`.
   - Result: In `test_cluster_diff_single_day_union_returns_nan_se`, observations on 1 common day produced $\text{SE} = 0.0$ instead of `NaN`. Killed by `test_cluster_diff_single_day_union_returns_nan_se` (OURS). Status: FOUND.

Noticed: Clustered sandwich variance estimators collapse to exactly zero when cluster count $k = 1$, making defensive $k < 2$ guards necessary for single-group and two-group difference estimators alike.
