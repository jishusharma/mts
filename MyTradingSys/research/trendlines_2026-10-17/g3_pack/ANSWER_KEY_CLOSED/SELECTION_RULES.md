# Window selection rules (CLOSED with KEY.csv: readers must not open)

Seed 20261017, per unit `<seed>-<code>`. Per unit 20 windows: 10 random (any eligible right edge, the false-positive floor) and 10 candidate-enriched (pre-filter true at the edge). Window ids carry the unit code and a shuffled number only.

## Pre-filter (OURS, written before any mark, causal: bars up to the decision bar only)
A decision bar i is a candidate when a legitimate line is live at i, on the contract's terms (`TRENDLINE_CONTRACT.md`, plain-SMA ATR(14), log price, wick arm):
1. swings with k=3 (strict, ties disqualify), known only from the close of bar j+3 (P2-P4, P6);
2. two same-side swings a < b, 10 to 200 bars apart (L3, L4), support rising / resistance falling, not flat: |pb-pa| > 0.25 ATR_b (L2, L7);
3. strict penetration test over a..b: no low (high) beyond the line by more than 0.10 ATR_b, no close beyond it (L6);
4. no close beyond the line between b and i (B1);
5. a third swing c after b, confirmed by i, with |price_c - line(c)| <= 0.25 ATR_b (E3);
6. the last close is within 3.0 current ATR(14) of the line at i (pre-filter only, OURS; keeps the line relevant to the picture).
Tag in the key: support / resistance / both. Counts before sampling (first version without rule 6: TL-4H 3007 of 5118 eligible, TL-1D 658 of 1218; rule 6 was added because 59 % / 54 % candidates is no enrichment).

## Sampling
Eligible edges: 4h bars with right edge 2022-03-01..2024-06-30 and at least 200 earlier bars; 1d bars from 2021-03-01 with at least 180 earlier bars. Enriched half: seeded shuffle of candidates, greedy spaced pick (TL-4H 40 bars, TL-1D 20 bars). Random half: seeded shuffle of all eligible edges, same spacing, spaced against the enriched picks. Final order shuffled, ids assigned in that order.
