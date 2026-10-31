# DSA bridge fix plan (AIBridge 0.7.3), 2026-10-31

Operator goal: fix the DSA (DeepSeek + AIBridge) bugs, check the logs, tell DSA how to use the current bridge, test end to end.
Planner: Builder (JIS-NUC). Plan only, no product code. Read by code, not by BUGS.md: repo `scripts/aibridge` @6ca00caa1 and the
install F:/AIBridge are byte-equal for content.js, loop.js, run-task.ps1, agent.ps1, checks.ps1 (background.js differs by the
machine token, as aibridge_verify.py expects). Both copies are 0.7.3 (loop.js:4).

## 1. Defects

| # | Queue row | Root cause (file:line) | 0.7.3 fixes it? |
|---|---|---|---|
| D1 | 082119 thinking blocks run | `allBlocks()` takes every `pre, code, [class*=code]` on the page whose first line is `# AIRUN` (content.js:142-153). Nothing excludes DeepSeek's thinking panel, so a fence DSA drafts while thinking is a runnable block. | NO |
| D2 | 130944 blocks 1-2 replayed in a 6-block reply | Same cause plus the key: `blockKey` = fnv(cmd)@occurrence among ALL page blocks (content.js:155-163). A thinking draft of blocks 1-2 is occurrence 0, the final copy occurrence 1: two different keys, so both run. `runBatch` takes every unrun block when text is quiet for 2 s (content.js:9, 443, 495); a pause between thinking and answer starts the batch mid-reply. Matches the report exactly: seen=5 = 2 drafts + final 1-3, results #1=#3 and #2=#4 with the same sha. No same-command guard inside a batch (content.js:448-449). loop.test.js:88-93 ("batch of 6") tests `formatResult` only; block selection is untested (it lives in content.js, which node cannot load). | NO |
| D3 | 082116 task PASS over EXIT_CODE=1 | run-task.ps1:70 writes the step command as-is into a .ps1; :74-76 takes `powershell -File` exit code; :83 `ok = code -eq 0`. A step like `python run_all_tests.py --quick; Write-Output "EXIT_CODE=$LASTEXITCODE"` ends on a successful statement, so the script exits 0. Logs: F:/AIBridge/run/tasks/6e92a4b3.log:1 `exit=0 ok=True` and :349 `EXIT_CODE=1`; same in a077ed6f:1/39, e012739d:1/44, b833e768:1-2; audit.jsonl rids eycbw6-...-16/-23/-35/-43/-54 all task exit=0. The B209 fix (run-task.ps1:89-92) only matches a `FAILED: N step(s)` line. | PARTIAL (B209 case only) |
| D3b | (same logs) gate dies with no summary | In all five 10-31 gate logs the gate output stops mid-run (6/72, 10/72, 66/72 done) with neither `ALL TESTS PASSED` nor `FAILED: N step(s)` (run_all_tests.py:1418/1425), then exit 1. Python stdout into a file is block-buffered, so the last lines are lost; the killer is NOT known from the logs. The task log never records the step command (run-task.ps1:95) and the audit stores only `task=inline {}` (agent.ps1:350), so the plan DSA sent cannot be recovered. | NO |
| D4 | 095323 stuck at "waiting for DSA" | After posting, `runBatch` waits up to 30 s for a mutation, then `waitQuiet` up to 180 s (content.js:476-481); quiet = whole page text unchanged 2 s (content.js:114). Then it only rescans (:483-485); nothing tells DSA its reply was lost. If any page text keeps changing (spinner/timer text) or a half-drawn block sits in `pending`, `pump` loops on `sleep(500); continue` with no deadline (content.js:495) and the status stays "waiting for DSA after #N" for ever. B210's `raceDeadline` (loop.js:177-210) covers only a lost agent reply during a run, not the wait for DSA. | PARTIAL (run phase only) |
| D5 | 082122 gate tests fail under the bridge | Bridge children get TEMP = `<root>\run\tmp` = F:\AIBridge\src\run\tmp (agent.ps1:132-134), which is inside the git repo F:\AIBridge\.git. test_wiring_scan.py:205 asserts `tempfile.gettempdir()` is not a repo; under the bridge it is. test_mts_signal: `ensure()` sets user.name/email only on a fresh init (mts_signal.py:223-226) and commits at :236; the empty stderr points at stdout-only output (hook or identity); reproduce with stdout captured. Not a 0.7.3 regression. | NO |
| D6 | 082125 async-queue prompt rules | DSA_SESSION_PROMPT.md 0.1/0.1a (lines 11-38) never say the bridge is a queue, never forbid fences in thinking, never say how exit codes reach a task step. Audit 2026-10-31T09:58:40 shows DSA testing `This-Is-A-Fake-Command` and expecting a stop: PowerShell continues after a non-terminating error (exit 0 is correct). | NO |
| D7 | 125045 cap 50 -> 200 | content.js:11 `aibridge_cap: 50` in the repo and in F:/AIBridge/extension/content.js:11. | NO |

DECISION (OURS): one bridge release 0.7.4 carries D1+D2+D4+D7 (extension) and D3/D3b (runner); version guard
test_aibridge_version_bump.py forces the bump, so the extension cards run in order (C1 then C2), C3 in parallel and takes the
next number if it ships second. No mainnet, no live-tree file is touched; F:/AIBridge changes only through aibridge_install.py.

## 2. What DSA must be told (DSA_SESSION_PROMPT.md, card C5; replaces nothing else)

0.1 add, after "A block without the AIRUN line is ignored.":
> Write AIRUN fences only in your final answer, never while thinking. From 0.7.4 the bridge ignores fences inside the
> thinking panel; before that they ran, and a draft plus the final copy ran twice. Two identical blocks in one reply: the
> second gets "NOT RUN: duplicate of block K"; if you mean to repeat a command, change it (add a `# again` line).
> The bridge is a queue. After you send blocks, your next input is their [AIRUN RESULT] (or BATCH) message. Never send a
> status-check block while a task runs; never put two gate or ship tasks in one reply; wait for the result header.
> Per chain the bridge runs 200 blocks, then hands-free turns off and says so.

0.1a add:
> A step passes on its own exit code. End every step `cmd` on the program call, or with `; exit $LASTEXITCODE`. Never add
> `Write-Output "EXIT_CODE=$LASTEXITCODE"` as the last line: it turns a failure into exit 0 (from 0.7.4 a line
> `EXIT_CODE=<non-zero>` also fails the step). For the gate use `task=mts-gate`, not an inline copy. A gate result counts only
> with its summary line `ALL TESTS PASSED` or `FAILED: N step(s)`; no summary = FAIL, report the log path, do not re-run blind.

0.5 add: "PowerShell keeps going after a non-terminating error (an unknown command, a missing file): exit 0 is normal. Put
`$ErrorActionPreference='Stop'` as line 2 when later lines depend on earlier ones."
0.7 add: "`[AIRUN NOTICE] your last reply ended without a final answer` = your generation dropped. Re-send the blocks of
that answer once. A second notice in a row turns hands-free off; say so in one line."
Header line 1: "AIBridge v0.7.4". Guard: MyTradingSys/tests/test_dsa_direct_mode.py gets asserts for each new sentence.

## 3. Cards (tasks.py ids; S0 freeze: bug fixes with tests)

State at filing: all 8 cards filled (goal, steps, tests, done_when, scope) but `raw`: `tasks.py fill` requires a Lab_Guy
review stamp before `ready`, and c8 (lane OPUS) also needs `approved_by`. DECISION (OURS): the planner does not stamp its own
cards; the next Lab_Guy pass promotes them.

| id | model | files | failing-first test | done when |
|---|---|---|---|---|
| dsabr-c1-block-select | SONNET, session M ~30 | extension/loop.js (new pure `selectBlocks(descs)`, `batchKeys`), content.js:142-163, 441-451, :11, manifest.json, RELEASES.json | tests/block_select.test.js: fixture of 2 thinking drafts + 6 final blocks -> 6 selected, each once; 2 identical final blocks -> second NOT_RUN duplicate; key stable when the thinking panel collapses. Fails on 0.7.3 (8 selected). | node tests pass; selector for DeepSeek's thinking container taken from a saved DOM snapshot (class names only, stored as tests/fixtures/deepseek_reply.html); cap 200; version 0.7.4 |
| dsabr-c2-dropped-gen | SONNET, session M ~25, after c1 | loop.js new pure `replyWatch(state, event, now)`; content.js:476-485, 495 | handsfree.test.js: timeline "result posted -> reply grows -> stops with no final text for 45 s" yields `notice` once, a second time `stop`; pump quiet loop past aibridge_wait_ms yields a visible status, not a silent loop. Fails on 0.7.3 (no such state). | notice posted under 60 s (45 s OURS), stop banner on the second miss; node tests pass; version bump |
| dsabr-c3-task-exit | SONNET, agent S ~15 | scripts/run-task.ps1:70, 90, 95; tasks/mts-gate.json, mts-ship.json | test_aibridge_task_gate_exit.py: step `python -c "import sys; sys.exit(1)"; Write-Output 'EXIT_CODE=1'` (no cmd.exe: nested shells are refused) -> TASK RESULT: FAIL, rc 1; `python -c "import sys; sys.exit(3)"` then `Write-Output ok` -> FAIL; gate step without a summary line -> FAIL via `expect`. All three PASS on 0.7.3 today. | step script ends with `exit $LASTEXITCODE` when a native command ran; default fail_on adds `(?m)^EXIT_CODE=[1-9]`; gate playbooks `expect: ALL TESTS PASSED`; PYTHONUNBUFFERED=1 for steps; task log records cmd + cwd per step |
| dsabr-c4-gate-tmp | SONNET, agent S ~12 | scripts/dev/test_wiring_scan.py:205, test_mts_signal.py, mts_signal.py:218-236 | both tests run with TEMP set to a folder inside a scratch git repo and with GIT_CONFIG_GLOBAL=NUL: fail today | tests use their own mkdtemp + GIT_CEILING_DIRECTORIES, commits pass `-c user.name -c user.email`, commit output captured on failure; both pass inside run_all_tests --quick launched through the bridge |
| dsabr-c5-dsa-prompt | SONNET, agent S ~10, after c1-c3 ship | DSA_SESSION_PROMPT.md 0.1/0.1a/0.5/0.7, MyTradingSys/tests/test_dsa_direct_mode.py | guard asserts the section 2 sentences: fail before the edit | prompt carries section 2 text; size caps in test_integrity pass |
| dsabr-c6-e2e-script | SONNET, agent S ~15, after c1-c3 | scripts/aibridge/tests/e2e_bridge.py (new), scripts/aibridge/tests/fixtures/ | the script itself run against 0.7.3 must report FAIL on E1-E4 | design section 4 implemented; exit 0 only when all rows PASS |
| dsabr-c7-install-e2e | HAIKU, agent S ~10, after c5+c6 | none (runs) | n/a | aibridge_install.py F:/AIBridge, aibridge_verify.py all PASS, e2e_bridge.py PASS on JIS-NUC; jis-nb via `mts_signal.py broadcast --cmd`; extension reload + F5 noted in the report |
| dsabr-c8-opus-audit | OPUS, session M ~20, after c7 | read-only | n/a | section 5 checklist answered with file:line evidence, verdict PASS/FIX per card |

## 4. E2E test script design: scripts/aibridge/tests/e2e_bridge.py

`python scripts/aibridge/tests/e2e_bridge.py [F:/AIBridge] [--json]` - read-only for the repo; writes only under
`<root>/run/e2e/<utc>/`. Exit 0 = every row PASS. Rows print `E<n> PASS|FAIL|NOT_CHECKED <evidence>`.
- E0 install: reuse aibridge_verify.py (file:/fix:/agent_ping/roundtrip rows); version = RELEASES.json current.
- E1 six-block reply (tier B, node): load the INSTALLED extension/loop.js; feed tests/fixtures/six_blocks.json (6 final blocks,
  nonces N1..N6) to `selectBlocks` -> exactly 6, order 1..6, no key twice. Then tier A: POST the 6 commands to the agent in
  order (`Write-Output E1-<nonce>`); count each nonce in audit.jsonl since the run start = 1 each.
- E2 thinking fixture (tier B): tests/fixtures/deepseek_reply.html descriptor list (2 drafts in the thinking container + the
  same 2 in the answer) -> 2 selected, both from the answer. A same-command pair in the answer -> second is NOT_RUN duplicate.
- E3 exit-1 command (tier A, task=inline through the agent like the extension: token from config.json, never printed):
  plans (a) `python -c "import sys; sys.exit(1)"; Write-Output 'EXIT_CODE=1'` (no cmd.exe: nested shells are refused), (b) `python -c "import sys; print('x'); sys.exit(1)"`,
  (c) a step printing step lines and no gate summary with `expect: ALL TESTS PASSED` -> each body has exit != 0 and
  `TASK RESULT: FAIL`; control plan `Write-Output ok` -> PASS. Plain block `This-Is-A-Fake-Command` -> exit 0 (documented).
- E4 dropped generation (tier B): timeline fixture (post at t0, reply grows to t0+5 s, no final text, quiet to t0+50 s) through
  `replyWatch` -> `notice` at <= 60 s; repeat -> `stop`. Pump-deadline fixture -> status text, not silence.
- E5 live (optional, NOT_CHECKED unless `--live`): a Haiku with Chrome access opens a NEW DeepSeek chat, asks for 6
  `Write-Output E5-<nonce>` blocks and thinking on; after the batch, audit.jsonl holds each nonce once and the posted
  BATCH says blocks_seen=6 blocks_run=6. No other chat is touched.
Hosts: JIS-NUC runs it directly; jis-nb gets `mts_signal.py broadcast --cmd "python scripts/aibridge/tests/e2e_bridge.py
F:/AIBridge --json"` after its own aibridge_install.py; both JSON outputs are quoted in the c7 report.

## 5. Opus audit checklist (card c8)

1. Each fix has a test that failed on 0.7.3: check out 6ca00caa1 bridge files into a scratch dir, run the new tests, see FAIL.
2. `selectBlocks` excludes thinking by structure, not by text; the selector is in the DOM fixture; an unknown layout fails closed (no block runs, status says why) rather than running thinking drafts.
3. Duplicate guard is per batch only; a block re-sent in the NEXT reply still runs (no silent drop across replies).
4. `ranKeys` marking still happens before any run (content.js mark-first invariant); Stop (`token++`) still aborts a batch.
5. `replyWatch` posts at most one notice per chain, never while a run is in flight, never into an operator draft (B196 postGate).
6. run-task: a step that succeeds still PASSes (control case); `exit $LASTEXITCODE` only appended when a native command ran (no false FAIL from a stale code); the task-level `exit $LASTEXITCODE` (agent.ps1:349) unchanged.
7. Gate playbooks: a real `--quick` run through the bridge PASSes with `ALL TESTS PASSED` and FAILs on one injected failing test.
8. test_wiring_scan / test_mts_signal pass under TEMP inside a repo and with no global git identity; no test writes to the user's real %TEMP% root.
9. Version: RELEASES.json current == loop.js VERSION == manifest version; test_aibridge_version_bump passes; install hashes match aibridge_verify.
10. Prompt: every section 2 sentence present; no rule contradicts V07_CONTRACT.md; size caps hold.
11. E2E JSON from JIS-NUC and jis-nb both all PASS (E5 may be NOT_CHECKED with a reason).
12. No live-tree file, HALT file, policy.json or secret touched; agent never restarted by a builder (install script only).
