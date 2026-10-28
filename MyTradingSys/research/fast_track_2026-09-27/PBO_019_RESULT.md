# Task 019 (ref-pbo) verify result + PBO band cross-check

## Verify step
`python scripts/worker/queue_tool.py.new verify 019-ref-pbo` -> **STATUS PARTIAL, verdict REVIEW**,
expected 3/3, unknown file names 0, proposals 2. Verdict at
`Dumps/workers/NUC-QUEUE/done/019-ref-pbo.verdict.txt`. Produced (not applied, still `.new`):
- `MyTradingSys/backtest/bt/ref_pbo.py.new` (+108 lines)
- `MyTradingSys/backtest/bt/test_ref_pbo.py.new` (+76 lines)

Reported failing tests: `test_ref_pbo_cscv_normal_case`, `test_sharpe`. Both are **bugs in the
worker's own test file**, not in `ref_pbo.py.new`: `test_sharpe` asserts `sharpe([1,2,3]) ==
2/sqrt(3)` but the spec-correct value (mean/pstdev, pop. std) is `2/sqrt(2/3) = 2.449`, which is
what the implementation returns; `test_ref_pbo_cscv_normal_case` asserts 1 combination for S=2
but C(2,1)=2 is correct. `ref_pbo.py.new`'s `ref_pbo_cscv`/`sharpe`/`iid_noise_experiment` match
the spec faithfully.

## Comparison: ref_pbo vs bt_stats.pbo_cscv (iid Gaussian noise, T=320, N=10, S=8, 50 seeds)
Script: scratchpad `pbo_compare/compare_pbo.py` (imports copies of `ref_pbo.py.new` and
`bt_stats.py.new`, not run against the live repo).

- **Agreement**: exact, `max abs diff = 0` across all 50 seeds (both compute identical PBO/log-odds
  logic; `bt_stats.pbo_cscv` only omits the `w`/ranks return value).
- **PBO distribution over 50 seeds** (identical for both implementations):
  mean=0.5623, median=0.6214, std=0.2439, min=0.0143, max=0.9714.
- **Fraction in (0.2, 0.8)**: 32/50 = **64%**. 36% of seeds land outside the band on pure iid noise.
- `ref_pbo.iid_noise_experiment()` reproduces the same 50 values exactly (diff 0 vs. the manual loop).
- Sorted values span [0.014, 0.971]; even dropping one tail value each side only tightens to
  [0.029, 0.957] (49/50 seeds) - i.e. a band that reliably contains ~all seeds is close to [0, 1].

## Is (0.2, 0.8) justified as a pass/fail band on iid noise?
**No.** Theory (PBO centered ~0.5 under pure noise) holds only loosely here: with this small
config (T=320, N=10, S=8 -> only C(8,4)=70 CSCV splits, N+1=11 discrete w levels), the PBO
estimator has very high seed-to-seed variance (std ~0.24) and is right-skewed (median 0.62, not
0.5). A single-seed test asserting `0.2 < pbo < 0.8` (as in `test_bt_stats.py.new`'s
`test_pbo_cscv`, seed=12345) has an empirical ~36% chance of failing correct code just from
sampling variance - it is a flaky gate, not a correctness check. A band that would actually hold
for ~99% of seeds is roughly [0.01, 0.98], i.e. nearly the full [0,1] range, so a tight
band test is not a meaningful discriminator at this T/N/S; only many-seed aggregate stats
(mean/median near 0.5-0.6, not an individual-seed band) would be defensible.

**Where the (0.2, 0.8) test lives**: `MyTradingSys/backtest/bt/test_bt_stats.py.new`, lines 62-64,
inside `test_pbo_cscv`, using a single fixed seed (`random.seed(12345)`), T=320/N=10/S=8. No other
occurrence of a 0.2/0.8 band was found in the backtest or research trees.

## Recommendation
Either drop the single-seed (0.2, 0.8) assertion or replace it with a multi-seed aggregate check
(e.g. mean/median of PBO over >=20 seeds falls in a much wider band, or falls near the ref_pbo
reference distribution above) so the test isn't flaky ~1 seed in 3.
