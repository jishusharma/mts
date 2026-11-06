# Blind read: level_approach_eth_2026-11 (C15 ETH / pooled replication)

Method: read PRE_REG.md agreement rule and sequences.csv first; recomputed rule 1 (n>=30 in BTC-A, BTC-B, ETH-A, ETH-B), rule 2 (same nonzero sign of p_half minus that symbol's base in all four cells) and rule 3 (pooled Wilson 95% CI, z=1.96, from POOL_n and POOL_p, excludes POOL_base) for the 64 near_miss / wick_back rows. Only then read RESULT.md. Not an independent event-level recomputation: the CSV cells are taken as given.

| Quantity | Recomputed | RESULT.md | Match |
|---|---|---|---|
| Rows judged (near_miss + wick_back) | 64 | 64 | yes |
| AGREES | 4 | 4 | yes |
| DISAGREES | 20 | 20 | yes |
| UNDERPOWERED | 40 | 40 | yes |
| Row-level label vs CSV `agreement` column | 0 differences in 64 | | yes |
| Verdict rule (>=1 AGREES) | REPLICATES | REPLICATES | yes |

Agreeing rows (all recomputed AGREES):
| class | TF | RSI>=50 | CVD12>0 | >BB mid | pooled n | pooled p | pooled base | RESULT.md |
|---|---|---|---|---|---|---|---|---|
| near_miss | 1m | 0 | 0 | 0 | 889 | 0.244 | 0.278 | AGREES (this is the C15 invalidation row) |
| near_miss | 1m | 0 | 0 | 1 | 1394 | 0.306 | 0.278 | AGREES |
| near_miss | 5m | 0 | 0 | 1 | 401 | 0.389 | 0.325 | AGREES |
| wick_back | 5m | 1 | 1 | 0 | 363 | 0.295 | 0.369 | AGREES |

C15 invalidation row (near_miss 1m, RSI<50, CVD12<=0, below BB mid): BTC n 466 p 0.2103 (A 0.2219 / B 0.1765); ETH n 423 p 0.2813 (A 0.287 / B 0.2746); pooled n 889 p 0.2441 vs base 0.2780, Wilson 0.217-0.273 excludes base; signs all negative vs base (BTC 0.2597, ETH 0.2968). Matches RESULT.md line 13 (BTC 466 / 0.210, ETH 423 / 0.281, pooled 889 / 0.244 vs 0.278, AGREES).

Diffs: none. Caveats unchanged from PRE_REG: no multiplicity correction over 64 rows, overlapping events make Wilson CIs too narrow. Note that the 4 pooled-base values differ by TF and class, and the rule uses each symbol's own base for sign and the pooled base for CI, as frozen.

FOUND: 6 of 6 headline numbers (64, 4, 20, 40, invalidation row, verdict). DIFF: 0.

VERDICT: MATCH
