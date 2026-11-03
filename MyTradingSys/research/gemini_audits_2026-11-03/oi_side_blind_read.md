# FOUND: 103, NOT_IN_DATA: 10, DIFF: 1

# Blind Re-read of oi_side_2026-10-30 RESULT.md Numbers vs output.txt

Audit of every empirical number, count, date, timeframe, percentage, sample size, standard error, and cross-reference in:
- `MyTradingSys/research/oi_side_2026-10-30/RESULT.md`

Cross-checked against:
- `MyTradingSys/research/oi_side_2026-10-30/output.txt`
- `MyTradingSys/research/oi_side_2026-10-30/study.py`

## Summary

- **Total Numbers / Claims Audited**: 114
- **FOUND (Exact match or directly derived from output.txt / study.py)**: 103
- **NOT_IN_DATA (External event prompt context / forward research references)**: 10
- **DIFF (Discrepancy between RESULT.md and output.txt)**: 1 (L67 cites sub-cells holding "39-169 cases", whereas output.txt Table D shows sub-cells holding 39-167 cases)

---

## 1. oi_side_2026-10-30 RESULT.md Audit Table

| Line | Section | Claim / Number | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L1 | Header | Date: 2026-10-30 | `RESULT.md:1` | 2026-10-30 | **FOUND** | `OURS` | Header study date |
| L6 | Data | 5m open interest | `study.py:7` | `5m grid. OI = sum_open_interest` | **FOUND** | `OURS` | 5m aggregation interval |
| L8 | Data | DEV 2022-2025 (start year 2022) | `output.txt:15`, `study.py:6` | `2022` in year columns | **FOUND** | `OURS` | Sample window start |
| L8 | Data | DEV 2022-2025 (end year 2025) | `output.txt:15`, `study.py:6` | `2025` in year columns | **FOUND** | `OURS` | Sample window end |
| L8 | Data | n = 35,963 events | `output.txt:1` | `events 35963` | **FOUND** | `OURS` | Total non-overlapping windows |
| L8 | Data | 30-minute windows | `output.txt:3`, `study.py:8` | `A. OI x price over the last 30 min` | **FOUND** | `OURS` | Window duration (6 x 5m bars) |
| L8 | Data | OI change >= 0.25% threshold | `study.py:9` | `dOI >= .0025 else 'down' if dOI <= -.0025` | **FOUND** | `OURS` | Window filter threshold |
| L10 | Trigger | Shot 072bbb83f7b1 | External event shot | Not in output.txt | **NOT_IN_DATA** | `SOURCED` | Operator's shot id trigger |
| L10 | Trigger | Date 10-29 | External event date | Not in output.txt | **NOT_IN_DATA** | `SOURCED` | Operator's shot timestamp (10-29) |
| L10 | Trigger | Window 23:05-23:38Z | External event time | Not in output.txt | **NOT_IN_DATA** | `SOURCED` | Operator's shot time window |
| L10 | Trigger | 1m resolution | External event timeframe | Not in output.txt | **NOT_IN_DATA** | `SOURCED` | Operator's shot chart timeframe |
| L10 | Trigger | OI from 93.3K | External event data | Not in output.txt | **NOT_IN_DATA** | `SOURCED` | Operator's shot initial OI |
| L10 | Trigger | OI to 93.6K | External event data | Not in output.txt | **NOT_IN_DATA** | `SOURCED` | Operator's shot final OI |
| L10 | Trigger | Price from 78.9k | External event data | Not in output.txt | **NOT_IN_DATA** | `SOURCED` | Operator's shot initial price |
| L10 | Trigger | Price to 78.79k | External event data | Not in output.txt | **NOT_IN_DATA** | `SOURCED` | Operator's shot final price |
| L17 | Sec A | 30 minutes header | `output.txt:3` | `over the last 30 min` | **FOUND** | `OURS` | Table A window |
| L19 | Sec A | 60 min horizon header | `output.txt:4` | `up60` | **FOUND** | `OURS` | 60 min forward horizon |
| L19 | Sec A | 4 h horizon header | `output.txt:4` | `up240` (240 min = 4 h) | **FOUND** | `OURS` | 240 min forward horizon |
| L19 | Sec A | +0.5% first horizon header | `output.txt:4` | `up_first` | **FOUND** | `OURS` | +0.5% barrier hit first |
| L19 | Sec A | -0.5% first horizon header | `output.txt:4` | `down_first` | **FOUND** | `OURS` | -0.5% barrier hit first |
| L21 | Sec A | up up n: 6,193 | `output.txt:11` | `6193` | **FOUND** | `OURS` | Table A row 1 n |
| L21 | Sec A | up up Up 60 min: 48.5% | `output.txt:11` | `0.485` | **FOUND** | `OURS` | Table A row 1 up60 |
| L21 | Sec A | up up Up 4 h: 49.4% | `output.txt:11` | `0.494` | **FOUND** | `OURS` | Table A row 1 up240 |
| L21 | Sec A | up up +0.5% first: 47.9% | `output.txt:11` | `0.479` | **FOUND** | `OURS` | Table A row 1 up_first |
| L21 | Sec A | up up -0.5% first: 43.6% | `output.txt:11` | `0.436` | **FOUND** | `OURS` | Table A row 1 down_first |
| L22 | Sec A | up flat n: 8,023 | `output.txt:10` | `8023` | **FOUND** | `OURS` | Table A row 2 n |
| L22 | Sec A | up flat Up 60 min: 51.3% | `output.txt:10` | `0.513` | **FOUND** | `OURS` | Table A row 2 up60 |
| L22 | Sec A | up flat Up 4 h: 51.0% | `output.txt:10` | `0.510` | **FOUND** | `OURS` | Table A row 2 up240 |
| L22 | Sec A | up flat +0.5% first: 41.9% | `output.txt:10` | `0.419` | **FOUND** | `OURS` | Table A row 2 up_first |
| L22 | Sec A | up flat -0.5% first: 39.3% | `output.txt:10` | `0.393` | **FOUND** | `OURS` | Table A row 2 down_first |
| L23 | Sec A | up down n: 4,985 | `output.txt:9` | `4985` | **FOUND** | `OURS` | Table A row 3 n |
| L23 | Sec A | up down Up 60 min: 52.7% | `output.txt:9` | `0.527` | **FOUND** | `OURS` | Table A row 3 up60 |
| L23 | Sec A | up down Up 4 h: 52.8% | `output.txt:9` | `0.528` | **FOUND** | `OURS` | Table A row 3 up240 |
| L23 | Sec A | up down +0.5% first: 43.5% | `output.txt:9` | `0.435` | **FOUND** | `OURS` | Table A row 3 up_first |
| L23 | Sec A | up down -0.5% first: 48.8% | `output.txt:9` | `0.488` | **FOUND** | `OURS` | Table A row 3 down_first |
| L24 | Sec A | down up n: 5,428 | `output.txt:8` | `5428` | **FOUND** | `OURS` | Table A row 4 n |
| L24 | Sec A | down up Up 60 min: 48.9% | `output.txt:8` | `0.489` | **FOUND** | `OURS` | Table A row 4 up60 |
| L24 | Sec A | down up Up 4 h: 49.0% | `output.txt:8` | `0.490` | **FOUND** | `OURS` | Table A row 4 up240 |
| L24 | Sec A | down up +0.5% first: 45.9% | `output.txt:8` | `0.459` | **FOUND** | `OURS` | Table A row 4 up_first |
| L24 | Sec A | down up -0.5% first: 43.3% | `output.txt:8` | `0.433` | **FOUND** | `OURS` | Table A row 4 down_first |
| L25 | Sec A | down flat n: 5,038 | `output.txt:7` | `5038` | **FOUND** | `OURS` | Table A row 5 n |
| L25 | Sec A | down flat Up 60 min: 49.7% | `output.txt:7` | `0.497` | **FOUND** | `OURS` | Table A row 5 up60 |
| L25 | Sec A | down flat Up 4 h: 51.0% | `output.txt:7` | `0.510` | **FOUND** | `OURS` | Table A row 5 up240 |
| L25 | Sec A | down flat +0.5% first: 37.5% | `output.txt:7` | `0.375` | **FOUND** | `OURS` | Table A row 5 up_first |
| L25 | Sec A | down flat -0.5% first: 41.3% | `output.txt:7` | `0.413` | **FOUND** | `OURS` | Table A row 5 down_first |
| L26 | Sec A | down down n: 6,296 | `output.txt:6` | `6296` | **FOUND** | `OURS` | Table A row 6 n |
| L26 | Sec A | down down Up 60 min: 53.5% | `output.txt:6` | `0.535` | **FOUND** | `OURS` | Table A row 6 up60 |
| L26 | Sec A | down down Up 4 h: 53.4% | `output.txt:6` | `0.534` | **FOUND** | `OURS` | Table A row 6 up240 |
| L26 | Sec A | down down +0.5% first: 43.3% | `output.txt:6` | `0.433` | **FOUND** | `OURS` | Table A row 6 up_first |
| L26 | Sec A | down down -0.5% first: 46.7% | `output.txt:6` | `0.467` | **FOUND** | `OURS` | Table A row 6 down_first |
| L29 | Reading | Direction bounds: 48% and 54% | `output.txt:6-11` | min up60 = 0.485 (48.5%), max up60 = 0.535 (53.5%) | **FOUND** | `OURS` | Span of up60 across all Table A cells |
| L30 | Reading | Lean against push: 48.5% and 52.7% | `output.txt:9, 11` | up up up60 = 0.485, up down up60 = 0.527 | **FOUND** | `OURS` | Quoted Table A cells |
| L30 | Reading | Gap of about 4 points | `output.txt:9, 11` | 52.7% - 48.5% = 4.2 pp | **FOUND** | `OURS` | Difference between cells |
| L30 | Reading | About 6 standard errors | `output.txt:9, 11` | Single cell SE = sqrt(0.5*0.5/6193) = 0.64 pp; 4.2 / 0.64 ~= 6.5 SE | **FOUND** | `OURS` | Standard error scaling |
| L34 | Sec A2 | 60 minutes horizon | `output.txt:13` | `up 60 min later, by year` | **FOUND** | `OURS` | Horizon definition |
| L34 | Sec A2 | n per cell min: 842 | `output.txt:20` | `842` (up down 2025 size) | **FOUND** | `OURS` | Minimum cell count in A-year |
| L34 | Sec A2 | n per cell max: 2,817 | `output.txt:21` | `2817` (up flat 2023 size) | **FOUND** | `OURS` | Maximum cell count in A-year |
| L34 | Sec A2 | SE range: 1.0-1.7 points | `output.txt:17-22` | sqrt(0.25/2817) = 0.94 pp (~1.0), sqrt(0.25/842) = 1.72 pp (~1.7) | **FOUND** | `OURS` | Standard error bounds |
| L36 | Sec A2 | Table years: 2022, 2023, 2024, 2025 | `output.txt:15` | `2022   2023   2024   2025` | **FOUND** | `OURS` | Table header years |
| L38 | Sec A2 | short covering (down up): 44% (2022) | `output.txt:19` | `0.442` (rounds to 44%) | **FOUND** | `OURS` | Table A-year row down up |
| L38 | Sec A2 | short covering (down up): 48% (2023) | `output.txt:19` | `0.475` (rounds to 48%) | **FOUND** | `OURS` | Table A-year row down up |
| L38 | Sec A2 | short covering (down up): 52% (2024) | `output.txt:19` | `0.521` (rounds to 52%) | **FOUND** | `OURS` | Table A-year row down up |
| L38 | Sec A2 | short covering (down up): 55% (2025) | `output.txt:19` | `0.549` (rounds to 55%) | **FOUND** | `OURS` | Table A-year row down up |
| L39 | Sec A2 | long liquidation (down down): 54% (2022) | `output.txt:17` | `0.541` (rounds to 54%) | **FOUND** | `OURS` | Table A-year row down down |
| L39 | Sec A2 | long liquidation (down down): 58% (2023) | `output.txt:17` | `0.581` (rounds to 58%) | **FOUND** | `OURS` | Table A-year row down down |
| L39 | Sec A2 | long liquidation (down down): 53% (2024) | `output.txt:17` | `0.529` (rounds to 53%) | **FOUND** | `OURS` | Table A-year row down down |
| L39 | Sec A2 | long liquidation (down down): 48% (2025) | `output.txt:17` | `0.481` (rounds to 48%) | **FOUND** | `OURS` | Table A-year row down down |
| L40 | Sec A2 | shorts pressing (up down): 52% (2022) | `output.txt:20` | `0.524` (rounds to 52%) | **FOUND** | `OURS` | Table A-year row up down |
| L40 | Sec A2 | shorts pressing (up down): 55% (2023) | `output.txt:20` | `0.551` (rounds to 55%) | **FOUND** | `OURS` | Table A-year row up down |
| L40 | Sec A2 | shorts pressing (up down): 53% (2024) | `output.txt:20` | `0.529` (rounds to 53%) | **FOUND** | `OURS` | Table A-year row up down |
| L40 | Sec A2 | shorts pressing (up down): 50% (2025) | `output.txt:20` | `0.496` (rounds to 50%) | **FOUND** | `OURS` | Table A-year row up down |
| L41 | Sec A2 | build-up (up flat): 52% (2022) | `output.txt:21` | `0.518` (rounds to 52%) | **FOUND** | `OURS` | Table A-year row up flat |
| L41 | Sec A2 | build-up (up flat): 52% (2023) | `output.txt:21` | `0.516` (rounds to 52%) | **FOUND** | `OURS` | Table A-year row up flat |
| L41 | Sec A2 | build-up (up flat): 50% (2024) | `output.txt:21` | `0.499` (rounds to 50%) | **FOUND** | `OURS` | Table A-year row up flat |
| L41 | Sec A2 | build-up (up flat): 52% (2025) | `output.txt:21` | `0.519` (rounds to 52%) | **FOUND** | `OURS` | Table A-year row up flat |
| L42 | Sec A2 | longs pressing (up up): 49% (2022) | `output.txt:22` | `0.494` (rounds to 49%) | **FOUND** | `OURS` | Table A-year row up up |
| L42 | Sec A2 | longs pressing (up up): 47% (2023) | `output.txt:22` | `0.466` (rounds to 47%) | **FOUND** | `OURS` | Table A-year row up up |
| L42 | Sec A2 | longs pressing (up up): 49% (2024) | `output.txt:22` | `0.485` (rounds to 49%) | **FOUND** | `OURS` | Table A-year row up up |
| L42 | Sec A2 | longs pressing (up up): 50% (2025) | `output.txt:22` | `0.496` (rounds to 50%) | **FOUND** | `OURS` | Table A-year row up up |
| L46 | Reading | Short covering 2022: 44% up | `output.txt:19` | `0.442` | **FOUND** | `OURS` | Reading bullet text |
| L46 | Reading | Short covering 2024-25: 52-55% | `output.txt:19` | `0.521` (2024) and `0.549` (2025) | **FOUND** | `OURS` | Reading bullet text |
| L46 | Reading | 11-point swing | `output.txt:19` | 54.9% - 44.2% = 10.7 pp (~11 points) | **FOUND** | `OURS` | Difference between 2025 and 2022 |
| L46 | Reading | About 5 standard errors | `output.txt:19` | SE of diff: sqrt(0.0119^2 + 0.0166^2) = 0.0204 (2.04 pp); 10.7 / 2.04 = 5.24 SE | **FOUND** | `OURS` | SE of difference |
| L47 | Reading | Long liquidations bounced 2023: 58% | `output.txt:17` | `0.581` | **FOUND** | `OURS` | Reading bullet text |
| L47 | Reading | Long liquidations 2025: 48% | `output.txt:17` | `0.481` | **FOUND** | `OURS` | Reading bullet text |
| L48 | Reading | Build-ups 50/50 | `output.txt:21` | 51.8%, 51.6%, 49.9%, 51.9% | **FOUND** | `OURS` | Reading bullet text |
| L49 | Reading | 20-day mean cycle definition | `output.txt:26`, `study.py:22` | `above 20d mean below 20d mean` | **FOUND** | `OURS` | Moving average window |
| L49 | Reading | At most 3.6 points between halves | `output.txt:28-33` | Max gap in A-cycle: down down (0.554 - 0.518 = 0.036 = 3.6 points) | **FOUND** | `OURS` | Table A-cycle max spread |
| L56 | Sec B | buyers (share >= +0.05) threshold | `study.py:34` | `R['delta'] = np.where(..., np.where(R.ds >= .05, 'buyers', ...))` | **FOUND** | `OURS` | Delta threshold for buyers |
| L56 | Sec B | buyers n: 2,035 | `output.txt:38` | `2035` | **FOUND** | `OURS` | Table B row 1 n |
| L56 | Sec B | buyers Up 60 min: 49.4% | `output.txt:38` | `0.494` | **FOUND** | `OURS` | Table B row 1 up60 |
| L56 | Sec B | buyers +0.5% first: 40.9% | `output.txt:38` | `0.409` | **FOUND** | `OURS` | Table B row 1 up_first |
| L56 | Sec B | buyers -0.5% first: 36.1% | `output.txt:38` | `0.361` | **FOUND** | `OURS` | Table B row 1 down_first |
| L57 | Sec B | mixed n: 3,765 | `output.txt:39` | `3765` | **FOUND** | `OURS` | Table B row 2 n |
| L57 | Sec B | mixed Up 60 min: 51.6% | `output.txt:39` | `0.516` | **FOUND** | `OURS` | Table B row 2 up60 |
| L57 | Sec B | mixed +0.5% first: 44.5% | `output.txt:39` | `0.445` | **FOUND** | `OURS` | Table B row 2 up_first |
| L57 | Sec B | mixed -0.5% first: 41.2% | `output.txt:39` | `0.412` | **FOUND** | `OURS` | Table B row 2 down_first |
| L58 | Sec B | sellers (share <= -0.05) threshold | `study.py:34` | `np.where(R.ds <= -.05, 'sellers', ...)` | **FOUND** | `OURS` | Delta threshold for sellers |
| L58 | Sec B | sellers n: 2,223 | `output.txt:40` | `2223` | **FOUND** | `OURS` | Table B row 3 n |
| L58 | Sec B | sellers Up 60 min: 52.6% | `output.txt:40` | `0.526` | **FOUND** | `OURS` | Table B row 3 up60 |
| L58 | Sec B | sellers +0.5% first: 38.3% | `output.txt:40` | `0.383` | **FOUND** | `OURS` | Table B row 3 up_first |
| L58 | Sec B | sellers -0.5% first: 39.0% | `output.txt:40` | `0.390` | **FOUND** | `OURS` | Table B row 3 down_first |
| L61 | Bullets | Next +-0.5% barrier: 38% up first vs 39% down first | `output.txt:40` | `0.383` (38.3% -> 38%), `0.390` (39.0% -> 39%) | **FOUND** | `OURS` | Table B sellers outcome |
| L61 | Bullets | About 23% reached neither | `output.txt:40` | 1 - (0.383 + 0.390) = 0.227 = 22.7% (~23%) | **FOUND** | `OURS` | Table B sellers neither share |
| L61 | Bullets | Within 4 hours | `output.txt:4`, `study.py:10` | 48 bars = 240 min = 4 hours | **FOUND** | `OURS` | Outcome window horizon |
| L66 | Sec C/D | Ratio moved > 1% threshold | `study.py:35` | `np.where(R.tt > 0.01, ..., np.where(R.tt < -0.01, ...))` | **FOUND** | `OURS` | Top-trader ratio change filter |
| L66 | Sec C/D | In only about 6% of build-ups | `output.txt:10, 46, 47` | (133 + 379) / 8023 = 512 / 8023 = 0.0638 (6.38% ~= 6%) | **FOUND** | `OURS` | Share of active top-trader changes |
| L66 | Sec C/D | n = 133 (top longs grew) | `output.txt:46` | `133` | **FOUND** | `OURS` | Table C top longs grew n |
| L66 | Sec C/D | n = 379 (top shorts grew) | `output.txt:47` | `379` | **FOUND** | `OURS` | Table C top shorts grew n |
| L67 | Sec C/D | Sub-cells hold 39-169 cases | `output.txt:53, 54, 56, 57, 59, 60` | Sub-cells in Table D with moved ratio hold 41, 87, 53, 167, 39, 125 cases (range: 39-167) | **DIFF** | `OURS` | RESULT.md states 39-169, but output.txt Table D shows max sub-cell count is 167 (mixed x top shorts grew) |
| L67 | Sec C/D | Sellers with top longs growing: 72% up | `output.txt:59` | `0.718` (rounds to 72%) | **FOUND** | `OURS` | Table D sellers x top longs grew up60 |
| L67 | Sec C/D | Sellers with top longs growing: n = 39 | `output.txt:59` | `39` | **FOUND** | `OURS` | Table D sellers x top longs grew n |
| L74 | Extends | U2 in CARD_SPECS.md | Research card reference | Not in output.txt | **NOT_IN_DATA** | `SOURCED` | Task spec reference |
| L75 | Task | `cvd-coil-and-absorption-u7-u8` | Task card reference | Not in output.txt | **NOT_IN_DATA** | `SOURCED` | Successor card reference |
