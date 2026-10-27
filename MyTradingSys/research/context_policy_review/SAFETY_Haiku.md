# Safety review, Haiku (round 2, revised)

Read SAFETY_Sonnet.md and SAFETY_Opus.md. Checked in code this round: USER_CAP is dead (turn_meter.py:32, 217, 224-225, 232); EVENT_PROMPTS includes "<system-reminder" (:172); model_guard SKIP_PREFIX lacks cross-session and ci-monitor tags (model_guard.py:179); Workflow is not in the hook matcher (.claude/settings.json:100). Tests not rerun here: Sonnet 26+7 passed, Opus 33 passed.

1. HIGH. Walk-away driven session gets no tool-turn nag. Lines 217, 224-225, 263. Agrees with Opus 2 and Sonnet 2. Fix: in PostToolUse only, drop driven after N tool turns or 30 min since the last typed prompt.
2. HIGH. Event prompts are never counted (:211-215). Agrees with Sonnet 1 (200 simulated prompts, counters 0). Adds: a prompt starting "<system-reminder" also escapes counting (:172, Sonnet 9).
3. HIGH. Fable has no cap at all (:224, :263). Agrees with all three. Fix: unattended Fable gets a context note at 500k; driven Fable stays free.
4. HIGH. Supervisor capped by context only, and only by a nag (:226-228, :266-268). Agrees with Sonnet 4 and Opus 4. Adds Sonnet 8: unreadable transcript returns context 0 (:148, :161), so no cap applies at all.
5. HIGH. Fan-out is unbounded. Subagent starts are not counted (model_guard.py:226-231). Agrees with Sonnet 5. NEW from Opus 6: Workflow is not in the matcher (settings.json:100), so a workflow's agents can pick Opus.
6. HIGH. NEW from Opus 1: a child's message naming Opus or Fable unlocks Opus or Fable spawns, because SKIP_PREFIX (model_guard.py:179) lacks cross-session and ci-monitor tags. Opus says its test returned True; I did not rerun it. Fix: add those prefixes and every EVENT_PROMPTS entry.
7. MED. Subagents skip every hook (:201). Agrees with Sonnet 6 and Opus 6. Fix: count Agent calls per parent in PreToolUse.
8. MED. The typed-prompt cap (USER_CAP=10) is dead code. Driven starts at the 2nd prompt (:217), so the check at :232 never runs for a session past its 2nd prompt. Fix: delete it, or show the count in `status`.
9. MED. Hook errors are swallowed (:288-295) and a failed save stops metering (:276). Agrees with Opus 7. Fix: write a visible failure flag that `status` and the doctor report.
10. MED. /clear and each new session id start from zero (:239-240). Stop_guard keeps one session only (stop_guard.py:53, Sonnet 11). Fix: budget per login per day, in a file that outlives sessions.
11. MED. Three devices, three meters (home() at :41-42). Agrees with Sonnet 10 and Opus 8. Opus says the main checkout is 1858 commits behind; I did not check that. Fix: a daily total per login, plus a check that each machine's meter matches trunk.
12. LOW. State older than 7 days is pruned (:72). Agrees with Opus 10. Resumed sessions restart at zero.
13. LOW. Sticky Supervisor role from a prompt starting "you are supervisor" (:190-193, :221-223). A worker that starts that way gets uncapped treatment. Fix: match only the start line in SUPER_SESSION.md.
14. LOW. `MTS_TURN_METER=off` silences everything but the operator count (Opus 10). Operator-set, so low.
15. DISPUTED. stop_guard blocks once and cannot loop (Opus 11). Sonnet 11 says alternating sessions repeat the block, about 150k per extra block. The one-session store (stop_guard.py:53) supports Sonnet. Not resolved here.
16. Withdrawn from round 1: nothing. The round-1 count of 11 items stands, with the subagent item merged into item 7 and the Opus and Fable items added above.

Fix order (typed prompts never blocked): 6 (prefix list, small), 2 (events counter, rate limit on send_message), 1 (driven expiry), 5 (child count and Workflow in matcher). Then 3 and 4 as notes.
