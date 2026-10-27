# WHEA DIAGNOSIS - desktop JIS (2026-10-07)

Session: MTS-2026-10-07-1000Z-APP-ANA-whea-htf (Track B). Read-only: Get-WinEvent, Get-PhysicalDisk, Get-Partition, Get-CimInstance.
Nothing changed on the machine.

## Answer

Every one of the 20 WHEA events carries the same source: a **Storport error record for `storahci` / `WDC WD1002FAEX-00Z3A0`**,
the 1 TB SATA hard disk (disk 0, volume **D:**). It is not CPU cache, memory controller, PCIe root port or bus/interconnect.
The source is constant, so one part is involved, not power delivery or thermals. Recommendation: **repair in place (the disk path),
and move the D: dependencies off it; shifting the live role to the NUC is not required by this evidence.**

## B1/B2. Events and source

Event: Microsoft-Windows-WHEA-Logger, Id 1, Error, message "A fatal hardware error has occurred". The data section is a UEFI CPER
record (462 bytes, signature `CPER`, revision 0x0210, 1 section, severity 1 = fatal, record length 462). Source read from the raw bytes:
section tag ASCII `STORPORT`, UTF-16 driver string `storahci`, device id `WDC     \0WD1002FAEX-00Z3A0`. This is identical in all 20
records. Byte-compare of consecutive records: only the timestamp, a 3-byte field at offsets 322-324, bytes 382-385, and the last 4-8 bytes
differ (they look like counters; I did not decode them, there is no field map on hand). The CPER header timestamp matches the event time.
Decoded device identity is solid; what exact storage condition (command timeout, port reset, link error) the counter bytes encode is not
determined here.

| # | Time UTC | Source (decoded) | Gap to next-older event |
|---|---|---|---|
| 1 | 2026-10-07 00:24:10 | STORPORT storahci WDC WD1002FAEX-00Z3A0 | 2.0 d |
| 2 | 2026-10-04 23:47:12 | same | 2.2 d |
| 3 | 2026-10-02 18:01:35 | same | 0.9 d |
| 4 | 2026-10-01 19:23:49 | same | 1.0 d |
| 5 | 2026-09-30 19:20:34 | same | 1.7 d |
| 6 | 2026-09-29 01:33:09 | same | 1.0 d |
| 7 | 2026-09-28 01:56:26 | same | 1.0 d |
| 8 | 2026-09-27 02:19:39 | same | 2.3 d |
| 9 | 2026-09-24 18:39:09 | same | 3.0 d |
| 10 | 2026-09-21 19:26:14 | same | 1.9 d |
| 11 | 2026-09-19 21:49:04 | same | 2.2 d |
| 12 | 2026-09-17 17:00:14 | same | 1.0 d |
| 13 | 2026-09-16 17:23:15 | same | 1.0 d |
| 14 | 2026-09-15 17:52:36 | same | 1.0 d |
| 15 | 2026-09-14 18:24:47 | same | 2.0 d |
| 16 | 2026-09-12 17:17:13 | same | 2.0 d |
| 17 | 2026-09-10 17:35:08 | same | 0.9 d |
| 18 | 2026-09-09 18:56:32 | same | 2.0 d |
| 19 | 2026-09-07 19:05:28 | same | 3.0 d |
| 20 | 2026-09-04 19:17:03 | same | (oldest of the 20) |

Full log: 43 WHEA events since 2026-07-19 18:55Z (earliest still in the System log, which starts 2026-06-06; 37,378 records),
roughly one every 1-3 days (gaps 0.9-3.0 d across the last 20; longest of the 43 is 9 d, Aug 15 to Aug 24). All 43 are Id 1. No other WHEA Id (17, 18, 19, 20) exists.
Time of day (20 events): 14 fall 17:00-19:59Z, 3 fall 01:33-02:19Z, 3 at 21:49Z, 23:47Z, 00:24Z. The machine reboots near 04-05Z every
day (Kernel-General 12, 29 boots in 30 d); the events cluster hours after boot, not at boot.

## B3. Correlation, +/-5 minutes of each of the 20 events

- BugCheck 1001, Kernel-Power 41, EventLog 6008: **none in the whole 30-day window.** No crash or unclean shutdown ever followed a WHEA event.
- Disk 7, 11, 15, 51, 153, 129, 157, Ntfs 55, volmgr: none anywhere in 30 days (Ntfs 98 x149 and Kernel-Processor-Power 55 x232 are informational noise, not within the windows).
- Thermal (Kernel-Power 86 / ACPI thermal): none.
- Kernel-PnP: 29 Id 219 errors in 30 d, all `\Driver\WudfRd failed to load for ROOT\WindowsHelloFaceSoftwareDriver`, at boot; unrelated.
- Other events inside the windows: 13 of 20 windows contain nothing besides the WHEA event; 7 contain only GroupPolicy 1129/1500/1501,
  DistributedCOM 10016, NETLOGON 5719 or WindowsUpdateClient 19/43/44 (domain/update chatter, no storage or power content).
- Most recent event 00:24:10Z: zero other System events in the window.

So the log gives a storage-path report with no OS-visible consequence. Absence of Disk 129/153 means Windows did not log a timeout/retry
for the same moment; the WHEA record is the only trace.

## B4. Summary

Interval: 43 events in 80 days; last 20 in 33 days, median gap 1.9 d, mean 1.7 d, not accelerating (23 events in the
earlier 46 days, Jul 19 - Sep 3). Source: **constant** (one device on one controller), which excludes the "varying source" pattern (power delivery, thermals, PCIe signalling).
Counter bytes change per event, so the events are not repeated copies of one fault record.
Disk health from Windows: `Get-PhysicalDisk` HealthStatus Healthy/OK for both disks. `Get-StorageReliabilityCounter` failed ("Access to a
CIM resource was not available", needs an elevated session), so SMART attributes were NOT read. Disk vs SATA cable vs port cannot be
separated from this evidence.

## Why it matters for MTS

Disk 0 = D: (838 GB used volume). Disk 1 (Kingston SUV400 240 GB SSD) holds C: and F:, where the live repo and F:\MTS data sit.
But the running live Java state machine (pid 18152, and 16668, cmd 20716) executes from **D:\tools\Installed_On_DDrive (JDK) and
D:\tools\apache-maven-3.9.14**, and the SMB share `MTS` is `D:\MTS_Share`. A stall on D: can freeze class loading, a Maven-launched
restart, or a share read, with no crash recorded. This is consistent with the intermittent unexplained stalls but not proven to cause any.

## B5. Recommendation

Source drives the call: storage path, so neither RAM/board nor PSU/slot nor CPU.
1. **Repair in place (primary).** Elevated: read SMART (`smartctl -a /dev/sda` or CrystalDiskInfo; look at 5 Reallocated, 197 Pending,
   198 Uncorrectable, **199 UDMA CRC**). CRC count rising points at the SATA cable or port: swap cable and move to another SATA port. Pending/
   reallocated sectors point at the drive (WD1002FAEX is a 2010-era 1 TB WD Black): replace it.
2. **Reduce exposure now.** Back up D: first. Move the JDK and Maven (`D:\tools`) to the SSD, or reinstall there; the supervisor
   (not a builder) restarts the loop once after that, once the fix is committed and gated.
3. **NUC: not needed on this evidence.** Shift a role to the NUC only if SMART shows a failing drive and the D: items cannot be moved quickly.
4. Re-check after the change: if WHEA Id 1 continues with `STORPORT` but a different device, widen to the controller/board.

Registry: filed as B140.
