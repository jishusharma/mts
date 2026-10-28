# B172 - Sonnet ritual token use

Status: OPEN (filed 2026-10-10). Severity HIGH.
Source: BUGS.md row B172; Control Room inbox bftuvmoo3owp3451dabt.

## Verbatim ask

Why does the current ritual make the Sonnet agent use a lot of tokens? Is it not optimized? This is high priority. Investigate latest guidance and optimise session tokens + automatic accurate prompt creation.

## State

Step 1 measure per-session tokens from transcripts (dispatcher ticks, relay sessions, CLAUDE.md/memory/skills load); step 2 trim always-loaded context; step 3 templatize prompts. Must fit the relay session switching. Scope each step to one relay session.

## Updates

- 2026-10-12: item file created by session MTS-2026-10-12-1403Z-DSA-COO to satisfy the Build-Check rule that every OPEN row has a matching items/ file. State copied from the BUGS.md row.
