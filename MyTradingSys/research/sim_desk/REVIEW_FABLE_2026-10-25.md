# Simulator desk: Fable review against world-standard backtesters (2026-10-25)

Reviewed on trunk d021c4d01 in a fresh worktree on JIS-NB (login C). Read the OPERATOR OVERRIDE, INPUTS.md 1, DESIGN.md, PLUGIN.md, HANDOVER_SIMV2.md, desk.py, page.html, charts.py, the three studies, the artifact page. Built the levels cache once (71 s), ran 29 checks in-process and through the real server on a free port (stopped after), ran test_reference.py (6 pass, 8 s). Nothing in desk.py, page.html or studies/ was touched (sim-v2 is editing them). No card created.

## One screen

**The engine is sound. The report is thin.** Every accuracy check passes: 255 filled trades at -0.119 R, filled-only counting, fees applied, no look-ahead, sealed windows refused, one ledger row per new setting, cached Run in 0.2 s. The one real gap in accuracy is **slippage: none is modelled** (stops fill at the exact stop price). Against what traders see in TradingView, Amibroker or QuantConnect, the desk shows 3 numbers and 6 pictures where the world shows an equity curve, a drawdown, a trade list and about 6 standard numbers. Three of those numbers (win rate, max drawdown, fee share) are already computed and hidden.

The most useful fact found this run, in plain words: **the levels rule makes +0.22 R per trade before fees and loses -0.12 R after them, because its stop is so tight that a 0.07 % round-trip fee becomes a third of the risk.** Fees are not a footnote here; they are the whole result. The page should say this on the first line.

Top 5 changes (details in section 3): equity curve with drawdown; the standard numbers strip; a slippage box; a trade list you can click; Monte Carlo reshuffle bands (the "magical" one).

## 1. Basic checks

All through `desk.run_setting` with a temporary ledger and cache, then again through the running server. Numbers are from this machine, this run.

| Check | levels | RSI 40/60 | WaveTrend |
|---|---|---|---|
| Reproduces the known number | PASS: 255 filled (517 never filled), -0.1194 R, win 40.8 %, 95 % range [-0.369, +0.148] | PASS: 2 filled (3 never filled), -1.036 R (PLUGIN.md says 2) | PASS: 369 filled, -0.158 R, FAILED (regression pin 369) |
| Only filled trades counted | PASS: page n 255 = filled 255; unfilled net all exactly 0 | PASS: n 2 = filled 2 | PASS: n 369 = filled 369 |
| Fees applied | PASS: net = gross - fees on all 255; mean fee 0.337 R per trade | PASS: mean fee 0.036 R | PASS: mean fee 0.130 R, min 0.011 R |
| Slippage applied | **FAIL: not modelled.** Stops fill at the stop price, limit fills at the level; a gap fills at the bar open. No slip box, no default | FAIL (same engine, `_bars.run_trade`) | FAIL (same) |
| No look-ahead | PASS: all 255 fills at or after the touch bar; the E1 filter uses 5m bars closed before the touch (ladder_run.py:287); exits after fills by construction | PASS: all entries at or after the close of the signal bar (next bar open or later), exits after entries | PASS: same, 369 trades replayed |
| VALIDATION / HOLDOUT locked | PASS: end 2024-07-01 and start 2022-03-31 refused in code; server returns HTTP 400 with a plain sentence | PASS; bars read stop at 2024-06-30 23:59 | PASS; same |
| TRIALS.md row | PASS: 1 row after the first run, still 1 after a repeat (served from cache). Defaults were already in the real ledger, so the server runs added no row ("already tried") | PASS | PASS |
| Run time, cached | PASS: 0.22 s through the server (uncached 5.6 s; cache build 71 s once) | PASS: 0.13 s (uncached 0.3 s) | PASS: 0.08 s (uncached 0.3 s) |
| Plain error on bad input | PASS: "please type a number" (HTTP 400) | | |

Also checked: `/api/studies` lists 3 studies with their try counts (levels 8, RSI 1, WaveTrend 1); the server starts and stops cleanly; test_reference.py 6 passed.

Notes on the engine, all good: every study fills on 1m bars even when the signal is daily (TradingView calls this the bar magnifier and sells it as a premium feature); on one bar the stop is checked before the target (pessimistic, the right default); the fill bar never also takes the target; the data read stops at the DEV end by an assert, not just by a date box.

## 2. World standards: what the desk has

HAS / PARTLY / LACKS, with what the standard tools do.

| Standard practice | Who does it | Desk | Note |
|---|---|---|---|
| Equity curve | TradingView, Amibroker, QuantConnect, backtrader, vectorbt: always the first picture | LACKS | sim-v2 step (d) is building it (R and $1,000, scrubbable). Keep that order |
| Drawdown chart / max drawdown | all of them; QuantConnect draws it under the equity curve | PARTLY | `stats` already computes max drawdown in R (`maxdd`); the page does not show it |
| Trade list (date, side, entry, exit, R, running total) | all of them; TradingView "List of trades" tab | LACKS on the desk | the hosted artifact has a percent-distance replay strip for levels only |
| Monthly / yearly returns table | Amibroker, QuantConnect, vectorbt | LACKS | low value at 2-369 trades; one small table by month in R is enough |
| Net profit, profit factor, win rate, expectancy, max DD, Sharpe (the standard 6) | TradingView overview strip, Amibroker report, Lean banner | PARTLY | expectancy (mean net R) and n shown; win rate and max DD computed but hidden; profit factor not computed; Sharpe not shown (the day-bootstrap 95 % range is its honest cousin for per-trade R) |
| Commission | all | HAS | maker/taker both free-form, labelled, SOURCED |
| Slippage | all (TradingView ticks per fill; Amibroker, backtrader, Lean fill models) | LACKS | see check table. tom_bt already has `slip_pts`; the desk engine does not |
| Intrabar fills on a lower timeframe | TradingView bar magnifier (premium), Lean fill-forward | HAS | everything fills on 1m bars |
| Same-bar stop/target ordering | backtrader and vectorbt default stop-first; TradingView assumes a path | HAS | stop first; a card (intrabar-stop-target-ordering-sensitivity) exists for the sensitivity study |
| Look-ahead guard | Lean enforces by data feed; others by discipline | HAS | causal features, next-bar entries, assert on the data end |
| Position sizing, compounding, money result | all show $ |  PARTLY | artifact shows $1,000 at 1 % risk for levels; desk shows R only |
| Parameter grid / optimizer | TradingView Deep Backtesting, Amibroker optimizer, vectorbt broadcasting | LACKS on purpose | hit-and-try one setting at a time with a ledger row each is the safer version for a 27-month window. Keep it; never add a one-click grid without a trial count |
| Out-of-sample lock | Amibroker walk-forward, Lean "research then backtest", every quant shop | HAS | DEV / VALIDATION / HOLDOUT sealed in code; validation read once off the desk. Better than most retail tools |
| Walk-forward (rolling re-fit windows) | Amibroker built in; quants by hand | PARTLY | one fixed split, not rolling. Right call: 27 months is too short to roll; do not build it |
| Counting trials | almost nobody in retail; Bailey and Lopez de Prado insist | HAS | TRIALS.md row per setting, "try #N" on the verdict, prior-study tries counted. This is the desk's best feature |
| Deflated / trial-adjusted Sharpe | quant practice (Bailey, Lopez de Prado 2014) | LACKS | the try count is there; the adjustment is one formula (section 3, item 7) |
| Monte Carlo trade reshuffle | Amibroker built in; FX Replay; quant practice | LACKS | 20 lines of numpy over the stored per-trade R |
| Compare two runs side by side | TradingView (two strategies), QuantConnect, vectorbt | LACKS | sim-v2 step (d) plans A vs B |
| Conditions / filters on any rule (session, trend, volatility, weekday) | Amibroker AFL, Pine inputs, by hand in Python | LACKS | OVERRIDE item 2; sim-v2 step (b) designed, not written |
| Plain-words verdict with a reason | nobody; the desk is ahead | HAS | PASSED / FAILED / NOT ENOUGH DATA with the 95 % range |
| Example trades on real candles | TradingView chart markers; journals (TradesViz) | HAS | 6 tiny SVGs with date, level, stop, target, exit |
| Result file per run, one page listing every test | QuantConnect project list; Lean report JSON | PARTLY | results/*.json schema and the artifact exist; the desk does not write a file per Run yet (sim-v2 step (e)) |

## 3. Simplifications and additions, ranked by value to him

Needs: 1 accuracy, 2 selectable params + conditions, 3 performance, 4 visualization, 5 user friendly, 6 wired (result files). Effort S = hours, M = a day.

| # | Change | Needs | Effort | Remove or merge |
|---|---|---|---|---|
| 1 | **Equity curve with the drawdown shaded under it**, in R and as $1,000 at 1 % risk (OURS), scrubbable; the curve turns red below the start line | 4, 5 | M | Merge sim-v2 step (d) with this; one chart, not two. Show `maxdd` (already computed) as a number beside it |
| 2 | **Standard numbers strip**: trades (ideas never filled), win rate, average R after fees with its 95 % range, profit factor, max drawdown, fee share ("before fees +0.22 R, fees -0.34 R, after fees -0.12 R") | 4, 5, 1 | S | Replaces the 3-tile row. Worst losing streak moves to a small line. win rate, maxdd, mean_gross_r, mean_fee_r already exist in `stats`; only profit factor is new (sum of gross wins / sum of gross losses) |
| 3 | **Slippage box** (ours): a percent of price added against the trade on every market and stop fill, default 0.02 % (one tick-ish on BTC), 0 on limit fills. One number, labelled OURS, one ledger label field | 1 | S | `_bars.run_trade` takes a `slip`; levels passes it through `_fees` as an extra cost on STOP/TIME legs. tom_bt's `slip_pts` is the precedent; do not invent a second model |
| 4 | **Trade list**: one row per filled trade (date, side, entry reason, exit reason, R, running R), click a row to see its candle chart | 4, 5 | M | Keep "3 winners, 3 losers" as the default six rows highlighted; the pictures stay. Lets him find the trade on a real chart (his words) |
| 5 | **Conditions panel** as a post-filter: side, UTC hour window, weekday, EMA trend (timeframe and length typed), ATR-percentile band; a breakdown table by condition with n | 2, 4 | M | sim-v2 step (b) as designed. Cut "layer B fired within N bars" to later: it needs another study's signal cache and will have tiny n. Show the table, not six separate runs |
| 6 | **Magical 1: Monte Carlo reshuffle bands.** Shuffle the order of the same filled trades 1,000 times, draw the 5 %-95 % band of the equity curve behind his curve, print "with this same edge, the worst drawdown is between X and Y R in 9 of 10 orderings". Traders rarely see that their drawdown is mostly luck of the order | 4, 1 | S | numpy only, runs in under a second on 369 trades; nothing to remove |
| 7 | **Magical 2: the luck line (trial-adjusted result).** With N tries in the ledger, the best of N no-edge rules reaches about sd x sqrt(2 ln N) / sqrt(n) R on average. Print one line under the verdict: "After 9 tries on this data, luck alone reaches +0.07 R; your +0.03 R is below that." This is the deflated Sharpe idea without the jargon | 1, 5 | S | Replaces the sentence "the best of many tries looks better than it is" with the number. Uses `sd`, `n` and `try_no`, all present |
| 8 | **Run time and run id on the page; write `results/desk-<id>.json` per Run** | 3, 6 | S | sim-v2 steps (c) and (e). The run time is already measurable; the id is the cache key |
| 9 | **Compare A vs B**: keep the last run, show the two number strips and both curves | 4, 5 | M | Merge the mockup's Compare tab (variant slider, family table) into this; precomputed variants are dropped |
| 10 | **Declutter the page**: move the Questions panel off the desk (questions.json stays; answers go through the Control Room), drop the "prior tries by the original study" footnote into the ledger line, show (trader) / (ours) as small coloured tags, delete `mockup/` (operator cut its polish; the override is the design) | 5 | S | Removes one section, one footnote and one folder; nothing of value lost |

Docs to trim in the same ship, not done here because sim-v2 owns the folder: SIM_DESIGN_RESEARCH.md sections 2-5 (five tabs, quiz, badges) are superseded by the OVERRIDE block; ROADMAP.md section 4 (the 2-hour planner for 2026-10-21) is history.

What not to build, confirmed: a parameter optimizer, rolling walk-forward, rolling Sharpe charts, a candle library, a public page that runs anything.

## 4. Ready card lines (id, title, done-when)

Not created; copy into tasks.py when sim-v2's steps (b)-(e) have shipped.

| id | title | done-when |
|---|---|---|
| sim-desk-numbers-strip | Standard numbers strip on the desk | page shows trades, win rate, mean R with range, profit factor, max drawdown, fee share (gross / fee / net) for every Run; test fails on old page; levels reads "+0.22 R before fees, -0.34 R fees, -0.12 R after" |
| sim-desk-slippage | Slippage box on every study | one OURS percent applied against market and stop fills in `_bars.run_trade` and the levels fee path; default 0.02 %; ledger label carries it; test: a 0.1 % slip lowers levels net by more than 0.05 R and leaves limit-only legs unchanged |
| sim-desk-equity-dd | Equity curve with drawdown, R and $1,000 | one SVG per Run: cumulative R (and $ at 1 % risk, OURS) with the drawdown shaded; scrub shows date and running R; `maxdd` shown beside it; sim-v2 step (d) closes this if it ships the same |
| sim-desk-trade-list | Clickable trade list | table of filled trades (date UTC, side, entry reason, exit reason, R, running R); clicking a row draws that trade's candle chart; the six default charts are highlighted rows |
| sim-desk-mc-bands | Monte Carlo reshuffle bands | 1,000 shuffles of the filled trades' R; 5-95 % band behind the equity curve; one sentence with the drawdown range; under 1 s for 400 trades; test on a fixed seed |
| sim-desk-luck-line | Luck line under the verdict | one sentence: "after N tries, luck alone reaches +X R" using sd x sqrt(2 ln N) / sqrt(n); N = ledger tries for the study incl. prior study rows; test with a planted no-edge sample |
| sim-desk-conditions | Conditions post-filter and breakdown | side, UTC hours, weekday, EMA trend, ATR band on any study; breakdown table with n per bucket; one ledger row per new condition set; test: hour window drops out-of-window trades (sim-v2 step (b)) |
| sim-desk-compare | Compare A vs B | last two Runs side by side: numbers strip and curves; nothing precomputed; mockup Compare tab retired |
| sim-desk-declutter | Declutter the desk page | Questions panel off the page, prior-tries footnote folded into the ledger line, trader/ours tags, `mockup/` deleted, SIM_DESIGN_RESEARCH.md sections 2-5 cut to one line pointing at the override |

## 5. Method notes (for the next reviewer)

- Checks ran from a scratch script (temp TRIALS and temp result caches); the only shared state touched was the gitignored `cache/` (bars, levels ideas, results).
- "No look-ahead" for RSI and WaveTrend: every filled trade replayed from its stored ref; entry time >= the signal bar's close. For levels: every filled trade re-simulated; no fill bar before the touch bar; E1/E4 features come from 5m bars closed before the touch (ladder_run.py:286-287).
- Fee share for levels: mean fee 0.337 R on filled trades (0.111 R averaged over all 772 ideas, as the old page showed); gross therefore +0.218 R. Fees in R are large because the K5 stop (just past today's extreme, +0.1 %) makes R small in price.
- Not checked: the artifact page in a browser (read-only export, out of scope); T09 live parity (it covers the live engine's layers, not these studies).
