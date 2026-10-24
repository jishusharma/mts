# Lead handover | written 2026-10-25T22:40Z by MTS_Doctor (mts-doctor-role-7762ef, retiring) | discussions since last rotation: 4 | verify: by hand until C6 ships
First real use of the form in research/mts_doctor/CONTEXT_FILES_DESIGN.md s10a. Re-check every Truth line on trunk before acting on it.

## Vision
MTS trades crypto on Deribit testnet only; fee-net out-of-sample results decide what trades, never doctrine (PROJECT_VISION.md).
Banned: mainnet, schedulers/routines, deploys or restarts by builders, runtime/account data in the public repo.
Every parameter is SOURCED (quote + file:line) or OURS.

## Priorities now
1. Operator yes on CONTEXT_FILES_DESIGN cards C1-C7 (plus s10g: the Lead loads modes one at a time as skills) -> then refine, C1+C3 first. Number: calls to first edit 12 -> 8, stale dispatched 10/28 -> 0.
2. Live parity: T09-F1 (live volume_fvg trades the opposite side, 0/24 agree), F2 (one bracket for all layers), F3 (untested RSI events): cards t09-f1/f2/f3, lane JIS-NB, live_path true; F3 waits for F2 (same file). Operator decision pending: switch volume_fvg off on testnet at the next deploy.
3. Gate speed: card registering-a-test-in-scripts-dev-run-ex (p1), test registration forces the 20-50 min full gate. Pilot 3 waits for it.
4. Confluence: S2 shipped 80413ab75 (FABLE_DESIGN.md, PRE_REG_CONFLUENCE.md); S3 blocked on card confluence-s1-f6-direction (raw, needs a Lab_Guy stamp).
5. Overnight NUC harvest (below, Next 3 steps).

## Decisions
- d-lead-one-session | 10-25 | one session to talk to = Lead (coordinator + Thinker); a Supervisor worker runs the wave; Lead never wakes on worker events
- d-lead-modes-sequential | 10-25 | the Lead loads Thinker/Admin/Pipeliner/Doctor jobs one at a time, not all at once (s10g)
- d-handover-fable | 10-25 | the context-files design ran on Fable (operator: "for this particular task I wanted a fable run")
- d-weekly-cap-45 | 10-25 | login C weekly cap 45%; overnight sessions no longer than 5-6 h
- d-terms | 10-25 | operator shorthand: "NT <term>" = new term; "RC" = Reloading Chat (I was compacted, the paste is the latest chat)
- d-youtube-on-gemini | 10-25 | all YouTube work to Gemini on the NUC
- d-one-ship-at-a-time | 10-24 | gates 50+ min -> ~2.5 min median

## Open questions
- Build C1-C7? default: wait for the operator (design approval rule) - operator
- volume_fvg off on testnet at next deploy? default: no change until he says - operator
- Lead model? default Sonnet; Opus only when named - operator

## Board
cards: ready 46 | refined 29 | raw 108 | blocked 8 | done 369 (`tasks.py list`, 22:35Z)
waves running: 0 | Claude child sessions: 0 (all archived) | last ship 5804138c1 | CI green 11b8f95c4, docs-only since
budget login C: week 40% (cap 45%), 5 h ~18%, reset 2026-10-27T20:00Z

## Ruled out
- A long-lived coordinator: this Doctor session took 12,768 steps in 24 h = 78% of all context read (corrected from 84%: health24.py counted pre-window turns). Cost = number of steps, not size per step.
- clear_session while a ship/worker is live in the same session (3 refusals); /compact by message does not run.
- Claude workers for YouTube (429); Haiku on raw cards; Opus "for quality".
- Hand-written NEXT_SESSION.md as handover (sent workers to shipped work).
- Dodging a safety gate (refine-run set live_path false; reverted to true).

## Discussions
- self-healing context files -> 6868a4650 + 2cd315dc1 + 5804138c1 (+ s10g) -> cards C1-C7 proposed, not filed, await yes
- Lead role -> s10, s10f, s10g -> C6, C7
- confluence S2 on Fable -> 80413ab75 -> confluence-s1-f6-direction (raw)
- refine run 28 p1 cards -> REFINE_2026-10-25.md -> 18 READY, 10 STALE (9 still show raw: sweep them)

## Next 3 steps
1. NUC harvest (jobs started ~20:50Z, GPT cburn + Gemini gburn): write a .ps1 and pipe it: `ssh -i ~/.ssh/nuc_gate -o BatchMode=yes e-ngineers@192.168.29.110 ps < script.ps1` (an inline command is refused). Read `F:\MTS\gq\night_gburn.out/err`, `night_cburn.out/err`, `F:\MTS\gq\<name>.log`. Jobs: GPT gx4-t09-f1-fvg-side, gx4-t09-f2-exits, gx4-t09-f3-rsi-events, gx4-statecode-races, gx4-t05-recheck (outputs on NUC branches gpt-q/<name>, dir research/gpt_burn_2026-10-24/<name>/); Gemini gb2-slippage-sources, gb2-deflated-sharpe, gb2-monte-carlo-presentation (research/gemini_burn_2026-10-25/), card yt-fabio-fetch-retry (gemini-q/<name>). GPT patches are proposals: review before any live-path use; Fabio extract must pass `verify_extract_quotes.py`.
2. Ask the operator for the C1-C7 yes; on yes, Session_Planner Agent refines C1+C3, then a Supervisor worker runs them.
3. Lab_Guy pass on confluence-s1-f6-direction; sweep the 9 STALE raw cards (`tasks.py done` refuses raw).

## Traps
- NUC `gemini_queue.py` claim hangs on a git credential push: use gburn.py/cburn.py (no claim).
- tasks.py dirties LAYERS.md: commit it with the change; a second ship within 10 min needs `--again`.
- Main checkout is 259 behind with others' edits: leave it; always `sync.py start <slug>` first.
- 3 published pages stale (mts_control_room, mts_layer_map, mts_home): republish, then `artifacts.py publish-record`.
- Main settings.json stale hooks: worktree sessions may miss role_loader (card main-checkout-stale-hooks, operator present).

## Missed last time
(fold not built yet: C2)
