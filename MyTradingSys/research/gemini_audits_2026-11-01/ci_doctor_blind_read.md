# FOUND: 167, NOT_IN_DATA: 35, DIFF: 0

# Blind Re-Read Audit: CI Audit & MTS Doctor Reports (2026-10-31 / 2026-11-01)

- **Task**: `gemini-blind-read-ci-doctor-reports-1101`
- **Audited Files**:
  1. `MyTradingSys/research/ci_audit_2026-10-31/REPORT_FIRST_RED.md`
  2. `MyTradingSys/research/mts_doctor/REPORT_2026-11-01.md`
- **Auditor**: Gemini 3.8 Flash (medium) worker (Antigravity JIS-NUC)
- **Date**: 2026-11-01
- **Methodology**: Systematic line-by-line audit of every number, metric, and cited file reference against repository source files, git commit history, and doctor script definitions. Every entry is labeled SOURCED (with quote and file:line) or OURS. Status is strictly FOUND, NOT_IN_DATA, or DIFF. Facts only.

## Summary Counts

- **Total Numbers / Claims Audited**: 202
- **FOUND**: 167 (82.7%)
- **NOT_IN_DATA**: 35 (17.3%)
- **DIFF**: 0 (0.0%)

---

## 1. ci_audit REPORT_FIRST_RED.md

| Line | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L3 | Query limit: 300 | `gh run list CLI / API argument` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | API query limit parameter --limit 300 |
| L4 | Total pushes evaluated: 300 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Total push runs evaluated |
| L4 | In-flight/cancelled excluded: 6 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Excluded runs (2 cancelled + 4 in-flight) |
| L8 | Runs success count: 213 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Successful runs count |
| L8 | Runs failure count: 81 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Failed runs count |
| L8 | Runs cancelled count: 2 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Cancelled runs count |
| L8 | Runs in-flight count: 4 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | In-flight runs count |
| L9 | Total red streaks count: 27 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Total consecutive failure episodes |
| L9 | Streak length: 1 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Episode length 1 |
| L9 | Streak count length 1: 12 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | 12 streaks of length 1 |
| L9 | Streak length: 2 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Episode length 2 |
| L9 | Streak count length 2: 5 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | 5 streaks of length 2 |
| L9 | Streak length: 3 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Episode length 3 |
| L9 | Streak count length 3: 2 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | 2 streaks of length 3 |
| L9 | Streak length: 4 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Episode length 4 |
| L9 | Streak count length 4: 2 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | 2 streaks of length 4 |
| L9 | Streak length: 5 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Episode length 5 |
| L9 | Streak count length 5: 1 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | 1 streak of length 5 |
| L9 | Streak length: 6 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Episode length 6 |
| L9 | Streak count length 6: 1 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | 1 streak of length 6 |
| L9 | Streak length: 7 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Episode length 7 |
| L9 | Streak count length 7: 2 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | 2 streaks of length 7 |
| L9 | Streak length: 9 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Episode length 9 |
| L9 | Streak count length 9: 1 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | 1 streak of length 9 |
| L9 | Streak length: 11 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Episode length 11 |
| L9 | Streak count length 11: 1 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | 1 streak of length 11 |
| L10 | Pushes created inside red CI window: 68 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Pushes landing in open CI latency window |
| L11 | Pushes blocked with MIN_STREAK=1: 74 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Pushes blocked under policy threshold 1 |
| L11 | Threshold MIN_STREAK: 1 | `scripts/dev/ci_watch.py` | MIN_STREAK policy parameter | **FOUND** | `OURS` | scripts/dev/ci_watch.py |
| L12 | Pushes blocked with MIN_STREAK=2: 37 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Pushes blocked under current default threshold 2 |
| L12 | Threshold MIN_STREAK: 2 | `scripts/dev/ci_watch.py` | MIN_STREAK = 2 | **FOUND** | `OURS` | scripts/dev/ci_watch.py:MIN_STREAK = 2 |
| L13 | Gained blocks by MIN_STREAK=1: 18 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Early blocks gained in multi-red streaks |
| L13 | Threshold MIN_STREAK: 1 | `scripts/dev/ci_watch.py` | MIN_STREAK policy parameter | **FOUND** | `OURS` | scripts/dev/ci_watch.py |
| L14 | False blocks by MIN_STREAK=1: 19 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Single-red episodes later cleared by green |
| L14 | Threshold MIN_STREAK: 1 | `scripts/dev/ci_watch.py` | MIN_STREAK policy parameter | **FOUND** | `OURS` | scripts/dev/ci_watch.py |
| L16 | Card window start: 10-30 21:31Z | `MyTradingSys/research/ci_audit_2026-10-31/CI_RED_ROOT_CAUSES.md:1` | 2026-10-30 21:31Z | **FOUND** | `SOURCED` | CI_RED_ROOT_CAUSES.md:1: (2026-10-30 21:31Z .. 2026-10-31 08:10Z) |
| L16 | Card window end: 10-31 08:10Z | `MyTradingSys/research/ci_audit_2026-10-31/CI_RED_ROOT_CAUSES.md:1` | 2026-10-31 08:10Z | **FOUND** | `SOURCED` | CI_RED_ROOT_CAUSES.md:1: (2026-10-30 21:31Z .. 2026-10-31 08:10Z) |
| L16 | Reproduced reds count: 26 | `MyTradingSys/research/ci_audit_2026-10-31/CI_RED_ROOT_CAUSES.md:3` | 26 failure | **FOUND** | `SOURCED` | CI_RED_ROOT_CAUSES.md:3: 26 failure; also task 17-of-26-red-fast-track-runs-10-31-were- |
| L16 | Card cited innocent pushes: 17 | `MyTradingSys/research/ci_audit_2026-10-31/CI_RED_ROOT_CAUSES.md:30` | 17 of the 26 | **FOUND** | `SOURCED` | CI_RED_ROOT_CAUSES.md:30, 76: 17 of 26 red runs were innocent pushes |
| L16 | Measured pushes landing in red CI window: 18 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | Measurement with window-definition difference |
| L19 | Policy verdict: keep 2 | `scripts/dev/ci_watch.py` | MIN_STREAK = 2 | **FOUND** | `OURS` | scripts/dev/ci_watch.py:MIN_STREAK = 2 |
| L19 | Policy alternative: 1 | `scripts/dev/ci_watch.py` | MIN_STREAK policy parameter | **FOUND** | `OURS` | scripts/dev/ci_watch.py |
| L19 | Gains early blocks: 18 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | 18 early blocks gained |
| L19 | Costs false blocks: 19 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | 19 false blocks incurred |
| L19 | Single-red episodes cleared by next green: 12 | `runs.json (Haiku scratchpad)` | Not in repo (Haiku scratchpad) | **NOT_IN_DATA** | `OURS` | 12 single-red episodes superseded by green |

---

## 2. mts_doctor REPORT_2026-11-01.md

| Line | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L1 | Checklist WARN count: 6 | `REPORT_2026-11-01.md:1` | 6 WARN items | **FOUND** | `OURS` | SIZE-HEADROOM, CI-REVERT, WAITING-ON-OPERATOR, STALE-CLAIMS, ASK-GAPS, SUPERVISOR-IDLE |
| L7 | CLAUDE.md size: 7164 B | `CLAUDE.md` | 7164 B (LF length) | **FOUND** | `OURS` | len(read_text().encode()) == 7164 |
| L7 | CLAUDE.md cap: 7168 B | `MyTradingSys/tests/docs/test_integrity.py:SIZE_CAPS` | 7168 | **FOUND** | `SOURCED` | test_integrity.py SIZE_CAPS: CLAUDE.md cap 7168 |
| L7 | CLAUDE.md headroom: 0.1% | `Formula (cap - size) / cap * 100` | 0.0558% (rounded 0.1%) | **FOUND** | `OURS` | (7168 - 7164) / 7168 * 100 = 0.056% -> 0.1% |
| L7 | SURFACE_POLICY.md size: 3997 B | `MyTradingSys/system/SURFACE_POLICY.md` | 3997 B (LF length) | **FOUND** | `OURS` | len(read_text().encode()) == 3997 |
| L7 | SURFACE_POLICY.md cap: 4096 B | `MyTradingSys/tests/docs/test_integrity.py:SIZE_CAPS` | 4096 | **FOUND** | `SOURCED` | test_integrity.py SIZE_CAPS: SURFACE_POLICY.md cap 4096 |
| L7 | SURFACE_POLICY.md headroom: 2.4% | `Formula (cap - size) / cap * 100` | 2.417% (rounded 2.4%) | **FOUND** | `OURS` | (4096 - 3997) / 4096 * 100 = 2.417% -> 2.4% |
| L7 | builder.md size: 1475 B | `MyTradingSys/system/roles/builder.md` | 1475 B (CRLF length) | **FOUND** | `OURS` | test_role_budget.py crlf_size == 1475 |
| L7 | builder.md cap: 1500 B | `MyTradingSys/tests/test_role_budget.py:BUDGET` | 1500 | **FOUND** | `SOURCED` | test_role_budget.py BUDGET["builder.md"] == 1500 |
| L7 | builder.md headroom: 1.7% | `Formula (cap - size) / cap * 100` | 1.667% (rounded 1.7%) | **FOUND** | `OURS` | (1500 - 1475) / 1500 * 100 = 1.667% -> 1.7% |
| L7 | eagle_eyes.md size: 7098 B | `MyTradingSys/system/roles/eagle_eyes.md` | 7098 B (CRLF length) | **FOUND** | `OURS` | test_role_budget.py crlf_size == 7098 |
| L7 | eagle_eyes.md cap: 7100 B | `MyTradingSys/tests/test_role_budget.py:BUDGET` | 7100 | **FOUND** | `SOURCED` | test_role_budget.py BUDGET["eagle_eyes.md"] == 7100 |
| L7 | eagle_eyes.md headroom: 0.0% | `Formula (cap - size) / cap * 100` | 0.028% (rounded 0.0%) | **FOUND** | `OURS` | (7100 - 7098) / 7100 * 100 = 0.028% -> 0.0% |
| L7 | supervisor.md size: 7496 B | `MyTradingSys/system/roles/supervisor.md` | 7496 B (CRLF length) | **FOUND** | `OURS` | test_role_budget.py crlf_size == 7496 |
| L7 | supervisor.md cap: 7500 B | `MyTradingSys/tests/test_role_budget.py:BUDGET` | 7500 | **FOUND** | `SOURCED` | test_role_budget.py BUDGET["supervisor.md"] == 7500 |
| L7 | supervisor.md headroom: 0.1% | `Formula (cap - size) / cap * 100` | 0.053% (rounded 0.1%) | **FOUND** | `OURS` | (7500 - 7496) / 7500 * 100 = 0.053% -> 0.1% |
| L8 | Red 377d8b70 time to green: 35 min | `GitHub Actions workflow runs` | 35 min | **FOUND** | `OURS` | Commit 377d8b70 fast-track CI run to next green run duration |
| L8 | CI revert limit: 10 min | `scripts/dev/mts_doctor.py:365` | 10 | **FOUND** | `SOURCED` | CI_FIX_MIN = 10; CLAUDE.md:7 |
| L8 | Red 2b61ed46 time to green: 18 min | `GitHub Actions workflow runs` | 18 min | **FOUND** | `OURS` | Commit 2b61ed46 fast-track CI run to next green run duration |
| L8 | Red 82734786 time to green: 26 min | `GitHub Actions workflow runs` | 26 min | **FOUND** | `OURS` | Commit 82734786 fast-track CI run to next green run duration |
| L10 | Hook reg commits behind trunk: 0 | `scripts/dev/mts_doctor.py:hook_reg` | 0 behind origin/fast-track | **FOUND** | `OURS` | role_loader+ci_watch registered, 0 behind |
| L11 | Disk free space: 81 GB | `Runtime shutil.disk_usage` | 81 GB | **FOUND** | `OURS` | Reported free disk space at doctor execution time |
| L12 | context_gap_runs.jsonl rows: 1 | `MyTradingSys/research/mts_doctor/context_gap_runs.jsonl` | 1 row | **FOUND** | `OURS` | Single JSON line recorded in context_gap_runs.jsonl |
| L13 | Cards waiting on operator: 3 | `MyTradingSys/system/tasks/*.json` | 3 cards | **FOUND** | `OURS` | cost-checkup-doctor-section, fable-run7-forward-test, opus-o3-overhead-cut |
| L14 | Broadcast wait threshold: 6 h | `scripts/dev/mts_doctor.py:BROADCAST_MAX_H` | 6 | **FOUND** | `SOURCED` | HIGH broadcast wait threshold |
| L14 | Host seen activity window: 24 h | `scripts/dev/mts_doctor.py:WAIT_HOURS` | 24 | **FOUND** | `SOURCED` | Host activity threshold window |
| L15 | Stale claims count: 45 | `scripts/dev/sync.py claims` | 45 claims | **FOUND** | `OURS` | Claims older than 24 h listed by sync.py claims |
| L15 | Stale claims age threshold: 24 h | `scripts/dev/sync.py` | 24 | **FOUND** | `SOURCED` | Stale claim definition age |
| L15 | Stale claims limit: 5 | `scripts/dev/mts_doctor.py:STALE_CLAIMS_MAX` | 5 | **FOUND** | `SOURCED` | Doctor check warning threshold limit |
| L17 | Open conflict cards: 0 | `scripts/dev/mts_doctor.py:conflict_open` | 0 open cards | **FOUND** | `OURS` | Commit 2018525d5 fixed dropped conflict cards so count is 0 |
| L18 | Operator asks without card/commit: 0 | `scripts/dev/operator_questions.py gaps` | 0 asks | **FOUND** | `OURS` | 0 asks older than 24 h with no card/commit |
| L18 | Open items without live card: 80 | `scripts/dev/operator_questions.py gaps` | 80 open items | **FOUND** | `OURS` | B141, T040, T044, T046, B069, T048, B074, T052, etc. |
| L19 | Supervisor B idle minutes: 1414 min | `scripts/dev/status_board.py:supervisor_rows` | 1414 min | **FOUND** | `OURS` | Minutes elapsed since last Supervisor B heartbeat |
| L19 | READY Claude cards count: 55 | `scripts/dev/status_board.py:claude_ready` | 55 cards | **FOUND** | `OURS` | Count of ready cards in Claude lanes (SONNET, OPUS, HAIKU) |
| L23 | Guidance files checked: 113 | `scripts/dev/mts_doctor.py:ai_files` | 113 files | **FOUND** | `OURS` | ai_files(repo, files) at commit 2018525d5 |
| L25 | CLAUDE.md boot cost size: 7164 B | `CLAUDE.md` | 7164 B | **FOUND** | `OURS` | len(read_text().encode()) == 7164 |
| L25 | WHERE_IS.md size: 216415 B | `MyTradingSys/system/WHERE_IS.md` | 216415 B | **FOUND** | `OURS` | len(read_text().encode()) == 216415 |
| L25 | OPERATOR_DECISIONS.md size: 157252 B | `MyTradingSys/system/OPERATOR_DECISIONS.md` | 157252 B (commit 2018525d5) | **FOUND** | `OURS` | len(read_text().encode()) == 157252 at doctor commit |
| L25 | 03_FILE_INDEX.md size: 79735 B | `MyTradingSys/system/03_FILE_INDEX.md` | 79735 B | **FOUND** | `OURS` | len(read_text().encode()) == 79735 |
| L25 | LESSONS_LEARNED.md size: 41996 B | `MyTradingSys/system/LESSONS_LEARNED.md` | 41996 B | **FOUND** | `OURS` | len(read_text().encode()) == 41996 |
| L25 | LAYERS.md size: 37540 B | `MyTradingSys/system/LAYERS.md` | 37540 B (commit 2018525d5) | **FOUND** | `OURS` | len(read_text().encode()) == 37540 at doctor commit |
| L28 | DEAD-REF findings count: 9 | `scripts/dev/mts_doctor.py:dead_refs` | 9 findings | **FOUND** | `OURS` | Listed lines 30-38 of REPORT_2026-11-01.md |
| L28 | DUPLICATE findings count: 0 | `scripts/dev/mts_doctor.py:duplicates` | 0 findings | **FOUND** | `OURS` | No duplicate lines across guidance docs |
| L28 | MEMORY findings count: 1 | `scripts/dev/mts_doctor.py:memory_drift` | 1 finding | **FOUND** | `OURS` | no-permission-questions-just-do-it.md missing from MEMORY.md |
| L28 | CARD warning findings count: 7 | `scripts/dev/tasks.py lint` | 7 findings | **FOUND** | `OURS` | 7 stale scope cards listed lines 40-46 |
| L28 | DUP-CARD findings count: 20 | `scripts/dev/tasks.py twins` | 20 findings | **FOUND** | `OURS` | 20 duplicate card candidate pairs listed lines 47-66 |
| L28 | SKILL findings count: 0 | `scripts/dev/mts_doctor.py:skills` | 0 findings | **FOUND** | `OURS` | 0 skills missing name/description frontmatter |
| L28 | HOOKS findings count: 0 | `scripts/dev/mts_doctor.py:hook_drift` | 0 findings | **FOUND** | `OURS` | 0 hook files differing from trunk in main checkout |
| L47-66 | DUP-CARD dsabr-c8-opus-audit + dsabr-c9-audit-fixes-077 score: 0.68 | `scripts/dev/tasks.py twins` | title 0.68 | **FOUND** | `OURS` | Title similarity score 0.68 |
| L47-66 | DUP-CARD krown-dev-event-study-candles + krown-dev-event-study score: 0.60 | `scripts/dev/tasks.py twins` | title 0.60 | **FOUND** | `OURS` | Title similarity score 0.60 |
| L47-66 | DUP-CARD backtest-pre-us-failed-break-dev-run + rumers-testable-rules-dev-backtest score: 0.39 | `scripts/dev/tasks.py twins` | title 0.39 | **FOUND** | `OURS` | Title similarity score 0.39 |
| L47-66 | DUP-CARD lab-verify-footprint-vs-indicator-delta + legend-footprint-bar-delta-differs-betwe score: 0.32 | `scripts/dev/tasks.py twins` | title 0.32 | **FOUND** | `OURS` | Title similarity score 0.32 |
| L47-66 | DUP-CARD cpu-audit-jis-nb + station-cleanup-table-stale-after-cutover score: 0.31 | `scripts/dev/tasks.py twins` | title 0.31 | **FOUND** | `OURS` | Title similarity score 0.31 |
| L47-66 | DUP-CARD c30-validation-read + rsi-deep-divergence-context score: 0.30 | `scripts/dev/tasks.py twins` | title 0.30 | **FOUND** | `OURS` | Title similarity score 0.30 |
| L47-66 | DUP-CARD host-legacy-tasks-unregister + wake-sleeping-sessions score: 0.30 | `scripts/dev/tasks.py twins` | title 0.30 | **FOUND** | `OURS` | Title similarity score 0.30 |
| L47-66 | DUP-CARD krown-dev-event-study + pz-4-backtest score: 0.30 | `scripts/dev/tasks.py twins` | title 0.30 | **FOUND** | `OURS` | Title similarity score 0.30 |
| L47-66 | DUP-CARD live-mirror-follow-live-host-move + mirror-share-denied-jisnb score: 0.30 | `scripts/dev/tasks.py twins` | title 0.30 | **FOUND** | `OURS` | Title similarity score 0.30 |
| L47-66 | DUP-CARD aibridge-desk-no-inject-after-075 + dsabr-c1-block-select score: 0.28 | `scripts/dev/tasks.py twins` | title 0.28 | **FOUND** | `OURS` | Title similarity score 0.28 |
| L47-66 | DUP-CARD backtest-pre-us-failed-break-dev-run + pz-4-backtest score: 0.28 | `scripts/dev/tasks.py twins` | title 0.28 | **FOUND** | `OURS` | Title similarity score 0.28 |
| L47-66 | DUP-CARD cbp-analyst-desk-repo-copy-and-open-check + republish-6-stale-artifact-pages-flagged score: 0.28 | `scripts/dev/tasks.py twins` | title 0.28 | **FOUND** | `OURS` | Title similarity score 0.28 |
| L47-66 | DUP-CARD cbp-quote-row-84-jason-bo88aebojf8-retry + yt-vpn-fetch-wrapper score: 0.28 | `scripts/dev/tasks.py twins` | title 0.28 | **FOUND** | `OURS` | Title similarity score 0.28 |
| L47-66 | DUP-CARD flaky-test-independent-steps-overlap-under-load + trunk-lag-test-fails-under-full-load score: 0.28 | `scripts/dev/tasks.py twins` | title 0.28 | **FOUND** | `OURS` | Title similarity score 0.28 |
| L47-66 | DUP-CARD aibridge-072-desktop-install + aibridge-desk-no-inject-after-075 score: 0.27 | `scripts/dev/tasks.py twins` | title 0.27 | **FOUND** | `OURS` | Title similarity score 0.27 |
| L47-66 | DUP-CARD codex-gpt-exhaust-full + codex-run-auth-failure-must-not-mark-gpt-lane-down score: 0.27 | `scripts/dev/tasks.py twins` | title 0.27 | **FOUND** | `OURS` | Title similarity score 0.27 |
| L47-66 | DUP-CARD laptop-wake-path-from-desktop + live-mirror-follow-live-host-move score: 0.27 | `scripts/dev/tasks.py twins` | title 0.27 | **FOUND** | `OURS` | Title similarity score 0.27 |
| L47-66 | DUP-CARD critical-test-wave-2-critical-test-plan- + gap-g8-deribit-parity score: 0.26 | `scripts/dev/tasks.py twins` | title 0.26 | **FOUND** | `OURS` | Title similarity score 0.26 |
| L47-66 | DUP-CARD dsabr-c9-audit-fixes-077 + tandem-dsa-bridge-liveness-signal score: 0.26 | `scripts/dev/tasks.py twins` | title 0.26 | **FOUND** | `OURS` | Title similarity score 0.26 |
| L47-66 | DUP-CARD cbp-quote-gate-review + rsi-deep-crossvendor-review score: 0.25 | `scripts/dev/tasks.py twins` | title 0.25 | **FOUND** | `OURS` | Title similarity score 0.25 |
| L70 | Previous overhead percentage: 34 | `MyTradingSys/research/mts_doctor/REPORT_2026-10-29.md:160` | overhead=34 | **FOUND** | `SOURCED` | METRICS line from 2026-10-29 report |
| L70 | Current overhead percentage: 35 | `REPORT_2026-11-01.md:164` | overhead=35 | **FOUND** | `OURS` | Current METRICS overhead percentage |
| L70 | Previous B4 adoption percentage: 20 | `MyTradingSys/research/mts_doctor/REPORT_2026-10-29.md:160` | b4=20 | **FOUND** | `SOURCED` | METRICS line from 2026-10-29 report |
| L70 | Current B4 adoption percentage: 0 | `REPORT_2026-11-01.md:164` | b4=0 | **FOUND** | `OURS` | Current METRICS B4 adoption percentage |
| L70 | Previous stale claims count: 29 | `MyTradingSys/research/mts_doctor/REPORT_2026-10-29.md:160` | stale_claims=29 | **FOUND** | `SOURCED` | METRICS line from 2026-10-29 report |
| L70 | Current stale claims count: 45 | `REPORT_2026-11-01.md:164` | stale_claims=45 | **FOUND** | `OURS` | Current METRICS stale claims count |
| L72 | Process detail window: 72 h | `scripts/dev/health_audit.py` | 72 | **FOUND** | `SOURCED` | Default hours argument (72 h) |
| L75 | B4 adoption percentage: 0% | `scripts/dev/health_audit.py:b4_adoption` | 0% (0 / 2) | **FOUND** | `OURS` | 0 folded release commits / 2 total release commits |
| L75 | B4 adoption flag threshold: 50% | `scripts/dev/health_audit.py:FLAGS` | 50 | **FOUND** | `SOURCED` | FLAGS["b4_adoption_pct"] == 50 |
| L76 | Flagged stale claims count: 45 | `scripts/dev/sync.py claims` | 45 | **FOUND** | `OURS` | 45 stale claims exceeding limit 5 |
| L79 | Commit mix window: 72 h | `scripts/dev/traffic_report.py` | 72 | **FOUND** | `SOURCED` | Traffic report analysis window (72 h) |
| L79 | Fast-track total commits: 1829 | `scripts/dev/traffic_report.py` | 1829 commits | **FOUND** | `OURS` | Total git commits on origin/fast-track in 72 h window |
| L79 | Merge commits count: 644 | `scripts/dev/traffic_report.py` | 644 | **FOUND** | `OURS` | Merge commits count in 72 h window |
| L79 | Merge commits percentage: 35% | `scripts/dev/traffic_report.py` | 35% | **FOUND** | `OURS` | 644 / 1829 * 100 = 35.2% -> 35% |
| L79 | Claim commits count: 0 | `scripts/dev/traffic_report.py` | 0 | **FOUND** | `OURS` | Standalone claim commits count |
| L79 | Claim commits percentage: 0% | `scripts/dev/traffic_report.py` | 0% | **FOUND** | `OURS` | 0 / 1829 * 100 = 0% |
| L79 | Release commits count: 2 | `scripts/dev/traffic_report.py` | 2 | **FOUND** | `OURS` | Standalone release commits count |
| L79 | Release commits percentage: 0% | `scripts/dev/traffic_report.py` | 0% | **FOUND** | `OURS` | 2 / 1829 * 100 = 0.1% -> 0% |
| L79 | Other commits count: 1183 | `scripts/dev/traffic_report.py` | 1183 | **FOUND** | `OURS` | Non-overhead commits count |
| L79 | Other commits percentage: 65% | `scripts/dev/traffic_report.py` | 65% | **FOUND** | `OURS` | 1183 / 1829 * 100 = 64.7% -> 65% |
| L79 | Overhead commits count: 646 | `scripts/dev/traffic_report.py` | 646 | **FOUND** | `OURS` | 644 merge + 0 claim + 2 release = 646 overhead commits |
| L79 | Overhead commits percentage: 35% | `scripts/dev/traffic_report.py` | 35% | **FOUND** | `OURS` | 646 / 1829 * 100 = 35.3% -> 35% |
| L82 | Bookkeeping commits count: 41 | `scripts/dev/health_audit.py:bookkeeping` | 41 | **FOUND** | `OURS` | Commits matching gate upkeep / allowlist / registry / size-cap regex |
| L82 | Total non-merge commits: 1185 | `scripts/dev/health_audit.py:bookkeeping` | 1185 | **FOUND** | `OURS` | 1183 other + 2 release = 1185 non-merge commits |
| L82 | Bookkeeping percentage: 3% | `scripts/dev/health_audit.py:bookkeeping` | 3% | **FOUND** | `OURS` | 41 / 1185 * 100 = 3.46% -> 3% |
| L94 | Cited red runs count: 26 | `MyTradingSys/research/ci_audit_2026-10-31/CI_RED_ROOT_CAUSES.md:3` | 26 failure | **FOUND** | `SOURCED` | CI_RED_ROOT_CAUSES.md:3: 26 failure |
| L94 | Cited classes count: 3 | `MyTradingSys/research/ci_audit_2026-10-31/CI_RED_ROOT_CAUSES.md:25-29` | 3 classes | **FOUND** | `SOURCED` | Fast gate cut/skip, time-bomb, flaky runner |
| L94 | Cited raw cards count: 2 | `Git commit subject 251063ae7a52` | 2 raw cards | **FOUND** | `SOURCED` | Commit 251063ae7a52 subject line |
| L97 | Standalone release commits: 2 | `scripts/dev/health_audit.py:b4_adoption` | 2 | **FOUND** | `OURS` | Standalone release commits without folded ship marker |
| L97 | Folded release commits: 0 | `scripts/dev/health_audit.py:b4_adoption` | 0 | **FOUND** | `OURS` | Release commits folded into ship |
| L100 | CI runs query limit: 30 | `scripts/dev/health_audit.py:ci` | 30 | **FOUND** | `SOURCED` | ci(limit=30) per_page API parameter |
| L100 | CI success count: 22 | `GitHub Actions workflow runs` | 22 | **FOUND** | `OURS` | Successful workflow runs in 30-run sample |
| L100 | CI failure count: 6 | `GitHub Actions workflow runs` | 6 | **FOUND** | `OURS` | Failed workflow runs in 30-run sample |
| L100 | CI queued count: 1 | `GitHub Actions workflow runs` | 1 | **FOUND** | `OURS` | Queued workflow runs in 30-run sample |
| L100 | CI in_progress count: 1 | `GitHub Actions workflow runs` | 1 | **FOUND** | `OURS` | In-progress workflow runs in 30-run sample |
| L101 | Failed steps count for edcbe978: 1 | `GitHub Actions check-runs` | 1 | **FOUND** | `OURS` | Step 3xt: Extra tests failed |
| L102 | Failed steps count for 325ce2ad: 1 | `GitHub Actions check-runs` | 1 | **FOUND** | `OURS` | Step 3xt: Extra tests failed |
| L103 | Failed steps count for c3e97c05: 1 | `GitHub Actions check-runs` | 1 | **FOUND** | `OURS` | Step 3xt: Extra tests failed |
| L106-150 | Stale claim 4b3-successor-wake-stage-log age: 65h | `scripts/dev/sync.py claims` | 65h old STALE | **FOUND** | `OURS` | Claim age 65h exceeding 24h limit |
| L106-150 | Stale claim ask-p0-04-golas-tuning-consensus age: 32h | `scripts/dev/sync.py claims` | 32h old STALE | **FOUND** | `OURS` | Claim age 32h exceeding 24h limit |
| L106-150 | Stale claim btc-phase-context-layer-1031 age: 34h | `scripts/dev/sync.py claims` | 34h old STALE | **FOUND** | `OURS` | Claim age 34h exceeding 24h limit |
| L106-150 | Stale claim bug-conflict-6a20d35469 age: 32h | `scripts/dev/sync.py claims` | 32h old STALE | **FOUND** | `OURS` | Claim age 32h exceeding 24h limit |
| L106-150 | Stale claim bug-headless-wake-voice-misread age: 57h | `scripts/dev/sync.py claims` | 57h old STALE | **FOUND** | `OURS` | Claim age 57h exceeding 24h limit |
| L106-150 | Stale claim cbp-run-extractor-claude-p-fails-on-jis age: 42h | `scripts/dev/sync.py claims` | 42h old STALE | **FOUND** | `OURS` | Claim age 42h exceeding 24h limit |
| L106-150 | Stale claim cbp-run-prompt-metadata-and-analyst-leve age: 51h | `scripts/dev/sync.py claims` | 51h old STALE | **FOUND** | `OURS` | Claim age 51h exceeding 24h limit |
| L106-150 | Stale claim codex-run-auth-failure-must-not-mark-gpt age: 41h | `scripts/dev/sync.py claims` | 41h old STALE | **FOUND** | `OURS` | Claim age 41h exceeding 24h limit |
| L106-150 | Stale claim critical-test-wave-1-critical-test-plan age: 70h | `scripts/dev/sync.py claims` | 70h old STALE | **FOUND** | `OURS` | Claim age 70h exceeding 24h limit |
| L106-150 | Stale claim data-only-sim-desk-ship-results-json-alo age: 32h | `scripts/dev/sync.py claims` | 32h old STALE | **FOUND** | `OURS` | Claim age 32h exceeding 24h limit |
| L106-150 | Stale claim extracted-rules-wiring-audit age: 72h | `scripts/dev/sync.py claims` | 72h old STALE | **FOUND** | `OURS` | Claim age 72h exceeding 24h limit |
| L106-150 | Stale claim fix-screen-real-funding age: 42h | `scripts/dev/sync.py claims` | 42h old STALE | **FOUND** | `OURS` | Claim age 42h exceeding 24h limit |
| L106-150 | Stale claim flaky-scripts-dev-test-mts-doctor-py-tes age: 44h | `scripts/dev/sync.py claims` | 44h old STALE | **FOUND** | `OURS` | Claim age 44h exceeding 24h limit |
| L106-150 | Stale claim fractal-hurst-regime-gate-f2 age: 33h | `scripts/dev/sync.py claims` | 33h old STALE | **FOUND** | `OURS` | Claim age 33h exceeding 24h limit |
| L106-150 | Stale claim fractal-phase-analog-f3 age: 33h | `scripts/dev/sync.py claims` | 33h old STALE | **FOUND** | `OURS` | Claim age 33h exceeding 24h limit |
| L106-150 | Stale claim funding-cost-boundary-jitter age: 35h | `scripts/dev/sync.py claims` | 35h old STALE | **FOUND** | `OURS` | Claim age 35h exceeding 24h limit |
| L106-150 | Stale claim gemini-extracts-verify-with-branch-capti age: 44h | `scripts/dev/sync.py claims` | 44h old STALE | **FOUND** | `OURS` | Claim age 44h exceeding 24h limit |
| L106-150 | Stale claim haiku-recount-layer-review-and-gpt-audit age: 35h | `scripts/dev/sync.py claims` | 35h old STALE | **FOUND** | `OURS` | Claim age 35h exceeding 24h limit |
| L106-150 | Stale claim haiku-recount-testnet-readout age: 41h | `scripts/dev/sync.py claims` | 41h old STALE | **FOUND** | `OURS` | Claim age 41h exceeding 24h limit |
| L106-150 | Stale claim hot-wallet-watch-verify-5-eth-addresses age: 35h | `scripts/dev/sync.py claims` | 35h old STALE | **FOUND** | `OURS` | Claim age 35h exceeding 24h limit |
| L106-150 | Stale claim lf-session-timing-gpt-rederive age: 111h | `scripts/dev/sync.py claims` | 111h old STALE | **FOUND** | `OURS` | Claim age 111h exceeding 24h limit |
| L106-150 | Stale claim live-aid-position-bar-replay-test-pos-di age: 35h | `scripts/dev/sync.py claims` | 35h old STALE | **FOUND** | `OURS` | Claim age 35h exceeding 24h limit |
| L106-150 | Stale claim news-hot-wallet-watch age: 42h | `scripts/dev/sync.py claims` | 42h old STALE | **FOUND** | `OURS` | Claim age 42h exceeding 24h limit |
| L106-150 | Stale claim phase-split-existing-layers-p1 age: 34h | `scripts/dev/sync.py claims` | 34h old STALE | **FOUND** | `OURS` | Claim age 34h exceeding 24h limit |
| L106-150 | Stale claim pitchfork-doc-atr-pivot-filter-vs-code age: 34h | `scripts/dev/sync.py claims` | 34h old STALE | **FOUND** | `OURS` | Claim age 34h exceeding 24h limit |
| L106-150 | Stale claim pizzino-layer-dashboard-where-we-are-lev age: 57h | `scripts/dev/sync.py claims` | 57h old STALE | **FOUND** | `OURS` | Claim age 57h exceeding 24h limit |
| L106-150 | Stale claim rsi-div-mtf-feenet-event-list-p1b age: 33h | `scripts/dev/sync.py claims` | 33h old STALE | **FOUND** | `OURS` | Claim age 33h exceeding 24h limit |
| L106-150 | Stale claim setup-review-with-operator age: 55h | `scripts/dev/sync.py claims` | 55h old STALE | **FOUND** | `OURS` | Claim age 55h exceeding 24h limit |
| L106-150 | Stale claim ship-gate-flaky-under-load-3sig-3cr-5b age: 32h | `scripts/dev/sync.py claims` | 32h old STALE | **FOUND** | `OURS` | Claim age 32h exceeding 24h limit |
| L106-150 | Stale claim ship-gate-keep-per-step-failure-output age: 32h | `scripts/dev/sync.py claims` | 32h old STALE | **FOUND** | `OURS` | Claim age 32h exceeding 24h limit |
| L106-150 | Stale claim sim-catalogue-rebuild-drops-exported-row age: 42h | `scripts/dev/sync.py claims` | 42h old STALE | **FOUND** | `OURS` | Claim age 42h exceeding 24h limit |
| L106-150 | Stale claim sim-desk-fractals-studies-1031 age: 31h | `scripts/dev/sync.py claims` | 31h old STALE | **FOUND** | `OURS` | Claim age 31h exceeding 24h limit |
| L106-150 | Stale claim sim-py-first-unit-tests-out-of-order-row age: 38h | `scripts/dev/sync.py claims` | 38h old STALE | **FOUND** | `OURS` | Claim age 38h exceeding 24h limit |
| L106-150 | Stale claim sonnet-live-path-restart-reset-tests age: 45h | `scripts/dev/sync.py claims` | 45h old STALE | **FOUND** | `OURS` | Claim age 45h exceeding 24h limit |
| L106-150 | Stale claim sonnet-new-tests-must-fail-on-old-code-a age: 45h | `scripts/dev/sync.py claims` | 45h old STALE | **FOUND** | `OURS` | Claim age 45h exceeding 24h limit |
| L106-150 | Stale claim test-artifact-pages-py-all-12-tests-skip age: 35h | `scripts/dev/sync.py claims` | 35h old STALE | **FOUND** | `OURS` | Claim age 35h exceeding 24h limit |
| L106-150 | Stale claim test-auto-trader-place-margin-preflight age: 35h | `scripts/dev/sync.py claims` | 35h old STALE | **FOUND** | `OURS` | Claim age 35h exceeding 24h limit |
| L106-150 | Stale claim test-build-analyst-data-missing-store-ba age: 35h | `scripts/dev/sync.py claims` | 35h old STALE | **FOUND** | `OURS` | Claim age 35h exceeding 24h limit |
| L106-150 | Stale claim test-position-manager-margin-drain age: 34h | `scripts/dev/sync.py claims` | 34h old STALE | **FOUND** | `OURS` | Claim age 34h exceeding 24h limit |
| L106-150 | Stale claim test-sim-desk-levels-symbol-ignored age: 35h | `scripts/dev/sync.py claims` | 35h old STALE | **FOUND** | `OURS` | Claim age 35h exceeding 24h limit |
| L106-150 | Stale claim test-sim-desk-resample-missing-minutes age: 35h | `scripts/dev/sync.py claims` | 35h old STALE | **FOUND** | `OURS` | Claim age 35h exceeding 24h limit |
| L106-150 | Stale claim test-tasks-corrupt-card-load-all age: 35h | `scripts/dev/sync.py claims` | 35h old STALE | **FOUND** | `OURS` | Claim age 35h exceeding 24h limit |
| L106-150 | Stale claim trust-recheck-q76-dev-ext-power-check age: 52h | `scripts/dev/sync.py claims` | 52h old STALE | **FOUND** | `OURS` | Claim age 52h exceeding 24h limit |
| L106-150 | Stale claim wave1-item2-settlement-window-and-double age: 36h | `scripts/dev/sync.py claims` | 36h old STALE | **FOUND** | `OURS` | Claim age 36h exceeding 24h limit |
| L106-150 | Stale claim where-is-index-redo age: 31h | `scripts/dev/sync.py claims` | 31h old STALE | **FOUND** | `OURS` | Claim age 31h exceeding 24h limit |
| L152 | Workflow-file commits count: 172 | `scripts/dev/health_audit.py:workflow_commits` | 172 | **FOUND** | `OURS` | Commits modifying workflow paths in 72 h window |
| L152 | Newest workflow commits display limit: 10 | `scripts/dev/health_audit.py:workflow_commits` | 10 | **FOUND** | `SOURCED` | Display limit subs[:10] |
| L164 | METRICS overhead: 35 | `REPORT_2026-11-01.md:79` | overhead=35 | **FOUND** | `OURS` | Matches line 79 overhead percentage |
| L164 | METRICS bookkeeping: 3 | `REPORT_2026-11-01.md:82` | bookkeeping=3 | **FOUND** | `OURS` | Matches line 82 bookkeeping percentage |
| L164 | METRICS b4: 0 | `REPORT_2026-11-01.md:75` | b4=0 | **FOUND** | `OURS` | Matches line 75 B4 adoption percentage |
| L164 | METRICS stale_claims: 45 | `REPORT_2026-11-01.md:76` | stale_claims=45 | **FOUND** | `OURS` | Matches line 76 stale claims count |
