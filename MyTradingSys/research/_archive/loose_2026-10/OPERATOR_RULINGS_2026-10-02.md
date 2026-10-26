# OPERATOR RULINGS - 2026-10-02

Session: MTS-2026-10-02-1423Z-DSA-COO.
Each ruling carries the operator's own words, verbatim.

## Ruling 1 - net_rr floor and [2.0, 3.5]R window (DIRECTION_REVIEW section 6 item 3)

Operator words, verbatim (2026-10-02, this session):
"Yes reverses both - i never asked for that - i clarified that it can be
anything for test net pruposes and must be as per Tom or Fabio for their
respective setups"

Plain interpretation:
- The DIRECTION_REVIEW framed this as "reverse ruling D1(a)". That framing
  is wrong. The operator never asked for a reversal.
- Testnet collection: the value may be anything. Its purpose is to collect
  data, not to gate a real trade.
- Live setups: the value must be sourced from Tom (for Tom setups) or from
  Fabio (for Fabio setups). No exceptions.

Consequence:
- The live net_rr floor is at 1.25 (d84fb83). That is a testnet collection
  value. No change owed while the path is testnet.
- The 2.0 floor in verdict.py and the [2.0, 3.5]R window in
  SetupCandidatesBuilder.java become a compliance gap to fix before live
  trading: sourced, or removed. Not reversed by this ruling.

Status: DIRECTION_REVIEW section 6 item 3 closed as "no reversal;
reframed by operator".

## Ruling 2 - rip out the 2.0 floor; streamline; apply defaults (2026-10-03)

Operator words, verbatim: "I did noty invent 2.o floor - just rip it out" ... "all blocked stuff must be just
resolved. Do not wait for me - apply deafaults from your judgements and flag/highlight those! We are now in
test-net! Do not be afraid!"

Consequence: [2.0, 3.5]R window and gross 1.5R drop removed; defaults D1-D5 and roadmap in
research/_archive/loose_2026-10/WHY_ENGINE_SILENT_2026-10-03.md, each flagged for override.

## Ruling 3 - MEASURED numbers for CONCEPT-ONLY parameters (accepted 2026-10-04)

Authority: Ruling 2 above, operator words verbatim, 2026-10-03:
  "all blocked stuff must be just resolved. Do not wait for me - apply deafaults from your judgements and flag/highlight those! We are now in test-net! Do not be afraid!"

Ruling:
- A CONCEPT-ONLY parameter (the trader names the idea, the number is ours) may take a value from a pre-registered historical measurement.
- The value carries the label MEASURED wherever it appears: code comment, config key, audit row, condition file.
- Scope is TESTNET ONLY. No MEASURED value may gate a mainnet trade. Promotion to mainnet requires a Tom or Fabio quote, or removal.
- NO-SOURCE parameters are excluded. They have no trader idea behind them; the rule is to remove or shadow them, never measure them.

Applied immediately to the values flagged MEASURE in MyTradingSys/research/EXEC_PROVENANCE_AUDIT.md and referenced by BUILD_PIPELINE row 1.7:
- E1b: Tom limit wait before cancel (tom.max_entry_seconds, AT:57, AT:336)
- E2: Tom time exit (tom.max_hold_minutes, AT:215-219)
- E4/E5: runner share and runner minimum distance (already MEASURED per Ruling 2 and RMD:3, unchanged)

Every existing and future MEASURED value is overridable by the operator at any time. Overrides land in the same file the value lives in, with the label UPDATE.

Status: OPEN until operator marks CLOSED. Effective now.


# END