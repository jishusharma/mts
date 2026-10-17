# WORKERS: which worker runs a task, on which model (canonical; operator 2026-10-17)

Every other file points here. Numbers come from `python scripts/dev/worker_cost_report.py --days 5` (311 transcripts, 2026-10-12..17;
"eq" = input-price-equivalent tokens: input 1, cache-write 1.25, cache-read 0.1, output 5; list-price ratios between models NOT applied).

## Evidence
- Same cost at the same length: Sonnet Agent and Sonnet session both median 428k eq per task (21 vs 28 turns). Per ship: Agent 921k, session 802k.
- Cost per turn by task length (Sonnet): 5-15 turns 15k eq, 16-30 14k, 31-60 19k, over 60 20k. Peak context 77k / 105k / 156k / 209k.
  So "100k" is about 30 turns; state limits in turns, not tokens.
- Cold start: an Agent starts at a median 52k context (session 73k) = 4-5 turns of cost. A fresh worker beats continuing a warm one
  once the warm one is 13+ turns past 30 (matches the 15-turn compaction payback in SUPER_SESSION.md).
- Overruns: 4 of 19 Agents ran over 40 turns (p90 55). An Agent cannot be seen or steered in the sidebar; a session can.
- Opus: 1,970k eq per ship vs Sonnet 802k (2.5x tokens before any price multiplier). Haiku sessions: median 2 turns (status only).
- Compaction: 12 of 311 transcripts, one per 44 turns. A backstop, not a plan.

## The rule
1. **Worker type is set before the work starts**, on the task card: `est_turns` (whole number) and `worker` (`agent` | `session`);
   `tasks.py check` enforces it for SONNET/HAIKU/OPUS-lane cards (TASK_REFINEMENT.md). Run lanes (DSA, JIS-NB) are not Claude-worker cards.
2. **Session** (`start_session`, visible in the sidebar) is the default: anything over 15 expected turns, size M, anything the
   operator may want to open or steer, any build wave or watch.
3. **One-use Agent** (background, Sonnet, used once, never SendMessage'd) only for size S with `est_turns` <= 15: a read, a single
   fix, a card. The brief says "stop at 20 turns and report". Also the fallback on event turns where `start_session` is refused.
   Name every Agent in one line to the operator (invisible in the sidebar).
4. **Over 40 expected turns: split the card.** A running worker hands over at the 40 tool-turn cap (RELAY.md) to a fresh worker;
   state lives in files (task card, notes folder), not context.
5. **Compaction is a backstop.** `.claude/settings.json` keeps CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=25. Never compact by hand a worker
   that will ship soon; compact a long-lived coordinator only with 15+ turns left and above ~150k, else hand over.
6. **Models.** Workers: Sonnet; Haiku for mechanical status/lookups; Opus only when the operator names it (card lane OPUS with
   `approved_by`). The coordinator runs on the model the operator started it on (Sonnet default; Opus when the operator picks it for
   judgment-heavy direction) and does little itself. Hook `model_guard.py` denies `Agent`/`start_session` without `model`, and Opus;
   to use Opus for a named reason set `MTS_ALLOW_OPUS=1` in that session's environment or ask the operator to start it.
7. **No clicks.** `start_session` with `initiation: "user_asked"` on operator turns (max 4 workers at once); on event turns where it is
   refused use rule 3's Agent. Never an `own_initiative` card for work already in scope.
8. **Cleanup.** A finished session marks itself completed; the coordinator marks each worker once its ship is verified.
