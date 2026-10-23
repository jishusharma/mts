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
2. **Session** (`start_session`, visible in the sidebar) is the default: anything over 30 expected turns, anything the
   operator may want to open or steer, any build wave or watch.
3. **One-use Agent** (background, Sonnet, used once, never SendMessage'd) for size S or M with `est_turns` <= 30 (same cost per ship as a session; overrun p90 55, so
   the brief says "stop at 40 turns and report", size S 20): a read, a fix, a card. On event turns where `start_session` is refused EVERY card runs as an Agent (chained cards allowed).
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
5. **Turn budget (operator 2026-10-18); the operator overrides every cap (operator 2026-10-21).** No hook ever blocks a prompt the operator types: "when I am telling sessions to do something ... that hook should never stop you". From his 2nd typed prompt a session is his: no hand-off nag, he compacts when he wants, it ends on his word (q-v1-turn-caps). Messages from child sessions, CI and the app are not his turns. Caps bind only unattended work (one brief, then only events), set per model by `scripts/dev/turn_meter.py` (RELAY.md): Sonnet/Haiku tool turns allowed = 4M / context (100k = 40, 250k = 16, floor 5); Opus no turn cap, hand over at 500k; Fable no cap; a Supervisor is capped by context (roles/supervisor.md). Facts (2026-10-21): 43 of 46 Opus compactions were manual `/compact`; auto-compaction fires at the window set by the MAIN checkout's `.claude/settings.json` (a stale one forced ~250k for every model). The super session owns worker reuse: on every wake it reads each running worker's `get_usage` (context), REUSES a session only when its next card needs the same files and its budget has room, and otherwise marks it completed and `archive_session`s it (delete_session needs the operator's click: never). Agents are always use-and-throw, never reused. Hard stop (safety review 2026-10-21, research/context_policy_review/DECISION_OPUS.md): an unattended session (not his 2nd+ typed prompt within 30 min) adds each turn's context to a read budget (1M for every model and the Supervisor, operator 2026-10-21, a note at 500k; events never reset it, his typed prompt does); past it PreToolUse allows only the hand-off. A Thinker (roles/thinker.md) has no turn, context or read cap: its start line or role_loader's record of an injected Thinker file exempts the session (turn_meter `uncapped_role`, 2026-10-22: a notice-briefed Thinker was denied web search and writes). Away, model_guard caps start_session 4/h, Agent 8/h, no Workflow; scheduling tools only when his latest message asks.
6. **Models.** Workers: Sonnet; Haiku for mechanical status/lookups. **Opus is the tight exception** (operator 2026-10-17: a session-spawned
   Opus can lose data on a bug or misreading, so only critical work): (a) the operator names it in their latest message, it is done;
   (b) a session starts it only for a task card in lane OPUS with `approved_by` and `crucial` (one line: live money, irreversible data,
   or a no-undo design call), cited by id in the brief. Nothing else, not "recommended" and not "better quality". Hook `model_guard.py`
   enforces both, and always denies a call without `model`. A cheap model first: Opus is for what Sonnet already got wrong or cannot undo.
7. **No clicks.** `start_session` with `initiation: "user_asked"` on operator turns (max 4 workers at once); on event turns (a message or event started the turn) the app shows an Allow card, so `model_guard.py` denies it (2026-10-23):
   use rule 3's Agent. Never an `offer` / `own_initiative` card, for any model: `model_guard.py` now denies them (operator 2026-10-18: nobody is at the screen to click).
8. **Cleanup.** A finished session marks itself completed; the coordinator marks each worker once its ship is verified.
