# B083 - prompt_check.ps1 gate

Status: CLOSED 2026-10-03. Severity: HIGH.

## Defect

DSA composes CL / CC / Opus prompts with claims that are not verified
against disk. Six of eight defects in session MTS-2026-10-03-0430Z-DSA-COO
repeat entries already logged 2026-10-02. No automated gate exists to
refuse a prompt whose cited paths, tokens, or clauses fail a disk check.

## Evidence

MyTradingSys/research/PROMPT_FAILURE_ANALYSIS_2026-10-03.md
MyTradingSys/system/LESSONS_LEARNED.md, 2026-10-02 entries

## Fix

Build scripts/dev/prompt_check.ps1. Input: a composed prompt as text.
Checks, each writing a PASS/FAIL row:

  1. Every path string in the prompt resolves on disk (Test-Path).
  2. Every file:line citation names a real line in that file.
  3. Every uppercase parameter token cited as being in a file is
     present in that file (Select-String).
  4. Every clause containing 'do not', 'never', 'must not', 'cannot',
     or a numeric cap is tagged as OPERATOR-SET or absent.
  5. No capability limit on another surface unless the operator's
     own words in this session carry it.

Output: a PASS/FAIL table and a final STATUS. FAIL is advisory. The prompt still ships and the operator decides. Warn and log; no stop.

## Receipt
2026-10-03: scripts/dev/prompt_check.ps1 and test_prompt_check.ps1 on disk.
test_prompt_check.ps1 reports TEST STATUS: PASS (4 of 4 fixtures).
Fixtures cover: fake path, valid paths, untagged clause, absent token.
# END
