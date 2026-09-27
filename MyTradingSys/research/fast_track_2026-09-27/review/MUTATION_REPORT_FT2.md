# FT-2 Mutation Testing Report — Offline Test Suite Strength

**Scope:** MyTradingSys/execution (staged .new code, built the same way
`scripts/dev/run_staged_tests.py` does) + `execution/testnet/offline`.
All mutation applied and executed in `~/mut/` (outside the repo mount);
nothing in the repo was modified. No network, no exchange calls, no git writes.

**Baseline (unmutated staged code):**
- `python3 -m unittest test_gh_retry_offline test_gh_executor_offline test_s6_orphan_offline
  test_s3_unprotected_offline test_s1_cap_offline test_risk_guard test_kill_switch
  test_daily_loss_guard test_daily_loss_monitor test_soak_report test_halt_preflight_offline`
  → 68/68 passed.
- `test_g1g2_offline.py` (deribit_orders replaced by fake_deribit_orders.py) → 12/12 PASS.

**Method:** one hand-picked, exact-string mutation applied at a time to a fresh copy
of the staged sandbox; both suites above re-run per mutant with a 120s timeout.
KILLED = either suite failed/errored/timed out. SURVIVED = both suites fully passed.
SKIPPED = the exact old-string wasn't found exactly once (none this run).

## Result

**44 mutants, 0 skipped. 31 KILLED / 13 SURVIVED → mutation score 70.5% (31/44).**

| # | File | Mutation | Result |
|---|------|----------|--------|
| R1 | risk_guard.py | `projected > cap` → `>=` | KILLED |
| R2 | risk_guard.py | drop `abs()`, mark_price=None branch | KILLED |
| R3 | risk_guard.py | drop `abs()`, mark_price given branch | **SURVIVED** |
| R4 | risk_guard.py | `cap=None` handling dropped | KILLED |
| R5 | risk_guard.py | drop `current_notional<0` ValueError | KILLED |
| R6 | risk_guard.py | drop `new_plan_notional<0` ValueError | KILLED |
| R7 | risk_guard.py | drop `cap<=0` ValueError | KILLED |
| D1 | daily_loss_guard.py | `total<=cap` → `<` | KILLED |
| D2 | daily_loss_guard.py | `cap_usd>=0` guard → `>0` | KILLED |
| D3 | daily_loss_guard.py | drop `"pnl_usd" in event` guard | KILLED |
| D4 | daily_loss_guard.py | invert halt/none action | KILLED |
| M1 | daily_loss_monitor.py | drop `breached_today` idempotency guard | **SURVIVED** |
| M2 | daily_loss_monitor.py | skip HALT_DAILY_LOSS file write | KILLED |
| M3 | daily_loss_monitor.py | skip `kill_all()`, stub success | KILLED |
| M4 | daily_loss_monitor.py | `_today_str` returns a constant | KILLED |
| M5 | daily_loss_monitor.py | invert day-rollover check | KILLED |
| M6 | daily_loss_monitor.py | drop `save_state()` persistence | KILLED |
| K1 | kill_switch.py | flatten positions before cancelling orders | **SURVIVED** |
| K2 | kill_switch.py | drop BTC-PERPETUAL fallback (no positions) | **SURVIVED** |
| K3 | kill_switch.py | `ok` always `True` regardless of errors | KILLED |
| K4 | kill_switch.py | BTC-PERPETUAL not appended, explicit instrument list | **SURVIVED** |
| E1 | executor.py | drop plan-level `max_notional_usd` size refusal | **SURVIVED** |
| E2 | executor.py | drop B079 `within_max_loss is False` refusal | **SURVIVED** |
| E3 | executor.py | drop market-entry estimated-loss refusal | **SURVIVED** |
| E4 | executor.py | drop generic HALT file refusal | KILLED |
| E5 | executor.py | disable HALT_DAILY_LOSS date-match refusal | KILLED |
| E6 | executor.py | drop S1 account-wide cap refusal | KILLED |
| E7 | executor.py | drop R8 existing-position/open-orders refusal | **SURVIVED** |
| E8 | executor.py | drop unsupported-stop-type refusal | **SURVIVED** |
| E9 | executor.py | fail_closed: drop entry-label sweep | KILLED |
| E10 | executor.py | fail_closed: drop stop-label sweep | KILLED |
| E11 | executor.py | fail_closed: drop target-labels sweep | **SURVIVED** |
| E12 | executor.py | fail_closed: drop `close_position()` flatten | KILLED |
| P1 | position_manager.py | `MAX_UNPROTECTED_SECONDS` comparison inverted | KILLED |
| P1b | position_manager.py | `MAX_UNPROTECTED_SECONDS` boundary `>`→`>=` | KILLED |
| P2 | position_manager.py | `unprotected_since` never reset when stop is live again | **SURVIVED** |
| P3 | position_manager.py | swallow stop re-place failure (no flatten_halt) | KILLED |
| P4 | position_manager.py | flatten_halt: drop label sweep | KILLED |
| P5 | position_manager.py | pos==0 "explained" check: OR → AND | **SURVIVED** |
| P6 | position_manager.py | sign-flip detection inverted | KILLED |
| DO1 | deribit_orders.py | 10050 back into retry set for order-creating calls | KILLED |
| DO2 | deribit_orders.py | `OrderStateUnknown` no longer subclasses `DeribitError` | KILLED |
| DO3 | deribit_orders.py | buy/sell/stop_market: `creates_order=False` | KILLED |
| DO4 | deribit_orders.py | close_position: `creates_order=False` | KILLED |

## Survivors — missing test, precisely

1. **R3** (`risk_guard.account_position_notional`, mark_price branch) — `test_risk_guard.py`'s
   `test_contract_denominated` only feeds non-negative `position_size_contracts` (2, 0) with a
   mark_price. Missing: a case like `account_position_notional(-2, 50000.0) == 100000.0`
   asserting `abs()` is applied in the mark_price-given branch, not just the mark_price=None branch.

2. **M1** (`daily_loss_monitor.run_once`, breached_today guard) — `test_breach_triggers_kill_once...`
   asserts `kill_all_calls == 1` on a second breached poll, but `FakeClient.close_position` zeroes
   `_position_size` on the first call, so a *second* `kill_all()` invocation finds zero positions
   and increments nothing — the assertion passes whether or not the guard exists. Missing: mock/count
   invocations of `kill_switch.kill_all` (or `daily_loss_monitor.kill_switch.kill_all`) directly across
   two same-day breached polls, independent of the fake client's position-size side effect.

3. **K1** (`kill_switch.kill_all`, phase order) — no test in `test_kill_switch.py` asserts operation
   *order* (e.g. via a client that records a call sequence and checks `cancel` precedes
   `close_position`); tests only check final counts. Missing: a test with an instrumented client
   logging call order, asserting every `cancel` call for an instrument happens before that
   instrument's `close_position` call.

4. **K2** (`kill_switch.kill_all`, no-positions fallback) — `test_kill_all_instruments_none_no_positions`
   asserts empty results but never checks that `get_open_orders`/`get_positions` were actually queried
   for the fallback `"BTC-PERPETUAL"` instrument (unlike the sibling "with discovered positions" test,
   which does check `order_queries`). Missing: assert `"BTC-PERPETUAL" in client.order_queries` (or
   equivalent) in the no-positions case too.

5. **K4** (`kill_switch.kill_all`, explicit `instruments=` list) — no test anywhere calls
   `kill_all(client, token, instruments=[...])` with an explicit list that omits BTC-PERPETUAL.
   Missing: a test passing `instruments=["ETH-PERPETUAL"]` and asserting BTC-PERPETUAL is still
   included (queried/cancelled/flattened) in the results.

6. **E1** (`executor.preflight`, plan-level `max_notional_usd` check) — no offline test builds a
   `compiled` plan whose `max_position_size` exceeds `caps_check.max_notional_usd` and calls
   `preflight()`/`execute_plan()` on it (existing tests only exercise the account-wide S1 check and
   the HALT files). Missing: a preflight test with `compiled["max_position_size"] >
   compiled["caps_check"]["max_notional_usd"]` asserting refusal.

7. **E2** (`executor.preflight`, B079 `within_max_loss is False`) — same gap: no test sets
   `caps_check.within_max_loss = False` and calls `preflight()`. Missing: a preflight test with that
   flag set, asserting a `B079: worst_case_loss ... exceeds cap ...` refusal reason.

8. **E3** (`executor.preflight`, market-entry estimated loss) — no test sets
   `within_max_loss == "unknown_until_fill"` with a `plan`+`mark` whose estimated loss
   (`max_position_size * percent_below_entry / 100`) exceeds `max_loss_usd`. Missing: a market-entry
   preflight test exercising this estimated-loss refusal branch.

9. **E7** (`executor.execute_plan`, R8 existing-position/open-orders refusal) — no offline test mocks
   `do.get_position`/`do.get_open_orders` to return a nonzero position or open order and asserts
   `execute_plan` refuses before placing anything. Missing: an `execute_plan` test where the
   pre-existing account state is dirty, asserting the R8 refusal fires and no entry orders are placed.

10. **E8** (`executor.preflight`, unsupported stop type) — no test calls `preflight()` with
    `compiled["stop_order"]["order_type"]` in `UNSUPPORTED_STOPS` (e.g. `trailing_percent`) or a
    `plan["stop"]["type"] != "fixed_percent"`. Missing: a preflight test asserting refusal for a
    trailing/breakeven stop spec.

11. **E11** (`executor.fail_closed`, target-labels sweep) — `test_gh_executor_offline.py` covers the
    entry-label sweep (test b) and the stop/post-fill flatten (test c), but no scenario reaches
    `fail_closed` *after* target orders have been placed (so `n_targets > 0`) to verify
    `cancel_by_label` is called for each `target_i` label. Missing: a test that places targets, then
    forces a `fail_closed` (e.g. a post-fill mismatch), asserting `cancel_by_label` was called with
    every `target_{i}` label.

12. **P2** (`position_manager.manage`, `unprotected_since` reset) — `test_s3_unprotected_offline.py`
    only exercises one continuous unprotected window ending in a flatten. Missing: a test where the
    stop goes unprotected, is confirmed live again (so `unprotected_since` should reset to `None`),
    then goes unprotected a second time for just under `MAX_UNPROTECTED_SECONDS` — asserting no halt
    fires (which the mutant would fail, since without the reset the *first* window's start time is
    reused and the second window is timed out immediately).

13. **P5** (`position_manager.manage`, pos==0 "explained" check OR vs AND) — in `test_g1g2_offline.py`
    T3 ("stop-out closes cleanly"), by fixture coincidence `target_filled` (50) already `>=
    stop["amount"]` by the time the stop fires, so `stop_fired or target_filled>=amount` and
    `stop_fired and target_filled>=amount` agree. Missing: a stop-out scenario with **zero** target
    fills (`target_filled == 0`) when the stop fires and fully closes the position — under AND this
    incorrectly raises `mismatch_halt` ("unexplained flat") on a legitimate stop-out; the current
    suite never asserts a clean close for that combination.

## Takeaway

The safety-critical *reaction* paths (HALT files, S1 account-wide cap, daily-loss kill+halt+persist,
label-orphan sweeps for entries/stops, 10050/OrderStateUnknown semantics, sign-flip and
unprotected-timer core logic) are well covered — every mutation there was KILLED. The gaps cluster in
two places: (1) **executor.py's plan-level preflight refusals** (E1/E2/E3/E7/E8) have zero offline
test coverage — only the account-wide (S1) and HALT-file refusals are exercised; and (2)
**kill_switch.py's instrument-selection/ordering edge cases** (K1/K2/K4) are undertested — counts are
checked but call order and the exact fallback-instrument path are not. M1 and P5 are subtler: existing
fixtures happen to make two different implementations agree, hiding a real behavioral difference.
