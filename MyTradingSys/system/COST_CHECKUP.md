# Cost checkup (COST, separate from AI health)

Purpose: a regular checkup for hidden costs we still pay and how to cut them. This is NOT the AI health checkup (mts_doctor, MTS_DOCTOR.md). Operator ask 2026-10-30 (verbatim): "Yeah, I need you to compare the readings. I need to know hidden costs that I'm still paying and how we can still economize it. So there should be a regular checkup for this. Maybe something could be told to doctor MTS doctor about this. Or in AI health checkups, we can keep these things in mind. But these are separate from AI health. Because this is about cost saving."

Who runs it: MTS doctor, as a separate section `COST` of its report (proposed, not wired), or Supervisor on request.

Method: take `mts_signal.py budget --login <A|B|C> --five <%> --week <%> --reset <UTC>` before and after each change; compare burn per hour at the same activity level. Record the readings in the COST section.

## Checklist (each run: measure, then cut)

| # | Hidden cost | How to measure | What to cut |
|---|---|---|---|
| a | Remote Control default for new sessions (OFF since 2026-10-30 ~08:36Z) | `get_settings` / session list: count sessions with remote control on | Keep OFF; turn on per session only when needed |
| b | prompt_suggestions setting (ON; each suggestion = one extra model request) | `get_settings`; count suggestion calls per session | Turn OFF unless the operator wants them |
| c | Runaway background-task output files and loops (e.g. 745 MB `b4nh1sdle.output` in the opus-picture-review-5bd04c worktree temp tasks folder, from a `git log --grep` Bash loop) | List `*.output` under worktree temp task dirs by size; check for loops in session transcripts | Stop the loop; delete the output; cap output size |
| d | Idle sessions holding background work or large context | `list_sessions`; flag idle sessions with background shells or big context | Archive done sessions; stop idle background work |
| e | Opus/Fable where Sonnet/Haiku would do | Count Opus/Fable sessions per week vs task type (WORKERS.md) | Move routine work to Sonnet or Haiku |
| f | Agent fan-out token use per task | Count Agent calls per task card; tokens from `get_usage` before/after | Cap waves at 4; one Agent per real need |
| g | Stale scheduled tasks and headless wakes (failed MTS-SuccWake-C) | `list_scheduled_tasks`; check for failed or repeating wakes | Delete or retire stale tasks; keep no wake without an owner |
| h | Context cost per session (system tools ~41k + MCP tools ~18k tokens) | Count loaded MCP servers and skills at session start | Disable unused MCP servers and skills |
| i | Keep-awake settings | `get_settings`; host keep-awake state | Turn OFF when no run needs the machine awake |

## Baseline (login C)

| Reading (UTC) | 5h | Week (all models) | Week (Fable) |
|---|---|---|---|
| 2026-10-30 02:17 | - | 28% | 11% |
| 2026-10-30 08:37 | 17% (resets 12:49) | 30% (resets 11-03 20:00) | 12% |

## Output of each run

One table: item, reading before, reading after, change made, estimated saving. Then one line on the next cut. Nothing here is a schedule; runs happen when the operator or the doctor asks.
