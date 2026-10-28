# Lab formula spec recount

Verdict: BLOCKED - sub-ID recount work is incomplete; no generator/regeneration, per-sub-ID formula recounts, worked-example refresh, or quick gate was completed.

## Checked

- Read-only canonical rules: `MyTradingSys/backtest/layers/FORMULAS.md` (F11.1-11.8 lines 213-322; F18.1-18.7 lines 415-483; F19.1-19.8 lines 489-507; F20.1-20.4 lines 513-523; F21.1-21.9 lines 529-545).
- Existing generator and checker: `MyTradingSys/research/layer_lab/formula_spec_text/gen_examples.py` lines 60-64 cloned parent rows into all sub-IDs; `test_formula_spec.py` line 53 had `else: got=val`.
- DEV input availability checked by read-only file inventory: `F:/MTS/data/bigtrade/cache/perp/klines_5m.npz` exists, as do 1h and 15m tape files. No bar contents at or after the 2024-07-01 cutoff were inspected.

## Findings

| Severity | File:line / command | Finding | Evidence | Proposed fix |
|---|---|---|---|---|
| HIGH | `gen_examples.py:60-64` | Every F11/F18/F19/F20/F21 sub-ID is a shallow copy of its family parent, including identical inputs and expected output. | Parsed `examples.json`: F18.1-F18.7 all use `typical price bin`, and F19.1-F19.8 all use `linear trendline`; likewise F11.1-8, F20.1-4, F21.1-9 repeat their parent. | Generate individual tape-backed inputs and rule-derived outputs for each catalog sub-entry. |
| HIGH | `test_formula_spec.py:53` (before edit) | Unknown formula names echoed the expected value. | Removed fallback; the existing test still passed (`python -m unittest ...test_every_catalog_id_has_spec_example_and_independent_tape_recount -v`), showing that the generic parent recount masked the copied sub-ID rows. | Keep unknown names fail-closed and recount by sub-ID contract. |
| HIGH | `test_formula_spec.py:32-33` (current partial edit) | Added an ownership assertion, proving current examples fail the required red-first check, but the implementation remains incomplete. | Same unittest command now fails: `AssertionError: None != 'F11.1' : F11.1: copied parent row has no sub-id-specific formula case`. | Finish the generator, explicit recounts, examples, and spec before rerunning. |

The task cannot be closed in this run because the proof of the old defect and an intentionally failing guard are the only completed changes; the requested independent sub-ID implementations and validations remain outstanding. `run_all_tests.py --quick` was not run. No `tasks.py done`, git, sync/ship/release, or push command was run. No REVIEWED stamp was added. `FORMULAS.md` was not modified.
