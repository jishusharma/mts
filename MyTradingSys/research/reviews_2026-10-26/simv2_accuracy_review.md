# sim-v2 accuracy batch — per-ship review

Trunk at `ec00608e`. All 9 commits verified in current code + tests (sim_desk 100 passed, 7 skipped; T06 cost_inventory 2 passed).

| commit | claim | verdict | proof | note |
|--------|-------|---------|-------|------|
| bba212e80 | Number strip: win rate, PF, max dd, gross/fee/net per trade; no duplicate vs `stats()` | HOLDS | desk.py:81–96 (`numbers()`); desk.py:60–75 (`stats()`); test_conditions.py:224–233 | `numbers()` and `stats()` are fully separate functions; `stats()` delegates to `ladder_run.cell`, `numbers()` recomputes only over `res['net'/'gross'/'fees']` — no shared intermediate. **Win-rate basis divergence**: `ladder_run` reports `win_rate = (gross>0).mean()` (ladder_run.py:185) but `desk.numbers` reports `(net>0).mean()` (desk.py:95). The page only renders `o.numbers.win_rate` (page.html:326); the `stats()` win_rate is in the JSON payload but not shown. So the strip label "trades that won" is honest to its net basis — the gap is that a reader comparing the strip number to a ledger/TRIALS row (gross basis, from `ladder_run.cell`) would find a different percentage with no annotation explaining why. |
| 1282d9c21 → cceaedf7b (revert) → 11b8f95c4 (re-land) | 0.02% slippage on market/stop fills only; limits unchanged; no leftover state from revert | HOLDS | _bars.py:23 `SLIP_DEFAULT=0.02`; _bars.py:176,207 (collect/replay merge slip into taker only); levels.py:169 (taker-only merge); costs.csv:203–205 (3 rows); test_cost_inventory.py 2 passed | Slippage is merged into `taker_pct` at the point of use — `collect` line 176: `(q['taker_pct']+q['slip_pct'])/100`; maker leg uses `q['maker_pct']/100` unchanged. In `levels.py._fees` line 169: `taker = (...)+ q['slip_pct']/100`, `maker` unchanged. No dangling references from the revert (current tree is the re-landed state). 0.02% = 2 bps is labelled OURS in costs.csv. |
| b99094841 | Equity curve shades drawdown; worst dd shown beside scrub readout | HOLDS | page.html:255–258 (polygon code); page.html:271 (`worst drawdown` in eqread); test_conditions.py:199 | |
| 2f2954f6e | Clickable trade list; row opens candle chart via /api/trade; entry/exit reason cols still missing | HOLDS | desk.py:124–131 (`trade_list`); desk.py:162–173 (`trade_chart`); page.html:283–301; HANDOVER_SIMV2.md:23 | **Confirmed**: `desk.py:139` `breakdown()` docstring states "The trade rows carry no exit or no-fill reason, so there are no reason columns." HANDOVER_SIMV2.md:23 repeats: "run results do not carry them yet." Core clickable list + /api/trade works. |
| afd937964 | MC reshuffle band (1000 fixed-seed) + luck line; luck = sd·√(2 ln N)/√(n) — DSR numerator, not full DSR z-test | HOLDS | desk.py:107–121 (`monte_carlo`, seed=7, shuffles=1000); desk.py:99–104 (`luck`); test_conditions.py:283–307 | **Explicitly NOT a DSR z-test**: `luck()` returns `sd * sqrt(2*ln(N)) / sqrt(n)` — the expected value of the maximum of N iid normal means. This is a heuristic upper bound on what pure luck could produce, not the z-statistic used in the Bailey/López de Prado DSR formula. The page label says "luck alone reaches about X R" (page.html:282), which is accurate. Fixed-seed test at test_conditions.py:283 asserts repeatable results. |
| 3ecd38c21 | Per-Run writes `results/desk-<study>-<hash>.json` in standard schema; `build_catalogue` picks it up | HOLDS | desk.py:393–422 (`export_result`); desk.py:425–431 (`refresh_catalogue`); build_catalogue.py:164–168 (step 7: desk-*.json loop) | `export_result` is called from the POST /api/run handler (desk.py:503) after each run. `build_catalogue.py` step 7 explicitly scans for `desk-*` files in the results dir and adds them as rows. |
| de7acbac6 | CONDITIONS post-filter (side, UTC hour, EMA, ATR, weekday, layer B within N bars); changed condition costs < 1 s | HOLDS | conditions.py:159–199 (`mask`); test_conditions.py:30–97 | EMA and ATR resampling is recomputed from the cached 1m array (`_bars._ALL` dict, not disk) on each `mask()` call — no I/O. The < 1 s claim in the commit message is not pinned to a test (the test asserts `< 10 s` budget, test_conditions.py:177). The sub-second number was a measured statement, not a regression guard. |
| 0337601f0 | Run-time display on every run; cached run under 10 s tested | HOLDS | page.html:342; test_conditions.py:168–178 | |
| 533eab730 | Equity curve in R and $1,000, scrubbable; A vs B side-by-side | HOLDS | desk.py:176–189 (`curve`); page.html:89–90 (equnit dropdown + pin A button); test_conditions.py:181–194 | |

## Regressions since ship

- **Win-rate basis split** (latent since bba212e80): `desk.numbers.win_rate` (net>0, the number the page shows) and `ladder_run.cell.win_rate` (gross>0, what TRIALS rows report via `stats()`) differ by however many trades fees flip from gross-positive to net-negative. No annotation and no test guards the two bases. Not a code bug — a readout-consistency gap.
- No other regressions found in current code. Slippage merge points, MC seed, catalogue pick-up, and all test assertions match the shipped claims.

## SOURCED vs OURS

| number | source |
|--------|--------|
| 0.02% slippage (SLIP_DEFAULT, levels DEFAULT) | **OURS** (labelled in _bars.py:23, costs.csv:203, levels.py:42) |
| BINANCE_MAKER / BINANCE_TAKER fee percentages | **SOURCED** (from `MyTradingSys/backtest/fees.py`, imported into _bars.py:16) |
| `ld.MAKER`, `ld.TAKER` (levels DEFAULT maker_pct/taker_pct) | **SOURCED** (from `ladder.py` constants, via levels.py:41–42) |
| MC shuffles=1000, seed=7 | **OURS** (desk.py:107) |
| Luck-line formula `sd·√(2 ln N)/√(n)` | **OURS** (desk.py:99–104; extreme-value approximation, not a trader formula) |
| Equity curve start $1,000 / 1% risk | **OURS** (desk.py:78) |
| conditions.py EMA/ATR/weekday parameters | **OURS** (defaults in conditions.py:25–27; all stated as "ours, tuned on DEV") |
