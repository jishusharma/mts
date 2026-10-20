# SHOT_REVIEW.md (c) patches C1-C12: what was applied (2026-10-20)

Applied to SPEC.md and the rsi-deep-* cards. No other step changed, no backtest run. Every new parameter is in the SPEC s5 trial-ledger table with its SOURCED/OURS label. OPUS_FRAMING.md wins where the two differ.

| Patch | Where | Status | Why / note |
|---|---|---|---|
| C1 | SPEC Step J pairing rule; card divergence-context | applied | P-anchor is primary, episode end above 50 (40/60 trials), P-anchor-split variant. h = 3 fixed added (OPUS_FRAMING s1). |
| C2 | SPEC Step J, new bullet "Price basis and tolerance"; trial ledger | adjusted | Conflict: OPUS s2.3 wants one value per parameter in the first pass, so the first pass is the primary row only (close, eps 0, min diff 0) and the rest are exploratory rows. "decimals count" cited as `rsi_divergence.py:7` (the review said `:6`, but line 6 is the params note). Added the long-mirror wording of FAILURE_SWING. |
| C3 | SPEC Step I sequence features; card divergence-context | adjusted | Added a look-ahead guard: "earlier firing reached +fee" counts only firings resolved before this B's stamp. |
| C4 | SPEC Step I context item (2); card divergence-context | applied | Merged into (2), so the 8-feature cap holds. |
| C5 | SPEC Step H candidate voters; card confluence | applied | Both voters fit inside the 8-voter cap. The WaveTrend count stays NOT_IN_DATA until `wavetrend-data-inference` pins its inputs. |
| C6 | SPEC Step J RSI regime; card divergence-context | adjusted | The five-week sanity weeks (2026-09-15..10-19) are HOLDOUT, so the check compares RSI floors only and reads no outcomes. |
| C7 | SPEC Step J phase key; card divergence-context | applied | Step I item (8) "session (Asia/EU/US)" left as is: the patch names Step J only. |
| C8 | SPEC Step G, new last bullet; cards divergence-context, prereg | adjusted | Conflict: OPUS s2.3/s5 (cut cells, stage order) beats "every table, before any engine work". The mirror is built only on TFs that survive Stage 0 on the long side, as exploratory rows, and does not block the engine. |
| C9 | SPEC s3 X1-X3 line; card run-dev | applied | The table itself is produced by econ-floor (C12). |
| C10 | card divergence-context tests | applied | K1-K10 fixture test, +-0.5 RSI. The same cases are also acceptance tests on card engine (task instruction). Tests assert detector outputs only, because the fixture windows are in HOLDOUT. |
| C11 | card confirmations | adjusted | Conflict: OPUS s3 item 7 defines C8 location as a new 7d/30d low. The 24h sweep is added as a third pre-registered form and does not replace those two. |
| C12 | card econ-floor | adjusted | Conflict: OPUS s5 Stage 0 is "one table". The trough-to-40/50/60 table is descriptive output from the same pass and stays out of the H1 kill. |

Cards with no matching patch: depth-map, prob-tables, context-tables (unchanged). Observed, not fixed: the rsi-deep-prob-tables `goal` ends mid-sentence ("...rarity").
