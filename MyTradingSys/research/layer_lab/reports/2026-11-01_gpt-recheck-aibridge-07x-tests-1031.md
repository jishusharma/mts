# GPT: cross-vendor recheck of AIBridge 0.7.x tests by mutation

Verdict: **BLOCKED**

The card simultaneously requires `Change no code and no spec` (audit step 3; `MyTradingSys/system/tasks/gpt-recheck-aibridge-07x-tests-1031.json:48`) and a new Python test at `MyTradingSys/tests/test_aibridge_07x_survivors.py` (card `tests` field, JSON line 53). The layer-lab audit guard allows audit outputs only under `research/layer_lab/` and `system/tasks/` (`MyTradingSys/system/LAYER_LAB.md`, Guards), so adding the requested test is out of scope. This report is in the allowed audit output location. As a result, the required end state (“each test fails on the mutated scratch copy and passes on original”) cannot be delivered under these instructions. Per the user-provided blocked rule, the task is not marked done.

## Checked

- Read all assertions in `MyTradingSys/tests/test_aibridge_task_gate_exit.py:22-83`, `MyTradingSys/tests/test_aibridge_cmd_kind.py:17-31`, `MyTradingSys/tests/test_aibridge_payload.py:22-96`, and `scripts/aibridge/extension/background.js:1-62`.
- Compared assertions to `scripts/aibridge/scripts/run-task.ps1:36-79, 96-116`, `scripts/aibridge/src/checks.ps1:168-185`, `scripts/aibridge/tests/agent_live_selftest.py` (task HTTP and concurrency checks), and `scripts/aibridge/tests/loop.test.js`.
- Available incident evidence: `MyTradingSys/research/BUGS.md:338` (B209), `MyTradingSys/items/B184_aibridge_multiblock_and_auto_run.md:1-35`, and `MyTradingSys/system/AIBRIDGE_LANE.md:43-49`. The original DSA coordinator field reports named in `test_aibridge_payload.py:4-5` are not present as standalone source files in this checkout; the available B184 summary documents the behaviors, but does not independently substantiate all field-report details.
- No backtest or market data was involved; PRE_REG_TEMPLATE does not apply.

## Assertion and mutation coverage

| Severity | File:line | What is wrong / assertion result if guarded behavior is removed | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `test_aibridge_task_gate_exit.py:34-37` | Kills removal of the default `FAILED: N step(s)` fail pattern: expects FAIL and rc 1 on “FAILED: 2” with shell exit 0. | `run-task.ps1:62-68`; B209 `BUGS.md:338`. | Keep; assertion is directly coupled to the B209 guard. |
| LOW | `test_aibridge_task_gate_exit.py:40-42` | Control; intentionally survives removing the failure guard because `FAILED: 0` must pass. | `run-task.ps1:62-68`. | Keep as the clean-output control. |
| LOW | `test_aibridge_task_gate_exit.py:45-49` | Kills removal of the native process exit-code propagation; Python exit 1 followed by successful `Write-Output` must remain FAIL/rc 1. | `run-task.ps1:44-47` propagates `$LASTEXITCODE`; B209 D3 history in test docstring. | Keep. |
| LOW | `test_aibridge_task_gate_exit.py:51-54` | Kills removal of the `EXIT_CODE=N` output check; positive code line beneath shell `exit 0` must fail. | `run-task.ps1:65-68`. | Keep. |
| LOW | `test_aibridge_task_gate_exit.py:56-64` | `expect=ALL TESTS PASSED` assertions catch removal of the two playbook expectations, but the inline control at 62-63 passes with no `expect`; it does not exercise a mutated gate playbook through the runner. | Test reads `tasks/mts-gate.json` and `mts-ship.json`; runner applies `expect` at `run-task.ps1:59-63`. | Add a runner-level test using a scratch playbook with `expect` and incomplete output, plus passing matching output. |
| LOW | `test_aibridge_task_gate_exit.py:66-68` | Control; survives removal of guards for ordinary successful commands. | `run-task.ps1:58-68`. | Keep. |
| LOW | `test_aibridge_task_gate_exit.py:71-83` | Unrelated to the requested task EXIT_CODE mutation; checks TEMP isolation. It will survive removal of task gate guards. | Assertion concerns `Scratch` and `TEMP`, not task result code. | Keep in a separate focused test if desired. |
| LOW | `test_aibridge_cmd_kind.py:23-26` | Kills removal of quoted-string blanking for the supplied quoted write words; both commands classify as read only when quoted content is ignored. | `checks.ps1:181-184`; B209 item 5 `BUGS.md:338`. | Keep. |
| LOW | `test_aibridge_cmd_kind.py:28-31` | Controls catch over-broad change to classify real writes as read; quoted-string mutation alone should not break these. | `checks.ps1:176-180, 184-185`. | Keep. |
| MED | `test_aibridge_payload.py:22-29` | File existence and three version checks do not detect removal of any runtime payload behavior; all assertions survive such behavior mutations unless the version string/files also change. | Assertions inspect presence/version only. Background request payload is assembled at `background.js:46-50`. | Add direct background-worker test asserting the serialized POST includes `task`, `task_params`, and `task_spec` when supplied, routes to selected machine, and omits undefined optional fields. |
| LOW | `test_aibridge_payload.py:39-49` | BOM/ASCII/EOL checks are package hygiene; they survive behavioral mutations that preserve encoding. | Assertions only inspect bytes/EOL/decoding. | Keep as hygiene coverage. |
| LOW | `test_aibridge_payload.py:52-55` | Invokes loop helper tests, not `background.js`; mutation of background POST payload survives. Loop tests cover parse/format/echo and helper behavior. | `loop.test.js` imports only `extension/loop.js`; no background worker import. | Add the payload test described above; keep helper test. |
| LOW | `test_aibridge_payload.py:58-59, 62-77` | Timeout constant and timeout cleanup helper do not assert bridge payload behavior. | Code-level timeout mechanics only. | Keep; unrelated to payload mutation. |
| LOW | `test_aibridge_payload.py:80-88` | Tests unique HKCU env names, not `background.js` payload; survives payload-field removal. | `agent_live_selftest.py` `_unique_env_name`; `background.js` unreferenced. | Keep; add isolated worker contract test. |
| LOW | `test_aibridge_payload.py:91-96` | Live selftest may catch agent/task API regressions, but it does not execute `extension/background.js`, so removing the extension JSON fields at `background.js:50` survives. | Selftest starts `src/agent.ps1` and sends HTTP directly; no Chrome worker is loaded. | Add an extension-side payload assertion as above. |
| MED | `background.js:46-50` | The `cmd`/`cwd`/`timeout_s`/`auto`/`write`/`rid`/`dry`/`shell`/`task`/`task_params`/`task_spec`/`token` envelope is not asserted by any of the three scope-in tests. In particular, deletion or renaming of `task_params` or `task_spec` is a survivor in current tests. | Existing payload tests never load `background.js`; selftest drives agent HTTP directly. The task-mode contract is described in `AIBRIDGE_LANE.md:43-49`, and B184 records task mode at `B184...md:32-35`. | Add a failing-first test that stubs Chrome APIs and `fetch`, invokes the registered `airun` listener with an inline task, and asserts exact POST URL, content type, and JSON fields. |
| LOW | `background.js:6-14, 38-45, 53-62` | Machine selection, ping forwarding, response parse/error handling, and keep-alive behavior also have no direct test among the scope-in files. | `loop.test.js` tests pure loop helpers only. | Cover these separately if the intended test contract includes them. |

## Mutation matrix

Mutation candidates checked against the test predicates:

1. Remove the `LASTEXITCODE` propagation block in `run-task.ps1:44-47`: assertion `test_native_exit_1_then_write_output_is_a_fail` at test lines 45-49 detects the regression.
2. Remove the default `EXIT_CODE` fail pattern in `run-task.ps1:65-68`: assertion at test lines 51-54 detects it.
3. Remove quote blanking in `Get-CmdKind` at `checks.ps1:181-183`: at least the quoted `git commit|Remove-Item|a>b` assertion at cmd-kind test line 24 detects it.
4. Remove `task_params` and `task_spec` from the background POST body at `background.js:50`: **survives** all current scope-in tests; none execute or inspect `background.js` behavior.

These are source-to-assertion predictions, not a recorded execution of four mutations. The fourth survivor is evidenced by the test call graph described above. A temporary mutant test and the requested new test file were not created because the audit/no-code and audit-path constraints prevent delivering the required test artifact. No source/spec was modified.

## Follow-up cards

None created: no HIGH finding was identified. The two MED findings are coverage gaps, and task-card scope does not permit editing tests or task metadata.

Verdict: **BLOCKED** — the audit’s no-code/out-of-scope rules conflict with the mandatory new test artifact. The original DSA field report files are also unavailable here and are recorded as a source limitation, not as the blocking reason.
