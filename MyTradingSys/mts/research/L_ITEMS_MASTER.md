# L-ITEMS MASTER
# Purpose: single source of truth for all L-numbered open loops.
# Built: 2026-09-15 from session_log.json + NEXT_SESSION_HANDOFF.md + SESSION_ENTRY.md + apparatus_fixes.md
# Rule: any L-number with no supporting detail gets [NO EVIDENCE]. Do not fabricate.

## CLOSED

| ID | Date | Status | Description | Evidence |
|---|---|---|---|---|
| L4 | 2026-09-14 | CLOSED | Non-ASCII census of session_log.json. Confirmed clean: 4x U+00A7, 5x U+2014, 0 mojibake. | session_log.json 2026-09-14T09:15:06Z |
| L7 | 2026-09-14 | CLOSED | BUILD_REPORT regenerated via scripts/Build-Check.ps1. STATUS PASS. | session_log.json 2026-09-14T09:28:31Z |
| L9 | 2026-09-14 | CLOSED-DOC | State-machine counters survive restart. Doc note only, no code change. | apparatus_fixes.md + session_log.json 2026-09-14T09:29:58Z |
| L10 | 2026-09-14 | CLOSED | session_state.json.new was a manual edit never committed. Deleted. | session_log.json 2026-09-14T09:15:06Z |
| L11 | 2026-09-14 | CLOSED-ROOTCAUSE | start_trading_day.ps1 L411 gates invalidation block on $v.setup -match 'scalp'. Dead for non-scalp. Design decision deferred. | session_log.json 2026-09-14T09:29:58Z |

## OPEN / HELD

| ID | Date | Status | Description | Evidence |
|---|---|---|---|---|
| L5 | 2026-09-13 | HELD | [NO EVIDENCE] вЂ” referenced in NEXT_SESSION_HANDOFF.md L20 as "held" with no detail. | NEXT_SESSION_HANDOFF.md L20 |
| L6 | 2026-09-13 | HELD | [NO EVIDENCE] вЂ” same as L5. | NEXT_SESSION_HANDOFF.md L20 |
| L8 | 2026-09-14 | OPEN | stop_day.ps1 'stopped 2' false success. Needs live repro. | NEXT_SESSION_HANDOFF.md L79 + SESSION_ENTRY.md L37 |

## NEW (2026-09-15 disk audit)

| ID | Date | Status | Description | Evidence |
|---|---|---|---|---|
| L13 | 2026-09-15 | OPEN | proof-change alert trigger noise. start_trading_day.ps1:349 fires on any proof count change. 6 of 13 alerts in 17:00 hour fired purely on this. Fix: threshold-cross, not raw-count change. | start_trading_day.ps1:349 |
| L14 | 2026-09-15 | OPEN | Runtime SESSION_MANIFEST.json pointed at SESSION_PROMPT.md instead of DSA_SESSION_PROMPT.md. Boot would miss Rules 42-50. Fixed 2026-09-15. | SESSION_MANIFEST.json + DSA L32 |
| L15 | 2026-09-15 | OPEN | Root SESSION_MANIFEST.json was an orphan duplicate (no reader). Deleted 2026-09-15. | backup_session/ |
| L16 | 2026-09-15 | OPEN | Snapshot cadence has 12.7h + 4.25h gaps on 14 Sep. Worker audit must segment by gap. | data/snapshots/ |
| L17 | 2026-09-15 | OPEN | Alert numbering gap #6-12 in apparatus_log. Never logged. | apparatus_log.txt |
| L18 | 2026-09-15 | OPEN | Apparatus silent exit at 13:23:20. finally block ran, no error to log. Needs repro. | apparatus_log.txt |
| L19 | 2026-09-15 | OPEN | DSA_SESSION_PROMPT.md had duplicate ## 13. Renamed to ## 15 on 2026-09-15. | DSA_SESSION_PROMPT.md |
| L20 | 2026-09-15 | OPEN | apparatus_fixes.md had # END marker mid-file with post-END appends. Rebuilt 2026-09-15. | apparatus_fixes.md |
| L21 | 2026-09-15 | CLOSED | runtime SESSION_PROMPT.md orphan resolved. Deleted with two siblings (backup: backup_session/prompt-orphans-20260915-185432). Content merged into DSA_SESSION_PROMPT + USER.md. Generator added: scripts/start-session.ps1. Alias mts-start. | 2026-09-15 session |
| L22 | 2026-09-15 | CLOSED | Rule 50 duplicate: market_state_rules.md == proof_requirements_formatted.md (57KB each). Deleted the latter 2026-09-15. Rule 50 gate now satisfied. | L_ITEMS_MASTER.md |
| L23 | 2026-09-15 | CLOSED 2026-09-16 | Dumps\kimi_*.md renamed to dump_*.md. Stale DUMP_*.md moved to backup. Legacy tool name removed from scripts, prompts, and docs. | 2026-09-16 session |
| L24 | 2026-09-15 | CLOSED | Mojibake claim in NEXT_SESSION_HANDOFF.md did not reproduce. Byte-level check of 5 declared files: 0 hits of C3 A2 E2 80 9D. L4 (prior viewer-artifact closure) stands. | Phase A A9 2026-09-15 |
| L27 | 2026-09-16 | OPEN | MTS_DICTIONARY.md Authority column has mojibake (Cyrillic-decoded UTF-8). Cosmetic. Fix by re-encoding source or accepting and moving on. | 2026-09-16 boot paste |
| L26 | 2026-09-16 | CLOSED 2026-09-16 | Root cause: computeCvdSlope gated on 40 samples (40 min warmup) and did not restore series from disk. Fixed: CVD_MIN_SAMPLES=10 with adaptive half-window, plus denom guard. Verified live. | StateCodeEmitter.java 20260916 |
| L25 | 2026-09-16 | OPEN | US cash open classifier uses fixed hour 13.5 UTC. Correct for DST (EDT). Wrong for winter (EST opens 14:30 UTC). Fix: compute DST per date or read from a season table. Needs 3-snapshot proof before any code change. | src\main\java\datafeed\MarketDataSnapshot.java line 761 |
| L28 | 2026-09-16 | OPEN | Loop exit orphans mvn/java child. start-trading-day.ps1 finally stops the powershell wrapper PID but not the java child. Repro: Ctrl+C the loop, Get-Process java shows 1. Fix candidate: match CommandLine datafeed.Main statemachine inside finally, stop child before wrapper. Needs its own test, no Rule 32 gate. | apparatus_log.txt 11:41:02 + 13:23:20; live repro 11:50:23 |
| L29 | 2026-09-16 | OPEN | VP shape classifier returns B on nearly every block. Rule in buildVp: second-peak > 60% of POC peak -> B; else D if left/right volume ratio 0.8-1.2; else P. Thresholds are screener inventions (schema v1.2.0 already says so). Downstream: SetupCandidatesBuilder.classifyState reads daily_vp.shape first; if B, state=balance always. Affects candidate generation, not the trend override. Fix: derive shape from Tom-consistent structure, or remove the balance shortcut from classifyState. Classifier fix not Rule 32 gated; any change wired into state classification is. | src/main/java/datafeed/MarketDataSnapshot.java buildVp; snapshots 2026-09-16 |

## NO EVIDENCE

L1, L2, L3, L12 вЂ” referenced nowhere in current disk state. Either never created or deleted. Treat as non-existent.

# END
