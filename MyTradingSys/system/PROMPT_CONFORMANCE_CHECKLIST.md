# PROMPT CONFORMANCE CHECKLIST
# Rewritten 2026-10-02 by MTS-2026-10-02-1710Z-CLI-SUP-prompt-shape (was 233 lines).
# Applies to DSA sessions. Before handing any Claude prompt to the operator: STEP -1,
# STEP 0, header tables, then the prompt. Evidence = command run and its output.
# The prompt is printed to the operator's screen only. Never written to disk
# (operator, 2026-10-02: "Prompt must always be pasted on my screen - never written to disk").

## STEP -1 - SAME-TURN VERIFICATION (before Step 0)
Every disk claim inside a prompt is read from disk in the same turn that the prompt is
written. On the DSA chat surface: run one verification block, receive the paste, then
compose. No exception for small prompts or "same as last time".

Prior pastes, handoffs, ledger entries and other surfaces' work are hypotheses, not evidence.
Every claim carries one tag, in the prompt or in the Verified facts table:

| Tag | Meaning |
|---|---|
| VERIFIED <YYYY-MM-DDTHH:MMZ> | read from disk this turn, receipt in the session |
| OPERATOR-SET | value supplied by the operator, not invented |
| UNVERIFIED | not read this turn; stated as a limit, not a fact |

A claim with no tag is a defect. Fix before delivery.
## STEP 0 - SURFACE AND PERMISSION

Answer both before composing anything else.
| # | Item | Failure mode |
|---|---|---|
| 0a | Surface: CC / CL / Opus on CL / Opus on CC / DSA / worker | inferring the surface |
| 0b | Permission: may edit code, run Maven/pytest, commit, push | inventing a restriction |

A restriction in the prompt that is not in the operator's words is a defect. "do not",
"never", "must not", "cannot" and any capability limit each need an operator quote.
If 0a or 0b is unknown, ask one question and stop. Never default to the restrictive option.

No fabrication by the DSA session while writing the prompt (operator direct, 2026-10-02).
Surface, permission, restriction, file path, line number, hash, count, and claim each come
from disk this turn, from the operator's words this session, or carry the UNVERIFIED tag.
A missing answer is left empty or asked; it is not filled with a guess.

## DELIVERY FORMAT

Two blocks, in order. Block 1 is the header tables, Block 2 is the prompt.

Block 1 - header tables (printed to screen, not saved):

### Verified facts (read from disk this turn, YYYY-MM-DDTHH:MMZ)
| # | Fact | Source line or command output |
|---|---|---|
(Every disk claim in the prompt appears here or is tagged UNVERIFIED.)

### Session
| Field | Value |
|---|---|
| Session type | CC / CL / Opus / worker |
| Account / Model / Effort | A or B / ... / low, medium, high |
| Ultracode / Subagent cap | off or on / 0..3 |
| Commit cadence | per step / per wave / end / n/a |
| Deliverable path / Gate | ... / ... |
| Budget cap | OPERATOR-SET only. Omit the row if the operator gave none. |

### Conformance
| # | Check | Status | Evidence |
|---|---|---|---|
| 1 | Every file and script path in the prompt exists (Test-Path) | PASS / FAIL | output |
| 2 | Mandatory lines present (below) | PASS / FAIL | quote |
| 3 | Prompt <= 30 lines, no restated hard rules or state (CLAUDE.md, STATUS.md have them) | PASS / FAIL | line count |
| 4 | End to end: deliverable, gate, save and commit cadence stated | PASS / FAIL | quote |

Block 2 - the prompt, one fenced block tagged text, ready to copy whole, no commentary
inside. At most one line between the blocks (the operator action). Any FAIL row = not delivered.

## MANDATORY LINES IN EVERY CL PROMPT (operator direct, 2026-10-02)
1. Process spawning: "CL runs commands as subprocesses (python, PowerShell, git, Maven).
   Spawn whatever child process the task needs, per SURFACE_POLICY 3b. Spawning is
   expected; stopping to ask whether it is allowed is a defect."
2. Operator proxy, verbatim: "Use my proxy when needed - Incase i forget - Claude must not
   stop and eat up my money without outputting work!" A stop that produces no artifact
   is the failure this line forbids; an authorized question is not re-asked.
3. Printing: "== T<n> <name> ==" at task start; "T<n> PASS|FAIL|BLOCKED <result>" at end;
   no wait for the operator between tasks.
4. Verify block at the end: TASK / DONE / VERIFIED / MISSED.
5. Parallel CL sessions, one tree, one staging area. Two lines:
   a. Stage only the exact paths you wrote. Never stage the whole tree.
   b. Before committing, list the staged paths and compare them to your
      expected output list. A staged path you did not write means stop;
      do not commit. On the commit line, name the paths the commit owns,
      so the commit records only those and leaves the rest of the staging
      area alone.

## CONTINUOUS EXECUTION (operator direct, 2026-10-02)
A DSA-composed prompt never contains "operator confirms or overrides" (unless a genuinely
blocking choice exists and the prompt names it as the only stop), "wait for the operator"
between tasks, or "if you have any questions, stop and ask".

Default is auto mode (SURFACE_POLICY 0): the session acts, logs it, continues. It stops only
on BLOCKED (a fact it cannot obtain), FAIL (a gate), or operator interruption.

## PROMPT SHAPE
- Line 1: session ID, -CLD- for CC or -CLI- for CL; then surface, model, effort, branch.
- Line 2: read-first list (CLAUDE.md, then STATUS.md, then task-specific files by line range).
- Budget: DSA never states a percent, token cap or dollar pool. A budget line exists only
  if the operator supplied it this session; Session Manager (SURFACE_POLICY s3) gates
  usage on its own, so the prompt carries no budget gate.
- The actual task: numbered T1..Tn, each with its gate, file:line or proof path.
- Authorization: the operator's words, verbatim, only.
- Total <= 30 lines. Hard rules live in CLAUDE.md and state lives in STATUS.md; the prompt
  names them and does not restate them.
- Last: the mandatory lines above.

# END
