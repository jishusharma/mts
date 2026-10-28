# ACCESS_LOG (S1): every file opened, with the min / max bar open time actually used

Cut: 2024-07-01 00:00 UTC (1719792000000) exclusive. No bar at or after the cut was used: `note()` aborts the run otherwise.
Event-table files are read with pandas `usecols` for timestamp, side, status, entry and stop columns only; mfe/mae/forward-return columns are not parsed.

| file | min bar/ts used | max bar/ts used | rows | note |
|---|---|---|---|---|
| krown_daily/BTCUSDT_1d.csv | 2017-08-17 00:00 | 2024-06-30 00:00 | 2510 | streamed, stopped at the first row >= cut |
| bigtrade/cache/perp/klines_1h.npz | 2022-01-01 00:00 | 2024-06-30 23:00 | 21888 | np.load reads whole arrays; mask applied before any value is used |
| bigtrade/cache/perp/klines_15m.npz | 2022-01-01 00:00 | 2024-06-30 23:45 | 87552 | np.load reads whole arrays; mask applied before any value is used |
| event table bb_top_reversal.csv [bb_top_reversal] | 2022-01-01 06:30 | 2024-06-29 19:30 | 1577 | timestamp + side + status + entry + stop columns only |
| event table malkan_rsi.csv [malkan_rsi] | 2022-01-03 05:00 | 2024-06-17 05:00 | 132 | timestamp + side + status + entry + stop columns only |
| event table rsi_reclaim.csv [rsi_reclaim] | 2022-01-02 02:00 | 2024-06-29 01:00 | 982 | timestamp + side + status + entry + stop columns only |
| event table cc_msb.csv [cc_msb] | 2022-01-03 04:00 | 2024-06-29 23:00 | 830 | timestamp + side + status + entry + stop columns only |
| event table fabio_escalation.csv [fabio_escalation] | 2022-01-20 22:00 | 2024-06-28 13:00 | 649 | timestamp + side + status + entry + stop columns only |
| event table session_momentum.csv [session_momentum] | 2022-01-02 00:30 | 2024-06-30 00:30 | 911 | timestamp + side + status + entry + stop columns only |
| event table rsi_divergence.csv [rsi_divergence_1h] | 2022-01-06 11:00 | 2024-06-29 17:00 | 502 | timestamp + side + status + entry + stop columns only |
| event table rsi_divergence.csv [rsi_divergence_4h] | 2022-01-07 20:00 | 2024-06-23 04:00 | 138 | timestamp + side + status + entry + stop columns only |
| event table candle_pattern_1h.csv [candle_pattern_1h] | 2022-01-01 03:00 | 2024-06-30 04:00 | 12195 | timestamp + side + status + entry + stop columns only |
| event table candle_pattern_4h.csv [candle_pattern_4h] | 2022-01-01 12:00 | 2024-06-27 16:00 | 3298 | timestamp + side + status + entry + stop columns only |
| event table volume_1h.csv [volume_1h] | 2022-02-26 01:00 | 2024-06-30 08:00 | 3388 | timestamp + side + status + entry + stop columns only |
| event table volume_4h.csv [volume_4h] | 2022-02-26 04:00 | 2024-06-29 04:00 | 643 | timestamp + side + status + entry + stop columns only |
| event table events.csv (repo) [wlow_bounce] | 2022-02-14 16:00 | 2023-09-25 20:00 | 8 | timestamp + side + status + entry + stop columns only |

Maximum bar/decision time used: 2024-06-30 23:45 (1719791100000) <= 1719792000000 (a decision time equal to the cut is the close of a bar that opened before it). PASS.

DEV_EXT 1m files (F:/MTS/data/dev_ext_2019_2021) are absent on this machine (JIS-NB): not opened.
