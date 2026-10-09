# B159 screenshot claim rows (MATCH/MISMATCH/NOT_IN_DATA) are kept only as counts; context reads without a side are never scored

Filed 2026-10-10 by T092 (Opus, JIS-NUC). Report: MyTradingSys/research/screenshot_context_2026-10-10/REPORT.md. Owner group: VIS.
Operator words (T092 brief, verbatim): "Does it have the context already built up. Does it apply it to the current screenshot?"

## Evidence
shot.py read_extract counts rows by regex and appends only `claims: counts` (scripts/dev/shot.py:406,414); missed.py scores only setups with a side (missed.py:6,12).

## Smallest fix
Store each claim row {id, class, claim, evidence} on the `read` event; follow-up: falsifier/invalidation lines to capture.py as chart_read with level.

## Test that fails first
test_shot.py: the manifest of a read 78f967b4e253-style extract holds 9 claim dicts (fails: holds counts only).

## Provenance
No market parameter is introduced; any window or threshold is an analysis setting printed in the output.
