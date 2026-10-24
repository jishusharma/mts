# Context cost: what MTS sessions pay for, and what to change (MTS_Doctor, 2026-10-24)

Operator ask (2026-10-24): "this is the biggest save that I want to have, context building ... what Anthropic says, what the community says, what really works."
Method: measured all 134 MTS session transcripts on JIS-NB from the last 7 days (10,262 main-thread turns, subagents excluded), plus two Sonnet research
agents (Anthropic docs; community practice). Scripts: read-only, run from the Doctor's scratchpad.

## 1. Measured (7 days, JIS-NB)
| What | Number |
|---|---|
| Context at a session's first turn | median 74,754 tokens (p10 67k, p90 79k) |
| ...of which MTS's own files | CLAUDE.md about 1,800; MEMORY.md about 1,000. The other ~72k is the app's system prompt and tool definitions |
| Context per turn | median 125,110, p90 187,747 |
| Share of all re-read context that is the first-turn base | 57% |
| Turns per session | median 40, p90 171, max 580 |
| Sessions over 200 turns | 10 of 134, but 39% of all context |
| Tokens | cache reads 1,315M, cache writes 34.9M, output 6.3M |
| Cache writes by cause | session starts 13%; full mid-session rewrites (cache misses, 126 of them) 33%; new content each turn 54% |
| Context by model | Sonnet 63%, Opus 25%, Haiku 7%, Fable 4% |

Weighted by API price (Opus/Sonnet 5.5: read 0.05x input, 1-hour cache write 2x, output 5x; platform.claude.com prompt-caching docs):
cache writes about 42% of cost, cache reads 39%, output 19%. Mid-session cache misses alone are about 14% of cost.
Whether the Max 5-hour/weekly limits weigh tokens the same way: NOT FOUND in Anthropic docs.

The hook removals of 2026-10-24 saved **time** (0.33 -> 0.27 s per tool call), not context: those hooks added a few hundred tokens per prompt at most.

## 2. What Anthropic says (code.claude.com docs)
- Every request re-sends system prompt + tools + CLAUDE.md + auto memory + all messages and tool results; caching makes the repeat cheap, not free (prompt-caching, costs).
- Max plan main conversation: 1-hour cache; subagents and compaction: 5 minutes. A gap over the TTL means the next turn re-writes the whole history.
- Breaks the cache: switching model, fast mode on, changing the tool set, compaction, Claude Code upgrade. Does not: editing CLAUDE.md (the edit applies only after clear/compact), effort change on 5.5-family models, permission mode, spawning a subagent.
- Cache is per machine and directory: parallel sessions in the same folder share it; separate worktrees do not.
- `/clear` costs nothing; `/compact` is cheap while the cache is warm and expensive on an old, cold session; compact at natural breaks between tasks.
- CLAUDE.md under 200 lines; "would removing this line cause mistakes?". MEMORY.md: first 200 lines / 25 KB load every session.
- Subagents: own context, only the summary returns; they still count toward usage limits.
- Measure: `/usage` shows a "Prompt cache (main)" hit line; `/context` shows per-item cost.

## 3. What experienced users report (blogs; no verified numbers)
Ranked: one task per fresh session with a handoff file; keep the prefix stable (pick model and effort at start); Sonnet default, Haiku for mechanical
subagents; prune unused MCP servers (tool search already defers them); small CLAUDE.md; filter long tool output; compact only at task breaks; subagents
for wide reading (but they carry 10-20k start-up each, so not for small tasks). Backfired: switching model or fast mode mid-session, relying on
auto-compact, proxies that strip caching.

## 4. Recommendations for MTS (ranked by measured saving)
1. **Stop mid-session cache misses (about 14% of cost).** A session that will sit idle over an hour (coordinator overnight, a session waiting on a child)
   rebuilds its whole history at 2x on the next wake. Rule: before an idle wait over an hour with context over ~100k, compact first (cheap while warm);
   never switch model or fast mode mid-session (Opus spawn recipe already sets the model on a tiny standby prompt, which is fine).
2. **Short sessions (sessions over 200 turns = 39% of context).** One task per session is already CLAUDE.md step 5; the long ones are coordinators and
   operator chats. Operator chats: start a fresh session per new topic instead of continuing a long one (`/clear` is free).
3. **Keep tool output small (new content = 54% of cache writes).** Wide reading in a subagent (only the summary returns); `head_limit`, filtered
   commands. Keeps CLAUDE.md "never conclude from truncated output": parse and count in the subagent or script, return the count.
4. **Base 75k: mostly not ours to cut.** MTS files are about 2.8k of it. Small wins: switch off connectors a lane never uses (scheduled-tasks is
   banned by SCHEDULING_POLICY anyway); keep CLAUDE.md and MEMORY.md at today's size. Expected saving: a few thousand tokens per turn, not tens.
5. **Not worth it:** more hook removals for context (negligible); disabling auto-memory (1k tokens, and it carries operator feedback).
6. **Measure, don't guess:** re-run this measurement after a week of the new rules; compare per-turn median, miss count and cost shares.
