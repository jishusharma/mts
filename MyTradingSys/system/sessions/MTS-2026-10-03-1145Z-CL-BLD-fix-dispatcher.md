# MTS-2026-10-03-1145Z-CL-BLD-fix-dispatcher
surface: App | host: JIS-NB | account: none | model: claude-sonnet-5-5 | role: BLD | branch: fast-track | branch_alias: none
predecessor: MTS-2026-10-03-1300Z-CL-BLD-queue-dispatcher | lanes: none (no subagents, no workers)
started: 2026-10-03 11:45Z (approx) | ended: 2026-10-03 12:10Z (approx) | status: closed | commits: one combined commit on fast-track
handoff: none. B086 and B087 closed; the next scheduler tick creates pick_state.json.

## Scope
Two dispatcher defects. App reached the repo filesystem and ran every child process; CLI fallback not needed.

## T0 contract (quoted from disk, HEAD c7802a9)
(a) pick_task.py:81 `def skip_reason(r, bugs, by_num)`; :83 `if r["status"] != "QUEUED": return "status " + r["status"]` is the QUEUED-only line; :163 `def archive_prior(now)`; main loop :202 `chosen = next((r for r in sorted(rows, ...) if skip_reason(r, bugs, by_num) is None), None)`.
(b) No. Nothing in pick_task.py reads pick_log.jsonl (log_line :187 only appends) or any state file. Rows stay QUEUED after a pick, so the same row wins each wake.
(c) tick.py:70 `def run_pick()` runs `scripts/sched/pick_task.py` (timeout 60); :128 `f.write("\n## Pick\n\n" + run_pick() + "\n")`.
(d) mts.ps1:273-281 verb go: reads queue/next_task.txt, IDLE check, `if ($Arg) { & claude --name $Arg $prompt } else { & claude $prompt }`. No dry path.
(e) BUGS.md:184 B086 OPEN HIGH; items/B086_dispatcher_second_writer.md candidates: dry-run default, separate flag, lock file, temp tree.
(f) BUGS.md:185 B087 OPEN MED; items/B087_pick_task_repick.md candidates: pick_state.json, computed SIZE header, slug-derived id.
(g) pick_log.jsonl before: R4-T2 10:09:21Z, B070 10:12:21Z, 10:14:09Z, 10:29:09Z, 10:44:09Z (B070 four times by 10:44; the brief said three).
(h) runtime/queue: next_task.txt/.json, four archived next_task_2026100310xxxxZ pairs, pick_log.jsonl, consumer.py. No pick_state.json.

## Choices and reasons
B086: guard in a new go.py, keyed on env CLAUDECODE plus a --dry flag. A lock file would go stale when the machine is switched off (operator note: not 24/7). Dry-run-by-default would break the operator's `mts go`. Temp-tree smoke tests do not stop a session from running the verb. CLAUDECODE is set in every Claude Code session and absent in the operator terminal, so the dispatcher is exercisable (prints prompt and name) and the operator still launches live. Logic moved out of mts.ps1 into go.py so it is testable; mts.ps1 go delegates.
B087a: pick_state.json in runtime/queue (gitignored), 6h cooldown (env MTS_PICK_COOLDOWN_H). A picked row still pickable is HELD: next_task.* untouched, no second row offered (one writer at a time). After the cooldown it is offered again, so a dead session never starves a row. A row that stops being pickable drops out of state at once. Corrupt or missing state means no history. No clock needed: the machine may be off for days, the cooldown is wall-clock.
B087b: header changed once to `computed`; test_4 now rejects any hand-kept KB figure and enforces a 100KB ceiling on the measured size. No claim exists to edit. cicd_run.py:894 reads the numeric header only when it matches, so it is silent now.
B087c: `mts go <slug>` requires lowercase kebab, at most 20 chars; name = MTS-<UTC>-CLI-BLD-<slug> per SURFACE_POLICY s4; the prompt's Session ID line is rewritten to match. No argument: name = session_id from next_task.json. New `-Dry` switch on mts.ps1.

## Tests
test_pick_task.py 8-13 (new): fail on HEAD pick_task.py (4 of 6 fail; 11 and 12 guard behaviour that held before). test_go.py 1-7 (new): go.py absent at HEAD, mts.ps1 lacks go.py. test_integrity.py test_4 amended: HEAD header `~46KB` fails it.

## T5 deviations
1. pick_task.py and the operator brief use surface code CL; SURFACE_POLICY s4 lists CLD APP CLI LAP DSA ASK. Left as is for pick_task (existing records use CL); go.py slug names use CLI. Flag for the supervisor.
2. B070 was picked four times, not three, before this fix.
3. Fake claude test wrapper on Windows is a .cmd, which keeps line 1 of a multi-line prompt; the tests assert line 1 only. Dry-run tests assert the whole prompt.
4. A first mts.ps1 patch duplicated the file; restored from HEAD and redone with Edit before anything ran.
5. Live `mts go` from the operator terminal was not run here (this session is CLAUDECODE, so it would be a dry run by design).
