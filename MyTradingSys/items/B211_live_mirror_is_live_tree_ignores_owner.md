# B211 - live_mirror.py is_live_tree ignores the live owner

Filed: 2026-10-31 by DSA on JIS-NB.
Status: OPEN
Priority: HIGH
Fixer: Claude
Logger: Claude

## What happened

`is_live_tree()` at scripts/dev/live_mirror.py:120-121 reads only the `.mts_live` marker.
JIS-NB kept that marker after the loop moved to the Lenovo.
So JIS-NB published its own stale tree to the shared mirror and overwrote the Lenovo copy.
`pull` then refused because the script thought JIS-NB owned the live data.

## Fix

`is_live_tree()` returns True only when the marker exists AND `resolve_owner()` names this host.
A marker on a host the owner file does not name is stale: report it, do not trust it.

## Test

Build a temp repo with `.mts_live` and an owner marker naming another host.
Assert `is_live_tree()` is False and `pull` proceeds.
