# EUR-low sweep -> reclaim -> long (mirror short), pooled BTC + ETH + SOL, Bybit 5m linear (2026-11-13)

Rule, data, split, fees, placebo, inference and verdict vocabulary as frozen in PRE_REG.md (committed before any outcome). No parameter was searched.

**VERDICT: FAIL, cannot see an effect below ~0.25 R**

- Best VALIDATION cell by mean (descriptive, not selected): long HIGH maker, n 173, fee-net mean R +0.105 [-0.298, +0.577], placebo -0.694 (p95 -0.515).
- Power: gate BLOCK recorded in PRE_REG.md (MDE ~0.25 R on VALIDATION before fees); a FAIL does not exclude a smaller edge.
- Fees: taker 5 bp/side; maker cell = 2 bp entry + 5 bp exit (fees.py); no funding, no slippage (optimistic).
- Regime mix: up 39.1 % / down 33.5 % / range 27.4 % (event days, BTC prior close vs SMA20 +-2 %, rule in PRE_REG).

## Cells (n / fee-net mean R [95 % day-cluster bootstrap CI]); placebo and BH on VALIDATION

| cell (side exit entry) | DEV | VALIDATION | RECENT | VAL hit | VAL placebo mean R | VAL p (1-sided) | BH 10 % | verdict |
|---|---|---|---|---|---|---|---|---|
| long MID taker | 1106 / -0.335 [-0.419, -0.244] | 378 / -0.226 [-0.407, -0.050] | 508 / -0.354 [-0.497, -0.200] | 39.4 % | -0.594 (p95 -0.508) beats | 0.993 | no | FAIL |
| long MID maker | 539 / -0.064 [-0.213, +0.100] | 173 / -0.078 [-0.379, +0.233] | 231 / +0.032 [-0.218, +0.308] | 31.2 % | -0.608 (p95 -0.444) beats | 0.697 | no | FAIL |
| long HIGH taker | 1130 / -0.360 [-0.465, -0.251] | 384 / -0.230 [-0.433, -0.010] | 511 / -0.294 [-0.517, -0.053] | 28.4 % | -0.676 (p95 -0.573) beats | 0.979 | no | FAIL |
| long HIGH maker | 539 / -0.179 [-0.349, +0.004] | 173 / +0.105 [-0.298, +0.577] | 231 / +0.133 [-0.198, +0.517] | 26.0 % | -0.694 (p95 -0.515) beats | 0.330 | no | FAIL |
| long 2R taker | 1135 / -0.347 [-0.423, -0.268] | 384 / -0.259 [-0.412, -0.090] | 513 / -0.374 [-0.503, -0.237] | 35.2 % | -0.584 (p95 -0.503) beats | 1.000 | no | FAIL |
| long 2R maker | 539 / -0.078 [-0.198, +0.048] | 173 / -0.120 [-0.332, +0.104] | 231 / +0.146 [-0.050, +0.346] | 37.6 % | -0.604 (p95 -0.479) beats | 0.845 | no | FAIL |
| short MID taker | 998 / -0.206 [-0.317, -0.095] | 331 / -0.303 [-0.456, -0.144] | 432 / -0.180 [-0.329, -0.022] | 38.4 % | -0.547 (p95 -0.450) beats | 0.999 | no | FAIL |
| short MID maker | 466 / -0.068 [-0.236, +0.115] | 148 / +0.015 [-0.262, +0.286] | 207 / +0.124 [-0.148, +0.401] | 40.5 % | -0.575 (p95 -0.435) beats | 0.452 | no | FAIL |
| short HIGH taker | 1019 / -0.133 [-0.277, +0.020] | 335 / -0.303 [-0.512, -0.081] | 443 / -0.034 [-0.270, +0.216] | 27.5 % | -0.613 (p95 -0.502) beats | 0.999 | no | FAIL |
| short HIGH maker | 466 / -0.074 [-0.269, +0.141] | 148 / -0.064 [-0.417, +0.325] | 207 / +0.246 [-0.112, +0.671] | 28.4 % | -0.554 (p95 -0.403) beats | 0.636 | no | FAIL |
| short 2R taker | 1026 / -0.178 [-0.269, -0.084] | 336 / -0.319 [-0.477, -0.157] | 443 / -0.183 [-0.316, -0.042] | 33.0 % | -0.544 (p95 -0.455) beats | 1.000 | no | FAIL |
| short 2R maker | 466 / +0.062 [-0.080, +0.206] | 148 / +0.094 [-0.150, +0.331] | 207 / +0.084 [-0.115, +0.298] | 43.9 % | -0.566 (p95 -0.457) beats | 0.229 | no | FAIL |

## Per coin, VALIDATION (n, mean R)

| cell | BTC | ETH | SOL |
|---|---|---|---|
| long MID taker | 113, -0.261 | 133, -0.145 | 132, -0.277 |
| long MID maker | 55, -0.510 | 61, +0.013 | 57, +0.240 |
| long HIGH taker | 114, -0.195 | 137, -0.182 | 133, -0.310 |
| long HIGH maker | 55, -0.199 | 61, +0.082 | 57, +0.424 |
| long 2R taker | 114, -0.263 | 137, -0.247 | 133, -0.269 |
| long 2R maker | 55, -0.445 | 61, -0.013 | 57, +0.079 |
| short MID taker | 122, -0.312 | 100, -0.428 | 109, -0.179 |
| short MID maker | 57, +0.112 | 45, -0.146 | 46, +0.054 |
| short HIGH taker | 124, -0.189 | 102, -0.458 | 109, -0.288 |
| short HIGH maker | 57, +0.018 | 45, -0.211 | 46, -0.021 |
| short 2R taker | 124, -0.330 | 103, -0.377 | 109, -0.253 |
| short 2R maker | 57, +0.056 | 45, +0.107 | 46, +0.127 |
