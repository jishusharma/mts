# B160 screenshot reads compare against whatever snapshot is current (or none); the engine's archive mode can rebuild its state at the screenshot's instant but no read calls it

Filed 2026-10-10 by T092 (Opus, JIS-NUC). Report: MyTradingSys/research/screenshot_context_2026-10-10/REPORT.md. Owner group: VIS.
Operator words (T092 brief, verbatim): "Does it have the context already built up. Does it apply it to the current screenshot?"

## Evidence
MarketDataSnapshot archive mode (MarketDataSnapshot.java:40-46), saveHistoricalSnapshot (:1368-1377) and research harness SnapAt.java exist; 78f967b4e253 had 5 of 9 rows NOT_IN_DATA for lack of a snapshot.

## Smallest fix
`shot.py engine <id>`: SnapAt at the shot's `at` floored to the minute, output beside the extract; rows cite it. Needs the 1m archive on the machine (else DSA task on JIS-NB).

## Test that fails first
test: wrapper refuses a shot without `at` and builds the instants file (fixture, no Java).

## Provenance
No market parameter is introduced; any window or threshold is an analysis setting printed in the output.
