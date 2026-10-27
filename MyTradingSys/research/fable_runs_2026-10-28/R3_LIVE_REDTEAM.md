# R3 LIVE RED TEAM — if a layer went live tomorrow on testnet

Fable 5.1 red-team pass, 2026-10-28. Testnet-only read (worktree; no live tree,
HALT files, `.secrets/` or `.env` touched; scratch tests only). Method: for each
MOVED_RULES live-path scenario, find the enforcing code and the test that proves
it, then try to break it. Baseline quick suite: green (exit 0).

## 1. Findings

| id | severity | where | scenario | failing test (or why none) | one-line fix |
|---|---|---|---|---|---|
| F-GAP-1 | BLOCKS-LIVE | `execution/position_manager.py:340-342` | Restart crash window: executor dies after the entry fill is journaled but before the protective stop is journaled (the window between `executor.py:461` entry-fill append and `:338` stop order_placed append — includes stop_market succeeded but the append lost). Restart replays a journal with a filled entry and NO stop; `_manage_impl` takes the early `ManagerHalted("journal has no entry/stop")` return **before the S3 loop exists**, so the open position is left naked (no live stop, no 4 s `MAX_UNPROTECTED_SECONDS` bound reachable) until the auto_trader respawn loop burns MAX_RESPAWNS and pings the operator. | **Failing test written**: `scratch_r3/test_stop_gap_r3.py` (temp copy, not shipped) — `FAILED (failures=1)`: "position_manager halted without protecting the open position: \|pos\|=100, close_position called=False". Passes only after the fix. | In `_manage_impl`, when `stop is None` but `entry_filled_total > 0`: re-place the stop from the journal (or flatten + HALT) instead of returning "nothing to manage". |
| F-T09-2 | NOTE | T09 `T09_live_parity.md` §4/§6 | Live exits are a fixed 1%/2%/8-bar bracket that **no backtest used** — 97% of exits are time-exits by bracket arithmetic. Backtest verdicts say nothing about live PnL for 5 layer families. This is the "loses money" mechanism on testnet, and it is intentional calibration (mainnet-gated), not a code bug. | No failing test by construction; documented in T09. | Backtest the live bracket exits before promoting any layer; otherwise accept as testnet calibration. |
| F-T09-3 | NOTE | T09 §4 (jishu_2/3/4) | Live RSI trades cross/failure/rejection@40 events that no backtest covered (5 m never run at all). | Same — T09-documented, no test. | Add those event types to the RSI backtest (or block them) before promotion. |
| F-BLK | NOTE | `auto_trader_config.json:135` | `trade_blocklist` is empty; failed layers (session_momentum, funding_cvd_fade, turn_of_candle, fabio escalation, rsi_events 15 m) still **trade** on testnet under `trade_blocklist_parked`. Intentional (calibration); `mainnet_plan_check.py:83` refuses mainnet unless the parked blocklist is restored — gate is correct and tested (`test_mainnet_plan_check.py:63-81`). | None needed — gate proven. | No action on testnet; keep the mainnet gate. |
| F-CLK | NOTE | `daily_loss_monitor.py` (`_utc_now`) | Daily-loss window is process-local UTC; no test for clock skew across a DLM restart (skewed clock can shift the day boundary). Low impact on testnet. | No test. | Add a frozen-clock test for the DLM day boundary. |

**Investigated and REJECTED (not shipped as findings):**
- *F-KILL-1* (kill_switch "wrong" get_open_orders signature): scratch test with the real
  client signature **passes** — `deribit_orders.get_open_orders(token, instrument_name=..., type_=...)`
  is keyword-compatible with the call at `kill_switch.py:114`. Invalid.
- *F-MON-1* (DLM failure path can't re-auth): `daily_loss_monitor.py:541-545` re-auths via
  `do.authenticate()` which reads the main secret (MTS_ACCOUNT restored to None) — correct
  account; and a blind halt still blocks orders fail-closed (`executor._check_halt_files`
  blocks on any daily-loss HALT by existence). Invalid.

## 2. Rule coverage matrix (MOVED_RULES live-path test rule)

| Scenario / rule | Enforcing code | Test that proves it | Status |
|---|---|---|---|
| Restart mid-position, stop not live | `position_manager.py:570-611` (S3, `MAX_UNPROTECTED_SECONDS=4 s`) | `testnet/offline/test_s3_unprotected_offline.py` (fake clock; proves the time bound, not the one-attempt counter, trips the flatten) | COVERED |
| Restart: manager adoption / respawn | `auto_trader.py:698-865` (`recover_slots`, `settle_slot`, MAX_RESPAWNS=3, exchange flat-check) | `execution/test_auto_trader.py` (adopt/DeadProc cases) | COVERED |
| Restart: entry filled, stop never journaled | `position_manager.py:340-342` early return | **None** — scratch failing test `scratch_r3/test_stop_gap_r3.py` exists, not in repo | **PARTIAL → F-GAP-1** |
| Non-trade balance moves | `mainnet_pnl.ALLOWED_TX_TYPES={trade,settlement}`; DLM run_once | `test_daily_loss_monitor.py:254` (deposit doesn't mask/fake a breach), `test_dlm_blind_recovery.py:142` (non-trade move is not a loss), `test_mainnet_pnl.py` | COVERED |
| Blind-halt auto-clear bounds | `daily_loss_monitor.py` BlindRecovery (≤2/day, 60-min flap, kind re-check before unlink) | `test_dlm_blind_recovery.py` (incl. restart-doesn't-shortcut-window:112), `test_dlm_failure_cap.py`, `test_dlm_aggregate.py` | COVERED |
| API 5xx / timeouts / OrderStateUnknown | G-h: no auto-retry on order-creating calls; `NETRETRY` `_retry_call` (ContactLost rc 3); S3 `query_failed` bound | `testnet/offline/test_gh_executor_offline.py`, `execution/test_netretry.py`, `test_s3_unprotected_offline.py` | COVERED |
| Duplicate fills / idempotency | `executor.py:289` (journal-exists → refuse re-run), S6 label sweep, reconciler | `execution/tests/test_executor_reject_diag.py`, `testnet/offline/test_s6_orphan_offline.py` | COVERED |
| Partial fills | `executor.py:455-473` per-increment `ensure_stop`; G1/G1-resize + L2 ambiguous sweep | `testnet/offline/test_g1g2_offline.py` | COVERED |
| Clock skew | DLM day boundary, process-local UTC | none | PARTIAL (F-CLK, NOTE) |
| Safety checks fail closed | HALT files block every order-creating call (`executor._check_halt_files`, FIX4 M4 mid-run check); HALT written first in every flatten path; orphan watchdog no-false-HALT on blips | `testnet/offline/test_halt_preflight_offline.py`, `test_kill_switch.py`, `test_orphan_watchdog.py` | COVERED |
| Promotion gate default-deny | `promotion/registry.py` (`decision_for_source`, shadow→collection-only, malformed registry→all collection-only) | `test_registry_gate.py`, `execution/test_auto_trader_promotion.py` | COVERED |

Matrix bottom line: every MOVED_RULES scenario is proven by a test **except** the
stop-gap restart state — which is exactly where safety stops failing closed.

## 3. Go / no-go

**NO-GO for "a layer goes live tomorrow" until F-GAP-1 is fixed** (BLOCKS-LIVE list:
`[F-GAP-1]`). Everything else testnet-safe: the promotion gate default-denies (registry
entries are empty; only the cryptocred grandfather list trades), mainnet gates are
enforced, and the one live-money risk is the documented T09 bracket-exit gap, which is
deliberate calibration, not a defect.

## 4. Card — F-GAP-1 (lane SONNET)

```json
{
  "id": "fable-r3-fix-stop-gap-early-return",
  "lane": "SONNET",
  "kind": "fix",
  "live_path": true,
  "size": "M",
  "goal": "position_manager._manage_impl must not leave an open position naked when the journal has a filled entry but no journaled stop (executor crash window). See research/fable_runs_2026-10-28/R3_LIVE_REDTEAM.md F-GAP-1.",
  "steps": [
    "Move scratch_r3/test_stop_gap_r3.py into MyTradingSys/execution/ (repo test; keep temp-copy path out).",
    "Run it: MUST fail on current code with the F-GAP-1 assertion ('halted without protecting the open position').",
    "Fix position_manager.py:340-342: when stop is None and entry_filled_total > 0, fail closed - either re-place the protective stop from the journal (trigger from intent/plan, amount = entry_filled_total) or flatten + write HALT, THEN return/halt.",
    "Re-run the new test: must pass. Run MyTradingSys/execution/testnet/offline/* (all) - must stay green.",
    "Commit body: Result: restart with filled entry and no journaled stop now re-places the protective stop instead of leaving the position naked."
  ],
  "done_when": "repo test fails on pre-fix code and passes post-fix; offline suite green; no change to the live tree beyond position_manager.py + the new test."
}
```
