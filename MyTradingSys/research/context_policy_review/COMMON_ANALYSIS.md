# Common analysis: unbounded-usage risks (Haiku, Sonnet, Opus, round 2; code 742fd744b, re-checked by me)
Base fact (AGREED, confirmed): turn_meter.handle() only returns text; no typed prompt is blocked. Every cap is a note the model may ignore.
Rule for all fixes: act in PostToolUse/PreToolUse/send_message only, never on UserPromptSubmit of a typed prompt. Lines = scripts/dev/.

## HIGH
1. AGREED (3/3 after cross-read; Opus found it) Child/coordinator message unlocks Opus/Fable spawns.
   Trigger: worker report or "write SAFETY_Opus.md" naming Opus. Guard: model_guard.py:179 SKIP_PREFIX lacks <cross-session-message, <ci-monitor-event (turn_meter.py:172 has them). Fix: one shared prefix list + fail-first test.
2. AGREED Event ping-pong is free. Trigger: parent send_message -> child turn -> side-session note -> parent turn. Guard: events return before counting (turn_meter.py:211-215); model_guard.py:114-145 checks ownership only. Fix: events counter, note past ~30/h; PreToolUse rate limit on send_message per target.
3. AGREED "Driven" never expires. Trigger: 2 typed prompts, operator leaves (:217; cleared only by an event, :212-214). Sim: 100 tool turns, 0 nags. Fix: PostToolUse drops driven after N tool turns or ~30 min since last typed prompt.
4. AGREED Fable has no cap (:224, :263). Fix: unattended Fable gets the Opus-style 500k context note; driven Fable stays free.
5. AGREED Supervisor bounded by context nag only (:226-228, :266-268); compaction keeps context under 500k so it never fires. Fix: note every ~150 tool turns or 2 h ("run get_usage, stop on THROTTLE"), cumulative read budget (Sonnet), supervisor.py plan prints STOP from mts-budget.json.
6. AGREED Fan-out unbounded: "4-session cap" is prose; model_guard.py:226-231 allows any start_session/Agent count. Fix: PreToolUse count of children per parent, deny the tool call above 4.

## MED
7. AGREED Subagents skip all hooks (:201); Workflow absent from matcher (.claude/settings.json:100) so workflow agents can pick Opus. Fix: add Workflow to matcher; count Agent calls/hour.
8. AGREED Fail-open and invisible: hook() swallows exceptions (:288-295), failed save stops metering (:276), notices silent (:86), status shows raw counts (:299-310). Fix: failure flag in status/doctor; token ledger column.
9. AGREED Three devices, per-machine state (home(), :41-42), hooks come from each checkout (main checkout stale per Opus; I did not count the 1858). /clear or new session id resets budget. Fix: sync.py start/doctor compares hooks + turn_meter.py to trunk; daily total per login in a file outliving sessions.
10. AGREED Dead code: USER_CAP check (:232) never runs once driven=1 (:217,:224). Fix: delete or show in status. (Operator intended driven; not a burn.)
11. MAJORITY (Sonnet, Haiku; Opus partly disagrees) Unknown context = no cap: ("",0) on unreadable transcript (:148,:161). Opus: Sonnet/Haiku keep the flat cap (:230 skips only scaling); only Opus tier and Supervisor lose the check. Verdict: Opus is right on scope. Fix: treat unknown as 250k.
12. DISPUTED Plain-text wake-ups (ScheduleWakeup, /loop, scheduled triggers) count as typed. Opus/Sonnet: yes, then driven after 2nd, never nagged. Haiku: silent. My check: is_event_prompt (:185-188) matches only the 5 prefixes in EVENT_PROMPTS (:172); any prompt without one is counted as typed (:216-217). So a plain-text wake IS counted as typed; one wrapped in <system-reminder is an event. What I could not verify: the real hook payload shape for wake-ups (needs a live payload capture). Fix either way: deny ScheduleWakeup/CronCreate/RemoteTrigger in PreToolUse (SCHEDULING_POLICY.md says none exist).
13. DISPUTED "<system-reminder" prefix (:172). Sonnet 9/Opus 12: if his typed prompt arrives with a reminder prepended it is not counted and can un-drive the session (misfire, wrong nags). Haiku: escape from counting. Code: startswith only; a prepended reminder triggers it. Real payload unverified. Fix: strip leading <system-reminder>...</system-reminder> blocks before the prefix test.

## LOW
14. DISPUTED stop_guard blocks once. Opus: at most once per state, cannot loop (stop_hook_active returns "" at stop_guard.py:~60; seen_before returns True for same session+reason). Sonnet/Haiku: alternating sessions repeat it, ~150k per extra block. Code: seen_before keeps ONE session (`d = {session_id: why}`, stop_guard.py:~53): a second session overwrites, so session A re-blocks after B ran. Both true: no loop inside one session; cost across interleaved sessions. Fix: dict of last 50 sessions.
15. AGREED State pruned after 7 days (:72): resumed session restarts at 0. Fix: prune completed only.
16. AGREED Sticky Supervisor role from any prompt starting "you are supervisor" (:190-193,:221-223). Fix: match only the SUPER_SESSION.md start line.
17. AGREED MTS_TURN_METER=off silences all but the operator count; operator-set.
18. DISPUTED Hard deny after ignored nags (Sonnet r1 / Opus 9) vs block the Stop (Haiku/Sonnet r2). Opus: Stop block buys one extra turn only (stop_hook_active). Fix chosen: PreToolUse deny for unattended (non-driven) sessions only; next typed prompt resets.

## Not broken by today's change
- Typed prompts never blocked; tests test_turn_meter.py + test_stop_guard.py pass (Sonnet 26+7, Opus 33).
- model_guard still hard-stops which model starts (Opus/Fable need named operator, apart from item 1 hole) and target ownership/Fable messaging (:165,:170).
- stop_guard still blocks a stop once per session and state.
- Supervisor context cap (500k Opus-tier nag), Opus context cap, Sonnet/Haiku flat tool cap and READ_BUDGET scaling still fire for non-driven sessions.
- Plan-window limit (account level) is untouched.

## Decision needed from Opus
1. Approve PreToolUse deny (tool calls only) for non-driven sessions after N ignored nags, or notes only?
2. Driven expiry value: 30 min or 2x cap in tool turns?
3. Deny ScheduleWakeup/CronCreate/RemoteTrigger outright, given item 12 is unverified?
4. Supervisor budget: 150 turns / 2 h note, or cumulative read budget (~40M)?
5. Child cap 4: deny or note? Per login daily budget file: build now?
