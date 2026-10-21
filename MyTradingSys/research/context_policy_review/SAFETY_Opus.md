# Safety review: Opus (round 2, 2026-10-21, code at 742fd744b; read SAFETY_Haiku.md and SAFETY_Sonnet.md @ 2d0a36409)
Tests run myself: test_turn_meter.py + test_stop_guard.py, 33 passed. All three reviews agree: turn_meter.py blocks nothing, every cap is
a note the model may ignore (turn_meter.py:224-233, 263-271), and the note says "Never tell the operator" (86). Hard stops left: model_guard
(which model starts) and stop_guard (one blocked stop). Nothing caps tokens, wall-clock or turns.

1. HIGH (mine only, confirmed by test): a child's message that names Opus or Fable unlocks Opus/Fable spawns. model_guard.py:179
   SKIP_PREFIX lacks `<cross-session-message` and `<ci-monitor-event`, so operator_named_opus() (206-233) treats "write SAFETY_Opus.md"
   from the coordinator as the operator naming Opus (ran it: True). Fix: skip every turn_meter EVENT_PROMPTS prefix; fail-first test.
2. HIGH (all 3): driven never expires. Two typed prompts, then the operator leaves: driven=1 (217), and only an event clears it (212-214).
   Sonnet simulated it: 100 tool turns, 0 nags. Fix: driven lapses after ~20-30 min with no typed prompt, or after 2x the cap in tool turns
   since the last typed prompt. Checked in PostToolUse only, so a typed prompt is never touched.
3. HIGH (Haiku, Sonnet; I missed it): event ping-pong is free. Event prompts return before any count (211-215); Sonnet's simulation sent
   200 events and the counters stayed 0. Correction to both: a child cannot message its parent. My SendMessage to the coordinator was
   denied by model_guard.py:165 ("not started by this session"). The real loop is parent send_message -> child turn -> automatic
   side-session note -> parent turn -> send again, bounded only by the model. Fix: an events counter, with a note past ~30 per hour
   and a PreToolUse rate limit on send_message per target.
4. HIGH (mine; the others did not see it): non-typed prompts with no event prefix count as typed. Examples: ScheduleWakeup and /loop wakes,
   `<<autonomous-loop`, and scheduled triggers. From the 2nd one the session is driven (217) and is never nagged again. No hook denies
   ScheduleWakeup, CronCreate or RemoteTrigger (SCHEDULING_POLICY.md is prose). Fix: deny those tools in PreToolUse (policy already
   says none). Still unverified: whether mcp__ccd_session_mgmt__send_message arrives with a prefix.
5. HIGH (all 3): Fable has no cap of any kind (224, 263). Fix: when it is not driven, a note at 500k context like Opus; a driven Fable
   stays free. Item 1 closes the unrequested-start path.
6. HIGH (all 3; Haiku and Sonnet rate it higher than I did): a Supervisor is bounded by context only. It is metered as Opus (222-223)
   and nagged at 500k (227, 266), and compaction keeps it below that, so the note never fires. Fix: a note every ~150 tool turns or 2 h
   ("run get_usage, stop on THROTTLE"), and `supervisor.py plan` prints STOP from mts-budget.json.
7. HIGH (Sonnet; I missed it): fan-out is unbounded. The 4-session cap is prose. model_guard allows any number of cheap
   start_session/Agent calls (decide 250-276). Fix: a PreToolUse count of running children per parent, denying start_session above 4.
8. MED (all 3): subagents and workflows are never metered (201). Workflow is not in the model_guard matcher (settings.json PreToolUse),
   so agent() can pick Opus. Fix: add Workflow to the matcher; count Agent calls per hour.
9. MED (Sonnet 7, Haiku direction): nags are only nags. Best hard lever that never blocks a typed prompt: for an unattended session
   past N ignored nags, PreToolUse denies tool calls, and the next typed prompt resets it. Disagree with Haiku's alternative, blocking
   the Stop: it buys at most one extra turn and is then let through (stop_hook_active, stop_guard.py:68).
10. MED (all 3): the operator cannot see the burn, and it fails open. Notices are silent (86, 246), `status` shows raw counts only
   (299-310), and exceptions go silently to hook_errors.log (288-295). Fix: a token ledger (sum of context per turn) plus driven, role
   and events columns in `status`; surface hook errors in the doctor.
11. MED (all 3): 3 devices, no combined total. State is per machine (42). Hooks come from each checkout via $CLAUDE_PROJECT_DIR, and
   the main checkout is 1858 commits behind. Fix: `sync.py start` or the doctor warns when hooks or turn_meter.py differ from trunk;
   a daily total per login.
12. MED (Sonnet 9, partly agree): the `<system-reminder` prefix (172). If his typed prompt reaches the hook with a reminder prepended,
   it is not counted and can un-drive a session. That is a misfire (wrong nags), not a burn. Verify on a real hook payload.
13. LOW (Sonnet 8, partly disagree): unknown context, ctx=0. For Sonnet/Haiku the flat cap of 40 still applies (230 only skips the
   scaling). Only Opus and Supervisor lose their check. Fix: treat unknown as 250k.
14. LOW: USER_CAP is unreachable once driven (Haiku 6; intended by the operator); /clear or a new session id resets the budget
   (Haiku 8; operator action); prune after 7 days (Haiku 10); a "you are supervisor" start line is sticky (Haiku 11);
   MTS_TURN_METER=off; stop_guard keeps one session in its dict (Sonnet 11).
Dropped from round 1: "Opus workers lost the 150k block". That block only ever applied to typed prompts, so it is not a burn.
Fix order: 1, 2, 4 (small, local), then 3, 7, 6, 9.
