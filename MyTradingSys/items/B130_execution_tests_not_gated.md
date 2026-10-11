# B130 - execution/tests not collected by the gate

Status: OPEN
Opened: 2026-10-04
Filed by: MTS-2026-10-04-0916Z-DSA-COO

## Defect

scripts/dev/run_all_tests.py does not collect MyTradingSys/execution/tests/.
The directory was created 2026-10-04 by session MTS-2026-10-04-1130Z-APP-BLD-t050-phase3
(commit f088b52), which added MyTradingSys/execution/tests/test_deribit_orders_phase3.py
(8 tests). run_all_tests.py --quick passed without running any of them.

## Effect

The test file exists but is invisible to the gate. A regression in
deribit_orders.py would not fire until a human ran the file by hand.

## Evidence

- Commit f088b52 touched 4 files including
  MyTradingSys/execution/tests/test_deribit_orders_phase3.py.
- Session reply from MTS-2026-10-04-1130Z-APP-BLD-t050-phase3: "the new test
  file isn't wired into run_all_tests.py, because that file wasn't in your
  scope."
- Running the file directly: 8 passed.

## Fix shape

Add MyTradingSys/execution/tests to the pytest path list in
scripts/dev/run_all_tests.py, same as the other layer test dirs. Add a guard
test that fails if the path is not present.

## Not fixed here

Filing only. Gate edit belongs to a follow-up session.

## 2026-10-04T12:50Z - CLOSED

Fixed: PYTEST_LAYER_PATHS in scripts/dev/run_all_tests.py gains
"MyTradingSys/execution/tests". Guard test added at
MyTradingSys/tests/test_run_all_tests_paths.py; it fails on the pre-change
runner and passes after. 8 deribit_orders phase 3 tests now execute in step 4
of the gate.
