# MTS-2026-10-03-CLI-BLD-r2-runner-exit
surface: CLI
host: JIS-NB
account: A
model: claude-sonnet-5-5
role: BLD
branch: fast-track
branch_alias: none
predecessor: MTS-2026-10-02-1930Z-CLI-BLD-fabio-v3-shadow
lanes: none (no subagents)
started: 2026-10-02 19:09Z (2026-10-03 local, IST)
ended: 2026-10-03 (commit carrying the MTS-Session trailer)
status: closed
commits: the commit with trailer MTS-Session: MTS-2026-10-03-CLI-BLD-r2-runner-exit
handoff: promotion of the 8 `.new` files is supervisor-only (checklist below)

## Scope
WHY_ENGINE_SILENT_2026-10-03.md section 4 row R2 (operator Ruling 2: apply the flagged defaults): take 50 % of size off at
`target`, run 50 % to `runner_target`, and move the stop to breakeven when leg 1 fills. Stage-only: every live-imported file
is a `.new`; no in-place edit under execution/, no restart, no HALT/AUTO_PAUSE touch, no orders.
This session's claim line is in SUPERVISOR_LOG.md and supersedes MTS-2026-10-03-CLI-BLD-tom-target-promote.

## T3 facts confirmed from disk (quoted)
(a) The alert card writer emits TARGET but not RUNNER_TARGET, and auto_trader's card regex does not know the field.
    - writer, `scripts/core/start-trading-day.ps1:319-320` (it is the PowerShell wrapper, not Python):
      `$lines += "TARGET:  $($top.math.target)"`
      `$lines += "R:R:     gross $($top.math.gross_rr) / net $($top.math.net_rr)"`
    - parser, `MyTradingSys/execution/auto_trader.py:102`:
      `CARD_FIELD = re.compile(r"^(VERDICT|TIME|SETUP|ZONE|ENTRY|STOP|TARGET|R:R):\s*(.*)$", re.M)`
    - `grep -rn RUNNER_TARGET MyTradingSys/execution scripts/core (*.py, *.ps1)` -> 0 matches before this session.
(b) `MyTradingSys/execution/executor.py:126-127` lists breakeven_after_fills:
      `UNSUPPORTED_STOPS = ("trailing_stop_metadata_only", "breakeven_metadata_only", "trailing_percent",`
      `                     "breakeven_after_fills")`
    and `executor.py:241` refuses on a second, independent condition:
      `if st in UNSUPPORTED_STOPS or (plan and plan["stop"]["type"] != "fixed_percent"):`

## Design (what was built and why it differs from the brief in two places)
Chain: Tom card `RUNNER_TARGET` -> `auto_trader.tom_signal` -> `new_plan.py --targets 50@a,50@b --breakeven-after-first-target`
-> validator -> `plan_compiler` (unchanged, already one order per plan target) -> `executor` (unchanged, target loop already a
list; the last target takes the remainder) -> `position_manager` moves the stop trigger to the entry after leg 1.

DEVIATION 1 - `breakeven_after_fills` was NOT lifted from UNSUPPORTED_STOPS. Evidence: that type means ladder RUNGS, not target
fills (`trade_plan_schema.json` "Stop moves to average entry once this many rungs have filled"; `plan_compiler.py:232-241`
`breakeven_metadata_only` with no price; `examples/valid_breakeven_stop.json` has no percent_below_entry, which
`executor.py:296` reads as `plan["stop"]["percent_below_entry"]`). Never implemented. Removing the tuple entry alone changes nothing (executor.py:241 still
refuses `stop.type != fixed_percent`); making it pass would mean redefining the type across validator, compiler, executor,
schema and the testnet suite, and would let an unimplemented plan type through pre-flight. Instead the request rides on a new
plan field `breakeven_after_first_target: true` with `stop.type` staying `fixed_percent` (the `max_hold_minutes` pattern):
the initial stop path is byte-for-byte the old one, and the ladder-rung type stays refused (a test pins that). If the
operator still wants the tuple edited, it is one line, but it is inert without the redefinition above.

DEVIATION 2 - `plan_compiler.py` and `executor.py` need no change, so there is no `.new` for them. `test_plan_compiler` pins
that a two-target plan compiles to two reduce-only orders 100 + 100 at 82985.5 / 82000.5 and that the new flag changes no order.

Breakeven rule (position_manager.py.new): once per plan, when the FIRST target order is completely filled AND |position| <
the original entry fill AND the live stop is already sized to |position| (after the G1 resize): edit the stop trigger to the
average entry fill (inverse-contract mean of the journaled entry fills, FORMULAS.md 11.4), snapped to the tick toward profit
(LONG up, SHORT down). Journaled as `stop_resized(reason=breakeven_first_target)` - the existing event, so
`journal.reconstruct_belief` stays right and a restarted manager replays it (trigger restored; a re-placed stop uses the
breakeven trigger; the move is never repeated).
Fails safe, never halts, never loosens: no verifiable entry average -> skipped + one journal `error`; mark at/through the entry
-> deferred and retried; edit error -> old stop untouched, retried up to BREAKEVEN_MAX_ATTEMPTS (5) then given up.
Decision recorded: a PARTIAL fill of leg 1 does not trigger it (test pins both halves). The 50/50 split is `runner_leg_pct`
(auto_trader DEFAULT_CONFIG tom, NO-SOURCE testnet default, operator Ruling 2; 0 = off). Absent / zero / not-beyond-target
RUNNER_TARGET, or a leg that would floor below 10 USD -> the old single-target plan, reason logged as `runner_skipped`.

## Staged files (all gitignored `*.new`, force-added; hashes = sha256 prefix; live = file now in the tree)
| staged | live sha / last commit | staged sha |
|---|---|---|
| execution/auto_trader.py.new | 0caef3f2b5fd5495 / c0123f6 | ed639a3c0eb3c4da |
| execution/new_plan.py.new | 383efb58a8519e32 / e8fec95 | 706fa76c0a0acb26 |
| execution/position_manager.py.new | 60262aaa5284133f / 863bae6 | 7447fa0ee66eb5d6 |
| execution/trade_plan_validator.py.new | e8cae05e127d97f0 / 5e387a1 | 3866a4df30f2bc6d |
| execution/trade_plan_schema.json.new (documentation only) | 5e2f31cb48b922c7 / e8fec95 | 5413d2aa01828225 |
| scripts/core/start-trading-day.ps1.new (card writer) | 67a42a7e3e43249a / 5c5a437 | 1679e96eb50dc509 |
| execution/test_auto_trader.py.new | - | 753413a9e033d4fa |
| execution/test_plan_compiler.py.new | - | 524e8f7e8a0011c7 |
New tests (plain files): execution/test_r2_runner_exit.py (7bcdca2e66340fa7), execution/test_r2_breakeven_move.py (1fbc6c9f4ffb1c23).
Also edited in place (not live-imported): scripts/dev/run_all_tests.py Step 1 module list (+2 names, else the gate never runs them).

## Tests
- test_r2_runner_exit: 18, staged all pass; pre-change 13 fail/error (the 5 that pass are regression guards: validator accepts
  valid plans, TARGET regex unchanged, `runner_leg_pct=0` = off, ladder-rung type still refused).
- test_r2_breakeven_move: 23, staged all pass; pre-change 16 fail/error (the 7 that pass are "stop is NOT moved" cases the old
  code satisfies trivially). Covers: moves on first fill / not before / not again (many polls AND restarts); partial leg-1 fill;
  position not shrunk; flag absent/false/"true"/1; missing plan file; SHORT tick snap; ladder inverse mean (79496.855 ->
  LONG 79497.0); restart replay (trigger 80000 restored, no edit, dead stop re-placed at breakeven not 79200, second restart
  no repeat, crash between fill and edit arms exactly once); API error (rejected edit: stop untouched, 5 attempts, then stops,
  no HALT, no close; transient rejection then success); mark at/through entry deferred; unreadable mark; unverifiable entry
  price; normal close after the breakeven stop fires.
- test_auto_trader.py.new + test_plan_compiler.py.new: 94 pass staged (this pair of modules); pre-change 11 fail/error (the
  new tests: RUNNER_TARGET parse, two-target args, config share, log fields, restart does not replay, compiler refuses a
  breakeven flag with one target or non-true).
- Pre-change runs used scratchpad `run_pre_change.py` (live files, `.new` code NOT applied, staged test files applied).
- Balance-move test: not applicable, no balance/equity read was added anywhere.
- `python scripts/dev/run_all_tests.py --quick` -> ALL TESTS PASSED (Maven/backtest skipped by design: no Java change).
- Tests are hermetic (temp journal/plans/HALT dirs, fake exchange, fake clock); run them through run_staged_tests.py, as the gate does.

## Supervisor: promotion checklist (nothing here is live until you do it)
Order matters: new_plan before auto_trader (auto_trader passes `--breakeven-after-first-target`; an old new_plan.py exits
non-zero on it -> plan_refused, fail closed, no trade); position_manager before the first runner trade (an old manager
ignores the flag: two legs but NO breakeven).
1. Promote with no trade open: trade_plan_validator.py, new_plan.py, position_manager.py (`.pre_r2` backups, rename, re-gate).
   The manager is a fresh python process per trade (spawn_manager), so new trades pick it up; running managers keep old code.
2. Promote auto_trader.py (+ trade_plan_schema.json as docs), re-gate, restart auto_trader (supervisor only).
3. Promote start-trading-day.ps1 and restart the wrapper (`loop-supervisor.ps1` relaunches it). Until then the card carries no
   RUNNER_TARGET and everything behaves as before. Java apparatus must be the c0123f6 build (it already emits runner_target;
   the Python mirror in the loop reloads every cycle).
4. First live runner trade: watch `execution/journal/<plan>.jsonl` for the `stop_resized` row with reason breakeven_first_target.

## Not verified / notes
- NOT verified against the real exchange: `private/edit` with a trigger price different from the placed one (G1 already sends
  trigger_price on every resize, but always the unchanged value). The move is fail-safe if Deribit rejects it; the first live
  runner trade is the proof.
- A breakeven stop at exactly the entry still loses fees and stop-market slippage on that leg; it is "no price loss", not "no cost".
- trade_ledger classifies a breakeven-stop exit after leg 1 as exit_reason "target" (`target_filled` > 0, trade_ledger.py:79):
  existing behaviour for any partial-target trade, not changed here.
- Only Tom alerts get runner legs; layer signals (fixed bracket, market entry) are untouched (test pins it).
- SUPERVISOR_LOG.md: claim line (committed with this session). Unrelated dirty paths left alone: runtime/BUILD_REPORT.md,
  `.claude/`, backtest/bt/bt_stats.py.stale_fragment_20261003.
- Claim on execution/ + layers/alerts/ is released when the supervisor promotes or abandons the `.new` files (layers/alerts/ was
  claimed but not touched).
