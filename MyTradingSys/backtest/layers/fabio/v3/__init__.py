"""Fabio core v3 (FABIO_V3_SPEC.md v3.1): signals, models, fills, management, costs, day gates, engine.

Public API: every name the spec-derived pending test needs (pending_test_fabio_v3.py docstring, lines 17-33) is
re-exported here, plus the engine (`run`). Imports: stdlib, orderflow_bars and the repo fee source only.
"""
from .costs import (EPS, FEE_MAKER, FEE_TAKER, FUNDING_STRESS_MULT, MIN_MS, SLIP_STRESS_BPS, TICK, fee_rate, funding_r,
                    leg_r)
from .day_gates import (DAILY_STOP_R, ENTRY_CUTOFF, GATE_MIN_ELAPSED, GATE_PRIOR_DAYS, MAX_FIRST_LEGS, MAX_MISSING,
                        RECOVERY_LEVEL_R, TREND_RATIO, US_CLOSED, WINDOW_BARS, Z_POWER, aggregate_day_r, asia_open_utc,
                        ci_halfwidth, day_gate_open, day_type, entry_allowed, first_leg_allowed, first_leg_risk,
                        london_open_utc, ny_open_utc, sample_size, uk_bst, us_dst, window_bars)
from .fill import find_fill, fills_in_bar, missed_winner, taker_fill
from .manage import (ADD_PUSH_M, MAX_ADDS, MIN_ADD_FRAC, add_allowed, add_size, be_update, opp_stop, simulate_trade,
                     trail_update, walk_trade)
from .models import (IB_MINUTES, RECLAIM_BARS, REST_VALID_B, REST_VALID_D, d_and_stop, model_a_trade, model_b,
                     model_c, model_d_trade, scan_model_a, scan_model_b, scan_model_c, scan_model_d)
from .signals import (B_PROF, BAL_POC_BAND, DRIFT_Q, EFFORT_L, K_BAL, LVN_FRAC, R_ABS, R_CTL, S8_AGE, S8_N, S8_P,
                      S8_Z_HI, VA_PCT, VR_DAYS, VR_MIN_DAYS, VR_TIER, atr, balance, big_push, breakout, build_profile,
                      contiguous, control_level, curve, defended_level, effort_arrays, effort_result, exhaustion,
                      failed_auction, lvn_levels, net_big, poc_center, pressure, select_lvn, true_range, value_area,
                      volume_tier)
