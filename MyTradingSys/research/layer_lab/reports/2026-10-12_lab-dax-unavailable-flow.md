Changed files: `MyTradingSys/backtest/tom_dax_bt.py`, `MyTradingSys/backtest/test_tom_dax_bt.py`, `MyTradingSys/research/layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md`. H6 regression RED (1 test, 5 assertion failures) -> GREEN (1 test OK); full harness GREEN (55 tests OK).

# H6: unavailable DAX order flow

Card: `lab-dax-unavailable-flow`. Surface: COD. Result date: 2026-10-12 UTC.

## What was checked

Repository-relative references:

- Audit file legend and H6: `MyTradingSys/research/layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md:13-23,61` (historical line references retained in the finding).
- Source contract: `MyTradingSys/research/tom_transfer_2026-10-11/PRE_REG_DAX.md:7-12`; half-volume encoding: `MyTradingSys/backtest/dax_data.py:98-106`; Java zero-delta labels and CVD serialization: `src/main/java/datafeed/MarketDataSnapshot.java:737-777`.
- Consumers: `MyTradingSys/runtime/math_object_builder.py:440-470`; `MyTradingSys/backtest/verdict.py:49-64,119-144`; `MyTradingSys/backtest/tom_bt.py:119-133`.
- Adapter changes: `MyTradingSys/backtest/tom_dax_bt.py:81,146-213`. Regression and unmasked preservation: `MyTradingSys/backtest/test_tom_dax_bt.py:319-369`.

Data: three in-memory synthetic bars, total volume 1 and taker-buy volume 0.5 per bar. Mirrored long/short candidates use entry 100, stop 99/101 and target 103/97. The test-only shift of four lifts the surviving rejection proof to five, exposing the downstream cap. This is an assertion fixture, not a sourced trading parameter. No real-data backtest, recall or holdout read; no performance trial was conducted.

## Findings

| Severity | File:line | Finding / classification | Evidence | Fix |
|---|---|---|---|---|
| HIGH | Audit H6:61; `MarketDataSnapshot.java:752-755`; `math_object_builder.py:467-469` | MISMATCH before fix: unavailable aggressor information became a long contradiction. | Hand calculation: 2 * 0.5 - 1 = 0; Java labels zero negative. RED regression returned long `(contradiction, WATCH)` and short `(aligned, SETUP_FORMING)`. | Clear placeholder CVD before gates, explicitly mark it unavailable. |
| HIGH | `tom_dax_bt.py:178-187`; `test_tom_dax_bt.py:319-360` | MATCH after fix: neither mirror receives directional delta evidence or a false contradiction. | GREEN test uses the actual `build_math_object` / `proof_dir_of` and verdict path; both yield `(aligned, SETUP_FORMING)`, with no positive/negative labels. Source snapshots are unchanged. | CVD availability/confidence `UNAVAILABLE`, value `None`, recent CVD empty, last-three labels empty, and both slope fields `unavailable`. Existing four proof flags stay masked. |
| MED | `tom_dax_bt.py:81,191-195`; `test_tom_dax_bt.py:362-369` | MATCH: adapter cache version changed; unmasked CVD retained. | Schema is `java-b144-no-volume-spike-net-rr-primary-unavailable-flow-v3`; the existing compatibility guard rejects earlier schemas. Explicit empty-mask identity assertion passes, including falling CVD. | Regenerate incompatible rows through the existing cache guard; apply clearing only when `cvd_aligned` is masked. |

The shared consumer still returns its existing status `aligned` when there is no contradiction. This status does not establish observed supportive order flow; the adapter explicitly records input unavailability. This resolves H6 within the adapter and does not establish overall scientific readiness.

## Red then green verification

All commands ran from `F:\MTS\mts-codex-lab`, with `PYTHONPATH` set to that root:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -B -m unittest MyTradingSys.backtest.test_tom_dax_bt.TestMask.test_half_volume_order_flow_unavailable_long_short_parity
```

EXPECT: absent aggressor data produces neither positive nor negative evidence; mirrored candidates get equal direction status and verdict.

RESULT (2026-10-12, COD lab), before editing the adapter: exit 1. Assertion excerpts and complete test summary:

```text
FFFFF
AssertionError: 'contradiction' != 'aligned'
AssertionError: {'negative'} is not false
AssertionError: 'WATCH' != 'SETUP_FORMING'
AssertionError: {'negative'} is not false
AssertionError: Lists differ: [('contradiction', 'WATCH'), ('aligned', 'SETUP_FORMING')] != [('aligned', 'SETUP_FORMING'), ('aligned', 'SETUP_FORMING')]
Ran 1 test in 0.017s
FAILED (failures=5)
```

RESULT (2026-10-12, COD lab), same command after the adapter fix: exit 0.

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.015s

OK
```

Full authorized harness command:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -B MyTradingSys/backtest/test_tom_dax_bt.py
```

RESULT (2026-10-12, COD lab): exit 0. Complete output:

```text
.......................................................
----------------------------------------------------------------------
Ran 55 tests in 0.340s

OK
wrote F:\MTS\mts-codex-lab\MyTradingSys\backtest\tmpcpfy1zx1\report.md (8 registry rows, 0s)
```

That report/registry output is the harness's temporary synthetic report fixture, not a market outcome run. No quick/all-tests gate was run; the runner performs its shipping gate. Shared Java/runtime files, original pre-registration and trial registries were not edited. The task-card JSON is updated only by the requested `tasks.py done` command.

## Follow-up cards created

None. H6 is fixed within scope; the remaining audit findings keep their existing owners.
