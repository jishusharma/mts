# Blind Read: `bigcandle_story_2026-11-05`

- **Card**: `gemini-blind-read-bigcandle-story-1106`
- **Reader**: Gemini (independent blind read worker), 2026-11-06
- **Target Study**: `MyTradingSys/research/bigcandle_story_2026-11-05/RESULT.md`
- **Data & Tables**: `tables.md`, `walkthrough.md`, `PRE_REG.md`
- **Data on Disk**:
  - 1m klines: SOURCED `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv` (89 DEV monthly files, 1,313,280 1m kline rows; OURS: 262,080 5m bars on grid 2022-01-03 to 2024-06-30).
  - 5m metrics: SOURCED `F:/MTS/data/metrics/BTCUSDT/BTCUSDT-metrics-*.csv` (1,762 daily files; OURS: 261,818 valid OI rows, 170,773 valid top-trader position ratios, 170,774 valid top-trader account ratios).
- **Independent Execution**:
  - Recomputed all 843 1h big events, 3,991 5m big events, 21,831 1h baseline bars, and 261,310 5m baseline bars independently from raw klines and metrics.
  - Recomputed all 472 lines of `tables.md` from raw data; verified 100% byte-for-byte exact match against committed `tables.md`.

---

## 1. Per-Claim Verification Table

Every number is labeled SOURCED (quote + file:line) or OURS (independent computation).

| # | Claim / Metric | SOURCED (Quote & file:line) | OURS (Recomputed Value) | Status |
|---|---|---|---|---|
| 1 | Baseline 1h total bars | `21,831 1h bars as baseline` [SOURCED `RESULT.md:7`, `tables.md:3`] | OURS: 21,831 bars (11,064 UP + 10,767 DOWN; 9 bars dropped for zero return or missing data out of 21,840 calendar hours) | MATCH |
| 2 | Big 1h events total | `843 big 1h events` [SOURCED `RESULT.md:7`, `tables.md:3`] | OURS: 843 events (sum of 8 stories: 180 + 223 + 269 + 117 + 16 + 12 + 16 + 10 = 843) | MATCH |
| 3 | Big 5m events total | `3,991 big 5m events (12-bar lockout)` [SOURCED `RESULT.md:7`, `tables.md:3`] | OURS: 3,991 events (sum of 8 stories: 615 + 1273 + 1437 + 467 + 71 + 36 + 57 + 35 = 3991) | MATCH |
| 4 | 1h Regime mix: bull / bear / range | `bull 27 % / bear 27 % / range 46 % (30-day band)` [SOURCED `RESULT.md:7`, `tables.md:4`] | OURS: bull 228 (27.0%), bear 227 (26.9%), range 388 (46.0%) of 843 events | MATCH |
| 5 | 1h Weekly streak groups | `R3+ 124, R1-2 350, G1-2 286, G3+ 83 events` [SOURCED `RESULT.md:7`, `tables.md:4`] | OURS: R3+ 124, R1-2 350, G1-2 286, G3+ 83 (sum = 843) | MATCH |
| 6 | 1h Top-trader class mix | `{"BD": 80, "BU": 145, "FLAT": 78, "NA": 303, "SL": 131, "SS": 106}` [SOURCED `tables.md:5`, `RESULT.md:68`] | OURS: BD 80, BU 145, FLAT 78, NA 303 (302 in 2022, 1 in 2023), SL 131, SS 106 (sum = 843) | MATCH |
| 7 | 1h Baseline UP bars | `all UP bars \| 11064 \| 47% [46-48] \| 48% [47-49] \| 50% [49-51] \| 25% / 34% / 43%` [SOURCED `tables.md:8`, `RESULT.md:37`] | OURS: n=11,064; cont 1h: 47.4% [46.5-48.3]; cont 4h: 48.1% [47.2-49.1]; cont 24h: 50.0% [49.0-50.9]; undone: 25.0% / 34.3% / 43.1% | MATCH |
| 8 | 1h Baseline DOWN bars | `all DOWN bars \| 10767 \| 45% [44-46] \| 47% [46-48] \| 48% [47-49] \| 26% / 35% / 44%` [SOURCED `tables.md:15`, `RESULT.md:37`] | OURS: n=10,767; cont 1h: 45.4% [44.5-46.3]; cont 4h: 46.8% [45.9-47.8]; cont 24h: 48.3% [47.4-49.2]; undone: 25.5% / 35.1% / 44.0% | MATCH |
| 9 | 1h UP/UP/BUY (new longs) | `180 \| 52 % [45-59] \| 59 % [51-66] \| 58 % [50-64]` [SOURCED `RESULT.md:41`, `tables.md:36`] | OURS: n=180; cont 1h: 52.2% [45.0-59.4]; cont 4h (nv=179): 58.7% [51.3-65.6]; cont 24h (nv=179): 57.5% [50.2-64.5]; undone: 7.2% / 11.7% / 26.3% | MATCH |
| 10 | 1h UP/DOWN/BUY (short covering) | `223 \| 46 % [40-53] \| 45 % [39-52] \| 51 % [44-57]` [SOURCED `RESULT.md:42`, `tables.md:34`] | OURS: n=223; cont 1h: 46.2% [39.8-52.7]; cont 4h (nv=223): 45.3% [38.9-51.8]; cont 24h (nv=223): 50.7% [44.1-57.2]; undone: 9.9% / 12.1% / 26.9% | MATCH |
| 11 | 1h DOWN/DOWN/SELL (long liq) | `269 \| 43 % [37-49] \| 46 % [40-52] \| 46 % [41-52]` [SOURCED `RESULT.md:43`, `tables.md:31`] | OURS: n=269; cont 1h: 43.1% [37.4-49.1]; cont 4h (nv=269): 46.1% [40.2-52.1]; cont 24h (nv=268): 46.3% [40.4-52.3]; undone: 3.0% / 8.2% / 28.4% | MATCH |
| 12 | 1h DOWN/UP/SELL (new shorts) | `117 \| 44 % [35-53] \| 44 % [36-54] \| 45 % [37-54]` [SOURCED `RESULT.md:44`, `tables.md:33`] | OURS: n=117; cont 1h: 43.6% [35.0-52.6]; cont 4h (nv=117): 44.4% [35.8-53.5]; cont 24h (nv=117): 45.3% [36.6-54.3]; undone: 6.8% / 21.4% / 35.0% | MATCH |
| 13 | 1h DOWN/DOWN/SELL x SS | `46 \| 41 % [28-56] \| 33 % [21-47] \| 39 % [26-54]` [SOURCED `RESULT.md:45`, `tables.md:46`] | OURS: n=46; cont 1h: 41.3% [28.3-55.7]; cont 4h (nv=46): 32.6% [20.9-46.9]; cont 24h (nv=46): 39.1% [26.4-53.6]; undone: 2.2% / 6.5% / 26.1% | MATCH |
| 14 | 1h "other 3 stories" label | `\| the other 3 stories \| 10-16 \| \| \| \| THIN \|` [SOURCED `RESULT.md:46`] | OURS: Exactly 4 remaining stories: DOWN\|DOWN\|BUY (n=16), DOWN\|UP\|BUY (n=12), UP\|DOWN\|SELL (n=16), UP\|UP\|SELL (n=10); range is 10-16, but story count is 4, not 3 (8 total - 4 main = 4) | MISMATCH (Defect: `RESULT.md:46`) |
| 15 | 1h price big, UP, SL | `51 \| 45 % [32-59] \| 53 % [40-66] \| 51 % [38-64]` [SOURCED `RESULT.md:52`, `tables.md:121`] | OURS: n=51; cont 1h: 45.1% [32.3-58.6]; cont 4h: 52.9% [39.5-66.0]; cont 24h: 51.0% [37.7-64.1] | MATCH |
| 16 | 1h price big, UP, SL, streak R1-2 | `30 \| 43 % [27-61] \| 50 % [33-67] \| 53 % [36-70]` [SOURCED `RESULT.md:53`, `tables.md:127`] | OURS: n=30; cont 1h: 43.3% [27.4-60.8]; cont 4h: 50.0% [33.2-66.8]; cont 24h: 53.3% [36.1-69.8] | MATCH |
| 17 | 1h price big, UP, SL, streak R3+ | `3 \| THIN \| THIN \| THIN` [SOURCED `RESULT.md:54`, `tables.md:128`] | OURS: n=3 THIN (cont 33% / 100% / 100%) | MATCH |
| 18 | 1h price big, UP, SL, streak G1-2 / G3+ | `12 / 6 \| THIN \| THIN \| THIN` [SOURCED `RESULT.md:55`, `tables.md:125,126`] | OURS: n=12 THIN / n=6 THIN | MATCH |
| 19 | 1h price big, UP, SL, band range/bull/bear | `27 / 20 / 4 \| THIN \| THIN \| THIN` [SOURCED `RESULT.md:56`, `tables.md:122-124`] | OURS: n=27 THIN / n=20 THIN / n=4 THIN (sum = 51) | MATCH |
| 20 | 5m price big, UP, SL (60m lockout) | `136 \| 46 % [38-55] \| 45 % [37-53] \| 45 % [37-54]` [SOURCED `RESULT.md:57`, `tables.md:338`] | OURS: n=136; cont 1h: 46.3% [38.2-54.7]; cont 4h: 44.9% [36.8-53.2]; cont 24h: 45.3% [37.2-53.7]; baseline UP 49.3%/49.9%/50.3% | MATCH |
| 21 | 5m price big, UP, SL, streak G1-2 | `52 \| 46 % [33-60] \| 35 % [23-48] \| 42 % [30-56]` [SOURCED `RESULT.md:58`, `tables.md:342`] | OURS: n=52; cont 1h: 46.2% [33.4-59.5]; cont 4h: 34.6% [23.2-48.2]; cont 24h: 42.3% [29.9-55.8] | MATCH |
| 22 | 5m price big, UP, SL, streak R1-2 | `47 \| 40 % [28-55] \| 47 % [33-61] \| 41 % [28-56]` [SOURCED `RESULT.md:59`, `tables.md:344`] | OURS: n=47; cont 1h: 40.4% [27.7-54.6]; cont 4h: 46.8% [33.3-60.8]; cont 24h: 41.3% [28.4-55.5] | MATCH |
| 23 | 5m price big, UP, SL, streak G3+ / R3+ | `29 / 8 \| THIN` [SOURCED `RESULT.md:60`, `tables.md:343,345`] | OURS: n=29 THIN / n=8 THIN (sum with G1-2 and R1-2: 52 + 47 + 29 + 8 = 136) | MATCH |
| 24 | 1h UP/DOWN/BUY/SL short-cover rally | `n 60 ... 37 %, CI 26-49; baseline 47 %` [SOURCED `RESULT.md:62`, `tables.md:55`] | OURS: n=60; cont 1h: 36.7% [25.8-49.1]; cont 4h: 43.3% [31.6-55.9]; cont 24h: 50.0% [37.7-62.3] | MATCH |
| 25 | 5m DOWN/DOWN/SELL (long liq) | `n 1,437 ... 42 % at 1h (CI 40-45) and 41 % at 4h against a 48 % DOWN baseline` [SOURCED `RESULT.md:65`, `tables.md:241`] | OURS: n=1,437; cont 1h: 42.5% [39.9-45.0]; cont 4h: 40.5% [38.0-43.1]; DOWN baseline 1h: 47.9%, 4h: 48.5% | MATCH |
| 26 | 5m UP/DOWN/BUY (short covering) | `n 1,273 ... 45 % / 45 % against 49 % / 50 %` [SOURCED `RESULT.md:65`, `tables.md:244`] | OURS: n=1,273; cont 1h: 44.9% [42.2-47.7]; cont 4h: 44.9% [42.2-47.7]; UP baseline 1h: 49.3%, 4h: 49.9% | MATCH |
| 27 | 11-04 02:55-03:00 flush reproduction | `close 76,019, OI +381, delta -3,279` [SOURCED `RESULT.md:13`, `walkthrough.md:64`] | OURS: close 76,019; OI chg: +114 + +267 = +381 BTC; delta: -1,970 + -1,308 = -3,278 BTC (1 BTC rounding vs 5m sum -3,279) | MATCH |
| 28 | 11-04 day's low vs flush close | `the 03:05 bar wicks lower, 75,690; 76,019 is the 03:00 bar close ... 329 lower` [SOURCED `RESULT.md:14`, `walkthrough.md:62,66`] | OURS: 76,019 - 75,690 = 329 BTC diff | MATCH |
| 29 | 11-04 14:35-15:10 rally big OI bars | `OI on the four big-OI bars 14:35, 15:00, 15:05, 15:10 = -2,862 ... all 7 bars sum -1,299` [SOURCED `RESULT.md:16`, `walkthrough.md:63,65`] | OURS: -734 + -730 + -536 + -862 = -2,862 BTC; 7 bars sum = -1,299 BTC | MATCH |
| 30 | 11-04 14:40 new-longs bar | `price +0.96 %, OI +207, delta +3,471, story UP/UP/BUY` [SOURCED `RESULT.md:17`, `walkthrough.md:28`] | OURS: price +0.96%, OI +207, delta +3,471 BTC, story UP\|UP\|BUY | MATCH |
| 31 | 11-04 day OI change | `-2,815 (stamps 00:05 to 23:55)` [SOURCED `RESULT.md:18`, `walkthrough.md:67`] | OURS: -2,815 BTC | MATCH |
| 32 | 11-04 top positions ratio | `1.72 -> 1.92` [SOURCED `RESULT.md:19`, `walkthrough.md:68`] | OURS: 1.72 -> 1.92 | MATCH |
| 33 | 11-04 top accounts ratio & global | `2.43 -> 1.48; 2.31 -> 1.39` [SOURCED `RESULT.md:20`, `walkthrough.md:69,70`] | OURS: 2.43 -> 1.48; global: 2.31 -> 1.39 | MATCH |
| 34 | 11-04 weekly streak count | `red weeks 10-05, 10-12, 10-19, 10-26 = 4 ... week of 11-02 ... green` [SOURCED `RESULT.md:21`, `walkthrough.md:12-16`] | OURS: Exactly 4 red weeks (10-05, 10-12, 10-19, 10-26); week of 09-28 was green; week of 11-02 open 78,313, close 80,466 is green | MATCH |
| 35 | 11-04 big hour DEV cell lookups | `02:00 DOWN/DOWN/SELL/BU (n=91: 43/50/45); 04:00 UP/DOWN/BUY/SL/range (n=37: 35/35/49); 14:00 UP/UP/BUY/SL (n=43: 44/56/60); 15:00 UP/DOWN/BUY/SL/range (n=37: 35/35/49)` [SOURCED `RESULT.md:28-34`, `walkthrough.md:76-79`] | OURS: Exactly matches DEV cells in `tables.md:44,64,206` | MATCH |
| 36 | Metrics directory path | `metrics 5m (F:/MTS/data/binance_metrics)` [SOURCED `PRE_REG.md:9`, `study.py:20`] | OURS: Path `F:/MTS/data/binance_metrics` does not exist on disk. Actual path is `F:/MTS/data/metrics/BTCUSDT` (1,762 files) | MISMATCH (Defect: `PRE_REG.md:9`, `study.py:20`) |

---

## 2. Contradictions with PRE_REG.md

A systematic audit of `PRE_REG.md` against `RESULT.md` and `tables.md` was conducted:
1. **Research Question & Non-Trading Nature**: `PRE_REG.md:3,5-7` defined this as descriptive, fee-free, with no trade rule and no costs. `RESULT.md:1,3,5` faithfully reports descriptive base rates without asserting a trading strategy or edge. MATCH.
2. **Data & Window**: `PRE_REG.md:9-10` defined DEV window `2022-01-03 to 2024-06-30` and holdout sealed. `RESULT.md:7` and `tables.md:1` adhered strictly to this window. MATCH.
3. **Bar & Feature Definitions**: `PRE_REG.md:13-14` specified price change $close/open - 1$, OI delta $OI_t - OI_{t-1}$, taker delta $2 \times taker\_buy - volume$, and big threshold $|z| \ge 3.0$ on trailing 30 days prior bars only ($w=720$ for 1h, $w=8640$ for 5m, requiring 80% valid). Recomputation verified this is implemented point-in-time without lookahead. MATCH.
4. **Story Sign Labels**: `PRE_REG.md:15` specified 8 story combinations dropping 0 or missing signs. Exactly 8 combinations were formed. MATCH.
5. **Event Lockout**: `PRE_REG.md:16` specified skipping the next 12 bars for 5m events so 1h outcome windows never overlap. `tables.md:3` and `RESULT.md:7` confirm 12-bar (60-minute) lockout. MATCH.
6. **Top-Trader Classification**: `PRE_REG.md:17` defined 60-minute window relative changes, flat band $|change| < 0.2\%$, and 4 classes: BU, BD, SL, SS. All 4 classes and FLAT/NA handling match. MATCH.
7. **Outcomes Definition**: `PRE_REG.md:18` defined continues (close beyond event close in event direction) and undone (close back past event bar start price) at 1h, 4h, 24h. Outcomes match definition exactly. MATCH.
8. **Phase Splits**: `PRE_REG.md:19` defined weekly streak groups (R3+, R1-2, G1-2, G3+) from Monday 00:00 UTC grid futures 5m bars, and 30-day band ($>+10\%$ bull, $<-10\%$ bear, else range). All split rates match. MATCH.
9. **Wilson 95% Confidence Intervals & THIN**: `PRE_REG.md:20` specified 95% Wilson CI and $n < 30$ marked THIN. MATCH.

**Contradiction Finding**:
There are **zero methodological or definitional contradictions** between `PRE_REG.md` and `RESULT.md`.

---

## 3. Defects Identified

1. **Defect 1 (`RESULT.md:46`)**:
   - Text states: `| the other 3 stories | 10-16 | | | | THIN |`.
   - Reality: There are 8 total stories. The 4 major stories listed above row 46 are UP/UP/BUY (n=180), UP/DOWN/BUY (n=223), DOWN/DOWN/SELL (n=269), and DOWN/UP/SELL (n=117). Row 45 is a subcell (`DOWN/DOWN/SELL x SS`), not a separate story. The remaining stories in `tables.md:30-37` are DOWN|DOWN|BUY (n=16), DOWN|UP|BUY (n=12), UP|DOWN|SELL (n=16), and UP|UP|SELL (n=10).
   - Defect: There are **4** other stories, not 3. The count range (10-16) is correct.
2. **Defect 2 (`PRE_REG.md:9` and `study.py:20`)**:
   - `PRE_REG.md:9` cites `metrics 5m (F:/MTS/data/binance_metrics)`.
   - `study.py:20` hardcodes `METRICS = 'F:/MTS/data/binance_metrics'`.
   - Reality: Directory `F:/MTS/data/binance_metrics` does not exist on disk (superseded per `MyTradingSys/system/DATA_NOTES.md:16`). The actual live metrics files reside in `F:/MTS/data/metrics/BTCUSDT/`. Running `python study.py` as cited in `RESULT.md:3` without aliasing or updating `METRICS` finds 0 metrics rows and fails to reproduce DEV tables.

---

## 4. Conclusion & Final Verdict

- All underlying numbers in `tables.md` (843 1h events, 3,991 5m events, 21,831 baseline 1h bars, 261,310 baseline 5m bars, all 472 lines) reproduce 100% byte-for-byte from raw Binance klines and metrics.
- Every substantive finding in `RESULT.md` holds: continuation remains in the 43-60% range against 45-50% baselines, and the operator's hypothesis regarding top-trader size-long / accounts-short after a big UP candle does not exhibit any edge over baseline.
- Because of Defect 1 (`RESULT.md:46` stating "3 stories" instead of 4) and Defect 2 (`PRE_REG.md:9` and `study.py:20` citing non-existent path `F:/MTS/data/binance_metrics`), strict per-claim matching records these two defects.

VERDICT: MISMATCH
