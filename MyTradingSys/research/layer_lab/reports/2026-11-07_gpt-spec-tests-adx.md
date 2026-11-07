PASS=62 FAIL=0 TOTAL=62

# GPT Spec Tests: ADX/DI (Wilder) from FORMULAS.md section 30

- **Card**: `gpt-spec-tests-adx-independent-tests-of-`
- **Audit Scope In**: `MyTradingSys/backtest/layers/FORMULAS.md` (read, section 30: lines 684-692); `MyTradingSys/backtest/layers/adx/adx.py` (run only); `MyTradingSys/research/layer_lab/reports/2026-11-07_gpt-spec-tests-adx.md` (new)
- **Audit Scope Out**: No edit to `adx.py` or `test_adx.py`; no live-tree edit; no `.secrets` or `.env` read
- **Methodology**: Independent GPT spec tests re-derived from mathematical definitions in `FORMULAS.md` section 30 only, without importing, referencing, or reading `test_adx.py`. Calculations executed in Python using exact arithmetic (`fractions.Fraction`) and verified against the live implementation `adx.adx_di` and `adx.crosses`.

## 1. Mathematical Clauses from FORMULAS.md Section 30

- **Default Period (30.1.13)**: `n = 14 by default` [SOURCED `FORMULAS.md:687`]
- **True Range (30.1.1)**: `TR_i = max(H_i - L_i, |H_i - C_{i-1}|, |L_i - C_{i-1}|)` for `i >= 1` [SOURCED `FORMULAS.md:689`]
- **Directional Movement (30.1.2-4)**: `up = H_i - H_{i-1}`, `dn = L_{i-1} - L_i`; `+DM_i = up if up > dn and up > 0 else 0`; `-DM_i = dn if dn > up and dn > 0 else 0` [SOURCED `FORMULAS.md:689`]
- **Wilder Smoothing (30.1.5-6)**: Initial `S = sum(first n values (bars 1..n))`; recursion `S_i = S_{i-1} - S_{i-1}/n + x_i` [SOURCED `FORMULAS.md:689`]
- **Directional Indicators (30.1.7-8)**: `DI+ = 100 * S(+DM) / S(TR)`, `DI- = 100 * S(-DM) / S(TR)` (both 0 if `S(TR) = 0`), first defined at bar `n` [SOURCED `FORMULAS.md:689`]
- **Directional Index DX (30.1.9)**: `DX = 100 * |DI+ - DI-| / (DI+ + DI-)` (0 if sum is 0) [SOURCED `FORMULAS.md:689`]
- **ADX (30.1.10-11)**: Initial ADX = mean of first `n` DX (first defined at bar `2n-1`); recursion `ADX_i = (ADX_{i-1} * (n-1) + DX_i) / n` [SOURCED `FORMULAS.md:689`]
- **Crosses (30.1.12)**: `Cross: the sign of DI+ - DI- flips (strict, zeros ignored); red = DI- over DI+, green = DI+ over DI-` [SOURCED `FORMULAS.md:689`]

## 2. 20-Bar Worked Toy Fixture (n = 3)

Data fixture from `FORMULAS.md:691`:
```
H = [10,11,12,11,13,14,13,12,11,12,13,15,14,13,12,11,12,14,15,14] [SOURCED FORMULAS.md:691]
L = [8,9,10,9,10,12,11,10,9,10,11,12,12,11,10,9,10,11,13,12] [SOURCED FORMULAS.md:691]
C = [9,10,11,10,12,13,12,11,10,11,12,14,13,12,11,10,11,13,14,13] [SOURCED FORMULAS.md:691]
```

Step-by-step intermediate hand values (all fractions exact):

| Bar | H | L | C | TR | +DM | -DM | S(TR) | S(+DM) | S(-DM) | DX | ADX |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 10 | 8 | 9 | - | - | - | - | - | - | - | - |
| 1 | 11 | 9 | 10 | 2 | 1 | 0 | - | - | - | - | - |
| 2 | 12 | 10 | 11 | 2 | 1 | 0 | - | - | - | - | - |
| 3 | 11 | 9 | 10 | 2 | 0 | 1 | 6.000 | 2.000 | 1.000 | 33.333 | - |
| 4 | 13 | 10 | 12 | 3 | 2 | 0 | 7.000 | 3.333 | 0.667 | 66.667 | - |
| 5 | 14 | 12 | 13 | 2 | 1 | 0 | 6.667 | 3.222 | 0.444 | 75.758 | 58.586 |
| 6 | 13 | 11 | 12 | 2 | 0 | 1 | 6.444 | 2.148 | 1.296 | 24.731 | 47.301 |
| 7 | 12 | 10 | 11 | 2 | 0 | 1 | 6.296 | 1.432 | 1.864 | 13.109 | 35.904 |
| 8 | 11 | 9 | 10 | 2 | 0 | 1 | 6.198 | 0.955 | 2.243 | 40.283 | 37.363 |
| 9 | 12 | 10 | 11 | 2 | 1 | 0 | 6.132 | 1.636 | 1.495 | 4.512 | 26.413 |
| 10 | 13 | 11 | 12 | 2 | 1 | 0 | 6.088 | 2.091 | 0.997 | 35.436 | 29.421 |
| 11 | 15 | 12 | 14 | 3 | 2 | 0 | 7.059 | 3.394 | 0.665 | 67.253 | 42.031 |
| 12 | 14 | 12 | 13 | 2 | 0 | 0 | 6.706 | 2.263 | 0.443 | 67.253 | 50.438 |
| 13 | 13 | 11 | 12 | 2 | 0 | 1 | 6.470 | 1.508 | 1.295 | 7.600 | 36.159 |
| 14 | 12 | 10 | 11 | 2 | 0 | 1 | 6.314 | 1.006 | 1.864 | 29.902 | 34.073 |
| 15 | 11 | 9 | 10 | 2 | 0 | 1 | 6.209 | 0.670 | 2.242 | 53.967 | 40.705 |
| 16 | 12 | 10 | 11 | 2 | 1 | 0 | 6.139 | 1.447 | 1.495 | 1.631 | 27.680 |
| 17 | 14 | 11 | 13 | 3 | 2 | 0 | 7.093 | 2.965 | 0.997 | 49.682 | 35.014 |
| 18 | 15 | 13 | 14 | 2 | 1 | 0 | 6.729 | 2.976 | 0.664 | 63.502 | 44.510 |
| 19 | 14 | 12 | 13 | 2 | 0 | 1 | 6.486 | 1.984 | 1.443 | 15.795 | 34.938 |

## 3. Spec Tests Table

| # | Formula Clause | Target | Hand Number / Spec Expected | adx.py Output | Status | Verification Note |
|---|---|---|---|---|---|---|
| 1 | 30.1.13 Default parameter | `adx_di(n=14)` | 14 [SOURCED FORMULAS.md:687: "Wilder's definitions, n = 14 by default"] | `14 [OURS]` | PASS | Signature parameter default matches specification |
| 2 | 30.1.7 DI+ initialization bar 0 | `DI+[0]` | None [OURS: first defined at bar n=3, FORMULAS.md:689] | `None [OURS]` | PASS | Bar 0 < n=3 returns None |
| 3 | 30.1.8 DI- initialization bar 0 | `DI-[0]` | None [OURS: first defined at bar n=3, FORMULAS.md:689] | `None [OURS]` | PASS | Bar 0 < n=3 returns None |
| 4 | 30.1.7 DI+ initialization bar 1 | `DI+[1]` | None [OURS: first defined at bar n=3, FORMULAS.md:689] | `None [OURS]` | PASS | Bar 1 < n=3 returns None |
| 5 | 30.1.8 DI- initialization bar 1 | `DI-[1]` | None [OURS: first defined at bar n=3, FORMULAS.md:689] | `None [OURS]` | PASS | Bar 1 < n=3 returns None |
| 6 | 30.1.7 DI+ initialization bar 2 | `DI+[2]` | None [OURS: first defined at bar n=3, FORMULAS.md:689] | `None [OURS]` | PASS | Bar 2 < n=3 returns None |
| 7 | 30.1.8 DI- initialization bar 2 | `DI-[2]` | None [OURS: first defined at bar n=3, FORMULAS.md:689] | `None [OURS]` | PASS | Bar 2 < n=3 returns None |
| 8 | 30.1.10 ADX initialization bar 0 | `ADX[0]` | None [OURS: first defined at bar 2n-1=5, FORMULAS.md:689] | `None [OURS]` | PASS | Bar 0 < 2n-1=5 returns None |
| 9 | 30.1.10 ADX initialization bar 1 | `ADX[1]` | None [OURS: first defined at bar 2n-1=5, FORMULAS.md:689] | `None [OURS]` | PASS | Bar 1 < 2n-1=5 returns None |
| 10 | 30.1.10 ADX initialization bar 2 | `ADX[2]` | None [OURS: first defined at bar 2n-1=5, FORMULAS.md:689] | `None [OURS]` | PASS | Bar 2 < 2n-1=5 returns None |
| 11 | 30.1.10 ADX initialization bar 3 | `ADX[3]` | None [OURS: first defined at bar 2n-1=5, FORMULAS.md:689] | `None [OURS]` | PASS | Bar 3 < 2n-1=5 returns None |
| 12 | 30.1.10 ADX initialization bar 4 | `ADX[4]` | None [OURS: first defined at bar 2n-1=5, FORMULAS.md:689] | `None [OURS]` | PASS | Bar 4 < 2n-1=5 returns None |
| 13 | 30.1.7 DI+ bar 3 | `DI+[3]` | 33.3333 [SOURCED FORMULAS.md:691: "DI+ = 33.333"] | `33.3333 [OURS]` | PASS | Exact rational 100/3 |
| 14 | 30.1.8 DI- bar 3 | `DI-[3]` | 16.6667 [SOURCED FORMULAS.md:691: "DI- = 16.667"] | `16.6667 [OURS]` | PASS | Exact rational 50/3 |
| 15 | 30.1.7 DI+ bar 4 | `DI+[4]` | 47.6190 [SOURCED FORMULAS.md:691: "DI+ = 47.619"] | `47.6190 [OURS]` | PASS | Exact rational 1000/21 |
| 16 | 30.1.8 DI- bar 4 | `DI-[4]` | 9.5238 [SOURCED FORMULAS.md:691: "DI- = 9.524"] | `9.5238 [OURS]` | PASS | Exact rational 200/21 |
| 17 | 30.1.7 DI+ bar 5 | `DI+[5]` | 48.3333 [SOURCED FORMULAS.md:691: "DI+ = 48.333"] | `48.3333 [OURS]` | PASS | Exact rational 145/3 |
| 18 | 30.1.8 DI- bar 5 | `DI-[5]` | 6.6667 [SOURCED FORMULAS.md:691: "DI- = 6.667"] | `6.6667 [OURS]` | PASS | Exact rational 20/3 |
| 19 | 30.1.10-11 ADX bar 5 | `ADX[5]` | 58.5859 [SOURCED FORMULAS.md:691: "ADX_5 = 58.586"] | `58.5859 [OURS]` | PASS | Exact rational 5800/99 |
| 20 | 30.1.7 DI+ bar 6 | `DI+[6]` | 33.3333 [SOURCED FORMULAS.md:691: "DI+ = 33.333"] | `33.3333 [OURS]` | PASS | Exact rational 100/3 |
| 21 | 30.1.8 DI- bar 6 | `DI-[6]` | 20.1149 [SOURCED FORMULAS.md:691: "DI- = 20.115"] | `20.1149 [OURS]` | PASS | Exact rational 1750/87 |
| 22 | 30.1.10-11 ADX bar 6 | `ADX[6]` | 47.3010 [SOURCED FORMULAS.md:691: "ADX_6 = 47.301"] | `47.3010 [OURS]` | PASS | Exact rational 435500/9207 |
| 23 | 30.1.7 DI+ bar 7 | `DI+[7]` | 22.7451 [OURS: exact 1160/51] | `22.7451 [OURS]` | PASS | Exact rational 1160/51 |
| 24 | 30.1.8 DI- bar 7 | `DI-[7]` | 29.6078 [OURS: exact 1510/51] | `29.6078 [OURS]` | PASS | Exact rational 1510/51 |
| 25 | 30.1.10-11 ADX bar 7 | `ADX[7]` | 35.9035 [OURS: exact 88260500/2458269] | `35.9035 [OURS]` | PASS | Exact rational 88260500/2458269 |
| 26 | 30.1.7 DI+ bar 8 | `DI+[8]` | 15.4050 [OURS: exact 11600/753] | `15.4050 [OURS]` | PASS | Exact rational 11600/753 |
| 27 | 30.1.8 DI- bar 8 | `DI-[8]` | 36.1886 [OURS: exact 27250/753] | `36.1886 [OURS]` | PASS | Exact rational 27250/753 |
| 28 | 30.1.10-11 ADX bar 8 | `ADX[8]` | 37.3634 [OURS: exact 71366878900/1910075013] | `37.3634 [OURS]` | PASS | Exact rational 71366878900/1910075013 |
| 29 | 30.1.7 DI+ bar 9 | `DI+[9]` | 26.6890 [OURS: exact 11930/447] | `26.6890 [OURS]` | PASS | Exact rational 11930/447 |
| 30 | 30.1.8 DI- bar 9 | `DI-[9]` | 24.3848 [OURS: exact 10900/447] | `24.3848 [OURS]` | PASS | Exact rational 10900/447 |
| 31 | 30.1.10-11 ADX bar 9 | `ADX[9]` | 26.4128 [OURS: exact 115178313897100/4360701254679] | `26.4128 [OURS]` | PASS | Exact rational 115178313897100/4360701254679 |
| 32 | 30.1.7 DI+ bar 10 | `DI+[10]` | 34.3473 [OURS: exact 228650/6657] | `34.3473 [OURS]` | PASS | Exact rational 228650/6657 |
| 33 | 30.1.8 DI- bar 10 | `DI-[10]` | 16.3737 [OURS: exact 109000/6657] | `16.3737 [OURS]` | PASS | Exact rational 109000/6657 |
| 34 | 30.1.10-11 ADX bar 10 | `ADX[10]` | 29.4206 [OURS: exact 866371372579639100/29447815572847287] | `29.4206 [OURS]` | PASS | Exact rational 866371372579639100/29447815572847287 |
| 35 | 30.1.7 DI+ bar 11 | `DI+[11]` | 48.0836 [OURS: exact 2226800/46311] | `48.0836 [OURS]` | PASS | Exact rational 2226800/46311 |
| 36 | 30.1.8 DI- bar 11 | `DI-[11]` | 9.4146 [OURS: exact 436000/46311] | `9.4146 [OURS]` | PASS | Exact rational 436000/46311 |
| 37 | 30.1.10-11 ADX bar 11 | `ADX[11]` | 42.0312 [OURS: exact 1177078832689954541300/28004872609777769937] | `42.0312 [OURS]` | PASS | Exact rational 1177078832689954541300/28004872609777769937 |
| 38 | 30.1.7 DI+ bar 12 | `DI+[12]` | 33.7425 [OURS: exact 1113400/32997] | `33.7425 [OURS]` | PASS | Exact rational 1113400/32997 |
| 39 | 30.1.8 DI- bar 12 | `DI-[12]` | 6.6067 [OURS: exact 218000/32997] | `6.6067 [OURS]` | PASS | Exact rational 218000/32997 |
| 40 | 30.1.10-11 ADX bar 12 | `ADX[12]` | 50.4383 [OURS: exact 4237555812803299138300/84014617829333309811] | `50.4383 [OURS]` | PASS | Exact rational 4237555812803299138300/84014617829333309811 |
| 41 | 30.1.7 DI+ bar 13 | `DI+[13]` | 23.3128 [OURS: exact 4453600/191037] | `23.3128 [OURS]` | PASS | Exact rational 4453600/191037 |
| 42 | 30.1.8 DI- bar 13 | `DI-[13]` | 20.0194 [OURS: exact 546350/27291] | `20.0194 [OURS]` | PASS | Exact rational 546350/27291 |
| 43 | 30.1.10-11 ADX bar 13 | `ADX[13]` | 36.1590 [OURS: exact 45723137862475882454768300/1264504012949295645965361] | `36.1590 [OURS]` | PASS | Exact rational 45723137862475882454768300/1264504012949295645965361 |
| 44 | 30.1.7 DI+ bar 14 | `DI+[14]` | 15.9279 [OURS: exact 8907200/559221] | `15.9279 [OURS]` | PASS | Exact rational 8907200/559221 |
| 45 | 30.1.8 DI- bar 14 | `DI-[14]` | 29.5165 [OURS: exact 16506250/559221] | `29.5165 [OURS]` | PASS | Exact rational 16506250/559221 |
| 46 | 30.1.10-11 ADX bar 14 | `ADX[14]` | 34.0732 [OURS: exact 31150955692579515768492845500/914236401362340752032956003] | `34.0732 [OURS]` | PASS | Exact rational 31150955692579515768492845500/914236401362340752032956003 |
| 47 | 30.1.7 DI+ bar 15 | `DI+[15]` | 10.7974 [OURS: exact 60800/5631] | `10.7974 [OURS]` | PASS | Exact rational 60800/5631 |
| 48 | 30.1.8 DI- bar 15 | `DI-[15]` | 36.1144 [OURS: exact 59584550/1649883] | `36.1144 [OURS]` | PASS | Exact rational 59584550/1649883 |
| 49 | 30.1.10-11 ADX bar 15 | `ADX[15]` | 40.7046 [OURS: exact 57605877908272482535550109115303300/1415218750344474874991223200567937] | `40.7046 [OURS]` | PASS | Exact rational 57605877908272482535550109115303300/1415218750344474874991223200567937 |
| 50 | 30.1.7 DI+ bar 16 | `DI+[16]` | 23.5682 [OURS: exact 115344950/4894089] | `23.5682 [OURS]` | PASS | Exact rational 115344950/4894089 |
| 51 | 30.1.8 DI- bar 16 | `DI-[16]` | 24.3496 [OURS: exact 119169100/4894089] | `24.3496 [OURS]` | PASS | Exact rational 119169100/4894089 |
| 52 | 30.1.10-11 ADX bar 16 | `ADX[16]` | 27.6799 [OURS: exact 183733175617079994168346791689257169003900/6637773615584433961148709344382984120297] | `27.6799 [OURS]` | PASS | Exact rational 183733175617079994168346791689257169003900/6637773615584433961148709344382984120297 |
| 53 | 30.1.7 DI+ bar 17 | `DI+[17]` | 41.7970 [OURS: exact 1417973600/33925263] | `41.7970 [OURS]` | PASS | Exact rational 1417973600/33925263 |
| 54 | 30.1.8 DI- bar 17 | `DI-[17]` | 14.0508 [OURS: exact 476676400/33925263] | `14.0508 [OURS]` | PASS | Exact rational 476676400/33925263 |
| 55 | 30.1.10-11 ADX bar 17 | `ADX[17]` | 35.0139 [OURS: exact 44034396474138387567451179556541868617149373228/1257625778076704780449040215933522086352071105] | `35.0139 [OURS]` | PASS | Exact rational 44034396474138387567451179556541868617149373228/1257625778076704780449040215933522086352071105 |
| 56 | 30.1.7 DI+ bar 18 | `DI+[18]` | 44.2352 [OURS: exact 30505985/689631] | `44.2352 [OURS]` | PASS | Exact rational 30505985/689631 |
| 57 | 30.1.8 DI- bar 18 | `DI-[18]` | 9.8744 [OURS: exact 47667640/4827417] | `9.8744 [OURS]` | PASS | Exact rational 47667640/4827417 |
| 58 | 30.1.10-11 ADX bar 18 | `ADX[18]` | 44.5101 [OURS: exact 2924345490317168621031981241508855065266860522516322364/65700768939085850006674177200058979017650867924797235] | `44.5101 [OURS]` | PASS | Exact rational 2924345490317168621031981241508855065266860522516322364/65700768939085850006674177200058979017650867924797235 |
| 59 | 30.1.7 DI+ bar 19 | `DI+[19]` | 30.5945 [OURS: exact 4270837900/139595061] | `30.5945 [OURS]` | PASS | Exact rational 4270837900/139595061 |
| 60 | 30.1.8 DI- bar 19 | `DI-[19]` | 22.2478 [OURS: exact 3105688850/139595061] | `22.2478 [OURS]` | PASS | Exact rational 3105688850/139595061 |
| 61 | 30.1.10-11 ADX bar 19 | `ADX[19]` | 34.9385 [SOURCED FORMULAS.md:691: "Bar 19: ADX = 34.938"] | `34.9385 [OURS]` | PASS | Exact rational 67730859096663278979970580785859463248355425686862073919501532/1938573918298943572482878986601900641205561397631935169214145 |
| 62 | 30.1.12 Cross events | `crosses(dip, dim)` | [(7, 'red'), (9, 'green'), (14, 'red'), (17, 'green')] [OURS: hand-derived from FORMULAS.md:689 clause 30.1.12] | `[(7, 'red'), (9, 'green'), (14, 'red'), (17, 'green')] [OURS]` | PASS | Strict sign flips at bars 7 (red), 9 (green), 14 (red), 17 (green) |

## 4. Negative / Mutation Testing (Fail on Faulty Code First)

To verify that the spec tests detect defects and fail on incorrect code, three mutant implementations were executed against this test suite:

| Mutant Description | Injected Defect | Spec Test Failures | Verdict |
|---|---|---|---|
| Mutant 1: Missing 100x Scale | Omit `100 *` scaling on `DI+` and `DI-` | 34 / 62 tests failed | PASS (defect detected) |
| Mutant 2: Incorrect ADX Smoothing | Altered smoothing factor in ADX recursion from bar 6 onwards | 14 / 62 tests failed | PASS (defect detected) |
| Mutant 3: Inverted Cross Signals | Swapped `green` and `red` cross labels | 1 / 62 tests failed | PASS (defect detected) |

## 5. Audit Summary

- **Total spec tests**: 62 [OURS]
- **Passed**: 62 [OURS]
- **Failed**: 0 [OURS]
- **Conformance**: `MyTradingSys/backtest/layers/adx/adx.py` fully conforms to Wilder ADX/DI mathematical specification in `MyTradingSys/backtest/layers/FORMULAS.md` section 30.
