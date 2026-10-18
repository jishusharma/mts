# layer_map.json null rows, 2026-10-19

Filled (fact stated in the report):
- BIGMOVES-A n: BIGMOVES_REPORT.md:160,165,170,175 (section 7 table, "all legs": 4h 1930, 1h 8173, 15m 33790, 5m 105235).
- FIRES-B1 split: FIRES_B1_REPORT.md:1 ("This report holds no split-based result").

Left null:
- BIGMOVES-A fees, split: not stated in BIGMOVES_REPORT.md (ground-truth legs only).
- CAPTURE-MATRIX n, split: not stated in CAPTURE_MATRIX_SPOT.md (only 51084 unscored rows, line 5; no scored-fire total).
- CANDLE-D19 split: not stated in D19_4H_RESULTS.md.
- VOL-V3 fees: not stated in V3_VALIDATION_RESULTS.md (gross +14 bp, net -2 bp, but no fee value).

Families without a card, no card created (no concrete goal in repo docs: LAYERS.md lists them as closed / no edge):
- guidance (Q33: no surviving cell, do not wire; Q34 skipped).
- session_timing (session_momentum FAIL, turn_of_candle no edge, session_levels no edge).
- cryptocred was not in scope.
