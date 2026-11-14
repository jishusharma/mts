# Test Gap Report: `scripts/dev/run_staged_tests.py`

- **Card ID**: `testgap-run-staged-tests-gemini4-1114`
- **Target**: `scripts/dev/run_staged_tests.py` (41 lines, SOURCED: `scripts/dev/run_staged_tests.py:1-41`)
- **Test file created**: `MyTradingSys/research/layer_lab/gemini_1114d/testgap-run-staged-tests/test_run_staged_tests.py`

## 1. Existing Coverage (`git grep -l "run_staged_tests" scripts MyTradingSys`)

- `git ls-files "*test_run_staged_tests*"`: 0 files (OURS: no test file named for `run_staged_tests.py`).
- References in existing test files:
  - `scripts/dev/test_gate_select.py:11`: `"1", "python scripts/dev/run_staged_tests.py MyTradingSys/execution -- test_risk_guard"` (SOURCED: `scripts/dev/test_gate_select.py:11`, string literal in `STEPS`).
  - `scripts/dev/test_gate_select.py:277`: `"run_staged_tests", "gate_impact"` (SOURCED: `scripts/dev/test_gate_select.py:277`, `GATE_RE` check).
  - `scripts/dev/test_nowin_calls.py:20`: `"run_staged_tests.py": 1` (SOURCED: `scripts/dev/test_nowin_calls.py:20`, subprocess call count allowlist).
  - `MyTradingSys/tests/test_target_nearest_node.py:4`: `# Staged as .new with math_object_builder.py.new; run via scripts/dev/run_staged_tests.py.` (SOURCED: `MyTradingSys/tests/test_target_nearest_node.py:4`, comment only).
- Conclusion: 0 functional unit tests existed for `scripts/dev/run_staged_tests.py` (OURS).

## 2. Functions & Hand-Computed Cases

`scripts/dev/run_staged_tests.py` defines 1 function: `main(argv)` (`scripts/dev/run_staged_tests.py:15-38`; not pure: reads/copies files, creates/deletes a temp dir, prints, calls `subprocess.call`).

Hand-computed test cases in `test_run_staged_tests.py` (all OURS, `subprocess.call` monkeypatched):
1. `test_py_new_overrides_live_py_and_copies_json_unittest_cmd`: `mod.py.new` overrides `mod.py` (`p.name[:-4]` at `scripts/dev/run_staged_tests.py:29`), `cfg.json` is copied, `cmd` is `[sys.executable, "-m", "unittest", "-v", "test_alpha", "test_beta"]` (`scripts/dev/run_staged_tests.py:32`), `MTS_REPO_ROOT == str(Path.cwd())` (`scripts/dev/run_staged_tests.py:36`), return code `0`, temp dir removed (`scripts/dev/run_staged_tests.py:38`).
2. `test_script_mode_and_fake_replacement`: `--script runner.py --fake fake_real.py=real.py` copies `fake_real.py` over `real.py` (`scripts/dev/run_staged_tests.py:31`) and sets `cmd` to `[sys.executable, "runner.py"]` (`scripts/dev/run_staged_tests.py:32`), return code `0`.
3. `test_nonzero_exit_code_propagates_and_cleans_up`: `subprocess.call` returning `3` causes `main` to return `3` (`scripts/dev/run_staged_tests.py:36`) and removes temp dir (`scripts/dev/run_staged_tests.py:38`).
4. `test_later_dir_overrides_earlier_dir_and_cleanup_on_exception`: second dir `d2/shared.py` overwrites `d1/shared.py` (`scripts/dev/run_staged_tests.py:25-27`), and `RuntimeError("boom")` still cleans up temp dir via `finally` (`scripts/dev/run_staged_tests.py:37-38`).

## 3. Verification

- `python -m pytest MyTradingSys/research/layer_lab/gemini_1114d/testgap-run-staged-tests/test_run_staged_tests.py -v`: `4 passed in 0.23s` (OURS).
- Scratch-copy mutation check: mutated `tmp / p.name[:-4]` -> `tmp / p.name` at line 29 in a temp copy; `test_py_new_overrides_live_py_and_copies_json_unittest_cmd` failed with `AssertionError` (`1 failed, 3 passed in 0.43s`) (OURS).
