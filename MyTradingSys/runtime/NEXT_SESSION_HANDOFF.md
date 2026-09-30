# NEXT SESSION HANDOFF
# Rewritten 2026-09-30T15:05Z by MTS-2026-09-30-1500Z-DSA-COO.

STATUS: Loop FAIL (java absent, supervisor absent, snapshot 967 min old).
Build PASS 2026-09-30T14:59:38Z. HEAD b46cbdc. Bugs 131 rows.
Index 25 open IDs. Working tree clean.

## THIS SESSION - WHAT LANDED

- USER.md: two reply-format rules added to COMMUNICATION.
  Every reply inside one fenced code block. Replies to another AI
  surface passive. COMMUNICATION block tightened. 3828 bytes, 87
  lines. Commit b46cbdc.
- items/INDEX.md: rows added for T053-T058. 51 lines. Commit b46cbdc.
- BUILD_REPORT.md: fresh PASS. Commit b46cbdc.
- DSA_SESSION_PROMPT.md: rules 8 and 9 added to section 3.
  Rule 8: path prefix. extracts/ has no MyTradingSys prefix. Test
  both path forms before claiming a file missing.
  Rule 9: cross-surface note header is exactly two lines.
  "<MTS|CBP> NOTE - from DSA COORDINATOR - <date>" then
  "To: <MTS Claude|CBP Claude>". Nothing else. Check the reply's
  file paths before naming the target.
- Two junk files from a mangled PowerShell paste removed from repo root.

## CLOUD WORK UNMERGED

origin/cloud/work at 304cc13, two commits past 357ffd6.
  74e4aa9 Missing-pieces research: Fabio/Tom applied readings, H1-H3
    (model only). 34,366 bytes, 446 lines.
  304cc13 03_FILE_INDEX header fix.
origin/main still 851218e. Local main b46cbdc, one commit ahead.
No merge scheduled. Operator decision.

## TASK 999

Output lost. Marked [x] in DSA_BACKLOG.md:16, no row in
DSA_GATE_LOG.md, no CONSOLIDATED_RULES.md file. Re-pack inputs
present at extracts/processed/tom/new_selected_10/ (extract_WQ_OAdz-PJ8.md,
extract_zAwEX_tRUfE.md, plus seven others).

## FEE SOURCE CONFLICT

Two incompatible fee constants for the same instrument.
  MyTradingSys/backtest/sim.py:18-20 - maker 0, taker 0.05%,
    source "verified 2026-09-26 via public/get_instrument".
  MyTradingSys/backtest/layers/fabio/fabio_of_model.py:40-44
    FEE_TAKER=0.00035, FEE_MAKER=-0.00015, source
    "T055b_PROVEN_SETUPS.md fee floor".
One source of truth needed before any layer verdict is trusted.

## OPEN QUEUE (from BUGS.md open rows)

T037 (pom), T040 (tick-delta), T042 (1w/1d/4h consumer), T044 (hybrid
REST/WS alert), T046 (Stage 3), T048 (satellite framework), T049 (NUC
worker v2), T050 (Deribit phase 3), T051 PARKED, T052 (SETUP_CONFIRMED
trigger), T053-T058 (new), T059 (paste size guard). B063 divergence
operator decision, B066 rank-1 distance gate, B069 wrapper stderr,
B070 UTC 00:00 + 0.75 slippage demote, B072-B079 (input validation,
net_rr rounding, rule order, historical mode, SETUP_CONFIRMED
unreachable, stop order type, cancel scope, caps_check enforcement).

DSA_BACKLOG.md sections open: cross-trader rulebook, T054 brief,
Fabio spec + impl, malkan/rsi_ma drivers, formula audits 083/084,
TOM_CORE_BT method review, FABIO_OF_REPORT review.

## NEXT SESSION - FIRST ACTION

1. Read items/INDEX.md + BUGS.md open rows.
2. Read DSA_SESSION_PROMPT.md section 3 rules 8 and 9 before any
   cross-surface reply.
3. State ROLE (COORDINATOR). State MISSION. Act.
4. Operator picks one: fee-source conflict, task 999 re-pack, or
   Cloud MISSING_PIECES review.

## DO NOT MISS

- extracts/ has no MyTradingSys prefix.
- Cross-surface header is exactly two lines. No role, no authority,
  no placeholder.
- Check reply file paths to decide MTS vs CBP destination.
- DSA_SESSION_PROMPT.md section 14 must not exist. If found, stop.
- Cloud is bound by CLAUDE.md only, not USER.md. USER.md rules do
  not reach Cloud.

## HARD RULES

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- Critical files: hash, edit, hash, diff.
- Read target line from disk same turn before composing anchor.
- MarketDataSnapshot.java is CRLF. math_object_builder.py is CRLF.
  SetupCandidatesBuilder.java is LF.
- PROJECT_VISION doctrine: modules never gate core.

# END