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

### 11. Evidence attached to every claim
Any observation, bug, note, or design claim cites the specific field values
from the paste or snapshot that drove it. Quote the field name and value
inline. No claim without its evidence, when the evidence is available.

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

## PROCESS SPEED RULES (added 2026-09-17 after MTS-2026-09-17-1357Z)

Seven waste classes seen today. Each has a fix. Each fix is a rule.

1. Note-file round trip. Do not require a helper file on disk for a
   one-shot dispatch. Inline the material with a here-string under 30
   lines, or `Get-Content -Raw` a real source file and inject it. No
   hand-authored note file.

2. Interactive `return` does not abort a pasted block. In an
   interactive PowerShell session, `return` at top level only exits
   the current pipeline stage. Use `throw` or wrap the whole block in
   `if (guard) { ...work... } else { "ABORT: reason" }`.

   CORRECTION 2026-09-19: the first sentence above is wrong. In an
   interactive paste, each line is a separate statement. A top-level
   `throw` prints an error and the next line still runs. Verified this
   session: a top-level `throw` was followed by more statements that
   ran, including a file write. The fix is to wrap the whole block in
   `& { ... }`. `throw` inside `& { }` aborts the block. The
   `if (guard) { } else { }` form is also correct, but only when the
   entire block is inside the same brace group. Bare top-level
   statements are never protected by either form.

   FOLLOW-ON RULE 2026-09-19: before composing any write, READ the
   exact target line from disk in the same turn. Do not compose an
   anchor from memory or from a prior paste. This session wrote a
   correction block targeting apparatus_fixes.md when the rule lived
   in live_session_protocol.md. The anchor never existed, the write
   was a silent no-op, and the commit message lied. Reading the
   target line first would have caught it before the write.

3. Worker scope. A worker has no shell and no disk. A file-level
   claim (line numbers, greps, hashes) is coordinator work, done here
   with disk commands. A worker interprets pasted text. Do not assign
   a disk-verification task to a worker.

   WORKER PROTOCOL 2026-09-19. Five rules (R1-R5). Added after a B044
   dispatch failure where a worker labeled invented check outputs
   as "Confirmed".

   R1. Worker never claims to run a command. Worker requests evidence
       by naming file and line range. Coordinator runs it and pastes
       the output back. Two rounds minimum for any task that needs
       disk facts.

   R2. Every worker dispatch includes a PATHS AND COMMANDS section:
       repo-relative paths to relevant files, and the exact commands
       the coordinator can run on the worker request.

   R3. Every worker dispatch includes an EVIDENCE ALREADY PROVIDED
       section listing each excerpt the worker has and, explicitly,
       what it does not have.

   R4. Worker output cannot include a "checks executed" section.
       That section is coordinator-only. Worker output is derived,
       not empirical.

   R5. Worker output must tag every disk-derived claim with its
       receipt: "per dispatch excerpt N", "per coordinator paste
       titled X", or "unverified". The word "Confirmed" is reserved
       for the coordinator own re-execution and never appears in
       worker output.

4. One DISPATCH file per worker. `DISPATCH.md` = prompt + attached
   source excerpts, concatenated. No separate WORKER_READY_1.md. No
   multi-part handshake. W1/W2 keep their old layout as history.

5. Reply save in the same block as the paste. Assign `$reply` via
   here-string in one block, write, verify bytes in that block. Never
   carry `$reply` across turns. An unset variable writes an empty file.

6. One-block dispatch build. mkdir, write DISPATCH, verify bytes +
   lines + BOM + non-ASCII. Same template every worker. If a step
   fails, the block prints and stops; do not paste a second block.

7. Boot section 11 must not be hand-edited during a live session. It
   goes stale within minutes. Regenerate at close from loop health,
   BUGS.md, and the last journal entry.

8. Never call mode.ps1 or start-trading-day.ps1 with the call operator
   (ampersand) from a script that needs to keep running. Both block
   forever because they enter the trading loop. Use Start-Process with
   -WindowStyle Hidden and no -Wait. Same rule applies to any wrapper
   around them. Verified 2026-09-17: restart-with-b034.ps1 hung at the
   mode.ps1 call; Ctrl+C killed the wrapper and the supervisor had to
   recover.

9. To stop a supervisor, kill the process directly by matching its
   command line for loop-supervisor. Do not use the stop flag plus a
   polling wait. The supervisor only checks the flag once every 30
   seconds, so a polling wait burns up to 45 seconds. One direct kill
   is 1 second and does the same thing.

10. Live mode runs mts-live. Every live session reads the feed and
    extends it with at least one block or field. The naming scheme
    is in MTS_DICTIONARY.md under LIVE FEED NAMES. Version and
    changelog live in the header of scripts/live/mts-watch.ps1.

## RULES 12-14 (added 2026-09-18, from the FRAME GATING / B046 mistake ledger)

12. Code claims require code reads. If a claim is about Java or Python
    behavior, Get-Content the range. Inference from a function name or a
    prior report does not count.

13. Prior-session claims are hypotheses. Handoffs, journals, and ledgers
    are read as suggestions, not facts. Verify on disk before acting.
    Same rule for the boot paste and for the manifest.

14. Boot paste is read line by line, not skimmed. If a correction exists
    in the paste, it supersedes any prior-session framing.

## RULE 15 (added 2026-09-19)

15. No new layer without a named decision-function reader and a
    sensitivity test. A layer is wired only when a named decision
    function reads its value, and two fixtures differing only in that
    layer produce a different verdict or reason string. A layer
    without a reader is exempt with a tracked reason and a review
    date, not "done". Supersedes "gauge by design" as a closing
    argument.

## WORKER TYPE (added 2026-09-23)

One worker type. Dispatched by the coordinator.

R1-R5 above apply. No shell, no disk. Interprets pasted evidence.
Requests facts by naming file + line range. Writes go through the
coordinator into Dumps/workers/<id>/. No direct repo writes.

## RULE 16 (added 2026-09-19)

16. No inferred levels. Any price level offered as actionable must carry a source tag from MTS_DICTIONARY. [SCREENER] levels are not signals. Prior-day POC, prior-day VAH/VAL, and any level not in conditions/ are SCREENER unless a rule names them.

## RULES 17-19 (added 2026-09-25, from the loop-survival session)

17. Anchor preflight. Before any write block, the same turn must
    contain a Get-Content of the exact target range, cited by line
    number. No anchor composed from memory, prior paste, or journal.
    After composing, count via [regex]::Matches. Count not 1, abort.

18. Interactive-scope declaration. Any block pasted at the operator
    prompt that references $R, $M, $pwshExe, $splat, or any non-
    environment variable must open with & { ... } and declare every
    one of those variables literally. No session-state reliance.
    Unique variable names within a block. Do not reuse a name for a
    different type.

19. Quote layering. When a command line must survive three or more
    quoting layers (PowerShell -> cmd/VBS/schtasks -> target
    program), build the string once in PowerShell, then double the
    quote char for each layer: -replace '"','""'. Do not hand-nest.
    Check operator precedence when mixing + and -f: parenthesize.

# END