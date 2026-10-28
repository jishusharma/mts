| harness | canary | n | expected (mean, pct) | got (mean, pct) | max abs diff | status | note |
|---|---|---|---|---|---|---|---|
| bt_engine.simulate_trade | a_zero_drift | 83 | -0.018655 | -0.018655 | 0.000000 | PASS |  |
| tom_bt.sim_limit_trade | a_zero_drift | 83 | -0.018655 | -0.018655 | 0.000000 | PASS |  |
| run_t055.score_trades | a_zero_drift | 83 | -0.018655 | -0.018655 | 0.000000 | PASS |  |
| screen.compute_cells | a_zero_drift | 83 | -0.018655 | -0.018655 | 0.000000 | PASS |  |
| chart_read_g5.trade_gross | a_zero_drift | 83 | -0.018655 | -0.018655 | 0.000000 | PASS |  |
| orderflow_views.trade (fw60) | a_zero_drift | 83 | -0.018655 | -0.018655 | 0.000000 | PASS |  |
| levels_sizing.run (day_end) | a_zero_drift | 83 | -0.018655 | -0.018655 | 0.000000 | PASS |  |
| zero-edge sanity | a_zero_drift | 1 | 0.000000 | -0.018655 | 0.018655 | PASS | seed 20261018; planted market has mean(exp)=0 within 3 SE of the walk |
| bt_engine.simulate_trade | b_planted_0.30 | 83 | 0.300000 | 0.300000 | 0.000000 | PASS |  |
| tom_bt.sim_limit_trade | b_planted_0.30 | 83 | 0.300000 | 0.300000 | 0.000000 | PASS |  |
| run_t055.score_trades | b_planted_0.30 | 83 | 0.300000 | 0.300000 | 0.000000 | PASS |  |
| screen.compute_cells | b_planted_0.30 | 83 | 0.300000 | 0.300000 | 0.000000 | PASS |  |
| chart_read_g5.trade_gross | b_planted_0.30 | 83 | 0.300000 | 0.300000 | 0.000000 | PASS |  |
| orderflow_views.trade (fw60) | b_planted_0.30 | 83 | 0.300000 | 0.300000 | 0.000000 | PASS |  |
| levels_sizing.run (day_end) | b_planted_0.30 | 83 | 0.300000 | 0.300000 | 0.000000 | PASS |  |
| bt_engine.simulate_trade | c_move_inside_signal_bar | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| tom_bt.sim_limit_trade | c_move_inside_signal_bar | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| run_t055.score_trades | c_move_inside_signal_bar | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| screen.compute_cells | c_move_inside_signal_bar | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| chart_read_g5.trade_gross | c_move_inside_signal_bar | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| orderflow_views.trade (fw60) | c_move_inside_signal_bar | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| levels_sizing.run (day_end) | c_move_inside_signal_bar | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| bt_engine.simulate_trade | d_move_after_exit | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| tom_bt.sim_limit_trade | d_move_after_exit | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| run_t055.score_trades | d_move_after_exit | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| screen.compute_cells | d_move_after_exit | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| chart_read_g5.trade_gross | d_move_after_exit | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| orderflow_views.trade (fw60) | d_move_after_exit | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| levels_sizing.run (day_end) | d_move_after_exit | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| bt_engine.simulate_trade | b_net_fees_taker_both_legs | 83 | 0.199998 | 0.199998 | 0.000000 | PASS | expected = 0.30 - 0.05 - 0.05*pout/pin (pct) |
| tom_bt.sim_limit_trade | b_net_fees_maker_in_taker_out | 83 | 0.249998 | 0.249998 | 0.000000 | PASS | Deribit maker 0 / taker 0.05 |
| run_t055.score_trades | b_net_cost_model | 83 | 0.001800 | 0.001800 | 0.000000 | PASS | net = gross - 0.0010 - 0.0002 (FORMULAS 13); fraction |
| bt_engine.simulate_trade | e_funding_interior_rate+0.0001 | 83 | 0.000120 | 0.000120 | 0.000000 | PASS |  |
| bt_engine.simulate_trade (funding=None) | e_funding_interior_rate+0.0001 | 83 | 0.000120 | 0.000000 | 0.010000 | FAIL | L5: None means 0 with no error |
| trade_costs.funding_paid | e_funding_interior_rate+0.0001 | 83 | 0.000120 | 0.000120 | 0.000000 | PASS |  |
| run_t055.score_trades | e_funding_interior_rate+0.0001 | 83 | 0.000120 | 0.000120 | 0.000000 | PASS |  |
| screen.compute_cells FUND | e_funding_interior_rate+0.0001 | 83 | 0.000120 | 0.010000 | 0.020000 | FAIL | flat 1 bp per crossing, blind to side and rate (L1) |
| chart_read_g5.funding_pct | e_funding_interior_rate+0.0001 | 83 | 0.000120 | 0.010000 | 0.020000 | FAIL | flat 1 bp per crossing, blind to side and rate (L1) |
| bt_engine.simulate_trade | e_funding_interior_rate-0.0001 | 83 | -0.000120 | -0.000120 | 0.000000 | PASS |  |
| bt_engine.simulate_trade (funding=None) | e_funding_interior_rate-0.0001 | 83 | -0.000120 | 0.000000 | 0.010000 | FAIL | L5: None means 0 with no error |
| trade_costs.funding_paid | e_funding_interior_rate-0.0001 | 83 | -0.000120 | -0.000120 | 0.000000 | PASS |  |
| run_t055.score_trades | e_funding_interior_rate-0.0001 | 83 | -0.000120 | -0.000120 | 0.000000 | PASS |  |
| screen.compute_cells FUND | e_funding_interior_rate-0.0001 | 83 | -0.000120 | 0.010000 | 0.020000 | FAIL | flat 1 bp per crossing, blind to side and rate (L1) |
| chart_read_g5.funding_pct | e_funding_interior_rate-0.0001 | 83 | -0.000120 | 0.010000 | 0.020000 | FAIL | flat 1 bp per crossing, blind to side and rate (L1) |
| bt_engine.simulate_trade | e_funding_entry_on_rate+0.0001 | 83 | 0.000000 | 0.000120 | 0.010000 | FAIL |  |
| trade_costs.funding_paid | e_funding_entry_on_rate+0.0001 | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| run_t055.score_trades | e_funding_entry_on_rate+0.0001 | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| screen.compute_cells FUND | e_funding_entry_on_rate+0.0001 | 83 | 0.000000 | 0.000000 | 0.000000 | PASS | flat 1 bp per crossing, blind to side and rate (L1) |
| chart_read_g5.funding_pct | e_funding_entry_on_rate+0.0001 | 83 | 0.000000 | 0.000000 | 0.000000 | PASS | flat 1 bp per crossing, blind to side and rate (L1) |
| bt_engine.simulate_trade | e_funding_entry_on_rate-0.0001 | 83 | 0.000000 | -0.000120 | 0.010000 | FAIL |  |
| trade_costs.funding_paid | e_funding_entry_on_rate-0.0001 | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| run_t055.score_trades | e_funding_entry_on_rate-0.0001 | 83 | 0.000000 | 0.000000 | 0.000000 | PASS |  |
| screen.compute_cells FUND | e_funding_entry_on_rate-0.0001 | 83 | 0.000000 | 0.000000 | 0.000000 | PASS | flat 1 bp per crossing, blind to side and rate (L1) |
| chart_read_g5.funding_pct | e_funding_entry_on_rate-0.0001 | 83 | 0.000000 | 0.000000 | 0.000000 | PASS | flat 1 bp per crossing, blind to side and rate (L1) |
| bt_engine.simulate_trade | e_funding_exit_on_rate+0.0001 | 83 | 0.000120 | 0.000000 | 0.010000 | FAIL |  |
| trade_costs.funding_paid | e_funding_exit_on_rate+0.0001 | 83 | 0.000120 | 0.000120 | 0.000000 | PASS |  |
| run_t055.score_trades | e_funding_exit_on_rate+0.0001 | 83 | 0.000120 | 0.000120 | 0.000000 | PASS |  |
| screen.compute_cells FUND | e_funding_exit_on_rate+0.0001 | 83 | 0.000120 | 0.010000 | 0.020000 | FAIL | flat 1 bp per crossing, blind to side and rate (L1) |
| chart_read_g5.funding_pct | e_funding_exit_on_rate+0.0001 | 83 | 0.000120 | 0.010000 | 0.020000 | FAIL | flat 1 bp per crossing, blind to side and rate (L1) |
| bt_engine.simulate_trade | e_funding_exit_on_rate-0.0001 | 83 | -0.000120 | 0.000000 | 0.010000 | FAIL |  |
| trade_costs.funding_paid | e_funding_exit_on_rate-0.0001 | 83 | -0.000120 | -0.000120 | 0.000000 | PASS |  |
| run_t055.score_trades | e_funding_exit_on_rate-0.0001 | 83 | -0.000120 | -0.000120 | 0.000000 | PASS |  |
| screen.compute_cells FUND | e_funding_exit_on_rate-0.0001 | 83 | -0.000120 | 0.010000 | 0.020000 | FAIL | flat 1 bp per crossing, blind to side and rate (L1) |
| chart_read_g5.funding_pct | e_funding_exit_on_rate-0.0001 | 83 | -0.000120 | 0.010000 | 0.020000 | FAIL | flat 1 bp per crossing, blind to side and rate (L1) |
| tom_bt.sim_limit_trade | e_funding | 0 |  |  |  | BLOCKED | no funding term in sim_limit_trade (fees only) |
| orderflow_views.trade | e_funding | 0 |  |  |  | BLOCKED | no funding term (FEE_RT only) |
| levels_sizing.run | e_funding | 0 |  |  |  | BLOCKED | no rate input; flat stress qty*op*1e-4/480 per bar, side-blind (cannot take a rate) |
| bt_engine.simulate_trade | e_funding_records_missing_for_hold | 1 | 76.000000 | 0.000000 | 76.000000 | FAIL | expected fail-closed (B103 behaviour of trade_costs) on every event whose exit is past the last funding record; got = events that raised |
| run_t055.score_trades | e_funding_records_missing_for_hold | 1 | 76.000000 | 76.000000 | 0.000000 | PASS | expected fail-closed on every event whose exit is past the last funding record |
| bt_engine.simulate_trade | f_gap_through_stop | 83 | -2.000000 | -2.000000 | 0.000000 | PASS |  |
| tom_bt.sim_limit_trade | f_gap_through_stop | 83 | -2.000000 | -2.000000 | 0.000000 | PASS |  |
| orderflow_views.trade (stop/2R leg) | f_gap_through_stop | 83 | -2.000000 | -0.500000 | 1.500000 | FAIL | N2 of 2026-10-15 audit: books the stop price, not the gap open |
| levels_sizing.run | f_gap_through_stop | 83 | -2.000000 | -2.000000 | 0.000000 | PASS |  |
| run_t055.score_trades | f_gap_through_stop | 0 |  |  |  | BLOCKED | fixed-hold harness: no stop concept |
| screen.compute_cells | f_gap_through_stop | 0 |  |  |  | BLOCKED | fixed-hold harness: no stop concept |
| chart_read_g5.trade_gross | f_gap_through_stop | 0 |  |  |  | BLOCKED | fixed-hold harness: no stop concept |
| bt_engine.simulate_trade | f2_trade_gaps_but_mark_does_not | 1 | 0.000000 | 0.000000 | 0.000000 | PASS | exchange stops trigger on MARK: no stop expected while mark stays above; got = share of events stopped (0 = consistent) |
| bt_engine.simulate_trade | g_same_bar_stop_and_target | 83 | -0.500000 | -0.500000 | 0.000000 | PASS |  |
| bt_engine.simulate_trade | g_ambiguous_counter | 1 | 83.000000 | 83.000000 | 0.000000 | PASS |  |
| tom_bt.sim_limit_trade | g_same_bar_stop_and_target | 83 | -0.500000 | -0.500000 | 0.000000 | PASS |  |
| orderflow_views.trade (stop/2R leg) | g_same_bar_stop_and_target | 83 | -0.500000 | -0.500000 | 0.000000 | PASS |  |
| levels_sizing.run | g_same_bar_stop_and_target | 83 | -0.500000 | -0.500000 | 0.000000 | PASS |  |
| run_t055.score_trades | g_same_bar_stop_and_target | 0 |  |  |  | BLOCKED | fixed-hold harness: no stop or target |
| screen.compute_cells | g_same_bar_stop_and_target | 0 |  |  |  | BLOCKED | fixed-hold harness: no stop or target |
| chart_read_g5.trade_gross | g_same_bar_stop_and_target | 0 |  |  |  | BLOCKED | fixed-hold harness: no stop or target |
| bt_engine.simulate_trade | h_timeout_reason_bars_exit_bar | 1 | 3.000000 | 3.000000 | 0.000000 | PASS |  |
| bt_engine.simulate_trade | h2_timeout_vs_next_open_gap | 83 | -1.000000 | 0.000000 | 1.000000 | FAIL | L5: timeout fills at the last bar's close; a market exit sent at that close fills at the next open. got=close fill, exp=next-open fill (-1.00 pct apart) |
| screen.compute_cells | h2_timeout_vs_next_open_gap | 83 | -1.000000 | -1.000000 | 0.000000 | PASS | screen exits at the next open: consistent with the next-open reading |
| tom_bt.sim_limit_trade | h2_timeout_vs_next_open_gap | 83 | -1.000000 | 0.000000 | 1.000000 | FAIL | same close-fill convention as bt_engine |
