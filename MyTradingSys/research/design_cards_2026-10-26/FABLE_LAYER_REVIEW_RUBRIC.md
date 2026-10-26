# Fable: per-layer evidence rubric for the simulator desk (2026-10-26)

Card: `fable-layer-review-evidence-rubric`. Sources: the `layer-review-after-simulator` card, `MyTradingSys/system/LAYERS.md`,
`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md`, `MyTradingSys/research/sim_desk/desk.py` and `page.html`.

What the operator looks at on the simulator desk for each layer before deciding anything: one question and its numbers per row.
Rows 1-10 are on the simulator page today (name = the box on the page that shows them). Rows 11-12 are NEW on the simulator
page; the numbers exist today on the research desk. No row in this rubric decides a layer: it lists what to look at, never
what to do with the layer.

| # | Question | Numbers to look at | Where on the desk today (or NEW) |
|---|---|---|---|
| 1 | What does the verdict say, and why? | verdict word (PASSED / FAILED / NOT ENOUGH DATA) plus its reason line; for NOT ENOUGH DATA the power line "n trades can only rule out edges above about ±X R" and the "+0.10 R per trade ruled out" check | Verdict banner (top result block), `desk.py` `verdict()` |
| 2 | Is the filled count big enough? | filled n, ideas never filled (nofill); below 30 filled the desk refuses to call it | Numbers strip tile "trades (N ideas never filled)" |
| 3 | Does it make money after fees? | average per trade after fees, 95 % range around it, and the fee split "before fees +X / fees −Y / after fees Z R" | Numbers strip tiles (mean + range; gross / fee / net split) |
| 4 | Is it stable, or just wide? | day-block bootstrap 95 % range of the average net R; FAILED when the whole range sits below zero | Verdict banner sub-line |
| 5 | Which window was actually tested? | start / end dates, the "DEV window only (2022-04-01 to 2024-06-30)" banner; VALIDATION and HOLDOUT are never offered and any date outside DEV is refused by the date fields | Top banner; settings strip date fields |
| 6 | How many tries has this layer had? | try #N on this data + tries by the original study; the luck line "after N tries, luck alone reaches about ±X R per trade" | Verdict sub-line; footer line "Tries on this desk so far" |
| 7 | How bad can the path get? | max drawdown in R (peak to trough, shaded), Monte Carlo 5-95 % drawdown band over 1,000 reshuffles; end-of-curve $1,000-at-1 %-risk value | Equity curve box |
| 8 | Wins, losses, streaks? | win rate, profit factor, worst losing streak | Numbers strip tiles |
| 9 | Does it trade like a real trade on the chart? | one row per filled trade (date UTC, side, net R, running R); clicking a row draws its candle chart with entry, stop, target, exit | "Filled trades" table + its candle chart; "Example trade charts" fold |
| 10 | Where does the result come from? | average net R per year, per side, per 4-hour UTC bucket; "too few trades" mark on any bucket under 30 | "Where the trades came from" breakdown box |
| 11 | Are the layer's parameter numbers the trader's or ours? (label coverage: SOURCED / OURS / NO-SOURCE) | per-family counts, e.g. rsi 4 / 10 / 12, krown "stop distance and size are OURS", live_engine proof bands NO-SOURCE | NEW on the simulator page; today: LAYER_SHEETS.md "Parameters" column (per-family totals from LAYER_PROVENANCE_AUDIT.md) |
| 12 | What known bugs sit on this layer's runner or formulas? | recorded error ids, e.g. B146/B147/B131 (tom), B142 + T09 F1/F4 (fabio), B075/B136 (live_engine), invalid C1 detector (wavetrend) | NEW on the simulator page; today: LAYER_SHEETS.md "Errors found" column (BACKTEST_ERRORS ids) + LAYERS.md status lines |
