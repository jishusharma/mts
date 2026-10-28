# B097 - kXhIAug0Gh8_v2.md line 65 mislabels trade 1 as entry-before-proof

Status: OPEN | Severity: LOW | Opened 2026-10-03

## Defect

The v2 extract line 65 says trade 1 was entered before proof. Decision rows
6-7 (kXhIAug0Gh8_v2.md:23-31) place the rejection / selling-overhang read
before the entry. The transcript supports proof-first.

## Evidence

- extracts/v2/tom/kXhIAug0Gh8_v2.md:65
- extracts/v2/tom/kXhIAug0Gh8_v2.md:23-31 (decision rows 6-7)
- MyTradingSys/research/EXEC_PROVENANCE_AUDIT.md E10 cross-check row

## Found by

TF4 session MTS-2026-10-03-1444Z-CLI-BLD-tf4-execution-proven, noted as
found-and-not-fixed (read-only session).

## Fix shape

Edit line 65 to match decision rows 6-7: proof first, entry second.

## 2026-10-05 receipt

kXhIAug0Gh8_v2.md L65 rewritten: proof row 6, entry row 7, further proof row 14. DSA session MTS-2026-10-04-1325Z-DSA-COO.
