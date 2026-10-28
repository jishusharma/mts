# B132 - DSA dispatches work it can do itself

Status: OPEN
Opened: 2026-10-04
Filed by: MTS-2026-10-04-0916Z-DSA-COO

## Operator directive (verbatim, 2026-10-04)

"I need u to also do the tasks - not just send all to Claude - u can do the
ones that are quick wins, something that unblocks and prepares the Claude
Code Sessions for working seamlessly on tasks that do not collide and are as
per MTS protocols. Also - Claude must assign work to DSA keeping all my
points in mind. DSA is a free tool that saves costs but adds extra overhead
of operator's time that is lost in copy pasting. So DSA tasks must be
assigned accordingly. So make changes where needed to enforce this asap!"

## Defect

DSA composes a Claude Code prompt for nearly every pipeline row, including
work DSA can do directly in one turn. Categories of work wrongly dispatched:

1. Registry writes: BUGS.md status flips, items/INDEX.md rows, item-doc
   receipts. USER.md AUTHORITY already grants these to DSA.
2. Section 11 refresh of DSA_SESSION_PROMPT.md.
3. 03_FILE_INDEX.md rows.
4. Small doc receipts and cross-links.
5. Session records for DSA-composed runs.
6. Single-line code changes with no test tree (rare, but observed).
7. Read-only verifications (e.g. B059 live tape check, which DSA did
   correctly at b9b0405 - and did then).

Cost when this is wrong: one operator copy/paste per task. The operator's
time is the scarce resource; the App session is not free either (Pro pool).

Cost when this is right: DSA does the work in one turn; the operator does
nothing.

## Fix shape

(a) Codify a "DSA does this directly" list in DSA_SESSION_PROMPT.md. Every
    item on the list runs in DSA's own turn, not in a Claude Code session.
(b) Require every composed Claude prompt to name the DSA-side unblock work
    already done, so the session does not re-derive it.
(c) Require every Claude prompt to name the collision check DSA ran (which
    file sets are held by other in-flight sessions).
(d) Route single-file edits, registry writes, doc appends, and status flips
    to DSA by default.

## Evidence

This session, MTS-2026-10-04-0916Z-DSA-COO, dispatched as Claude Code
prompts: B075/B084, B074/B069, T052/B063/T046, T053, T050 phase 3, B104,
B100, T037, B129, B059-verify-planned, B085-planned, B102/B103, LY1. Of
those, at minimum the registry flips, item-doc receipts, 03_FILE_INDEX rows,
and section 11 refresh were DSA-executable. Observed retries when the CC
session hit path or line-ending issues that DSA could have caught on disk
first (LESSONS_LEARNED entries 2026-10-04: Resolve-Path, diagnostic throw,
trailer format, verdict-label flip).

## Not fixed here

Filing only. The DSA_SESSION_PROMPT.md change lands in the same commit.

# END