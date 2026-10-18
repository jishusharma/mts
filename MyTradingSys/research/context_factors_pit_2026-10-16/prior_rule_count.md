# Trial T8: PRIOR_RULE last_closed (primary) vs cur_k_minus_1 (first draft), counts at every 8h close of DEV

2736 grid points x 2 sides. A row 'differs' when any of the listed fields differs between the two rules.

| side | level fields differ | ladder fields differ | at_level (last_closed) | at_level (cur_k_minus_1) |
|---|---|---|---|---|
| long | 629 of 2736 | 2736 of 2736 | 2581 | 2545 |
| short | 628 of 2736 | 2735 of 2736 | 2612 | 2584 |

Level fields: near_price, near_src, n_layers, at_level, level_age_h, touch_count, n_levels. Ladder fields: ladder_rung, ladder_stop_pct, stop_d_pct, stop_12_pct, stop_8_pct, ladder_cond.
Why the primary: the decision is taken at the close of bar t and filled at the open of bar t+1, which lies in the next bucket;
the candle that completed at t is closed information at that moment, exactly like the Bollinger bands and ATR already use it.
