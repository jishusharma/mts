# Context V2 realised-MDE verdict rule

## Built

- `mde_rule.py` provides a pure verdict helper. FAIL requires `mean_e <= 0` and `2.8 * day_se + cost_r <= 0.30 R`; PASS requires positive E and both absolute day/week clustered t statistics at least 3.241; remaining outcomes are INCONCLUSIVE. Inputs are checked for invalid/nonfinite values.
- `n_needed()` computes ceil of the pre-registered normal approximation with the OURS planning inputs and threshold. The draft addendum labels 0.375 R as OURS and presents 0.30 R sensitivity, including both day counts.
- The test is registered in `scripts/dev/run_extra_tests.py` EXTRA, and the helper is registered in `wiring_registry.json`.
- No study was run. Study/trial rows: 0; outcome rows read: 0; missing study data: NOT_IN_DATA (not needed for this pure-function task).

## Verification

- EXPECT: pre-change test fails because `mde_rule.py` does not exist. RESULT: `python -m pytest test_mde_rule.py -q` from the test directory failed during collection with `ModuleNotFoundError: No module named 'mde_rule'` (red).
- RESULT: same command after implementation: `4 passed in 0.02s`.
- `n_needed(0.30) == 685`; `n_needed(0.375) == 393`, verified by the synthetic test assertions in `test_mde_rule.py`.

## Files

- `mde_rule.py:1` pure verdict and planning helpers.
- `test_mde_rule.py:1` synthetic contract tests.
- `PRE_REG_V3_ADDENDUM_DRAFT.md:1` draft rule text; it must be adopted into governing pre-registration before a study run.
- `scripts/dev/run_extra_tests.py:20` includes this test in EXTRA.
- `MyTradingSys/system/wiring_registry.json:807` registers the helper as a TOOL.

No VALIDATION or HOLDOUT data was read. No trial was run, so no TRIALS.md row was added.
