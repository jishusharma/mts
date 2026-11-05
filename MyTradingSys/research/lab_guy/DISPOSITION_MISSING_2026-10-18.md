# Disposition: MISSING_2026-10-18 (reviewed 2026-11-05, trunk 6a41d1416)

Repro `missing_2026-10-18_repro.py.txt` re-run on trunk: BOTH synthetic defects still reproduce
(`renamed.csv` accepted by `lab_flow.safe_file`; CRITICAL base -> B-SHARED via `tasks.promote_shared`, tasks.py:95-114).
All cited cards are archived (done); none of their results touch these two paths.

| Finding | Status on trunk | Owner / evidence |
|---|---|---|
| P1 trust tag / invalidation | FIXED (partial by design) | lab-trust-tag, 334c6e860: 181 tests; 24 bases stay UNCHECKED, 8 C2 re-check cards |
| P1 sharing downgrades weight | CONFIRMED, UNFIXED | NEW card lab-shared-keeps-weight (fail-first CRITICAL/CRUCIAL fixtures) |
| P1 data check location-bound | CONFIRMED, UNFIXED | NEW card lab-safe-file-repo-data-gate (lab-holdout-access-control covers DATA_ROOT only) |
| P1 formula pack | FIXED | lab-formula-spec-text (F01/F11.4-6 corrected, 2 tests), lab-formula-spec-recount c48b25859 |
| P2 review receipts vs v3.1 stack | PARTIAL | lab-review-gate-harden2 585144a43 (R2-R6 fixed, R1 authority open), lab-vendor-gate-harden2 (V1-V7 closed); R1 stays on harden2 note, no new card |
| P2 error-detection rate | PARTIAL | lab-planted-error-trial 23426b191: machine layer 1/8 caught; reviewer legs are coordinator follow-ups |
| P2 queue recovery | STALE | 2026-10-18 snapshot; coordinator duty, no card |
| P3 docs contract | NOT CHECKED here | out of scope; LAYER_LAB.md/LAB_RECIPES.md wording is a docs-only follow-up, no card filed |

DECISION (OURS): labguy-pass-a found no card file; its commits (0107ac34b, 4403f023c) are claim bookkeeping only, so no overlap blocks the new cards.