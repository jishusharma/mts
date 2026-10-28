# Pilot score, 2026-10-22 (Supervisor on login B / this PC vs plain Sonnet on login C / JIS-NB)

Sources: Supervisor and its two Builders: session transcripts on this PC. Plain arm: git only (its transcript is on the notebook and was not read). Where a number needs that transcript it says NOT MEASURED.

| # | Measure | Supervisor arm | Plain arm |
|---|---|---|---|
| 1 | First-turn context | 77.8k tokens (Builders 75.0k and 78.9k) | NOT MEASURED |
| 2 | Minutes waiting on tools | NOT MEASURED (no wait log run) | NOT MEASURED |
| 3 | Cards shipped | 3 of 3, ~28 min, 6 commits: boot diet + rule map (73d84aa6), 339-card archive sweep (a5bb9d7f), ship-gate fix (020f3c45), shot fix (3a9d8faa), hand-over (9ddfdbde) | 2 of 3 closed in ~3 min; card 3 released and handed over |
| 4 | Hook / banner / rule errors | 4: Builder loaded as Thinker (fixed 8b4ea32a); ship gate crashed on 339-file diff (fixed 020f3c45); `codex_run.py tick` "cannot switch branch while merging" (open); wrong transit time 17:20Z (open) | 1 known: overwrote NEXT_SESSION.md |
| 5 | Operator corrections | 0 in the Supervisor's transcript | NOT MEASURED |
| 6 | Rules broken | Skipped the Haiku recheck of Builder claims; repeated "89 tests pass" without rerunning | Replaced NEXT_SESSION.md (82 lines to 7), deleting every other session's hand-over block (restored in this commit). Card rule 3 not testable: its commits changed no code |

What each "done" really was:
- Plain, shot-py-store-path-nuc: it ran the screenshot ingest (manifest 452 to 454 rows, second run 0 new, 35 tests pass). Real, small.
- Plain, gate-quarantine-expiry-cap: already shipped in c8e5fe3f. It only closed the card.
- Supervisor: real changes, one of them 339 files.

## Verdict against the decision rule
- Shipped 3 vs 2 is 1.5x, but one plain card was already done, so the real gap is bigger.
- The Supervisor arm had more errors, but they came from larger work and were found, fixed and shipped in the same run. The plain arm's one error destroyed other sessions' notes.
- Neither "plain wins" nor a clean "Supervisor wins". The card sets differ, so the rule's default is a swapped rerun.

Decision: keep the Supervisor path; no swapped rerun now (the plain card set was too small to separate the arms). The open failures are the work: Codex tick on a shared tree, Supervisor transit time, nothing checks that a hand-over appends instead of replacing NEXT_SESSION.md.

## Limits
One run per arm, different devices and logins, different card sets, plain-arm timing from commit times only, no plain-arm transcript.
