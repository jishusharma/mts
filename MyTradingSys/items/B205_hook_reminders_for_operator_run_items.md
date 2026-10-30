# B205 - Hook reminders for operator-run items repeat every turn and after every compaction even after the session acke

Filed: 2026-10-26
Status: OPEN
Priority: MED
Fixer: Claude
Logger: Claude

## Row (verbatim from BUGS.md)

| B205 | 2026-10-26 | OPEN | MED | Hook reminders for operator-run items repeat every turn and after every compaction even after the session acked `told`: b-4c2dfe, b-3ee970, b-1fdd2e, b-4053da, b-2a5b44 are things this session cannot run (primary checkout / other machine), yet each prompt carries 10 broadcast status lines plus 5 HIGH reminders. In a live-market thread this is noise that crowds out the chart. Fix: a told-with-blocker ack mutes the reminder for this host for 24 h, and the broadcast status list shows only items addressed to this host. | UserPromptSubmit / SessionStart hook output on every turn 10-26 evening | |
