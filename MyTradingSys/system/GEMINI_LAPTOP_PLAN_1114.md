# GEMINI LAPTOP PLAN, 2026-11-13 20:50Z to 2026-11-14 14:20Z (Supervisor A, operator order 2045Z)

Goal: use 100% of the laptop's Antigravity Gemini quota before it refreshes (~14:20Z 11-14). Reading at 20:45Z:
Gemini pool 81% of the week left, 93% of the 5 h left. Claude/GPT pool inside agy: 50% of the week left (refreshes in 6 d).
Written by Opus for a Haiku Supervisor A to follow. Use only the steps below; anything else goes to login C as an `ask`.

## Facts (checked 20:45Z)
- argon on this account answers `429 RESOURCE_EXHAUSTED Individual quota reached, resets ~14:17Z 11-14`. Use `:flash` only.
  All 12 argon jobs of the GEMINI_NOW.md run died after 11 s (log: `~/.gemini/mts-gq/<id>.log`), so those cards stayed ready.
- Run the queue with `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` (otherwise it crashes on cp1252 output).
- Delivery `solo` (default): each finished card ships itself via `sync.py ship`. A card someone else claims prints SKIP.
- Work tree: `C:\Users\e-ngineers\IdeaProjects\mts-desktop-f7iu69n-supervisor-a-gemini-1114` (WT below).
- NUC (login C's flash account) runs the blind-edge 1114 set and the plain 1113 flash twins. The laptop takes the rest.

## Queues
Started 20:50Z as two background Bash calls (`run_in_background`, never `&`), in WT:
- LA (21 cards): every `*-argon-1113` card, run on flash (hunt x3, gap-hunt, mine x4, hilega-formula, review x7, i3-ny-open, i4-hedging, nk-extract, conceptualizer, crypto).
- LB (20 cards): 1114 synthesis, rsi-census, rederive x4, hilega-recheck, sourcecheck x2, then the 11 `gemini-rulebook-*-1113` in reverse.
- LC (when LA or LB ends): every card still `ready` in the CODEX lane. List it fresh in WT:
  `git -C <WT> fetch -q origin`, `git -C <WT> merge -q origin/fast-track`, then `python scripts/dev/tasks.py list --lane CODEX --state ready`.
  Run them as `<id>:low:flash` in one `gemini_queue.py run` call (claimed or done cards SKIP by themselves). At most 2 queues at once.

## Every wake (Haiku), in this order, all cheap
1. The normal Supervisor wake (role file): `get_usage`, `usage_reminder.py record`, `supervisor.py plan`, act on its lines.
2. In WT: `python scripts/dev/gemini_queue.py status | tail -45` (with the two env vars). Count DONE / FAILED / RUNNING.
3. A queue finished (task notification) and fewer than 2 run: start LC (above). Nothing ready and unclaimed: go to step 6.
4. A log shows `RESOURCE_EXHAUSTED` for flash: start no queue until the reset time it prints; note it in one line.
   If it says the weekly pool is empty: the goal is met, stop the Gemini work.
5. CI: `gh run list --branch fast-track --limit 3 --json conclusion,headSha,status`. Red: find the breaking commit
   (`gh run view <id> --log-failed`). A `gemini-queue` commit broke it: `git revert` that commit in WT and ship within 10 min. Never forward-fix.
6. Refill (the ready list will run dry in ~4-6 h): login C was asked (q-51556b, 20:50Z) to have Session_Planner file 30+ READY
   CODEX cards for Gemini. No reply or no cards by 22:00Z: start ONE background Agent, model sonnet:
   `You are Session_Planner.` Brief: file and refine 20 READY CODEX-lane cards for the Gemini queue (`<id>-gemini-1114`, est. 10-20 min each, done_when testable):
   test-gap writers (a module without tests -> a new test that fails on the old code first), diff review of the last 24 h of
   trunk commits (one card per area), raw -> refined drafts of the raw cards on the board, blind re-derivation of edge results
   that already have a PASS/FAIL verdict, PRE_REG lint and quote audits, doc contradiction scans. Not YouTube-only.
   Ship once. Then queue those cards on flash.
7. After the Gemini pool is used up (or 14:20Z): stop. Do not use the agy Claude/GPT pool (`:sonnet`, `:gpt`) unless login C answered yes in q-51556b.
8. Re-arm `supervisor.py wait --timeout 50m --login A` (own background call) and end on `supervisor.py watchcheck --login A` rc 0.

## Economy
- Haiku reads status lines and tails only, never whole Gemini outputs. Gemini output review is login C's job (or a Sonnet Agent when C asks).
- No Opus. At most one Sonnet Agent at a time for this plan.
