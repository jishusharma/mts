"""Fabio core v3 (FABIO_V3_SPEC.md v3.1): signals, models, fills, management, costs, day gates, engine.

Public API: every name the spec-derived pending test needs (pending_test_fabio_v3.py docstring, lines 17-33) is
re-exported here, plus the engine (`run`). Imports: stdlib, orderflow_bars and the repo fee source only.
"""
from .costs import (EPS, FEE_MAKER, FEE_TAKER, FUNDING_STRESS_MULT, MIN_MS, SLIP_STRESS_BPS, TICK, fee_rate, funding_r,
                    leg_r)
from .day_gates import (ENTRY_CUTOFF, US_CLOSED, WINDOW_BARS, aggregate_day_r, asia_open_utc, ci_halfwidth,
                        day_gate_open, day_type, entry_allowed, first_leg_allowed, first_leg_risk, london_open_utc,
                        ny_open_utc, sample_size, uk_bst, us_dst, window_bars)
from .fill import find_fill, fills_in_bar, missed_winner, taker_fill
from .manage import (add_allowed, add_size, be_update, opp_stop, simulate_trade, trail_update, walk_trade)
from .models import (d_and_stop, model_a_trade, model_b, model_c, model_d_trade, scan_model_a, scan_model_b,
                     scan_model_c, scan_model_d)
from .signals import (B_PROF, atr, balance, big_push, breakout, build_profile, contiguous, control_level, curve,
                      defended_level, effort_arrays, effort_result, exhaustion, failed_auction, lvn_levels, net_big,
                      poc_center, pressure, select_lvn, true_range, value_area, volume_tier)
