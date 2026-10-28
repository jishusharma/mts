# Gap G1 power / MDE helper

Verdict: BUILD COMPLETE ? six G1 rows reproduced within 2 percentage points; 7 focused tests pass.

## What was checked or run

- Read `MyTradingSys/research/backtest_gap_review_2026-10-13/REPORT.md:85-107` for G1 and `:210-213` for its independent section 9 formula.
- Read `MyTradingSys/system/LAYERS.md:10-25` (Tom layer scope). Existing `MyTradingSys/research/volume_2026-10-09/vstats.py` was read only; it implements bootstrap family statistics rather than the requested two-point normal power calculation.
- Added `MyTradingSys/backtest/power_mde.py` with pure `power_mde(p, rr, cost_r, n)` API returning mean net R, two-sided 95% CI-lower-bound test power, MDE at N, and N for 80% power.
- Added `MyTradingSys/tests/test_power_mde.py`; red-first run before module creation failed collection with `ModuleNotFoundError: No module named 'MyTradingSys.backtest.power_mde'`.
- Green command: `python -m pytest MyTradingSys/tests/test_power_mde.py -q` ? **7 passed**. Pytest emitted one cache-directory warning because `.pytest_cache` already exists; tests completed successfully.

## Results

| p | R:R | cost R | mean net R | power at 100 | at 150 | at 300 | trades for 80% |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.45 | 1.5 | 0.012 | +0.11 | 14.86% | 19.68% | 35.24% | 951 |
| 0.45 | 1.5 | 0.062 | +0.06 | 7.99% | 9.61% | 14.27% | 3,059 |
| 0.40 | 2.0 | 0.012 | +0.19 | 24.86% | 34.40% | 59.60% | 480 |
| 0.40 | 2.0 | 0.062 | +0.14 | 15.55% | 20.98% | 36.85% | 890 |
| 0.45 | 2.0 | 0.062 | +0.29 | 48.80% | 65.92% | 92.35% | 211 |
| 0.45 | 2.5 | 0.062 | +0.51 | 83.80% | 94.64% | 99.86% | 90 |

G1 table comparison: all six rows match to under 2 percentage points for each reported N; requested anchor powers are approximately 15% and 84%, and 80%-power Ns are approximately 951 and 90. The helper reports power numerically so preregistration callers can label a verdict INCONCLUSIVE whenever power is below 0.80.

## Findings

| Severity | Location | Finding | Evidence |
|---|---|---|---|
| LOW | `MyTradingSys/backtest/power_mde.py` | Pure normal approximation assumes independent two-point outcomes and a fixed per-trade cost, as the G1 table does. | Section 9 equation at `REPORT.md:210-213`; six row outputs above. |

No existing files were changed. No follow-up cards created.
