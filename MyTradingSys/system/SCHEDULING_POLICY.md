# SCHEDULING POLICY (operator 2026-10-17, canonical)

Operator, OPERATOR_DECISIONS.md `q-host-sched-tasks` / `q-sched-scope`: "no more schedulers in any device, no routines, we have super sessions now, they run for defined timelines"; "remove every scheduled task on every device now, accepting that deploys, revival and the relay stop."
Any doc that still describes a dispatcher, relay tick, AutoDeploy, Supervisor, MTS-CodexLab or MTS-DispatchGate as running is the old design (marked `RETIRED 2026-10-17`); this file wins.

## 1. Rule
No standing Windows scheduled tasks and no Claude routines (App scheduled tasks, cron triggers, `mts-dispatcher`, `mts-lane-watch`) on any device, except the exceptions listed in sections 4, 4b, 4b2, 4b3, 4c and the CBP block under 5 (name, trigger and removal in each). Two devices, same or different logins, work from one repo and one queue.

## 2. Who does what instead
- A super-session coordinator (SUPER_SESSION.md) is the dispatcher. On every wake it keeps the Codex lab busy (`python scripts/dev/codex_run.py status`, then `python scripts/dev/tasks.py next`), checks CI, and starts workers as background Agents (roles/supervisor.md:35).
- "Schedule this for the next 5h / 10h" is planned by a session on demand: the coordinator writes the card order up front in a plan file (like `PLAN_2026-10-17_NEXT_5H.md`) and works it for that window. When the window ends, nothing keeps running.
- No coordinator running = nothing moves on its own. That is accepted.

## 3. What stopped, and the cover
| Stopped | Cover |
|---|---|
| MTS-AutoDeploy (green-SHA deploy to the JIS-NB live tree) | manual deploy per DEPLOY_RUNBOOK.md, or a coordinator-run deploy step |
| MTS-Supervisor (process revival) | coordinator checks the live processes on wake |
| Relay dispatcher (`mts-dispatcher`, MTS-DispatchGate) | the coordinator starts the next session; `relay.py handoff` no longer auto-starts anything |
| MTS-CodexLab (`codex_run.py tick` every 30 min) | coordinator runs `codex_run.py tick` / `status` on wake (LAYER_LAB.md) |
| MTS-DailyHygiene, MTS-Backup, MTS-LiveMirror and the other MTS-* checks | run the script by hand when needed (`daily_hygiene.py`, `live_mirror.py`) |

## 4. First allowed exception (the full list is the section 1 sentence; each later exception has its own section)
A one-shot task created by `scripts/dev/nuc_wake.py` to wake a headless worker for one card. It must be unregistered after it fires. Anything not in sections 4-4c or the CBP block is forbidden.

## 4b. Second allowed exception (operator via the 2026-10-21 wt-maint-job card)
`MTS-WorktreeMaint-<device>`: daily headless worktree/branch cleanup, `scripts/dev/wt_maint.py`, same on every device (DEVICES.md s8b). DECISION (OURS): it reverses nothing else; no revival, deploy or relay is implied. Remove with `wt_maint.py uninstall`.

## 4b2. Third allowed exception: one-time App task for a successor session (chain test passed 2026-10-26)
A one-time task (`create_scheduled_task` with `fireAt`, never `cron`) may start ONE successor session so a hand-over does not wait for an operator click. Proof: `chain_test_proof.txt` (commit ce8194ba2): task `chain-test-2` fired at 09:06:43Z, all tools and SessionStart/UserPromptSubmit hooks present, the run shipped to fast-track, and the task was deleted after its run. Rules (OURS): one `fireAt`, no repeat, the task prompt names the model (the test ran on Opus; cost rules say Sonnet), the successor never creates another task, and the creating session records the task id in its hand-over.

## 4b3. Fourth allowed exception: one-shot Windows task that wakes a sleeping headless session (local, no SSH; proven 2026-10-28)
`scripts/dev/successor_wake.py` registers ONE one-shot `Register-ScheduledTask` (Interactive principal = the logged-in Windows user, no password) under the name `MTS-SuccWake-<login>` that boots a headless `claude -p` successor via `conhost --headless`, then self-unregisters in the same run script's `finally` — the 4b2 "must be unregistered after it fires" rule. It is §4b2 implemented **locally** (the machine that needs waking; no cross-host gate), and carries a **usage handoff**: a `USAGE` JSON (the pacer's last get_usage reading, five/week %, resets, mode, slots) is written next to the task's `prompt.txt` and named in the boot prompt, so a woken session can read its own budget off disk (a gateway profile has no get_usage). One trigger or start-now only, no repeat. Proof: `MyTradingSys/research/lead/wake_proof_2026-10-28T06-25Z.md` (task `MTS-SuccWake-B` fired, headless session did its work, task gone; the woken session's proof file and the `USAGE` handoff both on disk). The `supervisor.py handover` default wires this automatically (4b2 auto-wiring); `--no-wake` stays the manual opt-out.

## 4c. Logon guard (operator 2026-10-24: cleanup on every restart, no scheduler)
A per-user Run value `MTSTempGuard` (HKCU\Software\Microsoft\Windows\CurrentVersion\Run) runs `scripts/dev/c_drive_guard.py logon` once at each logon, headless (`conhost --headless`). It prunes the %TEMP% set in STATION_CLEANUP.md section 3 and exits. It has no timer, no repeat and no admin rights, so it is not a scheduled task. Register with `c_drive_guard.py install` from the primary checkout; remove with `uninstall`. Operator yes 2026-10-24 (OURS); registered per station as each acks (STATION_CLEANUP.md section 4).

## 5. Current state (update this table whenever it changes)

### CBP-only exception (operator request 2026-10-26)
The operator explicitly requested automatic CBP inputs twice daily. `scripts/dev/cbp_schedule.py`
owns ONE task `MTS-CBP-Ingestion`: 09:00 and 13:00 UTC (14:30 and 18:30 IST, OURS), daily including
weekends because crypto analysts publish every day. It runs only fetch -> extract -> quote check ->
CBP store; no session dispatcher, trading process, deploy or revival is authorized by this exception.
Install only on the host holding the configured CBP home, from a durable non-live MTS checkout.
It requires an existing signed-in Windows session, Claude login and yt-dlp. Failed prerequisites refuse
installation. Retry: three times at 15-minute intervals; missed starts run when available in today's
remaining window. The task ignores overlapping scheduled invocations. Until installation and a real
successful run are recorded, this is prepared wiring, not an operating feed.
2026-10-27 NUC verification: NOT INSTALLED; `F:/CryptoScrapper/cbp_v2/analysts.json` absent. Claude
has been asked to identify the current host/path via the desk board.
| Device | State |
|---|---|
| JIS-NUC | none (0 MTS scheduled tasks, verified 2026-10-17 after the operator removed `MTS-NUC-Worker` and the nine `MTS-Wake-*`). `MTS-CodexLab`, `MTS-DailyHygiene`, `MTS-DispatchGate` were unregistered earlier the same day; XML backups: `F:/MTS/backups/sched_tasks_2026-10-17_NUC` (restore with `Register-ScheduledTask -Xml`, only on operator say-so) |
| JIS-NB | none (operator checked Task Scheduler himself and says every MTS task is removed, 2026-10-23, d-jisnb-no-sched-tasks). Any session that reports MTS-* tasks on JIS-NB must paste a `schtasks /query` result from this turn, never repeat an older note |

| JIS-NUC (2026-10-21) | `MTS-WorktreeMaint-JIS-NUC` registered by wt-maint-job (section 4b). Any other MTS-* task still must not exist. |

A Windows task registered by hand again must be reported in this table. Someone re-registered `MTS-CodexLab` on 2026-10-17 ~15:00 IST; it was unregistered again.

