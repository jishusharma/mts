# CI / ship speed diagnosis, 2026-10-22 (MTS Doctor, PARTIAL hand-over)

Source: `gh run list --workflow CI --limit 150` (10-17..22) and step times of runs 39731255517 / 39731394387.

## Measured
- Median CI wall 12-13.5 min/day, max 43 min. Failures: 10-18 43/63, 10-19 8/35, 10-20 2/19, 10-21 12/29.
- cd861f0b: ubuntu gate 2m47s, windows gate 11m15s (4x). Setup+pip under 1 min both OSes: pip cache not worth it. Maven cache hits.
- 57b77eab: created 06:01:30, started 06:12:47 (11m17s queue behind cd861f0b), windows gate 13 min, mark-green 06:26:33. Total 25 min, 11 of it queue.

## Why serialized
ci.yml: `concurrency: ci-${{ github.ref }}`, `cancel-in-progress: false` on fast-track (deliberate, to stop starving mark-green). Docs-only pushes run no CI; the pointer reaches them via the next code SHA; `workflow_dispatch` on that SHA closes the gap.

## Ranked improvements (none shipped; mark-green controls the live pointer, coordinator waiting on 57b77eab: DECISION (OURS) no workflow change now)
1. Concurrency per SHA on fast-track + mark-green guard `git merge-base --is-ancestor <green> <sha>` else skip: saves up to 11-13 min when pushes overlap. Needs fail-first test.
2. Shard the Windows leg (steps 4/4b/4c/4g/4h as matrix shards) or gate the pointer on ubuntu + Windows smoke: 11 -> ~5 min. Blocking policy is the operator's call.
3. `sync.py wait-ci <sha>`: poll `gh run list --workflow CI --branch fast-track --json headSha,status,conclusion` from inside a checkout; compare pointer via full ref `refs/remotes/origin/green/fast-track` (bare name is ambiguous).
4. Defer more of the local ship gate to CI.

## Wiring checklist
- CLAUDE.md 7.2 KB: works. Role loader: works but GUESSED Admin_Guy because `ROLE: MTS Doctor` is not parsed (only "You are ..."): BROKEN, add `ROLE:` prefix.
- TURN METER hook blocked Read/Write/Bash in this side session before the audit finished: too tight for audit work (UNKNOWN how it counts).
- NEXT_SESSION.md 16 KB, LIVE_HOST_MOVE.md 16.5 KB, sync.py 70 KB: lazy-load candidates. Memory index, skills lists, other hooks: NOT audited.
- Hard-coded dev paths (scripts/sched, docs, MTS-Wrapper task): NOT audited; guard test covers launch scripts only.

## Open
sync.py stage timings, `pytest --durations=30` on Windows, context token audit, path sweep, implement item 1 with test.

## Built 2026-10-22 late (Admin_Guy, operator: "Can you finish this task end-to-end?")
Measured before (run 0cf9fdf4, 23:37 IST): Linux 3m14s, Windows 14m00s (gate 12m54s), plus up to ~15 min queued behind the
running fast-track run (fe6537de waited 10 min, then was superseded). Worst push-to-green ~30 min.
1. One CI run per fast-track commit: `concurrency.group` carries the SHA on fast-track; a push starts at once. mark-green runs one
   at a time, publishes only when the current green is an ancestor of the SHA, with `--force-with-lease` (never backwards).
2. Windows leg in 3 parallel shards: `run_all_tests.py --shard K/N`, greedy longest-first on `shard_est` (OURS estimates:
   SHARD_EST_S, SLOWEST_FIRST, STEP_EST); each step runs in exactly one shard; all shards must pass before mark-green.
3. Windows temp on D: (`runner.temp`) and real-time Defender off on the throwaway runner (sources: runner-images #7320/#8755,
   nextest Dev Drive notes, GitLab real-time-monitoring commit). Expected ~5-6 min push-to-green; retune SHARD_EST_S from the
   first sharded runs' per-step times. Tests: scripts/dev/test_ci_split.py (fails on the pre-change code).
Not built (operator's call): Windows leg only for live-path changes; test impact analysis (testmon) in CI.

## Other gaps found the same night (for the record)
- App worktrees (.claude/worktrees/<name>) were cut from a stale main checkout and skipped by session-start catch-up: fixed fe6537de.
- A main checkout with local edits stayed behind silently: now named at session start (trunk_lag.py).
- Cards: dispatch sorts prio before weight (tasks.py dispatch); Supervisor workers as in-session Agents die with the Supervisor;
  signal notes cut long folder names as secrets (NB shows `[cut]`). Control room, home and layer-map pages lag the repo.
