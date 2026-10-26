# B150 - The test gate is a hand-maintained allow-list: new live-path safety tests (dlm_failure_cap, auto_trader_blocklist, auto_trader_sizes) are not in it; the calibration test pins an empty blocklist; nothing in code enforces restoring the parked blocklist

Status: CLOSED. Severity: MED. Opened 2026-10-09.
Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Source: research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md (audit revalidated by four read-only workers; no code edited).

## Defect

The test gate is a hand-maintained allow-list: new live-path safety tests (dlm_failure_cap, auto_trader_blocklist, auto_trader_sizes) are not in it; the calibration test pins an empty blocklist; nothing in code enforces restoring the parked blocklist.

## Evidence

- scripts/dev/run_all_tests.py:91-97 lists execution test modules by name. Worker count: 173 tracked test_*.py, 154 run by the full gate, 19 not run, of which 14 are live code tests, incl. execution/test_dlm_failure_cap.py, test_auto_trader_blocklist.py, test_auto_trader_sizes.py, test_auto_trader_confirm.py (all pass when run by hand, 38 tests). I re-checked that run_all_tests.py names test_dlm_aggregate and test_orphan_sweep_loop but not these. A regression in the DLM failure cap would not fail the gate.
- Three ungated tests FAIL at HEAD (test_audit_t0_checks::test_find_leftover_names_matches_rejected_and_raw, two in tests/test_worker_prefix_hash.py): look Windows-specific, undiagnosed.
- auto_trader_config.json (2026-10-08, '_calibration') parked trade_blocklist; routes ~21 prefixes to jishu_1..jishu_21 with size_overrides 20-1000 USD. Nothing in code reads trade_blocklist_parked or _calibration. test_auto_trader_blocklist.py:96 test_shipped_calibration_config_blocks_no_layer ASSERTS an empty blocklist, so restoring the list (as _calibration instructs) will fail the gate. Mainnet itself stays protected independently (executor called without --mainnet, typed confirmation at deribit_orders.py:177-199, named accounts refused on mainnet :153-155, 50 USD cap).

## Fix shape

Make the gate discover tests (glob test_*.py, with an explicit skip-list that needs a reason) or add a check that fails when a tracked execution/ test is neither listed nor skip-listed. Diagnose the 3 failing ungated tests. Replace the empty-blocklist assertion with a check that either the blocklist is present or a calibration flag explicitly allows empty, and add a mainnet-path guard that refuses non-empty-size_overrides/empty-blocklist config.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md

## Receipt

2026-10-09 consolidate session: gate now lists test_dlm_failure_cap, test_auto_trader_blocklist, test_auto_trader_sizes, test_auto_trader_confirm, test_b146/b148; MyTradingSys/tests/test_gate_discovery_b150.py fails when any execution/test_*.py is neither gated nor in SKIP-with-reason. Open: the 3 failing ungated tests (audit_t0_checks, worker_prefix_hash), non-execution dirs not covered by discovery, blocklist-restore guard (test_shipped_calibration_config_blocks_no_layer still pins an empty list).

2026-10-10 close (b7e644a): gate discovery over all tracked tests (MyTradingSys/tests/test_gate_discovery_b150.py), scripts/dev/run_extra_tests.py (step 3xt) runs the 14 files outside the collected dirs, test_fix3_mutants_offline added to step 1. Diagnosed: worker prefix tests failed because core.autocrlf=true checked worker_prefix.md out as CRLF (run_worker refuses it, so the scheduled worker never ran on Windows): .gitattributes pins it to LF. test_audit_t0 patched REPO for a tmp path. Blocklist restore: executor.mainnet_config_refusals refuses mainnet while trade_blocklist is empty with trade_blocklist_parked set or size_overrides present (7 tests in test_mainnet_plan_check.py); test_auto_trader_blocklist no longer pins an empty list.

# END
