# Inventory: scripts/dev and bug origins (14 days to 2026-10-24, trunk origin/fast-track d1513184d)

Method: Python scripts in the scratchpad (inv_a2.py, inv_a3.py, inv_b1.py, inv_b3.py, inv_b4.py). Repo untouched.
Churn = commits on origin/fast-track since 2026-10-10 that touch the file (git log --name-only, no merges counted twice).
Callers = files (tree at origin/fast-track, checked out copy) that name the script as `stem.py`, `import stem` or `from stem` and are not test_ files:
  S=other scripts/dev, H=.claude hook or .github workflow, C=other code (execution, research, scripts/*), D=system docs + CLAUDE.md, O=other .md. Archive and planted-lab paths excluded.
Caveat: callers built at run time (f-strings, config lists, subprocess of a name read from JSON) are not seen; read 'orphan' as 'no static caller'.

## Part A numbers
- scripts/dev .py: 201 = 111 non-test + 90 test_. Non-test churn total 660 file-touches; test_ files add 382 more.
- 818 commits touched scripts/dev in 14 days (out of 3678 non-merge commits on trunk; 5363 with merges).
- Hot 15 files hold 429 of 660 file-touches (65 percent). Top 3: run_extra_tests.py 92, run_all_tests.py 68, tasks.py 41.
- (a) True orphans (no static caller anywhere, not even a doc): 0. Scripts with no live caller (only docs): 15 (list below).
- No test file at all (no test_<name>.py and no test mentions the name): 22 of 111. Only indirectly mentioned by some test: 15.
- Hot-15 with a direct test_<name>.py: 12 of 15.

## (b) The 15 hot files
| # | script | lines | churn | S | H | C | D+O docs | test |
|---|---|---|---|---|---|---|---|---|
| 1 | run_extra_tests.py | 221 | 92 | 2 | 0 | 9 | 36 | direct |
| 2 | run_all_tests.py | 1255 | 68 | 10 | 1 | 29 | 107 | direct |
| 3 | tasks.py | 1578 | 41 | 23 | 0 | 80 | 148 | direct |
| 4 | codex_run.py | 1080 | 39 | 7 | 0 | 16 | 45 | direct |
| 5 | sync.py | 1476 | 35 | 31 | 0 | 70 | 157 | direct |
| 6 | turn_meter.py | 485 | 23 | 3 | 1 | 6 | 30 | indirect |
| 7 | mts_signal.py | 930 | 19 | 3 | 1 | 8 | 30 | direct |
| 8 | role_loader.py | 1031 | 18 | 4 | 1 | 14 | 19 | indirect |
| 9 | lab_flow.py | 405 | 16 | 2 | 0 | 6 | 31 | direct |
| 10 | model_guard.py | 599 | 16 | 1 | 1 | 6 | 15 | indirect |
| 11 | supervisor.py | 1281 | 15 | 3 | 0 | 9 | 20 | direct |
| 12 | auto_deploy.py | 576 | 14 | 1 | 0 | 6 | 9 | direct |
| 13 | make_status.py | 519 | 12 | 5 | 0 | 13 | 18 | direct |
| 14 | shot.py | 1142 | 12 | 1 | 1 | 12 | 43 | direct |
| 15 | gate_select.py | 262 | 9 | 2 | 0 | 2 | 6 | direct |

## (c) Scripts whose only caller is a doc (no script, hook, workflow or code caller)
| script | lines | churn | doc callers | test |
|---|---|---|---|---|
| relay_board.py | 205 | 4 | 3 (MyTradingSys/system/CONTROL_ROOM.md) | direct |
| soak_six_slots.py | 438 | 2 | 1 (MyTradingSys/research/thinker/2026-10-22_six_slots.md) | direct |
| config_check.py | 57 | 1 | 1 (MyTradingSys/system/GATE_SPEED.md) | direct |
| deploy_untrack_backup.py | 201 | 1 | 1 (MyTradingSys/system/DEPLOY_RUNBOOK.md) | none |
| gq_after_reset.py | 9 | 1 | 2 (MyTradingSys/system/handoff_history/2026-10-21_next_session_trim.md, MyTradingSys/research/mts_doctor/REPORT_2026-10-18.md) | none |
| indicator_audit_sample.py | 143 | 1 | 2 (MyTradingSys/research/indicator_audit_2026-10-14/AUDIT.md) | indirect |
| interview_feed.py | 126 | 1 | 2 (MyTradingSys/system/QUICK_ANSWERS.md) | direct |
| lab_query.py | 162 | 1 | 1 (MyTradingSys/system/GEMINI_START.md) | direct |
| research_kit_lint.py | 90 | 1 | 2 (MyTradingSys/system/QUICK_ANSWERS.md) | direct |
| task_state.py | 172 | 1 | 2 (MyTradingSys/system/TASK_REFINEMENT.md, MyTradingSys/research/BACKLOG_REFINEMENT_GAPS_2026-10-18.md) | indirect |
| traffic_report.py | 38 | 1 | 6 (MyTradingSys/system/DEBUGGING.md, MyTradingSys/research/v1_plan_2026-10-20/D8_OPERATIONS.md) | none |
| wait_pid.py | 17 | 1 | 2 (MyTradingSys/system/handoff_history/2026-10-21_next_session_trim.md, MyTradingSys/research/mts_doctor/REPORT_2026-10-18.md) | none |
| worker_cost_report.py | 162 | 1 | 4 (MyTradingSys/system/DEBUGGING.md) | none |
| wt_maint.py | 307 | 1 | 2 (MyTradingSys/system/DEVICES.md) | direct |
| funnel_report.py | 146 | 0 | 5 (MyTradingSys/system/03_FILE_INDEX.md, MyTradingSys/research/CC_TASK_LIST_2026-10-03.md) | direct |
Of these 15, 5 have no test at all: deploy_untrack_backup, gq_after_reset, traffic_report, wait_pid, worker_cost_report.

## Full table, sorted by churn (all 111 non-test scripts)
cols: script | lines | churn | S/H/C/D+O callers | test (d=direct, i=indirect, -=none)
run_extra_tests.py | 221 | 92 | 2/0/9/36 | d
run_all_tests.py | 1255 | 68 | 10/1/29/107 | d
tasks.py | 1578 | 41 | 23/0/80/148 | d
codex_run.py | 1080 | 39 | 7/0/16/45 | d
sync.py | 1476 | 35 | 31/0/70/157 | d
turn_meter.py | 485 | 23 | 3/1/6/30 | i
mts_signal.py | 930 | 19 | 3/1/8/30 | d
role_loader.py | 1031 | 18 | 4/1/14/19 | i
lab_flow.py | 405 | 16 | 2/0/6/31 | d
model_guard.py | 599 | 16 | 1/1/6/15 | i
supervisor.py | 1281 | 15 | 3/0/9/20 | d
auto_deploy.py | 576 | 14 | 1/0/6/9 | d
make_status.py | 519 | 12 | 5/0/13/18 | d
shot.py | 1142 | 12 | 1/1/12/43 | d
gate_select.py | 262 | 9 | 2/0/2/6 | d
lane_health.py | 469 | 9 | 3/0/2/13 | d
make_home.py | 398 | 9 | 0/0/1/6 | i
stop_guard.py | 144 | 8 | 0/1/1/10 | d
artifacts.py | 450 | 7 | 2/0/3/13 | d
daily_hygiene.py | 99 | 6 | 3/0/1/2 | d
desk.py | 501 | 6 | 7/0/17/53 | d
lease.py | 523 | 6 | 2/0/2/6 | i
make_control_room.py | 218 | 6 | 1/0/2/6 | d
nowin.py | 146 | 6 | 0/0/4/9 | d
trunk_lag.py | 271 | 6 | 0/1/0/7 | d
backup_snapshot.py | 140 | 5 | 1/0/1/3 | d
cloud_setup.py | 63 | 5 | 1/0/0/1 | d
live_mirror.py | 515 | 5 | 3/0/12/26 | d
mts_doctor.py | 214 | 5 | 1/0/4/8 | d
nuc_wake.py | 105 | 5 | 1/0/0/5 | i
wiring_scan.py | 462 | 5 | 2/0/8/2 | d
check_handoff.py | 117 | 4 | 0/0/3/2 | d
ci_watch.py | 149 | 4 | 1/1/0/7 | d
fetch_captions_timed.py | 194 | 4 | 1/0/2/5 | i
gemini_queue.py | 105 | 4 | 5/0/9/15 | -
preship.py | 279 | 4 | 0/1/1/2 | d
relay_board.py | 205 | 4 | 0/0/0/3 | d
verdicts.py | 493 | 4 | 1/0/17/39 | d
aibridge_install.py | 121 | 3 | 0/0/4/2 | -
chart_verify.py | 122 | 3 | 0/0/4/3 | d
codex_pack.py | 95 | 3 | 1/0/0/4 | d
health_audit.py | 154 | 3 | 2/0/0/2 | d
make_layers_md.py | 147 | 3 | 0/0/5/8 | d
operator_questions.py | 316 | 3 | 0/0/1/4 | -
planted_error_trial.py | 213 | 3 | 0/0/1/3 | d
role_hook_launcher.py | 140 | 3 | 0/0/2/0 | -
tom_noise_units.py | 198 | 3 | 0/0/1/6 | -
verify_extract_quotes.py | 153 | 3 | 0/0/18/81 | d
alert_rate_check.py | 134 | 2 | 0/0/2/19 | d
c_drive_guard.py | 150 | 2 | 2/1/0/1 | d
ci_red_card.py | 96 | 2 | 1/0/0/5 | d
dsa.py | 751 | 2 | 2/0/3/6 | d
exhaust.py | 76 | 2 | 0/0/1/3 | -
gate_impact.py | 246 | 2 | 1/0/3/5 | d
hook_bench.py | 205 | 2 | 0/0/2/1 | d
host_health.py | 511 | 2 | 1/0/0/1 | d
lookahead_lint.py | 360 | 2 | 3/0/4/16 | i
make_layers_board.py | 281 | 2 | 1/0/3/3 | d
make_planner_data.py | 149 | 2 | 0/0/3/0 | -
market_guide.py | 381 | 2 | 0/0/5/7 | d
prereg_gate.py | 71 | 2 | 0/0/13/19 | d
role_line.py | 86 | 2 | 1/0/0/1 | -
session_log.py | 104 | 2 | 1/0/1/3 | d
soak_six_slots.py | 438 | 2 | 0/0/0/1 | d
testnet_canary.py | 474 | 2 | 0/0/3/12 | d
tom_holdout_split.py | 131 | 2 | 0/0/2/1 | d
trace.py | 230 | 2 | 0/0/2/5 | d
traffic.py | 745 | 2 | 2/0/9/15 | i
churn 1 or 0 (not listed one by one): 43 scripts; of them 14 have no test, 9 have zero churn: check_guide.py, declutter_backups.py, fetch_captions.py, funnel_report.py, make_groups.py, prompt_contract.py, refresh_klines.py, run_staged_tests.py, testnet_status.py.
## Part B: bug origins, 2026-10-10 to 2026-10-24

### Source 1: commits (non-merge) on origin/fast-track whose subject matches fix|bug|red|revert|hotfix|regression (case-insensitive substring)
- 3678 non-merge commits in window; 272 subjects match. Every one of the 272 was read. 162 are not defects (claim/release
  bookkeeping, research reviews that say "FIX-FIRST", card filings, hand-overs, features whose subject says "fix list"). 110 are real
  defect fixes or bug filings; that is the classified set (sample 110 of 272, above the 60 asked). The classification is by
  subject plus files touched (judgement, not a script); counts below come from the script inv_b3.py.
- Per day (classified): 10-10:4 11:6 12:3 13:3 14:2 15:6 16:13 17:7 18:16 19:9 20:2 21:10 22:10 23:17 24:2.

Origin x cause (counts of 110). Cause codes: MC merge collision / two sessions on one file; NH non-hermetic test (machine, file, clock,
network, port, console); GT gate/timeout/infrastructure (allowlists, registries, gate steps, hooks not live); LB logic bug in new code;
DR doc/rule drift (role budgets, size caps, card lint, stale text); OT other.
| origin \ cause | MC | NH | GT | LB | DR | OT | total |
|---|---|---|---|---|---|---|---|
| dev-tooling (scripts/dev, hooks, gates, roles, system docs) | 5 | 13 | 15 | 27 | 21 | 6 | 87 (79 pct) |
| trading code (execution, backtest DAX/Tom, layers, Java) | 0 | 0 | 0 | 12 | 1 | 0 | 13 (12 pct) |
| research/runtime tools (outcome_labeler, g3_pack, studies, lab tests) | 0 | 3 | 0 | 6 | 0 | 1 | 10 (9 pct) |
| total | 5 | 16 | 15 | 45 | 22 | 7 | 110 |
Cause totals: LB 41 pct, DR 20, NH 15, GT 14, OT 6, MC 5 (percent of 110).

Examples (sha, subject):
- dev / MC: be8a5b190 remove merge-conflict markers shipped in OPERATOR_DECISIONS.md; 9867b26fa fix merged wiring_registry.json seam (missing brace).
  Also 8ee38e8d9 (SUPER_SESSION log 6 rows, trunk had 6), 3cd1c67b4 (origin text won the merge), f9f30140d (merge fix).
- dev / NH: 7facabce8 planted-error trial test made hermetic (CI red); 3e9e1601e agent_live_selftest fixed port 7199 collided across concurrent gate runs.
  Also 9c1c81452 (needs F:/codex_home), 5e702b655 (needs hidden launcher console), 9703a302b (Linux CI spawns Windows processes), 3acc181da (file order by clock).
- dev / GT: 1ff9157fe lookahead allowlist rows (trunk step 4c red); 1f3fdb66b CI red fix: register test_pit_leakage in the gate (B150).
  Same family: 48cadd596, 8454bf954, 02a477d9c, 049a5a965, 2d0e6452b (12 commits touch lookahead_allowlist / wiring_registry / run_extra_tests / gate_select).
- dev / LB: 26aca7f3b role line = first line only (corrects 9f0cb459c, a fix from the day before); a0e50314c lease.role_name(None) crash.
- dev / DR: e3ac66a23 trim supervisor.md under role budget; 59d64023f CLAUDE.md under its size cap (CI red).
  supervisor.md alone appears in 8 of the 110 fixes (retoken, trim, reword, read-first); roles/role_loader/ROLES.md files in 14.
- dev / OT: 27acf65f9 Revert "MTS Doctor: CI speed diagnosis (partial)"; d6f2802b5 test_artifacts newline literal broken by shell heredoc.
- trading / LB: 3fb582de3 DAX rows gated on exact net RR not Java's 2-decimal display value; 7d7b059d1 B118 label layer bracket SAMPLING on every layer log row.
  Also 289c09bf1 B122 reject text, 6b876f6d2 B124 canary, 150840644 RSI flat window 100 to 50. (Not checked: whether each ships a test or touched live orders.)
- trading / DR: 04be239f1 test_tom_profile_parity expects FORMULAS 18.1 edge convention (CI red since d8efebc2).
- research/runtime / NH: 5d8124639 outcome_labeler zero-budget check fails on a coarse Windows clock; 80eef44df lab test needs the F: DEV tape.
- research/runtime / LB: c791836a4 outcome_labeler timer boundary; 3b3ea9df4 Q79 touch-bar look-ahead in levels study.

CI-red link: 39 of the 110 subjects say CI red / trunk red / ci-fix / gate red. Commit 4fce77e7a records one red that lasted 4 h (ci-1bb1b39).

### Fixes for problems introduced by tooling added in the last 14 days
- Of the 87 dev-tooling fixes, 42 (48 pct) touch a scripts/dev, scripts/aibridge, .claude or roles file that did not exist before 2026-10-10
  and was not created by that same commit (first-add date from git log --diff-filter=A; tests and task cards excluded). Strict lower bound.
- Looser test (also counting files in MyTradingSys/tests and scripts/dev tests added in the window): 56 of 87 (64 pct).
- Biggest clusters of new-tooling fixes: role_line.py / role_loader.py / turn_meter.py (26aca7f3b, 8fb467dea; both within 24 h), supervisor.py + supervisor.md "six slots"
  (88db1afdd, c21235c8f), planted_error_trial.py (7facabce8), preship.py (e2f1d72bd), ci_watch.py/nowin.py hooks (ce4a04a0f), gate_select.py (7a9777b8d, 02a477d9c),
  mts_signal.py (a6eaa2925, 4ac1af884, 3acc181da), prereg_gate.py (8f988e38f).
- Fix-of-fix, subject names the earlier commit: 26aca7f3b corrects 9f0cb459c; 3cd1c67b4 re-applies a lost edit; the 12 BUGS-style subjects naming 'since <sha>' or 'corrects <sha>' are 5e702b655, bd098eb26, 26aca7f3b, a4e813ed5, 04be239f1 and 7 more (regex over subjects, script inv_b3.py).
- Reading: 110 classified, 87 in tooling, 42 of those in tooling under 14 days old, so about 38 pct of all classified fixes (42 of 110) repair brand-new tooling.

### Source 2: MyTradingSys/research/BUGS.md (path is research/, not system/)
- 271 rows with ID and date (BUGS section plus TASKS section). Opened on or after 2026-10-10: 42 B rows (B157-B187, B190-B200) and 1 T row.
- Status: 30 OPEN, 11 CLOSED, 1 IN-FIX. Severity: 14 HIGH, 22 MED, 6 LOW. (B188 and B189 absent from file.)
- Origin by title (hand classified): dev-tooling 36 (AIBridge, screenshot pipeline, session/ritual, gates, backups, Control Room), trading code 1 (B174 snapshot OI gauge precision),
  research asks / operator feature requests 5 (B162, B163, B171, B179, B187), so BUGS.md is 86 pct tooling, 2 pct trading code.
- Cause of the 36: LB 11 (B157-B161 screenshot pipeline gaps, B166, B184, B185, B195, B196, B198); GT/infra 10 (B168-B170, B173, B175, B176, B178, B190-B192);
  DR/rule 10 (B164, B167, B172, B180, B183, B186, B194, B197, B199, B200); NH 1 (B193 test_nowin hidden launcher console); OT/UX 4 (B165, B177, B181, B182); MC 0.
- Gap: merge collisions are invisible in BUGS.md (0 rows) but are the fix subject of 5 commits; BUGS.md rows B188/B189 and most CI-red fixes are never filed.
  CI-red fixes are filed as pinned ci-<sha> cards, not as BUGS rows.

### Two-source total
Dev-tooling origin: 87 of 110 commit fixes + 36 of 42 BUGS rows. Trading code: 13 of 110 and 1 of 42; no live-order incident is visible in the subjects (not verified in the diffs).
