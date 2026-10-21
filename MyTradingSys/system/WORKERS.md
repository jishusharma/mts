# WORKERS: which worker runs a task, on which model (canonical; operator 2026-10-17)

Every other file points here. Numbers come from `python scripts/dev/worker_cost_report.py --days 5` (311 transcripts, 2026-10-12..17;
"eq" = input-price-equivalent tokens: input 1, cache-write 1.25, cache-read 0.1, output 5; list-price ratios between models NOT applied).

## Evidence
- Same cost at the same length: Sonnet Agent and Sonnet session both median 428k eq per task (21 vs 28 turns). Per ship: Agent 921k, session 802k.
- Cost per turn by task length (Sonnet): 5-15 turns 15k eq, 16-30 14k, 31-60 19k, over 60 20k. Peak context 77k / 105k / 156k / 209k.
  So "100k" is about 30 turns; state limits in turns, not tokens.
- Cold start: an Agent starts at a median 52k context (session 73k) = 4-5 turns of cost. A fresh worker beats continuing a warm one
  once the warm one is 13+ turns past 30.
- Overruns: 4 of 19 Agents ran over 40 turns (p90 55). An Agent cannot be seen or steered in the sidebar; a session can.
- Opus: 1,970k eq per ship vs Sonnet 802k (2.5x tokens before any price multiplier). Haiku sessions: median 2 turns (status only).

## The rule
1. **Worker type is set before the work starts**, on the task card: `est_turns` (whole number) and `worker` (`agent` | `session`);
   `tasks.py check` enforces it for SONNET/HAIKU/OPUS-lane cards (TASK_REFINEMENT.md). Run lanes (DSA, JIS-NB) are not Claude-worker cards.
2. **Session** (`start_session`, visible in the sidebar) is the default: anything over 15 expected turns, size M, anything the
   operator may want to open or steer, any build wave or watch.
3. **One-use Agent** (background, Sonnet, used once, never SendMessage'd) only for size S with `est_turns` <= 15: a read, a single
   fix, a card. The brief says "stop at 20 turns and report". Also the fallback on event turns where `start_session` is refused.
   Name every Agent in one line to the operator (invisible in the sidebar).
3a. **Haiku for scoped work (operator 2026-10-17: Haiku is underused).** A task is *scoped* when the brief can name the files, the
   exact change or command, and a check that says done (a test, a count, a diff to compare): mechanical edits, lookups, recomputing
   numbers, spec-derived tests, doc and registry upkeep, running a script and reporting. Scoped work goes to a one-use Haiku Agent,
   not to the session itself and not to Sonnet. Brief = files + change + done check + "stop at 15 turns and report". A session spawns
   **at most 5 Haiku Agents at a time**; the session reads each result and spot-checks one claim (`git cherry`, a re-run). Needing
   more than 5 in parallel means the work is a wave: make that session a super session (SUPER_SESSION.md), which budgets turns as in
   rule 5. Unscoped or judgment work (design, a bug nobody has located, anything touching live money) is not Haiku work.
4. **Over 40 expected turns: split the card.** A running worker hands over at the 40 tool-turn cap (RELAY.md) to a fresh worker;
   state lives in files (task card, notes folder), not context.
5. **Turn budget, no compaction (operator 2026-10-18).** Caps bind unattended workers only (a Supervisor is capped by context, 500k, not turns: roles/supervisor.md); a session the operator is driving ends on his word (q-v1-turn-caps, 2026-10-20). Nobody runs `/compact` and `.claude/settings.json` sets no auto-compact override (Claude Code's own built-in auto-compact near the full window still exists; the caps below keep sessions well short of it). A turn costs the whole context, so the limit is turns per context size, set per model by the hook
   `scripts/dev/turn_meter.py` (RELAY.md): Sonnet/Haiku: tool turns allowed = 4M / context (100k = 40, 250k = 16, floor 5), 10 operator turns;
   **Opus: no turn cap, hand over at 500k context**; **Fable: no cap of any kind except ONE operator message per session, a HARD rule**
   (the hook blocks the 2nd prompt and ignores `MTS_TURN_METER=off` and the cap env vars; nobody changes it). Long single-message
   Opus/Fable sessions are wanted. The super session owns this: on every wake it reads each running worker's `get_usage` (context),
   REUSES a session only when its next card needs the same files and its budget has room, and otherwise marks it completed and
   `archive_session`s it (delete_session needs the operator's click: never). Agents are always use-and-throw, never reused.
6. **Models.** Workers: Sonnet; Haiku for mechanical status/lookups. **Opus is the tight exception** (operator 2026-10-17: a session-spawned
   Opus can lose data on a bug or misreading, so only critical work): (a) the operator names it in their latest message, it is done;
   (b) a session starts it only for a task card in lane OPUS with `approved_by` and `crucial` (one line: live money, irreversible data,
   or a no-undo design call), cited by id in the brief. Nothing else, not "recommended" and not "better quality". Hook `model_guard.py`
   enforces both, and always denies a call without `model`. A cheap model first: Opus is for what Sonnet already got wrong or cannot undo.
7. **No clicks.** `start_session` with `initiation: "user_asked"` on operator turns (max 4 workers at once); on event turns where it is
   refused use rule 3's Agent. Never an `offer` / `own_initiative` card, for any model: `model_guard.py` now denies them (operator 2026-10-18: nobody is at the screen to click).
8. **Cleanup.** A finished session marks itself completed; the coordinator marks each worker once its ship is verified.
