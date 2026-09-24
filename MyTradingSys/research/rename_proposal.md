# Rename Proposal

Written: 2026-09-16
Purpose: every folder, file, and recurring term that is not self-explanatory gets a plain name. Nothing is renamed yet. You approve first.

## Rule for this project

When giving the user an update, or when providing information:
- No internal codes. No letters, no numbers, no hashes, no byte counts unless the count itself is the point.
- No shorthand invented in the session. If a thing has a name, use its full name.
- Plain sentences first. Tables only when the table saves reading.
- Any term used twice in a session must exist in the dictionary or be replaced.

## Folder names - current and proposed

| current | why unclear | proposed |
|---|---|---|
| Dumps | capital letter, vague ("dumps of what") | dumps |
| extracts | what is extracted from what | transcripts_work |
| extracts/processed | processed how | transcripts_work/cleaned |
| extracts/pending_raw | pending means what | transcripts_work/to_clean |
| extracts/fresh | fresh compared to what | transcripts_work/new |
| raw_transcripts_canonical | "canonical" is jargon | transcripts_raw |
| backup_session | fine, but singular/plural drift | backups |
| docs | fine | docs |
| data | fine | data |
| scripts | fine | scripts |
| src | fine | src |
| target | build output, standard | target |
| MyTradingSys | the system name, fine | MyTradingSys |

## File names - current and proposed

| current | why unclear | proposed |
|---|---|---|
| session-start.ps1 | two scripts with similar names | start-session.ps1 |
| scripts/core/start-trading-day.ps1 | it starts the trading day, not the chat session | keep, but rename to avoid confusion with session-start.ps1 |
| scripts/core/mode.ps1 | "mode" of what | set-run-mode.ps1 |
| scripts/core/stop-day.ps1 | fine | keep |
| scripts/load.ps1 | loads what | load-aliases.ps1 |
| DSA_SESSION_PROMPT.md | "DSA" is never defined | session-prompt.md |
| L_ITEMS_MASTER.md | "L-items" is an internal code | open-loops.md |
| apparatus_fixes.md | "apparatus" is internal jargon | system-fixes.md |
| MTS_DICTIONARY.md | fine | keep |
| PROJECT_VISION.md | fine | keep |
| compiled_engine.md | "compiled" from what | engine.md |
| compiled_output_audit_20260915.md | "compiled-output" is jargon | audit-2026-09-15.md |
| runtime_data/apparatus_log.txt | same jargon issue | runtime_data/system_log.txt |
| Dumps/SESSION_PASTE.txt | fine | keep |

## Key terms - current and proposed

Terms that appear in docs, logs, or prompts with no definition anywhere.

| term | where it appears | proposed replacement |
|---|---|---|
| | session boot instructions | "one sourced PowerShell session in the project root" |
| A / B / E | worker instructions | name the actual file or folder |
| D / H | worker instructions | name the actual file or folder |
| L8, L13, L16, L17, L18, L23 | open-loop tracking | give each loop a short plain title (see open-loops.md) |
| DSA | filenames and prompts | "session" (drop the prefix entirely) |
| MTS | everywhere | fine, but add one line to the dictionary: "MTS = MyTradingSys, the decision system in this repo" |
| nrr | runtime log lines | "net reward to risk" - spell it out in the log |
| pd | runtime log lines | "prior day bias" - spell it out in the log |
| W1, W2, W3, W4 | coordinator dispatch | name workers by what they do: schema, gaps, structure, open-loops |
| R32, R38, R40, R46, R51, R52 | rules in docs | spell out "Rule 32" once, then refer by a short title if needed |

## Priority order for renaming

1. Key terms - fix these first. They cost the most to leave unclear, and they have no downstream file moves.
2. Files with obvious replacements - low risk, one file each.
3. Folders - do these last, because each move touches many references.

## What still needs your answer

Resolved 2026-09-16 - renamed to plain words (quick, deltas, trend, snapshot, overview, health, alerts).
2. Do you want the open-loop items (currently L8, L13, and so on) renamed to short plain titles now, or kept as numbers with a title column added?
3. Folder renames - do you want them this session, or plan only?

## End


## UPDATE 2026-09-16

The seven live aliases were renamed to plain words:
quick, deltas, trend, snapshot, overview, health, alerts.
The proposal above is closed. See COMMANDS.md for the current names.
