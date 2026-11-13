# Malkan MAL-R03 / MAL-R04 regular RSI divergence, 1h/4h, 20 perps (edge4-malkan-c-1114)

**Result: FAIL.** 0 of 8 VALIDATION cells PASS; rule in PRE_REG.md frozen before any outcome. VALIDATION n by cell 379..1754. Rule: `PRE_REG.md` (frozen before any outcome). Fee-net (round trip 0.0012 of entry), no funding.

Regime mix (BTC daily close vs 200-day SMA: above / below / within 5%), share of days: DEV 0.57/0.34/0.09; VALIDATION 0.62/0.11/0.27; RECENT 0.36/0.54/0.10

## VALIDATION cells (the verdict)
| rule | tf | lookback | n | mean net R | 95% CI | win | boot p | placebo p | placebo mean R | BH10 | ONE-REGIME | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R03 | 1h | 12 | 1752 | -0.333 | [-0.417, -0.247] | 0.39 | 1.000 | 0.953 | -0.256 | False | False | FAIL |
| R03 | 1h | 18 | 1754 | -0.334 | [-0.415, -0.241] | 0.39 | 1.000 | 0.967 | -0.236 | False | False | FAIL |
| R04 | 1h | 12 | 1651 | -0.320 | [-0.405, -0.232] | 0.42 | 1.000 | 0.687 | -0.300 | False | False | FAIL |
| R04 | 1h | 18 | 1652 | -0.315 | [-0.395, -0.236] | 0.42 | 1.000 | 0.495 | -0.318 | False | False | FAIL |
| R03 | 4h | 12 | 379 | -0.167 | [-0.304, -0.017] | 0.47 | 0.985 | 0.547 | -0.159 | False | False | FAIL |
| R03 | 4h | 18 | 379 | -0.167 | [-0.301, -0.018] | 0.47 | 0.988 | 0.627 | -0.133 | False | False | FAIL |
| R04 | 4h | 12 | 383 | -0.074 | [-0.285, 0.149] | 0.47 | 0.748 | 0.195 | -0.149 | False | False | FAIL |
| R04 | 4h | 18 | 382 | -0.083 | [-0.293, 0.135] | 0.47 | 0.778 | 0.171 | -0.169 | False | False | FAIL |

## DEV and RECENT (context; CI only at n >= 30)
| rule | tf | lookback | split | n | mean net R | 95% CI | placebo p |
|---|---|---|---|---|---|---|---|
| R03 | 1h | 12 | DEV | 4857 | -0.253 | [-0.296, -0.211] | 0.003 |
| R03 | 1h | 12 | RECENT | 2168 | -0.347 | [-0.425, -0.261] | 0.377 |
| R03 | 1h | 18 | DEV | 4870 | -0.252 | [-0.293, -0.209] | 0.130 |
| R03 | 1h | 18 | RECENT | 2174 | -0.348 | [-0.424, -0.266] | 0.777 |
| R04 | 1h | 12 | DEV | 4787 | -0.245 | [-0.299, -0.192] | 0.001 |
| R04 | 1h | 12 | RECENT | 2441 | -0.348 | [-0.427, -0.264] | 0.054 |
| R04 | 1h | 18 | DEV | 4794 | -0.245 | [-0.298, -0.192] | 0.003 |
| R04 | 1h | 18 | RECENT | 2447 | -0.343 | [-0.423, -0.254] | 0.052 |
| R03 | 4h | 12 | DEV | 1122 | -0.124 | [-0.209, -0.037] | 0.236 |
| R03 | 4h | 12 | RECENT | 469 | -0.039 | [-0.194, 0.110] | 0.064 |
| R03 | 4h | 18 | DEV | 1122 | -0.123 | [-0.206, -0.035] | 0.382 |
| R03 | 4h | 18 | RECENT | 469 | -0.046 | [-0.197, 0.101] | 0.127 |
| R04 | 4h | 12 | DEV | 1171 | -0.099 | [-0.207, 0.011] | 0.004 |
| R04 | 4h | 12 | RECENT | 590 | -0.258 | [-0.405, -0.098] | 0.796 |
| R04 | 4h | 18 | DEV | 1174 | -0.089 | [-0.196, 0.020] | 0.005 |
| R04 | 4h | 18 | RECENT | 590 | -0.256 | [-0.399, -0.099] | 0.710 |

Limitations: no funding charge; stops and targets assumed taker with 2 bp slippage in total; placebo pools are random subsets (up to 3000 candidate bars per coin and cell, split by entry time); swing = 1-bar-each-side close pivot and the 2x lookback time cap are OURS; a stop touched in the same bar as the target counts as the stop.
The 12 and 18 lookback cells are near copies (A is the most recent swing, usually well inside 12 bars), so they are not independent tests. The stop is one signal candle wide, so the 0.0012 round-trip cost alone is a large fraction of R (the loss is mostly cost, not direction).
One-sided p is the share of day-cluster bootstrap means at or below zero; BH 10% over the 8 VALIDATION p-values. n < 30 is UNDERPOWERED, never no edge.
