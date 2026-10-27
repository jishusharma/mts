---
name: mts-dispatcher
description: Relay dispatcher, every 10 min (operator 2026-10-14). ONE Bash call decides: TICK NOOP = one-line reply, TICK KICK = this session is the relay.
---
MTS dispatcher (cron, unattended, never ask). No task list, no update_plan or wrap_up, minimal output, read no file a step does not name. Working folder is the live tree: never edit or commit there.
MODEL GUARD (operator 2026-10-14): the model comes only from the routine's App settings (Haiku 5.5). If your model id contains "opus": print `dispatcher: MODEL_WRONG <id>; set Haiku in the routine settings` and stop, no tool calls.
1. ONE Bash call, nothing before it (copies both scripts from origin: the live tree lags; `;` keeps a network blip from hiding the TICK line):
   D="$TEMP/mts_relay"; mkdir -p "$D"; git fetch -q origin fast-track; for f in relay handoff_lint; do git show origin/fast-track:scripts/sched/$f.py > "$D/$f.new" && mv "$D/$f.new" "$D/$f.py"; done; python "$D/relay.py" tick --peer-quiet-min 90
2. `TICK NOOP ...`: reply `dispatcher: <that line>` and stop. No other call.
3. `TICK KICK ...`: you are the relay session: follow the relay_session.md text printed under it exactly.
4. A `HOURLY` line lists extras still due. `refine=REFINE_NEEDED`: MyTradingSys/system/TASK_REFINEMENT.md "Refiner run" step 3, inside ../mts-refiner. `housekeep=yes`: ToolSearch "select:mcp__ccd_session_mgmt__list_sessions,mcp__ccd_session_mgmt__archive_session", list_sessions limit 40, archive_session each session titled "Mts dispatcher" that is not running, not this one, idle over 3 h; no other title.
5. Last line `dispatcher: <TICK line>` plus what step 4 did.
Never start other scheduled tasks. Never kill processes by image name (taskkill /IM python.exe took down live stack 2026-10-10). Never touch live files, HALT files or trades. CLAUDE.md is already in context; do not cat or Read CLAUDE.md.
Output caps (B172): pipe long command output through `| tail -20`, use `--quiet` flags, no `ls`/`head` probes; finish within 15 tool turns.
