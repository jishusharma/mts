# B140 - WHEA Id 1 fatal hardware error: source is the D: HDD (storahci)

Opened 2026-10-07. Status OPEN. Severity HIGH. Session MTS-2026-10-07-1000Z-APP-ANA-whea-htf.

## Problem
Microsoft-Windows-WHEA-Logger Id 1 on the desktop, 43 events 2026-07-19..2026-10-07, one every 1-3 days, latest 2026-10-07 00:24Z.

## Finding
- All 20 newest records are a Storport CPER section naming driver storahci and device WDC WD1002FAEX-00Z3A0 (1 TB SATA HDD, disk 0, D:).
  Source is constant: one part, not CPU/RAM/PCIe/power.
- No BugCheck, Kernel-Power 41, 6008, disk 7/11/15/51/153 or thermal event in 30 days. The OS never crashed on one.
- SMART not read (needs elevation). Disk vs SATA cable vs port is open.
- Live exposure: java 18152 and Maven run from D:	ools; SMB share MTS is D:\MTS_Share. The repo and F:\MTS data are on the SSD.

## Next
1. Elevated SMART read (5, 197, 198, 199). 2. Swap SATA cable and port. 3. Back up D:. 4. Move JDK/Maven to the SSD (supervisor restarts the loop once).
5. Replace the drive if pending/reallocated sectors. NUC move not required by this evidence.

Report: MyTradingSys/research/WHEA_DIAGNOSIS_2026-10-07.md
