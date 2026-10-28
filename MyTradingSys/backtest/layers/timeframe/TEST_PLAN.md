# TEST_PLAN.md — timeframe layer (tf_resample.py)

Hand-computed expected values per the spec (Dumps/workers/NUC-QUEUE/specs/070-tf-resample.md), covering
D1 (RSI_TF_LAYER_DESIGN.md). Registry used throughout: `layers/timeframe/registry.json`.
All timestamps are UTC. Values computed by hand and cross-checked with Python `datetime`/arithmetic
scratch (not the future implementation). A Haiku worker should turn each case into a `unittest` method
against the real module once built; do not re-derive expected values, use these.

Public API under test:
- `bucket_start(t_ms: int, tf: str, registry: dict) -> int` — pure boundary math, no aggregation.
- `bucket_end(t_ms: int, tf: str, registry: dict) -> int` — bucket_start plus the bucket's duration.
- `resample(bars_1m: list, tf: str, registry: dict) -> list` — full aggregation: merges 1m bars into
  closed bars only, with a gap count. Built on top of `bucket_start`/`bucket_end`.

Bucket boundary rules (registry `unit` field): `seconds` -> floor(epoch_sec / seconds) * seconds.
`days` -> anchor_day = epoch_day of `anchor_date` (UTC midnight); bucket_day = anchor_day +
days*floor((epoch_day - anchor_day) / days). `week` -> Monday 00:00 UTC: epoch_day 0 (1970-01-01) is a
Thursday, so Monday is the day where `epoch_day % 7 == 4`; bucket_day = epoch_day - ((epoch_day - 4) % 7)
(Python `%` is non-negative for a positive divisor, so this holds for any epoch_day, including dates
before 1970). `month` -> first day of the UTC calendar month containing t_ms.

A bucket is **closed** (eligible for output) only when `bucket_end(bucket_start, tf, registry) <=
last_bar_close_ms`, where `last_bar_close_ms` = the close time (t + 60000) of the LAST 1m bar in the
input list. This is what makes `resample` emit closed bars only, never a partial trailing bucket,
regardless of how many bars happen to already be present in it.

`n_expected` minutes per bucket: seconds-kind = seconds // 60; days-kind = days * 1440; week = 10080;
month = (bucket_end - bucket_start) // 60000 (calendar-dependent, e.g. 41760 for Feb 2024 (leap),
43200 for a 30-day month). `gap_count` = n_expected - n_actual (count of 1m bars actually present in
the bucket), never negative.

## Part A — bucket_start / bucket_end boundary math (2d, 3d, 5d, 1w, 1M anchoring)

Reference epoch days (registry anchor_date "1970-01-01" => anchor_day = 0), computed from UTC calendar
dates via `datetime(y,m,d,tzinfo=utc).timestamp() // 86400`:

| date (UTC) | epoch_day | epoch_day % 7 |
|---|---|---|
| 2026-09-28 (Mon) | 20724 | 4 |
| 2026-09-29 (Tue) | 20725 | 5 |
| 2026-09-30 (Wed) | 20726 | 6 |
| 2026-10-05 (Mon) | 20731 | 4 |

### Case TF-A1 — 2d bucket_start, odd epoch_day
t = 2026-09-29 00:00 UTC (epoch_day 20725). `2d`: floor(20725/2)=10362, *2=20724.
`bucket_start(t, "2d", registry)` -> epoch_day 20724 * 86400000 = **1790553600000** (2026-09-28 00:00 UTC).
`bucket_end` -> bucket_start + 2*86400000 = epoch_day 20726 * 86400000 = **1790726400000** (2026-09-30 00:00 UTC).
(Reference point used throughout this file: epoch_day 20724 == 2026-09-28 00:00 UTC == 1790553600000 ms;
every other epoch_day's ms value below is that plus (day - 20724) * 86400000.)

### Case TF-A2 — 3d bucket_start, epoch_day 20724/20725/20726 fall in the same bucket
floor(20724/3)=6908, *3=20724 (exact). floor(20725/3)=6908 (rem 1) -> 20724. floor(20726/3)=6908 (rem 2) -> 20724.
So `bucket_start` for 2026-09-28, -09-29 and -09-30 (all UTC midnight) are all **1790553600000** (epoch_day 20724).
floor(20727/3)=6909, *3=20727 -> 2026-10-01 00:00 UTC starts a NEW 3d bucket at epoch_day 20727.

### Case TF-A3 — 5d bucket_start, bucket boundary crosses mid-week
floor(20724/5)=4144 (4144*5=20720, rem 4) -> bucket_day 20720 (2026-09-24 00:00 UTC), bucket spans
epoch_day 20720..20724 (2026-09-24 .. 2026-09-28).
floor(20725/5)=4145 (4145*5=20725, rem 0) -> bucket_day 20725 (2026-09-29 00:00 UTC): 2026-09-29 starts
a NEW 5d bucket even though it is only one day after 2026-09-28, because 20725 is itself a multiple of 5.
`bucket_start(2026-09-28 00:00 UTC, "5d", registry)` -> **1790208000000** (epoch_day 20720, i.e. 2026-09-24 00:00 UTC).
`bucket_start(2026-09-29 00:00 UTC, "5d", registry)` -> **1790640000000** (epoch_day 20725, i.e. 2026-09-29 00:00 UTC itself).

### Case TF-A4 — 1w, Monday anchoring
t = 2026-09-30 15:00 UTC (epoch_day 20726, a Wednesday). bucket_day = 20726 - ((20726-4) % 7) =
20726 - (20722 % 7) = 20726 - 2 = 20724 (2026-09-28, the Monday of that week).
`bucket_start` -> epoch_day 20724 * 86400000 = **1790553600000**. `bucket_end` -> + 7*86400000 =
epoch_day 20731 * 86400000 = **1791158400000** (2026-10-05 00:00 UTC, the next Monday).
Edge check: t = 2026-09-28 10:15:00 UTC (a Monday, mid-day) must bucket to the SAME Monday 00:00, not
the following one: epoch_day 20724, (20724-4)%7 = 20720%7 = 0 -> bucket_day 20724 (unchanged). Confirms
a timestamp already on the Monday does not shift.

### Case TF-A5 — 1M, calendar month incl. leap year
t = 2026-09-30 23:59:00 UTC. `bucket_start("1M")` -> 2026-09-01 00:00 UTC = **1788220800000**.
`bucket_end` -> 2026-10-01 00:00 UTC = **1790812800000**. n_expected minutes = (1790812800000 -
1788220800000)//60000 = 2592000000//60000 = **43200** (30 days).
Leap-year case: t = 2024-02-29 12:00:00 UTC. `bucket_start` -> 2024-02-01 00:00 UTC = **1706745600000**.
`bucket_end` -> 2024-03-01 00:00 UTC = **1709251200000**. n_expected minutes = 2505600000//60000 =
**41760** (29 days, leap February correctly counted).

## Part B — resample() aggregation, alignment, gap counting, closed-bars-only

`t` values below are epoch MINUTES for readability (real `t` is epoch ms = minute * 60000). Every bar
has `v=1` unless noted, so `v` in the output bar equals the count of source bars summed. `last_bar_close`
= t of the last input bar + 1 minute.

### Case TF-B1 — 3m, data NOT starting on a 3-minute boundary (alignment) + gap + closed-only
Input 1m bars at minutes **7, 8, 9, 10, 11, 12** (o=c=h=l=minute value, v=1 each). last_bar_close = 13.
Bucket boundaries (floor(minute/3)*3): min7,8 -> bucket 6 (window 6,7,8 — minute 6 is MISSING from input:
gap). min9,10,11 -> bucket 9 (window 9,10,11 — complete). min12 -> bucket 12 (window 12,13,14).
- bucket 6: bucket_end = 9. last_bar_close(13) >= 9 -> CLOSED. n_expected=3, n_actual=2 (7,8 present, 6
  missing) -> gap_count=1. o=7 (first present bar in the bucket, NOT the missing minute 6), c=8, h=8, l=7, v=2.
- bucket 9: bucket_end = 12. 13>=12 -> CLOSED. n_expected=3, n_actual=3 -> gap_count=0. o=9, c=11, h=11, l=9, v=3.
- bucket 12: bucket_end = 15. 13 < 15 -> NOT CLOSED -> excluded from output even though 1 bar (minute 12)
  is present in it.
`resample(bars, "3m", registry)` ->
```
[{"t":6,"o":7,"h":8,"l":7,"c":8,"v":2,"gap_count":1,"n_bars":2},
 {"t":9,"o":9,"h":11,"l":9,"c":11,"v":3,"gap_count":0,"n_bars":3}]
```
(t is the bucket's epoch-minute start here for readability; real output uses epoch ms.)

### Case TF-B2 — 10m, full data run, closed-bars-only cuts a bucket with 5/10 bars present
Input 1m bars at minutes **0..24** inclusive (25 bars, o=c=h=l=minute, v=1), last_bar_close = 25.
Buckets (floor(min/10)*10): bucket 0 = minutes 0-9 (complete, 10 bars). bucket 10 = minutes 10-19
(complete, 10 bars). bucket 20 = minutes 20-29, but only minutes 20-24 exist in input (5 bars).
- bucket 0: bucket_end=10, 25>=10 -> CLOSED. gap_count=0. o=0,c=9,h=9,l=0,v=10.
- bucket 10: bucket_end=20, 25>=20 -> CLOSED. gap_count=0. o=10,c=19,h=19,l=10,v=10.
- bucket 20: bucket_end=30, 25<30 -> NOT CLOSED -> excluded, even though it has 5 real bars and would
  otherwise look like "5 missing / gap_count=5" — closed-bars-only takes precedence over gap accounting;
  a not-yet-closed bucket is never emitted with a gap_count at all.
`resample(bars, "10m", registry)` ->
```
[{"t":0,"o":0,"h":9,"l":0,"c":9,"v":10,"gap_count":0,"n_bars":10},
 {"t":10,"o":10,"h":19,"l":10,"c":19,"v":10,"gap_count":0,"n_bars":10}]
```

### Case TF-B3 — empty input
`resample([], tf, registry)` -> `[]` for any tf (no bars, nothing can be closed).

### Case TF-B4 — unknown timeframe key
`resample(bars, "7m", registry)` (not in registry) -> raises `KeyError` (or `ValueError`; pick one and
document it in the module docstring — the test only asserts that some exception is raised, not which).

### Case TF-B5 — 1d native-bar cross-check (correctness gate, D1)
This is the D1 correctness gate ("resampled 1d from 1m must equal Binance's native 1d archive bars
exactly") and is NOT a hand-computed unit case — it needs real Binance data and belongs in an
integration/backtest check, not this unit TEST_PLAN. Noted here so it is not silently dropped; tracked
as follow-up outside 070-075.
