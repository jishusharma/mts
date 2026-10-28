# consensus: one observation row per core alert

Doctrine: `MyTradingSys/research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md` :29-43 (consensus row), :76-83 (acceptance).
Consensus is an observation. It never gates, vetoes or delays a core, and nothing in this directory edits core state.
Every claim below cites file:line; "unknown" means the clone shows nothing.

Files (staged as `*.new` until the parent promotes them): `writer.py`, `test_writer.py` (this directory),
`../rsi/observation.py`, `../rsi/test_observation.py`.

## Status: nothing calls it yet

`append_row` is not wired into anything (no import of it exists in `live_runner_cli.py`, `live_runner_core.py`,
`auto_trader.py`). Hook points, owner and the snapshot id are open items (below).

## Invocation

```python
from MyTradingSys.backtest.layers.consensus.writer import append_row
from MyTradingSys.backtest.layers.rsi.observation import read_latest

ok = append_row(snapshot, tom, fabio, read_latest())       # True / False; never raises, never blocks
# optional keyword-only: notes="free text", base_dir=<dir holding the daily files>, now=<UTC datetime>
```

| argument | what the caller passes | what is written |
|---|---|---|
| `snapshot` | the snapshot / math-object dict (read only) | `snapshot_id`, `price` (see OPEN 1 and the price rule) |
| `tom` | dict like `auto_trader.parse_tom_alert(alert)` (`execution/auto_trader.py:103-119`), or `None` | block with exactly `verdict, setup, side, entry, stop, target, net_rr`; `None` -> `"tom": null` |
| `fabio` | dict with `verdict, model, side, entry, stop, target`, or `None` | block with exactly those six keys; `None` -> `"fabio": null` |
| `rsi` | `observation.read_latest()` result, or `None` | the six keys `1m,3m,15m,1h,4h,1d` always (null if absent), then any extra key (`5m`) unchanged |

Notes on the blocks:

- `parse_tom_alert` actually returns `{alert_no, verdict, zone_tf, time, setup, side, entry, stop, target, net_rr}`
  (`auto_trader.py:116-119`; `zone_tf` is also there) or `{}` when the alert is unusable (`:110-111`). The row keeps only the
  seven documented keys (ARCHITECTURE:37); `alert_no`, `zone_tf`, `time` are dropped (put anything worth keeping in `notes`).
  Pass `None`, not `{}`, when there is no Tom alert: `{}` is written as a block of seven nulls, `None` as `null`.
- The fabio block comes from the Fabio v3 core being built in parallel under `MyTradingSys/backtest/layers/fabio/v3`, whose
  output fields are `verdict, model, side, entry, stop, target`: this is per the wave-2 contract, not yet verified (that
  directory does not exist in this clone when this was written).
- A non-mapping `tom`/`fabio`/`rsi`/`snapshot` is logged and treated as absent; it is not an error.

## File and row

`<repo>/Dumps/consensus/consensus_<YYYYMMDD of the UTC date>.jsonl` (`Dumps/*` is gitignored, `.gitignore` "Dumps/*"; the directory
is created on first write). `base_dir` replaces `<repo>/Dumps/consensus`. UTC date and `utc_timestamp` come from one `now`
(default real UTC now; a naive datetime is taken as UTC, an aware one is converted). One row = one line, LF only, keys in
this order, `utc_timestamp` ISO-8601 UTC with milliseconds:

```json
{"snapshot_id": null, "utc_timestamp": "2026-10-01T19:30:15.123Z", "price": 67123.5,
 "tom": {"verdict": "SETUP_CONFIRMED", "setup": "pullback_long", "side": "long", "entry": 67000.0, "stop": 66800.0, "target": 67500.0, "net_rr": 2.4},
 "fabio": null,
 "rsi": {"1m": null, "3m": null, "15m": {"rsi": 51.0, "ma_sma": 49.0, "ma_ema": null, "support_or_reject": "support", "level": 40.0, "t_close": 1790000000000, "t_confirm": 1790000000000},
         "1h": null, "4h": null, "1d": null,
         "5m": {"rsi": 44.0, "ma_sma": 47.5, "ma_ema": null, "support_or_reject": "cross", "level": 40.0, "t_close": 1790000900000, "t_confirm": 1790000900000}},
 "notes": "snapshot_id absent in input"}
```

(The values are illustrative, hand-written for this document, not a real row.)

## The six-vs-seven timeframe note

ARCHITECTURE:39 lists six rsi keys (`1m,3m,15m,1h,4h,1d`); `observation.read_latest()` returns seven (it also has `5m`, because
the live runner registers `rsi_events` at 5m, `live_runner_cli.py:152-158`). The writer always writes the six architecture keys
(null if absent) and carries `5m` (any key not among the six) through unchanged after them. Acceptance ARCHITECTURE:82-83
("all six TF keys") is therefore met by every row regardless of what `read_latest` found.

## RSI block: which timeframes have a source today

Investigation (2026-10-01): `rsi_ma_events` has NO live producer (it is imported only by `rsi/run_rsi_backtest.py:50`, offline,
and not registered in `alerts/live_runner_cli.py:137-194`); no persisted output of it exists. The only persisted RSI output is
the alert files `MyTradingSys/runtime/alerts/<tf>.jsonl` (`live_runner_cli.py:263-273`, `alert_emitter.append_alerts_jsonl`
`alert_emitter.py:69-92`). One file per timeframe holds every layer's alerts for that tf; `observation.read_latest()` scans a
file backward for the newest line with `layer == "rsi"`, `sub == "rsi_events"` and `tf ==` the file's tf.

| tf | source today | file:line |
|---|---|---|
| 1m | none. The runner fetches 1m (default `--tfs "1h,15m,5m,1m"`, `live_runner_cli.py:247`) but registers no rsi layer at 1m; `1m.jsonl` carries `turn_of_candle` alerts only | registry `live_runner_cli.py:137-158` (rsi at 1h/15m/5m only), `:185` (turn_of_candle 1m) |
| 3m | none: not in default `--tfs`, no layer registered (`TF_SECONDS` in `auto_trader.py:48` has no 3m either) | `live_runner_cli.py:247` |
| 5m | `rsi_events` alert in `5m.jsonl` | registered `live_runner_cli.py:152-158` (tf at :155) |
| 15m | `rsi_events` alert in `15m.jsonl` | registered `live_runner_cli.py:145-151` (tf at :148) |
| 1h | `rsi_events` alert in `1h.jsonl` (the `malkan_bull`/`malkan_bear` 1h alerts, `:180-181`, are NOT used: different `sub` and event names) | registered `live_runner_cli.py:138-144` (tf at :141) |
| 4h | none: not in default `--tfs`, no layer registered | `live_runner_cli.py:247` |
| 1d | none: not in default `--tfs`, no layer registered | `live_runner_cli.py:247` |

"Source today" means a source exists in the code; the file only exists once the runner has emitted an `rsi_events` alert at that
tf. This clone has no `MyTradingSys/runtime/alerts/` directory (gitignored, `.gitignore` "MyTradingSys/runtime/alerts/*.jsonl"), so
here every tf reads all-None; whether the live machine has the files is unknown. Nothing here computes an RSI or fetches klines
to fill a gap.

Per-tf fields (all copied from the newest valid record, else None):

| field | from | cite |
|---|---|---|
| `rsi` | `record["rsi"]`: RSI(14) on the latest closed bar when the alert was first seen | `alert_emitter.py:41`, `live_runner_core.py:137-138,149-150` |
| `ma_sma` | `record["rsi_ma"]`: SMA(14) of that RSI | `live_runner_core.py:139` `_rsi_ma(rs, "SMA", 14)`; the record does not name the MA type, the producer code does (if the producer changes, this mapping is silently wrong) |
| `ma_ema` | always None: no live code produces an EMA of the RSI | grep of `"EMA"` outside `rsi_ma.py`/tests: none; `run_rsi_backtest.py:259` uses `"SMA"` |
| `support_or_reject` | `record["event"]` verbatim: `support`, `rejection`, `failure` or `cross` (so not only support/reject) | `rsi_events.py:70,78,93` |
| `level` | `record["level_value"]` | `rsi_events.py:85,94`; the live adapter uses `RSI_LEVEL` `live_layers.py:142` |
| `t_close` (extra) | `record["t_close"]`: OPEN time (ms) of the event bar, despite the name | `alert_emitter.py:46-47`, `auto_trader.py:221` |
| `t_confirm` (extra, not requested) | `record["t_confirm"]`: open time of the latest closed bar when first seen = the bar `rsi`/`ma_sma` belong to | `live_runner_core.py:151` |

Rules (tested): "latest" is the last valid matching line of the file; empty, non-UTF-8, non-JSON, non-object, other-layer,
other-sub and wrong-tf lines are skipped, so a half-written last line falls back to the previous valid rsi record and a file with
none gives all None; non-finite or wrongly typed numbers become None; only the tail is read (64 KiB chunks backward, at most
16 MiB, then stop: a match older than that is not found); a missing, unreadable or non-file path gives all None and nothing is
created. The default directory is `<repo>/MyTradingSys/runtime/alerts` (`auto_trader.py:46`); the runner's own default is
cwd-relative (`live_runner_cli.py:249`), so a runner started from another cwd writes elsewhere (pass `alerts_dir=`).

IMPORTANT staleness: the values are as of the last `rsi_events` alert on that tf (a rare event at one level), NOT the RSI at the
time of the consensus row. On 1h that can be many hours old. Compare `t_confirm` with the row's `utc_timestamp` before using a
block. A truly per-snapshot RSI per tf needs a producer that persists the RSI on every poll (not built; it would touch
`layers/alerts/`, which needs a SUPERVISOR_LOG ownership claim, CLAUDE.md). Related, not implemented: every alert of any layer
also carries `rsi`/`rsi_ma` for its own tf (`live_runner_core.py:149-150`), so the newest alert of any layer on a tf has a
fresher RSI, but it would mix fields from two different records; that is a decision for the parent/supervisor.

## OPEN items (nothing here is invented)

1. `snapshot_id`: there is no `snapshot_id` in `MyTradingSys/runtime/math_object_builder.py` (grep count 0) or anywhere else in the
   repo apart from the two 2026-10-01 design docs. Who mints it is unknown. The writer takes `snapshot.get("snapshot_id")` if
   present, else writes `null` and adds `"snapshot_id absent in input"` to `notes`. Rows can therefore not yet be keyed by
   snapshot_id (ARCHITECTURE:42); no id scheme is invented.
2. `price`: `snapshot["current_price"]` (key of the raw snapshot, `math_object_builder.py:6,43,64,91`, and of the math object
   it returns, `:376`), else `snapshot.get("price")`, else null. A key present with value `None` counts as absent.
   `math_object_builder` itself substitutes `0.0` for a missing `current_price` (`:64,:91`); the writer does not.
3. Hook points and owner: SCAFFOLD section 3 proposes Tom side at `auto_trader.py:507` and Fabio/RSI side at
   `live_runner_core.py:149` (`TWO_CORES_SCAFFOLD_2026-10-01.md:32`); which side owns the write is unknown. Both files are in
   areas that need a SUPERVISOR_LOG claim and staged `.new` edits. Boundary conflict found: `test_layer_boundaries.py:81-101`
   fails any `.py` under `execution/` that imports `MyTradingSys.backtest.layers...`, so `auto_trader.py` cannot import this
   writer from `layers/consensus/` without changing that rule or moving the writer (supervisor decision), and layers cannot
   import execution (`:43-79`).
4. Row timing: ARCHITECTURE:31 says "at the moment an alert fires from either core". Two different processes would write the same
   daily file; the writer takes no lock (by design), relies on one `write` of one short line in append mode, and was not tested
   with concurrent writers.

## Guarantees (each has a test in `test_writer.py` / `test_observation.py`)

- Append-only: mode `"a"`, `newline="\n"`, one write per row; never read back, rewritten or truncated; old bytes stay identical.
- Never raises, never blocks on IO or serialization errors: logs (`logging`, stderr by default, nothing on stdout) and returns
  `False`. Serialization happens before the file is opened (no partial line), `allow_nan=False` (every line is valid JSON).
- Arguments are not mutated; no network; no locks; stdlib only; no import from `execution/` (boundary test green).
- Writes only `<base_dir>/consensus_<date>.jsonl`; `observation.read_latest` writes nothing at all.
- Observation only: neither module is imported by, nor feeds, any core or gate.

## Acceptance (ARCHITECTURE:76-83)

| acceptance | status |
|---|---|
| :78-79 two cores emit verdicts independently | not covered here (core behaviour, not this module) |
| :80 every alert writes one consensus row ("fire N alerts, count N rows") | the writer half is tested (N `append_row` calls -> N lines, each valid JSON); the "every alert" half cannot be satisfied until the hook points above exist (owner unknown) |
| :81 every trade row carries source tom or fabio | not covered here (ledger) |
| :82-83 consensus row carries all six TF keys | satisfied by the writer for every row (tested with `rsi=None`, `{}`, partial, full); the VALUES are mostly null until 3m/4h/1d (and 1m) have a source (table above) and are stale between rsi events |

## Run the tests

`python -m unittest MyTradingSys.backtest.layers.consensus.test_writer MyTradingSys.backtest.layers.rsi.test_observation`
from the repo root (namespace packages, no `__init__.py`; `run_all_tests.py` Step 5b collects `MyTradingSys/backtest/layers/**/test_*.py`
as dotted modules). All tests write only under temp directories.
