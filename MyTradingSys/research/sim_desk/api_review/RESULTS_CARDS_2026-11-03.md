# Simulator results: one plain card per result file (Haiku 5.5 on the Console Batch API, 2026-11-03)

Source: every `research/sim_desk/results/*.json` (337), jobs built by `research/api_jobs_2026-11-03/build_sim_cards_jobs.py`, batch msgbatch_01VrQRnGRLr21FeMyrzxtt6P. Raw replies: `sim_results_cards_raw.jsonl`. Numbers in a card come only from its JSON; a card is a reading aid, not a verdict of record.

Cost: 508537 in + 134680 out tokens, about 0.59 USD at batch price.

## Totals
| Verdict | Files |
|---|---|
| NO TEXT | 225 |
| UNPARSED | 93 |
| EMPTY | 19 |
| Keep: NO | 17 |
| flagged duplicate params | 0 |

## Cards
| id | Verdict | Keep | Claim | Finding |
|---|---|---|---|---|
| dir-coinglass_field_guide_2026-11-01 | EMPTY | NO, because the file has no trades | CoinGlass wall and depth panels can be mapped to our engines and checked, but this is not evidence of an edge. | In the loaded two days, 191 walls were placed, 1 filled, and 176 pulled; depth within ±1% was -20.4% (asks heavier). |
| dir-cryptocred_s3_2026-11 | EMPTY | NO, because the result has no trades and no outcome was computed. | The 4h CryptoCred S3 redesign cells on BTCUSDT DEV are blocked before any outcome is computed. | Trade rows 0; N about 207 / 200 against a required 540 fills per setup; 6 registered cells; no net-R figure. |
| dir-cryptocred_stop_2026-10-10 | EMPTY | NO, because the file has zero trade rows and no decision value can be drawn from it | Every stop rule tested on the CryptoCred setups is net-negative, so stop placement alone does not make the entry profita | Trade rows in file: 0; the source states no trade count, net-R figure, or test window. |
| dir-gap_g3_shadow_fills_2026-10-18 | EMPTY | NO, the file holds zero tr | G3 GO_LIVE_BAR on shadow fills from the real tape (2026-10-18) | 0 trades in file |
| dir-indicator_audit_2026-10-14 | EMPTY | NO, no trades and no decision | Indicator values match across multiple models, per the committed audit note (card indicator-values-multi-model-audit). | 0 trade rows; no KPIs or net-R figure reported; trust tag MACHINE-OK, not VERIFIED (no non-Claude column filled yet). |
| dir-layer_readiness_2026-10-16 | EMPTY | NO, because the result has no trade rows to evaluate. | Layer readiness census (2026-10-16) lists 9 layers as TRADES, but no trade rows are in this file. | 0 trade rows in file; source states 9 TRADES layers, all passing only through pre_pipeline_sources. |
| dir-malkan_extract_2026-10-15 | EMPTY | NO (EMPTY, the file has no trade list to evaluate). | This is a setup summary of every Malkan setup taught in 6 extracted videos, not a tested trading edge. | 0 trades in the ledger; no net-R figure or test window is stated in the source. |
| dir-malkan_ledger_2026-10 | EMPTY | NO, the source holds no trade list and no decision value. | Malkan's dated-call ledger can be built from his lecture, with RSI-based parity points (Gate 0c audit). | 0 dated trades; trades count 0; the source gives no net-R figure and no test window. |
| dir-news_feeds_2026-10-30 | EMPTY | NO, because the file has no trade rows and no decision value. | The source note sets out what news to watch for MTS, where it comes from, and how fast it arrives (2026-10-30). | 0 trade rows in the file; the source states no trade count, no net-R figure, no test window, and no parameters. |
| dir-setup_review_2026-10 | EMPTY | NO, because the file holds 0 trades and no decision value is measured. | Review sheet of 22 chart setups from Tom and Fabio (2026-10-30); nothing here is tested and no results are claimed. | 0 trades in the file; the source states no net-R figure and no test window. |
| dir-tom_btc_2026-10-13 | EMPTY |  | Tom's BTC trades were reviewed for what to apply, and the plan is to apply them ourselves (2026-10-13). | 0 trade rows in file; the source states no trade count and no net-R figure. |
| dir-trendlines_2026-10-17 | EMPTY | NO, there are no trades and no decision value to act on. | Trend-line study on BTC context and daily charts; the source sets out a rule framework but reports no tested result. | 0 trade rows; no KPIs; no test window or trade count stated; the source reports no net-R figure. |
| dir-vp_pivots_2026-10-09 | EMPTY |  | Tom says volume profiles should not be drawn from pivot points, only from meaningful highs and lows, but he gives no mec | 0 trade rows; the source states no trade count, no net-R figure, and no test window. |
| st-_archive-loose_2026-10-cbp_profile6_result | EMPTY | NO, because the file has no tr | The CBP actionable-6 extraction profile was tested as a backtest. | Trade rows in file: 0. The source states no trade count, no net-R figure, and no test window. |
| st-fractals_2026-10-31-p1_split-result | EMPTY | NO, | Fractals P1 split test on RSI-DIV-MTF and Krown; no edge is claimed or refuted. | No numbers: n, fee-net mean R, and CI are all blocked. The RSI event table holds 643 gross events with no exit and no fees. |
| st-gemini_audits_2026-11-01-fractal_results_blind_read | EMPTY | NO, because the file exports no trade rows and the source holds no trade list. | Blind read audit of the fractal results RESULT.md for six runs (f1 through f4, p1_split, p1b_rsi_feenet). | sample size n 2556 (first value in source, may not be trades); net R after fees -0.305. |
| st-michael_lines_2026-11-result | EMPTY | NO, because the file has no trades | Michael's stated trend lines match trendline_core detector events on BTC, 2022-01-01 to 2024-06-30. | 0 trade rows in file; the source states no trade count and no net-R figure; detector events exist at 5 kinds on 4h/1d. |
| st-no_source_sweep_2026-10-09-result | EMPTY | NO, because there are no trades and the rule has no source to evaluate. | A stop at the previous 1-minute bar high or low (the "No Source Sweep" rule) is in the source files. | No source found in 154 files, and the file holds 0 trade rows. |
| st-setup_alpha_beta_2026-10-10-beta_results | EMPTY | NO, the file has no trades and no decision value. | Liquidity sweep plus CVD absorption event study on Binance BTCUSDT perp, 15m levels and 5m entry | 0 trade rows; no trade count, net-R, or test window stated (window null) |
| ask-p0-65-setup-alpha-beta-backtest | NO TEXT |  |  |  |
| audit-t02_f1_unsafe | NO TEXT |  |  |  |
| audit-t03_planted_edges | NO TEXT |  |  |  |
| audit-t04_clean_room_twin | NO TEXT |  |  |  |
| audit-t08_split_trials | NO TEXT |  |  |  |
| audit-t10_missing_aspects | NO TEXT |  |  |  |
| c26-h1-structural-lower-high | NO TEXT |  |  |  |
| c26-q5-touch-factors | NO TEXT |  |  |  |
| c26-q7-liquidation-bands | NO TEXT |  |  |  |
| c26-q8-cvd-divergence | NO TEXT |  |  |  |
| c26-q9-footprint | NO TEXT |  |  |  |
| desk-cowen_bmsb-0bae3f5d | NO TEXT |  |  |  |
| desk-cowen_bmsb-113933da | NO TEXT |  |  |  |
| desk-cowen_bmsb-235436d9 | NO TEXT |  |  |  |
| desk-cowen_bmsb-245ae944 | NO TEXT |  |  |  |
| desk-cowen_bmsb-24c47838 | NO TEXT |  |  |  |
| desk-cowen_bmsb-74b965eb | NO TEXT |  |  |  |
| desk-cowen_bmsb-79fca995 | NO TEXT |  |  |  |
| desk-cowen_bmsb-808a38e7 | NO TEXT |  |  |  |
| desk-cowen_bmsb-a0c48d6a | NO TEXT |  |  |  |
| desk-cowen_bmsb-d3a470df | NO TEXT |  |  |  |
| desk-cowen_bmsb-d5315728 | NO TEXT |  |  |  |
| desk-cowen_bmsb-f53ed8d7 | NO TEXT |  |  |  |
| desk-fabio_v3-0694292f | NO TEXT |  |  |  |
| desk-fabio_v3-305051dc | NO TEXT |  |  |  |
| desk-fabio_v3-3441877d | NO TEXT |  |  |  |
| desk-fabio_v3-7da588cc | NO TEXT |  |  |  |
| desk-fabio_v3-820e427d | NO TEXT |  |  |  |
| desk-fabio_v3-a955213e | NO TEXT |  |  |  |
| desk-fabio_v3-b3972cec | NO TEXT |  |  |  |
| desk-fabio_v3-b6b13619 | NO TEXT |  |  |  |
| desk-fabio_v3-cc240f2b | NO TEXT |  |  |  |
| desk-fabio_v3-dd786e4e | NO TEXT |  |  |  |
| desk-krown-304c64f8 | NO TEXT |  |  |  |
| desk-krown-634f1a37 | NO TEXT |  |  |  |
| desk-krown-8f1747e4 | NO TEXT |  |  |  |
| desk-krown-b092f221 | NO TEXT |  |  |  |
| desk-levels-2b122b99 | NO TEXT |  |  |  |
| desk-levels-50dbba30 | NO TEXT |  |  |  |
| desk-levels-f213f66e | NO TEXT |  |  |  |
| desk-levels-fb213d4c | NO TEXT |  |  |  |
| desk-meta_label_fabio_c | NO TEXT |  |  |  |
| desk-meta_label_fabio_c_dev_ext | NO TEXT |  |  |  |
| desk-meta_label_tom_vp | NO TEXT |  |  |  |
| desk-rsi-2a5162fe | NO TEXT |  |  |  |
| desk-rsi-593e9c2d | NO TEXT |  |  |  |
| desk-rsi-a6a97db2 | NO TEXT |  |  |  |
| desk-rsi-db26327f | NO TEXT |  |  |  |
| desk-tom_vp-0fd1a3c0 | NO TEXT |  |  |  |
| desk-tom_vp-20c09090 | NO TEXT |  |  |  |
| desk-tom_vp-23158b32 | NO TEXT |  |  |  |
| desk-tom_vp-4c1bc9c3 | NO TEXT |  |  |  |
| desk-tom_vp-5568b609 | NO TEXT |  |  |  |
| desk-tom_vp-55a87543 | NO TEXT |  |  |  |
| desk-tom_vp-8639b801 | NO TEXT |  |  |  |
| desk-tom_vp-bcb15fd4 | NO TEXT |  |  |  |
| desk-tom_vp-c8d2f341 | NO TEXT |  |  |  |
| desk-tom_vp-d21ae701 | NO TEXT |  |  |  |
| desk-tom_vp-d249f15a | NO TEXT |  |  |  |
| desk-tom_vp-f0e6a008 | NO TEXT |  |  |  |
| desk-wavetrend-9f0363ce | NO TEXT |  |  |  |
| desk-wavetrend-a6e775a2 | NO TEXT |  |  |  |
| desk-wavetrend-bddd48ea | NO TEXT |  |  |  |
| desk-wavetrend-d879ce95 | NO TEXT |  |  |  |
| dir-audits_2026-10-26 | NO TEXT |  |  |  |
| dir-autopilot_2026-10-16 | NO TEXT |  |  |  |
| dir-bb_state_map_2026-10 | NO TEXT |  |  |  |
| dir-bb_top_reversal_2026-10-18 | NO TEXT |  |  |  |
| dir-bg_process_audit_2026-10-28 | NO TEXT |  |  |  |
| dir-bollinger_2026-10-14 | NO TEXT |  |  |  |
| dir-c26_roadmap_2026-11-01 | NO TEXT |  |  |  |
| dir-cloud_2026-10-06 | NO TEXT |  |  |  |
| dir-context_loading_wiring_2026-10 | NO TEXT |  |  |  |
| dir-context_null_2026-10-16 | NO TEXT |  |  |  |
| dir-coordination_audit_20261026 | NO TEXT |  |  |  |
| dir-core_readiness_2026-09-27 | NO TEXT |  |  |  |
| dir-cowen_q4_2026-10-31 | NO TEXT |  |  |  |
| dir-critical_test_wave1_2026-10-30 | NO TEXT |  |  |  |
| dir-cryptocred_htf_2026-10 | NO TEXT |  |  |  |
| dir-cryptocred_ledger_2026-10 | NO TEXT |  |  |  |
| dir-design_cards_2026-10-26 | NO TEXT |  |  |  |
| dir-extraction_ledger_2026-10 | NO TEXT |  |  |  |
| dir-fabio_asr_2026-10-16 | NO TEXT |  |  |  |
| dir-fabio_date_match_2026-10-18 | NO TEXT |  |  |  |
| dir-fabio_video_search_2026-10-17 | NO TEXT |  |  |  |
| dir-fable_audit_2026-10-16 | NO TEXT |  |  |  |
| dir-fable_audit_2026-10-18 | NO TEXT |  |  |  |
| dir-fable_audit_2026-10-20 | NO TEXT |  |  |  |
| dir-fable_setups_2026-10-19 | NO TEXT |  |  |  |
| dir-fix_verification_2026-10-28 | NO TEXT |  |  |  |
| dir-flow_layers_concepts_2026-10-28 | NO TEXT |  |  |  |
| dir-gemini_audits_2026-10-30 | NO TEXT |  |  |  |
| dir-gemini_audits_2026-10-31 | NO TEXT |  |  |  |
| dir-gemini_burn_2026-10-25 | NO TEXT |  |  |  |
| dir-gemini_burn_2026-10-31 | NO TEXT |  |  |  |
| dir-gpt_burn_2026-10-24 | NO TEXT |  |  |  |
| dir-gpt_rederive_2026-10-26 | NO TEXT |  |  |  |
| dir-habib_plan_imbalance_2026-10-20 | NO TEXT |  |  |  |
| dir-imbalance_2026-10-10 | NO TEXT |  |  |  |
| dir-jala_layer_2026-10-31 | NO TEXT |  |  |  |
| dir-krown_audit_2026-10-22 | NO TEXT |  |  |  |
| dir-krown_free_2026-10-31 | NO TEXT |  |  |  |
| dir-krown_malkan_g3_2026-10-16 | NO TEXT |  |  |  |
| dir-krown_ta101_2026-10-13 | NO TEXT |  |  |  |
| dir-layer_combo_verdict_2026-10-13 | NO TEXT |  |  |  |
| dir-layer_review_2026-10-26 | NO TEXT |  |  |  |
| dir-malkan_div_flags_2026-10-28 | NO TEXT |  |  |  |
| dir-meta_label_roadmap_2026-10-31 | NO TEXT |  |  |  |
| dir-meta_label_tom_fabio_2026-10-31 | NO TEXT |  |  |  |
| dir-mfe_exit_2026-10-13 | NO TEXT |  |  |  |
| dir-mts_flow_audit_2026-10-13 | NO TEXT |  |  |  |
| dir-multi_tf_bias_2026-10-18 | NO TEXT |  |  |  |
| dir-oi_pivot_2026-10-26 | NO TEXT |  |  |  |
| dir-opus_run_design_2026-10-28 | NO TEXT |  |  |  |
| dir-overhead_cut_2026-10-28 | NO TEXT |  |  |  |
| dir-overnight_2026-10-16 | NO TEXT |  |  |  |
| dir-pit_levels_2026-10-16 | NO TEXT |  |  |  |
| dir-pivot_pattern_audit_2026-10-14 | NO TEXT |  |  |  |
| dir-pizzino_layer_2026-10-27 | NO TEXT |  |  |  |
| dir-positioning_c1_2026-10 | NO TEXT |  |  |  |
| dir-qriptal_2026-10-10 | NO TEXT |  |  |  |
| dir-reviews_2026-10-26 | NO TEXT |  |  |  |
| dir-rsi_deep_buy_2026-10-19 | NO TEXT |  |  |  |
| dir-rsi_kurisko_2026-10-09 | NO TEXT |  |  |  |
| dir-screenshot_context_2026-10-10 | NO TEXT |  |  |  |
| dir-session_flow_context_2026-10-18 | NO TEXT |  |  |  |
| dir-test_hunt_2026-10-31 | NO TEXT |  |  |  |
| dir-testnet_cotrade_2026-10-31 | NO TEXT |  |  |  |
| dir-tom_correlation_trick_2026-10-26 | NO TEXT |  |  |  |
| dir-tom_dax_what_is_proven_2026-10-13 | NO TEXT |  |  |  |
| dir-tom_direction_health_audit_2026-10-17 | NO TEXT |  |  |  |
| dir-tom_fabio_concepts_2026-10-29 | NO TEXT |  |  |  |
| dir-tom_fabio_review_2026-10-31 | NO TEXT |  |  |  |
| dir-video_priority_2026-10-15 | NO TEXT |  |  |  |
| eagle-c21-bb-pierce | NO TEXT |  |  |  |
| eagle-c23-daily-shorts | NO TEXT |  |  |  |
| eagle-c24-oi-after-flush | NO TEXT |  |  |  |
| eagle-c25-stochrsi | NO TEXT |  |  |  |
| eagle-c26-fade | NO TEXT |  |  |  |
| eagle-c26-magnet | NO TEXT |  |  |  |
| eagle-c26-ride | NO TEXT |  |  |  |
| eagle-c27-wavetrend | NO TEXT |  |  |  |
| eagle-c28-wt-structure | NO TEXT |  |  |  |
| eagle-c29-wt-lower-tf | NO TEXT |  |  |  |
| eagle-c30-wt-rsi-div | NO TEXT |  |  |  |
| eagle-preus-pullback | NO TEXT |  |  |  |
| fractals-f1-swing-confluence | NO TEXT |  |  |  |
| fractals-f2-hurst-gate | NO TEXT |  |  |  |
| fractals-f3-phase-analogs | NO TEXT |  |  |  |
| fractals-f4-8h-state-analogs | NO TEXT |  |  |  |
| fractals-p1b-rsi-by-phase | NO TEXT |  |  |  |
| fractals-phase-tag | NO TEXT |  |  |  |
| krown-s8-e2-desk-crosscheck | NO TEXT |  |  |  |
| ledger-context_factors_2026-10-16-trials-csv | NO TEXT |  |  |  |
| ledger-context_factors_pit_2026-10-16-trials-csv | NO TEXT |  |  |  |
| ledger-layer_lab-trials-md | NO TEXT |  |  |  |
| ledger-mal_bb_mid_engulf_2026-10-16-trials-csv | NO TEXT |  |  |  |
| ledger-opr_bb_mtf_center_2026-10-16-trials-csv | NO TEXT |  |  |  |
| ledger-opr_preopen_tops_2026-10-16-trials-csv | NO TEXT |  |  |  |
| levels_ladder | NO TEXT |  |  |  |
| lm-alpha | NO TEXT |  |  |  |
| lm-bigmoves-a | NO TEXT |  |  |  |
| lm-candle-p0 | NO TEXT |  |  |  |
| lm-candle-p1 | NO TEXT |  |  |  |
| lm-dax-smoke | NO TEXT |  |  |  |
| lm-eur-low-us-sweep-followups-20261018 | NO TEXT |  |  |  |
| lm-fabio-of | NO TEXT |  |  |  |
| lm-fabio-v3 | NO TEXT |  |  |  |
| lm-fires-b1 | NO TEXT |  |  |  |
| lm-l1-d3 | NO TEXT |  |  |  |
| lm-l1-fabio | NO TEXT |  |  |  |
| lm-lc-sizing-quick-20261014 | NO TEXT |  |  |  |
| lm-oi-delta | NO TEXT |  |  |  |
| lm-pitchfork-1d-20261019 | NO TEXT |  |  |  |
| lm-pitchfork-4h-vp-20261028 | NO TEXT |  |  |  |
| lm-price-cvd-div-1m5m-20261014 | NO TEXT |  |  |  |
| lm-q33 | NO TEXT |  |  |  |
| lm-rsi-div-mtf | NO TEXT |  |  |  |
| lm-t055-c1 | NO TEXT |  |  |  |
| lm-t055-c3 | NO TEXT |  |  |  |
| lm-t087 | NO TEXT |  |  |  |
| lm-tom-core-0929 | NO TEXT |  |  |  |
| lm-tom-core-1007 | NO TEXT |  |  |  |
| lm-tom-core-bt | NO TEXT |  |  |  |
| lm-tom-vp-phase2 | NO TEXT |  |  |  |
| lm-tom-vp-return | NO TEXT |  |  |  |
| lm-vol-v1 | NO TEXT |  |  |  |
| lm-vol-v2 | NO TEXT |  |  |  |
| lm-vol-v3 | NO TEXT |  |  |  |
| lm-vol-v4 | NO TEXT |  |  |  |
| lm-volume | NO TEXT |  |  |  |
| malkan-div-breaks | NO TEXT |  |  |  |
| meta-label-breaks | NO TEXT |  |  |  |
| st-carry_basis_2026-10-18-result | NO TEXT |  |  |  |
| st-context_factors_2026-10-16-result | NO TEXT |  |  |  |
| st-cowen_q4_2026-10-31-event_study-result | NO TEXT |  |  |  |
| st-fable_run6_powered_prereg-result | NO TEXT |  |  |  |
| st-fast_track_2026-09-27-pbo_019_result | NO TEXT |  |  |  |
| st-gemini_audits_2026-11-01-older_results_blind_read | NO TEXT |  |  |  |
| st-gemini_audits_2026-11-01-recent_results_blind_read | NO TEXT |  |  |  |
| st-gross_effect_screen_2026-10-15-result | NO TEXT |  |  |  |
| st-imbalance_qriptal_2026-10-16-filter-result | NO TEXT |  |  |  |
| st-jala_layer_2026-10-31-trigger_result | NO TEXT |  |  |  |
| st-layer_relations_2026-10-results_tables | NO TEXT |  |  |  |
| st-lh_break_2026-10-30-result | NO TEXT |  |  |  |
| st-live_not_fired_2026-10-29-result | NO TEXT |  |  |  |
| st-meta_label_breaks_2026-10-31-ext_result | NO TEXT |  |  |  |
| st-meta_label_dev_ext_2026-10-31-result | NO TEXT |  |  |  |
| st-netdelta_panel_2026-10-18-result | NO TEXT |  |  |  |
| st-opr_bb_mtf_center_2026-10-16-result | NO TEXT |  |  |  |
| st-opr_preopen_tops_2026-10-16-result | NO TEXT |  |  |  |
| st-opr_weekly_low_round_sweep_2026-10-16-result | NO TEXT |  |  |  |
| st-prev_close_break_2026-10-29-result | NO TEXT |  |  |  |
| st-published_strats_2026-10-13-results | NO TEXT |  |  |  |
| st-reclaim_close_stop_2026-11-result | NO TEXT |  |  |  |
| st-tom_correlation_trick_2026-10-26-result | NO TEXT |  |  |  |
| st-tom_v2_gross_first_2026-11-result | NO TEXT |  |  |  |
| st-transcript_inventory_2026-10-09-result | NO TEXT |  |  |  |
| st-us_open_levels_2026-10-30-result | NO TEXT |  |  |  |
| st-wlow_bounce_bbrsi60_2026-10-16-result | NO TEXT |  |  |  |
| t06_cost_fill | NO TEXT |  |  |  |
| t07_stale_verdicts | NO TEXT |  |  |  |
| t09_live_parity | NO TEXT |  |  |  |
| tom-corr-divergence-backtest | NO TEXT |  |  |  |
| wavetrend_atlas | NO TEXT |  |  |  |
| ask-p0-45-tf-break-event-study | UNPARSED |  |  |  |
| audit-t01_data_forensics | UNPARSED |  | The bars the DSA studies read match the bars that actually happened in the 2022-01-01 to 2026-09-26 window. | 905 open and 847 volume day-level mismatches between the 1m resample and raw_1d; max volume rel-diff 12%; five studies point to a missing fundingRate path; Krow |
| audit-t02_lookahead_time | UNPARSED |  | T02 checks the DSA backtest for look-ahead and time-alignment bias, and the source says the audit shows one earlier resu | 27 layers tested; 5 N |
| audit-t05_placebo_nulls | UNPARSED |  | What does chance alone produce in this audit |  |
| c26-q10-path-distribution | UNPARSED |  | The take-out's price path (overshoot, wait, MAE, MFE, L1) can set a stop and target grid for a short after the reclaim. |  |
| c26-range-ladder | UNPARSED |  | A martingale short ladder on 1m-5m RSI |  |
| desk-krown-a2e514ff | UNPARSED |  | Exploratory desk try (not the pre-registered study) of the S5 21/55 EMA cross on 4h BTCUSDT or ETHUSDT, 2R target, fees  |  |
| desk-krown-f70f0e73 | UNPARSED |  | Exploratory desk try of the S5 4h MA cross (2R target, fees and slippage) on BTCUSDT or ETHUSDT, long only, UTC 8-16, no |  |
| dir-asks_audit_2026-10-30 | UNPARSED |  | Operator asks ledger for 2026-09-28 to 2026-10-30 records the asks made and their status, as copied from the committed s |  |
| dir-audit_inventory | UNPARSED |  | This is a read-only inventory of which trading-system audits exist and what they cover, not a strategy test. | The 2026-09-27 core readiness audit cites a SetupCandidatesBuilder proof count of D |
| dir-audits | UNPARSED |  | Session Start Ritual Audit vs AI-Health Token Goals (B183) | 0 trade rows; no trade count, net-R, or test window stated; source verdict line reads only "Date: 2026- |
| dir-backtest_gap_review_2026-10-13 | UNPARSED |  | The backtest review asks whether our backtests are sound: enough power, out-of-sample testing, realistic costs, and a co | The frozen DAX bar has 7-35 % power at 100-150 trades, and "FAIL on dev = stop" makes that miss final; the source gives 150 as the first trade count; the window |
| dir-binance_backtesting_2026-10-18 | UNPARSED |  | Reliable backtesting for Binance BTC and the general research standard; the file does not show a strategy result. | Trade rows in file: 0; the source states no trade count, net-R, or parame |
| dir-btc_ma_2026-10-03 | UNPARSED |  | Whether BTC moving-average rules show out-of-sample predictability, per the consolidated Q_ALL pass |  |
| dir-ci_audit_2026-10-31 | UNPARSED |  | ci_watch MIN_STREAK: should it block after the first red or the second? |  |
| dir-cloud_ai_health_2026-10-26 | UNPARSED |  | The source note attributes the Claude/cloud AI health problems to budget press |  |
| dir-coinglass_survey_2026-10-29 | UNPARSED |  | CoinGlass public-page survey of 2026-10-29 (free pages, read-only, no login), not a strategy backtest. |  |
| dir-coinglass_usage_2026-10-28 | UNPARSED |  | The source note proposes an order-flow idea: negative-delta new highs and the first retest of stacked-imbalance zones on | 0 trade rows in the file; the source states no trade count and no net-R figure. |
| dir-confluence_read_2026-10-17 | UNPARSED |  | Market context around the operator's 2026-10-16 reads, taken from the committed source note rather than a trade test. | 0 trades in file (n=0); the prior-day value-area failed-auction pattern was blocked by the power gate with n=0, so no output exists for these days. / Verd |
| dir-dedupe_audit_2026-10 | UNPARSED |  | Infra dedupe audit of hooks, startup and cleanup, device tasks, broadcast |  |
| dir-dsa_bridge_2026-10-27 | UNPARSED |  | DSA bridge (AIBridge) status on every MTS machine, dated 2026-10-27, is an operator order to run a verification check, n | No trades exported and no net-R figure, test window, or pass/fail reason is stated; the only number is the 28-row check list. / |
| dir-dsa_bridge_fix_plan_2026-10-31 | UNPARSED |  | DSA bridge fix plan (AIBridge 0.7.3), 2026-10-31, a plan for fixing the b |  |
| dir-dsa_bridge_keepalive_2026-10-17 | UNPARSED |  | The DSA bridge keep-alive decision, dated 2026-10-17, was to not add an audio emitter. |  |
| dir-eagle_eyes_picture_2026-10-28 | UNPARSED |  | This file is a plan for redesigning MTS alerts, not a trade test of a BTC strategy. | 0 trades in the file; the source gives no trade |
| dir-fabio_cvd_2026-10-30 | UNPARSED |  | Fabio and his channel mates' CVD and delta concepts can be used for BTC and other markets. | 0 trade rows in file; the |
| dir-fabio_v3_s28_diffs_2026-11-01 | UNPARSED |  | This brief compares the Fabio v3 code against the s28.6 worked examples in the spec, not a strategy's trading performanc |  |
| dir-fable_run_design_2026-10-28 | UNPARSED |  | Freeze one pre-registered, fee-net test that confirms or kills the BTC trading-edge program, using event counts only. |  |
| dir-fable_runs_2026-10-28 | UNPARSED |  | R1 "Edge or Stop" (Fable 5.1 |  |
| dir-g3_marks_2026-10-16 | UNPARSED |  | The G3 marking pack, first batch, is ready to mark; it is a thought experiment with no trade list. |  |
| dir-gap_audit_2026-10-19 | UNPARSED |  | The MTS critical-gap audit (2026-10-19) found a fail-open defect in StateCodeEmitter after tick gaps. |  |
| dir-gap_g7_stop_slippage_2026-10-18 | UNPARSED |  | Gap G7 stop-slippage proxy on BTCUSDT (Binance aggT |  |
| dir-gemini_audits_2026-11-02 | UNPARSED |  | The source note's audit of the Gemini grandfather API re-run (blind read) is reported as written, not independently test |  |
| dir-gemini_burn_2026-10-24 | UNPARSED |  | Every parameter, threshold, and formula in the backtesting literature and repo is cataloged and labeled as sourced or as | The file reports no trade count and no net-R figure. It states the current tuning relies on a naive boot |
| dir-golas_2026-10 | UNPARSED |  | Internet consensus on indicator settings for BTC (GOLAS-C, ledger P0-04) |  |
| dir-gpt_lane_review_2026-10-15 | UNPARSED |  | This read-only plan reviews which GPT model the NUC uses and sets a cap on automatic runs, and it does not report a trad |  |
| dir-health_checks_run_2026-10-28 | UNPARSED |  | The health-check triage report lists two script issues: an unguarded stdin read that can hang, and a batch hygiene runne | 0 trades in file; the only figures are a 5-second per-check subprocess timeout and a 1500-second |
| dir-krown_capture_2026-10-16 | UNPARSED |  | Krown's draft rules from a pilot of 6 transcripts outside the TA 101 corpus, including a daily-video event-study method. | 6 transcripts, 0 trade rows in the file, no trade count, no net-R figure, and no test window stated |
| dir-kurisko_2026-10-18 | UNPARSED |  | Pre-registered |  |
| dir-layer_rebuild_2026-10-15 | UNPARSED |  | The source is a prompt pack for a Fable audit session asking whether the setup catalogue is faithful and complete and wh |  |
| dir-level_ledger_2026-10-16 | UNPARSED |  | The source note reports building the level ledger (PIT_CONTRACT section 1) and verifying the Java zones, dated 2026-10-1 |  |
| dir-liquidation_layer_2026-10-28 | UNPARSED |  | The liquidation layer (CoinGlass BTCUSDT leverage heatmap and Hyperliquid liquidation map) is a modelled estimate of whe | 0 trade rows; no tr |
| dir-live_loop_timeouts_2026-10-18 | UNPARSED |  | Live-loop network timeouts are handled by a 30-minute classpath retry backoff and a 180 s snapshot fallback, as audited  |  |
| dir-malkan_rsi_2026-09-28 | UNPARSED |  | The source describes RSI divergence rules, where a negative divergence signals a bearish reversal and a daily RSI sustai |  |
| dir-malkan_rsi_2026-10-31 | UNPARSED |  | The source document compiles RS |  |
| dir-malkan_universe_2026-10 | UNPARSED |  | Single-stock Indian-equity tests are underpowered; the source says a single stock gives too few events (below N = 100) t | Daily setups give about 6 to 42 events in 10 years on one stock and weekly |
| dir-non_core_layer_audit_2026-10-12 | UNPARSED |  |  |  |
| dir-nuc_restart_2026-10-28 | UNPARSED |  | The audit register flags Tom rule-set wiring gaps and quote mismatches, with no trade result behind it. |  |
| dir-observer_2026-10-15 | UNPARSED |  | Observer report (2026-10-15) says cross-session align |  |
| dir-pitchfork_2026-10-19 | UNPARSED |  | Pitchfork and Volume Profile 4-h |  |
| dir-positioning_flowhorse_2026-10 | UNPARSED |  | FlowHorse positioning (liquidation cascade, OI pickup, news second move) is a hypothesis that fails Gate 0c and Gate 0d. | 0 trade rows |
| dir-pre_us_failed_break_2026-10 | UNPARSED |  | Pre-registered pre-US failed-break short on BTC 1m, exploratory; docs only, no rule adopted. |  |
| dir-prob_dist_layer_brief_2026-10-16 | UNPARSED |  | The source brief sets out a design for a probability-distribution layer for an operator talk, with no test run and no ne |  |
| dir-review_chart_cards_2026-10-17 | UNPARSED |  | The chart checklist and two chart cards were audited for accuracy, not tested as a trading rule. |  |
| dir-role_flow_2026-10-23 | UNPARSED |  | The Option A end-to- |  |
| dir-rolling_session_cost_2026-10 | UNPARSED |  | Rolling |  |
| dir-rsi_2a_2026-10-09 | UNPARSED |  | RSI 2a/2a' ideas were written up against Malkan's sources, and the earlier RSI backtests may not test Malkan's own exit. |  |
| dir-rumers_2026-11-01 | UNPARSED |  | Rumers rules can be tested with a fee and power gate before any rule runs. | 6 of 12 stop/shape cells are dead on fees (net <= 0 R), including every 0.3 |
| dir-screenshots | UNPARSED |  | BTCUSDT screenshot set from 2026-10-07 (set 29ff |  |
| dir-self_heal_2026-10-28 | UNPARSED |  | The 2026-10-28 MTS doctor report for the Self Heal family, copied from its source note, with a note that it may duplicat | 30 runs: success 25, failure 5; newest finished run: success; two RED runs at 10-28T13:01 and 10-28T12:37 failed offline gates. |
| dir-setup_catalog_2026-10-15 | UNPARSED |  | This file is a catalog of the trade setups Tom and Fabio describe, copied from a committed source note, not a test of wh |  |
| dir-shipping_speed_2026-10-19 | UNPARSED |  | Shipping verification (19 Oct 2026) passed its functional checks |  |
| dir-station_c_rolling_audit_20261026 | UNPARSED |  | Repair ownership, current-state dispatch, and truthful completion before increasing the wake rate, then test a bounded r |  |
| dir-tom_check_set_2026-10-18 | UNPARSED |  | The Tom CHECK set is frozen at 2 trades (S7/T11 and S8/T12), with the trade recaps checked from |  |
| dir-two_workers_collision_2026-10-30 | UNPARSED |  |  |  |
| dir-us_open_oos_2026-10-30 | UNPARSED |  | The original US-open session pattern on BTCUSDT was re-tested on 2020-01 to 2021-12 out-of-sample data | The move is smaller than originally reported (1.36- |
| dir-v1_plan_2026-10-20 | UNPARSED |  | MTS v1 plan (Thinker, 2026-10-20) is a thought experiment; the source states no claim beyond its title. |  |
| dir-wiring_audit_2026-10 | UNPARSED |  | This is a wiring audit that checks quotes copied into a CSV, so it does not test a trading strategy. |  |
| dir-worktree_triage_2026-10-20 | UNPARSED |  | JIS-NB worktree triage on 2026-10-20 cleaned up stale git worktrees; this is maintenance, not a trading result. | 18 of |
| dir-yt_feed_2026-10-31 | UNPARSED |  | Crypto Crew University (@CryptoCrewUniversity) stated BTC and alt entry rules, levels, and indicator setups, extracted f | 8 videos read, 8 English transcripts captioned, 0 UNVERIFIED, 0 trade rows in file. / |
| ledger-eur_low_us_sweep_followups_2026-10-18-trials-csv | UNPARSED |  | The trial ledger for EUR low US sweep follow-ups logs the variants |  |
| ledger-imbalance_qriptal_2026-10-16-filter-trials-csv | UNPARSED |  | Trial ledger for the imbalance qriptal filter (2026-10-16) recording the variants tried. | 30 trial r |
| ledger-opr_weekly_low_round_sweep_2026-10-16-trials-csv | UNPARSED |  | The OPR weekly low round sweep ran 12 trial variants, as logged in the committ |  |
| lm-bigtrade-exit | UNPARSED |  | The live |  |
| lm-candle-close-dev-20261014 | UNPARSED |  | Close sequences at prior 4h, day, and week highs and lows may predict next-hour BTC direction. |  |
| lm-candle-d19 | UNPARSED |  | D19 4h long-only bullish engulfing/kicker entries at |  |
| lm-capture-matrix | UNPARSED |  | The big-move capture matr |  |
| lm-eur-low-us-sweep-20261014 | UNPARSED |  | A retested 24h low gets broken in the US window, so a short and a 1- |  |
| lm-market-guide | UNPARSED |  | This is a read-only market guide digest that summarises indicator and candle state as observation only, with no trading  |  |
| lm-tom-diag-btc | UNPARSED |  | Tom probe diagnostics on a BTC backtest |  |
| lm-vp-pivot-p2 | UNPARSED |  |  |  |
| st-b154_stratified_2026-10-09-result | UNPARSED |  | B154 stratified verdicts, split by UTC session and by regime, from source note st-b154_stratified_2026-10-09-result / |  |
| st-bb_dance_2026-10-30-result | UNPARSED |  | Bollinger "dance" exits: does leaving early on a take-profit give up the big leg? |  |
| st-bb_pierce_force_2026-10-29-result | UNPARSED |  | A 15m Bollinger pierce near the US open, with its "force" and whether it reaches the prior-day level, is t |  |
| st-bounce_shift_2026-10-30-result | UNPARSED |  | Does an oversold 5m BTCUSDT casc |  |
| st-drop_bounce_2026-10-29-result | UNPARSED |  | Fast 1m BTCUSDT drops followed by a bounce to the BB mid, with the next 4 hours tracked, as descriptive counts only |  |
| st-dsa_bridge_fix_plan_2026-10-31-c7_nuc_results | UNPARSED |  |  |  |
| st-large_trade_absorption_2026-10-30-result | UNPARSED |  | Large trades on 5m bars were counted to see whether absorption reversed price, as textbook absorption predicts. | 0 tr |
| st-mal_bb_mid_engulf_2026-10-16-result | UNPARSED |  | Midline bounce plus bearish |  |
| st-oi_side_2026-10-30-result | UNPARSED |  | Which side open interest is picking, using descriptive counts only (no fees, no edge claim) | n = 35963 windows; every row's direction sits between 48% and |
| st-pre_us_squeeze_2026-10-29-result | UNPARSED |  | Just before the US session, price is contracting. The question is what the price does next, with the 15m BTCUSDT Bolling | Phase (F6) does not change direction beyond noise. Squ |
| st-t090_7h_2026-10-09-result | UNPARSED |  | T090 7h research and T088 lead robustness check; the source's verdict is NOT robust. |  |
| st-volume_2026-10-09-v0_results | UNPARSED |  | V0 is a BTC volume data-QA, magnitude, and time-map check over 2020-01-01 to 2024-06-30, with no event forward return co |  |
| st-wt30_sequence_2026-10-30-result | UNPARSED |  | Describes how |  |

Noticed: 225 replies came back without text (max_tokens 400 spent before any output: rerun those with max-tokens 800 if needed).
