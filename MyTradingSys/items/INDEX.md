# ITEMS INDEX
# One line per item. Boot-loaded. Read a full item doc only when its
# row is the active task.
#
# Format: <id> | <status> | <file> | <one-line state>

B058 | CLOSED  | B058_floor_reaction_mode.md | floor-reaction mode; receipt in BUGS row
B059 | CLOSED  | B059_rank1_zone_drift.md | pf_vp bin-edge drift; fix landed 2026-09-24, pinned by BuildVpFixedGridTest 2026-10-11
B062 | CLOSED  | B062_alert_direction_position.md | position-aware alert gating; landed
B063 | OPEN    | B063_divergence.md | decision: restore divergence in schema, or deprecate
B064 | CLOSED  | B064_supervisor_stop_flag.md | supervisor_stop.flag retired 2026-09-24, loop_stop.flag only
B065 | CLOSED  | B065_stale_swing_consumer.md | stale-swing rejection in extractZones + stop selection; landed
B066 | CLOSED  | B066_rank1_distance_gate.md | rank-1 shown at trigger_ready while 150 pts from price; split from B059
B139 | OPEN    | B139_cbp_adapter.md | CBP adapter registered; real-queue run 0 candidates (1 acked, 1 rejected); analyst-rule backtests pending
B140 | BLOCKED | B140_whea_storport_hdd.md | NEEDS OPERATOR (hardware): swap SATA cable+port, elevated smartctl short test, back up D:, move D:\tools to SSD; SMART already clean
B141 | OPEN    | B141_htf_balance_null.md | htf bal_4h/bal_1d null: NS-fixed k_bal 0.8 balanced 0.4% of windows; replace-via-backtest pre-reg BOUND, run next
T034 | OPEN    | T034_positioning_states.md | 4 positioning flags; blocked on Rule 33 readers + output type
T035 | CLOSED  | T035_multi_venue_cvd.md | DEFER - SCREENER module, no Tom source
T037 | CLOSED | T037_test_coverage_gap.md | tests for all 8 files; MarketDataSnapshot bodies filled (21 tests, seam b); mvn test 128 pass
T038 | CLOSED  | T038_context_bucket_gate.md | spec delivered W3; trigger 21000 labels
T039 | CLOSED  | T039_functionality_doc_sweep.md | doc sweep; landed
T040 | OPEN    | T040_tick_delta_layer.md | tick delta layer; thresholds need Tom citation or documented exception
T041 | CLOSED  | T041_verdict_timeframe_gap.md | reframed: misframe, not a defect; closed 2026-09-23
T042 | OPEN    | T042_schema_gap.md | 1w/1d/4h structure emitted, no consumer; OI/CVD peak ref not emitted
T043 | WONTFIX | T043_traceability_gap.md | source-to-code traceability; closed as WONTFIX 2026-09-23
T044 | OPEN    | T044_hybrid_run_mode_divergence_alert.md | hybrid REST/WS >3pt divergence alert; not started
T045 | CLOSED  | T045_marginal_new_high_materiality.md | materiality is consumer-layer; producer emits raw
T046 | OPEN    | T046_stage3_pending_decisions.md | 5 pending decisions; bundle

B067 | CLOSED  | B067_crypto_module_audit.md | audit delivered W4; demote action in B070
B069 | OPEN    | B069_update_market_state_wrapper.md | wrapper STATE_UPDATE_WARN exit=1; stderr hidden | LOW
B070 | CLOSED  | B070_crypto_demote.md | net_rr = fee model (fees.py), UTC 00:00 anchor display-only; c8d36b8; NetRRConstantTest, CvdAnchorDisplayOnlyTest, test_b070_fee_parity; live jar rebuild + supervisor restart pending
T048 | OPEN    | T048_satellite_framework.md | exchange API layer active (Deribit); freeze lifted 2026-09-26; satellites follow
T049 | CLOSED  | T049_nuc_worker_v2.md | Qwen decommissioned 2026-10-01; NUC lane retired; AIBridge replaces run-command surface
T050 | CLOSED  | T050_deribit_execution_layer.md | phase 3 live testnet PASS 2026-10-04
T051 | PARKED  | T051_backtest_parked.md | backtest on MTS raw verdict done; parked by operator 2026-09-26; resumes after T050 ph4 + B071 fixed
B071 | CLOSED  | B071_fail_open_proof_direction.md | fail-open fix applied live 2026-09-27 (harness-verified, PS execution unconfirmed); was: Python error defaulted proof-direction to "aligned"
B072 | CLOSED  | B072_l2_input_validation.md | L2 input validation absent for current_price "x" or None in build_math_object (F10)
B073 | CLOSED  | B073_net_rr_rounding.md | net_rr rounding inconsistency: output 2dp, sanity check unrounded (F11)
B074 | OPEN    | B074_rule_order_dependence.md | rule-order dependence: contradiction cap runs before broken-value override (F12)
B075 | CLOSED  | B075_historical_mode_unfit.md | historical snapshot no live calls, flow fields null/UNAVAILABLE; 86313de 2f40ea5 3fdf8cb; HistoricalSnapshotNoLiveCallsTest, HistoricalBookImbalanceNullTest
B076 | CLOSED  | B076_setup_confirmed_unreachable.md | SETUP_CONFIRMED unreachable; Compute-Verdict never emits it (F9)
B077 | CLOSED  | B077_stop_order_wrong_type.md | stop_market via deribit_orders.py; closed 5e387a1; receipt in BUGS row
B078 | CLOSED  | B078_cancel_all_by_label_overscope.md | cancel_by_label is label-scoped server-side; closed 5e387a1; receipt in BUGS row
B079 | CLOSED  | B079_caps_check_not_enforced.md | caps enforced in executor.py; closed 5e387a1, b05c1cf; receipt in BUGS row
T052 | OPEN    | T052_setup_confirmed_trigger.md | define a Tom-cited trigger for SETUP_CONFIRMED per operator D6b ruling
T059 | WONTFIX | T059_paste_size_guard.md | auto-split dropped 2026-10-08: operator wants the 100-250 KB paste whole
T053 | OPEN    | T053_two_account_hedge_scalping.md | two-account hedge / leveraged scalping research; ask restated 2026-09-28
T054 | OPEN    | T054_us_session_news_correlation.md | US session / pre-market alerts, US-equity correlation, news sentiment; filed 2026-09-28
T055 | OPEN    | T055_positioning_flow_and_proven_setups.md | Net/New Longs and Shorts research plus proven BTC setups; filed 2026-09-28
T056 | WONTFIX | T056_qwen_audit_program.md | premise gone: Qwen NUC lane decommissioned 2026-10-01 (263b13f, T049 + B082 closed)
T057 | OPEN    | T057_simplify_declutter.md | simplify / optimize / declutter; follows DEV_VELOCITY_AUDIT.md 2026-09-27
T058 | OPEN    | T058_broken_extremes_sweep_vs_continuation.md | broken lows/highs by timeframe: continuation vs liquidity sweep; filed 2026-09-29
T060 | OPEN    | T060_low_volatility_btc.md | low-volatility anomaly; test whether trailing realized-vol rank predicts BTC forward return
T061 | OPEN    | T061_wavetrend_lazybear.md | WaveTrend with Crosses [LazyBear]; integrate as separate indicator layer
B080 | CLOSED  | B080_dsa_pace_hourly_cap.md | stale/future/non-epoch entries filter + self-heal in pacing_block; regression tests
B081 | CLOSED  | B081_fee_source_conflict.md | fees.py single source; receipt 1ec7d8f, 547 tests pass
B082 | CLOSED  | B082_qwen_feeder_missing.md | task deleted; Qwen decommissioned 2026-10-01
T062 | CLOSED  | T062_deprecate_manager.md | deprecate mts-manager; superseded by DSA-composed CL prompts
B083 | CLOSED  | B083_prompt_check_gate.md | prompt_check.ps1 advisory gate; test_prompt_check.ps1 PASS 4/4 2026-10-03
B084 | CLOSED  | B084_book_imbalance_zero_origin.md | origin found (ProofResult default 0 + asDouble null->0.0); fixed 2f40ea5 0c34a2d; BookImbalanceUnavailableTest, HistoricalBookImbalanceNullTest
B085 | CLOSED  | B085_tom_bt_proof5_skew.md | hypothesis refuted; skew is upstream (see B131)
B086 | CLOSED  | B086_dispatcher_second_writer.md | dispatcher demo launched a second CL writer; one-writer-per-file-set violated; Claude decides fix
B087 | CLOSED  | B087_pick_task_repick.md | pick_task.py re-picks same row each wake; two smaller flags attached; Claude decides fixes
B088 | CLOSED  | B088_session_id_surface_code.md | one code CLI via pick_task.session_id; cooldown default = stale-session window; receipt in BUGS row
B089 | CLOSED  | B089_bugs_invisible_to_scheduler.md | shape A: pick_task.py sweeps BUGS-only OPEN ids into wave max+1; receipt in BUGS row
B090 | OPEN    | B090_cloud_credit_approval.md | two-bucket cloud plan ($50 today + $49 contingent); Claude approves; 2 of 8 items need a desktop precondition
B091 | CLOSED  | B091_build_check_speed.md | Build-Check.ps1 ~45s and dirties tree each run; fast tier + read-only mode; Claude decides shape
B092 | CLOSED  | B092_dsa_write_batching.md | DSA appends gate+commit to every write; add section 6b BATCHING rule; Claude decides wording
B093 | CLOSED  | B093_parallel_dispatch.md | pick-side fix at 1c81d81 (shape B, 3 slots); launcher side fixed (go.py --id, test_go 10-13)
B094 | CLOSED  | B094_headless_scheduler.md | autogo.py + go.py per-run cap + tick check; ships disabled, operator enables; 4 auto-disable conditions
B095 | OPEN    | B095_per_session_cost.md | per-session cost not on disk; session record + prompt composer need a cost field; Claude decides shape
B097 | CLOSED  | B097_kxh_mislabel.md | kXhIAug0Gh8_v2.md:65 says entry before proof; rows 6-7 say proof first
B098 | OPEN    | B098_python_cpu_spin.md | CPU spike was TF8 backtest pool; closed
B099 | CLOSED  | B099_v3_l3_pool_hang.md | run_v3_l3 pool stall now fails closed + resumable; re-run completed; original cause unknown
B100 | CLOSED  | B100_audit_verdict_mismatch.md | E1b/E2 labelled NO-SOURCE but carry Tom quotes; should be CONCEPT-ONLY per audit's own rules
B101 | CLOSED  | B101_dsa_context_ask.md | behavioral; the two one-liners exist at DSA_SESSION_PROMPT.md L99 and L100
B104 | CLOSED  | B104_rules_vs_gates.md | rules exist for prompt hygiene; check is advisory, not blocking; blocking + checks 6-10 (60f3250) + check 11 (b796edb)
B102 | CLOSED  | B102_dst_session_anchors.md | fixed-UTC session anchors in offline models; wrong 1h on ~40% of days
B103 | CLOSED  | B103_funding_coverage.md | funding cost silently 0 outside loaded range; archive has funding from 2020-01
B116 | CLOSED  | B116_unsourced_stop_floor_and_fallback.md | 0.1 pct floor + 0.2 pct fallback removed 0c34a2d (SetupCandidatesBuilder.java:48,104,116-124); SetupCandidatesBuilderStopT3Test
B117 | OPEN    | B117_unsourced_proof_bands.md | proof bands 3/5 NO-SOURCE still gate the verdict ladder; filing only
B118 | CLOSED  | B118_layer_bracket_unsourced.md | layer bracket stop_pct 1.0 / targets 2 / size 100 unsourced in auto_trader.py (live path); filing only
B119 | OPEN    | B119_desktop_operator_gated_revalidation.md | paper verification, kappa clean reader, T2 run all need desktop/operator
B120 | OPEN    | B120_provenance_audit_doc_followups.md | receipt 2026-10-07: W3-5 parked on operator DATA-PLUMBING definition; other sub-items unblocked doc work, not run
B121 | OPEN    | B121_poll_cadence_defaults.md | poll cadence: live_runner 60 s not bar-aligned, auto_trader 20 s; proposals not landed
B122 | OPEN    | B122_reject_text_event_fallback.md | auto_trader reject text uses alert.get('event') not the fallback; cosmetic
B123 | OPEN    | B123_zero_trade_and_quiet_families.md | zero-trade after AUTO_PAUSE (cleared), 24 h re-run pending, jishu_4 QUIET to investigate
B124 | CLOSED  | B124_journal_dir_open_plan_check.md | no check that execution/journal holds each open plan; canary has no journal check
B125 | CLOSED  | B125_consensus_writer_staged_only.md | 2026-10-10: 2fccf66 consensus writer + RSI observation wired into the live runner; 164 layer tests pass
B126 | OPEN    | B126_supervisor_inbox_consumption.md | cloud to SUP inbox consumption unverifiable; no mechanism on disk
B127 | CLOSED  | B127_partial_code_no_test.md | CLOSED 2026-10-08: 13 of 13 rows dispositioned; A11 reclassified TOM-CONCEPT-ONLY by operator
B128 | OPEN    | B128_partial_code_partial_no_test.md | receipt 2026-10-08: 11 of 18 closed (rsi:cross side-by-level landed); residual RA-W2-N, TC-W2-MDS/SCE, TC-W1-10, M29-14, M30-04/11
B129 | CLOSED  | B129_b074_test_harness_fragility.md | test_b074_rule_order.py fail-before fires on parser error, not assertion
B130 | CLOSED  | B130_execution_tests_not_gated.md | execution/tests wired into PYTEST_LAYER_PATHS; guard test passes
B131 | CLOSED  | B131_tom_pool_skew_upstream.md | Tom proof-5 pool 2:1 short at SetupCandidatesBuilder, before proof-direction; separate from B085
B132 | OPEN    | B132_dsa_does_quick_wins.md | DSA dispatches work it can do itself; codify DSA-does-this list + CC-prompt names DSA unblock work
B133 | CLOSED  | B133_dsa_default_cli_over_app.md | CLOSED: checks 12-13 (81c7e9f), section 9 App-opening line (e41de5f), LESSONS (ed0e3c1)
B134 | CLOSED  | B134_compose_surface_marker.md | pick_task.py:256 emits SURFACE: APP; prompt_check.ps1 check 13 PASS on composed probe
B135 | CLOSED  | B135_b131_threshold_recheck.md | B131 follow-up: ps1 proof-count thresholds and allshorts parity re-run
B136 | CLOSED  | B136_oi_endpoint_path.md | URLs fixed 881f22b (tests 3/3, mvn 133/133), loop restarted 2026-10-06; REOPENED 2026-10-08: buildOiBreakdown still fail-open (0.0 + LOW, no UNAVAILABLE), TESTNET_STATUS taint rows not found
B137 | OPEN    | B137_device_roles_undecided.md | 2026-10-10: 4 decided on disk (Q2, Q3, Q6-proposed, Q7), 7 operator-owed (Q1, Q4, Q5, Q8, Q9, Q10, Q11); DEVICES.md sec 4-10 carry the state
B138 | OPEN    | B138_dumps_two_copies.md | 2026-10-10: C: canonical, F: stale; share stays C:; junction deferred to supervisor window (move_dumps_to_F.ps1 ready)
T063 | PARTIAL | T063_stop_run_oi_flush_signature.md | pre-reg + A0 + A1 (n=21 inconclusive, below 30 min); holds 09-29.., ~7d overlap not 30d; commits 3776f2f b055c2b c61a26a 690b238
T064 | DONE    | T064_timeframe_selection_confirmation.md | 35 quotes (20 Tom, 15 Fabio); Tom zone/trigger sourced, Fabio retrace NO-SOURCE; verify_extract_quotes.py green; 65d4748. Cross-check TOM-091 vs TOM-092 pending
T065 | DONE    | T065_lazybear_survey.md | shortlist 4 (SQZMOM, BVI, WaveTrend=T061, VFI); Pine sources verified on Desktop (BVI lookback 8/no thresholds, VFI 130/0.2/2.5/5, SQZ BB-mult bug); 1569678 e9bd822
T066 | BLOCKED | T066_my_charts_module.md | my_charts/ created (README only); Claude in Chrome not connected; operator to connect extension + open two layouts; 1c0d276
T067 | PARTIAL | T067_alert_improvements.md | spec + 29 failing-first tests; sweep+OI alert held because T063 A1 inconclusive; alerts.ps1 untouched; b92bd29; buy-detection meaning still pending operator
T068 | OPEN    | T068_oi_arm_rerun.md | P3 OI arm rerun of T063 when n>=30 per arm; queued (research-agenda)
T069 | OPEN    | T069_funding_settlement_clock.md | P5 funding settlement clock event study; queued (research-agenda)
T070 | OPEN    | T070_volatility_timing_read_only.md | P6 volatility timing read-only analysis; queued (research-agenda)
T071 | OPEN    | T071_absorption_events_post_p2.md | P7 absorption events after P2 Fabio L3-FAIL; queued (research-agenda)
B142 | CLOSED  | B142_extrasetupbuilder_1m_stop_unsourced.md | momentum candidates disabled in code 2026-10-11 (ExtraSetupBuilderDisabledTest); live after the JIS-NB Java window
B143 | BLOCKED | B143_cryptocred_stop_buffer_and_target_unsourced.md | NEEDS OPERATOR: 1.5R sourced (CC Rule 9), 0.1pct buffer NOT FOUND; default alert-only + replace at next CC build
B144 | OPEN    | B144_exhaustion_proxy_unsourced_params.md | D17 answered: screener-only now, remove at Java window; finding: volume spike still counts in Tom proof (Java change)
B145 | CLOSED  | B145_cc_range_noise_live_neutrality.md | neutrality test run on archive: filter NOT neutral for 2 of 3 setups, flag stays off; opt-in test in cryptocred/
B146 | CLOSED  | B146_no_min_stop_after_floor_removal.md | fee-to-stop admission gate on at 0.3 (D09), tests gated; Java stop buffer is T081
B147 | CLOSED  | B147_tom_live_rule_evidence_unreliable.md | row drop attributed to removed 0.2pct fallback stop (0c34a2d, B131); exact regen done 2026-10-10 (93.6pct of lost snapshots were fallback-stop; 0 proof>=5 rows under sourced stops); DSR moot at N=0
B148 | IN-FIX  | B148_dlm_reauth_main_account_and_account_drops.md | code+tests complete (parts 1-5); Step 0 test fallout fixed 9b27da3; close on first live beat_utc refresh
B149 | CLOSED | B149_l6_pnl_source_tracker_stale_settlement_gap.md | log captured 2026-10-10: settlement + close = whole PnL, no double count; mainnet_pnl.py now includes type settlement (2026-10-10); live monitor picks it up at next restart
B150 | CLOSED  | B150_gate_is_hand_maintained_allowlist.md | discovery covers every tracked test; extra-tests step; mainnet refuses testnet calibration; 3 ungated failures fixed
B151 | CLOSED  | B151_backtest_fill_optimism_and_selection.md | fib bear zone + blow-through, target trade-through, open_at_end printed, rerun: all CC setups FAIL
B152 | CLOSED  | B152_retention_deletes_read_data_and_deploy_trap.md | retention keeps audit data and mtime; deploy runbook + auto_deploy copy/restore _state.json
B153 | CLOSED  | B153_netrr_floor_ownerless_and_cross_language_parity.md | Py+Java parity table, floor owner/review date 2026-11-10, OI breakdown UNAVAILABLE; floor value is an operator question in the decision block
B154 | OPEN    | B154_regime_and_session_stratified_backtest.md | no regime or session stratified verdict; from research pass 2026-10-09 (playbook PART I)
B155 | CLOSED  | B155_claude_prompt_contract_unchecked.md | section 5d contract is an executing gate (prompt_contract.py, step 3pc)
B156 | CLOSED  | B156_tom_alert_stale_ssot_thesis.md | alert card thesis line shows when it was written (age), tests
T093 | CLOSED  | T093_toc_imbalance_klines.md | turn-of-candle 4-12h imbalance on klines 2022-2026: NO REPLICATION (gross +0.5bp vs 10bp fee)
B162 | OPEN    | B162_qriptal_signal_layer.md | Qriptal (Habib) layer: score his public record first, Discord feed route = D21, own testnet account
B163 | OPEN    | B163_setup_alpha_beta_handoff.md | Setup Alpha (1d SMA200 trend) / Beta (sweep+CVD) handoff: NO-SOURCE research backtest only, waits on D22
B171 | OPEN    | B171_imbalance_indicator_end_to_end.md | operator: profitable imbalance indicator end to end; none exists (T093/P4 NO REPLICATION); pre-register, backtest, testnet via supervisor
B174 | OPEN    | B174_snapshot_oi_quantized.md | snapshot OI quantized to 0.01; full-precision series in backtest/raw/metrics unread; Claude decides consumer or display-only
# END
B175 | OPEN    | B175_defender_msmpeng_cpu.md | Defender MsMpEng ~0.94 core on JIS-NB; ordered fix plan (pid 3200, ext exclusions, Dev Drive), operator confirms host changes
B177 | OPEN    | B177_control_room_layer_board_tab.md | operator: Control Room 'Layer Board' tab - per active layer: dev/test activity, combined indicators, step count, actionables only
B178 | OPEN    | B178_cicd_deploy_gate_speed.md | operator: CI/CD end-to-end speed - deploy gate runs the full layer suite as one cold call; backup_snapshot competes for disk
B179 | OPEN    | B179_tom_fabio_layers_story_slides.md | operator: turn the Tom and Fabio layers story (principles and concepts) into a slide deck artifact so the operator can learn what they taught
B180 | OPEN    | B180_dsa_host_routing_and_scheduler.md | operator: DSA picks its tasks by default from the machine it runs on, and something assigns DSA tasks on a schedule (cost)
B181 | OPEN    | B181_control_room_inbox_progress.md | operator: Control Room Inbox shows no progress per item; an item without a registry ref shows nothing
B182 | OPEN    | B182_dsa_parallel_sessions_nb_nuc_scope.md | DSA AIBridge tasks run in parallel with NB/NUC scope kept; split units, per-host lane, claim per task
B183 | OPEN    | B183_session_start_ritual_audit.md | session start ritual audit after AI-health changes; measure boot reads against the B172 token plan
T081 | OPEN    | T081_backtest_d_stop_tuning.md | Backtest D: walk-forward stop_buffer_atr; Tom part NO 2026-10-09, tight-stop layers blocked on B143
T082 | OPEN    | T082_capture_matrix_rerun.md | re-run capture matrix + Tom core after Stage 1 data fixes
T083 | OPEN    | T083_rsi_events_1h_lead_check.md | rsi_events 1h on full 2022-2026 history with fees
T084 | OPEN    | T084_fabio_escalation_1h_lead_check.md | fabio escalation 1h walk-forward with fees
T085 | OPEN    | T085_time_exit_dominates.md | 97pct of testnet trades end on the time exit; fix exits
T086 | OPEN    | T086_go_live_bar.md | go-live bar for real money: operator-signed criteria
T090 | OPEN    | T090_7h_timeframe_research.md | 7h timeframe research under playbook PART I
B167 | OPEN    | B167_project_vision_stale.md | PROJECT_VISION.md stale; VISION_GAP report on disk, addendum awaits D23
B168 | IN-FIX  | B168_aibridge_autorun_stops.md | AIBridge auto-run stops between turns + slow; content.js stay-armed landed, reload pending
B170 | OPEN    | B170_github_ci_emails_and_stuck_green.md | GitHub CI emails + green/fast-track stuck; operator + workflow-scope token
B172 | OPEN    | B172_sonnet_ritual_token_use.md | Sonnet ritual token use; measure, trim, templatize
B173 | OPEN    | B173_terminal_window_flashes.md | terminal window flashes and steals focus; find visible-console starts
B176 | OPEN    | B176_aibridge_autorun_readonly_scripts.md | AIBridge refuses read-only python/node blocks; policy.json + agent.ps1 (outside repo)
T087 | CLOSED  | T087_session_levels_observation_layer.md | session-levels observation layer + failed first break base rates (71df3aa): 913 breaks 2022-2026, no edge
T088 | CLOSED  | T088_all_timeframe_module.md | timeframe registry: 4m, 3h, 7h day-reset, 7h_epoch added (0aa8f56); 9 tests failed on old code, 152 pass
B159 | OPEN    | B159_screenshot_claims_not_machine_readable.md | screenshot claim rows kept as counts only; store per-row
B161 | OPEN    | B161_screenshot_header_values_hand_typed.md | screenshot header BB/RSI/VWAP hand-typed; no check tool
T072 | QUEUED  | T072_volume_context_read_layer.md | time-adjusted volume read for the market guide (observation only)
T073 | QUEUED  | T073_p06_volume_spike_time_bias.md | P06 volume-spike proof time-of-day bias and NO-SOURCE status; Java window only
T092 | OPEN    | T092_screenshot_context_gap.md | what context does a single screenshot get; Opus session
B157 | CLOSED  | B157_screenshot_read_starts_cold.md | prior-context slot + prior falsifier scoring; landed 2026-10-10
B158 | CLOSED  | B158_session_state_thesis_dead.md | thesis line removed from the card (D13); landed 2026-10-10
B160 | CLOSED  | B160_engine_state_at_screenshot_time.md | shot.py engine replays the engine at the shot minute; landed 2026-10-10
B185 | OPEN    | B185_silent_malformed_bugs_row.md | malformed BUGS.md row passes the parser silently; restore B141 + reject over-wide rows
B186 | OPEN    | B186_write_discipline_stray_backup_and_dup_section.md | stray .bak + duplicate section passed all write checks; fix is one-line backup rule + post-write stray scan
B194 | OPEN    | B194_gemini_dispatch_tagging.md | Claude dispatcher lacks explicit tagging/assignment for Gemini-tailored task cards in task queue
B195 | OPEN    | B195_task_mode_block_silent_drop.md | task-mode gate block silently never ran; no receipt, no refusal on three sends; ack and duplicate-rid fix
B196 | OPEN    | B196_aibridge_auto_off_operator_draft.md | auto-OFF on operator draft blocks runs silently; ignore drafts, post a receipt on auto-off
B197 | OPEN    | B197_search_discipline_content_before_absence.md | content search before absence; lessons go in LESSONS_DIGEST.md not apparatus_fixes.md
B198 | OPEN    | B198_aibridge_background_tab_stall.md | hands-free stalls when tab backgrounded; Chrome throttling pauses loop, misfires on wake
