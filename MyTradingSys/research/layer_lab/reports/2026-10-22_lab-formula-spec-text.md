# Formula spec text lab — 2026-10-22

BLOCKED — the acceptance requirements conflict with the available DEV tape example search, and complete F18–F21 recount coverage is not established.

## Work and evidence

- Read `MyTradingSys/backtest/layers/FORMULAS.md` and the existing `FORMULAS_SPEC.md`; `FORMULAS.md` was not changed.
- Added/updated `MyTradingSys/research/layer_lab/formula_spec_text/gen_examples.py`, `examples.json`, and `test_formula_spec.py`. The generator reads only `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz`, slices `t < 1719792000000`, and generated 59 IDs/sub-IDs from 21,888 permitted rows (last open 2024-06-30 23:00 UTC).
- Replaced every worked-example line in `FORMULAS_SPEC.md` using generated records; its header now names the tape-based IDs and claims no SYNTHETIC examples. Updated `scripts/dev/run_extra_tests.py` was unnecessary: the test was already listed in `EXTRA`.
- Fail-first: `python -m pytest MyTradingSys/research/layer_lab/formula_spec_text/test_formula_spec.py -q -p no:cacheprovider` failed on the old content: `AssertionError: unknown formula name: 'population Sharpe one-observation undefined' (F10)`. The original test had masked failure with `expectedFailure`; that mask was removed.
- Current scoped test: same command → `2 passed in 0.22s`.
- `python scripts/dev/tasks.py check lab-formula-spec-text` → `NOT READY (ready): review stamp voided or missing: scope or card changed after review`.

## Blockers

| Severity | Evidence | Finding | Resolution needed |
|---|---|---|---|
| HIGH | `gen_examples.py`; generated `examples.json` F01; DEV tape rows with 15 consecutive closes | The closest 14-delta Wilder RSI seed among every consecutive 15-close DEV window rounds to **57.8302** (full value 57.830163407447), not the required **57.8313**. Searching rolling RSI values seeded from the start of the available tape also did not produce 57.8313 to four decimals. Therefore the explicit acceptance value cannot be reconciled with the tape-only requirement by choosing a valid contiguous warmup window. | Resolve which acceptance value or tape constraint governs F01, then regenerate the spec/example from that agreed definition. |
| HIGH | `gen_examples.py` F18/F19/F20/F21 cases and `test_formula_spec.py` recount dispatcher | Although each required ID has its own record and the test recounts its listed arithmetic, several sub-ID examples exercise formula primitives (for example bin edges, slope thresholds, and warmup placeholders), not the full catalog worked cases such as profile value-area expansion/touch outcomes or Krown detector hard cases. The required independent recomputation of all F18–F21 catalog hard cases is therefore not demonstrated. | Map every sub-ID to its specific worked case in `FORMULAS.md` and build the corresponding full tape-window recount before accepting the card. |

No task completion command was run because the card remains blocked; the test pass does not resolve these acceptance gaps. No git or sync operations were run.
