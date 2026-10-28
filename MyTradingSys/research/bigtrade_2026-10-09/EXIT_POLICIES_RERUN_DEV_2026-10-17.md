> **RERUN of EXIT_POLICIES_REPORT after the split alignment (card split-relabel-fires, 2026-10-17).** DEV only: TRAIN = 2022-01-01..2024-06-30; the VALIDATE column is empty on purpose (not read; VALIDATION 2024-07..2025-06 was partly spent by the old run and no single-check pre-registration covers it). HOLDOUT unread. Old numbers: EXIT_POLICIES_REPORT.md. Each cell is a new trial (layer_lab/TRIALS.md).

# EXIT POLICIES REPORT (backtest C), 2026-10-17

Fires: F:\MTS\data\bigtrade\fires_spot. Bars: F:\MTS\data\bigtrade\cache\spot (spot). Entry = open of the bar after the fire bar closes. Costs 10.0 bp RT taker + 2.0 bp slippage (assumed). Stop-first on shared bars. HOLDOUT (2025-07..) not read. Policies:

- `live_like_1pct_2pct_8bars`: {'kind': 'bracket', 'stop': 0.01, 'target': 0.02, 'hold': 8, 'pct': True}
- `bracket_1atr_2atr_24`: {'kind': 'bracket', 'stop': 1.0, 'target': 2.0, 'hold': 24, 'pct': False}
- `bracket_1.5atr_3atr_24`: {'kind': 'bracket', 'stop': 1.5, 'target': 3.0, 'hold': 24, 'pct': False}
- `time_24_wide_stop_2atr`: {'kind': 'bracket', 'stop': 2.0, 'target': None, 'hold': 24, 'pct': False}
- `time_96_wide_stop_2atr`: {'kind': 'bracket', 'stop': 2.0, 'target': None, 'hold': 96, 'pct': False}
- `be1atr_trail2atr_96`: {'kind': 'trail', 'stop': 1.0, 'be_at': 1.0, 'trail': 2.0, 'hold': 96}

Columns: n, mean net return in bp of price, win share (net > 0), mean net in R (R = stop distance), mean fee share of risk.
`BOTH+` = mean net > 0 in TRAIN and VALIDATE with n >= 30 in each (necessary, not sufficient; no PBO yet).

| layer key | policy | TRAIN n / bp / win / R | VALIDATE n / bp / win / R | BOTH+ |
|---|---|---|---|---|
| layer:cryptocred:failed_msb:15m | live_like_1pct_2pct_8bars | 343 / -8.0 / 0.36 / -0.08 | 0 |  |
| layer:cryptocred:failed_msb:15m | bracket_1atr_2atr_24 | 343 / -10.8 / 0.33 / -0.51 | 0 |  |
| layer:cryptocred:failed_msb:15m | bracket_1.5atr_3atr_24 | 343 / -8.1 / 0.35 / -0.33 | 0 |  |
| layer:cryptocred:failed_msb:15m | time_24_wide_stop_2atr | 343 / -14.1 / 0.31 / -0.30 | 0 |  |
| layer:cryptocred:failed_msb:15m | time_96_wide_stop_2atr | 343 / -12.6 / 0.20 / -0.24 | 0 |  |
| layer:cryptocred:failed_msb:15m | be1atr_trail2atr_96 | 343 / -13.1 / 0.20 / -0.58 | 0 |  |
| layer:cryptocred:failed_msb:1h | live_like_1pct_2pct_8bars | 98 / -11.2 / 0.38 / -0.11 | 0 |  |
| layer:cryptocred:failed_msb:1h | bracket_1atr_2atr_24 | 98 / -8.6 / 0.33 / -0.24 | 0 |  |
| layer:cryptocred:failed_msb:1h | bracket_1.5atr_3atr_24 | 98 / -14.1 / 0.32 / -0.18 | 0 |  |
| layer:cryptocred:failed_msb:1h | time_24_wide_stop_2atr | 98 / +0.8 / 0.26 / -0.02 | 0 |  |
| layer:cryptocred:failed_msb:1h | time_96_wide_stop_2atr | 98 / +39.5 / 0.21 / +0.35 | 0 |  |
| layer:cryptocred:failed_msb:1h | be1atr_trail2atr_96 | 98 / +2.6 / 0.22 / -0.04 | 0 |  |
| layer:cryptocred:fib_pullback:15m | live_like_1pct_2pct_8bars | 1009 / -13.5 / 0.36 / -0.13 | 0 |  |
| layer:cryptocred:fib_pullback:15m | bracket_1atr_2atr_24 | 1009 / -12.3 / 0.34 / -0.51 | 0 |  |
| layer:cryptocred:fib_pullback:15m | bracket_1.5atr_3atr_24 | 1009 / -10.7 / 0.36 / -0.32 | 0 |  |
| layer:cryptocred:fib_pullback:15m | time_24_wide_stop_2atr | 1009 / -15.7 / 0.33 / -0.30 | 0 |  |
| layer:cryptocred:fib_pullback:15m | time_96_wide_stop_2atr | 1009 / -14.1 / 0.20 / -0.27 | 0 |  |
| layer:cryptocred:fib_pullback:15m | be1atr_trail2atr_96 | 1009 / -9.7 / 0.22 / -0.45 | 0 |  |
| layer:cryptocred:fib_pullback:1h | live_like_1pct_2pct_8bars | 250 / -14.6 / 0.37 / -0.15 | 0 |  |
| layer:cryptocred:fib_pullback:1h | bracket_1atr_2atr_24 | 250 / -13.2 / 0.32 / -0.32 | 0 |  |
| layer:cryptocred:fib_pullback:1h | bracket_1.5atr_3atr_24 | 250 / -20.6 / 0.36 / -0.22 | 0 |  |
| layer:cryptocred:fib_pullback:1h | time_24_wide_stop_2atr | 250 / -24.6 / 0.37 / -0.17 | 0 |  |
| layer:cryptocred:fib_pullback:1h | time_96_wide_stop_2atr | 250 / -7.1 / 0.22 / +0.03 | 0 |  |
| layer:cryptocred:fib_pullback:1h | be1atr_trail2atr_96 | 250 / -19.0 / 0.22 / -0.31 | 0 |  |
| layer:cryptocred:sr_flip:15m | live_like_1pct_2pct_8bars | 3450 / -11.4 / 0.34 / -0.11 | 0 |  |
| layer:cryptocred:sr_flip:15m | bracket_1atr_2atr_24 | 3450 / -12.4 / 0.33 / -0.50 | 0 |  |
| layer:cryptocred:sr_flip:15m | bracket_1.5atr_3atr_24 | 3450 / -13.0 / 0.33 / -0.34 | 0 |  |
| layer:cryptocred:sr_flip:15m | time_24_wide_stop_2atr | 3450 / -14.9 / 0.30 / -0.28 | 0 |  |
| layer:cryptocred:sr_flip:15m | time_96_wide_stop_2atr | 3450 / -9.8 / 0.20 / -0.17 | 0 |  |
| layer:cryptocred:sr_flip:15m | be1atr_trail2atr_96 | 3450 / -13.0 / 0.19 / -0.51 | 0 |  |
| layer:cryptocred:sr_flip:1h | live_like_1pct_2pct_8bars | 878 / -16.2 / 0.33 / -0.16 | 0 |  |
| layer:cryptocred:sr_flip:1h | bracket_1atr_2atr_24 | 878 / -17.8 / 0.31 / -0.29 | 0 |  |
| layer:cryptocred:sr_flip:1h | bracket_1.5atr_3atr_24 | 878 / -21.8 / 0.33 / -0.21 | 0 |  |
| layer:cryptocred:sr_flip:1h | time_24_wide_stop_2atr | 878 / -12.8 / 0.34 / -0.09 | 0 |  |
| layer:cryptocred:sr_flip:1h | time_96_wide_stop_2atr | 878 / +7.6 / 0.23 / +0.14 | 0 |  |
| layer:cryptocred:sr_flip:1h | be1atr_trail2atr_96 | 878 / -19.3 / 0.20 / -0.28 | 0 |  |
| layer:fabio:cvd_absorption:15m | live_like_1pct_2pct_8bars | 2497 / -13.8 / 0.34 / -0.14 | 0 |  |
| layer:fabio:cvd_absorption:15m | bracket_1atr_2atr_24 | 2497 / -13.4 / 0.32 / -0.59 | 0 |  |
| layer:fabio:cvd_absorption:15m | bracket_1.5atr_3atr_24 | 2497 / -15.7 / 0.32 / -0.43 | 0 |  |
| layer:fabio:cvd_absorption:15m | time_24_wide_stop_2atr | 2497 / -16.6 / 0.29 / -0.34 | 0 |  |
| layer:fabio:cvd_absorption:15m | time_96_wide_stop_2atr | 2497 / -12.2 / 0.18 / -0.27 | 0 |  |
| layer:fabio:cvd_absorption:15m | be1atr_trail2atr_96 | 2497 / -12.6 / 0.19 / -0.56 | 0 |  |
| layer:fabio:cvd_absorption:1h | live_like_1pct_2pct_8bars | 603 / -11.6 / 0.38 / -0.12 | 0 |  |
| layer:fabio:cvd_absorption:1h | bracket_1atr_2atr_24 | 603 / -15.0 / 0.33 / -0.25 | 0 |  |
| layer:fabio:cvd_absorption:1h | bracket_1.5atr_3atr_24 | 603 / -16.5 / 0.35 / -0.16 | 0 |  |
| layer:fabio:cvd_absorption:1h | time_24_wide_stop_2atr | 603 / -4.6 / 0.35 / -0.02 | 0 |  |
| layer:fabio:cvd_absorption:1h | time_96_wide_stop_2atr | 603 / +26.7 / 0.23 / +0.35 | 0 |  |
| layer:fabio:cvd_absorption:1h | be1atr_trail2atr_96 | 603 / -19.8 / 0.20 / -0.28 | 0 |  |
| layer:fabio:escalation:15m | live_like_1pct_2pct_8bars | 658 / -17.0 / 0.26 / -0.17 | 0 |  |
| layer:fabio:escalation:15m | bracket_1atr_2atr_24 | 658 / -11.7 / 0.31 / -0.99 | 0 |  |
| layer:fabio:escalation:15m | bracket_1.5atr_3atr_24 | 658 / -13.4 / 0.32 / -0.68 | 0 |  |
| layer:fabio:escalation:15m | time_24_wide_stop_2atr | 658 / -9.9 / 0.26 / -0.49 | 0 |  |
| layer:fabio:escalation:15m | time_96_wide_stop_2atr | 658 / -3.5 / 0.16 / -0.44 | 0 |  |
| layer:fabio:escalation:15m | be1atr_trail2atr_96 | 658 / -13.9 / 0.15 / -1.12 | 0 |  |
| layer:fabio:escalation:1h | live_like_1pct_2pct_8bars | 47 / -25.6 / 0.28 / -0.26 | 0 |  |
| layer:fabio:escalation:1h | bracket_1atr_2atr_24 | 47 / -18.9 / 0.36 / -0.32 | 0 |  |
| layer:fabio:escalation:1h | bracket_1.5atr_3atr_24 | 47 / -14.9 / 0.34 / -0.26 | 0 |  |
| layer:fabio:escalation:1h | time_24_wide_stop_2atr | 47 / +15.3 / 0.17 / +0.05 | 0 |  |
| layer:fabio:escalation:1h | time_96_wide_stop_2atr | 47 / -5.0 / 0.13 / +0.00 | 0 |  |
| layer:fabio:escalation:1h | be1atr_trail2atr_96 | 47 / +7.0 / 0.28 / -0.04 | 0 |  |
| layer:fabio:volume_fvg:15m | live_like_1pct_2pct_8bars | 469 / -9.2 / 0.34 / -0.09 | 0 |  |
| layer:fabio:volume_fvg:15m | bracket_1atr_2atr_24 | 469 / -11.8 / 0.32 / -0.53 | 0 |  |
| layer:fabio:volume_fvg:15m | bracket_1.5atr_3atr_24 | 469 / -11.6 / 0.33 / -0.34 | 0 |  |
| layer:fabio:volume_fvg:15m | time_24_wide_stop_2atr | 469 / -8.7 / 0.31 / -0.22 | 0 |  |
| layer:fabio:volume_fvg:15m | time_96_wide_stop_2atr | 469 / -9.7 / 0.22 / -0.09 | 0 |  |
| layer:fabio:volume_fvg:15m | be1atr_trail2atr_96 | 469 / -11.2 / 0.19 / -0.49 | 0 |  |
| layer:fabio:volume_fvg:1h | live_like_1pct_2pct_8bars | 111 / -23.9 / 0.32 / -0.24 | 0 |  |
| layer:fabio:volume_fvg:1h | bracket_1atr_2atr_24 | 111 / -33.7 / 0.27 / -0.42 | 0 |  |
| layer:fabio:volume_fvg:1h | bracket_1.5atr_3atr_24 | 111 / -38.1 / 0.35 / -0.20 | 0 |  |
| layer:fabio:volume_fvg:1h | time_24_wide_stop_2atr | 111 / -42.5 / 0.35 / -0.19 | 0 |  |
| layer:fabio:volume_fvg:1h | time_96_wide_stop_2atr | 111 / -27.3 / 0.23 / -0.03 | 0 |  |
| layer:fabio:volume_fvg:1h | be1atr_trail2atr_96 | 111 / -23.1 / 0.19 / -0.23 | 0 |  |
| layer:rsi:malkan_bear:1h | live_like_1pct_2pct_8bars | 71 / -12.0 / 0.35 / -0.12 | 0 |  |
| layer:rsi:malkan_bear:1h | bracket_1atr_2atr_24 | 71 / -19.1 / 0.32 / -0.23 | 0 |  |
| layer:rsi:malkan_bear:1h | bracket_1.5atr_3atr_24 | 71 / -29.8 / 0.30 / -0.25 | 0 |  |
| layer:rsi:malkan_bear:1h | time_24_wide_stop_2atr | 71 / -16.1 / 0.28 / -0.18 | 0 |  |
| layer:rsi:malkan_bear:1h | time_96_wide_stop_2atr | 71 / -30.7 / 0.21 / -0.21 | 0 |  |
| layer:rsi:malkan_bear:1h | be1atr_trail2atr_96 | 71 / -19.1 / 0.20 / -0.25 | 0 |  |
| layer:rsi:malkan_bull:1h | live_like_1pct_2pct_8bars | 60 / -28.3 / 0.35 / -0.28 | 0 |  |
| layer:rsi:malkan_bull:1h | bracket_1atr_2atr_24 | 60 / -23.0 / 0.28 / -0.38 | 0 |  |
| layer:rsi:malkan_bull:1h | bracket_1.5atr_3atr_24 | 60 / -19.4 / 0.30 / -0.29 | 0 |  |
| layer:rsi:malkan_bull:1h | time_24_wide_stop_2atr | 60 / +7.3 / 0.43 / +0.10 | 0 |  |
| layer:rsi:malkan_bull:1h | time_96_wide_stop_2atr | 60 / +82.6 / 0.28 / +0.89 | 0 |  |
| layer:rsi:malkan_bull:1h | be1atr_trail2atr_96 | 60 / -7.1 / 0.17 / -0.07 | 0 |  |
| layer:rsi:rsi_events:15m | live_like_1pct_2pct_8bars | 808 / -8.2 / 0.37 / -0.08 | 0 |  |
| layer:rsi:rsi_events:15m | bracket_1atr_2atr_24 | 808 / -8.7 / 0.36 / -0.40 | 0 |  |
| layer:rsi:rsi_events:15m | bracket_1.5atr_3atr_24 | 808 / -6.8 / 0.38 / -0.24 | 0 |  |
| layer:rsi:rsi_events:15m | time_24_wide_stop_2atr | 808 / -8.1 / 0.35 / -0.19 | 0 |  |
| layer:rsi:rsi_events:15m | time_96_wide_stop_2atr | 808 / -5.9 / 0.22 / -0.17 | 0 |  |
| layer:rsi:rsi_events:15m | be1atr_trail2atr_96 | 808 / -10.5 / 0.22 / -0.43 | 0 |  |
| layer:rsi:rsi_events:1h | live_like_1pct_2pct_8bars | 197 / -5.8 / 0.40 / -0.06 | 0 |  |
| layer:rsi:rsi_events:1h | bracket_1atr_2atr_24 | 197 / -14.4 / 0.36 / -0.16 | 0 |  |
| layer:rsi:rsi_events:1h | bracket_1.5atr_3atr_24 | 197 / -7.0 / 0.42 / +0.01 | 0 |  |
| layer:rsi:rsi_events:1h | time_24_wide_stop_2atr | 197 / +11.8 / 0.43 / +0.23 | 0 |  |
| layer:rsi:rsi_events:1h | time_96_wide_stop_2atr | 197 / +25.0 / 0.27 / +0.42 | 0 |  |
| layer:rsi:rsi_events:1h | be1atr_trail2atr_96 | 197 / -9.2 / 0.25 / -0.08 | 0 |  |
| layer:rsi:rsi_events:5m | live_like_1pct_2pct_8bars | 2655 / -11.3 / 0.31 / -0.11 | 0 |  |
| layer:rsi:rsi_events:5m | bracket_1atr_2atr_24 | 2655 / -11.7 / 0.30 / -0.96 | 0 |  |
| layer:rsi:rsi_events:5m | bracket_1.5atr_3atr_24 | 2655 / -11.2 / 0.33 / -0.62 | 0 |  |
| layer:rsi:rsi_events:5m | time_24_wide_stop_2atr | 2655 / -11.8 / 0.30 / -0.48 | 0 |  |
| layer:rsi:rsi_events:5m | time_96_wide_stop_2atr | 2655 / -10.3 / 0.22 / -0.44 | 0 |  |
| layer:rsi:rsi_events:5m | be1atr_trail2atr_96 | 2655 / -11.9 / 0.16 / -0.93 | 0 |  |
| layer:session:session_momentum:15m | live_like_1pct_2pct_8bars | 911 / -14.3 / 0.36 / -0.14 | 0 |  |
| layer:session:session_momentum:15m | bracket_1atr_2atr_24 | 911 / -13.2 / 0.33 / -0.46 | 0 |  |
| layer:session:session_momentum:15m | bracket_1.5atr_3atr_24 | 911 / -14.0 / 0.34 / -0.37 | 0 |  |
| layer:session:session_momentum:15m | time_24_wide_stop_2atr | 911 / -11.9 / 0.34 / -0.23 | 0 |  |
| layer:session:session_momentum:15m | time_96_wide_stop_2atr | 911 / -12.4 / 0.22 / -0.22 | 0 |  |
| layer:session:session_momentum:15m | be1atr_trail2atr_96 | 911 / -12.1 / 0.18 / -0.43 | 0 |  |
| layer:turn_of_candle:turn_of_candle:1m | live_like_1pct_2pct_8bars | 87535 / -11.8 / 0.19 / -0.12 | 0 |  |
| layer:turn_of_candle:turn_of_candle:1m | bracket_1atr_2atr_24 | 87535 / -12.0 / 0.17 / -3.32 | 0 |  |
| layer:turn_of_candle:turn_of_candle:1m | bracket_1.5atr_3atr_24 | 87535 / -11.9 / 0.22 / -2.21 | 0 |  |
| layer:turn_of_candle:turn_of_candle:1m | time_24_wide_stop_2atr | 87535 / -11.3 / 0.22 / -1.56 | 0 |  |
| layer:turn_of_candle:turn_of_candle:1m | time_96_wide_stop_2atr | 87535 / -11.3 / 0.17 / -1.55 | 0 |  |
| layer:turn_of_candle:turn_of_candle:1m | be1atr_trail2atr_96 | 87535 / -11.2 / 0.12 / -3.03 | 0 |  |

## Summary

- cells run: 114 (all are trials; none dropped).
- cells positive in TRAIN and VALIDATE with n >= 30: 0.
