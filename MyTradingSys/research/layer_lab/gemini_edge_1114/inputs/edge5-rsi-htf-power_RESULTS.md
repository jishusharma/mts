# RESULT: RSI-HTF extreme power test on new spot data (edge5-rsi-htf-power-1113)

**Verdict: 0 of 6 cells PASS. S1 (operator rule 4h<=12 & daily<30) both exits: UNDERPOWERED (18 signal days < 30). S2 (4h<=15 & d<30) both exits: FAIL. S3 (12h<=20) both exits: FAIL.**

Regime mix: BTC daily close vs 200d SMA (bull above, bear at or below) at the signal bar close of the traded signals, POOL: S1 bull 7 / bear 29 trades; S2 bull 32 / bear 53; S3 bull 64 / bear 146. Underlying BTC day mix: 2017-2019 bull 30% / bear 70%; 2020-now bull 59% / bear 41%.

Data: Binance spot 1h/1d (data-api.binance.vision), all 60 coins loaded (first bars in meta.json; BTC/ETH 2017-08-17). B1 = parent's 20 coins, entries before 2020-01-01 (signals S1/S2/S3 = 5 / 9 / 17). B2 = 40 new coins, full history (31 / 76 / 193). Rules, costs (5 bp taker + 1 bp slippage per side) and exit code are the parent's. Placebo A = same coin, same calendar month, same stop distance; placebo B = same coin, entries only where the last closed BTC daily RSI < 35; 400 draws each. Bonferroni threshold 0.05/6 = 0.0083 on day-bootstrap p and both placebo p. Pre-registered rule: PRE_REG.md.

## What the new data says
- S1 looks strong on B2: mean +1.07R (2R) / +1.45R (time10), trade CI above zero, both placebo p 0.002-0.015. It fails on clustering: day CI [-0.16, +1.53] (2R) and [-0.18, +2.09] (time10), only 18 distinct signal days. One date, 2024-07-05, supplies 14 of the 36 trades and 27.7R of the 33.8R total (82%) at 2R; the best 5 days are 109% of total R (all other days net negative) and without them the mean is -0.19R (2R) / -0.33R (time10), n 16. B1 (2018-2019, n 5) is inconclusive (+0.15R at 2R, -0.20R at time10).
- S2: same shape with more days (34): trade CI [0.05, 0.57] but day CI [-0.20, 0.82]; best 5 days 143% of total R, without them -0.19R. B1 (n 9) is negative (-0.71R / -0.64R, both CIs below zero on the trade view).
- S3 (12h<=20): 2R mean +0.15R, trade CI [-0.01, 0.31], day CI [-0.16, 0.41], placebo B p 0.117 (random 12h closes on BTC-oversold days do as well); time10 exit is negative (-0.06R). Without the best 5 days (2024-08-05, 2026-02-05, 2024-07-05, 2024-04-13, 2022-11-09): -0.23R (2R) / -0.38R (time10).
- Placebo A (month-matched) is easy to beat because the gated cells fire only in crashes; placebo B is the fairer test and S1/S2 pass it, but the day-cluster CI and the 30-day floor bind.
- Parent leads: (a) keeps its sign on new data (+0.9R to +1.2R) but rests on 18 independent days dominated by one flush, so no edge claim; (b) does not replicate (+0.15R at 2R, CI crosses zero, time exit negative).
- Regime: the gated cells earn in bear (S1 bear +1.00R / +1.34R n 29; S2 bear +0.51R / +0.60R n 53) and about zero in bull; S3 at 2R is regime-flat.
- top5 share above 1 means the top 5 signal days sum to more than total R (the remaining days net negative).

## Results table
Verdict is on POOL rows only. per-year = mean R (n) by entry year.

| cell | block | n | days | win% | mean R net | trade CI | day CI | placebo p (A month / B BTC<35) | per-year | without best 5 days (n, mean) | top5 share | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4h<=12 & d<30 tgt2R | B1 | 5 | 4 | 40 | 0.150 | [-1.07, 1.37] | [-1.06, 1.96] | 0.192 / 0.277 | 2018:0.48(n4); 2019:-1.15(n1) | 0, - | 1.00 |  |
| 4h<=12 & d<30 tgt2R | B2 | 31 | 14 | 74 | 1.067 | [0.60, 1.50] | [-0.12, 1.61] | 0.002 / 0.002 | 2022:0.09(n8); 2023:1.16(n4); 2024:1.90(n15); 2025:0.09(n3); 2026:-1.01(n1) | 11, -0.331 | 1.11 |  |
| 4h<=12 & d<30 tgt2R | POOL | 36 | 18 | 69 | 0.940 | [0.49, 1.38] | [-0.16, 1.53] | 0.002 / 0.002 | 2018:0.48(n4); 2019:-1.15(n1); 2022:0.09(n8); 2023:1.16(n4); 2024:1.90(n15); 2025:0.09(n3); 2026:-1.01(n1) | 16, -0.191 | 1.09 | UNDERPOWERED |
| 4h<=12 & d<30 time10 | B1 | 5 | 4 | 40 | -0.204 | [-0.98, 0.69] | [-0.91, 0.85] | 0.339 / 0.392 | 2018:0.03(n4); 2019:-1.15(n1) | 0, - | - |  |
| 4h<=12 & d<30 time10 | B2 | 31 | 14 | 81 | 1.447 | [0.88, 2.03] | [-0.16, 2.28] | 0.015 / 0.005 | 2022:0.01(n8); 2023:1.05(n4); 2024:2.68(n15); 2025:0.22(n3); 2026:-0.20(n1) | 11, -0.339 | 1.08 |  |
| 4h<=12 & d<30 time10 | POOL | 36 | 18 | 75 | 1.218 | [0.68, 1.74] | [-0.18, 2.09] | 0.015 / 0.005 | 2018:0.03(n4); 2019:-1.15(n1); 2022:0.01(n8); 2023:1.05(n4); 2024:2.68(n15); 2025:0.22(n3); 2026:-0.20(n1) | 16, -0.334 | 1.12 | UNDERPOWERED |
| 4h<=15 & d<30 tgt2R | B1 | 9 | 7 | 11 | -0.711 | [-1.05, -0.06] | [-1.06, 0.21] | 0.923 / 0.953 | 2018:-1.04(n6); 2019:-0.06(n3) | 4, -1.024 | - |  |
| 4h<=15 & d<30 tgt2R | B2 | 76 | 28 | 61 | 0.434 | [0.16, 0.70] | [-0.10, 0.95] | 0.002 / 0.002 | 2018:-1.01(n1); 2019:0.48(n2); 2020:-0.02(n3); 2022:0.51(n20); 2023:-0.48(n8); 2024:1.54(n14); 2025:0.18(n24); 2026:0.22(n4) | 50, -0.101 | 1.15 |  |
| 4h<=15 & d<30 tgt2R | POOL | 85 | 34 | 55 | 0.313 | [0.05, 0.57] | [-0.20, 0.82] | 0.002 / 0.005 | 2018:-1.03(n7); 2019:0.15(n5); 2020:-0.02(n3); 2022:0.51(n20); 2023:-0.48(n8); 2024:1.54(n14); 2025:0.18(n24); 2026:0.22(n4) | 59, -0.194 | 1.43 | FAIL |
| 4h<=15 & d<30 time10 | B1 | 9 | 7 | 11 | -0.637 | [-0.98, -0.24] | [-1.07, -0.25] | 0.865 / 0.858 | 2018:-0.71(n6); 2019:-0.49(n3) | 4, -0.549 | - |  |
| 4h<=15 & d<30 time10 | B2 | 76 | 28 | 62 | 0.497 | [0.16, 0.86] | [-0.20, 1.27] | 0.002 / 0.005 | 2018:-1.01(n1); 2019:0.67(n2); 2020:-0.76(n3); 2022:0.15(n20); 2023:-0.85(n8); 2024:2.50(n14); 2025:0.22(n24); 2026:0.82(n4) | 45, -0.215 | 1.26 |  |
| 4h<=15 & d<30 time10 | POOL | 85 | 34 | 56 | 0.377 | [0.06, 0.70] | [-0.27, 1.13] | 0.002 / 0.020 | 2018:-0.75(n7); 2019:-0.02(n5); 2020:-0.76(n3); 2022:0.15(n20); 2023:-0.85(n8); 2024:2.50(n14); 2025:0.22(n24); 2026:0.82(n4) | 54, -0.285 | 1.48 | FAIL |
| 12h<=20 tgt2R | B1 | 17 | 12 | 29 | -0.112 | [-0.67, 0.53] | [-0.75, 0.83] | 0.287 / 0.641 | 2018:-0.11(n12); 2019:-0.11(n5) | 11, -0.958 | - |  |
| 12h<=20 tgt2R | B2 | 193 | 59 | 50 | 0.171 | [0.01, 0.34] | [-0.15, 0.43] | 0.002 / 0.095 | 2018:-1.02(n1); 2019:-1.03(n5); 2020:-1.02(n5); 2021:0.18(n4); 2022:-0.18(n52); 2023:-0.03(n44); 2024:0.90(n45); 2025:0.16(n12); 2026:0.47(n25) | 130, -0.249 | 1.98 |  |
| 12h<=20 tgt2R | POOL | 210 | 70 | 48 | 0.148 | [-0.01, 0.31] | [-0.16, 0.41] | 0.002 / 0.117 | 2018:-0.18(n13); 2019:-0.57(n10); 2020:-1.02(n5); 2021:0.18(n4); 2022:-0.18(n52); 2023:-0.03(n44); 2024:0.90(n45); 2025:0.16(n12); 2026:0.47(n25) | 147, -0.234 | 2.10 | FAIL |
| 12h<=20 time10 | B1 | 17 | 12 | 35 | -0.423 | [-0.79, -0.02] | [-0.85, 0.20] | 0.544 / 0.825 | 2018:-0.33(n12); 2019:-0.64(n5) | 11, -0.977 | - |  |
| 12h<=20 time10 | B2 | 193 | 59 | 42 | -0.031 | [-0.20, 0.17] | [-0.35, 0.33] | 0.065 / 0.713 | 2018:-1.02(n1); 2019:-1.03(n5); 2020:-1.02(n5); 2021:-0.36(n4); 2022:-0.30(n52); 2023:0.09(n44); 2024:0.78(n45); 2025:-0.18(n12); 2026:-0.58(n25) | 153, -0.370 | - |  |
| 12h<=20 time10 | POOL | 210 | 70 | 41 | -0.063 | [-0.22, 0.13] | [-0.36, 0.26] | 0.072 / 0.786 | 2018:-0.38(n13); 2019:-0.84(n10); 2020:-1.02(n5); 2021:-0.36(n4); 2022:-0.30(n52); 2023:0.09(n44); 2024:0.78(n45); 2025:-0.18(n12); 2026:-0.58(n25) | 170, -0.376 | - | FAIL |

Regime split (BTC daily close vs 200d SMA at signal bar close), POOL

| cell | bull n | bull mean | bull win% | bear n | bear mean | bear win% | no-SMA n |
|---|---|---|---|---|---|---|---|
| 4h<=12 & d<30 tgt2R | 7 | 0.700 | 71 | 29 | 0.998 | 69 | 0 |
| 4h<=12 & d<30 time10 | 7 | 0.697 | 86 | 29 | 1.343 | 72 | 0 |
| 4h<=15 & d<30 tgt2R | 32 | -0.007 | 56 | 53 | 0.506 | 55 | 0 |
| 4h<=15 & d<30 time10 | 32 | 0.001 | 72 | 53 | 0.604 | 47 | 0 |
| 12h<=20 tgt2R | 64 | 0.155 | 50 | 146 | 0.145 | 47 | 0 |
| 12h<=20 time10 | 64 | 0.040 | 50 | 146 | -0.108 | 38 | 0 |

## Files
PRE_REG.md (committed before outcomes), pick_universe.py, fetch.py, study.py, report.py, make_result.py, test_power.py (2 tests, not registered), htf_lib.py and rsi_grid_lib.py (parent's, unchanged), cells.csv, trades.csv, tables.md, meta.json.

## Caveats
Spot not perps, no funding; B2 universe chosen by present liquidity (survivorship); the 14-trade date 2024-07-05 is one market observation, so even the day CI may overstate independence; S1 and S2 share trades; Bonferroni over 6 is conservative.

Next: END: leads do not survive the day-cluster view; revisit only with more independent crash days (longer history); no layer promotion.
