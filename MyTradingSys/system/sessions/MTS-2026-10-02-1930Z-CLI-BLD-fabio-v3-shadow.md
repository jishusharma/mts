# MTS-2026-10-02-1930Z-CLI-BLD-fabio-v3-shadow
surface: CLI
host: JIS-NB
account: A
model: claude-sonnet-5-5
role: BLD
branch: fast-track
branch_alias: none
predecessor: none
lanes: none (no subagents)
started: 2026-10-02 19:30Z
ended: 2026-10-02 (commit carrying the MTS-Session trailer)
status: closed
commits: the commit with trailer MTS-Session: MTS-2026-10-02-1930Z-CLI-BLD-fabio-v3-shadow
handoff: promotion of live_runner_cli.py.new is supervisor-only (below)

## Scope
DIRECTION_REVIEW P7: source the 8 Fabio v3 NS-grid values (P01, P03, P04, P07, P12, P21, P31, P34) from his words
where a quote exists; the rest run shadow-only (collection_only signals, no orders). Live emitter staged as `.new`.

## Outcome
- FABIO_V3_SOURCING_2026-10-02.md: 8 rows, quotes verbatim at the spec locations (each checked as a substring of the
  located transcript lines). SOURCE 0 of 8, SHADOW 8 of 8: no quote gives a number. P31, P34: quote not located.
- Staged `MyTradingSys/backtest/layers/alerts/live_runner_cli.py.new` (gitignored; sha256 prefix d7e4384193c77f19;
  original 66e49658e1c693cb, last commit 7058bc2). Adds `make_fabio_v3_layer`, one registry key `fabio|v3_grid|1m`,
  72 grid cells (N 3 x p 2 x z_hi 3 x m_c 2 x f 2; g off, confirm entry, event mgmt). SHADOW alert: `collection_only`,
  `shadow_side`, no `side` -> auto_trader.layer_signal() returns no plan_args (unmapped). SOURCE alert: `side`, as any fabio.*.
  A cell is SOURCE only if every parameter is SOURCE; missing/partial = SHADOW.
- Test `test_live_runner_v3_shadow.py`: 9 pass on the staged file; 8 of 9 fail on the unpromoted file; mutating a SHADOW
  event to carry `side` fails 3 (a, b, partial-source). Existing 88 alerts tests pass against the .new via import hook.
  `run_all_tests.py --quick`: ALL TESTS PASSED (the gate picks the new test up).

## Supervisor: before promoting live_runner_cli.py.new (it will not fire on the current feed)
1. DATA: the live runner feeds Binance klines {t,o,h,l,c,v,tbv}. v3 needs order-flow bars (aggTrades: b99_*, fp, thr_days).
   On klines `fabio_v3_flow_window` returns None and the layer emits nothing (poll line shows `fabio|v3_grid|1m=0`).
   A 1m order-flow source for the live runner is a separate build. Until then promoting changes nothing at runtime.
2. BARS: runner `--limit` default 100; N 120/240 and the NY window need up to 390 bars (Binance klines limit 1000).
3. COST: 72 engine runs on 300 bars = 7.7 s per poll (synthetic bars); poll loop is 60 s. Trim the grid if it grows.
4. Shadow safety rests on the auto-trader having no layer_rules entry for these events (the turn_of_candle pattern). An
   explicit `collection_only` reject in `execution/auto_trader.py layer_signal` would not depend on that: supervisor call,
   execution/ is not claimed by this session.
5. alert_rate_check / canary were not run against `fabio|v3_grid|1m`; up to 72 alerts per signal bar.
6. Promotion: back up to `.pre_v3shadow`, rename .new, re-gate, restart live_runner_cli (supervisor only).

## Not done / notes
- SUPERVISOR_LOG.md has this session's claim line appended (uncommitted: not in the brief's three-path commit list).
- Other uncommitted paths in the tree (runtime/BUILD_REPORT.md, research/_archive/loose_2026-10/OPERATOR_RULINGS_2026-10-02.md) are not this session's.
- Claim on layers/alerts/ is released when the supervisor promotes or abandons the .new.
