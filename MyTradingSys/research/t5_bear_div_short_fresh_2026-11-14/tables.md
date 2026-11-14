# T5 tables (step C output, generated)

Verdict: **KILL** labels [] failing bars {'12_nofund': [2, 3, 4, 5, 6, 7], '12_fund': [2, 3, 4, 5, 6, 7]} raw VAL p (larger row) 0.7726136931534233

| split|row | n | weeks | mean R | sd | win | CI lo | CI hi | p one |
|---|---|---|---|---|---|---|---|---|
| DEV|12_nofund | 476 | 110 | -0.020 | 0.876 | 0.363 | -0.129 | 0.102 | 0.632 |
| DEV|12_fund | 476 | 110 | -0.018 | 0.875 | 0.366 | -0.127 | 0.103 | 0.621 |
| DEV|6_nofund | 476 | 110 | -0.010 | 0.876 | 0.370 | -0.119 | 0.112 | 0.569 |
| DEV|6_fund | 476 | 110 | -0.008 | 0.876 | 0.368 | -0.116 | 0.113 | 0.555 |
| VAL|12_nofund | 352 | 90 | -0.046 | 0.883 | 0.338 | -0.159 | 0.078 | 0.773 |
| VAL|12_fund | 352 | 90 | -0.043 | 0.885 | 0.344 | -0.157 | 0.081 | 0.762 |
| VAL|6_nofund | 352 | 90 | -0.035 | 0.883 | 0.347 | -0.149 | 0.089 | 0.716 |
| VAL|6_fund | 352 | 90 | -0.032 | 0.885 | 0.344 | -0.146 | 0.092 | 0.704 |
| POOLED|12_nofund | 828 | 200 | -0.031 | 0.878 | 0.353 | -0.113 | 0.049 | 0.789 |
| POOLED|12_fund | 828 | 200 | -0.029 | 0.879 | 0.356 | -0.110 | 0.051 | 0.774 |
| POOLED|6_nofund | 828 | 200 | -0.021 | 0.879 | 0.360 | -0.102 | 0.060 | 0.716 |
| POOLED|6_fund | 828 | 200 | -0.018 | 0.879 | 0.357 | -0.099 | 0.062 | 0.693 |
| RECENT|12_nofund | 169 | 49 | -0.035 | 0.875 | 0.343 | -0.193 | 0.149 | 0.661 |
| RECENT|12_fund | 169 | 49 | -0.033 | 0.877 | 0.355 | -0.191 | 0.151 | 0.654 |
| RECENT|6_nofund | 169 | 49 | -0.024 | 0.876 | 0.355 | -0.183 | 0.160 | 0.611 |
| RECENT|6_fund | 169 | 49 | -0.023 | 0.878 | 0.355 | -0.181 | 0.162 | 0.603 |

Placebo (12 bp rows)

| split|row | pct | beats 97.5 | p97.5 draw mean | matched | unmatched |
|---|---|---|---|---|---|
| DEV|12_nofund | 81.400 | False | 0.029 | 476 | 0 |
| DEV|12_fund | 83.000 | False | 0.029 | 476 | 0 |
| VAL|12_nofund | 29.800 | False | 0.088 | 352 | 0 |
| VAL|12_fund | 31.400 | False | 0.088 | 352 | 0 |
| POOLED|12_nofund | 58.200 | False | 0.025 | 828 | 0 |
| POOLED|12_fund | 62.400 | False | 0.025 | 828 | 0 |

Baseline (per day)

| split|row | signal rate | baseline rate | baseline days |
|---|---|---|---|
| DEV|12_nofund | -0.002 | -0.002 | 1140 |
| DEV|12_fund | -0.002 | -0.002 | 1140 |
| VAL|12_nofund | -0.003 | 0.001 | 932 |
| VAL|12_fund | -0.003 | 0.000 | 932 |

By coin (12 bp with funding)

| coin | n | mean R | underpowered |
|---|---|---|---|
| 1INCH | 25 | -0.013 | True |
| AAVE | 12 | 0.138 | True |
| ANKR | 22 | -0.122 | True |
| AXS | 22 | -0.180 | True |
| BAND | 29 | -0.147 | True |
| BAT | 24 | 0.103 | True |
| CELR | 22 | 0.097 | True |
| CHZ | 24 | -0.024 | True |
| COMP | 14 | -0.349 | True |
| CRV | 20 | 0.333 | True |
| DASH | 17 | 0.048 | True |
| EGLD | 24 | -0.047 | True |
| ENJ | 18 | -0.016 | True |
| EOS | 22 | -0.146 | True |
| FTM | 7 | -0.106 | True |
| FTT | 15 | 0.071 | True |
| GRT | 15 | -0.140 | True |
| HBAR | 13 | -0.302 | True |
| ICX | 30 | 0.403 | False |
| IOST | 23 | -0.111 | True |
| IOTA | 19 | 0.150 | True |
| KAVA | 20 | 0.312 | True |
| KNC | 20 | -0.191 | True |
| LUNA | 16 | 0.032 | True |
| MANA | 15 | -0.185 | True |
| MATIC | 9 | 0.077 | True |
| MKR | 9 | -0.378 | True |
| OCEAN | 12 | 0.104 | True |
| OMG | 12 | -0.076 | True |
| ONE | 16 | -0.111 | True |
| ONT | 29 | -0.181 | True |
| QTUM | 25 | -0.140 | True |
| RUNE | 14 | -0.022 | True |
| RVN | 22 | -0.058 | True |
| SAND | 20 | 0.103 | True |
| SNX | 19 | -0.142 | True |
| STORJ | 20 | -0.152 | True |
| SUSHI | 18 | 0.386 | True |
| THETA | 23 | -0.120 | True |
| WAVES | 9 | 0.077 | True |
| XMR | 11 | -0.327 | True |
| XTZ | 20 | -0.396 | True |
| YFI | 9 | 0.088 | True |
| ZIL | 22 | 0.052 | True |
| ZRX | 21 | -0.017 | True |

By year (12 bp with funding)

| year | n | mean R |
|---|---|---|
| 2019 | 15 | 0.513 |
| 2020 | 21 | -0.285 |
| 2021 | 15 | -0.272 |
| 2022 | 239 | 0.076 |
| 2023 | 186 | -0.132 |
| 2024 | 107 | -0.057 |
| 2025 | 139 | 0.032 |
| 2026 | 106 | -0.129 |

Control, BEAR false by Test 1 label (12 bp with funding)

| label | n | mean R |
|---|---|---|
| UP | 631 | 0.042 |
| BASE | 642 | 0.080 |
| RANGE | 106 | -0.116 |
| DOWN | 5 | 0.081 |
| POSTPEAK_BEAR | 0 | n/a |
