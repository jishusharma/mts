# B197 - DSA search discipline

Status: OPEN. Opened 2026-10-22.
Owner: [FIXER: Claude] [LOGGER: Claude]
Source: DSA chat MTS-2026-10-22-0601Z (JIS-NB)

## What went wrong (three misses, one cause)

1. Q "roles for my use, doctor, admin, etc?" DSA said "no doctor or admin role exists" from the paste alone. Both exist: START_HERE.txt:2 names the roster; roles/ROSTER.json is the file. The paste lists named files only; it is not the tree.
2. Q "print mts useful cmds file" DSA searched filenames (git ls-files, Get-ChildItem) and said no match. The file is START_HERE.txt, line 2 reads "MTS CHEAT SHEET". A content search found it in one call.
3. DSA proposed the rule fix go in apparatus_fixes.md. Wrong home: LESSONS_DIGEST section 1 is the file built for this; its header says "append the story to LESSONS_LEARNED.md AND one rule line here, same commit".

Cost: five wasted turns. No data lost.

## Proposed fix (three pieces, all non-critical)

(a) LESSONS_DIGEST.md section 1, two rule lines:
  - Absence and discovery both need a content search: git grep -n -i <term> before git ls-files/Get-ChildItem, and before saying a file, role or concept does not exist. [10-22 cheat sheet + roles]
  - A thinking or accuracy lesson goes in LESSONS_LEARNED.md plus one rule line here, same commit; apparatus_fixes.md is for apparatus defects only. [10-22]

(b) apparatus_fixes.md line 9, replace "1. Backup to backup_YYYYMMDD_HHMMSS/ first." with "1. Backup to backup_session\ first (USER.md). Never a backup beside the live file (B186)." This closes B186 item (a), the open half of a HIGH bug whose fix is one line.

(c) Optional: scripts/dev/find_thing.py, ~70 lines, wraps git grep + ls-files in one call. Not required for (a) or (b). Operator may decline.

## Why Claude should accept

- (b) alone is one line that closes an OPEN HIGH bug item (a). No dependency.
- (a) is two lines in a file built to store exactly this rule. Its header is the rule.
- All proposed files are docs and scripts; none under execution/, none critical, none on a running import path.
- Same class as B186 (write discipline) and B184 (bridge contract). Both filed and open. Cost of doing nothing: five wasted turns this session.

## Evidence

- MyTradingSys/system/START_HERE.txt:2 (MTS CHEAT SHEET)
- MyTradingSys/system/START_HERE.txt:118 (MTS_Doctor)
- MyTradingSys/system/START_HERE.txt:115 (Admin_Guy)
- MyTradingSys/system/LESSONS_DIGEST.md:11 (section 1)
- MyTradingSys/research/apparatus_fixes.md:9 (backup_YYYYMMDD)
- MyTradingSys/research/BUGS.md:301 (B186 HIGH)
- git grep -n -i "MTS CHEAT SHEET" at 2026-10-22T06:06Z returned MyTradingSys/system/START_HERE.txt:2 in one call.
