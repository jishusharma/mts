# Sonnet review: context and compaction policy (2026-10-21, read-only)

Measured from ~/.claude/projects: Fable 7 sessions, 3 compacted (6 compactions, 4 manual, median 281k, range 238-326k, peak p50/p90 201k/273k).
Opus 133 sessions, 21 compacted (16%), 46 compactions (3 auto, 43 manual), median 200k (101-298k), peak p50/p90/p99 122k/236k/364k.
Of 55 Opus sessions that reached 150k, 35 never compacted. Only 1 Opus session ever hit 500k.

## A. Code vs rules (scripts/dev/turn_meter.py)
Right: Opus second-message block >=150k, Opus nag >=500k, Fable hard block at 1 message, subagent hooks skipped.
Gaps: (1) a resumed or already-large Opus session over 150k gets no block until the next operator message and only a nag at 500k;
(2) the 150k check reads the previous assistant message, one turn late; (3) block cannot tell operator from event turn;
(4) hooks come from $CLAUDE_PROJECT_DIR, a stale checkout runs old code, no version shown; (5) Fable job size is unlimited (4 of 7 peaked at 201-273k);
(6) WORKERS.md rule 5 says nobody runs /compact, yet 43 of 46 Opus compactions were manual.

## C. What is configurable (from docs, not tested live)
Per model: modelSettings.<model>.autoCompactWindow (v2.1.288+, 100k-1M). Per launch: --autocompact <n> or env CLAUDE_CODE_AUTO_COMPACT_WINDOW (env wins).
Global only: autoCompactEnabled=false, DISABLE_AUTO_COMPACT=1, DISABLE_COMPACT=1 (also blocks manual).
PreCompact hook can block (exit 2 or {"decision":"block"}); input has trigger auto|manual. Settings env block applies to every session.
Not tested: blocking an auto compaction near the window limit.

## D. Unattended Supervisor
Event turns cannot call start_session. Write handover/SUPERVISOR_<L>.md and NEXT_SESSION.md with the successor line already built at 350k context;
next operator turn or a peer Supervisor starts the successor with one call.

## E. Leaks
Resumed Opus over 150k; 70-80k fixed cost per turn; manual /compact on sessions meant to stay detailed.

## Changes, priority order
1. roles/supervisor.md Transit: write hand-over files + successor line at 350k, hand over at 400k; not only "put the line in your reply".
2. turn_meter.py: Supervisor PostToolUse nag at 350k; Opus nag at 300k (replace 500k); block next operator message of a resumed Opus session already over 150k.
3. .claude/settings.json: PreCompact hook blocking manual /compact on Opus and Fable (Supervisors allowed); optional modelSettings autoCompactWindow for Opus/Fable; test the blocked-auto case first.
4. WORKERS.md rule 5 and SUPER_SESSION.md: replace "nobody runs /compact" with the measured facts.
5. turn_meter.py: record its git sha in the state file and `status`, so a stale hook checkout is visible.
