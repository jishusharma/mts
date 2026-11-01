# C30 VALIDATION read (2024-07-01..2025-06-30), pre-registered in PRE_REG_C30.md (commit bb124f5cd, earlier than this file)

Script `c30_validation.py` (reuses `wt_rsi_div.run` unchanged); data Binance spot BTCUSDT 5m, public, warm-up from 2024-04-01, fetch stops before 2025-07-01 (HOLDOUT never requested).
Preflight on the VALIDATION bars, all PASS: P1 coverage (30m 21888/21888, 15m 43776/43776), P2b prefix (0/15 cuts differ, both charts), P6 fee identity (gap 0), P7 overlap (0).
Note: the earlier C30 DEV run printed a split at 2024-07 over "whole history" (sim card), so these months had been seen as a split summary; the frozen rule was not tuned on them.

| Hyp | Chart / rule | n | Win | Mean (fee-net) | SD | 95 % CI | Worst | Half-years (n, mean) | p one-sided | Holm p (m=2) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | 30m, any trend | 35 | 74 % | -0.066 % | 1.97 | -0.720 .. +0.588 | -6.63 % | 19 -0.013 %, 16 -0.129 % | 0.578 | 0.578 | FAIL (mean <= 0) |
| H2 | 15m, 2h trend up | 22 | 73 % | +0.220 % | 0.81 | -0.120 .. +0.560 | -1.45 % | 11 +0.298 %, 11 +0.143 % | 0.109 | 0.218 | INCONCLUSIVE |

- P8 random entries (same exit, same side/trend state, 30 draws): H2 beats 30/30 (random median -0.037 %); H1 beats 10/30 (random median +0.001 %): H1 has no edge over random entries.
- H2 matches the DEV sign (+0.261 % DEV vs +0.220 %) but the CI includes 0 and Holm p 0.218 > 0.05: not a pass. As pre-registered, no re-tuning on VALIDATION; promotion needs the HOLDOUT read (operator's call).
- Gaps (unchanged from pre-reg section 4): spot not perp, no funding, taker fees, fill at next open, p from a t-test normal approximation.
