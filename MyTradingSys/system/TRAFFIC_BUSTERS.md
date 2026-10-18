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
| B2 | (automatic since B16) Skip claim + release when the task writes only NEW files under its own dated folder (a report, a lab run): nothing to collide on. Claim when the area can overlap another session's (shared code, NEXT_SESSION.md, registries). | POLICY, in force |
| B3 | One ship per task: commit small, but run `sync.py ship` once at the end (each ship adds a merge commit while origin moves). Mid-task ships only for a hand-off the next session needs. | POLICY, in force |
| B4 | `release` rides the last ship: `sync.py ship --release <slug>` deletes the claim file in a commit on the branch, so it goes out in the same push as the work (one push and one fetch less per task; nothing to ship falls back to the B1 plumbing release). Tests: `test_ship_release_drops_the_claim_in_the_same_push_as_the_work`, `test_ship_release_with_nothing_to_ship_still_releases` (fail on the old code: no `release_slug`). Est. saving: 1 of ~3 pushes per claimed task (OURS). | DONE 2026-10-16 |
| B5 | Read less at boot: STATUS.md head only (first 40 lines), tail files with `-n`/offset, one `Grep` instead of reading a file to find a line. | POLICY |
| B6 | Run a test file, not the suite, while iterating (`pytest path -k name`); the full gate runs once in `ship`, CI repeats it. | POLICY |
| B7 | Never poll: one background shell per wait (`run_in_background`), results come back as a notification. | POLICY (CLAUDE.md) |
| B8 | Mechanical work (renames, table rewrites, report counting) goes to a script in T0, not to model turns. | POLICY |
| B9 | CI: workflow-level `paths` (already in ci.yml) skips the whole run, which is right for a non-required check; if CI ever becomes a REQUIRED check, a skipped workflow reports nothing and blocks the push, so then switch to job-level detection (cheap job + `if:` on the heavy job; a job skipped by `if:` counts as passing). Keep `cancel-in-progress` off trunk (already set). Saving: the heavy job on docs-only pushes, unmeasured (SOURCED: Pants blog 2022-10-10 on skipping jobs under branch protection; GitHub community discussions 26251 and 44490). | DONE 2026-10-16: verified ci.yml has trigger `paths` + trunk-safe `cancel-in-progress`; fast-track is NOT branch-protected (gh api 404), so no required check blocks a skipped run; nothing to change |
| B10 | `git config pull.ff only` / `merge --ff-only` where a tree only follows trunk (live mirror pulls, relay lanes): a diverged pull fails loudly instead of making a merge commit. `sync.py ship` still merges trunk on purpose (`merge_trunk`), so this config is not set globally. Est. saving: part of the 40% merge share (SOURCED: git docs `pull.ff`). | POLICY, no code: ship keeps its merge |
| B11 | Keep the context prefix stable: CLAUDE.md short and edited rarely, MCP tools deferred, no compaction (turn budget per WORKERS.md rule 5; hand over instead), verbose runs (tests, logs) to a subagent that returns a summary. Cache read 0.1x, 5-minute write 1.25x, 1-hour write 2x of base input (0.025x reads on Fable 5.1); the 5-minute cache expires in a quiet stretch and the next turn re-writes it. A forked subagent reuses the parent's cache, a fresh one does not; agent teams cost about 7x a plain session. Saving: unmeasured (SOURCED: platform.claude.com prompt-caching docs; code.claude.com costs and sub-agents docs). | POLICY |
| B13 | `tasks.py lint` reports a stale ready card as `WARN`, exit 0 (it failed ship gates and trunk CI red 2026-10-17 07:36 for any session that added a ready card). `tasks.py stale` still exits 1. Test: `test_lint_only_warns_about_stale_ready_cards`. | DONE 2026-10-17 |
| B14 | Wiring gate ignores `MyTradingSys/research/**`: no registry entry needed for run-once study scripts, a gone or now-live entry there is no failure (registry file was touched by 68 commits in 72 h and broke once on a merge). Test: `test_study_scripts_never_fail_the_gate_declared_or_not`. | DONE 2026-10-17 |
| B15 | `run_extra_tests.discovered()`: every tracked `test_*.py` under `research/` runs without an EXTRA entry; B150 accepts it. Test: `test_study_folder_tests_are_discovered_without_an_entry`. ~100 of 1162 non-merge commits in 72 h were registry/allowlist/size-cap upkeep. | DONE 2026-10-17 |
| B16 | `sync.py claim` skips itself (prints why, no commit) when the task's whole scope is NEW files under a dated folder: scope = `--area` paths, else `scope_in` of the card named like the task (read from origin's tip); `read-only:` entries ignored; fail open (no card, `live_path`, an existing file, any path outside a dated folder = claim). `--force` claims anyway. `release` prints a one-line `ship --release <slug>` hint when the tree has unshipped commits. 72 h before: 51 claims, 56 standalone releases, 2 `ship --release`. Tests: `test_claim_skips_itself_for_new_files_under_a_dated_folder`, `test_claim_skip_by_area_and_force_override`, `test_release_hints_at_ship_release_when_the_tree_has_unshipped_commits` (fail on the old code). | DONE 2026-10-17 |
| B17 | Lane-health heartbeat no longer edits `lane_state.json`: it is pushed as a plumbing commit to the side branch `lane-heartbeat` (`push_heartbeat`; not trunk, CI does not run on it); every sweep fetches it (`remote_heartbeat`) so the Haiku watchdog on another host still sees a dead lab. Status changes still commit to trunk. No remote = old behaviour. 55 of 1822 commits in 72 h were hourly heartbeat-only edits ("lane health: GPT up"). Tests: `HeartbeatSideBranch` (3, two fail on the old code). | DONE 2026-10-17 |
| B18 | CLAUDE.md size cap raised by 1 KB (value: `test_integrity.SIZE_CAPS`, the only place it is written): 7 "trim to size cap" commits in 72 h; +1 KB is ~256 cached tokens. `test_7b_nothing_else_depends_on_the_claude_md_cap_number` proves no other file quotes the number (passes before and after: it is the safety proof, not a regression test). Add detail to a system/ doc rather than word-trimming. Not a warning: a soft cap would let the always-loaded prefix grow back. | DONE 2026-10-17 |
| B19 | Ship gate speed (GATE_SPEED.md D1-D7): precheck of cheap steps + targeted pytest before the slot, fail-fast with NOT RUN, slot around the main phase only, same-tree pass record, push/fetch race retries with a scoped re-gate, research data and config files no longer force a full gate, smoke 3xt/5b run only the reachable subset, test_turn_meter in-process (195 s -> 7 s). Tests: `TestGateSpeed`, `TestPassRecord`, `GateSpeedRules`, `ShipRaceTest`, `test_config_check.py` (fail on the old code). | DONE 2026-10-18 |
| B12 | Boot in one message: the independent boot reads (sync start, STATUS head, claims) go out as parallel tool calls, not one turn each. Est. saving: 3-4 turns per session (OURS). | POLICY |

Searched, no usable source found: batching tool calls (no solid source), shallow / partial fetch (not covered by results; our repo fetch is small, untested).

## Baseline 2026-10-17 (before B16-B18), `traffic_report.py 24`
622 commits: merge 219 (35%), claim 76 (12%), release 79 (13%), other 248 (40%), overhead 374 (60%). 72 h: 1822 commits, overhead 64%. Re-measure on a window starting after these ship; expect claim/release/lane-health to fall, merge share only follows once fewer pushes race.

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

## Gate and boot speed, 2026-10-18 (DOCTOR-NB-1018, measured locally, `pytest --durations`)
- Done: `screen.py` `build_ledger` called `np.nanpercentile(axis=0)` per day (1440 Python-level column loops): 91 s per call, three tests, 295 s of step 3xt. `col_percentile` (one sort, numpy's own lerp) is bit-identical (test) and the file runs in 9 s. `test_pit_leakage.f4_planted` rescanned all earlier bars per bar (O(n^2)): 126 s -> under 9 s with `bisect`. Step 3xt serial sum fell by about 7 min; it was the slowest gate step and the Windows CI job's critical path.
- Done: SUPER_SESSION.md 22.1 -> 19.0 KB (rules 11-13 moved out of the log, retired bullets and the 10-15 audit table cut): read by every coordinator boot.
- Next levers, biggest first: (1) enforce B4 in `sync.py`: `ship` on a branch whose claim slug is known closes that claim itself (release 13% + claim 14% of commits; adoption 19%); (2) layer tests step 5b 207 s and `test_sync.py` 231 s serial (63 tests, 8-17 s each, git-bound) are the next slowest steps; (3) Windows CI 12-17 min vs Ubuntu 2-4 min gates mark-green: profile the Windows-only slow steps from `gate_timing.jsonl`; (4) 201 of 642 commits per day are `Merge remote-tracking branch` from ship merging trunk in: fewer, bigger ships per task.

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

## Opus cost review, 2026-10-18 (operator-named Opus; DOCTOR-NB-1018) - to implement, ranked
Measured over 12 sessions / 33 gate-timing files. Done: stop_guard blocks a session once per unchanged state; model_guard denies click cards.
Gate (wall time): (1) one machine-wide process budget for run_all_tests.gate_jobs / exec_layer_chunks / exec_unittest_shards / run_extra_tests.jobs (2 gates run ~26 procs on 6 CPUs; 3k 617 s vs 63 s best); (2) 3xt and 5b run only affected tests via gate_select.mentions (CI stays full); (3) gate_select.explain: research non-.py files, lookahead_allowlist.tsv, .gitignore, .aiexclude must not force the full gate (14 of 21 full gates); (4) claims on a separate branch (181 trunk commits/day) and merge-tree scratch merge in ship; (5) gate_slot FIFO with queue position, `ship --wait N` exit 75 "NOT SHIPPED" (a silent exit 0 was the tool timeout killing the call, ship itself waits forever: run ship with run_in_background); (6) run_all_tests sets CODEX_HOME to an empty temp dir, ship refuses non-docs work when ci_watch shows 2 red runs (`--ci-fix` / `--force-red`); (7) per-step pass cache keyed by code hash; (8) CI: Windows job runs selected steps only, pip cache, drop MyTradingSys/items/** from path filter.
Session tokens: boot steps run once per session (CLAUDE.md "every turn" wording costs 2-4%); no foreground sleeps/polls (PreToolUse deny, B7: 20% of tokens); ship prints "verified: cherry empty"; one-line Opus-session warning; do not re-read own Artifact (Grep the local file); BASH_MAX_OUTPUT_LENGTH=8000 (check the app honours it); disable unused plugins/MCPs in build sessions; tasks.py check prints failures only; Haiku for scoped briefs.
