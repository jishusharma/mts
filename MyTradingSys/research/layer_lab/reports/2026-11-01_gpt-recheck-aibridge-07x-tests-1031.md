# GPT recheck: AIBridge 0.7.x tests by mutation

Verdict: **FIX-FIRST** — 3/4 hand mutants were killed by existing tests; the extension POST cache policy mutant survived the permanent suite and was killed by a contract-derived scratch assertion.

## Scope and evidence

Read the three requested tests, `scripts/aibridge/extension/background.js`, `scripts/aibridge/scripts/run-task.ps1`, `scripts/aibridge/src/checks.ps1`, `scripts/aibridge/docs/V07_CONTRACT.md`, `MyTradingSys/items/B184_aibridge_multiblock_and_auto_run.md`, `MyTradingSys/system/AIBRIDGE_LANE.md`, and `MyTradingSys/backtest/PRE_REG_TEMPLATE.md`. No backtest or market data applies. The report does not read holdout data.

The source contract specifies task PASS/FAIL reporting and a per-command kind label (`V07_CONTRACT.md:22-28,44`); B184 records the shipped AIBridge behavior and reports `rid`/STALE_REPLY/no-store (`items/B184_aibridge_multiblock_and_auto_run.md:29-36`). The cited DSA session transcript/field report files themselves were not present in this checkout; the committed B184 note and V07 contract were available. This is recorded as NOT_IN_DATA below.

## Assertion map

| Test assertion | Guarded behavior | Source / result |
|---|---|---|
| `test_failed_line_with_exit_zero_is_a_fail` (`test_aibridge_task_gate_exit.py:34-37`) | A zero process exit plus `FAILED: N step(s)` must produce task FAIL and exit 1. | Runner fail-pattern gate (`run-task.ps1:90-94,116-117`); contract task result (`V07_CONTRACT.md:22-28`). M1 killed. |
| `test_clean_step_still_passes` (`:40-42`) | `FAILED: 0` is not a failure; successful control remains PASS/0. | Runner default pattern excludes zero (`run-task.ps1:90-94`). Baseline control passes. |
| `test_native_exit_1_then_write_output_is_a_fail` (`:45-48`) | Preserve native process failure after a later successful PowerShell statement. | Runner resets and propagates `$LASTEXITCODE` (`run-task.ps1:70-73`). M2 killed. |
| `test_exit_code_line_under_exit_zero_is_a_fail` (`:51-53`) | Nonzero `EXIT_CODE=N` summary is a failure. | Runner default fail pattern (`run-task.ps1:90-94`). Baseline passes. |
| `test_gate_step_without_summary_is_a_fail` (`:56-63`) | Real gate playbooks require `ALL TESTS PASSED`; plain inline step is an unaffected control. | Test reads `mts-gate.json` and `mts-ship.json`; V07 task reports require PASS/FAIL (`:22-28`). Baseline passes. |
| `test_control_write_output_after_clean_native_passes` (`:66-68`) | Successful native child followed by output remains PASS/0. | Runner propagation behavior (`run-task.ps1:70-73`). Baseline passes. |
| `test_child_temp_is_outside_a_git_repo_around_the_bridge_folder` (`:71-82`) | Child TEMP is outside bridge repo ancestry. | V07 contract child TEMP location (`V07_CONTRACT.md:47-48`). Not run in mutation harness because this test invokes Git, which was outside the permitted commands. |
| `test_quoted_write_words_do_not_make_a_read_block_write` (`test_aibridge_cmd_kind.py:23-26`) | Quoted search-pattern data does not change kind to write. | Kind classifier blanks quoted text before regex classification (`checks.ps1:199-210`); V07 kind label (`V07_CONTRACT.md:44`). M3 killed. |
| `test_real_writes_still_write` (`test_aibridge_cmd_kind.py:28-31`) | Actual file writes, git commit and redirection classify as write. | `checks.ps1:202-210`; baseline passes. |
| `test_payload_files_exist_and_versions_agree` (`test_aibridge_payload.py:22-30`) | Required payload components exist and extension/agent/loop versions agree. | Contract identifies payload (`V07_CONTRACT.md:3`); structural/version checks. |
| `test_payload_is_ascii_lf_no_bom` (`:39-50`) | Payload encoding and line-ending constraints. | AIBridge lane rules (`AIBRIDGE_LANE.md:27-29`). Not run in mutation harness because it shells out to Git to inspect index EOL. |
| `test_extension_helpers_node` (`:53-55`) | Extension helper behavior under Node. | `scripts/aibridge/tests/loop.test.js`; baseline passes. |
| `test_selftest_registry_variable_is_unique_per_run` (`:81-89`) | Fresh per-run registry variable prevents concurrent self-test collisions. | Test's incident description at `:84-86`; the referenced 2026-10-16 gate log is not in scope files. Not executed separately in baseline (covered by baseline focused suite). |
| `test_agent_live_selftest` (`:92-97`) | Live scratch agent integrated behavior and summary. | Contract points to 36 live checks (`V07_CONTRACT.md:3`). Full focused run failed here due HKCU write denial and scratch temp access denial in this sandbox (details below). |

The tests cover the named task gate and kind behavior well. Payload assertions include presence/version/format/helper/self-test checks, but no permanent assertion protects the POST `/run` `cache: 'no-store'` contract. The separate scratch check proves this omission.

## Mutation execution

Reproduction command (from repository root):

```powershell
python MyTradingSys/research/layer_lab/aibridge_07x_mutation_audit.py.txt
```

The harness copies the payload and focused tests into disposable directories under the workspace, applies one replacement per mutant, and records pytest exit/results. Baseline harness command was `python -m pytest -q MyTradingSys/tests/test_aibridge_task_gate_exit.py MyTradingSys/tests/test_aibridge_cmd_kind.py MyTradingSys/tests/test_aibridge_payload.py -k "not test_agent_live_selftest and not test_child_temp_is_outside_a_git_repo_around_the_bridge_folder and not test_payload_is_ascii_lf_no_bom"`: **11 passed, 3 deselected, exit 0**.

| Mutant and exact scratch diff | Executed result |
|---|---|
| M1 `run-task.ps1`: `if ($out -match $fo) { $ok = $false; $why = "output matched fail pattern /$fo/ although exit was $code" }` → `# MUTANT: summary detector removed` | Existing `test_failed_line_with_exit_zero_is_a_fail`: **killed**, pytest exit 1. Mutant printed TASK PASS over `FAILED: 2 step(s)`. |
| M2 `run-task.ps1`: `if (`$null -ne `$global:LASTEXITCODE) { exit [int]`$global:LASTEXITCODE }` → `# MUTANT: native exit code ignored` | Existing `test_native_exit_1_then_write_output_is_a_fail`: **killed**, pytest exit 1. Mutant printed PASS after native `python` exit 1. |
| M3 `checks.ps1`: `$Cmd = [regex]::Replace($Cmd, '\x27[^\x27\r\n]*\x27|\x22[^\x22\r\n]*\x22', '\x27\x27')` → `# MUTANT: quoted text not masked` | Existing `test_quoted_write_words_do_not_make_a_read_block_write`: **killed**, pytest exit 1 (`write` observed, expected `read`). |
| M4 `background.js`: `method: 'POST',\n      cache: 'no-store',` → `method: 'POST',` | Existing focused tests **survived** this mutant. Contract-derived scratch assertion checks that POST `/run` options include `cache: 'no-store'`: original **PASS**, mutant **FAIL**. |

Unmutated full focused command `python -m pytest MyTradingSys/tests/test_aibridge_task_gate_exit.py MyTradingSys/tests/test_aibridge_cmd_kind.py MyTradingSys/tests/test_aibridge_payload.py -q` produced **13 passed, 1 failed**. The failure was `test_agent_live_selftest`: PowerShell reported access denied writing its temp scratch files, and the Python self-test ended with `PermissionError: [WinError 5] Access is denied` on `HKCU\Environment`. This is an environment limitation, not counted as a source defect. The reproducible harness excludes that integration test and the two tests that invoke Git.

## Findings

| Severity | File:line | What is wrong | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `scripts/aibridge/extension/background.js:46-49`; tests `test_aibridge_payload.py:22-30,53-55` | Existing permanent tests do not guard the POST `/run` no-cache option. | M4 survived existing suite; a scratch spec check passed on original and failed after removing `cache: 'no-store'`. B184:34 records no-store; `background.js:48` implements it. | Add a contract-derived assertion to `test_aibridge_payload.py` and run through the registered focused test gate. Follow-up card `aibridge-extension-guard-no-store-respon` (SONNET, build) includes `test_aibridge_payload.py` and `scripts/dev/run_extra_tests.py`. |
| LOW / NOT_IN_DATA | `MyTradingSys/tests/test_aibridge_payload.py:4-5`; `MyTradingSys/items/B184_aibridge_multiblock_and_auto_run.md:33-36` | The test docstring attributes expectations to DSA coordinator field reports, but the underlying cited transcript/report artifacts are not included in this checkout. | B184 summarizes the field reports and the V07 contract is available; original transcript files are not. | Keep claims anchored to the committed B184 note/V07 contract; add transcript file/line references if the source artifacts are later checked in. |

## Follow-up

- `aibridge-extension-guard-no-store-respon` — READY SONNET build card; regression assertion path `MyTradingSys/tests/test_aibridge_payload.py`; registration path `scripts/dev/run_extra_tests.py`; implementation path `scripts/aibridge/extension/background.js`.

Harness saved at `MyTradingSys/research/layer_lab/aibridge_07x_mutation_audit.py.txt`. No production code, permanent tests, specs, holdout data, or market data were changed/read for this audit.
