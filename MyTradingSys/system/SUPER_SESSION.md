# SUPER SESSION - one coordinator, many workers, hours of continuous work (operator term, 2026-10-15)

A **super session** is one coordinator session in the Claude Code Win App that spawns, steers, checks and archives worker sessions
(`start_session`) for several hours, with the operator in the loop only for direction. Max plan only, and only when the weekly
meter has headroom (Pacing below). First one: 2026-10-15, coordinator local_62faa820 (Opus), about 20 linked workers, an Opus
observer, and a second coordinator (coord-2) that drained the ship queue at the end.

While a super session runs, the relay is paused: the coordinator IS the dispatcher. When none runs, the relay (MTS-DispatchGate +
`mts-dispatcher` routine, RELAY.md) keeps the queue moving at the pace the meter allows.

## Audit of the first one (2026-10-15, 139 transcripts in the last ~24 h, scripts: transcript usage blocks)
| What | Number |
|---|---|
| Sessions | 14 Opus, 32 Sonnet, 93 Haiku (mostly dispatcher ticks) |
| Turns / tool calls / output | 4,077 assistant turns, 8,252 tool calls, 3.2 M output tokens |
| Cache reads / cache writes | 527 M / 14 M tokens (Opus 191 M, Sonnet 294 M, Haiku 42 M) |
| Coordinator alone | 319 turns, 39 M cache reads, 10 manual compactions: the most expensive single session |
| Weekly meter | 32 % used after 1.9 of 7 days (pace +5 points ahead of even spend) |
| Fixed cost of every turn | ~70-80 k tokens before any message: system tools 39 k, MCP tools 26 k, system prompt 9 k, skills 6 k, memory 3 k |

### Did compacting help?
68 real compactions (all manual) in 30 sessions; the context fell from 169 k to 70 k on average. Re-reading after a compaction
was negligible (about 1.8 k tokens per compaction: the summaries carried what the session needed).
- Overall it paid: about 17 M input-equivalent tokens saved against about 10 M spent (summary output, re-caching the new prefix).
- But 39 of 68 lost: a compaction pays back only after **about 15 more turns** (it saves ~10 k per later turn and costs
  ~145 k once). The median session ran 23 turns after compacting; 14 compactions came less than 5 turns before the session ended.
- Compaction never goes below the ~70-80 k fixed floor, so on a 1 M window a session at 120 k gains little from it.

## Rules (from the audit)
1. **Compact only if the session will run at least 15 more turns and is above ~150 k.** Otherwise: finish the step, hand off
   (NEXT_SESSION.md or a `start_session` brief) and archive. Never compact a session that is about to ship.
2. **The coordinator works little itself.** It reads results, decides, spot-checks one claim per worker (`git cherry` empty =
   shipped), and archives. Mechanical status goes to a Haiku worker; drafting and code to Sonnet; Opus only for the coordinator
   and an observer the operator asks for. Fable only when the operator starts it.
3. **At most 4 workers running at once** (gate slots are 2 per machine, `sync.py`), one writer per set of files, each with a
   full brief: goal, files, DONE-when, defaults for every open question, hard limits. Workers never ask the operator; questions
   go to the coordinator, which decides toward the goal and logs the decision in the worker's deliverable.
4. **Parallel tool calls in one message**: one turn re-reads the whole context, so batching is the cheapest saving there is.
5. **Second coordinator for the tail.** When the coordinator passes ~300 turns or the operator is about to restart, it hands the
   drain (ship queue, archive, hand-over note) to a fresh Sonnet coordinator instead of compacting again.
6. **No disk or process scans in loops** (Defender finding 2026-10-15): size a folder once with a timeout; never kill processes.

## Start (operator: open a new session, model Opus, paste the prompt below)
The coordinator, on its first turn: `get_usage` (stop if the Pacing state is THROTTLE), `python scripts/sched/relay.py stop
"super-session <session id>"` on this machine, read STATUS.md and NEXT_SESSION.md, then spawn.

## End
Drain: every worker shipped (`git cherry` empty) or its partial work handed over in NEXT_SESSION.md; archive finished workers;
`get_usage` written into the hand-over note; `python scripts/sched/relay.py resume`; one line to the operator.

## Pacing (when no super session runs) - state from the weekly meter
`f` = fraction of the week elapsed since the last weekly reset, `U` = Weekly all-models % used.
| State | Condition | What runs |
|---|---|---|
| SPEND | U < 100 f - 10, or less than 24 h to the reset with U < 85 | super session worth starting; relay on Sonnet; Fable cards allowed (operator starts them) |
| NORMAL | between | relay on its normal cadence, Sonnet builders, Haiku dispatcher |
| THROTTLE | U > 100 f + 5, or the 5-hour window > 80 % | only model-free work: Codex lab, DSA desk, CI; relay KICKs wait |
Today (10-15 17:45Z): f = 0.27, U = 32 -> NORMAL. The meter is only readable from an App session (`get_usage`), so the
coordinator (and any KICK session) writes it to `~/.claude/mts-budget.json` (not in git); the gate treats a reading older than 6 h as NORMAL.
Wiring that file into `dispatch_gate.py` is a SONNET card (not built yet).

## Prompt: start a super session (paste into a new Opus session, permission mode bypass or auto)
```
You are the MTS super-session coordinator (MyTradingSys/system/SUPER_SESSION.md). Run for hours with zero operator input except direction I give.
Goal today: <one line, e.g. "rebuild layers setups-first: catalogue -> PRE_REG -> screens">.
First turn: get_usage (THROTTLE -> tell me and stop), relay.py stop "super-session", read STATUS.md and NEXT_SESSION.md, pick the tasks that serve the goal.
Spawn workers with start_session (Sonnet; Haiku for mechanical status), at most 4 running, each with a full brief: goal, files, DONE when, defaults for open questions, hard limits from CLAUDE.md. Workers never ask me; you decide toward the goal and log it.
Verify every ship with git cherry, archive finished workers, compact only per SUPER_SESSION.md rule 1, hand the tail to a second coordinator per rule 5.
End: drain, hand-over note with get_usage, relay.py resume, one line to me.
```

## Prompt pattern: any worker or Fable session that must not stop
Lead with: "Run with zero operator input: never ask; on any open question take the most conservative default, write it as
`DECISION (OURS): ...` in the deliverable, and continue." Then: the task file on origin/fast-track, the DONE-when, the hard limits
(testnet only, no secrets, no live tree or processes, no VALIDATION/HOLDOUT reads unless the card says so), a budget stop
(+N weekly points), and a reply limit (at most 5 lines). Model and effort are set in the App before pasting; the prompt cannot set them.
Used for the Fable pilot 2026-10-15 (FABLE_PILOT_PROMPT.md).
