# T052 - DEFINE A TOM-CITED TRIGGER FOR SETUP_CONFIRMED

Opened: 2026-09-27 by session Claude Sonnet 5, per operator ruling on D6b
(research/core_readiness_2026-09-27/D1_D7_DECISION_BRIEF.md).
Severity: MED (alert-gating logic references a verdict that can never
fire; not a defect but a real gap).
Status: OPEN.

## BACKGROUND

B076 (filed 2026-09-27) found that Compute-Verdict never emits
SETUP_CONFIRMED - compiled_engine.md sec 8 defines it and alert gating
lists it, but no code path produces it. The proof thresholds 3 and 5
that Compute-Verdict actually uses have no Tom citation either (see D6a,
being documented as [SYSTEM] separately).

The plan's own recommendation was to simply remove SETUP_CONFIRMED from
alert-gating logic and compiled_engine sec 8, since it's dead weight.
Operator ruled instead (D6b) to find or confirm a real Tom-cited trigger
for it, rather than removing it.

## SCOPE

Research task, not a code task: search Tom's transcripts / TOM_VERBATIM_INDEX.md
for language describing a "confirmed" setup state distinct from
SETUP_FORMING - something with a specific, citable trigger condition
(e.g. a further proof threshold, a specific price action confirmation,
a specific timeframe requirement). If found: propose the trigger
condition, a TOM-NNN citation, and the compiled_engine.md sec 8 change
(critical file, four-step proof, operator approval) plus the
Compute-Verdict code change to actually emit it.

If NO such citable trigger exists after a genuine search: report that
back explicitly rather than inventing one - per the project's
no-fabrication rule, a threshold without a citation or documented
[SYSTEM] exception does not enter the engine. In that case the operator
will need to choose between the plan's original recommendation (remove
it) or documenting it as a [SYSTEM] (non-Tom) exception.

## BLOCKS

- D6b resolution (compiled_engine.md sec 8 text, part of C5).
- Any executor treating SETUP_CONFIRMED as real (already guarded against
  in T050's executor.py, which doesn't reference verdict states directly
  yet).

## UPDATES

2026-09-27: Filed per operator's D6b ruling (define a trigger, don't
remove). Not yet started.
