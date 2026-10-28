# P2 FABIO V3 HOLDOUT - STATUS REVIEW

Session: MTS-2026-10-06-1254Z-APP-ANA-research-agenda  
Pre-registration: MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md  
Code under test: backtest/layers/fabio/v3 (commit state verified: unchanged since pre-reg)

## Verification

✓ Code unchanged: No commits to backtest/layers/fabio/v3/*.py or backtest/fees.py after pre-registration (8ca8403)
CORRECTED 2026-10-09 (B147): PRE_REG_FABIO_V3.md:28 says the 2026-06-26.. holdout was NOT read for Fabio v3 (holdout step 'not executed'). The earlier line 'read once, 2026-10-04' was wrong. The same date range IS burned for Tom (read twice: tom_core_20260929 and tom_core_20261007).
✓ Pre-reg frozen: IS selection frozen before OOS pass (as specified)

## Result

**L3-FAIL** for all four models (from PRE_REG_FABIO_V3.md Result block 2, lines 43-48):

| Model | IS Trades | OOS Trades | OOS Mean R | CI95 | Status |
|-------|-----------|-----------|------------|------|--------|
| A (N60/p0.05/f0.003/rest/g0.8) | 1 | 0 | 0.0000 | [0.0000, 0.0000] | NOT EVALUABLE |
| B (N60/z2/f0.003/rest) | 0 | 0 | 0.0000 | [0.0000, 0.0000] | NOT EVALUABLE |
| C (m5/f0.005/rest/g0.8) | 142 | 79 | -0.1038 | [-0.2087, -0.0053] | FAIL |
| D (N240/p0.05/f0.003/rest) | 1 | 0 | 0.0000 | [0.0000, 0.0000] | NOT EVALUABLE |

**Verdict (exact quote from PRE_REG_FABIO_V3.md):**

> L3-FAIL for all four models by the registered thresholds. Model C is the only evaluable one: OOS mean day net R is negative and its CI95 upper bound is below 0, and it stays negative at 0 bps and at 5 bps; DSR and the mean threshold fail. A, B, D produced 0 OOS trade days and at most 1 IS trade day: they are NOT EVALUABLE (a fail by absence of trades, not evidence of losses); their IS-best cell is effectively arbitrary. var_sr across cells 0.01521. Not executed (declared in the pre-registration): stage 1, null permutation, stop-first and funding-2x stress, regime rule, 12 variants without an engine key, holdout. Per TOM_FABIO_REVIEW s2 limit b, a fail on BTC does not mean the extraction was wrong.

## Action

No re-run needed. Pre-registration constraint satisfied (code unchanged, single OOS read). Result stands: L3-FAIL.

**File path:** MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md (lines 43-48, dated 2026-10-04)
