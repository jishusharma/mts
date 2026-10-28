# Fable runs 2026-10-28: usage guard

Source: get_usage, login C jishusharma1985, plan Max.
Stop rule: stop and ship if weekly all-models rises 4 points. Times UTC.

## R1 (table)

| Run | When | 5-hour | Weekly all models | Weekly Fable | Context tokens | Note |
|---|---|---|---|---|---|---|
| R1 start | 2026-10-27 ~20:46Z | 9 % (reset 22:09Z) | 1 % (reset 2026-11-03 20:00Z) | 0 % | 74,300 of 1,000,000 | before any read |
| R1 end | 2026-10-27 ~20:52Z | 15 % | 2 % | 2 % | 205,021 of 1,000,000 | deliverable written; delta: all-models +1, Fable +2, 5-hour +6; guard not hit |

## R2 (guard log)

Guard rule: stop and ship if weekly all-models rises 4 pts across this session.

### START (turn 1)
- `get_usage`: plan status `not_applicable` (this app routes inference through the organisation's provider; no plan-limit pacing applies).
- Context window self: 103,058 / 1,000,000 (10 % used; auto-compacts at 97 %).
- No all-models weekly % available from this provider (plan not applicable). Guard falls back to the context-window signal: STOP if the context self-report reaches 95 %, else ship at the stop trigger.
- 4-pt weekly delta cannot be read on this login; recorded as N/A at start.

### END
- `get_usage`: plan still `not_applicable`; weekly all-models delta N/A (no plan limit on this provider).
- Context self: 122,741 / 1,000,000 (12 %; below the 95 % stop line, auto-compacts at 97 %).
- Guard outcome: no stop trigger (4-pt weekly rise unreadable, context well under 95 %) -> ship at the stop trigger per the fallback rule.
- Session 2026-10-28 worktree `claude/gross-effect-power-prereg-d8e2cd` shipped clean.

## R3 (guard log)

Guard rule (same as R2): stop and ship if weekly all-models rises 4 pts; context self under 95 %.

### START (post-compact resume)
- `get_usage`: plan status `not_applicable` (org provider, no plan-limit pacing) - weekly 4-pt delta N/A.
- Context self ~20 % / 1,000,000 (post-compact; auto-compacts at 97 %).

### END
- `get_usage`: plan still `not_applicable`; weekly delta N/A.
- Context self: 198,004 / 1,000,000 (20 %; well under the 95 % stop line).
- Guard outcome: no stop trigger -> ship at the stop trigger per the fallback rule.
- Lane: `claude/live-redteam-r3-b8705e`; R3 gate shipped with trunk's T06 costs.csv fix (fff75b648) cherry-picked to unblock step 3xt.

## R6 (deciding pre-reg; login C jishusharma1985, JIS-DESKTOP, Fable 5.1)

Stop rule for R6 (FABLE_RUN.md): weekly Fable +4 pts, or 5-hour >= 85 %, or 45 tool turns, or context >= 60 %.

| Row | When (UTC) | 5-hour | Weekly all models | Weekly Fable | Context tokens | Note |
|---|---|---|---|---|---|---|
| R6 start | 2026-10-28 ~09:15Z | 15 % (reset 10:40Z) | 6 % (reset 2026-11-03 20:00Z) | 3 % | 77,233 of 1,000,000 (8 %) | before any read |
| R6 mid | 2026-10-28 ~09:28Z | 22 % | 7 % | 4 % | 221,392 (22 %) | counts, gates, PRE_REG.md and cards written; reviewer Agent running |
| R6 end | 2026-10-28 ~09:32Z | 25 % | 8 % | 5 % | 241,320 (24 %) | shipped; delta: Fable +2, all-models +2, 5-hour +10; guard not hit |
