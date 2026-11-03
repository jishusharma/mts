FOUND=23 NOT_IN_DATA=18 DIFF=0

| # | Line / Section | Quoted Number | Context in RESULT.md | Value in output.txt (file:line) | Status | Notes |
|---|---|---|---|---|---|---|
| 1 | L6 | 78 thousand | 10-23 CBP row target (SOURCED: `RESULT.md:6`) | - | NOT_IN_DATA | External CBP analyst quote |
| 2 | L6 | 75 thousand | 10-23 CBP row support zone (SOURCED: `RESULT.md:6`) | - | NOT_IN_DATA | External CBP analyst quote |
| 3 | L7 | $75,000 | 10-26 CBP row Sept 15 bottom (SOURCED: `RESULT.md:7`) | - | NOT_IN_DATA | External CBP analyst quote |
| 4 | L8 | 76,444 | Perp low on 10-30 (SOURCED: `RESULT.md:8`) | - | NOT_IN_DATA | Live/recent bar measurement not in `output.txt` |
| 5 | L8 | 76,500 | Spot low on 10-30 (SOURCED: `RESULT.md:8`) | - | NOT_IN_DATA | Live/recent bar measurement not in `output.txt` |
| 6 | L16 (Table: After >= 3 falling 4h highs) | 22 | n (SOURCED: `RESULT.md:16`) | `22` (`output.txt:5` `lower-highs n`) | FOUND | Exact match |
| 7 | L16 (Table: After >= 3 falling 4h highs) | 8.4% | Median H (SOURCED: `RESULT.md:16`) | `8.423` (`output.txt:5` `H_pct_med`) | FOUND | Rounded to 1 decimal place (8.423 -> 8.4%) |
| 8 | L16 (Table: After >= 3 falling 4h highs) | 73% | Drop reached 0.5 H (SOURCED: `RESULT.md:16`) | `0.727` (`output.txt:5` `reach_half_H`) | FOUND | Rounded to nearest percent (0.727 -> 73%) |
| 9 | L16 (Table: After >= 3 falling 4h highs) | 36% | Drop reached 1 H (SOURCED: `RESULT.md:16`) | `0.364` (`output.txt:5` `reach_1H`) | FOUND | Rounded to nearest percent (0.364 -> 36%) |
| 10 | L16 (Table: After >= 3 falling 4h highs) | 18% | Drop reached 1.618 H (SOURCED: `RESULT.md:16`) | `0.182` (`output.txt:5` `reach_1618H`) | FOUND | Rounded to nearest percent (0.182 -> 18%) |
| 11 | L16 (Table: After >= 3 falling 4h highs) | 50% | Back above S within 24 h (SOURCED: `RESULT.md:16`) | `0.500` (`output.txt:5` `failed_24h`) | FOUND | Exact match (0.500 -> 50%) |
| 12 | L16 (Table: After >= 3 falling 4h highs) | 0.83 H | Median max drop (SOURCED: `RESULT.md:16`) | `0.833` (`output.txt:5` `med_drop_H`) | FOUND | Rounded to 2 decimal places (0.833 -> 0.83 H) |
| 13 | L17 (Table: Any other 10-day-low break) | 44 | n (SOURCED: `RESULT.md:17`) | `44` (`output.txt:4` `control n`) | FOUND | Exact match |
| 14 | L17 (Table: Any other 10-day-low break) | 8.9% | Median H (SOURCED: `RESULT.md:17`) | `8.894` (`output.txt:4` `H_pct_med`) | FOUND | Rounded to 1 decimal place (8.894 -> 8.9%) |
| 15 | L17 (Table: Any other 10-day-low break) | 48% | Drop reached 0.5 H (SOURCED: `RESULT.md:17`) | `0.477` (`output.txt:4` `reach_half_H`) | FOUND | Rounded to nearest percent (0.477 -> 48%) |
| 16 | L17 (Table: Any other 10-day-low break) | 18% | Drop reached 1 H (SOURCED: `RESULT.md:17`) | `0.182` (`output.txt:4` `reach_1H`) | FOUND | Rounded to nearest percent (0.182 -> 18%) |
| 17 | L17 (Table: Any other 10-day-low break) | 9% | Drop reached 1.618 H (SOURCED: `RESULT.md:17`) | `0.091` (`output.txt:4` `reach_1618H`) | FOUND | Rounded to nearest percent (0.091 -> 9%) |
| 18 | L17 (Table: Any other 10-day-low break) | 70% | Back above S within 24 h (SOURCED: `RESULT.md:17`) | `0.705` (`output.txt:4` `failed_24h`) | FOUND | Rounded to integer percent (31/44 = 0.704545 -> 70%) |
| 19 | L17 (Table: Any other 10-day-low break) | 0.47 H | Median max drop (SOURCED: `RESULT.md:17`) | `0.470` (`output.txt:4` `med_drop_H`) | FOUND | Exact match (0.470 -> 0.47 H) |
| 20 | L21 | 73% | Lower-highs reaches 0.5 H (SOURCED: `RESULT.md:21`) | `0.727` (`output.txt:5` `reach_half_H`) | FOUND | Matches table (`output.txt:5`) |
| 21 | L21 | 48% | Other breaks reach 0.5 H (SOURCED: `RESULT.md:21`) | `0.477` (`output.txt:4` `reach_half_H`) | FOUND | Matches table (`output.txt:4`) |
| 22 | L22 | 36% | Lower-highs reaches 1 H (SOURCED: `RESULT.md:22`) | `0.364` (`output.txt:5` `reach_1H`) | FOUND | Matches table (`output.txt:5`) |
| 23 | L22 | 18% | Other breaks reach 1 H (SOURCED: `RESULT.md:22`) | `0.182` (`output.txt:4` `reach_1H`) | FOUND | Matches table (`output.txt:4`) |
| 24 | L23 | 70% | Other breaks back above S within 24 h (SOURCED: `RESULT.md:23`) | `0.705` (`output.txt:4` `failed_24h`) | FOUND | Matches table (`output.txt:4`) |
| 25 | L23 | 50% | Lower-highs back above S within 24 h (SOURCED: `RESULT.md:23`) | `0.500` (`output.txt:5` `failed_24h`) | FOUND | Matches table (`output.txt:5`) |
| 26 | L24 | 73% | Lower-highs failed_24h=True reaching 0.5 H (SOURCED: `RESULT.md:24`) | `0.727` (`output.txt:23` `failed=True reach_half_H`) | FOUND | Rounded to nearest percent (`output.txt:23` `0.727`, n=11) |
| 27 | L25 | n=22 | Sample size of lower-highs breaks (SOURCED: `RESULT.md:25`) | `22` (`output.txt:5` `lower-highs n`) | FOUND | Exact match |
| 28 | L25 | 87.4k, 87.2k, 87.0k, 84.4k/84.9k, 81.97k | Weekly/daily staircase highs (SOURCED: `RESULT.md:25`) | - | NOT_IN_DATA | Daily/weekly highs outside `output.txt` |
| 29 | L29 | 77,992 | 10-29 20:00Z 4h break bar close (SOURCED: `RESULT.md:29`) | - | NOT_IN_DATA | Real-time 10-29 break bar measurement not in `output.txt` |
| 30 | L29 | 79,221 | 10-29 break support level S (SOURCED: `RESULT.md:29`) | - | NOT_IN_DATA | Real-time 10-29 break bar measurement not in `output.txt` |
| 31 | L30 | 81.3k, 81.8k, 81.8k | Last three 4h highs on 10-29 (SOURCED: `RESULT.md:30`) | - | NOT_IN_DATA | Real-time 10-29 break bar measurement not in `output.txt` |
| 32 | L31 | 2,602 | Pattern height H on 10-29 break (SOURCED: `RESULT.md:31`) | - | NOT_IN_DATA | Real-time 10-29 break bar measurement not in `output.txt` |
| 33 | L32 | 77,920 | 0.5 H target price on 10-29 break (SOURCED: `RESULT.md:32`) | - | NOT_IN_DATA | Real-time 10-29 break target not in `output.txt` |
| 34 | L33 | 76,618 | 1 H target price on 10-29 break (SOURCED: `RESULT.md:33`) | - | NOT_IN_DATA | Real-time 10-29 break target not in `output.txt` |
| 35 | L33 | 76,500 | Low hit on 10-29/10-30 break (SOURCED: `RESULT.md:33`) | - | NOT_IN_DATA | Real-time 10-29 break low not in `output.txt` |
| 36 | L34 | 75,010 | 1.618 H target price on 10-29 break (SOURCED: `RESULT.md:34`) | - | NOT_IN_DATA | Real-time 10-29 break target not in `output.txt` |
| 37 | L34 | 75k | Michael's named support target (SOURCED: `RESULT.md:34`) | - | NOT_IN_DATA | External CBP analyst quote |
| 38 | L35 | 9% | 4h control rate for 1.618 H (SOURCED: `RESULT.md:35`) | `0.091` (`output.txt:4` `reach_1618H`) | FOUND | Matches table (`output.txt:4`) |
| 39 | L35 | 18% | 4h lower-highs rate for 1.618 H (SOURCED: `RESULT.md:35`) | `0.182` (`output.txt:5` `reach_1618H`) | FOUND | Matches table (`output.txt:5`) |
| 40 | L39 | 5 | `cbp.query(since_days=5)` parameter (SOURCED: `RESULT.md:39`) | - | NOT_IN_DATA | Role config parameter (OURS) |
| 41 | L41 | 7-day | Scoring window length (SOURCED: `RESULT.md:41`) | - | NOT_IN_DATA | Study window definition (OURS) |
