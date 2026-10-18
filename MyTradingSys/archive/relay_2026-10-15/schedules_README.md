# Scheduled task prompts (reference copies)

Purpose: version the prompt text for scheduled tasks so their content lives
in git and can be audited. F6 decision 2026-10-07, from the wiring audit
(2026-10-01) root cause 4: protocol definitions outside git.

Reference copies live here. The live text lives inside the Claude App
scheduled task configuration. When the live task changes, refresh the copy
here and note the date in the file header.

Claude App scheduled tasks with prompt text (both decommissioned, not registered; archived 2026-10-15):
- mts-hourly-builder-check -> hourly-check.md
- mts-dsa-feeder -> dsa-feeder.md

Windows Task Scheduler tasks without prompt text:
- MTS-Scheduler-Tick (scripts/sched/tick.py)
- MTS-Feed-Watchdog (scripts/live/feed-watchdog.ps1)
