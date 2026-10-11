# MTS-2026-10-02-1710Z-CLI-SUP-prompt-shape
surface: CLI
host: JIS-NB
account: A
model: claude-sonnet-5-5
role: SUP
branch: fast-track
branch_alias: none
predecessor: MTS-2026-10-02-1700Z-CLI-SUP-verdict-parity
lanes: none (no subagents)
started: 2026-10-02 17:10Z
ended: 2026-10-02 17:25Z
status: closed
commits: see trailer MTS-Session
handoff: none; operator moves the tag once after both parallel sessions close

## Scope (operator brief, 2026-10-02)
- T1 compress PROMPT_CONFORMANCE_CHECKLIST.md to <= 100 lines. T2 CLAUDE.md "What a CL prompt carries". T3 DSA_SESSION_PROMPT.md s3 step 11. T4 move stray *PROMPT* files to _archive. T5 close.
- Operator authorization (verbatim): "why create such a big prompt?"; "Prompt must always be pasted on my screen - never written to disk";
  "it carries info like which file is where and the current state of MTS"; "The actual Task as per protocol!".
- Ownership: the checklist, CLAUDE.md, DSA_SESSION_PROMPT.md section 3, the straggler move. Not runtime/, execution/, backtest/.
- Git: runs parallel to another session on the same tree; add only exact paths written; no gitsnap, no tag move.

## Results
- T1 PASS checklist 233 -> 98 lines (backup .pre_prompt_shape, gitignored). Kept STEP -1, STEP 0, DELIVERY FORMAT, MANDATORY LINES, CONTINUOUS EXECUTION, PROMPT SHAPE. Deleted BEFORE DELIVERING table, CC-ONLY, CL-ONLY, PROMPT TYPES, failure history. Budget contradiction fixed: operator-set only, no budget gate line in the prompt. Delivery no longer says tables may be saved.
- T2 PASS CLAUDE.md "What a CL prompt carries" (4 lines).
- T3 PASS DSA_SESSION_PROMPT.md section 3 step 11.
- T4 PASS 11 files research/ -> research/_archive/2026-10-02-prompts/ (git mv), 2 files Dumps/operator/context/ -> Dumps/_archive/2026-10-02-prompts/. All mtime < 16:00Z.
- T5 gate: run_all_tests --quick Step 4 FAIL on test_integrity::test_2_no_forbidden_refs, hit only in sessions/MTS-2026-10-02-1720Z-CLI-MON-diagnostics.md:14 (another session's record). Not this session's file; not edited here. Owner should reword that line.
