# NK phase-specific + MTS brains: synthesis (2026-11-14)

**VERDICT: FAIL. 0 of 17 DEV-chosen cells (nkp1 3, nkp2 2, nkp3 12, nkp4 0) pass VAL (2024-26) fee-net at 12 bp. Phase plus MTS context did not make any NK rule useful.**

Cells were chosen on DEV (2019-2023) only, tested once on VAL, with fee in R. Studies: nkp1 session rules, nkp2 levels, nkp3 Hilega-Milega, nkp4 NK + MTS confluence. All four have independent reviews; each supports its verdict.

## Per phase

| Phase | Best NK + context cell (study) | n VAL | Net R 12bp | Day CI low | Pass |
|---|---|---|---|---|---|
| MARKUP | NK2-core long, OI 24h <= -3% (nkp2) | 1081 | -0.021 | -0.175 | No |
| MARKUP (session) | NK1-UTC long, 4h %B < 0.10 (nkp1) | 232 | -0.174 | -0.819 | No |
| ACCUM-RANGE | BO4h long, 4h RSI >= 60 (nkp3) | 384 | +0.324 | -0.322 | No (placebo p 0.14, ex-best-5 negative) |
| CAPITULATION | X3 long, NK + 3 MTS layers agree (nkp4) | 306 (6 days) | +0.347 | -0.202 | No, under-powered (2.8% of DEV days) |
| DISTRIBUTION | NK2-core short (nkp2) | n/a | descriptive only | n/a | No cell kept (DEV sign opposite) |
| MARKDOWN | NK5 NY-Asia short (nkp1) | 229 | +0.749 descriptive | n/a | No cell kept (DEV net -0.482) |
| RELIEF | none | n/a | n/a | n/a | No cell kept |

## What we learn

- DEV winners shrank on VAL by about 1 R (nkp1 mean -1.006 R). That is the signature of chance selection, not edge.
- Gross R sits near 0 (-0.12 to +0.09). Fee plus funding costs 0.15-0.23 R per trade, so fees decide.
- Phase-appropriate direction did not beat the opposite one. In nkp4 ACCUM-RANGE it was significantly worse (z down to -3.56).
- S2/S3 longs and R2/R3 shorts lose at every level, DEV and VAL (nkp2).
- Only lead: CAPITULATION long is positive on DEV and VAL, but on 52 DEV days and 6 VAL days. Not testable without more symbols or history.
- No phase or context layer makes NK rules useful. The one positive-net VAL cell (ACCUM-RANGE BO4h) has a CI that spans zero.

## Review corrections to carry

- nkp4 RESULT: "largest diff/se is 1.9" is wrong; JSON max |z| is 3.56. Verdict unchanged.
- nkp1/nkp3/nkp4 PRE_REG or code were edited after results (context lines, renames). Numbers unchanged; disclosure missing in RESULT.
- nkp3: "4 of 34 rows above +2 se" are all CAPITULATION rows with 1-6 days; 0 of 31 otherwise. Trades are not de-overlapped, so n is overstated.
- Seven plus six look-ahead allowlist rows were self-reviewed.
- nkp1 shipped hash quoted as 7d14af32c is wrong (that is nkp2); nkp1 is in e3a92d6e6 / 374d93942.
- nkp1 PRE_REG says C7 uses 1h returns and C8 spec session hours; code uses daily returns and 0-8/8-16/16-24. Three studies use three C8 mappings.

## Active now for BTC (descriptive, not a signal)

BTC and ETH both read MARKDOWN (label 2026-11-13; 11-14 provisional). No kept cell exists, so no trade is active. OI, funding and taker data ended before the latest bars (NO-DATA on those layers).

## Next 3 tests

1. CAPITULATION long, own pre-registration: add symbols and pre-2019 history until at least 40 independent episodes; gate on episodes, not signals.
2. Gross-edge first: drop any rule whose gross R is under 2x its fee R on DEV before spending VAL; try wider targets (fewer, larger trades) so fee is a smaller share of R.
3. Operator's hand-drawn range (BB range-to-range) with MTS context as the where, tested on more symbols with day-and-coin clustered CI and de-overlapped trades.

Housekeeping: add a PRE_REG-vs-spec diff and a research-module name-prefix check to the ship gate (tasks already filed).
