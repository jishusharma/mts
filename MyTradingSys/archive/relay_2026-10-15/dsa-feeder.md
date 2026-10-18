# mts-dsa-feeder - reference copy

Status: reference stub. Live task text not yet exported from Claude App
settings. Refresh from the App scheduled-task configuration when the task
changes.

Purpose per WIRING_MAINTENANCE_AUDIT_2026-10-01 section 2 row 2:
gates DSA replies, packs the next backlog item (DSA_BACKLOG.md rules,
specs, backtest drivers). One Haiku per 2h tick in the original design.

Last known firing: 2026-09-30 02:38 IST (HOURLY_CHECK_LOG.md).
Disabled at the weekly cap 2026-09-30. B080 pace bug also stalled the
dsa_worker at that time.
Archived 2026-10-15: task not registered; the resume rule left SURFACE_POLICY.
