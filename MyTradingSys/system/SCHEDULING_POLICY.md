# SCHEDULING POLICY (operator 2026-10-17, canonical)

Operator, OPERATOR_DECISIONS.md `q-host-sched-tasks` / `q-sched-scope`: "no more schedulers in any device, no routines, we have super sessions now, they run for defined timelines"; "remove every scheduled task on every device now, accepting that deploys, revival and the relay stop."
Any doc that still describes a dispatcher, relay tick, AutoDeploy, Supervisor, MTS-CodexLab or MTS-DispatchGate as running is the old design (marked `RETIRED 2026-10-17`); this file wins.

## 1. Rule
No standing Windows scheduled tasks and no Claude routines (App scheduled tasks, cron triggers, `mts-dispatcher`, `mts-lane-watch`) on any device. Two devices, same or different logins, work from one repo and one queue.

## 2. Who does what instead
- A super-session coordinator (SUPER_SESSION.md) is the dispatcher. On every wake it keeps the Codex lab busy (`python scripts/dev/codex_run.py status`, then `python scripts/dev/tasks.py next`), checks CI, and starts workers with `start_session`.
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

## 4. Only allowed exception
A one-shot task created by `scripts/dev/nuc_wake.py` to wake a headless worker for one card. It must be unregistered after it fires. Nothing else.

## 4b. Second allowed exception (operator via the 2026-10-21 wt-maint-job card)
`MTS-WorktreeMaint-<device>`: daily headless worktree/branch cleanup, `scripts/dev/wt_maint.py`, same on every device (DEVICES.md s8b). DECISION (OURS): it reverses nothing else; no revival, deploy or relay is implied. Remove with `wt_maint.py uninstall`.

## 5. Current state (update this table whenever it changes)
| Device | State |
|---|---|
| JIS-NUC | none (0 MTS scheduled tasks, verified 2026-10-17 after the operator removed `MTS-NUC-Worker` and the nine `MTS-Wake-*`). `MTS-CodexLab`, `MTS-DailyHygiene`, `MTS-DispatchGate` were unregistered earlier the same day; XML backups: `F:/MTS/backups/sched_tasks_2026-10-17_NUC` (restore with `Register-ScheduledTask -Xml`, only on operator say-so) |
| JIS-NB | none (operator checked Task Scheduler himself and says every MTS task is removed, 2026-10-23, d-jisnb-no-sched-tasks). Any session that reports MTS-* tasks on JIS-NB must paste a `schtasks /query` result from this turn, never repeat an older note |

| JIS-NUC (2026-10-21) | `MTS-WorktreeMaint-JIS-NUC` registered by wt-maint-job (section 4b). Any other MTS-* task still must not exist. |

A Windows task registered by hand again must be reported in this table. Someone re-registered `MTS-CodexLab` on 2026-10-17 ~15:00 IST; it was unregistered again.

