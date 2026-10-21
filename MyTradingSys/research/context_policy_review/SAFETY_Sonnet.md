# SAFETY review - Sonnet, round 1 (independent)  (ran test_turn_meter 26 passed, test_stop_guard 7 passed, own simulation)
Base fact: no cap in turn_meter.py blocks anything. Each cap only prints a nag (turn_meter.py:228,233,267,270) the model may ignore.
Hard limits that exist: model_guard (which model starts) and the plan window. "Bounded before" meant "asked nicely before".

1. HIGH (NEW) Event ping-pong. Trigger: two sessions message each other, or ci_watch/task-notification repeat. is_event_prompt
   (:185-188, return :215) never counts them. Sim: 200 cross-session prompts, counters stay 0. Before: they hit USER_CAP.
   Stops it: nothing (model_guard.py:114-145 checks only that the target is yours, not a rate). Cost: unbounded full-context re-reads.
   Fix: separate "events" counter, nag only past ~30/hour; PreToolUse rate limit on send_message per target.
2. HIGH (NEW) "Driven" is set by count alone (:217) and sticky. Trigger: a worker gets its brief plus ONE follow-up, operator leaves.
   Sim: after 2 prompts, 100 tool turns gave 0 nags. Only an event prompt un-drives (:212-214). Stops it: nothing. Cost: a worker
   runs until the plan limit. Fix: driven expires with idle time (no typed prompt for ~20 min: tool-turn nag binds again). A typed
   prompt is never touched.
3. HIGH (NEW) Fable: no cap, no nag (:224,:263). Trigger: operator names Fable once and leaves, or a brief starts it. Stops it: nothing
   (model_guard.py:131-133 only refuses messaging it). Cost: dearest model, context grows unbounded. Fix: unattended Fable only
   (not driven) gets a nag at 500k context; driven stays free.
4. HIGH (NEW+OLD) Supervisor: capped by context only, and only by nag (:226-228,:266-268). Sim: 300 tool turns with unknown context,
   0 nags. A Supervisor under 500k (autocompact override 50) is never nagged however long it runs, on Opus, for hours. postTokens
   after a compact hides size (:146). Stops it: get_usage pacing in SUPER_SESSION.md is prose read by the same model. Fix: nag every
   150 tool turns / 2 h "run get_usage, stop on THROTTLE"; make `supervisor.py plan` print STOP from mts-budget.json.
5. HIGH (OLD) Fan-out is unbounded. The "4-session cap" is prose: no script enforces it (grep scripts/dev). model_guard.py:226-231 allows
   any number of start_session/Agent calls with a cheap model; Opus unlimited once "opus" is in the operator's latest message
   (:171-187) or a card cites it (:192-201). Cost: workers x turns x context. Fix: PreToolUse count of running children per parent,
   deny start_session above 4 (a tool call, never a typed prompt).
6. MED (OLD) Subagents skip every hook (:201). An Agent worker has no cap or nag; the parent counts it as one tool turn; several can
   run in parallel. Fix: model_guard requires a stated turn limit in the Agent prompt; Supervisor limits parallel Agents.
7. MED (OLD) Nag-only caps: Sonnet is re-nagged every 5 turns (:269) but nothing ends it. Fix: after 3 ignored nags, PostToolUse may
   deny further tool calls (never UserPromptSubmit); the next typed prompt resets it.
8. MED (NEW) Unknown context means no cap: model_and_context returns ("",0) on an unreadable transcript (:161,:164) or postTokens 0
   (:148); then the 4M/ctx scaling (:230,:261) and the Opus check are skipped. Fix: treat unknown as 250k and log it.
9. MED (NEW) "<system-reminder" counts as an event (:172). If operator prompts reach the hook with that prefix (this chat's do), he is
   never counted or "driven" and a stray reminder can un-drive a session (:212). Not blocked, but caps misfire. Fix: match event tags
   only, drop system-reminder, or check the real hook payload.
10. MED (OLD) Three devices: state is per machine (:42), no combined total. Hooks and the autocompact env come from the MAIN checkout's
   settings.json; a stale one means no meter and a larger window (WORKERS.md rule 5). Budget sharing is mts_signal text. Fix:
   `sync.py start` verifies the hook and env lines exist and prints a loud warning if not.
11. LOW (OLD) stop_guard stores one session (stop_guard.py:53), so alternating sessions repeat the same block; bounded by
   stop_hook_active (:68), ~150k per extra block. Fix: keep the last 50 sessions in the dict.
12. LOW (NEW) `turn_meter.py status` flags OVER by raw counts (:306), ignores driven/role/events; the operator's view can miss runaways.
   Fix: add those columns.
Never blocks a typed prompt: confirmed, handle() only returns text.
Do first: 1 (events counter + send rate), 2 (driven expires), 4 (Supervisor wake gate), 5 (child count).
