Changed files: `MyTradingSys/backtest/tom_dax_bt.py`, `MyTradingSys/backtest/test_tom_dax_bt.py`, and the H8 addendum in `2026-10-11_lab-audit-tom-dax-bt.md`. H8 red: 2 tests, 4 failures. Green: 2 requested tests pass; all 62 harness tests pass.

# H8: frozen cached rows and counted run identities

Card: `lab-dax-trial-identity`. RESULT (2026-10-12, COD lab, Windows/Python 3.14): stale caches are refused; two same-day shift looks have two run ids and eight variant trial rows; identical rerendering adds zero rows. These are synthetic harness assertions, not market results.

## What was checked

Paths are relative to `F:/MTS/mts-codex-lab`.

- Read the audit's file legend and H8 row, including its original D:374-375,393,595,603-605,661-673 references. In this checkout those functions had already moved after H1/H2/H3/H5/H6/H7 fixes: row reuse still checked proof schema only and `cmd_report` still deduplicated by a date-based id. Read the cited PRE_REG_DAX frozen-input/registry contract and `verdict.py:66-70`; the prior H5 change had already frozen the floor per month, but did not reject reuse under a different floor.
- Inspected the Tom section of `system/LAYERS.md:10-35`, producer code `backtest/dax_engine.py:25-45`, floor reader `runtime/net_rr_floor.py:1-39`, and actual existing bootstrap/null defaults in `tom_bt.py:304-315`, `tom_bt_report.py:89`, and `tom_dax_bt.py:353`. Shared files were read as dependencies, never edited.
- Changed producer/input/cache validation in `tom_dax_bt.py:606-869`; run freezing, report provenance and trial registration in `tom_dax_bt.py:975-1130,1162-1177,1277-1308`.
- Requested regression tests: `test_tom_dax_bt.py:860` and `:1068`. Additional producer/data guards: `:826` and `:913`. Existing fixtures now carry provenance or explicitly isolate timestamp-selection testing; all temporary fixtures live inside the work tree.
- Data range: invented snapshots, flat price bars and byte fixtures only. The generation test mocks both conversion and engine subprocesses. Its printed `gen` command/rate is fixture output; no Java generation, empirical backtest, recall or real holdout read occurred. No market trial was performed and no production trial ledger was edited.

## Findings

| Severity | File:line | Classification / issue | Evidence | Fix / result |
|---|---|---|---|---|
| HIGH | `tom_dax_bt.py:724-809` | MISMATCH before / MATCH after: existing cache filename concealed mask, shifts, floor and producer differences. | Red: three `ValueError not raised` assertions. Green: mask, shift, floor, code, snapshot, snapshot metadata and row-content changes are refused. | Full SHA-256 identities bind source provenance, configuration and row bytes; rows also carry their input id. |
| HIGH | `tom_dax_bt.py:606-659,724-741` | MISMATCH before / MATCH after: current engine hashes could be attributed to historical snapshots. | Synthetic generation records its producer source/config/runtime/dependency/data identities; missing or changed producer provenance is refused. | Producer sidecars record exact generation inputs. Old unproven snapshots are refused, not retroactively blessed with current hashes. |
| HIGH | `tom_dax_bt.py:743-771,820-841,1026-1034` | MATCH after: DAX cached rows depend on the actual price/real-bar data and cutoff. | Synthetic `real` mutation and cutoff change each cause refusal. | Development row jobs require the split and use isolated development bars. Reports compare the current in-memory execution data with the cache's frozen arrays and cutoff. |
| HIGH | `tom_dax_bt.py:705-721,1037-1047,1277-1293` | MISMATCH before / MATCH after: same-day new arms vanished from the registry. | Red: `AssertionError: 4 != 8`. Green: 8 rows / 2 ids after shifts 0 and 1; rerender remains 8; a fresh look label yields 12 rows / 3 ids. | Content-based run id includes split, markets, data, cache, code/config, floor, arms and seeds. Deduplicate each `(run_id, variant)`, not a whole calendar day. |
| MED | `tom_dax_bt.py:1047,1118-1130,1175` | MATCH after: frozen provenance is durable before simulation and remains reviewable. | Synthetic simulation checks that the run JSON already exists; tampering with that file causes refusal. | Create-only manifests are printed in the outcome report. Recheck code, floor, owner manifests and cache identities before accepting results. |
| LOW | `tom_dax_bt.py:705-710,1308` | NOT_IN_DATA: no recall-driver execution or integration was requested inside these two harness files. | No recall driver was edited or invoked. | `freeze_run` and `--look-id` expose the same identity vocabulary for explicitly labelled future recall/design looks; this report claims only the tested harness behavior. |

## Red then green evidence

EXPECT: a cache created under one mask/shift/floor cannot be reused under another; shifts 0 and 1 on the same date produce separate trial identities; an identical rerender produces no extra trials.

PowerShell environment for every test command:

```powershell
$env:PYTHONPATH = (Get-Location).Path
```

Command run before changing `tom_dax_bt.py`:

```powershell
python -m unittest MyTradingSys.backtest.test_tom_dax_bt.TestDriver.test_h8_cached_rows_refuse_changed_mask_shift_or_floor MyTradingSys.backtest.test_tom_dax_bt.TestReadinessGate.test_h8_second_arm_same_day_is_counted_and_rerender_is_idempotent
```

RESULT red (pre-change implementation; exit 1), relevant assertion output:

```text
FAIL: test_h8_cached_rows_refuse_changed_mask_shift_or_floor (changed shifts)
AssertionError: ValueError not raised
FAIL: test_h8_cached_rows_refuse_changed_mask_shift_or_floor (changed mask)
AssertionError: ValueError not raised
FAIL: test_h8_cached_rows_refuse_changed_mask_shift_or_floor (changed floor)
AssertionError: ValueError not raised
FAIL: test_h8_second_arm_same_day_is_counted_and_rerender_is_idempotent
AssertionError: 4 != 8
Ran 2 tests in 0.072s
FAILED (failures=4)
```

The initial test invocation also exposed a fixture-only import-path error; that was corrected before the valid red run above, with the production implementation unchanged.

RESULT green (same command, after fix; exit 0):

```text
Ran 2 tests in 0.714s
OK
```

Required full harness command:

```powershell
python MyTradingSys/backtest/test_tom_dax_bt.py
```

RESULT green (exit 0):

```text
Ran 62 tests in 1.931s
OK
```

The complete tool output was inspected; the blocks above extract unittest verdicts and relevant assertions, excluding temporary path/fixture print noise. The quick gate was not run; the runner owns shipping and its gate.

## Compatibility and limits

Legacy snapshots without `.inputs.json` are deliberately rejected. The generation error directs the owner to a fresh snapshot directory; after authorized generation, old row caches require `rows --force`. DAX development rows also require `--split-manifest`. No existing data was regenerated during this card. Identical inputs and look labels are rerenders; an intentional fresh experiment with the same inputs must use a fresh `--look-id`. Smoke trials retain their existing separate registry.

No trader parameters or seeds were tuned. PRE_REG_DAX.md, Java, runtime and the live path were not edited. Scientific readiness, the clean split's source validity and external recall drivers remain their owners' responsibility.

## Follow-up cards

None created. This report and the audit H8 addendum are the build delivery. The required `tasks.py done` command updates `system/tasks/lab-dax-trial-identity.json` and regenerates `system/LAYERS.md` as its normal metadata side effect; the runner owns commit, ship and release.
