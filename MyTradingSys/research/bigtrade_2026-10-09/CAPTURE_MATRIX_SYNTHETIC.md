# CAPTURE MATRIX  -  SYNTHETIC FIXTURE, NOT LAYER OUTPUT

Generated 2026-10-09 06:05 by capture.py. Fire files: fires_synthetic.csv.
The fires here are generated from the ground-truth legs themselves (oracle / random / anti-oracle) to exercise the tool. They say nothing about any real layer.
Ground truth: bigmoves.py legs + labels, TFs 5m, 15m, 1h, 4h, coverage 2022-01-01 00:05 .. 2026-10-08 00:00 UTC.
Settings: ATR(14) Wilder per TF; legs = ATR zigzag, r in [1.5, 2.0] (reversal), k in [3, 5, 8] (leg size, ATR); H in [24, 96] bars; round-trip fee 0.0010 of price (2 x Deribit taker).
Columns: legs = same-side legs flagged (r,k); E/M/L = share of legs with a same-side fire in the first 25% / 25-50% / last 50% of the leg; catch = E or M; lead = median bars of leg still ahead at the first E/M fire; hitH = share of fires with forward MFE(H) >= k ATR; baseH = same share over all bars in the layer's fire span; lift = hit/base; feeDom = share of fires with stop < round-trip fee.

## r=1.5  k=3

| layer key | tf | side | set | legs | E | M | L | catch | lead | fires | hit24 | base24 | lift24 | hit96 | base96 | lift96 | feeDom |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| synthetic:anti_at_pivot:1h | 1h | long | all | 1410 | 0.00 | 0.00 | 0.44 | 0.00 | - | 1455 | 0.13 | 0.34 | 0.39 | 0.45 | 0.64 | 0.70 | 0.00 |
| synthetic:anti_at_pivot:1h | 1h | long | ok | 1410 | 0.00 | 0.00 | 0.44 | 0.00 | - | 1454 | 0.13 | 0.34 | 0.39 | 0.45 | 0.64 | 0.69 | 0.00 |
| synthetic:anti_at_pivot:1h | 1h | short | all | 1455 | 0.00 | 0.00 | 0.38 | 0.00 | - | 1410 | 0.14 | 0.34 | 0.40 | 0.43 | 0.63 | 0.68 | 0.00 |
| synthetic:anti_at_pivot:1h | 1h | short | ok | 1455 | 0.00 | 0.00 | 0.38 | 0.00 | - | 1409 | 0.14 | 0.34 | 0.40 | 0.42 | 0.63 | 0.67 | 0.00 |
| synthetic:anti_at_pivot:4h | 4h | long | all | 369 | 0.00 | 0.00 | 0.42 | 0.00 | - | 352 | 0.12 | 0.35 | 0.33 | 0.46 | 0.66 | 0.69 | 0.00 |
| synthetic:anti_at_pivot:4h | 4h | short | all | 352 | 0.00 | 0.00 | 0.45 | 0.00 | - | 369 | 0.11 | 0.33 | 0.32 | 0.39 | 0.60 | 0.64 | 0.00 |
| synthetic:oracle_at_pivot:1h | 1h | long | all | 1410 | 1.00 | 0.00 | 0.00 | 1.00 | 7.0 | 1410 | 0.72 | 0.34 | 2.15 | 0.88 | 0.64 | 1.37 | 0.00 |
| synthetic:oracle_at_pivot:1h | 1h | long | ok | 1410 | 1.00 | 0.00 | 0.00 | 1.00 | 7.0 | 1409 | 0.72 | 0.34 | 2.15 | 0.88 | 0.64 | 1.37 | 0.00 |
| synthetic:oracle_at_pivot:1h | 1h | short | all | 1455 | 1.00 | 0.00 | 0.00 | 1.00 | 6.0 | 1455 | 0.76 | 0.34 | 2.23 | 0.89 | 0.63 | 1.41 | 0.00 |
| synthetic:oracle_at_pivot:1h | 1h | short | ok | 1455 | 1.00 | 0.00 | 0.00 | 1.00 | 6.0 | 1454 | 0.76 | 0.34 | 2.23 | 0.89 | 0.63 | 1.41 | 0.00 |
| synthetic:oracle_at_pivot:4h | 4h | long | all | 369 | 1.00 | 0.00 | 0.00 | 1.00 | 8.0 | 369 | 0.72 | 0.35 | 2.03 | 0.88 | 0.66 | 1.33 | 0.00 |
| synthetic:oracle_at_pivot:4h | 4h | short | all | 352 | 1.00 | 0.00 | 0.00 | 1.00 | 7.0 | 352 | 0.73 | 0.33 | 2.19 | 0.86 | 0.60 | 1.43 | 0.00 |
| synthetic:random:1h | 1h | long | all | 1410 | 0.07 | 0.05 | 0.10 | 0.11 | 8.0 | 1040 | 0.35 | 0.34 | 1.05 | 0.63 | 0.65 | 0.98 | 0.31 |
| synthetic:random:1h | 1h | long | ok | 1410 | 0.05 | 0.04 | 0.07 | 0.08 | 8.5 | 714 | 0.35 | 0.34 | 1.06 | 0.62 | 0.65 | 0.96 | 0.00 |
| synthetic:random:1h | 1h | short | all | 1455 | 0.06 | 0.04 | 0.09 | 0.10 | 7.0 | 960 | 0.38 | 0.34 | 1.12 | 0.62 | 0.63 | 0.99 | 0.30 |
| synthetic:random:1h | 1h | short | ok | 1455 | 0.04 | 0.03 | 0.06 | 0.07 | 8.0 | 670 | 0.40 | 0.34 | 1.18 | 0.64 | 0.63 | 1.01 | 0.00 |
| synthetic:random:4h | 4h | long | all | 369 | 0.25 | 0.17 | 0.31 | 0.37 | 9.0 | 971 | 0.35 | 0.35 | 1.00 | 0.66 | 0.66 | 0.99 | 0.25 |
| synthetic:random:4h | 4h | long | ok | 369 | 0.19 | 0.12 | 0.26 | 0.28 | 10.0 | 726 | 0.34 | 0.35 | 0.98 | 0.65 | 0.66 | 0.98 | 0.00 |
| synthetic:random:4h | 4h | short | all | 352 | 0.22 | 0.18 | 0.32 | 0.36 | 7.0 | 1029 | 0.33 | 0.33 | 0.98 | 0.60 | 0.60 | 1.00 | 0.25 |
| synthetic:random:4h | 4h | short | ok | 352 | 0.17 | 0.12 | 0.27 | 0.28 | 7.0 | 776 | 0.33 | 0.33 | 0.99 | 0.59 | 0.60 | 0.98 | 0.00 |

## r=1.5  k=5

| layer key | tf | side | set | legs | E | M | L | catch | lead | fires | hit24 | base24 | lift24 | hit96 | base96 | lift96 | feeDom |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| synthetic:anti_at_pivot:1h | 1h | long | all | 475 | 0.00 | 0.00 | 0.44 | 0.00 | - | 1455 | 0.06 | 0.16 | 0.37 | 0.30 | 0.45 | 0.67 | 0.00 |
| synthetic:anti_at_pivot:1h | 1h | long | ok | 475 | 0.00 | 0.00 | 0.44 | 0.00 | - | 1454 | 0.06 | 0.16 | 0.37 | 0.30 | 0.45 | 0.67 | 0.00 |
| synthetic:anti_at_pivot:1h | 1h | short | all | 455 | 0.00 | 0.00 | 0.38 | 0.00 | - | 1410 | 0.07 | 0.16 | 0.42 | 0.30 | 0.44 | 0.68 | 0.00 |
| synthetic:anti_at_pivot:1h | 1h | short | ok | 455 | 0.00 | 0.00 | 0.38 | 0.00 | - | 1409 | 0.07 | 0.16 | 0.41 | 0.30 | 0.44 | 0.68 | 0.00 |
| synthetic:anti_at_pivot:4h | 4h | long | all | 121 | 0.00 | 0.00 | 0.38 | 0.00 | - | 352 | 0.05 | 0.16 | 0.31 | 0.29 | 0.46 | 0.63 | 0.00 |
| synthetic:anti_at_pivot:4h | 4h | short | all | 107 | 0.00 | 0.00 | 0.46 | 0.00 | - | 369 | 0.04 | 0.14 | 0.27 | 0.25 | 0.40 | 0.64 | 0.00 |
| synthetic:oracle_at_pivot:1h | 1h | long | all | 475 | 1.00 | 0.00 | 0.00 | 1.00 | 8.0 | 1410 | 0.37 | 0.16 | 2.30 | 0.65 | 0.45 | 1.45 | 0.00 |
| synthetic:oracle_at_pivot:1h | 1h | long | ok | 475 | 1.00 | 0.00 | 0.00 | 1.00 | 8.0 | 1409 | 0.37 | 0.16 | 2.30 | 0.65 | 0.45 | 1.45 | 0.00 |
| synthetic:oracle_at_pivot:1h | 1h | short | all | 455 | 1.00 | 0.00 | 0.00 | 1.00 | 7.0 | 1455 | 0.39 | 0.16 | 2.42 | 0.66 | 0.44 | 1.50 | 0.00 |
| synthetic:oracle_at_pivot:1h | 1h | short | ok | 455 | 1.00 | 0.00 | 0.00 | 1.00 | 7.0 | 1454 | 0.39 | 0.16 | 2.42 | 0.66 | 0.44 | 1.50 | 0.00 |
| synthetic:oracle_at_pivot:4h | 4h | long | all | 121 | 1.00 | 0.00 | 0.00 | 1.00 | 10.0 | 369 | 0.33 | 0.16 | 2.11 | 0.64 | 0.46 | 1.39 | 0.00 |
| synthetic:oracle_at_pivot:4h | 4h | short | all | 107 | 1.00 | 0.00 | 0.00 | 1.00 | 9.0 | 352 | 0.34 | 0.14 | 2.37 | 0.64 | 0.40 | 1.60 | 0.00 |
| synthetic:random:1h | 1h | long | all | 475 | 0.08 | 0.06 | 0.12 | 0.13 | 11.0 | 1040 | 0.17 | 0.16 | 1.07 | 0.44 | 0.45 | 0.96 | 0.31 |
| synthetic:random:1h | 1h | long | ok | 475 | 0.05 | 0.04 | 0.07 | 0.09 | 11.0 | 714 | 0.17 | 0.16 | 1.09 | 0.43 | 0.45 | 0.95 | 0.00 |
| synthetic:random:1h | 1h | short | all | 455 | 0.07 | 0.06 | 0.11 | 0.12 | 9.0 | 960 | 0.19 | 0.16 | 1.18 | 0.43 | 0.44 | 0.99 | 0.30 |
| synthetic:random:1h | 1h | short | ok | 455 | 0.05 | 0.05 | 0.09 | 0.09 | 9.0 | 670 | 0.20 | 0.16 | 1.28 | 0.44 | 0.44 | 1.00 | 0.00 |
| synthetic:random:4h | 4h | long | all | 121 | 0.26 | 0.19 | 0.37 | 0.39 | 11.0 | 971 | 0.15 | 0.16 | 0.97 | 0.47 | 0.46 | 1.01 | 0.25 |
| synthetic:random:4h | 4h | long | ok | 121 | 0.18 | 0.14 | 0.31 | 0.29 | 11.0 | 726 | 0.13 | 0.16 | 0.83 | 0.44 | 0.46 | 0.96 | 0.00 |
| synthetic:random:4h | 4h | short | all | 107 | 0.29 | 0.25 | 0.44 | 0.48 | 10.0 | 1029 | 0.13 | 0.14 | 0.92 | 0.39 | 0.40 | 0.97 | 0.25 |
| synthetic:random:4h | 4h | short | ok | 107 | 0.22 | 0.20 | 0.37 | 0.38 | 11.0 | 776 | 0.13 | 0.14 | 0.87 | 0.38 | 0.40 | 0.96 | 0.00 |

Full matrix (all r, k, fire sets, counts, z, MAE): F:\MTS\data\bigtrade\CAPTURE_MATRIX_SYNTHETIC.csv
