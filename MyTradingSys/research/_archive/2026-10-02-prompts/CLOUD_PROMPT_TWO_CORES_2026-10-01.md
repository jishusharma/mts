# CLOUD SESSION PROMPT: TWO CORES + WIRING + REVALIDATION FIXES
# Written 2026-10-01 by MTS-2026-10-01-1755Z-DSA-COO.
# Revised at 2026-10-02: real live_runner_cli path; budget-tier branch;
# new-tests-fail-first rule; ownership claim for execution/ and
# layers/alerts/; 03_FILE_INDEX row requirement; verify-block template;
# child tier = cheapest workable; one wave of 3, cap 3.

You are a cloud Sonnet session. One task. Deliverables committed.
Checkpoint commits, not one commit at the end. Reason: on 2026-10-01 the
1800Z chart-read session lost 75 lines of work to a container reclaim
because its brief asked for one commit after all steps.

Line 1 of your reply: session ID MTS-YYYY-MM-DD-HHMMZ-CLD-BLD-two-cores
Line 2: usage percent from chat header, or "85 assumed" if unreadable.

## BUDGET

Never refuse work for budget. Work to completion.
If usage is at 95 percent or above (5 percent or less remaining), commit
and push immediately, then continue with a commit after each step. At 1
percent remaining, still work.

At 85 percent or above: prefer one session reading by range over subagent
fan-out. Do not stop. Do not skip a wave.

## BOOT (read by line range)

- MyTradingSys/system/CLOUD_INBOX.md (all lines). Act on any note
  addressed to this session. Otherwise write "no note addressed to this
  session".
- CLAUDE.md (full, 37 lines). Hard rules apply.
- MyTradingSys/system/SURFACE_POLICY.md (full).
- MyTradingSys/system/sessions/README.md.
- MyTradingSys/system/sessions/MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio.md (shape).

Branch: harness assigns claude/<name>. Record as branch_alias.
Do not create cloud/work. Operator cherry-picks.

## READ THESE (architecture + audits)

- MyTradingSys/research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md (doctrine).
- MyTradingSys/PROJECT_VISION.md (ADD-ON, ISOLATE FIRST, PEERS).
- MyTradingSys/research/fast_track_2026-09-27/WIRING_MAINTENANCE_AUDIT_2026-10-01.md.
- MyTradingSys/research/_archive/loose_2026-10/REVALIDATION_ACTIONS_2026-10-01.md (W1-W8).
- MyTradingSys/research/_archive/loose_2026-10/HANDOFF_FOR_CLAUDE_2026-10-01.md (W1-W8 work items).
- MyTradingSys/research/_archive/loose_2026-10/FABIO_PROVENANCE_AUDIT_2026-10-01.md.
- MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md.
- MyTradingSys/execution/auto_trader.py (lines 1-100 for config and
  source routing).
- MyTradingSys/backtest/layers/alerts/live_runner_cli.py (the file the
  1800Z chart-read cited; the path MyTradingSys/layers/live_runner_cli.py
  does NOT exist).
- MyTradingSys/backtest/layers/rsi/ (RSI layer modules and tests).

## WAVE 1: THREE TABLES (1 subagent, three sections, one return)

Cap 3 children per wave. Wave 1 = 1 child. Brief 20 lines or fewer,
files and line ranges, this task. Child reads only its brief, returns
tables only, no prose.

Section W1. WIRING CHECK. Every row in WIRING_MAINTENANCE_AUDIT.md
  section 1, marked OK / BROKEN / MISSING with file:line at current HEAD.
  Use the real live_runner_cli.py path above.
Section W2. TEST GAP INVENTORY. For each of the 8 engine files in the
  T037 row of BUGS.md, list tests that exist and tests that are missing.
Section W3. REVALIDATION TABLE. For each of W1-W8 in
  REVALIDATION_ACTIONS_2026-10-01.md, mark DONE / PARTIAL / NOT-STARTED
  with evidence file:line.

Commit checkpoint 1 with trailer. Push.

## WAVE 2: FIX PASS (1 subagent, Sonnet)

Scope: smallest fix for each of the top 5 BROKEN or MISSING items from
wave 1. One file per fix, staged as <file>.new under the target
directory. One-line acceptance check per fix.

Before staging any .new under a path matching */execution/* or
*/layers/alerts/*, append one line to
MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_LOG.md claiming
ownership: session ID, path, expected end. This is the CLAUDE.md rule
"one session owns execution/ or layers/alerts/ at a time".

New tests must fail on the pre-change code at least once. CLAUDE.md gate.
Include the failing run in the fix description.

No executor.py edits. No live_runner_cli.py edits; stage .new only.

Commit checkpoint 2 with trailer. Push.

## WAVE 3: TWO-CORE SCAFFOLD (1 subagent, spec only, no code)

MyTradingSys/research/TWO_CORES_SCAFFOLD_<YYYY-MM-DD>.md
  Sections:
    1. Current state of each core (Tom, Fabio) with file paths.
    2. What changes make each a compiled core, one by one.
    3. Consensus writer design (jsonl path, fields, hook point).
    4. RSI observation block design (TFs, fields, snapshot position).
    5. Switchability config block shape.
    6. Migration order (first, second, third).
  Every claim cites file:line. Write "unknown" where evidence is absent.

Commit checkpoint 3 with trailer. Push.

## DELIVERABLES

MyTradingSys/research/TWO_CORES_READINESS_<YYYY-MM-DD>.md
  - W1, W2, W3 tables; merged priority list; top-5 fix descriptions
    with acceptance checks.
  - LF, no BOM, first line names this session.
MyTradingSys/research/TWO_CORES_SCAFFOLD_<YYYY-MM-DD>.md
  - The scaffold from wave 3.
MyTradingSys/system/sessions/<session ID>.md
  - Template from sessions/README.md, 14 fields.
  - model = see-chat (harness policy keeps model ids out of artifacts).
  - predecessor = none (no prior -CLD-BLD record exists). If one
    appears, use the newest.
MyTradingSys/system/CLOUD_INBOX.md
  - Remove any note addressed to this session. Append one line:
    - <UTC> | from: <session ID> | two cores readiness + scaffold |
      done when: TWO_CORES_READINESS committed
MyTradingSys/system/03_FILE_INDEX.md
  - Append one row per new file above. Use the existing row format and
    cite this session ID in the origin column.
MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_INBOX.md
  - Append one entry: session ID, top-5 fix list, one-line priority.

Commit trailer on every commit: MTS-Session: <session ID from line 1>.

## GATES

Run scripts/dev/run_all_tests.py --quick if any committed file type
requires it. Report what ran and its result. Docs-only commits likely
do not need it. OUTPUT_TOKENS must fit the whole reply.

## CONSTRAINTS

- Read committed refs. No writes to main. No Maven. No LAN. No F drive.
- Every claim carries file:line or TOM-/FR- id.
- Write unknown where evidence is absent. Never infer a rule.
- No new extractions in this task.
- Stop after deliverables.

## VERIFY BLOCK (exactly four lines at end)

TASK: <one line>
DONE: <one line>
VERIFIED: <mechanical | routed | unverifiable-on-this-surface; name it>
MISSED: <anything dropped, or none>

# END