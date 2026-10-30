# Station disk roll-call, 2026-10-30 00:57-01:13Z (Supervisor A)

Source: `python scripts/dev/station_disk_report.py --send` (read-only). Sizes in GB; `+` = scan hit its 15 s cap.

| Machine | C: free | F: free | Claude data | VM images | Worktrees | Live tree | Temp | java / python |
|---|---|---|---|---|---|---|---|---|
| JIS-LAPTOP (Lenovo, live host) | 406 | n/a | 1.1 | none | 2.2 | 0.6 | 0.3+ | 1 / 7 |
| JIS-NUC (backtest/data) | 76 | 213 | 1.0 | none | 3.8 | n/a | 0.6+ | 1 / 2 |
| JIS-NB (old live host, operator screen) | 28 | 48 | 12.5 | 11.3 (on F:) | 3.5 | 0.9 (`.mts_live`, old tree) | 0.7+ | **0 / 54** |

## Findings
- The Java engine is gone from JIS-NB (java=0); the Lenovo runs it. Only the old `.mts_live` (0.9 GB) is left there.
- VM images exist only on JIS-NB, already moved off C: to F:\ClaudeVM (junction). Not compressed; nobody confirmed.
- C: on JIS-NB went 12.8 -> 28 GB free since 10-24. Biggest C: item there is Claude data (12.5 GB).
- JIS-NB has 54 python processes with no live engine: unexplained, asked C (no answer yet).
- Device tasks on JIS-NB: c-guard-logon, disk-free, no-stray-sched, live-owner-dir DONE; primary-checkout-current and wt-maint MISSING (refresh waits on b-4c2dfe).
- Lenovo and NUC are comfortable. Nothing to clean there beyond the card `station-cleanup-table-stale-after-cutover`.

## Cleanup / dedup candidates (nothing deleted; data deletion is the operator's call)
1. JIS-NB `.mts_live` (0.9 GB): retired old live tree. Delete after the operator agrees and after confirming no runtime files are unique (liq/state backups live on the Lenovo).
2. JIS-NB Claude data (12.5 GB): check which session folders are stale; `c_drive_care.ps1` (DISK_CARE.md) covers it.
3. JIS-NB VM images (11.3 GB on F:): stay on F:; compress only if F: drops under 30 GB (F: has 48 GB free).
4. JIS-NB 54 python processes: list and stop the stale ones (C to do, they are on its screen).
5. JIS-NB refresh primary checkout (2467+ behind, dirty): C's b-4c2dfe; then the SessionStart guard works there.
6. Check twice a day: `station_disk_report.py` from each machine; alert if C: < 15 GB (`device_tasks.py` row disk-free-15gb).
