# Spec tests for `cbp_scorecard.py`

**8 tests pass; 3/3 scratch mutations detected.** Added `scripts/dev/test_cbp_scorecard.py` and registered it in `scripts/dev/extra_tests.tsv`.

## Checked and run

- Read `scripts/dev/cbp_scorecard.py` lines 1-42. Audited pure counting logic in `recount(data)` and CLI runner `main()`.
- Branches covered:
  - `recount`:
    - Empty input dictionary or empty `"rows"` list returns empty dictionary.
    - Missing `"analyst"` key in row defaults to `"UNKNOWN"`.
    - Preservation of distinct keys: Michael (@MichaelPizzino) and Michaal (@michaelvdpoppe) remain separate dictionary entries and are never merged or folded.
    - Trades accumulation counts all entries across list of trades in a row (and safely handles `None` or missing trade lists).
    - Tradable rows incrementation strictly adheres to `cbp.is_tradable(r)` contract (requiring entry, target, invalidation, and valid direction).
    - Multiple analysts and multi-row accumulation are aggregated independently.
  - `main`:
    - CLI options parsing `--store <path>` with custom temp JSON files.
    - Alphabetical sorting of analysts and per-analyst formatted line output.
    - Summary total row count and rejected row count reporting.
    - Graceful fallback when the specified store file does not exist.
- `python -m pytest scripts/dev/test_cbp_scorecard.py -v`: **8 passed in 0.37s**.
- Scratch mutations on temporary copies:
  - M1: Merging/folding analyst names (`r.get("analyst").lower().replace("aa", "ae")`) (**6 failed, 2 passed**; caught by `test_recount_preserves_distinct_michael_and_michaal` and `test_main_cli_with_store_file`).
  - M2: Unconditional incrementation of `tradable_rows` (**5 failed, 3 passed**; caught by `test_recount_trades_and_tradable_rows_accumulation` and `test_main_cli_with_store_file`).
  - M3: Changed trades counter accumulation from `len(...)` to `+= 1` (**4 failed, 4 passed**; caught by `test_recount_trades_and_tradable_rows_accumulation`).
- Audited source unchanged: SHA-256 of `scripts/dev/cbp_scorecard.py` is `1a2d94b31db38a4ba7f886e2d40011dfc6513fc93c80eaade94df05e0ce664fc`.

## Findings

| Severity | File:line | Result | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `scripts/dev/cbp_scorecard.py:1-42` | MATCH | Pure counting and CLI execution match docstring rules, distinct analyst preservation, and tradable criteria. Source hash unchanged. | None. |
| LOW | `scripts/dev/extra_tests.tsv:188` | MATCH | Registered `scripts/dev/test_cbp_scorecard.py` into extra test runner. | None. |

## Follow-up cards

None.
