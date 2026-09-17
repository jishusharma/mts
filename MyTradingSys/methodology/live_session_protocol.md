# LIVE SESSION PROTOCOL
# Purpose: reduce AI errors during live tape reads.
# Scope: AI-side behavior only. Process bugs go to BUGS.md.
# Written 2026-09-17 during MTS-2026-09-17-1241Z after two live mistakes.

## OPERATIONAL CHECKS

These run before any statement about price, level, state, or flow.

### 1. Quote the number
Every price, level, state, or flow claim must be a direct quote from a paste
in this session. No paraphrase. No rounding. No words like "near" or "roughly"
without the number beside them.

### 2. Delta check before verdict
Before using any of: new, broke, failed, rejected, confirmed, held, flipped.
Compare the current number to the prior number in the same paste series.
- "new low": current low < prior low, explicitly.
- "bounce failed": the bounce high is retraced past its origin, explicitly.
- "held": the level was tested and the price did not pass through it.
If the comparison is not visible in the paste, do not use the word.

### 3. Timestamp every temporal claim
"now", "current", "at this moment" require the timestamp from the paste.
If the paste is older than 60 seconds, say so. Do not present stale as live.

### 4. Label inference
Numbers from a chart, a screenshot, or a mental model are labeled
"chart read" or "inferred". Numbers from a paste are labeled "system".
Never mix them in the same sentence without the label.

### 5. No sleep in issued commands
Any delay belongs inside a script file. Never in a block the operator pastes.
If a launch check needs a pause, put it inside the script.

### 6. Parse before launch
After any new or edited .ps1, run the PowerShell parser. No PARSE OK, no launch.

### 7. No here-strings in generated script content
USER.md warns against them. Use array-join or a temp .py file for anything
over 20 lines with nested quotes.

### 8. Doc notes are not code
live_session_log.md, apparatus_fixes.md, and BUGS.md are non-critical.
Write them when the gap is seen. Do not defer to after close.

### 9. Corrections are one line
When corrected: state the correction, state the corrected fact, move on.
No essay. No re-diagnosis. No defending the original read.

### 10. Session context is read, not recalled
Before answering a field-level question, check the boot paste or the live feed.
Do not answer from conversation memory. The paste supersedes.

## MISTAKE LEDGER - 2026-09-17

Format: Said | True | Class

| Said | True | Class |
|---|---|---|
| "Bounce failed. New low." (13:47) | Price 76050.1, session low 75975 unbroken. Retrace, not failure. | Factual claim without delta check |
| "No writes during US session." | Doc notes are non-critical per USER.md; write when seen. | Rule misread |
| "Anchor check at 13:30:15." | Anchor is a window; snapshot lands 45-50s after cycle start. | Temporal claim |
| "current_market_state.md is stale." (13:04) | File was mid-write; 13:25 fresh. | Temporal claim |
| Walked back VWAP anchor concern. | Source confirmed original concern was correct. | Flip-flop under challenge |
| "Add a Start-Sleep 4" in issued block. | Rule: no sleep in issued commands. | Rule violation |
| "5.7K OI build" presented as system number. | Chart read, not snapshot field. | Inference as data |
| "Two javas running" presented as current. | One had exited before the read. | Temporal claim |
| "Everything you need" about tape tail. | Missing session, conditions, all setups. | Overstatement |
| Manifest append via `+=` on ConvertFrom-Json property. | Replaced the array instead of extending. Count went 7 to 1. | Wrong method |
| Told operator to write manifest entry with `read: tail` and no `lines` field. | start-session.ps1 crashed with a parameter binding error. | Manifest schema incomplete |

## MISTAKE CLASSES OBSERVED

Four classes, in order of frequency today.

1. Factual claim without delta check. Example: new low. Fix: rule 2.
2. Temporal claim without clock. Examples: two javas, cms stale, anchor moment. Fix: rule 3.
3. Inference presented as data. Example: 5.7K OI. Fix: rule 4.
4. Rule violation on issued commands. Example: Start-Sleep. Fix: rule 5.

## CORRECTION PROTOCOL

When the operator says "false" or "wrong":
1. Accept in the first line. No qualification.
2. State the corrected fact from the paste, quoted.
3. State which rule above would have caught it.
4. Do not re-diagnose the original.

## WHAT THIS IS NOT

- Not a claims ledger for the engine. Engine defects go to BUGS.md.
- Not a rule for Tom-derived conditions. Those live in conditions/.
- Not prose. Add a row to the ledger, do not write an essay.

# END
