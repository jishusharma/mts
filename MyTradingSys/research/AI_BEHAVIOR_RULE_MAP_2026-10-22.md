# 01_AI_BEHAVIOR.md rule map (card ai-behavior-fold-or-archive, 2026-10-22)

DECISION (OURS): the file is a critical file (critical_files.json blob pin, cicd_run.py CRITICAL_PATHS, DSA_SESSION_PROMPT section 6b) and
Section 14 is the live DSA JSON workflow. Cutting it needs the operator's critical-file approval, so it is NOT edited or archived here.
This table is the mapping; a later approved cut removes the OBSOLETE and COVERED rows.

| Part | Canonical home | Status |
|---|---|---|
| S0 NON-NEGOTIABLE (Tom-only rules, 25% haircut, -3%/-10% limits, neutral language) | PROJECT_VISION.md layers rule (2026-10-13), CLAUDE.md Layers/Numbers | PRICE-LEVEL ban already marked SUPERSEDED; rest COVERED |
| S1 file location map, session start check | CLAUDE.md boot, PROJECT_MAP.md | OBSOLETE (upload-only mirror model) |
| S2 research gate | methodology/playbook.md Part I | COVERED (pointer only) |
| S3 extraction rules | methodology/playbook.md Part J, methodology/extraction.md | COVERED (extraction.md cites Rules 31-36: keep those) |
| S4 archive protocol | playbook.md Part K | COVERED |
| S5, S8 session workflow / start order | CLAUDE.md boot + step 4 | COVERED (pointers) |
| S6 output rules | playbook.md Part G, CLAUDE.md commit Result: | COVERED |
| S7 circuit breakers | playbook.md Part G, live-path gates in CLAUDE.md | COVERED |
| S9 protocols I-00..I-06 | CLAUDE.md boot, roles/*.md | OBSOLETE (I-07 kept via S14) |
| S10 rules 1-30 (PowerShell, write_file, CRLF, Unicode) | CLAUDE.md Windows line, role files | OBSOLETE/COVERED (sys_AI chat tooling) |
| S10 rules 31-38 (validate before fix, 3-snapshot proof, lean DSA contract, cross-market, extraction gate, vocab mining, bug-fix vs new-rule, coordinator prompts) | nowhere else | KEEP (referenced by extraction.md) |
| S10 rules 39-41 (string safety, pre-write revalidate, post-write retest) | CLAUDE.md Gates (partly) | KEEP |
| S11 mistake history M-001..M-034 | LESSONS_LEARNED.md / LESSONS_DIGEST.md | OBSOLETE (history; ~3k tokens saving when cut) |
| S14 JSON workflow (I-07) | nowhere else | KEEP (live DSA workflow) |

Saving if approved: S0-S9 + S11 about 3.5k of 8.8k tokens.
