# B185 - Build-Check passes a malformed BUGS.md row silently

Status: OPEN (filed 2026-10-12). Severity MED.
Source: BUGS.md row B185; found by session MTS-2026-10-12-1403Z-DSA-COO.

## What happened

The mts-dsa work tree (HEAD 1ce3b3de claim reg-close-stale-rows) holds an uncommitted BUGS.md, written 2026-10-12 11:05:47 UTC by session MTS-2026-10-12-1032Z-APP-BLD-reg-close-stale-rows, the reg-close-stale-rows card.

In that copy the B141 row has receipt text spliced into the evidence cell, after the text R <= 0.8*sqrt(N)*ATR_N and, which splits the pre-existing pipe characters that close the evidence cell. The row keeps status OPEN, so no receipt check fires. The bug-row parser still reports Bugs: OK (249 rows).

## Why it matters

A malformed row that passes the check is worse than a failing row: the register is the single source of truth for defects, and a silent pass hides the damage. The cell-count check only fires below the header width, not above it.

## Fix shape

1. Restore B141 to one evidence cell and one empty receipt cell in the mts-dsa copy, owned by the session that wrote it.
2. Find why the bug-row parser accepts a row whose cell count exceeds the header, and reject it.

## Updates

- 2026-10-12: filed by session MTS-2026-10-12-1403Z-DSA-COO.
- 2026-10-12: the B141 malformation itself is in another session's uncommitted work tree; this row tracks the parser gap, not the B141 edit.
- 2026-10-14: renumbered from B177 (origin fast-track already used B177 for the Layer Board row). B141 restored on fast-track by jis-nb/fix-live-edits: abs(c-poc) in the evidence cell, the section 9 receipt in its own cell, 7 cells. Parser guard (reject over-wide rows) still open.
