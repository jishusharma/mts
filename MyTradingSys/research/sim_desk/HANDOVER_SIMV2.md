# sim-v2 hand-over (Builder, 2026-10-25)

Worktree `.claude/worktrees/mts-device-cleanup-5bfbdf`, branch `claude/heuristic-goldstine-7da61f`, trunk `origin/fast-track`.
Standing rules: testnet only; DEV only (2022-04-01..2024-06-30); public repo (percent and R only, no raw prices); `newline='\n'`; ship only via `python scripts/dev/sync.py ship --release sim-v2`; commit body has `Result:`; co-author `Claude Sonnet 5.5`; do NOT publish the static page; no quiz, badges, scoreboard, play animation.

## Done
- Batch 1 (shipped, cherry empty at the time): levels bug fixed (255 filled of 772 ideas, 517 never filled, mean -0.119 R, win 40.8%); result schema in `results/*.json` plus DESIGN.md "Result files" and "Catalogue"; `export_results.py` (levels_ladder, t09_live_parity, t06_cost_fill, t07_stale_verdicts, wavetrend_atlas); `build_catalogue.py` -> `results/_catalogue.json` (151 rows, 5 exported); `artifact/build_artifact.py` + `test_artifact.py`; TASK_REFINEMENT.md one line.
- Step (a) accuracy: `test_reference.py` (6 tests, 9 s), commit `0fc67ac06`. Levels 255/517/-0.1194; rsi 2 trades; wavetrend 369 trades; net = gross - fees; unfilled net exactly 0. The desk engine reproduces the reference.

## Shipped
`git cherry origin/fast-track HEAD` shows `0fc67ac06` NOT shipped. Ship it with the next commit (retry the gate until cherry is empty).

## Next (OVERRIDE order): step (b), then (c), (d), (e), each its own commit and ship; report each SHA and measured Run time to the Doctor
(b) Shared CONDITIONS panel (side, UTC hour window, EMA trend filter with typed timeframe and length, ATR-percentile band, weekday, "layer B fired within N bars"); free-form values labelled (ours); one TRIALS row per new setting; tests that fail on old code. Design decided, no code written:
- New `conditions.py` applied as a POST-FILTER in `desk.run_setting` after `study.run`, on rows' `touch_t` and `side`. Result-cache key excludes conditions (no re-simulation); TRIALS tag includes a condition label; output gets a `cond` field.
- Run outputs have no `side` array yet: add it in levels (`idea['side']`), and in rsi/wavetrend via `_bars.collect` (`ref[0]` from `make`); `collect` is at `studies/_bars.py` ~line 171 and builds the dict `day, touch_t, net, gross, fees, filled, refs, all_days`.
- Features causal: last CLOSED bar before `touch_t`, from `_bars.load_1m` resampled with `_bars.resample` to the typed timeframe. "Layer B within N bars" uses another study's cached signal times.
- Caveat to document: post-filter is exact only for independent trades; rsi/wavetrend allow one position at a time so filtered sets can differ from a true re-run.
- Add a conditions form to `page.html` and `/api/studies`; tests: hour window drops out-of-window trades, ledger row per new condition, side filter.
(c) Cached Run <= 10 s, run time (`run_seconds`) shown on page. Measured: levels uncached 8.7 s, cached 0.0 s; rsi 0.4 s; wavetrend 0.6 s (under load). Levels cache build `python desk.py --build` ~86 s (gitignored `cache/`).
(d) Equity curve in R and $1,000 (scrubbable) in `page.html`, plus run A vs run B side by side; add a `curve` example kind.
(e) `desk.py` writes `results/<id>.json` on every Run (id prefixed `desk-`); the static builder already adds missing exported results to the catalogue.

## Open problems
- Ship gate is flaky under load: `test_lease.py` times out at the 240 s per-step limit (passes alone, 108 s); one push race. Retry; avoid heavy CPU jobs during a gate.
- Catalogue `kind` is inferred from text (`kind_source`); 146 rows have no charts yet (backfill list in the Doctor's side-session-notes `sim-v2_backfill_list.md`).
- T07 audit prose says 8 of 10 reproduce, its csv says 9; the page follows the csv.
- Bash tool strips backslashes: use Write/Edit or `chr()` in Python strings.
