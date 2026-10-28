# Coordinator idle while a background task runs: design note, 2026-10-28

Card `coordinator-sits-idle-during-long-backgr`. It was folded into `bug-long-background-processes-dead-ends`, and its evidence comes from `research/bg_process_audit_2026-10-28/AUDIT.md`.

The operator, 2026-10-27: "you are sleeping while a process is running for 1 hour 15 minutes. This is a gap." That was link `a13f34b0fe4c70a85`: 75 min, 37 tool calls, polling itself with placeholder calls.

## 1. How long is too long for one link (evidence)
Agent links over 7 days (255 links), in minutes:

| p50 | p90 | max | over 45 min |
|---|---|---|---|
| 5 | 34 | 181 | 18 (7%) |

Of the 30 links that ran over 30 min:
- 11 were useful on time.
- 6 were useful but late (over 90 min).
- 13 ended as "waiting on its own background work", the same pattern as `a13f34b0`.

**Default: 45 min per link (OURS, about p93).** Other kinds have their own caps; the table is in AUDIT.md.

## 2. What the coordinator does while it waits
| option | cost | risk | evidence |
|---|---|---|---|
| A. Keep waiting on a 50-min watcher (status quo) | 0 tokens | 10 of 15 watchers timed out with nothing to report (7.9 h). A hung link is seen only at the timeout, or never | AUDIT by-kind table |
| B. Put a second ready card into the free slot right away | one worker | gate contention (2 slots per machine) | `plan` already prints SPAWN when a slot and a card are free; the watcher wakes ACTIONABLE once per plan |
| C. Poll more often (every 5 min) | about 12 coordinator wakes per hour | burns the 5-hour window for nothing; the operator rejected the 5-min wake loop (`supervisor.py:455` STUCK_MAX) | - |
| D. Read-only triage between wakes (RAW-AGED cards, a review of a shipped diff) | small, and a Haiku Agent can do it | none: it is read-only | coordinator-sits-idle sat raw and unseen for 2 h, and 8 IMPORTANT/CRUCIAL cards are raw > 12 h today |

**Default: B, then D.** Fill every free slot first. If there is no slot or no card, refine or drop the oldest `RAW-AGED` card from `plan` (one per wake). Never C.

## 3. How a stuck link gets escalated
**Default (built):**
- `bg_watch.py` reports any background task past its cap. `supervisor.py wait` wakes on it the moment it crosses the cap: `TRANSITION STALLED-BG ...`. It does not wait for the 50-min timeout.
- `plan` prints `STALLED-BG <kind> <id> <age> > cap, no output Nm -> owner: TaskStop <id>`.
- The coordinator then does three things that same wake:
  1. `TaskStop`s the task.
  2. Writes one line saying why.
  3. Re-dispatches the card. If the same card stalls twice, it marks the card BLOCKED with the reason, following SUPER_SESSION.md Failure handling.
- No operator question is asked.

## Why `watchcheck` did not close this
Card `super-session-coordinator-stalls-when-it` (5d9748041) made sure every coordinator turn ends with *a* wake source, a live `supervisor.py wait`. It never asked whether the work behind that wake was still moving:
- A coordinator waiting on a 50-min watcher passes watchcheck while a link hangs.
- The watcher woke only on shas, CI and gate slots (`_detect_transition`). A hung task changes none of these.

The fix gives the watcher a fourth wake reason: a task crossing its cap.

## Why no session saw the raw card
`0fd607ca4` shipped this card as `raw` with an empty result and no deliverable. Nothing surfaced it:
- `tasks.py dispatch` never offers raw cards.
- `plan` listed no raw cards.

Now `plan` prints `RAW-AGED n IMPORTANT/CRUCIAL card(s) still raw > 12h (...)` every wake, so the Supervisor sees a filed-but-unrefined bug within 12 h.

## Follow-up card
None needed. The default is built and tested in the same ship (`bg_watch.py`, `supervisor.py` plan and wait, `test_bg_watch.py`).
