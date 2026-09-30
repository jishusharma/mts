# NEXT SESSION HANDOFF
# Written 2026-10-01T00:30Z by MTS-2026-09-30-1733Z-COORD.

STATUS: Loop UP. Build PASS 2026-09-30T19:25:12Z. HEAD e9251d4. Bugs 134 rows. Index 28 open IDs.
Working tree clean on main. 13 DSA recon tasks done this session.

## LANDED THIS SESSION

- USER.md line 11: code fence language tag rule. Commits f574b4f.
- MyTradingSys/queue/consumer.py + test: CBP mts_queue desktop consumer,
  ack-only, utf-8-sig tolerant. Commit 2d20a5c. Handshake with CBP PASSED.
- T060 low-volatility anomaly, T061 WaveTrend LazyBear. Commit 6b099b2.
- DSA backlog section D ticked; 13 recons run; gate log rows added. f658dee,
  e9251d4.
- B080 dsa_worker hourly-cap bug filed. e9251d4.

## CBP SIDE

- CBP cloud/work = e3e7a5e handshake ack; 19ea4f6 handshake PASS record.
- mts_queue/acks/handshake_test_2026-09-30.json written by the desktop consumer.
- mts_queue and docs/COMMON.md ownership: CBP. MTS read + write to acks only.
- Consumer is read-only, ack-only, no live import. Wiring to auto-trader NOT
  authorized. Stays that way until supervisor accepts.

## CLOUD/WORK STILL UNMERGED

origin/cloud/work = e6601af. Two commits past 304cc13. Not merged.
Content: MISSING_PIECES report, 03_FILE_INDEX header, SURFACE_POLICY, CLOUD_INBOX,
session registry, Fabio v3 spec, RSI runners, bracket grid, formula audit,
TOM_CORE_BT review. All merged into main already via selective commits.
Only 74e4aa9 MISSING_PIECES and 304cc13 header fix remain unmerged.

## OPEN QUEUE (top items)

- B080 dsa_worker pace bug (MED). Stale pace file blocks worker for hours.
  Workaround: move dsa_pace.json aside, restart worker.
- 2113 zAwEX_tRUfE recon: content complete, template deviation on ## Portability
  heading. Usable but verifier flags it.
- MISSING_PIECES_2026-09-30.md read on desktop: sections 0 and 4 not yet read.
- Auto-mode rule for cloud: Path B not yet applied. Awaiting operator pick.
- 4 fee sets in code, not 2. B080 on fee conflict is a different B080. Need
  to resolve naming or the conflict is invisible. CORRECTION: B080 is the pace
  bug now. The fee conflict does not yet have an id.
- classify_msb live cryptocred alert bug: staged as .new, belongs to supervisor.
- Tom backtest artefact: proof counts top at 5 not 6; all 19 live signals short.

## NEXT SESSION FIRST ACTION

1. Read items/INDEX.md + BUGS.md open rows.
2. Read DSA_SESSION_PROMPT.md section 3 rules 8-9.
3. State ROLE (COORDINATOR). State MISSION. Act.
4. Operator picks one: fee-set consolidation, B080 pace fix, MISSING_PIECES read,
   or the DSA recon .new files triage.

## DO NOT MISS

- .new files under extracts/ are gitignored (*.new in .gitignore L4).
  Proposals live on disk, not in repo. Deliberate.
- DSA worker needs Chrome on 127.0.0.1:9222 with profile F:\MTS\dsa\chrome-profile.
  Restart order: start-dsa-chrome.ps1, then start-dsa-worker.ps1.
- Two dsa_pace bugs already seen: file can be blocked by stale entries;
  restart worker if "paced" for more than min_gap_s + poll_wait_s.
- $pid is a reserved PowerShell variable. Use $procId.

## HARD RULES (carried)

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- Critical files: hash, edit, hash, diff.
- Read target line from disk same turn before composing anchor.
- MarketDataSnapshot.java CRLF. math_object_builder.py CRLF. SetupCandidatesBuilder.java LF.
- PROJECT_VISION doctrine: modules never gate core.

# END
