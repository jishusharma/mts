# 130-SONNET: executor + position_manager wiring for env stamping, env refusal and the mainnet plan cap

Audit items #6 (wiring half) and #7, `research/fast_track_2026-09-27/review/OPUS_PREMAINNET_AUDIT.md`. Both smoke blockers.

## Why Sonnet, not Qwen
The edits are small (about 25 lines) but sit in executor.py (562 lines) and position_manager.py (~380 lines), which are safety code
next to the stop ordering, and each file is too big for a 5k-token Qwen package. Do not touch the stop / fail_closed / flatten_halt
ordering; the edits below are all before the first order or exchange call.

## Prerequisites (promote in this order, each gated)
1. 126 journal env (`journal.EnvMismatch`, `journal.assert_env`, `journal.plan_env`; `append_event("intent")` now REQUIRES `data["env"]`).
2. 128 `mainnet_plan_check.plan_refusals(compiled, plan, env, cap_usd)`.
Promotion: back up to `.pre_<tag>`, rename `.new`, re-gate. 127 (reconciler) is independent of this brief.

## Edits
executor.py
1. `import mainnet_plan_check` next to the other sibling imports.
2. `preflight()`: right after the existing `_mn`/`mainnet_plan_refusal` block, add
   `reasons.extend(mainnet_plan_check.plan_refusals(compiled, plan, do.active_env(), do.MAINNET_MAX_NOTIONAL_USD))`.
   `plan` is None exactly when `load()` took a pre-compiled file, so this is what refuses compiled input on mainnet. Testnet returns [].
3. `execute_plan()`: the `intent` event gets `"env": do.active_env()` (this is now mandatory or `append_event` raises ValueError,
   which would surface as R7 fail_closed after entries - so add it in the SAME edit, and note the intent append happens after preflight
   and before any order, so a ValueError there cannot leave exposure).
4. Nothing else. `load()` keeps accepting compiled files (dry run and testnet still work).

position_manager.py
5. `manage()`: first statement, before `journal.reconstruct_belief`:
   `try: journal.assert_env(plan_id, do.active_env())` / `except journal.EnvMismatch as e: raise ManagerHalted(str(e))`.
   No journal write on this path (no mismatch_halt: the plan belongs to the other environment and must stay untouched).
   `main()` already prints `HALTED: ...` and returns 1 for ManagerHalted; no change there.

## Tests
`MyTradingSys/execution/test_env_wiring.py.new` (written, fails today: 5 failures + 2 errors on the pre-change code). It imports
`FakeExchange`, `PATCHED_NAMES`, `_compiled` from `test_s1_cap_offline.py`, so keep that file. Promote the test to
`test_env_wiring.py`. Also run `test_s1_cap_offline`, `test_mainnet_flag_offline`, `test_executor_math`, `test_gh_retry_offline`,
`test_triggered_stop_offline` (existing suites must stay green; any test that calls `journal.append_event(..., "intent", ...)` directly
needs `env` added).

## Gates
`python scripts/dev/run_all_tests.py --quick`. Manually confirm: `python MyTradingSys/execution/executor.py <compiled.json>` (dry run) still prints.
Update MAINNET_READINESS_CHECKLIST.md audit items #6 (wiring + reconciler once 127 is in) and #7 to `[x]` with the commit tag.
Operator note to keep in the checklist until this lands: use the raw plan on mainnet; never run reconciler on a mainnet plan_id.
