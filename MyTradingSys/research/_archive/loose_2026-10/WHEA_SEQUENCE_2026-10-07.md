# B140 WHEA - revised sequence (after clean SMART)

Session MTS-2026-10-07-1800Z-APP-ANA-whea-step2-decide. Item: items/B140_whea_storport_hdd.md.

## Evidence
Drive internals clean (all critical SMART attrs 0, no error log, PredictFailure False). WHEA still names storahci + this drive every 1-3 days.
So the fault is on the path: SATA cable/port (H1), controller (H2), driver (H3), PSU rail (H4). Drive age (6.83 y) is an independent retirement argument.

## Order (cheapest first, each step gives a distinct signal)
| # | Step | Owner | Cost | Signal |
|---|------|-------|------|--------|
| 1 | Back up D: (D:\MTS_Share, D:\tools, rest) to the SSD or F: | CC script | 0, no downtime | Do first regardless of outcome. Read-only on D:, live loop keeps running. |
| 2 | Short self-test: `smartctl -t short /dev/sda` from an ADMIN shell, then `smartctl -l selftest /dev/sda` after 2 min | Operator (admin) | 0, no downtime | Pass = media/electronics fine; fail = go to step 7. Also run `smartctl -i` elevated to log current link speed. |
| 3 | Baseline: record WHEA count/date and SMART attr 199 (UDMA_CRC) now | CC | 0 | Reference for steps 4-5. Attr 199 rising after a swap = link still bad. |
| 4 | Swap SATA data cable (new, latching) and move drive to a different port (use a 6 Gb/s port on the PCH, not an add-on) | Operator (power off, ~10 min downtime of the live loop; supervisor restarts it) | cable ~Rs 150 | Primary fix. Watch 7-10 days (3+ expected events at the old rate). |
| 5 | Check/replace SATA power connector (different PSU cable, not a Molex adapter) | Operator, same downtime as 4 | 0 | Cheap H4 test; bundle with step 4. |
| 6 | Move D:\tools (JDK, Maven) to the SSD; supervisor restarts the loop once from the new path | Supervisor (restart is theirs); CC prepares the script | 0 | Removes the live system from D: dependency whatever the cause. Do bundled with the step 4 downtime to restart once. |
| 7 | Contingency: if WHEA continues after 4-6 -> test with the drive disconnected for a week (D: contents already backed up); if events stop, drive/port-specific, replace drive (operator purchase). If events continue with no drive, controller/PSU: investigate PSU, Intel RST driver. | Operator decision (purchase, downtime) | drive/PSU purchase | Isolates drive vs board. |
| 8 | Driver: install Intel RST / Intel AHCI driver for H87 (inbox storahci 10.0.19041.3636 on Standard SATA AHCI). Only after 4-6 fail, one change at a time. No vendor driver is installed today; check Windows Update first. | CC investigates, operator approves install | 0 | H3 test. Low prior: inbox storahci is the normal driver for this chipset. |

## Why this order
- Backup first: every later step risks the data and costs nothing.
- Cable+port and power are the likeliest causes, the cheapest, and one downtime window covers both plus the tools move.
- Self-test is free but low information given clean SMART; run it anyway, it needs only an admin shell.
- Driver change changes an untested variable on a live system; last of the free options.
- Replacement only if the swap and SSD move do not stop the events. Drive age alone justifies a spare, not an emergency.

## Operator decisions needed
1. Approve downtime window for step 4/5/6 (loop offline ~10-15 min).
2. Buy one SATA cable (and a spare drive if step 7 triggers).
3. Run step 2 in an admin shell (this session could not self-elevate).

## Done in this session (no hardware)
- storahci 10.0.19041.3636 (inbox); controller Intel 8 Series/C220 SATA AHCI, MSI H87-G43; no vendor AHCI driver.
- Link speed: not readable without admin; Step 1 recorded SATA 3.0, 6.0 Gb/s (negotiated max).
- Short self-test: NOT run (admin required).
