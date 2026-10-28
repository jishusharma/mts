# B161 screenshot indicator header values (BB, RSI, VWAP) are hand-typed and recomputed ad hoc per read; no check tool

Filed 2026-10-10 by T092 (Opus, JIS-NUC). Report: MyTradingSys/research/screenshot_context_2026-10-10/REPORT.md. Owner group: VIS.
Operator words (T092 brief, verbatim): "Does it have the context already built up. Does it apply it to the current screenshot?"

## Evidence
78f967b4e253 header typed by hand (extract line 14) and BB/RSI recomputed by hand (D-02, D-03); the Sep-2026 JSON extractor was never used (screenshot_intake.md:84).

## Smallest fix
`shot.py header <id>`: recompute BB/RSI from fapi klines with the chart legend's own settings at `at`, print the diff vs the typed header. VWAP stays NOT_IN_DATA until the chart anchor is known.

## Test that fails first
test: a typed header with a wrong BB mid is not flagged today.

## Provenance
No market parameter is introduced; any window or threshold is an analysis setting printed in the output.
