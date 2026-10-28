# B183 - Session start ritual audit after AI-health changes

Opened 2026-10-12 | Status OPEN | Severity MED | FIXER: Claude | LOGGER: Claude
Source: Control Room inbox kvsh4c9zt1bvw26dhore (verbatim in system/OPERATOR_INBOX.md)

## Operator words

we have had changes in the way to improve AI health in MTS - I still see sessions doing starting rituals - is it expected/correct/optimized? If not fix as per our goals.

## What

Sessions still run the start ritual (boot read, sync start, STATUS/LESSONS reads, inbox fetch) after the AI-health changes. Measure whether that is still needed, then trim.

## Fix shape

Measure what a fresh session reads and runs at start from transcripts. Compare to the B172 token plan. Trim what is redundant. The refiner scopes it. Relates to B172.

## Done when

A token count of a fresh session boot is below the 2026-10-12 baseline, or a written reason says the ritual is required.
