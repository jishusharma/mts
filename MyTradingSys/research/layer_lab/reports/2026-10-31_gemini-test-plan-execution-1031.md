# Execution Test Plan Report: Boundary and Failure Cases

**Task ID:** `gemini-test-plan-execution-1031`  
**Date (UTC):** 2026-10-31  
**Artifact Generated:** `MyTradingSys/research/gemini_burn_2026-10-31/TEST_PLAN_EXECUTION.md`  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  
**Scope Covered:** `MyTradingSys/execution/` (22 production modules, 57 test files, 695 test cases)  

---

## 1. Summary of Findings

- **Total Execution Modules Analyzed:** 22 modules in `MyTradingSys/execution/` (SOURCED: `MyTradingSys/system/03_FILE_INDEX.md:85-115`).
- **Total Test Definitions Grepped:** 695 test functions across 57 test files in `MyTradingSys/execution/` (SOURCED: `git grep -n "def test_" -- MyTradingSys/execution`).
- **Cataloged Boundary / Failure Scenarios:** 48 concrete test scenarios mapped across Restart/Reset State, Non-Trade Balance Moves, API Errors, and Stale State (OURS: derived from codebase analysis).
- **Existing Coverage (EXISTS):** 38 scenarios (79.2%) have concrete unit or offline test implementations passing in the test suite (OURS).
- **Gaps Identified (MISSING):** 10 scenarios (20.8%) represent missing failure tests, cataloged and ranked by blast radius (OURS).

---

## 2. Top-10 Missing Gaps Ranked by Blast Radius

1. **[CRITICAL] `position_manager.py:336` (`_manage_impl`):** Non-trade margin depletion (funding fees / withdrawals) while position is open. Manager tracks contracts (`|pos|`), not wallet margin.
2. **[CRITICAL] `auto_trader.py:643` (`place`):** Pre-flight margin exhaustion check missing before order dispatch; relies on raw exchange rejection.
3. **[CRITICAL] `executor.py:286` (`execute_plan`):** Mid-ladder entry process termination before protective stop attachment.
4. **[HIGH] `orphan_watchdog.py:64` (`run_once`):** Transient network partition (orders endpoint fails while positions succeeds).
5. **[HIGH] `kill_switch.py:39` (`kill_all`):** Emergency `close_position` API failure after order cancellation leaves position naked.
6. **[HIGH] `reconciler.py:45` (`reconcile`):** Order history propagation lag causing false `ReconciliationMismatch`.
7. **[HIGH] `daily_loss_monitor.py:314` (`transaction_log_pnl_btc`):** Non-monotonic clock skew / timestamp jitter across midnight boundary.
8. **[HIGH] `deribit_orders.py:377,385` (`stop_market`, `edit`):** Ambiguous socket reset on stop order replacement (`OrderStateUnknown`).
9. **[MEDIUM] `pm_heartbeat.py:136` (`read_heartbeats`):** Truncated/corrupted heartbeat JSON handling during abrupt manager termination.
10. **[MEDIUM] `trade_plan_validator.py:64` (`validate`):** Missing unit tests for IEEE 754 NaN/Inf boundary values in trade plans.

---

## 3. Verification Commands Run

```powershell
# 1. Grep tests per case:
git grep -n "def test_" -- MyTradingSys/execution

# 2. Run test execution offline checks:
python MyTradingSys/execution/test_auto_trader_failclosed.py
python -m unittest MyTradingSys/execution/test_auto_trader.py
python -m unittest MyTradingSys/execution/test_daily_loss_monitor.py
python -m unittest MyTradingSys/execution/testnet/offline/test_fix3_offline.py
python -m unittest MyTradingSys/execution/testnet/offline/test_fix4_offline.py
python -m unittest MyTradingSys/execution/testnet/offline/test_s6_orphan_offline.py
python -m unittest MyTradingSys/execution/tests/test_executor_reject_diag.py
python MyTradingSys/execution/trade_plan_validator.py --examples
```
