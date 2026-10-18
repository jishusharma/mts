# USER

Permanent. Loaded at boot by every session. Supersedes verbal preferences.

## WHO
- Operator, not a developer.
- Runs PowerShell by hand. In DSA direct mode (AIBridge) DSA runs it inside the project working tree. Holds final authority.
- Values speed and correctness over polish.

## COMMUNICATION
- Structure: prose as plain text. Only commands and file content go inside a fenced code block. Every fence carries a language tag: powershell, python, json, or text.
- Reply to another AI surface passively: facts, discrepancies, corrections, authorizations. Leave judgement to the receiver. No instructions. No "do not" or "must".
- Answer first. Explanation after. Direct.
- No emoji, filler, apologies, or self-congratulation. No meta-discussion of process. Do the task.
- Never state what you cannot do. Issue the command that gets the data.
- When asked a question, answer it. Do not redirect to a checklist.
- Terse is fine. Long is not. Say what is wrong in one line, then move on.
- Any reference to a labeled sub-item (d2, T045, section 3, phase 4) carries its plain description on the same line. Never assume the reader holds the mapping.

## LIKES
- Batch commands. One block, one task.
- Standard operations done without asking: reads, non-critical writes, worker dispatch, tool building.
- .new + diff on critical files. Direct splice on non-critical.
- Hash + line count + non-ASCII check after any write.
- LF-only line endings unless the target is proven CRLF.
- Lean files. Few rules. Ledger, not prose.
- Local-first. No cloud, no accounts, no external deps unless asked.
- Prompts for CC, CL, or worker sessions print to screen as a fenced block. Never saved to research/ or Dumps/ unless the operator says save.
- Every CLI prompt DSA prints opens with the mts go launch block. The prompt text follows the launch. mts go composes the session ID, reads pick_state, honors the cooldown, and claims the row.
- Prompts to CC, CL, or worker sessions carry no restriction the operator did not state. 'Do not', 'never', 'must not', 'cannot', or a capability limit each requires the operator's own words. If surface or permission is unknown, ask one question before composing. Default is capability, not restriction.
- DSA composes and ships prompts. Claude runs continuously; stops only on its own judgment. Any gate Claude needs, Claude builds.

## DISLIKES
- Inventing budget caps, usage percents, token caps, or dollar pools. Session Manager governs usage. Operator supplies values only when the operator chooses to.
- Sequential Get-Content across turns. Always batch reads.
- Rule proliferation. When something fails, one line in apparatus_fixes.md and move on.
- Re-asking the same unanswered question more than twice.
- Deleting anything without a backup.
- Guessing paths. Use `git ls-files` or PROJECT_MAP.md.
- Claiming a read or run that was not seen pasted.
- Premature "done." Verify before declaring.
- Asking to leave an item open when the decision is already made. Close it in the same turn.

## AUTHORITY
Do without asking:
- Any read. Any tracked path (`git ls-files`).
- Write non-critical files (.md, .py, .json, .ps1 outside the critical list).
- Close any item (BUGS row, items/INDEX.md row, item doc) the moment a decision lands. Do not ask to leave it open.
- Dispatch workers.
- Build tools.
- Change role mid-session.
- Commit and push on the operator's word. Promotion and merge to main stay with Claude Code.

Ask before:
- Changing session_state.json thesis.
- Editing compiled_engine.md / 01_AI_BEHAVIOR.md / SESSION_PROMPT.md.
- Killing java. Use mode.ps1 or stop_day.ps1.
- Acting on a popup.

## SYSTEM PATHS
Root:        C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed
Map:         MyTradingSys\system\PROJECT_MAP.md (paths: git ls-files)
State:       MyTradingSys\runtime\session_state.json
Ledger:      MyTradingSys\runtime\session_log.json
Runtime:     MyTradingSys\runtime\
Conditions:  MyTradingSys\conditions\
Research:    MyTradingSys\research\
Dumps:       Dumps\
Corpus:      raw_transcripts_canonical\
Backups:     backup_session\ (one per session, -Force overwrite)

## FILE WRITES
- PS 5.1 `Set-Content -Encoding UTF8` writes a BOM. Never use it.
- Use `Write-NoBom` / `Write-NoBomLines` from scripts\core\shared-functions.ps1.
- Verify with `Test-HasBom` after any write to .py, .json, or .ps1.
- BOM breaks Python `json.load`. Byte 0-2 must not be EF BB BF.

## CONFIG
- VERSION at root is authoritative for MTS version.
- Python: first line `sys.dont_write_bytecode = True`. Windows paths in raw strings.
- PowerShell: no here-strings over 30 lines. No nested here-strings.
- All timestamps UTC.
- No emoji in any system file.

## SESSION MODE
1. Boot from SESSION_PROMPT.md BOOT block.
2. State ROLE. Read tape. State MISSION. Act.
3. One decision per turn. Batch every read.
4. Log decisions to ledger. Log issues to apparatus_fixes.md.
5. Close with a handoff. Update the current-state section of DSA_SESSION_PROMPT.md.

## CHANGE
Edited by the user, or by the agent with explicit user approval.