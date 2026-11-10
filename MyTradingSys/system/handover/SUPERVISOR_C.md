# Supervisor C handover | written 2026-11-10T12:35Z by JIS-NB (the desktop), Lead C on Fable | hand-written, not by the tool

## Goal
Login C on the desktop runs PLAN_24H_2026-11-10.md section 8 as rolling Sonnet links L1 to L4. You are the link whose window holds the time now.
Budget read 12:22Z: 5 h 40 % (reset 15:20Z), week 95 % (reset 2026-11-10T20:00Z). Until 20:00Z spend 2 points at most: no workers, no Agents, no page publishes.
After 20:00Z the week is fresh: one worker at a time per set of files, model named on every start (Sonnet; Haiku for mechanical work).

## Truth (read 12:20Z; check each from disk or git before you rely on it)
- Trunk a1ecadd52. CI for 292cd042, 888aa3a7, 9172d00f, a1ecadd5 was not read.
- BTC 74,344 at 12:20Z. Levels: prior day high 75,599; value area high 75,350; POC 74,975; day VWAP 74,858; Asia low 74,379; value area low 74,300; prior day low 73,750. US CPI 13:30Z.
- OI poller ship: tree mts-jis-nb-live-aid-oi-poller-all-venues-1110 had 3 commits not on trunk; a retry was running. `git -C <tree> cherry origin/fast-track` empty = shipped. The earlier failure was step 3sig timing out under load, not the poller.
- Live Aid coach commit 61be0d9cc: not confirmed on trunk.
- Sessions: live-aid-coach (local_8343982a-abc6-461b-b614-8038b2a87891) and arch-optimise-cut (local_68ba50e6-d5bf-4163-b573-f8a452b6e239) may be archived once their work is on trunk. tf-real-frame (local_be19f664-2b58-4849-b28f-4b9246d30a8f) holds unshipped files: do not archive.
- Asks: q-def2f8 to login A (24 h order) unanswered; q-2295a4 to login B (do NUC jobs open console windows) unanswered; q-55e95f (deploy fdbf20a0) is for the operator or the live-tree coordinator, never a Builder; b-ea3809 (dsa_watch.py) told, not done.

## Ruled out
- Flashing windows on the desktop: four watchers found no new window on this desktop (last one 75 s, every window class). A Remote Desktop window to the NUC is open here; the windows may be inside it. Not confirmed; the operator was asked.
- `sync.py tidy --apply --all` removes nothing on this machine (keeps 30 as the gateway session's trees).
- A wide `find` across IdeaProjects times out.

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-C-2026-11-10-L<n>`; `get_usage`; the budget and plan lines of CLAUDE.md step 5b.
2. Run your row of PLAN_24H_2026-11-10.md section 8. Every wake starts with price against the levels above. US prep: `us_prep.py --phase` P2 13:15Z, P3 14:45Z, P4 21:15Z, scenario ledger add, file sent to the operator.
3. At the end of your window: rewrite this file, ship it, start the next link with the one line "Run MyTradingSys/system/handover/SUPERVISOR_C.md", then stop.

## Traps
- A cleanup script must skip the lane trees named in PLAN section 8 L4. Lead C removed three of them on 11-10 and had to restore them.
- `--next` on a ship must be a card id, a stage or `END: reason`; a commit with a bad Next line blocks every later ship until that card exists.
- Republishing a page needs a read of the live page first; sim_desk is 4.3 MB.
- Three ship gates at once time out step 3xm (240 s) and 3sig: one ship at a time on this machine.
- Operator replies: bold result line, table, under 8 lines, only what is new. Record every operator decision in OPERATOR_DECISIONS.md the same turn.

## Open
- Review rows 1 to 5 have no cards yet: file each with `tasks.py new` before its worker starts.
- Tom captions retry after 13:54Z belongs to the Gemini queues (PLAN section 4).
