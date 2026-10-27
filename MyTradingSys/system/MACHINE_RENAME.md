# Machine rename (operator steps, quiet time only)

DECISION (OURS, operator 2026-10-25): JIS-NB becomes **JIS-DESKTOP** (the desktop tower), DESKTOP-F7IU69N becomes **JIS-LAPTOP**
(the Lenovo laptop), JIS-NUC stays. The repo already works under the old and the new name: one table in `scripts/dev/hosts.py`
maps every old name to the new one, so signals, acks, owner files, claims and `JIS-NB/...` branches written earlier keep matching.
Nothing here is urgent and no script renames a machine: you do it, one machine at a time, never both in one hour.

## Desktop (JIS-NB -> JIS-DESKTOP)
1. `cd C:\MTS\mts-jisnb; Rename-Computer -NewName JIS-DESKTOP -Restart` (admin PowerShell).
2. After the reboot run the checks below.

## Laptop (DESKTOP-F7IU69N -> JIS-LAPTOP): the testnet live loop runs there
1. Stop the loop the way DEPLOY_RUNBOOK.md says (section 2 restart rules; flat book preferred): `mts stop`, then
   `cd C:\MTS\mts-live; python scripts/dev/live_owner.py release` (or wait 180 s for the owner heartbeat to go stale).
2. `cd C:\MTS\mts-live; Rename-Computer -NewName JIS-LAPTOP -Restart`.
3. After the reboot, start the loop again per DEPLOY_RUNBOOK.md / LIVE_HOST_MOVE.md (`mts start`), then run the checks below.

## Checks after each rename
- `$env:COMPUTERNAME` shows the new name.
- `cd C:\MTS\mts-jisnb; python scripts/dev/mts_signal.py who` lists the machine (the old name's earlier lines count as the same host).
- `python scripts/dev/live_owner.py check` prints ok (an owner file written under the old name still matches).
- The NUC reaches the share: from the NUC, `Test-Path \\JIS-DESKTOP\MTS-Queue` (the old `\\JIS-NB\MTS-Queue` stops resolving after
  the rename; shares and saved credentials that name the old host need the new name once). Code tries the new name first and the
  old one as fallback (`hosts.unc_path`).

## Roll back
`Rename-Computer -NewName JIS-NB -Restart` (desktop) or `-NewName DESKTOP-F7IU69N` (laptop). The repo works under either name, so
nothing else needs undoing.

## Known leftovers (not renamed on purpose)
Card lane names and desk targets (`JIS-NB`, `DSA-NB`), `traffic_inventory.json` machine keys, device names in wt_maint task names,
and old hand-over history keep the old spelling; they are labels, not machine checks. Move them later, one at a time, with a test.
