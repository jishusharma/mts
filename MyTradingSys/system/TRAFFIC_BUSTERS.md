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
| B11 | Keep the context prefix stable: CLAUDE.md short and edited rarely, MCP tools deferred, `/compact` with instructions before auto-compact, verbose runs (tests, logs) to a subagent that returns a summary. Cache read 0.1x, 5-minute write 1.25x, 1-hour write 2x of base input (0.025x reads on Fable 5.1); the 5-minute cache expires in a quiet stretch and the next turn re-writes it. A forked subagent reuses the parent's cache, a fresh one does not; agent teams cost about 7x a plain session. Saving: unmeasured (SOURCED: platform.claude.com prompt-caching docs; code.claude.com costs and sub-agents docs). | POLICY |
| B12 | Boot in one message: the independent boot reads (sync start, STATUS head, claims) go out as parallel tool calls, not one turn each. Est. saving: 3-4 turns per session (OURS). | POLICY |

Searched, no usable source found: batching tool calls (no solid source), shallow / partial fetch (not covered by results; our repo fetch is small, untested).

## How to claim a result
Rerun `traffic_report.py 24` a day after a buster ships; write the overhead % in the Session log line of SUPER_SESSION.md.
Target after B1: claim + release near 0% of commits (merge share falls with them). B4 (shipped) saves one more push per task.

## NUC (JIS-NUC) and other hosts
Nothing to install: the change is in `scripts/dev/sync.py`, and every host gets it with its next `sync.py start` (git is the channel, PARALLEL.md).
Relay sessions on the NUC use the same `claim`/`release` calls and need no prompt change.
