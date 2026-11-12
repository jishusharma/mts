# DATA_B2: aggTrades fetch and reduce log summary (card btc-of-level-auction-b2-fetch-run-1112)

Source: data.binance.vision futures/um/monthly/aggTrades/BTCUSDT (USD-M, same market as the B1 1m klines). 29 monthly zips 2022-01 (warm-up for trailing windows only) .. 2024-05, each verified against its .CHECKSUM (sha256), 0 mismatches. Zips kept on D:/MTS_data/binance_aggtrades/um/BTCUSDT (15 GB), reduced 15m tables in D:/MTS_data/binance_aggtrades/reduced (2.8 MB). Nothing unpacked, nothing on C: or F:, nothing from D: committed. Resume command: python MyTradingSys/research/btc_of_level_auction_1112/fetch_b2.py

DECISION (OURS): 2022-01 is fetched as well as the 28 DEV months because the 30-day and 24h trailing windows of February events need it (PREREG: warm-up month, trailing windows may reach into earlier splits; no event is taken before 2022-02-01).
DECISION (OURS): bucket = floor(price / (0.0001 x bar open)); aggressor = is_buyer_maker false is a taker buy.

D: speeds: download is network-bound (about 18 MB/s, D: write keeps up); the reduce step is CPU-bound (single-thread pandas groupby), so its zip read speed (3-9 MB/s, 0.26-0.66 M trades/s) is not the limit of the disk. No separate disk benchmark was run.

| Month | zip GB | download s | download MB/s | trades | 15m bars | reduce wall s | zip read MB/s | M trades/s |
|---|---|---|---|---|---|---|---|---|
| 2022-01 | 0.78 | 42 | 18.7 | 58645303 | 2976 | 125 | 6.3 | 0.47 |
| 2022-02 | 0.70 | 38 | 18.5 | 52823155 | 2688 | 129 | 5.5 | 0.41 |
| 2022-03 | 0.63 | 34 | 18.5 | 47102107 | 2976 | 95 | 6.6 | 0.50 |
| 2022-04 | 0.48 | 26 | 18.1 | 35748548 | 2880 | 120 | 4.0 | 0.30 |
| 2022-05 | 0.80 | 44 | 18.3 | 60764860 | 2973 | 197 | 4.1 | 0.31 |
| 2022-06 | 0.98 | 53 | 18.4 | 74364398 | 2880 | 175 | 5.6 | 0.43 |
| 2022-07 | 0.83 | 45 | 18.6 | 62336640 | 2976 | 138 | 6.0 | 0.45 |
| 2022-08 | 0.54 | 30 | 18.3 | 40556504 | 2688 | 61 | 8.8 | 0.66 |
| 2022-09 | 0.55 | 30 | 18.6 | 44223166 | 2688 | 149 | 3.7 | 0.30 |
| 2022-10 | 0.38 | 22 | 17.6 | 27752738 | 2880 | 101 | 3.8 | 0.27 |
| 2022-11 | 0.47 | 26 | 18.1 | 33974166 | 2688 | 114 | 4.1 | 0.30 |
| 2022-12 | 0.24 | 14 | 17.1 | 16952163 | 2976 | 45 | 5.3 | 0.38 |
| 2023-01 | 0.39 | 22 | 18.0 | 28360744 | 2976 | 60 | 6.5 | 0.47 |
| 2023-02 | 0.43 | 24 | 18.3 | 32013508 | 2688 | 72 | 6.0 | 0.45 |
| 2023-03 | 0.77 | 41 | 18.6 | 57718929 | 2976 | 123 | 6.2 | 0.47 |
| 2023-04 | 0.51 | 28 | 18.2 | 38499736 | 2880 | 120 | 4.3 | 0.32 |
| 2023-05 | 0.48 | 26 | 18.4 | 36757013 | 2976 | 120 | 4.0 | 0.31 |
| 2023-06 | 0.51 | 28 | 18.3 | 39024962 | 2880 | 145 | 3.5 | 0.27 |
| 2023-07 | 0.33 | 18 | 17.9 | 24963535 | 2976 | 87 | 3.8 | 0.29 |
| 2023-08 | 0.32 | 18 | 17.6 | 24166578 | 2976 | 83 | 3.8 | 0.29 |
| 2023-09 | 0.30 | 17 | 17.7 | 22596398 | 2880 | 79 | 3.8 | 0.29 |
| 2023-10 | 0.49 | 27 | 18.4 | 38272235 | 2976 | 127 | 3.9 | 0.30 |
| 2023-11 | 0.41 | 22 | 18.2 | 31204314 | 2880 | 113 | 3.6 | 0.28 |
| 2023-12 | 0.43 | 24 | 18.1 | 32959424 | 2976 | 120 | 3.6 | 0.28 |
| 2024-01 | 0.52 | 29 | 18.1 | 40294620 | 2976 | 155 | 3.4 | 0.26 |
| 2024-02 | 0.47 | 26 | 18.3 | 36317913 | 2784 | 138 | 3.4 | 0.26 |
| 2024-03 | 0.85 | 46 | 18.5 | 66512993 | 2976 | 256 | 3.3 | 0.26 |
| 2024-04 | 0.67 | 36 | 18.6 | 52506247 | 2880 | 200 | 3.4 | 0.26 |
| 2024-05 | 0.50 | 27 | 18.7 | 38945717 | 2976 | 148 | 3.4 | 0.26 |
