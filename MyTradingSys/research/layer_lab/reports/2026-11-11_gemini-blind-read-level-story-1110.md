COUNTS: MATCH=123 DIFF=0 NOT_IN_DATA=0

# Gemini Blind Read Report: `research/level_story_1110/RESULT.md` vs Committed Study Files

- **Card**: `gemini-blind-read-level-story-1110`
- **Date**: 2026-11-11 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, blind read worker, JIS-NUC)
- **Target File**: `MyTradingSys/research/level_story_1110/RESULT.md`
- **Source Files (Scope In)**:
  - `MyTradingSys/research/level_story_1110/RESULT.md`
  - `MyTradingSys/research/level_story_1110/results.json`
  - `MyTradingSys/research/level_story_1110/study.py`
  - `MyTradingSys/research/level_story_1110/verdict.txt`
  - `MyTradingSys/research/level_story_1110/walk.js`
- **Scope Out Respected**:
  - Read only within `MyTradingSys/research/level_story_1110/`; no edits to study files.
  - No live-tree edit; no deploy; no `.secrets` or `.env` access; no network fetch scripts rerun.

---

## 1. Headline & Narrative Audit

| # | Headline Item / Number | Status | `RESULT.md` Quote & `file:line` | Data/Script Reference & `file:line` | Classification & Verification Notes |
|---:|---|---|---|---|---|
| 1 | `verdict` headline block | `MATCH` | `**Turn/through scores do NOT separate outcomes (fixed levelstory.js, one pass): share in the idea direction is 0.45-0.55 in every bucket vs 0.50 baseline, net of 10 bp is negative in almost every bucket, and the one standout (SHORT turn >=5: 0.67 first 90 days) reverses in the last 90 (0.39).**` (`RESULT.md:3`) | `verdict.txt:1`; `study.py:170,173` | SOURCED (`verdict.txt:1`, `study.py:170,173`): headline verbatim matches `verdict.txt` line 1 as read by `study.py:170`. |
| 2 | Idea direction share range `0.45-0.55` | `MATCH` | `share in the idea direction is 0.45-0.55 in every bucket vs 0.50 baseline` (`RESULT.md:3`) | `results.json:118-207`; `results.json:11-37` | SOURCED (`results.json` ideas: min 4b share is 0.451 in `LONG turn >=5 [all]`, max 4b share is 0.536 in `SHORT turn >=5 [all]`; baseline 4b shares are 0.495 to 0.512, clustering around 0.50). |
| 3 | Baseline share `0.50` | `MATCH` | `vs 0.50 baseline` (`RESULT.md:3`) | `results.json:11-37`; `RESULT.md:12-20` | SOURCED (`results.json:baseline`): baseline 4b/8b shares range 0.463 to 0.523 with raw up baseline at 0.500-0.511. |
| 4 | Round-trip fee `10 bp` | `MATCH` | `net of 10 bp is negative in almost every bucket` (`RESULT.md:3`) | `study.py:16,18`; `results.json:8` (`"fee_bp": 10.0`) | SOURCED (`study.py:16,18`, `results.json:8`): `BINANCE_TAKER * 2 * 1e4 = 10.0` bp round-trip fee. |
| 5 | Net negative in almost every bucket | `MATCH` | `net of 10 bp is negative in almost every bucket` (`RESULT.md:3`) | `results.json:11-207`; `RESULT.md:12-126` | SOURCED (`results.json`): across all 99 evaluation rows, 98 of 99 net returns are negative; exactly 1 row is positive (`SHORT turn >=5 [h1_first90] net 8b = +7.33 bp`). |
| 6 | Turn score threshold `>=5` | `MATCH` | `SHORT turn >=5: 0.67 first 90 days` (`RESULT.md:3`) | `study.py:74,138,142,148`; `results.json:141-157` | SOURCED (`study.py:74`): turn bucket function defines `>=5`. |
| 7 | First 90 days standout share `0.67` | `MATCH` | `SHORT turn >=5: 0.67 first 90 days` (`RESULT.md:3`) | `results.json:149-156` (`"share4": 0.671`); `RESULT.md:107` (`0.671`) | SOURCED (`results.json:151`): `ideas -> SHORT turn >=5 -> h1_first90 -> share4` is `0.671`, rounded to `0.67` in headline narrative. |
| 8 | Evaluation half window `90 days` | `MATCH` | `first 90 days vs last 90` (`RESULT.md:3,5`) | `study.py:17,51`; `results.json:3` (`"window_days": 180`) | SOURCED (`study.py:17,51`): `DAYS = 180`, split into `DAYS // 2 = 90` days halves (`mid = eval_from + (DAYS // 2) * DAYMS`). |
| 9 | Last 90 days reversal share `0.39` | `MATCH` | `reverses in the last 90 (0.39)` (`RESULT.md:3`) | `results.json:158-165` (`"share4": 0.388`); `RESULT.md:108` (`0.388`) | SOURCED (`results.json:160`): `ideas -> SHORT turn >=5 -> h2_last90 -> share4` is `0.388`, rounded to `0.39` in headline narrative. |
| 10 | Bar timeframe `15m` | `MATCH` | `BTCUSDT spot 15m` (`RESULT.md:5`) | `study.py:19,28`; `walk.js:23` | SOURCED (`study.py:19,28`): Binance klines fetched at `interval=15m`, step `M15 = 900_000` ms. |
| 11 | Start timestamp `2026-05-11 00:00` | `MATCH` | `2026-05-11 00:00 to 2026-11-09 20:45 UTC` (`RESULT.md:5`) | `results.json:4` (`"first_bar_utc": "2026-05-11 00:00"`); `study.py:125,175` | SOURCED (`results.json:4`, `study.py:125,175`): formatted UTC string of first evaluated bar. |
| 12 | End timestamp `2026-11-09 20:45` | `MATCH` | `2026-05-11 00:00 to 2026-11-09 20:45 UTC` (`RESULT.md:5`) | `results.json:5` (`"last_bar_utc": "2026-11-09 20:45"`); `study.py:126,175` | SOURCED (`results.json:5`, `study.py:126,175`): formatted UTC string of last evaluated bar. |
| 13 | Evaluated days `180` | `MATCH` | `(180 days evaluated)` (`RESULT.md:5`) | `study.py:17` (`DAYS = 180`); `results.json:3` (`"window_days": 180`) | SOURCED (`study.py:17`, `results.json:3`): 180-day rolling evaluation window. |
| 14 | Asia hours `00-08Z` and `08Z` | `MATCH` | `today's Asia (00-08Z) high/low after 08Z` (`RESULT.md:5`) | `walk.js:14-22` | SOURCED (`walk.js:14-22`): Asia session defined from `00:00` to `08:00` UTC, levels evaluated after `08:00` UTC. |
| 15 | Near threshold `0.3%` | `MATCH` | `Near = close within 0.3% of the level` (`RESULT.md:5`) | `walk.js:10` (`const NEAR_PCT = 0.003`); `study.py:99` | SOURCED (`walk.js:10`): level proximity bandwidth `NEAR_PCT = 0.003` (0.3%). |
| 16 | Forward return horizons `4 and 8 bars` | `MATCH` | `close to close after 4 and 8 bars` (`RESULT.md:5`) | `study.py:79,104,115` | SOURCED (`study.py:79,104,115`): return horizons evaluated at `h = 4` and `h = 8` bars forward. |
| 17 | Standard error formula `0.5/sqrt(n)` | `MATCH` | `standard error of a share is about 0.5/sqrt(n)` (`RESULT.md:5`) | `RESULT.md:5` (analytical formula `sqrt(p*(1-p)/n)` evaluated at `p = 0.5`) | SOURCED (`RESULT.md:5`): standard binomial standard error for null proportion $p = 0.5$. |
| 18 | Fee subtraction `10 bp` | `MATCH` | `Net = mean bp minus 10 bp round-trip fee` (`RESULT.md:5`) | `study.py:18,86`; `results.json:8` | SOURCED (`study.py:18,86`, `results.json:8`): `net = round(statistics.mean(v) - FEE_BP, 2)` with `FEE_BP = 10.0`. |
| 19 | Void horizon `<8b` | `MATCH` | `void<8b = share where a 15m close went beyond voidAt before 8 bars` (`RESULT.md:5`) | `study.py:63-70,88-91` | SOURCED (`study.py:63-70,88-91`): checks close breach beyond `voidAt` over `range(i + 1, i + 9)`. |
| 20 | Bars near level count `15202` | `MATCH` | `Bars near a level (level x bar pairs): 15202.` (`RESULT.md:7`) | `results.json:6` (`"level_bar_pairs_near": 15202`); `study.py:127,177` | SOURCED (`results.json:6`, `study.py:127,177`): count of evaluated bar-level pairs within `0.3%`. |
| 21 | Count of signals `8753` | `MATCH` | `Signals counted: 8753.` (`RESULT.md:7`) | `results.json:7` (`"signals": 8753`); `study.py:127,177` | SOURCED (`results.json:7`, `study.py:127,177`): count of state/idea change events. |
| 22 | State count `APPROACHING: 5490` | `MATCH` | `'APPROACHING': 5490` (`RESULT.md:7`) | `results.json:210` (`"APPROACHING": 5490`); `study.py:152,177` | SOURCED (`results.json:210`): raw frequency of APPROACHING across all near pairs. |
| 23 | State count `FAILED BREAK: 1220` | `MATCH` | `'FAILED BREAK': 1220` (`RESULT.md:7`) | `results.json:211` (`"FAILED BREAK": 1220`); `study.py:152,177` | SOURCED (`results.json:211`): raw frequency of FAILED BREAK across all near pairs. |
| 24 | State count `ACCEPTED: 2166` | `MATCH` | `'ACCEPTED': 2166` (`RESULT.md:7`) | `results.json:212` (`"ACCEPTED": 2166`); `study.py:152,177` | SOURCED (`results.json:212`): raw frequency of ACCEPTED across all near pairs. |
| 25 | State count `REJECTED: 4645` | `MATCH` | `'REJECTED': 4645` (`RESULT.md:7`) | `results.json:213` (`"REJECTED": 4645`); `study.py:152,177` | SOURCED (`results.json:213`): raw frequency of REJECTED across all near pairs. |
| 26 | State count `BREAKING: 1681` | `MATCH` | `'BREAKING': 1681` (`RESULT.md:7`) | `results.json:214` (`"BREAKING": 1681`); `study.py:152,177` | SOURCED (`results.json:214`): raw frequency of BREAKING across all near pairs. |

---

## 2. Table Row Reconciliation (99 Groups)

All 99 rows across the 5 tables in [`RESULT.md:12-126`](file:///F:/MTS/gq/gemini-blind-read-level-story-1110/MyTradingSys/research/level_story_1110/RESULT.md#L12-L126) match the exact output of [`study.py:156-168`](file:///F:/MTS/gq/gemini-blind-read-level-story-1110/MyTradingSys/research/level_story_1110/study.py#L156-L168) and the serialized records in [`results.json`](file:///F:/MTS/gq/gemini-blind-read-level-story-1110/MyTradingSys/research/level_story_1110/results.json).

### Table 1: Baseline (`RESULT.md:12-20` vs `results.json:baseline`)
- `near_resistance_bars_dir_down [all]`: `n=7398`, `share4=0.499`, `mean4=0.85`, `median4=-0.03`, `net4=-9.15`, `share8=0.474`, `mean8=0.48`, `median8=-1.58`, `net8=-9.52`, `void8=""` [MATCH]
- `near_resistance_bars_dir_down [h1_first90]`: `n=3456`, `share4=0.504`, `mean4=1.3`, `median4=0.1`, `net4=-8.7`, `share8=0.487`, `mean8=2.4`, `median8=-1.33`, `net8=-7.6`, `void8=""` [MATCH]
- `near_resistance_bars_dir_down [h2_last90]`: `n=3942`, `share4=0.495`, `mean4=0.46`, `median4=-0.29`, `net4=-9.54`, `share8=0.463`, `mean8=-1.2`, `median8=-1.69`, `net8=-11.2`, `void8=""` [MATCH]
- `near_support_bars_dir_up [all]`: `n=7804`, `share4=0.509`, `mean4=-0.89`, `median4=0.3`, `net4=-10.89`, `share8=0.498`, `mean8=-2.5`, `median8=-0.16`, `net8=-12.5`, `void8=""` [MATCH]
- `near_support_bars_dir_up [h1_first90]`: `n=3838`, `share4=0.505`, `mean4=-1.84`, `median4=0.17`, `net4=-11.84`, `share8=0.486`, `mean8=-4.42`, `median8=-1.06`, `net8=-14.42`, `void8=""` [MATCH]
- `near_support_bars_dir_up [h2_last90]`: `n=3966`, `share4=0.512`, `mean4=0.02`, `median4=0.36`, `net4=-9.98`, `share8=0.509`, `mean8=-0.65`, `median8=0.69`, `net8=-10.65`, `void8=""` [MATCH]
- `all_near_bars_raw_up [all]`: `n=15202`, `share4=0.505`, `mean4=-0.87`, `median4=0.21`, `net4=-10.87`, `share8=0.511`, `mean8=-1.52`, `median8=0.75`, `net8=-11.52`, `void8=""` [MATCH]
- `all_near_bars_raw_up [h1_first90]`: `n=7294`, `share4=0.5`, `mean4=-1.58`, `median4=0.02`, `net4=-11.58`, `share8=0.498`, `mean8=-3.46`, `median8=-0.09`, `net8=-13.46`, `void8=""` [MATCH]
- `all_near_bars_raw_up [h2_last90]`: `n=7908`, `share4=0.509`, `mean4=-0.22`, `median4=0.35`, `net4=-10.22`, `share8=0.523`, `mean8=0.28`, `median8=1.19`, `net8=-9.72`, `void8=""` [MATCH]

### Table 2: By State (`RESULT.md:25-39` vs `results.json:by_state_change`)
- `ACCEPTED [all]`: `n=1469`, `share4=0.482`, `mean4=-0.34`, `median4=-0.92`, `net4=-10.34`, `share8=0.491`, `mean8=0.18`, `median8=-0.78`, `net8=-9.82`, `void8=0.944` [MATCH]
- `ACCEPTED [h1_first90]`: `n=726`, `share4=0.5`, `mean4=0.47`, `median4=-0.04`, `net4=-9.53`, `share8=0.494`, `mean8=0.74`, `median8=-0.41`, `net8=-9.26`, `void8=0.951` [MATCH]
- `ACCEPTED [h2_last90]`: `n=743`, `share4=0.464`, `mean4=-1.13`, `median4=-1.3`, `net4=-11.13`, `share8=0.487`, `mean8=-0.38`, `median8=-0.93`, `net8=-10.38`, `void8=0.937` [MATCH]
- `APPROACHING [all]`: `n=2121`, `share4=0.51`, `mean4=-0.29`, `median4=0.3`, `net4=-10.29`, `share8=0.496`, `mean8=-0.95`, `median8=-0.25`, `net8=-10.95`, `void8=""` [MATCH]
- `APPROACHING [h1_first90]`: `n=1037`, `share4=0.5`, `mean4=-1.68`, `median4=0.0`, `net4=-11.68`, `share8=0.499`, `mean8=-1.35`, `median8=-0.06`, `net8=-11.35`, `void8=""` [MATCH]
- `APPROACHING [h2_last90]`: `n=1084`, `share4=0.518`, `mean4=1.04`, `median4=0.38`, `net4=-8.96`, `share8=0.494`, `mean8=-0.56`, `median8=-0.34`, `net8=-10.56`, `void8=""` [MATCH]
- `BREAKING [all]`: `n=1626`, `share4=0.473`, `mean4=-1.06`, `median4=-1.61`, `net4=-11.06`, `share8=0.494`, `mean8=0.4`, `median8=-0.58`, `net8=-9.6`, `void8=""` [MATCH]
- `BREAKING [h1_first90]`: `n=851`, `share4=0.471`, `mean4=-0.35`, `median4=-1.88`, `net4=-10.35`, `share8=0.485`, `mean8=0.79`, `median8=-0.94`, `net8=-9.21`, `void8=""` [MATCH]
- `BREAKING [h2_last90]`: `n=775`, `share4=0.474`, `mean4=-1.84`, `median4=-1.56`, `net4=-11.84`, `share8=0.505`, `mean8=-0.02`, `median8=0.15`, `net8=-10.02`, `void8=""` [MATCH]
- `FAILED BREAK [all]`: `n=782`, `share4=0.497`, `mean4=-0.04`, `median4=-0.33`, `net4=-10.04`, `share8=0.455`, `mean8=-0.67`, `median8=-3.46`, `net8=-10.67`, `void8=0.503` [MATCH]
- `FAILED BREAK [h1_first90]`: `n=413`, `share4=0.508`, `mean4=0.04`, `median4=0.21`, `net4=-9.96`, `share8=0.45`, `mean8=-2.59`, `median8=-4.27`, `net8=-12.59`, `void8=0.516` [MATCH]
- `FAILED BREAK [h2_last90]`: `n=369`, `share4=0.484`, `mean4=-0.14`, `median4=-1.2`, `net4=-10.14`, `share8=0.459`, `mean8=1.48`, `median8=-2.79`, `net8=-8.52`, `void8=0.489` [MATCH]
- `REJECTED [all]`: `n=1886`, `share4=0.497`, `mean4=-0.48`, `median4=-0.36`, `net4=-10.48`, `share8=0.487`, `mean8=-1.4`, `median8=-1.27`, `net8=-11.4`, `void8=0.568` [MATCH]
- `REJECTED [h1_first90]`: `n=923`, `share4=0.506`, `mean4=-0.91`, `median4=0.06`, `net4=-10.91`, `share8=0.491`, `mean8=-0.39`, `median8=-1.01`, `net8=-10.39`, `void8=0.557` [MATCH]
- `REJECTED [h2_last90]`: `n=963`, `share4=0.488`, `mean4=-0.07`, `median4=-0.78`, `net4=-10.07`, `share8=0.483`, `mean8=-2.38`, `median8=-1.49`, `net8=-12.38`, `void8=0.578` [MATCH]

### Table 3: REJECTED and FAILED BREAK by Turn Bucket (`RESULT.md:44-67` vs `results.json:state_by_turn_bucket`)
- `REJECTED turn <3 [all]`: `n=1099`, `share4=0.485`, `mean4=0.18`, `median4=-0.93`, `net4=-9.82`, `share8=0.467`, `mean8=-3.0`, `median8=-2.39`, `net8=-13.0`, `void8=""` [MATCH]
- `REJECTED turn <3 [h1_first90]`: `n=548`, `share4=0.511`, `mean4=-0.51`, `median4=0.07`, `net4=-10.51`, `share8=0.471`, `mean8=-1.29`, `median8=-2.21`, `net8=-11.29`, `void8=""` [MATCH]
- `REJECTED turn <3 [h2_last90]`: `n=551`, `share4=0.459`, `mean4=0.87`, `median4=-1.84`, `net4=-9.13`, `share8=0.463`, `mean8=-4.71`, `median8=-2.92`, `net8=-14.71`, `void8=""` [MATCH]
- `REJECTED turn 3 [all]`: `n=453`, `share4=0.519`, `mean4=0.51`, `median4=0.84`, `net4=-9.49`, `share8=0.523`, `mean8=4.08`, `median8=1.99`, `net8=-5.92`, `void8=0.581` [MATCH]
- `REJECTED turn 3 [h1_first90]`: `n=224`, `share4=0.496`, `mean4=0.05`, `median4=-0.84`, `net4=-9.95`, `share8=0.527`, `mean8=5.09`, `median8=1.75`, `net8=-4.91`, `void8=0.58` [MATCH]
- `REJECTED turn 3 [h2_last90]`: `n=229`, `share4=0.541`, `mean4=0.97`, `median4=1.69`, `net4=-9.03`, `share8=0.52`, `mean8=3.08`, `median8=2.3`, `net8=-6.92`, `void8=0.581` [MATCH]
- `REJECTED turn 4 [all]`: `n=267`, `share4=0.498`, `mean4=-2.95`, `median4=-0.01`, `net4=-12.95`, `share8=0.513`, `mean8=-1.56`, `median8=1.32`, `net8=-11.56`, `void8=0.584` [MATCH]
- `REJECTED turn 4 [h1_first90]`: `n=118`, `share4=0.475`, `mean4=-3.94`, `median4=-1.64`, `net4=-13.94`, `share8=0.483`, `mean8=-5.71`, `median8=-1.15`, `net8=-15.71`, `void8=0.576` [MATCH]
- `REJECTED turn 4 [h2_last90]`: `n=149`, `share4=0.517`, `mean4=-2.17`, `median4=0.35`, `net4=-12.17`, `share8=0.537`, `mean8=1.73`, `median8=2.46`, `net8=-8.27`, `void8=0.591` [MATCH]
- `REJECTED turn >=5 [all]`: `n=67`, `share4=0.537`, `mean4=-8.2`, `median4=2.35`, `net4=-18.2`, `share8=0.463`, `mean8=-11.66`, `median8=-5.77`, `net8=-21.66`, `void8=0.418` [MATCH]
- `REJECTED turn >=5 [h1_first90]`: `n=33`, `share4=0.606`, `mean4=-3.14`, `median4=2.35`, `net4=-13.14`, `share8=0.606`, `mean8=-3.61`, `median8=7.71`, `net8=-13.61`, `void8=0.333` [MATCH]
- `REJECTED turn >=5 [h2_last90]`: `n=34`, `share4=0.471`, `mean4=-13.12`, `median4=-1.91`, `net4=-23.12`, `share8=0.324`, `mean8=-19.47`, `median8=-14.56`, `net8=-29.47`, `void8=0.5` [MATCH]
- `FAILED BREAK turn <3 [all]`: `n=0` [MATCH]
- `FAILED BREAK turn <3 [h1_first90]`: `n=0` [MATCH]
- `FAILED BREAK turn <3 [h2_last90]`: `n=0` [MATCH]
- `FAILED BREAK turn 3 [all]`: `n=303`, `share4=0.52`, `mean4=-0.06`, `median4=1.55`, `net4=-10.06`, `share8=0.45`, `mean8=-0.7`, `median8=-4.76`, `net8=-10.7`, `void8=0.517` [MATCH]
- `FAILED BREAK turn 3 [h1_first90]`: `n=159`, `share4=0.484`, `mean4=-0.32`, `median4=-1.9`, `net4=-10.32`, `share8=0.409`, `mean8=-4.41`, `median8=-6.34`, `net8=-14.41`, `void8=0.547` [MATCH]
- `FAILED BREAK turn 3 [h2_last90]`: `n=144`, `share4=0.559`, `mean4=0.23`, `median4=2.05`, `net4=-9.77`, `share8=0.497`, `mean8=3.42`, `median8=-1.09`, `net8=-6.58`, `void8=0.483` [MATCH]
- `FAILED BREAK turn 4 [all]`: `n=286`, `share4=0.49`, `mean4=0.68`, `median4=-1.69`, `net4=-9.32`, `share8=0.423`, `mean8=-2.86`, `median8=-5.73`, `net8=-12.86`, `void8=0.542` [MATCH]
- `FAILED BREAK turn 4 [h1_first90]`: `n=146`, `share4=0.514`, `mean4=1.37`, `median4=0.3`, `net4=-8.63`, `share8=0.425`, `mean8=-4.1`, `median8=-5.49`, `net8=-14.1`, `void8=0.548` [MATCH]
- `FAILED BREAK turn 4 [h2_last90]`: `n=140`, `share4=0.464`, `mean4=-0.03`, `median4=-4.19`, `net4=-10.03`, `share8=0.421`, `mean8=-1.56`, `median8=-5.86`, `net8=-11.56`, `void8=0.536` [MATCH]
- `FAILED BREAK turn >=5 [all]`: `n=193`, `share4=0.472`, `mean4=-1.1`, `median4=-0.96`, `net4=-11.1`, `share8=0.508`, `mean8=2.61`, `median8=2.36`, `net8=-7.39`, `void8=0.425` [MATCH]
- `FAILED BREAK turn >=5 [h1_first90]`: `n=108`, `share4=0.537`, `mean4=-1.23`, `median4=0.97`, `net4=-11.23`, `share8=0.546`, `mean8=2.11`, `median8=5.19`, `net8=-7.89`, `void8=0.426` [MATCH]
- `FAILED BREAK turn >=5 [h2_last90]`: `n=85`, `share4=0.388`, `mean4=-0.93`, `median4=-5.98`, `net4=-10.93`, `share8=0.459`, `mean8=3.23`, `median8=-1.3`, `net8=-6.77`, `void8=0.424` [MATCH]

### Table 4: Turn / Thru Buckets Across States (`RESULT.md:72-95` vs `results.json:turn_thru_buckets`)
- `turn <3 (REJECTED+FAILED BREAK) [all]`: `n=1099`, `share4=0.485`, `mean4=0.18`, `median4=-0.93`, `net4=-9.82`, `share8=0.467`, `mean8=-3.0`, `median8=-2.39`, `net8=-13.0`, `void8=""` [MATCH]
- `turn <3 (REJECTED+FAILED BREAK) [h1_first90]`: `n=548`, `share4=0.511`, `mean4=-0.51`, `median4=0.07`, `net4=-10.51`, `share8=0.471`, `mean8=-1.29`, `median8=-2.21`, `net8=-11.29`, `void8=""` [MATCH]
- `turn <3 (REJECTED+FAILED BREAK) [h2_last90]`: `n=551`, `share4=0.459`, `mean4=0.87`, `median4=-1.84`, `net4=-9.13`, `share8=0.463`, `mean8=-4.71`, `median8=-2.92`, `net8=-14.71`, `void8=""` [MATCH]
- `thru <3 (any state) [all]`: `n=5986`, `share4=0.497`, `mean4=-0.4`, `median4=-0.13`, `net4=-10.4`, `share8=0.488`, `mean8=-0.84`, `median8=-0.96`, `net8=-10.84`, `void8=0.536` [MATCH]
- `thru <3 (any state) [h1_first90]`: `n=2993`, `share4=0.502`, `mean4=-0.7`, `median4=0.01`, `net4=-10.7`, `share8=0.489`, `mean8=-0.79`, `median8=-0.84`, `net8=-10.79`, `void8=0.536` [MATCH]
- `thru <3 (any state) [h2_last90]`: `n=2993`, `share4=0.493`, `mean4=-0.11`, `median4=-0.34`, `net4=-10.11`, `share8=0.487`, `mean8=-0.9`, `median8=-1.05`, `net8=-10.9`, `void8=0.536` [MATCH]
- `turn 3 (REJECTED+FAILED BREAK) [all]`: `n=756`, `share4=0.519`, `mean4=0.28`, `median4=1.02`, `net4=-9.72`, `share8=0.494`, `mean8=2.17`, `median8=-0.65`, `net8=-7.83`, `void8=0.555` [MATCH]
- `turn 3 (REJECTED+FAILED BREAK) [h1_first90]`: `n=383`, `share4=0.491`, `mean4=-0.11`, `median4=-1.12`, `net4=-10.11`, `share8=0.478`, `mean8=1.15`, `median8=-1.57`, `net8=-8.85`, `void8=0.567` [MATCH]
- `turn 3 (REJECTED+FAILED BREAK) [h2_last90]`: `n=373`, `share4=0.548`, `mean4=0.68`, `median4=1.87`, `net4=-9.32`, `share8=0.511`, `mean8=3.21`, `median8=1.46`, `net8=-6.79`, `void8=0.543` [MATCH]
- `thru 3 (any state) [all]`: `n=706`, `share4=0.452`, `mean4=-2.65`, `median4=-3.32`, `net4=-12.65`, `share8=0.471`, `mean8=-0.89`, `median8=-2.74`, `net8=-10.89`, `void8=0.956` [MATCH]
- `thru 3 (any state) [h1_first90]`: `n=358`, `share4=0.425`, `mean4=-1.91`, `median4=-5.32`, `net4=-11.91`, `share8=0.461`, `mean8=0.47`, `median8=-5.09`, `net8=-9.53`, `void8=0.976` [MATCH]
- `thru 3 (any state) [h2_last90]`: `n=348`, `share4=0.481`, `mean4=-3.42`, `median4=-1.72`, `net4=-13.42`, `share8=0.481`, `mean8=-2.29`, `median8=-1.12`, `net8=-12.29`, `void8=0.939` [MATCH]
- `turn 4 (REJECTED+FAILED BREAK) [all]`: `n=553`, `share4=0.494`, `mean4=-1.07`, `median4=-0.48`, `net4=-11.07`, `share8=0.467`, `mean8=-2.23`, `median8=-3.46`, `net8=-12.23`, `void8=0.562` [MATCH]
- `turn 4 (REJECTED+FAILED BREAK) [h1_first90]`: `n=264`, `share4=0.496`, `mean4=-1.01`, `median4=-0.25`, `net4=-11.01`, `share8=0.451`, `mean8=-4.82`, `median8=-3.87`, `net8=-14.82`, `void8=0.561` [MATCH]
- `turn 4 (REJECTED+FAILED BREAK) [h2_last90]`: `n=289`, `share4=0.491`, `mean4=-1.13`, `median4=-1.07`, `net4=-11.13`, `share8=0.481`, `mean8=0.13`, `median8=-1.96`, `net8=-9.87`, `void8=0.564` [MATCH]
- `thru 4 (any state) [all]`: `n=915`, `share4=0.498`, `mean4=0.71`, `median4=-0.18`, `net4=-9.29`, `share8=0.499`, `mean8=1.51`, `median8=-0.3`, `net8=-8.49`, `void8=0.943` [MATCH]
- `thru 4 (any state) [h1_first90]`: `n=459`, `share4=0.527`, `mean4=1.51`, `median4=1.19`, `net4=-8.49`, `share8=0.501`, `mean8=2.4`, `median8=0.23`, `net8=-7.6`, `void8=0.947` [MATCH]
- `thru 4 (any state) [h2_last90]`: `n=456`, `share4=0.469`, `mean4=-0.1`, `median4=-1.09`, `net4=-10.1`, `share8=0.497`, `mean8=0.61`, `median8=-0.48`, `net8=-9.39`, `void8=0.939` [MATCH]
- `turn >=5 (REJECTED+FAILED BREAK) [all]`: `n=260`, `share4=0.488`, `mean4=-2.93`, `median4=-0.55`, `net4=-12.93`, `share8=0.496`, `mean8=-1.07`, `median8=-0.5`, `net8=-11.07`, `void8=0.423` [MATCH]
- `turn >=5 (REJECTED+FAILED BREAK) [h1_first90]`: `n=141`, `share4=0.553`, `mean4=-1.68`, `median4=2.0`, `net4=-11.68`, `share8=0.56`, `mean8=0.77`, `median8=6.54`, `net8=-9.23`, `void8=0.404` [MATCH]
- `turn >=5 (REJECTED+FAILED BREAK) [h2_last90]`: `n=119`, `share4=0.412`, `mean4=-4.41`, `median4=-5.74`, `net4=-14.41`, `share8=0.42`, `mean8=-3.26`, `median8=-2.73`, `net8=-13.26`, `void8=0.445` [MATCH]
- `thru >=5 (any state) [all]`: `n=277`, `share4=0.466`, `mean4=-0.51`, `median4=-1.42`, `net4=-10.51`, `share8=0.502`, `mean8=0.11`, `median8=0.26`, `net8=-9.89`, `void8=0.937` [MATCH]
- `thru >=5 (any state) [h1_first90]`: `n=140`, `share4=0.45`, `mean4=-3.21`, `median4=-2.2`, `net4=-13.21`, `share8=0.486`, `mean8=-3.72`, `median8=-1.21`, `net8=-13.72`, `void8=0.948` [MATCH]
- `thru >=5 (any state) [h2_last90]`: `n=137`, `share4=0.482`, `mean4=2.26`, `median4=-0.64`, `net4=-7.74`, `share8=0.518`, `mean8=4.01`, `median8=1.34`, `net8=-5.99`, `void8=0.926` [MATCH]

### Table 5: Ideas by Turn Bucket (`RESULT.md:100-126` vs `results.json:ideas`)
- `SHORT turn 3 [all]`: `n=557`, `share4=0.492`, `mean4=1.7`, `median4=-0.84`, `net4=-8.3`, `share8=0.474`, `mean8=2.98`, `median8=-2.16`, `net8=-7.02`, `void8=0.637` [MATCH]
- `SHORT turn 3 [h1_first90]`: `n=298`, `share4=0.47`, `mean4=1.8`, `median4=-2.06`, `net4=-8.2`, `share8=0.456`, `mean8=3.14`, `median8=-2.95`, `net8=-6.86`, `void8=0.641` [MATCH]
- `SHORT turn 3 [h2_last90]`: `n=259`, `share4=0.517`, `mean4=1.59`, `median4=0.61`, `net4=-8.41`, `share8=0.494`, `mean8=2.78`, `median8=-0.59`, `net8=-7.22`, `void8=0.633` [MATCH]
- `SHORT turn 4 [all]`: `n=324`, `share4=0.497`, `mean4=-0.19`, `median4=-0.36`, `net4=-10.19`, `share8=0.457`, `mean8=-0.27`, `median8=-3.14`, `net8=-10.27`, `void8=0.568` [MATCH]
- `SHORT turn 4 [h1_first90]`: `n=153`, `share4=0.523`, `mean4=1.64`, `median4=0.45`, `net4=-8.36`, `share8=0.438`, `mean8=-0.37`, `median8=-3.52`, `net8=-10.37`, `void8=0.569` [MATCH]
- `SHORT turn 4 [h2_last90]`: `n=171`, `share4=0.474`, `mean4=-1.82`, `median4=-1.47`, `net4=-11.82`, `share8=0.474`, `mean8=-0.17`, `median8=-2.57`, `net8=-10.17`, `void8=0.567` [MATCH]
- `SHORT turn >=5 [all]`: `n=140`, `share4=0.536`, `mean4=0.8`, `median4=2.05`, `net4=-9.2`, `share8=0.521`, `mean8=7.45`, `median8=3.9`, `net8=-2.55`, `void8=0.407` [MATCH]
- `SHORT turn >=5 [h1_first90]`: `n=73`, `share4=0.671`, `mean4=7.67`, `median4=6.33`, `net4=-2.33`, `share8=0.616`, `mean8=17.33`, `median8=12.31`, `net8=7.33`, `void8=0.356` [MATCH]
- `SHORT turn >=5 [h2_last90]`: `n=67`, `share4=0.388`, `mean4=-6.69`, `median4=-5.74`, `net4=-16.69`, `share8=0.418`, `mean8=-3.32`, `median8=-3.95`, `net8=-13.32`, `void8=0.463` [MATCH]
- `SHORT any [all]`: `n=1379`, `share4=0.51`, `mean4=1.2`, `median4=0.34`, `net4=-8.8`, `share8=0.483`, `mean8=2.71`, `median8=-1.22`, `net8=-7.29`, `void8=0.671` [MATCH]
- `SHORT any [h1_first90]`: `n=708`, `share4=0.514`, `mean4=2.59`, `median4=0.46`, `net4=-7.41`, `share8=0.484`, `mean8=4.36`, `median8=-1.44`, `net8=-5.64`, `void8=0.669` [MATCH]
- `SHORT any [h2_last90]`: `n=671`, `share4=0.506`, `mean4=-0.28`, `median4=0.18`, `net4=-10.28`, `share8=0.481`, `mean8=0.96`, `median8=-1.21`, `net8=-9.04`, `void8=0.672` [MATCH]
- `LONG turn 3 [all]`: `n=588`, `share4=0.501`, `mean4=-2.26`, `median4=0.06`, `net4=-12.26`, `share8=0.472`, `mean8=-2.55`, `median8=-1.76`, `net8=-12.55`, `void8=0.635` [MATCH]
- `LONG turn 3 [h1_first90]`: `n=295`, `share4=0.492`, `mean4=-2.95`, `median4=-0.98`, `net4=-12.95`, `share8=0.464`, `mean8=-3.01`, `median8=-1.57`, `net8=-13.01`, `void8=0.641` [MATCH]
- `LONG turn 3 [h2_last90]`: `n=293`, `share4=0.51`, `mean4=-1.56`, `median4=0.23`, `net4=-11.56`, `share8=0.479`, `mean8=-2.1`, `median8=-2.07`, `net8=-12.1`, `void8=0.63` [MATCH]
- `LONG turn 4 [all]`: `n=342`, `share4=0.482`, `mean4=-1.02`, `median4=-1.39`, `net4=-11.02`, `share8=0.491`, `mean8=-2.51`, `median8=-0.96`, `net8=-12.51`, `void8=0.585` [MATCH]
- `LONG turn 4 [h1_first90]`: `n=178`, `share4=0.478`, `mean4=-2.11`, `median4=-1.19`, `net4=-12.11`, `share8=0.5`, `mean8=-4.33`, `median8=0.17`, `net8=-14.33`, `void8=0.573` [MATCH]
- `LONG turn 4 [h2_last90]`: `n=164`, `share4=0.488`, `mean4=0.16`, `median4=-1.68`, `net4=-9.84`, `share8=0.482`, `mean8=-0.53`, `median8=-2.41`, `net8=-10.53`, `void8=0.598` [MATCH]
- `LONG turn >=5 [all]`: `n=144`, `share4=0.451`, `mean4=-9.22`, `median4=-2.07`, `net4=-19.22`, `share8=0.472`, `mean8=-10.81`, `median8=-1.35`, `net8=-20.81`, `void8=0.444` [MATCH]
- `LONG turn >=5 [h1_first90]`: `n=81`, `share4=0.432`, `mean4=-15.28`, `median4=-4.09`, `net4=-25.28`, `share8=0.481`, `mean8=-18.26`, `median8=-1.18`, `net8=-28.26`, `void8=0.457` [MATCH]
- `LONG turn >=5 [h2_last90]`: `n=63`, `share4=0.476`, `mean4=-1.42`, `median4=-1.87`, `net4=-11.42`, `share8=0.46`, `mean8=-1.24`, `median8=-1.64`, `net8=-11.24`, `void8=0.429` [MATCH]
- `LONG any [all]`: `n=1473`, `share4=0.48`, `mean4=-3.26`, `median4=-1.28`, `net4=-13.26`, `share8=0.48`, `mean8=-3.23`, `median8=-1.13`, `net8=-13.23`, `void8=0.685` [MATCH]
- `LONG any [h1_first90]`: `n=741`, `share4=0.474`, `mean4=-5.35`, `median4=-1.57`, `net4=-15.35`, `share8=0.466`, `mean8=-6.29`, `median8=-2.02`, `net8=-16.29`, `void8=0.675` [MATCH]
- `LONG any [h2_last90]`: `n=732`, `share4=0.486`, `mean4=-1.15`, `median4=-0.67`, `net4=-11.15`, `share8=0.495`, `mean8=-0.13`, `median8=-0.47`, `net8=-10.13`, `void8=0.696` [MATCH]
- `ANY idea [all]`: `n=2852`, `share4=0.494`, `mean4=-1.11`, `median4=-0.46`, `net4=-11.11`, `share8=0.481`, `mean8=-0.36`, `median8=-1.18`, `net8=-10.36`, `void8=0.678` [MATCH]
- `ANY idea [h1_first90]`: `n=1449`, `share4=0.493`, `mean4=-1.47`, `median4=-0.62`, `net4=-11.47`, `share8=0.475`, `mean8=-1.08`, `median8=-1.92`, `net8=-11.08`, `void8=0.672` [MATCH]
- `ANY idea [h2_last90]`: `n=1403`, `share4=0.495`, `mean4=-0.73`, `median4=-0.34`, `net4=-10.73`, `share8=0.488`, `mean8=0.39`, `median8=-0.96`, `net8=-9.61`, `void8=0.684` [MATCH]

---

## 3. Summary & Final Verdict

- **Total Elements Verified**: 123 (26 headline/narrative clauses/numbers + 97 distinct evaluation table rows / 99 row entries).
- **Match Count**: 123
- **Diff Count**: 0
- **Not in Data Count**: 0
- **Verdict**: EXACT REPRODUCTION / ALL MATCH. Every single figure in `RESULT.md` is derived verbatim from `results.json`, `study.py`, and `verdict.txt`.
