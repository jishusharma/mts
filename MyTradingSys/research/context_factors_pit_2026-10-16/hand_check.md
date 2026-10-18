# Angle (c): hand arithmetic (pandas, raw CSVs) vs the engine

Points chosen before any row was read (OURS): a mid-day 1h close, a 4h close and a day close in 2023. `hand` is
indep_pandas.py (resample + rolling + the spec's rules, no engine code); `engine` is the VEC build. A mismatch is a finding.

## t = 629939 (2023-03-14 10:59 UTC close), long

| field | hand | engine | ok |
|---|---|---|---|
| price | 24571.5 | 24571.5 | yes |
| c_4h | (24379.9, 24850, 24148, 24251.9) | (24379.9, 24850, 24148, 24251.9) | yes |
| c_8h | (24119.5, 24850, 23990, 24251.9) | (24119.5, 24850, 23990, 24251.9) | yes |
| c_12h | (22092.6, 24517.2, 21945, 24119.5) | (22092.6, 24517.2, 21945, 24119.5) | yes |
| c_1d | (21986.2, 24517.2, 21804, 24119.5) | (21986.2, 24517.2, 21804, 24119.5) | yes |
| p_4h | (24252.3, 24636.8, 24121.7, 24571.5) | (24252.3, 24636.8, 24121.7, 24571.5) | yes |
| p_1d | (24119.5, 24850, 23990, 24571.5) | (24119.5, 24850, 23990, 24571.5) | yes |
| c_1w_hl | (22594.5, 19521.6) | (22594.5, 19521.6) | yes |
| pat_4h | bear_pin | bear_pin | yes |
| pat_8h | bear_pin|three_up | bear_pin|three_up | yes |
| pat_12h | three_up | three_up | yes |
| pat_1d | three_up | three_up | yes |
| atr4 | 699.036 | 699.036 | yes |
| bb_4h_state | inside | inside | yes |
| bb_4h_pctb | 0.891537 | 0.891537 | yes |
| bb_4h_bw | 0.306309 | 0.306309 | yes |
| bb_1d_state | inside | inside | yes |
| bb_1d_pctb | 0.819 | 0.819 | yes |
| bb_1d_bw | 0.210227 | 0.210227 | yes |
| phase_a | markdown | markdown | yes |
| phase_b | markup | markup | yes |
| intraday | trend_up | trend_up | yes |
| intraday_alt | trend_up | trend_up | yes |
| vol_regime | high | high | yes |
| squeeze | False | False | yes |
| session | london | london | yes |
| weekend | False | False | yes |
| funding | low | low | yes |
| htf_align | True | True | yes |
| n_levels | 89 | 89 | yes |
| n_krown | 72 | 72 | yes |
| near_price | 24517.2 | 24517.2 | yes |
| near_src | krown_zone | krown_zone | yes |
| near_dist_atr | 0.0776784 | 0.0776784 | yes |
| level_age_h | 7.01667 | 7.01667 | yes |
| at_level | True | True | yes |
| n_layers | 3 | 3 | yes |
| touch_count | 1 | 1 | yes |
| first_touch | False | False | yes |
| approach | away | away | yes |
| sweep | True | True | yes |
| near_src_4hrule | krown_zone | krown_zone | yes |
| stop_d_pct | 11.263 | 11.263 | yes |
| stop_12_pct | 10.6892 | 10.6892 | yes |
| stop_8_pct | 2.36656 | 2.36656 | yes |
| ladder_rung | 8h | 8h | yes |
| ladder_stop_pct | 2.36656 | 2.36656 | yes |
| ladder_cost_r | 0.0591575 | 0.0591575 | yes |
| ladder_below_floor | False | False | yes |
| ladder_cond | True | True | yes |
| ladder_cond_alt | True | True | yes |
| bb_long_conf | False | False | yes |
| bb_short_veto_walk | False | False | yes |
| bb_short_veto_band | False | False | yes |

hand ledger: 89 levels from 9 sources (fabio_vp_day, krown_zone, malkan_bb_d, prior_d_hl, prior_w_hl, round_1k, tom_vp_week, vwap_session, vwap_week); the nearest long level by hand = 24517.2 (krown_zone), by the engine = 24517.2 (krown_zone).

## t = 629939 (2023-03-14 10:59 UTC close), short

| field | hand | engine | ok |
|---|---|---|---|
| price | 24571.5 | 24571.5 | yes |
| c_4h | (24379.9, 24850, 24148, 24251.9) | (24379.9, 24850, 24148, 24251.9) | yes |
| c_8h | (24119.5, 24850, 23990, 24251.9) | (24119.5, 24850, 23990, 24251.9) | yes |
| c_12h | (22092.6, 24517.2, 21945, 24119.5) | (22092.6, 24517.2, 21945, 24119.5) | yes |
| c_1d | (21986.2, 24517.2, 21804, 24119.5) | (21986.2, 24517.2, 21804, 24119.5) | yes |
| p_4h | (24252.3, 24636.8, 24121.7, 24571.5) | (24252.3, 24636.8, 24121.7, 24571.5) | yes |
| p_1d | (24119.5, 24850, 23990, 24571.5) | (24119.5, 24850, 23990, 24571.5) | yes |
| c_1w_hl | (22594.5, 19521.6) | (22594.5, 19521.6) | yes |
| pat_4h | bear_pin | bear_pin | yes |
| pat_8h | bear_pin|three_up | bear_pin|three_up | yes |
| pat_12h | three_up | three_up | yes |
| pat_1d | three_up | three_up | yes |
| atr4 | 699.036 | 699.036 | yes |
| bb_4h_state | inside | inside | yes |
| bb_4h_pctb | 0.891537 | 0.891537 | yes |
| bb_4h_bw | 0.306309 | 0.306309 | yes |
| bb_1d_state | inside | inside | yes |
| bb_1d_pctb | 0.819 | 0.819 | yes |
| bb_1d_bw | 0.210227 | 0.210227 | yes |
| phase_a | markdown | markdown | yes |
| phase_b | markup | markup | yes |
| intraday | trend_up | trend_up | yes |
| intraday_alt | trend_up | trend_up | yes |
| vol_regime | high | high | yes |
| squeeze | False | False | yes |
| session | london | london | yes |
| weekend | False | False | yes |
| funding | low | low | yes |
| htf_align | False | False | yes |
| n_levels | 89 | 89 | yes |
| n_krown | 72 | 72 | yes |
| near_price | 24588 | 24588 | yes |
| near_src | krown_zone | krown_zone | yes |
| near_dist_atr | 0.0236039 | 0.0236039 | yes |
| level_age_h | 451.017 | 451.017 | yes |
| at_level | True | True | yes |
| n_layers | 1 | 1 | yes |
| touch_count | 1 | 1 | yes |
| first_touch | False | False | yes |
| approach | slow | slow | yes |
| sweep | True | True | yes |
| near_src_4hrule | krown_zone | krown_zone | yes |
| stop_d_pct | nan | nan | yes |
| stop_12_pct | nan | nan | yes |
| stop_8_pct | 1.13343 | 1.13343 | yes |
| ladder_rung | 8h | 8h | yes |
| ladder_stop_pct | 1.13343 | 1.13343 | yes |
| ladder_cost_r | 0.123519 | 0.123519 | yes |
| ladder_below_floor | False | False | yes |
| ladder_cond | False | False | yes |
| ladder_cond_alt | False | False | yes |
| bb_long_conf | False | False | yes |
| bb_short_veto_walk | False | False | yes |
| bb_short_veto_band | False | False | yes |

hand ledger: 89 levels from 9 sources (fabio_vp_day, krown_zone, malkan_bb_d, prior_d_hl, prior_w_hl, round_1k, tom_vp_week, vwap_session, vwap_week); the nearest short level by hand = 24588 (krown_zone), by the engine = 24588 (krown_zone).

## t = 860639 (2023-08-21 15:59 UTC close), long

| field | hand | engine | ok |
|---|---|---|---|
| price | 25925.1 | 25925.1 | yes |
| c_4h | (26020.8, 26193.6, 25800, 25925.1) | (26020.8, 26193.6, 25800, 25925.1) | yes |
| c_8h | (26011.9, 26193.6, 25800, 25925.1) | (26011.9, 26193.6, 25800, 25925.1) | yes |
| c_12h | (26175.9, 26183.2, 25861, 26020.7) | (26175.9, 26183.2, 25861, 26020.7) | yes |
| c_1d | (26088.4, 26285, 25948.5, 26175.9) | (26088.4, 26285, 25948.5, 26175.9) | yes |
| p_4h | (26020.8, 26193.6, 25800, 25925.1) | (26020.8, 26193.6, 25800, 25925.1) | yes |
| p_1d | (26175.9, 26193.6, 25800, 25925.1) | (26175.9, 26193.6, 25800, 25925.1) | yes |
| c_1w_hl | (29686.7, 24581) | (29686.7, 24581) | yes |
| pat_4h | bear_engulf|outside | bear_engulf|outside | yes |
| pat_8h | outside | outside | yes |
| pat_12h | bear_engulf | bear_engulf | yes |
| pat_1d | none | none | yes |
| atr4 | 201.957 | 201.957 | yes |
| bb_4h_state | inside | inside | yes |
| bb_4h_pctb | 0.204894 | 0.204894 | yes |
| bb_4h_bw | 0.0193293 | 0.0193293 | yes |
| bb_1d_state | walk_down | walk_down | yes |
| bb_1d_pctb | -0.000486286 | -0.000486286 | yes |
| bb_1d_bw | 0.174557 | 0.174557 | yes |
| phase_a | markdown | markdown | yes |
| phase_b | markdown | markdown | yes |
| intraday | trend_down | trend_down | yes |
| intraday_alt | trend_down | trend_down | yes |
| vol_regime | mid | mid | yes |
| squeeze | False | False | yes |
| session | ny | ny | yes |
| weekend | False | False | yes |
| funding | neg | neg | yes |
| htf_align | False | False | yes |
| n_levels | 102 | 102 | yes |
| n_krown | 85 | 85 | yes |
| near_price | 25600 | 25600 | yes |
| near_src | krown_zone | krown_zone | yes |
| near_dist_atr | 1.60975 | 1.60975 | yes |
| level_age_h | 56.0167 | 56.0167 | yes |
| at_level | False | False | yes |
| n_layers | 0 | 0 | yes |
| touch_count | 0 | 0 | yes |
| first_touch | True | True | yes |
| approach | slow | slow | yes |
| sweep | False | False | yes |
| near_src_4hrule | krown_zone | krown_zone | yes |
| stop_d_pct | nan | nan | yes |
| stop_12_pct | 0.247251 | 0.247251 | yes |
| stop_8_pct | 0.482544 | 0.482544 | yes |
| ladder_rung | 12h | 12h | yes |
| ladder_stop_pct | 0.247251 | 0.247251 | yes |
| ladder_cost_r | 0.566227 | 0.566227 | yes |
| ladder_below_floor | True | True | yes |
| ladder_cond | False | False | yes |
| ladder_cond_alt | True | True | yes |
| bb_long_conf | False | False | yes |
| bb_short_veto_walk | False | False | yes |
| bb_short_veto_band | False | False | yes |

hand ledger: 102 levels from 9 sources (fabio_vp_day, krown_zone, malkan_bb_d, prior_d_hl, prior_w_hl, round_1k, tom_vp_week, vwap_session, vwap_week); the nearest long level by hand = 25600 (krown_zone), by the engine = 25600 (krown_zone).

## t = 860639 (2023-08-21 15:59 UTC close), short

| field | hand | engine | ok |
|---|---|---|---|
| price | 25925.1 | 25925.1 | yes |
| c_4h | (26020.8, 26193.6, 25800, 25925.1) | (26020.8, 26193.6, 25800, 25925.1) | yes |
| c_8h | (26011.9, 26193.6, 25800, 25925.1) | (26011.9, 26193.6, 25800, 25925.1) | yes |
| c_12h | (26175.9, 26183.2, 25861, 26020.7) | (26175.9, 26183.2, 25861, 26020.7) | yes |
| c_1d | (26088.4, 26285, 25948.5, 26175.9) | (26088.4, 26285, 25948.5, 26175.9) | yes |
| p_4h | (26020.8, 26193.6, 25800, 25925.1) | (26020.8, 26193.6, 25800, 25925.1) | yes |
| p_1d | (26175.9, 26193.6, 25800, 25925.1) | (26175.9, 26193.6, 25800, 25925.1) | yes |
| c_1w_hl | (29686.7, 24581) | (29686.7, 24581) | yes |
| pat_4h | bear_engulf|outside | bear_engulf|outside | yes |
| pat_8h | outside | outside | yes |
| pat_12h | bear_engulf | bear_engulf | yes |
| pat_1d | none | none | yes |
| atr4 | 201.957 | 201.957 | yes |
| bb_4h_state | inside | inside | yes |
| bb_4h_pctb | 0.204894 | 0.204894 | yes |
| bb_4h_bw | 0.0193293 | 0.0193293 | yes |
| bb_1d_state | walk_down | walk_down | yes |
| bb_1d_pctb | -0.000486286 | -0.000486286 | yes |
| bb_1d_bw | 0.174557 | 0.174557 | yes |
| phase_a | markdown | markdown | yes |
| phase_b | markdown | markdown | yes |
| intraday | trend_down | trend_down | yes |
| intraday_alt | trend_down | trend_down | yes |
| vol_regime | mid | mid | yes |
| squeeze | False | False | yes |
| session | ny | ny | yes |
| weekend | False | False | yes |
| funding | neg | neg | yes |
| htf_align | True | True | yes |
| n_levels | 102 | 102 | yes |
| n_krown | 85 | 85 | yes |
| near_price | 25948.5 | 25948.5 | yes |
| near_src | krown_zone | krown_zone | yes |
| near_dist_atr | 0.115866 | 0.115866 | yes |
| level_age_h | 12.0167 | 12.0167 | yes |
| at_level | True | True | yes |
| n_layers | 5 | 5 | yes |
| touch_count | 2 | 2 | yes |
| first_touch | False | False | yes |
| approach | away | away | yes |
| sweep | True | True | yes |
| near_src_4hrule | krown_zone | krown_zone | yes |
| stop_d_pct | 1.38823 | 1.38823 | yes |
| stop_12_pct | 0.99556 | 0.99556 | yes |
| stop_8_pct | 1.03568 | 1.03568 | yes |
| ladder_rung | 1d | 1d | yes |
| ladder_stop_pct | 1.38823 | 1.38823 | yes |
| ladder_cost_r | 0.100848 | 0.100848 | yes |
| ladder_below_floor | False | False | yes |
| ladder_cond | True | True | yes |
| ladder_cond_alt | True | True | yes |
| bb_long_conf | False | False | yes |
| bb_short_veto_walk | False | False | yes |
| bb_short_veto_band | False | False | yes |

hand ledger: 102 levels from 9 sources (fabio_vp_day, krown_zone, malkan_bb_d, prior_d_hl, prior_w_hl, round_1k, tom_vp_week, vwap_session, vwap_week); the nearest short level by hand = 25948.5 (krown_zone), by the engine = 25948.5 (krown_zone).

## t = 1006559 (2023-11-30 23:59 UTC close), long

| field | hand | engine | ok |
|---|---|---|---|
| price | 37716.8 | 37716.8 | yes |
| c_4h | (37745.4, 37805, 37585, 37716.8) | (37745.4, 37805, 37585, 37716.8) | yes |
| c_8h | (37613.9, 37807, 37520, 37716.8) | (37613.9, 37807, 37520, 37716.8) | yes |
| c_12h | (37867.1, 37964.6, 37442.9, 37716.8) | (37867.1, 37964.6, 37442.9, 37716.8) | yes |
| c_1d | (37837.2, 38132, 37442.9, 37716.8) | (37837.2, 38132, 37442.9, 37716.8) | yes |
| p_4h | (37745.4, 37805, 37585, 37716.8) | (37745.4, 37805, 37585, 37716.8) | yes |
| p_1d | (37837.2, 38132, 37442.9, 37716.8) | (37837.2, 38132, 37442.9, 37716.8) | yes |
| c_1w_hl | (38425, 35610.7) | (38425, 35610.7) | yes |
| pat_4h | inside | inside | yes |
| pat_8h | inside | inside | yes |
| pat_12h | bear_engulf | bear_engulf | yes |
| pat_1d | bear_engulf | bear_engulf | yes |
| atr4 | 452.293 | 452.293 | yes |
| bb_4h_state | inside | inside | yes |
| bb_4h_pctb | 0.532806 | 0.532806 | yes |
| bb_4h_bw | 0.038336 | 0.038336 | yes |
| bb_1d_state | inside | inside | yes |
| bb_1d_pctb | 0.719752 | 0.719752 | yes |
| bb_1d_bw | 0.073465 | 0.073465 | yes |
| phase_a | markup | markup | yes |
| phase_b | markup | markup | yes |
| intraday | trend_down | trend_down | yes |
| intraday_alt | balance | balance | yes |
| vol_regime | mid | mid | yes |
| squeeze | False | False | yes |
| session | late | late | yes |
| weekend | False | False | yes |
| funding | low | low | yes |
| htf_align | True | True | yes |
| n_levels | 93 | 93 | yes |
| n_krown | 76 | 76 | yes |
| near_price | 37695 | 37695 | yes |
| near_src | fabio_vp_day | fabio_vp_day | yes |
| near_dist_atr | 0.0481989 | 0.0481989 | yes |
| level_age_h | 0.0166667 | 0.0166667 | yes |
| at_level | True | True | yes |
| n_layers | 3 | 3 | yes |
| touch_count | 0 | 0 | yes |
| first_touch | True | True | yes |
| approach | slow | slow | yes |
| sweep | True | True | yes |
| near_src_4hrule | fabio_vp_day | fabio_vp_day | yes |
| stop_d_pct | 0.726202 | 0.726202 | yes |
| stop_12_pct | 0.726202 | 0.726202 | yes |
| stop_8_pct | 0.521783 | 0.521783 | yes |
| ladder_rung | 1d | 1d | yes |
| ladder_stop_pct | 0.726202 | 0.726202 | yes |
| ladder_cost_r | 0.192784 | 0.192784 | yes |
| ladder_below_floor | False | False | yes |
| ladder_cond | False | False | yes |
| ladder_cond_alt | True | True | yes |
| bb_long_conf | False | False | yes |
| bb_short_veto_walk | False | False | yes |
| bb_short_veto_band | False | False | yes |

hand ledger: 93 levels from 9 sources (fabio_vp_day, krown_zone, malkan_bb_d, prior_d_hl, prior_w_hl, round_1k, tom_vp_week, vwap_session, vwap_week); the nearest long level by hand = 37695 (fabio_vp_day), by the engine = 37695 (fabio_vp_day).

## t = 1006559 (2023-11-30 23:59 UTC close), short

| field | hand | engine | ok |
|---|---|---|---|
| price | 37716.8 | 37716.8 | yes |
| c_4h | (37745.4, 37805, 37585, 37716.8) | (37745.4, 37805, 37585, 37716.8) | yes |
| c_8h | (37613.9, 37807, 37520, 37716.8) | (37613.9, 37807, 37520, 37716.8) | yes |
| c_12h | (37867.1, 37964.6, 37442.9, 37716.8) | (37867.1, 37964.6, 37442.9, 37716.8) | yes |
| c_1d | (37837.2, 38132, 37442.9, 37716.8) | (37837.2, 38132, 37442.9, 37716.8) | yes |
| p_4h | (37745.4, 37805, 37585, 37716.8) | (37745.4, 37805, 37585, 37716.8) | yes |
| p_1d | (37837.2, 38132, 37442.9, 37716.8) | (37837.2, 38132, 37442.9, 37716.8) | yes |
| c_1w_hl | (38425, 35610.7) | (38425, 35610.7) | yes |
| pat_4h | inside | inside | yes |
| pat_8h | inside | inside | yes |
| pat_12h | bear_engulf | bear_engulf | yes |
| pat_1d | bear_engulf | bear_engulf | yes |
| atr4 | 452.293 | 452.293 | yes |
| bb_4h_state | inside | inside | yes |
| bb_4h_pctb | 0.532806 | 0.532806 | yes |
| bb_4h_bw | 0.038336 | 0.038336 | yes |
| bb_1d_state | inside | inside | yes |
| bb_1d_pctb | 0.719752 | 0.719752 | yes |
| bb_1d_bw | 0.073465 | 0.073465 | yes |
| phase_a | markup | markup | yes |
| phase_b | markup | markup | yes |
| intraday | trend_down | trend_down | yes |
| intraday_alt | balance | balance | yes |
| vol_regime | mid | mid | yes |
| squeeze | False | False | yes |
| session | late | late | yes |
| weekend | False | False | yes |
| funding | low | low | yes |
| htf_align | False | False | yes |
| n_levels | 93 | 93 | yes |
| n_krown | 76 | 76 | yes |
| near_price | 37751.6 | 37751.6 | yes |
| near_src | vwap_session | vwap_session | yes |
| near_dist_atr | 0.0768559 | 0.0768559 | yes |
| level_age_h | 24 | 24 | yes |
| at_level | True | True | yes |
| n_layers | 4 | 4 | yes |
| touch_count | 12 | 12 | yes |
| first_touch | False | False | yes |
| approach | away | away | yes |
| sweep | True | True | yes |
| near_src_4hrule | vwap_session | vwap_session | yes |
| stop_d_pct | 1.10084 | 1.10084 | yes |
| stop_12_pct | 0.657002 | 0.657002 | yes |
| stop_8_pct | 0.239151 | 0.239151 | yes |
| ladder_rung | 1d | 1d | yes |
| ladder_stop_pct | 1.10084 | 1.10084 | yes |
| ladder_cost_r | 0.127176 | 0.127176 | yes |
| ladder_below_floor | False | False | yes |
| ladder_cond | True | True | yes |
| ladder_cond_alt | True | True | yes |
| bb_long_conf | False | False | yes |
| bb_short_veto_walk | False | False | yes |
| bb_short_veto_band | False | False | yes |

hand ledger: 93 levels from 9 sources (fabio_vp_day, krown_zone, malkan_bb_d, prior_d_hl, prior_w_hl, round_1k, tom_vp_week, vwap_session, vwap_week); the nearest short level by hand = 37751.6 (vwap_session), by the engine = 37751.6 (vwap_session).

**324 field comparisons, 0 mismatches.**
