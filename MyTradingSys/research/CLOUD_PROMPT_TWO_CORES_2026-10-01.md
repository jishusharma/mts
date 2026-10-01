# CLOUD SESSION PROMPT: TWO CORES + WIRING + REVALIDATION FIXES
# Written 2026-10-01 by MTS-2026-10-01-1755Z-DSA-COO.

You are a cloud Sonnet session. One task. Deliverables committed.
Checkpoint commits, not one commit at the end. Reason: on 2026-10-01
the 1800Z chart-read session lost 75 lines of work to a container
reclaim because its brief asked for one commit after all steps.

Line 1 of your reply: session ID MTS-YYYY-MM-DD-HHMMZ-CLD-BLD-two-cores
Line 2: usage percent from chat header, or 85 percent assumed.

## BOOT (read by line range)

- MyTradingSys/system/CLOUD_INBOX.md (all lines). Act on any note
  addressed to this session. Write no-note if none.
- CLAUDE.md (full). Gates may apply. Hard rules apply.
- MyTradingSys/system/SURFACE_POLICY.md (full).
- MyTradingSys/system/sessions/README.md.
- MyTradingSys/system/sessions/MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio.md (shape).

Branch: harness assigns claude/<name>. Record as branch_alias.
Do not create cloud/work. Operator cherry-picks.

## READ THESE (architecture + audits)

- MyTradingSys/research/ARCHITECTURE_TWO_CORES_2026-10-01.md (doctrine).
- MyTradingSys/PROJECT_VISION.md (ADD-ON, ISOLATE FIRST, PEERS).
- MyTradingSys/research/fast_track_2026-09-27/WIRING_MAINTENANCE_AUDIT_2026-10-01.md.
- MyTradingSys/research/REVALIDATION_ACTIONS_2026-10-01.md (W1-W8).
- MyTradingSys/research/HANDOFF_FOR_CLAUDE_2026-10-01.md (W1-W8 work items).
- MyTradingSys/research/FABIO_PROVENANCE_AUDIT_2026-10-01.md.
- MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md.
- MyTradingSys/execution/auto_trader.py (lines 1-100 for config and source routing).
- MyTradingSys/backtest/layers/rsi/ (RSI layer modules and tests).

## SUBAGENTS: SONNET

Spawn up to 3 Sonnet subagents, one per check workstream.
Each gets its own brief of 20 lines or fewer. Each brief names
files and line ranges. Each subagent exits at task end. No
subagent reads a file not named in its brief. Each subagent
returns a table only, no prose.

Workstreams:
  W1 WIRING CHECK. Every wiring row in WIRING_MAINTENANCE_AUDIT.md
     section 1. Mark OK / BROKEN / MISSING with file:line at current
     HEAD. Also locate live_runner_cli.py (it is cited in the audit
     but does not exist at MyTradingSys/layers/live_runner_cli.py).
  W2 TEST GAP INVENTORY. For each of the 8 engine files in the T037
     row of BUGS.md, list what tests exist and what is missing.
  W3 REVALIDATION TABLE. For each W1-W8 item in REVALIDATION_ACTIONS,
     mark DONE / PARTIAL / NOT-STARTED with evidence.

Commit checkpoint 1 after W1 returns. Checkpoint 2 after W2.
Checkpoint 3 after W3. This way a reclaim loses at most one workstream.

## FIX PASS (after the three tables)

One Sonnet subagent. Scope: the smallest fix for each of the top 5
BROKEN or MISSING items from the merged tables. One file per fix,
staged as file.new under the target directory. Include a one-line
acceptance check per fix. No executor.py edits. No live_runner_cli
edits until its real path is confirmed in W1. Execution/ and
layers/alerts/ edits stage .new only.

Commit checkpoint 4 after the fix pass.

## TWO-CORE SCAFFOLD (spec-only this pass)

One Sonnet subagent. Scope: a design document, not code.

MyTradingSys/research/TWO_CORES_SCAFFOLD_<YYYY-MM-DD>.md
  Sections:
    1. Current state of each core (Tom, Fabio) with file paths.
    2. What changes to make each a compiled core, one by one.
    3. Consensus writer design (jsonl path, fields, hook point).
    4. RSI observation block design (which TFs, which fields, where
       in the snapshot it goes).
    5. Switchability config block shape.
    6. Migration order (what to build first, second, third).
  Every claim cites file:line. Unknown where evidence is absent.

Commit checkpoint 5 after the scaffold.

## DELIVERABLES

MyTradingSys/research/TWO_CORES_READINESS_<YYYY-MM-DD>.md
  - W1 table, W2 table, W3 table, merged priority list, top-5 fix
    descriptions with acceptance checks.
  - LF, no BOM. First line names this session.
MyTradingSys/research/TWO_CORES_SCAFFOLD_<YYYY-MM-DD>.md
  - The scaffold from the section above.
MyTradingSys/system/sessions/<session ID>.md
  - Template from sessions/README.md. Same 14 fields as the 1604Z
    record. model = see-chat. predecessor = the 1604Z record unless
    a newer -CLD-BLD exists.
MyTradingSys/system/CLOUD_INBOX.md
  - Remove any note addressed to this session. Append one line.
MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_INBOX.md
  - Append one entry: session ID, top-5 fix list, one-line priority.

Commit trailer on every commit: MTS-Session: <session ID from line 1>.

## GATES

Run scripts/dev/run_all_tests.py --quick if any committed file type
requires it. Report what was run and the result. A docs-only commit
likely does not need it.

## CONSTRAINTS

- Read committed refs. No writes to main.
- No Maven. No LAN. No F drive.
- Every claim carries file:line or TOM-/FR- id.
- Write unknown where evidence is absent. Never infer a rule.
- No new extractions in this task. Architecture, wiring, tests,
  revalidation only.
- Stop after deliverables. Print the four-line verify block.

# END
