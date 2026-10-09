# B155 - Section 5d Claude-prompt contract is hand-checked; no executable gate

Status: CLOSED. Severity: MED. Opened 2026-10-09.
Session: MTS-2026-10-09-DSA-COO.

## Defect

DSA_SESSION_PROMPT.md section 5d states six requirements for any Claude Code prompt: at most 30 lines; no restated hard rules or state; no restriction the operator did not state; opening sequence Session ID / Mode / repo root / task; three named blocks; screen only, never saved. None of these is enforced by an executing gate.

## Evidence

- scripts/dev/prompt_check.ps1 checks 12-13 test only the App-vs-CLI surface marker (B133, B134).
- On 2026-10-09 DSA claimed the B154 prompt passed section 5d. The claim was checked by eye against paste text, not by code.
- Revalidation ran as a manual PowerShell block, count by hand (29 lines). A human or a model did the check, not a test.
- LESSONS rule in force: a check that never executes the changed file is not a gate.

## Fix shape

Add one pytest or PowerShell test that reads a prompt string and asserts: total lines <= 30; three named blocks present (DSA-side work already done, Collision check, Registry work DSA will do after); first three non-empty lines match Session ID, Mode, Repo root, then TASK; restriction-word scan over the whole prompt returns zero. Fail on the current hand-written version of the B154 prompt because the three named blocks use different heading text than the test expects, or because the opening sequence is off. Pass on the corrected version printed 2026-10-09.

## Related

- DSA_SESSION_PROMPT.md section 5d
- scripts/dev/prompt_check.ps1 (checks 12-13, the current surface-marker gate)
- MyTradingSys/system/LESSONS_LEARNED.md (a check that never executes the changed file is not a gate)
- B150 (gate is a hand-maintained allow-list; this narrows to the prompt contract specifically)

## Receipt

2026-10-10 close (cc16a73): scripts/dev/prompt_contract.py checks the six section 5d requirements; scripts/dev/test_prompt_contract.py (10 tests, derived from 5d) runs in the quick gate as step 3pc. Run on any composed prompt: python scripts/dev/prompt_contract.py <file>.
