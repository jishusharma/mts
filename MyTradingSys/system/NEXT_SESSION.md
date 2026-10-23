# NEXT_SESSION: JIS-NUC unexpected shutdowns

Written 2026-10-23 by a session running on JIS-NUC. Overwrites the previous hand-over, which stays in git history (commit b1d691a0). Everything below was read from this NUC's event log and settings in this session. Nothing on the NUC was changed.

## Task for the next session (one)
Find and fix why JIS-NUC (Intel NUC10i7FNH, Windows 10 22H2) goes down without a clean shutdown. Claim it first: `python scripts/dev/sync.py claim "nuc-unexpected-shutdown"`.
Steps: (1) run the internet research under "Not done", (2) build `scripts/operator/nuc_power_fix.ps1` as set out under "Fix", (3) leave the operator steps listed below. Builders do not reboot this NUC, flash BIOS, or change power or registry settings. Those are operator steps.

## Evidence (System log, last 60 days to 2026-10-23)
- 15 Kernel-Power 41 events ("rebooted without cleanly shutting down"). BugcheckCode = 0 in all 15, so no Windows bugcheck. No new minidump: CrashDumpEnabled = 7 and MEMORY.DMP is dated 2023.
- 0 planned shutdowns (event 1074). No MTS script calls shutdown or Restart-Computer (grep of scripts/).
- 14 event 6008 records ("previous shutdown was unexpected") in 2026, plus one stale 2024 entry.
- 6 of the 15 have SleepInProgress = 6, meaning the machine died during a standby transition. 2 have a power-button timestamp. 9 have SleepInProgress = 0.
- 22 Oct: "exiting connected standby, reason Power Button" at 03:03:30. Last record 03:03:21. Back at 10:29.
- 23 Oct (last night): last record 02:19:35, with no System events for about 40 minutes before. Back at 02:28:45. Event 13 "system watchdog timer was triggered" at 02:28:52.
- Only S0 low-power idle (Modern Standby) is available. S1 to S3 are not supported by the firmware (`powercfg /a`).
- 133 connected-standby entries and exits in 60 days, including "Idle Timeout" entries, although AC sleep-after is Never (STANDBYIDLE index 0). Not explained yet.
- Clock: at 2026-09-25 19:09:58 the system time jumped from 2024-10-14. That points to a dead CMOS/RTC battery or BIOS defaults being reset.
- Firmware CPU limit: event 37 ("processor 11 ... limited by system firmware") 74 times in 60 days. Some runs last about one day.
- WHEA-Logger "fatal hardware error", 2 times: 2026-09-30 18:23:49 and 2026-10-08 08:17:12. Not decoded yet.
- Config: BIOS FNCML357.0059.2022.1019 (Oct 2022). Fast Startup on (HiberbootEnabled = 1). Auto sign-in on. Sleep and hibernate on AC set to Never.
- `C:\MTS-Worker\logs\launcher.log` has no entries after 2026-10-06, so the worker launcher may have stopped. Check whether it is running.

## Hypotheses (ranked, not proven)
1. BIOS and firmware: a 2022 BIOS, a suspect RTC battery and reset defaults, firmware CPU limits. Check the BIOS date and time, the newest BIOS for NUC10i7FNH, "After Power Failure = Power On", and the watchdog and deep-sleep settings.
2. Modern Standby entry or resume hang: 6 of 15 deaths were during standby transitions. Fix path: `PlatformAoAcOverride = 0` (needs reboot) and Fast Startup off.
3. Power loss (PSU brick, outlet, outage): not excluded. 9 of 15 have no SleepInProgress and no bugcheck. Fix path: UPS.
4. Thermal or load: firmware throttling, plus heavy load from Defender MsMpEng at 25 to 30 % (item b-544817). Fix path: check temperatures, clean the fan, run the Defender exclusions.

## Fix to build (next session)
`scripts/operator/nuc_power_fix.ps1`, modelled on `scripts/operator/defender_exclusions.ps1`:
- Self-elevating. `-Check` lists what is missing and changes nothing.
- Sets `HKLM\SYSTEM\CurrentControlSet\Control\Power\PlatformAoAcOverride = 0`, `HiberbootEnabled = 0`, runs `powercfg /hibernate off`, and keeps sleep and hibernate at Never on AC.
- Prints "reboot required". Never reboots.
- Logs to F:\MTS\scratch, as defender_exclusions does.
- No scheduled tasks (SCHEDULING_POLICY.md).
- Test: `-Check` changes nothing (registry and powercfg state identical before and after).

Defaults for open questions (the build needs no operator input):
- Apply PlatformAoAcOverride = 0: yes. This box is always-on and never needs standby.
- BIOS flash: do not flash without a UPS in place (a failed flash bricks the board). Leave it as an operator step.

## Operator steps (need a person at the NUC)
1. Admin PowerShell: run `scripts\operator\defender_exclusions.ps1 -Check`, then without `-Check` (item b-544817).
2. After the next session builds it: run `scripts\operator\nuc_power_fix.ps1 -Check`, then without `-Check`, then reboot once when no worker is running.
3. BIOS (F2 at power-on): set the correct date and time, set After Power Failure = Power On, and disable the watchdog and deep sleep if those options exist.
4. Replace the CR2032 CMOS battery if the clock is wrong after a power-off.
5. Put a UPS between the wall and the NUC.

## Not done in this run
- Internet research: no search was run. Queries for next time: "NUC10i7FNH unexpected shutdown Kernel-Power 41"; "Windows 10 Modern Standby PlatformAoAcOverride 0"; "NUC10 FN BIOS latest version FNCML357"; "NUC CMOS battery clock reset".
- `nuc_power_fix.ps1` is not written.
- WHEA fatal errors not decoded.
- No changes to the NUC in this run: no registry, power, service or BIOS change. Read-only.

## Done when
Event 6008 ("unexpected") count is 0 over 7 days after the fix and reboot. Record the count from the event log, not from memory.
