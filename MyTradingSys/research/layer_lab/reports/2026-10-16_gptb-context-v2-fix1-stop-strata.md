# gptb-context-v2-fix1-stop-strata — build report

Changed files: `context_fix1_stop_strata/stop_strata.py`, `test_stop_strata.py`, `PRE_REG_V3_ADDENDUM_DRAFT.md`, `system/wiring_registry.json`, and `scripts/dev/run_extra_tests.py`.

## What was built and run

Files checked: `stop_strata.py:1-193`; `test_stop_strata.py:1-50`; `PRE_REG_V3_ADDENDUM_DRAFT.md:1-28`; `run_extra_tests.py:14-17, 63-67`; `wiring_registry.json:798-807`; V2 design `PRE_REG_V2.md:1-60`; audit `AUDIT_BEFORE_RUN.md:1-38`.

- `stop_strata.py` provides per-side stop-timeframe shares, median/p90 `f3_stop_pct`, relative median-gap flags, and `f3_stop_tf`-stratified E with `kmin=10`.
- Count-only DEV reconstruction used `context_asof.CACHE` frame pickles for 2022-04-01 through 2024-06-30, C membership from `study.form_c(study.tradeable_ledger(frame), side)`, and V2 pool membership from `f1_at_level`, valid `f3_stop_tf`, exclusion of C, and the inclusive 24-hour C exclusion. No outcome or price after T was loaded. No `study_v2.py` run.
- Counts: C long 554, short 456; V2 pool long 6,664, short 8,021. C / pool median stop_pct: long 2.084% / 1.616% (22.45% relative gap); short 2.161% / 1.619% (25.10%). See `PRE_REG_V3_ADDENDUM_DRAFT.md` for side-wise timeframe shares and p90 values.
- Test-first evidence: before implementation, pytest failed collection with `ModuleNotFoundError: No module named 'stop_strata'` (red). `python MyTradingSys/research/layer_lab/context_fix1_stop_strata/stop_strata.py` prints the side-wise geometry summary from cached decision frames. Final own-test command `python -m pytest MyTradingSys/research/layer_lab/context_fix1_stop_strata/test_stop_strata.py -q -p no:cacheprovider` -> `3 passed in 0.09s`.
- Registration: test listed in `run_extra_tests.py` EXTRA; `stop_strata.py` registered as a research TOOL in `wiring_registry.json`.
- No trial row: no backtest or outcome/recall run was made.

## Findings

| Severity | Evidence | Finding | Status |
|---|---|---|---|
| MED | `PRE_REG_V3_ADDENDUM_DRAFT.md:18-20` | Short-side median stop width differs by 25.10% relative to C; mark `R units not comparable`, and do not call FAIL under FIX-FIRST 1. | MATCH to `AUDIT_BEFORE_RUN.md` item 1 |
| LOW | `test_stop_strata.py:5-50` | Synthetic hand values verify timeframe shares, median/p90, stratified E and kmin exclusion, and the strict >25% flag. | MATCH to card tests |
| LOW | `stop_strata.py:112-164`; `PRE_REG_V3_ADDENDUM_DRAFT.md:22-25` | The count phase is implemented and measured. Applying `stratified_e` to post-run net_R rows and its >=80% positive-strata PASS coverage remains for the V2 executor/addendum consumer. | NOT_IN_DATA (outcome run intentionally not performed) |

Follow-up cards created: none.
