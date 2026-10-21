# Safety review, Haiku (round 1)

Read: scripts/dev/turn_meter.py, test_turn_meter.py, .claude/settings.json, stop_guard.py, model_guard.py, WORKERS.md rule 5. Lines are from the worktree copy.
Tests: `pytest MyTradingSys/tests/test_turn_meter.py` = 26 passed. A replay script was denied by the permission system, so items below come from code reading, not a run.

Key fact: turn_meter.py blocks nothing. It only prints text into context (84-86, 244-246, 267-271). No "decision": "block" exists. Every cap is a request the model can ignore.

1. HIGH. Walk-away driven session gets no tool-turn nag. Trigger: operator types 2 prompts and leaves; the session runs for hours. Lines 217, 224-225, 263-264 skip all checks once driven=1. Cost: each turn re-reads the context (100k x 200 turns = 20M tokens). Fix: count tool turns since the last typed prompt; nag or hand off over the cap. Typed prompts reset it and are never blocked.

2. HIGH. Event prompts are free. Trigger: two sessions message each other in a loop, or a CI/cross-session cycle. Lines 211-215 return before any count. model_guard.py 154-175 checks ownership and Fable only, no rate. Cost: unbounded turns. Fix: count events per session per hour; nag over the cap; cap message pairs.

3. HIGH. Fable has no cap at all. Trigger: any long Fable session. Lines 224-225, 263-264. Fable is the costliest model and its context grows without limit. Fix: same unattended ceiling as item 1, plus a context cap like Opus (OPUS_CTX_CAP, line 35).

4. HIGH. Supervisor is capped by context only. Trigger: Supervisor runs for hours under 500k context. Lines 221-223, 226-228: no turn limit. Compaction drops the context below the cap and is not counted (241-246), so the cap never fires again. Cost: every turn re-reads up to 500k. Fix: hourly turn ceiling for unattended Supervisor turns; count compactions and nag.

5. MED. Subagents are not metered. Trigger: Agent or workflow workers spawned in a loop. Lines 89-94 and 201 skip them. model_guard.py decide() (250-276) checks model and initiation only, no count. Cost: unlimited fresh contexts. Fix: count the parent's Agent and start_session calls per hour in PreToolUse.

6. MED. The typed-prompt cap is dead code. After the 2nd typed prompt driven=1 (217) and line 224 passes, so USER_CAP (232) is never reached. A chatty session is never handed off. Fix: delete it or make it a count in the status line.

7. MED. Fails open. hook() swallows every exception (288-295), and a failed save (276) silently stops metering. Trigger: unwritable state dir. Fix: write a visible failure flag that the doctor and `status` report.

8. MED. Budget resets on /clear (239-240) and on every new session id. A loop of spawn and restart gets a fresh budget each time. Fix: budget per login per day, in a file that outlives sessions.

9. MED. Three devices, three meters. home() (41-42) is per machine under ~/.claude; no total is kept across devices or logins. Cost: the shared allowance is not metered. Fix: one daily total per login, read by the supervisor's pacing.

10. LOW. State files older than 7 days are deleted (71-78, called at 247). A session resumed by id after a week starts at zero. Fix: prune only completed sessions.

11. LOW. The sticky Supervisor role (193, 221) fires on any prompt starting "you are supervisor". A worker that starts that way gets uncapped treatment (222-223). Fix: match only the start line in SUPER_SESSION.md.

Direction (no typed prompt is ever blocked): keep the typed-prompt path free; add ceilings counted since the last typed prompt for every model, including Fable and Supervisor; count spawns and events; over the ceiling, block the Stop once using the stop_guard.py seen_before pattern (stop_guard.py 41-80), not text.
