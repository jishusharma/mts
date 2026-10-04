# T046 - STAGE 3 PENDING DECISIONS

Register row: MyTradingSys/research/BUGS.md T046.
Convention: one item, one doc. Verbatim ask at top. Updates appended chronologically, newest last.

## VERBATIM ASK (what_is_next.md Stage 3, anchor L32)

## Stage 3 - Pending your decision

Nothing moves on these until you decide.

| item | decision needed |
|---|---|
| Rename or keep the seven live shortcuts | Current recommendation: keep them, they are already documented and used in commands file. |
| Rename or keep open-loop numbers | Current recommendation: keep the number, add a plain title next to it. |
| Folder renames | Current recommendation: plan this session, do next session in a quiet window. |
| Pull duplicate function into shared file | Two copies exist. Extract or leave? |
| Confirm the A, B, E mapping | The letters were shorthand in the task package. Mapping proposed in the name audit. Confirm or correct. |

Verbatim lead-in (L34):
> Nothing moves on these until you decide.

## STATE

2026-09-23 OPEN. Five pending decisions. Downstream stages (Stage 4 deferred items and open-loops full sweep) are gated on Stage 3 per what_is_next.md. This item is a decision bundle; each row is an independent coordinator decision.

## UPDATES (chronological, newest last)

### 2026-09-23T15:30Z - coordinator, session MTS-2026-09-23-1445Z

Item doc created from what_is_next.md Stage 3. Verbatim ask captured. Source-folded as part of T039 sweep. Register row added this session.
### 2026-09-24T10:05Z - coordinator, session MTS-2026-09-24-0639Z

d4 result: Pull duplicate function into shared file.

Search run across scripts/*.ps1 and MyTradingSys/**/*.py.

PowerShell duplicates:
  Fmt (context.ps1, live.ps1) - identical after whitespace normalization.
    Fails Claude rule 4 (no tests). Leave separate.
  Write-TextNoBom (Build-Check.ps1, start-session.ps1) - not identical:
    Build-Check takes a lines array, start-session takes a text string.
    Both duplicate existing shared-functions.ps1 entries:
      Write-TextNoBom (lines)  ==  Write-NoBomLines
      Write-TextNoBom (text)   ==  Write-NoBom
    Local copies lack the rooted-path check present in shared.
    Fails rule 4 (no tests). Leave separate; note for future cleanup.

Python collisions (main x7, classify x3, load x2, parse_ts x2, load_snapshot x2,
write_state x2, load_labels x2): different implementations under common names.
Rule 1 fails. Not duplicates.

Decision: no extraction this session. Per Claude 4-rule test rule 4 (coverage)
fails on both PS candidates. Two-item cross-reference cleanup can be filed
as a low-severity task if drift is ever observed.

Status: d4 DONE (no extraction, finding recorded).

### 2026-10-04T10:15Z - builder, session MTS-2026-10-04-1009Z-APP-BLD-t052-b063-t046

One line per item (what_is_next.md Stage 3, L32-L41). Note: D1_D7_DECISION_BRIEF.md covers D1-D7 and does not mention these
five items; decisions below rest on name_audit_20260915.md, COMMANDS.md and the disk state.
1. Rename or keep the seven live shortcuts: ACCEPT keep. name_audit v1.0.1 verdict is "document, do not rename"; lx..la no longer
   exist on disk (scripts/live holds alerts, context, deltas, health, live, quick, ...), so there is nothing to rename.
2. Rename or keep open-loop numbers: ACCEPT keep the number, add a plain title. L_ITEMS_MASTER.md is frozen (live list is BUGS.md);
   open_loops_status.md already uses plain titles.
3. Folder renames: NEEDS OPERATOR. The plan calls for a quiet window, and the working tree runs the live testnet system whose
   processes import from these paths; only the operator can name a window.
4. Pull duplicate function into shared file: REJECT. Get-Descendants (the audit's duplicate) is already in
   scripts/core/shared-functions.ps1:4 and mode.ps1 uses it; stop-day.ps1 no longer defines it. The remaining PS duplicates
   were declined by the 2026-09-24 d4 result (rule 4, no tests).
5. Confirm the A, B, E mapping: ACCEPT. A = compiled_engine.md, B = conditions/*.md, E = CONSOLIDATED_RULES.md (all exist on disk;
   extracts/processed/tom/CONSOLIDATED_RULES.md). The task package is no longer used (name_audit sec 6).
Stage 3 status: 3 accept, 1 reject, 1 needs operator. Stage 4 "Folder renames" stays gated on item 3.
