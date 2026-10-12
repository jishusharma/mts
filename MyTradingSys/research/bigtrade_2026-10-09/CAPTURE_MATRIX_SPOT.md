# CAPTURE MATRIX

Generated 2026-10-09 06:55 by capture.py. Fire files: fires_cryptocred_failed_msb_15m.csv, fires_cryptocred_failed_msb_1h.csv, fires_cryptocred_fib_pullback_15m.csv, fires_cryptocred_fib_pullback_1h.csv, fires_cryptocred_sr_flip_15m.csv, fires_cryptocred_sr_flip_1h.csv, fires_fabio_cvd_absorption_15m.csv, fires_fabio_cvd_absorption_1h.csv, fires_fabio_escalation_15m.csv, fires_fabio_escalation_1h.csv, fires_fabio_volume_fvg_15m.csv, fires_fabio_volume_fvg_1h.csv, fires_rsi_malkan_bear_1h.csv, fires_rsi_malkan_bull_1h.csv, fires_rsi_rsi_events_15m.csv, fires_rsi_rsi_events_1h.csv, fires_rsi_rsi_events_5m.csv, fires_session_session_momentum_15m.csv, fires_turn_of_candle_turn_of_candle_1m.csv.
Ground truth: bigmoves.py legs + labels, TFs 5m, 15m, 1h, 4h, coverage 2022-01-01 00:05 .. 2026-10-08 00:00 UTC.
51084 fire rows were not scored because they carry no long/short side or no time (for the RSI event files these are the tradable=0 rows: cross / support / rejection events with an empty side).
Settings: ATR(14) Wilder per TF; legs = ATR zigzag, r in [1.5, 2.0] (reversal), k in [3, 5, 8] (leg size, ATR); H in [24, 96] bars; round-trip fee 0.0010 of price (2 x Deribit taker).
Columns: legs = same-side legs flagged (r,k); E/M/L = share of legs with a same-side fire in the first 25% / 25-50% / last 50% of the leg; catch = E or M; lead = median bars of leg still ahead at the first E/M fire; hitH = share of fires with forward MFE(H) >= k ATR; baseH = same share over all bars in the layer's fire span; lift = hit/base; feeDom = share of fires with stop < round-trip fee.

## r=1.5  k=3

| layer key | tf | side | set | legs | E | M | L | catch | lead | fires | hit24 | base24 | lift24 | hit96 | base96 | lift96 | feeDom |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| layer:cryptocred:failed_msb:15m | 15m | long | all | 5889 | 0.00 | 0.00 | 0.01 | 0.01 | 7.0 | 286 | 0.35 | 0.33 | 1.06 | 0.65 | 0.64 | 1.01 | 0.00 |
| layer:cryptocred:failed_msb:15m | 15m | short | all | 5865 | 0.00 | 0.00 | 0.01 | 0.01 | 6.0 | 280 | 0.39 | 0.34 | 1.16 | 0.67 | 0.64 | 1.06 | 0.00 |
| layer:cryptocred:failed_msb:1h | 1h | long | all | 1410 | 0.00 | 0.01 | 0.01 | 0.01 | 6.0 | 98 | 0.36 | 0.34 | 1.06 | 0.54 | 0.65 | 0.84 | 0.00 |
| layer:cryptocred:failed_msb:1h | 1h | short | all | 1455 | 0.01 | 0.00 | 0.00 | 0.01 | 6.0 | 75 | 0.27 | 0.34 | 0.78 | 0.55 | 0.63 | 0.87 | 0.00 |
| layer:cryptocred:fib_pullback:15m | 15m | long | all | 5889 | 0.03 | 0.01 | 0.02 | 0.04 | 7.5 | 1446 | 0.36 | 0.33 | 1.09 | 0.67 | 0.64 | 1.04 | 0.00 |
| layer:cryptocred:fib_pullback:15m | 15m | short | all | 5865 | 0.00 | 0.00 | 0.02 | 0.01 | 8.0 | 263 | 0.33 | 0.34 | 0.99 | 0.59 | 0.63 | 0.93 | 0.00 |
| layer:cryptocred:fib_pullback:1h | 1h | long | all | 1410 | 0.03 | 0.01 | 0.02 | 0.05 | 7.0 | 373 | 0.34 | 0.34 | 1.02 | 0.66 | 0.65 | 1.02 | 0.00 |
| layer:cryptocred:fib_pullback:1h | 1h | short | all | 1455 | 0.00 | 0.00 | 0.02 | 0.00 | 10.0 | 70 | 0.47 | 0.34 | 1.38 | 0.69 | 0.63 | 1.09 | 0.00 |
| layer:cryptocred:sr_flip:15m | 15m | long | all | 5889 | 0.05 | 0.09 | 0.18 | 0.14 | 7.0 | 3130 | 0.34 | 0.33 | 1.03 | 0.64 | 0.64 | 1.00 | 0.49 |
| layer:cryptocred:sr_flip:15m | 15m | short | all | 5865 | 0.04 | 0.08 | 0.17 | 0.13 | 6.0 | 3066 | 0.35 | 0.34 | 1.05 | 0.64 | 0.64 | 1.01 | 1.00 |
| layer:cryptocred:sr_flip:1h | 1h | long | all | 1410 | 0.05 | 0.07 | 0.19 | 0.12 | 7.0 | 807 | 0.32 | 0.34 | 0.96 | 0.66 | 0.65 | 1.02 | 0.48 |
| layer:cryptocred:sr_flip:1h | 1h | short | all | 1455 | 0.05 | 0.07 | 0.18 | 0.12 | 6.0 | 781 | 0.36 | 0.34 | 1.05 | 0.66 | 0.63 | 1.05 | 1.00 |
| layer:fabio:cvd_absorption:15m | 15m | long | all | 5889 | 0.05 | 0.05 | 0.08 | 0.09 | 7.0 | 2923 | 0.34 | 0.33 | 1.04 | 0.66 | 0.64 | 1.03 | - |
| layer:fabio:cvd_absorption:15m | 15m | short | all | 5865 | 0.02 | 0.02 | 0.04 | 0.05 | 7.0 | 1501 | 0.35 | 0.34 | 1.04 | 0.64 | 0.64 | 1.01 | - |
| layer:fabio:cvd_absorption:1h | 1h | long | all | 1410 | 0.05 | 0.04 | 0.08 | 0.09 | 7.0 | 787 | 0.34 | 0.34 | 1.02 | 0.64 | 0.65 | 1.00 | - |
| layer:fabio:cvd_absorption:1h | 1h | short | all | 1455 | 0.01 | 0.02 | 0.03 | 0.03 | 6.0 | 282 | 0.33 | 0.34 | 0.97 | 0.62 | 0.63 | 0.98 | - |
| layer:fabio:escalation:15m | 15m | long | all | 5889 | 0.00 | 0.01 | 0.03 | 0.01 | 4.0 | 322 | 0.41 | 0.33 | 1.26 | 0.72 | 0.64 | 1.12 | - |
| layer:fabio:escalation:15m | 15m | short | all | 5865 | 0.01 | 0.01 | 0.03 | 0.01 | 4.0 | 347 | 0.42 | 0.34 | 1.24 | 0.68 | 0.63 | 1.08 | - |
| layer:fabio:escalation:1h | 1h | long | all | 1410 | 0.00 | 0.00 | 0.01 | 0.00 | 4.5 | 26 | 0.46 | 0.34 | 1.38 | 0.69 | 0.64 | 1.08 | - |
| layer:fabio:escalation:1h | 1h | short | all | 1455 | 0.00 | 0.00 | 0.01 | 0.01 | 2.5 | 33 | 0.42 | 0.34 | 1.24 | 0.72 | 0.63 | 1.15 | - |
| layer:fabio:volume_fvg:15m | 15m | long | all | 5889 | 0.01 | 0.01 | 0.03 | 0.02 | 6.0 | 493 | 0.35 | 0.33 | 1.07 | 0.64 | 0.64 | 1.00 | - |
| layer:fabio:volume_fvg:15m | 15m | short | all | 5865 | 0.01 | 0.01 | 0.03 | 0.01 | 7.0 | 521 | 0.37 | 0.34 | 1.09 | 0.67 | 0.63 | 1.06 | - |
| layer:fabio:volume_fvg:1h | 1h | long | all | 1410 | 0.01 | 0.01 | 0.02 | 0.02 | 5.0 | 122 | 0.35 | 0.34 | 1.05 | 0.65 | 0.64 | 1.01 | - |
| layer:fabio:volume_fvg:1h | 1h | short | all | 1455 | 0.01 | 0.01 | 0.03 | 0.02 | 7.0 | 116 | 0.32 | 0.34 | 0.94 | 0.66 | 0.63 | 1.04 | - |
| layer:rsi:malkan_bear:1h | 1h | short | all | 1455 | 0.02 | 0.00 | 0.00 | 0.02 | 4.0 | 138 | 0.41 | 0.34 | 1.21 | 0.70 | 0.63 | 1.12 | - |
| layer:rsi:malkan_bull:1h | 1h | long | all | 1410 | 0.01 | 0.00 | 0.00 | 0.01 | 7.0 | 112 | 0.38 | 0.34 | 1.11 | 0.65 | 0.65 | 1.00 | - |
| layer:rsi:rsi_events:15m | 15m | long | all | 5889 | 0.02 | 0.02 | 0.01 | 0.04 | 8.0 | 664 | 0.30 | 0.33 | 0.90 | 0.64 | 0.64 | 0.99 | - |
| layer:rsi:rsi_events:15m | 15m | short | all | 5865 | 0.01 | 0.02 | 0.07 | 0.03 | 6.0 | 914 | 0.39 | 0.34 | 1.15 | 0.66 | 0.64 | 1.04 | - |
| layer:rsi:rsi_events:1h | 1h | long | all | 1410 | 0.02 | 0.01 | 0.01 | 0.04 | 9.0 | 162 | 0.31 | 0.34 | 0.93 | 0.68 | 0.65 | 1.05 | - |
| layer:rsi:rsi_events:1h | 1h | short | all | 1455 | 0.01 | 0.01 | 0.07 | 0.02 | 7.0 | 208 | 0.38 | 0.34 | 1.11 | 0.64 | 0.63 | 1.02 | - |
| layer:rsi:rsi_events:5m | 5m | long | all | 18910 | 0.02 | 0.02 | 0.01 | 0.04 | 7.0 | 2084 | 0.29 | 0.34 | 0.84 | 0.61 | 0.64 | 0.96 | - |
| layer:rsi:rsi_events:5m | 5m | short | all | 18964 | 0.01 | 0.02 | 0.08 | 0.03 | 6.0 | 3063 | 0.37 | 0.35 | 1.07 | 0.64 | 0.64 | 1.00 | - |
| layer:session:session_momentum:15m | 15m | long | all | 5889 | 0.01 | 0.01 | 0.03 | 0.03 | 7.0 | 866 | 0.20 | 0.33 | 0.60 | 0.60 | 0.64 | 0.93 | - |
| layer:session:session_momentum:15m | 15m | short | all | 5865 | 0.02 | 0.01 | 0.03 | 0.03 | 7.5 | 873 | 0.27 | 0.34 | 0.80 | 0.61 | 0.64 | 0.95 | - |

## r=1.5  k=5

| layer key | tf | side | set | legs | E | M | L | catch | lead | fires | hit24 | base24 | lift24 | hit96 | base96 | lift96 | feeDom |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| layer:cryptocred:failed_msb:15m | 15m | long | all | 1774 | 0.00 | 0.01 | 0.01 | 0.01 | 6.0 | 286 | 0.18 | 0.15 | 1.18 | 0.46 | 0.45 | 1.04 | 0.00 |
| layer:cryptocred:failed_msb:15m | 15m | short | all | 1805 | 0.00 | 0.00 | 0.01 | 0.01 | 7.0 | 280 | 0.19 | 0.16 | 1.15 | 0.46 | 0.45 | 1.04 | 0.00 |
| layer:cryptocred:failed_msb:1h | 1h | long | all | 475 | 0.01 | 0.01 | 0.01 | 0.02 | 6.0 | 98 | 0.19 | 0.16 | 1.21 | 0.40 | 0.45 | 0.88 | 0.00 |
| layer:cryptocred:failed_msb:1h | 1h | short | all | 455 | 0.01 | 0.00 | 0.00 | 0.01 | 9.0 | 75 | 0.19 | 0.16 | 1.16 | 0.39 | 0.44 | 0.88 | 0.00 |
| layer:cryptocred:fib_pullback:15m | 15m | long | all | 1774 | 0.03 | 0.02 | 0.02 | 0.05 | 10.0 | 1446 | 0.18 | 0.15 | 1.17 | 0.49 | 0.45 | 1.10 | 0.00 |
| layer:cryptocred:fib_pullback:15m | 15m | short | all | 1805 | 0.01 | 0.01 | 0.02 | 0.01 | 10.5 | 263 | 0.17 | 0.16 | 1.09 | 0.42 | 0.45 | 0.93 | 0.00 |
| layer:cryptocred:fib_pullback:1h | 1h | long | all | 475 | 0.03 | 0.02 | 0.01 | 0.05 | 7.0 | 373 | 0.18 | 0.16 | 1.10 | 0.46 | 0.45 | 1.01 | 0.00 |
| layer:cryptocred:fib_pullback:1h | 1h | short | all | 455 | 0.01 | 0.00 | 0.02 | 0.01 | 13.0 | 70 | 0.20 | 0.16 | 1.25 | 0.49 | 0.44 | 1.10 | 0.00 |
| layer:cryptocred:sr_flip:15m | 15m | long | all | 1774 | 0.07 | 0.10 | 0.17 | 0.17 | 8.0 | 3130 | 0.17 | 0.15 | 1.11 | 0.46 | 0.45 | 1.02 | 0.49 |
| layer:cryptocred:sr_flip:15m | 15m | short | all | 1805 | 0.07 | 0.10 | 0.16 | 0.17 | 7.0 | 3066 | 0.18 | 0.16 | 1.10 | 0.45 | 0.45 | 1.01 | 1.00 |
| layer:cryptocred:sr_flip:1h | 1h | long | all | 475 | 0.08 | 0.10 | 0.15 | 0.17 | 8.0 | 807 | 0.17 | 0.16 | 1.04 | 0.47 | 0.45 | 1.05 | 0.48 |
| layer:cryptocred:sr_flip:1h | 1h | short | all | 455 | 0.09 | 0.07 | 0.17 | 0.16 | 6.0 | 781 | 0.18 | 0.16 | 1.10 | 0.49 | 0.44 | 1.10 | 1.00 |
| layer:fabio:cvd_absorption:15m | 15m | long | all | 1774 | 0.06 | 0.05 | 0.08 | 0.10 | 8.0 | 2923 | 0.18 | 0.15 | 1.15 | 0.47 | 0.45 | 1.05 | - |
| layer:fabio:cvd_absorption:15m | 15m | short | all | 1805 | 0.03 | 0.02 | 0.04 | 0.05 | 8.0 | 1501 | 0.17 | 0.16 | 1.06 | 0.46 | 0.45 | 1.03 | - |
| layer:fabio:cvd_absorption:1h | 1h | long | all | 475 | 0.05 | 0.04 | 0.08 | 0.09 | 7.0 | 787 | 0.16 | 0.16 | 0.99 | 0.44 | 0.45 | 0.98 | - |
| layer:fabio:cvd_absorption:1h | 1h | short | all | 455 | 0.02 | 0.01 | 0.02 | 0.03 | 11.0 | 282 | 0.13 | 0.16 | 0.80 | 0.42 | 0.44 | 0.95 | - |
| layer:fabio:escalation:15m | 15m | long | all | 1774 | 0.01 | 0.02 | 0.05 | 0.02 | 4.0 | 322 | 0.25 | 0.15 | 1.59 | 0.53 | 0.45 | 1.20 | - |
| layer:fabio:escalation:15m | 15m | short | all | 1805 | 0.01 | 0.01 | 0.05 | 0.02 | 4.5 | 347 | 0.24 | 0.16 | 1.51 | 0.53 | 0.45 | 1.20 | - |
| layer:fabio:escalation:1h | 1h | long | all | 475 | 0.00 | 0.00 | 0.03 | 0.01 | 6.0 | 26 | 0.27 | 0.16 | 1.69 | 0.58 | 0.45 | 1.28 | - |
| layer:fabio:escalation:1h | 1h | short | all | 455 | 0.00 | 0.01 | 0.02 | 0.01 | 3.5 | 33 | 0.27 | 0.16 | 1.71 | 0.69 | 0.44 | 1.57 | - |
| layer:fabio:volume_fvg:15m | 15m | long | all | 1774 | 0.01 | 0.01 | 0.05 | 0.02 | 7.0 | 493 | 0.16 | 0.15 | 1.06 | 0.43 | 0.44 | 0.97 | - |
| layer:fabio:volume_fvg:15m | 15m | short | all | 1805 | 0.01 | 0.01 | 0.04 | 0.02 | 7.0 | 521 | 0.18 | 0.16 | 1.11 | 0.50 | 0.45 | 1.11 | - |
| layer:fabio:volume_fvg:1h | 1h | long | all | 475 | 0.01 | 0.01 | 0.04 | 0.02 | 6.5 | 122 | 0.23 | 0.16 | 1.43 | 0.50 | 0.45 | 1.10 | - |
| layer:fabio:volume_fvg:1h | 1h | short | all | 455 | 0.01 | 0.02 | 0.04 | 0.03 | 7.0 | 116 | 0.17 | 0.16 | 1.08 | 0.47 | 0.44 | 1.08 | - |
| layer:rsi:malkan_bear:1h | 1h | short | all | 455 | 0.02 | 0.01 | 0.00 | 0.03 | 5.0 | 138 | 0.22 | 0.16 | 1.40 | 0.51 | 0.44 | 1.17 | - |
| layer:rsi:malkan_bull:1h | 1h | long | all | 475 | 0.01 | 0.00 | 0.00 | 0.01 | 6.0 | 112 | 0.17 | 0.16 | 1.05 | 0.43 | 0.46 | 0.94 | - |
| layer:rsi:rsi_events:15m | 15m | long | all | 1774 | 0.03 | 0.01 | 0.00 | 0.04 | 9.0 | 664 | 0.14 | 0.15 | 0.89 | 0.42 | 0.45 | 0.94 | - |
| layer:rsi:rsi_events:15m | 15m | short | all | 1805 | 0.01 | 0.03 | 0.10 | 0.04 | 7.0 | 914 | 0.20 | 0.16 | 1.23 | 0.48 | 0.45 | 1.06 | - |
| layer:rsi:rsi_events:1h | 1h | long | all | 475 | 0.03 | 0.01 | 0.01 | 0.04 | 13.0 | 162 | 0.16 | 0.16 | 1.00 | 0.43 | 0.45 | 0.94 | - |
| layer:rsi:rsi_events:1h | 1h | short | all | 455 | 0.01 | 0.03 | 0.08 | 0.04 | 7.0 | 208 | 0.19 | 0.16 | 1.20 | 0.48 | 0.44 | 1.08 | - |
| layer:rsi:rsi_events:5m | 5m | long | all | 5811 | 0.02 | 0.01 | 0.01 | 0.04 | 9.0 | 2084 | 0.12 | 0.15 | 0.76 | 0.40 | 0.44 | 0.90 | - |
| layer:rsi:rsi_events:5m | 5m | short | all | 5661 | 0.01 | 0.03 | 0.10 | 0.05 | 6.0 | 3063 | 0.19 | 0.16 | 1.21 | 0.46 | 0.45 | 1.02 | - |
| layer:session:session_momentum:15m | 15m | long | all | 1774 | 0.01 | 0.01 | 0.03 | 0.02 | 8.0 | 866 | 0.08 | 0.15 | 0.54 | 0.40 | 0.45 | 0.89 | - |
| layer:session:session_momentum:15m | 15m | short | all | 1805 | 0.02 | 0.01 | 0.03 | 0.03 | 9.0 | 873 | 0.10 | 0.16 | 0.64 | 0.43 | 0.45 | 0.95 | - |

## Groups with no ground truth (tf not built)
- layer:turn_of_candle:turn_of_candle:1m 1m long: 80965 fire rows
- layer:turn_of_candle:turn_of_candle:1m 1m short: 86155 fire rows

Full matrix (all r, k, fire sets, counts, z, MAE): F:\MTS\data\bigtrade\CAPTURE_MATRIX_SPOT.csv
