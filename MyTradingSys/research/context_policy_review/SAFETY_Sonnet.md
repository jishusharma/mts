# SAFETY review - Sonnet, round 2 (revised after reading Haiku and Opus; tests 26+7 passed, own simulation)
Base fact (all three agree): no cap in turn_meter.py blocks anything. Every cap is a nag the model may ignore (turn_meter.py:228,233,267,270).
Hard limits that exist: model_guard (which model starts) and the plan window. "Bounded before" meant "asked nicely before".
No typed prompt is ever blocked: handle() only returns text. Confirmed.

1. HIGH (NEW from Opus, I missed it, verified) A child's message unlocks Opus/Fable spawns. model_guard.py:179 SKIP_PREFIX lists
   system-reminder, task-notification, side-sessions-event but NOT <cross-session-message or <ci-monitor-event, which turn_meter.py:172
   already treats as events. A worker report naming "Opus" reads as the operator naming it (:206-233). Fix: share one prefix list; fail-first test.
2. HIGH (OLD+NEW) Event ping-pong: events never counted (turn_meter.py:185-188, return :215). Sim: 200 cross-session prompts, counters 0.
   model_guard.py:114-145 checks target ownership only, no rate (Haiku #2 agrees). Fix: events counter, nag past ~30/hour; send_message rate limit.
3. HIGH (all three agree) "Driven" is set by count alone (:217), sticky, cleared only by an event prompt (:212-214). Two prompts then walk
   away: 100 tool turns, 0 nags (sim). Fix: PostToolUse drops driven after N tool turns / ~20-30 min since last typed prompt. Typed prompts untouched.
4. HIGH (all three agree) Fable: no cap, no nag (:224,:263). Fix: unattended Fable gets the Opus-style context nag; driven stays free.
5. HIGH (all three agree) Supervisor: context-only nag at 500k (:226-228,:266-268); compaction hides size (:146; Haiku adds compaction is not
   counted, :241-246). Sim: 300 tool turns, 0 nags. Fix: hourly/150-turn "run get_usage, stop on THROTTLE" nag; Opus's cumulative
   read budget (sum of ctx per turn, note at ~40M) is better than a turn count: adopt it.
6. HIGH (OLD) Fan-out unbounded: the "4-session cap" is prose (no script enforces it). model_guard.py:226-231 allows any number of cheap
   start_session/Agent calls. Fix: PreToolUse count of children per parent, deny above 4 (tool call only).
7. MED (all three agree) Subagents skip every hook (:201), parent sees one tool turn. NEW from Opus, verified: settings.json:100 matcher
   has no Workflow, so workflow agents can pick any model. Fix: add Workflow to the matcher; require a turn limit in Agent prompts.
8. MED (NEW from Opus, unverified) Plain-text wake-ups (ScheduleWakeup, /loop, <<autonomous-loop>>, scheduled triggers) count as typed
   prompts, so a session is driven after the 2nd and never nagged. I did not trace one into the hook. Fix: PreToolUse deny on
   scheduling tools (SCHEDULING_POLICY says none) and treat those prefixes as events.
9. MED (NEW from Haiku) USER_CAP (:232) is dead code once driven=1 (:217,:224). I had it as "nag-only"; it never fires at all. Delete it or
   show it in status.
10. MED (NEW from Haiku/Opus) Fail-open: hook() swallows all exceptions (:288-295) to hook_errors.log; a failed save (:276) silently ends
   metering. Fix: visible failure flag in `status` and the doctor.
11. MED (mine) Unknown context = no cap: ("",0) on unreadable transcript (:161,:164) or postTokens 0 (:148) skips scaling (:230,:261). Fix: assume 250k, log.
12. MED (mine) Three devices: state per machine (:41-42), no account-wide total; hooks come from each checkout's settings.json (Opus: main is
   1858 commits behind). Fix: `sync.py start` verifies hook+env lines; doctor compares turn_meter.py to trunk. Haiku #8 (budget resets on
   /clear and new session id) is the same gap: per-login daily file.
14. DROPPED my round-1 #7 (PostToolUse deny after 3 ignored nags): contradicts "model never told / never blocked" direction and Haiku's
   better pattern: block the Stop once via the stop_guard.py:41-80 seen_before pattern. Use that, not a tool deny.
15. LOW stop_guard: I said one stored session repeats blocks (stop_guard.py:53). Opus: blocks at most once per state, cannot loop. Keep as
   cost only (~150k per extra block), fix: dict of last 50 sessions.
16. LOW Haiku #11 sticky Supervisor role matches any prompt starting "you are supervisor" (:193,:221): match SUPER_SESSION start line only.
   Haiku #10 / Opus #10 state pruned after 7 days (:71-78) restarts a resumed session at 0: prune completed only.
17. LOW Opus #7 operator cannot see burn (notices silent by design :86): per-session token ledger in `turn_meter.py status` (which flags
   OVER by raw counts only, :306, my old #12). Never in chat.
Do first: 1 (prefix list, one line), 3 (driven expires), 2 (events counter), 5 (Supervisor budget), 6 (child count).
