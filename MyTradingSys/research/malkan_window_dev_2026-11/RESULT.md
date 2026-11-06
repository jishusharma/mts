Regime mix: 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)
VERDICT: INCONCLUSIVE (underpowered; power gate BLOCK, see PRE_REG.md / BLOCKED.md). Default window 3-10 unchanged.

# RESULT: Malkan regular-divergence windows, fee-net, DEV 2022-01..2024-06, BTC+ETH pooled

Cost 0.14 % round trip, entry at event-bar close, exit 10 bars later, cluster = symbol x day, Holm m = 16. Files: `dev_cells.csv`, `counts.csv`.

| TF | Side | Arm | n | days | gross % | fee-net mean % | 95 % CI | Holm p |
|---|---|---|---|---|---|---|---|---|
| 1h | bear | S3_10 | 550 | 405 | -0.106 | -0.246 | -0.443..-0.049 | 0.213 |
| 1h | bear | B11_12 | 1 | 1 | 1.49 | 1.35 | n/a | 1.0 |
| 1h | bear | C13_18 | 2 | 2 | 2.22 | 2.08 | 0.48..3.68 | 0.177 |
| 1h | bear | D19_50 | 0 | 0 | | | | |
| 1h | bull | S3_10 | 517 | 399 | -0.021 | -0.161 | -0.393..0.072 | 1.0 |
| 1h | bull | B/C/D | 0 | 0 | | | | |
| 4h | bear | S3_10 | 132 | 128 | 0.092 | -0.048 | -0.748..0.653 | 1.0 |
| 4h | bear | B/C/D | 0 | 0 | | | | |
| 4h | bull | S3_10 | 129 | 125 | 0.181 | 0.041 | -0.818..0.900 | 1.0 |
| 4h | bull | B11_12 | 1 | 1 | 4.30 | 4.16 | n/a | 1.0 |
| 4h | bull | C13_18 / D19_50 | 0 | 0 | | | | |

Findings:
- No cell survives the DEV rule. Every fee-net mean for the SOURCED 3-10 arm is below or inside noise of zero (1h bearish -0.25 % is the only CI wholly below zero, Holm p 0.21).
- The OURS windows (11-12, 13-18, over 18) hold 4 events in total on DEV. With consecutive strict-close swings, a pair more than 10 bars apart is almost never the next pivot, so this detector cannot test the operator's 12 / 18 / over-18 split. The two non-empty cells (n=1, n=2) are anecdotes, not evidence.
- Not a PASS, not a FAIL: the power gate blocks (1h needs ~3227 days, has 405; 4h needs ~12907, has 128).
- Next step (needs a different detector, e.g. non-adjacent swing pairs or a wider pivot strength; not built here): compare windows on pivots with a lookaround of 3+ bars so 11-50 bar spans occur.

Not read: VALIDATION, HOLDOUT. Default window unchanged.
