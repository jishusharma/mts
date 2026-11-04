# Layer Lab Report: `gemini-blind-read-of-scripts-dev-gate-se`

- **Card**: `gemini-blind-read-of-scripts-dev-gate-se`
- **Date**: 2026-11-04 UTC
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_GATE_SELECT_DOC_MUST_1104.md`
- **Reviewed Code**: `scripts/dev/gate_select.py:50-80`
- **Test File**: `scripts/dev/test_gate_select.py:36-49`
- **Verdict**: `VERDICT: SOUND`

## Findings and Evidence

1. **DOC_MUST Regex to Step Routing (`scripts/dev/gate_select.py:58-62`)**:
   - `3tl`: `re.compile(r"^MyTradingSys/system/tasks/[^/]+\.json$")` (`CARD_RE` at line 55).
     - Matching sample: `MyTradingSys/system/tasks/task-gemini-blind-read.json` -> routes to `('docs', ['3tl'])`. SOURCED: `test_gate_select.py:37-39`.
     - Non-matching sample: `MyTradingSys/system/tasks/archive/task-old.json` -> routes to `('docs', [])`. OURS.
   - `3af`: `re.compile(r"^MyTradingSys/system/OPERATOR_DECISIONS\.md$")` (`scripts/dev/gate_select.py:60`).
     - Matching sample: `MyTradingSys/system/OPERATOR_DECISIONS.md` -> routes to `('docs', ['3af'])`. SOURCED: `test_gate_select.py:41-44`.
     - Non-matching sample: `MyTradingSys/system/OPERATOR_INBOX.md` -> routes to `('docs', [])`. OURS.
   - `4d`: `re.compile(r"^MyTradingSys/system/handover/[^/]+\.md$")` (`scripts/dev/gate_select.py:61`).
     - Matching sample: `MyTradingSys/system/handover/SUPERVISOR_B.md` -> routes to `('docs', ['4d'])`. SOURCED: `test_gate_select.py:46-48`.
     - Non-matching sample: `MyTradingSys/system/handover/archive/SUPERVISOR_A_202610.md` -> routes to `('docs', [])`. OURS.

2. **Escaping Analysis**:
   - Generic markdown/docs outside the explicit `DOC_MUST` table (such as `MyTradingSys/system/RELAY.md` or `MyTradingSys/system/PLAN_24H_2026-11-04.md`) intentionally route to `('docs', [])` per `DOC_STEPS = ()` (`scripts/dev/gate_select.py:54`). SOURCED: `test_gate_select.py:30-34`.
   - All 3 specific revert classes from `gate_gap_2026-11-03` are accurately matched and routed to their respective required check step.
