# lab-formula-spec-text

BLOCKED ? spec and coverage check are complete, but card completion is gated on independent review.

## Work performed

- Read `MyTradingSys/backtest/layers/FORMULAS.md:10-557`; IDs are sections 1?23. Subformula ranges 11.1?11.8, 18.1?18.7, 19.1?19.8, 20.1?20.4, and 21.1?21.9 are covered in their parent entries.
- Added `MyTradingSys/backtest/layers/FORMULAS_SPEC.md:1-150`: inputs, close/bar alignment, precision and rounding, warmup/edge behavior, provenance labels, and a DEV-derived hand example for each top-level ID.
- Examples use only `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz` bars open 2022-01-01 through 2022-01-01 04:00 UTC (below the 2024-07-01 cutoff). For C3, 1h data cannot resolve minute-of-quarter; this is explicitly marked NOT_IN_DATA at spec line 110.
- Coverage check command: Python regex over `FORMULAS.md` top-level `## <id>.` headings and `FORMULAS_SPEC.md` headings; result `catalog top-level IDs: 23`, `spec top-level IDs: 23`, `missing: []`, and `PASS`. The check also asserts 23 DEV-example labels.

## Findings

| Severity | File:line | Result | Evidence / action |
|---|---|---|---|
| LOW | `MyTradingSys/backtest/layers/FORMULAS.md:10-557` | MATCH | 23 numbered top-level formula entries; all have a matching spec entry. |
| LOW | `MyTradingSys/backtest/layers/FORMULAS_SPEC.md:17-150` | MATCH | Each entry has an input/alignment/rounding/edge contract, provenance, and a DEV example; entry 16 records the 1m-resolution limitation. |

## Blocker

`python scripts/dev/tasks.py done lab-formula-spec-text --result "23 formula IDs specified; MyTradingSys/backtest/layers/FORMULAS_SPEC.md"` refused completion: `weight/class needs review: add 'REVIEWED: <reviewer> <date>' to the note first`. An independent reviewer is unavailable in this unattended run. Per task instructions, the card is not marked done.

No producer code was read or changed. No event tables or gates were executed; this task was specification-only. No follow-up cards were created.
