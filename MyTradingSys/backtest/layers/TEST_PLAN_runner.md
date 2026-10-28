# TEST_PLAN_runner.md — layers/runner.py (forward-return stats + run manifest)

Hand-computed / Python-scratch-verified expected values per the spec (Dumps/workers/NUC-QUEUE/specs/
074-layers-runner.md), covering D7's runner row and D5's manifest fields. A Haiku worker should turn
each case into a `unittest` method against the real module once built; do not re-derive expected values,
use these.

Public API under test:
- `forward_return_stats(events: list, closes: list, horizons=(1,3,5,10,20)) -> dict` — per horizon:
  `{"n","mean_return","hit_rate","mae"}`. `events` is a list of `{"i": int, "side": "long"|"short"}`
  (the bar index the event fires on and its direction; any extra keys, e.g. `rule_id`, are ignored).
- `baseline_return_stats(closes: list, horizons=(1,3,5,10,20)) -> dict` — same shape, computed over
  EVERY bar in `closes` (long-only convention), for the "hit rate vs a no-event baseline" comparison in
  D3.
- `build_manifest(**fields) -> dict` — assembles the run manifest (D5); a pure dict builder, validated
  for required-field presence, not numerically.

Return convention: for horizon `h` and event at index `i` with side sign `sgn` (+1 long, -1 short):
`ret = sgn * (closes[i+h] - closes[i]) / closes[i]`, only when `i+h < len(closes)` (otherwise this
event contributes nothing at that horizon — insufficient data, not a zero). `mae` (max adverse move) at
horizon `h` = `min(sgn * (closes[j] - closes[i]) / closes[i] for j in range(i+1, min(i+h, len(closes)-1)+1))`
(the worst point reached along the way to horizon h, inclusive) — using CLOSE prices only, since this
hand test's bars carry no separate high/low; the real runner should prefer intrabar low/high when the
bar dicts have them (documented as a scope note, not tested here). `hit_rate` = fraction of contributing
events with `ret > 0` at that horizon. `n` = count of contributing events at that horizon (events with
insufficient trailing data are excluded from `n`, `mean_return`, `hit_rate` and `mae`, not counted as 0
or as a miss).

## Case R1 — forward_return_stats, two events, mixed long/short, horizon data runs out

`closes = [100,102,101,104,103,105,108,107,110,112]` (index 0..9, len 10).
`events = [{"i":2,"side":"long"}, {"i":5,"side":"short"}]`.

Per-event, per-horizon raw returns (computed via `ret = sgn*(closes[i+h]-closes[i])/closes[i]`; blank
means `i+h >= 10`, insufficient data, excluded):

| event | h=1 | h=3 | h=5 | h=10 | h=20 |
|---|---|---|---|---|---|
| i=2 long  (closes[2]=101) | (104-101)/101=**0.029703** | (105-101)/101=**0.039604** | (107-101)/101=**0.059406** | — | — |
| i=5 short (closes[5]=105) | -(108-105)/105=**-0.028571** | -(110-105)/105=**-0.047619** | — (i+5=10, out of range) | — | — |

`forward_return_stats(events, closes, horizons=(1,3,5,10,20))` ->
```
{1:  {"n":2, "mean_return":0.000566, "hit_rate":0.5, "mae":?},
 3:  {"n":2, "mean_return":-0.004008,"hit_rate":0.5, "mae":?},
 5:  {"n":1, "mean_return":0.059406, "hit_rate":1.0, "mae":?},
 10: {"n":0, "mean_return":None,     "hit_rate":None,"mae":None},
 20: {"n":0, "mean_return":None,     "hit_rate":None,"mae":None}}
```
(`mean_return` at h=1: (0.029703 + -0.028571)/2 = 0.000566. At h=3: (0.039604 + -0.047619)/2 = -0.004008.
At h=5: only the long event has data -> 0.059406, hit_rate 1.0 since it's positive.)

`mae` per event per horizon (min of the running `sgn*(closes[j]-closes[i])/closes[i]` for
`j in [i+1, min(i+h, len-1)]`):
```
i=2 long:  h=1 -> min over j={3}          -> 0.029703
           h=3 -> min over j={3,4,5}      -> min(0.029703, (103-101)/101=0.019802, 0.039604) = 0.019802
           h=5 -> min over j={3,4,5,6,7}  -> min(0.029703,0.019802,0.039604,(108-101)/101=0.069307,(107-101)/101=0.059406) = 0.019802
i=5 short: h=1 -> min over j={6}          -> -(108-105)/105 = -0.028571
           h=3 -> min over j={6,7,8}      -> min(-0.028571, -(107-105)/105=-0.019048, -(110-105)/105=-0.047619) = -0.047619
```
`mae` reported per horizon = the mean of the contributing events' per-event mae (same aggregation as
`mean_return`, averaged only over events with data at that horizon):
```
h=1: mean(0.029703, -0.028571) = 0.000566
h=3: mean(0.019802, -0.047619) = -0.013909
h=5: only i=2 has data -> 0.019802
```
Filled-in expected result:
```
{1:  {"n":2,"mean_return":0.000566, "hit_rate":0.5,"mae":0.000566},
 3:  {"n":2,"mean_return":-0.004008,"hit_rate":0.5,"mae":-0.013909},
 5:  {"n":1,"mean_return":0.059406, "hit_rate":1.0,"mae":0.019802},
 10: {"n":0,"mean_return":None,"hit_rate":None,"mae":None},
 20: {"n":0,"mean_return":None,"hit_rate":None,"mae":None}}
```
(6 significant figures; assert with `abs(got-expected) < 1e-4` on numeric fields, exact `None` on empty
horizons, exact `n`.)

## Case R2 — forward_return_stats, empty events list

`forward_return_stats([], closes, horizons=(1,3))` -> `{1:{"n":0,"mean_return":None,"hit_rate":None,
"mae":None}, 3:{"n":0,"mean_return":None,"hit_rate":None,"mae":None}}`.

## Case R3 — baseline_return_stats, h=1, long-only over every bar

`closes = [100,102,101,104,103,105,108,107,110,112]`. Every consecutive pair `(i, i+1)` for
`i in 0..8` (9 pairs), raw return `(closes[i+1]-closes[i])/closes[i]`:
```
0.02, -0.009804, 0.029703, -0.009615, 0.019417, 0.028571, -0.009259, 0.028037, 0.018182
```
sum = 0.115232 (verified by running summation), mean = 0.115232/9 = **0.012804**.
`baseline_return_stats(closes, horizons=(1,))` -> `{1: {"n":9, "mean_return":0.012804,
"hit_rate": 0.666667, "mae": ...}}` (hit_rate: 6 of 9 pairs are positive -> 6/9 = 0.666667; the three
negative pairs are i=1->2 (102->101), i=3->4 (104->103) and i=6->7 (108->107)).

## Case R4 — build_manifest required fields (D5)

D5 lists the manifest fields verbatim: "git hash, params_id, data file hashes, command, start/end, row
counts". `build_manifest(revision_hash="abc123", params_id="rsi_default_2026-09-28",
data_file_hashes={"BTCUSDT_1m.csv":"sha256:deadbeef"}, command="python layers/runner.py --tf 1h",
start="2026-09-28T00:00:00Z", end="2026-09-28T00:05:00Z", row_counts={"BTCUSDT_1m.csv": 43200})` ->
returns a dict containing exactly those keys (`revision_hash`, `params_id`, `data_file_hashes`, `command`,
`start`, `end`, `row_counts`) with the given values, plus a `run_id` key the function generates itself
(any non-empty string; the test only asserts it is present and non-empty, not its exact value).

### Case R5 — build_manifest missing required field raises

`build_manifest(revision_hash="abc123")` (missing `params_id`, `command`, `start`, `end`, `row_counts`,
`data_file_hashes`) -> raises `ValueError` (or `TypeError` if the module uses required positional/keyword
args without defaults — pick one and document it in the module docstring; the test only asserts some
exception is raised for a call missing required fields).
