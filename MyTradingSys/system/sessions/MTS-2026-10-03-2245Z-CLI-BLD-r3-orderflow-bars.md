# MTS-2026-10-03-2245Z-CLI-BLD-r3-orderflow-bars
surface: CLI | role: BLD | model: claude-sonnet-5-5 | branch: fast-track | lanes: none | status: closed
predecessor: MTS-2026-10-03-CLI-BLD-r2-runner-exit (its layers/alerts/ claim is still open; this session only touches the staged .new there)

## T0 contract (quoted)
(a) R3, `MyTradingSys/research/_archive/loose_2026-10/WHY_ENGINE_SILENT_2026-10-03.md:46`: "| R3 | Live order-flow bar writer (aggTrades -> 1m OF bars with b99/fp/thr_days); live runner `--limit` >= 300 | Binance aggTrades websocket | v3 shadow rows appear in runtime/alerts with `collection_only` |"
    Cause row :27: "Fabio has no live input: v3 needs 1m order-flow bars, live runner feeds klines; OF files stop 2026-09-28".
    `research/fast_track_2026-09-27/OPUS_PLAN_2026-10-02.md` (the brief's path was wrong; real path is research/_archive/loose_2026-10/OPUS_PLAN_2026-10-02.md) has no R3 / order-flow text.
(b) "Order-flow bar" = the schema of `backtest/layers/fabio/orderflow_bars.py:10-17,39-42` (27 COLUMNS, 1m, USD-M aggTrades,
    10 USD fp bins, causal prior-30-day b99/b999 thresholds, thr_days). Spec: FABIO_V3_SPEC.md:25-29.
(c) Emitter: `backtest/layers/alerts/live_runner_cli.py.new` (staged; live file has no v3). Missing source consumed in
    `fabio_v3_flow_window` (.new:155-174; FABIO_V3_FLOW_COLS :137), called by `make_fabio_v3_layer._layer` (.new `flow_fn or ...`).
    No `.new.h3` exists.
(d) The emitter takes an IMPORT-time list of bar dicts (the registry's 1m klines). Klines lack the columns -> returns None.
    So a file reader was needed inside the emitter.

## Built
- NEW `MyTradingSys/backtest/layers/fabio/orderflow_live.py` (live writer + reader). Same 27-column schema and the SAME
  `aggregate_day` code as the offline tool. REST `/fapi/v1/aggTrades` paged by fromId, closed minutes only, resumable via
  `runtime/orderflow_live/_state.json`, daily CSV `runtime/orderflow_live/YYYY-MM-DD.csv`, 10-day retention, per-day
  `_qhist` sidecar so thresholds stay causal; priors also read from the offline archive's `_qhist` (F:). No prior day ->
  thr_days 0 (emitter refuses). Fetch error -> nothing written, state not advanced.
- STAGED `live_runner_cli.py.new`: `fabio_v3_live_flow` (default flow source). Bars with OF columns used as before; on klines
  it reads the writer files, cut at the last closed kline; behind/gap/thr_days 0/corrupt/missing -> None (silent).

## DEVIATIONS from the R3 roadmap row
1. REST polling, not websocket: no `websockets` package on this box; REST is resumable by id so a restart loses nothing.
2. `--limit` >= 300 NOT done: it is global to every TF and the other detectors were lag-calibrated on 99-bar windows.
   The v3 layer reads its own 390-bar window from the writer files, so klines `--limit` stays 100.
3. Writer lives in layers/fabio/ (next to the schema it reuses), not scripts/live/.
4. The writer is NOT started as a persistent process (persistent config / operator-supervisor step).

## Tests
- `fabio/test_orderflow_live.py` 9 tests: pre-change (module absent) collection error; with writer 9 pass.
- `alerts/test_live_runner_of_feed.py` 10 tests: pre-change (`OF_FEED_TEST_SOURCE=py`, live file) 10 fail; staged 10 pass;
  existing `test_live_runner_v3_shadow` still passes (19+9 = 28 OK).
- `run_all_tests.py --quick`: ALL TESTS PASSED.
## T4 manual run
`--once --since <6 min ago>` into a scratch dir: 6 bars, thr_days=27, no error. Minute 14:17-ish check vs `fapi/v1/klines`:
volume 14.484 / taker_buy 11.683 == writer 14.484 / 11.683. Emitter pickup is NOT demonstrated: the NY window (13:30Z +390 min)
is closed at run time and the staged .new is not promoted; covered by the stubbed-engine registry test instead.
## Promotion / start (supervisor)
1. Promote live_runner_cli.py.new (with the other staged v3 work), re-gate, restart the live runner.
2. Start the writer before the next NY open: `python -m MyTradingSys.backtest.layers.fabio.orderflow_live` (needs no key;
   add `--since <NY open ISO>` to backfill the current window).
