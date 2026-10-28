# MTS-2026-10-03-1300Z-CL-BLD-queue-dispatcher
surface: App | host: JIS-NB | account: none | model: claude-sonnet-5-5 | role: BLD | branch: fast-track | branch_alias: none
predecessor: MTS-2026-10-03-0600Z-CL-BLD-registry-and-cicd | lanes: none (no subagents, no workers)
started: 2026-10-03 10:00Z (approx) | ended: 2026-10-03 10:25Z | status: closed | commits: none (operator commits)
handoff: operator. Review the stray R4-T2 change set (see T5 item 1), then commit staged paths you wrote.

## Scope
Scheduler picks work: pick_task.py, tick.py Pick section, `mts go`, tests. App reached the repo filesystem and ran every child process; CLI fallback not needed.

## T0 contract (quoted from disk)
(a) tick.py:31-38 `CHECKS = [("snapshot_age", ..., "event"), ("canary", ..., "event"), ("sessions", ..., "digest"), ("bug_age", ..., "digest"), ("paste_size", ..., "digest"), ("new_aging", ..., "digest")]`; kinds at :28 "event" and "digest". Report written :114 `out.write_text(...)`.
(b) run_worker.py: `spawn(cmd, prompt, ttl)` :234; `build_prompt(prefix, mode, check, exit_code, evidence, utc)` :228; main flow :251-358.
(c) cicd_run.py `stage_intake(ctx)` :272 returns a list of check rows (ck(...)), never a task row; it needs a `ctx` object (read/git/p helpers) and emits PASS/WARN lines only. A next-QUEUED function would have to be added (filter pipeline rows by status, blocker, BUGS status, item doc, git history, return one row). pick_task.py does not call stage_intake: it is a dependency-free T0 script run from the scheduler tick, and stage_intake pulls the whole runner context for a 15-minute clock.
(d) BUILD_PIPELINE.md:25 `| # | ID | Slug | Status | Blocker | Next |`; status values :21 QUEUED / IN-FLIGHT / GATED / LANDED / BLOCKED / PARKED.
(e) BUGS.md:24 `| ID | Opened | Status | Severity | Title | Evidence | Receipt |`; valid status Build-Check.ps1:139 `$validStatus = @("OPEN","IN-FIX","BLOCKED","CLOSED","WONTFIX")`.
(f) items/INDEX.md:8 `# Format: <id> | <status> | <file> | <one-line state>`.
(g) mts.ps1:23 `# VERBS-BEGIN`, :47 `# VERBS-END`; verb "go" absent before this session.
(h) .gitignore: `MyTradingSys/runtime/queue/` absent before this session (grep "queue" empty).
(i) header shape: line 1 `# <session id>`; line 2 `surface: ... | host: ... | account: ... | model: ... | role: ... | branch: ... | branch_alias: ...`; line 3 `predecessor: ... | lanes: ...`; line 4 `started: ... | ended: ... | status: ... | commits: ...`; line 5 `handoff: ...` (registry-and-cicd record).
(j) MTS-Scheduler-Tick: StartWhenAvailable True, repetition interval PT15M.

## T1 pick_task.py
New, 229 lines, LF. Pickable rule as briefed. Reads pipeline and BUGS fresh each run; prior next_task.* renamed to next_task_<composed_utc>.*; IDLE writes an IDLE next_task.txt so a stale prompt cannot be launched. Test hook: env MTS_PICK_ROOT.

## T2 tick.py
`run_pick()` plus a `## Pick` section appended after the report write; timeout 60 s; failure writes `ERROR: <reason>`. Detectors untouched.

## T3 wiring
mts.ps1 verb `go` (`mts go`, `mts go <id>` uses `claude --name <id>`). Guide row added; check_guide.py PASS. .gitignore carries `MyTradingSys/runtime/queue/`.

## T4 tests
test_pick_task.py, 7 fixtures. Fail-before: 7 failed with pick_task.py absent. After: 7 passed.
Live run 1: `PICK R4-T2 wave=2 slug=r4t2-false-vs-null surface=App`; wrote next_task.txt, next_task.json, pick_log.jsonl. B075 skipped (a commit "b075:" exists). Live run 2 (tick.py --only snapshot_age): report ends `## Pick` / `PICK B070 wave=4 slug=b070-demote-utc-00 surface=App` (R4-T2 had meanwhile been marked LANDED, see T5).

## T5 MISSED
1. Stray session: my check of `mts go` launched a real claude session on the R4-T2 prompt, which ran headless until I killed it. It edited htf_context_live.py, test_htf_context_live.py and marked BUILD_PIPELINE row 2.2 LANDED. Not committed, not reverted, no session record from it; its 24 tests pass here. Operator reviews and decides. Lesson: never run `mts go` as a test; use a stub claude.
2. Test 7 brief says `_missed_` suffix, the machine-wake section says next_task_<prior_composed_utc>.txt; the latter is implemented.
3. Added rule: a blocker naming a row number (e.g. 1.2) skips the row until that row is LANDED.
4. `mts go <id>` uses `claude --name`; claude `--session-id` needs a UUID, not an MTS id.
5. The R4 HTF prompt is not on disk as a prompt, only its session record; the T0-T5 shape was taken from the record and BUILD_PIPELINE "How an item runs".
6. Rows with ID "-" are never picked. Rows stay QUEUED after a pick (no IN-FLIGHT write), so one row is re-picked each wake until it lands; each re-pick archives the prior pair.
7. mts.ps1, tick.py, guide, .gitignore keep their existing CRLF; new files are LF.
8. B075 residual and T037 (BUGS status BLOCKED) are not pickable under the rules.
