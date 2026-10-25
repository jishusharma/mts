# LENOVO NEXT SESSION (DESKTOP-F7IU69N, login A), written 2026-10-25 by the Doctor on JIS-NB

Goal: use the rest of this login's 5-hour window on the Lenovo (about 32% left, ending within 5 h) on real queue work, without touching the live loop this laptop runs.

## Hard limits (this laptop runs the testnet live loop)
- Never stop, start or restart any process. Never touch `.mts_live`, HALT files, the live loop window or `mts_run.py loop`. Never deploy.
- Work only in a worktree printed by `sync.py start`. Testnet only. Never read `.secrets/`, `.env` or keys. No scheduled tasks.
- Never rebase, reset, force-push or stash. Use `git -C <dir>`, never chained `cd x && git`.
- Something looks wrong with the live loop: report it in one line and do nothing else.

## Steps
0. `$env:COMPUTERNAME` must print `DESKTOP-F7IU69N`; anything else, stop.
1. `cd C:\MTS\mts-lenovo; git pull; python scripts/dev/sync.py start lenovo-1025`. Work in the printed WORKTREE.
2. Broadcasts for this host, in order:
   - b-d0ee55, Defender exclusions: `cd C:\MTS\mts-lenovo; .\scripts\operator\defender_exclusions.ps1`. The operator clicks Yes on the admin prompt. Then run it again with `-Check`; nothing missing gives `python scripts/dev/mts_signal.py ack b-d0ee55 done`.
   - b-be9727, b-79ee5e, b-10b3d8: `python scripts/dev/mts_signal.py acks <id>` shows each one's command. Run it if it is safe under the limits above, then ack `done`. If it is not safe here, ack `told --note "<why>"`.
3. Budget: run `get_usage`, then `python scripts/dev/mts_signal.py budget ...` and `python scripts/dev/exhaust.py plan ...` (EXHAUST_PHASE.md). Take `python scripts/dev/sync.py claim "exhaust-A"`; if another session holds it, carry on without it.
4. Cards, one at a time, each shipped before the next: **B195** (task-mode gate block never ran; no receipt, no refusal), then **B196** (AIBridge auto-OFF on operator draft).
   For each card:
   - `tasks.py brief <card>` and `sync.py claim "<card>"`.
   - New tests must fail on the old code.
   - Before shipping, run every test that reads a file you changed (`git grep -l <filename> -- '*test*'`).
   - `sync.py ship --release <slug>`. Then `git cherry origin/fast-track HEAD` must print nothing, and CI must be green on your sha. If CI is red, `git revert` your commit and ship within 10 minutes.
5. Quota left and no card fits: do read-only second checks of today's shipped commits `f581b9d20`, `8971d69e6` and `c540fc3d8`. Does each one do what its `Result:` line says? Write findings to `MyTradingSys/research/mts_doctor/LENOVO_AUDIT_2026-10-25.md` and ship it.
6. Antigravity (Gemini) on this laptop: do not start Gemini or YouTube work here. That lane runs on the NUC (gemini_queue).
7. Keep working for the whole 5-hour window (operator 2026-10-25: "make it work for 5 hours, without sleeping"). Do not stop after step 5:
   - Never sleep, wait or poll. A card that is blocked gets one line in its claim note; then take the next card.
   - Next card: `python scripts/dev/tasks.py next`. Skip anything on the "Not on this list" below, anything live-path that needs a deploy, and any card another session has claimed (`sync.py claim` refuses it).
   - Between cards, look for guidance: `python scripts/dev/mts_signal.py read --hours 1`. A broadcast or note from `jis-nb` (the desktop's guide session) outranks this list. Follow it if it fits the hard limits above.
   - After each ship, report: `python scripts/dev/mts_signal.py send "lenovo: <card> shipped <sha> CI <green|red>" --to jis-nb`.
   - Every third card, run `get_usage` again. Stop taking new cards only at 5-hour use of 95% or more, or at the window reset.
   - Once in the window: `cd C:\MTS\mts-lenovo; python scripts\dev\live_mirror.py publish` (the mirror fix 242fbf7a1 is green). It only reads and copies; it starts and stops nothing.
8. End: overwrite nothing else. Ship, run `sync.py where` (tree clean), ack `exhaust-A` done and `b-9c6516` done, then reply in one line: cards shipped with shas, CI state, broadcasts acked.

## Not on this list (do not start)
- Removing or demoting layers (the operator said NO on 2026-10-25; the review comes after the simulator).
- New roles, rules or tooling (a freeze is pending the operator's answer).
- Gemini or YouTube work (that runs on the NUC).
