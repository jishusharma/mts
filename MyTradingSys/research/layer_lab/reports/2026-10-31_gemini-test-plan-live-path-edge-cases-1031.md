# Live-Path Edge Cases Test Plan Report

**Task ID:** `gemini-test-plan-live-path-edge-cases-1031`  
**Date (UTC):** 2026-10-30 / 2026-10-31  
**Target Modules:** `MyTradingSys/execution/auto_trader.py`, `MyTradingSys/execution/position_manager.py`, `src/main/java/datafeed/Main.java` & `src/main/java/datafeed/StateCodeEmitter.java`  
**Artifact Generated:** `MyTradingSys/research/gemini_burn_2026-10-31/LIVE_PATH_TEST_PLAN.md`  
**Registry Ref:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  

---

## 1. Summary of Findings

- **Total Test Cases Cataloged:** 19 concrete test cases across 3 target modules (OURS: derived from system inspection).
- **Existing Coverage (EXISTS):** 16 test cases (84.2%) have concrete unit/fail-closed tests already implemented and passing.
  - `auto_trader.py`: 8 cases cataloged, 7 **EXISTS**, 1 **MISSING** (`TC-AT-04`: pre-flight balance shift check).
  - `position_manager.py`: 6 cases cataloged, 5 **EXISTS**, 1 **MISSING** (`TC-PM-04`: external margin depletion check).
  - `Java StateMachine` (`StateCodeEmitter` / `Main`): 5 cases cataloged, 5 **EXISTS** (100% covered across restart, gap seam, REST API error, and non-trade message filtering).
- **Gaps Identified (MISSING):** 2 test cases (10.5%) relate to non-trade wallet balance movements (deposits/withdrawals/margin depletion) where execution modules currently rely entirely on downstream execution failure or Deribit rejection rather than explicit fail-closed pre-flight validation.

---

## 2. Key File & Line Citations

### 2.1 `execution/auto_trader.py`
- Restart recovery entry: `auto_trader.py:839` (`recover_slots`), tested at `test_auto_trader.py:619` and `test_auto_trader_failclosed.py:239`.
- Duplicate alert rejection: `auto_trader.py:271` (`tom_signal`), tested at `test_auto_trader.py:487` and `test_auto_trader.py:783`.
- Exchange flat check on unreadable state: `auto_trader.py:709-715` (`settle_slot`), tested at `test_auto_trader.py:564` and `test_auto_trader_failclosed.py:60,66,119`.
- Subprocess execution refusal: `auto_trader.py:643-664` (`place`), tested at `test_auto_trader.py:572` and `test_auto_trader_failclosed.py:163,172`.

### 2.2 `execution/position_manager.py`
- Heartbeat / crash detection: `position_manager.py:496`, tested at `test_pm_heartbeat_wiring.py:12`.
- Emergency flatten on unreadable stop order: `position_manager.py:580-582`, tested at `testnet/offline/test_fix3_offline.py:164` and `testnet/offline/test_s3_unprotected_offline.py:27`.
- Stop order kept on flatten close failure: `position_manager.py:485`, tested at `testnet/offline/test_fix3_offline.py:180`.
- Position size growth outside plan: `position_manager.py:613-626`, tested at `testnet/offline/test_fix4_offline.py:44`.

### 2.3 Java StateMachine (`Main.java` & `StateCodeEmitter.java`)
- Mid-day restart and REST backfill: `StateCodeEmitter.java:237-250`, tested at `StateCodeEmitterTest.java:354`.
- Reconnect gap seam verification: `StateCodeEmitter.java:251-260`, tested at `StateCodeEmitterTest.java:379,708,723`.
- Binance REST API backfill failure: `StateCodeEmitter.java:292-308`, tested at `StateCodeEmitterTest.java:411,672,744`.
- Non-trade WebSocket frame filtering: `StateCodeEmitter.java:166-200`, tested at `StateCodeEmitterTest.java:471,652`.

---

## 3. Verification Commands

```powershell
# Verify Python offline fail-closed tests pass:
python MyTradingSys/execution/test_auto_trader_failclosed.py
python -m unittest MyTradingSys/execution/test_auto_trader.py
python -m unittest MyTradingSys/execution/testnet/offline/test_fix3_offline.py
python -m unittest MyTradingSys/execution/testnet/offline/test_fix4_offline.py

# Verify Java StateMachine tests pass:
mvn -q test -Dtest=StateCodeEmitterTest,LiquidationLogWiringTest
```

Noticed: Both `auto_trader.py` and `position_manager.py` focus heavily on position contract count invariants (`|pos|`) and order state machines, but lack direct non-trade wallet balance checks (e.g. tracking margin ratio depletion or deposit/withdrawal events), delegating those failure modes to raw exchange rejection.
