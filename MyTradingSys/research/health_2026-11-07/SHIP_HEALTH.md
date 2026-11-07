# SHIP_HEALTH 2026-11-07

Measured 2026-11-07 ~18:10-18:35 UTC on DESKTOP-F7IU69N. Window: 7 days unless stated. Every number is followed by the command that produced it. Scratch scripts were run from the session scratchpad; their logic is described in the Method line so a reader can redo it. No runtime, order or account data is in this file.

Scope limit: gate timings come from this machine's 10 trees (`runtime_data/gate_timing.jsonl` is per tree and gitignored). JIS-NUC and JIS-NB ships are not in item 1 numbers. CI (item 2) and signals (item 5) cover all machines.

## Summary

| Question | Answer | Source item |
|---|---|---|
| Ship gate wall time (7 d, this machine) | p50 4.0 min, p90 13.2 min, max 29.1 min (n=44 gate runs) | 1 |
| Whole `ship` wall time | p50 13 s, p90 324 s, max 1088 s (n=64) | 1 |
| Failed ships | 12 of 64 (19 %) | 1 |
| Second ship from one tree within 10 min (the `--again` case) | 40 of 64 (62 %); the flag itself is not logged | 1 |
| CI red episodes on origin/fast-track | 92, trunk red about 26.7 % of the 7 d (closed episodes only) | 2 |
| Revert commits on origin/fast-track | 64 (23 name "CI RED" in the subject) | 2 |
| Stale artifact pages | 2 (`mts_layer_map`, `mts_home`) | 3 |
| HIGH broadcasts still needing action | 22, all for jis-nuc, oldest 32.8 h | 5 |
| Ask to first ack | median 0.13 h, mean 16.8 h (0.7 d), p90 80.5 h (n=35) | 5 |

The seed said "avg ask-to-answer 3 days". Measured mean first-ack is 0.7 days; the 3-day figure belongs to the slowest asks only (p90 3.4 days).

## 1. Ship gate

Method: read all `C:/Users/e-ngineers/IdeaProjects/*/runtime_data/gate_timing.jsonl` (10 files, 1512 rows, 0 unparseable, 2026-10-27 to 2026-11-07), keep rows with `utc` in the last 7 d (1044 rows). `ship_wall` rows = whole ship. A gate run = step rows of one sha in one tree; a repeated step id starts a new run; wall = first step start (utc minus secs) to last step end (same rule as `mts_doctor.py ship_time`).
Command: `python gt.py` (scratchpad script implementing the above). Cross-check: `python scripts/dev/mts_doctor.py` SHIP-TIME rule uses the same logic over 24 h.

| Metric (7 d) | n | p50 | p90 | max |
|---|---|---|---|---|
| Gate run wall (min) | 44 | 4.0 | 13.2 | 29.1 |
| `ship_wall` (s) | 64 | 13.4 | 323.5 | 1088.1 |
| Gate run wall, all 15 days on disk (min) | 58 | 4.0 | 15.9 | 36.0 |
| `ship_wall` all days (s) | 94 | 23.2 | 638.3 | 3048.7 |

The seed fact (doctor, 24 h: gate median 13.5 min, max 63.4 min) is a different window and a different tree set (the doctor reads the one tree it runs in). Both are real: the same gate ranges 4 to 63 min depending on how many gates share the machine.

| Failure measure (7 d) | Value | Command |
|---|---|---|
| Ships with `ok:false` | 12 of 64 | `python gt.py` (ship rows) |
| Gate runs with a failing step | 13 of 44 | same |
| Sum of ship run time | 4136 s; retry time 16 s; wait time 0 s | same |
| Second ship within 10 min in the same tree | 40 of 64 (mts-gemini tree 54 ships) | same, `ship_wall` pairs < 600 s apart |

`--again`: since 2026-10-25 it is a no-op that only silences a note (`scripts/dev/sync.py` `check_ship_gap`, l.739-749; flag handling l.2262). It is not logged anywhere, so a direct count is impossible; the second-ship-within-10-min row above is the measurable equivalent. Needs: fail reason in `gate_timing.jsonl` (card below).

Failing gate steps, 7 d (`python gt.py`, rows with `ok:false`): 3xm Extra tests the change must pass 3; 3gi Gate impact tests 2; 3cm Conflict markers 2; 3af Artifact registry tests 2; 3rb, 3vd, 3lm, 3js 1 each.

Slowest gate steps, 7 d (steps run in parallel shards, so totals are CPU-minutes, not wall):

| Step | Name | n | median s | max s |
|---|---|---|---|---|
| 3xt | Extra tests outside the collected dirs | 6 | 695 | 726 |
| 4f | Pytest layer + live-writer tests | 7 | 404 | 863 |
| 3sig | Signals between logins (mts_signal.py) | 6 | 357 | 769 |
| 5b | Layer tests (87 modules, 4 parallel) | 6 | 346 | 407 |
| 4h | Pytest shard 5/5 | 3 | 711 | 810 |
| 4g | Pytest shard 4/5 (22 files) | 6 | 274 | 380 |

Command: `python gt.py` (per-step table).

### ORPHAN gate tree, "kill failed"

- Where: not in `sync.py` itself. `sync.py run_host_health` (l.2168) calls `host_health.run_safe`; the text is built in `scripts/dev/host_health.py` `run()` l.432-435: `"ORPHAN gate tree PID n (no live claude.exe/ship above it) - kill failed"`. The kill is `kill_tree(pid)`, l.105-107: `taskkill /PID <pid> /T /F`, success = return code 0.
- Why it fails on Windows (measured and read from code):
  1. Return code 128 means "process not found". Measured: `taskkill /PID 999999 /T /F` returns 128, `ERROR: The process "999999" not found.` An orphan gate that exits between the process snapshot and the kill (gates are minutes-long and finish on their own) is already gone, but is counted as "kill failed".
  2. `taskkill /T` walks live ParentProcessId links. Windows does not re-parent children of a dead process, so any pytest worker whose intermediate parent already died is unreachable by the tree kill. `find_orphan_gates` (l.147-166) only lists processes whose command line contains `run_all_tests.py` and returns the top-most, so such leftovers are neither killed nor reported.
  3. `taskkill` returns non-zero if any process in the tree cannot be terminated (Access denied for an elevated or other-session child), so one stubborn child makes the whole tree "failed".
  4. The captured stderr is dropped, so the reason is never written (`health.log` holds only 1 line, from 2026-10-23, a powershell timeout; `ls %TEMP%/mts_host_health`). The message gives no cause.
- Not reproduced today: 0 orphan gate trees on this machine (process list, below). The causes above are code analysis plus the 128 measurement.
- Fix filed as raw card `host-health-kill-tree-orphan-1107` (lane SONNET). Not fixed here.

## 2. CI on origin/fast-track

Method: `gh run list --branch fast-track --limit 1000 --json databaseId,conclusion,createdAt,updatedAt,workflowName,status` (1000 runs reach back to 2026-10-31T06:58Z); keep createdAt in the last 7 d (882, all workflow `CI`). Red episode = first `failure` (by updatedAt) after a `success`, ended by the next `success`.
Commands: `gh run list ...` then `python ci.py` (scratchpad); `git log origin/fast-track --since="7 days ago" --no-merges --format=%s | grep -c '^Revert'`.

| Measure (7 d) | Value |
|---|---|
| CI runs | 882: 609 success, 238 failure, 25 cancelled, 10 unfinished |
| Failure rate of finished runs | 238 / 847 = 28 % |
| CI run duration (success or failure) | p50 4.6 min, p90 8.9 min, max 64.5 min |
| Red episodes | 92 (one still open since 2026-11-07 17:55Z; newest run was queued when measured) |
| Time red, closed episodes | 2688 min of 10080 = 26.7 % |
| Longest red episodes | 782 min (11-02 20:24Z), 439 min (11-01 22:32Z), 203 min (11-04 09:25Z), 97 min (11-02 11:33Z) |
| Median red episode | 9 min (most episodes are minutes, the tail is hours) |
| Trunk commits in window | 3217 (incl. merges) |
| Revert commits (non-merge, subject starts `Revert`) | 64; 23 name "CI RED" |

Caveat: red time counts from the first failed run's finish to the next success's finish; concurrent runs overlap, so it over-states the red the author sees by up to one CI run (about 5 min) per episode. Reverts include human reverts, not only CI auto-reverts.

Which step turns CI red: `gh run view <id> --json jobs` on the 60 newest failed runs: 60 parsed, 0 errors, all failures sit in the one job `Offline gate` (183 failed-step hits across the matrix legs), so the job level does not discriminate. One run's `--log-failed` (the newest red when measured) shows the inner failure: `Step 4: Pytest tests: FAIL`, `test_aibridge_version_bump.py` (2 tests), a pytest file the ship smoke gate did not select. A per-test census over 50 failed runs was started (`gh run view --log-failed`, grep `Step ...: FAIL`) but did not finish in the time box; it is the first step of card `ci-red-ship-gate-parity-1107`.

## 3. Artifact pages

Command: `python scripts/dev/artifacts.py stale` (exit text, 2 lines):

| Page | Status |
|---|---|
| mts_layer_map | STALE (repo build differs from last publish) |
| mts_home | STALE (repo build differs from last publish) |

n stale pages = 2. The republish cards exist and are done (`republish-6-stale-artifact-pages-flagged`); the pages went stale again as the repo moved.

## 4. Doctor and status board

Command: `python scripts/dev/mts_doctor.py` (took longer than the 120 s foreground limit and was moved to the background: itself a time sink; wall time not measured exactly). Result line: `HEALTH: 6 WARN: SIZE-HEADROOM, CI-REVERT, WAITING-ON-OPERATOR, BROADCAST, ASK-GAPS, SUPERVISOR-IDLE`; 40 findings in its report (the report file it writes was deleted, not shipped).

Command: `python scripts/dev/status_board.py` (head):

| Item | Value |
|---|---|
| Status line | week budget up to 71 %; CI green (at that moment); 45 CRITICAL/CRUCIAL cards open; RED idle with ready work: login B, C |
| Trunk commits per UTC day | 11-07 153 (partial), 11-06 540, 11-05 152, 11-04 360, 11-03 291, 11-02 270 |
| Cards closed | today 32, yesterday 92 |
| Gate wall, median of last 5 ships | 32 s [19, 39, 32, 24, 51] |
| Ships running, stalled over 30 min | 1 running, 1 stalled |
| Stale claims over 24 h | 4: hot-wallet-watch-verify-5-eth-addresses (180 h), lf-session-timing-gpt-rederive (256 h), news-hot-wallet-watch (187 h), pizzino-layer-dashboard-where-we-are-lev (202 h) |
| Cards | open CRITICAL 18, CRUCIAL 27, parked 8, raw 22, blocked 37 |
| Asks table | 19 OVERDUE of 24 waiting |
| Supervisors section | NOT_IN_DATA: `git checkout -q -B mts-signals FETCH_HEAD` failed ("FETCH_HEAD is not a commit and a branch 'mts-signals' ..."), so the board shows no supervisor mode (finding, no card: Job 1 builder owns signals code) |

Seed check: the SHIP-TIME numbers in the seed (ship_wall median 140 s, p90 5121 s) are not what the board shows now (median 32 s). They move with the window; use item 1 for the 7 d view.

## 5. Signals

Method: the `mts-signals` branch holds one JSON file per signal (2241 files at origin/mts-signals head). Parsed all with `git cat-file --batch` into a list, 2241 parsed, 0 lost. Kinds: ack 755, note 707, done 423, broadcast 157, ytuse 105, ask 37, claim 26, esc 16, ytblock 13, ytclean 2. Commands: `git ls-tree -r --name-only origin/mts-signals`, `python sig.py`, `python sig2.py`, `python scripts/dev/mts_signal.py pending --host <h> --json`.

Authoritative pending list (the tool's own rule, state none or told older than 2 h):

| Host | HIGH broadcasts needing action | States | Oldest |
|---|---|---|---|
| jis-nuc | 22 | 16 expired-told, 6 none | 32.8 h |
| jis-nb | 0 | | |
| desktop-f7iu69n | 0 | | |

Command: `for h in jis-nuc jis-nb desktop-f7iu69n; do python scripts/dev/mts_signal.py pending --host $h --json; done`.

Own count of all 54 HIGH broadcasts of the last 7 d against every other host (ignores the `to` field, so it is an upper bound):

| Host | done | none > 2 h | told > 2 h | young or other |
|---|---|---|---|---|
| desktop-f7iu69n | 29 | 12 | 0 | 8 |
| jis-nb | 26 | 2 | 0 | 0 |
| jis-nuc | 5 | 9 | 12 | 5 |

Median time from a HIGH broadcast to the host's latest ack (7 d): desktop-f7iu69n 1.1 h (n=41), jis-nb 12.7 h (n=39), jis-nuc 48.1 h (n=27). The receiver-side problem is one host: jis-nuc.

Asks (all 35 asks with an id, 2026-11-02 to now; none older):

| Measure | Value |
|---|---|
| Asks answered by any ack (told or done) | 35 of 35 |
| First ack: mean / median / p90 / max | 16.8 h (0.7 d) / 0.13 h / 80.5 h / 92.0 h |
| First `done` ack: mean / median / p90 | 18.0 h / 1.14 h / 80.5 h |
| First ack inside 1 minute | 2 of 35 |
| First ack inside 60 minutes | 23 of 35 |
| Escalations sent (`esc`) | 16 |

Interpretation for the 1-minute goal (Job 1): 66 % of asks get a first ack within the hour but only 6 % within a minute; the mean is dominated by a few asks to an idle host. Related existing card (twin, not re-filed): `broadcast-hygiene-stale-and-b4c2dfe` (ready, SONNET): close or expire broadcasts to hosts that cannot ack.

## 6. Trees, tidy, processes

| Check | Result | Command |
|---|---|---|
| Trees holding work not on origin/fast-track | 9 of 13 trees (`sync.py where`) | `python scripts/dev/sync.py where` |
| Largest | spikefade-a-20261031-2: 3 unshipped commits, 61 modified files; dsabr-c6-e2e-script-2: 11 unshipped commits | same |
| Tidy dry run | would remove 0, kept 11 (uncommitted 4, unshipped 3, active 2, branch 1, hand-named 1) | `python scripts/dev/sync.py tidy` |
| Stray processes | none that are orphan gates (list below) | `Get-CimInstance Win32_Process` filtered to python, claude, node, git |

Processes found (listed, none killed): Claude desktop app and helper processes (parent 4768, started 18:56 local), one `claude-code 2.1.317` session process (PID 5092), `scripts/dev/bg_watch.py until --file ...sigtest.o...` (PID 16284), `scripts/dev/supervisor.py wait --timeout 50m --login A` (PID 17500), and this session's own scratch scripts (mine). Zero `run_all_tests.py` processes, so zero orphan gates. Local times in the listing are IST (UTC+5:30).

## 7. Top-5 time sinks and the raw cards

Twin check: `python scripts/dev/tasks.py twins` run after filing, 0 twins for the 4 new cards; existing related cards read: `gate-flakes-under-load-test-lease-py-tes` (blocked; load flakes), `broadcast-hygiene-stale-and-b4c2dfe` (ready), `trunk-lag-test-fails-under-full-load`, `ci-auto-revert-red-trunk` (done), `bug-session-handoff-ship-speed-audit` (done).

| # | Sink | Evidence | Fix card (raw, lane) |
|---|---|---|---|
| 1 | Trunk red 26.7 % of the week, 92 episodes, 64 reverts | item 2 | `ci-red-ship-gate-parity-1107` (SONNET) |
| 2 | Three gate steps at 357-695 s median (3xt, 4f, 3sig) | item 1 | `gate-slow-steps-3xt-3sig-4f-1107` (SONNET) |
| 3 | 19 % of ships fail, 62 % re-ship within 10 min, and the failing step is not recorded | item 1 | `ship-record-gate-failure-step-1107` (SONNET) |
| 4 | Orphan gate reaping reports "kill failed" (cause hidden, exit 128 counted as failure, orphaned children unreachable) | item 1 | `host-health-kill-tree-orphan-1107` (SONNET) |
| 5 | Stale signal backlog: 22 HIGH broadcasts for jis-nuc, median ack 48 h | item 5 | none: twin `broadcast-hygiene-stale-and-b4c2dfe` already covers it; this report adds the numbers |

Not carded (noted): `mts_doctor.py` runs over 120 s; `status_board.py` Supervisors section fails on the `mts-signals` checkout.

## Method notes and limits

- Gate and ship timing: this machine only (10 trees), not JIS-NUC or JIS-NB.
- CI red time is an upper bound (episode ends at the finish of the next green run).
- Ask "answer" = first `ack` record with the ask id (the signals tool has no separate answer record; `ack` carries told or done). An ask answered in chat or by a commit is not seen.
- Seed facts were re-measured, not copied; where a seed number differs it is said above.
