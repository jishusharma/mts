# Lab build cards BLOCKED: gptb-volume-event-table, gptb-candle-pattern-event-table (2026-10-17)

## Cause
Both cards ended BLOCKED (4 runs: candle 2026-10-16 18:00Z and 18:30Z, volume 19:00Z and 19:30Z; MAX_ATTEMPTS=2 then SKIPPED, `codex_run.py:45`) with the same verdict: "required DEV 1h/4h klines are missing".
The klines exist on JIS-NUC. The card briefs named no usable path, so Codex looked in the wrong places:
- volume report: searched `Dumps/backtest` (absent on the NUC; `LAYER_LAB.md:62-63` says it is not copied) and found nothing (`reports/2026-10-16_gptb-volume-event-table.md`, "DEV data and row counts").
- candle report: card goal pointed at `F:/MTS/data/binance_tf/um` 1h,4h, which holds 2025-11..2026-09 only (11 files each); the DEV period 2022-01-01..2024-06-30 is not there (`reports/2026-10-16_gptb-candle-pattern-event-table.md`, "What was checked").
- The DEV source is `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz` (arrays t,o,h,l,c,v,tbv,n,atr; 41,784 bars; 2022-01-01 00:00Z .. 2026-10-07 23:00Z), also `klines_15m.npz`. The earlier bigtrade card used it (`bigtrade_event_table/REPORT.md:14`). No 4h file exists: 4h = 4 consecutive 1h bars at 00/04/08/12/16/20 UTC (`PRE_REG_VOLUME_2026-10-09.md:21`).
- The harness failure: `codex_run.py` `prompt()` carried no data location, and the runs ended in 66-169 s (the model bails on a missing input; `BAIL_S`, `codex_run.py:41`). Code and synthetic tests in both modules are green (volume 5 passed, candle 6 passed); only the data hookup is missing.

## Fix (this commit)
- `scripts/dev/codex_run.py`: new `DATA_HINT` line in `prompt()` (klines path, array names, 4h rule, DEV cut 2024-07-01, "binance_tf / Dumps are not the DEV source").
- `scripts/dev/test_codex_run.py`: `test_prompt_names_the_dev_kline_source_so_cards_do_not_block_on_missing_data`; fails on `git show HEAD:scripts/dev/codex_run.py` (1 failure, AssertionError on the klines path), passes now (55 tests OK).
- Cards `MyTradingSys/system/tasks/gptb-volume-event-table.json` and `gptb-candle-pattern-event-table.json`: goal now names the npz path, `reopened` stamp set (resets the 2 failed tries, `codex_run.py:871-877`), state ready, `tasks.py check` clean.

## Open items (not fixed here)
- DECISION (OURS): DEV cut for both cards is bar open < 2024-07-01 (volume pre-reg `PRE_REG_VOLUME_2026-10-09.md:23`; candle pre-reg `PRE_REG_CANDLE_PILOT.md:9-12` says through 2024-06-30, same boundary).
- `bigtrade_event_table/event_table.py:14` uses `DEV_END_MS = 2025-01-01`, six months past the repo DEV boundary (VALIDATION starts 2024-07-01). Needs an audit card; that table's rows after 2024-06-30 are not DEV.
- `gptb-oi-delta-event-table` is a different cause: OI snapshot inputs (`runtime_data/snapshots`) are absent (`oi_delta_event_table/REPORT.md`), card needs a data decision, left untouched.
- The existing modules take bars as arguments; the next run must add the loader (npz path param) and the real DEV row counts and TRIALS.md rows. The volume module's R definition (spike range, body direction) is an implementation choice: OURS.
