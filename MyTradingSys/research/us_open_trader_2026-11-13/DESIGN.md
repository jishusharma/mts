# us_open_trader DESIGN v1 (lead, 2026-11-13). Binding interface for all builders.

Package: `MyTradingSys/execution/us_open_trader/` (stdlib only, `sys.dont_write_bytecode = True`, tests beside the
code as `test_*.py`, same style as `MyTradingSys/execution/test_cotrade*.py`). TESTNET ONLY, no mainnet flag anywhere.
Every parameter carries a comment `SOURCED (<file>)` or `OURS`. Never read `.secrets/`, `.env`, keys.
Runtime output only under `<repo>/runtime_data/us_open_trader/` (gitignored; env override `US_OPEN_TRADER_DIR`).

## 1. Plan JSON (public-safe, committed next to the plan .md)
```
{"day":"2026-11-13","frozen_utc":"2026-11-13T13:10Z","ref_feed":"binance_spot_BTCUSDT","instrument":"BTC-PERPETUAL",
 "arm_utc":"13:35","flat_utc":"16:30","max_entries":3,"amount_usd":5000,"leverage":50,"be_at_r":1.0,
 "fee_per_side":0.0005,
 "orders":[{"id":"A","side":"buy","kind":"breakout","trigger":69620,"stop_dist":250,"target_dist":360,
            "level":"Europe high 69,571","confluence":["live_aid:EU_HIGH"],"arm_after":null}, ...]}
```
kind = breakout (buy triggers when price trades AT/ABOVE trigger, sell AT/BELOW) or fade (sell triggers when price
rises TO trigger, buy when it falls TO trigger). `arm_after`: id of an order that must be closed/cancelled/void first.
Today's file: `MyTradingSys/research/us_open_trader_2026-11-13/plan_2026-11-13.json` (on trunk).

## 2. engine.py (pure, no I/O, no clock) - the single source of rules for replay AND live
```
new_state(plan) -> dict                      # JSON-serialisable
step(state, bar) -> (state, events)          # bar = {"t": ms, "o","h","l","c"} on the ref feed; any bar length
replay(plan, bars) -> {"trades": [...], "events": [...], "state": state}
```
Rules (all OURS unless noted; plan md has the sources):
- Bars with t < arm are ignored. An order whose trigger is already crossed at the first armed bar's open is `void`.
- Flat + entries < max_entries: an armed order triggers per kind above; entry price = trigger. Two triggers in one
  bar: the one nearer the bar open wins. Each order fills at most once.
- Entry bar: if the bar's adverse extreme reaches the stop -> exit `stop` in that bar. Target is NOT counted on the entry bar.
- In position, later bars: stop touched -> exit at stop (reason `stop`, or `be_stop` once moved); a bar touching stop
  and target = stop. Target touched -> exit at target. After a bar whose favourable extreme >= be_at_r * stop_dist,
  the stop moves to the entry (event `move_stop`), effective from the next bar.
- First bar with t >= flat: an open position exits at that bar's open (reason `time`); everything else is cancelled; done.
- Survival: a breakout exiting at target cancels every other breakout. A breakout stopped out leaves the opposite
  breakout armed. A fade is armed only when its `arm_after` order is closed, cancelled or void.
- Events: {"t","type": enter|exit|move_stop|cancel|void, "order_id","price","reason"}.
- Trade row: order_id, side, kind, level, confluence, entry_t, entry, exit_t, exit, exit_reason, r_gross
  (signed move / stop_dist), r_net (r_gross - 2*fee_per_side*entry/stop_dist), stop_moved (bool).
- External exits (live): `force_exit(state, t, price, reason) -> (state, events)` for a server-side stop fill.

## 3. score.py
`score(plan_path, bars=None, out_dir=None)`: fetch public 1m klines for arm..flat+1 bar (hosts in order
data-api.binance.vision, api.binance.com; injectable fetch for tests), `engine.replay`, write
`runtime_data/us_open_trader/<day>.jsonl` (one trade row per line + one summary row, `"mode":"replay"`), print a
markdown summary table (public numbers only) to stdout. The Live Aid learner reads this jsonl: keep keys stable.

## 4. levels.py + plan.py
levels.py `gather(day, now, fetch=None) -> {"price","atr15","atr1h","levels":[{"price","name","source","label"}]}`:
reuse `scripts/dev/analyst_levels.py` and `MyTradingSys/tools/live_aid/daily_playbook.py` (`key_levels`,
`value_area`, `session_stats`) by import; do not copy their logic. ATR(14) Wilder on closed bars.
plan.py `build_plan(gathered, day) -> plan dict` + `render_md(plan, gathered) -> str`. Rules (OURS): breakout
trigger = session (Europe) high/low +- 0.2*ATR15 (rounded to 10); stop_dist = 1*ATR15 rounded to 10, floored at
0.08 % and capped at 1.43 % of price (SOURCED Habib range, `research/imbalance_qriptal_2026-10-16/discord/README.md:15`);
target = min(2*stop_dist, distance to the next level beyond - 20); skip an order whose target < 1*stop_dist; fades at
the first analyst cluster beyond each breakout target, 20 in front of it, target 2*stop_dist;
amount_usd = min(5000, risk_guard.MAX_ACCOUNT_NOTIONAL_USD / 2); refuse a plan whose stop_dist/price*leverage >= 0.5
(stop must sit far inside liquidation). Reference output: today's hand-made plan json/md must be reproducible in shape.

## 5. cotrade.py addition (live-path file, minimal diff) : `close_trade`
`close_trade(client=None, account=None, journal_dir=None, halt_path=None, env=None, reason="") -> dict`
Testnet check first. Order of operations: (1) `client.close_position` (reduce-only market) (2) verify position == 0
(3) `client.cancel_by_label(LABEL)` (4) journal state `closed` (add `closed` to RECONCILED). NEVER cancels the stop
before the position is flat. Flat already -> cancel leftovers, journal `closed`, ok. Any failure in (1)/(2) ->
existing `_flatten_and_halt` pattern + journal `unknown`. A normal close writes NO HALT. CLI: `cotrade.py close`.
Tests: restart (journal says open, exchange flat), API error on each step, non-testnet env refused with no call,
OrderStateUnknown never retried, new `place` allowed after `closed`.

## 6. runner.py (live watcher, WAVE 2, after engine + close_trade exist)
`run(plan_path, mode="paper"|"testnet", poll_secs=5, clock=..., sleep=..., price_fn=..., client=..., said=...)`.
Loop until flat time + done: poll ref price (public), feed `engine.step` with a tick bar (o=h=l=c=price, or
hi/lo since last poll), act on events:
- enter  -> `cotrade.place_order(said, side, "market", None, amount, stop)`; stop = deribit mark -/+ stop_dist
  (basis = mark - ref stored in state; every exchange price = engine price + basis). Refusal or failure -> engine
  order marked cancelled, no retry.
- move_stop -> `cotrade.ensure_stop(stop_px=new + basis)`.
- exit target/time -> `cotrade.close_trade`.
- each poll in position: `get_position`; flat on the exchange = server stop filled -> `engine.force_exit(..., "stop")`.
State file `runtime_data/us_open_trader/state_<day>.json` written atomically after every event.
Fail closed: missing/corrupt state on a mid-session restart, state/exchange mismatch (position without state),
HALT file, stale price (> 30 s), or any cotrade `ok: False` -> NO new entries for the day; an open position stays
under its server stop and is still closed at flat time. Never widens a stop. Never touches orders without label
`cotrade`. `mode="paper"` makes no exchange call at all. `--said` is required in testnet mode (operator's words).
Tests: restart mid-position, restart with corrupt state, price feed errors, cotrade refusal, server stop detected,
flat-time close failing, HALT present, paper mode makes zero client calls.

## 7. recorder.py (scope add, operator 2026-11-13 ~13:10Z; cadence SOURCED OPERATOR_DECISIONS.md 2026-11-12 13:05Z)
`MyTradingSys/execution/us_open_trader/recorder.py`, replaces the stop-gap `research/us_open_trader_2026-11-13/record_now.py`
(keep its record keys: ts_utc, kind, binance_spot, bybit, bybit_1m, bybit_15m, okx, deribit, levels_touched, gaps).
Cadence (his words 11-12: "hourly in the Asian/Eur sessions, every 15 mins 2 hr before US open, every min from US open
-2 min to +15 min, then every 10-15 mins during the US session"): pure `next_due(now, open_dt)`; open from
`MyTradingSys/tools/us_open_alert.py open_utc` (DST-aware; do not hard-code 14:30). Until 21:00Z.
Readings per tick, per venue where public REST answers (each call independent, a failure is a recorded gap, never
an invented number): price, hi/lo since last, volume, net delta + CVD (Binance spot taker split via
data-api.binance.vision), open interest, funding, long/short share (Bybit), Deribit perp mark/OI/funding, Bollinger(20,2)
and RSI(14) on 1m and 15m, levels touched (levels from the day's plan json), large trades and footprint line by reusing
`scripts/dev/footprint_12h.py` if it can be called without a download (else gap). Known gaps to state in every record:
liquidations (no public REST; see `tools/live_aid/xliq_collector.py` for what exists), CoinGlass (needs a browser; Chrome
tools are off), fapi.binance.com (does not answer on this machine: try, record the gap).
Output: `runtime_data/us_open_trader/readings_<day>.jsonl` (git-ignored), append-only, one JSON per line; restart-safe
(CVD resumes from the last line of the day's file). `--once`, `--until`, injectable fetch/clock/sleep; tests offline.

## 8. Daily auto-start (no scheduler: SCHEDULING_POLICY.md)
`scripts/dev/supervisor.py plan` prints one RUN line on US trading days from 2 h before the cash open until 2 h after it:
`RUN US session (Agent, haiku): follow MyTradingSys/execution/us_open_trader/RUNBOOK.md` - hidden once the day's
session is claimed (`sync.py claim us-session-<day>`), so only one machine starts it. Weekdays only (OURS: the module
trades the US cash open, which does not exist at weekends). US market holidays are not skipped (OURS: no maintained
holiday list; the record is still wanted and the runbook notes a thin session). One line in the supervisor role doc.

## 9. RUNBOOK.md (`MyTradingSys/execution/us_open_trader/RUNBOOK.md`)
One file, one start command, numbered steps a Haiku worker can follow: command, expected output, on-failure action.
Steps: claim the day -> start recorder (background) -> build plan (plan.py; cites BIBLE.md, scenario ledger, Eagle_Eyes
session studies, yesterday's readings/score if present) -> paper runner (testnet mode ONLY when the supervisor passes the
operator's words via --said and the tree holds the testnet keys; otherwise paper) -> at flat time score -> ship the
public summary -> release the claim. Never touches .mts_live, HALT, or processes it did not start.

## 10. Design v2 changes (lead, 2026-11-13 ~14:00Z). BINDING: overrides DESIGN.md sections 1-6 where they differ.

Source: Opus design check (10 findings, all accepted). Builders: where v1 text and this file differ, this file wins.

## Process change (trunk went red at 13:23Z on an unregistered test file)
- Builders DO NOT run `sync.py ship`. Commit on your worktree branch (message body ends `Result: ...` and
  `Next: us-open-trader-module-1113`), report the branch name and commit. The lead merges, registers every new test file in
  `scripts/dev/extra_tests.tsv` (one row per test path; `MyTradingSys/tests/test_gate_discovery_b150.py` fails CI
  otherwise) and ships once. Do NOT edit `extra_tests.tsv` yourself (one writer: the lead).

## V2-1 engine: live mode never invents a stop exit
`new_state(plan, live=False)`. With live=True, `step()` emits `stop_hint` (no state change) where replay would exit on
stop/be_stop; the only stop exit is `force_exit`. Target, time, move_stop, cancel, void behave as in replay.
Test: live engine sees the stop touched -> still in position, hint emitted once per bar.

## V2-2 engine: `fill(state, order_id, t, price) -> (state, events)`
Live entry is two steps: step() emits `enter` (state: order `entering`, no position yet) -> runner places the order ->
runner calls `fill()` with the actual average fill price converted to the ref feed (fill - basis). Stop, target and
break-even level are rebased on the fill (entry = fill; stop = fill -/+ stop_dist; target = fill +/- target_dist).
`reject(state, order_id, t, reason)` marks the order cancelled (refusal, failure, slippage guard). In replay (live=False)
step() fills at the trigger at once as in v1. Slippage guard (OURS): runner refuses the entry (calls reject, places
nothing) when the current ref price is more than 0.25*stop_dist beyond the trigger.
Trade rows carry `mode`: replay | paper | testnet; live rows are scored from the fill.

## V2-3 engine: fade arming
A fade arms from the bar AFTER its `arm_after` order closed/cancelled/void, and only if that bar's open is on the
approach side (below the trigger for a sell fade, above for a buy fade); otherwise the fade is void. A touch = bar high
(sell fade) / low (buy fade) reaches the trigger. Tests with today's numbers: A target 69,980 == C trigger 69,980 (bar
high 70,150 -> C does NOT fill in A's exit bar; next bar opens 70,100 -> C void; next bar opens 69,900, high 69,990 -> C fills).

## V2-4 engine/runner: one bar shape
The runner steps the engine ONLY on closed 1m klines of the ref feed (same source and parser as score.py). No tick
bars. Parity test: the same 1m bars through `replay` and through the runner in paper mode (with fills at the trigger)
give identical trades.

## V2-5 plan: no leverage input
Remove `leverage` from the plan and from plan.py. Size from risk: `risk_usd` (OURS, default 18) ->
amount_usd = round_down_to_10(risk_usd * price / stop_dist), capped at risk_guard.MAX_ACCOUNT_NOTIONAL_USD / 2.
Remove the "stop_dist/price*leverage" guard and any "margin at 50x" wording. Deribit BTC-PERPETUAL is inverse and
cross-margined: the plan md says "leverage is reported after the fill as notional / account equity". The stop floor/cap
(0.08 % .. 1.43 % of price, SOURCED Habib) stays. Today's plan json keeps its `leverage` key: readers must ignore unknown keys.

## V2-6 cotrade.ensure_stop (live-path fix, with tests)
- Default stop when `stop_px is None`: the newest journaled `stop_placed` stop for the current position lineage (records
  after the last real place), else the place action's stop.
- Never loosen: if a live labelled reduce-only stop is tighter than the requested stop_px (higher for a long, lower for
  a short), keep it, return ok True with note "kept tighter stop"; do not place, do not cancel, do not flatten.
Test: break-even stop live, ensure_stop() with no stop_px leaves it untouched; explicit looser stop_px is ignored.

## V2-7 cotrade.close_trade (re-land of reverted 627330d8e, reworked)
Order: (0) refuse (journal `refused`, no client call beyond reads) when `_unknown_state` reports a ladder or hedge
lineage, when the last real place is a ladder, or when any OTHER co-trade slot holds a position (`rebuild`): tell the
caller to use kill. (1) read get_position; if 0 skip to (3). (2) close_position; on ANY exception re-read the
position: 0 -> continue to (3) with no HALT; still open after OrderStateUnknown -> HALT + journal `unknown`, do NOT
resend (the server stop stays); still open after another error -> existing `_flatten_and_halt` + journal `unknown`.
(3) cancel_by_label, then get_open_orders must show no labelled order: ok -> journal `closed` (RECONCILED); failure ->
journal `closed_cancel_failed` (UNRECONCILED, no HALT), return ok False; a re-run reconciles it.
`closed` is written only for a single-place lineage. Result dict includes `was_flat` (bool).
Tests: every branch above + restart (journal open, exchange flat) + stop filled in the race before (2) -> no HALT +
closed after ladder_placed / hedge_placed / unknown-in-flight all refused + new place allowed after `closed`,
refused after `closed_cancel_failed`.

## V2-8 runner (replaces v1 section 6 where different)
- Engine created with live=True in BOTH paper and testnet mode (paper simulates the exchange: fills at the next bar's
  open, a fake position that a simulated stop closes; zero client calls).
- Write-ahead: state gets `entering {order_id, t}` and is saved BEFORE place_order. On restart an `entering` intent is
  settled from the cotrade journal (placed record + exchange position): position present -> fill(); none -> reject().
- enter -> slippage guard -> `cotrade.place_order(said, side, "market", None, amount, stop)` with stop = mark -/+
  stop_dist; then read the fill (order average price) -> `engine.fill`; then liquidation check: read get_position
  `estimated_liquidation_price`; if the stop is not at least 2*stop_dist (OURS) inside it (or it cannot be read and the
  position is open) -> close_trade + no new entries.
- Basis = deribit mark - ref price, re-measured every poll with its time; never act on a basis older than 30 s.
- move_stop -> new trigger = engine stop + basis; if it is not at least 2 ticks on the protective side of the current
  mark -> `close_trade` (exit reason `be_close`) instead of sending a stop that would be rejected.
- exit target/time -> `close_trade`; `stop_hint` -> nothing (keep polling get_position).
- Every poll while the engine is in position: get_position; flat -> `close_trade` (cleans leftovers, journals `closed`),
  exit price from `get_user_trades_by_instrument_and_time` (no matching trade -> exit price unknown, row flagged,
  never invented), then `force_exit`.
- At flat time: `close_trade` is called unconditionally (whatever the engine thinks), then the engine is finished.
- Any cotrade `ok: False` -> no new entries for the day (state `halted_reason`), position management continues.
Tests add: write-ahead restart (both outcomes), stop_hint with position open -> no state change, flat-time
unconditional close, liquidation check fail -> closed, be_close path, basis stale -> no action, parity (V2-4).

