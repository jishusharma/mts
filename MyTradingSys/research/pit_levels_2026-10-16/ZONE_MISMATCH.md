# Java vs Python prior-day zone mismatch (2026-10-16, session java-zone-mismatch)

Source: commit 59b85fd2, `level_ledger_2026-10-16/java_zone_check.py` (48 DEV days, 144 levels, 79 match = 54.9 %). Re-run here: identical (79/144).
Classifier: `level_ledger_2026-10-16/zone_mismatch_classify.py` (Python port of Java `buildVp`, checked against the compiled Java: 144/144 levels equal to 0.01). Counts only, DEV days, no outcomes.

## Counts per cause (65 mismatching levels, sequential attribution)
| cause | POC | VAH | VAL | total |
|---|---|---|---|---|
| session/day boundary or timezone | 0 | 0 | 0 | 0 (both sides get the same UTC-day closed 1m bars) |
| bar-close vs intrabar | 0 | 0 | 0 | 0 (closed bars on both sides) |
| data source / volume field | 0 | 0 | 0 | 0 (same arrays) |
| lookback | 0 | 0 | 0 | 0 (same window) |
| rounding / edge convention (Java reports bin lower edges; research: POC = bin centre, VAH = top edge) | 4 | 9 | 0 | 13 |
| grid / bin size (Java dynamic ~5 USDT, origin = day low; research 10 USDT fixed) | 7 | 7 | 8 | 22 |
| VP weighting algorithm (Java triangular around typical price, sample points; research uniform overlap) | 9 | 8 | 12 | 29 |
| unresolved (near-tied peaks, VA path) | 0 | 0 | 1 | 1 |
| **mismatches** | 20 | 24 | 21 | 65 |

Order: edge, then grid, then weighting, then remainder; a level is counted in the first counterfactual that makes it match.

## Which side is wrong (FORMULAS.md 18.1)
- Edge convention: Java deviates from 18.1 (VAH/VAL are lower edges of the bounding bins, so VAH is one bin, about 5 USDT, low). A real but small defect, 13 of 65.
- Grid and weighting: 51 of 65. FORMULAS 18.1 itself marks the 10 USDT grid NO-SOURCE and the weighting difference as "accepted"; Java's ~5 grid and triangular weights are NO-SOURCE too. Neither side is defined by the trader's words, so neither is "wrong" against a source.
DECISION (OURS): ambiguous, report only. No Java or research code changed; changing live `buildVp` on an unsourced choice would alter live behaviour without evidence it is more right.
Follow-up for the owner: pick one sourced profile definition for both sides (the W2a adapter already uses the Python reference), then port it to Java with the live-path gate.

## DECISION (OURS) - single volume-profile definition (card zone-profile-standard-ours, 2026-10-17)
Label: OURS (NO-SOURCE; chosen for reproducibility, not for edge). The one profile definition for research is FORMULAS 18.1:
1. Grid: fixed 10 USDT bins anchored at multiples of 10 (bin k = [10k, 10k+10)).
2. Weighting: uniform overlap spread of each bar's volume over its high-low (point mass if high == low).
3. Edge convention: POC = bin centre, VAH = top edge of the top value-area bin, VAL = bottom edge of the bottom bin.
Pinned by `level_ledger_2026-10-16/test_zone_standard.py` (3 hand-computed days; `standard_profile()` in the classifier;
registered in run_extra_tests.py). No Java file changed.
Follow-up Q for NB (JIS-NB live-path item, not done here): port this definition to `MarketDataSnapshot.buildVp` (10 USDT fixed grid,
uniform weights, 18.1 edges) with the live-path gate (restart/reset state, API errors), or keep Java's ~5 USDT triangular profile and
accept that live zones differ from research zones (51 of 65 mismatching levels are grid and weighting, 13 are edges). Default if no answer: keep Java as is.
