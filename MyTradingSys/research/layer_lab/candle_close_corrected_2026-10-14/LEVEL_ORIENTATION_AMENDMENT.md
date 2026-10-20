# Additional directional level arm, registered before its analysis

2026-10-14. The first corrected result was inspected and remains preserved in analysis_v1/. Its six candle-signature arms are unchanged.

A semantic review found that the `level_test` arm pools both trade orientations of each encounter. Where joint context and matching are symmetric (e.g. TRANSITION_OTHER), signed gross returns cancel exactly, funding cancels, and the mean cost screen becomes -14bp by construction. The example 1m/4h/TRANSITION_OTHER cell has 2304 matched rows, gross 0 and net14 -0.0014. This is a direction-balanced diagnostic, not evidence for or against level-bounce skill. Keep it in the registry, but make it ineligible as a candidate; do not silently replace it.

Register a separate OURS `level_bounce` arm: REAL versus PLACEBO encounters, but side=known approach (previous close above level implies long bounce; previous close below implies short bounce). Approach is already fixed before the contact bar. Controls use the exact same side/approach/phase/family/high-low identity, calipers and common three-bar decision; donor days exclude the signal day. No signature filter, no selecting a favourable direction from later prices.

The family becomes (six signatures +direction-balanced diagnostic +directional bounce) x7 TF x3 level families x6 contexts x2 horizons=2016 cells, with conservative metric correction 6048. Retain the diagnostic's cells in multiplicity counting so the bar cannot be lowered after seeing output. All phase thresholds, matching rules, costs, horizons and six signal definitions remain frozen. Reuse the identical feature/outcome ledger with a recorded hash, rematch only the new arm, and recompute bounds under the enlarged family. This is an additional logged DEV analysis, not OOS, and not a hidden rerun of the original candidate search.

The original feature/outcome engine hash is retained alongside the revised analysis hash. FROZEN_ATTEMPT2.json and analysis_v1 preserve code/result provenance. This amendment was written before viewing aggregate directional-bounce results; the algebraic cancellation, not a promising return, motivated the new arm.
