# B076 - SETUP_CONFIRMED UNREACHABLE; COMPUTE-VERDICT NEVER EMITS IT

Opened: 2026-09-27 by session Claude Sonnet 5 (via NUC worker task 010, reviewed by coordinator).
Severity: MED (gating logic inconsistency).
Status: CLOSED 2026-10-04.

## DESCRIPTION

"SETUP_CONFIRMED is unreachable: Compute-Verdict never emits it;
compiled_engine.md sec 8 defines it; alert gating lists it. Proof
thresholds 3 and 5 in Compute-Verdict appear nowhere in compiled_engine.md."

Per-item doc: research/core_readiness_2026-09-27/CORE_READINESS_PLAN.md
section 2, finding F9.

## BLOCKS

- Decision D6 (proof thresholds / SETUP_CONFIRMED, per CORE_READINESS_PLAN.md).

## UPDATES

2026-09-27: Filed per CORE_READINESS_PLAN.md F9.

2026-10-04: CLOSED. Traced: Compute-Verdict (start-trading-day.ps1 L225-231) and verdict.py (L121-126) end at SETUP_FORMING; compiled_engine.md sec 8 already documents proof thresholds 3/5 and the unreachable status (C5). Unreachable by design until T052 supplies a Tom-cited trigger; Tom corpus index (TOM_VERBATIM_INDEX.md L24,L39) has only retest narration, no rule. Pinned by tests/test_b076_setup_confirmed_unreachable.py.
