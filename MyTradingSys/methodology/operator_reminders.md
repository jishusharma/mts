# OPERATOR REMINDERS

Paste a section into chat to steer the AI. A-E are prompts. F is terminal commands.
Every protocol step must be cited and evidenced. A step is not skipped silently.
If a step cannot be done, say so.

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

### B2. DONE
Print the four lines from DSA section 5b: TASK / DONE / VERIFIED / MISSED.
Show the numbers: hash, line count, non-ASCII count.
Nothing missed is not evidence. A count is.
A worker reply is not verification. Re-execute.

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

---

## C. TRADING

### C1. SCREENSHOT
Follow chart_read_protocol.md. Show each layer by name.
If a layer cannot be completed, say so.
Label every number chart read or system. Never mix them.
liquidation_clusters is deprecated. Do not quote it.
Do not mix the read with a position or a verdict. Give the read.

### C2. TRADE ENTRY
Read direction, entry, stop, target. Label each chart read.
Ask once for anything missing.
Write MyTradingSys\mts\runtime\position.json. Echo the file in one line.
stop=0 disables the stop-proximity alert. Same for target.

### C3. TRADE EXIT
Delete MyTradingSys\mts\runtime\position.json.
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
Follow live_session_protocol.md W1-W5. Show each rule as it is applied.
One DISPATCH.md per worker. Worker has no shell and no disk.
No checks executed section. No Confirmed. Receipt tags required.

### D3. FILE A BUG
Follow the rules block at the top of BUGS.md.
Confirm the defect from disk first. Cite path and line range.
Append one row before the END marker.
Verify: line count, tail, no BOM, non-ASCII count.

---

## E. SYSTEM

### E1. LOOP CONTROL
Loop control per DSA_SESSION_PROMPT.md section 9.
Read wrapper PID, lock, log mtime. All three together.
A log tail alone is not a health check.

### E2. SESSION CLOSE
Close per DSA_SESSION_PROMPT.md section 12.
Show each numbered step and its result.
Build-Check must PASS before close. No close on FAIL.

---

## F. COMMANDS

### F1. OPEN
cd scripts
.\start-session.ps1
mts-live
mts-tape

### F2. READ THE TAPE NOW
Get-Content .\data\apparatus_log.txt -Tail 30
Get-Content .\MyTradingSys\mts\runtime\current_market_state.md -Tail 40
Get-Content .\data\live_tape.md -Tail 40

### F3. PROCESS CHECK
Get-CimInstance Win32_Process | Where-Object {
  $_.CommandLine -match "statemachine|start-trading-day|loop-supervisor|tape-watch"
} | Select ProcessId, Name

### F4. STOP, RESTART, CLOSE
.\scripts\core\stop-day.ps1
.\scripts\core\mode.ps1 -M armed
.\scripts\Build-Check.ps1
gitsnap "one line"

Full command list: COMMANDS.md

# END
