# OPERATOR REMINDERS

Paste a section into chat to steer the AI. A-G are prompts. F is terminal commands.
Every protocol step must be cited and evidenced. A step is not skipped silently.
If a step cannot be done, say so.

---

## 0. MACHINE

Three machines, one repo (on the desktop). WORKSTATION_MODES.md is authority.

- Desktop (JIS-NB): runs the DSA browser worker (working files on F:\MTS\dsa), the loop, auto-trader, alert runner, loss monitor, testnet suites, polling station,
  supervisor session + hourly check. E1 applies. mts-live and mts-tape available. The only place commits happen.
- NUC (JIS-NUC): backtests and heavy research (Qwen lane decommissioned 2026-10-01). Control via the ssh gate only.
- Laptop (DESKTOP-F7IU69N): monitor only. Read-only monitors, Claude CLI for questions.
  No loop control (no mode.ps1, stop-day.ps1), no trading processes, no commits to the desktop repo.

Laptop reaches the queue via \\JIS-NB\MTS-Queue.

---

## A. ORIENTATION

### A1. DISCOVER
List disk across the directories you care about. Newest first.
Ask for whatever you need. Do not assume the paste is complete.

### A2. FETCH
Issue one batched block of commands to read everything you need for the current task.
One block. Operator runs and pastes back.

---

## B. CORRECT THE AI

### B1. CLAIM
Prove from disk. Cite path and line range. Quote verbatim.
Before using new, broke, failed, rejected, confirmed, held, flipped: compare current to prior. Show both numbers.
Every claim carries the field name and value that drove it.
Now, current, at this moment: give the paste timestamp.
Corrections are one line. No essay.
Verbatim / substring check: [regex]::Matches($text,[regex]::Escape($q)).Count. Not $text.Split($q) - it splits on every character.

### B2. DONE
Print the four lines from DSA section 5b: TASK / DONE / VERIFIED / MISSED.
Show the numbers: hash, line count, non-ASCII count.
Nothing missed is not evidence. A count is.
A worker reply is not verification. Re-execute.
Verify by a method other than the one used to write.

### B3. BATCH
Think the whole task through first.
Issue every command in one block, not one per turn.
If the task has steps, state the steps and batch each step reads.

### B4. ANGLES
Same task, three fresh angles. Name each one.
Angle A: reread every input against every output.
Angle B: assume the work is wrong and find where.
Angle C: pick the model or method that would fail this task if it could, and apply it.
Report each angle separately. Do not merge.
If all three agree, say so once. Report the count.

### B5. NO PLACEHOLDERS
No angle-bracket placeholders in pasted blocks.
Ask for the value first. Then issue the block with the value in it.

### B6. NO FAKE RUNS
Never claim a run you did not see pasted back.
Issue the command. Wait for the paste.

### B7. ASK OR ACT
Truly ambiguous: stop, ask one question.
Answer findable from disk or the paste: read it, do not ask.
Never proceed on an assumption.
Never ask for what is already in front of you.
New file vs amend: prefer amending an existing file. Ask before naming a new file or artifact.

---

## C. TRADING

### C1. SCREENSHOT
Follow chart_read_protocol.md. Show each layer by name.
Output the layer name and your work for it. If a layer cannot be completed, say so.
Label every number chart read or system. Never mix them.
liquidation_clusters is deprecated. Do not quote it.
Do not mix the read with a position or a verdict. Give the read.

### C2. TRADE ENTRY
Read direction, entry, stop, target. Label each chart read.
Ask once for anything missing.
Write MyTradingSys\runtime\position.json. Echo the file in one line.
stop=0 disables the stop-proximity alert. Same for target.

### C3. TRADE EXIT
Delete MyTradingSys\runtime\position.json.
Confirm removal in one line.
If the file is left in place, the loop ignores it after 24 hours.

### C4. POSITION OPEN
Recompute from the live panel every reply. Never from the last turn.
Exit levels come from disk or from the operator. Never invented.
The engine fires entries. Exits are the operator decision.
Confirm the loop sees the position: verdict line ends pos=long or pos=short.

---

## D. TASK DISPATCH

### D1. RESEARCH
Follow playbook.md Part I. Research how to research first.
Show each step: meta-research, source-tier commitment, execution.
Tag every finding with source tier, methodology quality, confidence.
Disk claims from files, cited by path and line.
Web claims from verified sources, tagged with URL.
If a web search cannot be run, tag UNVERIFIED-WEB.
Never blend disk and web in one sentence.

### D2. WORKER DISPATCH
One type. See live_session_protocol.md WORKER PROTOCOL R1-R5.
Worker has no shell, no disk. Interprets pasted evidence only.
Requests disk facts by naming file + line range; coordinator runs and pastes back.
Never claims to run anything. Never touches state files. Never commits.
One DISPATCH.md per worker (uppercase). Reply-path line required:
  Write reply to Dumps/workers/<id>/REPLY.md
No checks executed section. No Confirmed. Receipt tags required.

### D3. FILE A BUG
Follow the rules block at the top of BUGS.md.
Confirm the defect from disk first. Cite path and line range.
Append one row before the LAST line that is exactly `# END`.
Verify anchor match count is 1 before writing (-ne 1, never -lt 1).
Then add a row to MyTradingSys/items/INDEX.md and an item doc at
MyTradingSys/items/<id>_*.md, or Build-Check will fail.
Verify: line count, tail, no BOM, non-ASCII count.

---

## E. SYSTEM

### E1. LOOP CONTROL - DESKTOP ONLY
Desktop only. Not applicable on the laptop.
Loop control per DSA_SESSION_PROMPT.md section 9.
Read all of: wrapper PID, supervisor PID, java PID, lock, snapshot age,
state_code age, log mtime. Together. A log tail alone is not a health check.
Read runtime_data\loop_state.json for the supervisor view.
Single stop flag: runtime_data\loop_stop.flag. Both wrapper and supervisor honor it.

### E2. SESSION CLOSE
Close per DSA_SESSION_PROMPT.md section 12.
Show each numbered step and its result.
Build-Check must PASS before close. No close on FAIL.

---

## G. HANDOFF FOR NEXT SESSION

### G1. WHEN
On request, or at session close. Print the handoff as ONE fenced code block.
Nothing outside the block. One click copies it whole. No commentary.
Never claim a handoff was printed if it was not.

### G2. WHAT TO INCLUDE
Session name and UTC stamp.
Loop / Build / Thesis state - one line each.
Landed this session: receipts only (hashes, line counts, commit id).
Open queue: from BUGS.md, not from memory.
First action next session: numbered, batched into blocks.
Do-not-miss: the two or three things most likely to be missed.
Hard rules: only the ones that matter for the next session.

### G3. WHAT NOT TO INCLUDE
Prose. Backstory. Self-congratulation. Anything not on disk this session.
Rules already in DSA or protocol - point, do not restate.

### G4. DO-NOT-MISS SECTION (mandatory)
Name the specific near-misses seen this session. A handoff without this
section is incomplete. Real examples:
  - Prior session counted 0 CT ids. Actual: 19. Wrong counts persist.
  - .Split() used as substring check. Use [regex]::Matches.
  - Lowercase dispatch.md fails Build-Check. Use DISPATCH.md.

### G5. SHAPE

    === MTS HANDOFF - <session name> ===
    NEXT SESSION TITLE: <exact string for UI>

    STATUS
      Loop:    <PIDs, lock, snapshot age>
      Build:   <PASS/FAIL, dispatch count, bug rows>
      Thesis:  <direction, confidence, changed or not>

    LANDED
      - <item> : <receipt>

    OPEN QUEUE
      - <id> <one line>  (from BUGS.md)

    NEXT SESSION - FIRST ACTION
      1. <step>
      2. <step>

    DO NOT MISS
      - <specific>

    HARD RULES (only the ones carried)
      - <rule>

    === END ===

### G6. SECTION 11
Never hand-edit section 11 of DSA from memory. Regenerate from this handoff.

---

## F. COMMANDS

### F1. OPEN
Both machines:
cd scripts
.\start-session.ps1
Desktop only:
mts-live
mts-tape

### F2. READ THE TAPE NOW
Get-Content .\runtime_data\apparatus_log.txt -Tail 30
Get-Content .\MyTradingSys\runtime\current_market_state.md -Tail 40
Get-Content .\runtime_data\live_tape.md -Tail 40

### F3. PROCESS CHECK
Get-CimInstance Win32_Process | Where-Object {
  $_.CommandLine -match "statemachine|start-trading-day|loop-supervisor|tape-watch"
} | Select ProcessId, Name

### F4. STOP, RESTART, CLOSE
Desktop only:
mts-loop stop          # single flag stops wrapper AND supervisor
mts-loop start         # start-session.ps1 + mts-up
mts-loop status        # read runtime_data\loop_state.json
.\scripts\core\stop-day.ps1
.\scripts\core\mode.ps1 -M armed
Both machines:
.\scripts\Build-Check.ps1
gitsnap "one line"

Full command list: COMMANDS.md

# END
