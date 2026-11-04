FOUND=68 DIFF=0 NOT_IN_DATA=1

# Blind Re-read Audit: `us_open_oos_2026-10-30/REPORT.md` vs `results_oos_2020_2021.json`

- **Card**: `gemini-blind-read-us-open-oos-1104`
- **Audited Document**: `MyTradingSys/research/us_open_oos_2026-10-30/REPORT.md`
- **Primary Data Source**: `MyTradingSys/research/us_open_oos_2026-10-30/results_oos_2020_2021.json`
- **Original Baseline Source**: `MyTradingSys/research/session_sweeps/results_2026-10-04.json` (used for 2022-26 comparison columns in `REPORT.md`)
- **Date**: 2026-11-04
- **Summary**: `FOUND=68 DIFF=0 NOT_IN_DATA=1` (1,052,640 raw 1m bar count is `NOT_IN_DATA` because `F:/MTS/Dumps/backtest/raw_1m_2019/klines` is absent on this host and `results_oos_2020_2021.json` does not store raw bar count; all 68 other numbers in `REPORT.md` match `results_oos_2020_2021.json` and `results_2026-10-04.json`).

| # | Source Line (`REPORT.md`) | Quoted Number / Claim | Quote Context (`REPORT.md`) | Matched Source (`file:line` & value) | Status |
|---|---|---|---|---|---|
| 1 | `REPORT.md:3` | `24` (monthly files) | `"F:/MTS/Dumps/backtest/raw_1m_2019/klines (24 monthly files, 1,052,640 bars, no gaps)."` | `run_oos.py:16` (`dt.date(2020, 1, 2), dt.date(2021, 12, 31)` = 24 months `2020-01..2021-12`) | FOUND |
| 2 | `REPORT.md:3` | `1,052,640` (bars) | `"F:/MTS/Dumps/backtest/raw_1m_2019/klines (24 monthly files, 1,052,640 bars, no gaps)."` | Not stored in `results_oos_2020_2021.json`; `F:/MTS/Dumps/backtest/raw_1m_2019/klines` absent on host (note: 731 days in 2020-2021 $\times 1440 = 1,052,640$) | NOT_IN_DATA |
| 3 | `REPORT.md:3` | `0` (`no gaps` / dropped) | `"(24 monthly files, 1,052,640 bars, no gaps)."` | `results_oos_2020_2021.json:3` (`"dropped": 0`) | FOUND |
| 4 | `REPORT.md:3` | `505` (valid days) | `"505 valid days (original: 1,178 days, 2022-01..2026-09)."` | `results_oos_2020_2021.json:2` (`"days": 505`) | FOUND |
| 5 | `REPORT.md:3` | `1,178` (original days) | `"505 valid days (original: 1,178 days, 2022-01..2026-09)."` | `session_sweeps/results_2026-10-04.json:2` (`"days": 1178`) | FOUND |
| 6 | `REPORT.md:11` | `10` ($k=10$ min) | `"| 10 | 0.498 [0.470,0.527] | 0.485 [0.442,0.529] |"` | `results_oos_2020_2021.json:71` (`"O_k10"`) | FOUND |
| 7 | `REPORT.md:11` | `0.498` (orig $k=10$ P) | `"| 10 | 0.498 [0.470,0.527] | 0.485 [0.442,0.529] |"` | `session_sweeps/results_2026-10-04.json:73` (`"p": 0.4983`) | FOUND |
| 8 | `REPORT.md:11` | `0.470` (orig $k=10$ CI lo) | `"| 10 | 0.498 [0.470,0.527] | 0.485 [0.442,0.529] |"` | `session_sweeps/results_2026-10-04.json:75` (`0.4698`) | FOUND |
| 9 | `REPORT.md:11` | `0.527` (orig $k=10$ CI hi) | `"| 10 | 0.498 [0.470,0.527] | 0.485 [0.442,0.529] |"` | `session_sweeps/results_2026-10-04.json:76` (`0.5268`) | FOUND |
| 10 | `REPORT.md:11` | `0.485` (OOS $k=10$ P) | `"| 10 | 0.498 [0.470,0.527] | 0.485 [0.442,0.529] |"` | `results_oos_2020_2021.json:73` (`"p": 0.4851`) | FOUND |
| 11 | `REPORT.md:11` | `0.442` (OOS $k=10$ CI lo) | `"| 10 | 0.498 [0.470,0.527] | 0.485 [0.442,0.529] |"` | `results_oos_2020_2021.json:75` (`0.4418`) | FOUND |
| 12 | `REPORT.md:11` | `0.529` (OOS $k=10$ CI hi) | `"| 10 | 0.498 [0.470,0.527] | 0.485 [0.442,0.529] |"` | `results_oos_2020_2021.json:76` (`0.5287`) | FOUND |
| 13 | `REPORT.md:12` | `15` ($k=15$ min) | `"| 15 | 0.494 [0.466,0.523] | 0.485 [0.442,0.529] |"` | `results_oos_2020_2021.json:79` (`"O_k15"`) | FOUND |
| 14 | `REPORT.md:12` | `0.494` (orig $k=15$ P) | `"| 15 | 0.494 [0.466,0.523] | 0.485 [0.442,0.529] |"` | `session_sweeps/results_2026-10-04.json:81` (`"p": 0.4941`) | FOUND |
| 15 | `REPORT.md:12` | `0.466` (orig $k=15$ CI lo) | `"| 15 | 0.494 [0.466,0.523] | 0.485 [0.442,0.529] |"` | `session_sweeps/results_2026-10-04.json:83` (`0.4656`) | FOUND |
| 16 | `REPORT.md:12` | `0.523` (orig $k=15$ CI hi) | `"| 15 | 0.494 [0.466,0.523] | 0.485 [0.442,0.529] |"` | `session_sweeps/results_2026-10-04.json:84` (`0.5226`) | FOUND |
| 17 | `REPORT.md:12` | `0.485` (OOS $k=15$ P) | `"| 15 | 0.494 [0.466,0.523] | 0.485 [0.442,0.529] |"` | `results_oos_2020_2021.json:81` (`"p": 0.4851`) | FOUND |
| 18 | `REPORT.md:12` | `0.442` (OOS $k=15$ CI lo) | `"| 15 | 0.494 [0.466,0.523] | 0.485 [0.442,0.529] |"` | `results_oos_2020_2021.json:83` (`0.4418`) | FOUND |
| 19 | `REPORT.md:12` | `0.529` (OOS $k=15$ CI hi) | `"| 15 | 0.494 [0.466,0.523] | 0.485 [0.442,0.529] |"` | `results_oos_2020_2021.json:84` (`0.5287`) | FOUND |
| 20 | `REPORT.md:13` | `30` ($k=30$ min) | `"| 30 | 0.501 [0.472,0.529] | 0.475 [0.432,0.519] |"` | `results_oos_2020_2021.json:87` (`"O_k30"`) | FOUND |
| 21 | `REPORT.md:13` | `0.501` (orig $k=30$ P) | `"| 30 | 0.501 [0.472,0.529] | 0.475 [0.432,0.519] |"` | `session_sweeps/results_2026-10-04.json:89` (`"p": 0.5008`) | FOUND |
| 22 | `REPORT.md:13` | `0.472` (orig $k=30$ CI lo) | `"| 30 | 0.501 [0.472,0.529] | 0.475 [0.432,0.519] |"` | `session_sweeps/results_2026-10-04.json:91` (`0.4723`) | FOUND |
| 23 | `REPORT.md:13` | `0.529` (orig $k=30$ CI hi) | `"| 30 | 0.501 [0.472,0.529] | 0.475 [0.432,0.519] |"` | `session_sweeps/results_2026-10-04.json:92` (`0.5294`) | FOUND |
| 24 | `REPORT.md:13` | `0.475` (OOS $k=30$ P) | `"| 30 | 0.501 [0.472,0.529] | 0.475 [0.432,0.519] |"` | `results_oos_2020_2021.json:89` (`"p": 0.4752`) | FOUND |
| 25 | `REPORT.md:13` | `0.432` (OOS $k=30$ CI lo) | `"| 30 | 0.501 [0.472,0.529] | 0.475 [0.432,0.519] |"` | `results_oos_2020_2021.json:91` (`0.432`) | FOUND |
| 26 | `REPORT.md:13` | `0.519` (OOS $k=30$ CI hi) | `"| 30 | 0.501 [0.472,0.529] | 0.475 [0.432,0.519] |"` | `results_oos_2020_2021.json:92` (`0.5188`) | FOUND |
| 27 | `REPORT.md:15` | `24` (fixed-UTC-hour anchors) | `"placebo spread of the 24 fixed-UTC-hour anchors (0.440..0.555, median 0.501)"` | `results_oos_2020_2021.json:111-304` (24 keys `"00:00"`..`"23:00"` in `"placebo_utc_k15"`) | FOUND |
| 28 | `REPORT.md:15` | `0.440` (placebo min) | `"placebo spread of the 24 fixed-UTC-hour anchors (0.440..0.555, median 0.501)"` | `results_oos_2020_2021.json:250,306` (`"17:00": {"p": 0.4396}`, `"placebo_p_range": [0.4396, ...]`) | FOUND |
| 29 | `REPORT.md:15` | `0.555` (placebo max) | `"placebo spread of the 24 fixed-UTC-hour anchors (0.440..0.555, median 0.501)"` | `results_oos_2020_2021.json:138,308` (`"03:00": {"p": 0.5545}`, `"placebo_p_range": [..., 0.5545]`) | FOUND |
| 30 | `REPORT.md:15` | `0.501` (placebo median) | `"placebo spread of the 24 fixed-UTC-hour anchors (0.440..0.555, median 0.501)"` | `results_oos_2020_2021.json:307` (`"placebo_p_range": [0.4396, 0.501, 0.5545]`) | FOUND |
| 31 | `REPORT.md:15` | `0.502` (2020 $O\_k15$ P) | `"By year: 2020 0.502, 2021 0.468 (both include 0.5)."` | `results_oos_2020_2021.json:314` (`"2020": {"n": 253, "p": 0.502, "ci": [0.4408, 0.5631]}`) | FOUND |
| 32 | `REPORT.md:15` | `0.468` (2021 $O\_k15$ P) | `"By year: 2020 0.502, 2021 0.468 (both include 0.5)."` | `results_oos_2020_2021.json:322` (`"2021": {"n": 252, "p": 0.4683, "ci": [0.4076, 0.5299]}`) | FOUND |
| 33 | `REPORT.md:22` | `13:30 1.92x [2.55]` (orig US DST #1) | `"| US DST | 13:30 1.92x [2.55], 14:00 1.77x, 13:45 1.72x |"` | `session_sweeps/results_2026-10-04.json:7-9` (`"bucket_utc": "13:30", "vol_x": 2.55, "absret_x": 1.92`) | FOUND |
| 34 | `REPORT.md:22` | `14:00 1.77x` (orig US DST #2) | `"| US DST | 13:30 1.92x [2.55], 14:00 1.77x, 13:45 1.72x |"` | `session_sweeps/results_2026-10-04.json:12-14` (`"bucket_utc": "14:00", "vol_x": 2.48, "absret_x": 1.77`) | FOUND |
| 35 | `REPORT.md:22` | `13:45 1.72x` (orig US DST #3) | `"| US DST | 13:30 1.92x [2.55], 14:00 1.77x, 13:45 1.72x |"` | `session_sweeps/results_2026-10-04.json:17-19` (`"bucket_utc": "13:45", "vol_x": 2.38, "absret_x": 1.72`) | FOUND |
| 36 | `REPORT.md:22` | `00:00 1.55x [1.52]` (OOS US DST #1) | `"| 00:00 1.55x [1.52], **13:30 1.36x [1.63]**, 12:00 1.35x |"` | `results_oos_2020_2021.json:7-9` (`"bucket_utc": "00:00", "vol_x": 1.52, "absret_x": 1.55`) | FOUND |
| 37 | `REPORT.md:22` | `13:30 1.36x [1.63]` (OOS US DST #2) | `"| 00:00 1.55x [1.52], **13:30 1.36x [1.63]**, 12:00 1.35x |"` | `results_oos_2020_2021.json:12-14` (`"bucket_utc": "13:30", "vol_x": 1.63, "absret_x": 1.36`) | FOUND |
| 38 | `REPORT.md:22` | `12:00 1.35x` (OOS US DST #3) | `"| 00:00 1.55x [1.52], **13:30 1.36x [1.63]**, 12:00 1.35x |"` | `results_oos_2020_2021.json:17-19` (`"bucket_utc": "12:00", "vol_x": 1.52, "absret_x": 1.35`) | FOUND |
| 39 | `REPORT.md:23` | `14:30 2.03x [2.81]` (orig US std #1) | `"| US std | 14:30 2.03x [2.81], 14:45 1.81x, 15:15 1.76x |"` | `session_sweeps/results_2026-10-04.json:39-41` (`"bucket_utc": "14:30", "vol_x": 2.81, "absret_x": 2.03`) | FOUND |
| 40 | `REPORT.md:23` | `14:45 1.81x` (orig US std #2) | `"| US std | 14:30 2.03x [2.81], 14:45 1.81x, 15:15 1.76x |"` | `session_sweeps/results_2026-10-04.json:44-46` (`"bucket_utc": "14:45", "vol_x": 2.66, "absret_x": 1.81`) | FOUND |
| 41 | `REPORT.md:23` | `15:15 1.76x` (orig US std #3) | `"| US std | 14:30 2.03x [2.81], 14:45 1.81x, 15:15 1.76x |"` | `session_sweeps/results_2026-10-04.json:49-51` (`"bucket_utc": "15:15", "vol_x": 2.23, "absret_x": 1.76`) | FOUND |
| 42 | `REPORT.md:23` | `00:00 1.51x [1.44]` (OOS US std #1) | `"| 00:00 1.51x [1.44], **14:30 1.39x [1.49]**, 16:00 1.35x [1.89] |"` | `results_oos_2020_2021.json:39-41` (`"bucket_utc": "00:00", "vol_x": 1.44, "absret_x": 1.51`) | FOUND |
| 43 | `REPORT.md:23` | `14:30 1.39x [1.49]` (OOS US std #2) | `"| 00:00 1.51x [1.44], **14:30 1.39x [1.49]**, 16:00 1.35x [1.89] |"` | `results_oos_2020_2021.json:44-46` (`"bucket_utc": "14:30", "vol_x": 1.49, "absret_x": 1.39`) | FOUND |
| 44 | `REPORT.md:23` | `16:00 1.35x [1.89]` (OOS US std #3) | `"| 00:00 1.51x [1.44], **14:30 1.39x [1.49]**, 16:00 1.35x [1.89] |"` | `results_oos_2020_2021.json:49-51` (`"bucket_utc": "16:00", "vol_x": 1.89, "absret_x": 1.35`) | FOUND |
| 45 | `REPORT.md:25` | `top-2` (`13:30 -> 14:30` rank) | `"the US-open bucket is the top-2 |ret| bucket in both regimes and shifts 13:30 -> 14:30 with US DST"` | `results_oos_2020_2021.json:11-15,43-47` (`13:30` is index 1 in `us_dst`; `14:30` is index 1 in `us_std`) | FOUND |
| 46 | `REPORT.md:26` | `1.36-1.39x` vs `1.92-2.03x` (\|ret\| multiple) | `"Does not replicate: magnitude (1.36-1.39x vs 1.92-2.03x; volume 1.5-1.6x vs 2.5-2.8x)"` | `results_oos_2020_2021.json:14,46` (`1.36`, `1.39`) vs `session_sweeps/results_2026-10-04.json:9,41` (`1.92`, `2.03`) | FOUND |
| 47 | `REPORT.md:26` | `1.5-1.6x` vs `2.5-2.8x` (vol multiple) | `"volume 1.5-1.6x vs 2.5-2.8x"` | `results_oos_2020_2021.json:13,45` (`1.63`, `1.49`) vs `session_sweeps/results_2026-10-04.json:8,40` (`2.55`, `2.81`) | FOUND |
| 48 | `REPORT.md:26` | `00:00 UTC is the top |ret| bucket in 2020-21 (it is not in the top 6 in the original)` | `"and rank: 00:00 UTC is the top |ret| bucket in 2020-21 (it is not in the top 6 in the original)."` | `results_oos_2020_2021.json:7-9,39-41` (`00:00` is #1 in both `us_dst` `1.55` and `us_std` `1.51`); `session_sweeps/results_2026-10-04.json:5-68` (`00:00` absent from both 6-row arrays) | FOUND |
| 49 | `REPORT.md:26` | `16:00 UTC (1.89x)` (highest std-time vol bucket) | `"In std-time days the highest volume bucket is 16:00 UTC (1.89x), not the open."` | `results_oos_2020_2021.json:49-51` (`"bucket_utc": "16:00", "vol_x": 1.89`) | FOUND |
| 50 | `REPORT.md:30` | `0.549` (T3 base P) | `"T3 base P(US up)=0.549 [0.505,0.591]"` | `results_oos_2020_2021.json:334` (`"p": 0.5485`) | FOUND |
| 51 | `REPORT.md:30` | `0.505` (T3 base CI lo) | `"T3 base P(US up)=0.549 [0.505,0.591]"` | `results_oos_2020_2021.json:336` (`0.5049`) | FOUND |
| 52 | `REPORT.md:30` | `0.591` (T3 base CI hi) | `"T3 base P(US up)=0.549 [0.505,0.591]"` | `results_oos_2020_2021.json:337` (`0.5914`) | FOUND |
| 53 | `REPORT.md:30` | `0.493` (T3 `H_sweep_back` P) | `"(H_sweep_back 0.493 n=75, none 0.600 n=75)."` | `results_oos_2020_2021.json:342` (`"p": 0.4933`) | FOUND |
| 54 | `REPORT.md:30` | `75` (T3 `H_sweep_back` n) | `"(H_sweep_back 0.493 n=75, none 0.600 n=75)."` | `results_oos_2020_2021.json:341` (`"n": 75`) | FOUND |
| 55 | `REPORT.md:30` | `0.600` (T3 `none` P) | `"(H_sweep_back 0.493 n=75, none 0.600 n=75)."` | `results_oos_2020_2021.json:382` (`"p": 0.6`) | FOUND |
| 56 | `REPORT.md:30` | `75` (T3 `none` n) | `"(H_sweep_back 0.493 n=75, none 0.600 n=75)."` | `results_oos_2020_2021.json:381` (`"n": 75`) | FOUND |
| 57 | `REPORT.md:30` | `n<=34` (T4 non-none classes) | `"T4 classes n<=34 so uninformative (H_sweep_back 0.647 n=34, CI [0.48,0.79])."` | `results_oos_2020_2021.json:693,701,709,717,725` (`n` = 34, 24, 30, 16, 0) | FOUND |
| 58 | `REPORT.md:30` | `0.647` (T4 `H_sweep_back` P) | `"(H_sweep_back 0.647 n=34, CI [0.48,0.79])."` | `results_oos_2020_2021.json:694` (`"p": 0.6471`) | FOUND |
| 59 | `REPORT.md:30` | `34` (T4 `H_sweep_back` n) | `"(H_sweep_back 0.647 n=34, CI [0.48,0.79])."` | `results_oos_2020_2021.json:693` (`"n": 34`) | FOUND |
| 60 | `REPORT.md:30` | `0.48` (T4 `H_sweep_back` CI lo) | `"(H_sweep_back 0.647 n=34, CI [0.48,0.79])."` | `results_oos_2020_2021.json:696` (`0.4791`) | FOUND |
| 61 | `REPORT.md:30` | `0.79` (T4 `H_sweep_back` CI hi) | `"(H_sweep_back 0.647 n=34, CI [0.48,0.79])."` | `results_oos_2020_2021.json:697` (`0.7851`) | FOUND |
| 62 | `REPORT.md:30` | `0.205` (T5 small IB trend P) | `"T5 small IB trend 0.205, mid 0.265, large 0.253 (no monotone link)."` | `results_oos_2020_2021.json:987` (`"p": 0.205`) | FOUND |
| 63 | `REPORT.md:30` | `0.265` (T5 mid IB trend P) | `"T5 small IB trend 0.205, mid 0.265, large 0.253 (no monotone link)."` | `results_oos_2020_2021.json:1013` (`"p": 0.2654`) | FOUND |
| 64 | `REPORT.md:30` | `0.253` (T5 large IB trend P) | `"T5 small IB trend 0.205, mid 0.265, large 0.253 (no monotone link)."` | `results_oos_2020_2021.json:1039` (`"p": 0.2531`) | FOUND |
| 65 | `REPORT.md:22` | `1.52` (OOS US DST `12:00` vol_x check) | `"| 00:00 1.55x [1.52], **13:30 1.36x [1.63]**, 12:00 1.35x |"` | `results_oos_2020_2021.json:18` (`"vol_x": 1.52`) | FOUND |
| 66 | `REPORT.md:15` | `253` (2020 valid days in `by_year_O_k15`) | `"By year: 2020 0.502, 2021 0.468 (both include 0.5)."` | `results_oos_2020_2021.json:313-317` (`n=253`, CI `[0.4408, 0.5631]` includes `0.5`) | FOUND |
| 67 | `REPORT.md:15` | `252` (2021 valid days in `by_year_O_k15`) | `"By year: 2020 0.502, 2021 0.468 (both include 0.5)."` | `results_oos_2020_2021.json:321-325` (`n=252`, CI `[0.4076, 0.5299]` includes `0.5`) | FOUND |
| 68 | `REPORT.md:22` | `13:30` OOS US DST rank #2 | `"**13:30 1.36x [1.63]**"` | `results_oos_2020_2021.json:11-15` (second element of `T1.us_dst`) | FOUND |
| 69 | `REPORT.md:23` | `14:30` OOS US std rank #2 | `"**14:30 1.39x [1.49]**"` | `results_oos_2020_2021.json:43-47` (second element of `T1.us_std`) | FOUND |
