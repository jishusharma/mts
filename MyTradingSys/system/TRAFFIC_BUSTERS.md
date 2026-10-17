# TRAFFIC_BUSTERS - cut dev time by removing steps nobody needs (operator ask 2026-10-16)

Job of this lane: find steps that cost time, tokens or pushes and add nothing, then remove them with a measured number.
Measure first: `python scripts/dev/traffic_report.py [hours]` (commit mix on origin/fast-track).

## Baseline 2026-10-16 (before B1)
24 h: 878 commits = merge 40%, claim 14%, release 14%, other 32% -> 68% overhead. 7 d: 59% overhead.
Cause: every claim and every release ran a full `ship()` (fetch, merge commit when origin moved, docs gate, push).

## Busters
| # | Buster | State |
|---|---|---|
| B1 | `sync.py claim` / `release` push ONE plumbing commit on origin's tip (`push_claim_commit`): no merge commit, no gate, works from a dirty or ahead tree, and no longer ships the tree's unrelated unshipped commits as a side effect. Re-checks area overlap on every push retry. Test: `test_claim_and_release_make_no_merge_commit_and_ship_nothing_else` (fails on the old code). | DONE 2026-10-16 |
| B2 | Skip claim + release when the task writes only NEW files under its own dated folder (a report, a lab run): nothing to collide on. Claim when the area can overlap another session's (shared code, NEXT_SESSION.md, registries). | POLICY, in force |
| B3 | One ship per task: commit small, but run `sync.py ship` once at the end (each ship adds a merge commit while origin moves). Mid-task ships only for a hand-off the next session needs. | POLICY, in force |
| B4 | `release` rides the last ship: `sync.py ship --release <slug>` deletes the claim file in a commit on the branch, so it goes out in the same push as the work (one push and one fetch less per task; nothing to ship falls back to the B1 plumbing release). Tests: `test_ship_release_drops_the_claim_in_the_same_push_as_the_work`, `test_ship_release_with_nothing_to_ship_still_releases` (fail on the old code: no `release_slug`). Est. saving: 1 of ~3 pushes per claimed task (OURS). | DONE 2026-10-16 |
| B5 | Read less at boot: STATUS.md head only (first 40 lines), tail files with `-n`/offset, one `Grep` instead of reading a file to find a line. | POLICY |
| B6 | Run a test file, not the suite, while iterating (`pytest path -k name`); the full gate runs once in `ship`, CI repeats it. | POLICY |
| B7 | Never poll: one background shell per wait (`run_in_background`), results come back as a notification. | POLICY (CLAUDE.md) |
| B8 | Mechanical work (renames, table rewrites, report counting) goes to a script in T0, not to model turns. | POLICY |
| B9 | CI: workflow-level `paths` (already in ci.yml) skips the whole run, which is right for a non-required check; if CI ever becomes a REQUIRED check, a skipped workflow reports nothing and blocks the push, so then switch to job-level detection (cheap job + `if:` on the heavy job; a job skipped by `if:` counts as passing). Keep `cancel-in-progress` off trunk (already set). Saving: the heavy job on docs-only pushes, unmeasured (SOURCED: Pants blog 2022-10-10 on skipping jobs under branch protection; GitHub community discussions 26251 and 44490). | DONE 2026-10-16: verified ci.yml has trigger `paths` + trunk-safe `cancel-in-progress`; fast-track is NOT branch-protected (gh api 404), so no required check blocks a skipped run; nothing to change |
| B10 | `git config pull.ff only` / `merge --ff-only` where a tree only follows trunk (live mirror pulls, relay lanes): a diverged pull fails loudly instead of making a merge commit. `sync.py ship` still merges trunk on purpose (`merge_trunk`), so this config is not set globally. Est. saving: part of the 40% merge share (SOURCED: git docs `pull.ff`). | POLICY, no code: ship keeps its merge |
| B11 | Keep the context prefix stable: CLAUDE.md short and edited rarely, MCP tools deferred, compaction only per WORKERS.md rule 5 (auto-compact is a backstop; hand over instead), verbose runs (tests, logs) to a subagent that returns a summary. Cache read 0.1x, 5-minute write 1.25x, 1-hour write 2x of base input (0.025x reads on Fable 5.1); the 5-minute cache expires in a quiet stretch and the next turn re-writes it. A forked subagent reuses the parent's cache, a fresh one does not; agent teams cost about 7x a plain session. Saving: unmeasured (SOURCED: platform.claude.com prompt-caching docs; code.claude.com costs and sub-agents docs). | POLICY |
| B12 | Boot in one message: the independent boot reads (sync start, STATUS head, claims) go out as parallel tool calls, not one turn each. Est. saving: 3-4 turns per session (OURS). | POLICY |

Searched, no usable source found: batching tool calls (no solid source), shallow / partial fetch (not covered by results; our repo fetch is small, untested).

## Re-measure 2026-10-16 (after B1/B4) and adoption
- The 24 h window is mostly pre-B1: 685 of 862 commits predate B1 (landed 10:09Z). Post-B4 (10:57Z) the overhead is ~51% (merge 34%, claim 8%, release 9%), not the 65% the full window shows.
- Release is still 9% because sessions were never told: CLAUDE.md boot step 3, PARALLEL.md step 4 and ~16 other docs/prompts said `ship` then a separate `release`. Fixed 2026-10-16: they now say `sync.py ship --release <slug>`; standalone `release` stays for 'nothing to ship'. Test: `MyTradingSys/tests/docs/test_ship_release_contract.py` (failed on the old text: 6 of 7 cases).
- Better metrics than commit share: ship-to-green time (push to the `green/fast-track` advance) and red-CI hours. CI coalesces runs (50 runs for 862 commits), so commit count is not CI load; green did not advance for 5.5 h on 2026-10-16 while commit share looked fine.
- Landing today from sibling sessions (check the log before relying on them): gate `explain()` + persisted step timings; `auto_deploy.py` takes a gate slot; `scripts/dev/trace.py` and `research_kit_lint.py`; the CI root-cause fix.

## Follow-up results 2026-10-17 (speed-followup-1017)
- CI: last 3 completed fast-track runs are green: 9894d9f2 success, ea530850 success, 790257cb success (earlier 204ac612/0e85eaa1/95fbea27 were cancelled by coalescing; 82dc8f27 was the last failure). origin/green/fast-track = 9894d9f2 (advanced). a84b90b3 was still in progress at check time.
- Deploy-slot merge: `pytest scripts/dev/test_auto_deploy.py scripts/dev/test_sync.py -q` = 163 passed in 85.66s (the task's path scripts/sched/test_auto_deploy.py does not exist).
- traffic_report 24 (849 commits): merge 321 (38%), claim 110 (13%), release 110 (13%), other 308 (36%), overhead 541 (64%). Baseline 2026-10-16: 890 commits, merge 40%, claim 14%, release 14%, overhead 68%. Small gain (-4 pts overhead); the window still contains pre-B1 commits, so the ship --release effect is not yet visible. Re-measure on a window starting after 2026-10-16 12:00Z.
- DECISION (OURS): no code fix needed (no red CI in the last 3 runs, no test failures).

## Rejected ideas (2026-10-16), do not re-propose without new evidence
| Idea | Why rejected |
|---|---|
| `sync.py` skips claims automatically when the task looks safe (auto B2) | Removes the duplicate-task guard: 13 tasks were claimed more than once. B2 stays a policy the session applies. |
| Windows CI job non-blocking | `mark-green` needs both OSes green; a non-blocking Windows job would publish `green/fast-track` for SHAs Windows rejects. |
| Quarantine gate step 4f (layer / live-writer paths) | It holds live-path execution tests; skipping it must fail closed, not open. |
| New gate-busy lock file | `gate_slot` (GATE_SLOTS=2) already limits concurrent gates; a second lock adds a stale-lock failure mode. |

## How to claim a result
Rerun `traffic_report.py 24` a day after a buster ships; write the overhead % in the Session log line of SUPER_SESSION.md.
Target after B1: claim + release near 0% of commits (merge share falls with them). B4 (shipped) saves one more push per task.

## NUC (JIS-NUC) and other hosts
Nothing to install: the change is in `scripts/dev/sync.py`, and every host gets it with its next `sync.py start` (git is the channel, PARALLEL.md).
Relay sessions on the NUC use the same `claim`/`release` calls and need no prompt change.
