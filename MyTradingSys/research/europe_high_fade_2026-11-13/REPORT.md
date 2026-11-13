# Europe high fade, full-history re-test (2026-11-13)

Rule, data, split, fee, placebo and verdicts as frozen in PRE_REG.md (committed before the run). The Live Aid code (levelstory.js, pulse.js, live_aid_indicators.js) ran unchanged; no parameter was searched.

**VERDICT: FAIL** - BTC VALIDATION n 1327, hit 48.7 %, fee-net mean R -0.291 [-0.477, -0.098], placebo mean -0.326 (p95 -0.195).
- Replication ETH: FAIL (VALIDATION n 746, mean R -0.468).
- Replication SOL: FAIL (VALIDATION n 302, mean R +0.094).

## Cell BTC  (2019-01-01 .. 2026-11-10, 2871 days; VALIDATION from 2024-07-02)
- Node run: {"bars5": 826496, "bars15": 275498, "steps": 825590, "idea_steps": 292373, "events": 66559, "first": 1546300800000, "last": 1794354900000}; flag events 4219, skipped (gap in 60-min window) 0, level-vs-independent-Europe-high mismatches 0
- Regime mix: up 41.1 % / down 32.2 % / range 26.8 % (days with a regime: 2851, rule in PRE_REG)

| slice | n | hit (gross) | fee-net mean bps [95 % CI] | fee-net mean R [95 % CI] | R at 10 bp | placebo mean R | note |
|---|---|---|---|---|---|---|---|
| ALL | 4219 | 51.6 % | -2.8 [-5.1, -0.3] | -0.168 [-0.282, -0.049] | -0.500 | -0.334 (p95 -0.253, p=0.00) beats |  |
| DEV | 2892 | 53.0 % | -1.7 [-4.8, +1.6] | -0.111 [-0.254, +0.027] | -0.432 | -0.338 (p95 -0.244, p=0.00) beats |  |
| VALIDATION | 1327 | 48.7 % | -5.2 [-8.4, -2.0] | -0.291 [-0.477, -0.098] | -0.649 | -0.326 (p95 -0.195, p=0.35) no |  |
| SHORT ALL | 3178 | 52.5 % | -3.4 [-6.3, -0.2] | -0.219 [-0.362, -0.078] | -0.555 | - |  |
| SHORT VALIDATION | 949 | 47.7 % | -7.6 [-11.9, -3.3] | -0.393 [-0.644, -0.140] | -0.755 | - |  |
| LONG ALL | 1041 | 49.1 % | -1.2 [-5.1, +2.9] | -0.009 [-0.213, +0.187] | -0.334 | - |  |
| LONG VALIDATION | 378 | 51.1 % | +0.6 [-4.7, +6.1] | -0.034 [-0.291, +0.233] | -0.384 | - |  |
| regime up DEV | 1169 | 51.9 % | -2.2 [-6.9, +2.6] | -0.123 [-0.382, +0.128] | -0.425 | - |  |
| regime up VALIDATION | 538 | 45.5 % | -5.5 [-10.5, -0.5] | -0.315 [-0.610, -0.004] | -0.687 | - |  |
| regime down DEV | 878 | 55.4 % | +2.1 [-5.2, +10.5] | +0.022 [-0.233, +0.276] | -0.264 | - |  |
| regime down VALIDATION | 429 | 50.8 % | -3.7 [-9.4, +2.4] | -0.090 [-0.404, +0.254] | -0.413 | - |  |
| regime range DEV | 836 | 52.0 % | -5.1 [-8.8, -1.8] | -0.244 [-0.453, -0.051] | -0.629 | - |  |
| regime range VALIDATION | 360 | 50.8 % | -6.8 [-12.9, -0.6] | -0.494 [-0.858, -0.140] | -0.874 | - |  |
| state REJECTED ALL | 2515 | 53.5 % | -3.0 [-6.0, -0.1] | -0.201 [-0.364, -0.044] | -0.558 | - |  |
| state FAILED BREAK ALL | 1704 | 48.9 % | -2.5 [-5.9, +1.0] | -0.118 [-0.246, +0.015] | -0.415 | - |  |
| source spot ALL | 571 | 56.7 % | -0.9 [-6.1, +4.0] | -0.039 [-0.371, +0.268] | -0.375 | - |  |
| source um ALL | 3637 | 50.8 % | -3.1 [-5.7, -0.4] | -0.188 [-0.307, -0.072] | -0.520 | - |  |
| source um-daily ALL | 11 | 54.5 % | -0.8 [-9.9, +6.6] | +0.050 [-0.993, +0.774] | -0.340 | - | UNDERPOWERED |

- Last 28 days of this cell (replay-window comparison, descriptive): n 32, hit 62.5 % (learning file: n 30, 60 %, window to 11-13)

- **BTC VALIDATION verdict: FAIL** (n 1327, fee-net mean R -0.291, CI lower -0.477, beats placebo False, regimes n>=30 in VALIDATION: 3)

## Cell ETH  (2022-01-01 .. 2026-09-30, 1734 days; VALIDATION from 2025-04-28)
- Node run: {"bars5": 499392, "bars15": 166464, "steps": 498492, "idea_steps": 175830, "events": 39933, "first": 1640995200000, "last": 1790812500000}; flag events 2416, skipped (gap in 60-min window) 0, level-vs-independent-Europe-high mismatches 0
- Regime mix: up 37.9 % / down 41.1 % / range 20.9 % (days with a regime: 1714, rule in PRE_REG)

| slice | n | hit (gross) | fee-net mean bps [95 % CI] | fee-net mean R [95 % CI] | R at 10 bp | placebo mean R | note |
|---|---|---|---|---|---|---|---|
| ALL | 2416 | 52.5 % | -5.3 [-8.8, -1.9] | -0.211 [-0.365, -0.056] | -0.493 | -0.309 (p95 -0.215, p=0.04) beats |  |
| DEV | 1670 | 53.4 % | -3.2 [-7.3, +1.1] | -0.096 [-0.261, +0.072] | -0.374 | -0.278 (p95 -0.171, p=0.01) beats |  |
| VALIDATION | 746 | 50.5 % | -10.1 [-16.8, -4.0] | -0.468 [-0.828, -0.135] | -0.759 | -0.380 (p95 -0.186, p=0.77) no |  |
| SHORT ALL | 1881 | 53.1 % | -6.0 [-10.4, -1.5] | -0.243 [-0.433, -0.055] | -0.524 | - |  |
| SHORT VALIDATION | 552 | 50.2 % | -13.2 [-21.7, -5.0] | -0.565 [-1.020, -0.127] | -0.860 | - |  |
| LONG ALL | 535 | 50.7 % | -2.8 [-9.9, +4.0] | -0.098 [-0.401, +0.195] | -0.383 | - |  |
| LONG VALIDATION | 194 | 51.5 % | -1.2 [-11.8, +9.4] | -0.192 [-0.703, +0.292] | -0.471 | - |  |
| regime up DEV | 603 | 52.7 % | -3.1 [-9.8, +4.0] | -0.094 [-0.397, +0.222] | -0.354 | - |  |
| regime up VALIDATION | 331 | 52.6 % | -10.1 [-19.4, -1.6] | -0.526 [-1.050, -0.071] | -0.796 | - |  |
| regime down DEV | 725 | 53.8 % | -3.0 [-9.8, +3.9] | -0.110 [-0.318, +0.107] | -0.374 | - |  |
| regime down VALIDATION | 227 | 46.7 % | -14.5 [-29.3, -1.0] | -0.435 [-1.088, +0.194] | -0.716 | - |  |
| regime range DEV | 329 | 54.7 % | -2.3 [-10.4, +6.4] | -0.029 [-0.413, +0.378] | -0.369 | - |  |
| regime range VALIDATION | 188 | 51.6 % | -4.7 [-16.6, +5.8] | -0.406 [-1.198, +0.257] | -0.744 | - |  |
| state REJECTED ALL | 1410 | 54.0 % | -6.6 [-11.7, -1.6] | -0.245 [-0.481, -0.009] | -0.548 | - |  |
| state FAILED BREAK ALL | 1006 | 50.5 % | -3.4 [-7.6, +0.8] | -0.163 [-0.324, +0.006] | -0.415 | - |  |

- Last 28 days of this cell (replay-window comparison, descriptive): n 50, hit 54.0 % (learning file: n 30, 60 %, window to 11-13)

- **ETH VALIDATION verdict: FAIL** (n 746, fee-net mean R -0.468, CI lower -0.828, beats placebo False, regimes n>=30 in VALIDATION: 3)

## Cell SOL  (2022-01-01 .. 2024-06-30, 912 days; VALIDATION from 2023-10-01)
- Node run: {"bars5": 261216, "bars15": 87072, "steps": 260314, "idea_steps": 90216, "events": 20669, "first": 1640995200000, "last": 1719791700000}; flag events 1138, skipped (gap in 60-min window) 0, level-vs-independent-Europe-high mismatches 0
- Regime mix: up 40.9 % / down 44.5 % / range 14.6 % (days with a regime: 847, rule in PRE_REG)

| slice | n | hit (gross) | fee-net mean bps [95 % CI] | fee-net mean R [95 % CI] | R at 10 bp | placebo mean R | note |
|---|---|---|---|---|---|---|---|
| ALL | 1138 | 53.6 % | -0.7 [-9.3, +7.8] | -0.041 [-0.358, +0.274] | -0.240 | -0.209 (p95 -0.018, p=0.09) no |  |
| DEV | 836 | 52.6 % | -3.2 [-13.8, +7.6] | -0.090 [-0.456, +0.299] | -0.290 | -0.202 (p95 -0.006, p=0.18) no |  |
| VALIDATION | 302 | 56.3 % | +6.1 [-7.0, +20.0] | +0.094 [-0.360, +0.572] | -0.104 | -0.227 (p95 +0.169, p=0.10) no |  |
| SHORT ALL | 848 | 54.7 % | +1.8 [-8.2, +12.1] | +0.103 [-0.296, +0.492] | -0.100 | - |  |
| SHORT VALIDATION | 231 | 58.0 % | +5.8 [-9.1, +21.5] | +0.142 [-0.428, +0.725] | -0.059 | - |  |
| LONG ALL | 290 | 50.3 % | -7.9 [-24.7, +8.8] | -0.462 [-0.924, -0.032] | -0.651 | - |  |
| LONG VALIDATION | 71 | 50.7 % | +7.1 [-26.8, +44.5] | -0.062 [-0.859, +0.734] | -0.250 | - |  |
| regime up DEV | 211 | 49.8 % | +4.4 [-17.4, +29.8] | +0.078 [-0.667, +1.012] | -0.102 | - |  |
| regime up VALIDATION | 169 | 58.0 % | +9.9 [-10.8, +31.6] | +0.116 [-0.548, +0.776] | -0.044 | - |  |
| regime down DEV | 429 | 55.0 % | -2.4 [-18.5, +13.9] | +0.009 [-0.551, +0.544] | -0.185 | - |  |
| regime down VALIDATION | 84 | 57.1 % | +12.4 [-7.2, +33.9] | +0.580 [-0.186, +1.409] | +0.352 | - |  |
| regime range DEV | 104 | 55.8 % | +3.9 [-6.3, +15.9] | -0.005 [-0.629, +0.575] | -0.271 | - |  |
| regime range VALIDATION | 49 | 49.0 % | -17.7 [-44.8, +7.4] | -0.817 [-1.885, +0.142] | -1.096 | - |  |
| state REJECTED ALL | 651 | 54.1 % | +0.1 [-11.8, +12.1] | +0.031 [-0.444, +0.530] | -0.195 | - |  |
| state FAILED BREAK ALL | 487 | 53.0 % | -1.8 [-12.1, +8.6] | -0.137 [-0.398, +0.128] | -0.301 | - |  |

- Last 28 days of this cell (replay-window comparison, descriptive): n 36, hit 61.1 % (learning file: n 30, 60 %, window to 11-13)

- **SOL VALIDATION verdict: FAIL** (n 302, fee-net mean R +0.094, CI lower -0.360, beats placebo False, regimes n>=30 in VALIDATION: 3)
