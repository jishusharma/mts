# Mutation-Kill Audit: backtest/research_kit.py (`gpt-mutation-research-kit`)

- **Target Module**: `MyTradingSys/backtest/research_kit.py` (161 lines, unchanged, `git diff` empty)
- **Test File**: `MyTradingSys/tests/test_research_kit.py` (30 passing tests)
- **Card**: `gpt-mutation-research-kit`

## Summary of Mutations

| # | Mutation Description | Target Code Location | Initial Status | Killing Test / Resolution |
|---|---|---|---|---|
| 1 | Holm running max dropped (`run = max(run, ...)`) | `research_kit.py:137-140` | **KILLED** | `test_holm_hand` (fails non-monotonic order `[0.01, 0.04, 0.03]` expecting `.06` not `.04`) |
| 2 | `cluster_mean_se` degrees of freedom ($n-1$ vs $n$) | `research_kit.py:48` | **KILLED** | `test_cluster_mean_se_hand` (SE denominator mismatch) |
| 3 | `cluster_mean_se` NaN guard for single-day ($k < 2$) removed | `research_kit.py:45-46` | **KILLED** | `test_cluster_mean_se_undefined_cases_are_nan` (expects NaN for 1 cluster) |
| 4 | `MDE_Z` multiplier changed ($2.8 \to 2.0$) | `research_kit.py:23` | **KILLED** | `test_mde_is_2p8_se` (asserts $2.8 \times 0.05 = 0.14$) |
| 5 | `cost_in_r` units error (divide cost % by 100 without stop %) | `research_kit.py:153` | **KILLED** | `test_cost_in_r` (asserts $0.14 / 0.5 = 0.28 \text{ R}$) |
| 6 | `norm_p_two` sign error (drop `abs(t)`) | `research_kit.py:94` | **KILLED** | `test_norm_p_two` (fails on negative $t = -1.96$) |
| 7 | `holm_reject` boundary strictness (`<=` changed to `<`) | `research_kit.py:146` | **SURVIVED** | **KILLED** by new test `test_holm_reject_boundary_at_alpha` |
| 8 | `cluster_diff` union single-day NaN guard ($k < 2$) removed | `research_kit.py:67-68` | **SURVIVED** | **KILLED** by new test `test_cluster_diff_single_day_union_returns_nan_se` |

## Detailed Breakdown of Survivor Mutations & New Tests

### Survivor 1 (Mutation 7): `holm_reject` exact boundary at $\alpha$
- **Mutation**: `return holm(p, m) < alpha` instead of `<= alpha`.
- **Why it survived**: Existing test `test_holm_reject` only tested $p$-values with adjusted values strictly below or strictly above $\alpha = 0.05$ (adjusted `.03 < .05` and `.06 > .05`). No test verified the exact boundary where an adjusted $p$-value equals $\alpha$.
- **New Test Added**: `test_holm_reject_boundary_at_alpha` in `MyTradingSys/tests/test_research_kit.py`:
  ```python
  def test_holm_reject_boundary_at_alpha():
      # boundary check: adjusted p equal to alpha is rejected (p <= alpha)
      assert list(K.holm_reject([0.05], alpha=0.05)) == [True]
      assert list(K.holm_reject([0.01, 0.025], alpha=0.025)) == [True, True]
  ```
- **Verification**: The new test fails with `assert [False] == [True]` on the mutation and passes on clean code.

### Survivor 2 (Mutation 8): `cluster_diff` union single-day NaN guard
- **Mutation**: Remove `if k < 2: return diff, float("nan")` in `cluster_diff`.
- **Why it survived**: Existing tests in `test_cluster_diff_small_groups_nan` only verified small sample sizes within an arm ($n_a < 2$ or $n_b < 2$). When both arms have $n \ge 2$ (e.g. $n_a=2, n_b=2$) but all observations occur on the exact same single calendar day, $k = 1$. Without the guard, `bincount` produces zero residuals, returning an artificial $\text{SE} = 0.0$ instead of `NaN`.
- **New Test Added**: `test_cluster_diff_single_day_union_returns_nan_se` in `MyTradingSys/tests/test_research_kit.py`:
  ```python
  def test_cluster_diff_single_day_union_returns_nan_se():
      # both groups have n >= 2, but all observations fall on the same single day (k = 1 distinct day)
      # docstring: 'NaN SE when either group has < 2 items or the union has one day'
      d, se = K.cluster_diff([1.0, 2.0], [0, 0], [3.0, 4.0], [0, 0])
      assert d == -2.0
      assert math.isnan(se)
  ```
- **Verification**: The new test fails with `assert False` (`math.isnan(0.0)`) on the mutation and passes on clean code.

## Verdict

All 6 core mutations and 2 boundary survivors were audited and confirmed KILLED by `MyTradingSys/tests/test_research_kit.py`. `research_kit.py` remains completely untouched (`git diff` clean). All 30 test suite items pass.

Noticed: clustered sandwich variance estimators collapse to exactly zero when the cluster count $k = 1$, making explicit $k < 2$ defensive guards essential across both single-mean and two-group difference estimators.
