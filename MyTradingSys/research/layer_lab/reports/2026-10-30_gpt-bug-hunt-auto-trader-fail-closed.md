# GPT auto-trader fail-closed audit

Verdict: **FIX-FIRST** — tested branches generally reject safely, but restart recovery can forget active exposure when its log or process enumeration is unavailable; subprocess exceptions also escape the polling path.

## Checked

- `MyTradingSys/execution/auto_trader.py:327-355,636-752,798-869,872-956` — ticker/API error handling, order subprocess outcomes, manager/exchange recovery, restart discovery, state and alert offsets.
- Tests searched: `MyTradingSys/execution/test_auto_trader.py`, `test_auto_trader_blocklist.py`, `test_auto_trader_confirm.py`, `test_auto_trader_promotion.py`, `test_auto_trader_sizes.py`.
- Test discovery command: `Select-String -Path MyTradingSys/execution/test_auto_trader*.py -Pattern 'restart|reset|balance|API|error|respawn|exchange|manager|timeout|ledger|process|unread' -CaseSensitive:$false`.
- No tests were run; this was a branch/test-presence audit as requested.

## Findings

| Severity | File:line | Finding | Evidence / reproducing input | Proposed fix |
|---|---|---|---|---|
| HIGH | `MyTradingSys/execution/auto_trader.py:821-824,839-845` | An unreadable/missing trade log is treated as an empty history. Restart then forgets entered trades and frees the slot for new signals. | `open_plans_from_log` returns `[]` on `OSError`; `recover_slots` consumes that empty list. Existing test `test_open_plans_skip_closed_and_non_entered` (`test_auto_trader.py:594-597`) does not cover an unreadable log. Repro: missing log + open exchange position + new actionable signal. | Treat recovery-log read failure as unknown exposure and block new entries pending reconciliation. |
| HIGH | `MyTradingSys/execution/auto_trader.py:798-808,839-845` | Process enumeration failure returns `[]`, indistinguishable from “no manager is running”; a restart can launch a second manager for an open account position. | Broad exception handler returns empty list. Tests cover PID matching and an explicit empty process list (`test_auto_trader.py:599-602,619-627`), not PowerShell/JSON failure. Repro: `subprocess.run` raises `OSError("powershell unavailable")`, logged plan exists, exchange position is open. | Preserve “process state unknown” separately from an empty list and prevent duplicate spawn until reconciled. |
| MED | `MyTradingSys/execution/auto_trader.py:636-640,643-663` | `run` does not catch launch errors/timeouts. A new-plan/executor timeout escapes `place`, then `cycle` and `main`; no controlled outcome is logged and later polling stops. | `place` handles returned nonzero codes but tests mock `place` itself (`test_auto_trader.py:572-575`; `test_auto_trader_blocklist.py:263-269,296-303`). Repro: patch `subprocess.run` to raise `subprocess.TimeoutExpired("executor", 60)` during `place`. | Convert launch exceptions to explicit refusal/uncertain-entry outcomes. For executor uncertainty, reconcile plan/position before allowing another entry. |
| MED | `MyTradingSys/execution/auto_trader.py:675-694` | `exchange_flat` has a fail-closed `None` result, but existing coverage injects `None` at its caller rather than proving auth/API exceptions become `None` and account env is restored. | `test_unreadable_exchange_keeps_slot_without_respawn` (`test_auto_trader.py:564-570`) verifies slot retention with a stub. Repro: `authenticate` or `get_position` raises `OSError`; test `MTS_ACCOUNT` restoration too. | Add unit coverage for both API exceptions and environment restoration. |
| MED | `MyTradingSys/execution/auto_trader.py:730-734` | Respawn exception retains the occupied slot and retries, which is safe, but this recovery branch has no direct test. | No test named for `respawn_error`. Repro: failed manager, `exchange_flat=False`, `spawn_manager` raises `OSError`. | Add test asserting no new signal can use the slot and each retry is logged. |
| LOW | `MyTradingSys/execution/auto_trader.py:393-408` | Layer alert file stat/open exceptions are uncaught; malformed complete records are skipped while the offset advances, so the bad record is consumed. | Existing offsets tests cover initial offsets/truncation (`test_auto_trader.py:363-385`), not permission/read failures or invalid complete JSON. Repro: `f.stat()` raises `PermissionError`; separately append `'{bad}\n'`. | Define behavior for inaccessible files and corrupt records; avoid advancing a cursor past data that cannot be interpreted safely. |
| LOW | `MyTradingSys/execution/auto_trader.py:936-940` | A missing state file is safely initialized from the current Tom alert, but valid JSON with a wrong top-level shape is not validated and can raise during use. | `test_reset_state_never_trades_the_alert_already_on_disk` (`test_auto_trader.py:810-820`) covers missing state only. Repro: state file contains `[]`. | Validate state schema on load; on invalid state, initialize conservatively and retain restart recovery lockout. |

## Covered branches and balance movement

Ticker errors and bad mark values reject before order placement (`auto_trader.py:335-355`; `test_auto_trader.py:700-756`). Manager exit with open/flat/unreadable position, respawn cap, restart adoption, dead-manager reconciliation, superseded plans, and first-start no-replay have tests (`auto_trader.py:702-738,839-869,936-946`; `test_auto_trader.py:487-497,528-644,783-820`). The ticker reader calls `get_ticker` only and does not authenticate or read account summary (`auto_trader.py:327-333`; `test_auto_trader.py:721-729`), so funding/transfers cannot alter its mark input through account-balance APIs. The branch-by-branch matrix, including exact untested inputs, is [auto_trader_failclosed_matrix.md](../test_hunt_2026-10-31/auto_trader_failclosed_matrix.md).

Follow-up cards created: none.

Noticed: restart recovery silently loses safety state when the trade log cannot be read or process enumeration fails; see HIGH findings above.
