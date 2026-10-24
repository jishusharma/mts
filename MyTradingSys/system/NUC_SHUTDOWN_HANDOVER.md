# NUC hand-over: JIS-NUC unexpected shutdowns

Brief for the card `nuc-unexpected-shutdown` (queued first in NEXT_SESSION.md). Written 2026-10-23 on JIS-NUC (Intel NUC10i7FNH, Windows 10 22H2 19045, BIOS FNCML357.0059 of 2022-10-19, one Kingston KC600 512 GB SATA SSD, firmware S4500105, holding C: and F:). Evidence comes from this NUC's own event log. Research sources are listed at the end.

## Applied so far
- 2026-10-23, step 1 (first half): display-off on AC set to Never (`powercfg /change monitor-timeout-ac 0`, High performance scheme). Before: AC 0x258 (600 s), DC 0xF0. After: AC 0, DC 0xF0. Last "Idle Timeout" event 506 was 2026-10-23 02:49:37, before the change; none at the 12:06 check (the NUC was in use, so not yet proof). Undo: `powercfg /change monitor-timeout-ac 10`.
- 2026-10-23, step 1 (second half, operator in admin shell): Fast Startup off, HiberbootEnabled = 0 (reg query confirms 0x0). Takes effect at the next shutdown.
- 2026-10-23: Defender exclusions `-Check` = 0 missing; b-544817 acked done.
- 2026-10-23 ~14:34, recurrence AFTER step 1: hard hang during an SMB copy into F:\MTS\backup_share (KC600 under sustained writes). Event 142 "hardware watchdog triggered a system reset", event 41 BugcheckCode 0, PowerButtonTimestamp 0, ConnectedStandbyInProgress = true; boot 14:38:07. No 506/507 since 02:49:37, display-off AC still 0, HiberbootEnabled 0. The 6008 time (14:09:04) is the last heartbeat, not the hang: copied files carry creation time 14:33:47. The last 4 files written had full size but all-zero contents (renamed *.broken for re-copy). Event 142 also on 10-23 02:28, 10-18 x2, 10-16, 10-12. This moves step 5 (KC600 firmware S4500109, SMART) ahead of BIOS 0067: hang under disk write load + the two WHEA storahci/KC600 records.
- 2026-10-24 21:38 boot: another event 142 + 41 (BugcheckCode 0, ConnectedStandbyInProgress false, SleepInProgress 0, PowerButtonTimestamp 0; so NOT standby this time). Count of event 142 since 10-23: 02:28, 14:38, 17:42, 10-24 21:38 (4 in 43 h, worsening). Last activity ~21:32 while Codex lab worker gx3-dsa-audit-04 was writing on F: (git, sqlite wal), a file-write load like the 10-23 copy. WHEA: only 2 records (09-30, 10-08), none since. KC600 via Windows counters (elevated read): Wear 0, ReadErrorsTotal 0, Temperature 42 C, PowerOnHours 1472, FlushLatencyMax 13, WriteLatencyMax 173: drive looks healthy, so the SSD is NOT proven and firmware is a low-cost check, not the likely fix. Pattern = hard freeze under write/CPU load with no bugcheck: now ranks adapter/PSU, heat, RAM above SSD. Next: try a different 19 V 120 W adapter, HWiNFO log temps/voltages, mdsched.
- 2026-10-24 ~22:00: operator found the DC/wall plug loose (it sparked) and replaced the socket; now firm. A loose contact gives exactly this signature (event 41 code 0 + 142, worse under load, plus the September clock reset). Treat as the leading fix: single-variable test, nothing else changed in this window. Verdict after 48 h of normal load: `powershell -File scripts/operator/nuc_health.ps1 -Days 2`; zero event 142 = fixed. Reset count to beat: 4 in 43 h.
- 2026-10-24 research recheck: Intel NUC10 TPS confirms the jack takes 19 V DC +-10 %, 5.5 mm OD / 2.5 mm ID plug, inner contact +19 V, shell GND, board designed for 120 W adapters on i7FN (power-sensing circuit caps CPU to 120 W; hardware monitor senses out-of-range supply voltage). ASUS page confirms BIOS 0067 (2026-06-11, "safety improvements, platform issue fix, feature updates"). Nothing online documents event 142 for this NUC; Intel 000025536 lists adapter, RAM, drive, thermals, Network Boot. No source gives a firmware fix for this symptom, so no further settings changed (keeps the plug test clean). Candidates if resets continue, in order: adapter swap (19 V, >= 120 W, 5.5/2.5, centre +), cap turbo (`powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 99`, undo 100), mdsched RAM test, BIOS 0067 behind a UPS, SSD firmware.
- Tools added: `scripts/operator/nuc_health.ps1` (read-only count of 142/41/506 plus settings; `-Fix` re-applies display-off) and `scripts/operator/nuc_watch.ps1` (hand-started logger, CSV in %LOCALAPPDATA%\MTS\logs, one row per 5 s: CPU, temp, memory, disk busy/latency/write, network; after a freeze the last row shows the state before it). Logger started 22:42 on 2026-10-24; it does not survive a reboot (no autostart by design).
- Station cleanup: `c_drive_guard.py install` run here (b-10b3d8): HKCU Run entry, status "installed for this checkout".
- Not done: steps 2-7 (BIOS, CR2032, UPS, SSD firmware, BIOS update). Check event 506 after an idle night.

## Operator facts (2026-10-23)
- BIOS "After Power Failure = Power On" (setup-nuc.ps1 step b): NOT done.
- 22 Oct 03:03 stop: all devices were switched off on purpose (LIVE_HOST_MOVE note in NEXT_SESSION.md). That is not a fault.

## Evidence (System log, 60 days to 2026-10-23)
- 15 Kernel-Power 41 events. BugcheckCode is 0 in all 15. PowerButtonTimestamp is set in 2 (2026-09-26 and 09-27; someone held the button). There is no event 1074 (planned shutdown), and no minidump since 2023.
- SleepInProgress = 6 in 6 of the 15 (09-26, 09-26, 09-27, 09-30, 10-13, 10-22).
- 23 Oct (last night): the log was silent for about 40 min, the last record is 02:19:35, and the NUC was back at 02:28:45. Event 13 "system watchdog timer was triggered" was logged at 02:28:52.
- Modern Standby (S0 low-power idle) is the only sleep model available. S1 to S3 are not supported by the firmware.
- The NUC enters standby on every 10 minutes of idle. Display-off on AC is 600 s (VIDEOIDLE 0x258), and the log shows "entering connected standby, Idle Timeout" 10 min after the last input (e.g. 22 Oct 10:49:04 input, 10:59:05 entry). Sleep-after = Never does not stop this, because on Modern Standby idle display-off is "Idle to Standby" (Microsoft). There were 133 standby entries and exits in 60 days.
- Clock reset: on 2026-09-25 the system time jumped from 2024-10-14. Intel's spec says date and time reset only when BOTH the CR2032 battery and AC power fail. So the coin cell is flat and the NUC lost mains power at least once.
- WHEA-Logger "fatal hardware error" twice, both on this NUC (MachineName JIS-NUC), at 2026-09-30 12:49:50 UTC and 2026-10-08 02:43:12 UTC. Decoded CPER record: STORPORT / storahci, device "KINGSTON SKC600". Neither lines up with a crash time. No disk-reset events (storahci 129) were logged.
- Event 37: firmware limited CPU 11 74 times in 60 days, some runs about a day long.

## What official support says (chronological)
- 2019-10, Intel BIOS 0032 notes: a Modern Standby wake fix (Cortana). Intel keeps fixing Modern Standby in BIOS updates.
- 2020-01 / 2020-10 / 2022-09, Kingston KC600 firmware: S4500105 (ours, Jan 2020: SMART E7h, TCG Opal); S4500107 (Oct 2020: RAID compatibility); S4500109 (Sep 2022): "Fixed an issue related to trim", "Fixed an issue related to the SMART error log". Update with Kingston SSD Manager.
- Intel NUC10 Technical Product Spec: CR2032 lasts about 3 years unplugged; "If the battery and AC power fail, date and time values will be reset". On standby: "You cannot switch between ACPI S3 and Modern Standby. Standby power model switching is only supported with a complete operating system reinstallation". So do NOT use the PlatformAoAcOverride registry hack.
- Intel article 000058747 (NUC can't wake from standby, Windows 10): turn off Fast Boot; in BIOS restore defaults (F9), Advanced > Power > Secondary power settings, untick "PCIe ASPM Support", set "Sleep type support" to Modern Standby.
- Microsoft, Event ID 41, Scenario 3 (BugcheckCode 0 and PowerButtonTimestamp 0, which is our case): a power supply problem (outage, unplugged, PSU under-powered or faulty) or a hard hang. Check memory, PSU, overheating; "consider obtaining an uninterruptible power supply (UPS)"; check events before the 6008 time.
- 2023: Intel left the NUC business and ASUS took over NUC support. The ASUS NUC10 Frost Canyon BIOS list: 0063 (2023-12-24), 0064 (2024-03-01, security + bug fix), 0065 (2024-08-20, security, flash robustness, platform fix), 0066 (2024-11-26), 0067 (2026-06-11). Ours is 0059, eight releases behind.
- ASUS FAQ 1052022 (NUC hangs / unexpected shut down), in order: test the power adapter (try another); reseat and test RAM one stick at a time; reseat or swap the drive; check thermals; in BIOS disable Network Boot or set "Boot Network Devices Last"; install the latest BIOS, drivers and firmware; BIOS recovery.
- ASUS FAQ 1052612 (thermal): random power-off is an overheating symptom. Update BIOS, load defaults, check temperatures and fan mode, and look for "Processor Thermal Trip" in the BIOS event log.

## What users did (chronological)
- 2020, Intel Community "NUC10i7FNH and Shutting Off - Over-Temperature Condition Message on Boot": new units shut off at idle or under load and showed an over-temperature warning on boot, while HWiNFO showed normal temperatures. No BIOS note explained it at the time.
- 2020-11, Intel Community "Solved: NUC10i7FNK & Win 10 Modern Standby / Sleep and restart issues" (BIOS 0047): after the display turned off, the NUC tried to enter standby and hung with the power LED solid, needing a hard power-off. Fixes that worked for posters: BIOS dynamic power = Custom with "OSACPI C2 Report" disabled; Sleep type = Legacy S3 (needs an OS reinstall per Intel); HDMI swapped for a Thunderbolt-to-DisplayPort cable.
- Kingston SSD freezes (Tom's Hardware, TenForums): firmware update via SSD Manager fixed them. When the drive is the boot drive, the tool may need it attached as a secondary drive.
- Mini-PC threads (Tom's Hardware, Intel Community NUC11): sudden "as if unplugged" power-off was traced to the adapter or heat. Advice: try another 19 V 120 W adapter and log temperatures with HWiNFO.

## Ranked plan (each step is the cheapest one that removes a cause; check the event log after each)
1. Stop idle-to-standby: on AC set "Turn off display" = Never (`powercfg /change monitor-timeout-ac 0`, no admin needed) and turn Fast Startup off. This removes the 10-minute Modern Standby entries. Source: Microsoft (idle to standby), Intel 000058747 (Fast Boot off).
2. BIOS (F2): After Power Failure = Power On; untick PCIe ASPM Support; Network Boot off or last; check date and time; read the BIOS event log for "Processor Thermal Trip". Source: Intel/ASUS.
3. Replace the CR2032 coin cell (spec: clock reset means battery and AC both failed).
4. UPS between the wall and the NUC; check or swap the 19 V 120 W adapter. Source: Microsoft scenario 3, ASUS step 1.
5. Kingston SSD Manager: update KC600 S4500105 to S4500109 (trim and SMART error-log fixes), and read SMART.
6. With the UPS in place, update BIOS 0059 to 0067 from ASUS, then load defaults (F9) and redo step 2.
7. Only if hangs continue: BIOS dynamic power Custom with OSACPI C2 Report off (the NUC10i7FNK fix), RAM test (mdsched), HWiNFO temperature logging.
Do not apply PlatformAoAcOverride (Intel: standby model switching needs an OS reinstall).

## Done when
Event 6008 count is 0 over 7 days after steps 1-4, and no "Idle Timeout" standby entries (event 506). Count from the log, not from memory.

## Sources
- Microsoft, Event ID 41: https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/event-id-41-restart
- Microsoft, Modern Standby wake sources (Idle to Standby): https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/modern-standby-wake-sources
- Intel NUC10 Technical Product Spec: https://cdrdv2-public.intel.com/841263/NUC10i357FN_TechProdSpec.pdf
- Intel article 000058747: https://www.intel.com/content/www/us/en/support/articles/000058747/intel-nuc.html
- Intel BIOS 0032 notes: https://community.intel.com/cipcp26785/attachments/cipcp26785/nucs/74303/1/FN_0042_ReleaseNotes.pdf
- ASUS NUC10 Frost Canyon BIOS list: https://www.asus.com/supportonly/nuc10i5fnh/helpdesk_bios/
- ASUS FAQ 1052022: https://www.asus.com/us/support/faq/1052022/
- ASUS FAQ 1052612: https://www.asus.com/support/faq/1052612/
- Kingston KC600 S4500109 notes: https://media.kingston.com/support/downloads/SKC600_S4500109_RN.pdf
- Intel Community NUC10i7FNH over-temperature thread: https://community.intel.com/t5/Intel-NUCs/NUC10i7FNH-and-Shutting-Off-Over-Temperature-Condition-Message/m-p/1187532
- Intel Community NUC10i7FNK Modern Standby thread: https://community.intel.com/t5/Intel-NUCs/NUC10i7FNK-amp-Win-10-Modern-Standby-Sleep-and-restart-issues/td-p/1237097
- Microsoft Q&A, WHEA with STORPORT/storahci: https://learn.microsoft.com/en-us/answers/questions/2239883/how-to-isolate-what-hardware-error-according-to-wh
