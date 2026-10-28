# Background processes that ran too long: audit, 2026-10-28

Card `bug-long-background-processes-dead-ends`, Builder (Opus agent). Operator, 2026-10-28: sessions leave background processes running for 1h39m+, most are dead ends, ships slow down.

## Result
- **1,070** background tasks in 7 days of transcripts. **142 ran over 30 min**, 173 h of wall time in total (tasks overlap, so this is not hours of operator time).
- **43 of the 142 were dead ends, hung or idle (72 h)**: 13 Agents sat waiting on their own background work, 10 watchers timed out with nothing to report, 6 were killed by their owner, 5 hung until the session died, 9 failed (3 of them ssh exit 255).
- **72 were useful but late**: they ran more than twice their kind's cap. Only 27 were useful and on time.
- **Why none was stopped sooner:** a background task reports only when it ends. A hung task never ends, so nothing saw it: no deadline in the command, no wall-time cap on Agents, and no check that a task was still moving.

## Method
- Read every `~/.claude/projects/**/*.jsonl` changed in the last 7 days.
- A start is a Bash/PowerShell `run_in_background` call, a command moved to the background automatically after 2 min, or an Agent call.
- The end is the `<task-notification>` for that task id. It arrives either as a user message or as a `queued_command` attachment. A first pass missed the attachments and over-counted hung tasks. A `TaskStop` also counts as the end.
- No end at all: the last time the session polled the task's output.
- Outcome comes from the notification: `exit code 0` or `finished` = useful; `waiting on its own background work` = Agent idle-wait; a non-zero exit, a kill or a session-end stop = dead end or hung.
- `scripts/dev/bg_watch.py` holds the same parse, so it can be re-run.
- Not covered: Gemini jobs on the NUC (F:/MTS/gq logs, read over the gate with `timeout 90`), checked separately below. `F:/MTS/nuc_wake` does not exist. `F:/MTS/succ_wake/C` holds one successor run (out.log written 03:50), which was fine.

## By kind (the 142 tasks over 30 min)
| kind | n | hours | useful | useful, late (>2x cap) | dead / hung / idle | dead hours | why it was not stopped sooner |
|---|---|---|---|---|---|---|---|
| command (auto-backgrounded at 2 min, misc) | 40 | 45.8 | 0 | 30 | 10 | 22.1 | moved to the background at 2 min, then the owner went on working; no cap |
| poll-loop (`until grep ...; do sleep`) | 14 | 37.3 | 0 | 11 | 3 | 21.3 | no deadline in the loop: worst 1,080 min (`until ! tasklist ... python`), 430, 398 |
| worker (Agent) | 30 | 36.0 | 11 | 6 | 13 | 12.4 | turn cap counts tool turns, not time; 13 sat waiting on their own background work |
| ship (`sync.py ship`) | 29 | 28.8 | 9 | 17 | 3 | 2.0 | every lost push race re-merges and re-gates (up to 5x); then a 10-min CI wait |
| watcher (`supervisor.py wait --timeout 50m`) | 15 | 10.9 | 5 | 0 | 10 | 7.9 | 50 min by design; 10 of 15 timed out with no event (exit 3) |
| tests (`run_all_tests`) | 8 | 6.4 | 2 | 5 | 1 | 0.6 | quick suite 30-75 min on a loaded machine |
| nuc (ssh over nuc_gate) | 3 | 4.5 | 0 | 1 | 2 | 3.8 | `printf ... | ssh ... ps` with no timeout: `codex_run.py tick` runs a whole job inside the ssh session (141 min, 87 min) |
| probe | 3 | 3.0 | 0 | 2 | 1 | 1.3 | auto-backgrounded heredoc edits |

All tasks, not only the long ones (p50 / p90 / max minutes):
- worker: 255 tasks, 5 / 34 / 181
- ship: 198 tasks, 5 / 40 / 140
- poll-loop: 48 tasks, 16 / 75 / 1,080
- nuc: 18 tasks, 10 / 24 / 141
- tests: 40 tasks, 12 / 52 / 75

The worker cap of 45 min sits at about p93: 18 of 255 Agents ran past it.

Gemini queue (NUC, `gemini_queue.py status` read 2026-10-28):
- 5 cards ended `CLAIM FAILED ... after 6 tries` or `claim push still rejected after 3 tries` (01:46-03:28): up to 18 pushes each.
- The push stderr was thrown away, and every failure was printed as "someone shipped first", so the real cause (race, auth or network) cannot be read back from the logs.
- 10 `gb-*`/`gw-*` jobs exited 3 within 15-90 s (2026-10-25). Those failed fast, which is fine.

Top 11 by minutes (the full 142 rows are in TASKS.md):

| task | session | kind | start (local) | min | cap | outcome | command |
|---|---|---|---|---|---|---|---|
| ba1idmtid | agent-a1 | poll-loop | 10-25 04:28 | 1080 | 15 | hung: died with session | until ! tasklist //FO CSV //V ... grep -qi "python" |
| bcqhsaoza | c6fb0840 | command | 10-24 17:09 | 430 | 10 | killed by owner | until grep -qE "cherry/rror/abort/FAIL" $TMP |
| bpi1wqlsw | agent-a1 | poll-loop | 10-25 04:39 | 398 | 15 | useful, late | until grep -qE "^shipped/push failed/..." /tmp/ship2.log |
| btvdbycje | agent-a8 | command | 10-25 17:44 | 323 | 10 | dead end: exit 1 | fold-on-ship-2 transcript read |
| aca69a15e3 | 1451cd3a | worker | 10-23 17:33 | 181 | 45 | useful, late | Builder: confluence-s1 counts |
| a1c47a4e61 | 2fe1800a | worker | 10-25 20:34 | 174 | 45 | useful, late | Builder: machine rename aliases |
| b8s1j7axj | 47a012c7 | command | 10-18 11:54 | 155 | 10 | hung: died with session | scratch script |
| bilf7ym40 | c6273250 | poll-loop | 10-27 18:25 | 142 | 15 | hung: died with session | while true; codex_run.py next; sleep |
| br731lvs2 | e75d3eec | nuc | 10-27 18:26 | 141 | 5 | hung: died with session | printf 'Set-Location F:/MTS/mts-codex-lab; ... tick' / ssh |
| bojim9rtb | 47a012c7 | ship | 10-18 06:44 | 140 | 20 | useful, late | for i in 1..6; sync.py ship; cherry |
| bjkaapgye | 411bc931 (coordinator) | nuc | 10-28 03:25 | 87 | 5 | killed by owner | printf 'cd F:/MTS/mts-codex-lab; git status ...' / ssh (the operator's example) |

## Root causes, with the gaps they came from (pre-change code)
| # | cause | where | tasks it explains |
|---|---|---|---|
| R1 | No timeout on NUC ssh verbs | `scripts/dev/nuc_lab.py:67` `runner(gate_cmd()+["ps"], ...)` with no timeout. `nuc_wake.py:97` is the same. `ConnectTimeout=10` covers only the connect, not a silent session. | nuc 3 (141, 87 min), operator's 1h39m example |
| R2 | No timeout on network git, and git may wait on a credential prompt | `scripts/dev/sync.py:69-74` `git()` calls `subprocess.run` with no timeout and no `GIT_TERMINAL_PROMPT=0`; gemini_queue.py:36 had fixed this for itself only | hung fetch/push inside ship, claim, release |
| R3 | Any failed push was treated as a lost race and retried | `sync.py:1280` (claims: 3 tries) and `sync.py:1059` (ship: 5 tries, each a full re-merge and re-gate) print "someone shipped first" for an auth or network failure too, and throw away stderr. `gemini_queue.py:67` then wraps 6 tries around that: up to 18 pushes | 5 Gemini CLAIM FAILED (10-28), ship 3 dead / 17 late |
| R4 | Poll loops with no deadline | session habit: `until grep ...; do sleep 5; done` on a log file that never gets the line. No rule in WORKERS.md said every background command needs a deadline | poll-loop 14 (37 h) |
| R5 | No wall-time cap on Agents | `WORKERS.md:30-32` caps tool turns only (40), and "No hook enforces a turn cap". An Agent waiting on its own background work burns wall time, not turns | worker 13 idle-wait |
| R6 | Nothing reports a stalled task | `SUPER_SESSION.md:66` already says "Stuck worker (45 min) -> one SendMessage then stop_session", but no code detects one. `SUPER_SESSION.md:71`: the app continues the coordinator only when a task *finishes*. A hung one never does | all hung rows |
| R7 | watchcheck checks that a wake exists, not that work is moving | `supervisor.py:565` `watchcheck` passes on any live 50-min watcher. `supervisor.py:509` `_detect_transition` wakes on shas, CI and gate slots only, never on a stalled task. That is why card `super-session-coordinator-stalls-when-it` (shipped 5d9748041) did not close this gap | watcher 10 timeouts, idle coordinator (card `coordinator-sits-idle-during-long-backgr`) |
| R8 | No external watchdog by policy | `SCHEDULING_POLICY.md:12` "No coordinator running = nothing moves on its own". `runaway_check.ps1` looks at OS processes, not at session tasks or their caps | - |
| R9 | A raw card that was shipped but has no deliverable is invisible | `0fd607ca4` shipped `coordinator-sits-idle-during-long-backgr` as raw with an empty result. Nothing in `plan` lists raw IMPORTANT/CRUCIAL cards, so no Supervisor saw it | that card |

## Target: maximum wall time per kind of task (OURS)
| kind | cap | basis |
|---|---|---|
| probe (read-only command) | 2 min | operator target |
| NUC verb (`nuc_lab status`, `nuc_wake`) | 5 min | operator target |
| NUC job verb (`nuc_lab tick` / `gemini`) | 45 min | runs a whole job in the ssh session; worker cap |
| poll loop | 15 min | p50 16 min for useful ones |
| ship | 20 min | 10 min gate (CLAUDE.md) plus `CI_WAIT_S` 10 min; p90 is 40 today |
| tests | 20 min | |
| watcher | its `--timeout` + 5 min | |
| worker (Agent) / Gemini job | 45 min | operator target; p93 of 255 Agents |
| git fetch / push | 180 s | normal is 1-20 s |

## Fixes shipped (small code, no new gate)
1. `sync.py git()`:
   - Network verbs (fetch, push, pull, ls-remote, clone) now time out after 180 s and never prompt for credentials.
   - A timeout returns rc 124 and prints `TIMEOUT git <verb> after 180s`. (R2)
2. `sync.py` new `push_race_lost()` / `PushFailed`:
   - Only a real race (`[rejected]`, `fetch first`, `non-fast-forward`, ...) is retried.
   - Any other failure (auth, network, timeout, hook) fails once with git's own message: `push FAILED (not a race, no retry): ...`.
   - A ship no longer re-gates 5 times on an auth error. (R3)
3. `gemini_queue.claim_with_retry` stops at once on a TIMEOUT or a "not a race" failure. A real race still gets 6 tries. (R3)
4. `nuc_lab.py`: `status` times out at 5 min; `tick` and `gemini` at 45 min. Each prints `TIMEOUT nuc_lab <verb> after Ns` and exits 124. `nuc_wake.py` times out at 5 min. (R1)
5. New `scripts/dev/bg_watch.py`:
   - Reads the active sessions' transcripts.
   - Prints `STALLED-BG <kind> <id> <age> > cap <cap>, no output Nm (session ..): <cmd> -> owner: TaskStop <id>` for each open background task past its cap.
   - Prints `RAW-AGED` for IMPORTANT/CRUCIAL cards still raw after 12 h. (R6, R9)
6. `supervisor.py`:
   - `plan` prints those lines every wake.
   - `wait` (the watcher) wakes on a newly stalled task with `TRANSITION STALLED-BG ...`, so a hung task now ends the 50-min idle instead of running out the clock. (R6, R7)
7. Docs, one line each:
   - WORKERS.md rule 4: every background command has a deadline (R4, R5).
   - SUPER_SESSION.md Failure handling: STALLED-BG means TaskStop that wake; RAW-AGED means refine or drop one card.

Tests:
- New tests in `test_sync.py`, `test_gemini_queue.py`, `test_nuc_lab.py` and a new `test_bg_watch.py` (registered in `extra_tests.tsv`).
- All of them failed on the pre-change code: 4 sync, 2 nuc_lab, 1 gemini, plus bg_watch, which had no module before.

DECISIONS (OURS):
- Caps as listed above.
- bg_watch only reports and never kills: only the owning session can `TaskStop` its own task, and killing another session's work is not safe.
- Ship re-gating on a real race is left as it is.

## Left (not done here)
- Ship p90 is 40 min. The cause is re-gating after lost push races plus the CI wait, not hangs. Fixing it needs a ship-queue design, not a timeout: one candidate is to push before re-gating when the incoming commits do not touch the outgoing files.
- The 5 Gemini claim failures of 2026-10-28 cannot be diagnosed after the fact, because stderr was dropped. The next failure will print git's real message.
- `bg_watch` sees only this machine's transcripts. A NUC or laptop session is seen only by a Supervisor running on that machine.
