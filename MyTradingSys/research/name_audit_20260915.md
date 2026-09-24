# Name Audit
Version: 1.0.1 | Date: 2026-09-16
Supersedes: 1.0.0 (v1.0.0 marked the seven live aliases as UNKNOWN.
The meanings are in the session log entry "MTS_SCRIPTS_CONSOLIDATED".
v1.0.1 corrects that. The verdict changes from "rename" to "document".)

## Summary

| class | count | action |
|---|---|---|
| Short live aliases | 7 | DOCUMENT, do not rename. Meanings already exist. |
| Duplicate function | 1 | extract to a shared file, or rename per scope |
| Undefined package tokens | 5 | replace with plain phrases or real paths |
| Undefined runtime label | 1 | add to the dictionary |

## 1. Short live aliases - meanings recovered

Source of meaning: session log entry "MTS_SCRIPTS_CONSOLIDATED"
(2026-09-15T16:08Z), plus the first-line headers now present in each
script under scripts\live\.

| name | meaning | script | verdict |
|---|---|---|---|
| lx | quick check - live price vs snapshot, one line | scripts\live\lx.ps1 | keep, header added |
| ld | deltas - last 12 minutes of one-minute bars | scripts\live\ld.ps1 | keep, header added |
| lt | trend - last 15 snapshots side by side | scripts\live\lt.ps1 | keep, header added |
| lf | full - one snapshot, all decision fields | scripts\live\lf.ps1 | keep, header added |
| lc | combo - live, snapshot, state, and log together | scripts\live\lc.ps1 | keep, header added |
| lh | health - java process, state file age, log tail | scripts\live\lh.ps1 | keep, header added |
| la | alerts - last 10 alert lines from the system log | scripts\live\la.ps1 | keep, header added |

These are curated shortcuts, not orphans. They are referenced in
COMMANDS.md. Renaming them would break that file. Action is to document,
not to rename.

## 2. Duplicate function

The function "Get-Descendants" exists identically in two scripts:
scripts\core\mode.ps1 and scripts\core\stop-day.ps1. Two options:
pull it into a shared file, or rename each copy after its purpose.
The naming proposal carries this forward as an open decision.

## 3. Undefined package tokens

These appeared in the original task package with no definition.

| token | plain replacement |
|---|---|
| | write "one sourced PowerShell session in the project root" |
| A | name the file - compiled_engine.md |
| B | name the folder - conditions\*.md |
| E | name the file - CONSOLIDATED_RULES.md |
| D | no referent - remove |
| H | write "the PARKED section in apparatus_fixes.md" |

## 4. Section letters are not names

The letters A, B, E, D, H appear thousands of times inside the compiled
engine because they are section headers there. They are not undefined
tokens in that document. No action on the document itself.

## 5. Runtime label

The runtime loader prints "mts loaded: ..." every session. The label
"mts" was never defined. The dictionary now defines it: mts is
MyTradingSys, the decision system in this repo.

## 6. Rename plan - status

| step | action | status |
|---|---|---|
| 1 |, A, B, E, D, H in the task package | package no longer used |
| 2 | add "mts" to the dictionary | done |
| 3 | add header to each live script | done |
| 4 | rename lx..la | not needed, documented instead |
| 5 | pull Get-Descendants into a shared file | pending user decision |

## 7. Open decisions

1. Pull Get-Descendants into a shared file, or leave the duplicate?
2. Confirm the A, B, E mapping above.

## End
