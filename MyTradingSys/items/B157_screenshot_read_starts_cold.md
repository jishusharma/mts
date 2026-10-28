# B157 Each screenshot read starts cold: the extract template has no prior-context slot and the next read does not score the previous read's falsifiers

Filed 2026-10-10 by T092 (Opus, JIS-NUC). Report: MyTradingSys/research/screenshot_context_2026-10-10/REPORT.md. Owner group: VIS.
Operator words (T092 brief, verbatim): "Does it have the context already built up. Does it apply it to the current screenshot?"

## Evidence
R1 wrote 'acceptance outside 82450-83470' and R3 'acceptance under 82630 = next daily POC ~82488' (live_reads.md:22,78); the 20:13Z read of shot 78f967b4e253 at C 82366.2 says neither was broken and calls the operator ray ~82496 'not established' although R2 had matched it to the daily VP POC (live_reads.md:38).

## Smallest fix
TEMPLATE.md gets a '## Carried context' section; shot.py read refuses a chart extract without a `Prior:` line (extract path or `Prior: none`) and returns the prior extract's Invalidation/Falsify lines to score HELD / BROKEN / UNTESTED.

## Test that fails first
test_shot.py: a chart extract with no `Prior:` line is accepted by read_extract today.

## Provenance
No market parameter is introduced; any window or threshold is an analysis setting printed in the output.
