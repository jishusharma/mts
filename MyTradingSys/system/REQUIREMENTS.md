# Operator requirements (his words first, one row each)

Why this file exists (operator 2026-10-28): requirements were unclear from the start and sessions assumed. Rule: when the operator states something new to be done, the session that hears it adds or edits ONE row here in the same turn, reads the row back to him in one line, and takes the stated default for any open point. A requirement is changed only by a newer operator message, never by a session's reading. Status: OPEN (not met), PARTIAL, MET (with proof), CONFLICT (two sources disagree, see Conflicts).

| Id | Requirement (operator's words, trimmed) | Date | Status | Proof / gap |
|---|---|---|---|---|
| R-01 | Rolling sessions must not need any human intervention. Small sessions run one after another. The system handles every pop-up, every button, every stop. | 2026-10-28 | OPEN | Today the successor needs the operator to paste the start line. See C-01 to C-04. |
| R-02 | Requirements are made clear from the beginning; the session reads each new one back and never assumes. | 2026-10-28 | PARTIAL | This file; read-back rule above. |
| R-03 | Do not make him guess trades on candle-only charts (G3 blind marking dropped). He uses his own tools (RSI, CVD, Bollinger, trend lines, structure, divergence, many timeframes). Help wanted: compute indicator logic (Malkan RSI, regular and hidden divergence, all timeframes) so nothing is missed; he confirms or corrects readings. | 2026-10-28 | MET (decision) | Memory operator-no-blind-g3-marking-use-his-own-tools. First task not yet built. |
| R-04 | Never miss a setup across timeframes; keep refining the rules that he could miss. | 2026-10-28 | OPEN | Needs R-03 first task. |
| R-05 | Unfinished gateway worktrees finished and shipped; NUC worktrees out of scope. | 2026-10-27 | MET | Desktop worktrees landed or dropped; trunk CI green. |

## Conflicts found against R-01 (each needs the default below unless the operator says otherwise)

| Id | Sources that disagree | Default taken (OURS) |
|---|---|---|
| C-01 | "No scheduled tasks anywhere" (CLAUDE.md, SCHEDULING_POLICY.md) vs a zero-click successor wake that uses a one-time scheduled task (card one-shot-successor-wake-task-4b2-no-human, research/lead/2026-10-27_successor-wake-design.md) | Narrow, expiring exception for the successor wake only. |
| C-02 | The app shows an approval card on session starts from a pasted brief, an event turn or after compaction; a hook cannot remove it (research/thinker/2026-10-23_requirements_review_opus.md) | Do not rely on start_session for the chain; use the scheduled wake. |
| C-03 | Rotation triggers disagree: 3 h or 150K context (audit proposal), 24 h or 200K (SUPER_SESSION), five-hour loop (supervisor role) | "Small" = one wave of at most 3 h or 150K context, hard stop 4 h. |
| C-04 | Auto-mode permission denials stop an unattended run (seen 2026-10-27: a merge abort, a checkout of theirs, a Builder brief about merging in place) | Briefs use only allowed forms (revert, cherry-pick in a clean tree, copy files); a denial is logged and the card parked, never waited on. |
| C-05 | When the weekly or five-hour cap is reached, the chain has no rule for pausing and resuming | Pause new starts, resume by itself after the reset time. |

Sources: station_c_rolling_audit_20261026/REPORT.md (policy contradictions table), thinker/2026-10-23_requirements_review_opus.md.
