# TOM ROW CACHE REGEN 2026-10-02 (T3, plan only - NOT run)

Session MTS-2026-10-02-1720Z-CLI-MON-diagnostics.

## Staleness check
- Commit 13295c8 (book_imbalance guard in `math_object_builder.py`): 2026-10-02T14:28:07+05:30 (08:58:07Z).
- `F:/MTS/data/tom_bt/*.rows.jsonl`: 57 files, mtimes 2026-09-30 02:42:38 .. 02:42:47 +05:30. That is about 2 days 12 h older than the fix.
- Verdict: STALE. `tom_bt_run.py:30-32` (`_rows_month`) returns early when `<month>.rows.jsonl` exists, so a plain re-run rebuilds nothing.

## Commands (supervisor/operator, from repo root; the F: cache is outside this session's ownership)
```
$ts = Get-Date -Format yyyyMMdd_HHmm
New-Item -ItemType Directory -Force F:\MTS\data\tom_bt\_archive_rows_$ts
Move-Item F:\MTS\data\tom_bt\*.rows.jsonl F:\MTS\data\tom_bt\_archive_rows_$ts\
Copy-Item F:\MTS\data\tom_bt\summary.json F:\MTS\data\tom_bt\_archive_rows_$ts\
python MyTradingSys\backtest\tom_bt_run.py rows 4
python MyTradingSys\backtest\tom_bt_run.py report
```
Move, never delete. `fabio_events.json` stays in place. `report` overwrites summary.json, hence the copy.

## Expected
- Input: 57 monthly files in `F:\MTS\data\tom_snapshots` (39 MB gz total), each with a `.meta.json`.
- `rows` prints 57 lines `<YYYY-MM>.rows.jsonl <n> <secs>s`; total 120,892 rows (same snapshots, same count as TOM_BT_SHORT_DIAGNOSIS_2026-10-02.md L8).
- Runtime: about 10 s with 4 processes (the old 57 files were written 02:42:38..02:42:47). Inferred from mtimes, not timed. `report` runtime not measured.
- Expected change: rows with `book_imbalance == 0.0` that were wrongly capped. Per the diagnosis, SETUP_FORMING goes 19 -> 28 (19 short, 9 long). Total rows and the proof histogram {0:10831, 1:20373, 2:39105, 3:39496, 4:10767, 5:320} should not change if proof is computed before the contradiction cap; this is the diagnosis' reading, not checked here. If either differs, stop and report.
- Gate first: 13295c8 is titled "WIP partial, unverified"; run `python scripts/dev/run_all_tests.py --quick` before trusting the new cache.
