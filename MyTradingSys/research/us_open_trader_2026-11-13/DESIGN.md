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
