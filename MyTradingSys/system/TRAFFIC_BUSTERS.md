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
| B4 | `release` rides the last ship: `sync.py ship --release <slug>` (saves one push and one fetch per task). | CARD: not built |
| B5 | Read less at boot: STATUS.md head only (first 40 lines), tail files with `-n`/offset, one `Grep` instead of reading a file to find a line. | POLICY |
| B6 | Run a test file, not the suite, while iterating (`pytest path -k name`); the full gate runs once in `ship`, CI repeats it. | POLICY |
| B7 | Never poll: one background shell per wait (`run_in_background`), results come back as a notification. | POLICY (CLAUDE.md) |
| B8 | Mechanical work (renames, table rewrites, report counting) goes to a script in T0, not to model turns. | POLICY |

## How to claim a result
Rerun `traffic_report.py 24` a day after a buster ships; write the overhead % in the Session log line of SUPER_SESSION.md.
Target after B1: claim + release near 0% of commits (merge share falls with them). B4 would save one more push per task.

## NUC (JIS-NUC) and other hosts
Nothing to install: the change is in `scripts/dev/sync.py`, and every host gets it with its next `sync.py start` (git is the channel, PARALLEL.md).
Relay sessions on the NUC use the same `claim`/`release` calls and need no prompt change.
