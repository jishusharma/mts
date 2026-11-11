MATCH=4 DIFF=0 NOT_IN_DATA=0

# Gemini Blind Read: CI Per-Test Limit Revert Audit (c2771d345 undoes 6b3d0cd27)

- **Card**: `gemini-blind-read-ci-revert-per-test-limit-1111`
- **Date**: 2026-11-11 UTC
- **Auditor**: Gemini (`gemini-3.8-flash-low`, throwaway worktree `gemini-q/gemini-blind-read-ci-revert-per-test-limit-1111`)
- **Target Commit**: `c2771d345e912b7cebcb056ce6f39121c1c2fb72` ("Result: reverted 6b3d0cd27 (per-test 120 s limit broke CI step 4.9, test_aibridge_chain long test); last-green bytes")
- **Original Breaking Commit**: `6b3d0cd274d1b802f7d26b682f0a7e96dc8ea31f` ("Result: every gate pytest call has a 120 s per-test limit (own plugin, no pytest-timeout installed; DECISION OURS); hung test fails by name")
- **Scope In**:
  - `scripts/dev/run_all_tests.py` (read)
  - `scripts/dev/extra_tests.tsv` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-ci-revert-per-test-limit-1111.md` (this report)
- **Scope Out**:
  - No edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit.

---

## Clause Verification Table

| # | Clause Requirement | Status | SOURCED File & Line / Command | Implementation Evidence & Verification Quotes |
|---|---|---|---|---|
| 1 | The revert removes every file and line 6b3d0cd27 added to the gate | MATCH | SOURCED `git diff 6b3d0cd27~1 c2771d345 -- scripts/dev/` (empty diff); SOURCED commit `c2771d345`: `scripts/dev/pytest_test_limit.py` (deleted 66 lines), `scripts/dev/test_pytest_test_limit.py` (deleted 40 lines), `scripts/dev/extra_tests.tsv:273` (deleted 1 line: `scripts/dev/test_pytest_test_limit.py`), `scripts/dev/run_all_tests.py` (deleted 10 lines: 8 lines at L207-214 defining `TEST_LIMIT_ARGS = ["-p", "pytest_test_limit"]`, and 2 usages in `pytest_cmd` and `build_plan` step 5c) | SOURCED `git show 6b3d0cd27`: added 123 lines, deleted 12 lines across 5 files. SOURCED `git show c2771d345`: deleted 123 lines, added 12 lines across the same 5 files. The 66-line plugin `scripts/dev/pytest_test_limit.py` was deleted (SOURCED `git show c2771d345:scripts/dev/pytest_test_limit.py` -> file deleted). The 40-line test file `scripts/dev/test_pytest_test_limit.py` was deleted (SOURCED `git show c2771d345:scripts/dev/test_pytest_test_limit.py` -> file deleted). The extra test entry was removed from `scripts/dev/extra_tests.tsv` (SOURCED `scripts/dev/extra_tests.tsv:270-272` ending with `scripts/dev/test_live_aid_learn.py`). All additions to `scripts/dev/run_all_tests.py` were reverted. Blob SHA comparison confirms byte-for-byte identity to pre-6b3d0cd27 state: `git rev-parse 6b3d0cd27~1:scripts/dev/run_all_tests.py` = `b6be08fc25f5bef3c9235f0b38a91f658a762f19` == `git rev-parse HEAD:scripts/dev/run_all_tests.py` = `b6be08fc25f5bef3c9235f0b38a91f658a762f19`. |
| 2 | No test still imports the removed plugin | MATCH | SOURCED `git grep "pytest_test_limit"` across the entire repository (0 matches in test files or codebase; 0 occurrences in `tests/`, `scripts/`, `dev/` or elsewhere except in task card JSONs describing the revert) | SOURCED `git grep -n "pytest_test_limit"` returns only `MyTradingSys/system/tasks/gemini-blind-read-ci-revert-per-test-limit-1111.json:39` (scope_in description). Grep for `import pytest_test_limit` or `from pytest_test_limit` yields 0 matches repo-wide. No test or script imports the removed plugin. |
| 3 | run_all_tests.py pytest commands match their pre-6b3d0cd27 form | MATCH | SOURCED `scripts/dev/run_all_tests.py:214-216` (`pytest_cmd`), SOURCED `scripts/dev/run_all_tests.py:696-697` (`cmd5c`); SOURCED `git rev-parse 6b3d0cd27~1:scripts/dev/run_all_tests.py` (`b6be08fc25f5bef3c9235f0b38a91f658a762f19`), SOURCED `git rev-parse HEAD:scripts/dev/run_all_tests.py` (`b6be08fc25f5bef3c9235f0b38a91f658a762f19`) | SOURCED `scripts/dev/run_all_tests.py:214-216`: `return [sys.executable, "-m", "pytest", *targets, "-q", "-p", "no:cacheprovider", *durations, transient_ignore_glob(root), f"--basetemp={Path(scratch) / 'bt'}", *[a for d in deselect for a in ("--deselect", d)]]`. SOURCED `scripts/dev/run_all_tests.py:696-697`: `cmd5c = [sys.executable, "-m", "pytest", "MyTradingSys/options/tests", "-q", "-p", "no:cacheprovider", transient_ignore_glob(), f"--basetemp={gate_tmp('mts_s5c_') / 'bt'}"]`. In both commands, `*TEST_LIMIT_ARGS` is completely gone. `git diff 6b3d0cd27~1 HEAD -- scripts/dev/run_all_tests.py` produces 0 diff. |
| 4 | Nothing left in the repo claims the 120 s limit is active | MATCH | SOURCED `git log -1 c2771d345` commit message; SOURCED `MyTradingSys/system/tasks/ship-gate-per-test-timeout-1111.json:30` (`state: "raw"`); SOURCED `MyTradingSys/system/tasks/cicd-run-per-test-limit-1111.json:29` (`"note": "Source: Builder shipgate Noticed. Mechanism owner: ship-gate-per-test-timeout-1111 (in review); align to it."`) | SOURCED `git log -1 c2771d345`: `"Result: reverted 6b3d0cd27 (per-test 120 s limit broke CI step 4.9, test_aibridge_chain long test); last-green bytes"`, `"Next: END: revert of the limit; C re-lands it with a per-test allowance"`. Neither active documentation nor task cards claim the limit is currently active: card `ship-gate-per-test-timeout-1111.json` is back in `state: "raw"`, `cicd-run-per-test-limit-1111.json` explicitly states mechanism is not yet in place, and repo-wide greps for `MTS_TEST_LIMIT_S` return 0 results across all tracked files. |

---

## Detailed Audit Summary

1. **Gate Reversion Verification**:
   - `6b3d0cd27` introduced `scripts/dev/pytest_test_limit.py`, added it to `scripts/dev/extra_tests.tsv`, added unit tests in `scripts/dev/test_pytest_test_limit.py`, and injected `TEST_LIMIT_ARGS = ["-p", "pytest_test_limit"]` into `scripts/dev/run_all_tests.py`.
   - `c2771d345` inverted this changeset completely, deleting `scripts/dev/pytest_test_limit.py` and `scripts/dev/test_pytest_test_limit.py`, removing `test_pytest_test_limit.py` from `extra_tests.tsv`, and restoring `run_all_tests.py` to its exact pre-6b3d0cd27 blob (`b6be08fc25f5bef3c9235f0b38a91f658a762f19`).
2. **Import Cleanliness**:
   - Zero tests or scripts import or reference `pytest_test_limit` or `test_pytest_test_limit`.
3. **Pytest Invocations**:
   - Both `pytest_cmd` (SOURCED line 214) and `cmd5c` (SOURCED line 696) in `scripts/dev/run_all_tests.py` contain no `-p pytest_test_limit` argument.
4. **Active Limit Claims**:
   - No task cards or documentation assert that the 120 s per-test limit is active; `ship-gate-per-test-timeout-1111` is reset to `raw` awaiting C's re-landing with per-test allowances.
