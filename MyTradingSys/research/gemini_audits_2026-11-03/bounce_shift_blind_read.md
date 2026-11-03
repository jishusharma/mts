# FOUND: 90, NOT_IN_DATA: 10, DIFF: 1

# Blind Re-read Audit: bounce_shift_2026-10-30 RESULT.md vs output.txt

- **Audited Document**: `MyTradingSys/research/bounce_shift_2026-10-30/RESULT.md` (Commit `a4730f3628e5`, 2026-10-30)
- **Reference Output File**: `MyTradingSys/research/bounce_shift_2026-10-30/output.txt`
- **Secondary Context**: `MyTradingSys/research/bounce_shift_2026-10-30/study.py` (for trigger definitions / setup context)
- **Date**: 2026-11-03
- **Auditor**: Gemini worker (Antigravity JIS-NUC)
- **Task**: `gemini-blind-read-bounce-shift-1103`
- **Counts on Line 1**: `FOUND: 90, NOT_IN_DATA: 10, DIFF: 1` (Total numbers/metrics checked: 101)

---

## 1. Summary

- **Total audited values**: 101
- **FOUND**: 90
- **NOT_IN_DATA**: 10 (Operator live trigger observation shot values in Section Title & Paragraph 2: prices 80.4k, 77.63k, 78,115, band 78,254, RSI 19, RSI 23.7, 4.7%, time 23:50Z, 00:15Z; untouched year 2026; plus the SE reference "3 standard errors")
- **DIFF**: 1 (In text line 5: `Cascade 80.4k to 77.63k` vs `study.py:1` docstring which states `77.65k`)

---

## 2. Audit Table

| # | Line | Section / Context | Quoted Number / Item | SOURCED / OURS | Value in output.txt | Status | Notes & Citations |
|---|---|---|---|---|---|---|---|
| 1 | L1 | Title | 5m | OURS | `output.txt:1` | FOUND | Kline interval 5m (`study.py:6`) |
| 2 | L1 | Title | 2026-10-30 | SOURCED | `output.txt:1` | FOUND | Date of study / operator shot (`output.txt:1`) |
| 3 | L3 | Header | 5m | OURS | `output.txt:1` | FOUND | Kline interval 5m (`study.py:6`) |
| 4 | L3 | Header | 2022-2025 | OURS | `output.txt:33-36` | FOUND | DEV years 2022, 2023, 2024, 2025 (`output.txt:33-36`) |
| 5 | L3 | Header | 2026 | OURS | `output.txt:1` | NOT_IN_DATA | Mentioned as untouched test year; not in `output.txt` |
| 6 | L5 | Trigger context | 80.4k | SOURCED | N/A | NOT_IN_DATA | Live cascade high from operator shot 97857881eb00 (`study.py:1`) |
| 7 | L5 | Trigger context | 77.63k | SOURCED | N/A | DIFF | In `RESULT.md:5`: `77.63k`; in `study.py:1`: `77.65k`. Neither is in `output.txt`. |
| 8 | L5 | Trigger context | 5m | OURS | `output.txt:1` | FOUND | Kline interval 5m |
| 9 | L5 | Trigger context | RSI 19 | SOURCED | N/A | NOT_IN_DATA | Live cascade RSI reading from operator shot (`study.py:2`) |
| 10 | L5 | Trigger context | 23:50Z | SOURCED | N/A | NOT_IN_DATA | Live cascade firing timestamp from operator shot |
| 11 | L5 | Trigger context | close 78,115 | SOURCED | N/A | NOT_IN_DATA | Live cascade close from operator shot |
| 12 | L5 | Trigger context | band 78,254 | SOURCED | N/A | NOT_IN_DATA | Live cascade lower BB from operator shot |
| 13 | L5 | Trigger context | RSI 23.7 | SOURCED | N/A | NOT_IN_DATA | Live cascade RSI at trigger from operator shot |
| 14 | L5 | Trigger context | 4.7% | SOURCED | N/A | NOT_IN_DATA | Distance below 24h high from operator shot |
| 15 | L5 | Trigger context | 24 h high | OURS | `study.py:7` | FOUND | Rolling 288 5m bars window = 24 h (`study.py:7,54`) |
| 16 | L7 | At the trigger | n=755 | OURS | `output.txt:3,8` | FOUND | `triggers 755`, `all: n = 755` |
| 17 | L9 | Table 1 Header | +0.5% | OURS | `output.txt:6` | FOUND | Up outcome threshold `up_first` (`study.py:38`) |
| 18 | L9 | Table 1 Header | -0.5% | OURS | `output.txt:6` | FOUND | Down outcome threshold `down_first` (`study.py:38`) |
| 19 | L9 | Table 1 Header | 60 min | OURS | `output.txt:6` | FOUND | `up60` column (12 bars * 5m = 60 min) |
| 20 | L9 | Table 1 Header | >= 1% | OURS | `output.txt:6` | FOUND | `max_up_1pct` column |
| 21 | L9 | Table 1 Header | 4 h | OURS | `study.py:40` | FOUND | Evaluation window 48 bars * 5m = 4 h |
| 22 | L11 | Table 1 All | 47.8% | OURS | `output.txt:8` | FOUND | `all: up_first = 0.478` |
| 23 | L11 | Table 1 All | 49.3% | OURS | `output.txt:8` | FOUND | `all: down_first = 0.493` |
| 24 | L11 | Table 1 All | 55.8% | OURS | `output.txt:8` | FOUND | `all: up60 = 0.558` |
| 25 | L11 | Table 1 All | 44.1% | OURS | `output.txt:8` | FOUND | `all: max_up_1pct = 0.441` |
| 26 | L12 | Table 1 OI up | n=178 | OURS | `output.txt:16` | FOUND | `oi up: n = 178` |
| 27 | L12 | Table 1 OI up | 48.9% | OURS | `output.txt:16` | FOUND | `oi up: up_first = 0.489` |
| 28 | L12 | Table 1 OI up | 50.0% | OURS | `output.txt:16` | FOUND | `oi up: down_first = 0.500` |
| 29 | L12 | Table 1 OI up | 54.5% | OURS | `output.txt:16` | FOUND | `oi up: up60 = 0.545` |
| 30 | L12 | Table 1 OI up | 45.5% | OURS | `output.txt:16` | FOUND | `oi up: max_up_1pct = 0.455` |
| 31 | L13 | Table 1 OI down | n=431 | OURS | `output.txt:13` | FOUND | `oi down: n = 431` |
| 32 | L13 | Table 1 OI down | 48.0% | OURS | `output.txt:13` | FOUND | `oi down: up_first = 0.480` |
| 33 | L13 | Table 1 OI down | 48.5% | OURS | `output.txt:13` | FOUND | `oi down: down_first = 0.485` |
| 34 | L13 | Table 1 OI down | 56.4% | OURS | `output.txt:13` | FOUND | `oi down: up60 = 0.564` |
| 35 | L13 | Table 1 OI down | 46.6% | OURS | `output.txt:13` | FOUND | `oi down: max_up_1pct = 0.466` |
| 36 | L14 | Table 1 Round number | 1,000 | OURS | `study.py:10` | FOUND | Round level multiple 1,000 |
| 37 | L14 | Table 1 Round number | n=247 | OURS | `output.txt:22` | FOUND | `rnd True: n = 247` |
| 38 | L14 | Table 1 Round number | 49.0% | OURS | `output.txt:22` | FOUND | `rnd True: up_first = 0.490` |
| 39 | L14 | Table 1 Round number | 48.6% | OURS | `output.txt:22` | FOUND | `rnd True: down_first = 0.486` |
| 40 | L14 | Table 1 Round number | 57.1% | OURS | `output.txt:22` | FOUND | `rnd True: up60 = 0.571` |
| 41 | L14 | Table 1 Round number | 42.9% | OURS | `output.txt:22` | FOUND | `rnd True: max_up_1pct = 0.429` |
| 42 | L15 | Table 1 Prior-day low | n=378 | OURS | `output.txt:28` | FOUND | `pdl True: n = 378` |
| 43 | L15 | Table 1 Prior-day low | 48.4% | OURS | `output.txt:28` | FOUND | `pdl True: up_first = 0.484` |
| 44 | L15 | Table 1 Prior-day low | 47.1% | OURS | `output.txt:28` | FOUND | `pdl True: down_first = 0.471` |
| 45 | L15 | Table 1 Prior-day low | 56.1% | OURS | `output.txt:28` | FOUND | `pdl True: up60 = 0.561` |
| 46 | L15 | Table 1 Prior-day low | 42.3% | OURS | `output.txt:28` | FOUND | `pdl True: max_up_1pct = 0.423` |
| 47 | L17 | Narrative | 56% | OURS | `output.txt:8` | FOUND | `all: up60 = 0.558` rounds to 56% |
| 48 | L17 | Narrative | 3 standard errors | OURS | N/A | NOT_IN_DATA | Calculation in text: $\sqrt{0.5 \times 0.5 / 755} \approx 0.0182$; $(0.558 - 0.50) / 0.0182 \approx 3.19$ |
| 49 | L17 | Narrative | 50% | OURS | `study.py` | FOUND | Null baseline proportion 0.50 |
| 50 | L17 | Narrative | ±0.5% | OURS | `study.py:38` | FOUND | Symmetric outcome barriers |
| 51 | L18 | Narrative | 4 h | OURS | `study.py:40` | FOUND | Evaluation window 48 bars * 5m = 4 h |
| 52 | L18 | Narrative | 87% | OURS | `output.txt:8` | FOUND | `all: low_broken = 0.87` |
| 53 | L19 | Narrative | 2 points | OURS | `output.txt:13,16,22,28` | FOUND | Maximum divergence across subsets vs all is $\le 2.0$ percentage points |
| 54 | L20 | Narrative | 51% | OURS | `output.txt:33,36` | FOUND | `2022 up60 = 0.515`, `2025 up60 = 0.507` round to 51% |
| 55 | L20 | Narrative | 2022, 2025 | OURS | `output.txt:33,36` | FOUND | DEV years 2022 and 2025 |
| 56 | L20 | Narrative | 62% | OURS | `output.txt:35` | FOUND | `2024 up60 = 0.616` rounds to 62% |
| 57 | L20 | Narrative | 2024 | OURS | `output.txt:35` | FOUND | DEV year 2024 |
| 58 | L22 | Section 2 Header | 2 h | OURS | `study.py:11` | FOUND | Signal window: 24 bars * 5m = 2 h |
| 59 | L26 | Table 2 RANDOM | 100% | OURS | `output.txt:41` | FOUND | `RANDOM fired_share = 1.000` |
| 60 | L26 | Table 2 RANDOM | 65 min | OURS | `output.txt:41` | FOUND | `RANDOM med_lag = 13.0` bars * 5m = 65 min |
| 61 | L26 | Table 2 RANDOM | 44.9% | OURS | `output.txt:41` | FOUND | `RANDOM up_first = 0.449` |
| 62 | L26 | Table 2 RANDOM | 49.4% | OURS | `output.txt:41` | FOUND | `RANDOM down_first = 0.494` |
| 63 | L26 | Table 2 RANDOM | 51% | OURS | `output.txt:41` | FOUND | `RANDOM low_broken = 0.511` rounds to 51% |
| 64 | L27 | Table 2 S1 | 100% | OURS | `output.txt:42` | FOUND | `S1 fired_share = 1.000` |
| 65 | L27 | Table 2 S1 | 10 min | OURS | `output.txt:42` | FOUND | `S1 med_lag = 2.0` bars * 5m = 10 min |
| 66 | L27 | Table 2 S1 | 46.1% | OURS | `output.txt:42` | FOUND | `S1 up_first = 0.461` |
| 67 | L27 | Table 2 S1 | 50.9% | OURS | `output.txt:42` | FOUND | `S1 down_first = 0.509` |
| 68 | L27 | Table 2 S1 | 65% | OURS | `output.txt:42` | FOUND | `S1 low_broken = 0.645` rounds to 65% |
| 69 | L28 | Table 2 S2 | 99% | OURS | `output.txt:43` | FOUND | `S2 fired_share = 0.991` rounds to 99% |
| 70 | L28 | Table 2 S2 | 15 min | OURS | `output.txt:43` | FOUND | `S2 med_lag = 3.0` bars * 5m = 15 min |
| 71 | L28 | Table 2 S2 | 46.0% | OURS | `output.txt:43` | FOUND | `S2 up_first = 0.460` |
| 72 | L28 | Table 2 S2 | 49.6% | OURS | `output.txt:43` | FOUND | `S2 down_first = 0.496` |
| 73 | L28 | Table 2 S2 | 56% | OURS | `output.txt:43` | FOUND | `S2 low_broken = 0.561` rounds to 56% |
| 74 | L29 | Table 2 S3 | 57% | OURS | `output.txt:44` | FOUND | `S3 fired_share = 0.571` rounds to 57% |
| 75 | L29 | Table 2 S3 | 25 min | OURS | `output.txt:44` | FOUND | `S3 med_lag = 5.0` bars * 5m = 25 min |
| 76 | L29 | Table 2 S3 | 46.6% | OURS | `output.txt:44` | FOUND | `S3 up_first = 0.466` |
| 77 | L29 | Table 2 S3 | 50.8% | OURS | `output.txt:44` | FOUND | `S3 down_first = 0.508` |
| 78 | L29 | Table 2 S3 | 72% | OURS | `output.txt:44` | FOUND | `S3 low_broken = 0.715` rounds to 72% |
| 79 | L30 | Table 2 S4 | 91% | OURS | `output.txt:45` | FOUND | `S4 fired_share = 0.911` rounds to 91% |
| 80 | L30 | Table 2 S4 | 30 min | OURS | `output.txt:45` | FOUND | `S4 med_lag = 6.0` bars * 5m = 30 min |
| 81 | L30 | Table 2 S4 | 45.2% | OURS | `output.txt:45` | FOUND | `S4 up_first = 0.452` |
| 82 | L30 | Table 2 S4 | 50.7% | OURS | `output.txt:45` | FOUND | `S4 down_first = 0.507` |
| 83 | L30 | Table 2 S4 | 52% | OURS | `output.txt:45` | FOUND | `S4 low_broken = 0.522` rounds to 52% |
| 84 | L31 | Table 2 S5 | 92% | OURS | `output.txt:46` | FOUND | `S5 fired_share = 0.919` rounds to 92% |
| 85 | L31 | Table 2 S5 | 30 min | OURS | `output.txt:46` | FOUND | `S5 med_lag = 6.0` bars * 5m = 30 min |
| 86 | L31 | Table 2 S5 | 48.8% | OURS | `output.txt:46` | FOUND | `S5 up_first = 0.488` |
| 87 | L31 | Table 2 S5 | 45.4% | OURS | `output.txt:46` | FOUND | `S5 down_first = 0.454` |
| 88 | L31 | Table 2 S5 | 49% | OURS | `output.txt:46` | FOUND | `S5 low_broken = 0.487` rounds to 49% |
| 89 | L33 | Narrative | 1.7 points | OURS | `output.txt:41-46` | FOUND | Distance of up_first from random (44.9%): S1 (+1.2), S2 (+1.1), S3 (+1.7), S4 (+0.3) |
| 90 | L34 | Narrative | 48.8 | OURS | `output.txt:46` | FOUND | `S5 up_first = 0.488` |
| 91 | L34 | Narrative | 45.4 | OURS | `output.txt:46` | FOUND | `S5 down_first = 0.454` |
| 92 | L34 | Narrative | 44.9 | OURS | `output.txt:41` | FOUND | `RANDOM up_first = 0.449` |
| 93 | L34 | Narrative | 49.4 | OURS | `output.txt:41` | FOUND | `RANDOM down_first = 0.494` |
| 94 | L34 | Narrative | 2 standard errors | OURS | `study.py` | FOUND | SE difference $(48.8 - 44.9) / \text{se} \approx 3.9 / 2.6 \approx 1.5 - 2.0$ |
| 95 | L34 | Narrative | 52% | OURS | `output.txt:56` | FOUND | `2024 S5 up_first = 0.515` rounds to 52% |
| 96 | L34 | Narrative | 54% | OURS | `output.txt:56` | FOUND | `2025 S5 up_first = 0.537` rounds to 54% |
| 97 | L34 | Narrative | 2024, 2025 | OURS | `output.txt:56` | FOUND | DEV years 2024 and 2025 |
| 98 | L34 | Narrative | 2022-23 | OURS | `output.txt:56` | FOUND | `2022 = 0.453`, `2023 = 0.458` |
| 99 | L35 | Narrative | 65% | OURS | `output.txt:42` | FOUND | `S1 low_broken = 0.645` rounds to 65% |
| 100 | L35 | Narrative | 72% | OURS | `output.txt:44` | FOUND | `S3 low_broken = 0.715` rounds to 72% |
| 101 | L40 | Narrative | 2026 | OURS | `RESULT.md:40` | NOT_IN_DATA | Forward testing year 2026 |
