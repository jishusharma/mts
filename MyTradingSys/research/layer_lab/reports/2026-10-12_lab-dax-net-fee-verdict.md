Changed files: tom_dax_bt.py, test_tom_dax_bt.py, historical audit report (H5 addendum only), this report. H5 red then green; 40 synthetic tests pass.

Card: `lab-dax-net-fee-verdict`. Surface: COD. Date: 2026-10-12 UTC.

## What was checked

Paths relative to the workspace root:

- `MyTradingSys/research/layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md:14-26,60` (file legend, H5 evidence and proposed fix); addendum at 152-158.
- `MyTradingSys/backtest/tom_dax_bt.py:18-20,68-77,176-198,450-487,742-747`: primary arm, cache version, selection, frozen monthly floor/fee metadata and generated report labels. Historical D:176-181,197-199,621-623 cited by H5 have shifted after preceding fixes; the gross overwrite was at pre-change lines 182-187 and primary labels at 67,745.
- `MyTradingSys/backtest/test_tom_dax_bt.py:426-473`: regression, all-candidate preservation, proof shift and input immutability.
- Read-only sources: `src/main/java/datafeed/SetupCandidatesBuilder.java:153-160`; `src/main/java/datafeed/ExecutionMathConstants.java:23-37`; `MyTradingSys/backtest/layers/FORMULAS.md:400-406`; `MyTradingSys/backtest/fees.py:34-50`; `MyTradingSys/backtest/verdict.py:65-94`; `MyTradingSys/system/net_rr_floor.json:2`; historical `PRE_REG_DAX.md:1-38`.

Data: synthetic fixtures only. The regression uses entry/zone/current price 100, stop 99, target 101.25, symbol GER40, five unmasked proofs and floor explicitly frozen at 1.25 to isolate the RR gate. No archive, holdout or real BTC data was read; no empirical trial was performed.

## Findings

| Severity | File:line | Status and finding | Evidence | Fix |
|---|---|---|---|---|
| HIGH | tom_dax_bt.py:68,183-198 | MATCH: H5 primary now preserves per-instrument net RR; pre-fix selection was MISMATCH | Independent formula: cost = 2 * .000005 * 100 = .001; net = (1.25-.001)/(1+.001) = 1.247752247752 < 1.25. Old primary returned SETUP_FORMING; fixed primary returns WAIT_RR. | Removed gross overwrite and gross-only arm; `coded` is sole primary. |
| MED | tom_dax_bt.py:77,176-180,450-487 | MATCH: pre-fix caches refused; monthly verdict floor is fixed during generation | Version advanced to java-b144-no-volume-spike-net-rr-primary-v2; metadata records floor, FDAX fee and ExecutionMathConstants hash. | Regenerate prior rows with current Java and rows --force before an authorized future run. |
| LOW | historical audit report:152-158; tom_dax_bt.py:742-747 | MATCH: historical selection contract preserved with addendum | Original PRE_REG_DAX.md remains untouched; generated reports identify the reviewed primary contract. | Added dated H5 contract; no gross-only arm remains. |

Full immutable run/snapshot provenance remains the separate H8 task (`lab-dax-trial-identity`). Recorded current fee/hash is not proof of the generator version of an arbitrary supplied snapshot. Other audit findings and readiness gates remain outside this fix; no market edge is established.

## Red then green

Commands run from `F:\MTS\mts-codex-lab`, with `$env:PYTHONPATH=(Get-Location).Path`.

EXPECT: the new test fails against the original harness because gross RR 1.25 passes the floor.

RESULT (2026-10-12, COD lab), before production changes:

```text
python -m unittest MyTradingSys.backtest.test_tom_dax_bt.TestVerdictPair.test_primary_rejects_ger40_gross_rr_at_floor
FAIL: test_primary_rejects_ger40_gross_rr_at_floor
AssertionError: 'SETUP_FORMING' != 'WAIT_RR'
Ran 1 test in 0.013s
FAILED (failures=1)
exit code 1
```

RESULT (2026-10-12, COD lab), after changes:

```text
python -m unittest MyTradingSys.backtest.test_tom_dax_bt.TestVerdictPair.test_primary_rejects_ger40_gross_rr_at_floor
.
Ran 1 test in 0.012s
OK
exit code 0

python MyTradingSys/backtest/test_tom_dax_bt.py
........................................
Ran 40 tests in 0.102s
OK
exit code 0
```

The complete allowed test file covers synthetic adapter, execution, masking, cache and split fixtures. The quick gate is reserved for the runner. No git or sync command was run.

## Follow-up cards

None created. H8 already has `lab-dax-trial-identity` (historical audit report:135). Card completion updates only its existing task JSON via the requested `tasks.py done` command; the runner owns commit, ship and release.
