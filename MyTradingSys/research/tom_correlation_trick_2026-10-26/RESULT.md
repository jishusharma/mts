# RESULT: TOM-CTX-DIV (2026-10-29)

**Verdict: NOT-ADD.** Neither primary variant has positive fee-net expectancy on DEV, and neither passes VALIDATION. Holdout not read (rule: only if VALIDATION passes). All parameters OURS; PRE_REG.md frozen before any outcome.

| Variant (primary, hold 3d) | Split | n | Mean net | Cluster SE | Boot lb95 |
|---|---|---|---|---|---|
| H1 DAX vs ES/Nikkei/BTC, L=2, top 20% | DEV | 35 | -110 bps | 79 | -266 |
| H1 | VALIDATION | 8 | -93 bps | 55 | -227 |
| H2 BTC vs ES/DXY(flip), L=2, top 20% | DEV | 52 | -72 bps | 91 | -240 |
| H2 | VALIDATION | 16 | -19 bps | 56 | -146 |
| H1 / H2 | HOLDOUT | not read | | | |

- Control (a), same move without cross-market condition: H1 DEV +1 bps (n 116), VALIDATION -59 bps (n 35); H2 DEV -99 bps (n 167), VALIDATION +16 bps (n 42). H1 signal did not beat control (a) on VALIDATION in a useful way (both negative); H2 VALIDATION signal (-19) is below control (+16).
- Shuffled-basket placebo (100 draws): H1 DEV placebo mean -0.4 bps, p95 +45 bps; real -110 bps. H2 DEV placebo -57 bps, p95 +77 bps; real -72 bps. 100% (H1) and 59% (H2) of placebo draws were at or above the real result: no cross-market information.
- Divergence-day entry (Tom's warned timing), reported not selected: H1 DEV -41 bps (n 38), H2 DEV -37 bps (n 79).
- Across the 40 DEV cells (lookback 1/2/3/5 d, 3+2 baskets, cut 0.8/0.7) only 10 are positive, all with lb95 < 0; best H1 B1 L3 +83 bps lb95 -60 bps. None selected (VALIDATION is primary-only by PRE_REG). All 40 are in layer_lab/TRIALS.md.
- Power: VALIDATION n is 8/16 and HOLDOUT would be 11/7, all below 30 by construction (INCONCLUSIVE at best); the DEV result is the informative one, and it is a clear fail.

Deviation from EXTRACT s4: daily as-of grid instead of hourly (free hourly history too short); recorded in PRE_REG.md. TOM-DIV flag is not added to the Tom layer; A-C4 keeps the unextended basket. Reproduce: `python run_div.py --split DEV` (data refresh: `fetch_data.py`, data/ committed, public).
