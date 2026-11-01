# FOUND: 201, NOT_IN_DATA: 20, DIFF: 0

# Blind Re-read of Recent RESULT.md Files Against Cited Sources

Audit of numbers across five recent studies:
1. `MyTradingSys/research/tom_v2_gross_first_2026-11/RESULT.md` (cited `results.json`, `full_report.md`)
2. `MyTradingSys/research/reclaim_close_stop_2026-11/RESULT.md` (cited `results_DEV.csv`)
3. `MyTradingSys/research/meta_label_breaks_2026-10-31/RESULT.md` (cited `output.md`, `explore_div_output.md`, `confirm_div.json`)
4. `MyTradingSys/research/cowen_q4_2026-10-31/event_study/RESULT.md` (cited `EVENTS.csv`)
5. `MyTradingSys/research/tf_break_event_study_2026-10-30/RESULT.md` (cited `output.md`)

## Summary

- **Total Numbers / Claims Audited**: 221
- **FOUND (Exact match in cited file)**: 201
- **NOT_IN_DATA (Cited file absent from repo/disk, or number omitted from saved source)**: 20
- **DIFF (Discrepancy between text and cited file)**: 0

---

## tom_v2_gross_first_2026-11

| Line | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L3 | Run timestamp: 2026-11-01 08:40 UTC | `results.json` | run_utc: 2026-11-01 08:40 | **FOUND** | `OURS` | results.json:meta.run_utc |
| L4 | Data range: 2020-01-02..2021-12-31 | `results.json` | first_day: 2020-01-02, last_day: 2021-12-31 | **FOUND** | `OURS` | results.json:meta |
| L4 | Complete UTC days: 730 | `results.json` | days_used: 730 | **FOUND** | `OURS` | results.json:days_used |
| L4 | Dropped: {'incomplete_day': 0, 'no_atr': 0, 'empty_profile': 0} | `results.json` | {'incomplete_day': 0, 'no_atr': 0, 'empty_profile': 0} | **FOUND** | `OURS` | results.json:dropped |
| L5 | Monthly files: 24 | `results.json` | bars_meta.files: 24 | **FOUND** | `OURS` | results.json:meta.bars_meta.files |
| L7 | CI lower bound: -0.3 pp (FAIL verdict threshold 0) | `results.json` | ci[0]: -0.00268 (-0.27 pp) | **FOUND** | `OURS` | results.json:primary_near.diff.ci[0] |
| L12 | Primary arm n: 352 | `results.json` | real.n: 352 | **FOUND** | `OURS` | results.json:primary_near.real.n |
| L12 | Primary arm mean difference: 4.4 pp | `results.json` | diff: 0.04429 (4.43 pp) | **FOUND** | `OURS` | results.json:primary_near.diff.diff |
| L12 | Primary arm SE: 2.35 pp | `results.json` | Derived from 95% CI [-0.27, 8.93] / 3.92 = 2.347 | **FOUND** | `OURS` | Formula SE = (CI_hi - CI_lo) / 3.92 |
| L14 | Real return share: 63.4 % (n 352) | `results.json` | share: 0.63352 (63.35 %) | **FOUND** | `OURS` | results.json:primary_near.real.share |
| L14 | Real 95% CI: 58.2..68.2 | `results.json` | ci: [0.58239, 0.68169] | **FOUND** | `OURS` | results.json:primary_near.real.ci |
| L14 | Near placebo return share: 58.9 % (n 353) | `results.json` | share: 0.58924 (58.92 %) | **FOUND** | `OURS` | results.json:primary_near.placebo.share |
| L14 | Near placebo 95% CI: 53.8..64.0 | `results.json` | ci: [0.53846, 0.64023] | **FOUND** | `OURS` | results.json:primary_near.placebo.ci |
| L14 | Difference: 4.4 pp | `results.json` | diff: 0.04429 (4.43 pp) | **FOUND** | `OURS` | results.json:primary_near.diff.diff |
| L14 | Day-block 95% CI: -0.3..8.9 | `results.json` | ci: [-0.00268, 0.08933] | **FOUND** | `OURS` | results.json:primary_near.diff.ci |
| L14 | Bootstrap resamples: 2000 | `PRE_REG.md` | 2000 resamples | **FOUND** | `OURS` | PRE_REG.md:38 |
| L14 | Days in primary: 365 | `results.json` | n_days: 365 | **FOUND** | `OURS` | results.json:primary_near.n_days |
| L15 | Card prior expectation: ~870 events | `CARD / PRE_REG.md` | Not in results.json | **NOT_IN_DATA** | `OURS` | Cited from task card expectation, not in results.json |
| L16 | Far band real return share (&#124;d&#124; >= 2): 58.5 % (n 349) | `results.json` | share: 0.58453 (58.45 %) | **FOUND** | `OURS` | results.json:far_descriptive.real.share |
| L16 | Far band placebo return share: 37.3 % (n 359) | `results.json` | share: 0.37326 (37.33 %) | **FOUND** | `OURS` | results.json:far_descriptive.placebo.share |
| L16 | Far band difference: 21.1 pp | `results.json` | diff: 0.21127 (21.13 pp) | **FOUND** | `OURS` | results.json:far_descriptive.diff.diff |
| L16 | Far band 95% CI: 13.7..28.6 | `results.json` | ci: [0.13678, 0.28648] | **FOUND** | `OURS` | results.json:far_descriptive.diff.ci |
| L16 | DEV vp_return result: real 57.2 % vs near 51.2 % | `vp_return DEV` | Not in results.json (DEV_EXT window) | **NOT_IN_DATA** | `OURS` | Prior DEV run results cited for comparison, explicitly not in results.json |
| L17 | Tom's 70 % claim | `extract_BB3c8visnkI.md:38` | 70% | **FOUND** | `SOURCED` | extract_BB3c8visnkI.md:38: "the other 70% he will try and strive to run back here" |
| L17 | All-d real return share: 60.9 % (n 701) | `results.json` | share: 0.60913 (60.91 %) | **FOUND** | `OURS` | results.json:A.real.share |
| L17 | All-d real 95% CI: 57.2..64.4 | `results.json` | ci: [0.57163, 0.64358] | **FOUND** | `OURS` | results.json:A.real.ci |
| L24 | DEV result of vp_return (57.2/46.8/51.2/47.8) | `vp_return DEV` | Not in results.json | **NOT_IN_DATA** | `OURS` | Explicitly stated in RESULT.md line 24: "is not re-derived here" |

## reclaim_close_stop_2026-11

| Line | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L3 | Fee-net round trip: 0.10 % | `fees.py` | 0.0010 (10 bp) | **FOUND** | `SOURCED` | fees.py:BINANCE_TAKER (5 bp * 2 legs) |
| L9 | 4h all DEV n: 114 | `results_DEV.csv` | n: 114 | **FOUND** | `OURS` | results_DEV.csv:line 2 |
| L9 | 4h all DEV gross %: 0.371 | `results_DEV.csv` | gross_pct: 0.3710 | **FOUND** | `OURS` | results_DEV.csv:line 2 |
| L9 | 4h all DEV mean fee-net %: 0.271 | `results_DEV.csv` | net_pct: 0.2710 | **FOUND** | `OURS` | results_DEV.csv:line 2 |
| L9 | 4h all DEV 95% CI: -0.253 .. 0.805 | `results_DEV.csv` | ci_lo: -0.2534, ci_hi: 0.8054 | **FOUND** | `OURS` | results_DEV.csv:line 2 |
| L10 | 1D all DEV n: 13 | `results_DEV.csv` | n: 13 | **FOUND** | `OURS` | results_DEV.csv:line 5 |
| L10 | 1D all DEV gross %: -1.093 | `results_DEV.csv` | gross_pct: -1.0934 | **FOUND** | `OURS` | results_DEV.csv:line 5 |
| L10 | 1D all DEV mean fee-net %: -1.193 | `results_DEV.csv` | net_pct: -1.1934 | **FOUND** | `OURS` | results_DEV.csv:line 5 |
| L10 | 1D all DEV 95% CI: -3.884 .. 1.496 | `results_DEV.csv` | ci_lo: -3.8836, ci_hi: 1.4962 | **FOUND** | `OURS` | results_DEV.csv:line 5 |
| L12 | 4h low-break reclaim n: 62 | `results_DEV.csv` | n: 62 | **FOUND** | `OURS` | results_DEV.csv:line 3 |
| L12 | 4h low-break reclaim net %: +0.427 | `results_DEV.csv` | net_pct: 0.4268 | **FOUND** | `OURS` | results_DEV.csv:line 3 |
| L12 | 4h low-break reclaim 95% CI: -0.251 .. 1.218 | `results_DEV.csv` | ci_lo: -0.2506, ci_hi: 1.2180 | **FOUND** | `OURS` | results_DEV.csv:line 3 |
| L12 | 4h high-break reclaim n: 52 | `results_DEV.csv` | n: 52 | **FOUND** | `OURS` | results_DEV.csv:line 4 |
| L12 | 4h high-break reclaim net %: +0.085 | `results_DEV.csv` | net_pct: 0.0852 | **FOUND** | `OURS` | results_DEV.csv:line 4 |
| L12 | 4h high-break reclaim 95% CI: -0.659 .. 0.811 | `results_DEV.csv` | ci_lo: -0.6588, ci_hi: 0.8115 | **FOUND** | `OURS` | results_DEV.csv:line 4 |
| L12 | 1D low-break reclaim n: 5 | `results_DEV.csv` | n: 5 | **FOUND** | `OURS` | results_DEV.csv:line 6 |
| L12 | 1D high-break reclaim n: 8 | `results_DEV.csv` | n: 8 | **FOUND** | `OURS` | results_DEV.csv:line 7 |
| L12 | 4h level-stop exit share: 50 % | `results_DEV.csv` | stop_share: 0.5000 | **FOUND** | `OURS` | results_DEV.csv:line 2 |
| L12 | 4h mean hold: 4.0 bars | `results_DEV.csv` | mean_hold: 4.0351 | **FOUND** | `OURS` | results_DEV.csv:line 2 |
| L12 | 4h win rate: 40 % | `results_DEV.csv` | win_pct: 40.3509 | **FOUND** | `OURS` | results_DEV.csv:line 2 |
| L14 | T058 fade-R 4h DEV: -0.417 % (n 111) | `tf_break output.md:12` | -0.417 %, n 111 | **FOUND** | `OURS` | tf_break_event_study_2026-10-30/output.md:12 |
| L14 | Difference vs T058: 0.7 points | `results_DEV.csv vs output.md` | 0.271 - (-0.417) = 0.688 (~0.7 pts) | **FOUND** | `OURS` | Derived difference between studies |

## meta_label_breaks_2026-10-31

| Line | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L4 | Round-trip taker fee: 0.10 % | `fees.py` | fees.BINANCE_TAKER both legs = 0.10 % | **FOUND** | `SOURCED` | fees.py:BINANCE_TAKER |
| L8 | 1h best third net: +0.063 % | `output.md` | top net: 0.063 | **FOUND** | `OURS` | output.md:7 |
| L9 | 1h best third 95% CI: -0.048..+0.179 | `output.md` | top CI: [-0.048, 0.179] | **FOUND** | `OURS` | output.md:7 |
| L9 | 1h best third 2022 / 2023-24: +0.129 % / +0.035 % | `output.md` | top net 2022 / 2023-24: 0.129 (107) / 0.035 (253) | **FOUND** | `OURS` | output.md:7 |
| L9 | 1h placebo p: 0.020 (beats 98 %) | `output.md` | placebo p: 0.020 | **FOUND** | `OURS` | output.md:7 |
| L9 | 1h Holm-adjusted p: 0.060 | `output.md` | Holm p: 0.060 | **FOUND** | `OURS` | output.md:7 |
| L10 | 1h detectable lift: 0.16 % (0.160 %) | `output.md` | lift detectable: 0.160 | **FOUND** | `OURS` | output.md:7 |
| L10 | 1h trades per third: 360 | `output.md` | top third n: 360 | **FOUND** | `OURS` | output.md:7 |
| L10 | 1h measured lift: 0.096 % | `output.md` | lift: 0.096 | **FOUND** | `OURS` | output.md:7 |
| L11 | 4h early exit difference: +0.07..+0.09 % | `output.md` | difference: 0.089 (k=1), 0.072 (k=2) | **FOUND** | `OURS` | output.md:17-18 |
| L13 | Winners under water at k=1: 27-28 % | `output.md` | 27 % (15m), 28 % (1h), 28 % (4h) | **FOUND** | `OURS` | output.md:13,15,17 |
| L13 | Losers under water at k=1: 62-67 % | `output.md` | 62 % (15m), 65 % (1h), 67 % (4h) | **FOUND** | `OURS` | output.md:13,15,17 |
| L19 | 15m trades: 4114 | `output.md` | trades: 4114 | **FOUND** | `OURS` | output.md:6 |
| L19 | 15m all trades net %: -0.094 | `output.md` | all net: -0.094 | **FOUND** | `OURS` | output.md:6 |
| L19 | 15m best third n: 1379 | `output.md` | top third n: 1379 | **FOUND** | `OURS` | output.md:6 |
| L19 | 15m best third gross %: +0.020 | `output.md` | top gross: 0.020 | **FOUND** | `OURS` | output.md:6 |
| L19 | 15m best third net %: -0.080 | `output.md` | top net: -0.080 | **FOUND** | `OURS` | output.md:6 |
| L19 | 15m best third 95% CI: -0.121..-0.036 | `output.md` | top CI: [-0.121, -0.036] | **FOUND** | `OURS` | output.md:6 |
| L19 | 15m worst third net %: -0.108 | `output.md` | bottom net: -0.108 | **FOUND** | `OURS` | output.md:6 |
| L19 | 15m placebo p: 0.090 | `output.md` | placebo p: 0.090 | **FOUND** | `OURS` | output.md:6 |
| L19 | 15m Holm p: 0.129 | `output.md` | Holm p: 0.129 | **FOUND** | `OURS` | output.md:6 |
| L20 | 1h trades: 1078 | `output.md` | trades: 1078 | **FOUND** | `OURS` | output.md:7 |
| L20 | 1h all trades net %: -0.033 | `output.md` | all net: -0.033 | **FOUND** | `OURS` | output.md:7 |
| L20 | 1h best third n: 360 | `output.md` | top third n: 360 | **FOUND** | `OURS` | output.md:7 |
| L20 | 1h best third gross %: +0.163 | `output.md` | top gross: 0.163 | **FOUND** | `OURS` | output.md:7 |
| L20 | 1h best third net %: +0.063 | `output.md` | top net: 0.063 | **FOUND** | `OURS` | output.md:7 |
| L20 | 1h best third 95% CI: -0.048..+0.179 | `output.md` | top CI: [-0.048, 0.179] | **FOUND** | `OURS` | output.md:7 |
| L20 | 1h worst third net %: -0.101 | `output.md` | bottom net: -0.101 | **FOUND** | `OURS` | output.md:7 |
| L20 | 1h placebo p: 0.020 | `output.md` | placebo p: 0.020 | **FOUND** | `OURS` | output.md:7 |
| L20 | 1h Holm p: 0.060 | `output.md` | Holm p: 0.060 | **FOUND** | `OURS` | output.md:7 |
| L21 | 4h trades: 417 | `output.md` | trades: 417 | **FOUND** | `OURS` | output.md:8 |
| L21 | 4h all trades net %: -0.153 | `output.md` | all net: -0.153 | **FOUND** | `OURS` | output.md:8 |
| L21 | 4h best third n: 145 | `output.md` | top third n: 145 | **FOUND** | `OURS` | output.md:8 |
| L21 | 4h best third gross %: +0.197 | `output.md` | top gross: 0.197 | **FOUND** | `OURS` | output.md:8 |
| L21 | 4h best third net %: +0.097 | `output.md` | top net: 0.097 | **FOUND** | `OURS` | output.md:8 |
| L21 | 4h best third 95% CI: -0.210..+0.403 | `output.md` | top CI: [-0.210, 0.403] | **FOUND** | `OURS` | output.md:8 |
| L21 | 4h worst third net %: -0.223 | `output.md` | bottom net: -0.223 | **FOUND** | `OURS` | output.md:8 |
| L21 | 4h placebo p: 0.065 | `output.md` | placebo p: 0.065 | **FOUND** | `OURS` | output.md:8 |
| L21 | 4h Holm p: 0.129 | `output.md` | Holm p: 0.129 | **FOUND** | `OURS` | output.md:8 |
| L23 | BH-FDR: 1h 0.060, 15m and 4h 0.090 | `output.md` | Derived from p-values | **FOUND** | `OURS` | Computed BH FDR across 3 tests |
| L29 | 15m k=1 hold net %: -0.094 | `output.md` | hold net: -0.094 | **FOUND** | `OURS` | output.md:13 |
| L29 | 15m k=1 early-exit net %: -0.101 | `output.md` | early-exit net: -0.101 | **FOUND** | `OURS` | output.md:13 |
| L29 | 15m k=1 difference: -0.007 | `output.md` | difference: -0.007 | **FOUND** | `OURS` | output.md:13 |
| L29 | 15m k=1 diff 95% CI: -0.016..+0.002 | `output.md` | diff CI: [-0.016, 0.002] | **FOUND** | `OURS` | output.md:13 |
| L29 | 15m k=1 winners under water: 27 % | `output.md` | winners under water at k: 27 % | **FOUND** | `OURS` | output.md:13 |
| L29 | 15m k=1 losers under water: 62 % | `output.md` | losers under water at k: 62 % | **FOUND** | `OURS` | output.md:13 |
| L30 | 15m k=2 hold net %: -0.094 | `output.md` | hold net: -0.094 | **FOUND** | `OURS` | output.md:14 |
| L30 | 15m k=2 early-exit net %: -0.097 | `output.md` | early-exit net: -0.097 | **FOUND** | `OURS` | output.md:14 |
| L30 | 15m k=2 difference: -0.004 | `output.md` | difference: -0.004 | **FOUND** | `OURS` | output.md:14 |
| L30 | 15m k=2 diff 95% CI: -0.012..+0.005 | `output.md` | diff CI: [-0.012, 0.005] | **FOUND** | `OURS` | output.md:14 |
| L30 | 15m k=2 winners under water: 18 % | `output.md` | winners under water at k: 18 % | **FOUND** | `OURS` | output.md:14 |
| L30 | 15m k=2 losers under water: 66 % | `output.md` | losers under water at k: 66 % | **FOUND** | `OURS` | output.md:14 |
| L31 | 1h k=1 hold net %: -0.033 | `output.md` | hold net: -0.033 | **FOUND** | `OURS` | output.md:15 |
| L31 | 1h k=1 early-exit net %: -0.062 | `output.md` | early-exit net: -0.062 | **FOUND** | `OURS` | output.md:15 |
| L31 | 1h k=1 difference: -0.029 | `output.md` | difference: -0.029 | **FOUND** | `OURS` | output.md:15 |
| L31 | 1h k=1 diff 95% CI: -0.066..+0.007 | `output.md` | diff CI: [-0.066, 0.007] | **FOUND** | `OURS` | output.md:15 |
| L31 | 1h k=1 winners under water: 28 % | `output.md` | winners under water at k: 28 % | **FOUND** | `OURS` | output.md:15 |
| L31 | 1h k=1 losers under water: 65 % | `output.md` | losers under water at k: 65 % | **FOUND** | `OURS` | output.md:15 |
| L32 | 1h k=2 hold net %: -0.033 | `output.md` | hold net: -0.033 | **FOUND** | `OURS` | output.md:16 |
| L32 | 1h k=2 early-exit net %: -0.031 | `output.md` | early-exit net: -0.031 | **FOUND** | `OURS` | output.md:16 |
| L32 | 1h k=2 difference: +0.003 | `output.md` | difference: 0.003 | **FOUND** | `OURS` | output.md:16 |
| L32 | 1h k=2 diff 95% CI: -0.023..+0.031 | `output.md` | diff CI: [-0.023, 0.031] | **FOUND** | `OURS` | output.md:16 |
| L32 | 1h k=2 winners under water: 17 % | `output.md` | winners under water at k: 17 % | **FOUND** | `OURS` | output.md:16 |
| L32 | 1h k=2 losers under water: 69 % | `output.md` | losers under water at k: 69 % | **FOUND** | `OURS` | output.md:16 |
| L33 | 4h k=1 hold net %: -0.154 | `output.md` | hold net: -0.154 | **FOUND** | `OURS` | output.md:17 |
| L33 | 4h k=1 early-exit net %: -0.065 | `output.md` | early-exit net: -0.065 | **FOUND** | `OURS` | output.md:17 |
| L33 | 4h k=1 difference: +0.089 | `output.md` | difference: 0.089 | **FOUND** | `OURS` | output.md:17 |
| L33 | 4h k=1 diff 95% CI: -0.019..+0.211 | `output.md` | diff CI: [-0.019, 0.211] | **FOUND** | `OURS` | output.md:17 |
| L33 | 4h k=1 winners under water: 28 % | `output.md` | winners under water at k: 28 % | **FOUND** | `OURS` | output.md:17 |
| L33 | 4h k=1 losers under water: 67 % | `output.md` | losers under water at k: 67 % | **FOUND** | `OURS` | output.md:17 |
| L34 | 4h k=2 hold net %: -0.154 | `output.md` | hold net: -0.154 | **FOUND** | `OURS` | output.md:18 |
| L34 | 4h k=2 early-exit net %: -0.081 | `output.md` | early-exit net: -0.081 | **FOUND** | `OURS` | output.md:18 |
| L34 | 4h k=2 difference: +0.072 | `output.md` | difference: 0.072 | **FOUND** | `OURS` | output.md:18 |
| L34 | 4h k=2 diff 95% CI: -0.017..+0.165 | `output.md` | diff CI: [-0.017, 0.165] | **FOUND** | `OURS` | output.md:18 |
| L34 | 4h k=2 winners under water: 20 % | `output.md` | winners under water at k: 20 % | **FOUND** | `OURS` | output.md:18 |
| L34 | 4h k=2 losers under water: 71 % | `output.md` | losers under water at k: 71 % | **FOUND** | `OURS` | output.md:18 |
| L37 | 1h trend_d: low third -0.103, high third +0.041 | `output.md` | low third: -0.103, high third: 0.041 | **FOUND** | `OURS` | output.md:40 |
| L38 | 1h 4h BBWP: low third -0.087, high third +0.009 | `output.md` | low third: -0.087, high third: 0.009 | **FOUND** | `OURS` | output.md:39 |
| L39 | 1h flow_e: low third +0.072, high third -0.112 | `output.md` | low third: 0.072, high third: -0.112 | **FOUND** | `OURS` | output.md:42 |
| L41 | 1h reclaim trades (class R): +0.037 (n 229) | `output.md` | high third: 0.037 (229) | **FOUND** | `OURS` | output.md:50 |
| L41 | 1h wick-sweep fades (W1): -0.068 (n 641) | `output.md` | high third: -0.068 (641) | **FOUND** | `OURS` | output.md:51 |
| L45 | Dropped trades for trend_d: 15m 1123, 1h 300, 4h 107 | `dev.json / meta.py` | Not in output.md | **NOT_IN_DATA** | `OURS` | Raw dev.json not on disk |
| L61 | 1h fixed 4 bars: -0.053 % | `explore_div_output.md` | net %: -0.053 | **FOUND** | `OURS` | explore_div_output.md:43 |
| L61 | 1h fixed 24 bars: -0.062 % | `explore_div_output.md` | net %: -0.062 | **FOUND** | `OURS` | explore_div_output.md:44 |
| L62 | 1h best divergence exit (CVD, lower TF): -0.042 % [-0.148, +0.066] | `explore_div_output.md` | net %: -0.042, 95% CI: -0.148..+0.066 | **FOUND** | `OURS` | explore_div_output.md:48 |
| L62 | 4h fixed 4 bars: -0.157 % | `explore_div_output.md` | net %: -0.157 | **FOUND** | `OURS` | explore_div_output.md:77 |
| L62 | 4h fixed 12 bars: -0.013 % | `explore_div_output.md` | net %: -0.013 | **FOUND** | `OURS` | explore_div_output.md:78 |
| L62 | 4h CVD lower TF exit: +0.029 % [-0.187, +0.242] | `explore_div_output.md` | net %: +0.029, 95% CI: -0.187..+0.242 | **FOUND** | `OURS` | explore_div_output.md:82 |
| L63 | Lower-TF CVD exit median hold: 6 bars | `explore_div_output.md` | median bars held: 6 (1h) / 6 (4h) | **FOUND** | `OURS` | explore_div_output.md:48,82 |
| L63 | 1h net without best 5%: -0.248 % (CVD) vs -0.413 % (fixed 24) | `explore_div_output.md` | -0.248 % vs -0.413 % | **FOUND** | `OURS` | explore_div_output.md:48,44 |
| L67 | 15m lower-TF reverse divergence: -0.085 (n 143) / -0.069 (n 127) vs -0.105 % | `explore_div_output.md` | -0.085 (143) / -0.069 (127) vs -0.105 % | **FOUND** | `OURS` | explore_div_output.md:26,38 |
| L67 | 1h lower-TF reverse divergence: +0.121 (n 65) / +0.015 (n 58) vs ~-0.06 % | `explore_div_output.md` | +0.121 (65) / +0.015 (58) vs -0.062 / -0.056 | **FOUND** | `OURS` | explore_div_output.md:61,72 |
| L68 | 4h lower-TF reverse divergence: +0.493 (n 36) / +0.322 (n 32) vs ~-0.20 % | `explore_div_output.md` | +0.493 (36) / +0.322 (32) vs -0.205 / -0.188 | **FOUND** | `OURS` | explore_div_output.md:94,103 |
| L72 | BTCUSDT 1m 2020-01..2021-12 bars: 1,052,640 | `confirm_div.json` | File not on disk | **NOT_IN_DATA** | `OURS` | confirm_div.json not in repo |
| L75 | 15m confirm_div flagged: 274, net -0.110 %, CI -0.239..+0.013, Holm 1.0, unflagged -0.101 % | `confirm_div.json` | File not on disk | **NOT_IN_DATA** | `OURS` | confirm_div.json not in repo |
| L76 | 1h confirm_div flagged: 131, net -0.180 %, CI -0.408..+0.052, Holm 1.0, unflagged -0.158 % | `confirm_div.json` | File not on disk | **NOT_IN_DATA** | `OURS` | confirm_div.json not in repo |
| L77 | 4h confirm_div flagged: 52, net -0.384 %, CI -1.208..+0.352, Holm 1.0, unflagged -0.291 % | `confirm_div.json` | File not on disk | **NOT_IN_DATA** | `OURS` | confirm_div.json not in repo |
| L79 | 1h PRD +0.068 % (n 79), NRD -0.556 % (n 52) | `confirm_div.json` | File not on disk | **NOT_IN_DATA** | `OURS` | confirm_div.json not in repo |
| L79 | 4h 2020 +0.292 % (n 27), 2021 -1.115 % (n 25) | `confirm_div.json` | File not on disk | **NOT_IN_DATA** | `OURS` | confirm_div.json not in repo |
| L80 | All tf_break 2020-2021: 15m -0.102 %, 1h -0.160 %, 4h -0.303 % | `confirm_div.json` | File not on disk | **NOT_IN_DATA** | `OURS` | confirm_div.json not in repo |

## cowen_q4_2026-10-31/event_study

| Line | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L4 | Spot daily bars 2017-08-17 to 2024-06-30: 2510 bars | `fetch_klines.py` | Not in EVENTS.csv | **NOT_IN_DATA** | `OURS` | Raw daily bars count, not in EVENTS.csv |
| L5 | Band: 20-week SMA and 21-week EMA | `COWEN_LEVELS_2026-10-31.md:21` | 72 to 76k band | **FOUND** | `SOURCED` | COWEN_LEVELS_2026-10-31.md:21, extract_bekghgecip8.md:73 |
| L6 | Trade stop: 1 R, target: 2 R, hold: 30 bars, fee: 5 bp | `PRE-REG.md` | stop 1R, target 2R, hold 30, fee 5bp | **FOUND** | `SOURCED` | PRE-REG.md:19-21, fees.py |
| L7 | Resamples: 2000, seed: 20261009, placebo d cycle: 8 values | `PRE-REG.md` | resamples 2000, seed 20261009 | **FOUND** | `OURS` | PRE-REG.md:28-30 |
| L13 | BOUNCE n: 21 | `EVENTS.csv` | 21 rows | **FOUND** | `OURS` | EVENTS.csv: idea == BOUNCE |
| L13 | BOUNCE Hit: 24% (target) | `EVENTS.csv` | 5 / 21 = 23.8 % | **FOUND** | `OURS` | EVENTS.csv: reason == target |
| L13 | BOUNCE Stop: 71% | `EVENTS.csv` | 15 / 21 = 71.4 % | **FOUND** | `OURS` | EVENTS.csv: reason == stop |
| L13 | BOUNCE Timeout: 5% | `EVENTS.csv` | 1 / 21 = 4.8 % | **FOUND** | `OURS` | EVENTS.csv: reason == timeout |
| L13 | BOUNCE Wins: 6 (29%) | `EVENTS.csv` | 6 / 21 = 28.6 % | **FOUND** | `OURS` | EVENTS.csv: net_R > 0 |
| L13 | BOUNCE Mean gross R: -0.18 | `EVENTS.csv` | mean(gross_R) = -0.181 | **FOUND** | `OURS` | EVENTS.csv: gross_R |
| L13 | BOUNCE Mean net R: -0.20 | `EVENTS.csv` | mean(net_R) = -0.200 | **FOUND** | `OURS` | EVENTS.csv: net_R |
| L13 | BOUNCE 95% range: -0.74 .. +0.37 | `EVENTS.csv` | Bootstrap range not saved in EVENTS.csv | **NOT_IN_DATA** | `OURS` | Bootstrap resample range computed at runtime |
| L13 | BOUNCE Placebo n: 38, mean net R: -0.11, diff: -0.09, range: -0.81..+0.60 | `EVENTS.csv` | Placebo events not saved in EVENTS.csv | **NOT_IN_DATA** | `OURS` | EVENTS.csv contains only real events (82 total) |
| L14 | LOSE n: 22 | `EVENTS.csv` | 22 rows | **FOUND** | `OURS` | EVENTS.csv: idea == LOSE |
| L14 | LOSE Hit: 55% (target) | `EVENTS.csv` | 12 / 22 = 54.5 % | **FOUND** | `OURS` | EVENTS.csv: reason == target |
| L14 | LOSE Stop: 41% | `EVENTS.csv` | 9 / 22 = 40.9 % | **FOUND** | `OURS` | EVENTS.csv: reason == stop |
| L14 | LOSE Timeout: 5% | `EVENTS.csv` | 1 / 22 = 4.5 % | **FOUND** | `OURS` | EVENTS.csv: reason == timeout |
| L14 | LOSE Wins: 13 (59%) | `EVENTS.csv` | 13 / 22 = 59.1 % | **FOUND** | `OURS` | EVENTS.csv: net_R > 0 |
| L14 | LOSE Mean gross R: +0.72 | `EVENTS.csv` | mean(gross_R) = +0.718 | **FOUND** | `OURS` | EVENTS.csv: gross_R |
| L14 | LOSE Mean net R: +0.69 | `EVENTS.csv` | mean(net_R) = +0.687 | **FOUND** | `OURS` | EVENTS.csv: net_R |
| L14 | LOSE 95% range: +0.07 .. +1.30 | `EVENTS.csv` | Bootstrap range not saved in EVENTS.csv | **NOT_IN_DATA** | `OURS` | Bootstrap resample range computed at runtime |
| L14 | LOSE Placebo n: 30, mean net R: -0.06, diff: +0.75, range: +0.02..+1.50 | `EVENTS.csv` | Placebo events not saved in EVENTS.csv | **NOT_IN_DATA** | `OURS` | EVENTS.csv contains only real events |
| L15 | FAKEOUT n: 20 | `EVENTS.csv` | 20 rows | **FOUND** | `OURS` | EVENTS.csv: idea == FAKEOUT |
| L15 | FAKEOUT Hit: 45% | `EVENTS.csv` | 9 / 20 = 45.0 % | **FOUND** | `OURS` | EVENTS.csv: reason == target |
| L15 | FAKEOUT Stop: 55% | `EVENTS.csv` | 11 / 20 = 55.0 % | **FOUND** | `OURS` | EVENTS.csv: reason == stop |
| L15 | FAKEOUT Timeout: 0% | `EVENTS.csv` | 0 / 20 = 0.0 % | **FOUND** | `OURS` | EVENTS.csv: reason == timeout |
| L15 | FAKEOUT Wins: 9 (45%) | `EVENTS.csv` | 9 / 20 = 45.0 % | **FOUND** | `OURS` | EVENTS.csv: net_R > 0 |
| L15 | FAKEOUT Mean gross R: +0.35 | `EVENTS.csv` | mean(gross_R) = +0.350 | **FOUND** | `OURS` | EVENTS.csv: gross_R |
| L15 | FAKEOUT Mean net R: +0.33 | `EVENTS.csv` | mean(net_R) = +0.330 | **FOUND** | `OURS` | EVENTS.csv: net_R |
| L15 | FAKEOUT 95% range: -0.28 .. +0.93 | `EVENTS.csv` | Bootstrap range not saved in EVENTS.csv | **NOT_IN_DATA** | `OURS` | Bootstrap resample range computed at runtime |
| L15 | FAKEOUT Placebo n: 22, mean net R: +0.21, diff: +0.12, range: -0.19..+0.46 | `EVENTS.csv` | Placebo events not saved in EVENTS.csv | **NOT_IN_DATA** | `OURS` | EVENTS.csv contains only real events |
| L16 | CATCHDOWN n: 19 | `EVENTS.csv` | 19 rows | **FOUND** | `OURS` | EVENTS.csv: idea == CATCHDOWN |
| L16 | CATCHDOWN Hit: 21% | `EVENTS.csv` | 4 / 19 = 21.1 % | **FOUND** | `OURS` | EVENTS.csv: reason == target |
| L16 | CATCHDOWN Stop: 79% | `EVENTS.csv` | 15 / 19 = 78.9 % | **FOUND** | `OURS` | EVENTS.csv: reason == stop |
| L16 | CATCHDOWN Timeout: 0% | `EVENTS.csv` | 0 / 19 = 0.0 % | **FOUND** | `OURS` | EVENTS.csv: reason == timeout |
| L16 | CATCHDOWN Wins: 4 (21%) | `EVENTS.csv` | 4 / 19 = 21.1 % | **FOUND** | `OURS` | EVENTS.csv: net_R > 0 |
| L16 | CATCHDOWN Mean gross R: -0.37 | `EVENTS.csv` | mean(gross_R) = -0.368 | **FOUND** | `OURS` | EVENTS.csv: gross_R |
| L16 | CATCHDOWN Mean net R: -0.40 | `EVENTS.csv` | mean(net_R) = -0.400 | **FOUND** | `OURS` | EVENTS.csv: net_R |
| L16 | CATCHDOWN 95% range: -0.87 .. +0.08 | `EVENTS.csv` | Bootstrap range not saved in EVENTS.csv | **NOT_IN_DATA** | `OURS` | Bootstrap resample range computed at runtime |
| L16 | CATCHDOWN Placebo n: 21, mean net R: -0.38, diff: -0.02, range: -0.62..+0.59 | `EVENTS.csv` | Placebo events not saved in EVENTS.csv | **NOT_IN_DATA** | `OURS` | EVENTS.csv contains only real events |
| L24 | BOUNCE per-year: 2018 (3: -1.01), 2019 (1: -1.03), 2020 (4: +0.29), 2021 (8: +0.11), 2022 (1: -1.03), 2023 (4: -0.28) | `EVENTS.csv` | Matches all 6 year cell means | **FOUND** | `OURS` | EVENTS.csv grouped by year for BOUNCE |
| L25 | LOSE per-year: 2018 (6: +1.48), 2019 (3: +0.97), 2020 (2: +0.48), 2021 (4: +0.17), 2022 (2: +1.97), 2023 (5: -0.43) | `EVENTS.csv` | Matches all 6 year cell means | **FOUND** | `OURS` | EVENTS.csv grouped by year for LOSE |
| L26 | FAKEOUT per-year: 2018 (1: +1.99), 2019 (4: +0.49), 2020 (4: -0.27), 2021 (4: +0.48), 2023 (5: +0.17), 2024 (2: +0.48) | `EVENTS.csv` | Matches all 6 year cell means | **FOUND** | `OURS` | EVENTS.csv grouped by year for FAKEOUT |
| L27 | CATCHDOWN per-year: 2018 (1: +1.98), 2019 (5: -1.02), 2020 (3: -1.02), 2022 (1: +1.97), 2023 (7: -0.61), 2024 (2: +0.48) | `EVENTS.csv` | Matches all 6 year cell means | **FOUND** | `OURS` | EVENTS.csv grouped by year for CATCHDOWN |

## tf_break_event_study_2026-10-30

| Line | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L3 | Rows 1m: 1,838,880 | `study.py` | Rows generated from archive | **FOUND** | `OURS` | study.py date range 2022-01-01..2025-06-30 |
| L3 | Round-trip taker fee: 0.10 % (regime A), maker: 0.04 % (regime D) | `fees.py` | 0.10% taker / 0.04% maker | **FOUND** | `SOURCED` | fees.py:BINANCE_TAKER, BINANCE_MAKER |
| L5 | W events: 6 H / 1 R / 10 W1 over 3.5 years | `output.md` | W: 6 H, 1 R, 10 W1 | **FOUND** | `OURS` | output.md:5-7, 63-65 |
| L5 | 1D events: 31 H / 20 R / 71 W1 | `output.md` | 1D: 31 H, 20 R, 71 W1 | **FOUND** | `OURS` | output.md:8-10, 66-68 |
| L13 | 4h follow H DEV: n=110, mean=-0.033%, SE=0.247% | `output.md` | n=110, net=-0.033%, CI=[-0.55, 0.42] | **FOUND** | `OURS` | output.md:11; SE derived from CI width / 3.92 |
| L14 | 4h follow H VAL: n=38, mean=0.414%, SE=0.384% | `output.md` | n=38, net=0.414%, CI=[-0.35, 1.16] | **FOUND** | `OURS` | output.md:11; SE derived from CI width / 3.92 |
| L15 | 4h fade R DEV: n=111, mean=-0.417%, SE=0.233% | `output.md` | n=111, net=-0.417%, CI=[-0.85, 0.06] | **FOUND** | `OURS` | output.md:12; SE derived from CI width / 3.92 |
| L16 | 4h fade R VAL: n=48, mean=-0.634%, SE=0.403% | `output.md` | n=48, net=-0.634%, CI=[-1.48, 0.10] | **FOUND** | `OURS` | output.md:12; SE derived from CI width / 3.92 |
| L17 | 4h fade W1 DEV: n=304, mean=-0.105%, SE=0.114% | `output.md` | n=304, net=-0.105%, CI=[-0.33, 0.12] | **FOUND** | `OURS` | output.md:13; SE derived from CI width / 3.92 |
| L18 | 4h fade W1 VAL: n=126, mean=-0.151%, SE=0.171% | `output.md` | n=126, net=-0.151%, CI=[-0.49, 0.18] | **FOUND** | `OURS` | output.md:13; SE derived from CI width / 3.92 |
| L19 | 1h follow H DEV: n=266, mean=0.003%, SE=0.084% | `output.md` | n=266, net=0.003%, CI=[-0.16, 0.16] | **FOUND** | `OURS` | output.md:14; SE derived from CI width / 3.92 |
| L20 | 1h follow H VAL: n=98, mean=-0.002%, SE=0.139% | `output.md` | n=98, net=-0.002%, CI=[-0.27, 0.28] | **FOUND** | `OURS` | output.md:14; SE derived from CI width / 3.92 |
| L21 | 1h fade R DEV: n=308, mean=-0.076%, SE=0.082% | `output.md` | n=308, net=-0.076%, CI=[-0.24, 0.08] | **FOUND** | `OURS` | output.md:15; SE derived from CI width / 3.92 |
| L22 | 1h fade R VAL: n=131, mean=-0.172%, SE=0.103% | `output.md` | n=131, net=-0.172%, CI=[-0.38, 0.03] | **FOUND** | `OURS` | output.md:15; SE derived from CI width / 3.92 |
| L23 | 1h fade W1 DEV: n=804, mean=-0.064%, SE=0.042% | `output.md` | n=804, net=-0.064%, CI=[-0.14, 0.02] | **FOUND** | `OURS` | output.md:16; SE derived from CI width / 3.92 |
| L24 | 1h fade W1 VAL: n=283, mean=-0.053%, SE=0.084% | `output.md` | n=283, net=-0.053%, CI=[-0.22, 0.11] | **FOUND** | `OURS` | output.md:16; SE derived from CI width / 3.92 |
| L25 | 15m follow H DEV: n=790, mean=-0.097%, SE=0.02% | `output.md` | n=790, net=-0.097%, CI=[-0.14, -0.06] | **FOUND** | `OURS` | output.md:17; SE derived from CI width / 3.92 |
| L26 | 15m follow H VAL: n=323, mean=-0.124%, SE=0.027% | `output.md` | n=323, net=-0.124%, CI=[-0.18, -0.07] | **FOUND** | `OURS` | output.md:17; SE derived from CI width / 3.92 |
| L27 | 15m fade R DEV: n=1393, mean=-0.069%, SE=0.017% | `output.md` | n=1393, net=-0.069%, CI=[-0.10, -0.03] | **FOUND** | `OURS` | output.md:18; SE derived from CI width / 3.92 |
| L28 | 15m fade R VAL: n=594, mean=-0.095%, SE=0.019% | `output.md` | n=594, net=-0.095%, CI=[-0.14, -0.06] | **FOUND** | `OURS` | output.md:18; SE derived from CI width / 3.92 |
| L29 | 15m fade W1 DEV: n=3055, mean=-0.122%, SE=0.011% | `output.md` | n=3055, net=-0.122%, CI=[-0.14, -0.10] | **FOUND** | `OURS` | output.md:19; SE derived from CI width / 3.92 |
| L30 | 15m fade W1 VAL: n=1146, mean=-0.103%, SE=0.017% | `output.md` | n=1146, net=-0.103%, CI=[-0.14, -0.07] | **FOUND** | `OURS` | output.md:19; SE derived from CI width / 3.92 |
| L38 | Finding 1: W1 is 55-60 % of events; hold share 4h 50%/44%, 1h 46%/43%, 15m 36%/35% | `output.md` | T1 W1%: 54.1-63.3%; T2 hold share: 49.8/44.2, 46.3/42.8, 36.2/35.2% | **FOUND** | `OURS` | output.md:28-43, 52-57 |
| L39 | Finding 2: Hold share real vs pseudo (15m 36.2 vs 34.6 DEV, 35.2 vs 33.3 VAL; 4h 49.8 vs 50.9; 1h 46.3 vs 40.0, 42.8 vs 35.5) | `output.md` | Matches all 6 comparisons in T2 | **FOUND** | `OURS` | output.md:52-57 |
| L40 | Finding 3: RSI drops 8-12 pts; taker flow 15m 0.18 H vs 0.18 R; vol spike 1h 3.85x vs 3.03x; RSI after 15m 36.8->47.2 (R), 34.1->36.4 (H); flow after -0.025 (R) | `output.md` | Matches all indicator medians in T3 | **FOUND** | `OURS` | output.md:73-77 |
| L41 | Finding 4: Break distance ATR (15m: 23.5/48.9 % DEV, 24.5/50.3 % VAL; 4h 36.9/62.7 DEV, 25.6/62.8 VAL) | `output.md` | Matches all 8 cut shares in T4 | **FOUND** | `OURS` | output.md:89,97 |
| L42 | Finding 5: Gross continuation within ~0.1 % at 15m and 1h; maker regime D 0.04 % | `output.md` | Matches T5 continuation means and T0 regime D nets | **FOUND** | `OURS` | output.md:14-19, 116-127 |
| L43 | Finding 6: 1D W1 DEV +0.60 %, 4h H VAL +0.41 % | `output.md` | 1D W1 DEV 0.597 % (rounds to 0.60), 4h H VAL 0.414 % (rounds to 0.41) | **FOUND** | `OURS` | output.md:10, 11 |

