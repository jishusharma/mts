STATUS: Session 2026-09-16 features complete through context.ps1 + regime_classifier.py. Next: verify, then trade cards.

# NEXT SESSION HANDOFF
# Written: 2026-09-16 13:30 UTC

## WHAT IS LIVE ON DISK

- Session block (MarketDataSnapshot.buildSession). Fifteen fields. Anchor US cash open, DST-aware. Commit ab6f863.
- context.ps1 (scripts/live/). Rolling per-TF envelope from local kline store. Commit 0414d9a.
- regime_classifier.py (mts/runtime/). Vote-based per-cycle label. Writes state_code_regime.json. Live label RANGE, HIGH, 24 cycles as of 13:24 UTC.
- kline_archiver.py (mts/runtime/). Persists 1h/15m/5m bars to MyTradingSys/data/klines/. Feeds context.ps1.
- Boot rules 5 and 6 in DSA_SESSION_PROMPT section 3. Commit eab0673.

## MISSION FOR NEXT SESSION

### Task 1: Verify feature layers on a live cycle
- Run verify_data.ps1. Confirm PASS or E-only fail if loop off.
- Start loop (mode.ps1 -M armed -IntervalMin 1) if not running.
- Read one cycle: run `live`, `context`, `snapshot`. Confirm session block, 24h envelope, and regime label all print consistent values.
- Confirm kline_archiver.py is producing fresh bars in MyTradingSys/data/klines/.

### Task 2: L29 VP shape classifier
Diagnose buildVp shape rule. Shape fires B near-constantly. Affects SetupCandidatesBuilder.classifyState balance shortcut. Not Rule 32 gated for the fix; wiring into verdict is.

### Task 3: Trade cards when actionable
Watch daily_vah and 4h_vah cluster. A candidate crossing net_rr >= 2.0 is the first actionable event. Card it. Otherwise WAIT_RR stands.

### Task 4 (deferred): L28 orphan java on loop exit. session_bias echo tool. RSI 40-60.

## LAYERED ARCHITECTURE (all but 5-7 live)

1. Per-cycle engine fields (LIVE).
2. Session block (LIVE).
3. Rolling 24h per-TF envelope (LIVE, context.ps1).
4. Regime label (LIVE, regime_classifier.py).
5. RSI read (deferred).
6. Probability layer (parked).
7. Analyst verdicts (distant).

## CAUTIONS

- Boot rules 5 and 6 added today: no fabricated values, no invented aliases.
- Never bare-kill java.
- Handoffs must be verified against disk. Prior handoff invented an archive that did not exist.

## OPEN LOOPS
- L8, L13, L16, L17. L28 orphan java. L29 VP shape.
- L25 CLOSED 2026-09-16.

# END