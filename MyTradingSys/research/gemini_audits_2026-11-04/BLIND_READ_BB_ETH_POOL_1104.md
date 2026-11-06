# Blind read: bb_range_retest_eth_pool_2026-11 RESULT.md vs dev_cells.csv, counts.csv and bb_range_retest_2026-11-04/dev_cells.csv (2026-11-06)

Method: recomputed with pandas from the CSVs before reading RESULT.md. Family = gate range, tag tagged, side both, sessions asia/london/ny, k 0.25/0.5/1.0, per symbol and POOL (27 rows have a Holm p; all 27 are survivor False). Net at 0.10 % = net + 0.04 (gross - net = 0.14 is the stored cost). Counts: FOUND 21, DIFF 0, NOT_IN_DATA 2.

| # | Headline number | Recomputed | Status |
|---|---|---|---|
| 1 | Regime mix POOL 260 weeks bull 36 / bear 0 / range 224; BTC bull 25 (19 %), ETH bull 11 (8 %) | regime_mix_dev.txt: identical | FOUND |
| 2 | POOL family n (asia 472/495/512, london 351/364/374, ny 439/458/472) | identical, 9 cells | FOUND |
| 3 | POOL days (asia 363/376/385, london 300/310/317, ny 339/352/361); "300-385" | identical | FOUND |
| 4 | POOL gross (+0.070 +0.058 +0.050 / +0.026 -0.005 -0.016 / +0.072 +0.096 +0.084) | 0.0702 0.0585 0.0499 / 0.0257 -0.0050 -0.0158 / 0.0724 0.0961 0.0839 | FOUND |
| 5 | POOL net 0.14 and CI (e.g. asia 0.25 -0.070 [-0.200,+0.060]; london 1.0 -0.156 [-0.288,-0.024]; ny 0.5 -0.044 [-0.185,+0.097]) | all 9 rows reproduce to 3 decimals; range -0.0439 to -0.1558 | FOUND |
| 6 | POOL net at 0.10 and CI (9 rows) | net+0.04: all 9 reproduce (e.g. ny 0.5 -0.004 [-0.145,+0.137]) | FOUND |
| 7 | POOL Holm p 1.00 0.99 0.86 / 0.86 0.29 0.19 / 1.00 1.00 1.00 | 1.0000 0.9901 0.8593 / 0.8593 0.2949 0.1869 / 1.0000 x3 | FOUND |
| 8 | POOL fill 63/66/69, 64/66/68, 59/61/63 % | 0.633 0.664 0.686 / 0.637 0.661 0.679 / 0.589 0.615 0.634 | FOUND |
| 9 | Target hit 18/19/18, 29/29/29, 18/19/19 % | 0.180 0.186 0.184 / 0.291 0.286 0.286 / 0.178 0.188 0.193 | FOUND |
| 10 | vs all-regime t -0.8 -1.2 -1.1 / 0.6 1.2 1.3 / 1.0 0.7 0.2 | -0.806 -1.155 -1.137 / 0.649 1.152 1.267 / 1.000 0.749 0.215 | FOUND |
| 11 | vs untagged t -0.1 to 1.1 | -0.135 to 1.099 | FOUND |
| 12 | 0 of 9 survive, dev_survivors.json [] | 0 True / 27 | FOUND |
| 13 | Per symbol BTC net -0.087 to -0.195, days 145-184, lowest Holm 0.21 | -0.0869 to -0.1945; 145-184; 0.2131 | FOUND |
| 14 | ETH net -0.122 to +0.011, days 155-201, lowest Holm 1.00 | -0.1224 to +0.0109; 155-201; 1.0000 | FOUND |
| 15 | POOL lowest Holm 0.19, net -0.044 to -0.156, days 300-385 | 0.1869; yes; yes | FOUND |
| 16 | ETH ny k 0.5: net +0.011 [-0.197,+0.219], n 241, Holm 1.0 | 0.0109 [-0.1968,+0.2186], 241, 0.9182 (rounds to 0.92, text says "1.0") | FOUND (Holm quoted loosely: 0.92, not 1.0) |
| 17 | All sessions k 0.5: BTC 771 -0.109 [-0.197,-0.022]; ETH 865 -0.115 [-0.214,-0.015]; POOL 1636 -0.112 [-0.179,-0.045] | 771 -0.1094 [-0.1968,-0.0220]; 865 -0.1148 [-0.2143,-0.0153]; 1636 -0.1122 [-0.1791,-0.0454] | FOUND |
| 18 | Pooled all-session at 0.10: -0.072 [-0.139,-0.005] | -0.0722 [-0.1391,-0.0054] | FOUND |
| 19 | BTC reproduction, this run n (asia 222/232/241, london 174/179/185, ny 209/217/226) and net (-0.087 -0.093 -0.121 / -0.126 -0.168 -0.195 / -0.127 -0.105 -0.091) | identical, from dev_cells.csv BTCUSDT rows | FOUND |
| 20 | BTC reproduction, shipped spot n (225/235/244, 175/180/186, 215/224/233) and net (-0.094 -0.105 -0.132 / -0.133 -0.175 -0.201 / -0.118 -0.083 -0.073) | identical, from bb_range_retest_2026-11-04/dev_cells.csv | FOUND |
| 21 | "n within 3 % in every cell, every sign the same" | max relative gap: ny 0.25 209 vs 215 = 2.8 %; all nets negative in both | FOUND |
| 22 | prereg_gate rows in BLOCKED.md (MDE, n needed 600-1944), "9 pooled cells BLOCK" | needs prereg_gate.py and sd inputs, not in the CSVs | NOT_IN_DATA |
| 23 | Data F:/MTS/data/tom_raw/klines, 4 tests failing on the stub | not in the CSVs | NOT_IN_DATA |

Observation: the BTC pool rows are not the shipped run row for row (different series, futures vs spot); RESULT.md states this and the tolerance holds.

VERDICT: MATCH
