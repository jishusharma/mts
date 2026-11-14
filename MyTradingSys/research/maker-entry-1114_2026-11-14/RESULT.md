**No PASS. Maker (limit) entries do not turn any of the six near-miss ideas into a fee-net pass: 0 of 6 rows have a positive day-cluster CI, and 5 of 6 have negative net R per filled trade on VALIDATION (2024+).**

The one row with positive maker net R, M4 (NK5 NY-asia), fails the day-cluster CI (low -0.110) and ex-best-5-days (-0.078); on fresh coins it already failed before (nk5-nyasia-fresh-coins -0.101 R).

## Results (VALIDATION 2024-01-01 on; maker = limit at signal level, filled only if 1m price trades through by 1 tick; misses counted)

| Row | Idea | Signals | Filled (fill rate) | Net R taker (12bp, all signals) | Net R maker per filled trade | Fee saved (R/trade) | Adverse selection (R) | Placebo p | Day-CI low | Ex-best-5 | Verdict | Checker |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 | NK2 pivot reclaim, 1h SHORT-P | 6102 | 3994 (65.5%) | -0.009 | -0.037 | 0.024 | -0.195 | 0.020 | -0.126 | -0.080 | FAIL (gates 2, 3, 6) | NOT RUN (stopped at budget freeze); study's own baseline matches the original exactly; row stands unchecked |
| M2 | NK3 fakeout fade, 1h B X1 | 2448 | 1227 (50.1%) | -0.034 | -0.123 | 0.019 | -0.323 | 0.420 | -0.214 | -0.159 | FAIL (2, 3, 4, 5, 6) | CLEAN (independent fill code: fill rate identical, net R within 0.001) |
| M3 | NK6 confluence L2&L3&L5 | 1996 | 1890 (94.7%) | -0.112 | -0.093 | 0.063 | -0.030 | 0.001 | -0.173 | -0.135 | FAIL (2, 3, 6) | MINOR (no bug; verdict stands) |
| M4 | NK5 NY-asia hold to 08:00 UTC | 1663 | 1541 (92.7%) | +0.074 | **+0.109** | 0.046 | +0.004 | 0.001 | -0.110 | -0.078 | FAIL (3, 6) | CLEAN (independent recompute: fill rate 0.9266, net 0.1093) |
| M5 | NY value area, POC target (SHORT at VAH, 10 coins) | 162 | 72 (44.4%) | +0.001 | -0.046 | about 0 | -0.232 | 0.425 | -0.275 | -0.246 | FAIL (1, 2, 3, 4, 5, 6; n 72 below 100) | MINOR (no bug; verdict stands) |
| M6 | Europe-low sweep reclaim, US session (BTC/ETH/SOL) | 1028 | 399 (38.8%) | -0.387 | -0.346 | 0.042 | -0.198 | 0.028 | -0.585 | -0.542 | FAIL (2, 3, 6) | CLEAN |

Adverse selection = mean gross R of the ORIGINAL next-open model over the filled subset minus over all signals (negative = the signals that fill are the worse ones). Fee saved = taker fee in R (12 bp round trip) minus maker-model fee in R per trade (maker entry 3 bp, maker target 3 bp, taker stop/time exit 6 bp); because 60-75% of fills exit at a taker stop, the saving is small.

Gate 5 (BH q 0.05 over the six placebo p values 0.020, 0.420, 0.001, 0.001, 0.425, 0.028): M1, M3, M4, M6 clear BH on the placebo alone; none of them clears gates 2, 3 and 6. Placebo p is "beats random limits with the same fill model", not "profitable": the placebos lose -0.10 to -0.73 R.

## What the maker model changes

| Finding | Evidence |
|---|---|
| Maker fee saving is real but small (0.02 to 0.06 R per trade) | most fills still exit at a taker stop |
| Level-based limits (M1, M2, M5) suffer heavy adverse selection (-0.20 to -0.32 R): price coming back to the level is exactly when the reclaim/fade fails | gross of the filled subset is worse than all signals |
| Level-less limits at the signal close (M3, M4) fill 93-95%, so no selection, and the gain is only the fee | M3 -0.112 to -0.093; M4 +0.074 to +0.109 |
| Gross R of the original ideas, not fees alone, is the gap | M1 gross +0.049 vs fee 0.086; M3 gross +0.040 vs fee 0.133 |

## Baseline replication (original taker rows)
M1, M2, M3, M4, M5 reproduce their original RESULT exactly (same n, same net to 3 decimals). M6 is a replication on Binance spot vs the original Bybit perp (net within 0.02-0.06 R; n within 3%), so M6 is a like-for-like re-run, not an exact one.

## Caveats and flags
- M1 adversarial checker was NOT RUN (stopped at the supervisor's budget freeze). Next step: one checker agent on `M1/` (recompute fill rate and net R for 30+ signals by hand, truncation test). The other five rows have a checker; none found a bug.
- The weekly limit killed the library agent and the first M1 agent mid-run (06:16 local). The library files and tests were on disk; M1 was re-run in a second workflow. Library tests are covered by each study's own tests and the checkers' independent recomputation.
- M2 checker note: the market stop fills at the stop price with no gap slippage (an optimism in favour of every row); the true results would be slightly worse.
- M4 is a fixed-time (08:00 UTC) hold with no target, so a maker entry is not what drives it; its +0.109 is the NK5 long tail (30% win rate), not fill selection. Day-cluster CI [-0.110, +0.357].
- M5 n 72 is far below the 100 gate: UNDERPOWERED as well as negative; M5 and M6 limit orders live only 5 x 1m (5m entry bar) as PRE_REG fixed; M6 sensitivity at a 60 min life: fill 57.7%, net -0.325 (still FAIL).
- Gates 5 in the per-row files were computed provisionally; the table above has the final BH over all six.
- Regime mix (VAL coin-days) for the NK rows: UP 24.8 / DOWN 35.1 / RANGE 40.1 %; per-row mix in each RESULT_Mx.md.

## Files
`MyTradingSys/research/maker-entry-1114_2026-11-14/` (PRE_REG.md, RESULT.md, lib/, M1..M6 each with study.py, test_study.py, RESULT_Mx.md, results.json, check_Mx.py where run). 1m data: `F:\MTS\data_cache\binance_1m\` (20 coins, 2019 to 2026-11-13).

## Next (if the operator wants more)
No path from here runs through maker entries on these ideas. The decision-relevant remainder: gross R of about +0.30 per trade is needed (EDGE_POSTMORTEM_1114); none of the six produces more than +0.24 (M4, a tail result that failed on 14 fresh coins).

Regime mix: VAL coin-days UP 24.8% / DOWN 35.1% / RANGE 40.1% (NK rows); M5 BTC>200d: 58% bull / 25% bear / 17% range; M6 signals up 39 / down 33 / range 28 %.
