# B140 - WHEA Id 1 fatal hardware error: source is the D: HDD (storahci)

Opened 2026-10-07. Status OPEN. Severity HIGH. Session MTS-2026-10-07-1000Z-APP-ANA-whea-htf.

## Problem
Microsoft-Windows-WHEA-Logger Id 1 on the desktop, 43 events 2026-07-19..2026-10-07, one every 1-3 days, latest 2026-10-07 00:24Z.

## Finding
- All 20 newest records are a Storport CPER section naming driver storahci and device WDC WD1002FAEX-00Z3A0 (1 TB SATA HDD, disk 0, D:).
  Source is constant: one part, not CPU/RAM/PCIe/power.
- No BugCheck, Kernel-Power 41, 6008, disk 7/11/15/51/153 or thermal event in 30 days. The OS never crashed on one.
- SMART not read (needs elevation). Disk vs SATA cable vs port is open.
- Live exposure: java 18152 and Maven run from D:\tools; SMB share MTS is D:\MTS_Share. The repo and F:\MTS data are on the SSD.

## Next
1. Elevated SMART read (5, 197, 198, 199). 2. Swap SATA cable and port. 3. Back up D:. 4. Move JDK/Maven to the SSD (supervisor restarts the loop once).
5. Replace the drive if pending/reallocated sectors. NUC move not required by this evidence.

Report: MyTradingSys/research/_archive/loose_2026-10/WHEA_DIAGNOSIS_2026-10-07.md

## Update 2026-10-07 18:00Z - Step 1 SMART read (clean), cause narrowed
Session MTS-2026-10-07-1800Z-APP-ANA-whea-step2-decide.
- SMART read 2026-10-07, elevated shell, smartmontools 7.5, /dev/sda = WDC WD1002FAEX-00Z3A0 (Caviar Black, fw 05.01D05, SATA 3.0 6.0 Gb/s).
- All critical attributes raw 0: 1, 5, 7, 10, 11, 196, 197, 198, 199, 200. SMART error log: none. Self-test log: never run.
- Reliability counter: ReadErrorsTotal 0, ReadErrorsUncorrected 0. WMI PredictFailure False (both drives).
- PowerOnHours 59874 (6.83 y), LoadCycleCount 39424, StartStopCount 39649, Temp 42 C.
- Cause narrowed from "drive failing" to SATA link, controller, or driver. Ranked: H1 cable/port, H2 controller, H3 driver, H4 PSU rail.
- Driver facts (non-elevated reads): storahci.sys 10.0.19041.3636, inbox; controller Intel 8 Series/C220 SATA AHCI (PCI DEV_8C02) on MSI H87-G43 (MS-7816), bound to "Standard SATA AHCI Controller" (mshdc.inf). No vendor (Intel RST) AHCI driver installed.
- Short self-test could not be started from this session: smartctl needs admin and self-elevation was declined. Operator step.
- Next: swap SATA cable + port; run short self-test; back up D:; move D:\tools to the SSD. Full order: MyTradingSys/research/_archive/loose_2026-10/WHEA_SEQUENCE_2026-10-07.md.

2026-10-10 triage: hardware fix is operator-side. Exact ask: (1) power off and swap the SATA data cable and port for the WDC WD1002FAEX (D:); (2) elevated shell: smartctl -t short /dev/sda and read the result after 2 minutes; (3) back up D:; (4) move D:\tools (live Java) to the SSD. Sequence: research/_archive/loose_2026-10/WHEA_SEQUENCE_2026-10-07.md. Status BLOCKED until the operator reports the swap; new WHEA events after it reopen the driver hypothesis.
