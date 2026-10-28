# B137 - Device roles undecided after Qwen NUC lane decommission

Opened 2026-10-06. Status OPEN.

## Problem
The Qwen NUC lane was decommissioned 2026-10-01 (CLAUDE.md work routing). The role split between desktop, NUC and laptop has not been decided since. There are 11 open questions on that split.

## Open questions
1. Laptop: specs, OS, role (Claude surface, second backtest worker, or spare).
2. Third-device session ("NUC project"): which device, still alive?
3. NUC code sync: today a manual zip via NUC-QUEUE\bt_stage; want an automated pull (git bundle or scheduled robocopy), and who owns it?
4. Desktop firewall blocks inbound HTTP, so any LAN pull needs the share; admin needed to change.
5. Moving the live system's working tree to F: needs a supervisor-owned restart window (auto_trader, live_runner_cli, orderflow_live, htf_context_live, daily_loss_monitor and the 2 mvn feeds run from the C: tree).
6. Which backtests are NUC-eligible (tom_bt rows/fabio/report; bt/ ladder; layers/run_t055) vs desktop-only.
7. NUC Ollama models (F:\ollama, ~38 GB: qwen3.6:35b, qwen3-coder:30b): keep or delete now Qwen is decommissioned.
8. NUC power: manual on/off today; allow BIOS auto-power-on for unattended batch runs?
9. System Restore / shadow storage on desktop C: unverified (needs admin `vssadmin list shadowstorage`).
10. Claude vm_bundles 11.6 GB on desktop C: clear or move?
11. Remote Desktop to the desktop: still NOT SET UP.

Source: research/BUGS.md row B137 (2026-10-06). Done already: NUC has Python 3.14.6 and a repo+data copy under F:\MTS; system/DEVICES.md rewritten.

## Decisions landed (2026-10-10, read on JIS-NUC)

Q2 third device: the laptop joined 2026-10-06 06:02Z (DEVICES.md sec 10). Decided.
Q3 NUC code sync: DEVICES.md sec 5 (2026-10-07); fast-track on GitHub is the hub, every work tree ships with scripts/dev/sync.py ship. Decided.
Q6 NUC-eligible backtests: DEVICES.md sec 7 PROPOSED - backtests that read only committed code plus F:\MTS\data. Desktop-only: anything reading live runtime state, Maven feeds or testnet. Awaiting operator confirmation.
Q7 NUC Ollama models: deleted 2026-10-06 (DEVICES.md sec 7); ollama list empty on JIS-NUC. Decided.

## Operator-owed (no decision on disk)

Q1 laptop specs/OS/role: DEVICES.md sec 8 PROPOSED.
Q4 desktop firewall inbound HTTP: admin change; no decision.
Q5 live-tree move to F:: needs supervisor restart window; none scheduled.
Q8 NUC BIOS auto-power-on: operator keeps manual control.
Q9 desktop C: shadow storage: needs vssadmin list shadowstorage by admin.
Q10 Claude vm_bundles 11.6 GB: DEVICES.md sec 6 PROPOSED keep.
Q11 Remote Desktop to desktop: NOT SET UP (DEVICES.md sec 4).

## Done when
Each question has a recorded decision (or an explicit WONTFIX), and CLAUDE.md / SURFACE_POLICY.md reflect the resulting device roles.
