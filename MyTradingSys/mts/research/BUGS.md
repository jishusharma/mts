# BUGS

Single source of truth for defects. Supersedes L_ITEMS_MASTER.md (frozen 2026-09-17) and
the OPEN section of apparatus_fixes.md. AUDIT_2026-09-17_TRACKER.md material defects folded in.

## RULES

1. Never edit ID, Opened, or Title.
2. Change status by replacing the Status cell. If the new status is CLOSED, add a Receipt.
3. Add a bug by appending one row at the end.
4. Never delete a row. Use WONTFIX.
5. The table is the file. No prose outside this rules block and the table.

Status values (exact): OPEN, IN-FIX, BLOCKED, CLOSED, WONTFIX.
Severity values (exact): HIGH, MED, LOW, COSMETIC.
Receipt required when Status = CLOSED. Format: hash, test name, commit, or doc-only.
IN-FIX rows older than 14 days fail Build-Check.

## TABLE

| ID | Opened | Status | Severity | Title | Evidence | Receipt |
|---|---|---|---|---|---|---|
| B001 | 2026-09-13 | BLOCKED | LOW | L5 referenced as held no detail | L_ITEMS L5 | - |
| B002 | 2026-09-13 | BLOCKED | LOW | L6 same as L5 | L_ITEMS L6 | - |
| B003 | 2026-09-14 | OPEN | MED | stop-day.ps1 reports false success | L_ITEMS L8 | - |
| B004 | 2026-09-15 | OPEN | LOW | Proof-change alert trigger noise | L_ITEMS L13; start_trading_day.ps1:349 | - |
| B005 | 2026-09-15 | OPEN | LOW | Runtime manifest pointed at wrong prompt | L_ITEMS L14 | - |
| B006 | 2026-09-15 | OPEN | COSMETIC | Orphan duplicate root manifest | L_ITEMS L15 | - |
| B007 | 2026-09-15 | OPEN | MED | Snapshot cadence has 12.7h and 4.25h gaps | L_ITEMS L16 | - |
| B008 | 2026-09-15 | OPEN | LOW | Alert numbering gap 6-12 | L_ITEMS L17 | - |
| B009 | 2026-09-15 | OPEN | MED | Apparatus silent exit at 13:23:20 | L_ITEMS L18 | - |
| B010 | 2026-09-15 | OPEN | COSMETIC | Duplicate section header in prompt | L_ITEMS L19 | - |
| B011 | 2026-09-15 | OPEN | COSMETIC | apparatus_fixes END marker mid-file | L_ITEMS L20 | - |
| B012 | 2026-09-16 | OPEN | MED | US open fixed 13.5 UTC wrong in winter | L_ITEMS L25; MarketDataSnapshot.java:761 | - |
| B013 | 2026-09-16 | CLOSED | COSMETIC | MTS_DICTIONARY Authority column mojibake | L_ITEMS L27 | hash 5CE01AA2->F05D3E0A; 30 sequences replaced |
| B014 | 2026-09-16 | OPEN | MED | Loop exit orphans mvn/java child | L_ITEMS L28 | - |
| B015 | 2026-09-16 | OPEN | LOW | context.ps1 reads Binance REST each call | L_ITEMS L30 | - |
| B016 | 2026-09-16 | OPEN | LOW | state_code_regime.json not read by Java | L_ITEMS L31 | - |
| B017 | 2026-09-16 | OPEN | MED | Ratio gate has no near-miss record | L_ITEMS I21 | - |
| B018 | 2026-09-16 | OPEN | HIGH | Zones move per cycle nrr against moving target | L_ITEMS I22 | - |
| B019 | 2026-09-16 | OPEN | MED | Quad vs setup direction mismatch not read | L_ITEMS I23 | - |
| B020 | 2026-09-16 | OPEN | MED | session_timing_rules.md documents EST all year | L_ITEMS I24 | - |
| B021 | 2026-09-16 | OPEN | LOW | order_flow block has no consumer | L_ITEMS I27 (ruled gauges) | - |
| B022 | 2026-09-16 | OPEN | LOW | session block has no consumer | L_ITEMS I28 (ruled gauges) | - |
| B023 | 2026-09-16 | OPEN | MED | Two builder paths contradict cvd_trade_flow_aligned | L_ITEMS I29; MarketDataSnapshot.java:1068 | - |
| B024 | 2026-09-16 | OPEN | HIGH | Book imbalance instability flips verdict | L_ITEMS I30 | - |
| B025 | 2026-09-16 | OPEN | MED | Verdict flicker has no debounce | L_ITEMS I31 | - |
| B026 | 2026-09-16 | OPEN | COSMETIC | Log line no-change ambiguous | L_ITEMS I32 | - |
| B027 | 2026-09-16 | OPEN | HIGH | OI field dead from 17:40 UTC | L_ITEMS I33 | - |
| B028 | 2026-09-16 | OPEN | MED | Sweep-entry rule missing | L_ITEMS I34 | - |
| B029 | 2026-09-16 | OPEN | MED | Supervisor not running after manual restart | L_ITEMS I35 | - |
| B030 | 2026-09-16 | OPEN | LOW | Binance OI data path reconciliation | L_ITEMS I37 | - |
| B031 | 2026-09-16 | OPEN | LOW | Two-phase OI/CVD pattern unnamed | L_ITEMS I38 | - |
| B032 | 2026-09-16 | OPEN | COSMETIC | session_end_logs.md wrong writer | L_ITEMS I39; StateCodeEmitter.java:441-452 | - |
| B033 | 2026-09-17 | OPEN | MED | Profile shape taxonomy does not match Tom | L_ITEMS I40 | - |
| B034 | 2026-09-17 | OPEN | HIGH | CVD ring not cleared at UTC rollover | AUDIT StateCodeEmitter row 1 | - |
| B035 | 2026-09-17 | OPEN | HIGH | Book imbalance threshold 0.4-0.6 treats balanced as extreme | AUDIT SetupCandidatesBuilder L541 | - |
| B036 | 2026-09-17 | OPEN | MED | setup_candidates and last_3_delta read from snapshot not normalized | AUDIT math_object_builder L357 L388 | - |
| B037 | 2026-09-17 | OPEN | MED | isinstance accepts booleans spurious contradiction | AUDIT math_object_builder L393 L400 | - |
| B038 | 2026-09-17 | OPEN | LOW | diff_state compares disjoint value spaces | AUDIT mts_math L204 | - |
| B039 | 2026-09-17 | OPEN | MED | ExtraSetupBuilder momentum has no RR gate | AUDIT ExtraSetupBuilder L103-135 | - |
| B040 | 2026-09-16 | CLOSED | LOW | Log prints STATE X to X with same value | L_ITEMS I36 | start-trading-day.ps1 L319 L419 L422 pendingStateFrom |
| B041 | 2026-09-17 | CLOSED | MED | Stale test asserted classification == B | test_mts_math.py:477 | test_mts_math.py:477 now trend_healthy; 130/130 pass |

# END
