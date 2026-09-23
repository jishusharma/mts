# NEXT SESSION HANDOFF
# Rewritten 2026-09-23T12:55Z by MTS-2026-09-23-1236Z.

STATUS: Loop ALIVE. Build PASS at 12:39Z. Architecture doctrine locked in
MyTradingSys/PROJECT_VISION.md.

## MISSION

Two streams.

Stream 1 - Session work (serial, done here).
Stream 2 - Independent Worker dispatches (parallel, six layers).

## STREAM 1 - SESSION WORK

1. Loop health check + Build-Check under pwsh.
2. Doctrine enforcement (deferred work from 2026-09-23 session):
   a. compiled_engine.md: add a header note naming which tag families are
      core vs module. Retag [CT-NNN] and [SCREENER] rules as module
      candidates, per PROJECT_VISION doctrine section 4.
   b. MTS_DICTIONARY.md: add [VISUAL FLAG] and a [CORE]/[MODULE]
      distinction to SOURCE TAGS.
   c. File T043 Phase 3 gap #3 (stop-beyond-liquidity rule 3 has no impl)
      as an OPEN bug row.
3. Log the completed hard stops slice audit result.

## STREAM 2 - INDEPENDENT WORKER DISPATCHES

Six dispatch stubs under Dumps/workers/RUN-2026-09-23-<LAYER>/dispatch.md.
Operator spawns each on its own surface. Workers write only in their own
directory. Repo changes come back as verbatim PowerShell write statements.

Layers: RSI, PROB, ANALYST, SESSION, TICK, ASSIST.

Full worker rules: MyTradingSys/methodology/live_session_protocol.md,
section WORKER TYPES.

## OPEN QUEUE (BUGS.md)

B058 part D, B059, B062, B063, B065, T034, T035, T037, T038, T039, T040,
T042, T043.

## HARD RULES

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- Ledger is not truth. Files are truth.
- PowerShell: single-quoted strings for embedded double quotes.
- One file, one change, verify before next.

# END