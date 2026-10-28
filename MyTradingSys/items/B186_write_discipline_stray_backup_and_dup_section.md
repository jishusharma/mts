# B186 - DSA write discipline: stray .bak and duplicated section went uncaught

Filed: 2026-10-14 by DSA coordinator on JIS-NUC.
Status: OPEN
Priority: HIGH
Fixer: Claude
Logger: Claude

## What happened

On 2026-10-14 about 14:26 local, MyTradingSys/research/apparatus_fixes.md was rewritten.
Two defects went in together:

1. A backup named apparatus_fixes.md.bak was left beside the live file in research/.
2. The JIS-NB build-defect section was appended twice.

The doc suite at 19:57 on JIS-NUC caught only the first: test_5_no_stray_cleanup_candidates
at MyTradingSys/tests/docs/test_integrity.py:116. No test caught the duplicate.

Measured: live 165 lines / 8261 bytes / sha256 F0DDE291; .bak 136 lines / 6891 bytes /
sha256 44D257E6. Two header occurrences; first-to-end 2739 chars, second 1369, prefix-identical.

## Why no rule caught it

1. Three backup locations stated, none enforced: apparatus_fixes.md HOW TO PATCH says
   backup_YYYYMMDD_HHMMSS/; USER.md says backup_session/. The actor used a fourth.
2. Write discipline checks line endings, forbidden phrases, BOM, hash, line count; it
   does not scan for files the writer left behind.
3. The doc gate is batched (DSA_SESSION_PROMPT.md section 6b), so this write ran no gate.
   The stray sat about 5.5 h before the next build saw it.

## Fix requested

(a) One line in apparatus_fixes.md HOW TO PATCH: backup goes to backup_session/ only;
    never beside the live file.
(b) A post-write check (small script under scripts/dev/) that lists new files in the
    working tree after any write and flags any path that is not the intended target.
(c) Keep test_5 as the backstop. Do not weaken the batched gate.

## Acceptance

- One test under MyTradingSys/tests/docs/ that proves the new post-write check fires on a
  synthetic stray file. Fail-before: on the current tree the check does not exist.
- apparatus_fixes.md HOW TO PATCH carries the one-line backup rule.
- test_5 still passes on the clean tree.

## Receipt

(to be added when the fix lands)
