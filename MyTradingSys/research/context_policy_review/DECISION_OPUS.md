# Decision: Opus (2026-10-21, on COMMON_ANALYSIS.md @ 18f4d9b90)
Operator constraints: a typed prompt of his is never blocked; no session tells him about caps, turn counts or compaction; no session
may silently burn the allowance (walk-away, ping-pong, spawn storms). One mechanism covers most items: an UNATTENDED READ BUDGET.
Every tool turn taken while he is not there adds that turn's context size to a counter. A typed prompt resets it to 0. Events
(child notes, CI, app) never reset it. Past the budget, PreToolUse denies tool calls except the hand-off ones (git, sync.py, relay.py,
tasks.py, mts_signal.py, NEXT_SESSION.md, mark_completed). He is "there" from his 2nd typed prompt until 30 min after his latest one.

## Answers to "Decision needed from Opus"
1. Hard deny: BUILD, but in PreToolUse on tool calls only, for sessions he is not driving. Prompts are never touched. The hand-off tools
   stay allowed, so work is committed, not lost. A Stop block was rejected because stop_hook_active lets the second stop through.
2. Driven expiry: 30 min since his last typed prompt. Time measures "he is here"; tool turns measure cost, which the budget already does.
3. Scheduling tools (ScheduleWakeup, CronCreate, RemoteTrigger, create_scheduled_task): DENY, unless his latest typed message asks for it
   (loop/schedule/remind/cron/wake). SCHEDULING_POLICY.md already says none exist; his own /loop still works.
4. Supervisor: cumulative read budget, 100M unattended (note at 50M), not a turn count. Opus/Fable workers 40M, Sonnet/Haiku 12M
   (3x READ_BUDGET; at 100k context that is 120 tool turns, the 40-turn note fires first).
5. Child cap: DENY, per hour and only when unattended: start_session above 4, Agent/Task above 8, Workflow always (it needs his opt-in).
   Per-login daily budget file: DEFER. It needs a shared store across 3 devices; the per-session budget bounds each session now.

## Per item
1 BUILD: model_guard and turn_meter share one event test (is_event_text). A child's note naming Opus no longer unlocks Opus.
2 BUILD via the budget: ping-pong turns are unattended turns and events never reset the counter. No separate send rate needed.
3 BUILD: driven lapses 30 min after his last typed prompt.
4 BUILD: unattended Fable gets the Opus 500k context note and the 40M budget. A driven Fable stays free.
5 BUILD: Supervisor 100M budget (item 4 above). DEFER: `supervisor.py plan` STOP from mts-budget.json, which is a separate card.
6 BUILD: hourly child cap (item 5 above).
7 BUILD partly: Workflow added to the model_guard matcher and denied when unattended. Subagents themselves stay unmetered; their
  parent's Agent calls are rate-limited instead.
8 BUILD partly: `turn_meter.py status` shows driven, tier and unattended read (M). DEFER: a doctor check on hook_errors.log.
9 DEFER: a doctor/sync.py check that each machine's hooks match trunk, and a daily per-login total (Network card). Per-session budgets
  bound each machine meanwhile.
10 DROP: USER_CAP is unreachable by the operator's design (driven); it costs nothing.
11 BUILD: unknown context counts as 250k in the budget.
12 BUILD (item 3 above). Unverified wake payloads no longer matter, because the tools that schedule wakes are denied.
13 BUILD: leading <system-reminder> blocks are stripped before the event test, in both hooks.
14 BUILD: stop_guard remembers the last 50 sessions, not 1.
15 DEFER: prune completed sessions only. It is LOW; the budget restarting after 7 idle days is harmless.
16 DEFER: the Supervisor start line is LOW, and its 100M budget now bounds it anyway.
17 DROP: MTS_TURN_METER=off is the operator's own switch.
18 = answer 1.
Activation: hooks run from each machine's MAIN checkout. Nothing here works until that checkout pulls trunk.
