# Lab formula spec recount

Verdict: BLOCKED — the canonical file provides one family-wide rule for each of F11 and F18–F21, but does not define which distinct subformula F11.1–8, F18.1–7, F19.1–8, F20.1–4, and F21.1–9 represent. The requested independent sub-ID results cannot be derived from FORMULAS.md alone without inventing mappings or importing producer rules.

## What was checked

- Read `MyTradingSys/backtest/layers/FORMULAS.md`, sections 11 and 18–21 (headings at lines 213, 415, 489, 513, 529). Each section gives a family overview, not per-sub-ID definitions.
- Read `MyTradingSys/backtest/layers/FORMULAS_SPEC.md`, which currently repeats the same family example under each sub-ID (F11.1 starts line 86; F18.1 line 160; F19.1 line 194; F20.1 line 232; F21.1 line 254).
- Read `formula_spec_text/gen_examples.py` lines 60–64: each listed sub-ID is a shallow copy of the parent row.
- Read `formula_spec_text/test_formula_spec.py`: removed the expected-failure annotation and replaced the `else: got=val` echo with an explicit `AssertionError` for unknown formula names.
- DEV source availability: `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz` exists per task context. No bar at or after 2024-07-01 was inspected.

## Findings

| Severity | File:line / command | Finding | Evidence | Disposition |
|---|---|---|---|---|
| HIGH | `FORMULAS.md:213,415,489,513,529` | No sub-ID-to-rule mapping exists in the read-only canonical spec. | Section 11 is “Execution math”; sections 18–21 each describe a broad family. None enumerates .1, .2, etc. with an input/output contract. | BLOCKED pending authoritative sub-ID mappings in FORMULAS.md or explicit clarification of the intended sub-ID contracts. |
| HIGH | `formula_spec_text/gen_examples.py:60-64` | Sub-ID examples duplicate their family parent. | The generator selects the parent row, then appends `{**base, 'id': ...}`; existing `examples.json` rows share identical inputs and expected formula names. | Not regenerated: no safe, spec-derived per-sub-ID cases can be selected. |
| HIGH | `formula_spec_text/test_formula_spec.py:55` | Removed the expected-value fallback; unsupported names now fail closed. | `python -m unittest discover -s MyTradingSys/research/layer_lab/formula_spec_text -p test_formula_spec.py -v` fails with `AssertionError: unknown formula name: 'population Sharpe one-observation undefined' (F10)`. This is outside the requested sub-ID families and shows the existing checker is not green even beyond the copy defect. | Retain fail-closed behavior; a complete independent recount and fixing all catalog cases remain necessary before passing. |

The requested regression proof is not complete: this run exposed the unsupported F10 case before reaching the copied sub-ID guard. No `formula_case`/sub-ID data, sub-ID recount implementation, regenerated examples, refreshed worked examples, or `run_all_tests.py --quick` result is claimed. `FORMULAS.md` remains read-only and no REVIEWED stamp was added.

No `tasks.py done`, git, sync, ship, release, or push command was run because the card is blocked and the user explicitly prohibited those release steps.

lab: lab-formula-spec-recount BLOCKED canonical FORMULAS.md lacks distinct sub-ID mappings; report 2026-10-21_lab-formula-spec-recount.md
