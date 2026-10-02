# PROMPT CONFORMANCE CHECKLIST
# Written 2026-10-02 by MTS-2026-10-01-1755Z-DSA-COO.
# Applies to DSA sessions only. Rule: before DSA hands any Claude prompt
# to the operator, print the table below with evidence per row. Do not
# deliver the prompt until every row is PASS. Evidence = the exact
# command run and its output, not a claim.

## PROMPT TYPES

CC - Claude Cloud Repo. Win Claude App, Cloud Mode.
  Sees: pushed git refs only. No disk. No LAN. No F:\\\\.
  Branch: harness-assigned claude/<name>. Record as branch_alias.
  Commits: to its own branch. Operator cherry-picks.
  Read-only means: no writes to main, no Maven, no gitignored paths.
    It does NOT mean no file output. Every analysis session names its
    deliverable path and commits it to the branch.

CL - Claude Code Mode. Win Claude App, Code Mode.
  Sees: local disk.
  Branch: fast-track per CLAUDE.md; never master.
  Can run Maven locally (D:\\tools\\apache-maven-3.9.14).
  Writes: <file>.new for staged work; commit after promotion.

Both conform to CLAUDE_MANAGER_SPEC routing and SURFACE_POLICY s2-s4.

## BEFORE DELIVERING ANY PROMPT

| # | Check | Evidence |
|---|---|---|
| 1 | Every file path in the prompt exists on disk | Test-Path per path |
| 2 | Every script path exists | Test-Path |
| 3 | Save-work clause: never refuse work for budget. Commit after each step when Session Manager signals low headroom. | quote |
| 4 | Model matches CLAUDE_MANAGER_SPEC routing table | quote |
| 5 | CLAUDE.md gates carried: run_all_tests --quick; new tests fail first; no in-place executor/live_runner edits; .new staging; no mainnet; no keys | quote |
| 6 | Ownership-claim line for any execution/ or layers/alerts/ .new staging | quote |
| 7 | Session record uses the 14-field template (sessions/README.md) | quote |
| 8 | Verify block names TASK / DONE / VERIFIED / MISSED | quote |
| 9 | 03_FILE_INDEX row requirement stated for every new file | quote |
| 10 | LF-only, no BOM; no Dumps/ path (Dumps/ is gitignored; CC cannot read it) | quote |

## CC-ONLY

- Deliverable path named. A no-writes prompt wastes the cloud budget.
  Cost 2026-10-01:  lost to a no-writes chart read.
- Checkpoint commits, not one at the end. Protects against container
  reclaim. Cost 2026-10-01: 1800Z chart-read lost 75 lines.
- No Maven, no LAN, no F:\\\\, no .secrets/, no .env.
- Branch created by harness, recorded as branch_alias. Do not create
  cloud/work.

## CL-ONLY

- Branch fast-track. Never master. Never push, merge, rebase, reset.
- Live-path files (auto_trader, position_manager, daily_loss_monitor,
  live_runner_cli) are never edited in place. Stage .new. Supervisor
  restarts.
- HALT files and open trades off limits to builders.

## STEP -1 - SAME-TURN VERIFICATION (before Step 0)

No prompt is printed to the operator until every disk claim inside it
has been read from disk in the same turn that the prompt is written.
On the DSA chat surface, "same turn" means: run one verification block,
receive the paste, then compose the prompt. No exceptions for small
prompts, no exceptions for prompts "mostly the same as last time."

A prompt is not composed from: prior pastes in the session, handoffs,
ledger entries, or earlier work by other surfaces. Those are read as
hypotheses. They are not evidence.

Every claim in the prompt carries one of three tags, in the prompt
itself or in the conformance table above it:

| Tag | Meaning |
|---|---|
| VERIFIED <YYYY-MM-DDTHH:MMZ> | read from disk this turn, receipt in the session |
| OPERATOR-SET | value supplied by the operator, not invented |
| UNVERIFIED | not read this turn; stated as a limit, not a fact |

A claim with none of the three tags is a defect. Fix before delivery.

Cost of the 2026-10-02 failures (two in one day):
  - Claimed 13 Fabio v3 files. Disk had 14.
  - Invented a 500K/100K token cap.
  - Invented four "do not read" restrictions.
  - Said a prompt was verified when it was composed from earlier pastes.

The cost of getting it right is one verification block per prompt.
The cost of getting it wrong is a burned Opus session. The trade is
not close.


## STEP 0 - SURFACE AND PERMISSION (before any other check)

Answer both, in the prompt itself, before composing anything else.

| # | Item | Required | Failure mode |
|---|---|---|---|
| 0a | Surface: CC / CL / Opus on CL / Opus on CC / DSA / worker | operator words | inferring the surface |
| 0b | Permission: may edit code, may run Maven/pytest, may commit, may push | operator words | inventing a restriction |

A restriction that appears in the prompt but not in the operator's words is a defect.
The words "do not", "never", "must not", "cannot", and any capability limit
each require a quote from the operator. If either item is unknown, ask one
question and stop. Do not default to the restrictive option.

Cost of the 2026-10-02 failure: an Opus CL prompt was written as plan-only
with "You do not edit code. You do not run commands." The operator was running
Opus on CL (disk, Maven, code). The session spent its budget for zero artifacts.
One question would have prevented it.


## NEVER INVENT BUDGET

DSA never states a numeric usage percent, budget cap, token cap, or dollar pool in any
prompt. Session Manager governs usage. Operator supplies a value only when the operator
chooses to. No default. No "85 assumed". No "operator hint" placeholder. The budget
row exists in the delivered tables only when the operator supplied a value this session.

## THREE QUESTIONS (every prompt answers all three, in the prompt itself)

| # | Question | Evidence |
|---|---|---|
| 11 | Operator-supplied budget only. Omit if the operator gave none. DSA never states a cap. | operator words, or omit |
| 12 | Is the prompt end to end? | yes / no + list of missing pieces |
| 13 | Does the prompt ask to save files and commit timely? | save cadence + git or no-git instruction |

A prompt missing one of the three is rejected. Do not deliver it.

## DELIVERY FORMAT (prompt printed to screen; format tables may be saved)

Every CC / CL / worker prompt is delivered as two blocks, in order.
The prompt itself is printed to screen only. Nothing under research/
or Dumps/ unless the operator says save.

Block 1 - header tables.

### Verified facts (read from disk this turn, YYYY-MM-DDTHH:MMZ)

| # | Fact | Source line or command output |
|---|---|---|

Above the Session table. Every disk claim in the prompt appears here or is
tagged UNVERIFIED. No prompt printed without this block filled. The block
carries the timestamp of the paste that supplied the facts.


### Session
| Field | Value |
|---|---|
| Session type | CC / CL / Opus / ... |
| Account | A / B |
| Model | ... |
| Effort | low / medium / high |
| Ultracode | off / on |
| Estimated work | ... |
| Budget cap | OPERATOR-SUPPLIED only. Omit if none given. Session Manager routes. |
| Subagent cap | 0..3 |
| Batch size | 1..3 |
| Commit cadence | per step / per wave / end / n/a |
| Deliverable path | ... |
| Gate | ... |

### Conformance
| # | Check | Status | Evidence |
|---|---|---|---|
| 1..10 | from BEFORE DELIVERING table | PASS / FAIL | quote |
| 11 | Operator-supplied budget (present only if operator provided one) | | |
| 12 | End to end | | |
| 13 | Save and commit cadence | | |

### Expected outputs
| Path | Kind | Lines (est) |
|---|---|---|

Block 2 - the prompt itself, in a fenced block tagged text, ready
to copy whole. No commentary inside the fence. At most one line of
commentary between the two blocks, stating the operator action.


## MANDATORY LINES IN EVERY CL PROMPT (added 2026-10-02, operator direct)

Three items appear in every CL prompt. No CL prompt ships without all three.

1. Process spawning. Add this line to the prompt:
   "CL on the desktop runs commands as subprocesses (python, PowerShell, git, Maven).
   Spawn whatever child process the task needs, per Session Manager routing
   (SURFACE_POLICY 3b). Do not refuse or stall a task because it requires spawning.
   Spawning is expected; stopping to ask whether spawning is allowed is a defect."

2. Operator proxy, verbatim (operator words, spelling preserved):
   "Use my proxy when needed - Incase i forget - Claude must not stop and eat up
   my money without outputting work!"
   Meaning: the operator's standing authorization covers proxy use and any question
   the operator has already pre-answered. When the task is authorized and the tool
   exists, run it. Do not halt to re-ask an authorized question. A stop that produces
   no artifact is the exact failure this line forbids.

3. Printing and continuity. Every CL prompt carries the PRINTING section:
   - At the start of each task, print one line: "== T<n> <task short name> ==".
   - After each task, print one line: "T<n> <PASS|FAIL|BLOCKED> <one-line result>".
   - Between tasks, print the next task's name and what it will do, in one line.
   - Do NOT wait for operator acknowledgment between tasks. Continue to the next task.
     An authorized session runs to completion. Stopping to confirm is the exact
     failure the operator-proxy line forbids.
   - Stop only on: BLOCKED (needs a fact the session cannot obtain), FAIL (gate),
     or operator interruption.
   No prompt ships without this section.

## CONTINUOUS EXECUTION (added 2026-10-02, operator direct)

A DSA-composed prompt never contains:
- "operator confirms or overrides" (except when a genuinely blocking choice exists,
  named in the prompt as the only stop).
- "wait for the operator" between tasks.
- "if you have any questions, stop and ask".

Default is auto mode (SURFACE_POLICY 0): the session acts, logs it, and continues.
The session stops only on BLOCKED (missing fact it cannot obtain), FAIL (gate), or
operator interruption. Any prompt that tells it to stop between steps is a defect.

## PROMPT SHAPE

- Line 1: session ID with -CLD- for CC or -CLI- for CL.
- Line 2: only present when the operator supplied a value this session. Never assume.
- Budget gate first (SURFACE_POLICY s3).
- Boot section: files, by line range.
- One task per prompt. One wave of children. Cap 3.
- Hard rules carried verbatim from CLAUDE.md.
- Every claim in the prompt carries file:line or a proof path.
- End with the four-line verify block template.

# END
