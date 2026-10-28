# B101 - DSA asks for context files already available as one-liners

Status: OPEN. Severity: LOW. Opened 2026-10-04.

## Defect

Before printing a CL prompt, DSA asked the operator to paste CLAUDE.md
and the mts go launch block text. Both are one-liners on disk.

- CLAUDE.md prompt cap: "Prompt <= 30 lines." One line, already quoted in
  LESSONS_LEARNED.
- mts go launch: mts.ps1 at repo root, invoked as "mts go". Wired
  2026-10-04, commit a516139.

Cost per occurrence: two extra round trips. No state damage.

## Evidence

Session MTS-2026-10-03-2037Z-DSA-COO. Boot handoff from
MTS-2026-10-03-2030Z-DSA-COO-close. The coordinator note that flagged
this cited session 2033Z; disk shows 2037Z.

## Fix (Claude decides)

(A) DSA composes the prompt body without a disk read; cap and launch
    block are held as one-line facts.
(B) Composer quotes cap and launch in one line at the top of every CL
    prompt composition.
(C) No change: accept the round trips.

## Receipt

-
# END
