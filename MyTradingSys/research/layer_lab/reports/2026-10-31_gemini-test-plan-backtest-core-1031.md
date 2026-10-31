# Report: Gemini Test Plan for Backtest Core

**Card:** `gemini-test-plan-backtest-core-1031`  
**Date:** 2026-10-31  
**Scope In:** `MyTradingSys/research/gemini_burn_2026-10-31/BACKTEST_CORE_TEST_PLAN.md`  
**Scope Out:** live tree; engine and layer code edits; any backtest or trading verdict; .secrets and .env  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  

---

## Findings Summary

A systematic boundary and failure audit of backtest core modules (`fees.py`, `sim.py`, `promote.py`, `prob_table.py`) was performed:
- Total boundary / failure cases catalogued: **60** [OURS]
- Existing verified test cases: **28** [OURS]
- Missing test cases: **32** [OURS]

### Key Module Observations:
1. **`MyTradingSys/backtest/fees.py`**:
   - `DERIBIT_TAKER` and `FDAX_PER_SIDE` verified against Java in `MyTradingSys/tests/test_b070_fee_parity.py:18` and `:27` (**EXISTS**).
   - `fees_dict` lacks validation for zero/negative inputs, NaN/None, or dictionary shape assertions (**MISSING**).
2. **`MyTradingSys/backtest/sim.py`**:
   - Wilson score interval calculation (`sim.py:34-39`), geometry check `geom_ok` (`sim.py:42-43`), and replay simulation `run` (`sim.py:46-82`) have 0 direct unit tests (**MISSING**).
   - High-risk failure modes identified: division by zero when $stop == entry$ (`sim.py:76`), math domain error on $k > n$ in `wilson` (`sim.py:38`), and chronological order assumptions on gap detection (`sim.py:63`).
3. **`MyTradingSys/backtest/layers/promotion/promote.py`**:
   - Broadest test coverage in `MyTradingSys/backtest/layers/promotion/test_promote.py:91-405` (54 test functions covering MDE trade floors, Holm-Bonferroni critical z, temporal pre-reg ordering, and blocklisting).
   - Missing negative edge cases: unhandled exceptions on non-numeric / corrupted values in `recompute_oos` (`promote.py:78`), and non-positive variants in `holm_z` (`promote.py:59`).
4. **`MyTradingSys/backtest/prob_table.py`**:
   - Outcome classification, Dirichlet smoothing, and sample size fallback well tested in `test_prob_table.py:13-178` and `test_prob_table_edge.py:18-75`.
   - Missing edge cases: empty input with $\alpha = 0.0$ leading to division by zero (`prob_table.py:72`), unhandled exceptions on missing/corrupted label JSON files in `load_labels` (`prob_table.py:8`).

### Verification:
Ran test suite covering related test files:
```bash
python -m pytest MyTradingSys/backtest/layers/promotion/test_promote.py MyTradingSys/backtest/test_prob_table.py MyTradingSys/backtest/test_prob_table_edge.py MyTradingSys/tests/test_b070_fee_parity.py
# 79 passed in 24.57s
```

Primary deliverable created:
`MyTradingSys/research/gemini_burn_2026-10-31/BACKTEST_CORE_TEST_PLAN.md`
