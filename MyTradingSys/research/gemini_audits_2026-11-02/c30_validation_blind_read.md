# FOUND: 71, NOT_IN_DATA: 0, DIFF: 0

# Blind Re-read of eagle_eyes_picture C30_VALIDATION.md Numbers vs c30_validation.py

Audit of every empirical number, date, timeframe, bar count, percentage, confidence interval, p-value, and section reference in:
- `MyTradingSys/research/eagle_eyes_picture_2026-10-28/C30_VALIDATION.md`

Cross-checked against:
- `MyTradingSys/research/eagle_eyes_picture_2026-10-28/c30_validation.py`
- `MyTradingSys/research/eagle_eyes_picture_2026-10-28/c30_validation_verdict.json`
- `MyTradingSys/research/eagle_eyes_picture_2026-10-28/PRE_REG_C30.md`
- Git commit repository history (commit `bb124f5cd`)

## Summary

- **Total Numbers / Claims Audited**: 71
- **FOUND (Exact match in cited source / machine-generated data)**: 71
- **NOT_IN_DATA**: 0
- **DIFF (Discrepancy between text and cited source)**: 0

---

## 1. C30_VALIDATION.md Audit Table

| Line | Section | Claim / Number | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L1 | Header | "C30" (Study identifier) | `PRE_REG_C30.md:1`, `c30_validation.py:1` | `C30` | **FOUND** | `OURS` | Quote: `"C30 VALIDATION read"` (`C30_VALIDATION.md:1`) |
| L1 | Header | "2024-07-01" (Window start date) | `c30_validation.py:10`, `c30_validation_verdict.json:3` | `START = MS(2024, 7, 1)`, `"window": "2024-07-01..2025-06-30"` | **FOUND** | `OURS` | Quote: `"(2024-07-01..2025-06-30)"` (`C30_VALIDATION.md:1`) |
| L1 | Header | "2025-06-30" (Window end date) | `c30_validation.py:10`, `c30_validation_verdict.json:3` | `END = MS(2025, 7, 1)` (exclusive: bars to 2025-06-30 23:55 UTC) | **FOUND** | `OURS` | Quote: `"(2024-07-01..2025-06-30)"` (`C30_VALIDATION.md:1`) |
| L1 | Header | "30" in "PRE_REG_C30.md" | `PRE_REG_C30.md:1` | `PRE_REG_C30.md` | **FOUND** | `OURS` | Quote: `"pre-registered in PRE_REG_C30.md"` (`C30_VALIDATION.md:1`) |
| L1 | Header | "bb124f5cd" (Pre-registration commit) | `git rev-parse bb124f5cd` | `bb124f5cdc7ed63042843f19996e409fb33f9aef` | **FOUND** | `FACT` | Quote: `"commit bb124f5cd, earlier than this file"` (`C30_VALIDATION.md:1`). Committed 2026-10-31 22:30:10 UTC |
| L3 | Data | "30" in "c30_validation.py" | `c30_validation.py:1` | `c30_validation.py` | **FOUND** | `OURS` | Quote: `"Script c30_validation.py"` (`C30_VALIDATION.md:3`) |
| L3 | Data | "5m" (Binance kline interval) | `c30_validation.py:19` | `interval=5m` | **FOUND** | `FACT` | Quote: `"Binance spot BTCUSDT 5m, public"` (`C30_VALIDATION.md:3`) |
| L3 | Data | "2024-04-01" (Warm-up start date) | `c30_validation.py:10` | `WARM = MS(2024, 4, 1)` | **FOUND** | `OURS` | Quote: `"warm-up from 2024-04-01"` (`C30_VALIDATION.md:3`) |
| L3 | Data | "2025-07-01" (Fetch stop / HOLDOUT boundary) | `c30_validation.py:10` | `END = MS(2025, 7, 1)` | **FOUND** | `OURS` | Quote: `"fetch stops before 2025-07-01 (HOLDOUT never requested)"` (`C30_VALIDATION.md:3`) |
| L4 | Preflight | "1" in "P1 coverage" | `c30_validation.py:66, 69` | `P1 coverage %s` | **FOUND** | `OURS` | Quote: `"P1 coverage"` (`C30_VALIDATION.md:4`) |
| L4 | Preflight | "30m" chart timeframe (P1) | `c30_validation.py:67, 69` | `tf == "30m"` | **FOUND** | `OURS` | Quote: `"30m 21888/21888"` (`C30_VALIDATION.md:4`) |
| L4 | Preflight | "21888/21888" (30m bar coverage) | `c30_validation.py:68-69` | 456 days * 48 bars/day = 21,888 bars | **FOUND** | `OURS` | Quote: `"21888/21888"` (`C30_VALIDATION.md:4`) |
| L4 | Preflight | "15m" chart timeframe (P1) | `c30_validation.py:67, 69` | `tf == "15m"` | **FOUND** | `OURS` | Quote: `"15m 43776/43776"` (`C30_VALIDATION.md:4`) |
| L4 | Preflight | "43776/43776" (15m bar coverage) | `c30_validation.py:68-69` | 456 days * 96 bars/day = 43,776 bars | **FOUND** | `OURS` | Quote: `"43776/43776"` (`C30_VALIDATION.md:4`) |
| L4 | Preflight | "2" in "P2b prefix" | `c30_validation.py:66, 77` | `P2b prefix %s` | **FOUND** | `OURS` | Quote: `"P2b prefix"` (`C30_VALIDATION.md:4`) |
| L4 | Preflight | "0/15" cuts differ | `c30_validation.py:71, 77` | `cuts = 15; bad == 0` | **FOUND** | `OURS` | Quote: `"0/15 cuts differ, both charts"` (`C30_VALIDATION.md:4`) |
| L4 | Preflight | "6" in "P6 fee identity" | `c30_validation.py:66, 83` | `P6 fee identity %s` | **FOUND** | `OURS` | Quote: `"P6 fee identity"` (`C30_VALIDATION.md:4`) |
| L4 | Preflight | "0" in "(gap 0)" | `c30_validation.py:83` | `worst < 1e-6` | **FOUND** | `OURS` | Quote: `"(gap 0)"` (`C30_VALIDATION.md:4`) |
| L4 | Preflight | "7" in "P7 overlap" | `c30_validation.py:66, 85` | `P7 overlap %s` | **FOUND** | `OURS` | Quote: `"P7 overlap"` (`C30_VALIDATION.md:4`) |
| L4 | Preflight | "0" in "(0)" overlaps | `c30_validation.py:84-85` | `ov == 0` | **FOUND** | `OURS` | Quote: `"(0)"` (`C30_VALIDATION.md:4`) |
| L5 | Note | "30" in "C30 DEV run" | `PRE_REG_C30.md:7-9` | `C30 DEV run` | **FOUND** | `OURS` | Quote: `"earlier C30 DEV run"` (`C30_VALIDATION.md:5`) |
| L5 | Note | "2024-07" split date | `PRE_REG_C30.md:7` | DEV window 2022-01-01..2024-06-30 (split 2024-07) | **FOUND** | `OURS` | Quote: `"split at 2024-07"` (`C30_VALIDATION.md:5`) |
| L7 | Table header | "95 %" CI confidence level | `c30_validation.py:61`, `PRE_REG_C30.md:38` | `1.96 * se` (standard normal 95% CI) | **FOUND** | `FACT` | Quote: `"95 % CI"` (`C30_VALIDATION.md:7`) |
| L7 | Table header | "2" in "m=2" Holm family size | `c30_validation.py:109-112`, `PRE_REG_C30.md:39` | `m = 2` | **FOUND** | `FACT` | Quote: `"Holm p (m=2)"` (`C30_VALIDATION.md:7`) |
| L9 | Table row H1 | "1" in "H1" (Hypothesis 1) | `c30_validation.py:100`, `c30_validation_verdict.json:6` | `H1` | **FOUND** | `OURS` | Quote: `"H1"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "30m" chart timeframe | `c30_validation.py:46, 100` | `30m` | **FOUND** | `OURS` | Quote: `"30m, any trend"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "35" trades (sample size n) | `c30_validation_verdict.json:7` | `"n": 35` | **FOUND** | `OURS` | Quote: `"35"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "74 %" win rate | `c30_validation_verdict.json:12` | `"win": 74.28571428571429` (rounds to 74%) | **FOUND** | `OURS` | Quote: `"74 %"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "-0.066 %" mean fee-net return | `c30_validation_verdict.json:8` | `"mean": -0.06591502449152191` (rounds to -0.066%) | **FOUND** | `OURS` | Quote: `"-0.066 %"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "1.97" sample SD | `c30_validation_verdict.json:9` | `"sd": 1.972865860558429` (rounds to 1.97) | **FOUND** | `OURS` | Quote: `"1.97"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "-0.720" 95% CI lower bound | `c30_validation_verdict.json:10` | `"ci_lo": -0.7195264071068822` (rounds to -0.720) | **FOUND** | `OURS` | Quote: `"-0.720 .. +0.588"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "+0.588" 95% CI upper bound | `c30_validation_verdict.json:11` | `"ci_hi": 0.5876963581238385` (rounds to +0.588) | **FOUND** | `OURS` | Quote: `"-0.720 .. +0.588"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "-6.63 %" worst trade | `c30_validation_verdict.json:13` | `"worst": -6.634847620857887` (rounds to -6.63%) | **FOUND** | `OURS` | Quote: `"-6.63 %"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "19" half-year 1 trade count n | `c30_validation_verdict.json:17` | `"n": 19` | **FOUND** | `OURS` | Quote: `"19 -0.013 %, 16 -0.129 %"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "-0.013 %" half-year 1 mean | `c30_validation_verdict.json:18` | `"mean": -0.01291764574386065` (rounds to -0.013%) | **FOUND** | `OURS` | Quote: `"19 -0.013 %, 16 -0.129 %"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "16" half-year 2 trade count n | `c30_validation_verdict.json:21` | `"n": 16` | **FOUND** | `OURS` | Quote: `"19 -0.013 %, 16 -0.129 %"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "-0.129 %" half-year 2 mean | `c30_validation_verdict.json:22` | `"mean": -0.12884941175436965` (rounds to -0.129%) | **FOUND** | `OURS` | Quote: `"19 -0.013 %, 16 -0.129 %"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "0.578" one-sided p-value | `c30_validation_verdict.json:15` | `"p_one_sided": 0.5777540966717036` (rounds to 0.578) | **FOUND** | `OURS` | Quote: `"0.578"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "0.578" Holm p-value | `c30_validation_verdict.json:207` | `"holm_p": 0.5777540966717036` (rounds to 0.578) | **FOUND** | `OURS` | Quote: `"0.578"` (`C30_VALIDATION.md:9`) |
| L9 | Table row H1 | "0" in "FAIL (mean <= 0)" | `c30_validation.py:115`, `PRE_REG_C30.md:40` | `"FAIL" if s["n"] < 2 or s["mean"] <= 0` | **FOUND** | `OURS` | Quote: `"FAIL (mean <= 0)"` (`C30_VALIDATION.md:9`) |
| L10 | Table row H2 | "2" in "H2" (Hypothesis 2) | `c30_validation.py:100`, `c30_validation_verdict.json:210` | `H2` | **FOUND** | `OURS` | Quote: `"H2"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "15m" chart timeframe | `c30_validation.py:46, 100` | `15m` | **FOUND** | `OURS` | Quote: `"15m, 2h trend up"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "2h" trend filter timeframe | `c30_validation.py:47`, `PRE_REG_C30.md:28` | `2h` | **FOUND** | `OURS` | Quote: `"15m, 2h trend up"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "22" trades (sample size n) | `c30_validation_verdict.json:211` | `"n": 22` | **FOUND** | `OURS` | Quote: `"22"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "73 %" win rate | `c30_validation_verdict.json:216` | `"win": 72.72727272727273` (rounds to 73%) | **FOUND** | `OURS` | Quote: `"73 %"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "+0.220 %" mean fee-net return | `c30_validation_verdict.json:212` | `"mean": 0.22029772521407937` (rounds to +0.220%) | **FOUND** | `OURS` | Quote: `"+0.220 %"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "0.81" sample SD | `c30_validation_verdict.json:213` | `"sd": 0.8140337918851395` (rounds to 0.81) | **FOUND** | `OURS` | Quote: `"0.81"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "-0.120" 95% CI lower bound | `c30_validation_verdict.json:214` | `"ci_lo": -0.11986534641838847` (rounds to -0.120) | **FOUND** | `OURS` | Quote: `"-0.120 .. +0.560"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "+0.560" 95% CI upper bound | `c30_validation_verdict.json:215` | `"ci_hi": 0.5604607968465471` (rounds to +0.560) | **FOUND** | `OURS` | Quote: `"-0.120 .. +0.560"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "-1.45 %" worst trade | `c30_validation_verdict.json:217` | `"worst": -1.4541170341777598` (rounds to -1.45%) | **FOUND** | `OURS` | Quote: `"-1.45 %"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "11" half-year 1 trade count n | `c30_validation_verdict.json:221` | `"n": 11` | **FOUND** | `OURS` | Quote: `"11 +0.298 %, 11 +0.143 %"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "+0.298 %" half-year 1 mean | `c30_validation_verdict.json:222` | `"mean": 0.29781851659450786` (rounds to +0.298%) | **FOUND** | `OURS` | Quote: `"11 +0.298 %, 11 +0.143 %"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "11" half-year 2 trade count n | `c30_validation_verdict.json:225` | `"n": 11` | **FOUND** | `OURS` | Quote: `"11 +0.298 %, 11 +0.143 %"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "+0.143 %" half-year 2 mean | `c30_validation_verdict.json:226` | `"mean": 0.1427769338336509` (rounds to +0.143%) | **FOUND** | `OURS` | Quote: `"11 +0.298 %, 11 +0.143 %"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "0.109" one-sided p-value | `c30_validation_verdict.json:219` | `"p_one_sided": 0.10919050979306728` (rounds to 0.109) | **FOUND** | `OURS` | Quote: `"0.109"` (`C30_VALIDATION.md:10`) |
| L10 | Table row H2 | "0.218" Holm p-value | `c30_validation_verdict.json:346` | `"holm_p": 0.21838101958613457` (rounds to 0.218) | **FOUND** | `OURS` | Quote: `"0.218"` (`C30_VALIDATION.md:10`) |
| L12 | P8 test | "8" in "P8" | `c30_validation.py:66, 89` | `p8` | **FOUND** | `OURS` | Quote: `"P8 random entries"` (`C30_VALIDATION.md:12`) |
| L12 | P8 test | "30" draws | `c30_validation.py:89` | `draws=30` | **FOUND** | `OURS` | Quote: `"30 draws"` (`C30_VALIDATION.md:12`) |
| L12 | P8 test | "2" in "H2" | `c30_validation.py:100` | `H2` | **FOUND** | `OURS` | Quote: `"H2 beats 30/30"` (`C30_VALIDATION.md:12`) |
| L12 | P8 test | "30/30" H2 beats | `c30_validation_verdict.json:343-344` | `[30, 30]` | **FOUND** | `OURS` | Quote: `"30/30"` (`C30_VALIDATION.md:12`) |
| L12 | P8 test | "-0.037 %" H2 random median | `c30_validation_verdict.json:342` | `-0.03714635804241989` (rounds to -0.037%) | **FOUND** | `OURS` | Quote: `"random median -0.037 %"` (`C30_VALIDATION.md:12`) |
| L12 | P8 test | "1" in "H1" | `c30_validation.py:100` | `H1` | **FOUND** | `OURS` | Quote: `"H1 beats 10/30"` (`C30_VALIDATION.md:12`) |
| L12 | P8 test | "10/30" H1 beats | `c30_validation_verdict.json:204-205` | `[10, 30]` | **FOUND** | `OURS` | Quote: `"10/30"` (`C30_VALIDATION.md:12`) |
| L12 | P8 test | "+0.001 %" H1 random median | `c30_validation_verdict.json:203` | `0.001066601775909393` (rounds to +0.001%) | **FOUND** | `OURS` | Quote: `"random median +0.001 %"` (`C30_VALIDATION.md:12`) |
| L13 | Interpretation | "2" in "H2" | `c30_validation.py:100` | `H2` | **FOUND** | `OURS` | Quote: `"H2 matches the DEV sign"` (`C30_VALIDATION.md:13`) |
| L13 | Interpretation | "+0.261 %" DEV mean | `PRE_REG_C30.md:16` | `+0.261 %` | **FOUND** | `OURS` | Quote: `"+0.261 % DEV"` (`C30_VALIDATION.md:13`) |
| L13 | Interpretation | "+0.220 %" VALIDATION mean | `c30_validation_verdict.json:212` | `0.22029772521407937` (rounds to +0.220%) | **FOUND** | `OURS` | Quote: `"+0.220 %"` (`C30_VALIDATION.md:13`) |
| L13 | Interpretation | "0" in "CI includes 0" | `c30_validation_verdict.json:214-215` | `ci_lo = -0.1198... < 0 < ci_hi = 0.5604...` | **FOUND** | `FACT` | Quote: `"the CI includes 0"` (`C30_VALIDATION.md:13`) |
| L13 | Interpretation | "0.218" Holm p-value | `c30_validation_verdict.json:346` | `0.21838101958613457` (rounds to 0.218) | **FOUND** | `OURS` | Quote: `"Holm p 0.218"` (`C30_VALIDATION.md:13`) |
| L13 | Interpretation | "0.05" significance threshold | `PRE_REG_C30.md:39`, `c30_validation.py:115` | `p < 0.05` | **FOUND** | `FACT` | Quote: `"> 0.05"` (`C30_VALIDATION.md:13`) |
| L14 | Gaps | "4" in "pre-reg section 4" | `PRE_REG_C30.md:51` | `## 4. Known weaknesses (disclosed now)` | **FOUND** | `FACT` | Quote: `"pre-reg section 4"` (`C30_VALIDATION.md:14`) |


## Claude review note (Lead, 2026-11-02)

- Spot-checked every table number in C30_VALIDATION.md rows H1/H2, the P8 line and the DEV figure against c30_validation_verdict.json, PRE_REG_C30.md and c30_validation.py: all match. Cites to c30_validation.py:10,19,61,66,83,85,89,100,115 and PRE_REG_C30.md:7,16,28,38-40,51 land on the stated content.
- Relabelled 7 entries from SOURCED to FACT: none quotes the trader; they are our pre-reg, our script or a standard statistic (MOVED_RULES.md).
- Headline row count is inflated: label digits ("1" in "H1", "30" in "C30") are counted as numbers; the distinct claims are the table cells, P8 line and preflight figures.
- Not checked: the cited line numbers inside c30_validation_verdict.json (a JSON file; values were matched by key, not line).
