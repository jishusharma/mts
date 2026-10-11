# CAPTURE MATRIX

Generated 2026-10-09 06:05 by capture.py. Fire files: fires_cryptocred_failed_msb_15m.csv, fires_cryptocred_failed_msb_1h.csv, fires_cryptocred_fib_pullback_15m.csv, fires_cryptocred_fib_pullback_1h.csv, fires_cryptocred_sr_flip_15m.csv, fires_cryptocred_sr_flip_1h.csv, fires_fabio_cvd_absorption_15m.csv, fires_fabio_cvd_absorption_1h.csv, fires_fabio_escalation_15m.csv, fires_fabio_escalation_1h.csv, fires_fabio_volume_fvg_15m.csv, fires_fabio_volume_fvg_1h.csv, fires_rsi_malkan_bear_1h.csv, fires_rsi_malkan_bull_1h.csv, fires_rsi_rsi_events_15m.csv, fires_rsi_rsi_events_1h.csv, fires_rsi_rsi_events_5m.csv, fires_session_session_momentum_15m.csv, fires_turn_of_candle_turn_of_candle_1m.csv.
Ground truth: bigmoves.py legs + labels, TFs 5m, 15m, 1h, 4h, coverage 2022-01-01 00:05 .. 2026-10-08 00:00 UTC.
50921 fire rows were not scored because they carry no long/short side or no time (for the RSI event files these are the tradable=0 rows: cross / support / rejection events with an empty side).
Settings: ATR(14) Wilder per TF; legs = ATR zigzag, r in [1.5, 2.0] (reversal), k in [3, 5, 8] (leg size, ATR); H in [24, 96] bars; round-trip fee 0.0010 of price (2 x Deribit taker).
Columns: legs = same-side legs flagged (r,k); E/M/L = share of legs with a same-side fire in the first 25% / 25-50% / last 50% of the leg; catch = E or M; lead = median bars of leg still ahead at the first E/M fire; hitH = share of fires with forward MFE(H) >= k ATR; baseH = same share over all bars in the layer's fire span; lift = hit/base; feeDom = share of fires with stop < round-trip fee.

## r=1.5  k=3

| layer key | tf | side | set | legs | E | M | L | catch | lead | fires | hit24 | base24 | lift24 | hit96 | base96 | lift96 | feeDom |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| layer:cryptocred:failed_msb:15m | 15m | long | all | 5889 | 0.00 | 0.01 | 0.01 | 0.01 | 6.0 | 317 | 0.36 | 0.33 | 1.09 | 0.65 | 0.64 | 1.02 | 0.00 |
| layer:cryptocred:failed_msb:15m | 15m | short | all | 5865 | 0.00 | 0.00 | 0.01 | 0.00 | 5.0 | 280 | 0.36 | 0.34 | 1.06 | 0.69 | 0.63 | 1.08 | 0.00 |
| layer:cryptocred:failed_msb:1h | 1h | long | all | 1410 | 0.00 | 0.00 | 0.01 | 0.01 | 4.5 | 102 | 0.40 | 0.34 | 1.20 | 0.66 | 0.65 | 1.02 | 0.00 |
| layer:cryptocred:failed_msb:1h | 1h | short | all | 1455 | 0.01 | 0.00 | 0.01 | 0.01 | 9.5 | 64 | 0.34 | 0.34 | 1.01 | 0.62 | 0.63 | 1.00 | 0.00 |
| layer:cryptocred:fib_pullback:15m | 15m | long | all | 5889 | 0.03 | 0.01 | 0.02 | 0.04 | 7.0 | 1376 | 0.36 | 0.33 | 1.11 | 0.66 | 0.64 | 1.03 | 0.00 |
| layer:cryptocred:fib_pullback:15m | 15m | short | all | 5865 | 0.00 | 0.00 | 0.01 | 0.01 | 7.0 | 254 | 0.33 | 0.34 | 0.97 | 0.63 | 0.64 | 0.99 | 0.00 |
| layer:cryptocred:fib_pullback:1h | 1h | long | all | 1410 | 0.03 | 0.02 | 0.02 | 0.05 | 7.0 | 324 | 0.38 | 0.34 | 1.12 | 0.65 | 0.65 | 1.01 | 0.00 |
| layer:cryptocred:fib_pullback:1h | 1h | short | all | 1455 | 0.01 | 0.00 | 0.01 | 0.01 | 6.0 | 66 | 0.42 | 0.34 | 1.25 | 0.62 | 0.63 | 0.99 | 0.00 |
| layer:cryptocred:sr_flip:15m | 15m | long | all | 5889 | 0.05 | 0.09 | 0.17 | 0.14 | 7.0 | 3062 | 0.34 | 0.33 | 1.03 | 0.64 | 0.64 | 1.00 | 0.49 |
| layer:cryptocred:sr_flip:15m | 15m | long | ok | 5889 | 0.03 | 0.04 | 0.09 | 0.07 | 6.0 | 1573 | 0.34 | 0.33 | 1.04 | 0.64 | 0.64 | 0.99 | 0.00 |
| layer:cryptocred:sr_flip:15m | 15m | short | all | 5865 | 0.04 | 0.08 | 0.17 | 0.12 | 6.0 | 3009 | 0.35 | 0.34 | 1.05 | 0.64 | 0.64 | 1.00 | 1.00 |
| layer:cryptocred:sr_flip:1h | 1h | long | all | 1410 | 0.05 | 0.08 | 0.19 | 0.12 | 7.0 | 755 | 0.34 | 0.34 | 1.00 | 0.64 | 0.65 | 0.99 | 0.50 |
| layer:cryptocred:sr_flip:1h | 1h | long | ok | 1410 | 0.02 | 0.04 | 0.09 | 0.07 | 6.0 | 380 | 0.35 | 0.34 | 1.03 | 0.67 | 0.65 | 1.04 | 0.00 |
| layer:cryptocred:sr_flip:1h | 1h | short | all | 1455 | 0.05 | 0.08 | 0.18 | 0.13 | 6.0 | 774 | 0.34 | 0.34 | 1.00 | 0.66 | 0.63 | 1.05 | 1.00 |
| layer:fabio:cvd_absorption:15m | 15m | long | all | 5889 | 0.04 | 0.03 | 0.05 | 0.07 | 7.0 | 1988 | 0.33 | 0.33 | 1.01 | 0.64 | 0.64 | 1.00 | - |
| layer:fabio:cvd_absorption:15m | 15m | short | all | 5865 | 0.03 | 0.03 | 0.04 | 0.05 | 6.0 | 1547 | 0.35 | 0.34 | 1.04 | 0.65 | 0.64 | 1.02 | - |
| layer:fabio:cvd_absorption:1h | 1h | long | all | 1410 | 0.03 | 0.04 | 0.05 | 0.06 | 8.0 | 504 | 0.34 | 0.34 | 1.01 | 0.66 | 0.64 | 1.02 | - |
| layer:fabio:cvd_absorption:1h | 1h | short | all | 1455 | 0.01 | 0.02 | 0.03 | 0.03 | 6.0 | 302 | 0.34 | 0.34 | 1.01 | 0.61 | 0.63 | 0.98 | - |
| layer:fabio:escalation:15m | 15m | long | all | 5889 | 0.01 | 0.01 | 0.04 | 0.02 | 3.0 | 340 | 0.46 | 0.33 | 1.40 | 0.73 | 0.64 | 1.14 | - |
| layer:fabio:escalation:15m | 15m | short | all | 5865 | 0.01 | 0.01 | 0.04 | 0.02 | 3.0 | 387 | 0.46 | 0.34 | 1.37 | 0.67 | 0.63 | 1.06 | - |
| layer:fabio:escalation:1h | 1h | long | all | 1410 | 0.00 | 0.00 | 0.01 | 0.01 | 4.0 | 25 | 0.60 | 0.34 | 1.77 | 0.84 | 0.64 | 1.31 | - |
| layer:fabio:escalation:1h | 1h | short | all | 1455 | 0.00 | 0.00 | 0.01 | 0.00 | 2.0 | 29 | 0.41 | 0.34 | 1.22 | 0.64 | 0.62 | 1.03 | - |
| layer:fabio:volume_fvg:15m | 15m | long | all | 5889 | 0.01 | 0.01 | 0.03 | 0.02 | 7.0 | 532 | 0.38 | 0.33 | 1.15 | 0.65 | 0.64 | 1.01 | - |
| layer:fabio:volume_fvg:15m | 15m | short | all | 5865 | 0.01 | 0.01 | 0.03 | 0.01 | 6.0 | 569 | 0.38 | 0.34 | 1.13 | 0.65 | 0.64 | 1.03 | - |
| layer:fabio:volume_fvg:1h | 1h | long | all | 1410 | 0.00 | 0.00 | 0.03 | 0.01 | 7.5 | 104 | 0.38 | 0.34 | 1.14 | 0.70 | 0.65 | 1.09 | - |
| layer:fabio:volume_fvg:1h | 1h | short | all | 1455 | 0.00 | 0.01 | 0.03 | 0.01 | 6.5 | 144 | 0.31 | 0.34 | 0.92 | 0.54 | 0.63 | 0.85 | - |
| layer:rsi:malkan_bear:1h | 1h | short | all | 1455 | 0.02 | 0.00 | 0.00 | 0.02 | 5.0 | 143 | 0.40 | 0.34 | 1.17 | 0.69 | 0.63 | 1.09 | - |
| layer:rsi:malkan_bull:1h | 1h | long | all | 1410 | 0.01 | 0.00 | 0.00 | 0.02 | 7.0 | 116 | 0.39 | 0.34 | 1.15 | 0.65 | 0.65 | 1.01 | - |
| layer:rsi:rsi_events:15m | 15m | long | all | 5889 | 0.02 | 0.02 | 0.01 | 0.04 | 7.0 | 675 | 0.27 | 0.33 | 0.82 | 0.62 | 0.64 | 0.96 | - |
| layer:rsi:rsi_events:15m | 15m | short | all | 5865 | 0.01 | 0.02 | 0.08 | 0.02 | 6.0 | 891 | 0.38 | 0.34 | 1.11 | 0.65 | 0.64 | 1.03 | - |
| layer:rsi:rsi_events:1h | 1h | long | all | 1410 | 0.02 | 0.01 | 0.01 | 0.03 | 10.0 | 171 | 0.29 | 0.34 | 0.85 | 0.65 | 0.65 | 1.01 | - |
| layer:rsi:rsi_events:1h | 1h | short | all | 1455 | 0.01 | 0.01 | 0.07 | 0.02 | 7.0 | 209 | 0.39 | 0.34 | 1.13 | 0.65 | 0.63 | 1.03 | - |
| layer:rsi:rsi_events:5m | 5m | long | all | 18910 | 0.02 | 0.02 | 0.01 | 0.04 | 7.0 | 2110 | 0.31 | 0.34 | 0.91 | 0.62 | 0.64 | 0.98 | - |
| layer:rsi:rsi_events:5m | 5m | short | all | 18964 | 0.01 | 0.02 | 0.08 | 0.03 | 6.0 | 3131 | 0.37 | 0.35 | 1.08 | 0.64 | 0.64 | 1.00 | - |
| layer:session:session_momentum:15m | 15m | long | all | 5889 | 0.01 | 0.01 | 0.03 | 0.03 | 6.5 | 865 | 0.20 | 0.33 | 0.60 | 0.60 | 0.64 | 0.93 | - |
| layer:session:session_momentum:15m | 15m | short | all | 5865 | 0.02 | 0.01 | 0.03 | 0.03 | 8.0 | 875 | 0.27 | 0.34 | 0.80 | 0.60 | 0.64 | 0.95 | - |

## r=1.5  k=5

| layer key | tf | side | set | legs | E | M | L | catch | lead | fires | hit24 | base24 | lift24 | hit96 | base96 | lift96 | feeDom |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| layer:cryptocred:failed_msb:15m | 15m | long | all | 1774 | 0.00 | 0.01 | 0.02 | 0.01 | 8.5 | 317 | 0.19 | 0.15 | 1.22 | 0.44 | 0.45 | 1.00 | 0.00 |
| layer:cryptocred:failed_msb:15m | 15m | short | all | 1805 | 0.00 | 0.00 | 0.01 | 0.01 | 6.0 | 280 | 0.14 | 0.16 | 0.89 | 0.46 | 0.45 | 1.04 | 0.00 |
| layer:cryptocred:failed_msb:1h | 1h | long | all | 475 | 0.01 | 0.01 | 0.02 | 0.01 | 7.0 | 102 | 0.22 | 0.16 | 1.35 | 0.44 | 0.45 | 0.98 | 0.00 |
| layer:cryptocred:failed_msb:1h | 1h | short | all | 455 | 0.01 | 0.00 | 0.00 | 0.01 | 10.0 | 64 | 0.17 | 0.16 | 1.08 | 0.41 | 0.44 | 0.92 | 0.00 |
| layer:cryptocred:fib_pullback:15m | 15m | long | all | 1774 | 0.03 | 0.02 | 0.02 | 0.05 | 9.0 | 1376 | 0.16 | 0.15 | 1.04 | 0.46 | 0.45 | 1.03 | 0.00 |
| layer:cryptocred:fib_pullback:15m | 15m | short | all | 1805 | 0.00 | 0.00 | 0.02 | 0.01 | 7.0 | 254 | 0.14 | 0.16 | 0.88 | 0.45 | 0.45 | 1.00 | 0.00 |
| layer:cryptocred:fib_pullback:1h | 1h | long | all | 475 | 0.04 | 0.02 | 0.02 | 0.06 | 9.0 | 324 | 0.20 | 0.16 | 1.23 | 0.47 | 0.45 | 1.04 | 0.00 |
| layer:cryptocred:fib_pullback:1h | 1h | short | all | 455 | 0.01 | 0.00 | 0.03 | 0.01 | 12.5 | 66 | 0.15 | 0.16 | 0.95 | 0.48 | 0.44 | 1.10 | 0.00 |
| layer:cryptocred:sr_flip:15m | 15m | long | all | 1774 | 0.06 | 0.10 | 0.16 | 0.16 | 8.0 | 3062 | 0.17 | 0.15 | 1.10 | 0.45 | 0.45 | 1.01 | 0.49 |
| layer:cryptocred:sr_flip:15m | 15m | long | ok | 1774 | 0.03 | 0.04 | 0.09 | 0.08 | 7.0 | 1573 | 0.18 | 0.15 | 1.15 | 0.45 | 0.45 | 1.02 | 0.00 |
| layer:cryptocred:sr_flip:15m | 15m | short | all | 1805 | 0.07 | 0.10 | 0.16 | 0.17 | 7.0 | 3009 | 0.17 | 0.16 | 1.08 | 0.45 | 0.45 | 1.01 | 1.00 |
| layer:cryptocred:sr_flip:1h | 1h | long | all | 475 | 0.07 | 0.08 | 0.18 | 0.15 | 7.0 | 755 | 0.18 | 0.16 | 1.12 | 0.46 | 0.45 | 1.01 | 0.50 |
| layer:cryptocred:sr_flip:1h | 1h | long | ok | 475 | 0.04 | 0.03 | 0.08 | 0.07 | 6.0 | 380 | 0.19 | 0.16 | 1.18 | 0.50 | 0.45 | 1.10 | 0.00 |
| layer:cryptocred:sr_flip:1h | 1h | short | all | 455 | 0.09 | 0.11 | 0.17 | 0.20 | 7.0 | 774 | 0.18 | 0.16 | 1.15 | 0.48 | 0.44 | 1.10 | 1.00 |
| layer:fabio:cvd_absorption:15m | 15m | long | all | 1774 | 0.04 | 0.04 | 0.04 | 0.08 | 8.0 | 1988 | 0.17 | 0.15 | 1.07 | 0.46 | 0.45 | 1.03 | - |
| layer:fabio:cvd_absorption:15m | 15m | short | all | 1805 | 0.03 | 0.03 | 0.03 | 0.06 | 7.0 | 1547 | 0.17 | 0.16 | 1.06 | 0.47 | 0.45 | 1.06 | - |
| layer:fabio:cvd_absorption:1h | 1h | long | all | 475 | 0.03 | 0.03 | 0.05 | 0.06 | 9.0 | 504 | 0.16 | 0.16 | 1.01 | 0.45 | 0.45 | 1.00 | - |
| layer:fabio:cvd_absorption:1h | 1h | short | all | 455 | 0.01 | 0.03 | 0.03 | 0.04 | 8.0 | 302 | 0.16 | 0.16 | 0.98 | 0.44 | 0.44 | 0.99 | - |
| layer:fabio:escalation:15m | 15m | long | all | 1774 | 0.01 | 0.02 | 0.06 | 0.03 | 4.0 | 340 | 0.29 | 0.15 | 1.88 | 0.56 | 0.45 | 1.27 | - |
| layer:fabio:escalation:15m | 15m | short | all | 1805 | 0.01 | 0.02 | 0.07 | 0.03 | 4.0 | 387 | 0.23 | 0.16 | 1.44 | 0.50 | 0.45 | 1.11 | - |
| layer:fabio:escalation:1h | 1h | long | all | 475 | 0.01 | 0.01 | 0.01 | 0.01 | 5.0 | 25 | 0.36 | 0.16 | 2.24 | 0.76 | 0.45 | 1.68 | - |
| layer:fabio:escalation:1h | 1h | short | all | 455 | 0.00 | 0.00 | 0.02 | 0.01 | 2.0 | 29 | 0.28 | 0.16 | 1.75 | 0.57 | 0.44 | 1.31 | - |
| layer:fabio:volume_fvg:15m | 15m | long | all | 1774 | 0.01 | 0.01 | 0.05 | 0.02 | 9.0 | 532 | 0.18 | 0.15 | 1.19 | 0.47 | 0.45 | 1.04 | - |
| layer:fabio:volume_fvg:15m | 15m | short | all | 1805 | 0.01 | 0.01 | 0.05 | 0.02 | 7.0 | 569 | 0.19 | 0.16 | 1.15 | 0.47 | 0.45 | 1.04 | - |
| layer:fabio:volume_fvg:1h | 1h | long | all | 475 | 0.01 | 0.01 | 0.04 | 0.01 | 7.0 | 104 | 0.15 | 0.16 | 0.96 | 0.46 | 0.45 | 1.02 | - |
| layer:fabio:volume_fvg:1h | 1h | short | all | 455 | 0.00 | 0.02 | 0.05 | 0.02 | 7.0 | 144 | 0.14 | 0.16 | 0.87 | 0.36 | 0.44 | 0.82 | - |
| layer:rsi:malkan_bear:1h | 1h | short | all | 455 | 0.02 | 0.01 | 0.00 | 0.03 | 6.5 | 143 | 0.20 | 0.16 | 1.22 | 0.50 | 0.44 | 1.13 | - |
| layer:rsi:malkan_bull:1h | 1h | long | all | 475 | 0.02 | 0.00 | 0.00 | 0.02 | 6.0 | 116 | 0.16 | 0.16 | 1.01 | 0.46 | 0.46 | 1.02 | - |
| layer:rsi:rsi_events:15m | 15m | long | all | 1774 | 0.03 | 0.01 | 0.00 | 0.04 | 9.0 | 675 | 0.13 | 0.15 | 0.82 | 0.41 | 0.45 | 0.92 | - |
| layer:rsi:rsi_events:15m | 15m | short | all | 1805 | 0.02 | 0.03 | 0.10 | 0.04 | 7.0 | 891 | 0.19 | 0.16 | 1.18 | 0.47 | 0.45 | 1.05 | - |
| layer:rsi:rsi_events:1h | 1h | long | all | 475 | 0.03 | 0.00 | 0.01 | 0.03 | 13.5 | 171 | 0.13 | 0.16 | 0.84 | 0.41 | 0.45 | 0.90 | - |
| layer:rsi:rsi_events:1h | 1h | short | all | 455 | 0.01 | 0.03 | 0.09 | 0.04 | 7.0 | 209 | 0.19 | 0.16 | 1.17 | 0.47 | 0.44 | 1.06 | - |
| layer:rsi:rsi_events:5m | 5m | long | all | 5811 | 0.03 | 0.01 | 0.01 | 0.04 | 9.0 | 2110 | 0.13 | 0.15 | 0.83 | 0.41 | 0.44 | 0.93 | - |
| layer:rsi:rsi_events:5m | 5m | short | all | 5661 | 0.01 | 0.04 | 0.11 | 0.05 | 6.0 | 3131 | 0.20 | 0.16 | 1.23 | 0.47 | 0.45 | 1.03 | - |
| layer:session:session_momentum:15m | 15m | long | all | 1774 | 0.01 | 0.01 | 0.03 | 0.02 | 8.0 | 865 | 0.09 | 0.15 | 0.56 | 0.40 | 0.45 | 0.89 | - |
| layer:session:session_momentum:15m | 15m | short | all | 1805 | 0.02 | 0.01 | 0.03 | 0.03 | 9.0 | 875 | 0.10 | 0.16 | 0.64 | 0.43 | 0.45 | 0.95 | - |

## Groups with no ground truth (tf not built)
- layer:turn_of_candle:turn_of_candle:1m 1m long: 83927 fire rows
- layer:turn_of_candle:turn_of_candle:1m 1m short: 83180 fire rows

Full matrix (all r, k, fire sets, counts, z, MAE): F:\MTS\data\bigtrade\CAPTURE_MATRIX.csv
