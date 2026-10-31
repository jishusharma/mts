# CI red on fast-track: root causes (2026-10-30 21:31Z .. 2026-10-31 08:10Z)

Source: `gh run list --branch fast-track --limit 100` = 100 runs: 73 success, 26 failure, 1 in progress.
Every failure log (`gh run view <id> --log-failed`) was downloaded whole and parsed for `FAILED`/`FAIL:` ids and the
`N step(s) failed` line; nothing below comes from truncated output. Local evidence: `runtime_data/gate_timing.jsonl`
and `mts_gate_record.json` of the shipping worktrees on JIS-NB.

## The main finding

The fast ship gate (`sync.py ship` -> `run_all_tests.py --fast`) has a 60 s step-phase deadline. A step that had not
finished by then was **reported PASS** ("DEFERRED TO CI", `exec_step`). On a loaded JIS-NB the tree-wide checks
(3la look-ahead lint, 3xt extra tests) take 50-60 s in the pool, so they were cut and counted as passes:

| ship | step | local result | same tree alone / in CI |
|---|---|---|---|
| 32756080e phase tag | 3la | ok=True at 52.99 s (deadline) | `lookahead_lint.py --new` exit 1 (harness.py:43) |
| b208537a8 -> ca807e364 F1 | 3la, 3xt | ok=True at 55.87 s / 55.94 s | T06 cost inventory FAIL (run_f1.py:115 `cost`) |
| 339356732 -> b17f0354f sim C21-C26 | 3xt | ok=True at 58.39 s | sim_desk test_backfill 265 != 210 |

The T06 cost inventory test was also never selected for a new research file: nothing imports it.

## Classes

| class | red runs | episodes | reverts | fix shipped | preventable before ship |
|---|---|---|---|---|---|
| Fast gate cut/skip of a tree-wide check (look-ahead lint, cost inventory, sim catalogue) | 19 | 5 | 5 | 201d47c73 (3la + new 3xm must-pass, never deadline-deferred) | Y |
| ...of which: cost inventory keyed by line number (a docstring moved a constant) | (7) | (1) | (1) | 5273a6f23 (match by file+name count) | Y |
| Time-bomb test (hard-coded date vs real clock) | 4 | 1 | 0 | 39e9eb030 (before this audit) | N (passed the day it shipped) |
| Flaky / runner-dependent test | 3 (+2 co-occurring) | 3 | 0 | d6cc31796 | N (CI container only) |
| Follow-on: innocent pushes landing while trunk was already red | 17 of the 26 | - | - | none (CI latency; `ci_state` blocks only after 2 finished reds) | - |

## Every failed run

| run id | sha | UTC | class | root cause | fix | preventable Y/N | gate that should have caught it |
|---|---|---|---|---|---|---|---|
| 41140240177 | 6d6f59da0 | 10-30 22:45 | flaky | test_auto_deploy tree-kill: killed grandchild is a zombie ('Z'), CI PID 1 does not reap | d6cc31796 | N | - (test bug) |
| 41145728834 | 6ed9f4a5c | 10-30 23:39 | fast-gate cut | oi_after_flush.py fwd-index lint hits (laptop ship; timing not on JIS-NB, same pattern assumed) | 201d47c73; revert 038faf401 | Y | 3la in ship |
| 41146579765 | cda67b1f4 | 10-30 23:47 | follow-on | same lint hits, trunk still red | - | - | - |
| 41168619722 | 60bec47ca | 10-31 04:27 | flaky | test_lease: copytree hit origin.git/objects/maintenance.lock (receive-pack auto-maintenance) | d6cc31796 | N | - (test bug) |
| 41173379647 | b17f0354f | 10-31 05:38 | fast-gate cut | sim C21-C26 catalogue rows without result cards (test_backfill 265 != 210); 3xt cut at 58.39 s | 201d47c73 (3xm); revert 23cbee722 | Y | 3xt in ship |
| 41173421801 | 9ef3b1c30 | 10-31 05:38 | follow-on | same | - | - | - |
| 41173566235 | c7f33dc1f | 10-31 05:41 | follow-on | same | - | - | - |
| 41173706612 | ba89bf90a | 10-31 05:43 | follow-on | same | - | - | - |
| 41173719971 | c89ec72aa | 10-31 05:43 | follow-on | same | - | - | - |
| 41173774113 | 73a4a11f6 | 10-31 05:44 | follow-on + flaky | same + test_lease maintenance.lock | d6cc31796 | - | - |
| 41174710296 | a17396f11 | 10-31 05:59 | time-bomb | test_mts_doctor broadcast test: now=2026-10-25 vs real-clock KEEP_DAYS=7 | 39e9eb030 | N | - |
| 41175038690 | 70151eb46 | 10-31 06:03 | follow-on + flaky | same + test_auto_deploy zombie | d6cc31796 | - | - |
| 41175118406 | 761352216 | 10-31 06:04 | follow-on | same time-bomb | - | - | - |
| 41175159008 | 64b656889 | 10-31 06:05 | follow-on | same time-bomb | - | - | - |
| 41176985913 | ca6ee3658 | 10-31 06:31 | fast-gate skip + line drift | 52c922ae5: docstring line above fabio_of_model.py `slip` (line-keyed check) + new FUNDING_SNAP_MS; T06 test not selected | 5273a6f23 + 201d47c73; revert 3ec1f0e28 | Y | 3xm (T06) in ship |
| 41177011666 | 7862d56a7 | 10-31 06:32 | follow-on | same | - | - | - |
| 41177116552 | 70526275b | 10-31 06:33 | follow-on | same | - | - | - |
| 41177209439 | f1a0f4515 | 10-31 06:35 | follow-on | same | - | - | - |
| 41177446130 | 773e96a40 | 10-31 06:38 | follow-on | same | - | - | - |
| 41177500663 | 563ad5793 | 10-31 06:39 | follow-on | same | - | - | - |
| 41177523561 | 9cb6cc647 | 10-31 06:39 | follow-on | same | - | - | - |
| 41180065781 | 32756080e | 10-31 07:18 | fast-gate cut | phase tag harness.py:43 `lab[i:i + L] = cur` fwd-index; 3la cut at 52.99 s | 201d47c73; revert bcbe36875 | Y | 3la in ship |
| 41180193963 | cedb286c9 | 10-31 07:20 | follow-on | same | - | - | - |
| 41180505932 | e9ceecdfb | 10-31 07:24 | follow-on | same (P1 split on top) | - | - | - |
| 41181218651 | 9a77f2181 | 10-31 07:35 | flaky | test_trunk_lag: a 1 us timeout did not fire before `git status` finished | d6cc31796 | N | - (test bug) |
| 41182783830 | ca807e364 | 10-31 08:00 | fast-gate cut + skip | F1 run_f1.py:115 `cost` not in costs.csv; 3xt cut at 55.94 s, T06 not selected | 201d47c73; reverts d498954d1, 15bab9e81 | Y | 3xm (T06) in ship |

## What changed (no new gate, no new paperwork)

- `run_all_tests.NO_DEFER_CMDS`: in a fast ship, 3la and the new step 3xm run to completion (cap 240 s from their own
  start); a timeout fails the ship instead of passing. Everything else keeps the 60 s deadline.
- `gate_select.MUST_EXTRAS` / `must_extras`: step 3xm = changed 3xt test files + the T06 cost inventory (any non-test
  backtest/research .py) + sim_desk/test_backfill (any sim_desk path). About 7 s together.
- T06 `test_cost_inventory.py` matches by (file, name) count, so a constant that moves a line is not "new".
- Three flaky tests fixed at the cause (zombie = dead, maintenance off in the template origin, assert the timeout value).

## Left open (cards filed)

- A data-only ship (sim_desk results .json alone) is a docs-mode ship and runs 0 steps, so test_backfill does not run.
- Time-bomb tests: no cheap static check found; one episode in 100 runs, not worth a gate.
- 17 of 26 red runs were other sessions' pushes landing on an already red trunk inside the CI latency.
