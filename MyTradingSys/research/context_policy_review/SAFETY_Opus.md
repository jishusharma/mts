# Safety review: Opus (round 1, 2026-10-21, code at 742fd744b)
Tests run myself: test_turn_meter.py + test_stop_guard.py, 33 passed. Read turn_meter.py, model_guard.py, stop_guard.py, both settings.json (identical hooks).
Headline: turn_meter.py can no longer stop anything. Every output is a text note the model may ignore (turn_meter.py:224-233, 263-271),
and since 742fd744b the note says "Never tell the operator" (turn_meter.py:86). The only hard stops left: model_guard (which model a session
or subagent starts on, click cards) and stop_guard (blocks a stop once). No hook caps total tokens, wall-clock or turns.

1. HIGH (confirmed by test): a child's message that names Opus/Fable unlocks Opus/Fable spawns. model_guard.py:179 SKIP_PREFIX lacks
   `<cross-session-message` and `<ci-monitor-event`, so operator_named_opus() (206-233) reads a worker's report "write SAFETY_Opus.md"
   as the operator naming Opus (ran it: True). Stops it: nothing. Cost: an Opus/Fable worker started on no operator word.
   Fix: add those two prefixes (and every turn_meter EVENT_PROMPTS entry) to SKIP_PREFIX; fail-first test. Typed prompts are untouched.
2. HIGH: driven never expires inside one long turn. Two typed prompts, then the operator walks away: driven=1 (turn_meter.py:217), and only
   a new event prompt clears it (212-214). A long turn has no prompts, so tool turns run with no nag at all (263). Before b200b4d85: a nag at
   4M/context turns. Fix: in PostToolUse only, drop driven after N tool turns since the last typed prompt (e.g. 2x the cap) or 30 min.
   Never touches a prompt he types.
3. HIGH (likely, not traced): any prompt without an event prefix counts as typed: wake-ups from ScheduleWakeup / /loop, `<<autonomous-loop>>`,
   scheduled triggers, and probably mcp__ccd_session_mgmt__send_message if it arrives plain (I could not trace one into a recipient).
   From the 2nd one the session is driven and is never nagged again (217, 224). No hook denies ScheduleWakeup/CronCreate/RemoteTrigger,
   and SCHEDULING_POLICY.md is prose only. Fix: PreToolUse deny on the scheduling tools (policy already says none); treat a prompt
   starting with `<<autonomous-loop` or a slash-loop as an event; verify the send_message format.
4. MED: a Supervisor is never bounded. It is metered as Opus (222-223), nagged only at 500k context (227, 266), and auto/manual compaction
   keeps it below that, so it can run for hours. It was unbounded before too. Fix: a cumulative read budget per session (sum of the
   context of each turn, e.g. a note at 40M) plus a wall-clock note. Notes only, so no typed prompt is blocked.
5. MED: Fable has no cap of any kind now (224, 263). Its one-message rule is gone (b200b4d85) and its tool turns were never capped. Brake:
   model_guard denies messaging a Fable session (174) and starting one without an operator word (but see item 1). Fix: item 1, plus the
   cumulative budget note from item 4.
6. MED: subagents and workflows are never metered (is_subagent skip, 201). Workflow is not in the model_guard matcher (settings.json
   PreToolUse), so a workflow's agents can pick Opus. A driven or Fable parent can fan out freely. Fix: add Workflow to the matcher and
   check each agent() model; meter subagents under their own key (notes only).
7. MED: the operator cannot see the burn. Notices are silent by design (86, 246), turn_meter.py status prints counts but not tokens, and
   hook crashes go silently to hook_errors.log (288-295), which means no cap at all. Fix: a per-session token ledger in the state file
   (sum of ctx per turn), surfaced in `turn_meter.py status`, STATUS.md or a page. Never in chat.
8. MED: 3 devices, 3 logins. State is per machine (~/.claude/mts-turn-meter) and there is no account-wide budget. Hooks run from each
   machine's own checkout via $CLAUDE_PROJECT_DIR: the main checkout is 1858 commits behind, and other devices may run older meters or none.
   Fix: the coordinator reads get_usage per worker each wake (SUPER_SESSION already says so); a doctor check that each machine's
   turn_meter.py matches trunk.
9. LOW: Opus workers lost the 150k follow-up block, but it only ever applied to typed prompts; SendMessage was already exempt. No new burn
   from workers.
10. LOW: MTS_TURN_METER=off silences everything except the operator count (198-204); pruned or resumed state restarts at 0 (PRUNE_DAYS 7).
11. LOW: stop_guard (stop_guard.py:41-80) blocks at most once per state and allows the second stop. It cannot loop.
Order to fix: 1, then 2, then 3. All three are small and none of them blocks a typed operator prompt.
