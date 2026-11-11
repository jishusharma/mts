# RESULT: trend following, 4h and daily (PREREG.md fixed before the run; script trend.py; one run)
Data: daily spot 2017-08-17..2026-11-06 (3369 bars); 4h from perp 1h 2018-08-14..2026-10-08 (71,458 1h bars, no gaps).
BTC only on disk; the "7y spot 1h" set was not found. Fee 10 bp round trip, 1x, fill next open, 60/30d gap/rest split.
Net R only where a stop exists (rules 1-2, stop = initial exit channel); rule 3 has no stop (nan). Placebo = same n, direction,
hold times, random entry, 200 draws. Pass bar from PREREG: VAL net > 0, t >= 2, placebo >= 95, DEV same sign.

## R1 daily Donchian 20/10
DEV 2017-08-17..2023-02-26 (2020 bars); VAL 2023-03-29..2026-11-05 (1318 bars)

| seg | side | n | win % | avg win % | avg loss % | net/trade % | net R | t | placebo pctile | B&H % |
|---|---|---|---|---|---|---|---|---|---|---|
| DEV | ALL | 50 | 48 | 35.30 | -10.14 | +11.67 | +1.20 | +1.49 | 100 | 453 |
| DEV | long | 24 | 50 | 56.95 | -9.93 | +23.51 | +2.48 | +1.49 | 96 | 453 |
| DEV | short | 26 | 46 | 13.64 | -10.32 | +0.74 | +0.02 | +0.26 | 90 | 453 |
| VAL | ALL | 38 | 39 | 13.59 | -7.44 | +0.87 | +0.12 | +0.39 | 69 | 179 |
| VAL | long | 19 | 42 | 18.38 | -5.86 | +4.35 | +0.50 | +1.15 | 64 | 179 |
| VAL | short | 19 | 37 | 8.13 | -8.88 | -2.62 | -0.26 | -1.24 | 40 | 179 |

## R2 4h Donchian 55/20
DEV 2018-08-14..2023-07-05 (10719 bars); VAL 2023-08-04..2026-10-08 (6966 bars)

| seg | side | n | win % | avg win % | avg loss % | net/trade % | net R | t | placebo pctile | B&H % |
|---|---|---|---|---|---|---|---|---|---|---|
| DEV | ALL | 123 | 40 | 12.85 | -5.35 | +1.90 | +0.39 | +1.62 | 96 | 405 |
| DEV | long | 65 | 42 | 15.16 | -4.82 | +3.48 | +0.57 | +1.91 | 88 | 405 |
| DEV | short | 58 | 38 | 10.03 | -5.90 | +0.14 | +0.19 | +0.10 | 86 | 405 |
| VAL | ALL | 85 | 35 | 8.64 | -3.24 | +0.95 | +0.12 | +0.97 | 88 | 182 |
| VAL | long | 46 | 39 | 10.41 | -3.45 | +1.98 | +0.24 | +1.20 | 77 | 182 |
| VAL | short | 39 | 31 | 5.97 | -3.02 | -0.25 | -0.02 | -0.28 | 79 | 182 |

## R3 TSMOM 28d weekly (daily)
DEV 2017-08-17..2023-02-26 (2020 bars); VAL 2023-03-29..2026-11-05 (1318 bars)

| seg | side | n | win % | avg win % | avg loss % | net/trade % | net R | t | placebo pctile | B&H % |
|---|---|---|---|---|---|---|---|---|---|---|
| DEV | ALL | 64 | 41 | 33.47 | -11.74 | +6.63 | +nan | +1.17 | 98 | 453 |
| DEV | long | 32 | 38 | 57.45 | -10.28 | +15.12 | +nan | +1.41 | 94 | 453 |
| DEV | short | 32 | 44 | 12.91 | -13.36 | -1.87 | +nan | -0.54 | 78 | 453 |
| VAL | ALL | 40 | 35 | 17.77 | -6.63 | +1.91 | +nan | +0.76 | 79 | 179 |
| VAL | long | 20 | 40 | 22.90 | -6.18 | +5.45 | +nan | +1.22 | 62 | 179 |
| VAL | short | 20 | 30 | 10.94 | -7.02 | -1.63 | +nan | -0.73 | 74 | 179 |
## Read (honest)
- No rule passes: VALIDATION t-stats are +0.39, +0.97, +0.76 (ALL), all under 2; placebo percentiles 69, 88, 79 (under 95).
- DEV looked better (R1 +11.7 % per trade, placebo 100) but it spans the 2017-2021 run-up (buy-and-hold +453 %); it did not carry into VALIDATION (+0.87 %).
- Long side carries all of it; shorts are about zero in DEV and negative in VAL for all three rules (n 19-39 per row, wide error).
- Placebo longs inherit BTC's drift, so a percentile of 62-96 on long-only rows is not separated from "being long BTC".
- Verdict: FAIL on the pre-registered bar (R2 4h is the nearest: positive in both segments, t 1.62 / 0.97, n 123 / 85); small n per row.
