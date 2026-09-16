STATUS: Session 2026-09-16 PM complete. Feature layer wired. BOM fixed permanently.

# NEXT SESSION HANDOFF
# Written: 2026-09-16 12:30 UTC

## WHAT LANDED THIS SESSION

- Task 1 DONE: context.ps1. Rolling 24h per-TF envelope from Binance REST.
  Windows: 1h->24h, 15m->6h, 5m->2h. Fields: high, low, close, range_pct,
  range_position_pct, slope_pct_per_hour, slope_word. Provisional 0.05 pct/hr
  threshold, not Tom-derived. Alias: context.
- Task 2 DONE: regime_classifier.py. Vote-based, per-cycle. Reads latest
  snapshot, writes state_code_regime.json (sibling, not state_code.json).
  3-cycle anti-whipsaw gate verified. Alias: regime.
- Task 3 DEFERRED: L29 VP shape classifier. Unchanged.
- C DONE: kline_archiver.py. Writes MyTradingSys\data\klines\BTCUSDT_{1h,15m,5m}.json.
  Rolling 500 bars, dedupe on open_time, atomic write. Idempotent.
- Wiring: start-trading-day.ps1 calls kline_archiver then regime_classifier
  before Compute-Verdict. One cycle verified live: kline mtime bumped,
  regime block updated.
- BOM fix permanent: Write-NoBom, Write-NoBomLines, Test-HasBom in
  scripts\core\shared-functions.ps1. Build-Check.ps1 now scans for BOM.
  USER.md FILE WRITES rule added. 9 pre-existing BOM files stripped.

## MISSION FOR NEXT SESSION

Live market trading session. Write scope. Runtime loop armed.

### Setup
1. Confirm runtime loop running: mode.ps1 -M armed -IntervalMin 1
2. Alias load: . .\scripts\load.ps1
3. Verify in one block: context, regime, live, snapshot

### Live duties
- Read live snapshots and context on demand
- Generate trade cards from setup_candidates when verdict is actionable
- Log decisions via log_decision.py
- Update session_state.json thesis only with user approval
- Read state_code_regime.json for regime label

### Known limitations
- L29 VP shape classifier returns B near-constantly. Affects candidate
  generation. Do not treat B as ground truth.
- context.ps1 15m slope sits on the 0.05 threshold. Cosmetically falling.
- state_code_regime.json is a sibling of state_code.json. Java does not
  yet read it. Deferred: Java merges at next write.

## LAYERED ARCHITECTURE (updated)

1. Per-cycle engine fields (LIVE).
2. Session block (LIVE).
3. Rolling 24h per-TF envelope (context.ps1, LIVE).
4. Regime label (regime_classifier.py, LIVE).
5. Kline archive (kline_archiver.py, LIVE, running).
6. RSI read (external, isolated, not built).
7. Probability layer (parked).
8. Analyst verdicts (distant).

## OPEN LOOPS
- L8 stop_day repro.
- L13 proof-change alert noise.
- L16 snapshot cadence gaps.
- L17 alert numbering gap.
- L28 orphan java on exit.
- L29 VP shape classifier.
- NEW: context.ps1 network dependency. Reads Binance REST per call.
  Durable fix is kline_archiver running long enough to drop REST.
- NEW: state_code_regime.json orphan. Java does not read it yet.
- NEW: BOM rule now enforced by Build-Check scan. Any new BOM file
  will show in BUILD_REPORT.

## CONSTRAINTS
- User runs commands, AI issues.
- No emoji in system files.
- Hash + line count + non-ASCII after any write.
- BOM check after write to .py, .json, .ps1.
- Read-only on live apparatus.
- Human commits all writes.

# END