# V2 DEV RESULTS - BTC volume STATE family on daily bars (run V2-2026-10-09, DEV)

Registered in PRE_REG_ADDENDUM_A_2026-10-09.md (commit 6e6227b) before any V2 outcome. 1272 bars in range (first valid state bar index 350), 96 trials (84 live, 12 INSUFFICIENT-N), **0 pass triage**.
Entry open(i+1), exit open(i+1+h), net of 14 bp and funding in (entry, exit]. 'follow' = trade in the label direction (HI long / LO short), 'fade' = opposite. Excess = oriented mean fwd | state minus mean fwd | all bars. Overlap warning: a state lasts many days and a 20-day holding window overlaps its neighbours, so the effective number of independent observations is far below n; block = 40 days handles the inference, MDE below is the naive i.i.d. figure and is optimistic.
sd of h-day fwd return: h=5 748 bp, h=10 1085 bp, h=20 1552 bp. Naive MDE at n=400: h=5 93 bp, h=10 135 bp, h=20 193 bp

| state | n | h=5 follow / fade (excess bp, p_adj) | h=10 follow / fade (excess bp, p_adj) | h=20 follow / fade (excess bp, p_adj) |
|---|---|---|---|---|
| D20_HI | 397 | +104 (0.71) / -104 (1.00) | +186 (0.77) / -186 (1.00) | +336 (0.74) / -336 (1.00) |
| D20_LO | 421 | +33 (1.00) / -33 (1.00) | +86 (1.00) / -86 (1.00) | +247 (0.90) / -247 (1.00) |
| VT_HI | 421 | -11 (1.00) / +11 (1.00) | -9 (1.00) / +9 (1.00) | +91 (1.00) / -91 (1.00) |
| VT_LO | 439 | -25 (1.00) / +25 (1.00) | -45 (1.00) / +45 (1.00) | +10 (1.00) / -10 (1.00) |
| MOM_HI | 446 | +30 (1.00) / -30 (1.00) | +101 (1.00) / -101 (1.00) | +207 (0.96) / -207 (1.00) |
| MOM_LO | 449 | -35 (1.00) / +35 (1.00) | -40 (1.00) / +40 (1.00) | +92 (1.00) / -92 (1.00) |
| DUS_HI | 425 | +85 (0.84) / -85 (1.00) | +171 (0.78) / -171 (1.00) | +365 (0.52) / -365 (1.00) |
| DUS_LO | 407 | +83 (0.86) / -83 (1.00) | +184 (0.64) / -184 (1.00) | +389 (0.43) / -389 (1.00) |
| DAS_HI | 458 | -5 (1.00) / +5 (1.00) | -15 (1.00) / +15 (1.00) | +36 (1.00) / -36 (1.00) |
| DAS_LO | 386 | -13 (1.00) / +13 (1.00) | +68 (1.00) / -68 (1.00) | +149 (1.00) / -149 (1.00) |
| BULLR_D20HI | 158 | +163 (0.61) / -163 (1.00) | +354 (0.28) / -354 (1.00) | +552 (0.49) / -552 (1.00) |
| BULLR_D20LO | 55 | INSUFF | INSUFF | INSUFF |
| RANGE_D20HI | 183 | +11 (1.00) / -11 (1.00) | -34 (1.00) / +34 (1.00) | +131 (1.00) / -131 (1.00) |
| RANGE_D20LO | 250 | +26 (1.00) / -26 (1.00) | +56 (1.00) / -56 (1.00) | +221 (0.99) / -221 (1.00) |
| BEARR_D20HI | 56 | INSUFF | INSUFF | INSUFF |
| BEARR_D20LO | 116 | -37 (1.00) / +37 (1.00) | +14 (1.00) / -14 (1.00) | +167 (1.00) / -167 (1.00) |

### 10 best trials by RC p_adj

| state | h | orient | n | gross bp | net bp [95% CI] | win | excess bp | t | p_raw | p_adj | q_BH | triage |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BULLR_D20HI | 10 | follow | 158 | +437 | +381 [+29, +629] | 68% | +354 | 2.43 | 0.006 | 0.283 | 0.46 | FAIL |
| DUS_LO | 20 | follow | 407 | +246 | +309 [-104, +725] | 60% | +389 | 2.17 | 0.022 | 0.434 | 0.46 | FAIL |
| BULLR_D20HI | 20 | follow | 158 | +695 | +589 [+33, +1074] | 65% | +552 | 2.09 | 0.022 | 0.491 | 0.46 | FAIL |
| DUS_HI | 20 | follow | 425 | +507 | +439 [+84, +758] | 60% | +365 | 2.06 | 0.027 | 0.517 | 0.46 | FAIL |
| BULLR_D20HI | 5 | follow | 158 | +205 | +172 [-46, +308] | 57% | +163 | 1.92 | 0.021 | 0.608 | 0.46 | FAIL |
| DUS_LO | 10 | follow | 407 | +101 | +129 [-104, +372] | 56% | +184 | 1.88 | 0.036 | 0.636 | 0.46 | FAIL |
| D20_HI | 5 | follow | 397 | +146 | +121 [-27, +251] | 58% | +104 | 1.77 | 0.043 | 0.707 | 0.46 | FAIL |
| D20_HI | 20 | follow | 397 | +478 | +414 [-70, +866] | 60% | +336 | 1.72 | 0.045 | 0.736 | 0.46 | FAIL |
| D20_HI | 10 | follow | 397 | +269 | +232 [-43, +490] | 61% | +186 | 1.67 | 0.048 | 0.772 | 0.46 | FAIL |
| DUS_HI | 10 | follow | 425 | +254 | +214 [-13, +419] | 58% | +171 | 1.65 | 0.045 | 0.782 | 0.46 | FAIL |

### Registered contrasts (h=10, follow-oriented; own BH family of 3)

| id | what | nA | nB | mean A bp | mean B bp | diff bp | 95% CI bp | p | q_BH | supported |
|---|---|---|---|---|---|---|---|---|---|---|
| K1 | momentum HI: buy-delta HI minus not (long) | 229 | 217 | +252 | +111 | +141 | [-371, +614] | 0.589 | 0.868 | no |
| K2 | momentum LO: sell-delta LO minus not (short) | 247 | 202 | -106 | -144 | +39 | [-435, +626] | 0.868 | 0.868 | no |
| K3 | US-hours buy-delta HI minus Asia-hours buy-delta HI (long) | 425 | 458 | +254 | +68 | +186 | [-85, +471] | 0.158 | 0.474 | no |

### Placebo calibration (volume and taker-buy shifted by 42*k days, k distinct in 1..38; family-wise pass = any trial with p_adj < 0.10)

- 20 placebo runs, family-wise pass rate 0.20 (expected <= 0.10; miscalibrated if > 0.20) -> **CALIBRATED**. Triggers: {'D20_HI': 1, 'VT_HI': 1, 'RANGE_D20LO': 1, 'BULLR_D20LO': 1}. Lags (days): [1596, 1092, 42, 294, 882, 378, 84, 168, 756, 1050, 1428, 840, 1554, 1512, 420, 924, 504, 1176, 546, 210]
- Revision note: the first V2 run drew lags WITH replacement from only 9 values (20 runs, pass rate 0.20, all 4 hits on VT_HI, so partly duplicated lags); this is the corrected draw of 20 distinct lags. The 96 trials and every non-placebo number are unchanged.

### V2 candidates frozen for VALIDATION

**None.** No state x horizon x orientation passes the registered triage on DEV.

