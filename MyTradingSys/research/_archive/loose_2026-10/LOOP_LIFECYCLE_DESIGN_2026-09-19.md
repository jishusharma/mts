# LOOP LIFECYCLE DESIGN
# Date: 2026-09-19
# Session: MTS-2026-09-19-0823Z
# Status: PLAN ONLY. No code changed this session.
# Purpose: collapse three owners of loop state into one owner each.
# ---

## PROBLEM

Three actors each run their own "is the loop alive" check, on three
surfaces, with no shared owner. Every observed loop-control bug is the
same defect in a different place: owner mismatch.

| Actor | Check | Kill | Start |
|---|---|---|---|
| mode.ps1 | read apparatus.lock, PID alive | lock-PID descendants + orphan java | fresh wrapper |
| loop-supervisor.ps1 | read apparatus.lock L71-86, L96-101 | all wrappers L56-59 | restart wrapper |
| start-trading-day.ps1 | write lock at start | finally: wrapper only | (self) |

Observed bugs, same root:

| Bug | Surface |
|---|---|
| B003 | two kill paths |
| B014 | java orphan on wrapper kill |
| SR-3 | mode.ps1 vs supervisor, start path |
| SR-4 | non-atomic lock, check-then-set |

## TARGET SHAPE

One writer of the lock. One reader of the lock. One start surface. One stop
surface.

1. Only start-trading-day.ps1 creates and removes apparatus.lock, using
   atomic create. If the lock exists and the PID is alive, it exits with
   "loop already running".
2. Supervisor is a reader. Its only job is: if the lock PID is dead, start
   a fresh wrapper. It never kills anything. No duplicate detection.
3. Everything that wants to start the loop goes through the supervisor.
   mode.ps1 either retires or becomes a pointer.
4. stop-day.ps1 creates a stop flag. The loop reads it on its next
   iteration and exits cleanly, shutting its own java in finally. No kill.

## STAGES

Four stages. Each closes a specific bug. Each is testable. Each is
reversible.

| Stage | Change | File | Critical? | Closes |
|---|---|---|---|---|
| 1 DONE 2026-09-19 4eff3de | Supervisor becomes reader-only. Remove L56-59 kill-all and L114-117 duplicate detection. Keep restart-on-dead-lock. | scripts/core/loop-supervisor.ps1 | No | SR-3 (partly) |
| 2 DONE 2026-09-19 b3eec33 | Atomic lock create in start-trading-day.ps1. One anchor. Four-step proof. | scripts/core/start-trading-day.ps1 | Yes | SR-4 |
| 3 | stop-day.ps1 becomes stop-flag + wait, no kill. Four-step proof. | scripts/core/stop-day.ps1 | Yes | B003, B014 |
| 4 | mode.ps1 becomes pointer or retires. Four-step proof. | scripts/core/mode.ps1 | Yes | SR-3 (rest) |

## WHAT EACH STAGE NEEDS

- Stage 1: read target, verify anchors, edit, Build-Check, live observation of one restart cycle.
- Stage 2: hash before, explicit replace, hash after, diff. Then live restart and confirm only one wrapper present.
- Stage 3: hash before, explicit replace, hash after, diff. Then create flag, observe loop exit, confirm java exits with it.
- Stage 4: hash before, explicit replace, hash after, diff. Then confirm refuse-or-point behavior.

## RISK

During stages 1-3 the system runs with mixed ownership: supervisor reduced,
mode.ps1 and stop-day.ps1 still kill. If both a supervisor and a mode.ps1
restart overlap, the current behavior (supervisor duplicate detection)
recovers. Removing duplicate detection at stage 1 removes the safety net
before mode.ps1 and stop-day.ps1 stop killing. Do not run mode.ps1 during
stages 1-3. Note this in the stage-1 handoff.

## WHAT IS NOT IN SCOPE

- Lock file format (PID TS). Current format is fine.
- Supervisor restart interval and grace clock. Current values are fine.
- Any change to the loop body (cycle cadence, candle alignment).
- Any change to session_state, session_log, or verdict path.

## DECISION

Adopted 2026-09-19 by operator. Stages execute one session each, in order.
Stage 1 is next session first action if no higher-priority defect is open.

## PROGRESS

Stage 1 DONE 2026-09-19 (commit 4eff3de). Supervisor is reader-only.
Stage 2 DONE 2026-09-19 (commit b3eec33). Atomic lock create.
Stages 2, 3, 4 pending. Do not run mode.ps1 until stage 3.

# END
