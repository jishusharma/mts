# Rolling sessions: measured cost comparison (card rolling-session-cost-comparison, 2026-10-28)

Decision d-measure-rolling-cost (OPERATOR_DECISIONS.md): how long do rolling Supervisor sessions run before data use hurts, and what did past issues look like. Method: committed logs, pilot reports and audits only (grep, no transcripts read, nothing run live). The tables below are printed by `build_table.py` in this folder; each row's source is `file:line`, found by the script from an exact quote (a missing quote stops the run), so the citations cannot drift from the files. Missing cells are NOT_IN_DATA.

## Answer (plain words)

| Question | Measured answer | Basis |
|---|---|---|
| Fixed cost of any session | About 70-75K tokens before the first prompt (median 71.6K over 38 sessions, 74.8K over 134 in 7 days); 57% of all re-read context is this base | Table 2; issue 4 |
| When does a coordinator's context start to hurt | Cost per turn is context re-read at every turn. Past about 200 turns a session costs disproportionately: 10 of 134 sessions over 200 turns used 39% of all context. Compaction paid back best at 220-280K (4.4-4.5x its cost), and lost money when done early (170K) or right before a session ended | Issues 1, 4 |
| Where the repo's own rule sits | D5 rotates an unattended coordinator at about 200K; supervisor.py hands over at 150K or after a 3 h wave (OURS, overlap not reconciled) | Issue 11 |
| What actually ended recent rolling chains | The 5 h plan window, not context: the 2026-10-27 chain was at 94% of the window with about 12% context | Issue 10, Table 1 |
| Run length seen | 14 min (pilot 3) to 4 h (pilot 1b) for measured coordinators; the chain ran 5 links per 5 h window; individual links p50 5 min, p90 34 min | Table 1, issue 13 |

Reading: for rolling coordinators the binding limit has been the 5 h window and the ship tail (gate, push races, CI wait), not context size. Context becomes the problem only for sessions that run for hours without rotating (cache misses on idle waits, about 14% of all cost) and for attended operator chats that go past 200 turns.

## Gaps (cannot be answered from committed data)

| Missing | Why | What would fill it |
|---|---|---|
| Turn-meter output | `turn_meter.py` was removed on 2026-10-24 (43d3bfc8f); no committed turn-meter log exists | none needed; the hook is gone |
| Supervisor heartbeats | The only committed heartbeat files are position-manager ones (`execution/pm_heartbeats/`), not Supervisor sessions; `sup=` heartbeat is read live by traffic.py, not stored | a snapshot job (no schedulers allowed), or the next chain writing context per wake into its notes file |
| Per-link context and budget % for the 2026-10-27/28 chain | Only the end state of link 5 is recorded | the coordinator logging `get_usage` at each wake via `usage_log.py row` |
| Compaction count per rolling session | The audits count fleet-wide (70 + 20 + 12 events), not per coordinator | `context_gap.py measure` run over transcripts on the machine that holds them (numbers only) |
| Whether the Max limits weigh cache reads like API prices | NOT FOUND in Anthropic docs (context_cost_2026-10-24.md) | none from the repo |

DECISION (OURS): the 200K and 150K lines are the repo's existing numbers, not new ones; this report proposes none. The 220-280K sweet spot is from COMPACTION_REPORT_2026-10-16.md (modelled cost, not billed).

## Table 1: past rolling and long coordinator sessions (NOT_IN_DATA = no committed number)

| Session | Role / login | Run length | Context at start | Context at end or peak | Budget spent | Compactions | Source |
|---|---|---|---|---|---|---|---|
| Rotation-test stand-in coordinator (local_1d839155) | Sonnet coordinator, login C, JIS-NB | 2 task turns + 5 rebuild model calls | 69K | 75K before clear; 72K after rebuild | NOT_IN_DATA | 0 compactions, 1 clear_session | research/mts_doctor/ROTATION_TEST_2026-10-24.md:21; research/mts_doctor/ROTATION_TEST_2026-10-24.md:22 |
| Pilot 1b coordinator | Sonnet coordinator, login C, JIS-NB | 4 h (14:28Z-18:30Z) | 109K after 10 min | NOT_IN_DATA | 5 h window stayed under 80% (PASS, no figure) | NOT_IN_DATA | research/mts_doctor/PILOT1B_NOTES.md:1; research/mts_doctor/compaction_long_runs_2026-10-24.md:27; research/mts_doctor/REPORT_pilots_2026-10-25.md:12 |
| Pilot 2 coordinator (6 workers) | Sonnet coordinator, login C, JIS-NB | about 2 h (18:48Z-20:50Z, ended early) | NOT_IN_DATA | 232K and 250K (two hand /compact, to 93K and 97K; which pilot is not stated) | 5 h window 13% -> 42%; week 34% -> 38% (whole fleet) | 2 manual /compact | research/mts_doctor/REPORT_pilots_2026-10-25.md:12; research/mts_doctor/REPORT_pilots_2026-10-25.md:21 |
| Pilot 3 supervisor (pilot3_sup, Haiku workers) | Sonnet supervisor, login C | 14 min (05:46Z-06:00Z) | NOT_IN_DATA | 127K at end | 5 h 3% -> 7%; week 44% -> 44% | 0 | system/handoff_history/PILOT3_RESULTS.md:17; system/handoff_history/PILOT3_RESULTS.md:17 |
| Rolling chain links 1-5 (local_37a9ec3e), 2026-10-27 | Coordinator chain, DESKTOP-F7IU69N | 5 links in one 5 h window; wall time NOT_IN_DATA | NOT_IN_DATA | about 12% (of the window; absolute tokens NOT_IN_DATA) | 5 h window 94% (about 1h06m left); week 40% | NOT_IN_DATA | system/NEXT_SESSION.md:40; system/SUPER_SESSION.md:54 |
| Rolling chain links 6-9, login A, 2026-10-27/28 | Coordinator chain, DESKTOP-F7IU69N / JIS-LAPTOP login A | 4 links; closed by operator, stopped before the 5 h window ran out | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | system/NEXT_SESSION.md:42 |
| Supervisor C, Krown session (528eee96), 2026-10-22 | Supervisor, login C, JIS-NB | 93 min (22:06Z-23:39Z) | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | research/mts_doctor/AUDIT_SUPER_C_2026-10-23.md:1; research/mts_doctor/AUDIT_SUPER_C_2026-10-23.md:15 |

## Table 2: fleet aggregate from context_gap_runs.jsonl (one run; main-thread sessions with 5+ turns)

| Sessions | First-turn context median (min-max) | Full cache rewrites (sum) | Sessions with a rewrite | Source |
|---|---|---|---|---|
| 38 | 71553 (69029-74681) | 58 | 10 | research/mts_doctor/context_gap_runs.jsonl:1 |

## Table 3: past issues

| # | Issue | Source |
|---|---|---|
| 1 | Compactions that lost money: 39 of 70 (56%) before the 10-15 audit; 3 of 20 (15%) after, once they ran at about 268K | research/_archive/loose_2026-10/COMPACTION_REPORT_2026-10-16.md:14 |
| 2 | 10-15 audit: 68 compactions, 39 lost work because state lived only in the context | system/SUPER_SESSION.md:14 |
| 3 | Mid-session cache misses: 126 in 7 days over 134 sessions, about 14% of cost (a long idle wait rebuilds the whole history at 2x) | research/mts_doctor/context_cost_2026-10-24.md:21 |
| 4 | Context bloat: 10 of 134 sessions ran over 200 turns and used 39% of all context; the first-turn base (about 75K) is 57% of re-read context | research/mts_doctor/context_cost_2026-10-24.md:15 |
| 5 | Auto-compact percent override does not work on current versions (GitHub #63186 closed, #82761 compactions at 370K-828K); the old 25/12 setting may never have worked | research/mts_doctor/compaction_long_runs_2026-10-24.md:21 |
| 6 | A stale main-checkout settings.json forced about 250K compaction on every model | system/WORKERS.md:33 |
| 7 | Opus: 43 of 46 compactions were manual; Fable session c11be9cb took 84 operator prompts and 13 compactions | research/context_policy_review/REVIEW_OPUS.md:7 |
| 8 | clear_session refused 3 times while a wake, ship or Remote Control was live; rotation in pilot 2 needed the operator | research/mts_doctor/REPORT_pilots_2026-10-25.md:21 |
| 9 | Early end by a hook: the turn meter cut Supervisor C 4 s after it tried to spawn the Krown Builder (turn_meter removed 2026-10-24, 43d3bfc8f) | research/mts_doctor/AUDIT_SUPER_C_2026-10-23.md:15 |
| 10 | Chain stopped by the 5 h plan window, not by context (context about 12% when the window was at 94%) | system/SUPER_SESSION.md:54 |
| 11 | Two hand-over triggers overlap: transit at 150K context or a 3 h wave (supervisor.py) versus D5 rotation at about 200K and D6 24 h runs | research/lead/2026-10-28_rolling-super-sessions-per-station.md:53 |
| 12 | Agents report no per-worker context, so Pilot 3 context was NOT MEASURED; only subagent token sums exist | system/handoff_history/PILOT3_RESULTS.md:7 |
| 13 | The ship tail, not the work, sets a link's length: worker Agent link p50 5 / p90 34 / max 181 min over 255 links | research/lead/2026-10-28_rolling-chain-link-latency-levers.md:10 |

Reproduce: python MyTradingSys/research/rolling_session_cost_2026-10/build_table.py (exit 0 = every source quote found).
