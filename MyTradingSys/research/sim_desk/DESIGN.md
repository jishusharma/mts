# Simulator desk: design (operator 2026-10-21; Opus proposal, chosen over Sonnet and Haiku because it checked the facts)

What he wants: ONE screen. Configure what to test (free-form values allowed: hit and try), click Run, the test runs with exactly those settings, a plain verdict and a few real example trades on tiny charts. Room for more layers later. Plain words; no internal names (LC3, ladder, KEEP, arm P) without a gloss. Thin first, critical first.

## Build
- One local app, stdlib `http.server` on 127.0.0.1, started by hand (`python desk.py`), no background service, no new installs. A claude.ai Artifact cannot run Python or reach F:/MTS/data, so it is not the app.
- Imports `levels_confluence_2026-10-14/ladder.py` and the `ladder_run.py` helpers unchanged.
- Layer-pluggable: a study is one small module with `params()`, `run(params)`, `describe()` and a plain-words label table (K5 -> "stop just past today's extreme"). The levels study is module 1; build no other.

## Screen
Top strip: plain-word settings + date range + Run. Verdict bar: PASSED / FAILED / NOT ENOUGH DATA + one reason. Three numbers: trades, mean net R, worst losing streak. Six trade charts (3 typical winners, 3 typical losers). Footer: "Trial #N logged. Tests run on this data so far: N."

## Run
- Stored setup (ladder_ideas_dev.csv holds only 24 S x K columns with exit X1, 3 extra exits for S2 K5 and arm P, plus E/family columns): filter rows + 2000-resample day bootstrap, about 1 s.
- Anything else: re-run `ladder.simulate` per month, about 3 min (full DEV took 180 s), progress line; cache `cache/<settings-hash>.json` (gitignored).
- Date lock: refuse an end date after 2024-06-30 in code (same assert as the runner). VALIDATION/HOLDOUT are never offered.
- Ledger: every real Run appends exactly one short TRIALS.md row before the result shows. A cached repeat adds none.
- Verdict: the card power rule (power_mde.py < 50 % = NOT ENOUGH DATA) governs; show the sample-sd rule as a one-line footnote. PASSED always reads "DEV only, needs validation".

## Charts (card sim-desk-charts)
After a Run pick the 3 trades closest to the median winner and loser (rule shown), re-run simulate() on that day's 1m bars, draw inline SVG 300x160, 5m candles from 30 min before the touch to 15 min after the exit; only level, entry, stop, target, exit; caption "+1.8 R, hit target 2"; 6-8 KB each; built on the fly, never committed (repo is public).

## Not now
Other studies / a general layer builder UI, equity curves, multi-asset, live or testnet hookup, saved presets, auth, VALIDATION read button.

## Lead review (Opus, 2026-10-21): what changed and why
- Overruled "lookup when stored, else 3 min re-run": the stored CSV holds only fee-net R per trade (no gross, no fee), so the card's power rule cannot be computed from it, and it covers 24 of 80 setups. Instead the first Run builds a local idea cache once (every trade idea plus that day's 1m bars, months in parallel, gitignored `cache/`); after that every Run, stored grid or free-form, re-simulates all ideas in seconds. The CSV stays only as a test cross-check.
- Overfitting brake, no new gate: the try number sits on the verdict bar itself ("try #N on this data; the best of many tries looks better than it is"), each new setting is one TRIALS.md row, a repeat is served from cache and adds none, and PASSED reads "on DEV only; needs its one validation run (not on this desk)".
- Layer-pluggable is a module shape, nothing more today: Tom's backtest (`backtest/tom_bt.py`) needs the Java snapshot pipeline, not a seconds-scale module; Fabio (`backtest/layers/fabio/fabio_of_model.py`, order-flow bars) is the likely study 2. v1 promises only the levels study.
- Free-form knobs v1: entry filter, scale-in, stop type, stop distance past the level (any %), exit (first level, ladder, or target at any R multiple), maker/taker fee (any %), date range inside DEV. Level-family subset left out (Haiku: next levels depend on the full set; exact only with a rebuild).
- Verdict order = the study runner's: lower CI above 0 -> PASSED (DEV only); else power_mde.py power < 50 % -> NOT ENOUGH DATA; else +0.10 R excluded -> FAILED; else NOT ENOUGH DATA. Sample-sd rule shown as a footnote.

## Result files (simulator page, card sim-v2)
One page lists every test. A test is one file `sim_desk/results/<id>.json`; `artifact/build_artifact.py` collects all of them into `artifact/index.html` (a new test = one new file; a missing field or a parameter without SOURCED|OURS fails the build). `export_results.py` writes the first ones from committed outputs; a test may also write its own file.
Fields: `id`, `family` (sidebar group), `title`, `what` (list of `{name, value_plain, label: SOURCED|OURS}`: rule, timeframe, costs, each parameter), `how` (2-3 lines), `window` (DEV only), `verdict` (`{label, tone: bad|good|warn|info}`), `why` (list of plain sentences), `kpis` (list of `{label, value, tone?}`), `examples`, `source_files`, `commit`.
Example kinds (`kind`, `title`, `caption`): `table` (`cols`, `rows`), `stack` (`rows` of `{label, parts:[{name, value %, tone}]}`), `sides` (`rows` of `{when, live, backtest}` with long/short/null), `replay` (`trades` as percent distances + `cum`), `none` ("no example trades exported"). Numbers only from precomputed files; no prices (percent distances and timestamps), the repo is public. Never invent examples: no chart data = a table plus `none`.
Added fields: `kind` (backtest | audit | thought_experiment), `parity` (null, or `[{layer, entries_match:[x,y], exits_match:[x,y]}]`, "41 of 43 entries match"), and an ROI kpi for trade tests (start 1,000 USD, fee-net end, window, assumption labelled OURS). A thought experiment uses the same layout: `what` = the question and the inputs, `how` = the reasoning steps, `kpis` = the numbers, `why` = the conclusion, `examples` only where real data exists.

### Catalogue
`results/_catalogue.json` (built by `build_catalogue.py` from tracked files only: `system/layer_map.json`, `research/**/RESULT*.md`, the DSA audit notes T01-T10, every `trials.csv`/`TRIALS.md`, and one row per remaining study folder) lists every known test: id, family, title, kind, verdict as written, source, exported. `kind` and verdict are read from the file text automatically (`kind_source: inferred from text`), so check them. The page lists all rows; one without a result file shows its verdict and source marked "charts not exported yet". To export a test: add `results/<id>.json`, add its source to `EXPORTED_BY_SOURCE` in `build_catalogue.py`, rerun `build_catalogue.py` and `artifact/build_artifact.py`.

## Conditions (shared panel, any layer)
`conditions.py` filters a study's trades before scoring: side, UTC hour window, EMA trend (timeframe and length typed), ATR-percentile band, weekday, "layer B fired within N bars". All values are free-form and OURS. Features use the last bar closed before the trade's touch time (causal). It is a post-filter: the cached run is reused, so a changed condition costs well under a second; each new condition adds one TRIALS row (`... ~ if <condition label>`). Exact for independent trades (levels); for rsi/wavetrend, which hold one position at a time, the filtered set is a subset of the unfiltered run, not a re-run. POST `/api/run` takes `cond`; GET `/api/conditions` lists the fields. Every result dict now carries `side`.
