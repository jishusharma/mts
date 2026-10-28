# CI: portable spawn-audit logging fixture

Fixed `MyTradingSys/tests/test_nowin_audit.py:26`: exercise the real nowin wrapper over a fake original process constructor. Windows creation flags no longer reach a real POSIX Popen. Both explicit flag values, parent/child IDs, command, elapsed time, and has_create_no_window are asserted. Context patches restore the original constructor and install marker. No production code or processes were changed.

Red baseline: [CI run 39198751302](https://github.com/jishusharma/mts/actions/runs/39198751302), head 74edd16043515bfbaf4b4faa1fcec7fe9299ceaa. Ubuntu Step 4g failed test_spawn_logging_opt_in with `ValueError: creationflags is only supported on Windows platforms`; 174 other tests passed. Windows job succeeded. Evidence retrieved from the public check-run annotations, not inferred from a Windows-only rerun.

Validation: `python -m pytest MyTradingSys/tests/test_nowin_audit.py scripts/dev/test_nowin.py -q` -> **12 passed in 0.45s**. A no-op _log_spawn mutation caused the positive fixture to fail at the missing-log assertion; `test_dummy_spawn_log_is_rejected` preserves that check. `git diff --check` passed. Linux CI confirmation remains required after push; the CI task remains active until both OS jobs pass.

Shipping uses the required `sync.py ship --fix-ci` gate, because the existing trunk failure blocks unrelated code delivery. The review-gate hardening already passed its 23 selected smoke steps before that CI block; this test repair addresses the named Ubuntu failure. No production exemption or CI bypass was added.
