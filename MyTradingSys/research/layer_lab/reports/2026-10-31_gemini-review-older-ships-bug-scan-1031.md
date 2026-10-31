# Bug Scan Report: Fast-Track Commits 41 to 120 Back

Date: 2026-10-31 (UTC)
Task: gemini-review-older-ships-bug-scan-1031
Command executed: git log --no-merges --format=%h -- MyTradingSys (filtering commits touching .py/.java/.js, skipping top 40, taking next 80)
Output artifact: MyTradingSys/research/gemini_burn_2026-10-31/OLDER_SHIPS_REVIEW.md

## Findings Summary
- Total commits audited: 80 (commits 41 to 120 back) [SOURCED: MyTradingSys/research/gemini_burn_2026-10-31/OLDER_SHIPS_REVIEW.md:9-88]
- Verdict distribution:
  - OK: 75 commits [OURS: 75/80]
  - UNVERIFIED: 5 commits (e68493fd, d133b4493, a2cc61d4, ca25ae86f, 450af836f) [SOURCED: git show <sha> - Git reverts containing no Result: line in commit message]
  - FIX: 0 commits [OURS: 0/80]

Every audited commit diff matches its Result: specification or represents a clean git revert of prior red/reverted changes.

Noticed: Older fast-track commits maintain rigorous alignment with Result: lines and CI test suites; revert commits that omit Result: lines are the only unverified entries.
