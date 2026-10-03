# ITEMS INDEX
# One line per item. Boot-loaded. Read a full item doc only when its
# row is the active task.
#
# Format: <id> | <status> | <file> | <one-line state>

B058 | CLOSED  | B058_floor_reaction_mode.md | floor-reaction mode; receipt in BUGS row
B059 | OPEN    | B059_rank1_zone_drift.md | pf_vp bin-edge drift; fix landed 2026-09-24, live tape pending
B062 | CLOSED  | B062_alert_direction_position.md | position-aware alert gating; landed
B063 | OPEN    | B063_divergence.md | decision: restore divergence in schema, or deprecate
B064 | CLOSED  | B064_supervisor_stop_flag.md | supervisor_stop.flag retired 2026-09-24, loop_stop.flag only
B065 | CLOSED  | B065_stale_swing_consumer.md | stale-swing rejection in extractZones + stop selection; landed
B066 | OPEN    | B066_rank1_distance_gate.md | rank-1 shown at trigger_ready while 150 pts from price; split from B059
T034 | OPEN    | T034_positioning_states.md | 4 positioning flags; blocked on Rule 33 readers + output type
T035 | CLOSED  | T035_multi_venue_cvd.md | DEFER - SCREENER module, no Tom source
T037 | BLOCKED | T037_test_coverage_gap.md | spec delivered W2; pom edit pending operator
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
B070 | OPEN    | B070_crypto_demote.md | demote UTC 00:00 anchor + 0.75 slippage from gating; split from B067
T048 | OPEN    | T048_satellite_framework.md | exchange API layer active (Deribit); freeze lifted 2026-09-26; satellites follow
T049 | CLOSED  | T049_nuc_worker_v2.md | Qwen decommissioned 2026-10-01; NUC lane retired; AIBridge replaces run-command surface
T050 | OPEN    | T050_deribit_execution_layer.md | Deribit execution layer, phase 1 (read-only testnet) scaffolded 2026-09-26
T051 | PARKED  | T051_backtest_parked.md | backtest on MTS raw verdict done; parked by operator 2026-09-26; resumes after T050 ph4 + B071 fixed
B071 | CLOSED  | B071_fail_open_proof_direction.md | fail-open fix applied live 2026-09-27 (harness-verified, PS execution unconfirmed); was: Python error defaulted proof-direction to "aligned"
B072 | OPEN    | B072_l2_input_validation.md | L2 input validation absent for current_price "x" or None in build_math_object (F10)
B073 | OPEN    | B073_net_rr_rounding.md | net_rr rounding inconsistency: output 2dp, sanity check unrounded (F11)
B074 | OPEN    | B074_rule_order_dependence.md | rule-order dependence: contradiction cap runs before broken-value override (F12)
B075 | OPEN    | B075_historical_mode_unfit.md | historical mode unfit for backtesting; zeroes flow fields, look-ahead leak (F7)
B076 | OPEN    | B076_setup_confirmed_unreachable.md | SETUP_CONFIRMED unreachable; Compute-Verdict never emits it (F9)
B077 | CLOSED  | B077_stop_order_wrong_type.md | stop_market via deribit_orders.py; closed 5e387a1; receipt in BUGS row
B078 | CLOSED  | B078_cancel_all_by_label_overscope.md | cancel_by_label is label-scoped server-side; closed 5e387a1; receipt in BUGS row
B079 | CLOSED  | B079_caps_check_not_enforced.md | caps enforced in executor.py; closed 5e387a1, b05c1cf; receipt in BUGS row
T052 | OPEN    | T052_setup_confirmed_trigger.md | define a Tom-cited trigger for SETUP_CONFIRMED per operator D6b ruling
T059 | OPEN    | T059_paste_size_guard.md | auto-split SESSION_PASTE at 80 KB; NUC 121 running
T053 | OPEN    | T053_two_account_hedge_scalping.md | two-account hedge / leveraged scalping research; ask restated 2026-09-28
T054 | OPEN    | T054_us_session_news_correlation.md | US session / pre-market alerts, US-equity correlation, news sentiment; filed 2026-09-28
T055 | OPEN    | T055_positioning_flow_and_proven_setups.md | Net/New Longs and Shorts research plus proven BTC setups; filed 2026-09-28
T056 | OPEN    | T056_qwen_audit_program.md | Qwen regular auditing program; design at research/fast_track_2026-09-27/QWEN_AUDIT_PROGRAM.md
T057 | OPEN    | T057_simplify_declutter.md | simplify / optimize / declutter; follows DEV_VELOCITY_AUDIT.md 2026-09-27
T058 | OPEN    | T058_broken_extremes_sweep_vs_continuation.md | broken lows/highs by timeframe: continuation vs liquidity sweep; filed 2026-09-29
T060 | OPEN    | T060_low_volatility_btc.md | low-volatility anomaly; test whether trailing realized-vol rank predicts BTC forward return
T061 | OPEN    | T061_wavetrend_lazybear.md | WaveTrend with Crosses [LazyBear]; integrate as separate indicator layer
B080 | CLOSED  | B080_dsa_pace_hourly_cap.md | stale/future/non-epoch entries filter + self-heal in pacing_block; regression tests
B081 | CLOSED  | B081_fee_source_conflict.md | fees.py single source; receipt 1ec7d8f, 547 tests pass
B082 | CLOSED  | B082_qwen_feeder_missing.md | task deleted; Qwen decommissioned 2026-10-01
T062 | CLOSED  | T062_deprecate_manager.md | deprecate mts-manager; superseded by DSA-composed CL prompts
B083 | OPEN    | B083_prompt_check_gate.md | prompt_check.ps1 gate; 6 of 8 prompt defects repeat 2026-10-02; pending since 2026-10-02
B084 | OPEN    | B084_book_imbalance_zero_origin.md | origin of 0.0 in Python proof block unverified; 13295c8 WIP-unverified load-bearing
B085 | OPEN    | B085_tom_bt_proof5_skew.md | proof-5 pool skew 215 short:105 long unexplained; second contradiction path (last_3_delta) affects longs
B086 | CLOSED  | B086_dispatcher_second_writer.md | dispatcher demo launched a second CL writer; one-writer-per-file-set violated; Claude decides fix
B087 | CLOSED  | B087_pick_task_repick.md | pick_task.py re-picks same row each wake; two smaller flags attached; Claude decides fixes
# END
