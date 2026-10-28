# RESULT: E2, Krown S8 squeeze break on 4h, BTC+ETH+SOL pooled, DEV stage 2020-01-01..2024-06-30 (run once 2026-10-28)

**Verdict: INCONCLUSIVE. C0 n 420 trades on 332 entry days (need >= 439), mean net R +0.1312, SE 0.0760, t +1.73 (need >= 3.364), mean gross R +0.1527 vs 4 x mean fee R 0.0861.**

PRE_REG.md (same folder) precedes this file and is unchanged. Code: `e2_run.py` (tests `test_e2_run.py`), one run, seed 20261028, 2000 day-block resamples. VALIDATION 2024-07-01.. and HOLDOUT were not loaded (the loader drops them; tested). Label: NO-RECALL-CLEARANCE (detector recall 3 of 12, `krown_ta101_2026-10-13/RECALL.md`): a hypothesis, never a core. Parameters: fees SOURCED `backtest/fees.py:27-28`; slippage 0.02 %, stop floor 0.56 %, 10-bar stop, 2R target, 100-bar time stop, seed OURS (PRE_REG s2 items 6-8). Net R = side x (exit - fill) minus entry and exit fees, over risk |fill - stop|; fee R = gross R - net R (fees plus slippage).

Freeze bar passed before any outcome: 807 events on 539 days (expected 807 / 539 +-1 %). Signals skipped: 386 while a position was open, 0 under the 0.56 % floor. Exits: 238 stop, 138 target, 44 time.

## Verdict arms

| arm | n | mean net R | SE | verdict |
|---|---|---|---|---|
| C0 pooled BTC+ETH+SOL, both sides, 2020-01..2024-06 | 420 | +0.1312 | 0.0760 | INCONCLUSIVE |
| C1 BTCUSDT only | 142 | +0.0664 | 0.1159 | - |
| C2 ETHUSDT only | 153 | +0.1529 | 0.1112 | - |
| C3 SOLUSDT only | 125 | +0.1782 | 0.1265 | - |
| C4 long only | 232 | +0.2967 | 0.1037 | - |
| C5 short only | 188 | -0.0731 | 0.1121 | - |
| C6 DEV_EXT 2020-01..2021-12 | 175 | +0.0817 | 0.1119 | - |
| C7 DEV 2022-01..2024-06 | 245 | +0.1665 | 0.0972 | - |
| C8 BTCUSDT x DEV 2022-01..2024-06 | 78 | +0.1005 | 0.1583 | - |

FAIL means stop: no detector, chart, layer or management work on the Krown S8 squeeze-break family on 4h BTC, ETH or SOL with this 10-bar stop; and, this being the last powered family of R1 E1, the R1 section 5 STOP list applies to the BTC trading-edge program.

Strata (C1-C8) carry no verdict word and can neither rescue nor kill C0.

## Cell detail

| cell | n | entry days | mean gross R | mean fee R | mean net R | t |
|---|---|---|---|---|---|---|
| C0 | 420 | 332 | +0.1527 | 0.0215 | +0.1312 | +1.73 |
| C1 | 142 | 142 | +0.0965 | 0.0301 | +0.0664 | +0.57 |
| C2 | 153 | 151 | +0.1736 | 0.0207 | +0.1529 | +1.37 |
| C3 | 125 | 125 | +0.1909 | 0.0127 | +0.1782 | +1.41 |
| C4 | 232 | 189 | +0.3184 | 0.0217 | +0.2967 | +2.86 |
| C5 | 188 | 149 | -0.0519 | 0.0213 | -0.0731 | -0.65 |
| C6 | 175 | 148 | +0.0994 | 0.0177 | +0.0817 | +0.73 |
| C7 | 245 | 184 | +0.1907 | 0.0242 | +0.1665 | +1.71 |
| C8 | 78 | 78 | +0.1350 | 0.0345 | +0.1005 | +0.63 |

## Year table (descriptive: signal year; n, mean net R; no t, no verdict)

| year | n | mean net R |
|---|---|---|
| 2020 | 76 | +0.0703 |
| 2021 | 99 | +0.0905 |
| 2022 | 96 | +0.1818 |
| 2023 | 99 | +0.1548 |
| 2024 | 50 | +0.1602 |

## Descriptive comparator (no verdict)

The same bracket at the open of every 4h bar that is not a signal bar (both sides, stop = far side of the 10 bars before it, overlapping allowed, same symbols and window): n 51831, mean net R -0.0249.
