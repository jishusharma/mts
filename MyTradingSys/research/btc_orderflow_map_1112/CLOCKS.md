# CLOCKS: BTC own clocks from 1m taker delta, DEV only (card btc-of-map-clocks-1112)

Code: clocks.py (tests: test_clocks.py, 4 pass, fail before clocks.py existed). Raw numbers: results_clocks.json. Placebo: 300 draws, seed 1112, random per-day hour offset and weekday permutation.
Data: Binance USD-M BTCUSDT 1m monthly archive (data.binance.vision, public), DEV 2022-02-01..2024-05-31 per PREREG.md: 1,225,440 of 1,225,440 bars, 0 missing. The F: drive is not on this machine, so the files were fetched; June 2024 onward never opened.
Definitions are in the clocks.py docstring. Forward net bp = sign(bar delta) x return from the next 1m open to the close h minutes later, minus 10 bp round trip (SOURCED fee). z = placebo z. |z| < 2 on every column is marked noise.
Regime mix: NOT_IN_DATA (not computed in this card; the PREREG.md per-regime split is card 3's job).

## Reading (descriptive, no edge claim)
- Volume-weighted delta share stays within +-0.8 % in every hour, weekday and funding window; the largest hour z is +-2.2, about what 24 buckets give by chance. No clock concentrates 1m taker delta.
- Activity concentrates, delta does not: mean abs 1m return peaks 13Z-16Z (6.25 bp at 14Z, z +22; US open and the 16Z funding window 5.91 bp, z +17), is lowest 04Z-05Z (3.4 bp) and on Sat/Sun (3.2 / 3.4 bp vs about 5.1 on weekdays).
- Following the 1m delta sign fee-net loses about the fee everywhere: forward 60m net is -9.3 to -10.8 bp in every hour (gross about 0), so no clock turns the raw delta sign into a fee-net trade. The only clustered hints (16Z fwd 15m -10.55 z -3.1; 01Z fwd 60m -9.33 z +3.0; Mon fwd 15m z +3.3) are 0.2 to 0.7 bp from the fee, below any threshold of PREREG.md and from overlapping 1m entries; read as noise-level.
- Funding windows: 00Z is noise on every column; 08Z is quiet (3.93 bp), 16Z is active (5.91 bp) but that is the US-session hour, not funding.

## DEV table (hours, funding windows, weekdays)

### Clock: hour

| bucket | n bars | delta share | z | mean abs ret bp | z | fwd 15m net bp | z | fwd 60m net bp | z | mark |
|---|---|---|---|---|---|---|---|---|---|---|
| 00Z | 51060 | +0.0030 | +1.2 | 4.86 | +3.4 | -9.87 | +2.5 | -10.25 | -0.3 |  |
| 01Z | 51060 | -0.0012 | -0.1 | 4.46 | -1.9 | -9.95 | +1.9 | -9.33 | +3.0 |  |
| 02Z | 51060 | -0.0077 | -1.9 | 4.10 | -7.1 | -9.89 | +2.0 | -9.83 | +1.3 |  |
| 03Z | 51060 | +0.0023 | +0.9 | 3.68 | -10.7 | -10.22 | -0.2 | -10.31 | -0.6 |  |
| 04Z | 51060 | -0.0021 | -0.4 | 3.44 | -15.2 | -10.20 | -0.1 | -10.39 | -0.8 |  |
| 05Z | 51060 | -0.0048 | -1.0 | 3.47 | -14.9 | -10.17 | +0.2 | -10.03 | +0.7 |  |
| 06Z | 51060 | +0.0005 | +0.4 | 3.63 | -13.2 | -10.04 | +1.0 | -9.97 | +0.9 |  |
| 07Z | 51060 | -0.0039 | -0.8 | 3.80 | -10.7 | -10.26 | -0.6 | -10.44 | -1.0 |  |
| 08Z | 51060 | +0.0052 | +1.9 | 4.04 | -7.1 | -10.16 | +0.2 | -10.53 | -1.4 |  |
| 09Z | 51060 | +0.0006 | +0.5 | 3.84 | -9.4 | -10.36 | -1.2 | -10.33 | -0.5 |  |
| 10Z | 51060 | +0.0038 | +1.3 | 3.83 | -9.0 | -10.40 | -1.6 | -10.61 | -1.7 |  |
| 11Z | 51060 | -0.0023 | -0.3 | 3.96 | -8.6 | -10.35 | -1.2 | -10.39 | -0.8 |  |
| 12Z | 51060 | -0.0012 | -0.0 | 4.90 | +4.0 | -10.58 | -2.8 | -10.33 | -0.5 |  |
| 13Z | 51060 | -0.0052 | -1.1 | 5.64 | +13.7 | -10.41 | -1.7 | -10.46 | -1.1 |  |
| 14Z | 51060 | +0.0022 | +1.0 | 6.25 | +22.1 | -10.16 | +0.4 | -9.95 | +0.9 |  |
| 15Z | 51060 | -0.0003 | +0.3 | 6.00 | +17.4 | -10.02 | +1.3 | -9.70 | +1.8 |  |
| 16Z | 51060 | -0.0054 | -1.2 | 5.74 | +14.8 | -10.63 | -3.1 | -10.82 | -2.4 |  |
| 17Z | 51060 | -0.0032 | -0.6 | 5.32 | +9.7 | -10.26 | -0.5 | -10.34 | -0.6 |  |
| 18Z | 51060 | +0.0051 | +1.7 | 5.27 | +8.9 | -10.28 | -0.7 | -10.56 | -1.3 |  |
| 19Z | 51060 | -0.0079 | -2.1 | 5.24 | +8.0 | -10.07 | +0.8 | -9.96 | +0.9 |  |
| 20Z | 51060 | +0.0067 | +2.2 | 5.00 | +5.3 | -10.08 | +0.9 | -9.81 | +1.3 |  |
| 21Z | 51060 | -0.0075 | -1.9 | 4.85 | +3.1 | -10.37 | -1.3 | -10.11 | +0.4 |  |
| 22Z | 51060 | +0.0037 | +1.3 | 4.73 | +1.7 | -9.82 | +2.7 | -10.05 | +0.5 |  |
| 23Z | 51060 | -0.0056 | -1.3 | 4.39 | -2.7 | -10.02 | +1.2 | -10.01 | +0.6 |  |

### Clock: funding

| bucket | n bars | delta share | z | mean abs ret bp | z | fwd 15m net bp | z | fwd 60m net bp | z | mark |
|---|---|---|---|---|---|---|---|---|---|---|
| 00Z | 51060 | +0.0008 | +0.6 | 4.59 | -0.2 | -10.13 | +0.5 | -10.32 | -0.6 | noise |
| 08Z | 51060 | -0.0025 | -0.4 | 3.93 | -8.6 | -10.17 | +0.1 | -10.48 | -1.1 |  |
| 16Z | 51060 | -0.0044 | -1.0 | 5.91 | +17.1 | -10.55 | -2.6 | -10.46 | -1.0 |  |
| other | 1072260 | -0.0008 | +0.9 | 4.57 | -5.7 | -10.18 | +1.3 | -10.15 | +1.7 |  |

### Clock: weekday

| bucket | n bars | delta share | z | mean abs ret bp | z | fwd 15m net bp | z | fwd 60m net bp | z | mark |
|---|---|---|---|---|---|---|---|---|---|---|
| Mon | 174240 | +0.0008 | +0.7 | 4.95 | +1.8 | -9.95 | +3.3 | -9.99 | +1.3 |  |
| Tue | 175680 | +0.0001 | +0.4 | 5.17 | +2.6 | -10.28 | -1.2 | -10.28 | -0.7 |  |
| Wed | 175680 | -0.0004 | +0.2 | 5.36 | +3.9 | -10.21 | -0.2 | -10.01 | +1.3 |  |
| Thu | 175680 | -0.0039 | -1.2 | 5.10 | +2.4 | -10.21 | -0.4 | -10.37 | -1.2 |  |
| Fri | 175680 | -0.0026 | -0.5 | 4.97 | +1.9 | -10.26 | -1.2 | -10.15 | +0.3 | noise |
| Sat | 174240 | -0.0027 | -0.7 | 3.23 | -7.0 | -10.32 | -1.9 | -10.34 | -1.1 |  |
| Sun | 174240 | +0.0019 | +1.3 | 3.42 | -6.0 | -10.09 | +1.4 | -10.19 | +0.1 |  |


## VALIDATION table

Not run. PREREG.md allows VALIDATION only for cells that clear DEV, and no clock cell here clears a DEV fee-net threshold (nothing to validate); the VALIDATION and HOLDOUT splits stay unopened (clocks.py refuses --split validation).
