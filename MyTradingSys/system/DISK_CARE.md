# DISK_CARE - keeping the desktop C: drive from filling (operator ask 2026-10-10)

Trigger: C: was red (7.6 GB free of 121). Operator ran Disk Cleanup (temp files) -> 15.9 GB free.
Nothing scheduled cleaned C: before this; MTS-Declutter-Backups only archives repo backup files.

## Where C: space goes (measured 2026-10-10, GB)
Windows 23.7 | WindowsApps 17.1 | Claude vm_bundles 11.7 (rootfs.vhdx 8.5, sessiondata.vhdx 1.9, rootfs.vhdx.zst 1.2)
| Chrome profiles 5.7 (3 profiles) | pagefile 4.75 | Docker program files 4.1 | Office 3.7 | repo+IdeaProjects 3.9.
The visible folders sum to well under the 105 GB used: the rest is protected (WinSxS, restore points). Check with an
admin shell: `vssadmin list shadowstorage`.

## Chrome profile: what clearing the cache breaks
Nothing you log in with. Logins live in Network\Cookies, Login Data, Local Storage, IndexedDB, Extensions: the script
never touches those. It clears only Cache, Code Cache, GPUCache (1.56 GB; 3.6 GB with the optional service-worker caches).
Cost: pages load slower once while Chrome re-downloads site files. Chrome must be closed. Moving the cache to F: saves the
same space but adds a Chrome flag or junction to maintain; clearing weekly is simpler. Extensions (0.66 GB) and Storage are
real data: left alone.

## Claude vm_bundles (11.7 GB): options
Name of the technique for moving a folder but keeping its path: a directory JUNCTION (symbolic link), `mklink /J`.
- It is the Claude app's workspace VM image (created 2026-09-25). Operator 2026-10-06: does not need it. DEVICES.md section 6 left it alone.
- Delete: the app re-downloads rootfs.vhdx.zst (1.2 GB) and re-expands to 8.5 GB the next time the VM feature runs,
  so deleting only helps if the feature stays unused. sessiondata.vhdx (1.9 GB) is that workspace's session data: lost.
- Move to F: with a junction (durable fix, 72 GB free on F:). NOT TESTED with this MSIX app and a VHDX. Do not use D: (HDD logging WHEA errors).
  Operator-only, with Claude fully quit:
    robocopy "<vm_bundles>" "F:\ClaudeVM\vm_bundles" /E /COPY:DAT
    ren "<vm_bundles>" vm_bundles.old
    mklink /J "<vm_bundles>" "F:\ClaudeVM\vm_bundles"
    start Claude, confirm it opens; only then delete vm_bundles.old. If it fails: rmdir the junction, ren vm_bundles.old back.
  <vm_bundles> = %LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\vm_bundles
- No scheduler can safely clean it: the app owns it. The weekly task only REPORTS its size.

## Tools (answer to "was D:\tools moved?")
COPIED, not moved: JDK 17.0.18 and a Maven 3.9.14 into C:\tools on 2026-10-10 04:13 (B140/D18, SSD preferred over the D: HDD).
D:\tools originals remain as fallback (start-trading-day.ps1:42-46). Nothing went to F:.

## The job
`scripts\dev\c_drive_care.ps1` (report by default, `-Apply` safe deletes) and `scripts\sched\register_c_drive_care.ps1`
(task MTS-CDriveCare, Sundays 04:00). Log: %LOCALAPPDATA%\MTS-DiskCare\c_drive_latest.md; WARN line under 15 GB free.
Both run under Windows PowerShell 5.1 (tested): no 7+ only calls.

## Gateway marker does not pin finished trees (2026-10-28)
With the machine flag `~/.claude/mts_gateway_on`, `sync.py start` marks every tree `.gateway_owner`; that pinned 66 trees (~4 GB) and the guard freed 0.66 GB. `wt_maint.py` now honours the marker only while the tree was active in the last `GATEWAY_IDLE_HOURS` (12 h); idle past that it is judged like any tree (clean, branch on trunk, no unshipped commits).
