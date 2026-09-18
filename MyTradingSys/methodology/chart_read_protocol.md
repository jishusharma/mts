# CHART READ PROTOCOL
# Purpose: six-layer method for reading chart panels without single-pass error.
# Scope: chart reads only. Not system snapshot fields.
# Written 2026-09-18 by MTS-2026-09-18-0848Z.
# Evidence: method caught one material error on 2026-09-18.

## WHEN TO APPLY
Any read of an external chart: heatmap, liquidation bubble, volume profile, order flow panel.
Not for system fields. Those are quoted verbatim per live_session_protocol Rule 1.

## THE SIX LAYERS

1. Panel identification.
   Name the panel and the data source. Record axis units and time window.

2. Neutral description.
   State what is visible without interpretation. Shapes, levels, clusters only.

3. Cross-view comparison.
   Read the same level on at least one other panel or timeframe. The overlap is the honest answer.

4. Multi-timeframe context.
   Locate the level on a higher timeframe. A level inside a range is not the same as a level at the range edge.

5. Bias check.
   State what would falsify the read. A read that only confirms is a rationalization.

6. Invalidation definition.
   State the price or condition that proves the read wrong. No invalidation, no read.

## WHAT IT CAUGHT

2026-09-18: initial chart read placed a short entry at 78000. Three-layer re-read placed entry
at 79500-79700 (fuel-band top). Single-pass method missed it. Two extra reads.

## LIMITS

- Chart reads are not system data. Never quote them as snapshot fields.
- liquidation_clusters is DEPRECATED at the system level per MTS_DICTIONARY.md.

