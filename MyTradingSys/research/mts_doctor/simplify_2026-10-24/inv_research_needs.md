# What the trading work needs from the dev machinery (read-only audit, worktree mts-doctor-role-7762ef, 2026-10-24)

Method: AST import scan plus path-string scan (`scripts/dev/<x>`) over 443 tracked trading files (MyTradingSys/{backtest,execution,cbp,market_data,observation,options,runtime,conditions,learning,items}, src/ Java and pom.xml, scripts/core, scripts/live, scripts/monitor, mts.ps1, runtime_data launchers, plus cbp_run.py itself). Transitive closure inside scripts/dev. Scripts: scratchpad an.py, an2.py, an3.py (same folder). Java: grep of src/ and pom.xml finds zero references to scripts/dev.

## 1. Dev modules reached from trading code (10 of 216 files in scripts/dev)

| Module | Reached from | Kind |
|---|---|---|
| verify_extract_quotes.py | cbp_run.py (import vq) | CBP quote checker, needed |
| cbp_run.py | itself the CBP entry (imports `cbp` = MyTradingSys/cbp/__init__.py, reads F:/CryptoScrapper) | CBP, needed |
| fetch_captions_timed.py | cbp_run.py (subprocess) | CBP transcript fetch, needed |
| live_mirror.py | closure via fetch_captions_timed/others | read-only desktop to worktree copy (data only) |
| shot.py | backtest/dax_engine.py (`import shot`, engine_jars), tom_dax_bt.py (hashes shot.py, uses shot.engine_jars) | Java engine classpath helper for DAX backtest, needed |
| nowin.py | closure via shot.py | no-console-window subprocess helper |
| tom_noise_units.py | backtest/tom_bt.py (`from tom_noise_units import min_stop_width`) | backtest formula, needed |
| prereg_gate.py | doc reference in layers/krown/krown_context.py (same formula, comment only); gate uses it | prereg check |
| verdicts.py | closure via prereg_gate.py | verdict registry |
| live_owner.py | scripts/core/loop-supervisor.ps1 lines 101 and 281 (`live_owner.py check` / `claim`) | LIVE PATH: supervisor calls it at start |

Test-only link: run_staged_tests.py is called by 6 execution tests (e.g. execution/test_r2_breakeven_move.py) and by gate steps 1, 2, 6. mts.ps1 (operator launcher, not trading) calls check_guide, desk, market_guide, run_all_tests, wiring_scan, live_owner.
Not reached: execution/*.py, backtest/layers/*, src/ Java and the Java launchers import nothing else from scripts/dev. Everything else (206 files) is coordination, tests of coordination, or research checkers (below).

## 2. scripts/dev by function (216 tracked files, 52,949 lines; keyword grouping, so edges are approximate)

| Group | Files | Lines | Main members |
|---|---|---|---|
| Tests of dev tooling (test_*.py, one per script) | 91 | 17,519 | test_sync, test_desk, test_tasks, test_supervisor ... |
| sync / ship / gates / CI | 25 | 9,394 | sync.py, run_all_tests.py, gate_select/impact, preship, ci_watch, ci_red_card, auto_deploy, lease, wiring_scan, wt_maint, soak_six_slots, lookahead_lint, research_kit_lint, planted_error_trial |
| status / docs / pages / research checkers | 27 | 5,364 | make_status, make_layers_md, make_control_room, make_groups, make_home, artifacts, check_guide, market_guide, trial_ledger, tom_ledger_dates, tom_holdout_split, chart_verify, refresh_klines, asr/captions |
| task cards (+ desk, DSA, codex, lab, ask_model) | 14 | 5,585 | tasks.py, task_state, desk.py, dsa.py, codex_run/pack, lab_flow, operator_questions |
| role / session hooks | 14 | 3,693 | role_loader, role_line, role_hook_launcher, model_guard, stop_guard, offer_guard, prereq_guard, prompt_contract, session_log, turn_meter |
| supervisor / host / backup | 14 | 3,426 | supervisor.py, host_health, lane_health, backup_snapshot, daily_hygiene, declutter, c_drive_*, nuc_wake, cloud_setup |
| signals / budget / exhaust / cost | 8 | 2,334 | mts_signal, exhaust, token_audit, traffic*, worker_cost_report, coord_overhead |
| doctor / audit / health | 9 | 1,971 | mts_doctor, health_audit, funnel_report, alert_rate_check, testnet_canary, testnet_status, trace, indicator_audit_* |
| relay / handoff | 2 | 320 | relay_board, check_handoff |
| other | 2 | 125 | bridge_selftest.ps1, skill_src/SKILL.md |
| Trading-reached (section 1) | 10 | 3,218 | |
| Total | 216 | 52,949 | |

Tests of dev tooling are about 33% of the lines in scripts/dev. Wider footprint: MyTradingSys/system has 911 tracked files (542 are task-card JSON); scripts/dev + system together 1,127.
Reclassify note: testnet_canary, testnet_status, alert_rate_check, soak_six_slots, lookahead_lint, research_kit_lint, planted_error_trial, trial_ledger, tom_*_dates/split, chart_verify, indicator_audit_*, funnel_report are trading checks or reports that sit in the coordination groups by name. Sum about 6k lines; they stand on the "keep" side, not "remove".

## 3. Live-path guards ("keep heavy" set)

Tests (counts of tracked test files, by script):
- MyTradingSys/execution: 56 test files (kill_switch, kill_switch_account, risk_guard, daily_loss_guard, daily_loss_monitor incl. blind_recovery/failure_cap/aggregate, orphan_watchdog, reconciler_env, executor_math, plan_compiler, auto_trader*, mainnet flag/plan/pnl offline, s1_cap, soak_report, journal_env, pm_heartbeat, trade_ledger, xferfix, b146/b148). Plus execution/tests and execution/testnet/offline (g1g2, test_suite_static).
- Java: src/test has 31 test files, src/main 21 files (10,448 Java lines in all); run by gate step 5 (`mvn -q test`).
- MyTradingSys/tests: 102 test files (b070 fee parity, b074 rule order, check_live_health, gate discovery B150 ...). Backtest: 105 test files; options: 10.
- Scripts-side live checks: test_live_owner, test_loop_supervisor_grace, test_feed_watchdog_script, test_wrapper_load_resilience, test_outcome_labeler_incremental, test_nowin, test_testnet_canary (in PYTEST_LAYER_PATHS list of run_all_tests.py).

run_all_tests.py steps (about 63 declared; about 17 cover trading): 1 Execution module tests (named list of about 30 execution tests via run_staged_tests), 2 G1G2 offline script, 3 static suite, 3tm timeframe map, 3cv/3cva chart and indicator audit, 3td/3hs Tom ledger dates and holdout split, 3ly layer index, 3vd verdict registry, 4 / 4b / 4c / 4g / 4h MyTradingSys/tests shards, 4e backtest function tests, 4f layer + live-writer tests, 5 Maven, 5b layer unit tests (all layer modules), 5c options tests, 6 backtest modules, 3gd test-file discovery (every tracked test is gated), 3dl CI deps lint, 3x/3w wiring.

Gate selection (gate_select.py FULL_RE): a ship touching execution/, runtime/, scripts/sched/, src/, pom.xml, .github/, the gate scripts themselves, or backtest/layers/*/*live*|*writer*.py runs every step (full). Unknown path = full (fail closed). Other code = smoke (name-matched steps + ALWAYS 3w, 3x, 3gd, 3dl). Docs = no local step.

CI (.github/workflows/ci.yml): triggers on push to fast-track for paths src/, backtest/, execution/, runtime/, MyTradingSys/tests, items, research py, options, observation, roles, scripts/**, workflows. Job offline-gate runs `run_all_tests.py --shard K/N` on 3 ubuntu + 12 windows shards (15 jobs; Maven in shard 1); mark-green publishes `green/fast-track` only fast-forward and only after all shards pass; auto-merge for PRs (needs both OS green).
Deploy gate (DEPLOY_RUNBOOK.md): section 1 live tree takes code only from origin/green/fast-track (`merge --ff-only`) or a tested reviewed tip; step 2 protects runtime state (_state.json backup); run unit/regression tests of affected components before restart; section 2 restart map (auto_trader, daily_loss_monitor, live_runner_cli, position_manager never killed, Java JVM needs mvn compile); builders never deploy, stop processes or touch HALT files. Supervisor ps1 (scripts/core/loop-supervisor.ps1) revives the processes and calls live_owner.py.

## 4. Commits on origin/fast-track, last 14 days (since 2026-10-08)

Total 5,363 commits: 1,685 merges (no file list) and 3,678 non-merge (3 empty). Classified by first match of touched paths: Trading = backtest/execution/cbp/market_data/observation/options/runtime/src/pom/scripts core,live,monitor (non-md); Coordination = scripts/dev, worker, aibridge, sched, ops, tools, .claude, .github, mts.ps1, runtime_data, MyTradingSys/system non-md (tasks, claims, desk_queue, roles, lane_state, artifacts, registries) and cards; Docs = .md (system docs, items); Research = MyTradingSys/research, MyTradingSys/tests.

| Of 3,675 non-empty non-merge commits | Count | Share |
|---|---|---|
| Touch trading code (any file) | 135 | 3.7% |
| Trading code only | 15 | 0.4% |
| Primary = coordination (no trading) | 1,612 | 43.9% |
| Primary = docs | 1,588 | 43.2% |
| Primary = research / tests (no trading, no coord) | 338 | 9.2% |
| Primary = other | 2 | 0.1% |
Touch any coordination file: 1,708 (46.5%).
Biggest churn paths (file touches): system/tasks 2,335, system/claims 1,359, research/layer_lab 484, NEXT_SESSION.md 289, desk_queue 274, runtime_data 248, LAYERS.md 217, research/tom_btc 191, lane_state.json 171, artifacts 117, roles 116, wiring_registry.json 115, backtest/layers 106, run_extra_tests.py 94. Authors: jishusharma 3,302, E-ngineers 308, Claude 66.
Reading: about 1 commit in 27 touches trading code; about 9 in 10 are coordination or docs.

## 5. Recommendation (1 machine, 1 operator)

Minimal set to keep:
1. Ship to trunk: a thin `sync.py ship` (branch, merge fast-track, run gate, push); the claim/lease/slot layers are optional on one machine.
2. CI: the existing offline-gate + mark-green + green-only deploy; consider trimming the Windows matrix from 12 shards (cost, not safety).
3. Live-path tests: everything in section 3 (execution 56 files, Maven, step 1/2/3, 4f, live_owner and loop-supervisor tests, test_testnet_canary) plus FULL_RE full-gate rule and DEPLOY_RUNBOOK rules.
4. Backtest correctness: steps 4e, 5b, 6, 3tm, 3cv/3cva, 3vd, lookahead_lint, research_kit_lint, planted_error_trial, trial_ledger, prereg_gate, tom holdout/ledger-date checks, B150 discovery (3gd), CI deps lint (3dl).
5. CBP: cbp_run, verify_extract_quotes, fetch_captions_timed, test_cbp_query.

Candidates to FREEZE (stop adding features; leave code, drop from gate or from daily use), ordered by lines:
- relay/handoff (2 files, 320 lines), signals/budget/exhaust/cost (8, 2,334): login juggling for multi-account fleets, no trading dependency.
- role/session hooks (14, 3,693) and task cards + desk/DSA/codex/lab (14, 5,585): the highest-churn area (tasks + claims + desk_queue about 3,970 file touches in 14 days); trading code never imports them.
- supervisor/host (14, 3,426): keep supervisor.py/host_health only if a single machine needs them; NUC wake, cloud_setup, c_drive, lane_health are multi-device.
- doctor/audit non-trading parts (mts_doctor, health_audit, trace).
- status/docs generators (make_home, make_control_room, make_groups, make_layer_map/board, artifacts, planner data): pages; keep make_layers_md only if LAYERS.md must stay generated.
- Their tests (about 60 of the 91 test files) leave the CI gate with them; steps 3tk, 3dk, 3k (sync, 3 shards), 3ds, 3bk, 3rb, 3lh, 3sig, 3sg, 3cr, 3mg, 3ms, 3af, 3cs, 3ad, 3hy are all coordination tests (about 44 of 63 steps).
- run_extra_tests.py (94 touches in 14 days) and gate_impact/quarantine machinery: gate speed tooling that the 3-minute CI shards partly make redundant.

Do not remove: anything in section 1 (10 files), gate runner core (run_all_tests, run_staged_tests, gate_select with the FULL_RE rule), and the wiring/discovery checks (3x, 3gd, 3dl) that stop silent unwired code.

Caveats: grouping is by file-name keywords, not by call graph; scripts/dev tools may call each other (e.g. sync.py to gate to tests) so freezing a group needs a removal check by import graph first. Hooks in .claude/settings.json (role_loader etc.) were not traced for dependencies. runtime_data counted as coordination (launchers and logs mixed).
