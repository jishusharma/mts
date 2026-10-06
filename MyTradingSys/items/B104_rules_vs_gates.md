# B104 - Rules exist; check is advisory; rules broken in-session

Status: OPEN. Severity: HIGH. Opened 2026-10-04.

## Defect

Nine rule-breaks in session MTS-2026-10-03-2037Z-DSA-COO, every one already covered by a rule on disk:

1. Claimed two files existed (tests/conftest.py, tests/test_build_check_switches.py) that were never written. USER.md DISLIKES: claiming a read or run not seen pasted.
2. Asked for CLAUDE.md and the mts go launch block before printing a CL prompt. Both one-liners. Filed as B101.
3. Session-ID timestamps from memory twice; wrong both times. live_session_protocol rule 10.
4. Claimed BUILD_PIPELINE.md missing; exists at MyTradingSys/runtime/BUILD_PIPELINE.md.
5. Placeholder <HHMM> in a pasted prompt. operator_reminders B5.
6. Wrote the App Code mode prompt with the mts go launch block after operator said App, not CLI. SURFACE_POLICY 1b.
7. Inserted "do not", "must not", "keep separate" restrictions the operator did not say. USER.md LIKES.
8. Broke MyTradingSys/items/INDEX.md line endings to CRLF; five attempts to land a one-line fix. DSA section 6.
9. Asked for disk read before composing a CL prompt (B101 shape, second occurrence in same session).

## Root cause

Structural, not moral. Reading a rule is not the same as executing it. The B083 check (scripts/dev/prompt_check.ps1) is advisory: it logs FAIL and the prompt still ships. Nothing blocks a non-compliant prompt or a line-ending-breaking write. A rule that depends on the agent remembering to apply it breaks under generate mode.

## Fix shape

(A) Make scripts/dev/prompt_check.ps1 blocking: non-zero exit on FAIL; the composer refuses to print a failing prompt.
(B) Extend prompt_check.ps1 with the checks that would have caught this session: session ID from [DateTime]::UtcNow not memory; mode line present (surface / model / Ultracode / cap / batch); no placeholder in the block; no restriction words the operator did not say; signature P.S : All Access present.
(C) Write-time gate: refuse to write CRLF to an LF-detected target and vice versa.
(D) Test must fail on pre-change prompt_check.ps1 at least once.

## Related

- B083 (CLOSED): built prompt_check.ps1 advisory.
- B101 (OPEN): the context-ask shape; step 2 and step 9 above are instances.
- LESSONS_LEARNED.md 2026-10-03 entries on prompt cap and directory-scoped stage.

## Receipt

- 2026-10-04 MTS-2026-10-04-1120Z-APP-BLD-b104-prompt-gate: fix (A)+(B) done: prompt_check.ps1 blocking (exit 1 on FAIL, names failing check) with checks 6-10 (session ID vs disk clock, mode line, placeholder, unstated restriction, signature); test_prompt_check.ps1 10/10 PASS, 8 of 10 fail on the pre-change script. (C) write-time line-ending gate still OPEN.
- 2026-10-04 MTS-2026-10-04-1300Z-APP-BLD-b104-eol-gate: fix (C) done: prompt_check.ps1 check 11 (-Target; CRLF/LF write vs on-disk target, both directions, exit 1 on mismatch); test_prompt_check.ps1 12/12 PASS, fixtures 1, 2, 11, 12 fail on the pre-change script.
# END
