# DATA_COVERAGE: Krown daily/weekly series (2026-10-16)

Fetched by `tools/fetch_daily_majors.py`, summarised by `tools/build_data_coverage.py`. Files live in `F:/MTS/data/krown_daily/` (never in git);
this table and `DATA_MANIFEST.csv` (every source file: URL, published SHA256, computed SHA256, status) are what is committed.
Each Binance monthly zip was compared with its published `.CHECKSUM`: all matched (status OK in the manifest). Coverage reads timestamps only; the weekly
aggregation touches OHLC mechanically (no return or outcome is computed) and its cross-check compares only bars before 2024-07-01. Bars from 2024-07-01 on are
stored for the one-time VALIDATION and HOLDOUT reads and are not studied here.

| series | first bar | last bar | bars | gaps | SHA256 of merged file |
|---|---|---|---|---|---|
| Binance spot BTCUSDT 1d | 2017-08-17 | 2026-09-30 | 3332 | 0 | `4ffbd947b3d11ab81f60e9f45face8f0d7cba6502713676745e03d85337e6751` |
| Binance spot BTCUSDT (published 1w) 1w | 2017-08-14 | 2026-06-29 | 456 | 8 | `763a808be2319ae6dedefe72c01e1bec2ca00c5c11f12c111f44a594d2f86e4f` |
| Binance spot ETHUSDT 1d | 2017-08-17 | 2026-09-30 | 3332 | 0 | `5963c9cbc498dc10945b2b883fefd36af4f523d07b08b2c71217f2f58bac4504` |
| Binance spot BNBUSDT 1d | 2017-11-06 | 2026-09-30 | 3251 | 0 | `21639f94e5ca53abf0ab2f033bfae54983b4bef4b09d94c988776300c56ebf47` |
| Binance spot SOLUSDT 1d | 2020-08-11 | 2026-09-30 | 2242 | 0 | `6390fae4abefe7a9e4b29632663c434f9f8ebbdfbb66ebe7044cee9666af805d` |
| Coinbase BTC-USD 1d | 2015-07-20 | 2026-10-15 | 4106 | 0 | `036379a475389d801ba54c315f127daf59c0f1efcde123849e8562850a74ae9e` |

## Gaps

- Binance spot BTCUSDT (published 1w) `BTCUSDT_1w.csv`: missing bars between 2022-05-23 and 2022-06-06; 2022-06-20 and 2022-07-04; 2022-08-22 and 2022-09-05; 2022-09-19 and 2022-10-03; 2022-10-24 and 2022-11-07; 2022-11-21 and 2022-12-05; 2025-01-20 and 2025-02-03; 2025-02-17 and 2025-03-03

## Weekly bars built from the daily files (Monday 00:00 UTC start, full 7-day weeks only)

Binance's published BTCUSDT 1w file has the gaps listed above (the monthly archive omits those weeks) and stops at the last full week of June 2026 (the 2026-07 to 2026-09 monthly 1w files are not published). The weekly series to use is the one built from the daily bars:

| series | first week | last week | weeks | partial weeks dropped | SHA256 |
|---|---|---|---|---|---|
| BTCUSDT 1w_from_1d | 2017-08-21 | 2026-09-21 | 475 | 2 | `9cff70d2c7916274aed8ffd74283900dedf90c8e2320e9d2ac4d91244e30217b` |
| ETHUSDT 1w_from_1d | 2017-08-21 | 2026-09-21 | 475 | 2 | `d8a89f4f00209321a71982be981b3476e2efa0a7af2ca024f5c8772f3d459233` |
| BNBUSDT 1w_from_1d | 2017-11-06 | 2026-09-21 | 464 | 1 | `9d5b19f93729a9abdce6c4e0e11067f281f479465e869d3013e0c059cd54a2c5` |
| SOLUSDT 1w_from_1d | 2020-08-17 | 2026-09-21 | 319 | 2 | `8092e8497f9fd4526efbbca32421d06d846b8d7038f0097177a35ad0746e29e4` |

Cross-check, BTCUSDT weeks dated before 2024-07-01 present in both: 352; open/high/low/close identical in 352; volume differs beyond 1e-6 relative in 0.

Coinbase BTC-USD volume is in BTC on that venue only; Binance spot volume is in the base asset on Binance. The venue question (conflict C6) is answered by the study, not here.

