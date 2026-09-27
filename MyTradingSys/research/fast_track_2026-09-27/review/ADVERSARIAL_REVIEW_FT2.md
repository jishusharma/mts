# Adversarial review - FT-2 staged execution layer (2026-09-28)

Scope: executor.py.new, position_manager.py.new, risk_guard.py.new, daily_loss_guard.py.new,
daily_loss_monitor.py.new, kill_switch.py.new, soak_report.py.new, deribit_orders.py (5e387a1),
testnet/run_testnet_suite_ft2.py.new, testnet/run_testnet_suite_g1g2.py.new.
Method: read + diff vs live; offline repros in `review/repro_ft2.py` (copies staged files into a temp
dir, strips `.new`, swaps deribit_orders for an in-memory fake; R-DO uses the REAL deribit_orders with
`_post` monkeypatched). Output: `review/repro_ft2_output.txt`. No network, no secrets, no git writes,
no existing file modified. Line numbers below are for the staged `.new` files.

Result: 18 repro cases, all CONFIRMED. Three CRITICAL, all in one family: the fail-closed paths
only catch `do.DeribitError`, and the stop gets cancelled before the flatten.

---

## CRITICAL

### C1. Transport errors on order-creating calls bypass G-h and every fail_closed (CONFIRMED: R-DO, R1)
- deribit_orders.py:118-125: `urlopen(..., timeout=15)`. A `socket.timeout` / `URLError` /
  `ConnectionResetError` propagates raw. A non-JSON HTTP error becomes `RuntimeError`. None of these is
  `DeribitError` or `OrderStateUnknown`. A lost response on private/buy is the most common ambiguous
  outcome in practice, and G-h covers only error code 10050.
- executor.py.new:300 `except do.DeribitError` -> fail_closed never runs. R1: the fake exchange accepts
  the buy, then the call raises `socket.timeout`. Result: TimeoutError escapes execute_plan, main()
  (:403) catches only ExecutionHalted, close_position is never called, pos=100 with 0 stops. Breaks
  invariants 1 and 2.
- Smallest fix: in `_call`, wrap `_post` for `creates_order=True` so any
  `(OSError, urllib.error.URLError, ValueError, RuntimeError)` becomes `raise OrderStateUnknown(...)`.
  For non-creating calls, convert it to `DeribitError` (code None). Then every existing
  `except do.DeribitError` handler routes it.

### C2. Poll-loop read failure escapes with a filled, unprotected position (CONFIRMED: R3)
- executor.py.new:316 `do.get_order_state(...)` is outside any try. If it raises (DeribitError after 3x
  10028 retries, or any transport error per C1) after a market fill and before ensure_stop, it escapes
  execute_plan. R3: pos=100, 0 live stops, close_position not called.
- Fix: wrap the whole poll-loop body (and the :352 verify and the targets section) in
  `try: ... except Exception as ex: fail_closed(f"R7 unexpected: {ex!r}")`, leaving out ExecutionHalted.

### C3. Both flatten paths cancel the protective stop BEFORE the flatten (CONFIRMED: R2, R5)
- executor.py.new:267-272: the S6 sweep runs `cancel_by_label(stop_label)` before `close_position` at
  :280-281. position_manager.py.new:133-149 does the same: it cancels by id and by label, then closes
  at :150-151.
- If close_position then fails (OrderStateUnknown, timeout, margin error), the position is left with
  no stop at all. That is worse than doing nothing. R2: order = cancel_by_label x2 -> close_position
  (10050) -> pos=100, 0 stops. R5: pos=300, 0 stops, "FLATTEN ITSELF FAILED".
- Fix: order the steps as cancel entries -> close_position -> verify pos==0 -> THEN cancel the stop and
  sweep the stop/target labels. The executor already does this for `stop["order_id"]` (:285); the S6
  label sweep undid it.

## HIGH

### H1. A non-DeribitError in any cancel aborts the flatten (CONFIRMED: R4)
- executor.py.new:244/252/271/278 and position_manager.py.new:136/148 each catch only
  `do.DeribitError`. A `ConnectionResetError` in one cancel jumps to the outer
  `except Exception` (:290 / :156) and skips close_position. R4: close_position not called, pos=100.
- Fix: inner loops `except Exception: pass` (log it). The flatten must be attempted regardless.
  C1's fix also mostly covers this.

### H2. kill_switch: phase-1 get_positions and authenticate are outside try; HALT is written last (CONFIRMED: R7, R8)
- kill_switch.py.new:63 is outside any try. If it raises, kill_all raises before cancelling anything.
  :151 authenticate and :153 kill_all both run before :156 `halt_path.write_text`, so any exception
  means no HALT. R7: TimeoutError, HALT not written, orders still open. R8: auth failure, HALT not
  written. Breaks invariant 5 ("leaves HALT so nothing restarts"), and the kill switch is the tool used
  exactly when the exchange or network is misbehaving.
- Fix: write HALT FIRST, as the first statement after the confirm check. Wrap phase 1 in try; on
  failure fall back to `instruments=["BTC-PERPETUAL"]` and record the error. Consider
  `private/cancel_all_by_currency` as the single phase-2 call.

### H3. daily_loss_monitor: a kill_all failure on breach means no HALT_DAILY_LOSS and a dead monitor (CONFIRMED: R9)
- daily_loss_monitor.py.new:154 kill_all runs before :160 HALT write. main() :184-189 has no try, so any
  exception (kill_all per H2, a get_account_summary timeout, a get_ticker 10028) ends the loop for good.
  Trading then continues unmonitored. R9: TimeoutError, HALT_DAILY_LOSS not written.
- Fix: on breach, write HALT_DAILY_LOSS first, then kill_all in try/except. In main(), wrap run_once in
  try/except. On N consecutive failures, write HALT_DAILY_LOSS (fail closed) rather than exit.

### H4. daily_loss_monitor state corruption silently resets the day's baseline (CONFIRMED: R10)
- :100-103 turns any JSONDecodeError/OSError into `{}`. ensure_day_state (:116-122) then re-snapshots
  `day_start_equity` from CURRENT equity and sets `breached_today=False`. save_state (:107) is a
  non-atomic `write_text`, so a crash or kill mid-write leaves a torn file. R10: a -800 USD day becomes
  total_pnl=0.0, ok=True, no halt. UnicodeDecodeError and non-dict JSON are not caught either (crash).
- Fix: atomic write (tmp + `os.replace`). If the state file exists but is unreadable, fail closed:
  write HALT_DAILY_LOSS with reason "state unreadable" and do not re-baseline.

### H5. position_manager treats a failed stop-state READ as "stop not live" and places extra stops (CONFIRMED: R6)
- position_manager.py.new:177-178 maps a read error to `"query_failed:..."`. That is not in
  LIVE_STOP_STATES, so :213-233 places a NEW stop_market while the old one is still live, and
  overwrites `stop["order_id"]`, so the old id is lost.
- With real timing (2s poll, 4s bound), 2 consecutive read failures produce 2 live stops, and then
  flatten_halt flattens a position that was protected all along. R6 (compressed poll): 7 live stops
  totalling 700 on a 100 position.
- The orphan stop is reduce_only, and the pos==0 branch (:190) cancels only the current id. The orphan
  then makes R8 refuse every later plan until manual cleanup.
- Fix: on query_failed, do not re-place. Only a confirmed non-live state (cancelled/filled/rejected/
  triggered) re-places. Separately, bound the time for query failures and flatten only after
  MAX_UNPROTECTED_SECONDS of consecutive failures, with the stop still in place during that window.

### H6. The FT-2 suite deletes the REAL halt and state files (PLAUSIBLE by reading)
- run_testnet_suite_ft2.py.new:97-100 and :128-131 `unlink()` `dlm.HALT_PATH` (execution/HALT_DAILY_LOSS)
  and `dlm.STATE_PATH` before and after T-c. Running the suite clears an operator's live daily-loss halt
  and resets the baseline of a concurrently running monitor.
- Fix: T-c should pass temp `halt_path`/`state_path` into run_once, and patch `ex.HALT_DAILY_LOSS_PATH`
  in-process. Also refuse to start the suite if HALT or HALT_DAILY_LOSS exists.

## MEDIUM

### M1. HALT_DAILY_LOSS fail-open on a garbage date (CONFIRMED: R12)
- executor.py.new:137-146: only `date == today` or `date is None` block. `20260928` (int), `"2026/09/28"`,
  `""` and `"2026-09-28 "` all go to the "stale" branch and do NOT block.
- Fix: block unless `date` is a string matching `^\d{4}-\d{2}-\d{2}$` AND is strictly before today.
  Better, block on existence (as daily_loss_monitor's own docstring :52-55 asks) and let the operator
  clear it.

### M2. Halt auto-resumes at 00:00 UTC, which contradicts the contract
- executor.py.new:140-146 treats yesterday's file as non-blocking. daily_loss_monitor.py.new:56-58 and
  executor.py.new:76-78 say "only an operator clears a hard halt, so it does not auto-resume". A breach at
  23:59 UTC resumes trading one minute later. Fix: pick one contract; the safe one is existence = block.

### M3. UTF-16 HALT_DAILY_LOSS -> UnicodeDecodeError escapes preflight (CONFIRMED: R11); UTF-8-BOM mislabelled (CONFIRMED: R11b)
- executor.py.new:131-134 reads `encoding="utf-8"` and catches `(JSONDecodeError, OSError, AttributeError)`.
  UnicodeDecodeError (a ValueError) escapes. PS 5.1 `Out-File` and `>` write UTF-16LE.
  No order goes out (preflight runs before auth), so this fails safe but as a crash with a traceback.
  A UTF-8 BOM (`Set-Content -Encoding UTF8` in PS 5.1) blocks, but is reported as "malformed".
- Fix: read with `encoding="utf-8-sig"`, try utf-16 on failure, and catch `ValueError` (which covers
  both decode and JSON errors).

### M4. Executor never re-checks HALT during a run (CONFIRMED: R14)
- HALT is checked once at preflight (:155). R14: HALT was written after rung 1 and rungs 2-3 were still
  placed. During a ladder of up to 600s, a kill_all by the monitor or CLI races the executor. If a fill
  lands before the kill, ensure_stop (:226) can place a new stop after the halt, and the targets loop can
  place orders after the halt.
- Fix: `_check_halt_files()` before every order-creating call in execute_plan (and in
  position_manager's re-place). On a hit, fail_closed("HALT observed mid-run").

### M5. "flatten + halt" is process-local only
- fail_closed/flatten_halt raise, and they journal a per-plan `mismatch_halt`, but they write no HALT
  file. The next plan with a new plan_id runs straight away. That includes a "FAIL-CLOSED ITSELF FAILED"
  case where the position has since been closed by hand. Fix: write `execution/HALT` in both paths.

### M6. Label truncation collisions (CONFIRMED: R13)
- executor.py.new:112 and position_manager.py.new:147/230 use `f"{plan_id}:{label}"[:64]`. The
  validator (trade_plan_validator.py:81) only checks that plan_id is a non-empty string. The schema's
  `^[a-zA-Z0-9_-]+$` is never enforced (no jsonschema) and has no maxLength.
- plan_id of 51 chars: `entry_rung_1` == `entry_rung_10`. 63 chars: stop == entry == target label.
  Two plan_ids with the same first 64 chars share every label, so cancel_by_label crosses plans
  (invariant 3). A ':' in plan_id is also allowed.
- Deribit cancel_by_label is exact-match, so there is no prefix risk otherwise. Today, R8 (a clean
  account is required) masks the cross-plan case. It becomes live with satellites/S1 concurrency.
- Fix: validator enforces `^[A-Za-z0-9_-]{1,40}$`, and `_xlabel` raises if the result exceeds 64
  instead of slicing.

### M7. Soak verdict ignores unresolved orders (CONFIRMED: R16)
- soak_report.py.new:262 computes `unresolved_orders`, but soak_verdict (:280-307) never uses it. A
  journal with a placed-but-never-resolved stop reports SOAK CLEAN. It is also noisy the other way:
  label-sweep, kill_all and fail_closed cancels are not journaled as `order_cancelled`.
- Fix: journal every cancel, and flag unresolved orders on plans whose final state is closed/halted.

### M8. S1 account cap is vacuous while R8 holds; position_manager assumes one plan per instrument
- executor.py.new:187-200: R8 refuses whenever pos != 0, so `current_notional` is always 0 when S1 is
  evaluated. S1 is then just "plan <= 10000".
- position_manager uses the whole-instrument position as the plan's position (:162) and resizes the
  plan's stop to it (:245). With two plans, each manager would resize its own stop to the combined size.
- Fix: document this as single-plan-only. Concurrency needs per-plan position accounting before R8 is
  relaxed.

## LOW

- L1. position_manager G2 "explained" check: `target_filled >= stop["amount"]` (:196). stop.amount has
  already shrunk after target fills, so a manual close of the remainder counts as explained.
  CONFIRMED (R15). Fix: compare against the original filled total (entry fills) or require
  `stop_fired or target_filled >= entry_filled`.
- L2. Executor targets loop (:369-371): `except do.DeribitError: continue` also swallows
  OrderStateUnknown, so a possibly-resting target is ignored and `remaining` is not reduced. It is
  reduce_only, so it cannot reverse the position, but targets can over-commit and leave orphans. Sweep
  by label on OrderStateUnknown.
- L3. Market-entry B079 post-fill breach (:219-221) is journaled only, not acted on.
- L4. MAX_UNPROTECTED_SECONDS uses `time.time()` (:220). Windows clock or NTP steps can distort it; use
  `time.monotonic()`. Poll latency plus 3x 10028 backoff (1+2+4s in `_call`) already exceeds the 4s
  bound, so the bound is looser than advertised.
- L5. Executor deadline path (:337-344): if the entry cancel keeps failing while the order stays open,
  the `continue` skips `time.sleep`, giving a hot loop of get_order_state and cancel calls until rate
  limited.
- L6. daily_loss_monitor PnL = delta BTC equity x mark. Deposits, transfers (future satellite
  sub-accounts) and funding all count as PnL. `breached_today` stays True after an operator clears the
  HALT the same day, so a further drawdown that day is never re-halted.
- L7. daily_loss_guard.py.new: unused `datetime`/`dataclass` imports; `pnl_usd` missing is silently
  skipped (fail-open if a caller mistypes the key).

## Checked, no defect found
- Units: executor VWAP `filled_total / sum(fa/avg_price)` is the correct inverse (harmonic) average.
  size/max_position_size/max_notional_usd are all USD. risk_guard `mark_price=None` path is correct
  for get_position.size (USD).
- Short sign handling: `abs(size)` at the verify step, sign-flip check `(pos > 0) != is_long`,
  stop/target side mirroring. Float vs int size equality (100.0 == 100) is fine.
- UTC: every date/time uses `timezone.utc` or `time.gmtime`. No local-time path found.
- Testnet lock: BASE is hard-coded to test.deribit.com, and the secret must have `env == "test"`
  (invariant 6 holds).
- 13009 re-auth resend of an order-creating call: the request was rejected before it was processed,
  so resending is safe.
