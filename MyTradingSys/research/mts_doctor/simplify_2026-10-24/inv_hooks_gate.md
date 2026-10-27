# Hooks and gate steps: cost / catch (read-only audit, 2026-10-24)

## Data and caveats
- Hooks: `.claude/settings.json` (26 hook entries, 12 scripts). Per-call ms from `python scripts/dev/hook_bench.py -n 3`, run today on this machine
  (median of 3, one Bash-tool payload, temp state dirs). No stored hook timing exists in runtime_data (hook_bench only prints).
  SubagentStart `role_loader` is not benched (assume ~0.25 s like its other two events).
- Hook history: `git log --since=14.days origin/fast-track` = 5367 commits. Catch/cause counts come from commit subjects (regex on the hook name),
  `MyTradingSys/research/BUGS.md` (320 lines; there is no MyTradingSys/system/BUGS.md) and
  `MyTradingSys/research/thinker/2026-10-23_guard_spiral_review.md`. Commit-subject counts are approximate (name regex).
- Gate: `runtime_data/gate_timing.jsonl` from 13 worktrees, 2167 rows, no duplicates, window 2026-10-19T21:39Z to 10-23T20:54Z.
  That is 5 days, not 14: the log is young. 111 rows are `ship` (sync.ship, not a test step; 47 of 112 not ok = ship aborts) and are excluded.
  2056 test-step rows used. Sub-shards (4h.1, 3xt.8, 5b.3 ...) are folded into the parent step.
- `secs` = queue wait + run + retry. Shards run in parallel, so "total min" is summed slot time, not wall time. Older rows have mode null;
  "smoke runs" counts only rows tagged `smoke`.
- Timeout = failed row with secs in [240,245): smoke steps are capped at FAST_STEP_TIMEOUT_S = 240 (run_all_tests.py:108). Timeouts are cost, not catches.
  "Other fails" = a real test/lint failure OR a slow full-gate hang; the log cannot tell which. No fail was verified as a real bug here.

## Table 1. Hooks (sorted by cost: ms x processes launched per event)
Each hook is a Python process start. A tool call = PreToolUse + PostToolUse. Bench wall: tool call 0.64 s vs budget 0.5 (OVER),
prompt 0.52 s (budget 0.8), stop 0.38 s (budget 1.0).

| hook script | events (matcher) | ms/call | LOC | last commit | commits 14d | subjects naming it 14d / BUGS.md | caught / caused |
|---|---|---|---|---|---|---|---|
| turn_meter.py | SessionStart, UserPromptSubmit, PreToolUse `*`, PostToolUse (all) | 160-350 (fires 2x per tool call) | 484 | 10-23 | 24 | 14 / 0 | caused: 49 false stops, halted the operator's Opus session and a Supervisor on 10-23 (guard_spiral_review); now warn-only. Catch: none recorded |
| model_guard.py | PreToolUse (Agent, start_session, SendMessage, wrap_up, +10 tools) | 290 | 598 | 10-23 | 17 | 17 / 4 (B200 HIGH, OPEN) | caused: blocked a real operator question, Eagle_Eyes started as an invisible Agent, 6+ fix-on-fix commits in 48 h; now warn-only. Catch: none recorded |
| role_loader.py | SessionStart, SubagentStart, UserPromptSubmit | 240-290 (x3 events) | 1030 | 10-23 | 19 | 12 / 0 | caused: "IdeaProjects" loaded Thinker; role at char 644 not seen; two role-line detectors diverged. Catch: injects role text (CLAUDE.md step 5a needs it) |
| mts_signal.py | SessionStart, UserPromptSubmit, PostToolUse Bash (async), Stop | 190-250 | 929 | 10-23 | 20 | 13 / 2 (B192) | caused: B192 visible console windows per git call; CI red 10-17. Catch: none recorded (a messenger, not a guard) |
| shot.py | SessionStart, UserPromptSubmit | 210-260 | 1141 | 10-22 | 12 | ~32 (many are the screenshot topic, not the hook) / 14 (reads, not the hook) | feature (screenshot intake), not a guard; cost is size |
| trunk_lag.py | SessionStart (40 s timeout), UserPromptSubmit | 520 prompt; 3800 at session start | 270 | 10-23 | 6 | 5 / 0 | catch: warns a session whose tree fell behind trunk (stale main hooks, cause #5). Cost: 3.8 s once per session (fetch) |
| stop_guard.py | Stop | 380 | 143 | 10-22 | 8 | 2 / 0 | catch: blocks ending a session with unshipped work; test step 3sg |
| preship.py | PreToolUse Bash (hook-commit, 180 s timeout), PostToolUse Edit/Write (hook-edit) | 200 commit, 300 edit | 278 | 10-24 | 4 | 1 / 0 | intent: catch the gate's most frequent failures at edit/commit (commit 10-22). No counted catches in the log |
| ci_watch.py | SessionStart, UserPromptSubmit | 150-160 | 148 | 10-23 | 4 | 2 / 0 | catch: red-CI notice (CLAUDE.md boot step 2 relies on it) |
| c_drive_guard.py | SessionStart | 190 | 149 | 10-18 | 2 | 3 / 0 | catch: C: fill incident 10-18 (pytest temp dirs); silent since |
| offer_guard.py | Stop | 170 | 120 | 10-22 | 1 | 1 / 0 | caused: bounced real decisions too (guard_spiral_review row 10-22 17:22). Catch: none recorded |
| prereq_guard.py | Stop | 170 | 135 | 10-22 | 1 | 1 / 0 | caused: false positive on quoted trigger phrases (card 10-22). Catch: none recorded |

### Hooks: cost high, catch ~0 (deletion candidates)
1. turn_meter.py: most launches per tool call (Pre + Post), 24 commits in 14 d, 49 false stops; now warn-only so it enforces nothing. guard_spiral_review already lists the turn_meter caps for removal.
2. model_guard.py: 17 commit subjects, open HIGH B200, fix-on-fix chain; now warn-only, still 290 ms on 14 tool types.
3. offer_guard.py + prereq_guard.py: 2 Stop processes (170 ms each), 1 commit each, false positives, no recorded catch. guard_spiral_review names offer_guard for removal.
4. mts_signal.py: 929 LOC, 4 events, 20 commits, B192; no recorded catch. Its test step 3sig is 80 slot-min with 2 fails.
5. trunk_lag session-start 3.8 s: could be prompt-only (0.5 s) and keep the notice.
6. SubagentStart role_loader duplicates the other two role_loader events (3 processes for one feature).

### Hooks: catches real things (keep)
stop_guard.py (unshipped work), ci_watch.py (red CI), c_drive_guard.py (real C: fill, cheap, silent), trunk_lag.py prompt hook (stale tree), role_loader.py (feature, but 1030 LOC is fragile).
preship.py is unproven (no counted catch); keep until its catches are counted.
A typical tool call launches 3-4 Python processes, 0.64 s measured wall, over the 0.5 s budget.

## Table 2. Gate steps, last 5 days (sorted by total slot time; shown if total >= 2 min or any fail)

| step | name | runs | med s | p90 s | total min | smoke runs | fails | timeouts | other fails |
|---|---|---|---|---|---|---|---|---|---|
| 4h | Pytest (fast): 1 of 27 files that the change reaches | 60 | 240.1 | 1021 | 357.5 | 39 | 13 | 13 | 0 |
| 3k | sync.py parallel ship tests | 37 | 327.2 | 912 | 281.2 | 12 | 1 | 0 | 1 |
| 3xt | Extra tests the change reaches (4 of 124 files) | 51 | 240.1 | 757 | 269.3 | 24 | 11 | 7 | 4 |
| 4g | Pytest (fast): 1 of 27 files that the change reaches | 80 | 60.4 | 303 | 160.1 | 58 | 1 | 1 | 0 |
| 4t | Precheck pytest: 1 test file that references the change | 22 | 140.4 | 985 | 153.3 | 1 | 4 | 0 | 4 |
| 4c | Pytest (fast): 4 of 25 files | 45 | 141.5 | 477 | 148.6 | 23 | 3 | 1 | 2 |
| 5b | Layer tests (78 modules, 4 parallel processes) | 25 | 332.7 | 498 | 127.0 | 2 | 0 | 0 | 0 |
| 4f | Pytest layer + live-writer tests | 25 | 252.1 | 642 | 126.9 | 3 | 0 | 0 | 0 |
| 4b | Pytest (fast): 4 of 16 files | 42 | 131.3 | 299 | 123.9 | 20 | 4 | 0 | 4 |
| 3tl | Task cards meet the Definition of Ready | 46 | 26.7 | 242 | 110.1 | 15 | 5 | 1 | 4 |
| 3sig | Signals between logins (mts_signal.py) | 18 | 187.7 | 561 | 80.1 | 3 | 2 | 0 | 2 |
| 4 | Pytest shard 1/5 (MyTradingSys/tests) | 23 | 92.1 | 395 | 66.8 | 0 | 0 | 0 | 0 |
| 4d | Pytest doc size/contract tests | 63 | 15.8 | 71 | 58.7 | 33 | 8 | 0 | 8 |
| 3dk | Desk board tests | 31 | 70.7 | 157 | 48.0 | 10 | 0 | 0 | 0 |
| 3cx | Layer lab runner tests | 30 | 59.5 | 139 | 36.5 | 13 | 1 | 1 | 0 |
| 3tk | Task card tests | 27 | 73.1 | 127 | 35.4 | 10 | 2 | 1 | 1 |
| 3lh | GPT lane health tests | 24 | 78.2 | 181 | 34.8 | 9 | 1 | 1 | 0 |
| 3dl | CI deps lint | 58 | 10.8 | 38 | 34.0 | 32 | 1 | 0 | 1 |
| 3ds | DSA helper CLI tests (dsa.py) | 21 | 73.3 | 126 | 33.9 | 1 | 1 | 0 | 1 |
| 3ad | Scheduled auto-deploy tests | 19 | 68.2 | 175 | 30.8 | 3 | 0 | 0 | 0 |
| 3bk | Backup snapshot tests | 19 | 63.4 | 177 | 28.1 | 1 | 0 | 0 | 0 |
| 3cr | Control Room page generator tests | 21 | 54.8 | 115 | 24.2 | 6 | 1 | 1 | 0 |
| 3sg | Stop guard tests | 19 | 40.2 | 150 | 23.1 | 3 | 0 | 0 | 0 |
| 3gi | Gate impact tests | 29 | 25.0 | 70 | 17.1 | 3 | 0 | 0 | 0 |
| 3ms | STATUS.md generator tests | 14 | 21.2 | 153 | 12.7 | 0 | 0 | 0 | 0 |
| 3g | Gate coverage tests | 29 | 14.8 | 43 | 11.3 | 3 | 1 | 0 | 1 |
| 3lm | Live mirror tests | 27 | 13.8 | 45 | 8.4 | 1 | 0 | 0 | 0 |
| 3w | Wiring gate tests | 19 | 18.4 | 43 | 7.7 | 2 | 0 | 0 | 0 |
| 4e | Pytest backtest function-style tests | 26 | 12.4 | 26 | 6.5 | 0 | 0 | 0 | 0 |
| 3x | Wiring check (wiring_scan.py --check) | 44 | 4.4 | 15 | 5.5 | 20 | 0 | 0 | 0 |
| 1 | Execution module tests | 26 | 9.9 | 21 | 4.9 | 0 | 0 | 0 | 0 |
| 5c | Options module tests | 27 | 6.7 | 14 | 4.6 | 0 | 1 | 0 | 1 |
| 3sh | Screenshot intake tests | 26 | 5.8 | 14 | 4.3 | 0 | 0 | 0 | 0 |
| 3gd | Gate discovery (B150) | 59 | 0.9 | 6 | 3.0 | 34 | 0 | 0 | 0 |
| 3af | Artifact registry tests | 29 | 1.1 | 6 | 2.1 | 4 | 0 | 0 | 0 |
| (rest) | 32 other steps, each < 2 min total, 0 fails | 895 | - | - | 17.5 | - | 0 | 0 | 0 |

Total slot time 2498 min over 2056 rows (5 days, 13 worktrees).

### Smoke (fast) gate vs full only
- Smoke ALWAYS set (gate_select.py:42): 3w, 3x, 3gd, 3dl (3qn quarantine check also appeared in all 32 smoke runs). About 45 slot-min over 5 days, 1 fail (3dl).
- Smoke also picks per changed file: pytest shards 4b/4c/4g/4h and 3xt, 3tl, 4d, 3tk, 3cx, 3lh, 3cr, 3dk (see smoke-run column). Smoke steps are capped at 240 s.
- Full only (0-3 smoke runs): 3k, 5b, 4f, 4, 3sig, 3ds, 3ad, 3bk, 3sg, 3gi, 3ms, 3g, 3lm, 4e, 1, 2, 5, 5c, 6 and the ~35 small unit steps (3b..3vd).
- CI runs everything behind each push, so full-only steps are duplicated there.

### Gate: cost high, catch ~0 (deletion / slim candidates)
- 4h (358 slot-min) and 3xt (269): the two biggest costs. 13 of 13 4h fails and 7 of 11 3xt fails are 240 s timeouts: they hang, they do not catch. The 4 other 3xt fails are 626-906 s full runs (slow, not shown to be real bugs).
- 3k sync.py parallel ship tests: 281 min, median 327 s, p90 912 s, 1 fail in 37 runs.
- 5b layer tests (127 min) and 4f layer+live-writer (127 min): 0 fails in 25 runs each. Live-path, so keep in CI, candidates to drop from the local full gate.
- 4 shard 1/5 (67 min), 3dk (48), 3ad (31), 3bk (28), 3sg (23): 0 fails each. 3sg and 3sig (80 min, 2 fails) test the hooks above; if a hook goes, its step goes (about 100 slot-min).
- 3ds (34 min, 1 fail), 3lh (35, 1 timeout), 3cx (37, 1 timeout), 3cr (24, 1 timeout): catches not distinguishable from timeouts.
- 4t precheck pytest: 153 min, 4 fails of 22, outlier runs to 2885 s (sha df3efd).

### Gate: catches real bugs (keep, unverified per-sha)
- 4d doc size/contract: 8 non-timeout fails in 63 runs (13%), cheap (median 16 s).
- 3tl task-card Definition of Ready: 4 non-timeout fails in 46 (9%), cheap (median 27 s).
- 4b (4 fails) and 4c (2 fails), non-timeout: pytest shards, real test failures likely.
- 3g, 3dl, 5c, 3ds, 3tk: one non-timeout fail each.
- ALWAYS set 3w/3x/3gd/3dl/3qn: 0.2-11 s each, 1 fail in about 195 runs; cheap insurance for known merge-time breaks.
- To confirm a fail is real, match the row's `sha` against a following commit that fixes the test; this audit did not do that.
