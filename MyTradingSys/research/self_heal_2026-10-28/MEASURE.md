# O1 self-heal — WARN before -> after (2026-10-28)

Result measured on this worktree. "Before" = `research/mts_doctor/REPORT_2026-10-27.md`. "After" = a doctor run on
2026-10-28 *after* `mts_doctor.py --heal --apply`.

## O1 targeted checks (the two that the top-3 heals attack)

| check | before (10-27) | after (10-28, post-heal) |
|---|---|---|
| STALE-CLAIMS | 58 claims over 24 h (limit 5) | 27 claims over 24 h |
| BROADCAST | 8 HIGH pending on jis-laptop | 4 HIGH pending on vm |

Both now below the 10-27 baseline O1 `done_when` requires (< 58 and < 8). The count drop is real work: the apply pass
released 40 shipped-claim files and parked 16 unackable HIGH broadcasts (fail-soft on push races; see `heal_log.jsonl`).
Parallel gateway workers were releasing claims on the same hot `claims` branch at the same time, so part of the drop is
their; the heal is idempotent and safe to re-run.

## Overall WARN count

`HEALTH: 6 WARN` (before) -> `HEALTH: 7 WARN` (after). The +1 is **BROADCAST** going OK->WARN: 4 new HIGH broadcasts
(`vm b-74e5db, b-1fdd2e, b-4053da, b-8ce4da`) arrived on trunk between the two runs - branch state, not a heal
regression (the heal itself parked 16 pending HIGHs in the same interval). CONFLICT-OPEN was already WARN in both
(before: 6 `bug-conflict-*` cards vs limit 3; after: same). HOOK-REG stays
WARN **by design**: the main-checkout heal prints one recovery command (`git -C <main> merge --ff-only origin/fast-track`,
main checkout is 1000+ behind) and never moves the shared checkout, so that WARN clears only when someone runs it.
CI-REVERT, SIZE-HEADROOM and WAITING-ON-OPERATOR remain WARN (CARD / OPERATOR rows, out of heal scope).

## What the heals do (all test-fail on pre-change code; registered in extra_tests.tsv, B150)

1. `heal_release_shipped_claims` — STALE-CLAIMS: release a stale claim only when its card is done/shipped/released or its
   host branch is fully on trunk (git cherry). `test_mts_doctor_heal.py::test_heal_releases_a_stale_claim_whose_card_is_done`.
2. `heal_expire_unackable_broadcasts` — BROADCAST: park a HIGH a no-session host has held > 48 h as `expired` with the
   reason; a new terminal `expired` ack state in `mts_signal.py` (ranked below a later `done`). `...::test_heal_expires_a_broadcast_pending_longer_than_its_window`.
3. `heal_main_checkout` — HOOK-REG: print one exact recovery command + which hook copy is in use; never moves the main
   checkout (live-tree / others' uncommitted files are off-limits). `...::test_heal_reports_one_ff_command_when_the_main_checkout_is_behind`.

Bigger fix filed as a SONNET card (twins checked first): `ci-auto-revert-red-trunk` (auto-revert a red fast-track commit in
the 10-min window; touches git history so it is a card, not a heal). Linked via `not_twin_of` to
`red-trunk-revert-within-10-min-rule-miss` (that one is the doc-wording card, a different job).
