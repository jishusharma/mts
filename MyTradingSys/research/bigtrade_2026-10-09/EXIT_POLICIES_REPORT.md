> **RERUN 2026-10-17 (DEV only, new labels):** see EXIT_POLICIES_RERUN_DEV_2026-10-17.md (same code, TRAIN = 2022-01..2024-06 only; the VALIDATE column was NOT re-read). TRAIN-positive cells 9 -> 11; the single old BOTH+ cell (sr_flip_1h time_96_wide_stop_2atr) is TRAIN +9.8 bp (n 1024) -> +7.6 bp (n 878). Verdict unchanged: no policy rescues the layers. VALIDATION 2024-07..2025-06 stays unchecked for that cell.

> **CONTAMINATED (DEV read VALIDATION 2024-07..12)** - TRAIN column ran to 2025-01-01 (exit_policies.py TRAIN_END), so it includes 2024-07..12; VALIDATE column is 2025-01..06 only (VALIDATION 2024-07..12 not in it). See MyTradingSys/backtest/bigtrade/SPLIT_ALIGNMENT_2026-10-17.md. Numbers below are kept as originally run, not recomputed.

# EXIT POLICIES REPORT (backtest C), 2026-10-09

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
| layer:cryptocred:failed_msb:15m | live_like_1pct_2pct_8bars | 396 / -8.0 / 0.37 / -0.08 | 57 / -11.2 / 0.32 / -0.11 |  |
| layer:cryptocred:failed_msb:15m | bracket_1atr_2atr_24 | 396 / -10.4 / 0.33 / -0.49 | 57 / -9.8 / 0.39 / -0.36 |  |
| layer:cryptocred:failed_msb:15m | bracket_1.5atr_3atr_24 | 396 / -8.5 / 0.36 / -0.32 | 57 / -15.2 / 0.33 / -0.39 |  |
| layer:cryptocred:failed_msb:15m | time_24_wide_stop_2atr | 396 / -12.9 / 0.32 / -0.29 | 57 / -4.2 / 0.37 / -0.12 |  |
| layer:cryptocred:failed_msb:15m | time_96_wide_stop_2atr | 396 / -13.4 / 0.20 / -0.23 | 57 / -2.2 / 0.18 / -0.03 |  |
| layer:cryptocred:failed_msb:15m | be1atr_trail2atr_96 | 396 / -13.8 / 0.20 / -0.58 | 57 / -0.2 / 0.28 / -0.08 |  |
| layer:cryptocred:failed_msb:1h | live_like_1pct_2pct_8bars | 109 / -15.3 / 0.36 / -0.15 | 17 / -27.6 / 0.29 / -0.28 |  |
| layer:cryptocred:failed_msb:1h | bracket_1atr_2atr_24 | 109 / -13.7 / 0.30 / -0.31 | 17 / -8.8 / 0.41 / -0.03 |  |
| layer:cryptocred:failed_msb:1h | bracket_1.5atr_3atr_24 | 109 / -19.6 / 0.30 / -0.22 | 17 / -50.7 / 0.29 / -0.37 |  |
| layer:cryptocred:failed_msb:1h | time_24_wide_stop_2atr | 109 / -5.1 / 0.25 / -0.05 | 17 / -53.1 / 0.35 / -0.36 |  |
| layer:cryptocred:failed_msb:1h | time_96_wide_stop_2atr | 109 / +22.6 / 0.19 / +0.20 | 17 / +27.6 / 0.29 / +0.41 |  |
| layer:cryptocred:failed_msb:1h | be1atr_trail2atr_96 | 109 / -3.9 / 0.21 / -0.13 | 17 / +23.7 / 0.41 / +0.42 |  |
| layer:cryptocred:fib_pullback:15m | live_like_1pct_2pct_8bars | 1149 / -13.8 / 0.37 / -0.14 | 147 / -9.7 / 0.35 / -0.10 |  |
| layer:cryptocred:fib_pullback:15m | bracket_1atr_2atr_24 | 1149 / -12.1 / 0.34 / -0.50 | 147 / -11.3 / 0.35 / -0.43 |  |
| layer:cryptocred:fib_pullback:15m | bracket_1.5atr_3atr_24 | 1149 / -10.1 / 0.36 / -0.31 | 147 / -13.5 / 0.36 / -0.30 |  |
| layer:cryptocred:fib_pullback:15m | time_24_wide_stop_2atr | 1149 / -13.7 / 0.34 / -0.27 | 147 / -18.3 / 0.32 / -0.37 |  |
| layer:cryptocred:fib_pullback:15m | time_96_wide_stop_2atr | 1149 / -12.3 / 0.20 / -0.23 | 147 / -23.1 / 0.18 / -0.49 |  |
| layer:cryptocred:fib_pullback:15m | be1atr_trail2atr_96 | 1149 / -10.2 / 0.22 / -0.45 | 147 / -3.7 / 0.24 / -0.25 |  |
| layer:cryptocred:fib_pullback:1h | live_like_1pct_2pct_8bars | 278 / -16.2 / 0.36 / -0.16 | 47 / -11.6 / 0.43 / -0.12 |  |
| layer:cryptocred:fib_pullback:1h | bracket_1atr_2atr_24 | 278 / -14.1 / 0.31 / -0.32 | 47 / -10.6 / 0.36 / -0.14 |  |
| layer:cryptocred:fib_pullback:1h | bracket_1.5atr_3atr_24 | 278 / -20.1 / 0.36 / -0.21 | 47 / -26.6 / 0.38 / -0.19 |  |
| layer:cryptocred:fib_pullback:1h | time_24_wide_stop_2atr | 278 / -25.6 / 0.37 / -0.17 | 47 / -29.3 / 0.40 / -0.09 |  |
| layer:cryptocred:fib_pullback:1h | time_96_wide_stop_2atr | 278 / -5.1 / 0.23 / +0.05 | 47 / -30.9 / 0.26 / -0.14 |  |
| layer:cryptocred:fib_pullback:1h | be1atr_trail2atr_96 | 278 / -18.6 / 0.21 / -0.30 | 47 / -17.3 / 0.28 / -0.18 |  |
| layer:cryptocred:sr_flip:15m | live_like_1pct_2pct_8bars | 4035 / -11.5 / 0.35 / -0.11 | 583 / -11.1 / 0.39 / -0.11 |  |
| layer:cryptocred:sr_flip:15m | bracket_1atr_2atr_24 | 4035 / -12.4 / 0.33 / -0.49 | 583 / -9.7 / 0.34 / -0.45 |  |
| layer:cryptocred:sr_flip:15m | bracket_1.5atr_3atr_24 | 4035 / -12.8 / 0.34 / -0.33 | 583 / -6.9 / 0.36 / -0.28 |  |
| layer:cryptocred:sr_flip:15m | time_24_wide_stop_2atr | 4035 / -14.9 / 0.31 / -0.28 | 583 / -4.1 / 0.35 / -0.16 |  |
| layer:cryptocred:sr_flip:15m | time_96_wide_stop_2atr | 4035 / -10.9 / 0.21 / -0.18 | 583 / -3.9 / 0.23 / -0.12 |  |
| layer:cryptocred:sr_flip:15m | be1atr_trail2atr_96 | 4035 / -13.1 / 0.19 / -0.50 | 583 / -11.4 / 0.19 / -0.50 |  |
| layer:cryptocred:sr_flip:1h | live_like_1pct_2pct_8bars | 1024 / -15.2 / 0.35 / -0.15 | 163 / -5.7 / 0.44 / -0.06 |  |
| layer:cryptocred:sr_flip:1h | bracket_1atr_2atr_24 | 1024 / -16.3 / 0.32 / -0.26 | 163 / -14.4 / 0.30 / -0.32 |  |
| layer:cryptocred:sr_flip:1h | bracket_1.5atr_3atr_24 | 1024 / -21.3 / 0.34 / -0.20 | 163 / -3.4 / 0.35 / -0.10 |  |
| layer:cryptocred:sr_flip:1h | time_24_wide_stop_2atr | 1024 / -13.3 / 0.35 / -0.09 | 163 / -11.4 / 0.33 / -0.05 |  |
| layer:cryptocred:sr_flip:1h | time_96_wide_stop_2atr | 1024 / +9.8 / 0.23 / +0.15 | 163 / +0.1 / 0.25 / +0.02 | YES |
| layer:cryptocred:sr_flip:1h | be1atr_trail2atr_96 | 1024 / -19.3 / 0.21 / -0.28 | 163 / -7.6 / 0.21 / -0.18 |  |
| layer:fabio:cvd_absorption:15m | live_like_1pct_2pct_8bars | 2861 / -12.5 / 0.35 / -0.12 | 417 / -3.4 / 0.43 / -0.03 |  |
| layer:fabio:cvd_absorption:15m | bracket_1atr_2atr_24 | 2861 / -12.8 / 0.32 / -0.57 | 417 / -5.9 / 0.37 / -0.41 |  |
| layer:fabio:cvd_absorption:15m | bracket_1.5atr_3atr_24 | 2861 / -14.8 / 0.33 / -0.41 | 417 / -3.7 / 0.40 / -0.23 |  |
| layer:fabio:cvd_absorption:15m | time_24_wide_stop_2atr | 2861 / -15.4 / 0.30 / -0.32 | 417 / +1.1 / 0.39 / -0.08 |  |
| layer:fabio:cvd_absorption:15m | time_96_wide_stop_2atr | 2861 / -12.0 / 0.19 / -0.26 | 417 / +8.0 / 0.26 / +0.06 |  |
| layer:fabio:cvd_absorption:15m | be1atr_trail2atr_96 | 2861 / -12.4 / 0.20 / -0.55 | 417 / -5.4 / 0.23 / -0.35 |  |
| layer:fabio:cvd_absorption:1h | live_like_1pct_2pct_8bars | 687 / -10.6 / 0.39 / -0.11 | 120 / -24.8 / 0.32 / -0.25 |  |
| layer:fabio:cvd_absorption:1h | bracket_1atr_2atr_24 | 687 / -13.6 / 0.34 / -0.22 | 120 / -23.2 / 0.27 / -0.44 |  |
| layer:fabio:cvd_absorption:1h | bracket_1.5atr_3atr_24 | 687 / -16.1 / 0.36 / -0.16 | 120 / -33.3 / 0.28 / -0.36 |  |
| layer:fabio:cvd_absorption:1h | time_24_wide_stop_2atr | 687 / -5.1 / 0.35 / -0.02 | 120 / -41.2 / 0.25 / -0.28 |  |
| layer:fabio:cvd_absorption:1h | time_96_wide_stop_2atr | 687 / +26.9 / 0.23 / +0.35 | 120 / -63.5 / 0.14 / -0.49 |  |
| layer:fabio:cvd_absorption:1h | be1atr_trail2atr_96 | 687 / -19.1 / 0.20 / -0.27 | 120 / -26.8 / 0.16 / -0.49 |  |
| layer:fabio:escalation:15m | live_like_1pct_2pct_8bars | 731 / -16.7 / 0.26 / -0.17 | 109 / -6.6 / 0.30 / -0.07 |  |
| layer:fabio:escalation:15m | bracket_1atr_2atr_24 | 731 / -11.2 / 0.31 / -0.95 | 109 / -3.1 / 0.44 / -0.35 |  |
| layer:fabio:escalation:15m | bracket_1.5atr_3atr_24 | 731 / -12.7 / 0.32 / -0.66 | 109 / -1.1 / 0.41 / -0.20 |  |
| layer:fabio:escalation:15m | time_24_wide_stop_2atr | 731 / -10.3 / 0.26 / -0.50 | 109 / +23.4 / 0.34 / +0.26 |  |
| layer:fabio:escalation:15m | time_96_wide_stop_2atr | 731 / -3.5 / 0.16 / -0.42 | 109 / +13.8 / 0.28 / +0.16 |  |
| layer:fabio:escalation:15m | be1atr_trail2atr_96 | 731 / -13.1 / 0.15 / -1.06 | 109 / -1.1 / 0.24 / -0.23 |  |
| layer:fabio:escalation:1h | live_like_1pct_2pct_8bars | 52 / -20.5 / 0.31 / -0.21 | 3 / -86.7 / 0.00 / -0.87 |  |
| layer:fabio:escalation:1h | bracket_1atr_2atr_24 | 52 / -18.8 / 0.35 / -0.34 | 3 / -80.3 / 0.00 / -1.19 |  |
| layer:fabio:escalation:1h | bracket_1.5atr_3atr_24 | 52 / -12.4 / 0.35 / -0.23 | 3 / -114.5 / 0.00 / -1.13 |  |
| layer:fabio:escalation:1h | time_24_wide_stop_2atr | 52 / +13.0 / 0.19 / +0.07 | 3 / -76.3 / 0.33 / -0.71 |  |
| layer:fabio:escalation:1h | time_96_wide_stop_2atr | 52 / -15.0 / 0.12 / -0.09 | 3 / -148.7 / 0.00 / -1.09 |  |
| layer:fabio:escalation:1h | be1atr_trail2atr_96 | 52 / +4.0 / 0.25 / -0.07 | 3 / -63.2 / 0.00 / -0.85 |  |
| layer:fabio:volume_fvg:15m | live_like_1pct_2pct_8bars | 606 / -9.3 / 0.35 / -0.09 | 107 / -17.9 / 0.36 / -0.18 |  |
| layer:fabio:volume_fvg:15m | bracket_1atr_2atr_24 | 606 / -11.9 / 0.32 / -0.52 | 107 / -14.3 / 0.34 / -0.51 |  |
| layer:fabio:volume_fvg:15m | bracket_1.5atr_3atr_24 | 606 / -11.8 / 0.33 / -0.35 | 107 / -13.9 / 0.32 / -0.41 |  |
| layer:fabio:volume_fvg:15m | time_24_wide_stop_2atr | 606 / -8.4 / 0.30 / -0.25 | 107 / -14.6 / 0.30 / -0.33 |  |
| layer:fabio:volume_fvg:15m | time_96_wide_stop_2atr | 606 / -10.3 / 0.21 / -0.14 | 107 / -22.8 / 0.15 / -0.34 |  |
| layer:fabio:volume_fvg:15m | be1atr_trail2atr_96 | 606 / -10.0 / 0.20 / -0.45 | 107 / -8.5 / 0.21 / -0.41 |  |
| layer:fabio:volume_fvg:1h | live_like_1pct_2pct_8bars | 142 / -17.9 / 0.35 / -0.18 | 30 / -27.4 / 0.30 / -0.27 |  |
| layer:fabio:volume_fvg:1h | bracket_1atr_2atr_24 | 142 / -29.6 / 0.28 / -0.38 | 30 / -21.7 / 0.33 / -0.28 |  |
| layer:fabio:volume_fvg:1h | bracket_1.5atr_3atr_24 | 142 / -31.4 / 0.35 / -0.17 | 30 / -26.0 / 0.37 / -0.17 |  |
| layer:fabio:volume_fvg:1h | time_24_wide_stop_2atr | 142 / -31.3 / 0.35 / -0.12 | 30 / +22.6 / 0.40 / +0.07 |  |
| layer:fabio:volume_fvg:1h | time_96_wide_stop_2atr | 142 / -12.0 / 0.23 / +0.10 | 30 / +70.3 / 0.30 / +0.17 |  |
| layer:fabio:volume_fvg:1h | be1atr_trail2atr_96 | 142 / -19.6 / 0.19 / -0.20 | 30 / +3.1 / 0.27 / +0.07 |  |
| layer:rsi:malkan_bear:1h | live_like_1pct_2pct_8bars | 86 / -14.1 / 0.34 / -0.14 | 20 / -27.4 / 0.35 / -0.27 |  |
| layer:rsi:malkan_bear:1h | bracket_1atr_2atr_24 | 86 / -15.5 / 0.33 / -0.23 | 20 / -1.2 / 0.25 / -0.47 |  |
| layer:rsi:malkan_bear:1h | bracket_1.5atr_3atr_24 | 86 / -19.6 / 0.31 / -0.20 | 20 / -18.2 / 0.25 / -0.44 |  |
| layer:rsi:malkan_bear:1h | time_24_wide_stop_2atr | 86 / -14.0 / 0.29 / -0.19 | 20 / -15.8 / 0.25 / -0.35 |  |
| layer:rsi:malkan_bear:1h | time_96_wide_stop_2atr | 86 / -16.9 / 0.20 / -0.20 | 20 / -39.3 / 0.15 / -0.42 |  |
| layer:rsi:malkan_bear:1h | be1atr_trail2atr_96 | 86 / -20.6 / 0.19 / -0.29 | 20 / -19.2 / 0.10 / -0.53 |  |
| layer:rsi:malkan_bull:1h | live_like_1pct_2pct_8bars | 72 / -24.8 / 0.36 / -0.25 | 12 / -15.2 / 0.33 / -0.15 |  |
| layer:rsi:malkan_bull:1h | bracket_1atr_2atr_24 | 72 / -20.3 / 0.29 / -0.35 | 12 / -39.6 / 0.25 / -0.48 |  |
| layer:rsi:malkan_bull:1h | bracket_1.5atr_3atr_24 | 72 / -7.7 / 0.33 / -0.18 | 12 / -76.0 / 0.17 / -0.65 |  |
| layer:rsi:malkan_bull:1h | time_24_wide_stop_2atr | 72 / +12.3 / 0.43 / +0.12 | 12 / -7.3 / 0.50 / +0.11 |  |
| layer:rsi:malkan_bull:1h | time_96_wide_stop_2atr | 72 / +76.0 / 0.29 / +0.77 | 12 / -104.3 / 0.08 / -0.93 |  |
| layer:rsi:malkan_bull:1h | be1atr_trail2atr_96 | 72 / -3.8 / 0.18 / -0.05 | 12 / -52.4 / 0.17 / -0.69 |  |
| layer:rsi:rsi_events:15m | live_like_1pct_2pct_8bars | 962 / -9.0 / 0.37 / -0.09 | 167 / -4.8 / 0.37 / -0.05 |  |
| layer:rsi:rsi_events:15m | bracket_1atr_2atr_24 | 962 / -8.9 / 0.36 / -0.39 | 167 / -7.0 / 0.39 / -0.34 |  |
| layer:rsi:rsi_events:15m | bracket_1.5atr_3atr_24 | 962 / -7.5 / 0.38 / -0.24 | 167 / -2.7 / 0.38 / -0.24 |  |
| layer:rsi:rsi_events:15m | time_24_wide_stop_2atr | 962 / -10.1 / 0.34 / -0.22 | 167 / -0.8 / 0.38 / -0.04 |  |
| layer:rsi:rsi_events:15m | time_96_wide_stop_2atr | 962 / -6.1 / 0.22 / -0.18 | 167 / +1.0 / 0.23 / -0.00 |  |
| layer:rsi:rsi_events:15m | be1atr_trail2atr_96 | 962 / -9.7 / 0.23 / -0.39 | 167 / -4.6 / 0.22 / -0.29 |  |
| layer:rsi:rsi_events:1h | live_like_1pct_2pct_8bars | 230 / -8.8 / 0.40 / -0.09 | 42 / -18.2 / 0.40 / -0.18 |  |
| layer:rsi:rsi_events:1h | bracket_1atr_2atr_24 | 230 / -19.2 / 0.33 / -0.22 | 42 / -7.9 / 0.33 / -0.13 |  |
| layer:rsi:rsi_events:1h | bracket_1.5atr_3atr_24 | 230 / -12.2 / 0.40 / -0.04 | 42 / -17.1 / 0.29 / -0.24 |  |
| layer:rsi:rsi_events:1h | time_24_wide_stop_2atr | 230 / +5.7 / 0.42 / +0.18 | 42 / -34.8 / 0.26 / -0.24 |  |
| layer:rsi:rsi_events:1h | time_96_wide_stop_2atr | 230 / +23.3 / 0.27 / +0.40 | 42 / -64.1 / 0.21 / -0.47 |  |
| layer:rsi:rsi_events:1h | be1atr_trail2atr_96 | 230 / -15.4 / 0.24 / -0.16 | 42 / -9.8 / 0.26 / -0.10 |  |
| layer:rsi:rsi_events:5m | live_like_1pct_2pct_8bars | 3204 / -11.8 / 0.32 / -0.12 | 532 / -12.8 / 0.27 / -0.13 |  |
| layer:rsi:rsi_events:5m | bracket_1atr_2atr_24 | 3204 / -11.9 / 0.30 / -0.95 | 532 / -13.1 / 0.27 / -1.13 |  |
| layer:rsi:rsi_events:5m | bracket_1.5atr_3atr_24 | 3204 / -11.2 / 0.34 / -0.61 | 532 / -13.3 / 0.29 / -0.78 |  |
| layer:rsi:rsi_events:5m | time_24_wide_stop_2atr | 3204 / -12.3 / 0.30 / -0.49 | 532 / -11.5 / 0.27 / -0.50 |  |
| layer:rsi:rsi_events:5m | time_96_wide_stop_2atr | 3204 / -11.4 / 0.21 / -0.45 | 532 / -13.9 / 0.20 / -0.58 |  |
| layer:rsi:rsi_events:5m | be1atr_trail2atr_96 | 3204 / -12.0 / 0.17 / -0.93 | 532 / -12.1 / 0.14 / -1.08 |  |
| layer:session:session_momentum:15m | live_like_1pct_2pct_8bars | 1095 / -15.2 / 0.36 / -0.15 | 181 / -11.6 / 0.39 / -0.12 |  |
| layer:session:session_momentum:15m | bracket_1atr_2atr_24 | 1095 / -13.5 / 0.33 / -0.46 | 181 / -8.9 / 0.35 / -0.42 |  |
| layer:session:session_momentum:15m | bracket_1.5atr_3atr_24 | 1095 / -14.7 / 0.34 / -0.37 | 181 / -11.2 / 0.34 / -0.30 |  |
| layer:session:session_momentum:15m | time_24_wide_stop_2atr | 1095 / -11.5 / 0.34 / -0.23 | 181 / -10.2 / 0.35 / -0.29 |  |
| layer:session:session_momentum:15m | time_96_wide_stop_2atr | 1095 / -10.7 / 0.22 / -0.19 | 181 / -12.3 / 0.22 / -0.15 |  |
| layer:session:session_momentum:15m | be1atr_trail2atr_96 | 1095 / -12.6 / 0.18 / -0.44 | 181 / -6.2 / 0.19 / -0.38 |  |
| layer:turn_of_candle:turn_of_candle:1m | live_like_1pct_2pct_8bars | 105199 / -11.8 / 0.20 / -0.12 | 17376 / -11.9 / 0.20 / -0.12 |  |
| layer:turn_of_candle:turn_of_candle:1m | bracket_1atr_2atr_24 | 105199 / -11.9 / 0.17 / -3.19 | 17376 / -11.7 / 0.13 / -3.24 |  |
| layer:turn_of_candle:turn_of_candle:1m | bracket_1.5atr_3atr_24 | 105199 / -11.9 / 0.22 / -2.12 | 17376 / -11.8 / 0.21 / -2.16 |  |
| layer:turn_of_candle:turn_of_candle:1m | time_24_wide_stop_2atr | 105199 / -11.3 / 0.22 / -1.49 | 17376 / -11.2 / 0.22 / -1.55 |  |
| layer:turn_of_candle:turn_of_candle:1m | time_96_wide_stop_2atr | 105199 / -11.3 / 0.17 / -1.49 | 17376 / -11.3 / 0.17 / -1.52 |  |
| layer:turn_of_candle:turn_of_candle:1m | be1atr_trail2atr_96 | 105199 / -11.1 / 0.12 / -2.91 | 17376 / -10.8 / 0.12 / -2.96 |  |

## Summary

- cells run: 114 (all are trials; none dropped).
- cells positive in TRAIN and VALIDATE with n >= 30: 1.
  - layer:cryptocred:sr_flip:1h / time_96_wide_stop_2atr

## Conclusion (backtest C, 2026-10-09)
- No exit policy rescues the existing fires. 1 of 114 cells is positive in both splits (cryptocred sr_flip 1h, 96-bar hold, 2 ATR stop: +9.8 bp TRAIN, +0.1 bp VALIDATE, n 1024 / 163). With 114 trials a few false positives are expected, VALIDATE is zero within noise, and no PBO was run: not a candidate until D.
- turn_of_candle 1m (79 % of live testnet trades): mean net is -11.1 to -11.9 bp under all six policies in both splits (n 105,199 / 17,376). The assumed round-trip cost is 12 bp, so gross is about +0.1 to +0.9 bp: the signal pays its fees and nothing else. Win share 12-22 %. Managed exits do not change it (answers F-BT-02: only the volume-generator purpose can justify keeping it).
- The live-like policy (1 % stop / 2 % target / 8 bars) is not worse than the managed ones on any layer. Time exits are not the reason the layers fail; the fires carry no directional information worth the cost (capture-matrix lift about 1.0 agrees).
- The positive TRAIN cells at long holds (malkan_bull 1h +76 bp, cvd_absorption 1h +27 bp) flip sign in VALIDATE (-104, -64 bp): regime dependence or noise, n 12-120.
- HOLDOUT not read. Backtest D (tuning) on these fires is not justified by C; the productive next step is new information (regime / session split B154, Tom zones), not tuning of current layers.
