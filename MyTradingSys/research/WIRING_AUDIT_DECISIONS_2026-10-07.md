# Wiring audit decisions - 2026-10-07

Source: WIRING_MAINTENANCE_AUDIT_2026-10-01.md (F1-F7 proposals).
Operator decisions taken 2026-10-07. Each decision carries the operator
verbatim words.

## Operator standing order (verbatim)

> why these questions exists for me? of course claude must decide decide these based on the task objectives. Since claude a full access from user Claud must try to finish the tasks instead of holding them. find the right solution and use default ones that are aligned to the task objectives!!!

> See all these are obvious choices based on why the task was worked upon in the first place! Claude must be able to do it going forward!

> Useless dependency on Jishu after Claude has been asked to already take decisions to keep CI CD going and trades being tested on test-net - all layers firing!

> If u are flagging it then why not already do it the default correct task oriented implementations an then flag later man!!!!!!!!

Recorded into DSA_SESSION_PROMPT.md section 5d. Standing rule: for any task
with a clear task-aligned default, DSA and CC pick the default and execute.
Flag after, not before. Ask only when no clear default exists, or the call
belongs to the operator (trading direction, orders, budget where no number
was supplied).

## Decisions

### F1 - Windows Task Scheduler runs the T0 set daily
Decision: A, schedule all six (make_status.py, audit_rotation.py --t0,
audit_digest.py, testnet_status.py, alert_rate_check.py,
declutter_backups.py dry-run).
Operator verbatim: "A. Schedule all six."
Status: operator runs the schtasks block; DSA composes it.

### F2 - Resume rule in SURFACE_POLICY
Decision: recast. Resume is tied to loop state, not the weekly reset.
Operator verbatim: "my stem be be manually shutdown regularly - so it makes sense to start these when loop is on and when we are actively working."
Status: applied to SURFACE_POLICY.md section 3.

### F3 - One inbox
Decision: A, COORD reads SUPERVISOR_INBOX.md at boot. Exact shape is
DSA-chosen.
Operator verbatim: "this seems right to me but i am not sure so let clause decide what works best!"
Status: applied as new boot step 12 in DSA_SESSION_PROMPT.md section 3.

### F4 - mts status reports live_runner_cli and orphan_watchdog_cli; add mts runner
Decision: A, both.
Operator verbatim: "obvious choices based on why the task was worked upon in the first place! Claude must be able to do it going forward!"
Status: handed to a CC session (needs test run).

### F5 - Commit execution/{plans,journal,halt_history}/.gitkeep
Decision: A, commit the three files, unignore specific paths.
Operator verbatim: "Same story! Obvious choices! User does not know what Claude has worked upon and what is needed."
Status: handed to a CC session.

### F6 - Version the scheduled-task prompts
Decision: A, copy both prompts into scripts/schedules/.
Operator verbatim: "Same story - trivial decision wasted time!!!!!!!"
Note: SKILL.md and the dsa-feeder prompt are not in the repo. Reference
stubs created; live text must be exported from Claude App settings.
Status: scripts/schedules/ created, three reference files written.

### F7 - Retire 06_SESSION_END_CHECKLIST / 02c
Decision: point them at the session record.
Operator verbatim: "If u are flagging it then why not already do it the default correct task oriented implementations an then flag later man!!!!!!!!"
Status: superseded header added to both files.

# END