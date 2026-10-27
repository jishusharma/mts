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
