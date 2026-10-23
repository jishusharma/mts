# CPU audit: DESKTOP-F7IU69N (Lenovo 20L90025RT, 8 logical CPUs), 2026-10-23

Read-only run of `scripts/operator/cpu_cleanup.ps1 -Audit` (no admin, nothing changed). Two script bugs found and fixed first
(`$lenovo` shadowed the `-Lenovo` switch, so `-Audit` threw and `-Lenovo` would have added a bool; two task/service regexes
had unescaped backslashes). Fail-first test: `MyTradingSys/tests/test_cpu_cleanup_script.py`.

## Top CPU over 20 s (core-seconds per second, 12 rows)
| Process | cores |
|---|---|
| claude | 0.495 |
| powershell | 0.019 |
| pwsh | 0.014 |
| chrome | 0.005 |
| java | 0.004 |
| msedgewebview2 | 0.002 |
| SynTPEnh | 0.001 |
| explorer | 0.001 |
| SearchHost | 0.001 |
| tposd | 0.001 |
| ShellHost | 0.001 |
| SecurityHealthSystray | 0 |

Finding: the machine is idle apart from this Claude app (0.5 core, the running session itself). MsMpEng is not in the top 12
here (NUC/NB problem, B175, does not reproduce on the laptop). Total non-session load is under 0.07 core: a cleanup buys little CPU.

## Non-Windows services found (33 running + 3 extra)
Keep: AnyDesk, Tailscale (remote access), RtkAudioService, SynTPEnhService (touchpad), MDCoreSvc / WinDefend / WdNisSvc / SecurityHealthService
(Defender), Spooler (printing, unless the operator never prints), WSearch, KeyIso, SamSs, VaultSvc, LSM, NetSetupSvc, RpcLocator,
CoworkVMService (Claude app), SafeExamBrowser (operator's call: only needed for exams).
Safe to disable (OEM helpers, same rules as the NUC list): AESMService, cphs, cplspcon, esifsvc, EvtEng (Intel PROSet event log), FirmwareUpdateService,
IBMPMSVC, igccservice, igfxCUIService2.0.0.0, jhi_service, Lenovo Instant On, LenovoVantageService, LITSSVC, SUService, ThunderboltService,
TPHKLOAD (hotkey loader: keep if the Fn keys matter), WMIRegistrationService, Dolby DAX2 API Service.
These are the `-Lenovo` list entries on this machine. Idle cost is small; the gain is fewer background wakeups, not CPU.

## Startup commands
OneDrive, JetBrains Toolbox, Teams, MicrosoftEdgeAutoLaunch, Docker Desktop, AnyDesk, Tailscale, SecurityHealth.
Safe to drop from startup: Teams, MicrosoftEdgeAutoLaunch, Docker Desktop (start on demand), JetBrains Toolbox. Keep: Tailscale, AnyDesk, SecurityHealth.

## Non-Microsoft scheduled tasks enabled
`MTS-Supervisor`, `MTS-Wrapper` (**legacy MTS tasks on this laptop: SCHEDULING_POLICY.md allows no schedulers anywhere**; card
`host-legacy-tasks-unregister` covers JIS-NB, this machine needs the same unregister), `RtHDVBg_Dolby`, `RtHDVBg_PushButton`, `RTKCPL`
(Realtek UI helpers), `Lenovo Service Bridge`, `Lenovo Power Manager Background monitor`, `PowerToys Autorun`, and five `SoftLanding*` tasks
(Windows upgrade nag, both user SIDs).

## Operator commands (admin shell, not run by this session)
```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/operator/cpu_cleanup.ps1 -Apply -Lenovo
```
Undo: same file with `-Restore`. The two `MTS-*` tasks are not in that script's lists; unregister them from the same shell:
```
Unregister-ScheduledTask -TaskName MTS-Supervisor,MTS-Wrapper -Confirm:$false
```
