# Layer Lab Report: Cross-Vendor Bug Scan of Fast-Track Commits 360 to 440

Task: gemini-review-ships-360-440-bug-scan-1031
Lane: CODEX
Reviewer: Gemini 3.8 Flash (independent cross-vendor review)
Date: 2026-10-31

## Summary of Findings

A cross-vendor diff-vs-Result audit was conducted on 80 code commits (skipping the newest 360, evaluating 360 to 440) touching .py, .java, or .js under MyTradingSys.

- Commits evaluated: 80 (SOURCED: git log --no-merges --format=%h -- MyTradingSys/*.py MyTradingSys/**/*.py MyTradingSys/*.java MyTradingSys/**/*.java MyTradingSys/*.js MyTradingSys/**/*.js slice [360:440])
- Range: c3f9ebfd to 1550ecab
- Commits verified with explicit, accurate Result: lines (OK): 76 / 80
- Commits lacking explicit Result: lines (UNVERIFIED): 4 / 80 (Row 3 59882977d, Row 5 341a0013, Row 7 8b4ea32a2, Row 11 10d793945)
- Commits with discrepancies or functional bugs requiring FIX: 0 / 80
- Complete 80-row audit table: MyTradingSys/research/gemini_burn_2026-10-31/SHIPS_360_440_REVIEW.md

## Audit Table

| Row | Commit | Subject | Verdict | Key File:Line Cited |
|---|---|---|---|---|
| 1 | fc3f9ebfd | model_guard: role sessions never show the operator buttons | OK | MyTradingSys/tests/test_model_guard.py:100 |
| 2 | e07d78793 | CI red fix: NEXT_SESSION keep-blocks check compares to where the tree left trunk, not trunk now | OK | MyTradingSys/tests/docs/test_next_session_keeps_blocks.py:23 |
| 3 | 59882977d | model_guard: a session started by another session starts its workers as background Agents, not start_session | UNVERIFIED | MyTradingSys/tests/test_model_guard.py:85 |
| 4 | 817f84ad3 | lab lab-formula-spec-text: BLOCKED (build) | OK | MyTradingSys/research/layer_lab/formula_spec_text/gen_examples.py:1 |
| 5 | b341a0013 | lab-formula-spec-recount: keep the expectedFailure marker (card still BLOCKED); the run's stricter unknown-name check stays | UNVERIFIED | MyTradingSys/research/layer_lab/formula_spec_text/test_formula_spec.py:11 |
| 6 | d15c4e55b | codex tick survives a merge left in progress; NEXT_SESSION.md may not drop other sessions' blocks | OK | MyTradingSys/tests/docs/test_next_session_keeps_blocks.py:1 |
| 7 | 8b4ea32a2 | role_loader: file paths never score and Supervisor briefs get no fallback role (pilot 2026-10-22: idea* matched IdeaProjects, Builder loaded as Thinker) | UNVERIFIED | MyTradingSys/tests/test_role_roster.py:142 |
| 8 | 9793661a7 | Hooks: context hooks synchronous again; HIGH broadcasts with per-host ack and Stop reminder | OK | MyTradingSys/tests/test_hook_settings.py:10 |
| 9 | ce4a04a0f | Hooks: background post-tool hooks, lazy imports, away-flag fix; RUN_MODEL design; interview feed | OK | MyTradingSys/observation/capture.py:10 |
| 10 | a6eaa2925 | review fixes: boot_step parser, role fallback keywords, signal hook per tool call, cheat sheet | OK | MyTradingSys/tests/test_role_loader.py:318 |
| 11 | 10d793945 | Launch scripts derive the tree root from their own location, not the dev checkout path | UNVERIFIED | MyTradingSys/runtime/backtest_oi_delta_4state.py:6 |
| 12 | 8fd2c71ac | sim-desk: symbol box (BTC/ETH) on RSI and WaveTrend, ETH 1m fetcher; supervisor role: started sessions use user_asked, never cards | OK | MyTradingSys/research/sim_desk/fetch_klines.py:1 |
| 13 | 1687ee803 | STATUS.md: Hand-over freshness (flags NEXT_SESSION blocks that newer commits overtook); CLAUDE.md boot rule | OK | MyTradingSys/tests/test_handoff_freshness.py:1 |
| 14 | 2ead83703 | usage bounds: unattended read budget 1M for every model and the Supervisor, note at 500k (operator 2026-10-21) | OK | MyTradingSys/tests/test_turn_meter.py:176 |
| 15 | 390f02e60 | usage bounds: unattended read budget with a PreToolUse hard stop, hourly spawn caps, scheduling tools denied, a child's note never unlocks Opus | OK | MyTradingSys/tests/test_turn_meter.py:182 |
| 16 | 742fd744b | turn_meter: caps, turn counts and compaction are never reported to the operator (silent notice); CLAUDE.md 5b | OK | MyTradingSys/tests/test_turn_meter.py:150 |
| 17 | b200b4d85 | turn_meter: an operator prompt is never blocked; from his 2nd prompt the session is his (no hand-off nag); child-session events re-arm the caps | OK | MyTradingSys/tests/test_turn_meter.py:120 |
| 18 | ba7c049b2 | turn_meter: /compact reopens a blocked Opus session (read size from compact_boundary), nothing blocks after a compaction, system-reminder messages are events | OK | MyTradingSys/tests/test_turn_meter.py:272 |
| 19 | 2b80ef52b | sim-desk: RSI 40/60 (Malkan) and WaveTrend (LazyBear) studies on the desk | OK | MyTradingSys/research/sim_desk/charts.py:11 |
| 20 | 8557ad144 | turn_meter: event prompts exempt, compaction ends Opus jobs, resumed >150k blocked; doctor flags stale main-checkout hooks | OK | MyTradingSys/tests/test_turn_meter.py:179 |
| 21 | 8906fb114 | roles: retoken supervisor.md and update size budget in test_role_budget.py | OK | MyTradingSys/tests/test_role_budget.py:12 |
| 22 | 02e00c4e2 | turn_meter: find a Supervisor from its transcript when the hook never saw the start line | OK | MyTradingSys/tests/test_turn_meter.py:230 |
| 23 | 64f366f2c | turn_meter: Opus is use-and-destroy, no second operator message above 150k context | OK | MyTradingSys/tests/test_turn_meter.py:170 |
| 24 | 48fb231bc | turn_meter: Supervisor capped by context (500k), not 40 tool turns; compaction-safe wake rule | OK | MyTradingSys/tests/test_turn_meter.py:199 |
| 25 | 220ec4619 | context-leaks: keep every role under the 10k hook cap, remind less often | OK | MyTradingSys/tests/test_role_loader.py:146 |
| 26 | 4052f0410 | lab lab-formula-spec-recount: BLOCKED (build) | OK | MyTradingSys/research/layer_lab/formula_spec_text/test_formula_spec.py:11 |
| 27 | 5f2c69939 | sim-desk: one-file plug-in seam for layers + Questions panel on the page | OK | MyTradingSys/research/sim_desk/desk.py:10 |
| 28 | 3c262f8b3 | sim-desk: count filled trades only, sample-spread verdict, dated charts (Fable review C1-C3, E) | OK | MyTradingSys/research/sim_desk/charts.py:5 |
| 29 | 293fb5515 | roles: Admin_Guy moves from Haiku 5.5 high to Sonnet 5.5 medium | OK | MyTradingSys/tests/test_role_loader.py:265 |
| 30 | 2998b4ac4 | roles: read-first rule for rule, role, super-session and budget answers | OK | MyTradingSys/tests/test_role_lint.py:32 |
| 31 | ab5f42d1e | sim-desk: one-screen simulator desk v1 (levels study, verdict, 6 example charts) | OK | MyTradingSys/research/sim_desk/charts.py:1 |
| 32 | 0c6700cd2 | roles: one roster, list command, best-role fallback | OK | MyTradingSys/tests/test_role_roster.py:1 |
| 33 | 119d763d2 | Pitchfork Phase 2: 4H timeframe & Volume Profile Value Area confluence study | OK | MyTradingSys/backtest/layers/pitchfork/test_pitchfork_detector.py:197 |
| 34 | 150840644 | b-item-krown-core-rsi-returns-100-on-a-f: fix flat window RSI 100 to 50 and update docstrings | OK | MyTradingSys/backtest/layers/alerts/live_bb_top_reversal.py:11 |
| 35 | f0f5dd475 | wt-triage-nuc: rescue candle-close corrected study (frozen, 0/2016 cells pass) and T04 log helper from stale NUC trees | OK | MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T04/_make_log.py:1 |
| 36 | bca2e763f | refactor(pitchfork): move research scripts under MyTradingSys/research & update lookahead allowlist | OK | MyTradingSys/research/pitchfork_2026-10-19/eval_btc_pitchfork_traders.py:14 |
| 37 | 1339d6af9 | feat(pitchfork): revalidate engine, implement fixes & complete 2020-2026 event study | OK | MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:115 |
| 38 | 4843f9284 | lc-ladder-dev: NEXT_SESSION title first, CSV written with LF | OK | MyTradingSys/research/levels_confluence_2026-10-14/ladder_run.py:447 |
| 39 | da096725e | lc-ladder-dev: LC3 ladder simulator, DEV run of all 240 pre-registered arms plus arm P | OK | MyTradingSys/research/levels_confluence_2026-10-14/ladder.py:1 |
| 40 | df2292067 | B183: instruct workers that CLAUDE.md is already in context to eliminate redundant startup reads | OK | MyTradingSys/tests/test_relay_prompts.py:86 |
| 41 | 4217c8da7 | trim-builder-cwd-and-prelaunch-worktree: launch builder workers in worktree CWD | OK | MyTradingSys/tests/test_relay.py:573 |
| 42 | ba46d25c7 | gate tiers by path: docs ship without a gate, smoke 240 s cap, claims on a side branch, 10-min ship gap | OK | MyTradingSys/tests/docs/test_integrity.py:1 |
| 43 | 1d9f4e8ab | analysts: implement Crypto Chase FVG social call listener and ledger | OK | MyTradingSys/research/analysts/cryptochase/__init__.py:1 |
| 44 | d1149b0c7 | Roles simplified (9 of 10) + Eagle_Eyes v4 Think mode | OK | MyTradingSys/tests/test_role_budget.py:1 |
| 45 | 595914d43 | analysts: implement DailyPriceAction market plan ingestion for Justin Bennett | OK | MyTradingSys/research/analysts/bennett/scraper.py:1 |
| 46 | f1ab5fa0c | Thinker role: accept thinker_guy / thinker guy triggers | OK | MyTradingSys/tests/test_role_loader.py:273 |
| 47 | c791836a4 | outcome_labeler: fix timer boundary check in load_snapshots so zero budget halts after first file | OK | MyTradingSys/runtime/outcome_labeler.py:37 |
| 48 | 726da12b3 | analysts: implement RLinda TradingView idea scraper and call ledger | OK | MyTradingSys/research/analysts/rlinda/scraper.py:1 |
| 49 | ac0f4e6e6 | Indicator values multi-model audit: 21 blind RSI/BB/StochRSI values, Haiku and Sonnet 0 mismatches (MACHINE-OK) | OK | MyTradingSys/research/indicator_audit_2026-10-14/replies/reviewer_haiku_compute.py:1 |
| 50 | b0e31e9eb | malkan: deliver GFS BTC HTF pre-reg, update test_pre_reg_template, close malkan-universe-data-power | OK | MyTradingSys/backtest/test_pre_reg_template.py:207 |
| 51 | aa3c4d445 | Reword runbook/test text to pass the doc forbidden-refs test | OK | MyTradingSys/tests/test_generated_files_untracked.py:41 |
| 52 | ee286acf0 | Untrack live-host generated files; add deploy backup/restore helper (commit 1 of 2) | OK | MyTradingSys/tests/test_check_live_health.py:72 |
| 53 | e236a3e15 | Simulator validation: planted edge, fee-including null, trade-list diff (q16) | OK | MyTradingSys/backtest/test_sim_planted_edge.py:1 |
| 54 | 10b434480 | Thinker role: Opus design partner (options with cost/ROI/risk, improvement scans, verbatim decisions, raw cards) | OK | MyTradingSys/tests/test_role_loader.py:268 |
| 55 | 69326506c | outcome_labeler: per-cycle open budget so a cold backlog drains; launcher logs labeler rc | OK | MyTradingSys/runtime/outcome_labeler.py:3 |
| 56 | fa7f26b87 | tom-ledger: add losing first attempts T1-a0 and T7-a0 from video statements | OK | MyTradingSys/research/tom_transfer_2026-10-11/check_attempt_rows.py:1 |
| 57 | 06b9b3115 | research: resolve shipping proof gaps and accurately report fast gate ALWAYS steps | OK | MyTradingSys/research/shipping_speed_2026-10-19/measure.py:1 |
| 58 | f47626249 | traffic: name DESKTOP-F7IU69N in Lenovo git email and traffic_inventory (tc6) | OK | MyTradingSys/tests/test_traffic.py:216 |
| 59 | c65b87811 | shot: bundle evidence packet per multi-chart set (RU3) | OK | MyTradingSys/tests/test_shot_bundle.py:1 |
| 60 | 653f99379 | Roles 11 -> 7: Pipeliner absorbs Traffic_Controller, Admin_Guy, 1985Artifacts_Guy, SPEND per login | OK | MyTradingSys/tests/test_builder_role.py:78 |
| 61 | 3a9b389a8 | T01 backtest audit: data forensics on DEV 1m bars, loader torture matrix, 1m-vs-1d resample mismatch | OK | MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T01/t01_cross.py:1 |
| 62 | 6b8e2cd46 | sync: machine-wide gate slots, precheck slot, and ship timing (SV7) | OK | MyTradingSys/tests/test_gate_budget.py:1 |
| 63 | 87535477b | test: payload version check expects agent 0.7.1 | OK | MyTradingSys/tests/test_aibridge_payload.py:23 |
| 64 | c73617400 | bt_engine.simulate_trade: fail closed on funding, window t_in < s <= t_out (T03-F1/F2) | OK | MyTradingSys/backtest/bt/bt_engine.py:7 |
| 65 | b9c448c72 | T02-F3a: event-forcing look-ahead fixtures (shared harness, malkan_bull, funding_cvd_fade) | OK | MyTradingSys/backtest/layers/alerts/test_lookahead_forcing.py:1 |
| 66 | ed732be05 | sync: test_ship_fast_path.py alias + close ship-gate-fast-path-under-60s | OK | MyTradingSys/tests/test_ship_fast_path.py:1 |
| 67 | 63e004f7f | coord_overhead: transcript parser and measurement test (SV6) | OK | MyTradingSys/tests/test_coord_overhead.py:1 |
| 68 | 9ccc1f3ab | Keep research N5 stop-width inputs causal at as-of cutoff | OK | MyTradingSys/tests/test_tom_min_stop_width.py:8 |
| 69 | 9703a302b | Fix Linux CI spawn-audit test without launching Windows-flagged processes | OK | MyTradingSys/tests/test_nowin_audit.py:24 |
| 70 | e0b69ea13 | tasks: fill subcommand promotes raw cards via CLI flags | OK | MyTradingSys/tests/test_tasks_fill.py:1 |
| 71 | 83d7484f3 | tasks: content-bound review receipts (RU6) | OK | MyTradingSys/tests/test_review_receipts.py:1 |
| 72 | 652468a49 | tasks: zero-token lab pre-check in tasks.py check (RU5) | OK | MyTradingSys/tests/test_tasks_lab_precheck.py:1 |
| 73 | 46a3db2ef | sv4-builder-role-and-brief: roles/builder.md + supervisor.py brief + dispatch role field | OK | MyTradingSys/tests/test_builder_role.py:1 |
| 74 | a0e50314c | CI fix: lease.role_name(None) crash + f1_rows lint | OK | MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/f1_rows.py:56 |
| 75 | 204195e11 | test_lease: speed up test setup using plumbing and shared clones | OK | MyTradingSys/tests/test_lease.py:19 |
| 76 | 674c87326 | RU9 Artifacts_Guy: artifacts.py audit-links | OK | MyTradingSys/tests/test_artifacts_audit_links.py:1 |
| 77 | dff6abaf1 | nowin: add spawn diagnostic log and audit subcommand (RU8) | OK | MyTradingSys/tests/test_nowin_audit.py:1 |
| 78 | 76a730641 | qa: add operator_questions.py pending with ranking and filter (RU7) | OK | MyTradingSys/tests/test_operator_questions_pending.py:1 |
| 79 | 1abed63bd | krown: fold liquidation cascades extract into KROWN_RULES.csv and spec, close wavetrend desk row | OK | MyTradingSys/research/krown_ta101_2026-10-13/tools/build_ledger.py:22 |
| 80 | a1550ecab | traffic controller: trunk lease keeps Pipeliner/Traffic_Controller single; traffic.py measure/status | OK | MyTradingSys/tests/test_lease.py:1 |
