# BUGS AND TASKS

Single source of truth for defects and open tasks. Supersedes L_ITEMS_MASTER.md (frozen 2026-09-17) and
the OPEN section of apparatus_fixes.md. AUDIT_2026-09-17_TRACKER.md material defects folded in.

## RULES

1. Never edit ID, Opened, or Title.
2. Change status by replacing the Status cell. If the new status is CLOSED, add a Receipt.
3. Add a bug by appending one row at the end.
4. Never delete a row. Use WONTFIX.
5. The tables are the file. No prose outside this rules block and the two tables.
6. Tasks are numbered T-NNN. Same columns, same rules as bugs. Bugs stay B-NNN.

Status values (exact): OPEN, IN-FIX, BLOCKED, CLOSED, WONTFIX.
Severity values (exact): HIGH, MED, LOW, COSMETIC.
Receipt required when Status = CLOSED. Format: hash, test name, commit, or doc-only.
IN-FIX rows older than 14 days fail Build-Check.

## BUGS

| ID | Opened | Status | Severity | Title | Evidence | Receipt |
|---|---|---|---|---|---|---|
| B001 | 2026-09-13 | WONTFIX | LOW | L5 referenced as held no detail | L_ITEMS L5 | 2026-09-18: L5 phantom, no current reference. |
| B002 | 2026-09-13 | WONTFIX | LOW | L6 same as L5 | L_ITEMS L6 | 2026-09-18: L6 phantom, no current reference. |
| B003 | 2026-09-14 | CLOSED | MED | stop-day.ps1 reports false success | L_ITEMS L8 | 2026-09-18: lock path fixed to trading_day.lock; commit af1cfc5. Earlier miss: fix landed but row not closed. |
| B004 | 2026-09-15 | WONTFIX | LOW | Proof-change alert trigger noise | L_ITEMS L13; start_trading_day.ps1:349 | 2026-09-18: fires only on 3<->5 threshold crossing; correct by design. |
| B005 | 2026-09-15 | WONTFIX | LOW | Runtime manifest pointed at wrong prompt | L_ITEMS L14 | 2026-09-18: SESSION_MANIFEST.json points at DSA_SESSION_PROMPT.md; file exists on disk. Correct. |
| B006 | 2026-09-15 | WONTFIX | COSMETIC | Orphan duplicate root manifest | L_ITEMS L15 | 2026-09-18: no root SESSION_MANIFEST.json exists. Phantom. |
| B007 | 2026-09-15 | WONTFIX | MED | Snapshot cadence has 12.7h and 4.25h gaps | L_ITEMS L16 | 2026-09-18: gaps reflect loop-off windows; loop cadence 60s when armed. Not a defect. |
| B008 | 2026-09-15 | WONTFIX | LOW | Alert numbering gap 6-12 | L_ITEMS L17 | Cosmetic; ids assigned in order, gaps historical. |
| B009 | 2026-09-15 | WONTFIX | MED | Apparatus silent exit at 13:23:20 | L_ITEMS L18 | 2026-09-18: exit 1 at L273 logs ABORT first; 13:23:20 incident has APPARATUS END finally in log at 2026-09-14; not silent. |
| B010 | 2026-09-15 | WONTFIX | COSMETIC | Duplicate section header in prompt | L_ITEMS L19 | Verified 2026-09-18: 13 headers, all unique. No duplicate. |
| B011 | 2026-09-15 | CLOSED | COSMETIC | apparatus_fixes END marker mid-file | L_ITEMS L20 | doc-only 2026-09-18: stray append moved above # END |
| B012 | 2026-09-16 | WONTFIX | MED | US open fixed 13.5 UTC wrong in winter | L_ITEMS L25; MarketDataSnapshot.java:761 | 2026-09-18: code uses ZoneId.of("America/New_York") at L723,L825,L862,L887; timezone-correct. Stale ref only. |
| B013 | 2026-09-16 | CLOSED | COSMETIC | MTS_DICTIONARY Authority column mojibake | L_ITEMS L27 | hash 5CE01AA2->F05D3E0A; 30 sequences replaced |
| B014 | 2026-09-16 | WONTFIX | MED | Loop exit orphans mvn/java child | L_ITEMS L28 | 2026-09-18: Invoke-WithTimeout calls taskkill /T /F at L98,L108; process tree killed. No orphan path in code. |
| B015 | 2026-09-16 | WONTFIX | LOW | context.ps1 reads Binance REST each call | L_ITEMS L30 | 2026-09-18: duplicate of T029 |
| B016 | 2026-09-16 | WONTFIX | LOW | state_code_regime.json not read by Java | L_ITEMS L31 | 2026-09-18: regime is display-only; T018 WONTFIX. No consumer intended. |
| B017 | 2026-09-16 | WONTFIX | MED | Ratio gate has no near-miss record | L_ITEMS I21 | 2026-09-18: distance-tier cutoff at SetupCandidatesBuilder L71; near-miss record is observability only, no consumer. Reopen if needed. |
| B018 | 2026-09-16 | WONTFIX | HIGH | Zones move per cycle nrr against moving target | L_ITEMS I22 | 2026-09-18: VP recompute is inherent (fresh klines per cycle); zone prices stable for the cycles they rank. B025 debounce covers downstream flicker. |
| B019 | 2026-09-16 | WONTFIX | MED | Quad vs setup direction mismatch not read | L_ITEMS I23 | 2026-09-18: quad_classify is display-only; no engine consumer intended. |
| B020 | 2026-09-16 | CLOSED | MED | session_timing_rules.md documents EST all year | L_ITEMS I24 | doc-only: timezone note added session_timing_rules.md L24-26 2026-09-17 |
| B021 | 2026-09-16 | WONTFIX | LOW | order_flow block has no consumer | L_ITEMS I27 (ruled gauges) | 2026-09-19 code-verified: grep of scripts + python shows zero read of order_flow fields outside mts-watch display. Gauge by design. |
| B022 | 2026-09-16 | WONTFIX | LOW | session block has no consumer | L_ITEMS I28 (ruled gauges) | 2026-09-19 code-verified: 1 diagnostic reader (divergence_monitor.py L54 compares session objects for change detection); mts-dashboard displays fields. No engine consumer. Gauge by design. |
| B023 | 2026-09-16 | WONTFIX | MED | Two builder paths contradict cvd_trade_flow_aligned | L_ITEMS I29; MarketDataSnapshot.java:1068 | 2026-09-19 code-verified: live path L294-297 computes real value from cvd_recent.slope_1h + nd1m; historical path L1087 hardcodes false. Live loop consumes live path only. Not a contradiction. Receipt corrected from comment-based to code-based. |
| B024 | 2026-09-16 | CLOSED | HIGH | Book imbalance instability flips verdict | L_ITEMS I30 | 2026-09-18: thresholds raised to <0.33 / >3.0 in math_object_builder.py; 20-snapshot proof shows firing drops 10/20 -> 2/20. |
| B025 | 2026-09-16 | CLOSED | MED | Verdict flicker has no debounce | L_ITEMS I31 | 2026-09-18: 2-cycle persistence added to start-trading-day.ps1 verdict-change block |
| B026 | 2026-09-16 | WONTFIX | COSMETIC | Log line no-change ambiguous | L_ITEMS I32 | Cosmetic; "no change:" prefix disambiguates. |
| B027 | 2026-09-16 | CLOSED | HIGH | OI field dead from 17:40 UTC | L_ITEMS I33 | false alarm: OI updates hourly not per-minute. 200-snapshot history shows 4 distinct buckets changing on the hour. Direct endpoint matches snapshot -0.24 exactly. Verified 2026-09-17 |
| B028 | 2026-09-16 | WONTFIX | MED | Sweep-entry rule missing | L_ITEMS I34 | 2026-09-19: corpus .txt, 2 hits (not .md as first pass). n7ZSkjb7JXs: "sweep the market" = descriptive. RwQBdF9TSvc (Trade the Traders, not Tom): explicitly debunks stop-hunting / "banks sweep the stops". Neither is a Tom rule. sweep_flag ubiquitous (>250/400 any moment). No source. |
| B029 | 2026-09-16 | WONTFIX | MED | Supervisor not running after manual restart | L_ITEMS I35 | 2026-09-18: B043 closed; matcher covers mode.ps1. Operator-start, not defect. |
| B030 | 2026-09-16 | WONTFIX | LOW | Binance OI data path reconciliation | L_ITEMS I37 | 2026-09-18: L220-223 reads openInterestHist 1h x2, direction correct. |
| B031 | 2026-09-16 | WONTFIX | LOW | Two-phase OI/CVD pattern unnamed | L_ITEMS I38 | 2026-09-18: naming; no engine consumer. |
| B032 | 2026-09-16 | CLOSED | COSMETIC | session_end_logs.md wrong writer | L_ITEMS I39; StateCodeEmitter.java:441-452 | doc-only: writer identified StateCodeEmitter.java 441-452; no code change |
| B033 | 2026-09-17 | WONTFIX | MED | Profile shape taxonomy does not match Tom | L_ITEMS I40 | 2026-09-19 code-verified: buildVp L553-561 emits TWOPEAK / D / P (not Tom s B). Screener taxonomy. Receipt corrected from comment-based to code-based. |
| B034 | 2026-09-17 | CLOSED | HIGH | CVD ring not cleared at UTC rollover | AUDIT StateCodeEmitter row 1 | code receipt: StateCodeEmitter.java L340 cvdSeries.clear() on day-change; loop restarted 2026-09-18T17:48Z; runtime verify at next 00:00 UTC rollover tracked by T028 |
| B035 | 2026-09-17 | CLOSED | HIGH | Book imbalance threshold 0.4-0.6 treats balanced as extreme | AUDIT SetupCandidatesBuilder L541 | SetupCandidatesBuilder.java L541 now 0.67/1.5; hash 3ED13909->C30EB08F; 2026-09-17 |
| B036 | 2026-09-17 | CLOSED | MED | setup_candidates and last_3_delta read from snapshot not normalized | AUDIT math_object_builder L357 L388 | 2026-09-18: normalized carries setup_candidates + cvd; call site reads normalized. First pass was incomplete; fixed on retry. |
| B037 | 2026-09-17 | CLOSED | MED | isinstance accepts booleans spurious contradiction | AUDIT math_object_builder L393 L400 | 2026-09-18: added not isinstance(_book, bool) at both branches |
| B038 | 2026-09-17 | WONTFIX | LOW | diff_state compares disjoint value spaces | AUDIT mts_math L204 | 2026-09-18: STATE.classification vs conditions.vp_shape; only print consumer. Cosmetic. |
| B039 | 2026-09-17 | CLOSED | MED | ExtraSetupBuilder momentum has no RR gate | AUDIT ExtraSetupBuilder L103-135 | 2026-09-18: candidate rejected when net RR < 2.0 |
| B040 | 2026-09-16 | CLOSED | LOW | Log prints STATE X to X with same value | L_ITEMS I36 | start-trading-day.ps1 L319 L419 L422 pendingStateFrom |
| B041 | 2026-09-17 | CLOSED | MED | Stale test asserted classification == B | test_mts_math.py:477 | test_mts_math.py:477 now trend_healthy; 130/130 pass |
| B042 | 2026-09-17 | WONTFIX | LOW | day_type derived with provisional thresholds, no 3-snapshot evidence | MTS-2026-09-17-1142Z | 2026-09-18: provisional confidence already in snapshot; doc-only. |
| B043 | 2026-09-17 | CLOSED | MED | Supervisor misses wrappers launched via mode.ps1 | handoff NEXT_SESSION_HANDOFF.md; MTS-2026-09-17-1514Z live incident | Get-AllWrappers matcher extended to mode.ps1; live verified 2026-09-17T17:54Z mts-live wrap=17792 |

| B044 | 2026-09-17 | WONTFIX | MED | CVD and trade_flow.net_delta computed from kline taker-buy proxy, not aggTrade tick delta | MarketDataSnapshot.java:178,633-648,379-381 | 2026-09-18: kline takerBuy proxy is documented design (DSA-HYG-007 L179); divergence vs state_code aggTrade is documented in MTS_DICTIONARY. Not a defect. |
| B045 | 2026-09-17 | WONTFIX | MED | WebSocket migration roadmap not started; archive doc 2026-09-05 unrealized | MyTradingSys/mts/archive/binance_api_integration_recommendations.md 1107 lines sections 1-11 | 2026-09-18: snapshot cadence is 60s REST; WebSocket only worth it for sub-second. Not in scope. |
| B046 | 2026-09-18 | CLOSED | MED | DSA section 11 and handoff claimed rewritten in ledger; both unchanged on disk | this session; ledger 2026-09-18T10:16:12Z | 832f1ec; both files rewritten and verified |
| B047 | 2026-09-18 | CLOSED | HIGH | finished_auction contradiction sign inverted in math_object_builder.py | math_object_builder.py L391,L398 vs SetupCandidatesBuilder.java L703; T009 | 2026-09-18; Python inverted, Java correct (Tom source oa8kxSLLkAo + VxN5IxTwpbE); 17/30 snapshots proof |
| B048 | 2026-09-18 | CLOSED | MED | verify_rule_citations.ps1 printed PASS despite 0 refs; header comment promised unreferenced-id check | scripts/tools/verify_rule_citations.ps1 L44 | 2026-09-18; verifier now fails on unused ids |
| B049 | 2026-09-18 | CLOSED | HIGH | determineSetupType skips state check on VAH/VAL/swing zones; violates compiled engine rule 3 | SetupCandidatesBuilder.java L432-437 | 6816cc0; VerifyScbEdits.java 12/12 PASS 2026-09-18 |

## TASKS

| ID | Opened | Status | Severity | Title | Evidence | Receipt |
|---|---|---|---|---|---|---|
| T001 | 2026-09-18 | CLOSED | MED | DSA_SESSION_PROMPT.md section 11 rewrite (v1.1.1 + current state) | B046 | 832f1ec; hash F4599EDA -> DD2CB93D |
| T002 | 2026-09-18 | CLOSED | MED | NEXT_SESSION_HANDOFF.md rewrite with current runtime | B046 | 832f1ec |
| T003 | 2026-09-18 | CLOSED | LOW | session_log correction entry for false close entries | B046 | ledger entry logged 2026-09-18T10:16Z |
| T004 | 2026-09-18 | CLOSED | LOW | mts-live-stop flag not auto-cleared on mts-live start | journal A1 | 186f483; load.ps1 L20 clears stop flag on mts-live |
| T005 | 2026-09-18 | CLOSED | LOW | DIRECTION column missing on dashboard TRADES | journal A2 | 186f483; live render 2026-09-18T15:52Z shows DIRECTION col |
| T006 | 2026-09-18 | CLOSED | LOW | Five verdict words not in MTS_DICTIONARY | journal A3 | 186f483; VERDICT WORDS section in MTS_DICTIONARY.md |
| T007 | 2026-09-18 | CLOSED | COSMETIC | MTS-CAND gate pass collision with GATE column | journal B6 | 186f483; renamed to rr_gate in mts-watch.ps1 L116 |
| T008 | 2026-09-18 | CLOSED | COSMETIC | mts-dashboard index row format mismatch | FYI-01 M3 | 186f483; 03_FILE_INDEX.md 5-col row |
| T009 | 2026-09-18 | CLOSED | MED | finished_auction sign confirmed inverted | journal B1; code read | closed with B047 2026-09-18; Tom source + 17/30 snapshots |
| T010 | 2026-09-18 | CLOSED | LOW | Engine confidence grade meaning undocumented | journal B3 | doc-only: confidence grade table added to MTS_DICTIONARY.md 2026-09-18 |
| T011 | 2026-09-18 | CLOSED | LOW | cms_age=-1s anomaly | journal B4 | clamp applied 2026-09-18; race between $now and Get-Item |
| T012 | 2026-09-18 | CLOSED | MED | Verdict parse fragility in dashboard | journal B5 | 14cfd60; known-word list applied; T022 tracks structured writer |
| T013 | 2026-09-18 | CLOSED | MED | MTS-TAPE sidecar baseline stale since 2026-09-17T20:11Z | live tape; journal O4 | 7ccd0e1; live STALE 70573s 2026-09-18T15:47Z |
| T014 | 2026-09-18 | WONTFIX | MED | Rank-1-only gate vs scan all candidates | journal A7 | 2026-09-18: rank-1-only is by design; confluence bonus already surfaces co-located zones. No change. |
| T015 | 2026-09-18 | WONTFIX | MED | Proof count direction-blind; Options A/B/C pending | journal B7 | 2026-09-18: proof_direction_status carries direction; B047 fix removed the false contradiction. Proof count stays direction-blind by design. |
| T016 | 2026-09-18 | WONTFIX | LOW | Five open comparison questions CVD anchor OI magnitude Net Delta what we trade on pre-open | journal E7 | 2026-09-18: all five covered in MTS_DICTIONARY cross-category warnings. No action. |
| T017 | 2026-09-18 | CLOSED | MED | Extraction chain 0 TOM-NNN refs in condition files (verify first) | FYI-03 | 2026-09-19: TOM_VERBATIM_INDEX rebuilt with 213 quotes (TOM-001..TOM-213) harvested from Source GPS lines and verified vs raw_transcripts_canonical; 213 tags applied; verify_rule_citations.ps1 PASS. |
| T018 | 2026-09-18 | WONTFIX | MED | Frame-view regime label has no verdict-block consumer | FYI-03 | WONTFIX 2026-09-18: superseded by 04_final_report. Frame is display only by design; real defect is determineSetupType |
| T019 | 2026-09-18 | CLOSED | MED | RSI documentation conflict VVP-001 vs COMPILED_DECISIONS | journal; FYI-02 | doc-only 2026-09-18: E4 in COMPILED_DECISIONS.md marked SUPERSEDED; VVP-001 Tier 3 wins; RSI not Tom-validated |
| T020 | 2026-09-18 | WONTFIX | COSMETIC | Rank-1 GATE cell not padded, runs into pipe on WAIT_TRIGGER | dashboard render 2026-09-18T11:31Z | superseded: GATE renamed to rr_gate (T007); value is boolean now, no padding needed |
| T021 | 2026-09-18 | CLOSED | COSMETIC | tape-watch emits duplicate line when snapshot unchanged between ticks | journal L85 2026-09-17 | tape-watch.ps1 skip-on-same-snapshot 2026-09-18; receipt commit follows |
| T022 | 2026-09-18 | WONTFIX | MED | Loop writes last_verdict.json for dashboard (needs critical-file approval) | journal B5; T012 | 2026-09-18: T012 known-word parse fix removes the need for a separate JSON file. |
| T023 | 2026-09-18 | CLOSED | HIGH | Enforce CT state gate: no ct_short at VAH/VAL when state is trend_healthy | 04_final_report Step 1 | merged into B049; 6816cc0 |
| T024 | 2026-09-18 | CLOSED | HIGH | Add TC long path: determineDirections above_vah must emit long; determineSetupType needs tc_long at VWAP for trend_healthy | 04_final_report Step 2 | 6816cc0; VerifyScbEdits.java 12/12 PASS 2026-09-18 |
| T025 | 2026-09-18 | CLOSED | HIGH | T023+T024 must land in one commit; T023 alone silences engine on 38 pct of day | disk: today state distribution | bundled in commit with T023+T024 |
| T026 | 2026-09-18 | WONTFIX | LOW | Frame Stage 2 wiring (regime into verdict path). Deferred until B049 is live | reply to 1600Z | 2026-09-18: T027 shipped regime label to verdict line. Stage 2 wiring has no rule basis. Superseded. |
| T027 | 2026-09-18 | CLOSED | LOW | Write regime label into verdict log line (Stage 1 annotation, no engine change) | reply to 1600Z | start-trading-day.ps1 loads state_code_regime.json, adds rg= to Format-VerdictLine 2026-09-18 |
| T028 | 2026-09-18 | OPEN | LOW | Verify B034 cvdSeries.clear fix at 00:00 UTC rollover | B034 code receipt | - |
| T029 | 2026-09-18 | CLOSED | LOW | context.ps1 makes 3 Binance REST calls per invocation; cache to disk | scripts\live\context.ps1 | duplicate of B015 (WONTFIX 2026-09-18); no consumer needs caching. |
| T030 | 2026-09-18 | CLOSED | MED | T017 scope: only session_timing_rules.md carries ID-row rule format; other 5 condition files use unnumbered headings | conditions/*.md tally 2026-09-18 | 2026-09-19: closed with T017. Tag pass ran on all 6 files; only session_timing_rules produced 0 tags. See T031. |
| T031 | 2026-09-19 | WONTFIX | LOW | session_timing_rules.md has 0 TOM-NNN tags; its Tom refs use T-001..T-005 inline format | session_timing_rules.md L301-309 | 2026-09-19: file is research-sourced (ATAS, CoinSwitch, SGT, Block Scholes B-001..B-005). Nine SR rules not Tom-derived. L301-309 is a background table, not rule source; T-002 and T-003 marked (implied). Zero tags correct. |
# END
