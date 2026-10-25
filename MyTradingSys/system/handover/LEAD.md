# Lead handover | written 2026-10-25 (evening IST) by MTS_Doctor (thinker-loader-c62751, retiring: Doctor is now Lead mode `doctor`, 2c9bbaf9c) | verify: by hand until C6 ships
Re-check every line on trunk before acting on it. Builders listed under "In flight" report to the old Doctor session, not to you: check trunk for their ships.

## Vision
MTS trades crypto on Deribit testnet only; fee-net out-of-sample results decide what trades, never doctrine (PROJECT_VISION.md).
Banned: mainnet, schedulers/routines, deploys or restarts by builders, runtime/account data in the public repo.
Every parameter is SOURCED (quote + file:line) or OURS.

## Operator asks of 2026-10-25 (his words, standing)
- "shipping time must be under 2 minutes": the gate-file ship is a smoke gate plus targeted tests with a 90 s cap, and the rest goes to CI (092925c0c). Measured 111 s logged, 141 s wall. The guard is in flight.
- Principles over word lists: voice dictation ("MPS" = MTS, "cloud" = Claude); never wait on a question (ask the one who started you, take the safe default); fleet-wide by default (a fix one machine needs goes to the repo plus `mts_signal.py broadcast --cmd`). All three go to CLAUDE.md through the lead-resume-1025 session (cards 3+5).
- Behavior is tested, not assumed: `scripts/dev/behavior_eval.py run|conflicts` (0439ff2c5). Sonnet passed 4 of 8 scenarios. The f-ship-again scenario is outdated (a second ship is now a note); fix it.
- No contradictory rules: run `behavior_eval.py conflicts` before adding a rule. Two weak memory pairs are still open.
- Cleanup decisions are the AI's, never his: keep the system lean, archive, then delete with time; C: must not fill. It is fleet-wide and runs while a login is active (no scheduler).
- Eagle_Eyes stays a separate session role with a Think mode (eagle_eyes.md:42-52).

## In flight (background Sonnet Builders started by the old Doctor; verify each: `git cherry` empty + CI green on its sha)
- Lead K2+K3: lead.md core gets the daily doctor HEALTH line (shipped in 2c9bbaf9c?), START_HERE gets `You are Lead.`, close card role-loader-mode-command.
- eagle-eyes-follows-live-owner: the live mirror follows the live owner (the loop runs on Lenovo DESKTOP-F7IU69N since 11:28Z; the mirror was last published 10-19 by JIS-NB).
- C2 fold-on-ship; C4 supervisor-handover-fixed-form (`--role lead`).
- ship-time guard: ship_wall row, SLOW line, doctor SHIP-TIME check at 120 s, cap regression test.
- c-drive-cleanup-holds: tidy removes shipped clean trees after 1 h, start reuses trees, tests delete basetemps, and the guard runs once a day per host from the SessionStart hook (under 15 GB free).
- Session lead-resume-1025 (local_d1399a2b): card 2 retry, then cards 3+5 in one ship (the 3 principles, eval scenario, HOW_MTS_RUNS.md:21 live-owner row).

## Open questions
- volume_fvg off on testnet at next deploy? default: no change until he says - operator
- Cowork workspace ~12.7 GB (Settings > Storage > Runtime): remove if unused - operator's own click

## Next 3 steps
1. Check trunk for each "In flight" ship; whatever has no ship and no running session: re-brief a Builder from its card.
2. Run `python scripts/dev/mts_doctor.py`, show HEALTH; fix the f-ship-again eval scenario and the 2 weak memory conflicts.
3. Broadcasts still open: b-10b3d8 (`c_drive_guard.py install`) on desktop-f7iu69n and vm; b-be9727, b-79ee5e on desktop-f7iu69n and vm.

## Traps
- The live loop is on the Lenovo: `live_owner.py check` on JIS-NB refuses. HOW_MTS_RUNS.md:21 is stale until cards 3+5 ship.
- Builders filed cards in the coordinator's tree: tell them to file in their own tree.
- Main checkout is 400+ behind with local edits: leave it; always `sync.py start <slug>` first.
- NUC `gemini_queue.py` claim hangs on a git credential push: use gburn.py/cburn.py.

## Missed last time
(fold not built yet: C2)
