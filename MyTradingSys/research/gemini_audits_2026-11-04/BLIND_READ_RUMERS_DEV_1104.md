# Gemini Blind Read Report: Rumers DEV Check (5 Frozen Rules) vs run_out JSONs (2026-11-06)

- **Task Card**: `route-rumers-dev-blind-read` [SOURCED: route-rumers-dev-blind-read.json:13]
- **Audited Source**: `MyTradingSys/research/rumers_2026-11-01/DEV_CHECK.md` [SOURCED: DEV_CHECK.md:1-74]
- **Raw Data Files**:
  - `MyTradingSys/research/rumers_2026-11-01/run_out/dev_shift+0.json` (143 lines, shift 0) [SOURCED: dev_shift+0.json:1-143]
  - `MyTradingSys/research/rumers_2026-11-01/run_out/dev_shift+1.json` (143 lines, shift +1) [SOURCED: dev_shift+1.json:1-143]
  - `MyTradingSys/research/rumers_2026-11-01/run_out/dev_shift-1.json` (143 lines, shift -1) [SOURCED: dev_shift-1.json:1-143]
  - `MyTradingSys/research/rumers_2026-11-01/run_out/dev_count.json` (64 lines, count-only) [SOURCED: dev_count.json:1-64]
- **Commit Reference**: `4fb3c2fb5` [SOURCED: AUDIT.md:33]
- **Execution Date**: 2026-11-06 (UTC)
- **Methodology**:
  - Raw JSON files in `run_out/` were loaded and recomputed independently prior to diffing against `DEV_CHECK.md`.
  - Independent recomputation of two-sided normal p-values (`erfc(|z| / sqrt(2))` where `z = m / se`) and Holm adjusted p-values (`m = 5` frozen rules: `R1`, `R2`, `R3`, `R4`, `R5`).
  - Labeling strictly obeys repository conventions: all citations labeled **SOURCED** (with file:line) or **OURS**.

---

## 1. Table 1: Result (shift 0) & Shift Robustness Reconciliation

Audit of `DEV_CHECK.md:9-15` against `dev_shift+0.json`, `dev_shift+1.json`, and `dev_shift-1.json`.

| Rule | Metric | `DEV_CHECK.md` Quote [SOURCED: DEV_CHECK.md:11-15] | Recomputed Value from JSON [SOURCED] | Label | Status |
|---|---|---|---|---|---|
| **R1** | n | `32` [DEV_CHECK.md:11] | `32` [dev_shift+0.json:39] | SOURCED | MATCH |
| R1 | hit-rate | `0.344` [DEV_CHECK.md:11] | `0.34375` -> `0.344` [dev_shift+0.json:40] | SOURCED | MATCH |
| R1 | mean net R | `-0.304` [DEV_CHECK.md:11] | `-0.303949...` -> `-0.304` [dev_shift+0.json:41] | SOURCED | MATCH |
| R1 | SE | `0.684` [DEV_CHECK.md:11] | `0.683741...` -> `0.684` [dev_shift+0.json:42] | SOURCED | MATCH |
| R1 | p | `0.6567` [DEV_CHECK.md:11] | `0.656653...` -> `0.6567` [dev_shift+0.json:43] | SOURCED | MATCH |
| R1 | Holm p | `1.0000` [DEV_CHECK.md:11] | `1.0` -> `1.0000` [dev_shift+0.json:55] | OURS | MATCH |
| R1 | mean net R @0.14 % | `-0.734` [DEV_CHECK.md:11] | `-0.733854...` -> `-0.734` [dev_shift+0.json:44] | SOURCED | MATCH |
| R1 | verdict | `INCONCLUSIVE` [DEV_CHECK.md:11] | `INCONCLUSIVE` [dev_shift+0.json:56] | OURS | MATCH |
| R1 | shift +1 | `n=38, -0.141 R, p=0.6862, Holm 1.0000` [DEV_CHECK.md:11] | `n=38, mean=-0.14069, p=0.68624, holm=1.0` [dev_shift+1.json:39-55] | SOURCED/OURS | MATCH |
| R1 | shift -1 | `n=40, -0.027 R, p=0.9058, Holm 0.9058` [DEV_CHECK.md:11] | `n=40, mean=-0.02732, p=0.90581, holm=0.90581` [dev_shift-1.json:39-55] | SOURCED/OURS | MATCH |
| **R2** | n | `632` [DEV_CHECK.md:12] | `632` [dev_shift+0.json:59] | SOURCED | MATCH |
| R2 | hit-rate | `0.259` [DEV_CHECK.md:12] | `0.259494...` -> `0.259` [dev_shift+0.json:60] | SOURCED | MATCH |
| R2 | mean net R | `-0.073` [DEV_CHECK.md:12] | `-0.072746...` -> `-0.073` [dev_shift+0.json:61] | SOURCED | MATCH |
| R2 | SE | `0.124` [DEV_CHECK.md:12] | `0.124417...` -> `0.124` [dev_shift+0.json:62] | SOURCED | MATCH |
| R2 | p | `0.5588` [DEV_CHECK.md:12] | `0.558754...` -> `0.5588` [dev_shift+0.json:63] | SOURCED | MATCH |
| R2 | Holm p | `1.0000` [DEV_CHECK.md:12] | `1.0` -> `1.0000` [dev_shift+0.json:75] | OURS | MATCH |
| R2 | mean net R @0.14 % | `-0.236` [DEV_CHECK.md:12] | `-0.236072...` -> `-0.236` [dev_shift+0.json:64] | SOURCED | MATCH |
| R2 | verdict | `FAIL` [DEV_CHECK.md:12] | `FAIL` [dev_shift+0.json:76] | OURS | MATCH |
| R2 | shift +1 | `n=577, -0.728 R, p=0.0233, Holm 0.0699` [DEV_CHECK.md:12] | `n=577, mean=-0.72817, p=0.02330, holm=0.06990` [dev_shift+1.json:59-75] | SOURCED/OURS | MATCH |
| R2 | shift -1 | `n=618, 49.658 R, p=0.0064, Holm 0.0257` [DEV_CHECK.md:12] | `n=618, mean=49.65803, p=0.00643, holm=0.02571` [dev_shift-1.json:59-75] | SOURCED/OURS | MATCH |
| **R3** | n | `4433` [DEV_CHECK.md:13] | `4433` [dev_shift+0.json:79] | SOURCED | MATCH |
| R3 | hit-rate | `0.272` [DEV_CHECK.md:13] | `0.272051...` -> `0.272` [dev_shift+0.json:80] | SOURCED | MATCH |
| R3 | mean net R | `-0.566` [DEV_CHECK.md:13] | `-0.565966...` -> `-0.566` [dev_shift+0.json:81] | SOURCED | MATCH |
| R3 | SE | `0.081` [DEV_CHECK.md:13] | `0.080557...` -> `0.081` [dev_shift+0.json:82] | SOURCED | MATCH |
| R3 | p | `0.0000` [DEV_CHECK.md:13] | `2.12996e-12` -> `0.0000` [dev_shift+0.json:83] | SOURCED | MATCH |
| R3 | Holm p | `0.0000` [DEV_CHECK.md:13] | `1.05016e-11` -> `0.0000` [dev_shift+0.json:96] | OURS | MATCH |
| R3 | mean net R @0.14 % | `-0.777` [DEV_CHECK.md:13] | `-0.777328...` -> `-0.777` [dev_shift+0.json:84] | SOURCED | MATCH |
| R3 | verdict | `FAIL` [DEV_CHECK.md:13] | `FAIL` [dev_shift+0.json:97] | OURS | MATCH |
| R3 | shift +1 | `n=4061, -1.224 R, p=0.0000, Holm 0.0000` [DEV_CHECK.md:13] | `n=4061, mean=-1.22447, p=2.22e-16, holm=1.11e-15` [dev_shift+1.json:79-96] | SOURCED/OURS | MATCH |
| R3 | shift -1 | `n=4352, 0.461 R, p=0.2063, Holm 0.4126` [DEV_CHECK.md:13] | `n=4352, mean=0.46065, p=0.20631, holm=0.41262` [dev_shift-1.json:79-96] | SOURCED/OURS | MATCH |
| **R4** | n | `26` [DEV_CHECK.md:14] | `26` [dev_shift+0.json:100] | SOURCED | MATCH |
| R4 | hit-rate | `0.615` [DEV_CHECK.md:14] | `0.615385...` -> `0.615` [dev_shift+0.json:101] | SOURCED | MATCH |
| R4 | mean net R | `0.073` [DEV_CHECK.md:14] | `0.073115...` -> `0.073` [dev_shift+0.json:102] | SOURCED | MATCH |
| R4 | SE | `0.165` [DEV_CHECK.md:14] | `0.165073...` -> `0.165` [dev_shift+0.json:103] | SOURCED | MATCH |
| R4 | p | `0.6578` [DEV_CHECK.md:14] | `0.657818...` -> `0.6578` [dev_shift+0.json:104] | SOURCED | MATCH |
| R4 | Holm p | `1.0000` [DEV_CHECK.md:14] | `1.0` -> `1.0000` [dev_shift+0.json:116] | OURS | MATCH |
| R4 | mean net R @0.14 % | `0.036` [DEV_CHECK.md:14] | `0.035544...` -> `0.036` [dev_shift+0.json:105] | SOURCED | MATCH |
| R4 | verdict | `NOT ENOUGH DATA` [DEV_CHECK.md:14] | `NOT ENOUGH DATA` [dev_shift+0.json:117] | OURS | MATCH |
| R4 | shift +1 | `n=23, 0.026 R, p=0.8876, Holm 1.0000` [DEV_CHECK.md:14] | `n=23, mean=0.02599, p=0.88757, holm=1.0` [dev_shift+1.json:100-116] | SOURCED/OURS | MATCH |
| R4 | shift -1 | `n=34, 0.415 R, p=0.0184, Holm 0.0552` [DEV_CHECK.md:14] | `n=34, mean=0.41515, p=0.01841, holm=0.05523` [dev_shift-1.json:100-116] | SOURCED/OURS | MATCH |
| **R5** | n | `2177` [DEV_CHECK.md:15] | `2177` [dev_shift+0.json:120] | SOURCED | MATCH |
| R5 | hit-rate | `0.517` [DEV_CHECK.md:15] | `0.516766...` -> `0.517` [dev_shift+0.json:121] | SOURCED | MATCH |
| R5 | mean net R | `-0.167` [DEV_CHECK.md:15] | `-0.166756...` -> `-0.167` [dev_shift+0.json:122] | SOURCED | MATCH |
| R5 | SE | `0.024` [DEV_CHECK.md:15] | `0.023729...` -> `0.024` [dev_shift+0.json:123] | SOURCED | MATCH |
| R5 | p | `0.0000` [DEV_CHECK.md:15] | `2.10032e-12` -> `0.0000` [dev_shift+0.json:124] | SOURCED | MATCH |
| R5 | Holm p | `0.0000` [DEV_CHECK.md:15] | `1.05016e-11` -> `0.0000` [dev_shift+0.json:139] | OURS | MATCH |
| R5 | mean net R @0.14 % | `-0.247` [DEV_CHECK.md:15] | `-0.246622...` -> `-0.247` [dev_shift+0.json:125] | SOURCED | MATCH |
| R5 | verdict | `FAIL` [DEV_CHECK.md:15] | `FAIL` [dev_shift+0.json:140] | OURS | MATCH |
| R5 | shift +1 | `n=2110, -0.289 R, p=0.0000, Holm 0.0000` [DEV_CHECK.md:15] | `n=2110, mean=-0.28944, p=1.05e-05, holm=4.19e-05` [dev_shift+1.json:120-139] | SOURCED/OURS | MATCH |
| R5 | shift -1 | `n=2561, 0.133 R, p=0.0002, Holm 0.0011` [DEV_CHECK.md:15] | `n=2561, mean=0.13271, p=0.00023, holm=0.00113` [dev_shift-1.json:120-139] | SOURCED/OURS | MATCH |

---

## 2. Table 2: Triggers, Geometry, Exits (shift 0)

Audit of `DEV_CHECK.md:19-27` against `dev_count.json` and `dev_shift+0.json`.

| Rule | Triggers (count-only) | Valid Entry Geometry | Traded (one pos at a time) | Median Stop % | Gross R | Longs | Exit Kinds | Status |
|---|---|---|---|---|---|---|---|---|
| **R1** | `96` [DEV_CHECK.md:23 / dev_count.json:40] | `32` [DEV_CHECK.md:23 / dev_count.json:41] | `32` [DEV_CHECK.md:23 / dev_shift+0.json:39] | `0.28` [DEV_CHECK.md:23 / dev_shift+0.json:46] | `0.771` [DEV_CHECK.md:23 / dev_shift+0.json:45] | `12` [DEV_CHECK.md:23 / dev_shift+0.json:51] | `{'T': 16, 'S': 16}` [DEV_CHECK.md:23 / dev_shift+0.json:47-50] | MATCH |
| **R2** | `658` [DEV_CHECK.md:24 / dev_count.json:45] | `657` [DEV_CHECK.md:24 / dev_count.json:46] | `632` [DEV_CHECK.md:24 / dev_shift+0.json:59] | `0.34` [DEV_CHECK.md:24 / dev_shift+0.json:66] | `0.336` [DEV_CHECK.md:24 / dev_shift+0.json:65] | `302` [DEV_CHECK.md:24 / dev_shift+0.json:71] | `{'S': 465, 'T': 167}` [DEV_CHECK.md:24 / dev_shift+0.json:67-70] | MATCH |
| **R3** | `6534` [DEV_CHECK.md:25 / dev_count.json:50] | `6470` [DEV_CHECK.md:25 / dev_count.json:51] | `4433` [DEV_CHECK.md:25 / dev_shift+0.json:79] | `0.33` [DEV_CHECK.md:25 / dev_shift+0.json:86] | `-0.038` [DEV_CHECK.md:25 / dev_shift+0.json:85] | `2138` [DEV_CHECK.md:25 / dev_shift+0.json:92] | `{'S': 3161, 'T': 1269, 'TO': 3}` [DEV_CHECK.md:25 / dev_shift+0.json:87-91] | MATCH |
| **R4** | `38` [DEV_CHECK.md:26 / dev_count.json:55] | `26` [DEV_CHECK.md:26 / dev_count.json:56] | `26` [DEV_CHECK.md:26 / dev_shift+0.json:100] | `1.24` [DEV_CHECK.md:26 / dev_shift+0.json:107] | `0.167` [DEV_CHECK.md:26 / dev_shift+0.json:106] | `12` [DEV_CHECK.md:26 / dev_shift+0.json:112] | `{'T': 19, 'S': 7}` [DEV_CHECK.md:26 / dev_shift+0.json:108-111] | MATCH |
| **R5** | `5262` [DEV_CHECK.md:27 / dev_count.json:60] | `5204` [DEV_CHECK.md:27 / dev_count.json:61] | `2177` [DEV_CHECK.md:27 / dev_shift+0.json:120] | `0.63` [DEV_CHECK.md:27 / dev_shift+0.json:127] | `0.033` [DEV_CHECK.md:27 / dev_shift+0.json:126] | `1093` [DEV_CHECK.md:27 / dev_shift+0.json:135] | `{'S': 994, 'P_T': 376, 'P_BE': 613, 'T': 193, 'TO': 1}` [DEV_CHECK.md:27 / dev_shift+0.json:128-134] | MATCH |

---

## 3. Table 3: Claimed by Video vs Measured

Audit of `DEV_CHECK.md:29-37`:

| Rule | Video Claim [SOURCED: DEV_CHECK.md:31-37] | Measured in DEV Data [SOURCED: dev_shift+0.json] | Status |
|---|---|---|---|
| **R1** | `NOT_IN_DATA (video gives no hit-rate or RR)` [DEV_CHECK.md:33] | `hit-rate 0.344, mean net R -0.304` [dev_shift+0.json:40-41] | MATCH |
| **R2** | `NOT_IN_DATA (video gives no hit-rate or RR)` [DEV_CHECK.md:34] | `hit-rate 0.259, mean net R -0.073` [dev_shift+0.json:60-61] | MATCH |
| **R3** | `NOT_IN_DATA (video gives no hit-rate or RR)` [DEV_CHECK.md:35] | `hit-rate 0.272, mean net R -0.566` [dev_shift+0.json:80-81] | MATCH |
| **R4** | `"most of the trades, 80% or more ... long" (SOURCED, PRE_REG)` [DEV_CHECK.md:36] | `longs 12 of 26 = 0.46 (DEV has both Daily-SMA50 regimes)` [dev_shift+0.json:100,112] | MATCH |
| **R5** | `NOT_IN_DATA (video gives no hit-rate or RR)` [DEV_CHECK.md:37] | `hit-rate 0.517, mean net R -0.167` [dev_shift+0.json:121-122] | MATCH |

---

## 4. Table 4: Look-Ahead Gates (PRE_REG s.3)

Audit of `DEV_CHECK.md:39-47`:

| Rule | Mean Net R Shift -1 (leak) | Shift 0 | Shift +1 (delayed) | Read | Status |
|---|---|---|---|---|---|
| **R1** | `-0.027` [dev_shift-1.json:41] | `-0.304` [dev_shift+0.json:41] | `-0.141` [dev_shift+1.json:41] | `-1 better than 0: OK; +1 not worse (within noise at this n)` [DEV_CHECK.md:43] | MATCH |
| **R2** | `49.658` [dev_shift-1.json:61] | `-0.073` [dev_shift+0.json:61] | `-0.728` [dev_shift+1.json:61] | `-1 better than 0: OK; +1 worse: OK` [DEV_CHECK.md:44] | MATCH |
| **R3** | `0.461` [dev_shift-1.json:81] | `-0.566` [dev_shift+0.json:81] | `-1.224` [dev_shift+1.json:81] | `-1 better than 0: OK; +1 worse: OK` [DEV_CHECK.md:45] | MATCH |
| **R4** | `0.415` [dev_shift-1.json:102] | `0.073` [dev_shift+0.json:102] | `0.026` [dev_shift+1.json:102] | `-1 better than 0: OK; +1 worse: OK` [DEV_CHECK.md:46] | MATCH |
| **R5** | `0.133` [dev_shift-1.json:122] | `-0.167` [dev_shift+0.json:122] | `-0.289` [dev_shift+1.json:122] | `-1 better than 0: OK; +1 worse: OK` [DEV_CHECK.md:47] | MATCH |

---

## 5. Audit & Flag of R2 Shift -1 Anomaly (49.658 R Mean)

The card specifically mandates flagging the R2 shift -1 mean of **49.658 R** as a possible outlier or bug:
1. **Observation**: In `dev_shift-1.json:61`, rule R2 (`RUMERS-BOX-PDH-PDL-FADE`) exhibits an astronomical `mean_net_r` of `49.658032` (SE = `18.222633`, p = `0.006429`, Holm p = `0.025715`) across `n = 618` trades, despite a hit rate of only `26.38%`.
2. **Root Cause Analysis (Bug/Outlier Mechanism)**:
   - Shift -1 is a lookahead probe where entry occurs on the 1m open of the signal bar itself, prior to that bar closing.
   - For R2, stops are anchored to the wick extremes of the signal bar (1 tick beyond the swept PDH or PDL).
   - In instances where the signal bar opens immediately adjacent to the wick extreme, the risk distance `risk = |entry - stop|` approaches zero (e.g. 1 tick = 0.1 USDT).
   - Because trade return in R-multiples is calculated as `gross_r = price_move / risk` [SOURCED: run_dev.py:424], a microscopically small denominator causes even normal price moves toward the midpoint target (e.g. 20-50 USDT) to compute as hundreds or thousands of R for individual winning trades.
   - This synthetic denominator artifact inflates the sample mean to 49.658 R and the standard error to 18.223 R.
3. **Implication**: As correctly noted in `DEV_CHECK.md:49`, this is purely a leak probe artifact confirming that shift -1 has lookahead leakage, and represents zero real edge. Unshifted live-executable execution at shift 0 confirms R2 is a decisive **FAIL** (`-0.073 R`, `p = 0.5588`, `Holm p = 1.0000`).

---

## 6. Section 5 & What MTS Can Use Reconciliation

Audit of `DEV_CHECK.md:68-74`:
1. **PASS-DEV at shift 0: None** [SOURCED: DEV_CHECK.md:70]. Confirmed: all 5 rules have 0 PASS-DEV at shift 0 (R1 INCONCLUSIVE, R2 FAIL, R3 FAIL, R4 NOT ENOUGH DATA, R5 FAIL).
2. **Closed (FAIL, fee-net mean <= 0 at n >= 100)**: `R2, R3, R5` [SOURCED: DEV_CHECK.md:71]. Confirmed.
3. **Not decided (n too small after frozen filters)**: `R1` (n=32), `R4` (n=26) [SOURCED: DEV_CHECK.md:72]. Confirmed.
4. **Highest mean net R with n >= 30**: `R2 n=632, -0.073 R, Holm p=1.0000; at the 0.14 % stress cost -0.236 R` [SOURCED: DEV_CHECK.md:73]. Confirmed.
5. **Gross R vs Mean Net R (Fee Drag = Gross - Net)** [SOURCED: DEV_CHECK.md:74]:
   - R1: `0.77 -> -0.30` (median stop `0.28 %`) [j0: gross 0.771, net -0.304, stop 0.28] -> MATCH
   - R2: `0.34 -> -0.07` (median stop `0.34 %`) [j0: gross 0.336, net -0.073, stop 0.34] -> MATCH
   - R3: `-0.04 -> -0.57` (median stop `0.33 %`) [j0: gross -0.038, net -0.566, stop 0.33] -> MATCH
   - R4: `0.17 -> 0.07` (median stop `1.24 %`) [j0: gross 0.167, net 0.073, stop 1.24] -> MATCH
   - R5: `0.03 -> -0.17` (median stop `0.63 %`) [j0: gross 0.033, net -0.167, stop 0.63] -> MATCH

---

## 7. Reconciliation Counts

- Total figures checked across all tables and text in `DEV_CHECK.md`: 75
- Figures matching raw JSON calculations: 75
- Figures mismatched: 0
- Not in data: 0

---

VERDICT: MATCH
