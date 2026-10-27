# Compaction for long and unattended sessions (MTS_Doctor, 2026-10-24)

Operator rule (2026-10-24): attended sessions (Thinker, monitored Fable runs) grow as the work needs; the operator compacts them when he sees fit.
Unattended sessions (super session coordinator, workers) must stay lean: "I am not ready to lose money and resources in burning tokens unnecessarily."
Method: one Sonnet research agent (Anthropic docs fetched directly; GitHub issues partly via mirrors). Items without a source are marked UNVERIFIED.

## What Anthropic documents
- 1M-window models auto-compact at about 967K by default (code.claude.com/docs/en/model-config, "Context window and auto-compaction").
- The working control is a token window, 100K-1M: `autoCompactWindow` (settings), `/autocompact <n>` (saved per model, so it hits every session on that model),
  `--autocompact` (one launch), env `CLAUDE_CODE_AUTO_COMPACT_WINDOW` (wins over all). Same page, "Set the auto-compact window".
- `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` (the knob MTS used 10-16..10-18) is a percent of that window and can only lower it (code.claude.com/docs/en/env-vars).
- Compaction with a warm cache costs "a fraction"; after the cache expires it reprocesses everything; compact at a natural break, not mid-task
  (code.claude.com/docs/en/prompt-caching). `/clear` costs nothing (code.claude.com/docs/en/costs).
- `idleCompaction`: compacts shortly before the 1 h cache expires once context is over 200K and idle about 54 min; documented for the terminal,
  desktop app UNVERIFIED (code.claude.com/docs/en/settings-reference).
- Long-running agents: "compaction isn't sufficient"; use discrete sessions plus a progress file and git (anthropic.com/engineering/effective-harnesses-for-long-running-agents).
  The lead agent saves its plan to memory and spawns fresh subagents (anthropic.com/engineering/multi-agent-research-system).

## What users report
- The percent override is broken on current versions: GitHub anthropics/claude-code #63186 (closed "not planned"; a settings.json env block does not
  reach the compaction logic) and #82761 (open; compactions fired anywhere from 370K to 828K). So MTS's old `"25"` / `"12"` setting may never have worked.
- Working pattern for multi-day agents: auto-compact off, the agent writes a checkpoint file, `/clear`, resumes from the file (dev.to "keep a Claude Code
  agent running for days"; 11 of 11 clean cycles, one machine). Failure modes seen: empty checkpoints, stale notes, a stall at the clear step.
- Window set below the base context (about 75-85K here) causes "Autocompact is thrashing" aborts: keep any window well above 150K (UNVERIFIED for MTS).

## Cost reasoning (prices: API docs; Max-limit weighting NOT FOUND)
Every turn re-reads the whole context. The pilot coordinator was at 109K after 10 minutes. Letting it grow toward 967K makes the average turn read
about 530K; resetting near 200K keeps it near 150K, about 3.5x fewer tokens read per turn. A warm compaction or a `/clear` plus re-reading the notes
file costs one small cache write. So for unattended sessions, earlier is cheaper; for attended work the operator decides.

## For MTS
1. **Attended** (Thinker, Fable, operator chats): no change. App default about 967K; the operator runs `/compact <what comes next>` at breaks.
2. **Workers** are already one task each, then thrown away (WORKERS.md rule 4, SUPER_SESSION D1/D3). Nothing to add.
3. **Unattended coordinator**: a project-wide setting would also hit attended sessions, and the desktop app has no per-session launch flag or env.
   The per-session way that fits the app: the coordinator rotates. At a natural break (after a wake's step 5, notes file rewritten) and context
   over about 200K, it is cleared and rebuilt from the notes file, which D5 already requires. Open: whether the app lets a session clear itself, or
   whether the parent must call `clear_session` and send "rebuild from notes" (the Doctor started pilot 1, so the Doctor can do it).
4. **Test before rollout** (one cheap test session after pilot 1, not mid-pilot): (a) does `clear_session` plus one message rebuild a coordinator
   correctly from its notes file; (b) does `autoCompactWindow` in a settings file take effect in the desktop app (watch the actual compaction point).
   Then measure it as its own pilot against pilot 1's coordinator context and cost.
