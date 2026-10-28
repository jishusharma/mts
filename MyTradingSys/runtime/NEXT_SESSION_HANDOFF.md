# NEXT SESSION HANDOFF
# Written 2026-10-01T05:56Z by MTS-2026-09-30-1733Z-COORD.

STATUS: Loop UP. Build PASS 2026-10-01T05:55:58Z. HEAD f3e94b0.
Bugs 136 rows. Index 30 open IDs. Working tree clean on main.

## LANDED THIS SESSION (main)

- USER.md line 11: code fence language tag rule. f574b4f
- CBP mts_queue desktop consumer + test. Handshake PASS. 2d20a5c
- T060 low-vol, T061 WaveTrend LazyBear. 6b099b2
- Merge cloud/work 21 commits: provenance rule, angle research,
  Fabio v3 spec, RSI + grid runners, testnet status script,
  Tom line-by-line, MISSING_PIECES. 7fbf178, b8867e4
- 13 DSA recon outputs promoted from .new to .md. 01e2649
- B080 pace bug, B081 fee-source conflict, B082 qwen_feeder
  missing. e9251d4, 0757810, e84e379, f3e94b0
- MTS testnet status scheduled task registered daily 08:00.
- LESSONS_LEARNED: 5 rules from this session.

## CLOUD/WORK

origin/cloud/work = 02fc346. 0 commits past main. Fully merged.
Credits: $42 of $100, expire 2026-11-05. No spend since.

## OPEN QUEUE (top items)

- Tom engine rebuild spec: provenance audit shows 36 of 76
  parameters have no Tom source. 2:1 net rule miscited. No
  spend started. Operator to say when.
- Book-imbalance 0.0 fix: live long-blocking. Approved 22:30Z.
  Supervisor-owned. Stage .new, four-step proof, restart.
- classify_msb fix: live cryptocred. Stage .new, supervisor.
- B081 fee-source: four fee sets. Needs single fees.py module.
- B080 dsa pace: stale pace file blocks worker. Workaround:
  move dsa_pace.json aside, restart worker.
- B082 qwen_feeder.cmd missing: task disabled. Operator
  decides write vs delete.
- NUC 2201-2203 (Fabio v3): lint clean, awaiting pack.
  Fabio spec v3.1 is landed on main.
- MISSING_PIECES_2026-09-30.md sections 0 and 4 not yet read.
- 2113 zAwEX_tRUfE recon: template deviation, content usable.
- Auto-mode rule on disk at SURFACE_POLICY.md sec 0 (125a64d).
  Not to be re-created.

## NEXT SESSION FIRST ACTION

1. Read items/INDEX.md + BUGS.md open rows.
2. State ROLE (COORDINATOR). State MISSION. Act.
3. Operator picks one: Tom engine spec spend, B081 fee fix,
   book-imbalance 0.0 supervisor handoff, or MISSING_PIECES read.

## DO NOT MISS

- Doc test test_2_no_forbidden_refs forbids eight repository-command
  phrases in items/ and system/. See test_2_no_forbidden_refs in
  MyTradingSys/tests/docs/test_integrity.py for the current list.
  Use plain verbs: staged, committed, checked out, history,
  working tree.
- .new files under extracts/ are gitignored (.gitignore L4).
- PowerShell $pid is reserved. Use $procId.
- Cross-branch diff uses three dots. Two-dot shows phantom
  removals.
- Never commit on Build-Check FAIL.
- DSA worker needs Chrome on 127.0.0.1:9222, profile
  F:\MTS\dsa\chrome-profile. Start chrome script, then worker.
- BUILD_REPORT.md stays dirty between sessions (loop writes).
  Commit before any merge.

## HARD RULES (carried)

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- Critical files: hash, edit, hash, diff.
- Read target line from disk same turn before composing anchor.
- MarketDataSnapshot.java CRLF. math_object_builder.py CRLF.
  SetupCandidatesBuilder.java LF.
- PROJECT_VISION doctrine: modules never gate core.
- Every engine/layer parameter comes from the trader's own
  words (transcript quote + file:line), or it does not exist.
  Unsourced = NO-SOURCE: flag, remove or replace, never tune.
  SAFETY limits exempt.

# END
