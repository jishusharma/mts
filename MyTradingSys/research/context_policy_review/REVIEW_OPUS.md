# Opus review: context and compaction policy (2026-10-21, read-only, nothing edited)

Root fact the Sonnet review missed: the trunk policy is NOT live. Hooks and env load from the main checkout
C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed (HEAD 614bbc889, 2026-10-17, 1858 commits behind, dirty). Its turn_meter.py has no
Fable block, no Opus 150k block, and resets counters on compaction; its settings.json still sets CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=25
(trunk removed it in 600149c4e). Proof: all 11 auto compactions in ~/.claude/projects fired at preTokens 245-288k on every model
(Haiku, Sonnet, Opus, Fable), dates 10-15..10-21; Fable session c11be9cb took 84 operator prompts (13 compactions), only generic "cap 40/10" nags.
So today no session can reach 300k/350k/400k/500k without compacting at ~250k first.

Sonnet items: 1 disagree (350k/400k unreachable; handover files already written by `supervisor.py handover`, supervisor.md:49-51).
2 partly: resumed-over-150k block agreed; 300k/350k nags drop (unreachable now; OURS numbers, only 5 of 141 Opus sessions ever passed 300k).
3 disagree: blocking an auto compaction near the limit lets the next request exceed the window -> "prompt too long" errors, session stuck; blocking
manual /compact gates the operator's own command. 4 agree (doc only). 5 is really #1, but a sha only shows the staleness, it does not fix it.
Bugs it missed: event turns count as operator turns (this session's state file: user=2 = standby + one cross-session message), so an Opus
coordinator over 150k gets its worker's report blocked and lost; Supervisor detection false positives (afa3fa90, 01d7aa30: the brief quotes
"You are Supervisor" -> marked Supervisor -> no 150k block, no turn cap; turn_meter.py:169).

Changes, priority order (each test must fail on today's trunk code):
1. Main checkout: operator/coordinator fast-forwards it to fast-track (builders don't touch its dirty files). Test: mts_doctor check that main
   checkout's scripts/dev/turn_meter.py and .claude/settings.json equal origin/fast-track's; fails today.
2. .claude/settings.json env: CLAUDE_AUTOCOMPACT_PCT_OVERRIDE "50" (OURS: = the 500k job size on 1M windows; the knob is proven by the data).
   Without it a Supervisor auto-compacts near the full window and re-reads ~1M per wake. Test: settings test asserts 50 == OPUS_CTX_CAP/10k.
3. turn_meter.py:216: drop `state["user"] > 1` (ctx >= 150k already proves an earlier turn; fixes resumed/pruned sessions). Test: fresh state,
   opus transcript 200k, one prompt -> blocked.
4. turn_meter.py UserPromptSubmit: prompts starting "<cross-session-message", "<side-sessions-event", "<ci-monitor-event", "<task-notification"
   neither count nor block. Test: opus 200k, user=2, cross-session prompt -> not blocked.
5. turn_meter.py SessionStart source=compact: Opus/Fable non-Supervisor -> state["compacted"]=1, next operator prompt blocked (use and destroy);
   Supervisor -> additionalContext "compacted: run supervisor.py plan, rebuild from board". Test: compact then small-ctx opus prompt -> blocked.
6. turn_meter.py:169: match only `"text":"You are Supervisor` / `"content":"You are Supervisor` at a block start. Test: quoted phrase -> not Supervisor.
7. Docs: supervisor.md:48 drop "or 500k context" from Transit (compaction is the net, item 5 rebuilds); WORKERS rule 5 "nobody runs /compact" -> fact.
Unattended Supervisor past its limit = no successor at all: auto-compact at 500k + item 5's rebuild nudge; hand over only on time/5h budget.
Not build: PreCompact hook, per-model autoCompactWindow (unverified), 300/350/400k nags, peer-starts-successor, sha in state file.
Unverified: whether the main checkout can be fast-forwarded without touching the operator's dirty files; that 50% maps to 500k on Opus/Fable windows.
