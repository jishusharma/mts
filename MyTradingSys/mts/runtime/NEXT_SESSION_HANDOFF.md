STATUS: Prior phases A/B/C complete. This session closed the cleanup + fix batch. Three tasks queued.

# NEXT SESSION HANDOFF
# Written: 2026-09-16 evening
# Mission: three open build tasks, in order.

## WHAT LANDED 2026-09-16

- Legacy "kimi" naming removed. 11 files renamed (kimi_*_dump.md -> dump_*.md, java_core_dump.md -> dump_java.md).
- Stale DUMP_*.md set (10 files) moved to backup, then purged.
- backup_session purged clean.
- 47 byte-identical extract dupes moved (old_47, new_selected_10 fresh copies).
- target/ and .pytest_cache/ moved.
- scripts/live/live.ps1 added. Alias `live` in load.ps1. Compact per-minute block for chat paste.
- scripts/live/story.ps1 added. Alias `story`. Last N cycles as tape.
- start-session.ps1 extended: git state, loop health, scripts inventory, COMMANDS.md, MTS_DICTIONARY canonical fields table, all inlined into SESSION_PASTE.txt.
- start-trading-day.ps1 SESSION_PASTE generator console NEXT line updated.
- StateCodeEmitter.java: cvd_slope warmup bug fixed (CVD_MIN_SAMPLES=10, adaptive half-window, denom guard). L26 CLOSED.
- L23 (kimi naming), L27 (mojibake), O1 (cvd_slope), O2 (endpoint guessing), O3 (boot paste field table) closed.
- Commits today: 3e7e704, 44afc61, 856e062.
- Data correctness revalidated end-to-end. Snapshot matches Binance futures. All invariants pass.

## MISSION FOR THIS SESSION (in order)

### Task 1: Fix L18 (apparatus silent exit) — HIGHEST PRIORITY
Loop parent exits silently. Java orphans survive. Recurred 2026-09-16 11:41:02 (this session).
- Read scripts/core/start-trading-day.ps1 main loop end + finally block.
- Find the path where the loop exits without logging.
- Known facts: finally block runs (logged "APPARATUS END (finally)"). No error line.
- Test: run loop, watch for exit, capture exit code and $Error.
- Rule 32 gate: this is a bug fix, not engine change. No 3-snapshot needed for the fix itself, but the fix must be proven by a loop surviving 24h.

### Task 2: Build scripts/live/context.ps1 — 24h per-timeframe context block
Purpose: from snapshot archive, compute rolling 24h per timeframe: high, low, range_pct, slope, range_position_pct, regime label.
- Sources: data/snapshots/*.json (1717 files). Snapshot has structure.1h/15m/5m swings, prior_day high/low. No 24h fields today.
- Specs exist: TREND_REGIME_DETECTOR_SPEC.md (regime classifier), schema_v5.1.0_spec.md (session_high/low/range_position_pct), compiled_output_audit_20260915.md (ABSENT table).
- Design: read last 1440 min of BTCUSDT snapshots, bucket by TF, compute. Output block similar to `live`.
- No Java change. No schema change. No Rule 32 gate.

### Task 3: Build scripts/tools/verify_data.ps1 — permanent data check
Purpose: assert snapshot truth against Binance futures and internal invariants.
- A: newest snapshot current_price vs futures close for same minute (diff < 5).
- B: spot_price, mark_price, basis_pct internally consistent.
- C: price_vs_va matches computed.
- D: net_delta window monotonicity.
- E: state_code.json age < 90s.
- Run at session start. Fail any, stop.
- Design done in this session's chat. No code yet.

## OPEN LOOPS (see L_ITEMS_MASTER.md)
- L5, L6 NO EVIDENCE
- L8 stop_day repro
- L13 proof-change alert noise
- L14, L15, L16, L17, L18, L19, L20, L21, L22, L23, L25, L26, L27
- L18 is Task 1 this session.
- L25 US cash open classifier DST bug.

## CONSTRAINTS
- Rule 5: user runs commands, AI issues.
- Rule 25: no emoji in system files.
- Rule 40/41: pre-write revalidation, post-write retest.
- Rule 51: per-task discipline.
- Rule 52: read MTS_DICTIONARY before field questions.
- Read-only on live apparatus. No session_state.json thesis change without approval.
- Human commits all writes. No auto-push.
- SESSION_PASTE.txt now inlines dictionary fields + git state + scripts + COMMANDS. Use it.

# END