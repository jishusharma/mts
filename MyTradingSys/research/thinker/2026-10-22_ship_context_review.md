# Ship + context changes review (Thinker, 2026-10-22 ~22:50Z)

Operator ask (2026-10-22): "check what needs to be improved/tuned wrt all the shipping related changed we made so far as well as the context changes".

Scope: this session's commits on origin/fast-track (ea175ecb, c21235c8, 88db1afd, e8ab70e2, 52715797, e9f1e3a1,
5e716d75, c8ff1542, 61573bae) and the signal log (`python scripts/dev/mts_signal.py read`, read 22:45Z).

## Working (verified this session)
- Context: after the operator's /compact the SessionStart hook re-injected thinker.md with the current sha (61573bae) and
  token duck-nail; the banner was right first time (5e716d75 works in the field).
- CI: run 848 on 61573bae green at 22:36Z (GitHub Actions list); `ci_watch.py` fresh read = ok.
- Soak (52715797): seed 7 wall-clock run, 0 FAIL at T+64 min; ends ~00:21Z.

## To fix (cards, raw)
1. Ship signal says "done" when the ship failed, and repeats. `scripts/dev/mts_signal.py:256-287` (`auto_send_text`) sends
   kind=done for every Bash call matching `sync.py ship`, without checking the ship succeeded. Evidence: signals 2229Z,
   2232Z, 2232Z (vm) are the same "done ... Result:" line; 2229Z and the first 2232Z were failed ships (extra tests, then
   Fix-first block). Jis-nb 2227Z/2237Z repeat one krown ack. Fix: send done only when the tool response shows the ship
   completed (cherry=0 / exit 0); a failed ship sends kind=note "ship FAILED <step>"; drop an identical text from the same
   host within 15 min. Lane SONNET.
2. Cloud ship fails on a shallow clone. Cloud containers clone with depth 50; `test_lab_query.py:183-187` compares a
   commit from history, so `sync.py ship` failed at Step 3xt until `git fetch --unshallow origin` by hand. Fix: ship
   (or run_extra_tests) runs `git fetch --unshallow` once when `git rev-parse --is-shallow-repository` is true. Lane SONNET.

## Open for the operator (PENDING OPERATOR)
3. Supervisor C ended early. Signals 2239Z: mode=NORMAL then mode=ENDED in the same minute, window end=02:19Z, 5h=4%,
   week=13%; 2240Z "next Supervisor spawns the Krown prereq/S0/S1 builders". 3.5 h of budget-cheap window unused and no
   one starts the next Supervisor (no schedulers by rule). Options: A) Supervisor stays up to its window end when ready
   cards exist (roles/supervisor.md change); B) leave as is, operator restarts by hand; C) Thinker reports it each
   30-min check (monitor, below). Recommend A (idle login hours are the cheapest work).
4. A worker posted `[done] ship cbp-channel-latest Result: not shipped; ... one test error unresolved` (2233Z): a
   failed task reads as done on boards that filter kind=done. Covered by fix 1 if ship failed; if it shipped a
   "not shipped" Result line, the worker template needs "ship only when green". Check after fix 1.

## Not a problem
- The "CI RED" prompt notice at 22:37Z after green 22:36Z: `ci_watch.py` caches 5 min (`ci_watch.py:25`); fresh read ok.

## Monitoring
Thinker runs a 30-min in-session check (background shell, no scheduler): new signals, CI on fast-track head, soak log.
Reports only changes.
