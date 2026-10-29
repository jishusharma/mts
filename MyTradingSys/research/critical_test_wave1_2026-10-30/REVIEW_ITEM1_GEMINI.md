# Second-Model Review (Gemini): FT2 C1-C3 + Kill-Switch B1 Fixes

- **Reviewer:** Gemini (Antigravity session, JIS-NUC)
- **Task:** `wave1-review-item1-ft2-fixes`
- **Scope:**
  - `MyTradingSys/execution/deribit_orders.py`
  - `MyTradingSys/execution/executor.py`
  - `MyTradingSys/execution/position_manager.py`
  - `MyTradingSys/execution/kill_switch.py`
- **Date:** 2026-10-30

---

## 1. Findings Analysis & Verification

### C1: Transport errors on order-creating calls bypass G-h and fail_closed
- **Status:** **FIXED**
- **Evidence (Code):**
  - `MyTradingSys/execution/deribit_orders.py:127-133`: `OrderStateUnknown` inherits from `DeribitError`.
  - `MyTradingSys/execution/deribit_orders.py:263-277`: Inside `_call_post`, when `creates_order=True`, transport exceptions (`OSError`, `URLError`, `TimeoutError`, etc.) raise `OrderStateUnknown(method, params_label, f"transport:{ex!r}")`.
  - Non-creating calls wrap transport exceptions into `DeribitError(method, params_label, f"transport:{ex!r}")`.
  - `MyTradingSys/execution/executor.py:442-446`: Handled and routed into `fail_closed`.
- **Covering Tests:**
  - `MyTradingSys/execution/testnet/offline/test_fix3_offline.py::test_r1_c1_transport_timeout_on_order_create_raises_order_state_unknown`
  - `MyTradingSys/execution/testnet/offline/test_fix3_offline.py::test_r_do_c1_post_transport_timeout_wrapped_in_order_state_unknown`

### C2: Poll-loop read failure escapes with a filled, unprotected position
- **Status:** **FIXED**
- **Evidence (Code):**
  - `MyTradingSys/execution/executor.py:420-565`: The entire poll-loop, order fill processing, and targets section are wrapped in a comprehensive `try: ... except ExecutionHalted: raise except Exception as ex: fail_closed(f"R7 unexpected: {ex!r}")` block.
- **Covering Tests:**
  - `MyTradingSys/execution/testnet/offline/test_fix3_offline.py::test_r3_c2_poll_loop_exception_triggers_fail_closed`
  - `MyTradingSys/execution/testnet/offline/test_fix3_offline.py::test_c2_targets_exception_triggers_fail_closed`

### C3: Protective stop cancelled BEFORE the flatten in flatten paths
- **Status:** **FIXED**
- **Evidence (Code):**
  - `MyTradingSys/execution/executor.py:374-418`: `fail_closed` explicitly cancels entries and target orders first, calls `close_position`, verifies flat (`size == 0`), and only removes the protective stop at lines 413-417 after flat is confirmed. If `size != 0`, `ExecutionHalted("... stop left in place")` is raised with the stop intact.
  - `MyTradingSys/execution/position_manager.py:459-493`: `manager_flatten` cancels targets first, invokes `close_position`, confirms `size == 0`, and cancels protective stop LAST at lines 489-492.
- **Covering Tests:**
  - `MyTradingSys/execution/testnet/offline/test_fix3_offline.py::test_r2_c3_close_failure_leaves_stop_intact_executor`
  - `MyTradingSys/execution/testnet/offline/test_fix3_offline.py::test_r5_c3_close_failure_leaves_stop_intact_manager`

### B1: Kill switch cancels protective stop before flatten
- **Status:** **FIXED**
- **Evidence (Code):**
  - `MyTradingSys/execution/kill_switch.py:88-154`:
    - Phase 2: calls `_close_open_positions()`.
    - Phase 3: separates orders; reduce-only orders are added to `protective` list and preserved. Only non-reduce-only orders are cancelled.
    - Phase 4: re-verifies `flat`. Protective stops are cancelled only if `flat` is True. If position is not confirmed flat, stops are kept and logged in `protective_orders_kept` with loud error.
- **Covering Tests:**
  - `MyTradingSys/execution/test_premainnet1_offline.py::test_b1_kill_switch_preserves_stops_on_flatten_failure`
  - `MyTradingSys/execution/test_premainnet1_offline.py::test_b1_kill_switch_cancels_stops_when_flat_confirmed`

---

## 2. Offline Test Suite Execution

Ran the offline verification suite:
```bash
python -m pytest -q MyTradingSys/execution/testnet/offline/test_fix3_offline.py MyTradingSys/execution/test_premainnet1_offline.py -o pythonpath=MyTradingSys/execution
```

**Summary Line:**
```
55 passed, 2 skipped in 0.44s
```

---

## 3. Verdict Summary

- **C1:** **FIXED** (`deribit_orders.py:263-277`)
- **C2:** **FIXED** (`executor.py:420-565`)
- **C3:** **FIXED** (`executor.py:374-418`, `position_manager.py:459-493`)
- **B1:** **FIXED** (`kill_switch.py:88-154`)

**Overall Verdict: FIXED (All 4 findings confirmed resolved on trunk)**
