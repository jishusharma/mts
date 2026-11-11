# US open: the first 1-3 minutes, what follows, and the 30 minutes before

BTCUSDT 1m 2023-01-02..2026-11-10, 1006 weekday opens (1 skipped for data gaps). Open = 09:30 New York. Definitions in `study.py` (OURS), fixed before the run. Descriptive, no fees, no entries, never a signal.

Regime mix: not split by regime (one pooled window; the last 60 opens are shown as a separate row).

| question | count |
|---|---|
| size of the first 1 min (abs move) | p50 0.07%, p75 0.12%, p90 0.19%; up 463, down 541 |
| size of the first 3 min (abs move) | p50 0.11%, p75 0.20%, p90 0.32%; up 477, down 529 |
| volume, first 3 min over the 3 min before (median) | 2.10 times |
| minute 1 direction = first 3 min direction | 645 / 1004 (64.2%) |
| first 3 min direction = next 27 min | 498 / 1006 (49.5%) |
| first 3 min direction = next 57 min | 474 / 1006 (47.1%) |
| big first 3 min (abs >= 0.20%) = next 27 min | 125 / 251 (49.8%) |
| big first 3 min = next 57 min | 113 / 251 (45.0%) |
| last 60 opens: first 3 min = next 27 min | 29 / 60 (48.3%) |
| last 60 opens: first 3 min = next 57 min | 22 / 60 (36.7%) |
| pre-open 30 min drift = first 3 min | 470 / 1006 (46.7%) |
| pre-open 5 min drift = first 3 min | 486 / 1006 (48.3%) |
| pre-open 30 min drift = the 57 min after the first 3 | 508 / 1006 (50.5%) |
| heaviest taker buying before the open (share >= 0.548, n 202) | first 3 min up 89 / down 113; next 57 min up 100 / down 102 |
| heaviest taker selling before the open (share <= 0.435, n 202) | first 3 min up 109 / down 93; next 57 min up 90 / down 112 |

Read: the first 3 minutes give the size of the opening move (about double the volume of the minutes before), not its direction. Neither the pre-open drift nor the pre-open taker share separates up from down. Not measured: open interest and long/short ratios (Binance keeps about 30 days), other symbols, fees.
