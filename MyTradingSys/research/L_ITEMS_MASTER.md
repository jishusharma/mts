# L-ITEMS MASTER
# FROZEN 2026-09-17. Live bug list is BUGS.md. This file is history.
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
| L5 | 2026-09-13 | HELD | [NO EVIDENCE] - referenced in NEXT_SESSION_HANDOFF.md L20 as "held" with no detail. | NEXT_SESSION_HANDOFF.md L20 |
| L6 | 2026-09-13 | HELD | [NO EVIDENCE] - same as L5. | NEXT_SESSION_HANDOFF.md L20 |
| L8 | 2026-09-14 | OPEN | stop_day.ps1 'stopped 2' false success. Needs live repro. | NEXT_SESSION_HANDOFF.md L79 + SESSION_ENTRY.md L37 |

## NEW (2026-09-15 disk audit)

| ID | Date | Status | Description | Evidence |
|---|---|---|---|---|
| L13 | 2026-09-15 | OPEN | proof-change alert trigger noise. start_trading_day.ps1:349 fires on any proof count change. 6 of 13 alerts in 17:00 hour fired purely on this. Fix: threshold-cross, not raw-count change. | start_trading_day.ps1:349 |
| L14 | 2026-09-15 | OPEN | Runtime SESSION_MANIFEST.json pointed at SESSION_PROMPT.md instead of DSA_SESSION_PROMPT.md. Boot would miss Rules 42-50. Fixed 2026-09-15. | SESSION_MANIFEST.json + DSA L32 |
| L15 | 2026-09-15 | OPEN | Root SESSION_MANIFEST.json was an orphan duplicate (no reader). Deleted 2026-09-15. | backup_session/ |
| L16 | 2026-09-15 | OPEN | Snapshot cadence has 12.7h + 4.25h gaps on 14 Sep. Worker audit must segment by gap. | runtime_data/snapshots/ |
| L17 | 2026-09-15 | OPEN | Alert numbering gap #6-12 in apparatus_log. Never logged. | apparatus_log.txt |
| L18 | 2026-09-15 | OPEN | Apparatus silent exit at 13:23:20. finally block ran, no error to log. Needs repro. | apparatus_log.txt |
| L19 | 2026-09-15 | OPEN | DSA_SESSION_PROMPT.md had duplicate ## 13. Renamed to ## 15 on 2026-09-15. | DSA_SESSION_PROMPT.md |
| L20 | 2026-09-15 | OPEN | apparatus_fixes.md had # END marker mid-file with post-END appends. Rebuilt 2026-09-15. | apparatus_fixes.md |
| L21 | 2026-09-15 | CLOSED | runtime SESSION_PROMPT.md orphan resolved. Deleted with two siblings (backup: backup_session/prompt-orphans-20260915-185432). Content merged into DSA_SESSION_PROMPT + USER.md. Generator added: scripts/start-session.ps1. Alias mts-start. | 2026-09-15 session |
| L22 | 2026-09-15 | CLOSED | Rule 50 duplicate: market_state_rules.md == proof_requirements_formatted.md (57KB each). Deleted the latter 2026-09-15. Rule 50 gate now satisfied. | L_ITEMS_MASTER.md |
| L23 | 2026-09-15 | CLOSED 2026-09-16 | Dumps\kimi_*.md renamed to dump_*.md. Stale DUMP_*.md moved to backup. Legacy tool name removed from scripts, prompts, and docs. | 2026-09-16 session |
| L24 | 2026-09-15 | CLOSED | Mojibake claim in NEXT_SESSION_HANDOFF.md did not reproduce. Byte-level check of 5 declared files: 0 hits of C3 A2 E2 80 9D. L4 (prior viewer-artifact closure) stands. | Phase A A9 2026-09-15 |
| L27 | 2026-09-16 | OPEN | MTS_DICTIONARY.md Authority column has mojibake (Cyrillic-decoded UTF-8). Now detected by Build-Check.ps1 non-ASCII scan (added 2026-09-17). Fix pending. | 2026-09-16 boot paste; Build-Check 2026-09-17 |
| L26 | 2026-09-16 | CLOSED 2026-09-16 | Root cause: computeCvdSlope gated on 40 samples (40 min warmup) and did not restore series from disk. Fixed: CVD_MIN_SAMPLES=10 with adaptive half-window, plus denom guard. Verified live. | StateCodeEmitter.java 20260916 |
| L25 | 2026-09-16 | OPEN | US cash open classifier uses fixed hour 13.5 UTC. Correct for DST (EDT). Wrong for winter (EST opens 14:30 UTC). Fix: compute DST per date or read from a season table. Needs 3-snapshot proof before any code change. | src\main\java\datafeed\MarketDataSnapshot.java line 761 |
| L28 | 2026-09-16 | OPEN | Loop exit orphans mvn/java child. start-trading-day.ps1 finally stops the powershell wrapper PID but not the java child. Repro: Ctrl+C the loop, Get-Process java shows 1. Fix candidate: match CommandLine datafeed.Main statemachine inside finally, stop child before wrapper. Needs its own test, no Rule 32 gate. | apparatus_log.txt 11:41:02 + 13:23:20; live repro 11:50:23 |
| L29 | 2026-09-16 | CLOSED 2026-09-17 | VP shape classifier returns B on nearly every block. Rule in buildVp: second-peak > 60% of POC peak -> B; else D if left/right volume ratio 0.8-1.2; else P. Thresholds are screener inventions (schema v1.2.0 already says so). Downstream: SetupCandidatesBuilder.classifyState reads daily_vp.shape first; if B, state=balance always. Affects candidate generation, not the trend override. Fix: derive shape from Tom-consistent structure, or remove the balance shortcut from classifyState. Classifier fix not Rule 32 gated; any change wired into state classification is. | src/main/java/datafeed/MarketDataSnapshot.java buildVp; snapshots 2026-09-16 |

| L30 | 2026-09-16 | OPEN | context.ps1 reads Binance REST each call. Durable fix is kline_archiver feeding it locally. | context.ps1 20260916 |
| L31 | 2026-09-16 | OPEN | state_code_regime.json sibling is not read by StateCodeEmitter.java. Java merge deferred. | regime_classifier.py 20260916 |
| L32 | 2026-09-16 | CLOSED | BOM from Set-Content -Encoding UTF8. Fixed: Write-NoBom helpers, Build-Check scan, USER.md rule. 9 files cleaned. | apparatus_fixes.md 20260916 |

| I40 | 2026-09-17 | OPEN | Profile shape taxonomy does not match Tom. buildVp emits TWOPEAK / D / P. TWOPEAK is a rename of the old B, not a Tom term. D has zero hits in the entire corpus (no Tom transcript uses "D profile"). P appears in Tom as a directional move (UOBgXV20yCM, yWO8hVpRXeY, OUM9LYwL8eA) but is defined by price action, not by left/right volume ratio as the code does. Tom's actual vocabulary: balance profile, normal profile, bell curve, trend profile, normal variation profile, double distribution day, aggressive trend profile. Decision needed: rename to Tom's terms, or accept the current letters and mark them as screener proxies. Naming only. Not Rule 32 gated until the field is read by a verdict rule. | Revalidation 2026-09-17: grep "D profile" corpus zero hits; grep "distribution" only in double-distribution context; extract UOBgXV20yCM L331-338, yWO8hVpRXeY L38-45, yWO8hVpRXeY L476-482, OUM9LYwL8eA L140-145 |

## NO EVIDENCE

L1, L2, L3, L12 - referenced nowhere in current disk state. Either never created or deleted. Treat as non-existent.

# END

## NEW (2026-09-16 live session)

| ID | Date | Status | Description | Evidence |
|---|---|---|---|---|
| I21 | 2026-09-16 | OPEN | Ratio gate has no near-miss record. scalp_short @ vwap 13:48:15 UTC printed net reward-to-risk 1.95, failed 2.0 by 0.05, dropped next cycle. A one-tick miss is invisible in the log. Fix: record candidates with nrr >= 1.75 in the ledger even when suppressed. Rule 32 gated. | apparatus_log 13:48:19; chart 75815 rejection |
| I22 | 2026-09-16 | OPEN | Zones are not fixed. daily_vp.val moved 75599 -> 75584 -> 75599 -> 75619 -> 75584 across 13 cycles. Engine derives the zone live each cycle, so net reward-to-risk is computed against a moving target. Design question. | apparatus_log cycles 1-20 |
| I23 | 2026-09-16 | OPEN | Quad versus setup direction mismatch is not read. Alert #373 card reported quad=new_shorts (OI +0.450%, CVD -337, net delta 15m -324.5) while candidate was ct_long. Engine does not compare quad to setup direction. | last_alert.json ALERT #373 |
| I24 | 2026-09-16 | OPEN | session_timing_rules.md section 2 documents EST open times (US Cash Open 14:30-15:00, Pre-Market 13:00-14:30). Engine anchors DST-aware 13:30 UTC. File wrong half the year. Same class as L25. | session_timing_rules.md L22-46 |

| I26 | 2026-09-16 | CLOSED 2026-09-17 | B-profile definition contradiction. market_state_rules.md L50 says "B = balance (bell-shaped, volume concentrated at POC)." setup_type_rules.md L221 says "B Profile = Weakness at the Extreme" and quotes Tom. entry_timing_triggers.md uses B profile as a proof qualifier at extremes. setup_type_rules.md L549 already documents that Tom did not define B criteria. Rule L50 is the outlier and was likely invented to fill the documented gap. L29 classifier fix is blocked by this. Needs a human ruling: B = weakness at extreme (per Tom) or B = balance (per L50). | L50 vs L221 vs L549; grep 2026-09-16 |

| I27 | 2026-09-16 | OPEN | order_flow block (6 fields: trades_ratio, volume_ratio, speed_state, trades_per_sec, volume_per_sec, baselines) has no consumer. Grep of all scripts, python, java found zero readers. Producer cites DSA_TASK_013. Thresholds "provisional, not Tom-derived" per snapshot note. Fix: wire into a proof or delete. Wire later. | T2 audit 2026-09-16 |
| I28 | 2026-09-16 | OPEN | session block (15 fields: open, high, low, gap, initial_balance, range_position, day_type, sweep_flag, open_location) has no consumer. Grep found zero readers. Same as I27, same producer. | T2 audit 2026-09-16 |
| I29 | 2026-09-16 | OPEN | MarketDataSnapshot.java:1065 second builder path sets cvd_trade_flow_aligned = false with comment "live-only, set false." Two snapshot paths produce contradicting values for the same field. Needs repro and dedupe. | T2 audit 2026-09-16 |

## RULING 2026-09-16 on I27 and I28

Both blocks are gauges, not controls. Decision: leave them in production, do not delete.

Reason: the session block and order flow block feed operator readouts and dashboards. They are dead to the engine only. Deleting would invalidate handoff lines that promised the layer and lose the readouts. Cost of keeping is negligible.

What this closes: no more re-audit of the same question. Both blocks are classified.

What remains open: promotion path. If either block should become a control (a rule that moves a verdict), that is a new task, needs three-snapshot proof per Rule 32, and is not covered by I27 or I28.

I29 remains open. Two builder paths producing contradicting values for the same field is a defect, not a design question.

| I30 | 2026-09-16 | OPEN | Book imbalance instability. Six flips in six cycles: 0.25 -> 1.52 -> 8.14 -> 0.46 -> 1.65 -> 0.44. Hard contradiction gate in the verdict. Every flip flips the verdict. Fix: smooth over 5 cycles or drop from the contradiction rule. Rule 32 gated if wired into verdict. | apparatus_log cycles 20-35; snapshots 17:15-17:29 |
| I31 | 2026-09-16 | OPEN | Verdict flicker has no debounce. SETUP_FORMING -> WATCH -> SETUP_FORMING in four of eight cycles 17:12-17:19 UTC. Only the 180s cooldown suppresses popup spam. Same class as the state debounce just built. Fix: two-cycle verdict persistence like the state fix. File: scripts/core/start-trading-day.ps1. | apparatus_log cycles 17-24 |
| I32 | 2026-09-16 | OPEN | Log line "no change" is ambiguous. Prints when nothing changed AND when a change was suppressed by cooldown. Reader cannot distinguish. Fix: add a cooldown-suppressed variant. Cosmetic. | apparatus_log 17:13:20 vs 17:14:21 |

| I33 | 2026-09-16 | OPEN | OI field went dead at ~17:40 UTC. Ten consecutive snapshots read direction=flat, change_1h_pct=0.0, while CoinGlass chart showed OI moving 107.25K -> 107.55K. Two builder paths exist: fetchSnapshot (line 35, real values, worked at 14:50 with 0.45%) and fetchHistoricalSnapshot (line 913, hardcodes 0.0 at line 1134). Live loop calls fetchSnapshot. Either the OI source started failing silently, or the live method fell through. Needs repro: check oiChangePct source and default behavior on missing data. Impact: every OI read from 17:40 onward was wrong. Same class as I29 (dual builder). | live session 2026-09-16 17:40-17:50 |

| I34 | 2026-09-16 | OPEN | Sweep-entry rule missing. Counter-trade candidates use zone price as entry. Six setups today failed the 2.0 cap. All would clear with sweep wick extreme as entry. Tom method: enter at the sweep, not the level. Rule 32 gated. Today is snapshot 1 of 3. | apparatus_log 13:48-18:16 |
| I35 | 2026-09-16 | OPEN | Supervisor not running after manual restart. Exited 17:52:52 on stop flag. Loop restarted 18:15:33 without supervisor. Loop unmonitored overnight. | supervisor_log 17:52:52; apparatus_log 18:15:33 |
| I36 | 2026-09-16 | CLOSED 2026-09-17 | Log prints "STATE X -> X" with same value on confirmed state alerts. Alerts #391, #392, #394. Cause: $lastState updated before alert fires on cycle 2. Fix: add $pendingStateFrom. Cosmetic. | apparatus_log 17:39, 18:24, 18:40 |

| I37 | 2026-09-16 | OPEN | Binance OI data path. Historical endpoint accepts 5-min minimum. Live endpoint pollable at 1-min. CoinGlass builds 1-min candles from live polls. MTS reads snapshot aggregate. Reconciliation: poll /fapi/v1/openInterest each cycle, store samples, build own 1-min series. Would match CoinGlass and likely fix I33. | Binance docs; CoinGlass Binance_BTCUSDT chart 2026-09-16 |
| I38 | 2026-09-16 | OPEN | Two-phase OI/CVD/price pattern has no named form in Tier 1 or Tier 2 literature. No base rate. OI is symmetric. Resolution requires funding rate sign + taker buy/sell ratio + liquidation stream. First two are in the snapshot. Third deprecated 2026-09-12. Track 3 sessions before any rule. Rule 32 gate. | Grok + Claude research 2026-09-16 |

| I39 | 2026-09-16 | OPEN | session_end_logs.md is written by StateCodeEmitter.java line 443. File header says "Archive of all session end logs." Reality: 886 of 1460 lines are state-machine tick transitions. Wrong file for the writer. Untracked in git, absent from 03_FILE_INDEX.md, absent from boot. 132KB grown over 9 days. Two options: point the emitter at a new file (e.g. state_code_log.jsonl) and keep the archive for session closes only, or rename the file to match the content and index it. Decide retention policy first. | StateCodeEmitter.java:443; file 2026-09-16 |
