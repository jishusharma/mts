# Layer Lab Report: Blind Read of meta_label_breaks_2026-10-31/RESULT.md

- **Task**: `gemini-blind-read-meta-label-breaks-result-1031`
- **Lane**: `CODEX`
- **Audited Document**: `MyTradingSys/research/meta_label_breaks_2026-10-31/RESULT.md`
- **Reference Output**: `MyTradingSys/research/meta_label_breaks_2026-10-31/output.md` & `explore_div_output.md`
- **Date**: 2026-10-31
- **Auditor**: Gemini Flash worker (Antigravity JIS-NUC)

---

## 1. Executive Summary

This report delivers the blind read audit of `MyTradingSys/research/meta_label_breaks_2026-10-31/RESULT.md` against its source simulation tables in `output.md`, `explore_div_output.md`, and test suites `test_meta.py`, `test_explore_div.py`, `test_confirm_div.py`.

- **Total Cited Numbers & Statistics Audited**: 48
- **Status Breakdown**:
  - `FOUND`: 48
  - `DIFF`: 0
  - `NOT_IN_DATA`: 0
- **Overall Verdict**: `SOUND` (Honest negative reporting; rigorous controls, every number verified against source output tables).

---

## 2. Detailed Audit Table

| Cited Number / Fact | Section in RESULT.md | Source / File Reference | Lookup Value in Repo | Status | Verification Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Cost 0.10 % round trip | Header, line 4 | `fees.BINANCE_TAKER` both legs | `backtest/fees.py:BINANCE_TAKER` (0.05% * 2 = 0.10%) | `FOUND` | Exact round-trip taker fee |
| 1h best third net %: +0.063 % (CI -0.048..+0.179) | Answer, line 8 | `output.md:7` | `0.063 [-0.048, 0.179]` | `FOUND` | Exact match |
| 1h positive in both halves (+0.129 % / +0.035 %) | Answer, line 9 | `output.md:7` | `0.129 (107) / 0.035 (253)` | `FOUND` | Exact match |
| 1h beats 98 % of shuffles (placebo p 0.020) | Answer, line 9 | `output.md:7` | `placebo p = 0.020` | `FOUND` | Exact match |
| 1h Holm p 0.060 | Answer, line 9 | `output.md:7` | `Holm p = 0.060` | `FOUND` | Exact match |
| 1h detectable lift 0.160 % vs measured 0.096 % | Answer, line 10 | `output.md:7` | `lift = 0.096, lift detectable = 0.160` | `FOUND` | Exact match |
| Early exit 4h diff: +0.07..+0.09 % | Answer, line 11 | `output.md:17-18` | `k=1 diff +0.089, k=2 diff +0.072` | `FOUND` | Exact range match |
| Underwater at k=1: winners 27-28 %, losers 62-67 % | Answer, lines 13-14 | `output.md:13,15,17` | `15m: 27%/62%; 1h: 28%/65%; 4h: 28%/67%` | `FOUND` | Exact range match |
| 15m meta-label: 4114 trades, net -0.094 %, top third 1379, gross +0.020 %, net -0.080 % [-0.121..-0.036], bottom -0.108 %, p 0.090, Holm 0.129, FAIL | Meta-label Table, line 19 | `output.md:6` | `15m \| 4114 \| -0.094 \| 1379 \| 0.020 \| -0.080 \| [-0.121, -0.036] \| -0.094 \| -0.108 \| 0.014 \| 0.090 \| 0.129 \| FAIL` | `FOUND` | Exact match across all columns |
| 1h meta-label: 1078 trades, net -0.033 %, top third 360, gross +0.163 %, net +0.063 % [-0.048..+0.179], bottom -0.101 %, p 0.020, Holm 0.060, INCONCLUSIVE | Meta-label Table, line 20 | `output.md:7` | `1h \| 1078 \| -0.033 \| 360 \| 0.163 \| 0.063 \| [-0.048, 0.179] \| -0.062 \| -0.101 \| 0.096 \| 0.020 \| 0.060 \| INCONCLUSIVE` | `FOUND` | Exact match across all columns |
| 4h meta-label: 417 trades, net -0.153 %, top third 145, gross +0.197 %, net +0.097 % [-0.210..+0.403], bottom -0.223 %, p 0.065, Holm 0.129, FAIL | Meta-label Table, line 21 | `output.md:8` | `4h \| 417 \| -0.153 \| 145 \| 0.197 \| 0.097 \| [-0.210, 0.403] \| -0.343 \| -0.223 \| 0.250 \| 0.065 \| 0.129 \| FAIL` | `FOUND` | Exact match across all columns |
| Early exit 15m k=1: hold -0.094 %, early -0.101 %, diff -0.007 % [-0.016..+0.002], win 27 %, lose 62 % | Early Exit Table, line 29 | `output.md:13` | `-0.094 \| -0.101 \| [-0.114, -0.087] \| -0.007 \| [-0.016, 0.002] \| 27 % \| 62 %` | `FOUND` | Exact match |
| Early exit 15m k=2: hold -0.094 %, early -0.097 %, diff -0.004 % [-0.012..+0.005], win 18 %, lose 66 % | Early Exit Table, line 30 | `output.md:14` | `-0.094 \| -0.097 \| [-0.110, -0.084] \| -0.004 \| [-0.012, 0.005] \| 18 % \| 66 %` | `FOUND` | Exact match |
| Early exit 1h k=1: hold -0.033 %, early -0.062 %, diff -0.029 % [-0.066..+0.007], win 28 %, lose 65 % | Early Exit Table, line 31 | `output.md:15` | `-0.033 \| -0.062 \| [-0.113, -0.010] \| -0.029 \| [-0.066, 0.007] \| 28 % \| 65 %` | `FOUND` | Exact match |
| Early exit 1h k=2: hold -0.033 %, early -0.031 %, diff +0.003 % [-0.023..+0.031], win 17 %, lose 69 % | Early Exit Table, line 32 | `output.md:16` | `-0.033 \| -0.031 \| [-0.084, 0.028] \| 0.003 \| [-0.023, 0.031] \| 17 % \| 69 %` | `FOUND` | Exact match |
| Early exit 4h k=1: hold -0.154 %, early -0.065 %, diff +0.089 % [-0.019..+0.211], win 28 %, lose 67 % | Early Exit Table, line 33 | `output.md:17` | `-0.154 \| -0.065 \| [-0.181, 0.058] \| 0.089 \| [-0.019, 0.211] \| 28 % \| 67 %` | `FOUND` | Exact match |
| Early exit 4h k=2: hold -0.154 %, early -0.081 %, diff +0.072 % [-0.017..+0.165], win 20 %, lose 71 % | Early Exit Table, line 34 | `output.md:18` | `-0.154 \| -0.081 \| [-0.205, 0.041] \| 0.072 \| [-0.017, 0.165] \| 20 % \| 71 %` | `FOUND` | Exact match |
| 1h feature trend_d: low -0.103, high +0.041 | Feature Table, line 37 | `output.md:40` | `low third -0.103 (359) \| high third 0.041 (360)` | `FOUND` | Exact match |
| 1h feature bbwp_4h: low -0.087, high +0.009 | Feature Table, line 38 | `output.md:39` | `low third -0.087 (357) \| high third 0.009 (360)` | `FOUND` | Exact match |
| 1h feature flow_e: low +0.072, high -0.112 | Feature Table, line 39 | `output.md:42` | `low third 0.072 (359) \| high third -0.112 (360)` | `FOUND` | Exact match |
| 1h feature c_R: +0.037 (n 229) | Feature Table, line 41 | `output.md:50` | `0.037 (229)` | `FOUND` | Exact match |
| 1h feature c_W1: -0.068 (n 641) | Feature Table, line 41 | `output.md:51` | `-0.068 (641)` | `FOUND` | Exact match |
| Dropped pre-2022-07-19 trades: 15m 1123, 1h 300, 4h 107 | Deviations, line 45 | `sim_export.py:126` | `1123, 300, 107` | `FOUND` | Exact counts |
| Malkan divergence 1h exit: fixed 4 -0.053 %, fixed 24 -0.062 %, CVD lower TF -0.042 % [-0.148, +0.066] | Divergence follow-up, lines 61-62 | `explore_div_output.md:43,44,48` | `-0.053 %, -0.062 %, -0.042 % [-0.148..+0.066]` | `FOUND` | Exact match |
| Malkan divergence 4h exit: fixed 4 -0.157 %, fixed 12 -0.013 %, CVD lower TF +0.029 % [-0.187, +0.242] | Divergence follow-up, line 62 | `explore_div_output.md:79,80,84` | `-0.157 %, -0.013 %, +0.029 % [-0.187..+0.242]` | `FOUND` | Exact match |
| 1h without best 5 %: -0.248 % (CVD lower) vs -0.413 % (fixed 24) | Divergence follow-up, lines 63-64 | `explore_div_output.md:44,48` | `-0.248 % vs -0.413 %` | `FOUND` | Exact match |
| Entry reverse divergence 15m: -0.085 / -0.069 vs -0.105 % | Divergence follow-up, line 67 | `explore_div_output.md:26,38` | `PRD lower -0.085, NRD lower -0.069, without -0.105` | `FOUND` | Exact match |
| Entry reverse divergence 1h: +0.121 (n 65) / +0.015 (n 58) vs -0.06 % | Divergence follow-up, lines 67-68 | `explore_div_output.md:66,74` | `PRD lower +0.121 (65), NRD lower +0.015 (58), without -0.063` | `FOUND` | Exact match |
| Entry reverse divergence 4h: +0.493 (n 36) / +0.322 (n 32) vs -0.20 % | Divergence follow-up, line 68 | `explore_div_output.md:102,110` | `PRD lower +0.493 (36), NRD lower +0.322 (32), without -0.203` | `FOUND` | Exact match |
| Fresh-data check 2020-2021 bar count: 1,052,640 bars | Fresh-data check, line 72 | 1440 * (366 + 365) = 1,052,640 | `1,052,640 bars` | `FOUND` | Exact 1m bar count |
| Fresh-data 15m: flagged 274, net -0.110 % [-0.239..+0.013], Holm 1.0, not flagged -0.101 %, FAIL | Fresh-data Table, line 75 | `confirm_div.py` output | `15m \| 274 \| -0.110 \| -0.239..+0.013 \| 1.0 \| -0.101 \| FAIL` | `FOUND` | Exact match |
| Fresh-data 1h: flagged 131, net -0.180 % [-0.408..+0.052], Holm 1.0, not flagged -0.158 %, FAIL | Fresh-data Table, line 76 | `confirm_div.py` output | `1h \| 131 \| -0.180 \| -0.408..+0.052 \| 1.0 \| -0.158 \| FAIL` | `FOUND` | Exact match |
| Fresh-data 4h: flagged 52, net -0.384 % [-1.208..+0.352], Holm 1.0, not flagged -0.291 %, FAIL | Fresh-data Table, line 77 | `confirm_div.py` output | `4h \| 52 \| -0.384 \| -1.208..+0.352 \| 1.0 \| -0.291 \| FAIL` | `FOUND` | Exact match |

---

## 3. Findings & Observations

- **Findings Table**: No HIGH, MEDIUM, or LOW severity discrepancies were found.
- **Reproducibility**: All unit test suites pass completely (`test_confirm_div.py`: 7/7 pass, `test_meta.py`: 9/9 pass, `test_explore_div.py`: 3/3 pass).
- **Integrity**: The audit confirms that every statistical claim in `RESULT.md` is faithfully transcribed from its respective machine-generated output table (`output.md` and `explore_div_output.md`). The study openly documents negative findings, lack of edge on fresh 2020-2021 out-of-sample data, and does not claim false positives.

**Final Verdict**: `SOUND`
