# CLAUDE MANAGER SPEC
# Written 2026-10-01 by MTS-2026-10-01-0557Z-DSA-COO.
# One script. One front door. You type a task in plain words.
# It handles model choice, context, budget, spawns, and close.

## WHY
The 2026-10-01 wiring audit found the policy exists but nobody
applies it. Subagents alone were 92% of last week of usage.
Sessions stayed open 8+ hours. Long-context re-reads cost $52
on one cloud Opus session. The operator cannot see context grow,
so the manager must keep it from growing.

## DESIGN RULE
One script, not an always-on Opus session. A Claude session as
manager re-reads its whole context on every check, the pattern
that produced the $52 figure. The manager is a process. It
starts, does one routing decision, launches children, and exits.

## OPERATOR INTERFACE
The operator types plain words. Nothing else. No model choice,
no context sizing, no spawn decision. The manager does all of
that and reports back in one line: what ran, which model, cost.

## COMMANDS
- mts go "<task>"   Main entry. Pipeline below.
- mts status        Open sessions, today spend, budget tier,
                    queued tasks.
- mts resume        Releases tasks queued while over budget.
- mts stop <slug>   Kills a running child session.

## PIPELINE (mts go)
1. Intake.      Haiku call sorts the request (fix, audit,
                extraction, backtest, question, status), picks
                a short slug, decides if the task splits into
                parallel children. About 1 cent.
2. Dedup.       Search session register and inboxes for the
                slug. Resume the match if one exists. Free.
3. Budget gate. Read usage level. Apply SURFACE_POLICY sec 3
                thresholds (70/85/95). Free.
4. Route.       Fixed table maps task type to the cheapest
                workable tier. Free.
5. Brief.       Write session record plus brief of 20 lines
                or fewer per child: task, files with line
                ranges, gates, hard rules. No whole-doc reads.
                Free.
6. Launch.      Start claude with chosen model and effort,
                brief as first message, token ceiling per
                child. Children run in parallel only when the
                intake step split the task. The work itself.
7. Close.       On exit of each child: append SUPERVISOR_LOG,
                close session record, update STATUS.md, run
                free daily scripts if overdue. Free.

## SPAWN RULES (set by the manager, not the operator)
Default:     one child per task.
Split only when:  the task has two or more independent files
                  or modules, AND each piece fits in one brief.
Never split when: the pieces share state, or the task is a
                  safety diff, or the budget tier is 85% or
                  above.
Cap:             3 children per mts go call, hard.
Each child:      cheapest workable model, own brief, own cap.

## ROUTING TABLE
| Task type   | Tier                                | Effort |
|-------------|-------------------------------------|--------|
| question    | Haiku                               | low    |
| status      | Haiku                               | low    |
| extraction  | Qwen NUC or DSA queue               | medium |
| docs / spec | Sonnet                              | medium |
| build       | Qwen or Sonnet, then Sonnet review  | medium |
| safety diff | Opus                                | high   |
| backtest    | Qwen; Sonnet for report             | medium |

## CONTROL LEVERS (set once, before the script)
Subagents:   none by default inside any child. When needed:
             cheapest model, per-child cap. Set via
             .claude/settings.json.
Default:     Sonnet at medium. Opus only for safety diff.
Session:     one task per child. Child exits at task end.
             No child stays open. No supervisor session open
             all day.
Context:     brief lists files with line ranges. Child reads
             only its brief, nothing else at start.
Budget:      never refuse. At 95% or above, commit-and-continue
             after each step. 100% hit still writes and saves.
             mts resume releases the queue after reset.

## CONFIG THE MANAGER MUST KNOW
Devices:      from DEVICES.md (jis-nb, JIS-NUC, laptop, roles).
Subscription: Pro plan. Weekly reset Fri 09:00 UTC (14:30 IST).
              Cloud credits $41 of $100, expire 2026-11-05.
              Weekly Pro pool and cloud credits are separate.
Usage:        primary = local transcript totals.
              fallback = operator enters percent once a day.
Project:      MTS root, CBP root, branch conventions, critical
              files list, condition files, compiled_engine.md.

## OPEN QUESTIONS
1. Reading weekly usage percent from a script. Local Claude
   Code writes token totals into transcript files. Weekly
   limit percent and cloud spend cannot be read from disk as
   of 2026-10-01. Fallback: operator enters percent daily.
2. Per-session token ceiling. Whether claude CLI accepts a
   hard cap depends on version. Fallback: script stops the
   child when transcript totals hit the ceiling.
3. Subagent model env var name. Confirm before writing
   .claude/settings.json.

## BUILD PLAN
One Sonnet session, Cloud, medium effort, any time now.
Draw from the $41 cloud credit pool (expires 2026-11-05).
Do NOT draw from the weekly Pro pool (at 100% until Fri).
Reads only: this spec, scripts/mts.ps1, SURFACE_POLICY.md,
scripts/operator/, DEVICES.md. Scope: one PowerShell script,
one Python helper, tests required by the budget gate. No Opus.
Does not touch live trading code.
The cloud session prompt is at
Dumps/operator/context/CLAUDE_MANAGER_BUILD_PROMPT.md.

## ACCEPTANCE
- mts go routes and launches correct tier without the operator
  picking a model.
- mts status prints open sessions, today spend, tier, queue.
- mts resume clears the queue after a reset.
- Over 95%, launch refused and task queued.
- Session record written before launch, closed after.
- SUPERVISOR_LOG gets one line per child.
- No child ever reads a file not named in its brief.

## END
