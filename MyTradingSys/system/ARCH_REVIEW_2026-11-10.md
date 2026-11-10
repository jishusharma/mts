# Architecture review of the dev system: ordered cut list (2026-11-10)

Read-only review on the desktop (JIS-NB), login C. Every item is a removal or a simplification, never a new check.
Bounds: operator decision d-simplify-align-s0 (machinery frozen, research never cut) and his order of 2026-11-10:
ship carefully, do not blindly ship. Nothing below is applied; each row is a card for the Lead to file.

## What was measured (source in brackets)
- 7 days: 159 ships, 124 pass, 35 fail; median 11.6 s, p90 176 s, worst 74 min. Today: 19 ships, 11 fail,
  median 166 s (runtime_data gate_timing.jsonl, 15 worktrees).
- The usual ship is fast. The cost is the tail: 9 ships of 10 min or more, and a red trunk that blocks every code ship.
- Today's 3 red CI runs: doc-wording tests twice, one exact-count research test once (health_audit.py, 72 h).
- Today 6 of 11 failures were step 3xm; at least 3 stopped at the 240 s limit. Alone that step takes 6.6 s, so the
  cause is load: 3 pools x 2 slots let 4 to 6 suites run at once on 8 CPUs. Slot wait is logged as 0, never measured.
- The same suite runs up to 3 times: local ship, CI (15 legs), deploy.
- Size: 814 test files (179 test the dev tools, 248 sit in research); 393 files in the extra-tests step, median 24 min
  in full mode; 37 worktrees (19 already on trunk); 639 task cards (434 closed, still in the live folder);
  139 rule docs, 1.66 MB; 17 hook entries over 9 scripts, no total size cap per turn.
- 21 days of trunk history: 74 revert incidents; 0 were a trading or live-path defect, 6 a dev-tool defect, 59 (80 %)
  noise: 40 doc, cap or registry tests, 10 count tests, 9 timing or OS. Trunk was red 94.6 h in 202 episodes.
- 7 days: 73 % of 2,004 commits are not research; 352 are route-tag commits, 335 of them touch no file.
- Not measured: slot wait, per-test durations, hook tokens per turn, the other two machines.

## Ordered cuts (do in this order)
| # | Cut | Why | Risk | Size |
|---|---|---|---|---|
| 1 | Delete tests that assert doc wording or format; keep path-exists and live-path rule checks | 2 of today's 3 reds; about 2 h of blocked ships | low: these never caught a code defect | S |
| 2 | Research count tests ("rows == 337") become set-based or use a frozen fixture; keep the trial ledger | 1 of today's 3 reds; breaks whenever a new result lands | low | S |
| 3 | One gate queue per machine (1 pool instead of 3) and log the real slot wait | removes the 240 s timeouts under load | low: a queue is slower only when idle CPUs exist | S |
| 4 | Hooks: drop the PAGES STALE line (or fix the 3 pages once); an ask goes to one owner, not every session | repeats every prompt in every session; an ask shown to all is owned by none | low: keep STOP, HOLD, HALT and red-CI lines | S |
| 5 | The stop guard blocks only on files this session changed | today it blocks a session over another session's file | low | S |
| 6 | Dev-tool tests run only when their script changes; always-on stay: tests of sync, preship, run_all_tests, gate_impact, deploy scripts | signals tests median 494 s, card tests 269 s, soak test 806 s in every full gate | medium: a tool can break through a dependency | M |
| 7 | Remove worktrees that are clean, on trunk and unclaimed (19 candidates of 37; S0 target 8) | disk, slot and reading noise | low; deleting needs one operator yes | S |
| 8 | Move the 434 closed cards out of the live task folder (existing sweep command) | every card read and lint walks them | low: a move, not a delete | S |
| 9 | STATUS.md: regenerate at ship or drop it from boot (6 days stale); stop the LAYERS.md regenerate-and-amend per ship; the route tag rides in the ship commit, no empty commit | a stale boot read misleads every session; LAYERS.md had 338 commits in 14 days; 50 empty route-tag commits a day | low | M |
| 10 | Docs: move dated one-off docs and append-only logs out of the rules folder; archive the retired relay scripts under scripts/sched | 36 dated docs, 46 untouched for 2 weeks, 2 index files nobody maintains | low: move only, update path tests | M |
| 11 | Extra-tests list becomes auto-discovery (262 hand-kept lines go) | "register test" commits; hand list drifts | low | S |
| 12 | TRIAL, one change only: ship through a pull request that merges itself when CI is green | would remove the local full gate (median 24 min) and red trunk | high until proven, see below | L |

## Row 12 is a trial, not a cut
Three facts found by the critics: a merge made by the CI token does not start the push run, so the green marker
would not move; 15 legs per run can hit the free-plan job limit; two changes green alone can be red together.
Prove each on one harmless change before any switch. Until then the local gate and the red-CI check stay.

## Rejected after critique
- Skipping full mode for live-path files by changed-path selection: full mode stays for those paths.
- Linux-only CI before merge: the live host is Windows.
- Dropping the must-pass rule for steps 3xm and 3la: it came from 19 of 26 red runs and 5 reverts
  (CI_RED_ROOT_CAUSES); do row 3 first, then re-measure.
- Look-ahead lint off for research: it stays blocking; only the allowlist upkeep gets cheaper.

## Must not be cut
1. The 61 execution tests: kill switch, daily loss guard, fail-closed auto trader, mainnet flag, orphan watchdog.
2. Full gate mode for live-path and live-import files.
3. All 15 CI legs required before the green marker moves.
4. Deploy by hand, from the green marker only.
5. Testnet-only and secrets rules; must-pass steps 3xm and 3la.

## Two-week order
Week 1: rows 1, 2, 3, 4, 5 (all S; they stop today's reds and timeouts). Then re-measure the gate tail.
Week 2: rows 6, 7, 8, 9, 10, 11; row 12 only as the one-change trial, and only if week 1 numbers hold.
Working notes with sources: the session notes folder, files arch_review_facts, outside_views, critiques.
